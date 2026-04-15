"""
divisional.py — Divisional Charts (Varga Charts) for Financial Astrology
Implements D1 (Rasi), D2 (Hora/Wealth), D9 (Navamsha), D10 (Dashamsha),
D3 (Drekkana), D12 (Dwadashamsha) with financial interpretations.
"""
from __future__ import annotations
from typing import Dict, List, Tuple

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_NUM = {s: i for i, s in enumerate(SIGNS)}

# Sign lordships
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Exaltation signs
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Gemini", "Ketu": "Sagittarius",
}

# Debilitation signs
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Sagittarius", "Ketu": "Gemini",
}

# Own signs
OWN_SIGNS = {
    "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"],
    "Rahu": [], "Ketu": [],
}

# ─────────────────────────────────────────────────────────────
# Financial house significance (for all charts)
# ─────────────────────────────────────────────────────────────
FINANCIAL_HOUSES = {
    1:  "Self / Overall strength of chart",
    2:  "Accumulated wealth, savings, family money (Dhana)",
    3:  "Efforts, short-term gains, courage",
    4:  "Fixed assets, property, vehicles, mother",
    5:  "Speculation, stock market, children, intelligence",
    6:  "Enemies, debt, competition, loans",
    7:  "Business partners, foreign trade",
    8:  "Sudden gains/losses, inheritance, insurance",
    9:  "Fortune, higher learning, long-distance trade",
    10: "Career, profession, status, government",
    11: "Income, gains, fulfillment of desires (Labha)",
    12: "Expenses, losses, foreign settlement, imports",
}


def _sign_from_degree(longitude: float) -> Tuple[str, float]:
    """Return (sign_name, degree_in_sign) from absolute longitude."""
    longitude = longitude % 360.0
    idx = int(longitude / 30)
    return SIGNS[idx], longitude % 30


def _get_strength(planet: str, sign: str) -> str:
    """Determine planet's strength in a sign."""
    if sign in OWN_SIGNS.get(planet, []):
        return "Own Sign (Swakshetra)"
    if EXALTATION.get(planet) == sign:
        return "Exalted (Uchcha)"
    if DEBILITATION.get(planet) == sign:
        return "Debilitated (Neecha)"
    return "Normal"


def _planet_entry(planet_name: str, longitude: float, speed: float = 0.0) -> Dict:
    sign, deg = _sign_from_degree(longitude)
    return {
        "planet":       planet_name,
        "longitude":    round(longitude % 360, 4),
        "sign":         sign,
        "sign_lord":    SIGN_LORDS.get(sign, ""),
        "degree":       round(deg, 4),
        "retrograde":   speed < 0,
        "strength":     _get_strength(planet_name, sign),
    }


# ──────────────────────────────────────────────────────────────
# D2 — Hora Chart (Wealth / Money)
# Odd signs (Aries, Gemini, ...): even degrees → Leo (Sun/Male)
#                                  odd degrees  → Cancer (Moon/Female)
# Even signs: even degrees → Cancer, odd → Leo
# Financial: Leo hora = Sun wealth; Cancer hora = Moon wealth
# ──────────────────────────────────────────────────────────────
def calc_d2_hora(planets: List[Dict]) -> Dict:
    """
    D2 Hora Chart — indicates wealth, liquid assets, earning capacity.
    Sun hora (Leo) = active/earned income; Moon hora (Cancer) = passive/savings.
    """
    hora_planets = []
    sun_hora_planets: List[str] = []
    moon_hora_planets: List[str] = []

    for p in planets:
        long = p["longitude"] % 360.0
        sign_idx = int(long / 30)
        deg_in_sign = long % 30

        # Odd signs (0,2,4,...): first 15° → Leo, second 15° → Cancer
        # Even signs (1,3,5,...): first 15° → Cancer, second 15° → Leo
        is_odd_sign = sign_idx % 2 == 0  # Aries=0 (odd), Taurus=1 (even)...
        in_first_half = deg_in_sign < 15.0

        if is_odd_sign:
            hora_sign = "Leo" if in_first_half else "Cancer"
        else:
            hora_sign = "Cancer" if in_first_half else "Leo"

        entry = {
            "planet":      p["planet"],
            "d1_sign":     p["sign"],
            "hora_sign":   hora_sign,
            "hora_lord":   "Sun" if hora_sign == "Leo" else "Moon",
            "hora_type":   "Sun Hora (Active/Earned)" if hora_sign == "Leo" else "Moon Hora (Passive/Saved)",
            "strength":    _get_strength(p["planet"], hora_sign),
        }
        hora_planets.append(entry)
        if hora_sign == "Leo":
            sun_hora_planets.append(p["planet"])
        else:
            moon_hora_planets.append(p["planet"])

    # Financial interpretation
    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
    sun_hora_benefics = [p for p in sun_hora_planets if p in benefics]
    moon_hora_benefics = [p for p in moon_hora_planets if p in benefics]

    return {
        "chart": "D2 - Hora (Wealth)",
        "description": "Wealth, liquid assets, and earning capacity",
        "planets": hora_planets,
        "sun_hora_planets": sun_hora_planets,
        "moon_hora_planets": moon_hora_planets,
        "financial_analysis": {
            "active_income_strength": f"{len(sun_hora_benefics)}/4 benefics in Sun Hora",
            "passive_income_strength": f"{len(moon_hora_benefics)}/4 benefics in Moon Hora",
            "wealth_indication": (
                "Strong wealth" if (len(sun_hora_benefics) + len(moon_hora_benefics)) >= 3
                else "Moderate wealth" if (len(sun_hora_benefics) + len(moon_hora_benefics)) >= 2
                else "Wealth requires effort"
            ),
            "jupiter_hora": next((p["hora_type"] for p in hora_planets if p["planet"] == "Jupiter"), "Not calculated"),
            "venus_hora":   next((p["hora_type"] for p in hora_planets if p["planet"] == "Venus"),   "Not calculated"),
        },
    }


# ──────────────────────────────────────────────────────────────
# D9 — Navamsha Chart (Strength of Planets, Marriage, Fortune)
# Each sign divided into 9 parts of 3°20' each
# Aries cycle starts at Aries; Cancer cycle starts at Cancer;
# Libra cycle starts at Libra; Capricorn cycle starts at Capricorn
# ──────────────────────────────────────────────────────────────
_NAVAMSHA_START = {0: 0, 1: 9, 2: 6, 3: 3, 4: 0, 5: 9, 6: 6, 7: 3, 8: 0, 9: 9, 10: 6, 11: 3}


def calc_d9_navamsha(planets: List[Dict], ascendant: Dict) -> Dict:
    """
    D9 Navamsha Chart.
    Critical for: strength of natal planets, fortune, divisional sign placement.
    A planet in the same sign in D1 and D9 = Vargottama (extremely strong).
    """
    nav_planets = []
    vargottama: List[str] = []

    for p in planets:
        long = p["longitude"] % 360.0
        sign_idx = int(long / 30)
        deg_in_sign = long % 30
        pada = int(deg_in_sign / (10.0 / 3.0))  # 0-8
        nav_sign_idx = (_NAVAMSHA_START[sign_idx] + pada) % 12
        nav_sign = SIGNS[nav_sign_idx]
        is_vargottama = nav_sign == p["sign"]
        if is_vargottama:
            vargottama.append(p["planet"])

        nav_planets.append({
            "planet":       p["planet"],
            "d1_sign":      p["sign"],
            "d9_sign":      nav_sign,
            "d9_lord":      SIGN_LORDS.get(nav_sign, ""),
            "vargottama":   is_vargottama,
            "d9_strength":  _get_strength(p["planet"], nav_sign),
            "financial_note": _d9_financial_note(p["planet"], nav_sign),
        })

    # Navamsha Ascendant
    asc_long = ascendant["longitude"]
    asc_sign_idx = int(asc_long / 30)
    asc_deg = asc_long % 30
    asc_pada = int(asc_deg / (10.0 / 3.0))
    nav_asc_idx = (_NAVAMSHA_START[asc_sign_idx] + asc_pada) % 12

    return {
        "chart": "D9 - Navamsha (Fortune & Strength)",
        "description": "Planetary strength, fortune, and long-term potential",
        "navamsha_ascendant": SIGNS[nav_asc_idx],
        "planets": nav_planets,
        "vargottama_planets": vargottama,
        "financial_analysis": {
            "vargottama_count": len(vargottama),
            "vargottama_note": (
                f"{', '.join(vargottama)} are Vargottama — exceptionally strong in D9. "
                "These planets deliver their promises in full." if vargottama
                else "No Vargottama planets — check D1 strength carefully."
            ),
            "jupiter_d9": next((p["d9_sign"] for p in nav_planets if p["planet"] == "Jupiter"), ""),
            "venus_d9":   next((p["d9_sign"] for p in nav_planets if p["planet"] == "Venus"),   ""),
        },
    }


def _d9_financial_note(planet: str, sign: str) -> str:
    strength = _get_strength(planet, sign)
    if strength == "Exalted (Uchcha)":
        return f"{planet} exalted in D9 — exceptional financial results promised."
    if strength == "Own Sign (Swakshetra)":
        return f"{planet} in own sign in D9 — reliable and consistent financial delivery."
    if strength == "Debilitated (Neecha)":
        return f"{planet} debilitated in D9 — may not deliver full financial promise."
    return ""


# ──────────────────────────────────────────────────────────────
# D10 — Dashamsha Chart (Career & Profession)
# Odd signs: start from the same sign and move forward by degree/3 parts.
# Even signs: start from the 9th sign from the natal sign, then move forward.
# Each sign is divided into 10 parts of 3° each.
# ──────────────────────────────────────────────────────────────
def calc_d10_dashamsha(planets: List[Dict], ascendant: Dict) -> Dict:
    """
    D10 Dashamsha Chart.
    Indicates career, professional success, public standing, and business success.
    Strong 10th lord and Sun in D10 = powerful career.
    """
    dash_planets = []

    for p in planets:
        long = p["longitude"] % 360.0
        sign_idx = int(long / 30)
        deg_in_sign = long % 30
        division = int(deg_in_sign / 3.0)  # 0-9
        if sign_idx % 2 == 0:  # odd sign in traditional astrology (Aries=0, Gemini=2, ...)
            d10_sign_idx = (sign_idx + division) % 12
        else:
            d10_sign_idx = (sign_idx + 8 + division) % 12
        d10_sign = SIGNS[d10_sign_idx]
        dash_planets.append({
            "planet":        p["planet"],
            "d1_sign":       p["sign"],
            "d10_sign":      d10_sign,
            "d10_lord":      SIGN_LORDS.get(d10_sign, ""),
            "d10_strength":  _get_strength(p["planet"], d10_sign),
            "career_note":   _d10_career_note(p["planet"], d10_sign),
        })

    # D10 Ascendant
    asc_sign_idx = int(ascendant["longitude"] / 30)
    asc_deg = ascendant["longitude"] % 30
    asc_part = int(asc_deg / 3.0)
    if asc_sign_idx % 2 == 0:
        d10_asc_idx = (asc_sign_idx + asc_part) % 12
    else:
        d10_asc_idx = (asc_sign_idx + 8 + asc_part) % 12

    sun_d10    = next((p for p in dash_planets if p["planet"] == "Sun"),     None)
    saturn_d10 = next((p for p in dash_planets if p["planet"] == "Saturn"),  None)
    jupiter_d10= next((p for p in dash_planets if p["planet"] == "Jupiter"), None)

    return {
        "chart": "D10 - Dashamsha (Career & Profession)",
        "description": "Professional success, career trajectory, public standing",
        "d10_ascendant": SIGNS[d10_asc_idx],
        "d10_asc_lord":  SIGN_LORDS.get(SIGNS[d10_asc_idx], ""),
        "planets": dash_planets,
        "financial_analysis": {
            "sun_d10_sign":      sun_d10["d10_sign"] if sun_d10 else "",
            "sun_d10_strength":  sun_d10["d10_strength"] if sun_d10 else "",
            "saturn_d10_sign":   saturn_d10["d10_sign"] if saturn_d10 else "",
            "jupiter_d10_sign":  jupiter_d10["d10_sign"] if jupiter_d10 else "",
            "career_strength": _overall_d10_strength(dash_planets),
        },
    }


def _d10_career_note(planet: str, sign: str) -> str:
    strength = _get_strength(planet, sign)
    career_planets = {"Sun": "authority/govt", "Saturn": "discipline/service",
                      "Jupiter": "finance/teaching", "Mars": "defense/real estate",
                      "Mercury": "IT/commerce", "Venus": "arts/luxury", "Moon": "public/FMCG"}
    note = career_planets.get(planet, "")
    if strength == "Exalted (Uchcha)":
        return f"Excellent {note} career potential."
    if strength == "Debilitated (Neecha)":
        return f"Challenges in {note} career — needs remedies."
    return note


def _overall_d10_strength(planets: List[Dict]) -> str:
    strong = sum(1 for p in planets
                 if "Exalted" in p["d10_strength"] or "Own" in p["d10_strength"])
    if strong >= 4:
        return "Very Strong career/business potential"
    if strong >= 2:
        return "Good career/business potential"
    return "Moderate career/business potential"


# ──────────────────────────────────────────────────────────────
# D3 — Drekkana (Siblings, Efforts, Business Partners)
# ──────────────────────────────────────────────────────────────
def calc_d3_drekkana(planets: List[Dict]) -> Dict:
    """D3 Drekkana — business partners, co-investors, efforts."""
    drek_planets = []
    for p in planets:
        long = p["longitude"] % 360.0
        sign_idx = int(long / 30)
        deg = long % 30
        part = int(deg / 10.0)  # 0, 1, or 2
        d3_sign_idx = (sign_idx + part * 4) % 12
        d3_sign = SIGNS[d3_sign_idx]
        drek_planets.append({
            "planet":    p["planet"],
            "d1_sign":   p["sign"],
            "d3_sign":   d3_sign,
            "strength":  _get_strength(p["planet"], d3_sign),
        })
    return {
        "chart": "D3 - Drekkana (Business Partners & Efforts)",
        "description": "Co-investors, business partners, short-term efforts",
        "planets": drek_planets,
    }


# ──────────────────────────────────────────────────────────────
# Master function: calculate all divisional charts
# ──────────────────────────────────────────────────────────────
def calculate_all_divisional(
    planets: List[Dict],
    ascendant: Dict,
    charts: List[str] = None,
) -> Dict:
    """
    Calculate all requested divisional charts.
    charts: list of ["D2", "D3", "D9", "D10"] — default all.
    """
    if charts is None:
        charts = ["D2", "D3", "D9", "D10"]
    charts = [c.upper() for c in charts]

    result: Dict = {}
    if "D2" in charts:
        result["d2_hora"]     = calc_d2_hora(planets)
    if "D3" in charts:
        result["d3_drekkana"] = calc_d3_drekkana(planets)
    if "D9" in charts:
        result["d9_navamsha"] = calc_d9_navamsha(planets, ascendant)
    if "D10" in charts:
        result["d10_dashamsha"] = calc_d10_dashamsha(planets, ascendant)

    return result
