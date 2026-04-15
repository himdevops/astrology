"""
sbc_analysis.py — Advanced Sarvatobhadra Chakra Analysis Engine
Implements:
  • Vedha (obstruction aspects: row/column/diagonal)
  • Latta (planetary kicks on specific nakshatras)
  • Six Personal Bindus (Janma, Karma, Sanghatika, Uday, Adhan, Vinash)
  • Navatara system (9 tara categories from Janma nakshatra)
  • Transit SBC analysis with Shubha/Papa vedha quality
  • Planet-speed-based Vedha type (Dakshina/Vama/Prishtha)
  • Vedha line data for visual rendering in the UI
  • NSE/BSE market signal derived from SBC state
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────
# Planet average speeds (degrees/day) for Vedha type classification
# ─────────────────────────────────────────────────────────────
PLANET_AVG_SPEED: Dict[str, float] = {
    "Sun":     1.000,
    "Moon":    13.176,
    "Mars":    0.524,
    "Mercury": 1.383,
    "Jupiter": 0.083,
    "Venus":   1.200,
    "Saturn":  0.034,
    "Rahu":    0.053,
    "Ketu":    0.053,
}

# Vedha type based on planet speed
# Dakshina = direct normal → full cross + diagonals (standard)
# Vama     = atichar (fast >1.5× avg) → extra strong, opposite emphasis
# Prishtha = retrograde → rear/behind direction emphasis
# Sthana   = near-stationary (< 0.1×avg) → concentrated, very strong


def classify_vedha_type(planet: str, speed: float) -> Dict:
    """
    Classify the type of Vedha based on planet speed.
    Returns type name, description, and line style hints for the UI.
    """
    avg = PLANET_AVG_SPEED.get(planet, 1.0)
    abs_speed = abs(speed)

    if speed < 0:
        return {
            "type":        "Prishtha Vedha",
            "description": "Retrograde — rear/hind vedha; aspects in reverse direction; very strong, inward effect",
            "direction":   "backward",
            "strength":    "strong",
            "line_style":  "dashed",
            "color_mod":   0.8,   # slightly dimmer
        }
    if abs_speed < avg * 0.1:
        return {
            "type":        "Sthana Vedha",
            "description": "Near-stationary — about to turn retrograde; concentrated, maximum intensity vedha",
            "direction":   "stationary",
            "strength":    "maximum",
            "line_style":  "double",
            "color_mod":   1.2,
        }
    if abs_speed > avg * 1.5:
        return {
            "type":        "Vama Vedha",
            "description": "Atichar (extra fast) — left/opposite vedha; disruptive, sudden effects",
            "direction":   "accelerated",
            "strength":    "intense",
            "line_style":  "thick",
            "color_mod":   1.0,
        }
    return {
        "type":        "Dakshina Vedha",
        "description": "Direct normal speed — standard right vedha; steady, measured effects",
        "direction":   "forward",
        "strength":    "normal",
        "line_style":  "solid",
        "color_mod":   1.0,
    }

# ─────────────────────────────────────────────────────────────
# Nakshatra sequence (0-indexed, Ashwini=0 … Revati=26)
# ─────────────────────────────────────────────────────────────
NAKSHATRAS_27: List[str] = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati",
]
NAK_INDEX: Dict[str, int] = {n: i for i, n in enumerate(NAKSHATRAS_27)}

# Abhijit is the special 28th; treat as equivalent to Uttara Ashadha for counting
_ABHIJIT_EQUIV = "Uttara Ashadha"


def _nak_idx(name: str) -> int:
    if name == "Abhijit":
        name = _ABHIJIT_EQUIV
    return NAK_INDEX.get(name, 0)


def nak_at_offset(from_nak: str, offset: int, direction: str = "forward") -> str:
    """
    Return the nakshatra at `offset` positions from `from_nak`.
    direction: 'forward' (increasing index) or 'backward' (decreasing).
    Offset is 0-based (offset=0 returns from_nak itself).
    """
    idx = _nak_idx(from_nak)
    if direction == "forward":
        return NAKSHATRAS_27[(idx + offset) % 27]
    else:
        return NAKSHATRAS_27[(idx - offset) % 27]


# ─────────────────────────────────────────────────────────────
# Navatara — 9 Tara categories from Janma Nakshatra
# ─────────────────────────────────────────────────────────────
NAVATARA_DEF: List[Tuple[str, str, str]] = [
    ("Janma",      "neutral",      "Birth star — sensitive, pivotal"),
    ("Sampat",     "auspicious",   "Prosperity — favorable transits"),
    ("Vipat",      "inauspicious", "Obstacle/danger — beware"),
    ("Kshema",     "auspicious",   "Welfare — good transits"),
    ("Pratyari",   "inauspicious", "Enemy star — unfavorable"),
    ("Sadhaka",    "auspicious",   "Achievement — success"),
    ("Naidhana",   "inauspicious", "Death/destruction — avoid"),
    ("Mitra",      "auspicious",   "Friend star — beneficial"),
    ("Adhi Mitra", "auspicious",   "Best friend — most favorable"),
]


def calc_navatara(janma_nak: str) -> Dict[str, Dict]:
    """
    For each of the 27 nakshatras, return its Tara relationship
    to the Janma Nakshatra.
    """
    result: Dict[str, Dict] = {}
    j = _nak_idx(janma_nak)
    for i, nak in enumerate(NAKSHATRAS_27):
        dist = (i - j) % 27           # 0-based offset from janma
        tara_idx = dist % 9           # which of the 9 taras
        name, quality, desc = NAVATARA_DEF[tara_idx]
        result[nak] = {
            "tara":        name,
            "quality":     quality,
            "description": desc,
            "offset_from_janma": dist + 1,   # 1-based as in texts
        }
    return result


# ─────────────────────────────────────────────────────────────
# Six Personal Bindus (identifiers) from Janma Nakshatra
# ─────────────────────────────────────────────────────────────
SIX_BINDUS_DEF: Dict[str, int] = {
    "Janma":      0,   # 1st  (Moon's natal nakshatra)
    "Karma":      9,   # 10th
    "Sanghatika": 15,  # 16th
    "Uday":       17,  # 18th
    "Adhan":      18,  # 19th
    "Vinash":     22,  # 23rd
}


def calc_six_bindus(janma_nak: str) -> Dict[str, Dict]:
    """Return the six personal bindus (sensitive nakshatras) from Janma."""
    result: Dict[str, Dict] = {}
    for bindu_name, offset in SIX_BINDUS_DEF.items():
        nak = nak_at_offset(janma_nak, offset, "forward")
        result[bindu_name] = {
            "nakshatra":   nak,
            "offset":      offset + 1,
            "description": _BINDU_DESC[bindu_name],
        }
    return result


_BINDU_DESC: Dict[str, str] = {
    "Janma":      "Moon's birth nakshatra — most sensitive personal point",
    "Karma":      "10th from Janma — career and action axis",
    "Sanghatika": "16th from Janma — collective/community karma",
    "Uday":       "18th from Janma — rising/manifestation point",
    "Adhan":      "19th from Janma — conception nakshatra",
    "Vinash":     "23rd from Janma — danger/destruction point",
}


# ─────────────────────────────────────────────────────────────
# Vedha Line Data for UI Rendering
# Returns the start/end grid coordinates for every vedha line
# ─────────────────────────────────────────────────────────────

def get_vedha_lines(
    planet_name: str,
    row: int,
    col: int,
    speed: float,
    grid_size: int = 9,
) -> Dict:
    """
    Return all vedha line segments for a planet at (row, col).
    Each line is a dict with from/to grid coordinates.
    Lines:
      1. Horizontal  — full row through (row, col)
      2. Vertical    — full column through (row, col)
      3. Diagonal ↘  — top-left to bottom-right diagonal
      4. Diagonal ↗  — top-right to bottom-left diagonal

    The vedha_type tells the UI which line style to use:
      - Dakshina (direct normal): solid
      - Vama     (atichar/fast):  thick
      - Prishtha (retrograde):    dashed
      - Sthana   (stationary):    double
    """
    vedha_info = classify_vedha_type(planet_name, speed)

    # Endpoints for horizontal line
    h_line = {
        "type": "horizontal",
        "from": [row, 0],
        "to":   [row, grid_size - 1],
    }

    # Endpoints for vertical line
    v_line = {
        "type": "vertical",
        "from": [0,   col],
        "to":   [grid_size - 1, col],
    }

    # Diagonal ↘ (top-left → bottom-right) — find endpoints
    step = min(row, col)
    d1_r0, d1_c0 = row - step, col - step
    steps_to_end = min(grid_size - 1 - d1_r0, grid_size - 1 - d1_c0)
    d1_r1, d1_c1 = d1_r0 + steps_to_end, d1_c0 + steps_to_end
    d1_line = {
        "type": "diagonal_main",
        "from": [d1_r0, d1_c0],
        "to":   [d1_r1, d1_c1],
    }

    # Diagonal ↗ (top-right → bottom-left) — find endpoints
    step_up = min(row, grid_size - 1 - col)
    d2_r0, d2_c0 = row - step_up, col + step_up
    steps_dn = min(grid_size - 1 - d2_r0, d2_c0)
    d2_r1, d2_c1 = d2_r0 + steps_dn, d2_c0 - steps_dn
    d2_line = {
        "type": "diagonal_anti",
        "from": [d2_r0, d2_c0],
        "to":   [d2_r1, d2_c1],
    }

    return {
        "planet":       planet_name,
        "position":     [row, col],
        "speed":        round(speed, 4),
        "vedha_type":   vedha_info["type"],
        "direction":    vedha_info["direction"],
        "strength":     vedha_info["strength"],
        "line_style":   vedha_info["line_style"],
        "description":  vedha_info["description"],
        "lines":        [h_line, v_line, d1_line, d2_line],
    }


# ─────────────────────────────────────────────────────────────
# Latta — Planetary Kicks
# Rules: the transiting planet "kicks" a nakshatra at a fixed
# offset. If the kicked nakshatra is a personal bindu or Janma,
# the native feels the latta effect.
# ─────────────────────────────────────────────────────────────
LATTA_RULES: Dict[str, Tuple[str, int]] = {
    # Traditional Vedic counting is INCLUSIVE (planet's own star = 1st)
    # So "nth nakshatra from planet" = offset of (n-1) in 0-based index
    "Sun":     ("forward",   11),   # 12th forward (inclusive) = +11
    "Mars":    ("forward",    2),   # 3rd forward  (inclusive) = +2
    "Jupiter": ("forward",    5),   # 6th forward  (inclusive) = +5
    "Saturn":  ("forward",    7),   # 8th forward  (inclusive) = +7
    "Venus":   ("backward",   4),   # 5th backward (inclusive) = -4
    "Mercury": ("backward",   6),   # 7th backward (inclusive) = -6
    "Rahu":    ("backward",   8),   # 9th backward (inclusive) = -8
    "Ketu":    ("backward",   8),   # 9th backward (inclusive) = -8
    "Moon":    ("backward",  21),   # 22nd backward (inclusive) = -21
}

LATTA_EFFECTS: Dict[str, str] = {
    "Sun":     "Financial loss in every venture; setbacks from authority",
    "Moon":    "Excessive financial loss; emotional disturbances",
    "Mars":    "Wounds, injuries, property disputes, impulsive losses",
    "Mercury": "Loss of position, status, and reputation",
    "Jupiter": "Loss of wisdom, prestige, and good fortune",
    "Venus":   "Quarrels, discord, relationship disruptions",
    "Saturn":  "Disease, sorrow, chronic delays, legal issues",
    "Rahu":    "Grief, unhappiness, deception, unexpected shocks",
    "Ketu":    "Confusion, accidents, hidden problems, isolation",
}

LATTA_FINANCIAL: Dict[str, str] = {
    "Sun":     "PSU/Govt stocks impacted; avoid large trades",
    "Moon":    "Consumer/FMCG stocks down; market emotionally weak",
    "Mars":    "Defense/Real estate sector under pressure",
    "Mercury": "IT/Telecom sector underperformance expected",
    "Jupiter": "Banking/Finance sector risk; avoid long positions",
    "Venus":   "FMCG/Luxury sector volatile",
    "Saturn":  "Infrastructure/Oil under sustained pressure",
    "Rahu":    "Tech/Foreign stocks crash risk",
    "Ketu":    "Pharma/Chemicals sector uncertain",
}


def calc_latta_for_planet(
    planet_name: str,
    transiting_nak: str,
    retrograde: bool = False,
) -> Dict:
    """
    Calculate which nakshatra this planet is currently kicking (Latta).
    Retrograde planets reverse their Latta direction.
    """
    if planet_name not in LATTA_RULES:
        return {}
    direction, offset = LATTA_RULES[planet_name]
    # Retrograde reverses direction
    if retrograde:
        direction = "backward" if direction == "forward" else "forward"

    kicked_nak = nak_at_offset(transiting_nak, offset, direction)
    return {
        "planet":       planet_name,
        "transiting":   transiting_nak,
        "latta_offset": offset,
        "direction":    direction,
        "kicked_nakshatra": kicked_nak,
        "effect":       LATTA_EFFECTS.get(planet_name, ""),
        "nse_impact":   LATTA_FINANCIAL.get(planet_name, ""),
        "retrograde":   retrograde,
    }


# ─────────────────────────────────────────────────────────────
# Vedha — Grid Aspects
# Each cell (row, col) vedhas (aspects):
#   • Its entire row (horizontal)
#   • Its entire column (vertical)
#   • Both diagonals through it
# ─────────────────────────────────────────────────────────────
BENEFIC_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFIC_PLANETS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

VEDHA_EFFECTS: Dict[str, str] = {
    "Sun":     "Grief, sorrow, setbacks from authority",
    "Moon":    "Mixed results — both good and bad",
    "Mars":    "Loss of wealth, property damage, disputes",
    "Mercury": "Sharpening of intellect, mental activity",
    "Jupiter": "Many gains, good happenings, prosperity",
    "Venus":   "Fear from enemies, relationship issues",
    "Saturn":  "Pain, chronic ailments, prolonged obstacles",
    "Rahu":    "Obstructions, sudden shocks, deception",
    "Ketu":    "Confusion, accidents, spiritual disruption",
}

VEDHA_MULTIPLE_EFFECTS: Dict[int, str] = {
    1: "Conflict and misunderstanding",
    2: "Loss of wealth and financial setbacks",
    3: "Defeat or significant failure",
    4: "Severe consequences — maximum caution",
}

VEDHA_FINANCIAL: Dict[str, Dict] = {
    "Jupiter": {"signal": "BULLISH", "score":  0.7, "impact": "Banking/Finance gains"},
    "Venus":   {"signal": "BULLISH", "score":  0.6, "impact": "FMCG/Luxury sector gains"},
    "Mercury": {"signal": "BULLISH", "score":  0.5, "impact": "IT/Commerce sector active"},
    "Moon":    {"signal": "NEUTRAL", "score":  0.3, "impact": "Consumer sentiment mixed"},
    "Sun":     {"signal": "CAUTION", "score": -0.2, "impact": "PSU sector under pressure"},
    "Mars":    {"signal": "BEARISH", "score": -0.5, "impact": "Market energy disrupted"},
    "Saturn":  {"signal": "BEARISH", "score": -0.4, "impact": "Structural market slowdown"},
    "Rahu":    {"signal": "BEARISH", "score": -0.6, "impact": "Tech/Foreign stocks volatile"},
    "Ketu":    {"signal": "BEARISH", "score": -0.5, "impact": "Pharma/Chemicals uncertain"},
}


def get_vedha_cells(row: int, col: int, grid_size: int = 9) -> Dict[str, List[Tuple[int,int]]]:
    """
    Return all cells that are under vedha from position (row, col).
    Returns 4 categories: horizontal, vertical, diagonal1, diagonal2.
    """
    horizontal = [(row, c) for c in range(grid_size) if c != col]
    vertical   = [(r, col) for r in range(grid_size) if r != row]

    # Diagonal top-left to bottom-right
    diag1: List[Tuple[int,int]] = []
    r, c = row, col
    while r > 0 and c > 0: r -= 1; c -= 1
    while r < grid_size and c < grid_size:
        if (r, c) != (row, col): diag1.append((r, c))
        r += 1; c += 1

    # Diagonal top-right to bottom-left
    diag2: List[Tuple[int,int]] = []
    r, c = row, col
    while r > 0 and c < grid_size - 1: r -= 1; c += 1
    while r < grid_size and c >= 0:
        if (r, c) != (row, col): diag2.append((r, c))
        r += 1; c -= 1
        if c < 0: break

    return {
        "horizontal": horizontal,
        "vertical":   vertical,
        "diagonal1":  diag1,
        "diagonal2":  diag2,
        "all":        list({*horizontal, *vertical, *diag1, *diag2}),
    }


# ─────────────────────────────────────────────────────────────
# Full SBC Transit Analysis
# ─────────────────────────────────────────────────────────────

def analyze_sbc_transits(
    janma_nak: str,
    natal_chakra_cells: List[Dict],
    transit_planets: List[Dict],
    nak_position_map: Dict[str, Tuple[int,int]],
) -> Dict:
    """
    Full SBC transit analysis.

    Args:
        janma_nak: Moon's birth nakshatra name
        natal_chakra_cells: flat list of all 81 cells from the chakra
        transit_planets: list of {"planet":..., "nakshatra":..., "retrograde":...}
        nak_position_map: nakshatra_name → (row, col) in the 9×9 grid

    Returns:
        Complete analysis dict with vedhas, lattas, bindu hits, navatara,
        NSE/BSE signal, and per-planet details.
    """
    six_bindus = calc_six_bindus(janma_nak)
    navatara   = calc_navatara(janma_nak)

    bindu_naks = {v["nakshatra"]: k for k, v in six_bindus.items()}

    # Build cell → entities lookup
    cell_entities: Dict[Tuple[int,int], List[str]] = {}
    for cell in natal_chakra_cells:
        key = (cell["row"], cell["col"])
        cell_entities[key] = [e["name"] for e in cell.get("entities", [])]

    planet_analyses: List[Dict] = []
    all_vedha_hits: List[Dict]  = []
    all_latta_hits: List[Dict]  = []

    overall_score = 0.0

    for tp in transit_planets:
        pname   = tp["planet"]
        nak     = tp.get("nakshatra", "")
        retro   = tp.get("retrograde", False)
        is_benefic = pname in BENEFIC_PLANETS
        fin    = VEDHA_FINANCIAL.get(pname, {"signal":"NEUTRAL","score":0,"impact":""})

        # ─ Latta ────────────────────────────────────────────
        latta = calc_latta_for_planet(pname, nak, retro)
        latta_hits: List[Dict] = []
        if latta:
            kicked = latta["kicked_nakshatra"]
            bindu_hit = bindu_naks.get(kicked)
            tara_info = navatara.get(kicked, {})
            severity = "CRITICAL" if bindu_hit in ("Janma","Vinash","Karma") else \
                       "HIGH"     if bindu_hit else \
                       "MODERATE" if tara_info.get("quality") == "inauspicious" else "LOW"
            if bindu_hit or tara_info.get("quality") == "inauspicious":
                latta_hit = {
                    "planet":         pname,
                    "transiting_nak": nak,
                    "kicked_nak":     kicked,
                    "bindu_type":     bindu_hit,
                    "tara":           tara_info.get("tara",""),
                    "tara_quality":   tara_info.get("quality",""),
                    "severity":       severity,
                    "effect":         latta["effect"],
                    "nse_impact":     latta["nse_impact"],
                    "nature":         "malefic_latta" if not is_benefic else "benefic_latta",
                    "retrograde":     retro,
                }
                latta_hits.append(latta_hit)
                all_latta_hits.append(latta_hit)
                if not is_benefic:
                    overall_score -= 0.3 if severity == "CRITICAL" else 0.15

        # ─ Speed-based Vedha type ────────────────────────────
        speed    = tp.get("speed", 0.0)
        vedha_type_info = classify_vedha_type(pname, speed)

        # ─ Vedha ────────────────────────────────────────────
        pos = nak_position_map.get(nak) or nak_position_map.get(
            tp.get("sign", ""))  # fallback to rashi cell
        vedha_hits: List[Dict] = []
        vedha_line_data: Optional[Dict] = None

        if pos:
            row, col = pos
            vedha_cells = get_vedha_cells(row, col)

            # Generate visual line data for the UI
            vedha_line_data = get_vedha_lines(pname, row, col, speed)

            for (vr, vc) in vedha_cells["all"]:
                entities = cell_entities.get((vr, vc), [])
                if not entities:
                    continue
                for entity_name in entities:
                    bindu_hit = bindu_naks.get(entity_name)
                    tara_info = navatara.get(entity_name, {})
                    if not bindu_hit and tara_info.get("quality") not in ("inauspicious",):
                        continue  # Only report significant hits
                    direction = _vedha_direction(row, col, vr, vc)
                    severity = "CRITICAL" if bindu_hit in ("Janma","Vinash","Karma") else \
                               "HIGH"     if bindu_hit else "MODERATE"
                    vedha_hit = {
                        "planet":        pname,
                        "from_nak":      nak,
                        "from_pos":      list(pos),
                        "to_entity":     entity_name,
                        "to_pos":        [vr, vc],
                        "bindu_type":    bindu_hit,
                        "tara":          tara_info.get("tara",""),
                        "tara_quality":  tara_info.get("quality",""),
                        "vedha_direction": direction,
                        "vedha_speed_type": vedha_type_info["type"],
                        "severity":      severity,
                        "nature":        "shubha_vedha" if is_benefic else "papa_vedha",
                        "effect":        VEDHA_EFFECTS.get(pname,""),
                        "nse_impact":    fin["impact"],
                        "retrograde":    retro,
                        "speed":         round(speed, 4),
                    }
                    vedha_hits.append(vedha_hit)
                    all_vedha_hits.append(vedha_hit)
                    if is_benefic:
                        overall_score += 0.25 if severity == "CRITICAL" else 0.12
                    else:
                        overall_score -= 0.25 if severity == "CRITICAL" else 0.12

        planet_analyses.append({
            "planet":          pname,
            "nakshatra":       nak,
            "retrograde":      retro,
            "speed":           round(speed, 4),
            "vedha_speed_type": vedha_type_info["type"],
            "vedha_direction": vedha_type_info["direction"],
            "vedha_strength":  vedha_type_info["strength"],
            "vedha_line_style":vedha_type_info["line_style"],
            "nature":          "benefic" if is_benefic else "malefic",
            "grid_position":   list(pos) if pos else None,
            "vedha_lines":     vedha_line_data,
            "latta":           latta if latta else {},
            "latta_hits":      latta_hits,
            "vedha_hits":      vedha_hits,
            "vedha_count":     len(vedha_hits),
            "financial":       fin,
        })
        overall_score += fin["score"] * 0.1

    # ─ Bindu summary ────────────────────────────────────────
    bindu_analysis = _analyze_bindus(six_bindus, all_vedha_hits, all_latta_hits)

    # ─ Market signal ────────────────────────────────────────
    overall_score = max(-1.0, min(1.0, overall_score))
    market_signal = _sbc_to_market_signal(overall_score, all_vedha_hits, all_latta_hits)

    # ─ Vedha count effects ───────────────────────────────────
    malefic_vedha_count = sum(
        1 for v in all_vedha_hits if v["nature"] == "papa_vedha" and
        v.get("bindu_type") in ("Janma","Karma","Vinash")
    )
    multiple_effect = VEDHA_MULTIPLE_EFFECTS.get(min(malefic_vedha_count, 4), "")

    # Collect all vedha lines for rendering
    vedha_lines_all = [
        pa["vedha_lines"] for pa in planet_analyses
        if pa.get("vedha_lines") is not None
    ]

    return {
        "janma_nakshatra":      janma_nak,
        "six_bindus":           six_bindus,
        "navatara":             navatara,
        "planet_analyses":      planet_analyses,
        "all_vedha_hits":       all_vedha_hits,
        "all_latta_hits":       all_latta_hits,
        "bindu_analysis":       bindu_analysis,
        "malefic_vedha_count":  malefic_vedha_count,
        "multiple_vedha_effect": multiple_effect,
        "overall_sbc_score":    round(overall_score, 3),
        "market_signal":        market_signal,
        "cells_under_vedha":   _cells_under_any_vedha(all_vedha_hits),
        "cells_with_latta":    _cells_with_latta(all_latta_hits, nak_position_map),
        "bindu_cells":          _bindu_cell_positions(six_bindus, nak_position_map),
        "vedha_lines_all":      vedha_lines_all,   # ← for Canvas rendering
    }


def _vedha_direction(fr: int, fc: int, tr: int, tc: int) -> str:
    if fr == tr:   return "horizontal"
    if fc == tc:   return "vertical"
    if (tr-fr) == (tc-fc): return "diagonal_main"
    return "diagonal_anti"


def _analyze_bindus(
    six_bindus: Dict, vedha_hits: List[Dict], latta_hits: List[Dict]
) -> List[Dict]:
    """Summarize the status of each of the 6 bindus."""
    result = []
    for bindu_name, info in six_bindus.items():
        nak = info["nakshatra"]
        v_hits = [v for v in vedha_hits if v.get("bindu_type") == bindu_name]
        l_hits = [l for l in latta_hits if l.get("bindu_type") == bindu_name]
        malefic_v = [v for v in v_hits if v["nature"] == "papa_vedha"]
        benefic_v = [v for v in v_hits if v["nature"] == "shubha_vedha"]
        status = ("AFFLICTED" if len(malefic_v) > len(benefic_v) + 1 else
                  "PROTECTED" if len(benefic_v) > 0 and len(malefic_v) == 0 else
                  "MIXED"     if (malefic_v or benefic_v) else "CLEAR")
        result.append({
            "bindu":          bindu_name,
            "nakshatra":      nak,
            "description":    info["description"],
            "status":         status,
            "malefic_vedhas": len(malefic_v),
            "benefic_vedhas": len(benefic_v),
            "latta_hits":     len(l_hits),
            "afflicting_planets": [v["planet"] for v in malefic_v],
            "protecting_planets": [v["planet"] for v in benefic_v],
        })
    return result


def _sbc_to_market_signal(
    score: float, vedha_hits: List[Dict], latta_hits: List[Dict]
) -> Dict:
    # Check Janma Nakshatra specifically
    janma_malefic = sum(1 for v in vedha_hits
                        if v.get("bindu_type") == "Janma" and v["nature"] == "papa_vedha")
    janma_latta   = sum(1 for l in latta_hits if l.get("bindu_type") == "Janma")
    vinash_hits   = sum(1 for v in vedha_hits if v.get("bindu_type") == "Vinash")

    if janma_malefic >= 2 or vinash_hits >= 2 or janma_latta >= 2:
        signal = "STRONGLY BEARISH"; color = "#FF3D00"; action = "Exit all positions"
    elif score >= 0.4:
        signal = "BULLISH";          color = "#00C851"; action = "Buy on dips"
    elif score >= 0.1:
        signal = "MILDLY BULLISH";   color = "#8BC34A"; action = "Selective accumulation"
    elif score >= -0.1:
        signal = "NEUTRAL";          color = "#FFC107"; action = "Hold — no new large entries"
    elif score >= -0.4:
        signal = "BEARISH";          color = "#FF5722"; action = "Reduce exposure"
    else:
        signal = "STRONGLY BEARISH"; color = "#FF3D00"; action = "Exit all positions"

    tips = []
    if janma_malefic > 0:
        tips.append(f"Janma nakshatra afflicted by {janma_malefic} malefic vedha(s)")
    if janma_latta > 0:
        tips.append(f"Active Latta on Janma nakshatra ({janma_latta} planet(s))")
    if vinash_hits > 0:
        tips.append(f"Vinash nakshatra under {vinash_hits} vedha(s) — high risk")

    return {"signal": signal, "color": color, "action": action,
            "score": round(score, 3), "warning_tips": tips}


def _cells_under_any_vedha(all_vedha_hits: List[Dict]) -> Dict[str, Dict]:
    """Map each cell position → all planets vedhaing it, and the net quality."""
    result: Dict[str, Dict] = {}
    for v in all_vedha_hits:
        key = f"{v['to_pos'][0]},{v['to_pos'][1]}"
        if key not in result:
            result[key] = {"row": v["to_pos"][0], "col": v["to_pos"][1],
                           "malefic": [], "benefic": [], "net": "neutral"}
        if v["nature"] == "papa_vedha":
            result[key]["malefic"].append(v["planet"])
        else:
            result[key]["benefic"].append(v["planet"])
    for key, d in result.items():
        m, b = len(d["malefic"]), len(d["benefic"])
        d["net"] = "malefic" if m > b else "benefic" if b > m else "mixed"
    return result


def _cells_with_latta(latta_hits: List[Dict],
                       nak_pos_map: Dict[str, Tuple[int,int]]) -> Dict[str, Dict]:
    result: Dict[str, Dict] = {}
    for l in latta_hits:
        nak = l["kicked_nak"]
        pos = nak_pos_map.get(nak)
        if not pos:
            continue
        key = f"{pos[0]},{pos[1]}"
        if key not in result:
            result[key] = {"row": pos[0], "col": pos[1], "planets": [], "nakshatra": nak}
        result[key]["planets"].append(l["planet"])
    return result


def _bindu_cell_positions(
    six_bindus: Dict, nak_pos_map: Dict[str, Tuple[int,int]]
) -> Dict[str, Dict]:
    result: Dict[str, Dict] = {}
    for bindu_name, info in six_bindus.items():
        nak = info["nakshatra"]
        pos = nak_pos_map.get(nak)
        if pos:
            result[bindu_name] = {"nakshatra": nak, "row": pos[0], "col": pos[1]}
    return result


# ─────────────────────────────────────────────────────────────
# NSE/BSE SBC Daily Signal
# ─────────────────────────────────────────────────────────────

def sbc_nse_daily_signal(
    janma_nak: str,
    transit_nak_map: Dict[str, str],   # planet → current nakshatra
    retrograde_map: Dict[str, bool],   # planet → is_retrograde
) -> Dict:
    """
    Quick daily NSE/BSE signal using just Latta + Navatara.
    Used for intraday/daily market signal without the full SBC grid.
    """
    navatara = calc_navatara(janma_nak)
    bindus   = calc_six_bindus(janma_nak)
    bindu_naks = {v["nakshatra"] for v in bindus.values()}

    active_lattas: List[Dict] = []
    active_vedha_naks: List[str] = []
    score = 0.0

    for planet, nak in transit_nak_map.items():
        retro = retrograde_map.get(planet, False)
        latta = calc_latta_for_planet(planet, nak, retro)
        if latta:
            kicked = latta["kicked_nakshatra"]
            tara = navatara.get(kicked, {})
            if kicked in bindu_naks or tara.get("quality") == "inauspicious":
                is_mal = planet in MALEFIC_PLANETS
                active_lattas.append({
                    "planet": planet, "kicked": kicked,
                    "tara": tara.get("tara",""), "quality": tara.get("quality",""),
                    "effect": LATTA_EFFECTS.get(planet,""),
                    "severity": "HIGH" if kicked in bindu_naks else "MODERATE",
                })
                score += -0.25 if is_mal else 0.15

        # Tara of transiting nakshatra
        tara_of_transit = navatara.get(nak, {})
        if tara_of_transit.get("quality") == "auspicious" and planet in BENEFIC_PLANETS:
            score += 0.1
        elif tara_of_transit.get("quality") == "inauspicious" and planet in MALEFIC_PLANETS:
            score -= 0.1
            active_vedha_naks.append(nak)

    score = max(-1.0, min(1.0, score))
    return {
        "janma_nakshatra":  janma_nak,
        "overall_score":    round(score, 3),
        "active_lattas":    active_lattas,
        "active_vedha_naks": active_vedha_naks,
        "market_signal":    _sbc_to_market_signal(score, [], active_lattas),
    }
