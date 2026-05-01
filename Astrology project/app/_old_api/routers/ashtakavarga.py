from fastapi import APIRouter, HTTPException

from app.chart_service import calculate_ashtakavarga, calculate_strength_calendar
from app.schemas import AshtakavargaInput, StrengthCalendarInput

router = APIRouter()


@router.post('/ashtakavarga', tags=['Ashtakavarga'], summary='Ashtakavarga + Transit Date Predictions')
def ashtakavarga(payload: AshtakavargaInput) -> dict:
    try:
        return calculate_ashtakavarga(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/strength-calendar', tags=['Ashtakavarga'], summary='Daily/Monthly/Yearly Strength Calendar')
def strength_calendar(payload: StrengthCalendarInput) -> dict:
    try:
        return calculate_strength_calendar(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
