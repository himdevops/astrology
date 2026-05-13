"""
vedha_list.py — Comprehensive Vedha Reference Module for SBC Engine
====================================================================
Provides complete vedha mapping for all 9 planets + Lagna (Ascendant):
  1. SBC Grid-Based Vedha: Row/Column/Diagonal intersections from the 9x9 grid
  2. Traditional Nakshatra Vedha Pairs: Classical vedha pairs per Shlokas 19-47
  3. Full Detail: Nakshatras, Affected Planets, Direction (Vama/Dakshina/Sammukha),
     and Strength classification

References:
  - Khemraj Publishers Sarvatobhadra Chakra text (Shlokas 19-47)
  - Parashara's Light 9.0 vedha classification
  - Traditional SBC grid layout per Shyam S Kansal

Usage:
  from app.vedha_list import (
      get_planet_vedha_report,
      get_all_vedha_reports,
      get_lagna_vedha_report,
      PLANETS_9,
  )
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from app.himanshu_sarvatobhdra import (
    SarvatobhadraChakra,
    EntityType,
    NAKSHATRAS_28,
    OUTER_NAK_POSITIONS,
    RASHI_CELL_MAP,
    RASHIS_12,
)
from app.sbc_analysis import (
    PER_NAKSHATRA_VEDHA_TARGETS,
    VEDHA_STRENGTH_MULTIPLIER,
    classify_vedha_type,
    PLANET_AVG_SPEED,
    ALWAYS_FULL_VEDHA_PLANETS,
)


# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

PLANETS_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Planet → default nakshatra for reference table (used when no transit data)
# This is the "natural" or exaltation nakshatra association for reference
PLANET_NATURAL_NAKSHATRA = {
    "Sun":     "Krittika",
    "Moon":    "Rohini",
    "Mars":    "Mrigashira",
    "Mercury": "Ashlesha",
    "Jupiter": "Punarvasu",
    "Venus":   "Bharani",
    "Saturn":  "Pushya",
    "Rahu":    "Ardra",
    "Ketu":    "Magha",
}

# Nakshatra → Rashi mapping (which rashi the nakshatra falls in)
# Based on 13°20' per nakshatra, 30° per rashi
NAKSHATRA_TO_RASHI = {
    "Ashwini": "Aries", "Bharani": "Aries", "Krittika": "Aries",
    "Rohini": "Taurus", "Mrigashira": "Taurus",
    "Ardra": "Gemini", "Punarvasu": "Gemini",
    "Pushya": "Cancer", "Ashlesha": "Cancer",
    "Magha": "Leo", "Purva Phalguni": "Leo",
    "Uttara Phalguni": "Virgo", "Hasta": "Virgo",
    "Chitra": "Libra", "Swati": "Libra",
    "Vishakha": "Scorpio", "Anuradha": "Scorpio",
    "Jyeshtha": "Scorpio", "Mula": "Sagittarius",
    "Purva Ashadha": "Sagittarius", "Uttara Ashadha": "Capricorn",
    "Abhijit": "Capricorn", "Shravana": "Capricorn",
    "Dhanishtha": "Aquarius", "Shatabhisha": "Aquarius",
    "Purva Bhadrapada": "Pisces", "Uttara Bhadrapada": "Pisces",
    "Revati": "Pisces",
}

# Rashi lord mapping
RASHI_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Nakshatra lord mapping (Vimshottari)
NAKSHATRA_LORD = {
    "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun",
    "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
    "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
    "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
    "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
    "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshtha": "Mercury",
    "Mula": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
    "Abhijit": "Mercury", "Shravana": "Moon", "Dhanishtha": "Mars",
    "Shatabhisha": "Rahu", "Purva Bhadrapada": "Jupiter",
    "Uttara Bhadrapada": "Saturn", "Revati": "Mercury",
}

# Malefic / Benefic classification
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}

# Traditional Nakshatra Vedha Pairs (Classical)
# These are the well-known vedha obstruction pairs where
# one nakshatra blocks the other's transit benefits
TRADITIONAL_VEDHA_PAIRS = [
    ("Ashwini",            "Jyeshtha"),
    ("Bharani",            "Anuradha"),
    ("Krittika",           "Vishakha"),
    ("Rohini",             "Swati"),
    ("Mrigashira",         "Chitra"),
    ("Ardra",              "Shravana"),
    ("Punarvasu",          "Uttara Ashadha"),
    ("Pushya",             "Purva Ashadha"),
    ("Ashlesha",           "Mula"),
    ("Magha",              "Revati"),
    ("Purva Phalguni",     "Uttara Bhadrapada"),
    ("Uttara Phalguni",    "Purva Bhadrapada"),
    ("Hasta",              "Shatabhisha"),
    ("Dhanishtha",         "Dhanishtha"),  # Self-vedha special case
]

# Build bidirectional lookup from pairs
TRADITIONAL_VEDHA_PARTNER: Dict[str, str] = {}
for a, b in TRADITIONAL_VEDHA_PAIRS:
    TRADITIONAL_VEDHA_PARTNER[a] = b
    if a != b:
        TRADITIONAL_VEDHA_PARTNER[b] = a


# ─────────────────────────────────────────────────────────────
# SBC Grid-Based Vedha Computation
# ─────────────────────────────────────────────────────────────

# Build reverse lookup: nakshatra → (row, col) from OUTER_NAK_POSITIONS
_NAK_TO_POS: Dict[str, Tuple[int, int]] = {v: k for k, v in OUTER_NAK_POSITIONS.items()}

# Reverse rashi lookup
_RASHI_TO_POS: Dict[str, Tuple[int, int]] = {v: k for k, v in RASHI_CELL_MAP.items()}


def _get_vedha_cells_from_grid(row: int, col: int, grid_size: int = 9) -> Dict[str, List[Tuple[int, int]]]:
    """
    Get all cells vedha'd from position (row, col) in the SBC grid.
    Returns cells grouped by direction: horizontal, vertical, diagonal_main, diagonal_anti.
    """
    cells: Dict[str, List[Tuple[int, int]]] = {
        "horizontal": [],
        "vertical": [],
        "diagonal_main": [],
        "diagonal_anti": [],
    }

    # Horizontal (same row)
    for c in range(grid_size):
        if c != col:
            cells["horizontal"].append((row, c))

    # Vertical (same column)
    for r in range(grid_size):
        if r != row:
            cells["vertical"].append((r, col))

    # Main diagonal (top-left to bottom-right)
    r, c = row - min(row, col), col - min(row, col)
    while r < grid_size and c < grid_size:
        if (r, c) != (row, col):
            cells["diagonal_main"].append((r, c))
        r += 1
        c += 1

    # Anti-diagonal (top-right to bottom-left)
    r, c = row, col
    while r > 0 and c < grid_size - 1:
        r -= 1
        c += 1
    while r < grid_size and c >= 0:
        if (r, c) != (row, col):
            cells["diagonal_anti"].append((r, c))
        r += 1
        c -= 1

    return cells


def _identify_entity_at_cell(pos: Tuple[int, int]) -> Optional[Dict[str, Any]]:
    """Identify what entity sits at a given grid position."""
    r, c = pos

    # Check nakshatras
    nak = OUTER_NAK_POSITIONS.get((r, c))
    if nak:
        return {
            "type": "nakshatra",
            "name": nak,
            "rashi": NAKSHATRA_TO_RASHI.get(nak, ""),
            "nak_lord": NAKSHATRA_LORD.get(nak, ""),
            "position": (r, c),
        }

    # Check rashis
    rashi = RASHI_CELL_MAP.get((r, c))
    if rashi:
        return {
            "type": "rashi",
            "name": rashi,
            "lord": RASHI_LORD.get(rashi, ""),
            "position": (r, c),
        }

    return None


def get_sbc_vedha_for_nakshatra(nakshatra: str) -> Dict[str, Any]:
    """
    Get complete SBC grid-based vedha for a given nakshatra.
    Returns all nakshatras, rashis hit via row/column/diagonal.
    """
    pos = _NAK_TO_POS.get(nakshatra)
    if not pos:
        return {"nakshatra": nakshatra, "error": "Not found in SBC grid"}

    row, col = pos
    direction_cells = _get_vedha_cells_from_grid(row, col)

    vedha_nakshatras: List[Dict[str, Any]] = []
    vedha_rashis: List[Dict[str, Any]] = []

    direction_map = {
        "horizontal": "Row (Horizontal)",
        "vertical": "Column (Vertical)",
        "diagonal_main": "Diagonal (Main \\)",
        "diagonal_anti": "Diagonal (Anti /)",
    }

    for direction, cells in direction_cells.items():
        for cell_pos in cells:
            entity = _identify_entity_at_cell(cell_pos)
            if entity:
                entity["direction"] = direction_map[direction]
                entity["direction_key"] = direction
                if entity["type"] == "nakshatra":
                    vedha_nakshatras.append(entity)
                elif entity["type"] == "rashi":
                    vedha_rashis.append(entity)

    return {
        "nakshatra": nakshatra,
        "position": pos,
        "vedha_nakshatras": vedha_nakshatras,
        "vedha_rashis": vedha_rashis,
        "total_nakshatras_hit": len(vedha_nakshatras),
        "total_rashis_hit": len(vedha_rashis),
    }


# ─────────────────────────────────────────────────────────────
# Planet Vedha Report — Full Detail
# ─────────────────────────────────────────────────────────────

def get_planet_vedha_report(
    planet: str,
    transit_nakshatra: Optional[str] = None,
    planet_speed: Optional[float] = None,
    natal_planet_positions: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Generate comprehensive vedha report for a planet.

    Args:
        planet: Planet name (Sun, Moon, Mars, etc.)
        transit_nakshatra: Current transit nakshatra (if None, uses natural nakshatra)
        planet_speed: Current speed in deg/day (if None, uses average)
        natal_planet_positions: Dict of {planet_name: nakshatra} for natal chart

    Returns:
        Full vedha report with SBC grid vedha + traditional vedha pairs +
        direction + strength for all affected nakshatras and planets.
    """
    if transit_nakshatra is None:
        transit_nakshatra = PLANET_NATURAL_NAKSHATRA.get(planet, "Ashwini")

    if planet_speed is None:
        planet_speed = PLANET_AVG_SPEED.get(planet, 1.0)

    # 1. Classify vedha type based on speed
    vedha_class = classify_vedha_type(planet, planet_speed)
    vedha_mode = vedha_class["vedha_mode"]
    vedha_type = vedha_class["type"]
    strength_multiplier = VEDHA_STRENGTH_MULTIPLIER.get(vedha_type, 1.0)

    # 2. Get SBC grid-based vedha
    sbc_vedha = get_sbc_vedha_for_nakshatra(transit_nakshatra)

    # 3. Get traditional per-nakshatra vedha targets (Shlokas 19-47)
    traditional_targets = PER_NAKSHATRA_VEDHA_TARGETS.get(transit_nakshatra, {})
    vama_targets = traditional_targets.get("vama", [])
    dakshina_targets = traditional_targets.get("dakshina", [])
    sammukha_targets = traditional_targets.get("sammukha", [])

    # 4. Determine active vedha targets based on vedha mode
    active_targets: Dict[str, List[str]] = {}
    if vedha_mode in ("three_way", "sthana"):
        active_targets = {
            "vama": vama_targets,
            "dakshina": dakshina_targets,
            "sammukha": sammukha_targets,
        }
    elif vedha_mode == "left":
        active_targets = {"vama": vama_targets}
    elif vedha_mode == "right":
        active_targets = {"dakshina": dakshina_targets}
    elif vedha_mode == "front":
        active_targets = {"sammukha": sammukha_targets}

    # 5. Get traditional vedha pair
    trad_pair = TRADITIONAL_VEDHA_PARTNER.get(transit_nakshatra, None)

    # 6. Build detailed vedha list with affected planets
    vedha_detail: List[Dict[str, Any]] = []
    all_vedha_nakshatras: List[str] = []

    direction_labels = {
        "vama": "Vama (Left / baaI)",
        "dakshina": "Dakshina (Right / daahini)",
        "sammukha": "Sammukha (Front / saamne)",
    }

    for direction, targets in active_targets.items():
        for target_nak in targets:
            entry = {
                "nakshatra": target_nak,
                "direction": direction_labels.get(direction, direction),
                "direction_key": direction,
                "rashi": NAKSHATRA_TO_RASHI.get(target_nak, ""),
                "rashi_lord": RASHI_LORD.get(NAKSHATRA_TO_RASHI.get(target_nak, ""), ""),
                "nak_lord": NAKSHATRA_LORD.get(target_nak, ""),
                "vedha_type": vedha_type,
                "strength": vedha_class["strength"],
                "strength_multiplier": strength_multiplier,
                "nature": "Papa" if planet in MALEFICS else "Shubha",
                "affected_natal_planets": [],
            }

            # Check if any natal planet sits in this nakshatra
            if natal_planet_positions:
                for natal_planet, natal_nak in natal_planet_positions.items():
                    if natal_nak == target_nak:
                        entry["affected_natal_planets"].append({
                            "planet": natal_planet,
                            "natal_nakshatra": natal_nak,
                            "effect": (
                                f"{planet} (Papa) vedha on natal {natal_planet} - Obstruction/Challenge"
                                if planet in MALEFICS
                                else f"{planet} (Shubha) vedha on natal {natal_planet} - Support/Benefit"
                            ),
                        })

            vedha_detail.append(entry)
            all_vedha_nakshatras.append(target_nak)

    # 7. SBC grid vedha nakshatras (geometric)
    sbc_nakshatras = [
        {
            "nakshatra": v["name"],
            "direction": v["direction"],
            "rashi": NAKSHATRA_TO_RASHI.get(v["name"], ""),
            "nak_lord": NAKSHATRA_LORD.get(v["name"], ""),
        }
        for v in sbc_vedha.get("vedha_nakshatras", [])
    ]

    # 8. SBC grid vedha rashis
    sbc_rashis = [
        {
            "rashi": v["name"],
            "direction": v["direction"],
            "lord": v.get("lord", ""),
        }
        for v in sbc_vedha.get("vedha_rashis", [])
    ]

    return {
        "planet": planet,
        "transit_nakshatra": transit_nakshatra,
        "transit_rashi": NAKSHATRA_TO_RASHI.get(transit_nakshatra, ""),
        "planet_speed": planet_speed,
        "nature": "Papa (Malefic)" if planet in MALEFICS else "Shubha (Benefic)",
        "vedha_classification": vedha_class,
        "grid_position": sbc_vedha.get("position"),

        # Traditional directional vedha (Shlokas 19-47)
        "traditional_vedha": {
            "active_directions": list(active_targets.keys()),
            "vama_targets": vama_targets,
            "dakshina_targets": dakshina_targets,
            "sammukha_targets": sammukha_targets,
            "all_active_targets": all_vedha_nakshatras,
            "detail": vedha_detail,
        },

        # Traditional vedha pair
        "traditional_vedha_pair": {
            "partner_nakshatra": trad_pair,
            "description": (
                f"{transit_nakshatra} <-> {trad_pair}: mutual vedha obstruction"
                if trad_pair else "No traditional vedha pair"
            ),
        },

        # SBC grid geometric vedha
        "sbc_grid_vedha": {
            "vedha_nakshatras": sbc_nakshatras,
            "vedha_rashis": sbc_rashis,
            "total_nakshatras": len(sbc_nakshatras),
            "total_rashis": len(sbc_rashis),
        },
    }


def get_lagna_vedha_report(
    lagna_nakshatra: str,
    natal_planet_positions: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Generate vedha report for Lagna (Ascendant).
    Lagna is treated like a benefic point; vedha from malefics is harmful,
    vedha from benefics is supportive.
    """
    # Lagna doesn't have speed — treat as stationary point
    sbc_vedha = get_sbc_vedha_for_nakshatra(lagna_nakshatra)

    traditional_targets = PER_NAKSHATRA_VEDHA_TARGETS.get(lagna_nakshatra, {})
    vama_targets = traditional_targets.get("vama", [])
    dakshina_targets = traditional_targets.get("dakshina", [])
    sammukha_targets = traditional_targets.get("sammukha", [])

    # Lagna receives vedha — find which transit planets vedha the lagna
    all_targets = list(set(vama_targets + dakshina_targets + sammukha_targets))

    # Build which planets affect lagna via vedha
    planets_vedha_to_lagna: List[Dict[str, Any]] = []
    if natal_planet_positions:
        for p_name, p_nak in natal_planet_positions.items():
            # Check if this planet's nakshatra vedhas the lagna nakshatra
            p_targets = PER_NAKSHATRA_VEDHA_TARGETS.get(p_nak, {})
            p_all = list(set(
                p_targets.get("vama", []) +
                p_targets.get("dakshina", []) +
                p_targets.get("sammukha", [])
            ))
            if lagna_nakshatra in p_all:
                direction_hit = []
                if lagna_nakshatra in p_targets.get("vama", []):
                    direction_hit.append("Vama")
                if lagna_nakshatra in p_targets.get("dakshina", []):
                    direction_hit.append("Dakshina")
                if lagna_nakshatra in p_targets.get("sammukha", []):
                    direction_hit.append("Sammukha")

                planets_vedha_to_lagna.append({
                    "planet": p_name,
                    "from_nakshatra": p_nak,
                    "direction": ", ".join(direction_hit),
                    "nature": "Papa" if p_name in MALEFICS else "Shubha",
                    "effect": (
                        f"{p_name} (Malefic) vedha on Lagna - Health/personality challenges"
                        if p_name in MALEFICS
                        else f"{p_name} (Benefic) vedha on Lagna - Support/enhancement"
                    ),
                })

    trad_pair = TRADITIONAL_VEDHA_PARTNER.get(lagna_nakshatra, None)

    # SBC grid nakshatras
    sbc_nakshatras = [
        {
            "nakshatra": v["name"],
            "direction": v["direction"],
            "rashi": NAKSHATRA_TO_RASHI.get(v["name"], ""),
            "nak_lord": NAKSHATRA_LORD.get(v["name"], ""),
        }
        for v in sbc_vedha.get("vedha_nakshatras", [])
    ]

    sbc_rashis = [
        {
            "rashi": v["name"],
            "direction": v["direction"],
            "lord": v.get("lord", ""),
        }
        for v in sbc_vedha.get("vedha_rashis", [])
    ]

    return {
        "entity": "Lagna (Ascendant)",
        "lagna_nakshatra": lagna_nakshatra,
        "lagna_rashi": NAKSHATRA_TO_RASHI.get(lagna_nakshatra, ""),

        "traditional_vedha": {
            "vama_targets": vama_targets,
            "dakshina_targets": dakshina_targets,
            "sammukha_targets": sammukha_targets,
            "all_targets": all_targets,
        },

        "traditional_vedha_pair": {
            "partner_nakshatra": trad_pair,
            "description": (
                f"{lagna_nakshatra} <-> {trad_pair}: mutual vedha obstruction"
                if trad_pair else "No traditional vedha pair"
            ),
        },

        "planets_making_vedha_to_lagna": planets_vedha_to_lagna,

        "sbc_grid_vedha": {
            "vedha_nakshatras": sbc_nakshatras,
            "vedha_rashis": sbc_rashis,
            "total_nakshatras": len(sbc_nakshatras),
            "total_rashis": len(sbc_rashis),
        },
    }


def get_all_vedha_reports(
    transit_positions: Optional[Dict[str, str]] = None,
    planet_speeds: Optional[Dict[str, float]] = None,
    natal_planet_positions: Optional[Dict[str, str]] = None,
    lagna_nakshatra: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate vedha reports for all 9 planets + Lagna.

    Args:
        transit_positions: {planet: nakshatra} for current transits
        planet_speeds: {planet: speed_deg_per_day}
        natal_planet_positions: {planet: nakshatra} for natal chart
        lagna_nakshatra: Ascendant nakshatra

    Returns:
        Complete vedha reference for all planets and lagna.
    """
    if transit_positions is None:
        transit_positions = PLANET_NATURAL_NAKSHATRA.copy()
    if planet_speeds is None:
        planet_speeds = PLANET_AVG_SPEED.copy()

    reports: Dict[str, Any] = {"planets": {}, "lagna": None, "summary": {}}

    total_papa_vedhas = 0
    total_shubha_vedhas = 0

    for planet in PLANETS_9:
        nak = transit_positions.get(planet, PLANET_NATURAL_NAKSHATRA.get(planet, "Ashwini"))
        speed = planet_speeds.get(planet, PLANET_AVG_SPEED.get(planet, 1.0))

        report = get_planet_vedha_report(
            planet=planet,
            transit_nakshatra=nak,
            planet_speed=speed,
            natal_planet_positions=natal_planet_positions,
        )
        reports["planets"][planet] = report

        # Count vedhas
        n_targets = len(report["traditional_vedha"]["all_active_targets"])
        if planet in MALEFICS:
            total_papa_vedhas += n_targets
        else:
            total_shubha_vedhas += n_targets

    # Lagna report
    if lagna_nakshatra:
        reports["lagna"] = get_lagna_vedha_report(
            lagna_nakshatra=lagna_nakshatra,
            natal_planet_positions=transit_positions,
        )

    reports["summary"] = {
        "total_papa_vedhas": total_papa_vedhas,
        "total_shubha_vedhas": total_shubha_vedhas,
        "net_vedha_score": total_shubha_vedhas - total_papa_vedhas,
        "vedha_balance": (
            "Strongly Negative" if (total_shubha_vedhas - total_papa_vedhas) < -10 else
            "Negative" if (total_shubha_vedhas - total_papa_vedhas) < -3 else
            "Neutral" if abs(total_shubha_vedhas - total_papa_vedhas) <= 3 else
            "Positive" if (total_shubha_vedhas - total_papa_vedhas) <= 10 else
            "Strongly Positive"
        ),
    }

    return reports


# ─────────────────────────────────────────────────────────────
# Static Reference Tables — for Excel/reference output
# ─────────────────────────────────────────────────────────────

def generate_static_vedha_table() -> List[Dict[str, Any]]:
    """
    Generate a flat reference table of all vedha mappings
    for all 28 nakshatras. Used for Excel export.

    Each row: Source Nakshatra | Direction | Target Nakshatra |
              Target Rashi | Target Nak Lord | Traditional Pair
    """
    rows: List[Dict[str, Any]] = []

    for nak in NAKSHATRAS_28:
        targets = PER_NAKSHATRA_VEDHA_TARGETS.get(nak, {})
        trad_pair = TRADITIONAL_VEDHA_PARTNER.get(nak, "")

        # SBC grid vedha
        sbc = get_sbc_vedha_for_nakshatra(nak)

        for direction in ["vama", "dakshina", "sammukha"]:
            dir_label = {
                "vama": "Vama (Left)",
                "dakshina": "Dakshina (Right)",
                "sammukha": "Sammukha (Front)",
            }[direction]

            for target in targets.get(direction, []):
                rows.append({
                    "source_nakshatra": nak,
                    "source_rashi": NAKSHATRA_TO_RASHI.get(nak, ""),
                    "source_nak_lord": NAKSHATRA_LORD.get(nak, ""),
                    "direction": dir_label,
                    "direction_key": direction,
                    "target_nakshatra": target,
                    "target_rashi": NAKSHATRA_TO_RASHI.get(target, ""),
                    "target_nak_lord": NAKSHATRA_LORD.get(target, ""),
                    "traditional_pair": trad_pair,
                    "sbc_grid_nakshatras_hit": sbc.get("total_nakshatras_hit", 0),
                    "sbc_grid_rashis_hit": sbc.get("total_rashis_hit", 0),
                })

    return rows


def generate_planet_vedha_summary_table() -> List[Dict[str, Any]]:
    """
    Generate a summary table: for each planet (at its natural nakshatra),
    list all vedha targets with full detail.
    """
    rows: List[Dict[str, Any]] = []

    for planet in PLANETS_9:
        nak = PLANET_NATURAL_NAKSHATRA[planet]
        speed = PLANET_AVG_SPEED.get(planet, 1.0)
        vedha_class = classify_vedha_type(planet, speed)

        targets = PER_NAKSHATRA_VEDHA_TARGETS.get(nak, {})
        trad_pair = TRADITIONAL_VEDHA_PARTNER.get(nak, "")

        for direction in ["vama", "dakshina", "sammukha"]:
            dir_label = {
                "vama": "Vama (Left)",
                "dakshina": "Dakshina (Right)",
                "sammukha": "Sammukha (Front)",
            }[direction]

            for target in targets.get(direction, []):
                rows.append({
                    "planet": planet,
                    "nature": "Papa" if planet in MALEFICS else "Shubha",
                    "transit_nakshatra": nak,
                    "transit_rashi": NAKSHATRA_TO_RASHI.get(nak, ""),
                    "vedha_type": vedha_class["type"],
                    "vedha_strength": vedha_class["strength"],
                    "strength_multiplier": VEDHA_STRENGTH_MULTIPLIER.get(vedha_class["type"], 1.0),
                    "direction": dir_label,
                    "target_nakshatra": target,
                    "target_rashi": NAKSHATRA_TO_RASHI.get(target, ""),
                    "target_nak_lord": NAKSHATRA_LORD.get(target, ""),
                    "traditional_pair": trad_pair,
                    "effect_type": (
                        "Obstruction/Challenge" if planet in MALEFICS else "Support/Benefit"
                    ),
                })

    return rows


# ─────────────────────────────────────────────────────────────
# Convenience: Quick lookup functions
# ─────────────────────────────────────────────────────────────

def which_nakshatras_does_planet_vedha(planet: str, nakshatra: str) -> Dict[str, List[str]]:
    """Quick lookup: given planet in nakshatra, which nakshatras does it vedha?"""
    targets = PER_NAKSHATRA_VEDHA_TARGETS.get(nakshatra, {})
    speed = PLANET_AVG_SPEED.get(planet, 1.0)
    vedha_class = classify_vedha_type(planet, speed)
    mode = vedha_class["vedha_mode"]

    if mode in ("three_way", "sthana"):
        return {
            "vama": targets.get("vama", []),
            "dakshina": targets.get("dakshina", []),
            "sammukha": targets.get("sammukha", []),
        }
    elif mode == "left":
        return {"vama": targets.get("vama", [])}
    elif mode == "right":
        return {"dakshina": targets.get("dakshina", [])}
    elif mode == "front":
        return {"sammukha": targets.get("sammukha", [])}
    return {}


def which_planets_are_vedha_to(
    target_nakshatra: str,
    transit_positions: Dict[str, str],
) -> List[Dict[str, Any]]:
    """
    Reverse lookup: given a target nakshatra, which transit planets
    are currently making vedha to it?
    """
    result: List[Dict[str, Any]] = []

    for planet, p_nak in transit_positions.items():
        targets = PER_NAKSHATRA_VEDHA_TARGETS.get(p_nak, {})
        all_targets = list(set(
            targets.get("vama", []) +
            targets.get("dakshina", []) +
            targets.get("sammukha", [])
        ))

        if target_nakshatra in all_targets:
            direction = []
            if target_nakshatra in targets.get("vama", []):
                direction.append("Vama")
            if target_nakshatra in targets.get("dakshina", []):
                direction.append("Dakshina")
            if target_nakshatra in targets.get("sammukha", []):
                direction.append("Sammukha")

            result.append({
                "planet": planet,
                "from_nakshatra": p_nak,
                "direction": ", ".join(direction),
                "nature": "Papa" if planet in MALEFICS else "Shubha",
            })

    return result


# ─────────────────────────────────────────────────────────────
# Demo / CLI
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("=" * 80)
    print("VEDHA REFERENCE — All 9 Planets + Lagna")
    print("=" * 80)

    for planet in PLANETS_9:
        report = get_planet_vedha_report(planet)
        print(f"\n{'─' * 60}")
        print(f" {planet} in {report['transit_nakshatra']} ({report['transit_rashi']})")
        print(f" Nature: {report['nature']}")
        print(f" Vedha Type: {report['vedha_classification']['type']}")
        print(f" Strength: {report['vedha_classification']['strength']}")
        print(f"{'─' * 60}")

        trad = report["traditional_vedha"]
        if trad["vama_targets"]:
            print(f"  Vama (Left):      {', '.join(trad['vama_targets'])}")
        if trad["dakshina_targets"]:
            print(f"  Dakshina (Right):  {', '.join(trad['dakshina_targets'])}")
        if trad["sammukha_targets"]:
            print(f"  Sammukha (Front):  {', '.join(trad['sammukha_targets'])}")

        pair = report["traditional_vedha_pair"]
        if pair["partner_nakshatra"]:
            print(f"  Traditional Pair:  {pair['description']}")

        sbc = report["sbc_grid_vedha"]
        print(f"  SBC Grid: {sbc['total_nakshatras']} nakshatras, {sbc['total_rashis']} rashis hit")

    print(f"\n{'=' * 80}")
    print("LAGNA (Ascendant) — Example: Ashwini")
    print("=" * 80)
    lagna = get_lagna_vedha_report("Ashwini")
    print(json.dumps(lagna, indent=2, default=str))
