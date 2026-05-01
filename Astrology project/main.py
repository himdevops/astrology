"""
main.py — Financial Astrology Engine v3.0
Slim entry point.  All features live in app/modules/ and are
auto-discovered by app.loader.  To add a new feature just drop a
Python file with a ``router`` into app/modules/.
"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.loader import discover_and_load

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

app = FastAPI(
    title="Financial Astrology Engine v3.0",
    version="3.0.0",
    description=(
        "Advanced Vedic Astrology API for NSE/BSE Financial Predictions.  "
        "Features are auto-discovered from app/modules/ — each module is "
        "isolated so one broken module cannot crash the rest of the engine."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auto-discover feature modules ──────────────────────────────
load_result = discover_and_load(app)

# ── Serve UI ───────────────────────────────────────────────────
ui_dir = Path(__file__).resolve().parent / "financial_astrology_ui"
if ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=ui_dir, html=True), name="ui")


# ── Health / root ──────────────────────────────────────────────
@app.get("/", tags=["Health"])
def home() -> dict:
    return {
        "message": "Financial Astrology Engine v3.0 is running",
        "market": "NSE/BSE India",
        "ui": "/ui",
        "docs": "/docs",
        "modules": load_result,
    }
