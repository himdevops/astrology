"""
astro_events module — Astrological Events endpoints.
9 event types: Combustion, Retrograde, Transit, Positions,
Mutual Aspects, Lunar Aspects, Mutual Parallel, Ecliptic Crossings, Graha Yuddha.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.astro_events import calculate_astro_events

router = APIRouter(tags=["v3.0 — Astro Events"])


# ── schemas ───────────────────────────────────────────────────

class AstroEventsInput(BaseModel):
    start_date: str = Field(..., example="2026-05-01",
        description="Start of date range (YYYY-MM-DD or DD-MM-YYYY)")
    end_date: str = Field(..., example="2026-06-01",
        description="End of date range (YYYY-MM-DD or DD-MM-YYYY)")
    ayanamsa: str = Field(default="lahiri", example="lahiri")
    timezone_offset_minutes: int = Field(default=330,
        description="Timezone offset in minutes (default: IST +5:30 = 330)")


def _parse_date(date_str: str) -> datetime:
    """Parse date string in multiple formats."""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or DD-MM-YYYY")


# ── endpoint ─────────────────────────────────────────────────

@router.post("/astro-events", summary="Astrological Events — All 9 Event Types")
def astro_events(payload: AstroEventsInput):
    """
    Calculate all 9 types of astrological events over a date range:

    1. **Combustion** — planets within combustion orb of Sun
    2. **Retrograde** — retrograde start/end dates
    3. **Transits** — sign ingress events
    4. **Positions** — periodic position snapshots
    5. **Mutual Aspects** — Vedic graha drishti between planets
    6. **Lunar Aspects** — Moon's aspects to other planets
    7. **Mutual Parallel** — planets at same declination
    8. **Ecliptic Crossings** — planet latitude crosses 0°
    9. **Graha Yuddha** — planetary war (Tara Grahas within 1°)
    """
    try:
        start_dt = _parse_date(payload.start_date)
        end_dt = _parse_date(payload.end_date)

        if end_dt <= start_dt:
            raise ValueError(
                f"End date ({payload.end_date} → {end_dt.date()}) must be after "
                f"start date ({payload.start_date} → {start_dt.date()})"
            )

        diff_days = (end_dt - start_dt).days
        if diff_days > 365:
            raise ValueError("Maximum date range is 1 year for astro events")

        result = calculate_astro_events(
            start_date=start_dt,
            end_date=end_dt,
            ayanamsa=payload.ayanamsa,
            tz_offset_minutes=payload.timezone_offset_minutes,
        )

        return {
            "type": "astro_events",
            **result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{exc}\n{tb}") from exc
