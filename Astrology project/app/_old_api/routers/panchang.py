from fastapi import APIRouter, HTTPException

from app.chart_service import calculate_panchang_endpoint, calculate_panchang_calendar_endpoint
from app.schemas import PanchangInput, PanchangCalendarInput

router = APIRouter()


@router.post('/panchang', tags=['v3.0 — Panchang'], summary='Daily Panchang with Muhurta')
def panchang(payload: PanchangInput) -> dict:
    try:
        return calculate_panchang_endpoint(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/panchang-calendar', tags=['v3.0 — Panchang'], summary='Multi-day Panchang Trading Calendar')
def panchang_calendar(payload: PanchangCalendarInput) -> dict:
    try:
        return calculate_panchang_calendar_endpoint(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
