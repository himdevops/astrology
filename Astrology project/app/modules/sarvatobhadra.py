"""
sarvatobhadra module — Advanced Sarvatobhadra Chakra endpoints.
Full 9×9 grid with Vedha, Latta, Six Bindus, Navatara, transit
analysis, vedha lines for chart rendering, and NSE/BSE signal.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models import BirthDataInput, TransitDataInput, resolve_chart
from app.sarvatobhadra import calculate_sarvatobhadra as cast_sarvatobhadra
from app.core import (
    resolve_location_and_time,
    to_julian_day_utc,
    calculate_planets,
)
from app.nakshatra import get_nakshatra
from app.sbc_analysis import sbc_nse_daily_signal

router = APIRouter(tags=["v3.0 — SBC (Sarvatobhadra)"])


# ── schemas ───────────────────────────────────────────────────

class SarvatobhadraInput(BirthDataInput):
    """Full SBC analysis — natal + transit."""
    transit_date: Optional[str] = Field(default=None, example="2026-04-15")
    transit_time: Optional[str] = Field(default="09:15", example="09:15")
    transit_place: Optional[str] = Field(default="Mumbai, Maharashtra, India")


class SBCDailySignalInput(BaseModel):
    """Quick daily SBC signal using Latta + Navatara (no full grid needed)."""
    # Natal Moon nakshatra source
    name: str = Field(default="Chart", example="Himanshu")
    date: str = Field(..., example="1990-01-15",
                      description="Birth date to derive Janma Nakshatra")
    time: str = Field(..., example="10:30")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")
    # Transit
    transit_date: Optional[str] = Field(default=None, example="2026-04-28")
    transit_time: str = Field(default="09:15")
    transit_place: str = Field(default="Mumbai, Maharashtra, India")


# ── endpoints ─────────────────────────────────────────────────

@router.post("/sarvatobhadra", summary="Advanced Sarvatobhadra Chakra")
def sarvatobhadra(payload: SarvatobhadraInput):
    """
    Full Sarvatobhadra Chakra with:

    - 9×9 grid with nakshatras, rashis, tithis, aksharas, weekdays
    - Natal planet placements on the grid
    - Transit planet positions enriched with nakshatras
    - **Vedha analysis**: horizontal, vertical, diagonal aspects with
      speed-based classification (Dakshina/Vama/Prishtha/Sthana)
    - **Latta analysis**: planetary kicks with direction (forward/backward),
      retrograde reversal, severity grading, and NSE sector impact
    - **Six Personal Bindus**: Janma, Karma, Sanghatika, Uday, Adhan, Vinash
    - **Navatara**: 9 tara categories from Janma Nakshatra
    - **Vedha line data**: start/end grid coordinates + line styles for
      chart rendering (solid/dashed/thick/double)
    - **Bindu analysis**: per-bindu status (AFFLICTED/PROTECTED/MIXED/CLEAR)
    - **NSE/BSE market signal**: composite score with action recommendations
    """
    try:
        return cast_sarvatobhadra(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sbc/daily-signal", summary="Quick SBC Daily NSE/BSE Signal")
def sbc_daily_signal(payload: SBCDailySignalInput):
    """
    Quick daily NSE/BSE signal using Latta + Navatara from SBC.
    Faster than full grid analysis — use for daily market scanning.

    Returns:
    - Active Lattas (which planets are kicking which nakshatras)
    - Navatara-based transit quality
    - Market signal (BULLISH / BEARISH / NEUTRAL)
    - Action recommendation
    """
    try:
        from datetime import date as _date

        # Get natal Moon nakshatra (Janma)
        natal_data = resolve_chart(payload, need_ascendant=False)
        moon = next(
            (p for p in natal_data.planets if p["planet"] == "Moon"), None,
        )
        if not moon:
            raise ValueError("Moon position not found")
        janma_nak_info = get_nakshatra(moon["longitude"])
        janma_nak = janma_nak_info["nakshatra"]

        # Get transit planets
        t_date = payload.transit_date or _date.today().isoformat()
        t_time = payload.transit_time
        t_place = payload.transit_place

        t_resolved, t_dt = resolve_location_and_time(
            place=t_place, date_str=t_date, time_str=t_time,
            latitude=None, longitude=None, timezone_offset_minutes=None,
        )
        t_jd = to_julian_day_utc(t_dt, t_resolved.timezone_offset_minutes)
        t_planets = calculate_planets(t_jd, payload.ayanamsa)

        # Build transit maps
        transit_nak_map = {}
        retrograde_map = {}
        for tp in t_planets:
            nak_info = get_nakshatra(tp["longitude"])
            transit_nak_map[tp["planet"]] = nak_info["nakshatra"]
            retrograde_map[tp["planet"]] = tp.get("retrograde", False)

        signal = sbc_nse_daily_signal(janma_nak, transit_nak_map, retrograde_map)

        return {
            "type": "sbc_daily_signal",
            "name": payload.name,
            "janma_nakshatra": janma_nak,
            "transit_date": t_date,
            "transit_place": t_resolved.place,
            **signal,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
