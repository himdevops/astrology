"""Bhrigu Samhita Predictions API — Classical life readings."""
from __future__ import annotations

import traceback
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.utils import parse_date
from core.cities import resolve_city
from modules.bhrigu import generate_bhrigu_reading, generate_bhrigu_transit

router = APIRouter(prefix="/api/v1/bhrigu", tags=["Bhrigu Samhita"])


class BhriguInput(BaseModel):
    """Bhrigu Samhita prediction input."""
    date: str = Field(..., example="23-09-1992", description="Birth date DD-MM-YYYY")
    time: str = Field(default="12:00", description="Birth time HH:MM")
    latitude: float = Field(default=23.1765)
    longitude: float = Field(default=75.7885)
    tz_offset: float = Field(default=5.5)
    city: Optional[str] = Field(default=None, description="City name for auto coordinates")
    ayanamsa: str = Field(default="lahiri")
    transit_date: Optional[str] = Field(default=None, description="Transit date DD-MM-YYYY (default today)")


@router.post("", summary="Bhrigu Samhita Birth Reading")
def bhrigu_reading(payload: BhriguInput):
    """
    Generate complete Bhrigu Samhita reading for a birth chart.
    Returns classical predictions for each planet based on house placement
    from the ascendant. Based on T.M. Rao's abridged Bhrigu Samhita.
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

        result = generate_bhrigu_reading(
            birth_dt=dt,
            lat=lat,
            lon=lon,
            tz_offset=tz,
            ayanamsa=payload.ayanamsa,
        )
        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transit", summary="Bhrigu Samhita Transit Reading")
def bhrigu_transit(payload: BhriguInput):
    """
    Generate Bhrigu Samhita transit predictions.
    Uses birth chart ascendant + current planetary positions to give
    transit-based life reading per Bhrigu principles.
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

        transit_d = None
        if payload.transit_date:
            transit_d = parse_date(payload.transit_date)
        else:
            transit_d = date.today()

        result = generate_bhrigu_reading(
            birth_dt=dt,
            lat=lat,
            lon=lon,
            tz_offset=tz,
            ayanamsa=payload.ayanamsa,
        )

        transit_result = generate_bhrigu_transit(
            birth_dt=dt,
            lat=lat,
            lon=lon,
            tz_offset=tz,
            ayanamsa=payload.ayanamsa,
            transit_date=transit_d,
        )

        result["transit"] = transit_result
        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
