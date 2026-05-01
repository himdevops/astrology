"""
kp module — KP (Krishnamurti Paddhati) System endpoint.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import BirthDataInput, resolve_chart
from app.core import (
    resolve_location_and_time,
    to_julian_day_utc,
    calculate_planets,
)
from app.kp_system import calculate_kp_analysis

router = APIRouter(tags=["v3.0 — KP System"])


# ── schemas ───────────────────────────────────────────────────

class KPAnalysisInput(BirthDataInput):
    ayanamsa: str = Field(default="krishnamurti")
    transit_date: Optional[str] = Field(default=None, example="2026-04-28")
    transit_time: Optional[str] = Field(default="09:15")


# ── endpoints ─────────────────────────────────────────────────

@router.post("/kp", summary="KP (Krishnamurti Paddhati) Analysis")
def kp_analysis(payload: KPAnalysisInput):
    """
    Cuspal sub-lords, significator analysis, financial house analysis
    (2nd/5th/7th/10th/11th), and ruling planets for timing.
    """
    try:
        data = resolve_chart(payload, need_houses=True)

        transit_planets = None
        transit_dt = None
        if payload.transit_date:
            tr, tdt = resolve_location_and_time(
                place=payload.place,
                date_str=payload.transit_date,
                time_str=payload.transit_time or "09:15",
                latitude=payload.latitude,
                longitude=payload.longitude,
                timezone_offset_minutes=payload.timezone_offset_minutes,
            )
            tjd = to_julian_day_utc(tdt, tr.timezone_offset_minutes)
            transit_planets = calculate_planets(tjd, payload.ayanamsa)
            transit_dt = tdt

        kp_data = calculate_kp_analysis(
            data.planets, data.houses, data.ascendant,
            transit_planets, transit_dt,
        )
        return {
            "type": "kp_analysis",
            "name": payload.name,
            "birth_date": payload.date,
            "ayanamsa": payload.ayanamsa,
            "ascendant": data.ascendant,
            "kp_analysis": kp_data,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
