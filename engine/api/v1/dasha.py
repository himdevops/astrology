"""Dasha (Planetary Periods) API routes."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas import DashaInput
from core.utils import parse_date
from core.cities import resolve_city
from modules.dasha import generate_dashas

router = APIRouter(prefix="/api/v1/dasha", tags=["Dasha (Planetary Periods)"])


@router.post("", summary="Calculate all Dasha systems")
def dasha_calc(payload: DashaInput):
    """
    Calculate Dasha periods for a birth chart.
    Returns up to 5 dasha systems: Vimshottari, Yogini, Ashtottari,
    Chara (Jaimini), and Narayana (Jaimini).
    Each nakshatra-based system supports up to 5 levels of sub-periods.
    """
    try:
        d = parse_date(payload.date)
        parts = payload.time.split(":")
        dt = datetime(d.year, d.month, d.day, int(parts[0]), int(parts[1]))

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        result = generate_dashas(
            dt, lat, lon, tz,
            payload.ayanamsa,
            payload.max_level,
            payload.systems,
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))
