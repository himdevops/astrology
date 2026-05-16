"""Hora (Planetary Hour) & Auspicious Time API routes."""
from __future__ import annotations

import traceback
from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas import HoraInput
from core.utils import parse_date
from core.cities import resolve_city
from modules.hora import generate_hora_analysis

router = APIRouter(prefix="/api/v1/hora", tags=["Hora & Auspicious Time"])


@router.post("", summary="Hora + Auspicious Time Analysis")
def hora_analysis(payload: HoraInput):
    """
    Generate Hora table with auspiciousness scoring.
    Combines Hora lords, Transit Navtara (from birth Moon),
    Ashtakavarga BAV scores, and Chaughadiya for each time slot.
    """
    try:
        # Birth datetime
        bd = parse_date(payload.date)
        bparts = payload.time.split(":")
        birth_dt = datetime(bd.year, bd.month, bd.day, int(bparts[0]), int(bparts[1]))

        # Target date
        td = parse_date(payload.target_date)
        target_dt = datetime(td.year, td.month, td.day, 6, 0)  # 6 AM for sunrise calc

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        result = generate_hora_analysis(birth_dt, target_dt, lat, lon, tz, payload.ayanamsa)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        print(f"HORA ERROR:\n{tb}", flush=True)
        raise HTTPException(400, f"{str(e)} | TRACE: {tb[-500:]}")
