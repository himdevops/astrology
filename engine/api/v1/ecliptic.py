"""Ecliptic Crossings API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import DateInput, DateRangeInput
from core.utils import parse_date
from modules.ecliptic import get_daily, get_all_crossings

router = APIRouter(prefix="/api/v1/ecliptic", tags=["Ecliptic Crossings"])


@router.post("", summary="Daily Ecliptic Status")
def daily(payload: DateInput):
    try:
        return get_daily(parse_date(payload.date), payload.tz_offset, payload.ayanamsa)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/crossings", summary="Find Crossings in Range")
def crossings(payload: DateRangeInput):
    try:
        return get_all_crossings(
            parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))
