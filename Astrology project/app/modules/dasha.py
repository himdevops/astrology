"""
dasha module — Vimshottari Dasha endpoint.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import BirthDataInput, resolve_chart
from app.dasha import calculate_vimshottari_dasha, get_current_dasha

router = APIRouter(tags=["Dasha"])


# ── schemas ───────────────────────────────────────────────────

class DashaInput(BirthDataInput):
    as_of_date: Optional[str] = Field(
        default=None, example="2026-04-15",
        description="Date to find current dasha (defaults to today)",
    )
    years_to_show: int = Field(default=120, ge=10, le=120)


# ── endpoints ─────────────────────────────────────────────────

@router.post("/dasha", summary="Vimshottari Dasha Tree (Maha/Antar/Pratyantar)")
def dasha(payload: DashaInput):
    """Full Vimshottari Dasha with exact dates and financial implications."""
    try:
        data = resolve_chart(payload, need_ascendant=False)
        moon = next((p for p in data.planets if p["planet"] == "Moon"), None)
        if not moon:
            raise ValueError("Moon position not found in chart")

        dasha_data = calculate_vimshottari_dasha(
            moon["longitude"], data.local_dt, payload.years_to_show
        )
        as_of = (
            datetime.strptime(payload.as_of_date, "%Y-%m-%d")
            if payload.as_of_date else datetime.utcnow()
        )
        current = get_current_dasha(dasha_data, as_of)

        return {
            "type": "vimshottari_dasha",
            "name": payload.name,
            "birth_date": payload.date,
            "birth_time": payload.time,
            "birth_place": data.resolved.place,
            "ayanamsa": payload.ayanamsa,
            "dasha_data": dasha_data,
            "current_dasha": current,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
