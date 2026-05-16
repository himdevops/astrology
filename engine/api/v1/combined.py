"""Combined: All events for a single date in one call."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.schemas import AllEventsInput
from core.panchang import get_panchang
from core.utils import parse_date
from modules.positions import get_daily_positions
from modules.retrograde import get_daily_status as retro_daily
from modules.combustion import check_daily as combustion_daily
from modules.aspects import get_daily as aspects_daily
from modules.lunar_aspects import get_daily as lunar_daily
from modules.parallels import get_daily as parallels_daily
from modules.ecliptic import get_daily as ecliptic_daily
from modules.graha_yuddha import check_daily as yuddha_daily

router = APIRouter(prefix="/api/v1", tags=["Combined"])


@router.post("/all-events", summary="All Events for a Date")
def all_events(payload: AllEventsInput):
    """Complete astrological snapshot: Panchang + all 9 event modules."""
    try:
        d = parse_date(payload.date)
        parts = payload.time.split(":")
        dt = datetime(d.year, d.month, d.day, int(parts[0]), int(parts[1]))

        return {
            "date": payload.date,
            "panchang": get_panchang(dt, payload.latitude, payload.longitude, payload.tz_offset, payload.ayanamsa).to_dict(),
            "positions": get_daily_positions(d, payload.tz_offset, payload.ayanamsa),
            "retrograde": retro_daily(d, payload.tz_offset, payload.ayanamsa),
            "combustion": combustion_daily(d, payload.tz_offset, payload.ayanamsa),
            "aspects": aspects_daily(d, payload.tz_offset, payload.ayanamsa),
            "lunar_aspects": lunar_daily(d, payload.tz_offset, payload.ayanamsa),
            "parallels": parallels_daily(d, payload.tz_offset, payload.ayanamsa),
            "ecliptic": ecliptic_daily(d, payload.tz_offset, payload.ayanamsa),
            "graha_yuddha": yuddha_daily(d, payload.tz_offset, payload.ayanamsa),
        }
    except Exception as e:
        raise HTTPException(400, str(e))
