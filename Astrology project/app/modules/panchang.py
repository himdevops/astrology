"""
panchang module — Panchang & Muhurta endpoints.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.panchang import calculate_panchang, calculate_panchang_calendar

router = APIRouter(tags=["v3.0 — Panchang"])


# ── schemas ───────────────────────────────────────────────────

class PanchangInput(BaseModel):
    date: str  = Field(...,  example="2026-04-28")
    time: str  = Field(default="09:15", example="09:15")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None, example=19.076)
    longitude: Optional[float] = Field(default=None, example=72.8777)
    timezone_offset_minutes: int = Field(default=330)
    ayanamsa: str = Field(default="lahiri")


class PanchangCalendarInput(BaseModel):
    start_date: str = Field(..., example="2026-04-01")
    days: int = Field(default=30, ge=7, le=365)
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None, example=19.076)
    longitude: Optional[float] = Field(default=None, example=72.8777)
    timezone_offset_minutes: int = Field(default=330)
    ayanamsa: str = Field(default="lahiri")


# ── endpoints ─────────────────────────────────────────────────

@router.post("/panchang", summary="Daily Panchang with Muhurta")
def panchang(payload: PanchangInput):
    """
    Tithi, Nakshatra, Yoga, Karana, Vara + Muhurta windows
    (Rahu Kalam, Gulika, Abhijit, Choghadiya).
    """
    try:
        lat = payload.latitude or 19.076
        lon = payload.longitude or 72.8777
        return calculate_panchang(
            payload.date, payload.time, lat, lon,
            payload.timezone_offset_minutes, payload.ayanamsa,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/panchang-calendar", summary="Multi-day Panchang Trading Calendar")
def panchang_calendar(payload: PanchangCalendarInput):
    """Best/worst trading days based on Panchang financial scores."""
    try:
        lat = payload.latitude or 19.076
        lon = payload.longitude or 72.8777
        return calculate_panchang_calendar(
            payload.start_date, payload.days, lat, lon,
            payload.timezone_offset_minutes, payload.ayanamsa,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
