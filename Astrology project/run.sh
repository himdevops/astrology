#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Financial Astrology Engine v2.0 — Startup Script
# ═══════════════════════════════════════════════════════════════

set -e
cd "$(dirname "$0")"

echo "🔮 Financial Astrology Engine v2.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install dependencies if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
  echo "📦 Installing dependencies..."
  pip3 install -r requirements.txt --break-system-packages -q
fi

echo "✅ Starting server on http://127.0.0.1:8001"
echo "📊 Dashboard UI: http://127.0.0.1:8001/ui"
echo "📖 API Docs:     http://127.0.0.1:8001/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
