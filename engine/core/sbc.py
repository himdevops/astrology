"""
sbc.py — Sarvatobhadra Chakra (SBC) Grid Layout & Vedha Engine.
================================================================
Traditional 9x9 grid containing:
  - 28 Nakshatras (including Abhijit) around the border
  - 12 Rashis in the inner ring
  - 7 Varas (weekdays) in the inner area
  - 5 Tithi groups (Nanda, Bhadra, Jaya, Rikta, Poorna)
  - Vowels and pada sounds in remaining cells

Vedha (aspect) types:
  - Sun, Moon, Rahu, Ketu: 3-way (straight + both diagonals)
  - Mars, Saturn: left vedha (straight + left diagonal)
  - Mercury, Jupiter, Venus: right vedha (straight + right diagonal)
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Any, Optional


# ═══════════════════════════════════════════════════════════════
# 1. 28 NAKSHATRAS (including Abhijit as #28)
# ═══════════════════════════════════════════════════════════════

NAKSHATRAS_28 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Abhijit",  # 28th nakshatra (between U.Ashadha & Shravana)
    "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

NAKSHATRAS_28_HI = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा",
    "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा",
    "मघा", "पू.फा.", "उ.फा.", "हस्त",
    "चित्रा", "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा",
    "मूल", "पू.आ.", "उ.आ.",
    "अभिजित",
    "श्रवण", "धनिष्ठा", "शतभिषा",
    "पू.भा.", "उ.भा.", "रेवती",
]

# Short names for grid display
NAKSHATRAS_28_SHORT = [
    "Ashw", "Bhar", "Krit", "Rohi", "Mrig",
    "Ardr", "Puna", "Push", "Ashl",
    "Magh", "P.Ph", "U.Ph", "Hast",
    "Chit", "Swat", "Vish", "Anur", "Jyes",
    "Mula", "P.As", "U.As",
    "Abhi",
    "Shra", "Dhan", "Shat",
    "P.Bh", "U.Bh", "Reva",
]


# ═══════════════════════════════════════════════════════════════
# 2. 9x9 GRID LAYOUT
# ═══════════════════════════════════════════════════════════════

# Each cell identified by (row, col) from 0-8.
# Cell types: "nak" (nakshatra), "rashi", "vara", "tithi", "vowel", "pada_sound"

# Nakshatra positions around the border (clockwise from top-left)
# Format: (row, col): nakshatra_index_in_NAKSHATRAS_28
# Top row (left to right): cols 1-7
# Right col (top to bottom): rows 1-7
# Bottom row (right to left): cols 7-1
# Left col (bottom to top): rows 7-1

NAK_POSITIONS: Dict[Tuple[int, int], int] = {
    # Top row: Krittika(2), Rohini(3), Mrigashira(4), Ardra(5), Punarvasu(6), Pushya(7), Ashlesha(8)
    (0, 1): 2,  (0, 2): 3,  (0, 3): 4,  (0, 4): 5,  (0, 5): 6,  (0, 6): 7,  (0, 7): 8,
    # Right col: Magha(9), P.Phalguni(10), U.Phalguni(11), Hasta(12), Chitra(13), Swati(14), Vishakha(15)
    (1, 8): 9,  (2, 8): 10, (3, 8): 11, (4, 8): 12, (5, 8): 13, (6, 8): 14, (7, 8): 15,
    # Bottom row (R to L): Anuradha(16), Jyeshtha(17), Mula(18), P.Ashadha(19), U.Ashadha(20), Abhijit(21), Shravana(22)
    (8, 7): 16, (8, 6): 17, (8, 5): 18, (8, 4): 19, (8, 3): 20, (8, 2): 21, (8, 1): 22,
    # Left col (B to T): Dhanishtha(23), Shatabhisha(24), P.Bhadrapada(25), U.Bhadrapada(26), Revati(27), Ashwini(0), Bharani(1)
    (7, 0): 23, (6, 0): 24, (5, 0): 25, (4, 0): 26, (3, 0): 27, (2, 0): 0,  (1, 0): 1,
}

# Reverse mapping: nakshatra index → (row, col)
NAK_TO_POS: Dict[int, Tuple[int, int]] = {v: k for k, v in NAK_POSITIONS.items()}

# Rashi positions in inner ring
# Format: (row, col): rashi_index (0=Aries, 1=Taurus, ...)
RASHI_POSITIONS: Dict[Tuple[int, int], int] = {
    (2, 3): 1,   # Taurus
    (2, 4): 2,   # Gemini
    (2, 5): 3,   # Cancer
    (3, 6): 4,   # Leo
    (4, 6): 5,   # Virgo
    (5, 6): 6,   # Libra
    (6, 5): 7,   # Scorpio
    (6, 4): 8,   # Sagittarius
    (6, 3): 9,   # Capricorn
    (5, 2): 10,  # Aquarius
    (4, 2): 11,  # Pisces
    (3, 2): 0,   # Aries
}

RASHI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
RASHI_NAMES_SHORT = [
    "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
    "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis",
]
RASHI_NAMES_HI = [
    "मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन",
]

# Vara (weekday) positions — center area
# Sunday=0, Monday=1, Tuesday=2, Wednesday=3, Thursday=4, Friday=5, Saturday=6
VARA_POSITIONS: Dict[Tuple[int, int], int] = {
    (3, 4): 0,  # Sunday (center-ish)
    (4, 5): 1,  # Monday
    (3, 4): 0,  # Sunday — placed at traditional position
    (4, 4): 6,  # Saturday (Poorna position)
    (4, 3): 5,  # Friday
    (5, 4): 4,  # Thursday
    (3, 5): 2,  # Tuesday (with Sunday)
}

# Tithi group positions in center
# Nanda (1,6,11), Bhadra (2,7,12), Jaya (3,8,13), Rikta (4,9,14), Poorna (5,10,15/Amavasya/Purnima)
TITHI_POSITIONS: Dict[Tuple[int, int], str] = {
    (3, 4): "Nanda",   # shares with Sun/Tue
    (4, 5): "Bhadra",  # shares with Mon
    (5, 4): "Jaya",    # shares with Thu
    (4, 3): "Rikta",   # shares with Fri
    (4, 4): "Poorna",  # shares with Sat
}

# Combined center cell data: each cell can have vara + tithi
# (row, col): {"vara": weekday_name, "tithi": tithi_group}
CENTER_CELLS: Dict[Tuple[int, int], Dict[str, str]] = {
    (3, 4): {"vara": "Sun", "vara2": "Tue", "tithi": "Nanda"},
    (4, 5): {"vara": "Mon", "vara2": "Wed", "tithi": "Bhadra"},
    (5, 4): {"vara": "Thu", "tithi": "Jaya"},
    (4, 3): {"vara": "Fri", "tithi": "Rikta"},
    (4, 4): {"vara": "Sat", "tithi": "Poorna"},
}

# Vowel positions (4 corners + edges)
VOWEL_POSITIONS: Dict[Tuple[int, int], str] = {
    (0, 0): "A",       # अ
    (0, 8): "Aa",      # आ
    (8, 0): "Ee",      # ई
    (8, 8): "I",       # इ
    (1, 1): "Uu",      # ऊ
    (1, 7): "U",       # ऊ (variant)
    (7, 1): "Ri",      # ऋ
    (7, 7): "Rii",     # ॠ
    (2, 2): "Lr",      # ल्
    (2, 6): "Lr2",     # ल्
    (6, 2): "Ai",      # ऐ
    (6, 6): "E",       # ए
    (3, 5): "O_Au",    # ओ/औ
    (5, 3): "Ah",      # अ:
    (3, 3): "O",       # ओ
    (5, 5): "An",      # अं
}

# Pada sound positions (consonant sounds)
PADA_SOUND_POSITIONS: Dict[Tuple[int, int], str] = {
    (1, 2): "A2",   # अ
    (1, 3): "Va",   # व
    (1, 4): "Ka",   # क
    (1, 5): "Ha",   # ह
    (1, 6): "Da",   # ड
    (2, 1): "La",   # ल
    (2, 7): "Ma",   # म
    (3, 1): "Cha",  # च
    (3, 7): "Ta",   # ट
    (4, 1): "De",   # दे
    (4, 7): "Pa",   # प
    (5, 1): "Sha",  # श
    (5, 7): "Ra",   # र
    (6, 1): "Ga",   # ग
    (6, 7): "Te",   # ते
    (7, 2): "Kha",  # ख
    (7, 3): "Ja",   # ज
    (7, 4): "Bha",  # भ
    (7, 5): "Ya",   # य
    (7, 6): "Na",   # न
}

# Hindi vowels for display
VOWEL_HI: Dict[str, str] = {
    "A": "अ", "Aa": "आ", "I": "इ", "Ee": "ई",
    "U": "उ", "Uu": "ऊ", "Ri": "ऋ", "Rii": "ॠ",
    "Lr": "ल्", "Lr2": "ल्", "E": "ए", "Ai": "ऐ",
    "O": "ओ", "O_Au": "ओ/औ", "Ah": "अ:", "An": "अं",
}

PADA_SOUND_HI: Dict[str, str] = {
    "A2": "अ", "Va": "व", "Ka": "क", "Ha": "ह", "Da": "ड",
    "La": "ल", "Ma": "म", "Cha": "च", "Ta": "ट",
    "De": "दे", "Pa": "प", "Sha": "श", "Ra": "र",
    "Ga": "ग", "Te": "ते", "Kha": "ख", "Ja": "ज",
    "Bha": "भ", "Ya": "य", "Na": "न",
}


# ═══════════════════════════════════════════════════════════════
# 3. PADA SYLLABLES FOR EACH NAKSHATRA
# ═══════════════════════════════════════════════════════════════

# Each nakshatra has 4 padas with associated syllables
NAKSHATRA_PADAS: Dict[str, List[str]] = {
    "Ashwini":            ["चू", "चे", "चो", "ला"],
    "Bharani":            ["ली", "लू", "ले", "लो"],
    "Krittika":           ["अ", "ई", "उ", "ए"],
    "Rohini":             ["ओ", "वा", "वी", "वू"],
    "Mrigashira":         ["वे", "वो", "का", "की"],
    "Ardra":              ["कू", "घ", "ङ", "छ"],
    "Punarvasu":          ["के", "को", "हा", "ही"],
    "Pushya":             ["हू", "हे", "हो", "डा"],
    "Ashlesha":           ["डी", "डू", "डे", "डो"],
    "Magha":              ["मा", "मी", "मू", "मे"],
    "Purva Phalguni":     ["मो", "टा", "टी", "टू"],
    "Uttara Phalguni":    ["टे", "टो", "पा", "पी"],
    "Hasta":              ["पू", "ष", "ण", "ठ"],
    "Chitra":             ["पे", "पो", "रा", "री"],
    "Swati":              ["रू", "रे", "रो", "ता"],
    "Vishakha":           ["ती", "तू", "ते", "तो"],
    "Anuradha":           ["ना", "नी", "नू", "ने"],
    "Jyeshtha":           ["नो", "या", "यी", "यू"],
    "Mula":               ["ये", "यो", "भा", "भी"],
    "Purva Ashadha":      ["भू", "धा", "फा", "ढा"],
    "Uttara Ashadha":     ["भे", "भो", "जा", "जी"],
    "Abhijit":            ["ज्यू", "जे", "जो", "घा"],
    "Shravana":           ["खी", "खू", "खे", "खो"],
    "Dhanishtha":         ["गा", "गी", "गू", "गे"],
    "Shatabhisha":        ["गो", "सा", "सी", "सू"],
    "Purva Bhadrapada":   ["से", "सो", "दा", "दी"],
    "Uttara Bhadrapada":  ["दू", "थ", "झ", "ञ"],
    "Revati":             ["दे", "दो", "चा", "ची"],
}


# ═══════════════════════════════════════════════════════════════
# 4. VEDHA (ASPECT) SYSTEM
# ═══════════════════════════════════════════════════════════════

# Vedha rules:
#   Sun, Moon, Rahu, Ketu → always 3-way (straight + left + right)
#   Other planets (Mars, Mercury, Jupiter, Venus, Saturn):
#     - Ati-chari (speed > 125% of avg) → left vedha (straight + left diagonal)
#     - Retrograde (speed < 0)           → right vedha (straight + right diagonal)
#     - Normal direct motion             → front vedha (straight only)

THREE_WAY_PLANETS = {"Sun", "Moon", "Rahu", "Ketu"}

# Average daily speeds (deg/day) for reference
PLANET_AVG_SPEED: Dict[str, float] = {
    "Sun": 0.9856, "Moon": 13.1764, "Mars": 0.5240,
    "Mercury": 1.3833, "Jupiter": 0.0831, "Venus": 1.2000,
    "Saturn": 0.0335, "Rahu": 0.0530, "Ketu": 0.0530,
}

ATICHARI_FACTOR = 1.50  # 50% above average = ati-chari


def get_vedha_type(planet: str, speed: float, retrograde: bool) -> str:
    """
    Determine vedha type based on planet, speed, and retrograde status.

    Returns: "3way", "left", "right", or "front"
    """
    # Sun, Moon, Rahu, Ketu always get 3-way vedha
    if planet in THREE_WAY_PLANETS:
        result = "3way"
    elif retrograde or speed < 0:
        result = "right"
    else:
        avg = PLANET_AVG_SPEED.get(planet, 1.0)
        if abs(speed) > avg * ATICHARI_FACTOR:
            result = "left"
        else:
            result = "front"

    print(f"[VEDHA-v3] {planet}: speed={speed:.4f}, retro={retrograde}, -> {result}", flush=True)
    return result


def get_vedha_targets(
    row: int, col: int, vedha_type: str
) -> List[Tuple[int, int]]:
    """
    Get all cells that a planet at (row, col) aspects via vedha.

    Vedha rays extend from a border cell toward the center along:
      - straight (horizontal/vertical toward center)
      - left diagonal (from the planet's perspective)
      - right diagonal (from the planet's perspective)

    Returns list of (row, col) tuples that are vedha targets.
    """
    targets = []

    # Determine which border the cell is on and ray directions
    if row == 0:
        # Top border — planet faces down
        straight = (1, 0)
        left_diag = (1, 1)    # vama = planet's left = down-right
        right_diag = (1, -1)  # dakshina = planet's right = down-left
    elif row == 8:
        # Bottom border — planet faces up
        straight = (-1, 0)
        left_diag = (-1, -1)  # vama = planet's left = up-left
        right_diag = (-1, 1)  # dakshina = planet's right = up-right
    elif col == 0:
        # Left border — planet faces right
        straight = (0, 1)
        left_diag = (-1, 1)   # vama = planet's left = up-right
        right_diag = (1, 1)   # dakshina = planet's right = down-right
    elif col == 8:
        # Right border — planet faces left
        straight = (0, -1)
        left_diag = (1, -1)   # vama = planet's left = down-left
        right_diag = (-1, -1) # dakshina = planet's right = up-left
    else:
        # Not on border — no vedha
        return []

    # Opposite border cell (for front/sammukh vedha)
    if row == 0:
        front_target = (8, col)
    elif row == 8:
        front_target = (0, col)
    elif col == 0:
        front_target = (row, 8)
    else:  # col == 8
        front_target = (row, 0)

    # Each motion state = exactly ONE vedha direction:
    #   front  → straight only (opposite border nakshatra)
    #   left   → left diagonal only (ati-chari)
    #   right  → right diagonal only (retrograde)
    #   3way   → straight + both diagonals (Sun/Moon/Rahu/Ketu)

    if vedha_type == "front":
        # Only the one opposite nakshatra
        targets.append(front_target)

    elif vedha_type == "left":
        # Only left diagonal ray — no straight
        r, c = row + left_diag[0], col + left_diag[1]
        while 0 <= r <= 8 and 0 <= c <= 8:
            targets.append((r, c))
            r += left_diag[0]
            c += left_diag[1]

    elif vedha_type == "right":
        # Only right diagonal ray — no straight
        r, c = row + right_diag[0], col + right_diag[1]
        while 0 <= r <= 8 and 0 <= c <= 8:
            targets.append((r, c))
            r += right_diag[0]
            c += right_diag[1]

    elif vedha_type == "3way":
        # Straight (opposite nakshatra only) + both full diagonals
        targets.append(front_target)
        for dr, dc in [left_diag, right_diag]:
            r, c = row + dr, col + dc
            while 0 <= r <= 8 and 0 <= c <= 8:
                targets.append((r, c))
                r += dr
                c += dc

    return targets


def get_nakshatra_index_28(nakshatra_name: str) -> Optional[int]:
    """Get index in NAKSHATRAS_28 list. Maps standard 27-nak names too."""
    # Direct match
    if nakshatra_name in NAKSHATRAS_28:
        return NAKSHATRAS_28.index(nakshatra_name)

    # Abhijit is between U.Ashadha and Shravana (6°40' to 10°53'20" Capricorn)
    # In the 27-nakshatra system it doesn't exist, but planets can be placed there
    return None


def get_planet_nakshatra_28(longitude: float) -> Tuple[int, str, int]:
    """
    Map a sidereal longitude to one of 28 nakshatras.
    Abhijit occupies 6°40' to 10°53'20" Capricorn (276°40' to 280°53'20").

    Returns: (nakshatra_index_28, nakshatra_name, pada)
    """
    # Abhijit range: 276.6667° to 280.8889°
    ABHIJIT_START = 276.0 + 40.0 / 60.0      # 276°40'
    ABHIJIT_END = 280.0 + 53.0 / 60.0 + 20.0 / 3600.0  # 280°53'20"

    if ABHIJIT_START <= longitude < ABHIJIT_END:
        pada = min(int((longitude - ABHIJIT_START) / ((ABHIJIT_END - ABHIJIT_START) / 4)) + 1, 4)
        return 21, "Abhijit", pada

    # For other nakshatras, use the standard 27-nakshatra system
    # but shift indices to account for Abhijit's position
    nak_span = 360.0 / 27.0  # 13.3333°
    index_27 = int(longitude / nak_span) % 27

    # Standard 27 nakshatra names (same order as constants.py)
    STANDARD_27 = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
        "Ardra", "Punarvasu", "Pushya", "Ashlesha",
        "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
        "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha",
        "Shravana", "Dhanishtha", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
    ]

    name_27 = STANDARD_27[index_27]
    pada = min(int((longitude % nak_span) / (nak_span / 4)) + 1, 4)

    # Map 27-nak index to 28-nak index
    idx_28 = NAKSHATRAS_28.index(name_27)
    return idx_28, name_27, pada


def get_cell_type(row: int, col: int) -> str:
    """Determine the type of a cell in the 9x9 grid."""
    pos = (row, col)
    if pos in NAK_POSITIONS:
        return "nakshatra"
    if pos in RASHI_POSITIONS:
        return "rashi"
    if pos in CENTER_CELLS:
        return "center"
    if pos in VOWEL_POSITIONS:
        return "vowel"
    if pos in PADA_SOUND_POSITIONS:
        return "pada_sound"
    return "empty"


def build_grid() -> List[List[Dict[str, Any]]]:
    """
    Build the full 9x9 SBC grid data structure.
    Each cell is a dict with type-specific fields.
    """
    grid = []
    for r in range(9):
        row_data = []
        for c in range(9):
            pos = (r, c)
            cell: Dict[str, Any] = {"row": r, "col": c}

            if pos in NAK_POSITIONS:
                idx = NAK_POSITIONS[pos]
                cell["type"] = "nakshatra"
                cell["nak_index"] = idx
                cell["name"] = NAKSHATRAS_28[idx]
                cell["name_hi"] = NAKSHATRAS_28_HI[idx]
                cell["short"] = NAKSHATRAS_28_SHORT[idx]
                cell["padas"] = NAKSHATRA_PADAS.get(NAKSHATRAS_28[idx], ["", "", "", ""])
            elif pos in RASHI_POSITIONS:
                idx = RASHI_POSITIONS[pos]
                cell["type"] = "rashi"
                cell["rashi_index"] = idx
                cell["name"] = RASHI_NAMES[idx]
                cell["short"] = RASHI_NAMES_SHORT[idx]
                cell["name_hi"] = RASHI_NAMES_HI[idx]
            elif pos in CENTER_CELLS:
                info = CENTER_CELLS[pos]
                cell["type"] = "center"
                cell["vara"] = info.get("vara", "")
                cell["vara2"] = info.get("vara2", "")
                cell["tithi"] = info.get("tithi", "")
            elif pos in VOWEL_POSITIONS:
                vkey = VOWEL_POSITIONS[pos]
                cell["type"] = "vowel"
                cell["vowel"] = vkey
                cell["display"] = VOWEL_HI.get(vkey, vkey)
            elif pos in PADA_SOUND_POSITIONS:
                skey = PADA_SOUND_POSITIONS[pos]
                cell["type"] = "pada_sound"
                cell["sound"] = skey
                cell["display"] = PADA_SOUND_HI.get(skey, skey)
            else:
                cell["type"] = "empty"

            row_data.append(cell)
        grid.append(row_data)
    return grid


# ═══════════════════════════════════════════════════════════════
# 5. JANMA – KARMA – VINASHA NAKSHATRAS
# ═══════════════════════════════════════════════════════════════

def get_jkv_nakshatras(moon_nak_idx_28: int) -> Dict[str, Any]:
    """
    From birth Moon nakshatra (28-nak index), compute:
      Janma  = 1st  (birth Moon's nakshatra)
      Karma  = 10th from Janma
      Vinasha = 19th from Janma
    Returns dict with nakshatra names, indices, and grid positions.
    """
    results = {}
    for label, offset in [("janma", 0), ("karma", 9), ("vinasha", 18)]:
        idx = (moon_nak_idx_28 + offset) % 28
        name = NAKSHATRAS_28[idx]
        cell = NAK_TO_POS.get(idx)
        results[label] = {
            "nak_index": idx,
            "name": name,
            "row": cell[0] if cell else None,
            "col": cell[1] if cell else None,
        }
    return results


# ═══════════════════════════════════════════════════════════════
# 6. SHUBH / ASHUBH PLANET CLASSIFICATION
# ═══════════════════════════════════════════════════════════════

BENEFIC_PLANETS = {"Jupiter", "Venus", "Moon"}  # Mercury is conditional
MALEFIC_PLANETS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def classify_planet(planet: str, moon_waxing: bool = True) -> str:
    """Classify planet as shubh (benefic) or ashubh (malefic)."""
    if planet in BENEFIC_PLANETS:
        if planet == "Moon" and not moon_waxing:
            return "ashubh"
        return "shubh"
    if planet == "Mercury":
        return "shubh"  # Mercury alone is benefic; with malefics becomes malefic
    return "ashubh"


def is_moon_waxing(sun_lon: float, moon_lon: float) -> bool:
    """True if Moon is waxing (Shukla Paksha)."""
    diff = (moon_lon - sun_lon) % 360
    return diff < 180


# ═══════════════════════════════════════════════════════════════
# 7. VEDHA RESULT ANALYSIS
# ═══════════════════════════════════════════════════════════════

def analyze_vedha_hits(
    vedha_lines: List[Dict],
    natal_placements: List[Dict],
    transit_weekday: str,
    transit_tithi_group: str,
) -> List[Dict[str, Any]]:
    """
    Cross-reference transit vedha targets with natal positions.
    Returns list of vedha hit events: which transit planet vedhas
    which natal planet/rashi/vara/tithi and whether it's shubh or ashubh.
    """
    # Build natal lookup: (row, col) → list of natal planet names
    natal_at = {}
    for np in natal_placements:
        key = (np["row"], np["col"])
        if key not in natal_at:
            natal_at[key] = []
        natal_at[key].append(np["planet"])

    # Vara cell positions
    vara_map = {
        "Sun": (3, 4), "Tue": (3, 4),  # Sun/Tue share
        "Mon": (4, 5), "Wed": (4, 5),  # Mon/Wed share
        "Thu": (5, 4),
        "Fri": (4, 3),
        "Sat": (4, 4),
    }

    # Tithi cell positions
    tithi_map = {
        "Nanda": (3, 4),
        "Bhadra": (4, 5),
        "Jaya": (5, 4),
        "Rikta": (4, 3),
        "Poorna": (4, 4),
    }

    hits = []
    for vl in vedha_lines:
        planet = vl["planet"]
        nature = vl.get("nature", "ashubh")

        for t in vl.get("targets", []):
            tr, tc = t["row"], t["col"]
            cell_key = (tr, tc)

            # Check if vedha hits any natal planet
            if cell_key in natal_at:
                for natal_p in natal_at[cell_key]:
                    hits.append({
                        "transit_planet": planet,
                        "natal_target": natal_p,
                        "target_type": "planet",
                        "nature": nature,
                        "row": tr, "col": tc,
                    })

            # Check if vedha hits current weekday cell
            vara_cell = vara_map.get(transit_weekday)
            if vara_cell and cell_key == vara_cell:
                hits.append({
                    "transit_planet": planet,
                    "natal_target": transit_weekday,
                    "target_type": "vara",
                    "nature": nature,
                    "row": tr, "col": tc,
                })

            # Check if vedha hits current tithi cell
            tithi_cell = tithi_map.get(transit_tithi_group)
            if tithi_cell and cell_key == tithi_cell:
                hits.append({
                    "transit_planet": planet,
                    "natal_target": transit_tithi_group,
                    "target_type": "tithi",
                    "nature": nature,
                    "row": tr, "col": tc,
                })

            # Check if vedha hits a rashi cell
            if cell_key in RASHI_POSITIONS:
                rashi_idx = RASHI_POSITIONS[cell_key]
                hits.append({
                    "transit_planet": planet,
                    "natal_target": RASHI_NAMES[rashi_idx],
                    "target_type": "rashi",
                    "nature": nature,
                    "row": tr, "col": tc,
                })

    return hits


# ═══════════════════════════════════════════════════════════════
# 8. UPAGRAHA SYSTEM (SUB-PLANETS)
# ═══════════════════════════════════════════════════════════════

def calc_upagrahas(sun_longitude: float) -> List[Dict[str, Any]]:
    """
    Calculate 5 upagrahas from Sun's sidereal longitude.
    Dhuma      = Sun + 133°20'
    Vyatipata  = 360° - Dhuma
    Parivesha  = Vyatipata + 180°
    Chapa      = 360° - Parivesha
    Upaketu    = Chapa + 16°40'
    """
    dhuma = (sun_longitude + 133.0 + 20.0/60.0) % 360
    vyatipata = (360.0 - dhuma) % 360
    parivesha = (vyatipata + 180.0) % 360
    chapa = (360.0 - parivesha) % 360
    upaketu = (chapa + 16.0 + 40.0/60.0) % 360

    results = []
    for name, lon in [("Dhuma", dhuma), ("Vyatipata", vyatipata),
                      ("Parivesha", parivesha), ("Chapa", chapa),
                      ("Upaketu", upaketu)]:
        nak_idx, nak_name, pada = get_planet_nakshatra_28(lon)
        cell = NAK_TO_POS.get(nak_idx)
        results.append({
            "name": name,
            "longitude": round(lon, 4),
            "nakshatra": nak_name,
            "pada": pada,
            "sign": RASHI_NAMES[int(lon / 30) % 12],
            "row": cell[0] if cell else None,
            "col": cell[1] if cell else None,
        })
    return results


# ═══════════════════════════════════════════════════════════════
# 9. GRAHA LATTA (PLANET KICKS)
# ═══════════════════════════════════════════════════════════════

# Each planet kicks a specific number of nakshatras forward (+) or backward (-)
# from its current nakshatra. The kicked nakshatra suffers harm.
GRAHA_LATTA: Dict[str, int] = {
    "Sun": -12,       # kicks 12th behind (backward)
    "Mars": -3,       # kicks 3rd behind
    "Saturn": -8,     # kicks 8th behind
    "Rahu": -9,       # kicks 9th behind
    "Jupiter": 6,     # kicks 6th ahead (forward)
    "Venus": 7,       # kicks 7th ahead
    "Mercury": 5,     # kicks 5th ahead
    "Moon": 22,       # kicks 22nd ahead
    "Ketu": -9,       # same as Rahu
}

LATTA_HI = {
    "Sun": "सूर्य लत्ता", "Mars": "मंगल लत्ता", "Saturn": "शनि लत्ता",
    "Rahu": "राहु लत्ता", "Jupiter": "गुरु लत्ता", "Venus": "शुक्र लत्ता",
    "Mercury": "बुध लत्ता", "Moon": "चन्द्र लत्ता", "Ketu": "केतु लत्ता",
}


def calc_graha_latta(
    transit_placements: List[Dict],
) -> List[Dict[str, Any]]:
    """
    Calculate graha latta (planet kicks) for transit planets.
    Returns list of latta events with source and kicked nakshatra info.
    """
    results = []
    for tp in transit_placements:
        planet = tp["planet"]
        kick = GRAHA_LATTA.get(planet)
        if kick is None:
            continue

        # Source nakshatra index
        src_nak = None
        for (r, c), idx in NAK_POSITIONS.items():
            if r == tp["row"] and c == tp["col"]:
                src_nak = idx
                break
        if src_nak is None:
            continue

        # Kicked nakshatra
        kicked_idx = (src_nak + kick) % 28
        kicked_name = NAKSHATRAS_28[kicked_idx]
        kicked_cell = NAK_TO_POS.get(kicked_idx)

        direction = "backward" if kick < 0 else "forward"
        results.append({
            "planet": planet,
            "planet_nak": NAKSHATRAS_28[src_nak],
            "kick_count": abs(kick),
            "direction": direction,
            "kicked_nak": kicked_name,
            "kicked_nak_idx": kicked_idx,
            "kicked_row": kicked_cell[0] if kicked_cell else None,
            "kicked_col": kicked_cell[1] if kicked_cell else None,
            "label_hi": LATTA_HI.get(planet, ""),
        })
    return results


# ═══════════════════════════════════════════════════════════════
# 10. NAKSHATRA DRISHTI (FIXED ASPECTS)
# ═══════════════════════════════════════════════════════════════

# In SBC, nakshatra drishti = fixed geometric relationships on the grid.
# Nakshatras that share the same row or column on the border aspect each other.
# Additionally, corner-connected nakshatras aspect diagonally.

def get_nakshatra_drishti(nak_idx_28: int) -> List[int]:
    """
    Get all nakshatras that a given nakshatra aspects in the SBC grid.
    Based on the geometric rule: nakshatras on the same row or column
    of the 9x9 border have drishti on each other.
    """
    cell = NAK_TO_POS.get(nak_idx_28)
    if not cell:
        return []

    row, col = cell
    aspected = []

    # All nakshatras in the same row
    for (r, c), idx in NAK_POSITIONS.items():
        if idx == nak_idx_28:
            continue
        if r == row or c == col:
            aspected.append(idx)

    return aspected


def get_all_natal_drishti(natal_placements: List[Dict]) -> List[Dict]:
    """
    For each natal planet, find which other natal nakshatras it aspects.
    """
    results = []
    for np in natal_placements:
        nak_name = np.get("nakshatra")
        if not nak_name:
            continue
        nak_idx = None
        for i, n in enumerate(NAKSHATRAS_28):
            if n == nak_name:
                nak_idx = i
                break
        if nak_idx is None:
            continue

        aspected = get_nakshatra_drishti(nak_idx)
        if aspected:
            results.append({
                "planet": np["planet"],
                "nakshatra": nak_name,
                "aspects": [NAKSHATRAS_28[a] for a in aspected],
                "aspect_indices": aspected,
            })
    return results


# ═══════════════════════════════════════════════════════════════
# 11. GRAHA BALA (PLANET STRENGTH IN SBC)
# ═══════════════════════════════════════════════════════════════

# Strength factors:
#   +1 for each vedha hit on a beneficial target
#   +1 if planet is in own nakshatra lord's nak
#   +1 if direct motion (not retrograde)
#   -1 for each vedha hit received from a malefic

def calc_graha_bala(
    vedha_lines: List[Dict],
    natal_placements: List[Dict],
    transit_placements: List[Dict],
) -> List[Dict[str, Any]]:
    """
    Calculate graha bala (strength score) for each transit planet in SBC.
    """
    # Count vedha hits given and received
    natal_cells = {}
    for np in natal_placements:
        natal_cells[(np["row"], np["col"])] = np["planet"]

    results = []
    for tp in transit_placements:
        planet = tp["planet"]
        score = 0
        factors = []

        # Direct motion bonus
        if not tp.get("retrograde", False):
            score += 1
            factors.append("Direct motion (+1)")
        else:
            score -= 1
            factors.append("Retrograde (-1)")

        # Speed factor
        avg = PLANET_AVG_SPEED.get(planet, 1.0)
        speed = abs(tp.get("speed", 0))
        if speed > avg * 1.2:
            score += 1
            factors.append("Fast speed (+1)")
        elif speed < avg * 0.5:
            score -= 1
            factors.append("Slow speed (-1)")

        # Count vedha hits on natal planets
        hits_given = 0
        for vl in vedha_lines:
            if vl["planet"] != planet:
                continue
            for t in vl.get("targets", []):
                if (t["row"], t["col"]) in natal_cells:
                    hits_given += 1
        if hits_given > 0:
            nature = classify_planet(planet)
            if nature == "shubh":
                score += hits_given
                factors.append(f"Benefic vedha on {hits_given} natal (+{hits_given})")
            else:
                score -= hits_given
                factors.append(f"Malefic vedha on {hits_given} natal (-{hits_given})")

        results.append({
            "planet": planet,
            "score": score,
            "factors": factors,
            "nature": classify_planet(planet),
        })

    return results


# ═══════════════════════════════════════════════════════════════
# 12. KURMA CHAKRA
# ═══════════════════════════════════════════════════════════════

# Maps nakshatras to body parts and directions of the cosmic turtle (Kurma).
# The turtle faces east; head=east, tail=west, right=south, left=north.

KURMA_BODY_PARTS: Dict[str, Dict[str, str]] = {
    "Ashwini":           {"direction": "E",  "body": "Head (right)"},
    "Bharani":           {"direction": "E",  "body": "Head (left)"},
    "Krittika":          {"direction": "SE", "body": "Right shoulder"},
    "Rohini":            {"direction": "S",  "body": "Right foreleg (upper)"},
    "Mrigashira":        {"direction": "S",  "body": "Right foreleg (lower)"},
    "Ardra":             {"direction": "NE", "body": "Left shoulder"},
    "Punarvasu":         {"direction": "N",  "body": "Left foreleg (upper)"},
    "Pushya":            {"direction": "N",  "body": "Left foreleg (lower)"},
    "Ashlesha":          {"direction": "NW", "body": "Left flank"},
    "Magha":             {"direction": "W",  "body": "Tail (left)"},
    "Purva Phalguni":    {"direction": "W",  "body": "Tail (right)"},
    "Uttara Phalguni":   {"direction": "W",  "body": "Tail (center)"},
    "Hasta":             {"direction": "S",  "body": "Right hind leg (upper)"},
    "Chitra":            {"direction": "S",  "body": "Right hind leg (lower)"},
    "Swati":             {"direction": "SW", "body": "Right flank"},
    "Vishakha":          {"direction": "SE", "body": "Right side"},
    "Anuradha":          {"direction": "SE", "body": "Right hip"},
    "Jyeshtha":          {"direction": "W",  "body": "Tail tip"},
    "Mula":              {"direction": "SW", "body": "Right foot"},
    "Purva Ashadha":     {"direction": "S",  "body": "Right thigh"},
    "Uttara Ashadha":    {"direction": "NW", "body": "Left hip"},
    "Abhijit":           {"direction": "C",  "body": "Heart (center)"},
    "Shravana":          {"direction": "N",  "body": "Left hind leg (upper)"},
    "Dhanishtha":        {"direction": "N",  "body": "Left hind leg (lower)"},
    "Shatabhisha":       {"direction": "NW", "body": "Left foot"},
    "Purva Bhadrapada":  {"direction": "NE", "body": "Left thigh"},
    "Uttara Bhadrapada": {"direction": "NE", "body": "Left side"},
    "Revati":            {"direction": "E",  "body": "Neck"},
}

KURMA_DIRECTIONS = {
    "E": "East (पूर्व)", "W": "West (पश्चिम)",
    "N": "North (उत्तर)", "S": "South (दक्षिण)",
    "NE": "NE (ईशान)", "NW": "NW (वायव्य)",
    "SE": "SE (आग्नेय)", "SW": "SW (नैऋत्य)",
    "C": "Center (मध्य)",
}


def get_kurma_data(natal_placements: List[Dict], transit_placements: List[Dict]) -> Dict:
    """
    Map natal and transit planets onto the Kurma Chakra.
    """
    natal_kurma = []
    for np in natal_placements:
        nak = np.get("nakshatra", "")
        info = KURMA_BODY_PARTS.get(nak, {})
        if info:
            natal_kurma.append({
                "planet": np["planet"],
                "nakshatra": nak,
                "direction": info["direction"],
                "direction_label": KURMA_DIRECTIONS.get(info["direction"], ""),
                "body_part": info["body"],
            })

    transit_kurma = []
    for tp in transit_placements:
        nak = tp.get("nakshatra", "")
        info = KURMA_BODY_PARTS.get(nak, {})
        if info:
            transit_kurma.append({
                "planet": tp["planet"],
                "nakshatra": nak,
                "direction": info["direction"],
                "direction_label": KURMA_DIRECTIONS.get(info["direction"], ""),
                "body_part": info["body"],
            })

    return {"natal": natal_kurma, "transit": transit_kurma}


# ═══════════════════════════════════════════════════════════════
# 13. SBC PRASHNA (HORARY) SUPPORT
# ═══════════════════════════════════════════════════════════════

def get_prashna_analysis(
    transit_weekday: str,
    transit_tithi_group: str,
    transit_moon_nak: str,
    vedha_hits: List[Dict],
) -> Dict[str, Any]:
    """
    Basic SBC Prashna analysis for the query moment.
    Evaluates: weekday lord, tithi nature, Moon nakshatra vedha status.
    """
    vara_lords = {
        "Sun": "Sun", "Mon": "Moon", "Tue": "Mars",
        "Wed": "Mercury", "Thu": "Jupiter", "Fri": "Venus", "Sat": "Saturn",
    }
    tithi_nature = {
        "Nanda": "auspicious", "Bhadra": "auspicious",
        "Jaya": "very auspicious", "Rikta": "inauspicious",
        "Poorna": "auspicious",
    }

    # Check if query Moon nak is being vedha'd
    moon_vedha_by = []
    for hit in vedha_hits:
        if hit.get("natal_target") == "Moon" or hit.get("natal_target") == transit_moon_nak:
            moon_vedha_by.append(hit["transit_planet"])

    vara_lord = vara_lords.get(transit_weekday, "")
    overall = "neutral"
    shubh_count = sum(1 for h in vedha_hits if h.get("nature") == "shubh")
    ashubh_count = sum(1 for h in vedha_hits if h.get("nature") == "ashubh")

    if shubh_count > ashubh_count:
        overall = "favorable"
    elif ashubh_count > shubh_count:
        overall = "unfavorable"

    return {
        "vara_lord": vara_lord,
        "tithi_group": transit_tithi_group,
        "tithi_nature": tithi_nature.get(transit_tithi_group, "neutral"),
        "moon_nakshatra": transit_moon_nak,
        "moon_vedha_by": moon_vedha_by,
        "shubh_hits": shubh_count,
        "ashubh_hits": ashubh_count,
        "overall": overall,
    }
