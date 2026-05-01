"""
prediction module — Autonomous NSE/BSE Market Prediction endpoint.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models import resolve_chart
from app.core import (
    resolve_location_and_time,
    to_julian_day_utc,
    calculate_planets,
    calculate_ascendant,
)
from app.dasha import calculate_vimshottari_dasha, get_current_dasha
from app.yoga_detector import detect_all_yogas
from app.transit_alerts import generate_transit_alerts
from app.prediction_engine import generate_market_prediction

router = APIRouter(tags=["Prediction"])


# ── schemas ───────────────────────────────────────────────────

class FullPredictionInput(BaseModel):
    """Combines transit data + optional natal chart for personalized prediction."""
    # Transit
    transit_date: str  = Field(...,  example="2026-04-15")
    transit_time: str  = Field(default="09:15")
    transit_place: str = Field(default="Mumbai, Maharashtra, India")
    transit_latitude:  Optional[float] = Field(default=None)
    transit_longitude: Optional[float] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")
    days_ahead: int = Field(default=90, ge=7, le=365)
    # Optional natal
    natal_name:  Optional[str]   = Field(default=None)
    natal_date:  Optional[str]   = Field(default=None)
    natal_time:  Optional[str]   = Field(default=None)
    natal_place: Optional[str]   = Field(default=None)
    natal_latitude:  Optional[float] = Field(default=None)
    natal_longitude: Optional[float] = Field(default=None)

    # Compatibility aliases so resolve_chart can treat this like a TransitDataInput
    @property
    def date(self) -> str:
        return self.transit_date

    @property
    def time(self) -> str:
        return self.transit_time

    @property
    def place(self) -> str:
        return self.transit_place

    @property
    def latitude(self) -> Optional[float]:
        return self.transit_latitude

    @property
    def longitude(self) -> Optional[float]:
        return self.transit_longitude

    @property
    def timezone_offset_minutes(self) -> Optional[int]:
        return None


# ── endpoints ─────────────────────────────────────────────────

@router.post("/predict", summary="Autonomous NSE/BSE Market Prediction")
def predict(payload: FullPredictionInput):
    """
    Combines ALL signals: planetary positions, Moon nakshatra, Dasha,
    Yogas, transit alerts, and retrogrades into a single BUY/SELL signal
    with 7-day outlook and sector recommendations.
    """
    try:
        data = resolve_chart(payload, need_ascendant=False)

        transit_alert_data = generate_transit_alerts(
            data.planets, None, None,
            data.local_dt, payload.days_ahead, payload.ayanamsa,
        )

        current_dasha_data = None
        yoga_data = None
        natal_chart_data = None

        if all([payload.natal_date, payload.natal_time, payload.natal_place]):
            nr, ndt = resolve_location_and_time(
                place=payload.natal_place,
                date_str=payload.natal_date,
                time_str=payload.natal_time,
                latitude=payload.natal_latitude,
                longitude=payload.natal_longitude,
                timezone_offset_minutes=None,
            )
            njd = to_julian_day_utc(ndt, nr.timezone_offset_minutes)
            natal_planets = calculate_planets(njd, payload.ayanamsa)
            natal_ascendant = calculate_ascendant(
                njd, nr.latitude, nr.longitude, payload.ayanamsa,
            )

            moon = next((p for p in natal_planets if p["planet"] == "Moon"), None)
            if moon:
                dasha_full = calculate_vimshottari_dasha(moon["longitude"], ndt)
                current_dasha_data = get_current_dasha(dasha_full, data.local_dt)

            yoga_data = detect_all_yogas(natal_planets, natal_ascendant)
            natal_chart_data = {
                "date": payload.natal_date,
                "place": nr.place,
                "ascendant": natal_ascendant,
                "planets": natal_planets,
            }

        prediction = generate_market_prediction(
            current_planets=data.planets,
            current_date=data.local_dt,
            current_dasha=current_dasha_data,
            yoga_data=yoga_data,
            transit_data=transit_alert_data,
            natal_chart=natal_chart_data,
        )

        return {
            "type": "full_market_prediction",
            "prediction_date": payload.transit_date,
            "market": "NSE/BSE India",
            "current_planets": data.planets,
            "natal_chart": natal_chart_data,
            "transit_alerts": transit_alert_data,
            "prediction": prediction,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
