"""Sarvatobhadra Chakra (SBC) API routes."""
from __future__ import annotations

import traceback
from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas import HoraInput
from core.utils import parse_date
from core.cities import resolve_city
from modules.sbc import generate_sbc

router = APIRouter(prefix="/api/v1/sbc", tags=["Sarvatobhadra Chakra"])


@router.post("", summary="Sarvatobhadra Chakra Analysis")
def sbc_analysis(payload: HoraInput):
    """
    Generate Sarvatobhadra Chakra (SBC) with natal and transit planets,
    vedha lines, and full 9x9 grid data.
    """
    try:
        # Birth datetime
        bd = parse_date(payload.date)
        bparts = payload.time.split(":")
        birth_dt = datetime(bd.year, bd.month, bd.day, int(bparts[0]), int(bparts[1]))

        # Transit date + time
        td = parse_date(payload.target_date)
        tt = (payload.target_time or "12:00").split(":")
        transit_dt = datetime(td.year, td.month, td.day, int(tt[0]), int(tt[1]))

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        result = generate_sbc(birth_dt, transit_dt, lat, lon, tz, payload.ayanamsa)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        print(f"SBC ERROR:\n{tb}", flush=True)
        raise HTTPException(400, f"{str(e)} | TRACE: {tb[-500:]}")
