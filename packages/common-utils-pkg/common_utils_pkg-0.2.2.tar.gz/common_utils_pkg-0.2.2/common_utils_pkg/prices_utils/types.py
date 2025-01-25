from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class MarketTypeEnum(str, Enum):
    SPOT = "spot"
    FUTURES = "futures"


class SymbolInfo(BaseModel):
    id: int
    symbol: str
    first_data_date: datetime | None
    last_loaded_data_date: datetime | None
    is_spot_finished: bool

    first_futures_data_date: datetime | None
    last_loaded_futures_data_date: datetime | None
    is_futures_finished: bool


class TickTrade(BaseModel):
    time: datetime
    symbol: str
    price: float
    quantity: float


class Kline(BaseModel):
    symbol: str
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class Funding(BaseModel):
    symbol: str
    time: datetime
    funding: float
    mark_price: float


class PremiumIndexKline(BaseModel):
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float


class ExchangeMetrics(BaseModel):
    symbol: str
    time: datetime
    sum_open_interest: float
    sum_open_interest_value: float
    count_toptrader_long_short_ratio: float
    sum_toptrader_long_short_ratio: float
    count_long_short_ratio: float
    sum_taker_long_short_vol_ratio: float


class Liquidations(BaseModel):
    symbol: str
    time: datetime
    is_buy_side: bool
    price: float
    orig_qty: float
    avg_price: float
    last_fill_qty: float
    accumulated_fill_qty: float


class SymbolVolatility(BaseModel):
    symbol: str
    date: datetime
    long_trades: int
    short_trades: int
    last_level_price: float | None
