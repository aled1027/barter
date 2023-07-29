from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Extra


class Candle(BaseModel):
    startedAt: str
    updatedAt: str
    market: str
    resolution: str
    low: str
    high: str
    open: str
    close: str
    baseTokenVolume: str
    trades: str
    usdVolume: str
    startingOpenInterest: str


class CandlesModel(BaseModel):
    candles: List[Candle]


class QuoteAsset(Enum):
    USD = "USD"


class Status(Enum):
    ONLINE = "ONLINE"
    CLOSE_ONLY = "CLOSE_ONLY"


class Type(Enum):
    PERPETUAL = "PERPETUAL"


class Market(BaseModel):
    class Config:
        extra = Extra.forbid

    market: str
    status: Status
    baseAsset: str
    quoteAsset: QuoteAsset
    stepSize: str
    tickSize: str
    indexPrice: str
    oraclePrice: str
    priceChange24H: str
    nextFundingRate: str
    nextFundingAt: datetime
    minOrderSize: str
    type: Type
    initialMarginFraction: str
    maintenanceMarginFraction: str
    transferMarginFraction: str
    volume24H: str
    trades24H: int
    openInterest: str
    incrementalInitialMarginFraction: str
    incrementalPositionSize: int
    maxPositionSize: int
    baselinePositionSize: int
    assetResolution: str
    syntheticAssetId: str


class DydxMarketsModel(BaseModel):
    class Config:
        extra = Extra.forbid

    markets: Dict[str, Market]
