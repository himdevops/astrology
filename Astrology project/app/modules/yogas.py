"""
yogas module — Financial Yoga Detection endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import BirthDataInput, resolve_chart
from app.yoga_detector import detect_all_yogas

router = APIRouter(tags=["Yogas"])


# ── endpoints ─────────────────────────────────────────────────

@router.post("/yogas", summary="Financial Yoga Detection")
def yogas(payload: BirthDataInput):
    """Detect Dhana, Raj, Pancha Mahapurusha, malefic yogas and more."""
    try:
        data = resolve_chart(payload)
        yoga_list = detect_all_yogas(data.planets, data.ascendant)
        return {
            "type": "yoga_detection",
            "name": payload.name,
            "birth_date": payload.date,
            "ayanamsa": payload.ayanamsa,
            "ascendant": data.ascendant,
            "planets": data.planets,
            "yogas": yoga_list,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
