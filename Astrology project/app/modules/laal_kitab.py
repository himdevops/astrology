"""
laal_kitab module — Laal Kitab (Red Book) Prediction endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import BirthDataInput, resolve_chart
from app.laal_kitab import calculate_laal_kitab_analysis
from app.nakshatra_predictions import calculate_nakshatra_analysis

router = APIRouter(tags=["v3.0 — Laal Kitab"])


# ── endpoints ─────────────────────────────────────────────────

@router.post("/laal-kitab", summary="Laal Kitab Full Analysis")
def laal_kitab(payload: BirthDataInput):
    """
    Complete Laal Kitab analysis including planet-in-house predictions,
    planetary debts (Rins), sleeping/blind/awake states, remedies,
    and house-wise summary using Kaalpurush Kundli.
    """
    try:
        data = resolve_chart(payload, need_houses=True)
        analysis = calculate_laal_kitab_analysis(data.planets, data.ascendant)
        return {
            **analysis,
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
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/nakshatra-predictions", summary="Nakshatra-Planet Deep Predictions")
def nakshatra_predictions(payload: BirthDataInput):
    """
    Advanced Nakshatra analysis: planet-in-nakshatra personality, events,
    career, relationship, health, financial, spiritual predictions.
    Multi-planet nakshatra effects and pada analysis.
    """
    try:
        data = resolve_chart(payload, need_houses=True)
        analysis = calculate_nakshatra_analysis(data.planets, data.ascendant)
        return {
            **analysis,
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
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
