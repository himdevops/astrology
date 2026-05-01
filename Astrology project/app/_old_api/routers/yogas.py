from fastapi import APIRouter, HTTPException

from app.chart_service import calculate_yogas, calculate_transit_alerts, calculate_full_prediction
from app.schemas import YogaInput, TransitAlertInput, FullPredictionInput

router = APIRouter()


@router.post('/yogas', tags=['Yogas'], summary='Financial Yoga Detection')
def yogas(payload: YogaInput) -> dict:
    try:
        return calculate_yogas(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/transit-alerts', tags=['Alerts'], summary='NSE/BSE Transit Alert System')
def transit_alerts(payload: TransitAlertInput) -> dict:
    try:
        return calculate_transit_alerts(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post('/predict', tags=['Prediction'], summary='Autonomous NSE/BSE Market Prediction')
def predict(payload: FullPredictionInput) -> dict:
    try:
        return calculate_full_prediction(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
