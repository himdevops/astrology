from fastapi import APIRouter, HTTPException

from app.chart_service import calculate_shadbala_endpoint, calculate_bhava_chalit_endpoint
from app.schemas import ShadbalaInput, BhavaChalitInput

router = APIRouter()


@router.post('/shadbala', tags=['v3.0 — Advanced'], summary='Shadbala (Six-fold Planetary Strength)')
def shadbala(payload: ShadbalaInput) -> dict:
    try:
        return calculate_shadbala_endpoint(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/bhava-chalit', tags=['v3.0 — Advanced'], summary='Bhava Chalit Chart')
def bhava_chalit(payload: BhavaChalitInput) -> dict:
    try:
        return calculate_bhava_chalit_endpoint(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
