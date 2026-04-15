"""
main.py — Financial Astrology Engine v2.0
Advanced Vedic Astrology API with Financial Automation for NSE/BSE
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.chart_service import (
    calculate_birth_chart,
    calculate_transits,
    calculate_dasha,
    calculate_divisional,
    calculate_sarvatobhadra,
    calculate_ashtakavarga,
    calculate_yogas,
    calculate_transit_alerts,
    calculate_full_prediction,
)
from app.schemas import (
    BirthInput,
    TransitInput,
    DashaInput,
    DivisionalInput,
    SarvatobhadraInput,
    AshtakavargaInput,
    YogaInput,
    TransitAlertInput,
    FullPredictionInput,
)

app = FastAPI(
    title="Financial Astrology Engine v2.0",
    version="2.0.0",
    description=(
        "Advanced Vedic Astrology API for NSE/BSE Financial Predictions. "
        "Includes: Birth Charts, Vimshottari Dasha, Nakshatras, Divisional Charts (D2/D9/D10), "
        "Ashtakavarga with Transit Dates, Financial Yoga Detection, Transit Alerts, "
        "and Autonomous Market Prediction Engine."
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

# Serve UI
ui_dir = Path(__file__).resolve().parent / "financial_astrology_ui"
if ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=ui_dir, html=True), name="ui")


@app.get("/", tags=["Health"])
def home() -> dict:
    return {
        "message": "Financial Astrology Engine v2.0 is running 🔮",
        "market":  "NSE/BSE India",
        "ui":      "/ui",
        "docs":    "/docs",
        "endpoints": {
            "birth_chart":     "POST /chart",
            "transits":        "POST /transits",
            "dasha":           "POST /dasha",
            "divisional":      "POST /divisional",
            "sarvatobhadra":  "POST /sarvatobhadra",
            "ashtakavarga":    "POST /ashtakavarga",
            "yogas":           "POST /yogas",
            "transit_alerts":  "POST /transit-alerts",
            "full_prediction": "POST /predict  ← Main autonomous prediction",
        },
    }


# ─── Birth Chart ────────────────────────────────────────────
@app.post("/chart", tags=["Charts"], summary="Birth Chart with Nakshatras")
def chart(payload: BirthInput) -> dict:
    """
    Calculate Vedic birth chart (D1) with:
    - Planetary positions (sidereal)
    - Ascendant & 12 house cusps
    - Nakshatra, pada, sub-lord for each planet
    - Financial significance of each placement
    """
    try:
        return calculate_birth_chart(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ─── Transits ────────────────────────────────────────────────
@app.post("/transits", tags=["Charts"], summary="Current Transit Positions + Moon Signal")
def transits(payload: TransitInput) -> dict:
    """
    Current planetary transits with:
    - Nakshatra positions of all planets
    - Moon nakshatra daily NSE/BSE signal
    """
    try:
        return calculate_transits(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ─── Vimshottari Dasha ───────────────────────────────────────
@app.post("/dasha", tags=["Dasha"], summary="Vimshottari Dasha Tree (Maha/Antar/Pratyantar)")
def dasha(payload: DashaInput) -> dict:
    """
    Full Vimshottari Dasha calculation:
    - Mahadasha, Antardasha, Pratyantar Dasha with exact dates
    - Current active dasha as of today (or specified date)
    - Financial sector implications of each dasha period
    """
    try:
        return calculate_dasha(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ─── Divisional Charts ───────────────────────────────────────
@app.post("/divisional", tags=["Charts"], summary="Divisional Charts D2/D9/D10")
def divisional(payload: DivisionalInput) -> dict:
    """
    Divisional chart analysis:
    - D2 Hora: Wealth and earning capacity
    - D3 Drekkana: Business partners and efforts
    - D9 Navamsha: Planetary strength and fortune
    - D10 Dashamsha: Career and professional success
    """
    try:
        return calculate_divisional(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ─── Sarvatobhadra Chakra ───────────────────────────────────────
@app.post("/sarvatobhadra", tags=["Charts"], summary="Sarvatobhadra Chakra Casting")
def sarvatobhadra(payload: SarvatobhadraInput) -> dict:
    """
    Sarvatobhadra Chakra casting based on natal Moon nakshatra and ascending sign.
    Returns chakra cells, planet placements, and moon nakshatra details.
    """
    try:
        return calculate_sarvatobhadra(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ─── Ashtakavarga ────────────────────────────────────────────
@app.post("/ashtakavarga", tags=["Ashtakavarga"], summary="Ashtakavarga + Transit Date Predictions")
def ashtakavarga(payload: AshtakavargaInput) -> dict:
    """
    Ashtakavarga system:
    - Bhinnashtakavarga (BAV) for all 7 planets
    - Sarvashtakavarga (SAV) total scores
    - Upcoming planetary transit dates with BAV/SAV scores
    - NSE/BSE market impact for each transit
    """
    try:
        return calculate_ashtakavarga(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ─── Yoga Detection ──────────────────────────────────────────
@app.post("/yogas", tags=["Yogas"], summary="Financial Yoga Detection")
def yogas(payload: YogaInput) -> dict:
    """
    Detect all financial yogas:
    - Dhana Yogas (wealth combinations)
    - Raj Yogas (power and authority)
    - Pancha Mahapurusha Yogas
    - Gaja Kesari, Venus-Jupiter, Budha-Aditya
    - Malefic yogas (Kemadruma, Mars-Saturn, Shakat)
    - Overall NSE/BSE buy/sell signal from yoga analysis
    """
    try:
        return calculate_yogas(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ─── Transit Alerts ──────────────────────────────────────────
@app.post("/transit-alerts", tags=["Alerts"], summary="NSE/BSE Transit Alert System")
def transit_alerts(payload: TransitAlertInput) -> dict:
    """
    Real-time NSE/BSE transit alerts:
    - Sign ingress alerts (Jupiter/Saturn/Mars)
    - Retrograde start/end alerts
    - Solar and lunar eclipse alerts
    - Critical degree (0°/29°) alerts
    - Conjunction alerts (Mars-Saturn, Jupiter-Venus, etc.)
    - Optional: Personal natal transit overlays
    """
    try:
        return calculate_transit_alerts(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ─── Full Autonomous Prediction ──────────────────────────────
@app.post("/predict", tags=["Prediction"], summary="🎯 Autonomous NSE/BSE Market Prediction")
def predict(payload: FullPredictionInput) -> dict:
    """
    **Main autonomous prediction endpoint.**

    Combines ALL signals for NSE/BSE market prediction:
    1. Current planetary sign positions (weighted)
    2. Moon nakshatra daily signal
    3. Active Vimshottari Dasha character (if natal chart provided)
    4. Financial yoga analysis (if natal chart provided)
    5. Ashtakavarga transit scores
    6. Retrograde, eclipse, and critical degree alerts

    Returns:
    - Overall BULLISH/BEARISH signal with confidence %
    - 7-day daily Moon nakshatra outlook
    - Sector-specific BUY/HOLD/AVOID recommendations
    - Key upcoming planetary events
    - Risk factors
    - Complete score breakdown with methodology
    """
    try:
        return calculate_full_prediction(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
