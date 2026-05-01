"""
kaksha module — Advanced Kaksha Ashtakavarga endpoints.
Prastara-style bindu timing, hourly Moon Kaksha windows,
and multi-day timeline analysis.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import BirthDataInput
from app.kaksha_engine import daily_kaksha_analysis, timeline_analysis

router = APIRouter(tags=["v3.0 — Kaksha Ashtakavarga"])


# ── schemas ───────────────────────────────────────────────────

class KakshaInput(BirthDataInput):
    """Daily Kaksha analysis — natal AV + transit scoring + hourly Moon."""
    transit_date: Optional[str] = Field(default=None, example="2026-04-28")
    transit_time: str = Field(default="09:15")
    transit_place: str = Field(default="Mumbai, Maharashtra, India")


class KakshaTimelineInput(BirthDataInput):
    """Multi-day Kaksha timeline for best/worst trading days."""
    transit_date: Optional[str] = Field(
        default=None, example="2026-04-28",
        description="Start date (defaults to today)",
    )
    transit_place: str = Field(default="Mumbai, Maharashtra, India")
    days: int = Field(default=30, ge=1, le=90)


# ── endpoints ─────────────────────────────────────────────────

@router.post("/kaksha/daily", summary="Daily Kaksha Ashtakavarga Analysis")
def kaksha_daily(payload: KakshaInput):
    """
    Advanced Kaksha Ashtakavarga for a given day:

    - Full BAV/SAV with Prastara matrices
    - Per-planet Kaksha window scoring (bindu, dignity, BAV, SAV)
    - Hourly Moon Kaksha windows (6 AM — midnight)
    - Best 3 / Worst 3 trading windows
    - Overall day quality signal
    """
    try:
        return daily_kaksha_analysis(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/kaksha/timeline", summary="Multi-day Kaksha Timeline")
def kaksha_timeline(payload: KakshaTimelineInput):
    """
    Multi-day Kaksha timeline analysis:

    - Daily scores for each day in the range
    - Best / worst planets per day
    - Moon Kaksha quality per day
    - Top 5 best and worst trading days
    """
    try:
        return timeline_analysis(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
