#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  Financial Astrology Engine v3.0 — Quick Start
# ═══════════════════════════════════════════════════════════════
set -e

cd "$(dirname "$0")"

# ── 1. Create virtual environment if missing ───────────────────
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# ── 2. Activate ────────────────────────────────────────────────
source .venv/bin/activate

# ── 3. Install / upgrade dependencies ─────────────────────────
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ── 4. Launch server ──────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Financial Astrology Engine v3.0 is starting..."
echo "  Dashboard:  http://localhost:8000/ui"
echo "  API Docs:   http://localhost:8000/docs"
echo "  Health:     http://localhost:8000/"
echo "═══════════════════════════════════════════════════════"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
