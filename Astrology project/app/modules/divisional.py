"""
divisional module — Divisional Charts (D2/D3/D9/D10) endpoint.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import BirthDataInput, resolve_chart
from app.divisional import calculate_all_divisional

router = APIRouter(tags=["Charts"])


# ── schemas ───────────────────────────────────────────────────

class DivisionalInput(BirthDataInput):
    charts: List[str] = Field(
        default=["D2", "D9", "D10"],
        example=["D2", "D9", "D10"],
        description="Which divisional charts to compute: D2, D3, D9, D10",
    )


# ── endpoints ─────────────────────────────────────────────────

@router.post("/divisional", summary="Divisional Charts D2/D9/D10")
def divisional(payload: DivisionalInput):
    """D2 Hora (wealth), D3 Drekkana (partners), D9 Navamsha, D10 Dashamsha."""
    try:
        data = resolve_chart(payload)
        charts = calculate_all_divisional(data.planets, data.ascendant, payload.charts)
        return {
            "type": "divisional_charts",
            "name": payload.name,
            "birth_date": payload.date,
            "ayanamsa": payload.ayanamsa,
            "ascendant": data.ascendant,
            "charts": charts,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
