"""
ashtakavarga.py — Complete Ashtakavarga calculation system.
============================================================
Implements:
  1. Bhinnashtakavarga (BAV) — individual benefic points per planet
  2. Sarvashtakavarga (SAV) — combined points across all planets
  3. Kaksha-based Ashtakavarga — 8 sub-divisions per sign
  4. Pinda Shodhana — Trikona, Ekadhipatya, Graha/Rashi/Yoga Pinda

Classical BPHS benefic point rules for 7 planets + Lagna.
Rahu/Ketu are excluded from Ashtakavarga (traditional system).
"""
from __future__ import annotations

from typing import Dict, List, Any

from core.constants import SIGNS, SIGN_LORDS


# ═══════════════════════════════════════════════════════════════
# BPHS Benefic Point Rules
# ═══════════════════════════════════════════════════════════════
# For each planet, from each contributing body (7 planets + Lagna),
# which houses (counted from the contributor) give a benefic point.
# Key: planet whose BAV we're computing
# Value: dict of contributor → list of benefic houses from contributor

# Houses are 1-indexed (1=same sign, 2=2nd from, etc.)

BAV_RULES = {
    "Sun": {
        "Sun":     [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":    [3, 6, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus":   [6, 7, 12],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":   [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun":     [3, 6, 7, 8, 10, 11],
        "Moon":    [1, 3, 6, 7, 10, 11],
        "Mars":    [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus":   [3, 4, 5, 7, 9, 10, 11],
        "Saturn":  [3, 5, 6, 11],
        "Lagna":   [3, 6, 10, 11],
    },
    "Mars": {
        "Sun":     [3, 5, 6, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus":   [6, 8, 11, 12],
        "Saturn":  [1, 4, 7, 8, 9, 10, 11],
        "Lagna":   [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun":     [5, 6, 9, 11, 12],
        "Moon":    [2, 4, 6, 8, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":   [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun":     [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon":    [2, 5, 7, 9, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus":   [2, 5, 6, 9, 10, 11],
        "Saturn":  [3, 5, 6, 12],
        "Lagna":   [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun":     [8, 11, 12],
        "Moon":    [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars":    [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn":  [3, 4, 5, 8, 9, 10, 11],
        "Lagna":   [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun":     [1, 2, 4, 7, 8, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus":   [6, 11, 12],
        "Saturn":  [3, 5, 6, 11],
        "Lagna":   [1, 3, 4, 6, 10, 11],
    },
    "Lagna": {
        "Sun":     [3, 4, 6, 10, 11, 12],
        "Moon":    [3, 6, 10, 11, 12],
        "Mars":    [1, 3, 6, 10, 11],
        "Mercury": [1, 2, 4, 6, 8, 10, 11],
        "Jupiter": [1, 2, 4, 5, 6, 7, 9, 10, 11],
        "Venus":   [1, 2, 3, 4, 5, 8, 9],
        "Saturn":  [1, 3, 4, 6, 10, 11],
        "Lagna":   [3, 6, 10, 11],
    },
}

# Planets that contribute to Ashtakavarga (7 true planets, no Rahu/Ketu)
ASHTAK_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Kaksha lords in order (8 kakshas per sign, each 3°45')
KAKSHA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]

# Planet multiplication factors for Graha Pinda
GRAHA_PINDA_FACTORS = {
    "Sun": 5, "Moon": 5, "Mars": 8, "Mercury": 5,
    "Jupiter": 10, "Venus": 7, "Saturn": 5,
}

# Rashi multiplication factors for Rashi Pinda
RASHI_PINDA_FACTORS = {
    0: 7, 1: 10, 2: 8, 3: 4, 4: 10, 5: 6,
    6: 7, 7: 8, 8: 9, 9: 5, 10: 11, 11: 12,
}  # Aries=7, Taurus=10, ...


# ═══════════════════════════════════════════════════════════════
# 1. BHINNASHTAKAVARGA (BAV) — Individual planet points
# ═══════════════════════════════════════════════════════════════

def _get_sign_index(lon: float) -> int:
    """Sign index (0-11) from longitude."""
    return int(lon / 30) % 12


def calc_bav(planet: str, planet_signs: Dict[str, int]) -> List[int]:
    """
    Calculate Bhinnashtakavarga for a single planet.

    Parameters:
        planet:       Planet name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)
        planet_signs: Dict mapping planet/Lagna name → sign index (0-11)

    Returns:
        List of 12 integers (0-8), benefic points for each sign (Aries=0 to Pisces=11)
    """
    rules = BAV_RULES.get(planet)
    if not rules:
        return [0] * 12

    points = [0] * 12

    for contributor, benefic_houses in rules.items():
        contrib_sign = planet_signs.get(contributor)
        if contrib_sign is None:
            continue

        for house in benefic_houses:
            target_sign = (contrib_sign + house - 1) % 12
            points[target_sign] += 1

    return points


def calc_all_bav(planet_signs: Dict[str, int]) -> Dict[str, List[int]]:
    """Calculate BAV for all 7 planets."""
    return {p: calc_bav(p, planet_signs) for p in ASHTAK_PLANETS}


# ═══════════════════════════════════════════════════════════════
# 2. SARVASHTAKAVARGA (SAV) — Combined points
# ═══════════════════════════════════════════════════════════════

def calc_sav(all_bav: Dict[str, List[int]]) -> List[int]:
    """
    Calculate Sarvashtakavarga by summing all BAVs.
    Returns list of 12 integers (total points per sign, max 56).
    """
    sav = [0] * 12
    for planet, points in all_bav.items():
        for i in range(12):
            sav[i] += points[i]
    return sav


# ═══════════════════════════════════════════════════════════════
# 3. KAKSHA (8 sub-divisions per sign)
# ═══════════════════════════════════════════════════════════════

def calc_kaksha(lon: float) -> Dict[str, Any]:
    """
    Determine which kaksha (sub-division) a longitude falls in.
    Each sign (30°) has 8 kakshas of 3°45' each.
    Returns kaksha number (1-8) and kaksha lord.
    """
    deg_in_sign = lon % 30
    kaksha_num = int(deg_in_sign / 3.75) + 1
    if kaksha_num > 8:
        kaksha_num = 8
    kaksha_lord = KAKSHA_LORDS[kaksha_num - 1]
    return {
        "kaksha": kaksha_num,
        "kaksha_lord": kaksha_lord,
        "degree_in_kaksha": round(deg_in_sign - (kaksha_num - 1) * 3.75, 4),
    }


def calc_kaksha_table(planet_signs: Dict[str, int], all_bav: Dict[str, List[int]]) -> Dict[str, Any]:
    """
    Build full Kaksha-based Ashtakavarga table.
    For each planet in each sign, shows which kaksha lords contribute
    benefic points and which don't.
    """
    result = {}
    for planet in ASHTAK_PLANETS:
        rules = BAV_RULES[planet]
        planet_kaksha = {}

        for sign_idx in range(12):
            kaksha_details = []
            for k_idx, k_lord in enumerate(KAKSHA_LORDS):
                # Check if this kaksha lord contributes a benefic point
                # The kaksha lord's position determines if it gives a point
                contrib_sign = planet_signs.get(k_lord)
                if contrib_sign is None:
                    has_point = False
                else:
                    benefic_houses = rules.get(k_lord, [])
                    house_from_contrib = ((sign_idx - contrib_sign) % 12) + 1
                    has_point = house_from_contrib in benefic_houses

                kaksha_details.append({
                    "kaksha": k_idx + 1,
                    "lord": k_lord,
                    "benefic": has_point,
                })

            planet_kaksha[SIGNS[sign_idx]] = {
                "kakshas": kaksha_details,
                "total_points": all_bav[planet][sign_idx],
            }

        result[planet] = planet_kaksha

    return result


# ═══════════════════════════════════════════════════════════════
# 4. PINDA SHODHANA (Reduction/Purification)
# ═══════════════════════════════════════════════════════════════

def trikona_shodhana(bav: List[int]) -> List[int]:
    """
    Trikona Shodhana: Subtract the minimum value among
    trikona signs (1-5-9, 2-6-10, 3-7-11, 4-8-12).
    """
    result = list(bav)
    trikona_groups = [
        [0, 4, 8],   # Aries, Leo, Sagittarius
        [1, 5, 9],   # Taurus, Virgo, Capricorn
        [2, 6, 10],  # Gemini, Libra, Aquarius
        [3, 7, 11],  # Cancer, Scorpio, Pisces
    ]

    for group in trikona_groups:
        min_val = min(result[i] for i in group)
        for i in group:
            result[i] -= min_val

    return result


def ekadhipatya_shodhana(
    bav: List[int], occupied_signs: set = None,
) -> List[int]:
    """
    Ekadhipatya Shodhana per BPHS Chapter 70.

    Rules (applied only when BOTH signs of a pair have >0):
      - Both signs occupied by planets → no change
      - Both unoccupied, same value   → both = 0
      - Both unoccupied, diff values  → both = smaller value
      - One occupied, one not:
          occupied bigger  → unoccupied = 0, occupied unchanged
          occupied smaller → unoccupied = big − small, occupied unchanged
      - Sun (Leo) / Moon (Cancer) own one sign only → not in pairs

    Parameters:
        bav:            12-element list (after Trikona Shodhana)
        occupied_signs: set of sign indices (0-11) occupied by any planet
    """
    result = list(bav)
    if occupied_signs is None:
        occupied_signs = set()

    dual_lords = [
        (0, 7),   # Aries-Scorpio (Mars)
        (1, 6),   # Taurus-Libra (Venus)
        (2, 5),   # Gemini-Virgo (Mercury)
        (8, 11),  # Sagittarius-Pisces (Jupiter)
        (9, 10),  # Capricorn-Aquarius (Saturn)
    ]

    for s1, s2 in dual_lords:
        v1, v2 = result[s1], result[s2]

        # Prerequisite: both must have > 0 after Trikona
        if v1 == 0 or v2 == 0:
            continue

        s1_occ = s1 in occupied_signs
        s2_occ = s2 in occupied_signs

        if s1_occ and s2_occ:
            # Both occupied: no reduction
            pass
        elif not s1_occ and not s2_occ:
            # Both unoccupied
            if v1 == v2:
                result[s1] = 0
                result[s2] = 0
            else:
                min_val = min(v1, v2)
                result[s1] = min_val
                result[s2] = min_val
        else:
            # One occupied, one not
            if s1_occ:
                # s1 occupied
                if v1 >= v2:
                    result[s2] = 0          # unoccupied → 0
                else:
                    result[s2] = v2 - v1    # unoccupied → diff
                # s1 (occupied) stays unchanged
            else:
                # s2 occupied
                if v2 >= v1:
                    result[s1] = 0          # unoccupied → 0
                else:
                    result[s1] = v1 - v2    # unoccupied → diff
                # s2 (occupied) stays unchanged

    return result


def calc_pinda_shodhana(
    all_bav: Dict[str, List[int]],
    planet_signs: Dict[str, int] = None,
    occupied_signs: set = None,
) -> Dict[str, Any]:
    """
    Perform full Pinda Shodhana on all BAVs (7 planets + Lagna).

    For each planet/Lagna:
      1. Trikona Shodhana  (subtract min of trikona group)
      2. Ekadhipatya Shodhana  (occupancy-aware per BPHS Ch. 70)
      3. Rashi Pinda  = Σ(shodhit[sign] × rashi_factor[sign])
      4. Graha Pinda  = Σ(shodhit[sign_of_planet_q] × graha_factor[q])
      5. Sodhya Pinda = Rashi Pinda + Graha Pinda

    Parameters:
        all_bav:        BAV dict — must include "Lagna" key for full results
        planet_signs:   sign index (0-11) for each planet + Lagna
        occupied_signs: set of sign indices occupied by any planet (for Ekadhipatya)
    """
    # Planets to process: 7 planets + Lagna (if present in all_bav)
    pinda_planets = list(ASHTAK_PLANETS)
    if "Lagna" in all_bav:
        pinda_planets.append("Lagna")

    shodhana = {}

    for planet in pinda_planets:
        original = all_bav[planet]

        # Step 1: Trikona Shodhana
        after_trikona = trikona_shodhana(original)

        # Step 2: Ekadhipatya Shodhana (occupancy-aware)
        after_ekadhi = ekadhipatya_shodhana(after_trikona, occupied_signs)

        # Step 3: Rashi Pinda — sum of (shodhit × rashi factor) for all 12 signs
        rashi_pinda = sum(
            after_ekadhi[i] * RASHI_PINDA_FACTORS[i] for i in range(12)
        )

        # Step 4: Graha Pinda — sum of (shodhit at planet q's sign × graha factor of q)
        graha_pinda = 0
        if planet_signs:
            for q in ASHTAK_PLANETS:          # only 7 true planets
                q_sign = planet_signs.get(q)
                if q_sign is not None:
                    graha_pinda += after_ekadhi[q_sign] * GRAHA_PINDA_FACTORS[q]

        # Step 5: Sodhya Pinda
        sodhya_pinda = rashi_pinda + graha_pinda

        shodhana[planet] = {
            "original": original,
            "after_trikona": after_trikona,
            "after_ekadhipatya": after_ekadhi,
            "rashi_pinda": rashi_pinda,
            "graha_pinda": graha_pinda,
            "sodhya_pinda": sodhya_pinda,
        }

    return {
        "planets": shodhana,
    }


# ═══════════════════════════════════════════════════════════════
# 5. TRANSIT SCORING (using Ashtakavarga)
# ═══════════════════════════════════════════════════════════════

def score_transit(
    transit_planet: str,
    transit_lon: float,
    all_bav: Dict[str, List[int]],
    sav: List[int],
) -> Dict[str, Any]:
    """
    Score a planet's transit position using Ashtakavarga.

    Returns:
        BAV score (planet's own points in transit sign)
        SAV score (total points in transit sign)
        Kaksha info (which kaksha lord the planet is transiting)
        Rating: good/neutral/bad
    """
    sign_idx = _get_sign_index(transit_lon)
    kaksha_info = calc_kaksha(transit_lon)

    bav_score = all_bav.get(transit_planet, [0]*12)[sign_idx] if transit_planet in all_bav else 0
    sav_score = sav[sign_idx]

    # BAV rating: >=4 good, 3-4 neutral, <3 bad (out of 8 max)
    # SAV rating: >=28 good, 25-28 neutral, <25 bad (out of 56 max, avg ~28)
    if bav_score >= 5 and sav_score >= 28:
        rating = "excellent"
    elif bav_score >= 4 or sav_score >= 28:
        rating = "good"
    elif bav_score >= 3 and sav_score >= 25:
        rating = "neutral"
    else:
        rating = "bad"

    return {
        "planet": transit_planet,
        "sign": SIGNS[sign_idx],
        "sign_index": sign_idx,
        "bav_score": bav_score,
        "sav_score": sav_score,
        "kaksha": kaksha_info,
        "rating": rating,
    }


# ═══════════════════════════════════════════════════════════════
# Master calculation
# ═══════════════════════════════════════════════════════════════

def calc_full_ashtakavarga(planet_lons: Dict[str, float], asc_lon: float) -> Dict[str, Any]:
    """
    Calculate complete Ashtakavarga system.

    Parameters:
        planet_lons: Dict of planet_name → sidereal longitude (7 planets)
        asc_lon:     Ascendant sidereal longitude

    Returns:
        Complete Ashtakavarga with BAV, SAV, Kaksha, and Pinda Shodhana.
    """
    # Build sign index map
    planet_signs = {}
    for planet in ASHTAK_PLANETS:
        if planet in planet_lons:
            planet_signs[planet] = _get_sign_index(planet_lons[planet])
    planet_signs["Lagna"] = _get_sign_index(asc_lon)

    # Compute which signs are occupied by any planet (for Ekadhipatya)
    # Only 7 Ashtakavarga planets (no Rahu/Ketu) — per BPHS tradition
    occupied_signs = set()
    for p_name in ASHTAK_PLANETS:
        if p_name in planet_lons:
            occupied_signs.add(_get_sign_index(planet_lons[p_name]))

    # BAV for all 7 planets
    all_bav = calc_all_bav(planet_signs)

    # Lagna BAV (Ascendant's own Bhinnashtakavarga)
    lagna_bav = calc_bav("Lagna", planet_signs)

    # SAV (sum of 7 planet BAVs — traditional)
    sav = calc_sav(all_bav)

    # Pinda Shodhana (7 planets + Lagna, with occupancy-aware Ekadhipatya)
    all_bav_with_lagna = {**all_bav, "Lagna": lagna_bav}
    pinda = calc_pinda_shodhana(all_bav_with_lagna, planet_signs, occupied_signs)

    # Kaksha details
    kaksha_table = calc_kaksha_table(planet_signs, all_bav)

    # Planet positions with kaksha info
    planet_kakshas = {}
    for planet in ASHTAK_PLANETS:
        if planet in planet_lons:
            planet_kakshas[planet] = calc_kaksha(planet_lons[planet])

    return {
        "bav": {p: pts for p, pts in all_bav.items()},
        "lagna_bav": lagna_bav,
        "sav": sav,
        "sav_total": sum(sav),
        "pinda_shodhana": pinda,
        "kaksha_table": kaksha_table,
        "planet_kakshas": planet_kakshas,
        "planet_signs": {p: SIGNS[idx] for p, idx in planet_signs.items()},
        "sign_names": SIGNS,
    }
