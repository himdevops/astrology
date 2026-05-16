"""Panchang API routes."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas import PanchangInput
from core.panchang import get_panchang
from core.utils import parse_date
from core.cities import resolve_city

router = APIRouter(prefix="/api/v1/panchang", tags=["Panchang"])


@router.post("", summary="Daily Panchang")
def daily_panchang(payload: PanchangInput):
    """Tithi, Nakshatra, Yoga, Karana, Vara, Sunrise/Sunset."""
    try:
        d = parse_date(payload.date)
        parts = payload.time.split(":")
        dt = datetime(d.year, d.month, d.day, int(parts[0]), int(parts[1]))

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        result = get_panchang(dt, lat, lon, tz, payload.ayanamsa)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(400, str(e))
