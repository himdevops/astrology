"""Mutual Aspects API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import DateInput, DateRangeInput
from core.utils import parse_date
from modules.aspects import get_daily, get_range

router = APIRouter(prefix="/api/v1/aspects", tags=["Mutual Aspects"])


@router.post("", summary="Daily Mutual Aspects")
def daily(payload: DateInput):
    try:
        return get_daily(parse_date(payload.date), payload.tz_offset, payload.ayanamsa)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/range", summary="Aspects — Date Range")
def range_(payload: DateRangeInput):
    try:
        return get_range(
            parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))
