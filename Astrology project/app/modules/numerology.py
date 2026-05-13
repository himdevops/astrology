"""
numerology module — Advanced Vedic + Western Numerology endpoints.
Life Path, Destiny, Soul Urge, Personality, Loshu Grid, Name Correction,
Mobile/Car/Password analysis, Personal Cycles.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.numerology import calculate_numerology

router = APIRouter(tags=["v3.0 — Numerology"])


# ── schemas ───────────────────────────────────────────────────

class NumerologyInput(BaseModel):
    name: str = Field(..., example="Himanshu",
        description="Full name for name number calculation")
    dob: str = Field(..., example="23-09-1992",
        description="Date of birth (DD-MM-YYYY or YYYY-MM-DD)")
    mobile: Optional[str] = Field(default=None, example="9876543210",
        description="Mobile number for analysis")
    car_number: Optional[str] = Field(default=None, example="MP09AB1234",
        description="Car/Vehicle number for analysis")
    password: Optional[str] = Field(default=None,
        description="Current password for numerological analysis")
    system: str = Field(default="both", example="both",
        description="Numerology system: 'pythagorean', 'chaldean', or 'both'")


# ── endpoint ─────────────────────────────────────────────────

@router.post("/numerology", summary="Advanced Numerology — Vedic + Western + Loshu Grid")
def numerology(payload: NumerologyInput):
    """
    Complete numerology analysis including:

    - **Core Numbers**: Life Path, Birthday, Destiny/Expression, Soul Urge, Personality, Maturity
    - **Loshu Grid**: Lo Shu magic square with planes, arrows, missing number remedies
    - **Name Correction**: Compatibility check + spelling suggestions
    - **Mobile Number**: Analysis & correction tips
    - **Car Number**: Numerological analysis
    - **Password**: Numerological suggestions for strong passwords
    - **Characteristics**: Full personality, behavior, career, health, lucky items
    - **Personal Year Cycle**: Current year energy
    """
    try:
        result = calculate_numerology(
            name=payload.name,
            dob=payload.dob,
            mobile=payload.mobile,
            car_number=payload.car_number,
            password=payload.password,
            system=payload.system,
        )

        return {
            "type": "numerology",
            **result,
        }
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"{exc}\n{tb}") from exc
