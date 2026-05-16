"""Special Lagnas & Sensitive Points API routes."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas import SpecialLagnasInput
from core.utils import parse_date
from core.cities import resolve_city
from modules.special_lagnas import generate_special_lagnas

router = APIRouter(
    prefix="/api/v1/special-lagnas",
    tags=["Special Lagnas & Sensitive Points"],
)


@router.post("", summary="Calculate Special Lagnas & Sensitive Points")
def special_lagnas(payload: SpecialLagnasInput):
    """
    Calculate all special lagnas (HL, GL, BL, SL, PP, VL, IL, KL, AL),
    sensitive points (Fortuna, Yogi, Bhrigu Bindu, etc.),
    Gulika/Mandi, and Chara Karakas.

    Uses the same input as Kundali + optional karaka_system (7 or 8).
    """
    try:
        d = parse_date(payload.date)
        parts = payload.time.split(":")
        seconds = 0
        if len(parts) == 3:
            seconds = int(parts[2])
        dt = datetime(d.year, d.month, d.day, int(parts[0]), int(parts[1]), seconds)

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        result = generate_special_lagnas(
            dt, lat, lon, tz, payload.ayanamsa,
            karaka_system=payload.karaka_system,
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))
