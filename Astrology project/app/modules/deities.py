"""
deities module — Divisional Chart Deity Analysis endpoints.
D3, D7, D9, D10, D12, D60 deity mappings + Dasha-Deity timeline.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import BirthDataInput, resolve_chart
from app.dasha import calculate_vimshottari_dasha, get_current_dasha
from app.deity_analysis import calculate_deity_analysis, build_dasha_deity_timeline

router = APIRouter(tags=["Deities"])


# ── schemas ───────────────────────────────────────────────────

class DeityInput(BirthDataInput):
    as_of_date: Optional[str] = Field(
        default=None, example="2026-04-15",
        description="Date to find current dasha-deity (defaults to today)",
    )
    years_to_show: int = Field(default=120, ge=10, le=120)


# ── endpoints ─────────────────────────────────────────────────

@router.post("/deities", summary="Divisional Deity Analysis (D3/D7/D9/D10/D12/D60)")
def deities(payload: DeityInput):
    """
    Full deity analysis across all divisional charts plus
    dasha-deity timeline integration for career, fortune, karma predictions.
    """
    try:
        data = resolve_chart(payload, need_houses=True)

        # Deity analysis for all divisional charts
        deity_data = calculate_deity_analysis(data.planets, data.ascendant)

        # Dasha calculation for timeline
        moon = next((p for p in data.planets if p["planet"] == "Moon"), None)
        if not moon:
            raise ValueError("Moon position not found in chart")

        dasha_data = calculate_vimshottari_dasha(
            moon["longitude"], data.local_dt, payload.years_to_show
        )

        # Current dasha
        as_of = (
            datetime.strptime(payload.as_of_date, "%Y-%m-%d")
            if payload.as_of_date else datetime.utcnow()
        )
        current = get_current_dasha(dasha_data, as_of)

        # Dasha-deity timeline
        dasha_deity_timeline = build_dasha_deity_timeline(
            dasha_data, data.planets, data.ascendant
        )

        return {
            "type": "deity_analysis",
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
            "deity_analysis": deity_data,
            "current_dasha": current,
            "dasha_deity_timeline": dasha_deity_timeline,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
