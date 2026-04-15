"""
himanshu_sarvatobhdra.py  —  Traditional Sarvatobhadra Chakra Grid Engine
9×9 grid with correct traditional placement:
  Ring 1 (outer perimeter): 28 Nakshatras (27 + Abhijit) + 4 directional corners
  Ring 2 (7×7 perimeter)  : 12 Rashis (2 cells each)
  Ring 3 (5×5 perimeter)  : 30 Tithis (16 cells, spaced)
  Ring 4 (3×3 perimeter)  : 7 Varas (weekdays)
  Center (1 cell)         : Special anchor
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
# Second ring (7×7 perimeter) → Rashis
# Clockwise from (1,1), 2 cells per rashi
# ─────────────────────────────────────────────────────────────
def _second_ring_clockwise() -> List[Tuple[int,int]]:
    """Return (row,col) list of 7×7 perimeter in clockwise order."""
    cells = []
    # top: (1,1)→(1,7)
    for c in range(1, 8): cells.append((1, c))
    # right: (2,7)→(7,7)
    for r in range(2, 8): cells.append((r, 7))
    # bottom: (7,6)→(7,1)
    for c in range(6, 0, -1): cells.append((7, c))
    # left: (6,1)→(2,1)
    for r in range(6, 1, -1): cells.append((r, 1))
    return cells  # 24 cells total

# Assign rashis: 2 cells each × 12 = 24 cells exactly
_SECOND_RING = _second_ring_clockwise()
RASHI_CELL_MAP: Dict[Tuple[int,int], str] = {}
for _i, _rashi in enumerate(RASHIS_12):
    RASHI_CELL_MAP[_SECOND_RING[_i * 2]]     = _rashi
    RASHI_CELL_MAP[_SECOND_RING[_i * 2 + 1]] = _rashi

# ─────────────────────────────────────────────────────────────
# Third ring (5×5 perimeter) → Tithis (16 cells, 15 tithis + Purnima/Amavasya)
# ─────────────────────────────────────────────────────────────
def _third_ring_clockwise() -> List[Tuple[int,int]]:
    cells = []
    for c in range(2, 7): cells.append((2, c))
    for r in range(3, 7): cells.append((r, 6))
    for c in range(5, 1, -1): cells.append((6, c))
    for r in range(5, 2, -1): cells.append((r, 2))
    return cells  # 16 cells

_THIRD_RING = _third_ring_clockwise()
TITHI_CELL_MAP: Dict[Tuple[int,int], str] = {}
_SELECTED_TITHIS = [TITHIS_30[i] for i in [0,2,4,6,8,10,12,14,15,17,19,21,23,25,27,29]]
for _i, _cell in enumerate(_THIRD_RING):
    TITHI_CELL_MAP[_cell] = _SELECTED_TITHIS[_i % len(_SELECTED_TITHIS)]

# ─────────────────────────────────────────────────────────────
# Fourth ring (3×3 perimeter) → Varas (8 cells, 7 days + 1 repeat)
# ─────────────────────────────────────────────────────────────
def _fourth_ring_clockwise() -> List[Tuple[int,int]]:
    cells = []
    for c in range(3, 6): cells.append((3, c))
    cells.append((4, 5)); cells.append((5, 5))
    for c in range(4, 2, -1): cells.append((5, c))  # (5,4),(5,3)
    cells.append((4, 3))
    return cells  # 8 cells

_FOURTH_RING = _fourth_ring_clockwise()
VARA_CELL_MAP: Dict[Tuple[int,int], str] = {}
for _i, _cell in enumerate(_FOURTH_RING):
    VARA_CELL_MAP[_cell] = WEEKDAYS[_i % 7]

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
        self._place_tithis()
        self._place_varas()
        self._place_center()

    def _register_entity(self, row: int, col: int, entity: ChakraEntity) -> None:
        self.grid[row][col].add_entity(entity)
        key = (entity.entity_type, entity.name.lower())
        self.entity_index[key] = (row, col)

    def _place_nakshatras(self) -> None:
        for (r, c), name in OUTER_NAK_POSITIONS.items():
            entity = ChakraEntity(name=name, entity_type=EntityType.NAKSHATRA,
                                  meta={"direction": _cell_direction(r, c)})
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
        for (r, c), name in RASHI_CELL_MAP.items():
            entity = ChakraEntity(name=name, entity_type=EntityType.RASHI,
                                  meta={"rashi_index": RASHIS_12.index(name) + 1})
            self._register_entity(r, c, entity)
            if not self.grid[r][c].label:
                self.grid[r][c].label = name

    def _place_tithis(self) -> None:
        for (r, c), name in TITHI_CELL_MAP.items():
            entity = ChakraEntity(name=name, entity_type=EntityType.TITHI, meta={})
            self._register_entity(r, c, entity)
            if not self.grid[r][c].label:
                self.grid[r][c].label = name[:12]

    def _place_varas(self) -> None:
        for (r, c), name in VARA_CELL_MAP.items():
            entity = ChakraEntity(name=name, entity_type=EntityType.VARA, meta={})
            self._register_entity(r, c, entity)
            if not self.grid[r][c].label:
                self.grid[r][c].label = name

    def _place_center(self) -> None:
        r, c = CENTER_CELL
        entity = ChakraEntity(name="Brahma (Center)", entity_type=EntityType.SPECIAL,
                               meta={"description": "Central Brahma cell — most powerful position"})
        self._register_entity(r, c, entity)
        self.grid[r][c].label = "✦ Center"

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
