"""
market module — Live NSE/BSE prices and sector performance endpoints.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.market_data import get_current_prices, get_sector_performance

router = APIRouter(tags=["v3.0 — Market Data"])


# ── schemas ───────────────────────────────────────────────────

class MarketDataInput(BaseModel):
    indices: List[str] = Field(
        default=["NIFTY_50", "SENSEX", "BANK_NIFTY"],
        description="Index names: NIFTY_50, SENSEX, BANK_NIFTY, NIFTY_IT, etc.",
    )


# ── endpoints ─────────────────────────────────────────────────

@router.post("/market/prices", summary="Live NSE/BSE Prices")
def market_prices(payload: MarketDataInput):
    """Current/latest prices for selected NSE/BSE indices."""
    try:
        return get_current_prices(payload.indices)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/market/sectors", summary="Sector Performance")
def sector_performance(period: str = "1mo"):
    """NSE sectoral index performance for sector rotation analysis."""
    try:
        return get_sector_performance(period)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
