"""
tarot module — Tarot Card Reading endpoints.
Draw 1-5 cards, auto-analyze combinations.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.tarot import draw_tarot

router = APIRouter(tags=["v3.0 — Tarot"])


class TarotInput(BaseModel):
    num_cards: int = Field(default=3, ge=1, le=5,
        description="Number of cards to draw (1-5)")
    question: Optional[str] = Field(default=None,
        description="Optional question for the reading")


@router.post("/tarot", summary="Tarot Card Reading — Draw 1-5 Cards")
def tarot(payload: TarotInput):
    """
    Draw random Tarot cards from the full 78-card deck.
    Each card drawn upright or reversed (30% reversal chance).
    Automatic combination analysis for multi-card spreads.
    """
    try:
        result = draw_tarot(
            num_cards=payload.num_cards,
            question=payload.question,
        )
        return {"type": "tarot_reading", **result}
    except Exception as exc:
        import traceback
        raise HTTPException(status_code=400, detail=f"{exc}\n{traceback.format_exc()}") from exc
