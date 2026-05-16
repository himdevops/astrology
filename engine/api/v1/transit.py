"""Transit (sign/nakshatra changes) API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import DateRangeInput, PlanetDateRangeInput
from core.utils import parse_date
from modules.transit import get_all_transits, find_sign_changes, find_nakshatra_changes

router = APIRouter(prefix="/api/v1/transit", tags=["Transit"])


@router.post("", summary="All Sign Changes in Range")
def all_transits(payload: DateRangeInput):
    try:
        return get_all_transits(
            parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/sign", summary="Planet Sign Changes")
def sign_changes(payload: PlanetDateRangeInput):
    try:
        return find_sign_changes(
            payload.planet, parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/nakshatra", summary="Planet Nakshatra Changes")
def nakshatra_changes(payload: PlanetDateRangeInput):
    try:
        return find_nakshatra_changes(
            payload.planet, parse_date(payload.start_date), parse_date(payload.end_date),
            payload.tz_offset, payload.ayanamsa,
        )
    except Exception as e:
        raise HTTPException(400, str(e))
