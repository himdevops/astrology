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

def build_planet_signification_table(
    planets: List[Dict],
    significator_data: Dict,
) -> List[Dict]:
    """
    Build a table showing each planet's complete house significations.
    For each planet: which houses it signifies and through what connection.
    """
    planet_houses = significator_data["planet_houses"]
    lord_houses = significator_data["lord_houses"]
    house_sigs = significator_data["houses"]

    table = []
    for p in planets:
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
            "house_occupied":      planet_houses.get(pname, 0),
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
        if planet in h_data.get("all_significators", []):
            houses.append(h_num)
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
) -> List[Dict]:
    """
    Nakshatra Nadi view: for each planet, show the star lord and sub lord
    with their signified house numbers in a compact nadi string.
    """
    house_sigs = significator_data["houses"]
    results = []

    for p in planets:
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
) -> List[Dict]:
    """
    Enhanced planet signification view showing occupancy and ownership
    for both the planet and its star lord, with combined signified houses.
    """
    planet_houses = significator_data["planet_houses"]
    lord_houses = significator_data["lord_houses"]
    results = []

    for p in planets:
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
) -> List[Dict]:
    """
    Detailed status for each planet: combustion, retrograde, speed,
    dignity (exalted/debilitated/own sign), and KP-specific details.
    """
    sun = next((p for p in planets if p["planet"] == "Sun"), None)
    sun_long = sun["longitude"] if sun else 0

    results = []
    for p in planets:
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
        if abs(speed) < 0.01:
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

    # 3. Planet signification table
    planet_table = build_planet_signification_table(planets, sig_data)

    # 4. Promise/Denial
    promise = analyze_promise_denial(cuspal, sig_data, planet_table)

    # 5. Financial analysis
    financial = kp_financial_analysis(cuspal, sig_data, promise)

    # 6. Ruling planets
    ruling_planets = None
    if transit_planets and transit_datetime:
        ruling_planets = calculate_ruling_planets(
            transit_planets, transit_datetime, ascendant
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

    # 12. Nakshatra Nadi view
    nakshatra_nadi = build_nakshatra_nadi(planets, sig_data)

    # 13. Planet signification v2
    planet_sig_v2 = build_planet_signification_v2(planets, sig_data)

    # 14. House significators view
    house_sig_view = build_house_significators_view(sig_data)

    # 15. Fortuna Point
    fortuna = calculate_fortuna_point(planets, ascendant, houses)

    # 16. Yogi / Avayogi
    yogi = calculate_yogi_avayogi(planets, ascendant, houses)

    # 17. Planet status (combustion, retro, dignity, speed)
    planet_status = calculate_planet_status(planets, houses)

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
