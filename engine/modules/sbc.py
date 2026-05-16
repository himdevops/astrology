"""
modules/sbc.py — Sarvatobhadra Chakra Generator.
==================================================
Combines the SBC grid layout with natal and transit planet positions,
calculates vedha lines, and returns the complete SBC data for rendering.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, List, Optional

from core.sbc import (
    NAKSHATRAS_28, NAK_POSITIONS, NAK_TO_POS, RASHI_POSITIONS,
    build_grid, get_vedha_targets, get_vedha_type,
    get_planet_nakshatra_28,
    get_jkv_nakshatras, classify_planet, is_moon_waxing,
    analyze_vedha_hits, calc_upagrahas, calc_graha_latta,
    get_all_natal_drishti, calc_graha_bala,
    get_kurma_data, get_prashna_analysis,
)
from core.ephemeris import get_all_planets, calc_ascendant
from core.utils import datetime_to_jd, local_to_utc
from core.constants import SIGNS


def _get_sign_index(longitude: float) -> int:
    """0-based sign index from longitude."""
    return int(longitude / 30.0) % 12


def _find_nak_cell(nak_name: str) -> Optional[Dict[str, int]]:
    """Find the grid cell for a nakshatra name."""
    for (r, c), idx in NAK_POSITIONS.items():
        if NAKSHATRAS_28[idx] == nak_name:
            return {"row": r, "col": c}
    return None


def _find_rashi_cell(rashi_index: int) -> Optional[Dict[str, int]]:
    """Find the grid cell for a rashi index (0-11)."""
    for (r, c), idx in RASHI_POSITIONS.items():
        if idx == rashi_index:
            return {"row": r, "col": c}
    return None


def generate_sbc(
    birth_dt: datetime,
    transit_dt: datetime,
    lat: float,
    lon: float,
    tz: float,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Generate complete Sarvatobhadra Chakra data.

    Args:
        birth_dt: Birth datetime (local)
        transit_dt: Transit datetime (local)
        lat, lon: Location coordinates
        tz: Timezone offset from UTC
        ayanamsa: Ayanamsa system

    Returns:
        Dict with grid, natal_planets, transit_planets, vedha_lines
    """
    # Calculate birth chart positions
    birth_utc = local_to_utc(birth_dt, tz)
    birth_jd = datetime_to_jd(birth_utc)
    birth_planets = get_all_planets(birth_jd, ayanamsa)
    birth_asc = calc_ascendant(birth_jd, lat, lon, ayanamsa)

    # Calculate transit positions
    transit_utc = local_to_utc(transit_dt, tz)
    transit_jd = datetime_to_jd(transit_utc)
    transit_planets = get_all_planets(transit_jd, ayanamsa)

    # Build grid
    grid = build_grid()

    # Place natal planets on the grid
    natal_placements = []
    for pp in birth_planets:
        nak_idx_28, nak_name_28, pada = get_planet_nakshatra_28(pp.longitude)
        cell_pos = NAK_TO_POS.get(nak_idx_28)
        if cell_pos:
            natal_placements.append({
                "planet": pp.planet,
                "longitude": round(pp.longitude, 4),
                "nakshatra": nak_name_28,
                "pada": pada,
                "sign": pp.sign,
                "retrograde": pp.retrograde,
                "row": cell_pos[0],
                "col": cell_pos[1],
            })

    # Place Lagna (Ascendant)
    asc_nak_idx, asc_nak_name, asc_pada = get_planet_nakshatra_28(birth_asc.longitude)
    asc_cell = NAK_TO_POS.get(asc_nak_idx)
    if asc_cell:
        natal_placements.append({
            "planet": "Asc",
            "longitude": round(birth_asc.longitude, 4),
            "nakshatra": asc_nak_name,
            "pada": asc_pada,
            "sign": birth_asc.sign,
            "retrograde": False,
            "row": asc_cell[0],
            "col": asc_cell[1],
        })

    # Birth weekday and tithi for Chandra Bindu
    weekday_names_all = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    birth_vara = weekday_names_all[birth_dt.weekday()]
    birth_tithi_group = ""
    birth_sun_lon = None
    birth_moon_lon = None
    for pp in birth_planets:
        if pp.planet == "Sun":
            birth_sun_lon = pp.longitude
        elif pp.planet == "Moon":
            birth_moon_lon = pp.longitude
    if birth_sun_lon is not None and birth_moon_lon is not None:
        bdiff = (birth_moon_lon - birth_sun_lon) % 360
        btithi_idx = int(bdiff / 12) % 30
        btithi_num = (btithi_idx % 15) + 1
        if btithi_num in (1, 6, 11):
            birth_tithi_group = "Nanda"
        elif btithi_num in (2, 7, 12):
            birth_tithi_group = "Bhadra"
        elif btithi_num in (3, 8, 13):
            birth_tithi_group = "Jaya"
        elif btithi_num in (4, 9, 14):
            birth_tithi_group = "Rikta"
        elif btithi_num in (5, 10, 15):
            birth_tithi_group = "Poorna"

    # Place transit planets
    transit_placements = []
    vedha_lines = []

    for pp in transit_planets:
        nak_idx_28, nak_name_28, pada = get_planet_nakshatra_28(pp.longitude)
        cell_pos = NAK_TO_POS.get(nak_idx_28)
        if cell_pos:
            transit_placements.append({
                "planet": pp.planet,
                "longitude": round(pp.longitude, 4),
                "nakshatra": nak_name_28,
                "pada": pada,
                "sign": pp.sign,
                "retrograde": pp.retrograde,
                "speed": round(pp.speed, 4),
                "row": cell_pos[0],
                "col": cell_pos[1],
            })

            # Calculate vedha lines based on speed & retrograde
            vedha_type = get_vedha_type(pp.planet, pp.speed, pp.retrograde)
            targets = get_vedha_targets(cell_pos[0], cell_pos[1], vedha_type)
            if targets:
                vedha_lines.append({
                    "planet": pp.planet,
                    "from": {"row": cell_pos[0], "col": cell_pos[1]},
                    "targets": [{"row": t[0], "col": t[1]} for t in targets],
                    "vedha_type": vedha_type,
                    "speed": round(pp.speed, 4),
                    "retrograde": pp.retrograde,
                })

    # Weekday of transit date
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    transit_weekday = weekday_names[transit_dt.weekday()]

    # Sun & Moon longitudes for tithi and upagraha
    transit_sun = None
    transit_moon = None
    transit_moon_lon = 0.0
    for pp in transit_planets:
        if pp.planet == "Sun":
            transit_sun = pp.longitude
        elif pp.planet == "Moon":
            transit_moon = pp.longitude
            transit_moon_lon = pp.longitude

    # Tithi calculation
    transit_tithi_group = ""
    transit_tithi_num = 0
    moon_waxing = True
    if transit_sun is not None and transit_moon is not None:
        diff = (transit_moon - transit_sun) % 360
        moon_waxing = diff < 180
        tithi_idx = int(diff / 12) % 30
        transit_tithi_num = (tithi_idx % 15) + 1
        if transit_tithi_num in (1, 6, 11):
            transit_tithi_group = "Nanda"
        elif transit_tithi_num in (2, 7, 12):
            transit_tithi_group = "Bhadra"
        elif transit_tithi_num in (3, 8, 13):
            transit_tithi_group = "Jaya"
        elif transit_tithi_num in (4, 9, 14):
            transit_tithi_group = "Rikta"
        elif transit_tithi_num in (5, 10, 15):
            transit_tithi_group = "Poorna"

    # ── Shubh/Ashubh classification for vedha lines ──
    for vl in vedha_lines:
        vl["nature"] = classify_planet(vl["planet"], moon_waxing)

    # ── Janma-Karma-Vinasha nakshatras ──
    birth_moon_nak_idx = None
    for np in natal_placements:
        if np["planet"] == "Moon":
            birth_moon_nak_idx = None
            # Find the 28-nak index from the nakshatra name
            for i, n in enumerate(NAKSHATRAS_28):
                if n == np["nakshatra"]:
                    birth_moon_nak_idx = i
                    break
            break
    jkv = get_jkv_nakshatras(birth_moon_nak_idx) if birth_moon_nak_idx is not None else {}

    # ── Vedha hit analysis ──
    vedha_hits = analyze_vedha_hits(
        vedha_lines, natal_placements, transit_weekday, transit_tithi_group
    )

    # ── Upagrahas ──
    upagrahas = calc_upagrahas(transit_sun) if transit_sun is not None else []

    # ── Graha Latta ──
    graha_latta = calc_graha_latta(transit_placements)

    # ── Nakshatra Drishti ──
    nakshatra_drishti = get_all_natal_drishti(natal_placements)

    # ── Graha Bala ──
    graha_bala = calc_graha_bala(vedha_lines, natal_placements, transit_placements)

    # ── Kurma Chakra ──
    kurma = get_kurma_data(natal_placements, transit_placements)

    # ── Transit Moon nakshatra for prashna ──
    transit_moon_nak_name = ""
    for tp in transit_placements:
        if tp["planet"] == "Moon":
            transit_moon_nak_name = tp["nakshatra"]
            break

    # ── Prashna Analysis ──
    prashna = get_prashna_analysis(
        transit_weekday, transit_tithi_group,
        transit_moon_nak_name, vedha_hits
    )

    return {
        "grid": grid,
        "natal_planets": natal_placements,
        "transit_planets": transit_placements,
        "vedha_lines": vedha_lines,
        "vedha_hits": vedha_hits,
        "transit_weekday": transit_weekday,
        "transit_tithi_group": transit_tithi_group,
        "transit_tithi_num": transit_tithi_num,
        "moon_waxing": moon_waxing,
        "jkv": jkv,
        "upagrahas": upagrahas,
        "graha_latta": graha_latta,
        "nakshatra_drishti": nakshatra_drishti,
        "graha_bala": graha_bala,
        "kurma": kurma,
        "prashna": prashna,
        "birth_date": birth_dt.strftime("%d-%m-%Y %H:%M"),
        "birth_vara": birth_vara,
        "birth_tithi_group": birth_tithi_group,
        "transit_date": transit_dt.strftime("%d-%m-%Y %H:%M"),
        "_vedha_version": "v3-complete",
    }
