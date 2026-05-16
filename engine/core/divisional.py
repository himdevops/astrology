"""
divisional.py — Shodashvarga (16 Divisional Chart) calculations.
================================================================
Each function takes a sidereal longitude (0-360) and returns the
divisional sign index (0-11, mapping to SIGNS[]).

All formulas follow Parashari rules (BPHS).
"""
from __future__ import annotations

from core.constants import SIGNS, SIGN_LORDS


# ─── Helper ─────────────────────────────────────────────────

def _sign_index(lon: float) -> int:
    """Sign index (0-11) from longitude."""
    return int(lon / 30) % 12


def _degree_in_sign(lon: float) -> float:
    """Degree within sign (0-30)."""
    return lon % 30


# ─── D1: Rashi (Natal) ──────────────────────────────────────

def d1_sign(lon: float) -> int:
    """D1 — Rashi chart. Same as natal sign."""
    return _sign_index(lon)


# ─── D2: Hora ───────────────────────────────────────────────

def d2_sign(lon: float) -> int:
    """
    D2 — Hora chart.
    First half (0-15°) of odd signs → Sun (Leo=4).
    Second half (15-30°) of odd signs → Moon (Cancer=3).
    First half of even signs → Moon (Cancer=3).
    Second half of even signs → Sun (Leo=4).
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    is_odd = (sign_idx % 2 == 0)  # 0=Aries(odd), 1=Taurus(even), etc.

    if is_odd:
        return 4 if deg < 15 else 3   # Leo : Cancer
    else:
        return 3 if deg < 15 else 4   # Cancer : Leo


# ─── D3: Drekkana ───────────────────────────────────────────

def d3_sign(lon: float) -> int:
    """
    D3 — Drekkana (Decanate).
    Each sign divided into 3 parts of 10°.
    Part 1 (0-10°): same sign.
    Part 2 (10-20°): 5th from sign.
    Part 3 (20-30°): 9th from sign.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)

    if deg < 10:
        return sign_idx
    elif deg < 20:
        return (sign_idx + 4) % 12
    else:
        return (sign_idx + 8) % 12


# ─── D4: Chaturthamsha ──────────────────────────────────────

def d4_sign(lon: float) -> int:
    """
    D4 — Chaturthamsha.
    Each sign divided into 4 parts of 7°30'.
    Part 1: same sign. Part 2: +3. Part 3: +6. Part 4: +9.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / 7.5)
    if part > 3:
        part = 3
    return (sign_idx + part * 3) % 12


# ─── D7: Saptamsha ──────────────────────────────────────────

def d7_sign(lon: float) -> int:
    """
    D7 — Saptamsha.
    Each sign divided into 7 parts of 4°17'8.57".
    Odd signs: count from same sign.
    Even signs: count from 7th from sign.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / (30.0 / 7))
    if part > 6:
        part = 6
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        return (sign_idx + part) % 12
    else:
        return (sign_idx + 6 + part) % 12


# ─── D9: Navamsha ───────────────────────────────────────────

def d9_sign(lon: float) -> int:
    """
    D9 — Navamsha (most important divisional chart).
    Each sign divided into 9 parts of 3°20'.
    Fire signs start from Aries, Earth from Capricorn,
    Air from Libra, Water from Cancer.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / (30.0 / 9))
    if part > 8:
        part = 8

    # Starting sign based on element
    element_start = [0, 9, 6, 3]  # Fire=Ar, Earth=Cap, Air=Lib, Water=Can
    element_idx = sign_idx % 4  # 0=Fire, 1=Earth, 2=Air, 3=Water

    # But the cycle is: Fire(0,4,8), Earth(1,5,9), Air(2,6,10), Water(3,7,11)
    # sign_idx % 4 gives: Ar=0,Ta=1,Ge=2,Ca=3,Le=0,Vi=1,Li=2,Sc=3...
    # This maps Fire→0, Earth→1, Air→2, Water→3 ✓

    start = element_start[element_idx]
    return (start + part) % 12


# ─── D10: Dashamsha ─────────────────────────────────────────

def d10_sign(lon: float) -> int:
    """
    D10 — Dashamsha.
    Each sign divided into 10 parts of 3°.
    Odd signs: count from same sign.
    Even signs: count from 9th from sign.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / 3.0)
    if part > 9:
        part = 9
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        return (sign_idx + part) % 12
    else:
        return (sign_idx + 8 + part) % 12


# ─── D12: Dwadashamsha ──────────────────────────────────────

def d12_sign(lon: float) -> int:
    """
    D12 — Dwadashamsha.
    Each sign divided into 12 parts of 2°30'.
    Count from same sign.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / 2.5)
    if part > 11:
        part = 11
    return (sign_idx + part) % 12


# ─── D16: Shodashamsha ──────────────────────────────────────

def d16_sign(lon: float) -> int:
    """
    D16 — Shodashamsha.
    Each sign divided into 16 parts of 1°52'30".
    Cardinal signs: count from Aries.
    Fixed signs: count from Leo.
    Mutable signs: count from Sagittarius.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / (30.0 / 16))
    if part > 15:
        part = 15

    modality = sign_idx % 3  # 0=Cardinal, 1=Fixed, 2=Mutable
    start = [0, 4, 8][modality]
    return (start + part) % 12


# ─── D20: Vimshamsha ────────────────────────────────────────

def d20_sign(lon: float) -> int:
    """
    D20 — Vimshamsha.
    Each sign divided into 20 parts of 1°30'.
    Cardinal signs: count from Aries.
    Fixed signs: count from Sagittarius.
    Mutable signs: count from Leo.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / 1.5)
    if part > 19:
        part = 19

    modality = sign_idx % 3
    start = [0, 8, 4][modality]
    return (start + part) % 12


# ─── D24: Chaturvimshamsha ──────────────────────────────────

def d24_sign(lon: float) -> int:
    """
    D24 — Chaturvimshamsha (Siddhamsha).
    Each sign divided into 24 parts of 1°15'.
    Odd signs: count from Leo.
    Even signs: count from Cancer.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / 1.25)
    if part > 23:
        part = 23
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        return (4 + part) % 12   # from Leo
    else:
        return (3 + part) % 12   # from Cancer


# ─── D27: Bhamsha (Nakshatramsha) ───────────────────────────

def d27_sign(lon: float) -> int:
    """
    D27 — Bhamsha / Nakshatramsha.
    Each sign divided into 27 parts of 1°6'40".
    Fire signs: count from Aries.
    Earth signs: count from Cancer.
    Air signs: count from Libra.
    Water signs: count from Capricorn.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / (30.0 / 27))
    if part > 26:
        part = 26

    element_idx = sign_idx % 4
    start = [0, 3, 6, 9][element_idx]
    return (start + part) % 12


# ─── D30: Trimshamsha ───────────────────────────────────────

def d30_sign(lon: float) -> int:
    """
    D30 — Trimshamsha.
    Unequal divisions (Parashari method).
    Odd signs: Mars(5°), Saturn(5°), Jupiter(8°), Mercury(7°), Venus(5°).
    Even signs: Venus(5°), Mercury(7°), Jupiter(8°), Saturn(5°), Mars(5°).
    Maps to the sign ruled by that planet (Aries/Scorpio, Capricorn/Aquarius, etc.)
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        # Odd: Mars 0-5, Saturn 5-10, Jupiter 10-18, Mercury 18-25, Venus 25-30
        if deg < 5:
            return 0   # Aries (Mars)
        elif deg < 10:
            return 10  # Aquarius (Saturn)
        elif deg < 18:
            return 8   # Sagittarius (Jupiter)
        elif deg < 25:
            return 2   # Gemini (Mercury)
        else:
            return 1   # Taurus (Venus)
    else:
        # Even: Venus 0-5, Mercury 5-12, Jupiter 12-20, Saturn 20-25, Mars 25-30
        if deg < 5:
            return 6   # Libra (Venus)
        elif deg < 12:
            return 5   # Virgo (Mercury)
        elif deg < 20:
            return 11  # Pisces (Jupiter)
        elif deg < 25:
            return 9   # Capricorn (Saturn)
        else:
            return 7   # Scorpio (Mars)


# ─── D40: Khavedamsha ───────────────────────────────────────

def d40_sign(lon: float) -> int:
    """
    D40 — Khavedamsha.
    Each sign divided into 40 parts of 0°45'.
    Odd signs: count from Aries.
    Even signs: count from Libra.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / 0.75)
    if part > 39:
        part = 39
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        return (0 + part) % 12
    else:
        return (6 + part) % 12


# ─── D45: Akshavedamsha ─────────────────────────────────────

def d45_sign(lon: float) -> int:
    """
    D45 — Akshavedamsha.
    Each sign divided into 45 parts of 0°40'.
    Cardinal signs: count from Aries.
    Fixed signs: count from Leo.
    Mutable signs: count from Sagittarius.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / (30.0 / 45))
    if part > 44:
        part = 44

    modality = sign_idx % 3
    start = [0, 4, 8][modality]
    return (start + part) % 12


# ─── D60: Shashtiamsha ──────────────────────────────────────

def d60_sign(lon: float) -> int:
    """
    D60 — Shashtiamsha.
    Each sign divided into 60 parts of 0°30'.
    Count from same sign.
    """
    sign_idx = _sign_index(lon)
    deg = _degree_in_sign(lon)
    part = int(deg / 0.5)
    if part > 59:
        part = 59
    return (sign_idx + part) % 12


# ═══════════════════════════════════════════════════════════════
# Master lookup
# ═══════════════════════════════════════════════════════════════

VARGA_FUNCTIONS = {
    "D1":  d1_sign,
    "D2":  d2_sign,
    "D3":  d3_sign,
    "D4":  d4_sign,
    "D7":  d7_sign,
    "D9":  d9_sign,
    "D10": d10_sign,
    "D12": d12_sign,
    "D16": d16_sign,
    "D20": d20_sign,
    "D24": d24_sign,
    "D27": d27_sign,
    "D30": d30_sign,
    "D40": d40_sign,
    "D45": d45_sign,
    "D60": d60_sign,
}

VARGA_NAMES = {
    "D1":  "Rashi",
    "D2":  "Hora",
    "D3":  "Drekkana",
    "D4":  "Chaturthamsha",
    "D7":  "Saptamsha",
    "D9":  "Navamsha",
    "D10": "Dashamsha",
    "D12": "Dwadashamsha",
    "D16": "Shodashamsha",
    "D20": "Vimshamsha",
    "D24": "Chaturvimshamsha",
    "D27": "Bhamsha",
    "D30": "Trimshamsha",
    "D40": "Khavedamsha",
    "D45": "Akshavedamsha",
    "D60": "Shashtiamsha",
}

VARGA_ORDER = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
               "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]


def calc_varga(lon: float, varga: str) -> dict:
    """
    Calculate divisional sign for a given longitude and varga.
    Returns dict with sign name, index, and lord.
    """
    func = VARGA_FUNCTIONS.get(varga)
    if not func:
        raise ValueError(f"Unknown varga: {varga}")

    sign_idx = func(lon)
    sign_name = SIGNS[sign_idx]
    return {
        "sign_index": sign_idx,
        "sign": sign_name,
        "sign_lord": SIGN_LORDS[sign_name],
    }


def calc_all_vargas(lon: float) -> dict:
    """Calculate all 16 divisional placements for a longitude."""
    return {v: calc_varga(lon, v) for v in VARGA_ORDER}


# ═══════════════════════════════════════════════════════════════
# Varga Deities — BPHS traditional deity names for each subdivision
# Reference: Brihat Parashara Hora Shastra (Santhanam translation)
# ═══════════════════════════════════════════════════════════════

VARGA_DEITIES = {
    "D1": None,  # Rashi — no subdivision deities per BPHS varga framework

    # D2 — Hora: Sun's hora / Moon's hora
    "D2": ["Surya", "Chandra"],

    # D3 — Drekkana: same for all signs (BPHS Santhanam)
    #   1st Drekkana (0-10°) = Narada, 2nd (10-20°) = Agastya, 3rd (20-30°) = Durvasa
    "D3": ["Narada", "Agastya", "Durvasa"],

    # D4 — Chaturthamsha: same for all signs (four Kumaras)
    "D4": ["Sanaka", "Sananda", "Sanatana", "Sanat Kumara"],

    # D7 — Saptamsha: the seven oceans/liquids (Sapta Samudra)
    #   Odd signs forward, even signs reversed (BPHS)
    "D7": {
        "odd":  ["Kshara", "Ksheera", "Dadhi", "Ghrita", "Ikshu Rasa", "Madhu", "Shuddha Jala"],
        "even": ["Shuddha Jala", "Madhu", "Ikshu Rasa", "Ghrita", "Dadhi", "Ksheera", "Kshara"],
    },

    # D9 — Navamsha: Deva/Manushya/Rakshasa — MODALITY-based (BPHS Ch.6)
    #   Each navamsha cycles individually (not blocks of 3).
    #   Cardinal: D,M,R repeating.  Fixed: M,R,D repeating.  Mutable: R,D,M repeating.
    #   Verified against Parashara Light for two charts.
    "D9": {
        "cardinal": ["Deva", "Manushya", "Rakshasa", "Deva", "Manushya", "Rakshasa", "Deva", "Manushya", "Rakshasa"],
        "fixed":    ["Manushya", "Rakshasa", "Deva", "Manushya", "Rakshasa", "Deva", "Manushya", "Rakshasa", "Deva"],
        "mutable":  ["Rakshasa", "Deva", "Manushya", "Rakshasa", "Deva", "Manushya", "Rakshasa", "Deva", "Manushya"],
    },

    # D10 — Dashamsha: 10 Dikpala (directional guardians)
    #   Odd signs forward, even signs reversed (BPHS)
    "D10": {
        "odd":  ["Indra", "Agni", "Yama", "Rakshasa", "Varuna", "Vayu", "Kubera", "Ishan", "Brahma", "Ananta"],
        "even": ["Ananta", "Brahma", "Ishan", "Kubera", "Vayu", "Varuna", "Rakshasa", "Yama", "Agni", "Indra"],
    },

    # D12 — Dwadashamsha: 4-deity cycle repeating 3 times (BPHS)
    #   Ganesha, Ashwini Kumara, Yama, Ahi — same for all signs
    "D12": [
        "Ganesha", "Ashwini Kumara", "Yama", "Ahi",
        "Ganesha", "Ashwini Kumara", "Yama", "Ahi",
        "Ganesha", "Ashwini Kumara", "Yama", "Ahi",
    ],

    # D16 — Shodashamsha: 4-deity cycle (Brahma, Vishnu, Shiva, Surya)
    #   Repeats 4 times. Odd signs forward, even signs reversed.
    "D16": {
        "odd":  ["Brahma", "Vishnu", "Shiva", "Surya"] * 4,
        "even": ["Surya", "Shiva", "Vishnu", "Brahma"] * 4,
    },

    # D20 — Vimshamsha: 20 Shakti/goddess deities
    #   Completely DIFFERENT lists for odd vs even signs (BPHS)
    "D20": {
        "odd": [
            "Kali", "Gauri", "Jaya", "Lakshmi",
            "Vijaya", "Vimala", "Sati", "Tara",
            "Jvalamukhi", "Sveta", "Lalita", "Bagalamukhi",
            "Pratyangira", "Shachi", "Raudri", "Bhavani",
            "Varada", "Jaya", "Tripura", "Sumukhi",
        ],
        "even": [
            "Daya", "Megha", "Chhinnamasta", "Pisachini",
            "Dhumavati", "Matangi", "Bala", "Bhadra",
            "Aruna", "Anala", "Pingala", "Chuchchuka",
            "Ghora", "Varahi", "Vaishnavi", "Sita",
            "Bhuvanesvari", "Bhairavi", "Mangala", "Aparajita",
        ],
    },

    # D24 — Chaturvimshamsha: 12 deities repeated twice
    #   Odd signs from Leo, even signs reversed
    "D24": {
        "odd": [
            "Skanda", "Parashudhara", "Anala", "Vishwakarma",
            "Bhaga", "Mitra", "Maya", "Antaka",
            "Vrishadhvaja", "Govinda", "Madana", "Bhima",
            "Skanda", "Parashudhara", "Anala", "Vishwakarma",
            "Bhaga", "Mitra", "Maya", "Antaka",
            "Vrishadhvaja", "Govinda", "Madana", "Bhima",
        ],
        "even": [
            "Bhima", "Madana", "Govinda", "Vrishadhvaja",
            "Antaka", "Maya", "Mitra", "Bhaga",
            "Vishwakarma", "Anala", "Parashudhara", "Skanda",
            "Bhima", "Madana", "Govinda", "Vrishadhvaja",
            "Antaka", "Maya", "Mitra", "Bhaga",
            "Vishwakarma", "Anala", "Parashudhara", "Skanda",
        ],
    },

    # D27 — Bhamsha/Nakshatramsha: 27 Nakshatra presiding deities (BPHS)
    #   Element-based start sign: Fire=Aries, Earth=Cancer, Air=Libra, Water=Capricorn
    "D27": [
        "Ashwini Kumara", "Yama", "Agni", "Brahma",
        "Chandra", "Rudra", "Aditi", "Brihaspati",
        "Sarpa", "Pitri", "Bhaga", "Aryaman",
        "Surya", "Tvashta", "Vayu", "Indragni",
        "Mitra", "Indra", "Nirrti", "Varuna",
        "Vishwadeva", "Vishnu", "Vasu", "Varuna",
        "Aja Ekapada", "Ahirbudhnya", "Pushan",
    ],

    # D30 — Trimshamsha: unequal divisions with DEITY names (BPHS)
    #   Mars=Agni, Saturn=Vayu, Jupiter=Indra, Mercury=Kubera, Venus=Varuna
    "D30": {
        "odd":  ["Agni", "Vayu", "Indra", "Kubera", "Varuna"],
        "even": ["Varuna", "Kubera", "Indra", "Vayu", "Agni"],
    },

    # D40 — Khavedamsha: 12-deity cycle repeating (BPHS)
    #   Vishnu, Chandra, Marichi, Tvashta, Dhata, Shiva, Ravi, Yama,
    #   Yaksha, Gandharva, Kala, Varuna — cycling through 40 parts
    #   Odd from Aries, even from Libra
    "D40": None,  # Handled by cycling logic in calc_varga_deity

    # D45 — Akshavedamsha: 3-deity cycle (BPHS)
    #   Cardinal: Brahma, Shiva, Vishnu (×15)
    #   Fixed:    Shiva, Vishnu, Brahma (×15)
    #   Mutable:  Vishnu, Brahma, Shiva (×15)
    "D45": None,  # Handled by cycling logic in calc_varga_deity

    "D60": [
        "Ghora", "Rakshasa", "Deva", "Kubera",
        "Yaksha", "Kinnara", "Bhrashta", "Kulaghna",
        "Garala", "Vahni", "Maya", "Purishaka",
        "Apampathi", "Marutvan", "Kaala", "Sarpa",
        "Amrita", "Indu", "Mridu", "Komala",
        "Heramba", "Brahma", "Vishnu", "Maheshwara",
        "Deva", "Ardra", "Kalinasha", "Kshiteesha",
        "Kamalakara", "Gulika", "Mrityu", "Kaala",
        "Davagni", "Ghora", "Yama", "Kantaka",
        "Sudha", "Amrita", "Poornachandra", "Vishadagdha",
        "Kulanasha", "Vamshakshaya", "Utpata", "Kaala",
        "Saumya", "Komala", "Sheetala", "Karaladamshtra",
        "Chandramukhi", "Praveena", "Kaala Pavaka", "Dhannayaka",
        "Nirmala", "Saumya", "Kroora", "Atisheetala",
        "Amrita", "Payodhi", "Bhramana", "Chandrarekha",
    ],
}

# D40 cycling deities (12 names repeat through 40 divisions)
_D40_CYCLE = [
    "Vishnu", "Chandra", "Marichi", "Tvashta",
    "Dhata", "Shiva", "Ravi", "Yama",
    "Yaksha", "Gandharva", "Kala", "Varuna",
]

# D45 cycling deities (3 names repeat through 45 divisions, modality-based start)
_D45_CYCLES = {
    "cardinal": ["Brahma", "Shiva", "Vishnu"],
    "fixed":    ["Shiva", "Vishnu", "Brahma"],
    "mutable":  ["Vishnu", "Brahma", "Shiva"],
}


def _calc_part_index(lon: float, divisions: int) -> int:
    """Calculate which subdivision a longitude falls in (0-based)."""
    deg = _degree_in_sign(lon)
    part = int(deg / (30.0 / divisions))
    if part >= divisions:
        part = divisions - 1
    return part


def _calc_d30_part(lon: float) -> int:
    """D30 has unequal divisions — return part index (0-4)."""
    deg = _degree_in_sign(lon)
    sign_idx = _sign_index(lon)
    is_odd = (sign_idx % 2 == 0)

    if is_odd:
        # Odd: Mars 0-5, Saturn 5-10, Jupiter 10-18, Mercury 18-25, Venus 25-30
        if deg < 5:
            return 0
        elif deg < 10:
            return 1
        elif deg < 18:
            return 2
        elif deg < 25:
            return 3
        else:
            return 4
    else:
        # Even: Venus 0-5, Mercury 5-12, Jupiter 12-20, Saturn 20-25, Mars 25-30
        if deg < 5:
            return 0
        elif deg < 12:
            return 1
        elif deg < 20:
            return 2
        elif deg < 25:
            return 3
        else:
            return 4


def _get_modality(sign_idx: int) -> str:
    """Return modality: cardinal (0,3,6,9), fixed (1,4,7,10), mutable (2,5,8,11)."""
    return ["cardinal", "fixed", "mutable"][sign_idx % 3]


def calc_varga_deity(lon: float, varga: str) -> dict | None:
    """
    Calculate the deity for a given longitude in a specific varga.
    Follows BPHS rules:
      - Modality-based: D3, D9, D45
      - Odd/even reversal: D7, D10, D16, D24, D60
      - Odd/even different lists: D20, D30
      - Cycling deities: D12, D40, D45
    Returns dict with deity name and part index, or None if varga has no deities.
    """
    sign_idx = _sign_index(lon)
    is_odd = (sign_idx % 2 == 0)  # 0=Aries(odd), 1=Taurus(even), etc.

    # ── D1: no subdivision deities ──
    if varga == "D1":
        return None

    # ── D2: Sun's hora / Moon's hora ──
    if varga == "D2":
        deities = VARGA_DEITIES["D2"]
        deg = _degree_in_sign(lon)
        if is_odd:
            part = 0 if deg < 15 else 1
        else:
            part = 1 if deg < 15 else 0
        return {"deity": deities[part], "part": part + 1}

    # ── D3: Drekkana — same for all signs ──
    if varga == "D3":
        deities = VARGA_DEITIES["D3"]
        part = _calc_part_index(lon, 3)
        return {"deity": deities[part], "part": part + 1}

    # ── D4: Chaturthamsha — same for all signs ──
    if varga == "D4":
        deities = VARGA_DEITIES["D4"]
        part = _calc_part_index(lon, 4)
        return {"deity": deities[part], "part": part + 1}

    # ── D7: Saptamsha — odd forward, even reversed ──
    if varga == "D7":
        key = "odd" if is_odd else "even"
        deity_list = VARGA_DEITIES["D7"][key]
        part = _calc_part_index(lon, 7)
        return {"deity": deity_list[part], "part": part + 1}

    # ── D9: Navamsha — modality-based Deva/Manushya/Rakshasa ──
    if varga == "D9":
        modality = _get_modality(sign_idx)
        deity_list = VARGA_DEITIES["D9"][modality]
        part = _calc_part_index(lon, 9)
        return {"deity": deity_list[part], "part": part + 1}

    # ── D10: Dashamsha — odd forward, even reversed ──
    if varga == "D10":
        key = "odd" if is_odd else "even"
        deity_list = VARGA_DEITIES["D10"][key]
        part = _calc_part_index(lon, 10)
        return {"deity": deity_list[part], "part": part + 1}

    # ── D12: Dwadashamsha — 4-deity cycle ──
    if varga == "D12":
        deities = VARGA_DEITIES["D12"]
        part = _calc_part_index(lon, 12)
        return {"deity": deities[part], "part": part + 1}

    # ── D16: Shodashamsha — 4-deity cycle, odd/even ──
    if varga == "D16":
        key = "odd" if is_odd else "even"
        deity_list = VARGA_DEITIES["D16"][key]
        part = _calc_part_index(lon, 16)
        return {"deity": deity_list[part], "part": part + 1}

    # ── D20: Vimshamsha — different 20-deity lists for odd/even ──
    if varga == "D20":
        key = "odd" if is_odd else "even"
        deity_list = VARGA_DEITIES["D20"][key]
        part = _calc_part_index(lon, 20)
        return {"deity": deity_list[part], "part": part + 1}

    # ── D24: Chaturvimshamsha — odd/even reversed ──
    if varga == "D24":
        key = "odd" if is_odd else "even"
        deity_list = VARGA_DEITIES["D24"][key]
        part = _calc_part_index(lon, 24)
        return {"deity": deity_list[part], "part": part + 1}

    # ── D27: Bhamsha — 27 Nakshatra deities, same order for all ──
    if varga == "D27":
        deities = VARGA_DEITIES["D27"]
        part = _calc_part_index(lon, 27)
        return {"deity": deities[part], "part": part + 1}

    # ── D30: Trimshamsha — unequal divisions, odd/even deity names ──
    if varga == "D30":
        part = _calc_d30_part(lon)
        key = "odd" if is_odd else "even"
        deity_name = VARGA_DEITIES["D30"][key][part]
        return {"deity": deity_name, "part": part + 1}

    # ── D40: Khavedamsha — 12-deity cycle through 40 parts ──
    if varga == "D40":
        part = _calc_part_index(lon, 40)
        deity_name = _D40_CYCLE[part % 12]
        return {"deity": deity_name, "part": part + 1}

    # ── D45: Akshavedamsha — 3-deity cycle, modality-based start ──
    if varga == "D45":
        modality = _get_modality(sign_idx)
        cycle = _D45_CYCLES[modality]
        part = _calc_part_index(lon, 45)
        deity_name = cycle[part % 3]
        return {"deity": deity_name, "part": part + 1}

    # ── D60: Shashtiamsha — 60 deities, even signs reversed ──
    if varga == "D60":
        deities = VARGA_DEITIES["D60"]
        part = _calc_part_index(lon, 60)
        if is_odd:
            deity_name = deities[part]
        else:
            deity_name = deities[59 - part]
        return {"deity": deity_name, "part": part + 1}

    return None
