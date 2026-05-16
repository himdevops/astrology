"""
hora.py — Hora Module: Auspicious Time Calculator.
====================================================
Combines:
  1. Hora (planetary hours) — sunrise-based unequal hours
  2. Chaughadiya — 8 day + 8 night muhurta periods
  3. Transit Navtara — hora lord's nakshatra tara relative to birth Moon
  4. Ashtakavarga — hora lord's BAV score in transit sign

Produces an auspiciousness score for each hora slot.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from core.hora import calc_hora_table, calc_chaughadiya
from core.ephemeris import get_all_planets, calc_ascendant, set_ayanamsa
from core.nakshatra import calc_nakshatra
from core.ashtakavarga import calc_all_bav, calc_sav, _get_sign_index, ASHTAK_PLANETS
from core.utils import datetime_to_jd, local_to_utc, jd_to_datetime
from core.constants import NAKSHATRAS_27, SIGNS


# Navtara constants (same as modules/nakshatra.py)
TARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
    "Sadhaka", "Vadha", "Mitra", "Ati-Mitra",
]
TARA_NAMES_HI = [
    "जन्म", "सम्पत्", "विपत्", "क्षेम", "प्रत्यरि",
    "साधक", "वध", "मित्र", "अतिमित्र",
]
GOOD_TARAS = {1, 2, 4, 6, 8, 9}


def _calc_tara(ref_nak_idx: int, target_nak_idx: int) -> dict:
    """Calculate Navtara for target nakshatra relative to reference."""
    offset = ((target_nak_idx - ref_nak_idx) + 27) % 27
    tara_num = (offset % 9) + 1
    cycle = (offset // 9) + 1
    is_good = tara_num in GOOD_TARAS
    return {
        "tara": tara_num,
        "tara_name": TARA_NAMES[tara_num - 1],
        "tara_name_hi": TARA_NAMES_HI[tara_num - 1],
        "cycle": cycle,
        "is_good": is_good,
    }


def generate_hora_analysis(
    birth_dt: datetime,
    target_date: datetime,
    lat: float,
    lon: float,
    tz: float,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Generate comprehensive Hora analysis with auspiciousness scoring.

    Parameters:
        birth_dt:    Birth datetime (local)
        target_date: Date to calculate horas for (local, time portion ignored)
        lat, lon:    Location coordinates
        tz:          Timezone offset
        ayanamsa:    Ayanamsa system

    Returns:
        Complete hora data with navtara + ashtakavarga cross-reference.
    """
    set_ayanamsa(ayanamsa)

    # ── Birth Moon Nakshatra (reference for Navtara) ──
    birth_utc = local_to_utc(birth_dt, tz)
    birth_jd = datetime_to_jd(birth_utc)
    birth_positions = get_all_planets(birth_jd, ayanamsa)

    birth_moon_lon = None
    for pp in birth_positions:
        if pp.planet == "Moon":
            birth_moon_lon = pp.longitude
            break
    if birth_moon_lon is None:
        return {"error": "Could not compute birth Moon position"}

    birth_moon_nak = calc_nakshatra(birth_moon_lon)

    # ── Birth Ashtakavarga (BAV for scoring) ──
    birth_planet_lons = {}
    birth_asc = calc_ascendant(birth_jd, lat, lon, ayanamsa)
    for pp in birth_positions:
        if pp.planet in ASHTAK_PLANETS:
            birth_planet_lons[pp.planet] = pp.longitude

    birth_planet_signs = {p: _get_sign_index(l) for p, l in birth_planet_lons.items()}
    birth_planet_signs["Lagna"] = _get_sign_index(birth_asc.longitude)
    all_bav = calc_all_bav(birth_planet_signs)
    sav = calc_sav(all_bav)

    # ── Hora Table ──
    hora_data = calc_hora_table(target_date, lat, lon, tz)
    if "error" in hora_data:
        return hora_data

    # ── Chaughadiya ──
    chaugh_data = calc_chaughadiya(target_date, lat, lon, tz)

    # ── Enrich each hora with Navtara + Ashtakavarga ──
    horas = hora_data["horas"]
    for hora in horas:
        lord = hora["lord"]

        # Get planet position at the midpoint of this hora
        mid_jd = (hora["start_jd"] + hora["end_jd"]) / 2.0
        transit_positions = get_all_planets(mid_jd, ayanamsa)

        # Find the hora lord's transit position
        lord_lon = None
        for pp in transit_positions:
            if pp.planet == lord:
                lord_lon = pp.longitude
                break

        if lord_lon is not None:
            # Navtara
            lord_nak = calc_nakshatra(lord_lon)
            tara = _calc_tara(birth_moon_nak.index, lord_nak.index)
            hora["navtara"] = {
                "nakshatra": lord_nak.name,
                "pada": lord_nak.pada,
                **tara,
            }

            # Ashtakavarga BAV score
            transit_sign = _get_sign_index(lord_lon)
            if lord in all_bav:
                bav_score = all_bav[lord][transit_sign]
                hora["bav_score"] = bav_score
                hora["bav_sign"] = SIGNS[transit_sign]
            else:
                hora["bav_score"] = None
                hora["bav_sign"] = SIGNS[transit_sign]

            # SAV score for that sign
            hora["sav_score"] = sav[transit_sign]

            # ── Auspiciousness Score ──
            # Scoring: Navtara good=2, bad=0 | BAV 5+=2, 4=1.5, 3=1, <3=0 | Chaughadiya bonus added later
            score = 0
            if tara["is_good"]:
                score += 2
            if hora["bav_score"] is not None:
                if hora["bav_score"] >= 5:
                    score += 2
                elif hora["bav_score"] >= 4:
                    score += 1.5
                elif hora["bav_score"] >= 3:
                    score += 1
            hora["auspicious_score"] = score
        else:
            hora["navtara"] = None
            hora["bav_score"] = None
            hora["bav_sign"] = None
            hora["sav_score"] = None
            hora["auspicious_score"] = 0

        # Remove JD values from output (internal use only)
        del hora["start_jd"]
        del hora["end_jd"]

    # ── Cross-reference with Chaughadiya ──
    # Add chaughadiya quality bonus to hora score
    # Map each hora to overlapping chaughadiya
    _add_chaughadiya_to_horas(horas, chaugh_data, hora_data)

    # ── Classify horas ──
    for hora in horas:
        score = hora.get("auspicious_score", 0)
        if score >= 4:
            hora["rating"] = "excellent"
        elif score >= 3:
            hora["rating"] = "very_good"
        elif score >= 2:
            hora["rating"] = "good"
        elif score >= 1:
            hora["rating"] = "average"
        else:
            hora["rating"] = "poor"

    # ── Summary stats ──
    excellent = sum(1 for h in horas if h["rating"] == "excellent")
    very_good = sum(1 for h in horas if h["rating"] == "very_good")
    good = sum(1 for h in horas if h["rating"] == "good")
    avg = sum(1 for h in horas if h["rating"] == "average")
    poor = sum(1 for h in horas if h["rating"] == "poor")

    # Best horas
    sorted_horas = sorted(horas, key=lambda h: h.get("auspicious_score", 0), reverse=True)
    best_times = [
        {"hora_num": h["hora_num"], "start": h["start"], "end": h["end"],
         "lord": h["lord"], "score": h["auspicious_score"], "rating": h["rating"]}
        for h in sorted_horas[:5]
    ]

    return {
        "birth_moon_nakshatra": birth_moon_nak.name,
        "birth_moon_index": birth_moon_nak.index,
        "birth_moon_lord": birth_moon_nak.lord,
        "date": hora_data["date"],
        "weekday": hora_data["weekday"],
        "weekday_hi": hora_data["weekday_hi"],
        "day_lord": hora_data["day_lord"],
        "day_lord_hi": hora_data["day_lord_hi"],
        "sunrise": hora_data["sunrise"],
        "sunset": hora_data["sunset"],
        "day_hora_min": hora_data["day_hora_min"],
        "night_hora_min": hora_data["night_hora_min"],
        "horas": horas,
        "chaughadiya": chaugh_data,
        "summary": {
            "excellent": excellent,
            "very_good": very_good,
            "good": good,
            "average": avg,
            "poor": poor,
            "best_times": best_times,
        },
        "tara_names": TARA_NAMES,
        "tara_names_hi": TARA_NAMES_HI,
        "ayanamsa": ayanamsa,
    }


def _add_chaughadiya_to_horas(
    horas: list,
    chaugh_data: dict,
    hora_data: dict,
) -> None:
    """
    Cross-reference horas with chaughadiya periods.
    Add chaughadiya quality bonus to auspicious_score.
    """
    if "error" in chaugh_data:
        return

    # Build a time-ordered list of chaughadiya with start/end in HH:MM
    all_chaugh = []
    for p in chaugh_data.get("day_periods", []):
        all_chaugh.append({**p, "is_day": True})
    for p in chaugh_data.get("night_periods", []):
        all_chaugh.append({**p, "is_day": False})

    # Simple overlap: find the chaughadiya that most overlaps with each hora
    # Using HH:MM string comparison (approximate but sufficient)
    for hora in horas:
        hora_start = hora["start"]
        best_match = None
        for ch in all_chaugh:
            # Check if hora start falls within this chaughadiya
            if _time_in_range(hora_start, ch["start"], ch["end"]):
                best_match = ch
                break

        if best_match:
            hora["chaughadiya"] = best_match["name"]
            hora["chaughadiya_hi"] = best_match["name_hi"]
            hora["chaughadiya_quality"] = best_match["quality"]

            # Bonus score based on chaughadiya
            cq = best_match["quality"]
            if cq == "excellent":   # Amrit
                hora["auspicious_score"] = hora.get("auspicious_score", 0) + 1.5
            elif cq == "very_good":  # Shubh, Labh
                hora["auspicious_score"] = hora.get("auspicious_score", 0) + 1.0
            elif cq == "good":       # Char
                hora["auspicious_score"] = hora.get("auspicious_score", 0) + 0.5
            elif cq == "bad":        # Rog, Udveg
                hora["auspicious_score"] = hora.get("auspicious_score", 0) - 0.5
            elif cq == "very_bad":   # Kaal
                hora["auspicious_score"] = hora.get("auspicious_score", 0) - 1.0
        else:
            hora["chaughadiya"] = None
            hora["chaughadiya_hi"] = None
            hora["chaughadiya_quality"] = None


def _time_in_range(time_str: str, start_str: str, end_str: str) -> bool:
    """Check if time_str falls within [start_str, end_str) using HH:MM strings."""
    def to_min(s):
        parts = s.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    t = to_min(time_str)
    s = to_min(start_str)
    e = to_min(end_str)

    if s <= e:
        return s <= t < e
    else:
        # Crosses midnight
        return t >= s or t < e
