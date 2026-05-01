"""
himanshu_sarvatobhdra.py  —  Traditional Sarvatobhadra Chakra Grid Engine
9×9 grid with correct traditional placement (per Shyam S Kansal / Khemraj):
  Ring 1 (outer perimeter): 28 Nakshatras (27 + Abhijit) + 4 directional corners
  Ring 2 (7×7 perimeter)  : 20 Consonant aksharas + 4 diagonal svaras
  Ring 3 (5×5 perimeter)  : 12 Rashis (1 per rashi) + 4 diagonal svaras
  Ring 4 (3×3 perimeter)  : 5 Vara cells (weekdays grouped by tithi type)
  Center (1 cell)         : Brahma / Saturday / Poorna
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import json


# ─────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────

class EntityType(str, Enum):
    NAKSHATRA = "nakshatra"
    RASHI     = "rashi"
    TITHI     = "tithi"
    VARA      = "vara"
    AKSHARA   = "akshara"
    CORNER    = "corner"
    EMPTY     = "empty"
    SPECIAL   = "special"


# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

TITHIS_30 = [
    "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi",
    "Shukla Panchami",  "Shukla Shashthi", "Shukla Saptami",  "Shukla Ashtami",
    "Shukla Navami",    "Shukla Dashami",  "Shukla Ekadashi", "Shukla Dwadashi",
    "Shukla Trayodashi","Shukla Chaturdashi","Purnima",
    "Krishna Pratipada","Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi",
    "Krishna Panchami", "Krishna Shashthi","Krishna Saptami", "Krishna Ashtami",
    "Krishna Navami",   "Krishna Dashami", "Krishna Ekadashi","Krishna Dwadashi",
    "Krishna Trayodashi","Krishna Chaturdashi","Amavasya",
]

RASHIS_12 = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

RASHI_HINDI: Dict[str, str] = {
    "Aries": "मेष", "Taurus": "वृष", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन",
}

# 28 Nakshatras for SBC (includes Abhijit between Uttara Ashadha & Shravana)
NAKSHATRAS_28 = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
    "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
    "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
    "Uttara Ashadha","Abhijit","Shravana","Dhanishtha","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati",
]

AKSHARAS_16 = ["A","Ka","Cha","Ta","Tha","Pa","Ya","Sha","Ra","La","Va","Sa","Ha","Ksha","Tra","Gya"]

# ─────────────────────────────────────────────────────────────
# Nakshatra Pada Sounds (syllables for each pada 1-4)
# Traditional syllables used in naming; per Shyam S Kansal reference
# ─────────────────────────────────────────────────────────────
NAKSHATRA_PADA_SOUNDS: Dict[str, List[str]] = {
    "Ashwini":            ["Chu", "Che", "Cho", "La"],
    "Bharani":            ["Li",  "Lu",  "Le",  "Lo"],
    "Krittika":           ["Aa",  "Ei",  "Ou",  "Ae"],
    "Rohini":             ["O",   "Va",  "Vi",  "Vu"],
    "Mrigashira":         ["Ve",  "Vo",  "Ka",  "Ki"],
    "Ardra":              ["Ku",  "Gha", "Ng",  "Chha"],
    "Punarvasu":          ["Ke",  "Ko",  "Ha",  "Hi"],
    "Pushya":             ["Hu",  "He",  "Ho",  "Da"],
    "Ashlesha":           ["Di",  "Du",  "De",  "Do"],
    "Magha":              ["Ma",  "Mi",  "Mu",  "Me"],
    "Purva Phalguni":     ["Mo",  "Ta",  "Ti",  "Tu"],
    "Uttara Phalguni":    ["Te",  "To",  "Pa",  "Pi"],
    "Hasta":              ["Pu",  "Sha", "Na",  "Tha"],
    "Chitra":             ["Pe",  "Po",  "Ra",  "Ri"],
    "Swati":              ["Ru",  "Re",  "Ro",  "Ta"],
    "Vishakha":           ["Ti",  "Tu",  "Te",  "To"],
    "Anuradha":           ["Na",  "Ni",  "Nu",  "Ne"],
    "Jyeshtha":           ["No",  "Ya",  "Yi",  "Yu"],
    "Mula":               ["Ye",  "Yo",  "Bha", "Bhi"],
    "Purva Ashadha":      ["Bhu", "Dha", "Pha", "Dha"],
    "Uttara Ashadha":     ["Bhe", "Bho", "Ja",  "Ji"],
    "Abhijit":            ["Ju",  "Je",  "Jo",  "Gha"],
    "Shravana":           ["Khi", "Khu", "Khe", "Kho"],
    "Dhanishtha":         ["Ga",  "Gi",  "Gu",  "Ge"],
    "Shatabhisha":        ["Go",  "Sa",  "Si",  "Su"],
    "Purva Bhadrapada":   ["Se",  "So",  "Da",  "Di"],
    "Uttara Bhadrapada":  ["Du",  "Tha", "Jha", "Da"],
    "Revati":             ["De",  "Tho", "Cha", "Chi"],
}

# ─────────────────────────────────────────────────────────────
# 16 Svaras (vowels) at diagonal corner positions (Shloka 5)
# "अकारादि १६ स्वर ईशानादि चारों कोण दिशाओं के कोठों में"
# Each diagonal has 4 vowels from outer corner inward to center.
# ─────────────────────────────────────────────────────────────
SVARAS_16 = ['अ','आ','इ','ई','उ','ऊ','ऋ','ॠ','ऌ','ॡ','ए','ऐ','ओ','औ','अं','अः']

SVARA_POSITIONS: Dict[Tuple[int,int], str] = {
    # ईशान (NE) diagonal — (0,0)→(1,1)→(2,2)→(3,3)
    (0,0): 'अ',  (1,1): 'उ',  (2,2): 'ऌ',  (3,3): 'ओ',
    # अग्नि (SE) diagonal — (0,8)→(1,7)→(2,6)→(3,5)
    (0,8): 'आ',  (1,7): 'ऊ',  (2,6): 'ॡ',  (3,5): 'औ',
    # नैऋत्य (SW) diagonal — (8,8)→(7,7)→(6,6)→(5,5)
    (8,8): 'इ',  (7,7): 'ऋ',  (6,6): 'ए',  (5,5): 'अं',
    # वायव्य (NW) diagonal — (8,0)→(7,1)→(6,2)→(5,3)
    (8,0): 'ई',  (7,1): 'ॠ',  (6,2): 'ऐ',  (5,3): 'अः',
}

# ─────────────────────────────────────────────────────────────
# 20 Consonant aksharas on the second ring (Shloka 7)
# "अवकहड ये ५ पूर्व में; मटपरत ये ५ दक्षिण में;
#  नयभजख ये ५ पश्चिम में; गसदचल ये ५ उत्तर में"
# These replace rashi name labels at non-diagonal second-ring cells.
# ─────────────────────────────────────────────────────────────
CONSONANT_POSITIONS: Dict[Tuple[int,int], str] = {
    # पूर्व / East (top row, second ring non-corner cells)
    (1,2): 'अ',  (1,3): 'व',  (1,4): 'क',  (1,5): 'ह',  (1,6): 'ड',
    # दक्षिण / South-Dakshin (right col, second ring non-corner cells)
    (2,7): 'म',  (3,7): 'ट',  (4,7): 'प',  (5,7): 'र',  (6,7): 'त',
    # पश्चिम / West (bottom row, second ring non-corner cells)
    (7,6): 'न',  (7,5): 'य',  (7,4): 'भ',  (7,3): 'ज',  (7,2): 'ख',
    # उत्तर / North (left col, second ring non-corner cells)
    (6,1): 'ग',  (5,1): 'स',  (4,1): 'द',  (3,1): 'च',  (2,1): 'ल',
}

# ─────────────────────────────────────────────────────────────
# Traditional outer-ring nakshatra positions (row, col) → name
# East=top, North=right, West=bottom, South=left  (Indian compass)
# ─────────────────────────────────────────────────────────────
OUTER_NAK_POSITIONS: Dict[Tuple[int,int], str] = {
    # EAST — top row, cols 1→7
    (0,1):"Krittika",    (0,2):"Rohini",       (0,3):"Mrigashira",
    (0,4):"Ardra",       (0,5):"Punarvasu",     (0,6):"Pushya",
    (0,7):"Ashlesha",
    # NORTH — right col, rows 1→7
    (1,8):"Magha",       (2,8):"Purva Phalguni",(3,8):"Uttara Phalguni",
    (4,8):"Hasta",       (5,8):"Chitra",        (6,8):"Swati",
    (7,8):"Vishakha",
    # WEST — bottom row, cols 7→1
    (8,7):"Anuradha",    (8,6):"Jyeshtha",      (8,5):"Mula",
    (8,4):"Purva Ashadha",(8,3):"Uttara Ashadha",(8,2):"Abhijit",
    (8,1):"Shravana",
    # SOUTH — left col, rows 7→1
    (7,0):"Dhanishtha",  (6,0):"Shatabhisha",   (5,0):"Purva Bhadrapada",
    (4,0):"Uttara Bhadrapada",(3,0):"Revati",   (2,0):"Ashwini",
    (1,0):"Bharani",
}

CORNER_POSITIONS: Dict[Tuple[int,int], str] = {
    (0,0):"NE", (0,8):"SE", (8,8):"SW", (8,0):"NW",
}

# Zone string for each ring
ZONE_MAP: Dict[str, str] = {
    "outer":"outer", "second":"second", "third":"third",
    "fourth":"fourth", "center":"center",
}

# ─────────────────────────────────────────────────────────────
# Second ring (7×7 perimeter) — aksharas only (consonants + svaras)
# Rashis are NOT placed here; the second ring has 20 consonants
# at non-diagonal positions + 4 svaras at diagonal positions.
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# Third ring (5×5 perimeter) → 12 Rashis at non-diagonal positions
# Per Shyam S Kansal / Khemraj reference:
#   East  (top):   Tau(2,3), Gem(2,4), Can(2,5)
#   South (right): Leo(3,6), Vir(4,6), Lib(5,6)
#   West  (bottom): Sco(6,5), Sag(6,4), Cap(6,3)
#   North (left):  Aqu(5,2), Pis(4,2), Ari(3,2)
# The 4 diagonal corners of 3rd ring (2,2), (2,6), (6,6), (6,2)
# have svaras (ऌ, ॡ, ए, ऐ) — placed by _place_svaras().
# ─────────────────────────────────────────────────────────────
RASHI_CELL_MAP: Dict[Tuple[int,int], str] = {
    # East / top of 3rd ring
    (2,3): "Taurus",    (2,4): "Gemini",     (2,5): "Cancer",
    # South / right of 3rd ring
    (3,6): "Leo",       (4,6): "Virgo",      (5,6): "Libra",
    # West / bottom of 3rd ring
    (6,5): "Scorpio",   (6,4): "Sagittarius",(6,3): "Capricorn",
    # North / left of 3rd ring
    (5,2): "Aquarius",  (4,2): "Pisces",     (3,2): "Aries",
}

# ─────────────────────────────────────────────────────────────
# Fourth ring → Varas grouped by Tithi type (Shlokas 9-10)
# "भौमादित्यौ च नन्दायां भद्रायां बुधशीतगु ।
#  जयायां च गुरुःप्रोक्तो रिक्तायां भार्गवस्तथा ।
#  पूर्णायां शनिवारश्च ।"
# Each tithi group → direction → weekday(s):
#   Nanda (1,6,11) → East  → Sun, Tue
#   Bhadra (2,7,12) → Dakshin → Mon, Wed
#   Jaya (3,8,13) → West  → Thu
#   Rikta (4,9,14) → North → Fri
#   Poorna (5,10,15/30) → Center → Sat
# Corner cells of 3×3 ring have svaras (placed later by _place_svaras).
# ─────────────────────────────────────────────────────────────
VARA_CELL_MAP: Dict[Tuple[int,int], List[str]] = {
    (3,4): ["Sunday", "Tuesday"],       # Nanda   → East  (पूर्व)
    (4,5): ["Monday", "Wednesday"],     # Bhadra  → Dakshin (दक्षिण)
    (5,4): ["Thursday"],                # Jaya    → West  (पश्चिम)
    (4,3): ["Friday"],                  # Rikta   → North (उत्तर)
    (4,4): ["Saturday"],                # Poorna  → Center (मध्य)
}

# Tithi group name + tithi numbers for each vara cell
VARA_TITHI_GROUP: Dict[Tuple[int,int], Dict[str, str]] = {
    (3,4): {"name": "Nanda",  "tithis": "1,6,11"},
    (4,5): {"name": "Bhadra", "tithis": "2,7,12"},
    (5,4): {"name": "Jaya",   "tithis": "3,8,13"},
    (4,3): {"name": "Rikta",  "tithis": "4,9,14"},
    (4,4): {"name": "Poorna", "tithis": "5,10,15/30"},
}

CENTER_CELL = (4, 4)


# ─────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────

@dataclass
class ChakraEntity:
    name:        str
    entity_type: EntityType
    meta:        Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "entity_type": self.entity_type.value, "meta": self.meta}


@dataclass
class ChakraCell:
    row:      int
    col:      int
    label:    str               = ""
    entities: List[ChakraEntity] = field(default_factory=list)
    zone:     str               = "inner"

    def add_entity(self, entity: ChakraEntity) -> None:
        self.entities.append(entity)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row": self.row, "col": self.col, "label": self.label,
            "zone": self.zone,
            "entities": [e.to_dict() for e in self.entities],
        }


@dataclass
class TransitPoint:
    planet:      str
    target_name: str
    target_type: EntityType
    relation:    str
    strength:    str            = "normal"
    notes:       Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"planet": self.planet, "target_name": self.target_name,
                "target_type": self.target_type.value, "relation": self.relation,
                "strength": self.strength, "notes": self.notes}


@dataclass
class VedhaResult:
    source:          ChakraEntity
    source_position: Tuple[int, int]
    impacted:        List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"source": self.source.to_dict(),
                "source_position": self.source_position, "impacted": self.impacted}


# ─────────────────────────────────────────────────────────────
# Grid Engine
# ─────────────────────────────────────────────────────────────

class SarvatobhadraChakra:
    """Traditional 9×9 Sarvatobhadra Chakra with correct placement."""

    GRID_SIZE = 9

    def __init__(self) -> None:
        self.grid: List[List[ChakraCell]] = [
            [ChakraCell(row=r, col=c) for c in range(self.GRID_SIZE)]
            for r in range(self.GRID_SIZE)
        ]
        self.entity_index: Dict[Tuple[EntityType, str], Tuple[int, int]] = {}
        self._assign_zones()
        self._populate_traditional_layout()

    # ── Zone assignment ──────────────────────────────────────

    def _assign_zones(self) -> None:
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                dist = min(r, c, self.GRID_SIZE-1-r, self.GRID_SIZE-1-c)
                self.grid[r][c].zone = (
                    "outer"  if dist == 0 else
                    "second" if dist == 1 else
                    "third"  if dist == 2 else
                    "fourth" if dist == 3 else
                    "center"
                )

    # ── Traditional placement ────────────────────────────────

    def _populate_traditional_layout(self) -> None:
        self._place_nakshatras()
        self._place_corners()
        self._place_rashis()
        self._place_varas()
        self._place_center()
        self._place_svaras()  # Last: vowels override labels at diagonal positions

    def _register_entity(self, row: int, col: int, entity: ChakraEntity) -> None:
        self.grid[row][col].add_entity(entity)
        key = (entity.entity_type, entity.name.lower())
        self.entity_index[key] = (row, col)

    def _place_nakshatras(self) -> None:
        for (r, c), name in OUTER_NAK_POSITIONS.items():
            pada_sounds = NAKSHATRA_PADA_SOUNDS.get(name, [])
            entity = ChakraEntity(name=name, entity_type=EntityType.NAKSHATRA,
                                  meta={"direction": _cell_direction(r, c),
                                        "pada_sounds": pada_sounds})
            self._register_entity(r, c, entity)
            self.grid[r][c].label = name

    def _place_corners(self) -> None:
        dir_map = {"NE": "East-South junction", "SE": "East-North junction",
                   "SW": "West-North junction", "NW": "West-South junction"}
        for (r, c), label in CORNER_POSITIONS.items():
            entity = ChakraEntity(name=label, entity_type=EntityType.CORNER,
                                  meta={"description": dir_map.get(label, "")})
            self._register_entity(r, c, entity)
            self.grid[r][c].label = label

    def _place_rashis(self) -> None:
        """Place 12 rashis in the 3rd ring (5×5 perimeter, non-diagonal cells)."""
        for (r, c), name in RASHI_CELL_MAP.items():
            hindi = RASHI_HINDI.get(name, "")
            entity = ChakraEntity(name=name, entity_type=EntityType.RASHI,
                                  meta={"rashi_index": RASHIS_12.index(name) + 1,
                                        "hindi": hindi})
            self._register_entity(r, c, entity)
            self.grid[r][c].label = name

    def _place_varas(self) -> None:
        for (r, c), days in VARA_CELL_MAP.items():
            tithi_info = VARA_TITHI_GROUP.get((r, c), {})
            for day in days:
                entity = ChakraEntity(name=day, entity_type=EntityType.VARA,
                                      meta={"tithi_group": tithi_info.get("name", ""),
                                            "tithi_numbers": tithi_info.get("tithis", "")})
                self._register_entity(r, c, entity)
            # Label: "Sun,Tue" or single day
            day_abbrs = ",".join(d[:3] for d in days)
            group_name = tithi_info.get("name", "")
            group_tithis = tithi_info.get("tithis", "")
            self.grid[r][c].label = day_abbrs
            # Store tithi group info in cell meta for frontend
            self.grid[r][c].entities[-1].meta["display_label"] = day_abbrs
            self.grid[r][c].entities[-1].meta["group_label"] = f"{group_name} {group_tithis}"

    def _place_center(self) -> None:
        r, c = CENTER_CELL
        entity = ChakraEntity(name="Brahma", entity_type=EntityType.SPECIAL,
                               meta={"description": "Central Brahma cell — Poorna → Saturday"})
        self._register_entity(r, c, entity)
        self.grid[r][c].label = "Sat"

    def _place_svaras(self) -> None:
        """Place 16 svaras (vowels) at diagonal positions AND
        20 consonant aksharas at non-diagonal second-ring positions.
        These override the display label but preserve underlying entities."""
        # 1) 16 svaras at diagonal corners
        for (r, c), svara in SVARA_POSITIONS.items():
            entity = ChakraEntity(name=svara, entity_type=EntityType.AKSHARA,
                                  meta={"svara": True, "diagonal": True})
            self.grid[r][c].entities.insert(0, entity)
            key = (EntityType.AKSHARA, svara)
            self.entity_index[key] = (r, c)
            self.grid[r][c].label = svara
        # 2) 20 consonant aksharas on second ring (replaces rashi name labels)
        for (r, c), akshara in CONSONANT_POSITIONS.items():
            entity = ChakraEntity(name=akshara, entity_type=EntityType.AKSHARA,
                                  meta={"svara": False, "consonant": True})
            self.grid[r][c].entities.insert(0, entity)
            key = (EntityType.AKSHARA, akshara + f"_{r}_{c}")
            self.entity_index[key] = (r, c)
            self.grid[r][c].label = akshara

    # ── Lookup helpers ───────────────────────────────────────

    def get_cell(self, row: int, col: int) -> ChakraCell:
        return self.grid[row][col]

    def find_entity(self, entity_type: EntityType, name: str) -> Optional[Tuple[int, int]]:
        return self.entity_index.get((entity_type, name.lower()))

    def get_entity_details(self, entity_type: EntityType, name: str) -> Optional[Dict[str, Any]]:
        pos = self.find_entity(entity_type, name)
        if not pos:
            return None
        r, c = pos
        cell = self.grid[r][c]
        return {"position": {"row": r, "col": c}, "zone": cell.zone,
                "entities": [e.to_dict() for e in cell.entities]}

    # ── Vedha logic ──────────────────────────────────────────

    def get_cross_vedha_positions(self, row: int, col: int) -> List[Tuple[int, int]]:
        return ([(row, c) for c in range(self.GRID_SIZE) if c != col] +
                [(r, col) for r in range(self.GRID_SIZE) if r != row])

    def get_diagonal_vedha_positions(self, row: int, col: int) -> List[Tuple[int, int]]:
        positions = []
        r, c = row - min(row, col), col - min(row, col)
        while r < self.GRID_SIZE and c < self.GRID_SIZE:
            if (r, c) != (row, col): positions.append((r, c))
            r += 1; c += 1
        r = row + min(self.GRID_SIZE-1-row, self.GRID_SIZE-1-col) - min(self.GRID_SIZE-1-row, self.GRID_SIZE-1-col)
        c = col + min(self.GRID_SIZE-1-row, self.GRID_SIZE-1-col)
        # anti-diagonal
        r, c = row, col
        while r > 0 and c < self.GRID_SIZE - 1: r -= 1; c += 1
        while r < self.GRID_SIZE and c >= 0:
            if (r, c) != (row, col): positions.append((r, c))
            r += 1; c -= 1
            if c < 0: break
        return positions

    def compute_vedha_for_entity(self, entity_type: EntityType, name: str,
                                  include_cross: bool = True,
                                  include_diagonal: bool = True) -> Optional[VedhaResult]:
        pos = self.find_entity(entity_type, name)
        if not pos: return None
        row, col = pos
        source_entity = next((e for e in self.grid[row][col].entities
                               if e.entity_type == entity_type and e.name.lower() == name.lower()), None)
        if not source_entity: return None

        impact_positions = set()
        if include_cross:    impact_positions.update(self.get_cross_vedha_positions(row, col))
        if include_diagonal: impact_positions.update(self.get_diagonal_vedha_positions(row, col))

        impacted = []
        for r, c in sorted(impact_positions):
            cell = self.grid[r][c]
            if cell.entities:
                impacted.append({"position": {"row": r, "col": c}, "zone": cell.zone,
                                  "entities": [e.to_dict() for e in cell.entities]})
        return VedhaResult(source=source_entity, source_position=(row, col), impacted=impacted)

    # ── Transit engine ───────────────────────────────────────

    def evaluate_transits(self, planet_transits: List[Dict[str, str]],
                           natal_targets: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        hits: List[TransitPoint] = []
        vedha_reports: List[Dict[str, Any]] = []

        for transit in planet_transits:
            planet = transit["planet"]
            for key, value in transit.items():
                if key == "planet": continue
                entity_type = self._key_to_entity_type(key)
                if not entity_type: continue
                details = self.get_entity_details(entity_type, value)
                if not details: continue
                hits.append(TransitPoint(planet=planet, target_name=value,
                                          target_type=entity_type, relation="direct_transit",
                                          strength="primary",
                                          notes=f"{planet} placed on {value}"))
                vedha = self.compute_vedha_for_entity(entity_type, value)
                if vedha: vedha_reports.append({"planet": planet, "vedha": vedha.to_dict()})
                if natal_targets:
                    if value in natal_targets.get(key.lower(), []):
                        hits.append(TransitPoint(planet=planet, target_name=value,
                                                  target_type=entity_type, relation="natal_direct_hit",
                                                  strength="high",
                                                  notes=f"{planet} hits natal target {value}"))
        return {"hits": [h.to_dict() for h in hits], "vedha_reports": vedha_reports}

    def _key_to_entity_type(self, key: str) -> Optional[EntityType]:
        return {"nakshatra": EntityType.NAKSHATRA, "rashi": EntityType.RASHI,
                "tithi": EntityType.TITHI, "vara": EntityType.VARA,
                "weekday": EntityType.VARA, "akshara": EntityType.AKSHARA}.get(key.lower())

    # ── Text display ─────────────────────────────────────────

    def grid_as_text(self, show_all_entities: bool = False) -> str:
        lines = []
        for r in range(self.GRID_SIZE):
            row_parts = []
            for c in range(self.GRID_SIZE):
                cell = self.grid[r][c]
                text = cell.label[:10] if cell.label and cell.label != "·" else (
                    cell.entities[0].name[:10] if cell.entities else "·")
                row_parts.append(f"{text:^12}")
            lines.append(" | ".join(row_parts))
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {"grid_size": self.GRID_SIZE,
                "cells": [self.grid[r][c].to_dict()
                          for r in range(self.GRID_SIZE)
                          for c in range(self.GRID_SIZE)]}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ─────────────────────────────────────────────────────────────
# Interpretation
# ─────────────────────────────────────────────────────────────

class SarvatobhadraInterpreter:
    MALEFICS = {"Saturn","Mars","Rahu","Ketu","Sun"}
    BENEFICS = {"Jupiter","Venus","Mercury","Moon"}

    def interpret_transit_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        summary = []
        severity = "neutral"
        for hit in report.get("hits", []):
            planet, target_type, target_name, relation = (
                hit["planet"], hit["target_type"], hit["target_name"], hit["relation"])
            tone = ("challenging" if planet in self.MALEFICS else
                    "supportive"  if planet in self.BENEFICS else "mixed")
            summary.append(f"{planet} gives a {tone} influence on {target_type} {target_name} via {relation}.")
        if any(h["planet"] in self.MALEFICS for h in report.get("hits", [])):
            severity = "elevated"
        if any(h["planet"] in self.BENEFICS for h in report.get("hits", [])):
            severity = "mixed_positive" if severity == "elevated" else "positive"
        return {"severity": severity, "summary": summary}


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _cell_direction(row: int, col: int) -> str:
    if row == 0: return "East"
    if col == 8: return "North"
    if row == 8: return "West"
    if col == 0: return "South"
    return ""


# ─────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sbc = SarvatobhadraChakra()
    print("=== SARVATOBHADRA CHAKRA ===")
    print(sbc.grid_as_text())
    print("\n=== OUTER RING NAKSHATRAS ===")
    for (r,c), name in OUTER_NAK_POSITIONS.items():
        print(f"  ({r},{c}) {name}")
