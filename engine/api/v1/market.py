"""Moon Market Analysis API — NSE/BSE Astrology Trading Signals."""
from __future__ import annotations

import traceback
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from core.utils import parse_date
from core.cities import resolve_city
from modules.market import generate_market_analysis, generate_trend_scan

router = APIRouter(prefix="/api/v1/market", tags=["Market Analysis"])


class MarketInput(BaseModel):
    """Market analysis input."""
    date: str = Field(..., example="16-05-2026", description="Analysis date DD-MM-YYYY")
    time: str = Field(default="09:15", description="Analysis time HH:MM (default 9:15 AM)")
    city: Optional[str] = Field(default="Mumbai", description="City for timezone")
    tz_offset: float = Field(default=5.5, description="Hours from UTC")
    ayanamsa: str = Field(default="lahiri")


class MarketDualInput(BaseModel):
    """Dual market analysis input with custom session times."""
    date: str = Field(..., example="16-05-2026", description="Analysis date DD-MM-YYYY")
    time1: str = Field(default="09:15", description="Session 1 time HH:MM")
    time2: str = Field(default="13:15", description="Session 2 time HH:MM")
    city: Optional[str] = Field(default="Mumbai", description="City for timezone")
    tz_offset: float = Field(default=5.5, description="Hours from UTC")
    ayanamsa: str = Field(default="lahiri")


class TrendScanInput(BaseModel):
    """Intraday trend scan input."""
    date: str = Field(..., example="16-05-2026", description="Scan date DD-MM-YYYY")
    start_time: str = Field(default="09:15", description="Scan start HH:MM")
    end_time: str = Field(default="17:00", description="Scan end HH:MM")
    interval: int = Field(default=15, description="Scan interval in minutes (15, 30, 60)")
    city: Optional[str] = Field(default="Mumbai", description="City for timezone")
    tz_offset: float = Field(default=5.5, description="Hours from UTC")
    ayanamsa: str = Field(default="lahiri")


@router.post("", summary="Moon Market Analysis for NSE/BSE")
def market_analysis(payload: MarketInput):
    """
    Generate Moon-based market analysis for trading signals.
    """
    try:
        bd = parse_date(payload.date)
        tparts = payload.time.split(":")
        analysis_dt = datetime(
            bd.year, bd.month, bd.day,
            int(tparts[0]), int(tparts[1])
        )

        tz = payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                tz = loc.tz_offset

        result = generate_market_analysis(
            analysis_dt=analysis_dt,
            tz=tz,
            ayanamsa=payload.ayanamsa,
        )
        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dual", summary="Market Analysis for two sessions")
def market_dual_analysis(payload: MarketDualInput):
    """
    Generate analysis for two custom session times.
    """
    try:
        bd = parse_date(payload.date)

        tz = payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                tz = loc.tz_offset

        t1 = payload.time1.split(":")
        t2 = payload.time2.split(":")
        dt1 = datetime(bd.year, bd.month, bd.day, int(t1[0]), int(t1[1]))
        dt2 = datetime(bd.year, bd.month, bd.day, int(t2[0]), int(t2[1]))

        session1 = generate_market_analysis(analysis_dt=dt1, tz=tz, ayanamsa=payload.ayanamsa)
        session2 = generate_market_analysis(analysis_dt=dt2, tz=tz, ayanamsa=payload.ayanamsa)

        return {
            "date": payload.date,
            "session1": session1,
            "session1_time": payload.time1,
            "session2": session2,
            "session2_time": payload.time2,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends", summary="Intraday Trend Change Scanner (Ardha Prahara)")
def market_trend_scan(payload: TrendScanInput):
    """
    Scan through the trading day at regular intervals to detect
    when Moon-based market signal changes direction (trend reversal).
    Identifies exact times when vedha shifts from bullish to bearish
    or vice versa.
    """
    try:
        bd = parse_date(payload.date)

        tz = payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                tz = loc.tz_offset

        st = payload.start_time.split(":")
        et = payload.end_time.split(":")

        result = generate_trend_scan(
            date_dt=datetime(bd.year, bd.month, bd.day),
            tz=tz,
            ayanamsa=payload.ayanamsa,
            start_hour=int(st[0]), start_min=int(st[1]),
            end_hour=int(et[0]), end_min=int(et[1]),
            interval_min=payload.interval,
        )
        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
