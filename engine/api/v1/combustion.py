"""Combustion API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import DateInput, DateRangeInput, PlanetDateRangeInput
from core.utils import parse_date
from modules.combustion import check_daily, find_periods, get_range

router = APIRouter(prefix="/api/v1/combustion", tags=["Combustion"])


@router.post("", summary="Daily Combustion Status")
def daily(payload: DateInput):
    try:
        return check_daily(parse_date(payload.date), payload.tz_offset, payload.ayanamsa)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/periods", summary="Combustion Periods")
def periods(payload: PlanetDateRangeInput):
    try:
        return find_periods(
            payload.planet, parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/range", summary="Combustion — Date Range")
def range_(payload: DateRangeInput):
    try:
        return get_range(
            parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))
