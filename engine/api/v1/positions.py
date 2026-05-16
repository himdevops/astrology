"""Planetary Positions API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import PanchangInput, DateRangeInput
from core.utils import parse_date
from core.cities import resolve_city
from modules.positions import get_daily_positions, get_positions_range

router = APIRouter(prefix="/api/v1/positions", tags=["Planetary Positions"])


@router.post("", summary="Daily Positions (with Ascendant)")
def daily(payload: PanchangInput):
    try:
        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset
        return get_daily_positions(
            parse_date(payload.date), tz, payload.ayanamsa,
            latitude=lat, longitude=lon,
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/range", summary="Positions — Date Range")
def range_(payload: DateRangeInput):
    try:
        return get_positions_range(
            parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))
