"""
sarvatobhadra module — Advanced Sarvatobhadra Chakra endpoints.
Full 9×9 grid with Vedha, Latta, Six Bindus, Navatara, transit
analysis, vedha lines for chart rendering, NSE/BSE signal,
and comprehensive Vedha List for all 9 planets + Lagna.
"""
from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models import BirthDataInput, TransitDataInput, resolve_chart
from app.sarvatobhadra import calculate_sarvatobhadra as cast_sarvatobhadra
from app.core import (
    resolve_location_and_time,
    to_julian_day_utc,
    calculate_planets,
)
from app.nakshatra import get_nakshatra
from app.sbc_analysis import sbc_nse_daily_signal, calc_planet_vedha_detail
from app.vedha_list import (
    get_planet_vedha_report,
    get_lagna_vedha_report,
    get_all_vedha_reports,
    which_planets_are_vedha_to,
    PLANETS_9,
    MALEFICS,
    NAKSHATRA_TO_RASHI,
    NAKSHATRA_LORD,
    TRADITIONAL_VEDHA_PARTNER,
    PER_NAKSHATRA_VEDHA_TARGETS,
)

router = APIRouter(tags=["v3.0 — SBC (Sarvatobhadra)"])


# ── schemas ───────────────────────────────────────────────────

class SarvatobhadraInput(BirthDataInput):
    """Full SBC analysis — natal + transit."""
    transit_date: Optional[str] = Field(default=None, example="2026-04-15")
    transit_time: Optional[str] = Field(default="09:15", example="09:15")
    transit_place: Optional[str] = Field(default="Mumbai, Maharashtra, India")


class SBCDailySignalInput(BaseModel):
    """Quick daily SBC signal using Latta + Navatara (no full grid needed)."""
    # Natal Moon nakshatra source
    name: str = Field(default="Chart", example="Himanshu")
    date: str = Field(..., example="1990-01-15",
                      description="Birth date to derive Janma Nakshatra")
    time: str = Field(..., example="10:30")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")
    # Transit
    transit_date: Optional[str] = Field(default=None, example="2026-04-28")
    transit_time: str = Field(default="09:15")
    transit_place: str = Field(default="Mumbai, Maharashtra, India")


class VedhaListInput(BirthDataInput):
    """Vedha List — which transit planet vedhas which nakshatras/planets."""
    transit_date: Optional[str] = Field(default=None, example="2026-05-13")
    transit_time: Optional[str] = Field(default="09:15", example="09:15")
    transit_place: Optional[str] = Field(default="Mumbai, Maharashtra, India")


# ── endpoints ─────────────────────────────────────────────────

@router.post("/sarvatobhadra", summary="Advanced Sarvatobhadra Chakra")
def sarvatobhadra(payload: SarvatobhadraInput):
    """
    Full Sarvatobhadra Chakra with:

    - 9×9 grid with nakshatras, rashis, tithis, aksharas, weekdays
    - Natal planet placements on the grid
    - Transit planet positions enriched with nakshatras
    - **Vedha analysis**: horizontal, vertical, diagonal aspects with
      speed-based classification (Dakshina/Vama/Prishtha/Sthana)
    - **Latta analysis**: planetary kicks with direction (forward/backward),
      retrograde reversal, severity grading, and NSE sector impact
    - **Six Personal Bindus**: Janma, Karma, Sanghatika, Uday, Adhan, Vinash
    - **Navatara**: 9 tara categories from Janma Nakshatra
    - **Vedha line data**: start/end grid coordinates + line styles for
      chart rendering (solid/dashed/thick/double)
    - **Bindu analysis**: per-bindu status (AFFLICTED/PROTECTED/MIXED/CLEAR)
    - **NSE/BSE market signal**: composite score with action recommendations
    """
    try:
        return cast_sarvatobhadra(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sbc/daily-signal", summary="Quick SBC Daily NSE/BSE Signal")
def sbc_daily_signal(payload: SBCDailySignalInput):
    """
    Quick daily NSE/BSE signal using Latta + Navatara from SBC.
    Faster than full grid analysis — use for daily market scanning.

    Returns:
    - Active Lattas (which planets are kicking which nakshatras)
    - Navatara-based transit quality
    - Market signal (BULLISH / BEARISH / NEUTRAL)
    - Action recommendation
    """
    try:
        from datetime import date as _date

        # Get natal Moon nakshatra (Janma)
        natal_data = resolve_chart(payload, need_ascendant=False)
        moon = next(
            (p for p in natal_data.planets if p["planet"] == "Moon"), None,
        )
        if not moon:
            raise ValueError("Moon position not found")
        janma_nak_info = get_nakshatra(moon["longitude"])
        janma_nak = janma_nak_info["nakshatra"]

        # Get transit planets
        t_date = payload.transit_date or _date.today().isoformat()
        t_time = payload.transit_time
        t_place = payload.transit_place

        t_resolved, t_dt = resolve_location_and_time(
            place=t_place, date_str=t_date, time_str=t_time,
            latitude=None, longitude=None, timezone_offset_minutes=None,
        )
        t_jd = to_julian_day_utc(t_dt, t_resolved.timezone_offset_minutes)
        t_planets = calculate_planets(t_jd, payload.ayanamsa)

        # Build transit maps
        transit_nak_map = {}
        retrograde_map = {}
        for tp in t_planets:
            nak_info = get_nakshatra(tp["longitude"])
            transit_nak_map[tp["planet"]] = nak_info["nakshatra"]
            retrograde_map[tp["planet"]] = tp.get("retrograde", False)

        signal = sbc_nse_daily_signal(janma_nak, transit_nak_map, retrograde_map)

        return {
            "type": "sbc_daily_signal",
            "name": payload.name,
            "janma_nakshatra": janma_nak,
            "transit_date": t_date,
            "transit_place": t_resolved.place,
            **signal,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sbc/vedha-list", summary="SBC Vedha List — All 9 Planets + Lagna")
def sbc_vedha_list(payload: VedhaListInput):
    """
    Comprehensive Vedha List for SBC analysis.

    For each of the 9 transit planets + Lagna (Ascendant), returns:

    - **Traditional Directional Vedha** (Shlokas 19-47):
      Vama (Left), Dakshina (Right), Sammukha (Front) target nakshatras
    - **SBC Grid Geometric Vedha**: Row/Column/Diagonal intersections
    - **Traditional Vedha Pairs**: Classical obstruction pairs
    - **Full Detail**: Target Nakshatra, Rashi, Nak Lord, Rashi Lord,
      Direction, Vedha Type, Strength, affected natal planets
    - **Speed-based Classification**: 3-Way / Front / Left / Right / Sthana
    - **Nature**: Papa (malefic obstruction) or Shubha (benefic support)
    """
    try:
        from datetime import date as _date

        # ── Natal chart ──
        natal_data = resolve_chart(payload, need_ascendant=True)
        asc_nak_info = None
        if natal_data.ascendant:
            asc_nak_info = get_nakshatra(natal_data.ascendant["longitude"])

        # Build natal planet → nakshatra map
        natal_positions = {}
        for p in natal_data.planets:
            nak_info = get_nakshatra(p["longitude"])
            natal_positions[p["planet"]] = nak_info["nakshatra"]

        # ── Transit planets ──
        t_date = payload.transit_date or _date.today().isoformat()
        t_time = payload.transit_time or "09:15"
        t_place = payload.transit_place or "Mumbai, Maharashtra, India"

        t_resolved, t_dt = resolve_location_and_time(
            place=t_place, date_str=t_date, time_str=t_time,
            latitude=None, longitude=None, timezone_offset_minutes=None,
        )
        t_jd = to_julian_day_utc(t_dt, t_resolved.timezone_offset_minutes)
        t_planets = calculate_planets(t_jd, payload.ayanamsa)

        # Build transit positions map
        transit_positions = {}
        transit_speeds = {}
        transit_detail = []
        for tp in t_planets:
            nak_info = get_nakshatra(tp["longitude"])
            nak_name = nak_info["nakshatra"]
            transit_positions[tp["planet"]] = nak_name
            transit_speeds[tp["planet"]] = tp.get("speed", 0.0)
            transit_detail.append({
                "planet": tp["planet"],
                "nakshatra": nak_name,
                "pada": nak_info.get("pada", 1),
                "sign": tp["sign"],
                "longitude": tp["longitude"],
                "speed": tp.get("speed", 0.0),
                "retrograde": tp.get("retrograde", False),
            })

        # ── Generate vedha reports for all 9 planets ──
        planet_vedha_reports = {}
        for planet in PLANETS_9:
            nak = transit_positions.get(planet)
            if not nak:
                continue
            speed = transit_speeds.get(planet, 0.0)
            report = get_planet_vedha_report(
                planet=planet,
                transit_nakshatra=nak,
                planet_speed=speed,
                natal_planet_positions=natal_positions,
            )
            planet_vedha_reports[planet] = report

        # ── Lagna vedha report ──
        lagna_report = None
        lagna_nak = None
        if asc_nak_info:
            lagna_nak = asc_nak_info["nakshatra"]
            lagna_report = get_lagna_vedha_report(
                lagna_nakshatra=lagna_nak,
                natal_planet_positions=transit_positions,
            )

        # ── Build flat vedha list for UI table ──
        vedha_flat_list = []
        for planet, report in planet_vedha_reports.items():
            is_malefic = planet in MALEFICS
            for entry in report["traditional_vedha"]["detail"]:
                vedha_flat_list.append({
                    "transit_planet": planet,
                    "nature": "Papa" if is_malefic else "Shubha",
                    "from_nakshatra": report["transit_nakshatra"],
                    "from_rashi": report["transit_rashi"],
                    "direction": entry["direction"],
                    "direction_key": entry["direction_key"],
                    "target_nakshatra": entry["nakshatra"],
                    "target_rashi": entry["rashi"],
                    "target_rashi_lord": entry["rashi_lord"],
                    "target_nak_lord": entry["nak_lord"],
                    "vedha_type": entry["vedha_type"],
                    "strength": entry["strength"],
                    "strength_multiplier": entry["strength_multiplier"],
                    "affected_natal_planets": entry["affected_natal_planets"],
                    "traditional_pair": TRADITIONAL_VEDHA_PARTNER.get(
                        report["transit_nakshatra"], ""
                    ),
                })

        # ── Summary counts ──
        papa_count = sum(1 for v in vedha_flat_list if v["nature"] == "Papa")
        shubha_count = sum(1 for v in vedha_flat_list if v["nature"] == "Shubha")

        return {
            "type": "sbc_vedha_list",
            "name": payload.name,
            "birth_date": payload.date,
            "birth_time": payload.time,
            "birth_place": natal_data.resolved.place,
            "transit_date": t_date,
            "transit_time": t_time,
            "transit_place": t_resolved.place,
            "ayanamsa": payload.ayanamsa,
            "lagna_nakshatra": lagna_nak,
            "transit_planets": transit_detail,
            "planet_vedha_reports": planet_vedha_reports,
            "lagna_vedha_report": lagna_report,
            "vedha_flat_list": vedha_flat_list,
            "summary": {
                "total_vedha_entries": len(vedha_flat_list),
                "papa_vedhas": papa_count,
                "shubha_vedhas": shubha_count,
                "net_score": shubha_count - papa_count,
                "balance": (
                    "Strongly Negative" if (shubha_count - papa_count) < -10 else
                    "Negative" if (shubha_count - papa_count) < -3 else
                    "Neutral" if abs(shubha_count - papa_count) <= 3 else
                    "Positive" if (shubha_count - papa_count) <= 10 else
                    "Strongly Positive"
                ),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
