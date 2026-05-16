"""Advanced Ashtakavarga Predictions API — Book-based techniques (separate from existing)."""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.utils import parse_date
from core.cities import resolve_city
from modules.ashtakavarga_advanced import generate_advanced_ashtakavarga

router = APIRouter(prefix="/api/v1/ashtakavarga-advanced", tags=["Ashtakavarga Advanced"])


class AdvancedAshtakInput(BaseModel):
    """Input for advanced ashtakavarga predictions."""
    date: str = Field(..., example="23-09-1992", description="Birth date DD-MM-YYYY")
    time: str = Field(default="12:00", description="Birth time HH:MM")
    latitude: float = Field(default=23.1765)
    longitude: float = Field(default=75.7885)
    tz_offset: float = Field(default=5.5)
    city: Optional[str] = Field(default=None, description="City for coordinates")
    ayanamsa: str = Field(default="lahiri")
    transit_date: Optional[str] = Field(default=None, description="Transit date DD-MM-YYYY (default today)")
    forecast_days: int = Field(default=7, description="Number of days for weekly forecast (max 30)")


@router.post("", summary="Advanced Ashtakavarga Predictions (Book Techniques)")
def advanced_ashtakavarga(payload: AdvancedAshtakInput):
    """
    Generate advanced Ashtakavarga predictions from 'Secrets of Ashtakavarga':
    - Gantavya Rasi (advance effects before sign change)
    - Rekha Strength % (transit effectiveness)
    - Daily SAV Score (day quality rating)
    - Trikona Nakshatra Trouble (dangerous transit nakshatras)
    - Bhava Vulnerability (Saturn-based bhava damage)
    - Life Predictions (planet-specific significations)
    - Kaksha Fine Timing (exact degree ranges for results)
    - Weekly Forecast (multi-day SAV scores)
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

        forecast_days = min(max(payload.forecast_days, 1), 30)

        result = generate_advanced_ashtakavarga(
            birth_dt=dt,
            lat=lat,
            lon=lon,
            tz_offset=tz,
            ayanamsa=payload.ayanamsa,
            transit_date=transit_d,
            forecast_days=forecast_days,
        )
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
