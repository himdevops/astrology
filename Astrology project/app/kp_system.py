"""
kp_system.py — Advanced Krishnamurti Paddhati (KP) System
==========================================================

Complete implementation of KP Astrology with:

1. **KP Sub-Lord Table** — 249-entry table dividing 360° into sign-lord,
   star-lord, sub-lord, and sub-sub-lord (4 steps).

2. **Planet KP Pointers** — Full 4-step KP chain for every planet:
   Sign Lord → Star Lord → Sub Lord → Sub-Sub Lord

3. **Cuspal Sub-Lord Theory** — Sub-lord of each house cusp determines
   whether that house's matters will fructify. The cusp sub-lord's
   signification decides PROMISE (will event happen) vs DENIAL.

4. **4-Step Significator System** (strongest → weakest):
   Step 1: Planets in the STAR of the OCCUPANT of a house
   Step 2: The OCCUPANT planet itself
   Step 3: Planets in the STAR of the LORD of a house
   Step 4: The LORD of the house itself
   + Sub-lord filtering: only significators whose sub-lord also
     supports the house are "effective significators."

5. **Rahu/Ketu as Agents** — Rahu and Ketu act as agents of:
   (a) Their sign lord (Rahu in Gemini → agent of Mercury)
   (b) Planets conjoining them
   (c) Planets aspecting them
   They take on the signification of these planets.

6. **Planet Signification Table** — Each planet's house connections:
   - Houses occupied (by planet)
   - Houses owned (lordship)
   - Star lord's houses (occupied + owned)
   - Sub lord's houses (occupied + owned)

7. **Promise/Denial Verdicts** — For each house:
   If cusp sub-lord signifies the house → PROMISE (event will happen)
   If cusp sub-lord signifies 12th from house → DENIAL
   Combined with sub-lord's star-lord signification.

8. **House Grouping** — Related house groups for analysis:
   - Wealth: 2, 6, 10, 11
   - Loss: 1, 8, 12
   - Marriage: 2, 7, 11
   - Career: 2, 6, 10
   - Speculation: 1, 2, 5, 11

9. **Ruling Planets (RP)** — For event timing:
   Sign lord + Star lord + Sub lord of Ascendant and Moon
   + Day lord. Common RPs = active significators.

10. **DBA (Dasha-Bhukti-Antara) Significator Matching** —
    Event happens when DBA lords are significators of the
    relevant house group AND match ruling planets.

11. **KP Horary (Prashna)** — Input KP number (1–249) to
    set the ascendant cusp for horary analysis.

Uses Placidus house system with Krishnamurti Ayanamsa (default).
Each nakshatra (13°20') is subdivided into 9 unequal sub-lords
proportional to Vimshottari Dasha years.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.constants import (
    SIGNS, SIGN_IDX, SIGN_LORDS,
    NAKSHATRA_LORD_ORDER, DASHA_YEARS, TOTAL_DASHA_YEARS,
    NAKSHATRA_SPAN_DEG, PADA_SPAN_DEG,
    FINANCIAL_KARAKAS,
)


# ═════════════════════════════════════════════════════════════
# 1. KP SUB-LORD TABLE (249 entries)
# ═════════════════════════════════════════════════════════════

def build_kp_sublord_table() -> List[Dict]:
    """
    Build the complete 249-entry KP sub-lord table.

    Each nakshatra (13°20') is divided into 9 subs proportional
    to the Vimshottari Dasha years of each planet.

    CRITICAL: When a sub-lord period crosses a sign boundary (e.g.,
    from Aries to Taurus at 30°), it is SPLIT into two KP entries
    because the sign lord changes. This is what creates 249 entries
    instead of 243 (27 nakshatras × 9 subs).

    This matches K.S. Krishnamurti's original KP sub-lord table
    used in KP Star One, JHora, and all standard KP software.
    """
    table = []
    entry_id = 1
    nak_names = [
        "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
        "Punarvasu","Pushya","Ashlesha","Magha","P.Phalguni","U.Phalguni",
        "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
        "Mula","P.Ashadha","U.Ashadha","Shravana","Dhanishtha","Shatabhisha",
        "P.Bhadrapada","U.Bhadrapada","Revati"
    ]

    # Sign boundaries at 30°, 60°, 90°, ... 330°
    sign_boundaries = [i * 30.0 for i in range(1, 12)]  # 30, 60, ..., 330

    for nak_idx in range(27):
        nak_start = nak_idx * NAKSHATRA_SPAN_DEG
        star_lord = NAKSHATRA_LORD_ORDER[nak_idx % 9]
        lord_start_idx = NAKSHATRA_LORD_ORDER.index(star_lord)

        sub_start = nak_start
        for sub_offset in range(9):
            sub_idx = (lord_start_idx + sub_offset) % 9
            sub_lord = NAKSHATRA_LORD_ORDER[sub_idx]
            sub_span = NAKSHATRA_SPAN_DEG * (DASHA_YEARS[sub_lord] / TOTAL_DASHA_YEARS)
            sub_end = sub_start + sub_span

            # Check if this sub crosses any sign boundary
            # If so, split it into two entries at the boundary
            # Use epsilon to avoid false splits when sub ends exactly at boundary
            _EPS = 1e-6
            split_point = None
            for boundary in sign_boundaries:
                if (sub_start + _EPS) < boundary < (sub_end - _EPS):
                    # Sub genuinely crosses this sign boundary — needs split
                    split_point = boundary
                    break

            if split_point is not None:
                # Part 1: from sub_start to sign boundary
                sign_idx_1 = int(sub_start / 30) % 12
                table.append({
                    "id":         entry_id,
                    "nakshatra":  nak_idx + 1,
                    "nak_name":   nak_names[nak_idx],
                    "sign":       SIGNS[sign_idx_1],
                    "sign_lord":  SIGN_LORDS[SIGNS[sign_idx_1]],
                    "star_lord":  star_lord,
                    "sub_lord":   sub_lord,
                    "start_deg":  round(sub_start, 6),
                    "end_deg":    round(split_point, 6),
                })
                entry_id += 1

                # Part 2: from sign boundary to sub_end
                sign_idx_2 = int(split_point / 30) % 12
                table.append({
                    "id":         entry_id,
                    "nakshatra":  nak_idx + 1,
                    "nak_name":   nak_names[nak_idx],
                    "sign":       SIGNS[sign_idx_2],
                    "sign_lord":  SIGN_LORDS[SIGNS[sign_idx_2]],
                    "star_lord":  star_lord,
                    "sub_lord":   sub_lord,
                    "start_deg":  round(split_point, 6),
                    "end_deg":    round(sub_end, 6),
                })
                entry_id += 1
            else:
                # No split needed — single entry
                sign_idx = int(sub_start / 30) % 12
                table.append({
                    "id":         entry_id,
                    "nakshatra":  nak_idx + 1,
                    "nak_name":   nak_names[nak_idx],
                    "sign":       SIGNS[sign_idx],
                    "sign_lord":  SIGN_LORDS[SIGNS[sign_idx]],
                    "star_lord":  star_lord,
                    "sub_lord":   sub_lord,
                    "start_deg":  round(sub_start, 6),
                    "end_deg":    round(sub_end, 6),
                })
                entry_id += 1

            sub_start = sub_end

    return table


# Pre-build the table at module load
KP_SUBLORD_TABLE = build_kp_sublord_table()


# ═════════════════════════════════════════════════════════════
# 2. KP POINTER — 4-step: Sign Lord → Star Lord → Sub → Sub-Sub
# ═════════════════════════════════════════════════════════════

def get_kp_pointer(longitude: float) -> Dict:
    """
    Complete 4-step KP pointer for any sidereal longitude.
    Returns: sign_lord, star_lord, sub_lord, sub_sub_lord, kp_number.
    """
    longitude = longitude % 360.0

    for entry in KP_SUBLORD_TABLE:
        if entry["start_deg"] <= longitude < entry["end_deg"]:
            # Sub-sub-lord: subdivide the sub-lord range further
            sub_start = entry["start_deg"]
            sub_span = entry["end_deg"] - entry["start_deg"]
            pos_in_sub = longitude - sub_start
            fraction = pos_in_sub / sub_span if sub_span > 0 else 0

            sub_lord_idx = NAKSHATRA_LORD_ORDER.index(entry["sub_lord"])
            sub_sub_lord = _find_sub_at_fraction(sub_lord_idx, fraction)

            # Nakshatra pada
            nak_start = (entry["nakshatra"] - 1) * NAKSHATRA_SPAN_DEG
            deg_in_nak = longitude - nak_start
            pada = min(int(deg_in_nak / PADA_SPAN_DEG) + 1, 4)

            return {
                "longitude":     round(longitude, 6),
                "sign":          entry["sign"],
                "sign_lord":     entry["sign_lord"],
                "star_lord":     entry["star_lord"],
                "sub_lord":      entry["sub_lord"],
                "sub_sub_lord":  sub_sub_lord,
                "kp_number":     entry["id"],
                "nakshatra":     entry["nak_name"],
                "nak_num":       entry["nakshatra"],
                "pada":          pada,
            }

    # Edge case for exactly 360.0
    entry = KP_SUBLORD_TABLE[-1]
    return {
        "longitude":     360.0,
        "sign":          entry["sign"],
        "sign_lord":     entry["sign_lord"],
        "star_lord":     entry["star_lord"],
        "sub_lord":      entry["sub_lord"],
        "sub_sub_lord":  entry["sub_lord"],
        "kp_number":     entry["id"],
        "nakshatra":     entry["nak_name"],
        "nak_num":       entry["nakshatra"],
        "pada":          4,
    }


def _find_sub_at_fraction(lord_start_idx: int, fraction: float) -> str:
    """Find which sub-lord governs at a given fraction (0–1) within a sub."""
    cumulative = 0.0
    for i in range(9):
        idx = (lord_start_idx + i) % 9
        lord = NAKSHATRA_LORD_ORDER[idx]
        span = DASHA_YEARS[lord] / TOTAL_DASHA_YEARS
        cumulative += span
        if fraction <= cumulative + 1e-10:
            return lord
    return NAKSHATRA_LORD_ORDER[lord_start_idx]


def get_kp_from_number(kp_number: int) -> Dict:
    """Get KP entry from KP number (1–249) — used for KP Horary."""
    if 1 <= kp_number <= len(KP_SUBLORD_TABLE):
        entry = KP_SUBLORD_TABLE[kp_number - 1]
        mid_deg = (entry["start_deg"] + entry["end_deg"]) / 2
        return get_kp_pointer(mid_deg)
    return {}


# ═════════════════════════════════════════════════════════════
# 3. CUSPAL SUB-LORD TABLE (all 12 houses)
# ═════════════════════════════════════════════════════════════

def calculate_cuspal_sublords(houses: List[Dict]) -> List[Dict]:
    """
    Calculate KP cuspal sub-lords for all 12 house cusps.
    The sub-lord of a cusp is the KEY factor in KP:
    it determines whether that house's matters will fructify.
    """
    cuspal_data = []
    for house in houses:
        cusp_long = house["longitude"]
        kp = get_kp_pointer(cusp_long)

        house_num = house["house"]
        cuspal_data.append({
            "house":          house_num,
            "cusp_longitude": round(cusp_long, 4),
            "sign":           kp["sign"],
            "sign_lord":      kp["sign_lord"],
            "star_lord":      kp["star_lord"],
            "sub_lord":       kp["sub_lord"],
            "sub_sub_lord":   kp["sub_sub_lord"],
            "kp_number":      kp["kp_number"],
            "nakshatra":      kp["nakshatra"],
            "pada":           kp["pada"],
        })

    return cuspal_data


# ═════════════════════════════════════════════════════════════
# 4. FOUR-STEP SIGNIFICATOR SYSTEM
# ═════════════════════════════════════════════════════════════

# Rahu/Ketu sign-lord agency
_RAHU_KETU_SIGN_LORDS = {}  # populated per chart

# Natural friendship (for Rahu/Ketu agent logic)
PLANET_ASPECTS = {
    "Sun":     [7],
    "Moon":    [7],
    "Mars":    [4, 7, 8],
    "Mercury": [7],
    "Jupiter": [5, 7, 9],
    "Venus":   [7],
    "Saturn":  [3, 7, 10],
    "Rahu":    [5, 7, 9],
    "Ketu":    [5, 7, 9],
}


def _planet_house_placidus(planet_longitude: float, houses: List[Dict]) -> int:
    """
    Determine which Placidus house a planet occupies using cusp boundaries.
    In KP/Placidus, a planet belongs to the house whose cusp it falls after
    (i.e., planet longitude is between cusp N and cusp N+1).
    """
    cusp_longs = []
    for h in sorted(houses, key=lambda x: x["house"]):
        cusp_longs.append(h["longitude"] % 360.0)
    planet_long = planet_longitude % 360.0

    for i in range(12):
        cusp_start = cusp_longs[i]
        cusp_end = cusp_longs[(i + 1) % 12]
        house_num = i + 1

        if cusp_start <= cusp_end:
            # Normal case: cusp_start < cusp_end (no 360° wrap)
            if cusp_start <= planet_long < cusp_end:
                return house_num
        else:
            # Wraps around 360°: e.g., cusp at 350° to next at 20°
            if planet_long >= cusp_start or planet_long < cusp_end:
                return house_num

    return 1  # fallback


def _planet_house(planet_sign: str, asc_idx: int) -> int:
    """Determine which house a planet occupies based on its sign and ascendant.
    LEGACY: use _planet_house_placidus() for KP/Placidus accuracy."""
    p_idx = SIGN_IDX.get(planet_sign, 0)
    return ((p_idx - asc_idx) % 12) + 1


def _houses_owned(planet_name: str) -> List[int]:
    """Return sign indices (0-11) owned by a planet."""
    owned = []
    for sign, lord in SIGN_LORDS.items():
        if lord == planet_name:
            owned.append(SIGN_IDX[sign])
    return owned


def calculate_significators(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
) -> Dict:
    """
    Complete 4-step KP significator analysis for each house.

    Step 1: Planets in the STAR of the OCCUPANT of the house (strongest)
    Step 2: The OCCUPANT planet itself
    Step 3: Planets in the STAR of the LORD of the house
    Step 4: The LORD of the house (weakest)

    Additionally: sub-lord filtering to determine effective significators.

    Uses PLACIDUS cusp boundaries for planet placement and actual cusp
    signs for house lordship (not whole-sign counting).
    """
    asc_sign = ascendant["sign"]
    asc_idx = SIGN_IDX.get(asc_sign, 0)

    # Build planet → house occupied mapping using Placidus cusp boundaries
    planet_house_map: Dict[str, int] = {}
    for p in planets:
        p_house = _planet_house_placidus(p["longitude"], houses)
        planet_house_map[p["planet"]] = p_house

    # Build planet → star-lord mapping
    planet_star_lord: Dict[str, str] = {}
    planet_sub_lord: Dict[str, str] = {}
    planet_kp_data: Dict[str, Dict] = {}
    for p in planets:
        kp = get_kp_pointer(p["longitude"])
        planet_star_lord[p["planet"]] = kp["star_lord"]
        planet_sub_lord[p["planet"]] = kp["sub_lord"]
        planet_kp_data[p["planet"]] = kp

    # Build house → lord mapping from ACTUAL Placidus cusp signs
    # (not whole-sign counting — handles interceptions correctly)
    house_lord_map: Dict[int, str] = {}
    for h in houses:
        cusp_sign = h.get("sign", "")
        if cusp_sign and cusp_sign in SIGN_LORDS:
            house_lord_map[h["house"]] = SIGN_LORDS[cusp_sign]
        else:
            # Fallback: derive sign from cusp longitude
            sign_idx = int(h["longitude"] / 30) % 12
            house_lord_map[h["house"]] = SIGN_LORDS[SIGNS[sign_idx]]

    # Build lord → owned houses (which houses does this planet rule?)
    lord_houses: Dict[str, List[int]] = {}
    for h, lord in house_lord_map.items():
        lord_houses.setdefault(lord, []).append(h)

    # Rahu/Ketu agent logic
    rahu_agents = _get_rahu_ketu_agents("Rahu", planets, planet_house_map, asc_idx)
    ketu_agents = _get_rahu_ketu_agents("Ketu", planets, planet_house_map, asc_idx)

    # Calculate significators for each house
    house_significators: Dict[int, Dict] = {}

    # Build a lookup for actual cusp signs from houses data
    cusp_sign_map: Dict[int, str] = {}
    for h in houses:
        cusp_sign_map[h["house"]] = h.get("sign", SIGNS[(asc_idx + h["house"] - 1) % 12])

    for house_num in range(1, 13):
        house_sign = cusp_sign_map.get(house_num, SIGNS[(asc_idx + house_num - 1) % 12])
        house_lord = house_lord_map[house_num]

        # ── Step 2: Occupants of this house ──
        occupants = [name for name, h in planet_house_map.items() if h == house_num]

        # ── Step 1: Planets in the STAR of occupants ──
        star_of_occupants = []
        for occ in occupants:
            for pname, sl in planet_star_lord.items():
                if sl == occ and pname not in star_of_occupants:
                    star_of_occupants.append(pname)

        # ── Step 3: Planets in the STAR of the lord ──
        star_of_lord = []
        for pname, sl in planet_star_lord.items():
            if sl == house_lord and pname not in star_of_lord:
                star_of_lord.append(pname)

        # ── Step 4: Lord itself ──
        lord_list = [house_lord]

        # ── Combined (ordered by strength) ──
        all_sigs = list(dict.fromkeys(
            star_of_occupants + occupants + star_of_lord + lord_list
        ))

        # ── Effective significators (sub-lord supports the house) ──
        effective = []
        for sig in all_sigs:
            sub = planet_sub_lord.get(sig, "")
            if sub:
                # Sub-lord should signify positive houses for this matter
                sub_house = planet_house_map.get(sub)
                sub_owned = lord_houses.get(sub, [])
                # If sub-lord occupies or owns the same house → effective
                if sub_house == house_num or house_num in sub_owned:
                    effective.append(sig)

        house_significators[house_num] = {
            "house":               house_num,
            "sign":                house_sign,
            "lord":                house_lord,
            "occupants":           occupants,
            "step1_star_of_occ":   star_of_occupants,
            "step2_occupants":     occupants,
            "step3_star_of_lord":  star_of_lord,
            "step4_lord":          lord_list,
            "all_significators":   all_sigs,
            "effective_significators": effective,
            "significator_count":  len(all_sigs),
        }

    return {
        "houses":          house_significators,
        "planet_houses":   planet_house_map,
        "house_lords":     house_lord_map,
        "lord_houses":     lord_houses,
        "rahu_agents":     rahu_agents,
        "ketu_agents":     ketu_agents,
    }


def _get_rahu_ketu_agents(
    node: str,
    planets: List[Dict],
    planet_house_map: Dict[str, int],
    asc_idx: int,
) -> Dict:
    """
    Determine which planets Rahu/Ketu acts as agent for.
    Rahu/Ketu takes on signification of:
    (a) Sign lord (strongest)
    (b) Conjunct planets (same house)
    (c) Aspecting planets
    """
    node_data = next((p for p in planets if p["planet"] == node), None)
    if not node_data:
        return {"node": node, "sign_lord": "", "conjunct": [], "aspecting": []}

    node_sign = node_data["sign"]
    node_house = planet_house_map.get(node, 0)
    sign_lord = SIGN_LORDS.get(node_sign, "")

    # Conjunct = planets in the same house
    conjunct = [
        pname for pname, h in planet_house_map.items()
        if h == node_house and pname != node
    ]

    # Aspecting planets (planets that aspect Rahu/Ketu's house)
    aspecting = []
    for p in planets:
        if p["planet"] == node:
            continue
        p_house = planet_house_map.get(p["planet"], 0)
        asp_houses = PLANET_ASPECTS.get(p["planet"], [7])
        for asp in asp_houses:
            target_house = ((p_house - 1 + asp) % 12) + 1
            if target_house == node_house:
                aspecting.append(p["planet"])
                break

    return {
        "node":       node,
        "sign_lord":  sign_lord,
        "conjunct":   conjunct,
        "aspecting":  aspecting,
        "acts_as":    list(dict.fromkeys([sign_lord] + conjunct)),
    }


# ═════════════════════════════════════════════════════════════
# 5. PLANET SIGNIFICATION TABLE
# ═════════════════════════════════════════════════════════════

def _make_ascendant_pseudo_planet(ascendant: Dict) -> Dict:
    """
    Create a pseudo-planet dict for the Ascendant so it can appear
    alongside planets in KP tables (planet_table, nadi, sig v2, status).
    """
    return {
        "planet": "Ascendant",
        "longitude": ascendant.get("longitude", 0.0),
        "sign": ascendant.get("sign", ""),
        "degree_in_sign": ascendant.get("degree_in_sign", 0.0),
        "speed": 0,
    }


def build_planet_signification_table(
    planets: List[Dict],
    significator_data: Dict,
    ascendant: Optional[Dict] = None,
) -> List[Dict]:
    """
    Build a table showing each planet's complete house significations.
    For each planet: which houses it signifies and through what connection.
    Includes Ascendant as an additional entry when provided.
    """
    planet_houses = significator_data["planet_houses"]
    lord_houses = significator_data["lord_houses"]
    house_sigs = significator_data["houses"]

    # Include Ascendant alongside planets
    all_bodies = list(planets)
    if ascendant:
        all_bodies.append(_make_ascendant_pseudo_planet(ascendant))

    table = []
    for p in all_bodies:
        pname = p["planet"]
        kp = get_kp_pointer(p["longitude"])

        # Houses this planet signifies (from significator analysis)
        signified_houses = []
        for h_num, h_data in house_sigs.items():
            if pname in h_data["all_significators"]:
                # Determine the step/level
                level = 4
                if pname in h_data["step1_star_of_occ"]:
                    level = 1
                elif pname in h_data["step2_occupants"]:
                    level = 2
                elif pname in h_data["step3_star_of_lord"]:
                    level = 3
                signified_houses.append({"house": h_num, "level": level})

        # Star lord's houses
        star_lord = kp["star_lord"]
        star_lord_occupied = planet_houses.get(star_lord)
        star_lord_owned = lord_houses.get(star_lord, [])

        # Sub lord's houses
        sub_lord = kp["sub_lord"]
        sub_lord_occupied = planet_houses.get(sub_lord)
        sub_lord_owned = lord_houses.get(sub_lord, [])

        table.append({
            "planet":              pname,
            "sign":                p["sign"],
            "longitude":           round(p["longitude"], 4),
            "sign_lord":           kp["sign_lord"],
            "star_lord":           kp["star_lord"],
            "sub_lord":            kp["sub_lord"],
            "sub_sub_lord":        kp["sub_sub_lord"],
            "kp_number":           kp["kp_number"],
            "nakshatra":           kp["nakshatra"],
            "pada":                kp["pada"],
            "house_occupied":      1 if pname == "Ascendant" else planet_houses.get(pname, 0),
            "houses_owned":        lord_houses.get(pname, []),
            "star_lord_occupied":  star_lord_occupied,
            "star_lord_owned":     star_lord_owned,
            "sub_lord_occupied":   sub_lord_occupied,
            "sub_lord_owned":      sub_lord_owned,
            "signified_houses":    signified_houses,
            "retro":               p.get("speed", 0) < 0,
        })

    return table


# ═════════════════════════════════════════════════════════════
# 6. PROMISE / DENIAL VERDICTS (Cuspal Sub-Lord Theory)
# ═════════════════════════════════════════════════════════════

# House groupings for common queries
HOUSE_GROUPS = {
    "wealth":       {"houses": [2, 6, 10, 11], "deny": [8, 12],  "label": "Wealth & Income"},
    "loss":         {"houses": [1, 8, 12],     "deny": [2, 11],  "label": "Loss & Expenses"},
    "marriage":     {"houses": [2, 7, 11],     "deny": [1, 6, 10, 12], "label": "Marriage & Partnership"},
    "career":       {"houses": [2, 6, 10],     "deny": [8, 12],  "label": "Career & Profession"},
    "speculation":  {"houses": [1, 2, 5, 11],  "deny": [8, 12],  "label": "Speculation & Stock Market"},
    "property":     {"houses": [4, 11],        "deny": [3, 12],  "label": "Property & Fixed Assets"},
    "children":     {"houses": [2, 5, 11],     "deny": [1, 4, 10], "label": "Children & Progeny"},
    "education":    {"houses": [4, 9, 11],     "deny": [8, 12],  "label": "Education & Knowledge"},
    "foreign":      {"houses": [3, 9, 12],     "deny": [4],      "label": "Foreign Travel/Settlement"},
    "health":       {"houses": [1, 5, 11],     "deny": [6, 8, 12], "label": "Health & Vitality"},
}

# ── Prashna (Horary) Question Categories ────────────────────
# Each question type maps to:
#   primary_house: the main cusp whose sub-lord decides YES/NO
#   conductive: houses the sub-lord should signify for YES
#   detrimental: houses that deny the matter
#   label: display name
PRASHNA_QUESTIONS = {
    # ── House groups cross-verified against Futuretek KP Horary FAQs (Sunil Dixit) ──
    # Format: primary_house = cusp whose sub-lord is checked
    #         conductive   = houses that promise YES
    #         detrimental  = houses that deny / obstruct

    # 7th house — PDF Q66 (p64)
    "marriage":         {"primary_house": 7,  "conductive": [2, 7, 11],     "detrimental": [1, 6, 10],  "label": "Will Marriage Happen?"},
    # 2nd house — PDF Q4 (p30): Best=2,6,11
    "wealth":           {"primary_house": 2,  "conductive": [2, 6, 11],     "detrimental": [5, 8, 12],  "label": "Will I Gain Wealth?"},
    # 10th house — PDF Q94-95 (p79)
    "job":              {"primary_house": 10, "conductive": [2, 6, 10, 11], "detrimental": [5, 8, 12],  "label": "Will I Get the Job?"},
    # 10th house — PDF Q94 (p79)
    "promotion":        {"primary_house": 10, "conductive": [2, 6, 10, 11], "detrimental": [5, 8, 12],  "label": "Will I Get Promotion?"},
    # 10th house — PDF Q9 (p32): 10th SL sig of 3rd = transfer
    "transfer":         {"primary_house": 10, "conductive": [3, 10],        "detrimental": [4, 12],     "label": "Will I Be Transferred?"},
    # 1st house — PDF Q2 (p28)
    "health":           {"primary_house": 1,  "conductive": [1, 5, 11],     "detrimental": [6, 8, 12],  "label": "Will Health Improve?"},
    # 3rd house — PDF Q8 (p32)
    "travel_short":     {"primary_house": 3,  "conductive": [3, 9, 11],     "detrimental": [4, 8, 12],  "label": "Will Short Journey Happen?"},
    # 12th house — PDF Q105 (p85): 12th SL → 3,9,12 [FIXED: was 9th cusp]
    "travel_foreign":   {"primary_house": 12, "conductive": [3, 9, 12],     "detrimental": [4],         "label": "Will I Go Abroad?"},
    # 6th house — PDF Q63-64 (p61-62): [FIXED: added 10 to conductive, 5 to detrimental]
    "court_case":       {"primary_house": 6,  "conductive": [6, 10, 11],    "detrimental": [5, 12],     "label": "Will I Win the Court Case?"},
    # 5th house — standard KP speculation
    "speculation":      {"primary_house": 5,  "conductive": [1, 2, 5, 11],  "detrimental": [8, 12],     "label": "Will Speculation Profit?"},
    # 4th house — PDF Q22 (p38)
    "buy_property":     {"primary_house": 4,  "conductive": [4, 11, 12],    "detrimental": [3, 5, 10],  "label": "Will I Buy Property?"},
    # 10th house — PDF Q23 (p38-39)
    "sell_property":    {"primary_house": 10, "conductive": [3, 5, 10],     "detrimental": [4, 11],     "label": "Will Property Be Sold?"},
    # 4th house — PDF Q33 (p45)
    "education":        {"primary_house": 4,  "conductive": [4, 9, 11],     "detrimental": [8, 12],     "label": "Will I Pass Exams?"},
    # 5th house — PDF Q39 (p49)
    "children":         {"primary_house": 5,  "conductive": [2, 5, 11],     "detrimental": [1, 4, 10],  "label": "Will I Have Children?"},
    # 6th house — PDF Q57 (p59): [FIXED: added 2 to conductive]
    "loan":             {"primary_house": 6,  "conductive": [2, 6, 11],     "detrimental": [5, 8, 12],  "label": "Will I Get the Loan?"},
    # 6th house — PDF Q55 (p58): [FIXED: primary was 11, PDF uses 6th cusp]
    "recovery_money":   {"primary_house": 6,  "conductive": [2, 6, 11],     "detrimental": [5, 8, 12],  "label": "Will I Recover Money?"},
    # 3rd house — PDF Q12 (p34): [FIXED: primary was 11, PDF uses 3rd cusp; detrimental 8,12]
    "interview":        {"primary_house": 3,  "conductive": [3, 9, 11],     "detrimental": [8, 12],     "label": "Will I Get Interview Call?"},
    # 3rd house — PDF Q15 (p36)
    "contract":         {"primary_house": 3,  "conductive": [3, 11],        "detrimental": [5, 8, 12],  "label": "Will I Get the Contract?"},
    # 5th house — standard KP lottery/speculation
    "lottery":          {"primary_house": 5,  "conductive": [2, 5, 6, 11],  "detrimental": [8, 12],     "label": "Will I Win the Lottery?"},
    # 4th house — standard KP vehicle
    "vehicle":          {"primary_house": 4,  "conductive": [4, 11],        "detrimental": [3, 12],     "label": "Will I Get a Vehicle?"},
    # 6th house — PDF Q58-59 (p60)
    "election":         {"primary_house": 6,  "conductive": [6, 10, 11],    "detrimental": [5, 8, 12],  "label": "Will I Win the Election?"},
    # 3rd house — PDF Q16 (p36)
    "appeal":           {"primary_house": 3,  "conductive": [6, 11],        "detrimental": [5, 12],     "label": "Will Appeal Succeed?"},
    # 11th house — general
    "general_success":  {"primary_house": 11, "conductive": [1, 2, 11],     "detrimental": [6, 8, 12],  "label": "Will I Succeed (General)?"},

    # ── New question types from Futuretek PDF ──
    # 12th house — PDF Q105-107 (p85): foreign settlement / green card
    "foreign_settle":   {"primary_house": 12, "conductive": [3, 9, 12],     "detrimental": [2, 4, 11],  "label": "Will I Settle Abroad?"},
    # 11th house — PDF Q103 (p83): lost item recovery
    "lost_item":        {"primary_house": 11, "conductive": [2, 11],        "detrimental": [5, 8, 12],  "label": "Will I Recover Lost Item?"},
    # 3rd house — PDF Q104 (p84): visa
    "visa":             {"primary_house": 3,  "conductive": [3, 9, 11, 12], "detrimental": [2, 8],      "label": "Will I Get Visa?"},
    # 7th house — PDF Q76 (p70): business profit
    "business_profit":  {"primary_house": 7,  "conductive": [2, 11],        "detrimental": [6, 12],     "label": "Will Business Be Profitable?"},
    # 7th house — PDF Q77-78 (p70): partnership
    "partnership":      {"primary_house": 7,  "conductive": [5, 11],        "detrimental": [6, 12],     "label": "Will Partnership Suit Me?"},
    # 5th house — PDF Q49 (p54): love affair
    "love_affair":      {"primary_house": 5,  "conductive": [7, 11],        "detrimental": [6, 12],     "label": "Will Love Affair Materialise?"},
    # 12th house — PDF Q58 (p60): debt freedom
    "debt_freedom":     {"primary_house": 12, "conductive": [5, 8, 12],     "detrimental": [2, 6, 11],  "label": "Will I Get Out of Debt?"},
    # 6th house — PDF Q59 (p60): competitive exam
    "competitive_exam": {"primary_house": 6,  "conductive": [4, 6, 9, 11],  "detrimental": [5, 8, 12],  "label": "Will I Clear Competitive Exam?"},
}


def calculate_prashna_yesno(
    kp_number: int,
    question_type: str,
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
    transit_planets: Optional[List[Dict]],
    transit_datetime: Optional[datetime],
    significator_data: Dict,
    cuspal_data: List[Dict],
    planet_sig_table: List[Dict],
) -> Dict:
    """
    Advanced KP Prashna (Horary) Yes/No system per Futuretek methodology:

    1. KP number (1-249) sets the ascendant degree
    2. Identify the primary house cusp for the question type
    3. Check cusp sub-lord's signification → does it signify conductive houses? (YES)
       or detrimental houses? (NO) or both? (MIXED)
    4. Check if cusp sub-lord is retrograde or in star of retrograde planet → weak/deny
    5. Compute Ruling Planets at query moment
    6. Cross-match significators with Ruling Planets → fruitful significators
    7. Final verdict with detailed reasoning

    Rules from Futuretek KP Horary:
    - Sub-lord of primary cusp must signify conductive houses → YES
    - Sub-lord signifying only detrimental houses → NO
    - Sub-lord in star of retrograde planet → matter delayed/denied
    - Rahu/Ketu act as agents of their sign lord among RPs
    - RP in star of retrograde planet should be discarded
    - Significators common with RP are FRUITFUL significators
    """
    q_config = PRASHNA_QUESTIONS.get(question_type)
    if not q_config:
        return {"error": f"Unknown question type: {question_type}"}

    primary_house = q_config["primary_house"]
    conductive = q_config["conductive"]
    detrimental = q_config["detrimental"]
    label = q_config["label"]

    # ── Step 1: KP Horary pointer ──
    horary_kp = get_kp_from_number(kp_number) if (1 <= kp_number <= 249) else {}

    # ── Step 2: Get cusp sub-lord of primary house ──
    primary_cusp = next((c for c in cuspal_data if c["house"] == primary_house), None)
    if not primary_cusp:
        return {"error": f"No cuspal data for house {primary_house}"}

    cusp_sub_lord = primary_cusp.get("sub_lord", "")
    cusp_star_lord = primary_cusp.get("star_lord", "")
    cusp_sign_lord = primary_cusp.get("sign_lord", "")

    # ── Step 3: Find which houses the sub-lord signifies ──
    house_sigs = significator_data.get("houses", {})
    sub_lord_signifies = _get_planet_signified_houses(cusp_sub_lord, house_sigs)
    star_lord_signifies = _get_planet_signified_houses(cusp_star_lord, house_sigs)

    # Check conductive vs detrimental overlap
    conductive_match = [h for h in conductive if h in sub_lord_signifies]
    detrimental_match = [h for h in detrimental if h in sub_lord_signifies]

    # ── Step 4: Retrograde check — 3-tier per Futuretek PDF Page 25 ──
    # Exception: Rahu & Ketu are always retrograde — treat as normal
    # Sun & Moon are never retrograde
    ALWAYS_RETRO = {"Rahu", "Ketu"}
    NEVER_RETRO = {"Sun", "Moon"}

    sub_lord_planet_data = next((p for p in planets if p["planet"] == cusp_sub_lord), None)
    is_sub_lord_retro = False
    if sub_lord_planet_data and cusp_sub_lord not in ALWAYS_RETRO and cusp_sub_lord not in NEVER_RETRO:
        is_sub_lord_retro = sub_lord_planet_data.get("speed", 0) < 0

    # Find the sub-lord's depositor (the star lord of the sub-lord's position)
    # This tells us: is the sub-lord deposited in the star of a retro/direct planet?
    sl_depositor = ""
    is_sl_depositor_retro = False
    if sub_lord_planet_data:
        sl_kp = get_kp_pointer(sub_lord_planet_data["longitude"])
        sl_depositor = sl_kp.get("star_lord", "")
        if sl_depositor and sl_depositor not in ALWAYS_RETRO and sl_depositor not in NEVER_RETRO:
            depositor_data = next((p for p in planets if p["planet"] == sl_depositor), None)
            if depositor_data:
                is_sl_depositor_retro = depositor_data.get("speed", 0) < 0

    # Also check cusp star lord retro (existing check)
    star_lord_planet_data = next((p for p in planets if p["planet"] == cusp_star_lord), None)
    is_star_lord_retro = False
    if star_lord_planet_data and cusp_star_lord not in ALWAYS_RETRO and cusp_star_lord not in NEVER_RETRO:
        is_star_lord_retro = star_lord_planet_data.get("speed", 0) < 0

    # ── 3-tier retrograde classification (Futuretek PDF p25) ──
    # Tier 1: Retro in star of DIRECT → delayed, materializes after becoming direct
    # Tier 2: Retro in star of RETRO (or own star when retro) → "promises only failure"
    # Tier 3: Direct in star of RETRO → "cannot give result in its period"
    retro_tier = 0  # 0 = no retro issue
    if is_sub_lord_retro and not is_sl_depositor_retro:
        retro_tier = 1  # Retro in star of direct → delayed but will happen
    elif is_sub_lord_retro and is_sl_depositor_retro:
        retro_tier = 2  # Retro in star of retro → absolute failure
    elif not is_sub_lord_retro and is_sl_depositor_retro:
        retro_tier = 3  # Direct in star of retro → cannot give result

    retro_weakness = retro_tier > 0 or is_star_lord_retro
    retro_denial = retro_tier >= 2  # Tier 2 and 3 = hard denial

    # ── Step 5: Compute Ruling Planets ──
    rp_data = None
    fruitful_significators = []
    rp_match_count = 0
    if transit_planets and transit_datetime:
        rp_data = calculate_current_ruling_planets(
            transit_planets,
            ascendant,
            transit_datetime,
        )
        rp_planets = [r["planet"] for r in rp_data.get("rp_rows", [])]
        rp_set = set(rp_planets)

        # ── Step 6: Discard RP in star of retrograde planet ──
        # Exception: Rahu/Ketu are always retro — don't discard planets in their stars
        valid_rps = []
        for rp_planet in rp_set:
            rp_planet_data = next((p for p in transit_planets if p["planet"] == rp_planet), None)
            if rp_planet_data:
                rp_kp = get_kp_pointer(rp_planet_data["longitude"])
                rp_star_lord = rp_kp.get("star_lord", "")
                if rp_star_lord not in ALWAYS_RETRO:
                    rp_star_planet = next((p for p in transit_planets if p["planet"] == rp_star_lord), None)
                    if rp_star_planet and rp_star_planet.get("speed", 0) < 0:
                        continue  # discard — in star of truly retrograde planet
            valid_rps.append(rp_planet)

        # Rahu/Ketu agent replacement among RPs
        for node in ["Rahu", "Ketu"]:
            node_data = next((p for p in transit_planets if p["planet"] == node), None)
            if node_data:
                node_kp = get_kp_pointer(node_data["longitude"])
                agent_of = node_kp.get("sign_lord", "")
                if agent_of in rp_set and node not in valid_rps:
                    valid_rps.append(node)

        # ── Step 7: Cross-match significators with RPs ──
        # Get all significators of the conductive houses
        all_sigs_for_group = set()
        for h in conductive:
            h_data = house_sigs.get(h, {})
            for s in h_data.get("all_significators", []):
                all_sigs_for_group.add(s)

        fruitful_significators = sorted(all_sigs_for_group & set(valid_rps))
        rp_match_count = len(fruitful_significators)

    # ── Step 8: Final Verdict ──
    reasons = []

    if conductive_match and not detrimental_match:
        base_verdict = "YES"
        reasons.append(f"Sub-lord {cusp_sub_lord} of H{primary_house} signifies conductive houses {conductive_match}")
    elif detrimental_match and not conductive_match:
        base_verdict = "NO"
        reasons.append(f"Sub-lord {cusp_sub_lord} of H{primary_house} signifies ONLY detrimental houses {detrimental_match}")
    elif conductive_match and detrimental_match:
        base_verdict = "YES (with obstacles)"
        reasons.append(f"Sub-lord {cusp_sub_lord} signifies both conductive {conductive_match} AND detrimental {detrimental_match}")
    else:
        # Sub-lord doesn't signify either group directly — check star lord
        star_conductive = [h for h in conductive if h in star_lord_signifies]
        star_detrimental = [h for h in detrimental if h in star_lord_signifies]
        if star_conductive:
            base_verdict = "LIKELY YES"
            reasons.append(f"Sub-lord's star lord {cusp_star_lord} signifies conductive houses {star_conductive}")
        elif star_detrimental:
            base_verdict = "LIKELY NO"
            reasons.append(f"Sub-lord's star lord {cusp_star_lord} signifies detrimental houses {star_detrimental}")
        else:
            base_verdict = "UNCERTAIN"
            reasons.append(f"Sub-lord {cusp_sub_lord} does not clearly signify conductive or detrimental houses")

    # Retrograde modifier — 3-tier per Futuretek PDF Page 25
    # Rahu/Ketu always retrograde — already excluded above
    if retro_tier == 1:
        # Retro in star of direct → delayed but will materialise after becoming direct
        reasons.append(f"RETRO TIER-1: Sub-lord {cusp_sub_lord} is RETROGRADE but in star of DIRECT {sl_depositor} — matter delayed, will materialise after {cusp_sub_lord} turns direct")
        if "YES" in base_verdict or base_verdict == "LIKELY YES":
            base_verdict = "YES (delayed — retro in star of direct)"
    elif retro_tier == 2:
        # Retro in star of retro → "promises only failure. Never success."
        reasons.append(f"RETRO TIER-2 DENIAL: Sub-lord {cusp_sub_lord} is RETROGRADE in star of RETROGRADE {sl_depositor} — promises ONLY FAILURE per Futuretek rules")
        if "YES" in base_verdict or base_verdict == "LIKELY YES":
            base_verdict = "NO (retro-retro: total failure)"
    elif retro_tier == 3:
        # Direct in star of retro → "cannot give result in its period"
        reasons.append(f"RETRO TIER-3 BLOCK: Sub-lord {cusp_sub_lord} is DIRECT but in star of RETROGRADE {sl_depositor} — CANNOT give result in its period per Futuretek rules")
        if "YES" in base_verdict or base_verdict == "LIKELY YES":
            base_verdict = "NO (direct in star of retro)"

    # Additional: cusp star lord retro = extra weakness
    if is_star_lord_retro and retro_tier == 0:
        reasons.append(f"WARNING: Cusp star lord {cusp_star_lord} is RETROGRADE — promise weakened, delays likely")
        if base_verdict.startswith("YES") and not is_sub_lord_retro:
            base_verdict = "YES (delayed)"

    # RP confirmation
    if rp_data:
        if rp_match_count >= 3:
            reasons.append(f"STRONG RP confirmation: {rp_match_count} fruitful significators match Ruling Planets: {', '.join(fruitful_significators)}")
        elif rp_match_count >= 1:
            reasons.append(f"PARTIAL RP confirmation: {rp_match_count} fruitful significators: {', '.join(fruitful_significators)}")
        else:
            reasons.append("WEAK RP confirmation: No significators match current Ruling Planets — timing may not be NOW")
            if base_verdict.startswith("YES"):
                base_verdict += " (not now)"

    # Confidence score
    score = 0
    if conductive_match:
        score += len(conductive_match) * 20
    if detrimental_match:
        score -= len(detrimental_match) * 20
    if rp_match_count:
        score += rp_match_count * 10
    if retro_tier == 2:
        score -= 70  # Retro in star of retro = absolute failure
    elif retro_tier == 3:
        score -= 60  # Direct in star of retro = cannot give result
    elif retro_tier == 1:
        score -= 25  # Retro in star of direct = delayed but possible
    if is_star_lord_retro and retro_tier == 0:
        score -= 20  # Cusp star lord retro = weaken
    # Clamp -100 to 100
    score = max(-100, min(100, score))

    # Determine verdict color
    if "YES" in base_verdict and "NO" not in base_verdict:
        verdict_type = "positive"
    elif "NO" in base_verdict:
        verdict_type = "negative"
    else:
        verdict_type = "neutral"

    # ── All cusps analysis for the question group ──
    group_cusp_analysis = []
    for h in conductive:
        cusp = next((c for c in cuspal_data if c["house"] == h), None)
        if cusp:
            sl = cusp.get("sub_lord", "")
            sl_houses = _get_planet_signified_houses(sl, house_sigs)
            cond = [x for x in conductive if x in sl_houses]
            detr = [x for x in detrimental if x in sl_houses]
            if cond and not detr:
                v = "PROMISE"
            elif detr and not cond:
                v = "DENIAL"
            elif cond and detr:
                v = "MIXED"
            else:
                v = "NEUTRAL"
            group_cusp_analysis.append({
                "house": h,
                "sub_lord": sl,
                "signifies": sl_houses,
                "verdict": v,
            })

    return {
        "question_type":        question_type,
        "question_label":       label,
        "kp_number":            kp_number,
        "horary_kp":            horary_kp,
        "primary_house":        primary_house,
        "conductive_houses":    conductive,
        "detrimental_houses":   detrimental,
        "cusp_sub_lord":        cusp_sub_lord,
        "cusp_star_lord":       cusp_star_lord,
        "cusp_sign_lord":       cusp_sign_lord,
        "sub_lord_signifies":   sub_lord_signifies,
        "conductive_match":     conductive_match,
        "detrimental_match":    detrimental_match,
        "is_sub_lord_retro":    is_sub_lord_retro,
        "is_star_lord_retro":   is_star_lord_retro,
        "retro_tier":           retro_tier,
        "sl_depositor":         sl_depositor,
        "is_sl_depositor_retro": is_sl_depositor_retro,
        "ruling_planets":       rp_data,
        "fruitful_significators": fruitful_significators,
        "rp_match_count":       rp_match_count,
        "group_cusp_analysis":  group_cusp_analysis,
        "verdict":              base_verdict,
        "verdict_type":         verdict_type,
        "confidence_score":     score,
        "reasons":              reasons,
    }


# ═════════════════════════════════════════════════════════════
# KP SPORTS / MATCH PREDICTION
# ═════════════════════════════════════════════════════════════
#
# Rules from notes (4-step significator theory):
#
# TEAM A (Querent / Favourite — takes Lagna):
#   WINS if 6th SL → 6, 10, 11, 1, 2, 3 at level 1 or 2
#     Prime importance: 6, 10, 11
#     Cross-check from 12th SL (should NOT signify opponent win houses)
#   LOSES if 6th SL → 12, 5, 4, 7, 8, 9 at level 1 or 2
#
# TEAM B (Opponent — 7th house):
#   WINS if 12th SL → 12, 5, 4, 7, 8, 9 at level 1 or 2
#     Prime importance: 12, 5, 4
#     Cross-check from 5th SL
#   LOSES if 12th SL → 6, 10, 11, 1, 2, 3 at level 1 or 2
#
# If mixed houses appear, check opponent combination also.
#
# BILATERAL SERIES: Same chart for all matches.
#   Moon's transiting nakshatra on match day → that nak lord's
#   signification decides result. If Moon crosses 2 nakshatras
#   during match, take the one at match END.
#
# TOURNAMENT: Give seed no per team. 6th SL → 5, 4, 12 = eliminated.
# ═════════════════════════════════════════════════════════════

MATCH_CATEGORIES = {
    "cricket":      "Cricket Match",
    "football":     "Football Match",
    "tennis":       "Tennis Match",
    "kabaddi":      "Kabaddi Match",
    "hockey":       "Hockey Match",
    "boxing":       "Boxing / Wrestling",
    "election":     "Election Contest",
    "competition":  "General Competition",
    "court_case":   "Court Case / Legal Battle",
    "business":     "Business Competition",
    "exam":         "Competitive Exam",
}


def _get_level12_houses(planet: str, house_sigs: Dict) -> List[int]:
    """
    Get houses where a planet is a Level-1 or Level-2 significator
    (star-of-occupant or occupant — strongest levels in 4-step theory).
    """
    houses = []
    for h_num, h_data in house_sigs.items():
        if not isinstance(h_data, dict):
            continue
        step1 = h_data.get("step1_star_of_occ", [])
        step2 = h_data.get("step2_occupants", h_data.get("occupants", []))
        if planet in step1 or planet in step2:
            houses.append(h_num)
    return houses


def _get_level34_houses(planet: str, house_sigs: Dict) -> List[int]:
    """
    Get houses where a planet is a Level-3 or Level-4 significator
    (star-of-lord or lord — weaker levels).
    """
    houses = []
    for h_num, h_data in house_sigs.items():
        if not isinstance(h_data, dict):
            continue
        step3 = h_data.get("step3_star_of_lord", [])
        step4 = h_data.get("step4_lord", [])
        if planet in step3 or planet in step4:
            houses.append(h_num)
    return houses


def calculate_match_prediction(
    kp_number: int,
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
    transit_planets: Optional[List[Dict]],
    transit_datetime: Optional[datetime],
    significator_data: Dict,
    cuspal_data: List[Dict],
    team_a: str = "Team A",
    team_b: str = "Team B",
    match_type: str = "cricket",
) -> Dict:
    """
    KP Horary Sports / Match Prediction — Who will WIN / LOSE.

    Exact rules from handwritten notes (4-step significator theory):

    TEAM A (Favourite / Querent — takes Lagna):
      WINS if 6th SL → 6, 10, 11, 1, 2, 3 at Level 1 or 2
        Prime importance: 6, 10, 11
        Cross-check from 12th SL
      LOSES if 6th SL → 12, 5, 4, 7, 8, 9 at Level 1 or 2

    TEAM B (Opponent — 7th house):
      WINS if 12th SL → 12, 5, 4, 7, 8, 9 at Level 1 or 2
        Prime importance: 12, 5, 4
        Cross-check from 5th SL
      LOSES if 12th SL → 6, 10, 11, 1, 2, 3 at Level 1 or 2

    Level 1 = Planets in STAR of OCCUPANT (strongest)
    Level 2 = OCCUPANT planet itself
    Level 3 = Planets in STAR of LORD
    Level 4 = LORD itself (weakest)

    If mixed houses appear, check opponent combination also.

    Bilateral Series: Same chart, Moon nakshatra lord on match day decides.
    Tournament: 6th SL → 5, 4, 12 = eliminated.
    """
    house_sigs = significator_data.get("houses", {})

    # ── KP Horary pointer ──
    horary_kp = get_kp_from_number(kp_number) if (1 <= kp_number <= 249) else {}

    # ═══ CUSP SUB-LORDS ═══
    def _get_cusp(h):
        c = next((x for x in cuspal_data if x["house"] == h), None)
        return c or {}

    cusp_6 = _get_cusp(6)
    cusp_12 = _get_cusp(12)
    cusp_5 = _get_cusp(5)
    cusp_1 = _get_cusp(1)
    cusp_7 = _get_cusp(7)
    cusp_11 = _get_cusp(11)

    sl_6 = cusp_6.get("sub_lord", "")
    sl_12 = cusp_12.get("sub_lord", "")
    sl_5 = cusp_5.get("sub_lord", "")
    sl_1 = cusp_1.get("sub_lord", "")
    sl_7 = cusp_7.get("sub_lord", "")
    sl_11 = cusp_11.get("sub_lord", "")

    # All houses signified (all 4 levels)
    sl_6_all = _get_planet_signified_houses(sl_6, house_sigs)
    sl_12_all = _get_planet_signified_houses(sl_12, house_sigs)
    sl_5_all = _get_planet_signified_houses(sl_5, house_sigs)

    # Level 1-2 only (strongest)
    sl_6_L12 = _get_level12_houses(sl_6, house_sigs)
    sl_6_L34 = _get_level34_houses(sl_6, house_sigs)
    sl_12_L12 = _get_level12_houses(sl_12, house_sigs)
    sl_12_L34 = _get_level34_houses(sl_12, house_sigs)
    sl_5_L12 = _get_level12_houses(sl_5, house_sigs)

    # ═══ TEAM A ANALYSIS (6th SL) ═══
    team_a_win_houses = [6, 10, 11, 1, 2, 3]
    team_a_win_prime = [6, 10, 11]
    team_a_lose_houses = [12, 5, 4, 7, 8, 9]

    team_a_score = 0
    team_b_score = 0
    reasons = []

    # Check 6th SL at Level 1-2
    sl6_win_L12 = [h for h in team_a_win_houses if h in sl_6_L12]
    sl6_win_prime_L12 = [h for h in team_a_win_prime if h in sl_6_L12]
    sl6_lose_L12 = [h for h in team_a_lose_houses if h in sl_6_L12]

    # Also check Level 3-4 (weaker)
    sl6_win_L34 = [h for h in team_a_win_houses if h in sl_6_L34]
    sl6_lose_L34 = [h for h in team_a_lose_houses if h in sl_6_L34]

    if sl6_win_prime_L12:
        team_a_score += 40
        reasons.append(f"6th SL ({sl_6}) is PRIMARY significator (L1/L2) of PRIME win houses {sl6_win_prime_L12} → STRONG for {team_a}")
    elif sl6_win_L12:
        team_a_score += 30
        reasons.append(f"6th SL ({sl_6}) is PRIMARY significator (L1/L2) of win houses {sl6_win_L12} → {team_a} favored")

    if sl6_lose_L12:
        team_b_score += 35
        reasons.append(f"6th SL ({sl_6}) is PRIMARY significator (L1/L2) of loss houses {sl6_lose_L12} → {team_a} likely to LOSE")

    # Level 3-4 (weaker confirmation)
    if sl6_win_L34 and not sl6_win_L12:
        team_a_score += 10
        reasons.append(f"6th SL ({sl_6}) is L3/L4 significator of win houses {sl6_win_L34} (weak support for {team_a})")
    if sl6_lose_L34 and not sl6_lose_L12:
        team_b_score += 8
        reasons.append(f"6th SL ({sl_6}) is L3/L4 significator of loss houses {sl6_lose_L34} (weak negative for {team_a})")

    # ═══ CROSS-CHECK from 12th SL ═══
    # 12th cusp = 6th from 7th = opponent's victory house
    team_b_win_houses = [12, 5, 4, 7, 8, 9]
    team_b_win_prime = [12, 5, 4]
    team_b_lose_houses = [6, 10, 11, 1, 2, 3]

    sl12_win_L12 = [h for h in team_b_win_houses if h in sl_12_L12]
    sl12_win_prime_L12 = [h for h in team_b_win_prime if h in sl_12_L12]
    sl12_lose_L12 = [h for h in team_b_lose_houses if h in sl_12_L12]
    sl12_win_L34 = [h for h in team_b_win_houses if h in sl_12_L34]
    sl12_lose_L34 = [h for h in team_b_lose_houses if h in sl_12_L34]

    if sl12_win_prime_L12:
        team_b_score += 40
        reasons.append(f"12th SL ({sl_12}) is PRIMARY significator (L1/L2) of PRIME opponent-win houses {sl12_win_prime_L12} → STRONG for {team_b}")
    elif sl12_win_L12:
        team_b_score += 30
        reasons.append(f"12th SL ({sl_12}) is PRIMARY significator (L1/L2) of opponent-win houses {sl12_win_L12} → {team_b} favored")

    if sl12_lose_L12:
        team_a_score += 30
        reasons.append(f"12th SL ({sl_12}) is PRIMARY significator (L1/L2) of opponent-loss houses {sl12_lose_L12} → {team_b} weakened, confirms {team_a}")

    if sl12_win_L34 and not sl12_win_L12:
        team_b_score += 8
        reasons.append(f"12th SL ({sl_12}) is L3/L4 significator of {sl12_win_L34} (weak for {team_b})")
    if sl12_lose_L34 and not sl12_lose_L12:
        team_a_score += 5
        reasons.append(f"12th SL ({sl_12}) is L3/L4 significator of {sl12_lose_L34} (weak confirmation for {team_a})")

    # ═══ 5th SL CROSS-CHECK (11th from 7th = opponent's gains) ═══
    sl5_b_gain = [h for h in team_b_win_houses if h in sl_5_L12]
    if sl5_b_gain:
        team_b_score += 15
        reasons.append(f"5th SL ({sl_5}) confirms {team_b} gains: L1/L2 in {sl5_b_gain}")

    sl5_b_deny = [h for h in team_b_lose_houses if h in sl_5_L12]
    if sl5_b_deny:
        team_a_score += 10
        reasons.append(f"5th SL ({sl_5}) denies {team_b} gains: L1/L2 in {sl5_b_deny}")

    # ═══ RETROGRADE CHECK — 3-tier per Futuretek PDF Page 25 ═══
    # Rahu & Ketu are always retrograde — exclude from retro penalty
    # Sun & Moon are never retrograde
    _ALWAYS_RETRO = {"Rahu", "Ketu"}
    _NEVER_RETRO = {"Sun", "Moon"}

    def _is_retro(planet_name, planet_list):
        if planet_name in _ALWAYS_RETRO or planet_name in _NEVER_RETRO:
            return False
        pd = next((p for p in planet_list if p["planet"] == planet_name), None)
        return pd and pd.get("speed", 0) < 0

    def _get_retro_tier(sl_name, planet_list):
        """Compute 3-tier retro status for a sub-lord."""
        sl_pd = next((p for p in planet_list if p["planet"] == sl_name), None)
        if not sl_pd:
            return 0, ""
        sl_is_retro = _is_retro(sl_name, planet_list)
        # Find depositor (star lord of sub-lord's position)
        sl_kp = get_kp_pointer(sl_pd["longitude"])
        depositor = sl_kp.get("star_lord", "")
        dep_is_retro = _is_retro(depositor, planet_list) if depositor else False
        if sl_is_retro and not dep_is_retro:
            return 1, depositor  # delayed
        elif sl_is_retro and dep_is_retro:
            return 2, depositor  # total failure
        elif not sl_is_retro and dep_is_retro:
            return 3, depositor  # cannot give result
        return 0, depositor

    sl_6_retro_tier, sl_6_dep = _get_retro_tier(sl_6, planets)
    sl_12_retro_tier, sl_12_dep = _get_retro_tier(sl_12, planets)

    sl_6_retro = sl_6_retro_tier >= 2  # For backward compat in return dict

    if sl_6_retro_tier == 1:
        team_a_score -= 12
        reasons.append(f"RETRO TIER-1: 6th SL ({sl_6}) is RETRO in star of DIRECT {sl_6_dep} — {team_a} result delayed")
    elif sl_6_retro_tier == 2:
        team_a_score -= 30
        reasons.append(f"RETRO TIER-2 DENIAL: 6th SL ({sl_6}) is RETRO in star of RETRO {sl_6_dep} — {team_a} victory DENIED (total failure)")
    elif sl_6_retro_tier == 3:
        team_a_score -= 25
        reasons.append(f"RETRO TIER-3 BLOCK: 6th SL ({sl_6}) is DIRECT in star of RETRO {sl_6_dep} — CANNOT give result for {team_a}")

    if sl_12_retro_tier == 1:
        team_b_score -= 10
        reasons.append(f"RETRO TIER-1: 12th SL ({sl_12}) is RETRO in star of DIRECT {sl_12_dep} — {team_b} result delayed")
    elif sl_12_retro_tier == 2:
        team_b_score -= 25
        reasons.append(f"RETRO TIER-2 DENIAL: 12th SL ({sl_12}) is RETRO in star of RETRO {sl_12_dep} — {team_b} victory DENIED")
    elif sl_12_retro_tier == 3:
        team_b_score -= 20
        reasons.append(f"RETRO TIER-3 BLOCK: 12th SL ({sl_12}) is DIRECT in star of RETRO {sl_12_dep} — CANNOT give result for {team_b}")

    # ═══ MOON NAKSHATRA (for bilateral series timing) ═══
    moon_nak_info = None
    if transit_planets:
        moon = next((p for p in transit_planets if p["planet"] == "Moon"), None)
        if moon:
            moon_kp = get_kp_pointer(moon["longitude"])
            nak_lord = moon_kp.get("star_lord", "")
            nak_lord_L12 = _get_level12_houses(nak_lord, house_sigs)
            nak_lord_all = _get_planet_signified_houses(nak_lord, house_sigs)
            moon_nak_info = {
                "nakshatra": moon_kp.get("nakshatra", ""),
                "nak_lord": nak_lord,
                "nak_lord_signifies_all": nak_lord_all,
                "nak_lord_signifies_L12": nak_lord_L12,
                "moon_sign": moon_kp.get("sign", ""),
                "moon_longitude": round(moon["longitude"], 4),
            }
            # Moon nak lord signification adds to score
            nak_a_houses = [h for h in team_a_win_houses if h in nak_lord_all]
            nak_b_houses = [h for h in team_b_win_houses if h in nak_lord_all]
            if nak_a_houses:
                team_a_score += len(nak_a_houses) * 3
                reasons.append(f"Moon in {moon_kp['nakshatra']} — Nak lord {nak_lord} signifies {team_a} win houses {nak_a_houses}")
            if nak_b_houses:
                team_b_score += len(nak_b_houses) * 3
                reasons.append(f"Moon in {moon_kp['nakshatra']} — Nak lord {nak_lord} signifies {team_b} win houses {nak_b_houses}")

    # ═══ RULING PLANETS ═══
    rp_data = None
    fruitful_a = []
    fruitful_b = []
    if transit_planets and transit_datetime:
        rp_data = calculate_current_ruling_planets(
            transit_planets, ascendant, transit_datetime
        )
        rp_planets = set(r["planet"] for r in rp_data.get("rp_rows", []))

        # Discard RP in star of retrograde (Rahu/Ketu always retro — exclude)
        valid_rps = []
        for rp_p in rp_planets:
            rp_pd = next((p for p in transit_planets if p["planet"] == rp_p), None)
            if rp_pd:
                rp_kp = get_kp_pointer(rp_pd["longitude"])
                rp_sl = rp_kp.get("star_lord", "")
                if rp_sl not in _ALWAYS_RETRO:
                    rp_sl_pd = next((p for p in transit_planets if p["planet"] == rp_sl), None)
                    if rp_sl_pd and rp_sl_pd.get("speed", 0) < 0:
                        continue
            valid_rps.append(rp_p)

        # Rahu/Ketu agent
        for node in ["Rahu", "Ketu"]:
            nd = next((p for p in transit_planets if p["planet"] == node), None)
            if nd:
                nkp = get_kp_pointer(nd["longitude"])
                agent = nkp.get("sign_lord", "")
                if agent in rp_planets and node not in valid_rps:
                    valid_rps.append(node)

        # Team A fruitful = significators of 1,2,3,6,10,11 ∩ RP
        sigs_a = set()
        for h in [1, 2, 3, 6, 10, 11]:
            hd = house_sigs.get(h, {})
            for s in hd.get("all_significators", []):
                sigs_a.add(s)
        fruitful_a = sorted(sigs_a & set(valid_rps))

        # Team B fruitful = significators of 4,5,7,8,9,12 ∩ RP
        sigs_b = set()
        for h in [4, 5, 7, 8, 9, 12]:
            hd = house_sigs.get(h, {})
            for s in hd.get("all_significators", []):
                sigs_b.add(s)
        fruitful_b = sorted(sigs_b & set(valid_rps))

        if len(fruitful_a) > len(fruitful_b):
            team_a_score += len(fruitful_a) * 4
            reasons.append(f"RP match favors {team_a}: {len(fruitful_a)} fruitful sigs ({', '.join(fruitful_a)}) vs {len(fruitful_b)} for {team_b}")
        elif len(fruitful_b) > len(fruitful_a):
            team_b_score += len(fruitful_b) * 4
            reasons.append(f"RP match favors {team_b}: {len(fruitful_b)} fruitful sigs ({', '.join(fruitful_b)}) vs {len(fruitful_a)} for {team_a}")
        else:
            reasons.append(f"RP match is equal: {len(fruitful_a)} each — very close contest")

    # ═══ TOURNAMENT ELIMINATION CHECK ═══
    elimination_houses = [5, 4, 12]
    sl6_elim = [h for h in elimination_houses if h in sl_6_L12]
    is_eliminated = len(sl6_elim) > 0
    if is_eliminated:
        reasons.append(f"TOURNAMENT: 6th SL ({sl_6}) is L1/L2 significator of {sl6_elim} → {team_a} would be ELIMINATED in a tournament")

    # ═══ FINAL VERDICT ═══
    if team_a_score > team_b_score + 15:
        winner = team_a
        verdict = f"{team_a} WINS"
        verdict_type = "team_a"
    elif team_b_score > team_a_score + 15:
        winner = team_b
        verdict = f"{team_b} WINS"
        verdict_type = "team_b"
    elif team_a_score > team_b_score:
        winner = team_a
        verdict = f"{team_a} slight edge — close match"
        verdict_type = "team_a_close"
    elif team_b_score > team_a_score:
        winner = team_b
        verdict = f"{team_b} slight edge — close match"
        verdict_type = "team_b_close"
    else:
        winner = "Too Close to Call"
        verdict = "DRAW / Very Close Match"
        verdict_type = "draw"

    # Confidence
    total = max(team_a_score + team_b_score, 1)
    confidence = abs(team_a_score - team_b_score) / total * 100
    confidence = min(95, max(5, confidence))

    # Per-cusp detail table — show levels
    cusp_details = []
    for h in [1, 5, 6, 7, 11, 12]:
        c = _get_cusp(h)
        if c:
            sl = c.get("sub_lord", "")
            sl_L12 = _get_level12_houses(sl, house_sigs)
            sl_L34 = _get_level34_houses(sl, house_sigs)
            sl_all = _get_planet_signified_houses(sl, house_sigs)
            role_map = {
                1: f"{team_a} (Self/Lagna)",
                5: f"{team_b} Gains (11th from 7th)",
                6: f"{team_a} Victory (PRIMARY)",
                7: f"{team_b} (Opponent)",
                11: f"{team_a} Gains/Desire",
                12: f"{team_b} Victory (6th from 7th)",
            }
            cusp_details.append({
                "house": h,
                "role": role_map.get(h, ""),
                "sub_lord": sl,
                "star_lord": c.get("star_lord", ""),
                "sign": c.get("sign", ""),
                "signifies_all": sl_all,
                "signifies_L12": sl_L12,
                "signifies_L34": sl_L34,
            })

    # Build 4-step detail for 6th and 12th SL
    def _build_4step_detail(planet, h_sigs):
        detail = {}
        for h_num, h_data in h_sigs.items():
            s1 = h_data.get("step1_star_of_occ", [])
            s2 = h_data.get("step2_occupants", h_data.get("occupants", []))
            s3 = h_data.get("step3_star_of_lord", [])
            s4 = h_data.get("step4_lord", [])
            levels = []
            if planet in s1:
                levels.append("L1 (Star-of-Occupant)")
            if planet in s2:
                levels.append("L2 (Occupant)")
            if planet in s3:
                levels.append("L3 (Star-of-Lord)")
            if planet in s4:
                levels.append("L4 (Lord)")
            if levels:
                detail[h_num] = levels
        return detail

    sl6_4step = _build_4step_detail(sl_6, house_sigs)
    sl12_4step = _build_4step_detail(sl_12, house_sigs)

    return {
        "match_type":           MATCH_CATEGORIES.get(match_type, match_type),
        "team_a":               team_a,
        "team_b":               team_b,
        "kp_number":            kp_number,
        "horary_kp":            horary_kp,
        "winner":               winner,
        "verdict":              verdict,
        "verdict_type":         verdict_type,
        "team_a_score":         team_a_score,
        "team_b_score":         team_b_score,
        "confidence":           round(confidence, 1),
        "cusp_6_sub_lord":      sl_6,
        "cusp_6_signifies":     sl_6_all,
        "cusp_6_L12":           sl_6_L12,
        "cusp_6_L34":           sl_6_L34,
        "cusp_12_sub_lord":     sl_12,
        "cusp_12_signifies":    sl_12_all,
        "cusp_12_L12":          sl_12_L12,
        "cusp_12_L34":          sl_12_L34,
        "cusp_11_sub_lord":     sl_11,
        "cusp_11_signifies":    _get_planet_signified_houses(sl_11, house_sigs),
        "is_6sl_retro":         bool(sl_6_retro),
        "retro_tier_6":         sl_6_retro_tier,
        "retro_tier_12":        sl_12_retro_tier,
        "is_12sl_retro":        sl_12_retro_tier >= 2,
        "is_eliminated":        is_eliminated,
        "elimination_houses":   sl6_elim,
        "cusp_details":         cusp_details,
        "sl6_4step":            sl6_4step,
        "sl12_4step":           sl12_4step,
        "moon_nakshatra":       moon_nak_info,
        "ruling_planets":       rp_data,
        "fruitful_team_a":      fruitful_a,
        "fruitful_team_b":      fruitful_b,
        "reasons":              reasons,
    }


def calculate_toss_prediction(
    kp_number: int,
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
    transit_planets: Optional[List[Dict]],
    transit_datetime: Optional[datetime],
    significator_data: Dict,
    cuspal_data: List[Dict],
    team_a: str = "Team A",
    team_b: str = "Team B",
) -> Dict:
    """
    KP Horary Toss Prediction — Who will WIN the TOSS.

    The toss is a separate mini-competition before the match.
    User thinks of a SEPARATE KP number (1-249) while asking
    "Who will win the toss?"

    KP Logic:
    - 6th cusp sub-lord signifying 6, 10, 11 → Team A wins toss
    - 6th cusp sub-lord signifying 5, 12 → Team B wins toss
    - 1st cusp sub-lord strength = Team A's overall luck at query moment
    - 3-tier retrograde rules apply (PDF Page 25)
    - Ruling Planets confirm timing

    Time to use: The moment you think of the KP number and ask
    "Who will win the toss?" — NOT the actual toss time.
    """
    house_sigs = significator_data.get("houses", {})

    horary_kp = get_kp_from_number(kp_number) if (1 <= kp_number <= 249) else {}

    # Cusps
    def _get_cusp(h):
        return next((x for x in cuspal_data if x["house"] == h), {})

    cusp_6 = _get_cusp(6)
    cusp_12 = _get_cusp(12)
    cusp_1 = _get_cusp(1)

    sl_6 = cusp_6.get("sub_lord", "")
    sl_12 = cusp_12.get("sub_lord", "")
    sl_1 = cusp_1.get("sub_lord", "")

    # House significations of 6th sub-lord
    sl_6_all = _get_planet_signified_houses(sl_6, house_sigs)
    sl_6_L12 = _get_level12_houses(sl_6, house_sigs)

    # Team A wins toss: 6th SL → 6, 10, 11 (own victory houses)
    team_a_toss_houses = [6, 10, 11]
    # Team B wins toss: 6th SL → 5, 12 (opponent's victory = 12th from 7th = 6th? No—
    # 12th = loss to querent, 5th = 11th from 7th = opponent's gain)
    team_b_toss_houses = [5, 12]

    team_a_score = 0
    team_b_score = 0
    reasons = []

    # Check 6th SL signification
    sl6_a_match = [h for h in team_a_toss_houses if h in sl_6_L12]
    sl6_a_all = [h for h in team_a_toss_houses if h in sl_6_all]
    sl6_b_match = [h for h in team_b_toss_houses if h in sl_6_L12]
    sl6_b_all = [h for h in team_b_toss_houses if h in sl_6_all]

    if sl6_a_match:
        team_a_score += len(sl6_a_match) * 15
        reasons.append(f"6th SL ({sl_6}) signifies {team_a} toss-win houses {sl6_a_match} at L1/L2 (strong)")
    if sl6_a_all and not sl6_a_match:
        a_extra = [h for h in sl6_a_all if h not in sl6_a_match]
        if a_extra:
            team_a_score += len(a_extra) * 5
            reasons.append(f"6th SL ({sl_6}) signifies {team_a} toss-win houses {a_extra} at L3/L4 (supportive)")

    if sl6_b_match:
        team_b_score += len(sl6_b_match) * 15
        reasons.append(f"6th SL ({sl_6}) signifies {team_b} toss-win houses {sl6_b_match} at L1/L2 (strong)")
    if sl6_b_all and not sl6_b_match:
        b_extra = [h for h in sl6_b_all if h not in sl6_b_match]
        if b_extra:
            team_b_score += len(b_extra) * 5
            reasons.append(f"6th SL ({sl_6}) signifies {team_b} toss-win houses {b_extra} at L3/L4 (supportive)")

    # Cross-check with 12th SL
    sl_12_all = _get_planet_signified_houses(sl_12, house_sigs)
    sl_12_L12 = _get_level12_houses(sl_12, house_sigs)
    sl12_b_match = [h for h in team_b_toss_houses if h in sl_12_L12]
    sl12_a_deny = [h for h in team_a_toss_houses if h in sl_12_L12]

    if sl12_b_match:
        team_b_score += len(sl12_b_match) * 10
        reasons.append(f"12th SL ({sl_12}) confirms {team_b}: signifies {sl12_b_match} at L1/L2")
    if sl12_a_deny:
        team_a_score -= len(sl12_a_deny) * 5
        reasons.append(f"12th SL ({sl_12}) weakens {team_a}: signifies {team_a} houses {sl12_a_deny} from opponent cusp")

    # 1st cusp sub-lord — querent's luck indicator
    sl_1_all = _get_planet_signified_houses(sl_1, house_sigs)
    sl1_luck = [h for h in [1, 3, 11] if h in sl_1_all]
    if sl1_luck:
        team_a_score += len(sl1_luck) * 3
        reasons.append(f"1st SL ({sl_1}) signifies luck houses {sl1_luck} — favours {team_a}")

    # ═══ RETROGRADE CHECK — 3-tier ═══
    _ALWAYS_RETRO = {"Rahu", "Ketu"}
    _NEVER_RETRO = {"Sun", "Moon"}

    def _is_retro_t(planet_name, planet_list):
        if planet_name in _ALWAYS_RETRO or planet_name in _NEVER_RETRO:
            return False
        pd = next((p for p in planet_list if p["planet"] == planet_name), None)
        return pd and pd.get("speed", 0) < 0

    def _get_retro_tier_t(sl_name, planet_list):
        sl_pd = next((p for p in planet_list if p["planet"] == sl_name), None)
        if not sl_pd:
            return 0, ""
        sl_is_retro = _is_retro_t(sl_name, planet_list)
        sl_kp = get_kp_pointer(sl_pd["longitude"])
        depositor = sl_kp.get("star_lord", "")
        dep_is_retro = _is_retro_t(depositor, planet_list) if depositor else False
        if sl_is_retro and not dep_is_retro:
            return 1, depositor
        elif sl_is_retro and dep_is_retro:
            return 2, depositor
        elif not sl_is_retro and dep_is_retro:
            return 3, depositor
        return 0, depositor

    retro_tier_6, dep_6 = _get_retro_tier_t(sl_6, planets)
    if retro_tier_6 == 1:
        team_a_score -= 8
        reasons.append(f"RETRO TIER-1: 6th SL ({sl_6}) RETRO in star of DIRECT {dep_6} — {team_a} toss delayed/uncertain")
    elif retro_tier_6 == 2:
        team_a_score -= 25
        reasons.append(f"RETRO TIER-2: 6th SL ({sl_6}) RETRO in star of RETRO {dep_6} — {team_a} toss DENIED")
    elif retro_tier_6 == 3:
        team_a_score -= 20
        reasons.append(f"RETRO TIER-3: 6th SL ({sl_6}) DIRECT in star of RETRO {dep_6} — cannot give toss result for {team_a}")

    # ═══ RULING PLANETS ═══
    rp_data = None
    fruitful_a = []
    fruitful_b = []
    if transit_planets and transit_datetime:
        rp_data = calculate_current_ruling_planets(
            transit_planets, ascendant, transit_datetime,
        )
        rp_planets = [r["planet"] for r in rp_data.get("rp_rows", [])]
        rp_set = set(rp_planets)

        # Discard RP in star of retro (except Rahu/Ketu stars)
        valid_rps = []
        for rp_p in rp_set:
            rp_pd = next((p for p in transit_planets if p["planet"] == rp_p), None)
            if rp_pd:
                rp_kp = get_kp_pointer(rp_pd["longitude"])
                rp_sl = rp_kp.get("star_lord", "")
                if rp_sl not in _ALWAYS_RETRO:
                    rp_star_pd = next((p for p in transit_planets if p["planet"] == rp_sl), None)
                    if rp_star_pd and rp_star_pd.get("speed", 0) < 0:
                        continue
            valid_rps.append(rp_p)

        # Fruitful significators for toss
        all_sigs_a = set()
        for h in team_a_toss_houses:
            h_data = house_sigs.get(h, {})
            for s in h_data.get("all_significators", []):
                all_sigs_a.add(s)
        fruitful_a = sorted(all_sigs_a & set(valid_rps))

        all_sigs_b = set()
        for h in team_b_toss_houses:
            h_data = house_sigs.get(h, {})
            for s in h_data.get("all_significators", []):
                all_sigs_b.add(s)
        fruitful_b = sorted(all_sigs_b & set(valid_rps))

        if len(fruitful_a) > len(fruitful_b):
            team_a_score += (len(fruitful_a) - len(fruitful_b)) * 5
            reasons.append(f"RP favours {team_a} toss: {len(fruitful_a)} fruitful sigs vs {len(fruitful_b)} for {team_b}")
        elif len(fruitful_b) > len(fruitful_a):
            team_b_score += (len(fruitful_b) - len(fruitful_a)) * 5
            reasons.append(f"RP favours {team_b} toss: {len(fruitful_b)} fruitful sigs vs {len(fruitful_a)} for {team_a}")

    # ═══ VERDICT ═══
    diff = team_a_score - team_b_score
    if diff > 10:
        winner = team_a
        verdict = f"{team_a} WINS THE TOSS"
        verdict_type = "team_a"
    elif diff < -10:
        winner = team_b
        verdict = f"{team_b} WINS THE TOSS"
        verdict_type = "team_b"
    else:
        winner = "Uncertain"
        verdict = "TOSS RESULT UNCLEAR — marginal difference"
        verdict_type = "draw"

    confidence = min(95, abs(diff) * 2.5 + 20) if abs(diff) > 5 else max(10, abs(diff) * 5)

    return {
        "prediction_type":      "toss",
        "team_a":               team_a,
        "team_b":               team_b,
        "kp_number":            kp_number,
        "horary_kp":            horary_kp,
        "winner":               winner,
        "verdict":              verdict,
        "verdict_type":         verdict_type,
        "team_a_score":         team_a_score,
        "team_b_score":         team_b_score,
        "confidence":           round(confidence, 1),
        "cusp_6_sub_lord":      sl_6,
        "cusp_6_signifies":     sl_6_all,
        "cusp_12_sub_lord":     sl_12,
        "cusp_12_signifies":    sl_12_all,
        "retro_tier_6":         retro_tier_6,
        "ruling_planets":       rp_data,
        "fruitful_team_a":      fruitful_a,
        "fruitful_team_b":      fruitful_b,
        "reasons":              reasons,
    }


def analyze_promise_denial(
    cuspal_data: List[Dict],
    significator_data: Dict,
    planet_sig_table: List[Dict],
) -> Dict:
    """
    For each house and each house group, determine PROMISE or DENIAL
    based on the cusp sub-lord's signification.

    KP Rule: The sub-lord of a house cusp determines the outcome.
    - If cusp sub-lord signifies the house → PROMISE
    - If cusp sub-lord signifies houses inimical to it → DENIAL
    - If cusp sub-lord's star-lord signifies → check further
    """
    house_sigs = significator_data["houses"]

    # Per-house promise/denial
    house_verdicts: Dict[int, Dict] = {}
    for cusp in cuspal_data:
        h_num = cusp["house"]
        sub_lord = cusp["sub_lord"]
        star_lord = cusp["star_lord"]

        # Find which houses the sub-lord signifies
        sub_lord_houses = _get_planet_signified_houses(sub_lord, house_sigs)
        star_lord_houses = _get_planet_signified_houses(star_lord, house_sigs)

        # Check: does sub-lord signify this house?
        signifies_own = h_num in sub_lord_houses
        # Check: does sub-lord signify 12th from this house? (denial)
        deny_house = ((h_num - 1 + 11) % 12) + 1  # 12th from h
        signifies_denial = deny_house in sub_lord_houses

        if signifies_own and not signifies_denial:
            verdict = "PROMISE"
            strength = "Strong"
        elif signifies_own and signifies_denial:
            verdict = "PROMISE (Mixed)"
            strength = "Moderate"
        elif signifies_denial and not signifies_own:
            verdict = "DENIAL"
            strength = "Blocked"
        else:
            # Neither directly promises nor denies — check star-lord
            if h_num in star_lord_houses:
                verdict = "PROMISE (Indirect)"
                strength = "Mild"
            else:
                verdict = "NEUTRAL"
                strength = "Uncertain"

        house_verdicts[h_num] = {
            "house":              h_num,
            "cusp_sub_lord":      sub_lord,
            "cusp_star_lord":     star_lord,
            "sub_lord_signifies": sub_lord_houses,
            "verdict":            verdict,
            "strength":           strength,
            "signifies_own":      signifies_own,
            "signifies_denial":   signifies_denial,
        }

    # House group analysis
    group_verdicts: Dict[str, Dict] = {}
    for group_key, group_info in HOUSE_GROUPS.items():
        group_houses = group_info["houses"]
        deny_houses = group_info["deny"]

        # Count promises and denials across group houses
        promises = 0
        denials = 0
        details = []
        for h in group_houses:
            hv = house_verdicts.get(h, {})
            v = hv.get("verdict", "NEUTRAL")
            if "PROMISE" in v:
                promises += 1
            elif v == "DENIAL":
                denials += 1
            details.append({"house": h, "verdict": v})

        if promises > denials:
            group_verdict = "FAVORABLE"
        elif denials > promises:
            group_verdict = "UNFAVORABLE"
        else:
            group_verdict = "MIXED"

        group_verdicts[group_key] = {
            "label":    group_info["label"],
            "houses":   group_houses,
            "verdict":  group_verdict,
            "promises": promises,
            "denials":  denials,
            "details":  details,
        }

    return {
        "house_verdicts": house_verdicts,
        "group_verdicts": group_verdicts,
    }


def _get_planet_signified_houses(planet: str, house_sigs: Dict) -> List[int]:
    """Get all houses a planet signifies."""
    houses = []
    for h_num, h_data in house_sigs.items():
        if isinstance(h_data, dict):
            if planet in h_data.get("all_significators", []):
                houses.append(h_num)
        # Skip non-dict entries (e.g. metadata strings)
    return houses


# ═════════════════════════════════════════════════════════════
# 7. RULING PLANETS (RP) for Event Timing
# ═════════════════════════════════════════════════════════════

def calculate_ruling_planets(
    transit_planets: List[Dict],
    transit_datetime: datetime,
    ascendant: Dict,
) -> Dict:
    """
    KP Ruling Planets at the moment of query/event.
    RP = Sign Lord + Star Lord + Sub Lord of:
    1. Ascendant at query time
    2. Moon at query time
    3. Day lord (weekday lord)

    Ruling planets indicate WHICH planets are active NOW and
    help pinpoint exact timing of market events.
    Planets appearing multiple times are stronger RPs.
    """
    weekday = transit_datetime.weekday()
    day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    day_lord = day_lords[weekday]

    moon = next((p for p in transit_planets if p["planet"] == "Moon"), None)
    moon_kp = get_kp_pointer(moon["longitude"]) if moon else {}
    asc_kp = get_kp_pointer(ascendant["longitude"])

    # Collect all ruling planets with sources
    rp_sources = []
    if asc_kp:
        rp_sources.append({"planet": asc_kp["sign_lord"],  "source": "Asc Sign Lord"})
        rp_sources.append({"planet": asc_kp["star_lord"],  "source": "Asc Star Lord"})
        rp_sources.append({"planet": asc_kp["sub_lord"],   "source": "Asc Sub Lord"})
    if moon_kp:
        rp_sources.append({"planet": moon_kp["sign_lord"], "source": "Moon Sign Lord"})
        rp_sources.append({"planet": moon_kp["star_lord"], "source": "Moon Star Lord"})
        rp_sources.append({"planet": moon_kp["sub_lord"],  "source": "Moon Sub Lord"})
    rp_sources.append({"planet": day_lord, "source": "Day Lord"})

    # Count
    rp_list = [r["planet"] for r in rp_sources]
    rp_counts = Counter(rp_list)
    sorted_rps = sorted(rp_counts.items(), key=lambda x: -x[1])

    primary = [rp for rp, count in sorted_rps if count >= 2]
    secondary = [rp for rp, count in sorted_rps if count == 1]

    return {
        "query_datetime":  transit_datetime.strftime("%Y-%m-%d %H:%M"),
        "day_lord":        day_lord,
        "ascendant_kp":    asc_kp,
        "moon_kp":         moon_kp,
        "rp_sources":      rp_sources,
        "ruling_planets": {
            "all":       [{"planet": rp, "strength": c} for rp, c in sorted_rps],
            "primary":   primary,
            "secondary": secondary,
        },
        "financial_timing": _rp_financial_timing(primary, secondary),
    }


def _rp_financial_timing(primary: List[str], secondary: List[str]) -> Dict:
    """Market timing interpretation from Ruling Planets."""
    bullish = {"Jupiter", "Venus", "Moon", "Mercury"}
    bearish = {"Saturn", "Mars", "Rahu", "Ketu"}

    bull_count = sum(1 for p in primary if p in bullish)
    bear_count = sum(1 for p in primary if p in bearish)

    if bull_count > bear_count:
        signal, action = "BULLISH", "Good time for market entry / buying"
    elif bear_count > bull_count:
        signal, action = "BEARISH", "Avoid new entries / consider exit"
    else:
        signal, action = "NEUTRAL", "Wait for clearer ruling planet alignment"

    active_sectors = []
    for rp in primary:
        sectors = FINANCIAL_KARAKAS.get(rp, "")
        if sectors:
            active_sectors.append(f"{rp}: {sectors}")

    return {
        "signal":         signal,
        "action":         action,
        "bullish_rps":    bull_count,
        "bearish_rps":    bear_count,
        "active_sectors": active_sectors,
    }


# ═════════════════════════════════════════════════════════════
# 8. DBA SIGNIFICATOR MATCHING (Dasha–Bhukti–Antara)
# ═════════════════════════════════════════════════════════════

def analyze_dba_significators(
    dasha_data: Optional[Dict],
    current_dasha: Optional[Dict],
    significator_data: Dict,
) -> Optional[Dict]:
    """
    Check if the current Dasha-Bhukti-Antara lords are significators
    of wealth/speculation houses. This confirms event timing.

    Rule: Event happens when DBA lords are significators of the
    relevant house group AND overlap with ruling planets.
    """
    if not current_dasha:
        return None

    house_sigs = significator_data["houses"]
    maha = current_dasha.get("mahadasha", "")
    antar = current_dasha.get("antardasha", "")
    pratyantar = current_dasha.get("pratyantar", "")

    dba_lords = [maha, antar, pratyantar]
    dba_lords = [d for d in dba_lords if d]

    # For each DBA lord, find signified houses
    dba_analysis = []
    for lord in dba_lords:
        signified = _get_planet_signified_houses(lord, house_sigs)
        dba_analysis.append({
            "lord":             lord,
            "signified_houses": signified,
        })

    # Check which house groups the DBA lords activate
    active_groups = {}
    for group_key, group_info in HOUSE_GROUPS.items():
        group_houses = set(group_info["houses"])
        activating_lords = []
        for da in dba_analysis:
            overlap = group_houses & set(da["signified_houses"])
            if overlap:
                activating_lords.append({
                    "lord":    da["lord"],
                    "houses":  sorted(overlap),
                })
        if activating_lords:
            active_groups[group_key] = {
                "label":  group_info["label"],
                "lords":  activating_lords,
                "active": True,
            }

    return {
        "mahadasha":    maha,
        "antardasha":   antar,
        "pratyantar":   pratyantar,
        "dba_analysis": dba_analysis,
        "active_groups": active_groups,
    }


# ═════════════════════════════════════════════════════════════
# 9. SENSITIVE DEGREE POINTS (Sub-Lord Change Boundaries)
# ═════════════════════════════════════════════════════════════

def get_sensitive_points(longitude: float, range_deg: float = 2.0) -> List[Dict]:
    """
    Find nearby sub-lord change boundaries (sensitive points).
    When a transit planet crosses these, the sub-lord changes
    and significant events may trigger.
    """
    long = longitude % 360.0
    start = long - range_deg
    end = long + range_deg
    points = []

    for entry in KP_SUBLORD_TABLE:
        if start <= entry["start_deg"] <= end:
            points.append({
                "degree":     round(entry["start_deg"], 6),
                "from_sub":   KP_SUBLORD_TABLE[entry["id"] - 2]["sub_lord"] if entry["id"] > 1 else "",
                "to_sub":     entry["sub_lord"],
                "star_lord":  entry["star_lord"],
                "distance":   round(entry["start_deg"] - long, 6),
                "kp_number":  entry["id"],
            })

    return points


# ═════════════════════════════════════════════════════════════
# 10. KP FINANCIAL HOUSE ANALYSIS (Enhanced)
# ═════════════════════════════════════════════════════════════

def kp_financial_analysis(
    cuspal_data: List[Dict],
    significator_data: Dict,
    promise_data: Dict,
) -> Dict:
    """
    Comprehensive KP financial analysis combining cuspal theory,
    significators, and promise/denial for wealth houses.
    """
    financial_houses = {
        2:  "Wealth & Savings",
        5:  "Stock Market & Speculation",
        7:  "Business & Partnerships",
        10: "Career & Professional Income",
        11: "Gains & Profit Realization",
    }

    house_verdicts = promise_data.get("house_verdicts", {})
    house_sigs = significator_data["houses"]
    analysis = {}
    total_score = 0

    for h_num, meaning in financial_houses.items():
        cusp = next((c for c in cuspal_data if c["house"] == h_num), None)
        hv = house_verdicts.get(h_num, {})
        hs = house_sigs.get(h_num, {})

        verdict = hv.get("verdict", "NEUTRAL")
        if "PROMISE" in verdict:
            score = 1.0 if verdict == "PROMISE" else 0.6
        elif verdict == "DENIAL":
            score = -1.0
        else:
            score = 0.0

        total_score += score
        analysis[h_num] = {
            "house":               h_num,
            "meaning":             meaning,
            "cusp_sub_lord":       cusp["sub_lord"] if cusp else "",
            "cusp_star_lord":      cusp["star_lord"] if cusp else "",
            "verdict":             verdict,
            "strength":            hv.get("strength", ""),
            "score":               score,
            "significators":       hs.get("all_significators", []),
            "effective_sigs":      hs.get("effective_significators", []),
            "sub_lord_signifies":  hv.get("sub_lord_signifies", []),
        }

    n = len(financial_houses)
    avg_score = total_score / n if n else 0

    if avg_score > 0.5:
        overall = "KP indicates STRONG financial potential — multiple wealth houses promised"
    elif avg_score > 0:
        overall = "KP indicates MODERATE financial potential — some houses favorable"
    elif avg_score > -0.5:
        overall = "KP indicates MIXED financial outlook — promises and denials coexist"
    else:
        overall = "KP indicates WEAK financial period — key wealth houses denied"

    return {
        "houses":           analysis,
        "avg_score":        round(avg_score, 3),
        "overall_verdict":  overall,
    }


# ═════════════════════════════════════════════════════════════
# 11. DEGREE TO DMS FORMAT
# ═════════════════════════════════════════════════════════════

def deg_to_dms(deg: float) -> str:
    """Convert decimal degrees to DD°MM'SS\" format string."""
    deg = deg % 360.0
    d = int(deg)
    m_full = (deg % 1) * 60
    m = int(m_full)
    s = int((m_full % 1) * 60)
    return f"{d:02d}°{m:02d}'{s:02d}\""


# ═════════════════════════════════════════════════════════════
# 12. ASPECTS ON KP CUSPS
# ═════════════════════════════════════════════════════════════

def calculate_aspects_on_cusps(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
) -> List[Dict]:
    """
    For each cusp (1-12), check which planets aspect it using
    exact degree-based aspects with standard orbs.
    """
    # All 10 aspects matching professional KP software with orbs and weights
    ASPECT_DEFS = [
        {"name": "CN",  "full": "Conjunction",       "angle": 0,   "orb": 15, "weight": 10},
        {"name": "OP",  "full": "Opposition",         "angle": 180, "orb": 15, "weight": 10},
        {"name": "TR",  "full": "Trine",              "angle": 120, "orb": 6,  "weight": 3},
        {"name": "SQ",  "full": "Square",             "angle": 90,  "orb": 6,  "weight": 3},
        {"name": "SX",  "full": "Sextile",            "angle": 60,  "orb": 6,  "weight": 3},
        {"name": "SS",  "full": "Semisquare",         "angle": 45,  "orb": 1,  "weight": 1},
        {"name": "NN",  "full": "Nonile",             "angle": 40,  "orb": 1,  "weight": 1},
        {"name": "QI",  "full": "Quintile",           "angle": 72,  "orb": 1,  "weight": 1},
        {"name": "SQ2", "full": "Sesquiquadrate",     "angle": 135, "orb": 1,  "weight": 1},
        {"name": "QC",  "full": "Quincunx",           "angle": 150, "orb": 1,  "weight": 1},
    ]

    results = []
    for house in houses:
        h_num = house["house"]
        cusp_deg = house["longitude"] % 360.0
        aspects = []

        for p in planets:
            p_long = p["longitude"] % 360.0
            p_speed = p.get("speed", 0)

            for asp_def in ASPECT_DEFS:
                angle = asp_def["angle"]
                max_orb = asp_def["orb"]

                diff = abs(p_long - cusp_deg)
                if diff > 180:
                    diff = 360 - diff

                orb_val = abs(diff - angle)
                if orb_val <= max_orb:
                    # Determine applying vs separating
                    # Project planet position forward by 1 unit of speed
                    future_long = (p_long + p_speed) % 360.0
                    future_diff = abs(future_long - cusp_deg)
                    if future_diff > 180:
                        future_diff = 360 - future_diff
                    future_orb = abs(future_diff - angle)
                    applying = future_orb < orb_val

                    aspects.append({
                        "planet":   p["planet"],
                        "aspect":   asp_def["name"],
                        "full":     asp_def["full"],
                        "orb":      round(orb_val, 2),
                        "weight":   asp_def["weight"],
                        "applying": applying,
                    })

        results.append({
            "house":    h_num,
            "cusp_deg": round(cusp_deg, 4),
            "aspects":  aspects,
        })

    return results


# ═════════════════════════════════════════════════════════════
# 13. CUSPAL SUB-SUB WITH SIGNIFIED HOUSES
# ═════════════════════════════════════════════════════════════

def calculate_cuspal_sub_sub(
    houses: List[Dict],
    significator_data: Dict,
) -> List[Dict]:
    """
    For each cusp, show the star_lord, sub_lord, sub_sub_lord along
    with which houses each lord signifies, and a position status.
    """
    house_sigs = significator_data["houses"]
    results = []

    for house in houses:
        h_num = house["house"]
        cusp_deg = house["longitude"] % 360.0
        kp = get_kp_pointer(cusp_deg)

        star_lord = kp["star_lord"]
        sub_lord = kp["sub_lord"]
        sub_sub_lord = kp["sub_sub_lord"]

        star_lord_houses = _get_planet_signified_houses(star_lord, house_sigs)
        sub_lord_houses = _get_planet_signified_houses(sub_lord, house_sigs)
        sub_sub_lord_houses = _get_planet_signified_houses(sub_sub_lord, house_sigs)

        # Position status: Promise if sub_lord signifies this house,
        # Denial if it signifies 12th from this house, else Neutral
        deny_house = ((h_num - 1 + 11) % 12) + 1  # 12th from h_num
        if h_num in sub_lord_houses:
            position_status = "Promise"
        elif deny_house in sub_lord_houses:
            position_status = "Denial"
        else:
            position_status = "Neutral"

        results.append({
            "house":               h_num,
            "cusp_deg":            round(cusp_deg, 4),
            "cusp_dms":            deg_to_dms(cusp_deg),
            "star_lord":           star_lord,
            "star_lord_houses":    star_lord_houses,
            "sub_lord":            sub_lord,
            "sub_lord_houses":     sub_lord_houses,
            "sub_sub_lord":        sub_sub_lord,
            "sub_sub_lord_houses": sub_sub_lord_houses,
            "position_status":     position_status,
        })

    return results


# ═════════════════════════════════════════════════════════════
# 14. NAKSHATRA NADI VIEW
# ═════════════════════════════════════════════════════════════

def build_nakshatra_nadi(
    planets: List[Dict],
    significator_data: Dict,
    ascendant: Optional[Dict] = None,
) -> List[Dict]:
    """
    Nakshatra Nadi view: for each planet, show the star lord and sub lord
    with their signified house numbers in a compact nadi string.
    Includes Ascendant when provided.
    """
    house_sigs = significator_data["houses"]
    results = []

    all_bodies = list(planets)
    if ascendant:
        all_bodies.append(_make_ascendant_pseudo_planet(ascendant))

    for p in all_bodies:
        pname = p["planet"]
        kp = get_kp_pointer(p["longitude"])
        star_lord = kp["star_lord"]
        sub_lord = kp["sub_lord"]

        star_lord_houses = _get_planet_signified_houses(star_lord, house_sigs)
        sub_lord_houses = _get_planet_signified_houses(sub_lord, house_sigs)

        sl_houses_str = ",".join(str(h) for h in sorted(star_lord_houses))
        sub_houses_str = ",".join(str(h) for h in sorted(sub_lord_houses))

        nadi_string = (
            f"{pname.upper()} — "
            f"{star_lord}-{sl_houses_str} — "
            f"{sub_lord}-{sub_houses_str}"
        )

        results.append({
            "planet":           pname,
            "star_lord":        star_lord,
            "star_lord_houses": sl_houses_str,
            "sub_lord":         sub_lord,
            "sub_lord_houses":  sub_houses_str,
            "nadi_string":      nadi_string,
        })

    return results


# ═════════════════════════════════════════════════════════════
# 15. PLANET SIGNIFICATION VIEW V2
# ═════════════════════════════════════════════════════════════

def build_planet_signification_v2(
    planets: List[Dict],
    significator_data: Dict,
    ascendant: Optional[Dict] = None,
) -> List[Dict]:
    """
    Enhanced planet signification view showing occupancy and ownership
    for both the planet and its star lord, with combined signified houses.
    Includes Ascendant when provided.
    """
    planet_houses = significator_data["planet_houses"]
    lord_houses = significator_data["lord_houses"]
    results = []

    all_bodies = list(planets)
    if ascendant:
        all_bodies.append(_make_ascendant_pseudo_planet(ascendant))

    for p in all_bodies:
        pname = p["planet"]
        kp = get_kp_pointer(p["longitude"])
        star_lord = kp["star_lord"]

        occupancy = planet_houses.get(pname, 0)
        ownership = lord_houses.get(pname, [])
        star_lord_occupancy = planet_houses.get(star_lord, 0)
        star_lord_ownership = lord_houses.get(star_lord, [])

        # Combine all signified houses (unique, sorted)
        all_houses = set()
        if occupancy:
            all_houses.add(occupancy)
        all_houses.update(ownership)
        if star_lord_occupancy:
            all_houses.add(star_lord_occupancy)
        all_houses.update(star_lord_ownership)

        results.append({
            "planet":              pname,
            "occupancy":           occupancy,
            "ownership":           sorted(ownership),
            "star_lord":           star_lord,
            "star_lord_occupancy": star_lord_occupancy,
            "star_lord_ownership": sorted(star_lord_ownership),
            "signified_houses":    sorted(all_houses),
        })

    return results


# ═════════════════════════════════════════════════════════════
# 16. HOUSE SIGNIFICATORS VIEW
# ═════════════════════════════════════════════════════════════

def build_house_significators_view(
    significator_data: Dict,
) -> List[Dict]:
    """
    For each house (1-12), list which planets signify it and at which
    step level (1=star of occupant, 2=occupant, 3=star of lord, 4=lord).
    """
    house_sigs = significator_data["houses"]
    results = []

    for h_num in range(1, 13):
        h_data = house_sigs.get(h_num, {})
        significators = []

        for planet in h_data.get("all_significators", []):
            if planet in h_data.get("step1_star_of_occ", []):
                level = 1
            elif planet in h_data.get("step2_occupants", []):
                level = 2
            elif planet in h_data.get("step3_star_of_lord", []):
                level = 3
            else:
                level = 4

            significators.append({
                "planet": planet,
                "level":  level,
            })

        results.append({
            "house":        h_num,
            "significators": significators,
        })

    return results


# ═════════════════════════════════════════════════════════════
# 17. FORTUNA POINT (Part of Fortune)
# ═════════════════════════════════════════════════════════════

def calculate_fortuna_point(
    planets: List[Dict],
    ascendant: Dict,
    houses: List[Dict],
) -> Dict:
    """
    Part of Fortune (Pars Fortunae / Fortuna Point).

    KP Standard Formula: Fortuna = Ascendant + Moon - Sun
    (KP system always uses this single formula, no day/night reversal)

    All longitudes must be sidereal (already the case from calculate_planets).
    The Fortuna point is analyzed like a planet — its star lord
    and sub lord reveal wealth/luck signification.
    """
    asc_long = ascendant["longitude"]
    sun = next((p for p in planets if p["planet"] == "Sun"), None)
    moon = next((p for p in planets if p["planet"] == "Moon"), None)

    if not sun or not moon:
        return {}

    sun_long = sun["longitude"]
    moon_long = moon["longitude"]

    # Day/night determination
    sun_house = _planet_house_placidus(sun_long, houses)
    is_day_chart = sun_house >= 7  # Sun above horizon

    # ── KP Formula: always Asc + Moon - Sun ──
    kp_long = (asc_long + moon_long - sun_long) % 360.0
    kp_kp = get_kp_pointer(kp_long)
    kp_house = _planet_house_placidus(kp_long, houses)

    # ── Western Formula: day = Asc+Moon-Sun, night = Asc+Sun-Moon ──
    if is_day_chart:
        west_long = kp_long  # Same as KP for day charts
    else:
        west_long = (asc_long + sun_long - moon_long) % 360.0
    west_kp = get_kp_pointer(west_long)
    west_house = _planet_house_placidus(west_long, houses)

    def _build_fortuna_entry(flong, fkp, fhouse, formula_label):
        return {
            "longitude":     round(flong, 4),
            "dms":           deg_to_dms(flong % 30),
            "sign":          fkp["sign"],
            "nakshatra":     fkp["nakshatra"],
            "pada":          fkp["pada"],
            "sign_lord":     fkp["sign_lord"],
            "star_lord":     fkp["star_lord"],
            "sub_lord":      fkp["sub_lord"],
            "sub_sub_lord":  fkp["sub_sub_lord"],
            "kp_number":     fkp["kp_number"],
            "house":         fhouse,
            "formula":       formula_label,
        }

    return {
        "is_day_chart":  is_day_chart,
        "kp": _build_fortuna_entry(
            kp_long, kp_kp, kp_house, "Asc + Moon - Sun"
        ),
        "western": _build_fortuna_entry(
            west_long, west_kp, west_house,
            "Asc + Moon - Sun" if is_day_chart else "Asc + Sun - Moon"
        ),
        "same_result": abs(kp_long - west_long) < 0.001,
        "debug": {
            "asc_long": round(asc_long, 4),
            "sun_long": round(sun_long, 4),
            "moon_long": round(moon_long, 4),
        },
    }


# ═════════════════════════════════════════════════════════════
# 18. YOGI POINT & AVAYOGI
# ═════════════════════════════════════════════════════════════

# Yogi nakshatra lord sequence (Sun's nakshatra + 12 nakshatras forward)
YOGI_SEQUENCE = {
    "Sun": "Moon", "Moon": "Mars", "Mars": "Mercury",
    "Mercury": "Jupiter", "Jupiter": "Venus", "Venus": "Saturn",
    "Saturn": "Rahu", "Rahu": "Ketu", "Ketu": "Sun",
}

# Duplicate yogi planet = the planet that owns the yogi point's sign
# Avayogi = 7th planet in dasha sequence from yogi point's nakshatra lord

def calculate_yogi_avayogi(
    planets: List[Dict],
    ascendant: Dict,
    houses: List[Dict],
) -> Dict:
    """
    Yogi Point, Yogi Planet, Duplicate Yogi, and Avayogi.

    Yogi Point = Sun longitude + Moon longitude + 93°20'
    Yogi Planet = Nakshatra lord of the Yogi Point
    Duplicate Yogi = Sign lord of the Yogi Point
    Avayogi = Planet 7 steps ahead in Vimshottari sequence from Yogi Planet

    In KP financial astrology:
    - Yogi planet periods bring gains
    - Avayogi planet periods bring losses
    - Duplicate Yogi supports Yogi
    """
    sun = next((p for p in planets if p["planet"] == "Sun"), None)
    moon = next((p for p in planets if p["planet"] == "Moon"), None)

    if not sun or not moon:
        return {}

    # Yogi Point = Sun + Moon + 93°20' (93.3333°)
    yogi_long = (sun["longitude"] + moon["longitude"] + 93.33333) % 360.0
    yogi_kp = get_kp_pointer(yogi_long)
    yogi_house = _planet_house_placidus(yogi_long, houses)

    yogi_planet = yogi_kp["star_lord"]  # Nakshatra lord of yogi point
    duplicate_yogi = yogi_kp["sign_lord"]  # Sign lord of yogi point

    # Avayogi = 7th in Vimshottari sequence from yogi planet
    avayogi = yogi_planet
    for _ in range(6):
        avayogi = YOGI_SEQUENCE.get(avayogi, "Sun")

    # Avayogi point = Yogi point + 186°40' (opposite + 6°40')
    avayogi_long = (yogi_long + 186.6667) % 360.0
    avayogi_kp = get_kp_pointer(avayogi_long)

    return {
        "yogi_point": {
            "longitude":    round(yogi_long, 4),
            "dms":          deg_to_dms(yogi_long % 30),
            "sign":         yogi_kp["sign"],
            "nakshatra":    yogi_kp["nakshatra"],
            "house":        yogi_house,
            "sign_lord":    yogi_kp["sign_lord"],
            "star_lord":    yogi_kp["star_lord"],
            "sub_lord":     yogi_kp["sub_lord"],
        },
        "yogi_planet":      yogi_planet,
        "duplicate_yogi":   duplicate_yogi,
        "avayogi":          avayogi,
        "avayogi_point": {
            "longitude":    round(avayogi_long, 4),
            "dms":          deg_to_dms(avayogi_long % 30),
            "sign":         avayogi_kp["sign"],
            "nakshatra":    avayogi_kp["nakshatra"],
        },
        "financial_impact": {
            "yogi_periods":      f"{yogi_planet} dasha/bhukti = gains, wealth accumulation",
            "dup_yogi_periods":  f"{duplicate_yogi} supports {yogi_planet} — secondary gains",
            "avayogi_periods":   f"{avayogi} dasha/bhukti = losses, obstacles",
        },
    }


# ═════════════════════════════════════════════════════════════
# 19. PLANET STATUS (Combustion, Speed, Retro, Exaltation)
# ═════════════════════════════════════════════════════════════

# Combustion orbs (degrees from Sun)
COMBUSTION_ORBS = {
    "Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11,
    "Venus": 10, "Saturn": 15,
}

# Exaltation degrees
EXALTATION = {
    "Sun": ("Aries", 10), "Moon": ("Taurus", 3), "Mars": ("Capricorn", 28),
    "Mercury": ("Virgo", 15), "Jupiter": ("Cancer", 5), "Venus": ("Pisces", 27),
    "Saturn": ("Libra", 20), "Rahu": ("Taurus", 20), "Ketu": ("Scorpio", 20),
}
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus",
}
OWN_SIGNS = {
    "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"],
    "Rahu": ["Aquarius"], "Ketu": ["Scorpio"],
}


def calculate_planet_status(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Optional[Dict] = None,
) -> List[Dict]:
    """
    Detailed status for each planet: combustion, retrograde, speed,
    dignity (exalted/debilitated/own sign), and KP-specific details.
    Includes Ascendant when provided.
    """
    sun = next((p for p in planets if p["planet"] == "Sun"), None)
    sun_long = sun["longitude"] if sun else 0

    all_bodies = list(planets)
    if ascendant:
        all_bodies.append(_make_ascendant_pseudo_planet(ascendant))

    results = []
    for p in all_bodies:
        pname = p["planet"]
        plong = p["longitude"]
        speed = p.get("speed", 0)
        sign = p["sign"]
        kp = get_kp_pointer(plong)
        house = _planet_house_placidus(plong, houses)

        # Retrograde
        is_retro = speed < 0

        # Combustion
        is_combust = False
        combust_orb = 0.0
        if pname in COMBUSTION_ORBS and sun:
            diff = abs(plong - sun_long)
            if diff > 180:
                diff = 360 - diff
            combust_orb = round(diff, 2)
            if diff <= COMBUSTION_ORBS[pname]:
                is_combust = True

        # Dignity
        exalt = EXALTATION.get(pname)
        dignity = "Neutral"
        if exalt and sign == exalt[0]:
            dignity = "Exalted"
        elif DEBILITATION.get(pname) == sign:
            dignity = "Debilitated"
        elif sign in OWN_SIGNS.get(pname, []):
            dignity = "Own Sign"

        # Speed category
        if pname == "Ascendant":
            speed_status = "—"
        elif abs(speed) < 0.01:
            speed_status = "Stationary"
        elif is_retro:
            speed_status = "Retrograde"
        elif pname == "Sun":
            speed_status = "Direct"
        elif speed > 0:
            avg_speeds = {"Moon": 13.0, "Mars": 0.52, "Mercury": 1.2,
                          "Jupiter": 0.08, "Venus": 1.0, "Saturn": 0.03,
                          "Rahu": 0.05, "Ketu": 0.05}
            avg = avg_speeds.get(pname, 1.0)
            speed_status = "Fast" if speed > avg * 1.2 else "Direct"
        else:
            speed_status = "Direct"

        results.append({
            "planet":       pname,
            "longitude":    round(plong, 4),
            "dms":          deg_to_dms(plong % 30),
            "full_dms":     deg_to_dms(plong),
            "sign":         sign,
            "house":        house,
            "speed":        round(speed, 6),
            "speed_status": speed_status,
            "is_retro":     is_retro,
            "is_combust":   is_combust,
            "combust_orb":  combust_orb,
            "dignity":      dignity,
            "sign_lord":    kp["sign_lord"],
            "star_lord":    kp["star_lord"],
            "sub_lord":     kp["sub_lord"],
            "sub_sub_lord": kp["sub_sub_lord"],
            "nakshatra":    kp["nakshatra"],
            "pada":         kp["pada"],
            "kp_number":    kp["kp_number"],
        })

    return results


# ═════════════════════════════════════════════════════════════
# 20. CURRENT RULING PLANETS (Real-time)
# ═════════════════════════════════════════════════════════════

def calculate_current_ruling_planets(
    current_planets: List[Dict],
    current_ascendant: Dict,
    current_datetime: datetime,
) -> Dict:
    """
    Current Ruling Planets for the PRESENT moment.
    Used for prashna (horary) and real-time market timing.

    Returns the 7 RP sources matching the reference app:
    1. Ascendant Nakshatra Lord
    2. Ascendant Sign Lord
    3. Moon Nakshatra Lord
    4. Moon Sign Lord
    5. Day Lord
    6. Ascendant Sub Lord
    7. Moon Sub Lord
    """
    weekday = current_datetime.weekday()
    day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    day_lord = day_lords[weekday]

    moon = next((p for p in current_planets if p["planet"] == "Moon"), None)
    moon_kp = get_kp_pointer(moon["longitude"]) if moon else {}
    asc_kp = get_kp_pointer(current_ascendant["longitude"])

    # Build the 7 standard RP rows
    rp_rows = []
    if asc_kp:
        rp_rows.append({"source": "Ascendant Nakshatra Lord", "planet": asc_kp["star_lord"]})
        rp_rows.append({"source": "Ascendant Sign Lord",      "planet": asc_kp["sign_lord"]})
    if moon_kp:
        rp_rows.append({"source": "Moon Nakshatra Lord",      "planet": moon_kp["star_lord"]})
        rp_rows.append({"source": "Moon Sign Lord",           "planet": moon_kp["sign_lord"]})
    rp_rows.append({"source": "Day Lord", "planet": day_lord})
    if asc_kp:
        rp_rows.append({"source": "Ascendant Sub Lord",       "planet": asc_kp["sub_lord"]})
    if moon_kp:
        rp_rows.append({"source": "Moon Sub Lord",            "planet": moon_kp["sub_lord"]})

    # Count and rank
    rp_list = [r["planet"] for r in rp_rows]
    rp_counts = Counter(rp_list)
    sorted_rps = sorted(rp_counts.items(), key=lambda x: -x[1])

    return {
        "datetime":      current_datetime.strftime("%d/%m/%Y %H:%M:%S"),
        "rp_rows":       rp_rows,
        "day_lord":      day_lord,
        "ascendant_kp":  asc_kp,
        "moon_kp":       moon_kp,
        "ranked": [{"planet": rp, "count": c} for rp, c in sorted_rps],
    }


# ═════════════════════════════════════════════════════════════
# 21. DAILY MOON NL / SL / SSL TIMELINE
# ═════════════════════════════════════════════════════════════

def calculate_daily_moon_nl_sl_ssl(
    jd_start: float,
    ayanamsa: str,
    minutes: int = 1440,
) -> List[Dict]:
    """
    Calculate Moon's NL (Nakshatra Lord), SL (Sub Lord), and SSL (Sub-Sub Lord)
    for every minute starting from jd_start for `minutes` minutes (default 1440 = 24h).

    Returns a list of TRANSITION rows — grouped consecutive minutes with the same
    NL+SL+SSL combination, showing start_minute, end_minute, duration, and pointer data.
    Each row also carries DMS position at start and end.
    """
    import swisseph as swe

    ayanamsa_map = {
        "lahiri": swe.SIDM_LAHIRI,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
        "raman": swe.SIDM_RAMAN,
    }
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa.lower(), swe.SIDM_KRISHNAMURTI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    minute_fraction = 1.0 / 1440.0  # 1 minute in Julian days

    transitions = []
    prev_key = None
    block_start_min = 0
    block_start_deg = 0.0
    block_pointer = None

    for m in range(minutes + 1):  # +1 to close last block
        jd = jd_start + m * minute_fraction
        result = swe.calc_ut(jd, swe.MOON, flags)
        moon_lon = result[0][0] % 360.0
        pointer = get_kp_pointer(moon_lon)
        current_key = (pointer["star_lord"], pointer["sub_lord"], pointer["sub_sub_lord"])

        if current_key != prev_key:
            # Close previous block
            if prev_key is not None and block_pointer is not None:
                transitions.append({
                    "start_minute": block_start_min,
                    "end_minute": m - 1,
                    "duration_min": m - block_start_min,
                    "start_deg": round(block_start_deg, 4),
                    "end_deg": round(moon_lon, 4),
                    "start_dms": deg_to_dms(block_start_deg),
                    "end_dms": deg_to_dms(moon_lon),
                    "sign": block_pointer["sign"],
                    "nakshatra": block_pointer["nakshatra"],
                    "pada": block_pointer["pada"],
                    "nl": block_pointer["star_lord"],
                    "sl": block_pointer["sub_lord"],
                    "ssl": block_pointer["sub_sub_lord"],
                    "kp_number": block_pointer["kp_number"],
                    "sign_lord": block_pointer["sign_lord"],
                })
            # Start new block
            prev_key = current_key
            block_start_min = m
            block_start_deg = moon_lon
            block_pointer = pointer

    return transitions


# ═════════════════════════════════════════════════════════════
# 22. MASTER KP ANALYSIS FUNCTION
# ═════════════════════════════════════════════════════════════

def calculate_kp_analysis(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
    transit_planets: Optional[List[Dict]] = None,
    transit_datetime: Optional[datetime] = None,
    dasha_data: Optional[Dict] = None,
    current_dasha: Optional[Dict] = None,
    kp_horary_number: Optional[int] = None,
    transit_ascendant: Optional[Dict] = None,
) -> Dict:
    """
    Complete advanced KP analysis.

    Returns:
    - cuspal_sublords: all 12 cusps with KP pointers
    - significators: 4-step significator for each house
    - planet_table: each planet's complete KP signification
    - promise_denial: per-house and per-group verdicts
    - financial_analysis: wealth house detailed analysis
    - ruling_planets: event timing (if transit data provided)
    - dba_analysis: DBA significator matching
    - kp_sublord_table: full 249-entry reference table
    """
    # 1. Cuspal sub-lords
    cuspal = calculate_cuspal_sublords(houses)

    # 2. 4-step significators
    sig_data = calculate_significators(planets, houses, ascendant)

    # 3. Planet signification table (includes Ascendant)
    planet_table = build_planet_signification_table(planets, sig_data, ascendant)

    # 4. Promise/Denial
    promise = analyze_promise_denial(cuspal, sig_data, planet_table)

    # 5. Financial analysis
    financial = kp_financial_analysis(cuspal, sig_data, promise)

    # 6. Ruling planets (use transit ascendant if available, else birth ascendant)
    ruling_planets = None
    if transit_planets and transit_datetime:
        rp_asc = transit_ascendant if transit_ascendant else ascendant
        ruling_planets = calculate_ruling_planets(
            transit_planets, transit_datetime, rp_asc
        )

    # 7. DBA analysis
    dba = analyze_dba_significators(dasha_data, current_dasha, sig_data)

    # 8. Sensitive points for each planet
    sensitive = {}
    for p in planets:
        sp = get_sensitive_points(p["longitude"])
        if sp:
            sensitive[p["planet"]] = sp

    # 9. KP Horary pointer (if number provided)
    horary = None
    if kp_horary_number and 1 <= kp_horary_number <= 249:
        horary = get_kp_from_number(kp_horary_number)
        horary["input_number"] = kp_horary_number

    # 10. Aspects on cusps
    aspects_on_cusps = calculate_aspects_on_cusps(planets, houses, ascendant)

    # 11. Cuspal sub-sub with signified houses
    cuspal_sub_sub = calculate_cuspal_sub_sub(houses, sig_data)

    # 12. Nakshatra Nadi view (includes Ascendant)
    nakshatra_nadi = build_nakshatra_nadi(planets, sig_data, ascendant)

    # 13. Planet signification v2 (includes Ascendant)
    planet_sig_v2 = build_planet_signification_v2(planets, sig_data, ascendant)

    # 14. House significators view
    house_sig_view = build_house_significators_view(sig_data)

    # 15. Fortuna Point
    fortuna = calculate_fortuna_point(planets, ascendant, houses)

    # 16. Yogi / Avayogi
    yogi = calculate_yogi_avayogi(planets, ascendant, houses)

    # 17. Planet status (combustion, retro, dignity, speed — includes Ascendant)
    planet_status = calculate_planet_status(planets, houses, ascendant)

    # 18. Aspect definitions reference
    aspect_defs = [
        {"abbr": "CN",  "full": "Conjunction",       "degree": 0,   "orb": 15, "weight": 10},
        {"abbr": "OP",  "full": "Opposition",         "degree": 180, "orb": 15, "weight": 10},
        {"abbr": "TR",  "full": "Trine",              "degree": 120, "orb": 6,  "weight": 3},
        {"abbr": "SQ",  "full": "Square",             "degree": 90,  "orb": 6,  "weight": 3},
        {"abbr": "SX",  "full": "Sextile",            "degree": 60,  "orb": 6,  "weight": 3},
        {"abbr": "SS",  "full": "Semisquare",         "degree": 45,  "orb": 1,  "weight": 1},
        {"abbr": "NN",  "full": "Nonile",             "degree": 40,  "orb": 1,  "weight": 1},
        {"abbr": "QI",  "full": "Quintile",           "degree": 72,  "orb": 1,  "weight": 1},
        {"abbr": "SQ2", "full": "Sesquiquadrate",     "degree": 135, "orb": 1,  "weight": 1},
        {"abbr": "QC",  "full": "Quincunx",           "degree": 150, "orb": 1,  "weight": 1},
    ]

    return {
        "type":                   "kp_advanced",
        "cuspal_sublords":        cuspal,
        "significators":          sig_data["houses"],
        "planet_houses":          sig_data["planet_houses"],
        "house_lords":            sig_data["house_lords"],
        "rahu_agents":            sig_data["rahu_agents"],
        "ketu_agents":            sig_data["ketu_agents"],
        "planet_table":           planet_table,
        "promise_denial":         promise,
        "financial_analysis":     financial,
        "ruling_planets":         ruling_planets,
        "dba_analysis":           dba,
        "sensitive_points":       sensitive,
        "horary":                 horary,
        "aspects_on_cusps":       aspects_on_cusps,
        "aspect_definitions":     aspect_defs,
        "cuspal_sub_sub":         cuspal_sub_sub,
        "nakshatra_nadi":         nakshatra_nadi,
        "planet_signification_v2": planet_sig_v2,
        "house_significators_view": house_sig_view,
        "fortuna_point":          fortuna,
        "yogi_avayogi":           yogi,
        "planet_status":          planet_status,
    }


# ═════════════════════════════════════════════════════════════
# 18. EVENT PROMISE CHECKER — Does the chart promise the event?
# ═════════════════════════════════════════════════════════════

def check_event_promise(
    question_type: str,
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
    cuspal_data: List[Dict],
    significator_data: Dict,
) -> Dict:
    """
    KP Event Promise Checker — checks if a natal/prashna chart PROMISES
    that a particular event will happen, using the 3-way sub-lord theory.

    KP Promise Theory:
    ─────────────────
    Step 1: Find the sub-lord of the PRIMARY house cusp for the question.
            e.g. Marriage → 7th cusp sub-lord
    Step 2: Check if the cusp sub-lord SIGNIFIES conductive houses.
            If yes → promise exists at this level.
    Step 3: Check the sub-lord's STAR LORD — which houses does the star lord
            signify? The star lord shows the SOURCE/flow of results.
    Step 4: Check the sub-lord's own SUB-LORD — which houses does it signify?
            The sub-sub level shows the FINAL outcome/delivery.
    Step 5: 3-way verdict:
            - Sub-lord → conductive = promise at surface level
            - Star lord → conductive = source supports the event
            - Sub-lord's sub → conductive = delivery confirmed
            All 3 pointing conductive = STRONG PROMISE
            Sub-lord conductive but star/sub deny = WEAK/CONDITIONAL
            Sub-lord detrimental = NO PROMISE

    Also checks retrograde status (3-tier) for denial/delay.

    This is SEPARATE from DBA timing — this tells you IF the event can
    happen at all. DBA timing tells you WHEN.
    """
    q_config = PRASHNA_QUESTIONS.get(question_type)
    if not q_config:
        return {"error": f"Unknown question type: {question_type}"}

    primary_house = q_config["primary_house"]
    conductive = q_config["conductive"]
    detrimental = q_config["detrimental"]
    label = q_config["label"]

    house_sigs = significator_data.get("houses", {})

    # ── Step 1: Get cusp sub-lord of the primary house ──
    primary_cusp = next((c for c in cuspal_data if c["house"] == primary_house), None)
    if not primary_cusp:
        return {"error": f"No cuspal data for house {primary_house}"}

    cusp_sub_lord = primary_cusp.get("sub_lord", "")
    cusp_star_lord = primary_cusp.get("star_lord", "")
    cusp_sign_lord = primary_cusp.get("sign_lord", "")
    cusp_longitude = primary_cusp.get("longitude", 0)

    # ── Step 2: Sub-lord signification (Level 1 — Promise) ──
    sl_signifies = _get_planet_signified_houses(cusp_sub_lord, house_sigs)
    sl_conductive = [h for h in conductive if h in sl_signifies]
    sl_detrimental = [h for h in detrimental if h in sl_signifies]

    # ── Step 3: Sub-lord's Star Lord signification (Level 2 — Source) ──
    # The star lord of the sub-lord's NATAL position (not the cusp's star lord)
    sl_planet_data = next((p for p in planets if p["planet"] == cusp_sub_lord), None)
    sl_natal_star = ""
    sl_natal_sub = ""
    sl_natal_kp = {}
    if sl_planet_data:
        sl_natal_kp = get_kp_pointer(sl_planet_data["longitude"])
        sl_natal_star = sl_natal_kp.get("star_lord", "")
        sl_natal_sub = sl_natal_kp.get("sub_lord", "")

    star_signifies = _get_planet_signified_houses(sl_natal_star, house_sigs) if sl_natal_star else []
    star_conductive = [h for h in conductive if h in star_signifies]
    star_detrimental = [h for h in detrimental if h in star_signifies]

    # ── Step 4: Sub-lord's Sub-Lord signification (Level 3 — Delivery) ──
    sub_sub_signifies = _get_planet_signified_houses(sl_natal_sub, house_sigs) if sl_natal_sub else []
    sub_sub_conductive = [h for h in conductive if h in sub_sub_signifies]
    sub_sub_detrimental = [h for h in detrimental if h in sub_sub_signifies]

    # ── Step 5: Retrograde check (3-tier) ──
    ALWAYS_R = {"Rahu", "Ketu"}
    NEVER_R = {"Sun", "Moon"}

    is_sl_retro = False
    if sl_planet_data and cusp_sub_lord not in ALWAYS_R and cusp_sub_lord not in NEVER_R:
        is_sl_retro = sl_planet_data.get("speed", 0) < 0

    # Depositor (star lord of sub-lord's natal position) retro check
    is_depositor_retro = False
    if sl_natal_star and sl_natal_star not in ALWAYS_R and sl_natal_star not in NEVER_R:
        dep_data = next((p for p in planets if p["planet"] == sl_natal_star), None)
        if dep_data:
            is_depositor_retro = dep_data.get("speed", 0) < 0

    # 3-tier classification
    retro_tier = 0
    retro_detail = "No retrograde issue"
    if is_sl_retro and not is_depositor_retro:
        retro_tier = 1
        retro_detail = f"{cusp_sub_lord} is retrograde in star of direct {sl_natal_star} — delayed but will materialise"
    elif is_sl_retro and is_depositor_retro:
        retro_tier = 2
        retro_detail = f"{cusp_sub_lord} is retrograde in star of retrograde {sl_natal_star} — promises only failure"
    elif not is_sl_retro and is_depositor_retro:
        retro_tier = 3
        retro_detail = f"{cusp_sub_lord} is direct but in star of retrograde {sl_natal_star} — cannot deliver result in its period"

    # ── Step 6: 3-Way Verdict ──
    reasons = []
    promise_score = 0

    # Level 1: Sub-lord check (most important)
    if sl_conductive:
        promise_score += 40
        reasons.append(f"LEVEL 1 (Sub-lord): {cusp_sub_lord} signifies conductive houses {sl_conductive} — PROMISE exists")
    elif sl_detrimental:
        promise_score -= 40
        reasons.append(f"LEVEL 1 (Sub-lord): {cusp_sub_lord} signifies detrimental houses {sl_detrimental} — DENIAL")
    else:
        reasons.append(f"LEVEL 1 (Sub-lord): {cusp_sub_lord} signifies houses {sl_signifies} — neutral (no conductive or detrimental)")

    if sl_conductive and sl_detrimental:
        promise_score -= 10
        reasons.append(f"  Sub-lord also signifies detrimental {sl_detrimental} — mixed signal, weakens promise")

    # Does sub-lord signify the primary house itself?
    if primary_house in sl_signifies:
        promise_score += 15
        reasons.append(f"  Sub-lord {cusp_sub_lord} directly signifies its own house {primary_house} — self-promising")

    # Level 2: Star lord check (source of results)
    if sl_natal_star:
        if star_conductive:
            promise_score += 25
            reasons.append(f"LEVEL 2 (Star lord): {cusp_sub_lord}'s star lord {sl_natal_star} signifies conductive {star_conductive} — source supports event")
        elif star_detrimental:
            promise_score -= 25
            reasons.append(f"LEVEL 2 (Star lord): {cusp_sub_lord}'s star lord {sl_natal_star} signifies detrimental {star_detrimental} — source opposes event")
        else:
            reasons.append(f"LEVEL 2 (Star lord): {cusp_sub_lord}'s star lord {sl_natal_star} signifies {star_signifies} — neutral source")

        if star_conductive and star_detrimental:
            promise_score -= 5
            reasons.append(f"  Star lord also hits detrimental {star_detrimental} — weakens source")

    # Level 3: Sub-sub lord check (final delivery)
    if sl_natal_sub:
        if sub_sub_conductive:
            promise_score += 20
            reasons.append(f"LEVEL 3 (Sub-sub): {cusp_sub_lord}'s sub-lord {sl_natal_sub} signifies conductive {sub_sub_conductive} — delivery confirmed")
        elif sub_sub_detrimental:
            promise_score -= 20
            reasons.append(f"LEVEL 3 (Sub-sub): {cusp_sub_lord}'s sub-lord {sl_natal_sub} signifies detrimental {sub_sub_detrimental} — delivery blocked")
        else:
            reasons.append(f"LEVEL 3 (Sub-sub): {cusp_sub_lord}'s sub-lord {sl_natal_sub} signifies {sub_sub_signifies} — neutral delivery")

        if sub_sub_conductive and sub_sub_detrimental:
            promise_score -= 5
            reasons.append(f"  Sub-sub also hits detrimental {sub_sub_detrimental}")

    # Retrograde impact
    if retro_tier == 2:
        promise_score -= 40
        reasons.append(f"RETRO DENIAL: {retro_detail}")
    elif retro_tier == 3:
        promise_score -= 30
        reasons.append(f"RETRO BLOCK: {retro_detail}")
    elif retro_tier == 1:
        promise_score -= 10
        reasons.append(f"RETRO DELAY: {retro_detail}")

    # Count how many levels are conductive
    levels_conductive = 0
    if sl_conductive:
        levels_conductive += 1
    if star_conductive:
        levels_conductive += 1
    if sub_sub_conductive:
        levels_conductive += 1

    levels_detrimental = 0
    if sl_detrimental:
        levels_detrimental += 1
    if star_detrimental:
        levels_detrimental += 1
    if sub_sub_detrimental:
        levels_detrimental += 1

    # Final verdict
    if retro_tier >= 2:
        verdict = "NO — RETROGRADE DENIAL"
        verdict_color = "red"
    elif not sl_conductive and sl_detrimental:
        verdict = "NO — Sub-lord denies the event"
        verdict_color = "red"
    elif not sl_conductive and not sl_detrimental:
        verdict = "UNCERTAIN — Sub-lord is neutral"
        verdict_color = "orange"
    elif sl_conductive and levels_conductive == 3 and levels_detrimental == 0:
        verdict = "YES — STRONG PROMISE (all 3 levels conductive)"
        verdict_color = "green"
    elif sl_conductive and levels_conductive >= 2 and retro_tier == 0:
        verdict = "YES — PROMISE EXISTS (2+ levels conductive)"
        verdict_color = "green"
    elif sl_conductive and levels_conductive >= 2 and retro_tier == 1:
        verdict = "YES but DELAYED — Promise with retrograde delay"
        verdict_color = "gold"
    elif sl_conductive and levels_detrimental >= 2:
        verdict = "WEAK — Sub-lord promises but star/sub deny"
        verdict_color = "orange"
    elif sl_conductive:
        verdict = "CONDITIONAL — Sub-lord promises, needs DBA support"
        verdict_color = "gold"
    else:
        verdict = "UNCERTAIN"
        verdict_color = "orange"

    # ── Also check all conductive-house cusps for promise ──
    # Check each conductive house cusp sub-lord to see which support
    all_cusp_analysis = []
    for h_num in conductive:
        cusp = next((c for c in cuspal_data if c["house"] == h_num), None)
        if not cusp:
            continue
        h_sl = cusp.get("sub_lord", "")
        h_sl_houses = _get_planet_signified_houses(h_sl, house_sigs)
        h_cond = [h for h in conductive if h in h_sl_houses]
        h_detr = [h for h in detrimental if h in h_sl_houses]

        # Star lord of this cusp sub-lord's natal position
        h_sl_pd = next((p for p in planets if p["planet"] == h_sl), None)
        h_star = ""
        h_sub = ""
        if h_sl_pd:
            h_kp = get_kp_pointer(h_sl_pd["longitude"])
            h_star = h_kp.get("star_lord", "")
            h_sub = h_kp.get("sub_lord", "")

        h_star_houses = _get_planet_signified_houses(h_star, house_sigs) if h_star else []
        h_star_cond = [h for h in conductive if h in h_star_houses]
        h_star_detr = [h for h in detrimental if h in h_star_houses]

        h_sub_houses = _get_planet_signified_houses(h_sub, house_sigs) if h_sub else []
        h_sub_cond = [h for h in conductive if h in h_sub_houses]
        h_sub_detr = [h for h in detrimental if h in h_sub_houses]

        supports = bool(h_cond and not h_detr)
        denies = bool(h_detr and not h_cond)
        mixed = bool(h_cond and h_detr)

        all_cusp_analysis.append({
            "house":          h_num,
            "cusp_sub_lord":  h_sl,
            "signifies":      sorted(h_sl_houses),
            "conductive_hit": sorted(h_cond),
            "detrimental_hit": sorted(h_detr),
            "star_lord":      h_star,
            "star_signifies": sorted(h_star_houses),
            "star_conductive": sorted(h_star_cond),
            "star_detrimental": sorted(h_star_detr),
            "sub_lord":       h_sub,
            "sub_signifies":  sorted(h_sub_houses),
            "sub_conductive":  sorted(h_sub_cond),
            "sub_detrimental": sorted(h_sub_detr),
            "status":         "SUPPORTS" if supports else "DENIES" if denies else "MIXED" if mixed else "NEUTRAL",
        })

    # Count supporting cusps
    supporting_cusps = sum(1 for c in all_cusp_analysis if c["status"] == "SUPPORTS")
    denying_cusps = sum(1 for c in all_cusp_analysis if c["status"] == "DENIES")

    return {
        "question_type":      question_type,
        "label":              label,
        "primary_house":      primary_house,
        "conductive":         sorted(conductive),
        "detrimental":        sorted(detrimental),
        "cusp_longitude":     round(cusp_longitude, 4),
        "cusp_sign_lord":     cusp_sign_lord,
        "cusp_star_lord":     cusp_star_lord,
        "cusp_sub_lord":      cusp_sub_lord,
        # Level 1: Sub-lord analysis
        "sub_lord_signifies":     sorted(sl_signifies),
        "sub_lord_conductive":    sorted(sl_conductive),
        "sub_lord_detrimental":   sorted(sl_detrimental),
        # Level 2: Star lord of sub-lord's position
        "sl_natal_star_lord":     sl_natal_star,
        "star_lord_signifies":    sorted(star_signifies),
        "star_lord_conductive":   sorted(star_conductive),
        "star_lord_detrimental":  sorted(star_detrimental),
        # Level 3: Sub-lord of sub-lord's position
        "sl_natal_sub_lord":      sl_natal_sub,
        "sub_sub_signifies":      sorted(sub_sub_signifies),
        "sub_sub_conductive":     sorted(sub_sub_conductive),
        "sub_sub_detrimental":    sorted(sub_sub_detrimental),
        # Retrograde
        "is_sl_retro":        is_sl_retro,
        "retro_tier":         retro_tier,
        "retro_detail":       retro_detail,
        # Verdict
        "promise_score":      promise_score,
        "levels_conductive":  levels_conductive,
        "levels_detrimental": levels_detrimental,
        "verdict":            verdict,
        "verdict_color":      verdict_color,
        "reasons":            reasons,
        # All conductive cusp analysis
        "cusp_analysis":      all_cusp_analysis,
        "supporting_cusps":   supporting_cusps,
        "denying_cusps":      denying_cusps,
    }


# ═════════════════════════════════════════════════════════════
# 19. DBA TIMING FINDER — Best future windows for any event
# ═════════════════════════════════════════════════════════════

def find_dba_timing_windows(
    question_type: str,
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
    moon_longitude: float,
    birth_date: datetime,
    search_start: datetime,
    search_end: datetime,
    transit_planets: Optional[List[Dict]] = None,
    transit_datetime: Optional[datetime] = None,
    validate_date: Optional[datetime] = None,
) -> Dict:
    """
    Find the best future DBA (Dasha-Bhukti-Antara) timing windows
    for a given question type using KP significator theory.

    KP Timing Rule:
    - An event fructifies when the Dasha lord, Bhukti lord, AND Antara lord
      are ALL significators of the conductive houses for that event.
    - Best windows = all 3 DBA lords signify conductive houses
    - Good windows  = 2 of 3 DBA lords signify conductive houses
    - Periods where DBA lords signify detrimental houses are penalised

    Args:
        question_type: Key from PRASHNA_QUESTIONS (marriage, vehicle, etc.)
        planets: Natal planet data
        houses: Natal house cusps (Placidus)
        ascendant: Natal ascendant
        moon_longitude: Natal Moon longitude (for Vimshottari calculation)
        birth_date: Date of birth
        search_start: Start of search window
        search_end: End of search window
        transit_planets: Current transit planets (for RP, optional)
        transit_datetime: Current time (for RP, optional)

    Returns:
        Dict with ranked timing windows, each showing DBA lords,
        signified houses, score, and reasoning.
    """
    from app.dasha import calculate_vimshottari_dasha

    q_config = PRASHNA_QUESTIONS.get(question_type)
    if not q_config:
        return {"error": f"Unknown question type: {question_type}"}

    conductive = set(q_config["conductive"])
    detrimental = set(q_config["detrimental"])
    label = q_config["label"]
    primary_house = q_config["primary_house"]

    # ── Step 1: Get KP significators for all 12 houses ──
    sig_data = calculate_significators(planets, houses, ascendant)
    house_sigs = sig_data["houses"]

    # Build planet → signified houses lookup
    planet_houses_map: Dict[str, List[int]] = {}
    for p in planets:
        pname = p["planet"]
        signified = _get_planet_signified_houses(pname, house_sigs)
        planet_houses_map[pname] = signified

    # ── Step 2: Get planet retrograde status ──
    ALWAYS_R = {"Rahu", "Ketu"}
    NEVER_R  = {"Sun", "Moon"}
    planet_retro: Dict[str, bool] = {}
    for p in planets:
        pname = p["planet"]
        if pname in ALWAYS_R or pname in NEVER_R:
            planet_retro[pname] = False
        else:
            planet_retro[pname] = p.get("speed", 0) < 0

    # ── Step 3: Calculate full Vimshottari Dasha tree ──
    years_needed = max(10, int((search_end - birth_date).days / 365.25) + 2)
    dasha_data = calculate_vimshottari_dasha(moon_longitude, birth_date, years_needed)

    # ── Step 4: Scan all Pratyantar periods in the search window ──
    search_start_str = search_start.strftime("%Y-%m-%d")
    search_end_str = search_end.strftime("%Y-%m-%d")

    windows = []

    for maha in dasha_data.get("dashas", []):
        maha_lord = maha["mahadasha_lord"]
        # Quick skip if maha is entirely outside search window
        if maha["end_date"] < search_start_str or maha["start_date"] > search_end_str:
            continue

        maha_houses = set(planet_houses_map.get(maha_lord, []))
        maha_cond = maha_houses & conductive
        maha_detr = maha_houses & detrimental

        for antar in maha.get("antardashas", []):
            antar_lord = antar["antardasha_lord"]
            if antar["end_date"] < search_start_str or antar["start_date"] > search_end_str:
                continue

            antar_houses = set(planet_houses_map.get(antar_lord, []))
            antar_cond = antar_houses & conductive
            antar_detr = antar_houses & detrimental

            for prat in antar.get("pratyantardashas", []):
                prat_lord = prat["pratyantar_lord"]
                prat_start = prat["start_date"]
                prat_end = prat["end_date"]

                # Must overlap with search window
                if prat_end < search_start_str or prat_start > search_end_str:
                    continue

                prat_houses = set(planet_houses_map.get(prat_lord, []))
                prat_cond = prat_houses & conductive
                prat_detr = prat_houses & detrimental

                # ── Score this DBA combination ──
                score = 0
                reasons = []
                lords_with_cond = 0

                # Check each DBA lord for conductive house signification
                for lord_name, lord_cond, lord_detr, lord_role in [
                    (maha_lord, maha_cond, maha_detr, "Dasha"),
                    (antar_lord, antar_cond, antar_detr, "Bhukti"),
                    (prat_lord, prat_cond, prat_detr, "Antara"),
                ]:
                    if lord_cond:
                        lords_with_cond += 1
                        score += 30
                        reasons.append(f"{lord_role} lord {lord_name} signifies conductive houses {sorted(lord_cond)}")
                    if lord_detr:
                        score -= 20
                        reasons.append(f"{lord_role} lord {lord_name} signifies detrimental houses {sorted(lord_detr)}")

                # Bonus: if primary house is signified by any DBA lord
                all_dba_houses = maha_houses | antar_houses | prat_houses
                if primary_house in all_dba_houses:
                    score += 15
                    reasons.append(f"Primary house {primary_house} directly signified")

                # Bonus: all 3 lords signify conductive = strongest window
                if lords_with_cond == 3:
                    score += 25
                    reasons.append("ALL 3 DBA lords signify conductive houses — STRONGEST window")
                elif lords_with_cond == 2:
                    score += 10
                    reasons.append("2 of 3 DBA lords signify conductive houses — good window")

                # Retrograde penalty (inline 3-tier logic)
                for lord_name, lord_role in [
                    (maha_lord, "Dasha"), (antar_lord, "Bhukti"), (prat_lord, "Antara"),
                ]:
                    lord_is_retro = planet_retro.get(lord_name, False)
                    # Find depositor (star lord of this planet)
                    lord_pd = next((p for p in planets if p["planet"] == lord_name), None)
                    depositor = ""
                    dep_is_retro = False
                    if lord_pd:
                        lord_kp = get_kp_pointer(lord_pd["longitude"])
                        depositor = lord_kp.get("star_lord", "")
                        if depositor and depositor not in ALWAYS_R and depositor not in NEVER_R:
                            dep_pd = next((p for p in planets if p["planet"] == depositor), None)
                            if dep_pd:
                                dep_is_retro = dep_pd.get("speed", 0) < 0
                    # 3-tier classification
                    if lord_is_retro and dep_is_retro:
                        score -= 40
                        reasons.append(f"{lord_role} lord {lord_name} retro in star of retro {depositor} — blocks event")
                    elif not lord_is_retro and dep_is_retro:
                        score -= 30
                        reasons.append(f"{lord_role} lord {lord_name} direct but star lord {depositor} retro — weak delivery")
                    elif lord_is_retro and not dep_is_retro:
                        score -= 10
                        reasons.append(f"{lord_role} lord {lord_name} retro in star of direct — delayed but possible")

                # Only include windows with some promise (at least 1 lord in conductive)
                if lords_with_cond >= 1:
                    # Clamp effective start/end to search window
                    eff_start = max(prat_start, search_start_str)
                    eff_end = min(prat_end, search_end_str)

                    # Determine quality tier
                    if lords_with_cond == 3 and score >= 80:
                        quality = "EXCELLENT"
                    elif lords_with_cond == 3:
                        quality = "VERY GOOD"
                    elif lords_with_cond == 2 and score >= 50:
                        quality = "GOOD"
                    elif lords_with_cond == 2:
                        quality = "FAIR"
                    else:
                        quality = "WEAK"

                    windows.append({
                        "start_date":     eff_start,
                        "end_date":       eff_end,
                        "dasha_lord":     maha_lord,
                        "bhukti_lord":    antar_lord,
                        "antara_lord":    prat_lord,
                        "score":          score,
                        "quality":        quality,
                        "lords_conductive": lords_with_cond,
                        "dasha_houses":   sorted(maha_houses),
                        "bhukti_houses":  sorted(antar_houses),
                        "antara_houses":  sorted(prat_houses),
                        "conductive_hit": sorted(all_dba_houses & conductive),
                        "detrimental_hit": sorted(all_dba_houses & detrimental),
                        "reasons":        reasons,
                        "dasha_retro":    planet_retro.get(maha_lord, False),
                        "bhukti_retro":   planet_retro.get(antar_lord, False),
                        "antara_retro":   planet_retro.get(prat_lord, False),
                    })

    # ── Step 5: Sort by score descending, then by start_date ──
    windows.sort(key=lambda w: (-w["score"], w["start_date"]))

    # ── Step 6: Current Ruling Planets (optional cross-check) ──
    ruling_planets = None
    if transit_planets and transit_datetime:
        try:
            ruling_planets = calculate_ruling_planets(
                transit_planets, transit_datetime, ascendant
            )
        except Exception:
            pass  # RP is a bonus, don't fail the whole request

    # ── Step 7: Mark windows that match current RPs ──
    if ruling_planets:
        rp_set = set()
        rp_data = ruling_planets.get("ruling_planets", {})
        rp_all = rp_data.get("all", []) if isinstance(rp_data, dict) else rp_data
        for rp in rp_all:
            if isinstance(rp, dict):
                rp_set.add(rp.get("planet", ""))
            elif isinstance(rp, str):
                rp_set.add(rp)
        for w in windows:
            dba_set = {w["dasha_lord"], w["bhukti_lord"], w["antara_lord"]}
            rp_match = dba_set & rp_set
            w["rp_match"] = sorted(rp_match)
            w["rp_confirmed"] = len(rp_match) >= 2
            if w["rp_confirmed"]:
                w["score"] += 15
                w["reasons"].append(f"Ruling Planets confirm: {sorted(rp_match)}")

    # Re-sort after RP bonus
    windows.sort(key=lambda w: (-w["score"], w["start_date"]))

    # ── Step 8: Current running DBA for reference ──
    current_dba = None
    try:
        from app.dasha import get_current_dasha
        current_dba = get_current_dasha(dasha_data, search_start)
    except Exception:
        pass

    # ── Step 9: Validate a known event date ──
    validation = None
    if validate_date:
        try:
            from app.dasha import get_current_dasha
            vd_str = validate_date.strftime("%Y-%m-%d")
            vd_dba = get_current_dasha(dasha_data, validate_date)

            if vd_dba and not vd_dba.get("error"):
                v_maha = vd_dba.get("mahadasha", "")
                v_antar = vd_dba.get("antardasha", "")
                v_prat = vd_dba.get("pratyantar", "")

                v_maha_houses = set(planet_houses_map.get(v_maha, []))
                v_antar_houses = set(planet_houses_map.get(v_antar, []))
                v_prat_houses = set(planet_houses_map.get(v_prat, []))

                # Score this DBA for the question type
                v_score = 0
                v_reasons = []
                v_lords_cond = 0

                for lname, lhouses, lrole in [
                    (v_maha, v_maha_houses, "Dasha"),
                    (v_antar, v_antar_houses, "Bhukti"),
                    (v_prat, v_prat_houses, "Antara"),
                ]:
                    lcond = lhouses & conductive
                    ldetr = lhouses & detrimental
                    if lcond:
                        v_lords_cond += 1
                        v_score += 30
                        v_reasons.append(f"{lrole} lord {lname} signifies conductive houses {sorted(lcond)}")
                    else:
                        v_reasons.append(f"{lrole} lord {lname} does NOT signify any conductive house")
                    if ldetr:
                        v_score -= 20
                        v_reasons.append(f"  -> Also signifies detrimental houses {sorted(ldetr)}")

                all_vd_houses = v_maha_houses | v_antar_houses | v_prat_houses
                if primary_house in all_vd_houses:
                    v_score += 15
                    v_reasons.append(f"Primary house {primary_house} is signified")

                if v_lords_cond == 3:
                    v_score += 25
                    v_reasons.append("ALL 3 DBA lords signify conductive houses")
                elif v_lords_cond == 2:
                    v_score += 10

                # Retro check
                for lname, lrole in [(v_maha, "Dasha"), (v_antar, "Bhukti"), (v_prat, "Antara")]:
                    lr = planet_retro.get(lname, False)
                    lpd = next((p for p in planets if p["planet"] == lname), None)
                    dep = ""
                    dr = False
                    if lpd:
                        lkp = get_kp_pointer(lpd["longitude"])
                        dep = lkp.get("star_lord", "")
                        if dep and dep not in ALWAYS_R and dep not in NEVER_R:
                            dpd = next((p for p in planets if p["planet"] == dep), None)
                            if dpd:
                                dr = dpd.get("speed", 0) < 0
                    if lr and dr:
                        v_score -= 40
                        v_reasons.append(f"{lrole} lord {lname} retro + star lord {dep} retro — blocks event")
                    elif not lr and dr:
                        v_score -= 30
                        v_reasons.append(f"{lrole} lord {lname} direct but star lord {dep} retro — weak")
                    elif lr and not dr:
                        v_score -= 10
                        v_reasons.append(f"{lrole} lord {lname} retro (delayed but possible)")

                # Quality tier
                if v_lords_cond == 3 and v_score >= 80:
                    v_quality = "EXCELLENT"
                elif v_lords_cond == 3:
                    v_quality = "VERY GOOD"
                elif v_lords_cond == 2 and v_score >= 50:
                    v_quality = "GOOD"
                elif v_lords_cond == 2:
                    v_quality = "FAIR"
                elif v_lords_cond == 1:
                    v_quality = "WEAK"
                else:
                    v_quality = "NO MATCH"

                # Find rank among all windows
                rank = None
                for idx, w in enumerate(windows):
                    if (w["start_date"] <= vd_str <= w["end_date"]
                        and w["dasha_lord"] == v_maha
                        and w["bhukti_lord"] == v_antar
                        and w["antara_lord"] == v_prat):
                        rank = idx + 1
                        break

                validation = {
                    "validate_date":     vd_str,
                    "dasha_lord":        v_maha,
                    "bhukti_lord":       v_antar,
                    "antara_lord":       v_prat,
                    "dasha_period":      f"{vd_dba.get('mahadasha_start','')} to {vd_dba.get('mahadasha_end','')}",
                    "antardasha_period": f"{vd_dba.get('antardasha_start','')} to {vd_dba.get('antardasha_end','')}",
                    "pratyantar_period": f"{vd_dba.get('pratyantar_start','')} to {vd_dba.get('pratyantar_end','')}",
                    "dasha_houses":      sorted(v_maha_houses),
                    "bhukti_houses":     sorted(v_antar_houses),
                    "antara_houses":     sorted(v_prat_houses),
                    "conductive_hit":    sorted(all_vd_houses & conductive),
                    "detrimental_hit":   sorted(all_vd_houses & detrimental),
                    "score":             v_score,
                    "quality":           v_quality,
                    "lords_conductive":  v_lords_cond,
                    "rank_in_search":    rank,
                    "total_windows":     len(windows),
                    "reasons":           v_reasons,
                }
            else:
                validation = {
                    "validate_date": vd_str,
                    "error":         "Date not found in Dasha range",
                }
        except Exception as e:
            validation = {"validate_date": validate_date.strftime("%Y-%m-%d"), "error": str(e)}

    return {
        "question_type":   question_type,
        "label":           label,
        "conductive":      sorted(conductive),
        "detrimental":     sorted(detrimental),
        "primary_house":   primary_house,
        "search_start":    search_start_str,
        "search_end":      search_end_str,
        "total_windows":   len(windows),
        "top_windows":     windows[:20],  # Top 20 best windows
        "current_dba":     current_dba,
        "ruling_planets":  ruling_planets,
        "validation":      validation,
        "planet_significations": {
            pname: sorted(houses_list)
            for pname, houses_list in planet_houses_map.items()
        },
    }
