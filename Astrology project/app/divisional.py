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
# D1 — Rasi Chart (basic natal — planets already in rasi signs)
# ──────────────────────────────────────────────────────────────
def calc_d1_rasi(planets: List[Dict], ascendant: Dict) -> Dict:
    """D1 Rasi — the natal chart itself."""
    d1_planets = []
    for p in planets:
        sign, deg = _sign_from_degree(p["longitude"])
        d1_planets.append({
            "planet":   p["planet"],
            "sign":     sign,
            "degree":   round(deg, 4),
            "retro":    p.get("speed", 0) < 0,
            "strength": _get_strength(p["planet"], sign),
        })
    asc_sign, asc_deg = _sign_from_degree(ascendant["longitude"])
    return {
        "chart":       "D1 - Rasi (Natal)",
        "division":    1,
        "description": "Birth chart — the foundation of all analysis",
        "ascendant":   asc_sign,
        "asc_degree":  round(asc_deg, 4),
        "planets":     d1_planets,
    }


# ──────────────────────────────────────────────────────────────
# D4 — Chaturthamsha (Property, Fixed Assets, Vehicles)
# Each sign divided into 4 parts of 7°30' each
# Odd signs: start from same sign; Even signs: start from sign+3
# ──────────────────────────────────────────────────────────────
def calc_d4(planets: List[Dict], ascendant: Dict) -> Dict:
    """D4 Chaturthamsha — property, vehicles, real estate."""
    out = []
    for p in planets:
        sign_idx, deg = int(p["longitude"] / 30), p["longitude"] % 30
        part = min(int(deg / 7.5), 3)
        if sign_idx % 2 == 0:  # odd sign (Aries=0)
            d_idx = (sign_idx + part * 3) % 12
        else:
            d_idx = (sign_idx + 3 + part * 3) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / 7.5), 3)
    if asc_idx % 2 == 0:
        d4_asc = (asc_idx + asc_part * 3) % 12
    else:
        d4_asc = (asc_idx + 3 + asc_part * 3) % 12
    return {"chart": "D4 - Chaturthamsha (Property & Assets)", "division": 4,
            "description": "Fixed assets, property, vehicles, land",
            "ascendant": SIGNS[d4_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D7 — Saptamsha (Children, Progeny)
# Each sign divided into 7 parts of 4°17'8.57" each
# Odd signs: start from same sign; Even signs: start from 7th sign
# ──────────────────────────────────────────────────────────────
def calc_d7(planets: List[Dict], ascendant: Dict) -> Dict:
    """D7 Saptamsha — children, progeny, creative power."""
    out = []
    span = 30.0 / 7.0
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / span), 6)
        if sign_idx % 2 == 0:
            d_idx = (sign_idx + part) % 12
        else:
            d_idx = (sign_idx + 6 + part) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / span), 6)
    if asc_idx % 2 == 0:
        d7_asc = (asc_idx + asc_part) % 12
    else:
        d7_asc = (asc_idx + 6 + asc_part) % 12
    return {"chart": "D7 - Saptamsha (Children & Progeny)", "division": 7,
            "description": "Children, progeny, creative output",
            "ascendant": SIGNS[d7_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D12 — Dwadashamsha (Parents, Ancestry)
# Each sign divided into 12 parts of 2°30' each
# Count starts from the sign itself
# ──────────────────────────────────────────────────────────────
def calc_d12(planets: List[Dict], ascendant: Dict) -> Dict:
    """D12 Dwadashamsha — parents, lineage, ancestry."""
    out = []
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / 2.5), 11)
        d_idx = (sign_idx + part) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / 2.5), 11)
    d12_asc = (asc_idx + asc_part) % 12
    return {"chart": "D12 - Dwadashamsha (Parents & Lineage)", "division": 12,
            "description": "Parents, ancestry, karmic lineage",
            "ascendant": SIGNS[d12_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D16 — Shodashamsha (Vehicles, Happiness, Comforts)
# Each sign divided into 16 parts of 1°52'30" each
# Movable signs start from Aries, Fixed from Leo, Dual from Sagittarius
# ──────────────────────────────────────────────────────────────
_D16_START = {
    # Movable: Aries(0), Cancer(3), Libra(6), Capricorn(9) → start Aries(0)
    0: 0, 3: 0, 6: 0, 9: 0,
    # Fixed: Taurus(1), Leo(4), Scorpio(7), Aquarius(10) → start Leo(4)
    1: 4, 4: 4, 7: 4, 10: 4,
    # Dual: Gemini(2), Virgo(5), Sagittarius(8), Pisces(11) → start Sagittarius(8)
    2: 8, 5: 8, 8: 8, 11: 8,
}

def calc_d16(planets: List[Dict], ascendant: Dict) -> Dict:
    """D16 Shodashamsha — vehicles, happiness, luxuries."""
    out = []
    span = 30.0 / 16.0
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / span), 15)
        start = _D16_START[sign_idx]
        d_idx = (start + part) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / span), 15)
    d16_asc = (_D16_START[asc_idx] + asc_part) % 12
    return {"chart": "D16 - Shodashamsha (Vehicles & Comforts)", "division": 16,
            "description": "Vehicles, conveyances, happiness",
            "ascendant": SIGNS[d16_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D20 — Vimshamsha (Spiritual Progress, Upasana)
# Each sign divided into 20 parts of 1°30' each
# Movable → start Aries, Fixed → start Sagittarius, Dual → start Leo
# ──────────────────────────────────────────────────────────────
_D20_START = {
    0: 0, 3: 0, 6: 0, 9: 0,       # Movable → Aries
    1: 8, 4: 8, 7: 8, 10: 8,      # Fixed → Sagittarius
    2: 4, 5: 4, 8: 4, 11: 4,      # Dual → Leo
}

def calc_d20(planets: List[Dict], ascendant: Dict) -> Dict:
    """D20 Vimshamsha — spiritual pursuits, devotion."""
    out = []
    span = 30.0 / 20.0
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / span), 19)
        start = _D20_START[sign_idx]
        d_idx = (start + part) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / span), 19)
    d20_asc = (_D20_START[asc_idx] + asc_part) % 12
    return {"chart": "D20 - Vimshamsha (Spiritual Progress)", "division": 20,
            "description": "Spiritual evolution, religious devotion, upasana",
            "ascendant": SIGNS[d20_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D24 — Chaturvimshamsha / Siddhamsha (Learning, Education)
# Each sign divided into 24 parts of 1°15' each
# Odd signs → start Leo, Even signs → start Cancer
# ──────────────────────────────────────────────────────────────
def calc_d24(planets: List[Dict], ascendant: Dict) -> Dict:
    """D24 Siddhamsha — education, knowledge, academic success."""
    out = []
    span = 30.0 / 24.0
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / span), 23)
        start = 4 if sign_idx % 2 == 0 else 3  # odd→Leo(4), even→Cancer(3)
        d_idx = (start + part) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / span), 23)
    d24_asc = ((4 if asc_idx % 2 == 0 else 3) + asc_part) % 12
    return {"chart": "D24 - Siddhamsha (Education & Learning)", "division": 24,
            "description": "Education, academic achievements, knowledge",
            "ascendant": SIGNS[d24_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D27 — Saptavimshamsha / Bhamsha (Strength & Weakness)
# Each sign divided into 27 parts of 1°6'40" each
# Fire signs → start Aries, Earth → start Cancer,
# Air → start Libra, Water → start Capricorn
# ──────────────────────────────────────────────────────────────
_D27_START = {
    0: 0, 4: 0, 8: 0,       # Fire (Aries, Leo, Sag) → Aries
    1: 3, 5: 3, 9: 3,       # Earth (Taurus, Virgo, Cap) → Cancer
    2: 6, 6: 6, 10: 6,      # Air (Gemini, Libra, Aqua) → Libra
    3: 9, 7: 9, 11: 9,      # Water (Cancer, Scorpio, Pisces) → Capricorn
}

def calc_d27(planets: List[Dict], ascendant: Dict) -> Dict:
    """D27 Bhamsha / Saptavimshamsha — strength & weakness analysis."""
    out = []
    span = 30.0 / 27.0
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / span), 26)
        start = _D27_START[sign_idx]
        d_idx = (start + part) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / span), 26)
    d27_asc = (_D27_START[asc_idx] + asc_part) % 12
    return {"chart": "D27 - Bhamsha (Strength & Weakness)", "division": 27,
            "description": "Inherent strengths and weaknesses of planets",
            "ascendant": SIGNS[d27_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D30 — Trimshamsha (Misfortune, Evils, Rishta)
# Each sign divided into 5 unequal parts (5°,5°,8°,7°,5°)
# Odd signs: Mars(5°), Sat(5°), Jup(8°), Mer(7°), Ven(5°) → Ari,Aqu,Sag,Gem,Lib
# Even signs: Ven(5°), Mer(7°), Jup(8°), Sat(5°), Mars(5°) → Tau,Vir,Pis,Cap,Sco
# ──────────────────────────────────────────────────────────────
_D30_ODD  = [(5, 0), (10, 10), (18, 8), (25, 2), (30, 6)]   # Aries, Aquarius, Sag, Gemini, Libra
_D30_EVEN = [(5, 1), (12, 5), (20, 11), (25, 9), (30, 7)]   # Taurus, Virgo, Pisces, Cap, Scorpio

def calc_d30(planets: List[Dict], ascendant: Dict) -> Dict:
    """D30 Trimshamsha — misfortune, evils, rishta."""
    out = []
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        table = _D30_ODD if sign_idx % 2 == 0 else _D30_EVEN
        d_idx = table[-1][1]  # fallback
        for boundary, idx in table:
            if deg < boundary:
                d_idx = idx
                break
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    # Ascendant
    asc_idx = int(ascendant["longitude"] / 30)
    asc_deg = ascendant["longitude"] % 30
    table = _D30_ODD if asc_idx % 2 == 0 else _D30_EVEN
    d30_asc_idx = table[-1][1]
    for boundary, idx in table:
        if asc_deg < boundary:
            d30_asc_idx = idx
            break
    return {"chart": "D30 - Trimshamsha (Misfortunes & Evils)", "division": 30,
            "description": "Misfortune, disease, hidden troubles",
            "ascendant": SIGNS[d30_asc_idx], "planets": out}


# ──────────────────────────────────────────────────────────────
# D40 — Khavedamsha (Auspicious / Inauspicious Effects)
# Each sign divided into 40 parts of 0°45' each
# Odd signs → start Aries, Even signs → start Libra
# ──────────────────────────────────────────────────────────────
def calc_d40(planets: List[Dict], ascendant: Dict) -> Dict:
    """D40 Khavedamsha — auspicious and inauspicious effects."""
    out = []
    span = 30.0 / 40.0
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / span), 39)
        start = 0 if sign_idx % 2 == 0 else 6  # odd→Aries, even→Libra
        d_idx = (start + part) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / span), 39)
    d40_asc = ((0 if asc_idx % 2 == 0 else 6) + asc_part) % 12
    return {"chart": "D40 - Khavedamsha (Matrilineal Legacy)", "division": 40,
            "description": "Auspicious/inauspicious effects, maternal legacy",
            "ascendant": SIGNS[d40_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D45 — Akshavedamsha (General Well-Being, Paternal Legacy)
# Each sign divided into 45 parts of 0°40' each
# Movable → start Aries, Fixed → start Leo, Dual → start Sagittarius
# ──────────────────────────────────────────────────────────────
_D45_START = {
    0: 0, 3: 0, 6: 0, 9: 0,       # Movable → Aries
    1: 4, 4: 4, 7: 4, 10: 4,      # Fixed → Leo
    2: 8, 5: 8, 8: 8, 11: 8,      # Dual → Sagittarius
}

def calc_d45(planets: List[Dict], ascendant: Dict) -> Dict:
    """D45 Akshavedamsha — general well-being, paternal legacy."""
    out = []
    span = 30.0 / 45.0
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / span), 44)
        start = _D45_START[sign_idx]
        d_idx = (start + part) % 12
        d_sign = SIGNS[d_idx]
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / span), 44)
    d45_asc = (_D45_START[asc_idx] + asc_part) % 12
    return {"chart": "D45 - Akshavedamsha (Paternal Legacy)", "division": 45,
            "description": "General well-being, paternal lineage, character",
            "ascendant": SIGNS[d45_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# D60 — Shashtiamsha (Past Life Karma, Overall Fortune)
# Each sign divided into 60 parts of 0°30' each
# Odd signs: count from Aries; Even signs: count from Libra
# Each part has a specific deity name (60 deities)
# ──────────────────────────────────────────────────────────────
D60_DEITIES = [
    "Ghora","Rakshasa","Deva","Kubera","Yaksha","Kinnara","Bhrashta","Kulaghna",
    "Garala","Agni","Maya","Purishaka","Apampathi","Marut","Kaala","Sarpa",
    "Amrita","Indu","Mridu","Komala","Heramba","Brahma","Vishnu","Maheshwara",
    "Deva","Ardra","Kalinasa","Kshitisa","Kamalaakara","Gulika","Mrityu","Kaala",
    "Davagni","Ghora","Yama","Kantaka","Sudha","Amrita","Poornachandra","Vishagdha",
    "Kulanashana","Vamshakshaya","Utpata","Kaala","Saumya","Komala","Sheetala",
    "Karala","Chandramukhi","Praveena","Kalapavaka","Dandayudha","Nirmala","Saumya",
    "Kroora","Atisheetala","Amrita","Payodhi","Bhramana","Chandrarekha"
]

def calc_d60(planets: List[Dict], ascendant: Dict) -> Dict:
    """D60 Shashtiamsha — past-life karma, overall fortune, deepest divisional."""
    out = []
    span = 30.0 / 60.0
    for p in planets:
        sign_idx = int(p["longitude"] / 30)
        deg = p["longitude"] % 30
        part = min(int(deg / span), 59)
        start = 0 if sign_idx % 2 == 0 else 6  # odd→Aries, even→Libra
        d_idx = (start + part) % 12
        d_sign = SIGNS[d_idx]
        deity = D60_DEITIES[part] if part < len(D60_DEITIES) else ""
        out.append({"planet": p["planet"], "d1_sign": p["sign"],
                     "sign": d_sign, "deity": deity,
                     "strength": _get_strength(p["planet"], d_sign)})
    asc_idx = int(ascendant["longitude"] / 30)
    asc_part = min(int(ascendant["longitude"] % 30 / span), 59)
    d60_asc = ((0 if asc_idx % 2 == 0 else 6) + asc_part) % 12
    return {"chart": "D60 - Shashtiamsha (Past Life Karma)", "division": 60,
            "description": "Past-life karma, overall fortune, deepest varga",
            "ascendant": SIGNS[d60_asc], "planets": out}


# ──────────────────────────────────────────────────────────────
# Vargottama detection across all vargas
# ──────────────────────────────────────────────────────────────
def detect_vargottama(d1_planets: List[Dict], all_charts: Dict) -> List[Dict]:
    """Find planets in the same sign in D1 and any divisional chart."""
    vargottama = []
    for p in d1_planets:
        planet = p["planet"]
        d1_sign = p["sign"]
        matches = []
        for key, chart_data in all_charts.items():
            if key in ("d1_rasi", "d1"):
                continue
            for cp in chart_data.get("planets", []):
                if cp["planet"] == planet:
                    div_sign = cp.get("sign") or cp.get("d9_sign") or cp.get("d10_sign") or cp.get("d3_sign") or cp.get("hora_sign", "")
                    if div_sign == d1_sign:
                        matches.append(key)
        if matches:
            vargottama.append({"planet": planet, "sign": d1_sign, "matching_charts": matches})
    return vargottama


# ──────────────────────────────────────────────────────────────
# Planetary dignity summary across all vargas
# ──────────────────────────────────────────────────────────────
DIGNITY_SCORES = {
    "Exalted (Uchcha)": 3,
    "Own Sign (Swakshetra)": 2,
    "Normal": 0,
    "Debilitated (Neecha)": -3,
}

def dignity_summary(all_charts: Dict) -> List[Dict]:
    """Summarize planetary dignity across all 16 vargas."""
    planet_scores: Dict[str, Dict] = {}
    for key, chart_data in all_charts.items():
        for cp in chart_data.get("planets", []):
            pname = cp["planet"]
            strength = cp.get("strength", cp.get("d9_strength", cp.get("d10_strength", "Normal")))
            if pname not in planet_scores:
                planet_scores[pname] = {"planet": pname, "total": 0, "details": {},
                                         "exalted": 0, "own": 0, "debilitated": 0}
            score = DIGNITY_SCORES.get(strength, 0)
            planet_scores[pname]["total"] += score
            planet_scores[pname]["details"][key] = strength
            if "Exalted" in strength:
                planet_scores[pname]["exalted"] += 1
            elif "Own" in strength:
                planet_scores[pname]["own"] += 1
            elif "Debilitated" in strength:
                planet_scores[pname]["debilitated"] += 1
    return sorted(planet_scores.values(), key=lambda x: x["total"], reverse=True)


# ──────────────────────────────────────────────────────────────
# SHODASVARGA_CHARTS — all 16 in order
# ──────────────────────────────────────────────────────────────
SHODASVARGA_LIST = [
    "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
    "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60",
]

SHODASVARGA_NAMES = {
    "D1":  "Rasi",        "D2":  "Hora",         "D3":  "Drekkana",
    "D4":  "Chaturthamsha","D7":  "Saptamsha",    "D9":  "Navamsha",
    "D10": "Dashamsha",   "D12": "Dwadashamsha",  "D16": "Shodashamsha",
    "D20": "Vimshamsha",  "D24": "Siddhamsha",    "D27": "Bhamsha",
    "D30": "Trimshamsha", "D40": "Khavedamsha",   "D45": "Akshavedamsha",
    "D60": "Shashtiamsha",
}


def calculate_shodasvarga(
    planets: List[Dict],
    ascendant: Dict,
    charts: List[str] = None,
) -> Dict:
    """
    Calculate any/all of the 16 Shodasvarga divisional charts.
    Returns a dict keyed by lowercase chart ID (e.g. "d1", "d9").
    """
    if charts is None:
        charts = SHODASVARGA_LIST
    charts = [c.upper() for c in charts]

    calc_map = {
        "D1":  lambda: calc_d1_rasi(planets, ascendant),
        "D2":  lambda: _wrap_legacy(calc_d2_hora(planets), 2),
        "D3":  lambda: _wrap_legacy(calc_d3_drekkana(planets), 3),
        "D4":  lambda: calc_d4(planets, ascendant),
        "D7":  lambda: calc_d7(planets, ascendant),
        "D9":  lambda: _wrap_d9(calc_d9_navamsha(planets, ascendant)),
        "D10": lambda: _wrap_d10(calc_d10_dashamsha(planets, ascendant)),
        "D12": lambda: calc_d12(planets, ascendant),
        "D16": lambda: calc_d16(planets, ascendant),
        "D20": lambda: calc_d20(planets, ascendant),
        "D24": lambda: calc_d24(planets, ascendant),
        "D27": lambda: calc_d27(planets, ascendant),
        "D30": lambda: calc_d30(planets, ascendant),
        "D40": lambda: calc_d40(planets, ascendant),
        "D45": lambda: calc_d45(planets, ascendant),
        "D60": lambda: calc_d60(planets, ascendant),
    }

    result: Dict = {}
    for c in charts:
        fn = calc_map.get(c)
        if fn:
            result[c.lower()] = fn()
    return result


def _wrap_legacy(data: Dict, division: int) -> Dict:
    """Normalize legacy D2/D3 output to match the new standardized format."""
    data["division"] = division
    # Normalize planet sign keys to 'sign'
    for p in data.get("planets", []):
        if "hora_sign" in p and "sign" not in p:
            p["sign"] = p["hora_sign"]
        if "d3_sign" in p and "sign" not in p:
            p["sign"] = p["d3_sign"]
    if "ascendant" not in data:
        data["ascendant"] = ""
    return data


def _wrap_d9(data: Dict) -> Dict:
    """Normalize D9 output."""
    data["division"] = 9
    data["ascendant"] = data.get("navamsha_ascendant", "")
    for p in data.get("planets", []):
        if "d9_sign" in p and "sign" not in p:
            p["sign"] = p["d9_sign"]
        if "d9_strength" in p and "strength" not in p:
            p["strength"] = p["d9_strength"]
    return data


def _wrap_d10(data: Dict) -> Dict:
    """Normalize D10 output."""
    data["division"] = 10
    data["ascendant"] = data.get("d10_ascendant", "")
    for p in data.get("planets", []):
        if "d10_sign" in p and "sign" not in p:
            p["sign"] = p["d10_sign"]
        if "d10_strength" in p and "strength" not in p:
            p["strength"] = p["d10_strength"]
    return data


# ──────────────────────────────────────────────────────────────
# Master function: calculate all divisional charts (legacy compat)
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
