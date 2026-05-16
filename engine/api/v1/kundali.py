"""Kundali (Birth Chart) API routes."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas import KundaliInput
from core.utils import parse_date
from core.cities import resolve_city
from modules.kundali import generate_kundali

router = APIRouter(prefix="/api/v1/kundali", tags=["Kundali (Birth Chart)"])


@router.post("", summary="Generate Birth Chart with all 16 Shodashvarga")
def birth_chart(payload: KundaliInput):
    """
    Generate complete Kundali (birth chart).
    Returns Ascendant, all 9 planet details with nakshatra/sub-lord,
    and all 16 divisional charts (D1 through D60).
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

        result = generate_kundali(dt, lat, lon, tz, payload.ayanamsa)
        return result
    except Exception as e:
        raise HTTPException(400, str(e))
