"""
chart module — Birth Chart & Transit endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import BirthDataInput, TransitDataInput, resolve_chart
from app.nakshatra import get_all_planet_nakshatras, get_moon_nakshatra_signal

router = APIRouter(tags=["Charts"])


# ── endpoints ─────────────────────────────────────────────────

@router.post("/chart", summary="Birth Chart with Nakshatras")
def chart(payload: BirthDataInput):
    """
    Vedic birth chart (D1) with planetary positions, nakshatras,
    house cusps, and financial significance.
    """
    try:
        data = resolve_chart(payload, need_houses=True)
        nakshatras = get_all_planet_nakshatras(data.planets)
        return {
            "type": "birth_chart",
            "name": payload.name,
            "input": {
                "date": payload.date,
                "time": payload.time,
                "place": data.resolved.place,
                "latitude": data.resolved.latitude,
                "longitude": data.resolved.longitude,
                "timezone_name": data.resolved.timezone_name,
                "timezone_offset_minutes": data.resolved.timezone_offset_minutes,
                "ayanamsa": payload.ayanamsa,
            },
            "ascendant": data.ascendant,
            "planets": data.planets,
            "planet_nakshatras": nakshatras,
            "houses": data.houses,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/transits", summary="Current Transit Positions + Moon Signal")
def transits(payload: TransitDataInput):
    """Current planetary transits with Moon nakshatra daily NSE/BSE signal."""
    try:
        data = resolve_chart(payload, need_ascendant=False)
        nakshatras = get_all_planet_nakshatras(data.planets)
        moon = next((p for p in data.planets if p["planet"] == "Moon"), None)
        moon_signal = get_moon_nakshatra_signal(moon["longitude"]) if moon else {}
        return {
            "type": "transits",
            "input": {
                "date": payload.date,
                "time": payload.time,
                "place": data.resolved.place,
                "latitude": data.resolved.latitude,
                "longitude": data.resolved.longitude,
                "timezone_name": data.resolved.timezone_name,
                "timezone_offset_minutes": data.resolved.timezone_offset_minutes,
                "ayanamsa": payload.ayanamsa,
            },
            "planets": data.planets,
            "planet_nakshatras": nakshatras,
            "moon_nakshatra_signal": moon_signal,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
