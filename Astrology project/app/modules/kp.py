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
from zoneinfo import ZoneInfo

from app.core import (
    resolve_location_and_time,
    to_julian_day_utc,
    calculate_planets,
    calculate_ascendant,
    geocode_place,
    resolve_timezone_name,
)
from app.kp_system import (
    calculate_kp_analysis, calculate_current_ruling_planets,
    calculate_daily_moon_nl_sl_ssl, calculate_prashna_yesno,
    calculate_match_prediction, calculate_toss_prediction,
    calculate_cuspal_sublords, calculate_significators,
    build_planet_signification_table, find_dba_timing_windows,
    check_event_promise,
    PRASHNA_QUESTIONS, MATCH_CATEGORIES,
)
from app.dasha import calculate_vimshottari_dasha, get_current_dasha

router = APIRouter(tags=["v3.0 — KP System"])


def _local_now(place: str, latitude=None, longitude=None):
    """
    Get the current LOCAL date/time at a given place.
    Returns (date_str, time_str) in 'YYYY-MM-DD' and 'HH:MM' format.
    MUST be used instead of datetime.utcnow() when the result is passed
    to resolve_location_and_time (which treats it as local time).
    """
    lat, lon = latitude, longitude
    if lat is None or lon is None:
        lat, lon, _ = geocode_place(place)
    tz_name = resolve_timezone_name(lat, lon)
    now = datetime.now(ZoneInfo(tz_name))
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")


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
        transit_asc = None
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
            transit_asc = calculate_ascendant(
                tjd, tr.latitude, tr.longitude, payload.ayanamsa
            )
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

        # Full KP analysis (pass transit ascendant for RP calculation)
        kp_data = calculate_kp_analysis(
            data.planets,
            data.houses,
            data.ascendant,
            transit_planets,
            transit_dt,
            dasha_data,
            current_dasha,
            payload.kp_horary_number,
            transit_ascendant=transit_asc,
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
        # Use specific date/time if provided, otherwise current LOCAL moment
        if payload.rp_date and payload.rp_time:
            use_date = payload.rp_date
            use_time = payload.rp_time
            is_realtime = False
        else:
            use_date, use_time = _local_now(
                payload.place, payload.latitude, payload.longitude
            )
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
            use_date, _ = _local_now(
                payload.place, payload.latitude, payload.longitude
            )
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


# ── schemas ─ Prashna Yes/No ────────────────────────────────

class PrashnaYesNoInput(BirthDataInput):
    """Input for KP Prashna Yes/No system."""
    ayanamsa: str = Field(default="krishnamurti")
    kp_number: int = Field(
        ..., ge=1, le=249,
        description="KP Horary number 1–249 (querent's number)",
    )
    question_type: str = Field(
        ..., example="marriage",
        description="Question category — marriage, wealth, job, speculation, etc.",
    )
    query_date: Optional[str] = Field(
        default=None, example="2026-05-02",
        description="Date of query for Ruling Planets (default: current moment)",
    )
    query_time: Optional[str] = Field(
        default=None, example="14:30",
        description="Time of query for Ruling Planets",
    )


@router.post("/kp/prashna-yesno", summary="KP Prashna Yes/No with RP Matching")
def prashna_yesno(payload: PrashnaYesNoInput):
    """
    Advanced KP Prashna (Horary) system that gives a clear YES / NO answer.

    Process:
    1. KP number (1-249) sets the horary ascendant
    2. Erect chart for query moment (date/time/place)
    3. Check cuspal sub-lord of the primary house for the question type
    4. Determine if sub-lord signifies conductive or detrimental houses
    5. Compute Ruling Planets at query moment
    6. Cross-match significators with RP → fruitful significators
    7. Check retrograde status of sub-lord and its star lord
    8. Return clear YES / NO verdict with detailed reasoning
    """
    try:
        data = resolve_chart(payload, need_houses=True)

        # Resolve query date/time for Ruling Planets
        if payload.query_date and payload.query_time:
            use_date = payload.query_date
            use_time = payload.query_time
        else:
            use_date, use_time = _local_now(
                payload.place, payload.latitude, payload.longitude
            )

        tr_res, tr_dt = resolve_location_and_time(
            place=payload.place,
            date_str=use_date,
            time_str=use_time,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone_offset_minutes=payload.timezone_offset_minutes,
        )
        tr_jd = to_julian_day_utc(tr_dt, tr_res.timezone_offset_minutes)
        transit_planets = calculate_planets(tr_jd, payload.ayanamsa)
        transit_asc = calculate_ascendant(
            tr_jd, tr_res.latitude, tr_res.longitude, payload.ayanamsa
        )

        # Cuspal sub-lords and significators for the chart
        cuspal = calculate_cuspal_sublords(data.houses)
        sig_data = calculate_significators(data.planets, data.houses, data.ascendant)
        planet_table = build_planet_signification_table(data.planets, sig_data, data.ascendant)

        # Run Prashna Yes/No
        result = calculate_prashna_yesno(
            kp_number=payload.kp_number,
            question_type=payload.question_type,
            planets=data.planets,
            houses=data.houses,
            ascendant=transit_asc,
            transit_planets=transit_planets,
            transit_datetime=tr_dt,
            significator_data=sig_data,
            cuspal_data=cuspal,
            planet_sig_table=planet_table,
        )

        return {
            "type":            "prashna_yesno",
            "name":            payload.name,
            "query_date":      use_date,
            "query_time":      use_time,
            "query_place":     tr_res.place,
            "ayanamsa":        payload.ayanamsa,
            "ascendant":       transit_asc,
            "houses":          data.houses,
            "planets":         data.planets,
            "prashna":         result,
            "available_questions": {k: v["label"] for k, v in PRASHNA_QUESTIONS.items()},
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ── schemas ─ Match Prediction ──────────────────────────────

class MatchPredictionInput(BirthDataInput):
    """Input for KP Match Prediction (Win/Lose)."""
    ayanamsa: str = Field(default="krishnamurti")
    kp_number: int = Field(
        ..., ge=1, le=249,
        description="KP Horary number 1–249",
    )
    match_type: str = Field(
        default="cricket", example="cricket",
        description="Type of match — cricket, football, tennis, etc.",
    )
    team_a: str = Field(
        default="Team A",
        description="Name of team you're asking about (querent's team)",
    )
    team_b: str = Field(
        default="Team B",
        description="Name of opponent team",
    )
    query_date: Optional[str] = Field(
        default=None, example="2026-05-02",
        description="Date of query for Ruling Planets",
    )
    query_time: Optional[str] = Field(
        default=None, example="14:30",
        description="Time of query for Ruling Planets",
    )


@router.post("/kp/match-prediction", summary="KP Match Prediction — Who Wins?")
def match_prediction(payload: MatchPredictionInput):
    """
    KP Horary Match Prediction using Ruling Planet theory.

    Who will WIN and who will LOSE in a competition:
    - H1 = Querent/Team A, H7 = Opponent/Team B
    - H6 sub-lord analysis → victory for querent
    - H12 sub-lord analysis → victory for opponent (6th from 7th)
    - H11 sub-lord → gains confirmation
    - Ruling Planets cross-validation
    - Retrograde checks on key sub-lords
    """
    try:
        data = resolve_chart(payload, need_houses=True)

        # Resolve query date/time for RP
        if payload.query_date and payload.query_time:
            use_date = payload.query_date
            use_time = payload.query_time
        else:
            use_date, use_time = _local_now(
                payload.place, payload.latitude, payload.longitude
            )

        tr_res, tr_dt = resolve_location_and_time(
            place=payload.place,
            date_str=use_date,
            time_str=use_time,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone_offset_minutes=payload.timezone_offset_minutes,
        )
        tr_jd = to_julian_day_utc(tr_dt, tr_res.timezone_offset_minutes)
        transit_planets = calculate_planets(tr_jd, payload.ayanamsa)
        transit_asc = calculate_ascendant(
            tr_jd, tr_res.latitude, tr_res.longitude, payload.ayanamsa
        )

        cuspal = calculate_cuspal_sublords(data.houses)
        sig_data = calculate_significators(data.planets, data.houses, data.ascendant)

        result = calculate_match_prediction(
            kp_number=payload.kp_number,
            planets=data.planets,
            houses=data.houses,
            ascendant=transit_asc,
            transit_planets=transit_planets,
            transit_datetime=tr_dt,
            significator_data=sig_data,
            cuspal_data=cuspal,
            team_a=payload.team_a,
            team_b=payload.team_b,
            match_type=payload.match_type,
        )

        return {
            "type":            "match_prediction",
            "name":            payload.name,
            "query_date":      use_date,
            "query_time":      use_time,
            "query_place":     tr_res.place,
            "ayanamsa":        payload.ayanamsa,
            "prediction":      result,
            "available_match_types": MATCH_CATEGORIES,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class TossPredictionInput(BirthDataInput):
    """Input for KP Toss Prediction."""
    ayanamsa: str = Field(default="krishnamurti")
    kp_number: int = Field(
        ..., ge=1, le=249,
        description="KP Horary number 1–249 (think while asking 'Who wins toss?')",
    )
    team_a: str = Field(
        default="Team A",
        description="Name of team you're asking about (querent's team)",
    )
    team_b: str = Field(
        default="Team B",
        description="Name of opponent team",
    )
    query_date: Optional[str] = Field(
        default=None, example="2026-05-02",
        description="Date of query for Ruling Planets",
    )
    query_time: Optional[str] = Field(
        default=None, example="14:30",
        description="Time of query for Ruling Planets",
    )


@router.post("/kp/toss-prediction", summary="KP Toss Prediction — Who Wins the Toss?")
def toss_prediction(payload: TossPredictionInput):
    """
    KP Horary Toss Prediction.

    Think of a SEPARATE KP number (1-249) while asking "Who will win the toss?"
    Uses 6th/12th cusp sub-lord analysis with 3-tier retrograde rules.
    """
    try:
        data = resolve_chart(payload, need_houses=True)

        if payload.query_date and payload.query_time:
            use_date = payload.query_date
            use_time = payload.query_time
        else:
            use_date, use_time = _local_now(
                payload.place, payload.latitude, payload.longitude
            )

        tr_res, tr_dt = resolve_location_and_time(
            place=payload.place,
            date_str=use_date,
            time_str=use_time,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone_offset_minutes=payload.timezone_offset_minutes,
        )
        tr_jd = to_julian_day_utc(tr_dt, tr_res.timezone_offset_minutes)
        transit_planets = calculate_planets(tr_jd, payload.ayanamsa)
        transit_asc = calculate_ascendant(
            tr_jd, tr_res.latitude, tr_res.longitude, payload.ayanamsa
        )

        cuspal = calculate_cuspal_sublords(data.houses)
        sig_data = calculate_significators(data.planets, data.houses, data.ascendant)

        result = calculate_toss_prediction(
            kp_number=payload.kp_number,
            planets=data.planets,
            houses=data.houses,
            ascendant=transit_asc,
            transit_planets=transit_planets,
            transit_datetime=tr_dt,
            significator_data=sig_data,
            cuspal_data=cuspal,
            team_a=payload.team_a,
            team_b=payload.team_b,
        )

        return {
            "type":            "toss_prediction",
            "name":            payload.name,
            "query_date":      use_date,
            "query_time":      use_time,
            "query_place":     tr_res.place,
            "ayanamsa":        payload.ayanamsa,
            "prediction":      result,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ── schemas ─ DBA Timing Finder ───────────────────────────────

class DBATimingInput(BirthDataInput):
    """Input for KP DBA Timing Finder — find best future windows for any event."""
    ayanamsa: str = Field(default="krishnamurti")
    question_type: str = Field(
        ..., example="marriage",
        description="Question category from PRASHNA_QUESTIONS",
    )
    mode: str = Field(
        default="natal", example="natal",
        description="'natal' uses birth chart, 'prashna' uses KP horary number",
    )
    kp_number: Optional[int] = Field(
        default=None, ge=1, le=249,
        description="KP Horary number 1–249 (required if mode='prashna')",
    )
    search_start_date: Optional[str] = Field(
        default=None, example="2026-05-01",
        description="Start of search window (default: today)",
    )
    search_end_date: Optional[str] = Field(
        default=None, example="2028-05-01",
        description="End of search window (default: 2 years from start)",
    )
    query_date: Optional[str] = Field(default=None, example="2026-05-02")
    query_time: Optional[str] = Field(default=None, example="14:30")
    validate_date: Optional[str] = Field(
        default=None, example="2023-05-28",
        description="Known event date to validate (DD-MM-YYYY or YYYY-MM-DD). Shows DBA analysis for this date.",
    )


# ── schemas ─ Event Promise Checker ─────────────────────────

class EventPromiseInput(BirthDataInput):
    """Input for KP Event Promise Checker."""
    ayanamsa: str = Field(default="krishnamurti")
    question_type: str = Field(
        ..., example="marriage",
        description="Question category from PRASHNA_QUESTIONS",
    )


@router.post("/kp/event-promise", summary="KP Event Promise Checker — Does the chart promise the event?")
def event_promise(payload: EventPromiseInput):
    """
    Check if a natal chart has the PROMISE of a specific event using
    KP 3-way sub-lord theory.

    Checks the primary house cusp sub-lord, its star lord, and its sub-lord
    to determine if the chart supports the event.

    This is separate from DBA timing — this answers IF, DBA answers WHEN.
    """
    try:
        data = resolve_chart(payload, need_houses=True)

        cuspal = calculate_cuspal_sublords(data.houses)
        sig_data = calculate_significators(data.planets, data.houses, data.ascendant)

        result = check_event_promise(
            question_type=payload.question_type,
            planets=data.planets,
            houses=data.houses,
            ascendant=data.ascendant,
            cuspal_data=cuspal,
            significator_data=sig_data,
        )

        return {
            "type":               "event_promise",
            "name":               payload.name,
            "ayanamsa":           payload.ayanamsa,
            "birth_date":         payload.date,
            "question_type":      payload.question_type,
            "promise":            result,
            "available_questions": {k: v["label"] for k, v in PRASHNA_QUESTIONS.items()},
        }
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{exc}\n{tb}") from exc


@router.post("/kp/dba-timing", summary="KP DBA Timing Finder — Best Future Windows")
def dba_timing(payload: DBATimingInput):
    """
    Find the best future Dasha-Bhukti-Antara timing windows for any
    event (marriage, buying vehicle, job, property, etc.) using KP
    significator theory.

    Supports two modes:
    - **natal**: Uses birth chart for DBA periods and significators
    - **prashna**: Uses KP horary number to set the ascendant

    Returns ranked timing windows where DBA lords signify the
    conductive houses for the chosen question type.
    """
    try:
        data = resolve_chart(payload, need_houses=True)

        # Determine Moon longitude for DBA calculation
        moon = next((p for p in data.planets if p["planet"] == "Moon"), None)
        if not moon:
            raise HTTPException(status_code=400, detail="Moon position not found")

        moon_longitude = moon["longitude"]

        # Use the already-resolved local datetime from resolve_chart
        birth_dt = data.local_dt

        # Parse search window — use local now for default dates
        local_date_str, local_time_str = _local_now(
            payload.place, payload.latitude, payload.longitude
        )
        now_local = datetime.strptime(f"{local_date_str} {local_time_str}", "%Y-%m-%d %H:%M")
        if payload.search_start_date:
            search_start = datetime.strptime(payload.search_start_date, "%Y-%m-%d")
        else:
            search_start = now_local

        if payload.search_end_date:
            search_end = datetime.strptime(payload.search_end_date, "%Y-%m-%d")
        else:
            from datetime import timedelta
            search_end = search_start + timedelta(days=730)  # 2 years default

        # Optional transit planets for RP cross-check
        transit_planets = None
        transit_dt = None
        if payload.query_date and payload.query_time:
            use_date = payload.query_date
            use_time = payload.query_time
        else:
            use_date = local_date_str
            use_time = local_time_str

        try:
            tr_res, tr_dt = resolve_location_and_time(
                place=payload.place,
                date_str=use_date,
                time_str=use_time,
                latitude=payload.latitude,
                longitude=payload.longitude,
                timezone_offset_minutes=payload.timezone_offset_minutes,
            )
            tr_jd = to_julian_day_utc(tr_dt, tr_res.timezone_offset_minutes)
            transit_planets = calculate_planets(tr_jd, payload.ayanamsa)
            transit_dt = tr_dt
        except Exception:
            pass  # RP is optional — continue without it

        # Use natal or Prashna ascendant
        use_ascendant = data.ascendant
        use_houses = data.houses
        use_planets = data.planets

        # Parse optional validate_date
        v_date = None
        if payload.validate_date:
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    v_date = datetime.strptime(payload.validate_date, fmt)
                    break
                except ValueError:
                    continue

        # Run DBA Timing Finder
        result = find_dba_timing_windows(
            question_type=payload.question_type,
            planets=use_planets,
            houses=use_houses,
            ascendant=use_ascendant,
            moon_longitude=moon_longitude,
            birth_date=birth_dt,
            search_start=search_start,
            search_end=search_end,
            transit_planets=transit_planets,
            transit_datetime=transit_dt,
            validate_date=v_date,
        )

        return {
            "type":               "dba_timing",
            "name":               payload.name,
            "mode":               payload.mode,
            "ayanamsa":           payload.ayanamsa,
            "birth_date":         payload.date,
            "search_start":       result.get("search_start"),
            "search_end":         result.get("search_end"),
            "question_type":      payload.question_type,
            "question_label":     result.get("label"),
            "timing":             result,
            "available_questions": {k: v["label"] for k, v in PRASHNA_QUESTIONS.items()},
        }
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{exc}\n{tb}") from exc
