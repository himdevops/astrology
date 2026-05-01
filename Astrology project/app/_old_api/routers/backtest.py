from fastapi import APIRouter, HTTPException

from app.chart_service import run_backtest_endpoint
from app.schemas import BacktestInput

router = APIRouter()


@router.post('/backtest', tags=['v3.0 — Backtesting'], summary='Backtest Astrology Signals')
def backtest(payload: BacktestInput) -> dict:
    try:
        return run_backtest_endpoint(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
