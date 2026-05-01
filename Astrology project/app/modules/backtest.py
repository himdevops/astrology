"""
backtest module — Backtest Astrology Signals endpoint.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.market_data import get_historical_data
from app.backtesting import (
    backtest_moon_nakshatra,
    backtest_planetary_transits,
    backtest_composite,
)

router = APIRouter(tags=["v3.0 — Backtesting"])


# ── schemas ───────────────────────────────────────────────────

class BacktestInput(BaseModel):
    ticker: str = Field(default="NIFTY_50", example="NIFTY_50")
    start_date: str = Field(default="2023-01-01", example="2023-01-01")
    end_date: Optional[str] = Field(default=None, example="2026-04-28")
    signal_type: str = Field(
        default="composite",
        description="'moon_nakshatra', 'planetary_transits', or 'composite'",
    )
    ayanamsa: str = Field(default="lahiri")


# ── endpoints ─────────────────────────────────────────────────

@router.post("/backtest", summary="Backtest Astrology Signals")
def backtest(payload: BacktestInput):
    """
    Test astrology signals against historical NSE/BSE data.
    Returns hit ratio, cumulative P&L, Sharpe ratio, drawdown,
    monthly breakdown, and per-nakshatra accuracy.
    """
    try:
        market = get_historical_data(
            payload.ticker, payload.start_date, payload.end_date,
        )
        if "error" in market:
            return market

        data = market.get("data", [])
        if len(data) < 30:
            return {"error": "Insufficient market data for backtesting (need 30+ days)"}

        if payload.signal_type == "moon_nakshatra":
            return backtest_moon_nakshatra(data, payload.ayanamsa)
        elif payload.signal_type == "planetary_transits":
            return backtest_planetary_transits(data, payload.ayanamsa)
        else:
            return backtest_composite(data, payload.ayanamsa)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
