from .types import SymbolInfo, Kline, TickTrade, Funding, MarketTypeEnum
from common_utils_pkg.types import KlineIntervalEnum
from common_utils_pkg.utils import (
    to_datetime_from_timestamp,
    get_postgres_database_connection_async,
)
from .formatters import (
    format_funding,
    format_ohlc_prices,
    format_premium_index,
    format_symbols,
    format_trades,
)


class PriceDatabaseAsync:
    def __init__(self):
        self.prices_connection = None

    @classmethod
    async def connect(cls, database_uri: str, attempts: int, delay=10):
        """
        Асинхронный фабричный метод для создания экземпляра класса.
        """
        instance = cls()
        instance.prices_connection = await get_postgres_database_connection_async(
            database_uri=database_uri, attempts=attempts, delay=delay
        )
        return instance

    async def get_all_symbols(self) -> list[SymbolInfo]:
        rows = await self.prices_connection.fetch("SELECT * FROM symbols")
        return format_symbols(rows, raw=False)

    async def get_symbol(self, symbol: str) -> SymbolInfo | None:
        row = await self.prices_connection.fetchrow(
            "SELECT * FROM symbols WHERE symbol = $1 LIMIT 1",
            symbol,
        )
        return format_symbols([row], raw=False)[0] if row else None

    async def get_spot_symbols(self) -> list[SymbolInfo]:
        rows = await self.prices_connection.fetch(
            "SELECT * FROM symbols WHERE first_data_date IS NOT NULL AND last_loaded_data_date IS NOT NULL"
        )
        return format_symbols(rows, raw=False)

    async def get_futures_symbols(self) -> list[SymbolInfo]:
        rows = await self.prices_connection.fetch(
            "SELECT * FROM symbols WHERE first_futures_data_date IS NOT NULL AND last_loaded_futures_data_date IS NOT NULL"
        )
        return format_symbols(rows, raw=False)

    async def get_spot_tick_prices(self, tickers: tuple[str], from_ts: int, to_ts: int, raw=False):
        return await self._get_tick_prices(
            tickers, from_ts, to_ts, type=MarketTypeEnum.SPOT, raw=raw
        )

    async def get_futures_tick_prices(
        self, tickers: tuple[str], from_ts: int, to_ts: int, raw=False
    ):
        return await self._get_tick_prices(
            tickers, from_ts, to_ts, type=MarketTypeEnum.FUTURES, raw=raw
        )

    async def get_spot_klines(
        self, tickers: tuple[str], from_ts: int, to_ts: int, period: KlineIntervalEnum, raw=False
    ):
        return await self._get_klines(
            tickers, from_ts, to_ts, period, type=MarketTypeEnum.SPOT, raw=raw
        )

    async def get_futures_klines(
        self, tickers: tuple[str], from_ts: int, to_ts: int, period: KlineIntervalEnum, raw=False
    ):
        return await self._get_klines(
            tickers, from_ts, to_ts, period, type=MarketTypeEnum.FUTURES, raw=raw
        )

    async def get_funding(
        self, tickers: tuple[str], from_ts: int, to_ts: int, raw=False
    ) -> list[dict] | list[Funding]:
        rows = await self.prices_connection.fetch(
            "SELECT * FROM funding WHERE symbol = ANY($1) AND time >= $2 AND time < $3 ORDER BY time ASC",
            tickers,
            to_datetime_from_timestamp(from_ts),
            to_datetime_from_timestamp(to_ts),
        )
        return format_funding(rows, raw)

    async def get_premium_index(self, tickers: tuple[str], from_ts: int, to_ts: int, raw=False):
        rows = await self.prices_connection.fetch(
            "SELECT * FROM premium_index_1m WHERE symbol = ANY($1) AND time >= $2 AND time < $3 ORDER BY time ASC",
            tickers,
            from_ts,
            to_ts,
        )

        return format_premium_index(rows, raw)

    async def _get_tick_prices(
        self, symbols: tuple[str], from_ts: int, to_ts: int, type: MarketTypeEnum, raw=False
    ) -> list[dict] | list[TickTrade]:
        tick_table_name = "tick_trades" if type is MarketTypeEnum.SPOT else "tick_futures_trades"
        rows = await self.prices_connection.fetch(
            f"SELECT * FROM {tick_table_name} WHERE symbol = ANY($1) AND time >= $2 AND time < $3 ORDER BY time ASC",
            tuple(symbols),
            to_datetime_from_timestamp(from_ts),
            to_datetime_from_timestamp(to_ts),
        )

        return format_trades(rows, raw)

    async def _get_klines(
        self,
        symbols: tuple[str],
        from_ts: int,
        to_ts: int,
        period: KlineIntervalEnum,
        type: MarketTypeEnum,
        raw=False,
    ) -> list[dict] | list[Kline]:
        period_type = period.value[-1]
        period_range = int(period.value[0:-1])

        if period_type == "m":
            klines_table_name = (
                "ohlc_data_minute" if type is MarketTypeEnum.SPOT else "ohlc_futures_data_minute"
            )
        else:
            klines_table_name = (
                "ohlc_data_hour" if type is MarketTypeEnum.SPOT else "ohlc_futures_data_hour"
            )

        need_to_aggregate = period not in [KlineIntervalEnum.ONE_MIN, KlineIntervalEnum.ONE_HOUR]

        rows = []
        if not need_to_aggregate:
            rows = await self.prices_connection.fetch(
                f"SELECT * FROM {klines_table_name} WHERE symbol = ANY($1) AND date >= $2 AND date < $3 ORDER BY date ASC",
                tuple(symbols),
                to_datetime_from_timestamp(from_ts),
                to_datetime_from_timestamp(to_ts),
            )
        else:
            bucket_period = str(period_range)
            if period_type == "m":
                bucket_period += " minute"
            elif period_type == "h":
                bucket_period += " hour"
            elif period_type == "d":
                bucket_period += " day"
            elif period_type == "w":
                bucket_period += " week"
            elif period_type == "M":
                bucket_period += " month"

            rows = await self.prices_connection.fetch(
                f"""SELECT symbol,
                        time_bucket('{bucket_period}', date) AS date_1d,
                        FIRST(open, date) AS open,
                        MAX(high) AS high,
                        MIN(low) AS low,
                        LAST(close, date) AS close,
                        SUM(volume) AS volume
                    FROM {klines_table_name}
                    WHERE symbol = ANY($1) AND date >= $2 AND date < $3
                    GROUP BY date_1d, symbol
                    ORDER BY date_1d ASC""",
                tuple(symbols),
                to_datetime_from_timestamp(from_ts),
                to_datetime_from_timestamp(to_ts),
            )

        return format_ohlc_prices(rows, raw)
