"""
main.py — Vedic Astrology Engine (FastAPI)
==========================================
Auto-registers all v1 API routers. Serves static files + UI.

Architecture:
  core/     → Low-level calculations (ephemeris, nakshatra, panchang, geo)
  modules/  → Independent event modules (positions, retrograde, transit, etc.)
  api/v1/   → Versioned REST endpoints (one router per module)
  main.py   → This file — glues everything together

To add a new feature:
  1. Create modules/new_feature.py  (imports only from core/)
  2. Create api/v1/new_feature.py   (imports from modules/ + api/schemas)
  3. Router auto-registers via the loop below
"""
from __future__ import annotations

import os
import sys

# Add project root to path so `core`, `modules`, `api` are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Import all v1 routers
from api.v1 import (
    panchang, positions, retrograde, transit,
    combustion, aspects, lunar, parallels,
    ecliptic, graha_yuddha, combined, city, kundali,
    birth_defaults, dasha, ashtakavarga, special_lagnas,
    nakshatra, hora, sbc, market, ashtakavarga_advanced, bhrigu,
)


app = FastAPI(
    title="Vedic Astrology Engine",
    description=(
        "Professional Vedic Astrology API with modular architecture. "
        "9 astrological event modules + Panchang + Planetary Positions. "
        "All endpoints versioned under /api/v1/."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register all v1 routers ────────────────────────────────
V1_ROUTERS = [
    panchang.router,
    positions.router,
    retrograde.router,
    transit.router,
    combustion.router,
    aspects.router,
    lunar.router,
    parallels.router,
    ecliptic.router,
    graha_yuddha.router,
    combined.router,
    city.router,
    kundali.router,
    birth_defaults.router,
    dasha.router,
    ashtakavarga.router,
    special_lagnas.router,
    nakshatra.router,
    hora.router,
    sbc.router,
    market.router,
    ashtakavarga_advanced.router,
    bhrigu.router,
]

for router in V1_ROUTERS:
    app.include_router(router)

# ─── Static files ───────────────────────────────────────────
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ─── Root → serve UI ────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(
        "<h1>Vedic Astrology Engine</h1>"
        "<p>UI not found. Visit <a href='/docs'>/docs</a> for API documentation.</p>"
    )


# ─── Kundali page ──────────────────────────────────────────
@app.get("/kundali", response_class=HTMLResponse)
def serve_kundali():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "kundali.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Kundali page not found</h1>")


# ─── Dasha page ───────────────────────────────────────────
@app.get("/dasha", response_class=HTMLResponse)
def serve_dasha():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dasha.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Dasha page not found</h1>")


# ─── Ashtakavarga page ────────────────────────────────────
@app.get("/ashtakavarga", response_class=HTMLResponse)
def serve_ashtakavarga():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "ashtakavarga.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Ashtakavarga page not found</h1>")


# ─── Special Lagnas page ─────────────────────────────────
@app.get("/special-lagnas", response_class=HTMLResponse)
def serve_special_lagnas():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "special_lagnas.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Special Lagnas page not found</h1>")


# ─── Nakshatra Analysis page ───────────────────────────────
@app.get("/nakshatra", response_class=HTMLResponse)
def serve_nakshatra():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "nakshatra.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Nakshatra page not found</h1>")


# ─── Hora & Auspicious Time page ─────────────────────────────
@app.get("/hora", response_class=HTMLResponse)
def serve_hora():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "hora.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Hora page not found</h1>")


# ─── Sarvatobhadra Chakra page ───────────────────────────────
@app.get("/sbc", response_class=HTMLResponse)
def serve_sbc():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "sbc.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Sarvatobhadra Chakra page not found</h1>")


# ─── Moon Market Analysis page ──────────────────────────────
@app.get("/market", response_class=HTMLResponse)
def serve_market():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "market.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Market Analysis page not found</h1>")


# ─── Bhrigu Samhita page ──────────────────────────────────
@app.get("/bhrigu", response_class=HTMLResponse)
def serve_bhrigu():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "bhrigu.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Bhrigu Samhita page not found</h1>")


# ─── Birth Profile page ──────────────────────────────────
@app.get("/profile", response_class=HTMLResponse)
def serve_profile():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "profile.html")
    if os.path.exists(template_path):
        with open(template_path) as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Profile page not found</h1>")


# ─── Health check ───────────────────────────────────────────
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "version": "1.0.0", "modules": len(V1_ROUTERS)}
