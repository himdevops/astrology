"""
kp module — Advanced KP (Krishnamurti Paddhati) System endpoint.
Full 4-step significator, cuspal sub-lord theory, promise/denial,
DBA matching, ruling planets, KP horary, and financial analysis.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import BirthDataInput, resolve_chart
from app.core import (
    resolve_location_and_time,
    to_julian_day_utc,
    calculate_planets,
    calculate_ascendant,
)
from app.kp_system import calculate_kp_analysis, calculate_current_ruling_planets, calculate_daily_moon_nl_sl_ssl
from app.dasha import calculate_vimshottari_dasha, get_current_dasha

router = APIRouter(tags=["v3.0 — KP System"])


# ── schemas ───────────────────────────────────────────────────

class KPAnalysisInput(BirthDataInput):
    ayanamsa: str = Field(default="krishnamurti")
    transit_date: Optional[str] = Field(
        default=None, example="2026-04-28",
        description="Transit date for Ruling Planets calculation",
    )
    transit_time: Optional[str] = Field(default="09:15")
    kp_horary_number: Optional[int] = Field(
        default=None, ge=1, le=249,
        description="KP Horary (Prashna) number 1–249",
    )


class CurrentRPInput(BirthDataInput):
    """Input for Current Ruling Planets — uses place for coordinates."""
    ayanamsa: str = Field(default="krishnamurti")
    rp_date: Optional[str] = Field(
        default=None, example="2026-05-02",
        description="Specific date for RP calculation (omit for current moment)",
    )
    rp_time: Optional[str] = Field(
        default=None, example="14:30",
        description="Specific time for RP calculation (omit for current moment)",
    )


# ── endpoints ─────────────────────────────────────────────────

@router.post("/kp", summary="Advanced KP (Krishnamurti Paddhati) Analysis")
def kp_analysis(payload: KPAnalysisInput):
    """
    Complete KP analysis with:
    - 4-step significator system (Star-of-Occupant → Occupant → Star-of-Lord → Lord)
    - Cuspal sub-lord theory with promise/denial verdicts
    - Planet signification table (sign-star-sub-subsub)
    - Rahu/Ketu agent analysis
    - Ruling Planets for event timing
    - DBA (Dasha-Bhukti-Antara) significator matching
    - KP Horary (optional)
    - Financial house group analysis
    """
    try:
        data = resolve_chart(payload, need_houses=True)

        # Transit data for Ruling Planets
        transit_planets = None
        transit_dt = None
        if payload.transit_date:
            tr, tdt = resolve_location_and_time(
                place=payload.place,
                date_str=payload.transit_date,
                time_str=payload.transit_time or "09:15",
                latitude=payload.latitude,
                longitude=payload.longitude,
                timezone_offset_minutes=payload.timezone_offset_minutes,
            )
            tjd = to_julian_day_utc(tdt, tr.timezone_offset_minutes)
            transit_planets = calculate_planets(tjd, payload.ayanamsa)
            transit_dt = tdt

        # Dasha data for DBA analysis
        moon = next((p for p in data.planets if p["planet"] == "Moon"), None)
        dasha_data = None
        current_dasha = None
        if moon:
            dasha_data = calculate_vimshottari_dasha(
                moon["longitude"], data.local_dt, 120
            )
            as_of = datetime.utcnow()
            current_dasha = get_current_dasha(dasha_data, as_of)

        # Full KP analysis
        kp_data = calculate_kp_analysis(
            data.planets,
            data.houses,
            data.ascendant,
            transit_planets,
            transit_dt,
            dasha_data,
            current_dasha,
            payload.kp_horary_number,
        )

        return {
            "type":          "kp_advanced",
            "name":          payload.name,
            "birth_date":    payload.date,
            "birth_time":    payload.time,
            "birth_place":   data.resolved.place,
            "ayanamsa":      payload.ayanamsa,
            "ascendant":     data.ascendant,
            "houses":        data.houses,
            "planets":       data.planets,
            "kp_analysis":   kp_data,
            "current_dasha": current_dasha,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/kp/current-rp", summary="Current Ruling Planets (Real-time)")
def current_ruling_planets(payload: CurrentRPInput):
    """
    Calculate Ruling Planets for the CURRENT moment at a given location.
    Uses real-time ascendant, Moon, and day lord.
    Returns the 7 standard RP sources used in KP prashna.
    """
    try:
        # Use specific date/time if provided, otherwise current moment
        if payload.rp_date and payload.rp_time:
            use_date = payload.rp_date
            use_time = payload.rp_time
            is_realtime = False
        else:
            now = datetime.utcnow()
            use_date = now.strftime("%Y-%m-%d")
            use_time = now.strftime("%H:%M")
            is_realtime = True

        res, local_dt = resolve_location_and_time(
            place=payload.place,
            date_str=use_date,
            time_str=use_time,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone_offset_minutes=payload.timezone_offset_minutes,
        )
        jd = to_julian_day_utc(local_dt, res.timezone_offset_minutes)
        current_planets = calculate_planets(jd, payload.ayanamsa)
        current_asc = calculate_ascendant(
            jd, res.latitude, res.longitude, payload.ayanamsa
        )

        rp_data = calculate_current_ruling_planets(
            current_planets, current_asc, local_dt
        )
        rp_data["place"] = res.place
        rp_data["coordinates"] = f"{res.latitude:.4f}N, {res.longitude:.4f}E"
        rp_data["timezone_offset"] = res.timezone_offset_minutes / 60
        rp_data["is_realtime"] = is_realtime
        rp_data["query_date"] = use_date
        rp_data["query_time"] = use_time

        return rp_data
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ── schemas ─ Daily Moon NL/SL/SSL ────────────────────────────

class DailyMoonNLInput(BirthDataInput):
    """Input for Daily Moon NL/SL/SSL timeline."""
    ayanamsa: str = Field(default="krishnamurti")
    query_date: Optional[str] = Field(
        default=None, example="2026-05-02",
        description="Date for Moon NL/SL/SSL timeline (default: today)",
    )
    query_time: Optional[str] = Field(
        default="00:00",
        description="Start time for the 24-hour timeline (default: 00:00)",
    )
    duration_hours: Optional[int] = Field(
        default=24, ge=1, le=72,
        description="Duration in hours (default: 24)",
    )


@router.post("/kp/daily-moon-nl", summary="Daily Moon NL/SL/SSL Timeline")
def daily_moon_nl_sl_ssl(payload: DailyMoonNLInput):
    """
    Calculate Moon's Nakshatra Lord (NL), Sub Lord (SL), and Sub-Sub Lord (SSL)
    minute-by-minute for an entire day (or custom duration).

    Returns a transition table showing when NL/SL/SSL changes — much more
    readable than 1440 individual rows. Each row shows the time range,
    duration, Moon position (DMS), sign, nakshatra, NL, SL, SSL, and KP number.
    """
    try:
        from datetime import timedelta

        # Resolve date/time
        use_date = payload.query_date
        if not use_date:
            use_date = datetime.utcnow().strftime("%Y-%m-%d")
        use_time = payload.query_time or "00:00"
        duration_min = (payload.duration_hours or 24) * 60

        res, local_dt = resolve_location_and_time(
            place=payload.place,
            date_str=use_date,
            time_str=use_time,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone_offset_minutes=payload.timezone_offset_minutes,
        )
        jd_start = to_julian_day_utc(local_dt, res.timezone_offset_minutes)

        # Calculate transitions
        transitions = calculate_daily_moon_nl_sl_ssl(
            jd_start, payload.ayanamsa, minutes=duration_min
        )

        # Add readable time strings to each transition
        tz_offset = res.timezone_offset_minutes
        for t in transitions:
            start_dt = local_dt + timedelta(minutes=t["start_minute"])
            end_dt = local_dt + timedelta(minutes=t["end_minute"])
            t["start_time"] = start_dt.strftime("%H:%M")
            t["end_time"] = end_dt.strftime("%H:%M")
            t["start_datetime"] = start_dt.strftime("%Y-%m-%d %H:%M")
            t["end_datetime"] = end_dt.strftime("%Y-%m-%d %H:%M")

        return {
            "type": "daily_moon_nl_sl_ssl",
            "query_date": use_date,
            "query_time": use_time,
            "duration_hours": payload.duration_hours or 24,
            "place": res.place,
            "coordinates": f"{res.latitude:.4f}N, {res.longitude:.4f}E",
            "timezone_offset": tz_offset / 60,
            "ayanamsa": payload.ayanamsa,
            "total_transitions": len(transitions),
            "transitions": transitions,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
