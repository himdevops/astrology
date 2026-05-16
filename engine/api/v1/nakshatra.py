"""Nakshatra Analysis API routes."""
from __future__ import annotations

import traceback
from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas import KundaliInput, TransitNavtaraInput
from core.utils import parse_date
from core.cities import resolve_city
from modules.nakshatra import generate_nakshatra_analysis, generate_transit_navtara

router = APIRouter(prefix="/api/v1/nakshatra", tags=["Nakshatra Analysis"])


@router.post("", summary="Comprehensive Nakshatra Analysis")
def nakshatra_analysis(payload: KundaliInput):
    """
    Generate comprehensive Nakshatra analysis.
    Returns Nakshatra detail for all 9 planets + Ascendant,
    Navtara grid, remedies, activation guidance, and pada-level details.
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

        result = generate_nakshatra_analysis(dt, lat, lon, tz, payload.ayanamsa)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        print(f"NAKSHATRA ERROR:\n{tb}", flush=True)
        raise HTTPException(400, f"{str(e)} | TRACE: {tb[-500:]}")


@router.post("/transit", summary="Transit Navtara Analysis")
def transit_navtara(payload: TransitNavtaraInput):
    """
    Calculate transit Navtara — which tara each planet is transiting
    on a given date, relative to the birth Moon's Nakshatra.
    """
    try:
        # Birth datetime
        bd = parse_date(payload.date)
        bparts = payload.time.split(":")
        birth_dt = datetime(bd.year, bd.month, bd.day, int(bparts[0]), int(bparts[1]))

        # Transit datetime
        td = parse_date(payload.transit_date)
        tparts = payload.transit_time.split(":")
        transit_dt = datetime(td.year, td.month, td.day, int(tparts[0]), int(tparts[1]))

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        result = generate_transit_navtara(birth_dt, transit_dt, lat, lon, tz, payload.ayanamsa)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        print(f"TRANSIT NAVTARA ERROR:\n{tb}", flush=True)
        raise HTTPException(400, f"{str(e)} | TRACE: {tb[-500:]}")
