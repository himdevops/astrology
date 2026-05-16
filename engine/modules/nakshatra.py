"""
nakshatra.py — Nakshatra Analysis Module.
==========================================
Takes birth data → produces:
  - Nakshatra & pada for all 9 planets + Ascendant
  - Full Nakshatra detail (deity, symbol, animal, remedies, etc.)
  - Navtara system from Moon's Nakshatra
  - Nakshatra-based compatibility/strength analysis
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, List

from core.ephemeris import get_all_planets, calc_ascendant, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc, deg_to_dms
from core.nakshatra import calc_nakshatra
from core.constants import NAKSHATRAS_27, NAKSHATRA_LORDS, PLANETS_9
from core.nakshatra_data import NAKSHATRA_DETAIL


# ─── Navtara Constants ────────────────────────────────────────

TARA_NAMES = [
    "Janma",       # 1 — Birth star
    "Sampat",      # 2 — Wealth
    "Vipat",       # 3 — Danger
    "Kshema",      # 4 — Prosperity
    "Pratyari",    # 5 — Obstacle
    "Sadhaka",     # 6 — Achievement
    "Vadha",       # 7 — Death/Obstacle
    "Mitra",       # 8 — Friend
    "Ati-Mitra",   # 9 — Great Friend
]

TARA_NAMES_HI = [
    "जन्म",        # 1
    "सम्पत्",      # 2
    "विपत्",       # 3
    "क्षेम",       # 4
    "प्रत्यरि",    # 5
    "साधक",        # 6
    "वध",          # 7
    "मित्र",       # 8
    "अतिमित्र",    # 9
]

# Favorable taras (1-indexed): Janma(1), Sampat(2), Kshema(4), Sadhaka(6), Mitra(8), Ati-Mitra(9)
GOOD_TARAS = {1, 2, 4, 6, 8, 9}
BAD_TARAS = {3, 5, 7}  # Vipat, Pratyari, Vadha


def _calc_tara(ref_nak_idx: int, target_nak_idx: int) -> dict:
    """Calculate Navtara for a target nakshatra relative to a reference."""
    offset = ((target_nak_idx - ref_nak_idx) + 27) % 27
    tara_num = (offset % 9) + 1  # 1-9
    cycle = (offset // 9) + 1     # 1st, 2nd, or 3rd cycle
    is_good = tara_num in GOOD_TARAS
    return {
        "tara": tara_num,
        "tara_name": TARA_NAMES[tara_num - 1],
        "tara_name_hi": TARA_NAMES_HI[tara_num - 1],
        "cycle": cycle,
        "is_good": is_good,
        "offset": offset,
    }


def generate_nakshatra_analysis(
    dt: datetime,
    lat: float,
    lon: float,
    tz: float,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Generate comprehensive Nakshatra analysis.

    Returns:
        - planet_nakshatras: Nakshatra detail for each planet + Ascendant
        - navtara: 27×10 Navtara grid (all nakshatras × all planets+Asc)
        - navtara_summary: best/worst nakshatras by favorable count
        - tara_names: reference data
    """
    set_ayanamsa(ayanamsa)

    utc_dt = local_to_utc(dt, tz)
    jd = datetime_to_jd(utc_dt)

    # Get all planet positions (returns list of PlanetPosition objects)
    planet_positions = get_all_planets(jd, ayanamsa)

    # Calculate ascendant (returns PlanetPosition)
    asc_pos = calc_ascendant(jd, lat, lon, ayanamsa)

    # ── Planet Nakshatras ──────────────────────────────────────
    planet_nakshatras = {}
    planet_nak_indices = {}  # planet_name -> nakshatra index

    # Ascendant first
    asc_nak = calc_nakshatra(asc_pos.longitude)
    asc_detail = NAKSHATRA_DETAIL.get(asc_nak.name, {})
    planet_nakshatras["Ascendant"] = {
        "longitude": round(asc_pos.longitude, 4),
        "longitude_dms": deg_to_dms(asc_pos.longitude),
        "nakshatra": asc_nak.name,
        "nakshatra_index": asc_nak.index,
        "pada": asc_nak.pada,
        "lord": asc_nak.lord,
        "degree_in_nakshatra": round(asc_nak.degree_in_nakshatra, 4),
        "detail": asc_detail,
    }
    planet_nak_indices["Ascendant"] = asc_nak.index

    # All 9 planets
    for pp in planet_positions:
        pname = pp.planet
        nak = calc_nakshatra(pp.longitude)
        detail = NAKSHATRA_DETAIL.get(nak.name, {})
        planet_nakshatras[pname] = {
            "longitude": round(pp.longitude, 4),
            "longitude_dms": deg_to_dms(pp.longitude),
            "nakshatra": nak.name,
            "nakshatra_index": nak.index,
            "pada": nak.pada,
            "lord": nak.lord,
            "degree_in_nakshatra": round(nak.degree_in_nakshatra, 4),
            "detail": detail,
        }
        planet_nak_indices[pname] = nak.index

    # ── Navtara Grid ───────────────────────────────────────────
    # For each of the 27 nakshatras, compute tara relative to each planet
    ref_bodies = ["Ascendant"] + list(PLANETS_9)
    navtara_grid = []

    for ni in range(27):
        nak_name = NAKSHATRAS_27[ni]
        row = {
            "nakshatra": nak_name,
            "index": ni,
            "lord": NAKSHATRA_LORDS[ni],
            "taras": {},
            "good_count": 0,
            "bad_count": 0,
        }
        good_count = 0
        bad_count = 0
        for body in ref_bodies:
            if body not in planet_nak_indices:
                continue
            ref_idx = planet_nak_indices[body]
            tara_info = _calc_tara(ref_idx, ni)
            row["taras"][body] = tara_info
            if tara_info["is_good"]:
                good_count += 1
            else:
                bad_count += 1
        row["good_count"] = good_count
        row["bad_count"] = bad_count
        navtara_grid.append(row)

    # ── Navtara Summary ───────────────────────────────────────
    # Sort by good_count descending
    sorted_naks = sorted(navtara_grid, key=lambda x: x["good_count"], reverse=True)
    best_nakshatras = [
        {"nakshatra": n["nakshatra"], "good_count": n["good_count"], "bad_count": n["bad_count"]}
        for n in sorted_naks[:5]
    ]
    worst_nakshatras = [
        {"nakshatra": n["nakshatra"], "good_count": n["good_count"], "bad_count": n["bad_count"]}
        for n in sorted_naks[-5:]
    ]

    # ── Birth Info ─────────────────────────────────────────────
    birth_info = {
        "date": dt.strftime("%d-%m-%Y"),
        "time": dt.strftime("%H:%M"),
        "latitude": lat,
        "longitude_geo": lon,
        "tz_offset": tz,
        "ayanamsa": ayanamsa,
    }

    return {
        "birth_info": birth_info,
        "planet_nakshatras": planet_nakshatras,
        "navtara": navtara_grid,
        "navtara_summary": {
            "best_nakshatras": best_nakshatras,
            "worst_nakshatras": worst_nakshatras,
            "total_bodies": len(ref_bodies),
        },
        "tara_names": TARA_NAMES,
        "tara_names_hi": TARA_NAMES_HI,
        "good_taras": list(GOOD_TARAS),
        "nakshatras_27": NAKSHATRAS_27,
        "nakshatra_lords": NAKSHATRA_LORDS,
    }


def generate_transit_navtara(
    birth_dt: datetime,
    transit_dt: datetime,
    lat: float,
    lon: float,
    tz: float,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Calculate transit Navtara — which Navtara each planet is transiting
    on a given date, relative to the birth Moon's Nakshatra.

    Returns for each transiting planet:
      - current nakshatra & pada
      - tara relative to birth Moon
      - whether it's favourable
    """
    set_ayanamsa(ayanamsa)

    # ── Birth Moon Nakshatra (reference) ──
    birth_utc = local_to_utc(birth_dt, tz)
    birth_jd = datetime_to_jd(birth_utc)
    birth_positions = get_all_planets(birth_jd, ayanamsa)

    # Find Moon in birth positions
    birth_moon_lon = None
    for pp in birth_positions:
        if pp.planet == "Moon":
            birth_moon_lon = pp.longitude
            break
    if birth_moon_lon is None:
        return {"error": "Could not compute birth Moon position"}

    birth_moon_nak = calc_nakshatra(birth_moon_lon)

    # ── Transit Positions ──
    transit_utc = local_to_utc(transit_dt, tz)
    transit_jd = datetime_to_jd(transit_utc)
    transit_positions = get_all_planets(transit_jd, ayanamsa)
    transit_asc = calc_ascendant(transit_jd, lat, lon, ayanamsa)

    # ── Compute Tara for each transiting body ──
    transit_planets = []

    # Ascendant
    asc_nak = calc_nakshatra(transit_asc.longitude)
    asc_tara = _calc_tara(birth_moon_nak.index, asc_nak.index)
    transit_planets.append({
        "planet": "Ascendant",
        "longitude": round(transit_asc.longitude, 4),
        "nakshatra": asc_nak.name,
        "pada": asc_nak.pada,
        "lord": asc_nak.lord,
        "tara": asc_tara["tara"],
        "tara_name": asc_tara["tara_name"],
        "tara_name_hi": asc_tara["tara_name_hi"],
        "cycle": asc_tara["cycle"],
        "is_good": asc_tara["is_good"],
    })

    # 9 planets
    for pp in transit_positions:
        nak = calc_nakshatra(pp.longitude)
        tara = _calc_tara(birth_moon_nak.index, nak.index)
        transit_planets.append({
            "planet": pp.planet,
            "longitude": round(pp.longitude, 4),
            "nakshatra": nak.name,
            "pada": nak.pada,
            "lord": nak.lord,
            "tara": tara["tara"],
            "tara_name": tara["tara_name"],
            "tara_name_hi": tara["tara_name_hi"],
            "cycle": tara["cycle"],
            "is_good": tara["is_good"],
        })

    # Group by tara type
    tara_groups = {}
    for tp in transit_planets:
        tname = tp["tara_name"]
        if tname not in tara_groups:
            tara_groups[tname] = []
        tara_groups[tname].append(tp["planet"])

    # Count good/bad
    good_planets = [tp for tp in transit_planets if tp["is_good"]]
    bad_planets = [tp for tp in transit_planets if not tp["is_good"]]

    return {
        "birth_moon_nakshatra": birth_moon_nak.name,
        "birth_moon_nakshatra_index": birth_moon_nak.index,
        "birth_moon_lord": birth_moon_nak.lord,
        "transit_date": transit_dt.strftime("%d-%m-%Y"),
        "transit_time": transit_dt.strftime("%H:%M"),
        "transit_planets": transit_planets,
        "tara_groups": tara_groups,
        "good_count": len(good_planets),
        "bad_count": len(bad_planets),
        "total": len(transit_planets),
        "tara_names": TARA_NAMES,
        "tara_names_hi": TARA_NAMES_HI,
    }
