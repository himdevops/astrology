"""
shadbala module — Shadbala (Six-fold Strength) + Bhava Chalit endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import BirthDataInput, resolve_chart
from app.shadbala import calculate_shadbala, calculate_bhava_chalit

router = APIRouter(tags=["v3.0 — Advanced"])


# ── endpoints ─────────────────────────────────────────────────

@router.post("/shadbala", summary="Shadbala (Six-fold Planetary Strength)")
def shadbala(payload: BirthDataInput):
    """
    All 6 Shadbala components: Sthana, Dig, Kala, Cheshta, Naisargika,
    Drig Bala.  Returns total Rupas and NSE/BSE sector confidence.
    """
    try:
        data = resolve_chart(payload)
        result = calculate_shadbala(
            data.planets, data.ascendant, data.local_dt, data.resolved.latitude,
        )
        return {
            "type": "shadbala",
            "name": payload.name,
            "birth_date": payload.date,
            "ayanamsa": payload.ayanamsa,
            "ascendant": data.ascendant,
            "shadbala": result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/bhava-chalit", summary="Bhava Chalit Chart")
def bhava_chalit(payload: BirthDataInput):
    """
    Bhava Chalit — actual house placement vs sign placement using
    Bhava Madhya midpoint system.  Shows shifted planets.
    """
    try:
        data = resolve_chart(payload, need_houses=True)
        chalit = calculate_bhava_chalit(data.planets, data.houses, data.ascendant)
        return {
            "type": "bhava_chalit",
            "name": payload.name,
            "birth_date": payload.date,
            "ayanamsa": payload.ayanamsa,
            "ascendant": data.ascendant,
            "bhava_chalit": chalit,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
