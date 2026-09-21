from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class MarketItem(ApiModel):
    ticker: str
    companyName: str | None = None
    spotPrice: float
    strategy: str | None = None
    rationale: str | None = None
    probabilityOfProfit: float | None = None
    dte: int | None = None
    expirationDate: str | None = None


class PickCollection(ApiModel):
    picks: list[MarketItem] = Field(default_factory=list)
    managementNote: str | None = None
    riskWarning: str | None = None


class Analysis(ApiModel):
    ticker: str
    companyName: str | None = None
    spotPrice: float
    previousClose: float
    change: float
    changePercent: float
    impliedVolatility: float
    spreads: list[dict[str, Any]]
    condors: list[dict[str, Any]]
    ranges: list[dict[str, Any]]
    rationale: str


class VixPredictor(ApiModel):
    vixLevel: float
    vixChange: float
    vixChangePct: float
    vixPercentile: float
    fearLabel: str
    fearColor: str
    spyPrice: float
    spyChange: float
    spyChangePct: float
    expectedMoves: list[dict[str, Any]]
    vixHistory: list[dict[str, Any]]
    commentary: str


class IndexPicks(ApiModel):
    snapshot: dict[str, Any]
    dtePicks: list[dict[str, Any]]
    weekendPlay: dict[str, Any]
    weekendEventRisk: dict[str, Any]
    methodology: str