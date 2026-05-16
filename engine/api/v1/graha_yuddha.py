"""Graha Yuddha API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import DateInput, DateRangeInput
from core.utils import parse_date
from modules.graha_yuddha import check_daily, find_events, get_range

router = APIRouter(prefix="/api/v1/graha-yuddha", tags=["Graha Yuddha"])


@router.post("", summary="Daily Graha Yuddha")
def daily(payload: DateInput):
    try:
        return check_daily(parse_date(payload.date), payload.tz_offset, payload.ayanamsa)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/events", summary="Graha Yuddha Events in Range")
def events(payload: DateRangeInput):
    try:
        return find_events(
            parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/range", summary="Graha Yuddha — Date Range")
def range_(payload: DateRangeInput):
    try:
        return get_range(
            parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))
