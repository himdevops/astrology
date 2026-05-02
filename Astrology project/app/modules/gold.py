"""
gold module — Gold Price Prediction endpoints.
Vedic astrology-based gold price direction prediction.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.gold_predictor import predict_gold

router = APIRouter(tags=["v3.0 — Gold Prediction"])


class GoldInput(BaseModel):
    start_date: str = Field(..., example="2026-05-01",
        description="Start of date range (YYYY-MM-DD or DD-MM-YYYY)")
    end_date: str = Field(..., example="2026-06-01",
        description="End of date range (YYYY-MM-DD or DD-MM-YYYY)")
    ayanamsa: str = Field(default="lahiri", example="lahiri")
    timezone_offset_minutes: int = Field(default=330,
        description="Timezone offset in minutes (default: IST +5:30 = 330)")


def _parse_date(date_str: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or DD-MM-YYYY")


@router.post("/gold/predict", summary="Gold Price Prediction — Vedic Astrology")
def gold_predict(payload: GoldInput):
    """
    Predict gold price direction over a date range using Vedic astrology rules.

    Based on Sarvatobhadra Chakra Ardha Prakaran (Khemraj Publishers):
    - **Papa-Shubha Vedha** (Shlokas 245-246) — malefic vedha = gold expensive
    - **Nakshatra Commodity Map** (Shlokas 379-406) — per-nakshatra gold triggers
    - **Jupiter Sankranti** (Shloka 349) — new commodity year cycle
    - **Graha Bala** (Shlokas 358-360) — planet strength for vedha weight
    - **Retrograde effects** (Shloka 337, 359) — retro benefic = gold rises
    - **Moon daily signal** — Moon nakshatra sentiment
    - **Ksheena Chandra** — waning Moon = fear = gold demand

    Returns daily signals (score/direction), transit events, and rule breakdown.
    """
    try:
        start_dt = _parse_date(payload.start_date)
        end_dt = _parse_date(payload.end_date)

        if end_dt <= start_dt:
            raise ValueError("End date must be after start date")

        diff_days = (end_dt - start_dt).days
        if diff_days > 36525:
            raise ValueError("Maximum date range is 100 years")

        result = predict_gold(
            start_date=start_dt,
            end_date=end_dt,
            ayanamsa=payload.ayanamsa,
            tz_offset_minutes=payload.timezone_offset_minutes,
        )

        return {
            "type": "gold_prediction",
            **result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{exc}\n{tb}") from exc
