"""
sarvatobhadra.py — Sarvatobhadra Chakra service
Computes natal chart placement + full transit Vedha/Latta/Bindu/Navatara analysis.
"""
from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, List, Tuple

from app.core import (
    calculate_ascendant,
    calculate_planets,
    normalize_degree,
    resolve_location_and_time,
    to_julian_day_utc,
)
from app.nakshatra import get_nakshatra
from app.schemas import SarvatobhadraInput
from app.himanshu_sarvatobhdra import (
    AKSHARAS_16,
    ChakraEntity,
    EntityType,
    OUTER_NAK_POSITIONS,
    RASHIS_12,
    SarvatobhadraChakra,
    TITHIS_30,
    WEEKDAYS,
)
from app.sbc_analysis import (
    analyze_sbc_transits,
    calc_navatara,
    calc_six_bindus,
    calc_latta_for_planet,
)


# ─────────────────────────────────────────────────────────────
# Nakshatra alias normalization
# ─────────────────────────────────────────────────────────────
_NAK_ALIASES: Dict[str, str] = {
    "Dhanishta":       "Dhanishtha",
    "Dhanistha":       "Dhanishtha",
    "Shravan":         "Shravana",
    "Sravana":         "Shravana",
    "Uttarashadha":    "Uttara Ashadha",
    "Purvashadha":     "Purva Ashadha",
    "Uttar Ashadha":   "Uttara Ashadha",
    "Purva Asadha":    "Purva Ashadha",
    "Uttara Asadha":   "Uttara Ashadha",
    "Purbabhadrapada": "Purva Bhadrapada",
    "Uttarabhadrapada":"Uttara Bhadrapada",
}


def _normalize_nak(name: str) -> str:
    return _NAK_ALIASES.get(name, name)


# ─────────────────────────────────────────────────────────────
# Build nakshatra → grid position map
# ─────────────────────────────────────────────────────────────
def _build_nak_position_map(chakra: SarvatobhadraChakra) -> Dict[str, Tuple[int,int]]:
    """Return {nakshatra_name: (row, col)} for all outer ring nakshatras."""
    return {name: (r, c) for (r, c), name in OUTER_NAK_POSITIONS.items()}


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _weekday_name(local_dt: datetime) -> str:
    return WEEKDAYS[(local_dt.weekday() + 1) % len(WEEKDAYS)]


def _tithi_name(sun_longitude: float, moon_longitude: float) -> str:
    degrees = normalize_degree(moon_longitude - sun_longitude)
    index = int(degrees // 12) % len(TITHIS_30)
    return TITHIS_30[index]


def _prepare_planet_meta(
    planet: Dict[str, Any],
    sun_longitude: float,
    moon_longitude: float,
    local_dt: datetime,
) -> Dict[str, Any]:
    nak = get_nakshatra(planet["longitude"])
    return {
        "longitude":      round(normalize_degree(planet["longitude"]), 6),
        "sign":           planet["sign"],
        "degree_in_sign": planet["degree_in_sign"],
        "nakshatra":      _normalize_nak(nak["nakshatra"]),
        "nakshatra_lord": nak["lord"],
        "nakshatra_pada": nak["pada"],
        "tithi":          _tithi_name(sun_longitude, moon_longitude),
        "weekday":        _weekday_name(local_dt),
        "retrograde":     planet.get("retrograde", False),
    }


def _place_natal_planets(
    chakra: SarvatobhadraChakra,
    planets: List[Dict[str, Any]],
    local_dt: datetime,
) -> SarvatobhadraChakra:
    sun  = next((p for p in planets if p["planet"] == "Sun"),  None)
    moon = next((p for p in planets if p["planet"] == "Moon"), None)
    if not sun or not moon:
        raise ValueError("Sun and Moon required for SBC casting")

    for planet in planets:
        nak      = get_nakshatra(planet["longitude"])
        nak_name = _normalize_nak(nak["nakshatra"])
        target   = (chakra.find_entity(EntityType.NAKSHATRA, nak_name) or
                    chakra.find_entity(EntityType.NAKSHATRA, nak_name.lower()))
        if not target:
            continue
        row, col = target
        meta = _prepare_planet_meta(planet, sun["longitude"], moon["longitude"], local_dt)
        chakra._register_entity(
            row, col,
            ChakraEntity(name=planet["planet"], entity_type=EntityType.SPECIAL, meta=meta)
        )
    return chakra


def _grid_cells(chakra: SarvatobhadraChakra) -> List[List[Dict[str, Any]]]:
    return [
        [chakra.grid[r][c].to_dict() for c in range(chakra.GRID_SIZE)]
        for r in range(chakra.GRID_SIZE)
    ]


def _flatten_cells(chakra: SarvatobhadraChakra) -> List[Dict[str, Any]]:
    return [
        chakra.grid[r][c].to_dict()
        for r in range(chakra.GRID_SIZE)
        for c in range(chakra.GRID_SIZE)
    ]


# ─────────────────────────────────────────────────────────────
# Main service function
# ─────────────────────────────────────────────────────────────

def calculate_sarvatobhadra(payload: SarvatobhadraInput) -> dict:
    """
    Compute Sarvatobhadra Chakra for natal chart + full transit SBC analysis
    (Vedha, Latta, Six Bindus, Navatara, NSE/BSE signal).
    """
    # ── Natal chart ──────────────────────────────────────────
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut     = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets   = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)

    moon       = next(p for p in planets if p["planet"] == "Moon")
    moon_nak   = _normalize_nak(get_nakshatra(moon["longitude"])["nakshatra"])
    janma_nak  = moon_nak

    # ── Build chakra grid ─────────────────────────────────────
    chakra = SarvatobhadraChakra()
    chakra = _place_natal_planets(chakra, planets, local_dt)

    nak_pos_map = _build_nak_position_map(chakra)
    flat_cells  = _flatten_cells(chakra)

    # ── Transit planets ───────────────────────────────────────
    transit_date  = payload.transit_date  or date.today().isoformat()
    transit_time  = payload.transit_time  or "09:15"
    transit_place = payload.transit_place or "Mumbai, Maharashtra, India"

    t_resolved, t_dt = resolve_location_and_time(
        place=transit_place,
        date_str=transit_date,
        time_str=transit_time,
        latitude=None,
        longitude=None,
        timezone_offset_minutes=None,
    )
    t_jd_ut    = to_julian_day_utc(t_dt, t_resolved.timezone_offset_minutes)
    t_planets  = calculate_planets(t_jd_ut, payload.ayanamsa)

    # Enrich transit planets with nakshatra + speed info
    transit_with_nak: List[Dict] = []
    for tp in t_planets:
        nak_info = get_nakshatra(tp["longitude"])
        transit_with_nak.append({
            "planet":     tp["planet"],
            "nakshatra":  _normalize_nak(nak_info["nakshatra"]),
            "sign":       tp["sign"],
            "longitude":  tp["longitude"],
            "retrograde": tp.get("retrograde", False),
            "speed":      tp.get("speed", 0.0),   # degrees/day from Swiss Ephemeris
        })

    # ── Full SBC analysis ─────────────────────────────────────
    sbc_analysis = analyze_sbc_transits(
        janma_nak=janma_nak,
        natal_chakra_cells=flat_cells,
        transit_planets=transit_with_nak,
        nak_position_map=nak_pos_map,
    )

    return {
        "type":           "sarvatobhadra_chakra",
        "name":           payload.name,
        "birth_date":     payload.date,
        "birth_time":     payload.time,
        "birth_place":    resolved.place,
        "transit_date":   transit_date,
        "transit_place":  t_resolved.place,
        "ayanamsa":       payload.ayanamsa,
        "ascendant":      ascendant,
        "moon_nakshatra": get_nakshatra(moon["longitude"]),
        "janma_nakshatra":janma_nak,
        "grid_size":      chakra.GRID_SIZE,
        "chakra_grid":    _grid_cells(chakra),
        "chakra_cells":   flat_cells,
        "planet_positions": planets,
        "transit_planets":  transit_with_nak,
        # ── Advanced analysis ──────────────────────────────
        "sbc_analysis":   sbc_analysis,
    }
