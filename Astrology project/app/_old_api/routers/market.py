from fastapi import APIRouter, HTTPException

from app.chart_service import get_market_prices_endpoint, get_sector_perf_endpoint
from app.schemas import MarketDataInput

router = APIRouter()


@router.post('/market/prices', tags=['v3.0 — Market Data'], summary='Live NSE/BSE Prices')
def market_prices(payload: MarketDataInput) -> dict:
    try:
        return get_market_prices_endpoint(payload.indices)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get('/market/sectors', tags=['v3.0 — Market Data'], summary='Sector Performance')
def sector_performance(period: str = '1mo') -> dict:
    try:
        return get_sector_perf_endpoint(period)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
