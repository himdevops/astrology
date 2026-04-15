from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.chart_service import calculate_birth_chart, calculate_transits
from app.schemas import BirthInput, TransitInput

app = FastAPI(
    title="Financial Astrology Engine",
    version="1.1.0",
    description="FastAPI backend for Vedic astrology charts with automatic place, coordinates, and timezone detection.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ui_dir = Path(__file__).resolve().parent.parent / "financial_astrology_ui"
if ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=ui_dir, html=True), name="ui")


@app.get("/")
def home() -> dict:
    return {
        "message": "Financial Astrology Engine is running",
        "docs": "/docs",
        "ui": "/ui",
        "endpoints": ["/chart", "/transits"],
    }


@app.post("/chart")
def chart(payload: BirthInput) -> dict:
    try:
        return calculate_birth_chart(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/transits")
def transits(payload: TransitInput) -> dict:
    try:
        return calculate_transits(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
