from common_utils_pkg.utils import (
    get_postgres_database_connection_async,
    to_datetime_from_timestamp,
)
from .formatters import format_symbol_volatility


class IndicatorsDatabaseAsync:
    def __init__(self):
        self.indicators_connection = None

    @classmethod
    async def connect(cls, database_uri: str, attempts: int, delay=10):
        """
        Асинхронный фабричный метод для создания экземпляра класса.
        """
        instance = cls()
        instance.indicators_connection = await get_postgres_database_connection_async(
            database_uri=database_uri, attempts=attempts, delay=delay
        )
        return instance

    # Indicators
    async def get_symbol_volatility(self, tickers: tuple[str], from_ts: int, to_ts: int, raw=False):
        rows = await self.indicators_connection.fetch(
            "SELECT * FROM symbol_futures_volatility WHERE symbol = ANY($1) AND date >= $2 AND date < $3 ORDER BY date ASC",
            tickers,
            to_datetime_from_timestamp(from_ts),
            to_datetime_from_timestamp(to_ts),
        )

        return format_symbol_volatility(rows, raw)
