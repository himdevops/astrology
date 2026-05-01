from fastapi import APIRouter, HTTPException

from app.chart_service import (
    calculate_birth_chart,
    calculate_transits,
    calculate_dasha,
    calculate_divisional,
    calculate_sarvatobhadra,
)
from app.schemas import (
    BirthInput,
    TransitInput,
    DashaInput,
    DivisionalInput,
    SarvatobhadraInput,
)

router = APIRouter()


@router.post('/chart', tags=['Charts'], summary='Birth Chart with Nakshatras')
def chart(payload: BirthInput) -> dict:
    try:
        return calculate_birth_chart(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/transits', tags=['Charts'], summary='Current Transit Positions + Moon Signal')
def transits(payload: TransitInput) -> dict:
    try:
        return calculate_transits(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/dasha', tags=['Dasha'], summary='Vimshottari Dasha Tree (Maha/Antar/Pratyantar)')
def dasha(payload: DashaInput) -> dict:
    try:
        return calculate_dasha(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/divisional', tags=['Charts'], summary='Divisional Charts D2/D9/D10')
def divisional(payload: DivisionalInput) -> dict:
    try:
        return calculate_divisional(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/sarvatobhadra', tags=['Charts'], summary='Sarvatobhadra Chakra Casting')
def sarvatobhadra(payload: SarvatobhadraInput) -> dict:
    try:
        return calculate_sarvatobhadra(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
