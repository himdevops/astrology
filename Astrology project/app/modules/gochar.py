"""
gochar module — Gochar (Transit) Panchang endpoints.
Planet transit dates, sign changes, nakshatra changes, pada changes, retro dates.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.gochar import calculate_gochar_transits

router = APIRouter(tags=["v3.0 — Gochar"])


# ── schemas ───────────────────────────────────────────────────

class GocharInput(BaseModel):
    start_date: str = Field(..., example="2026-05-01",
        description="Start of date range (YYYY-MM-DD or DD-MM-YYYY)")
    end_date: str = Field(..., example="2026-06-01",
        description="End of date range (YYYY-MM-DD or DD-MM-YYYY)")
    ayanamsa: str = Field(default="lahiri", example="lahiri")
    timezone_offset_minutes: int = Field(default=330,
        description="Timezone offset in minutes (default: IST +5:30 = 330)")
    planets: Optional[List[str]] = Field(default=None,
        description="Filter to specific planets (default: all 9 + Lagna)")
    latitude: Optional[float] = Field(default=None, example=28.6139,
        description="Latitude for Lagna calculation (required if Lagna included)")
    longitude: Optional[float] = Field(default=None, example=77.2090,
        description="Longitude for Lagna calculation (required if Lagna included)")


def _parse_date(date_str: str) -> datetime:
    """Parse date string in multiple formats."""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or DD-MM-YYYY")


@router.post("/gochar/transits", summary="Gochar Panchang — All Planet Transit Events")
def gochar_transits(payload: GocharInput):
    """
    Calculate all planet transit events over a date range.

    Returns chronological list of:
    - **Sign changes** — when a planet enters a new rashi
    - **Nakshatra changes** — when a planet enters a new nakshatra
    - **Pada changes** — when a planet moves to next pada within a nakshatra
    - **Retrograde start/end** — when a planet goes retrograde or direct

    Also returns current planet positions at the start date and per-planet summaries.
    """
    try:
        start_dt = _parse_date(payload.start_date)
        end_dt = _parse_date(payload.end_date)

        if end_dt <= start_dt:
            raise ValueError("End date must be after start date")

        # Limit range to 100 years max
        diff_days = (end_dt - start_dt).days
        if diff_days > 36525:
            raise ValueError("Maximum date range is 100 years")

        result = calculate_gochar_transits(
            start_date=start_dt,
            end_date=end_dt,
            ayanamsa=payload.ayanamsa,
            tz_offset_minutes=payload.timezone_offset_minutes,
            planets_filter=payload.planets,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )

        return {
            "type": "gochar_transits",
            **result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{exc}\n{tb}") from exc
