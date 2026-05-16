"""
special_lagnas.py — Special Lagnas & Sensitive Points module.
=============================================================
Orchestrates core/special_lagnas.py calculations, enriches each
point with sign/nakshatra info and varga placements.

Called from api/v1/special_lagnas.py.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, List

import swisseph as swe

from core.ephemeris import (
    get_all_planets, calc_ascendant, set_ayanamsa,
)
from core.utils import datetime_to_jd, local_to_utc, normalize_degree, deg_to_dms
from core.signs import calc_sign
from core.nakshatra import calc_nakshatra
from core.constants import SIGNS, SIGN_LORDS, VARAS, VARA_LORDS
from core.divisional import calc_varga, VARGA_ORDER, VARGA_NAMES
from core.special_lagnas import (
    calc_all_special_points,
    calc_chara_karakas,
    KARAKA_NAMES, KARAKA_ABBREV,
    INDU_VALUES,
)


# ─── Sunrise / Sunset JD ───────────────────────────────────

def _calc_sunrise_jd(jd_start_of_day: float, lat: float, lon: float) -> float:
    """Get Julian Day of sunrise using swe.rise_trans."""
    try:
        res = swe.rise_trans(
            jd_start_of_day, swe.SUN, lon, lat, 0.0, 0.0,
            1,  # 1 = rise
        )
        if res and len(res) >= 2:
            return res[1][0] if isinstance(res[1], (list, tuple)) else res[1]
    except Exception:
        pass
    # Fallback: approximate sunrise at 6:00 AM local
    return jd_start_of_day + 0.25


def _calc_sunset_jd(jd_start_of_day: float, lat: float, lon: float) -> float:
    """Get Julian Day of sunset using swe.rise_trans."""
    try:
        res = swe.rise_trans(
            jd_start_of_day, swe.SUN, lon, lat, 0.0, 0.0,
            2,  # 2 = set
        )
        if res and len(res) >= 2:
            return res[1][0] if isinstance(res[1], (list, tuple)) else res[1]
    except Exception:
        pass
    # Fallback: approximate sunset at 18:00 local
    return jd_start_of_day + 0.75


# ─── Enrich a longitude with sign/nak info ─────────────────

def _enrich_longitude(lon: float, label: str = "") -> Dict[str, Any]:
    """Add sign, nakshatra, degree info for a longitude."""
    lon = normalize_degree(lon)
    sign_info = calc_sign(lon)
    nak_info = calc_nakshatra(lon)
    sign_idx = SIGNS.index(sign_info.name)
    return {
        "longitude": round(lon, 4),
        "sign": sign_info.name,
        "sign_index": sign_idx,
        "sign_lord": sign_info.lord,
        "degree_in_sign": round(sign_info.degree_in_sign, 4),
        "degree_display": f"{deg_to_dms(sign_info.degree_in_sign)} {sign_info.name}",
        "nakshatra": nak_info.name,
        "nakshatra_lord": nak_info.lord,
        "nakshatra_pada": nak_info.pada,
    }


# ─── Varga placements for a longitude ─────────────────────

def _calc_varga_placements(lon: float) -> Dict[str, Dict[str, str]]:
    """Get sign placement in each of the 16 vargas for a longitude."""
    placements = {}
    for varga in VARGA_ORDER:
        v = calc_varga(lon, varga)
        placements[varga] = {
            "sign": v["sign"],
            "sign_lord": v["sign_lord"],
        }
    return placements


# ─── Gulika longitude (Asc at Gulika JD) ──────────────────

def _calc_gulika_longitude(
    gulika_jd: float, lat: float, lon: float, ayanamsa: str
) -> float:
    """Calculate the Ascendant at the Gulika JD = Gulika's longitude."""
    set_ayanamsa(ayanamsa)
    sidereal = ayanamsa.lower() != "tropical"
    flags = swe.FLG_SIDEREAL if sidereal else 0
    cusps, ascmc = swe.houses_ex(gulika_jd, lat, lon, b'P', flags)
    return normalize_degree(ascmc[0])


# ═══════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════

def generate_special_lagnas(
    birth_dt: datetime,
    lat: float,
    lon: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    karaka_system: int = 7,
) -> Dict[str, Any]:
    """
    Generate all special lagnas and sensitive points.

    Parameters:
        birth_dt:  Local datetime of birth
        lat:       Birth place latitude
        lon:       Birth place longitude
        tz_offset: Timezone offset from UTC
        ayanamsa:  Ayanamsa system
        karaka_system: 7 (standard, no Rahu/Ketu) or 8 (Jaimini, Rahu included)

    Returns complete special lagnas data with sign/nak info and varga placements.
    """
    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(birth_dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    # Get planet positions and ascendant
    planet_positions = get_all_planets(jd, ayanamsa)
    ascendant = calc_ascendant(jd, lat, lon, ayanamsa)
    asc_lon = ascendant.longitude

    # Weekday (Sunday=0)
    weekday_idx = (birth_dt.weekday() + 1) % 7  # Python Monday=0 → Sunday=0

    # Sunrise/Sunset JDs for birth date
    start_of_day_utc = local_to_utc(
        birth_dt.replace(hour=0, minute=0, second=0), tz_offset
    )
    jd_start = datetime_to_jd(start_of_day_utc)
    sunrise_jd = _calc_sunrise_jd(jd_start, lat, lon)
    sunset_jd = _calc_sunset_jd(jd_start, lat, lon)

    # ── Core calculations ──
    raw = calc_all_special_points(
        planet_positions=planet_positions,
        asc_lon=asc_lon,
        birth_jd=jd,
        sunrise_jd=sunrise_jd,
        sunset_jd=sunset_jd,
        weekday=weekday_idx,
        lat=lat,
        lon=lon,
        karaka_system=karaka_system,
    )

    # ── Gulika longitude (Ascendant at gulika JD) ──
    gulika_jd = raw["gulika_jd"]
    gulika_lon = _calc_gulika_longitude(gulika_jd, lat, lon, ayanamsa)

    # ── Enrich special lagnas with sign/nak/varga info ──
    special_lagnas_enriched = {}
    lagna_labels = {
        "hora_lagna": "Hora Lagna (HL)",
        "ghati_lagna": "Ghati Lagna (GL)",
        "bhava_lagna": "Bhava Lagna (BL)",
        "sree_lagna": "Sree Lagna (SL)",
        "pranapada_lagna": "Pranapada Lagna (PP)",
        "varnada_lagna": "Varnada Lagna (VL)",
        "indu_lagna": "Indu Lagna (IL)",
        "karakamsha": "Karakamsha (KL)",
        "swamsha": "Swamsha",
        "arudha_lagna": "Arudha Lagna (AL)",
    }

    for key, label in lagna_labels.items():
        lagna_lon = raw["special_lagnas"][key]
        enriched = _enrich_longitude(lagna_lon, label)
        enriched["key"] = key
        enriched["label"] = label
        enriched["vargas"] = _calc_varga_placements(lagna_lon)
        special_lagnas_enriched[key] = enriched

    # ── Add Gulika as a special point ──
    gulika_enriched = _enrich_longitude(gulika_lon, "Gulika (Mandi)")
    gulika_enriched["key"] = "gulika"
    gulika_enriched["label"] = "Gulika (Mandi)"
    gulika_enriched["vargas"] = _calc_varga_placements(gulika_lon)

    # ── Enrich sensitive points ──
    sensitive_points_enriched = {}
    sp_labels = {
        "fortune_vedic": "Part of Fortune (Vedic)",
        "fortune_western": "Part of Fortune (Western)",
        "yoga_point": "Yoga Point",
        "yogi_point": "Yogi Point",
        "avayogi_point": "Avayogi Point",
        "bhrigu_bindu": "Bhrigu Bindu (BB)",
    }

    for key, label in sp_labels.items():
        sp_lon = raw["sensitive_points"][key]
        enriched = _enrich_longitude(sp_lon, label)
        enriched["key"] = key
        enriched["label"] = label
        enriched["vargas"] = _calc_varga_placements(sp_lon)
        sensitive_points_enriched[key] = enriched

    # ── Enrich chara karakas ──
    karakas = raw["chara_karakas"]
    for kd in karakas:
        planet_lon = kd["longitude"]
        kd_extra = _enrich_longitude(planet_lon)
        kd["sign"] = kd_extra["sign"]
        kd["sign_lord"] = kd_extra["sign_lord"]
        kd["degree_display"] = kd_extra["degree_display"]
        kd["nakshatra"] = kd_extra["nakshatra"]
        kd["nakshatra_lord"] = kd_extra["nakshatra_lord"]

    # ── Planet positions for chart rendering ──
    planet_chart_data = []
    for pp in planet_positions:
        sign_idx = SIGNS.index(pp.sign)
        planet_chart_data.append({
            "planet": pp.planet,
            "sign": pp.sign,
            "sign_index": sign_idx,
            "retrograde": pp.retrograde,
        })

    # ── Sunrise/sunset info ──
    sunrise_hours = (sunrise_jd - jd_start) * 24.0 + tz_offset
    sunset_hours = (sunset_jd - jd_start) * 24.0 + tz_offset
    sunrise_h, sunrise_m = int(sunrise_hours), int((sunrise_hours % 1) * 60)
    sunset_h, sunset_m = int(sunset_hours), int((sunset_hours % 1) * 60)

    return {
        "birth_info": {
            "date": birth_dt.strftime("%d-%m-%Y"),
            "time": birth_dt.strftime("%H:%M"),
            "latitude": lat,
            "longitude": lon,
            "tz_offset": tz_offset,
            "ayanamsa": ayanamsa,
            "weekday": VARAS[weekday_idx],
            "weekday_lord": VARA_LORDS[weekday_idx],
            "is_day_birth": raw["is_day_birth"],
            "sunrise": f"{sunrise_h:02d}:{sunrise_m:02d}",
            "sunset": f"{sunset_h:02d}:{sunset_m:02d}",
            "ghatis_from_sunrise": raw["ghatis_from_sunrise"],
        },
        "ascendant": _enrich_longitude(asc_lon, "Lagna"),
        "planets": planet_chart_data,
        "special_lagnas": special_lagnas_enriched,
        "gulika": gulika_enriched,
        "sensitive_points": sensitive_points_enriched,
        "yogi_avayogi": raw["yogi_avayogi"],
        "chara_karakas": karakas,
    }
