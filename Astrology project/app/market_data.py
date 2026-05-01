"""
market_data.py — NSE/BSE Market Data Integration
Uses yfinance for free access to:
- Nifty 50, Sensex, and sectoral indices
- Historical OHLCV data for backtesting
- Real-time (15-min delayed) prices

Ticker symbols:
- ^NSEI = Nifty 50
- ^BSESN = Sensex
- Sectoral: ^NSEBANK, ^CNXIT, etc.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

from app.constants import NSE_SECTORS


# ─────────────────────────────────────────────────────────────
# Ticker Mapping
# ─────────────────────────────────────────────────────────────
TICKERS = {
    "NIFTY_50":     "^NSEI",
    "SENSEX":       "^BSESN",
    "BANK_NIFTY":   "^NSEBANK",
    "NIFTY_IT":     "^CNXIT",
    "NIFTY_PHARMA": "^CNXPHARMA",
    "NIFTY_AUTO":   "NIFTY_AUTO.NS",
    "NIFTY_FMCG":   "NIFTY_FMCG.NS",
    "NIFTY_METAL":  "^CNXMETAL",
    "NIFTY_REALTY":  "NIFTY_REALTY.NS",
    "NIFTY_ENERGY":  "NIFTY_ENERGY.NS",
    "NIFTY_INFRA":  "NIFTY_INFRA.NS",
    "GOLD_INR":     "GC=F",
    "SILVER_INR":   "SI=F",
    "USD_INR":      "INR=X",
}


def get_market_status() -> Dict:
    """Check if market data is available and return current status."""
    if not HAS_YFINANCE:
        return {
            "available": False,
            "message": "yfinance not installed. Run: pip install yfinance",
        }
    return {"available": True, "message": "Market data ready"}


def get_current_prices(indices: Optional[List[str]] = None) -> Dict:
    """
    Get current (or last available) prices for NSE/BSE indices.
    Returns OHLCV + change % for today.
    """
    if not HAS_YFINANCE:
        return {"error": "yfinance not installed"}

    if indices is None:
        indices = ["NIFTY_50", "SENSEX", "BANK_NIFTY"]

    results = {}
    for idx_name in indices:
        ticker_symbol = TICKERS.get(idx_name)
        if not ticker_symbol:
            continue
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="2d")
            if hist.empty:
                results[idx_name] = {"error": "No data available"}
                continue

            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else latest
            change = latest["Close"] - prev["Close"]
            change_pct = (change / prev["Close"]) * 100 if prev["Close"] else 0

            results[idx_name] = {
                "ticker": ticker_symbol,
                "date": str(hist.index[-1].date()),
                "open": round(float(latest["Open"]), 2),
                "high": round(float(latest["High"]), 2),
                "low": round(float(latest["Low"]), 2),
                "close": round(float(latest["Close"]), 2),
                "volume": int(latest["Volume"]),
                "change": round(float(change), 2),
                "change_pct": round(float(change_pct), 2),
                "trend": "UP" if change > 0 else "DOWN" if change < 0 else "FLAT",
            }
        except Exception as e:
            results[idx_name] = {"error": str(e)}

    return {"timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), "prices": results}


def get_historical_data(
    ticker_name: str = "NIFTY_50",
    start_date: str = "2020-01-01",
    end_date: Optional[str] = None,
    interval: str = "1d",
) -> Dict:
    """
    Get historical OHLCV data for backtesting.
    interval: 1d, 1wk, 1mo
    """
    if not HAS_YFINANCE:
        return {"error": "yfinance not installed"}

    ticker_symbol = TICKERS.get(ticker_name, ticker_name)
    if end_date is None:
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(start=start_date, end=end_date, interval=interval)

        if hist.empty:
            return {"error": "No data found", "ticker": ticker_symbol}

        data = []
        for idx, row in hist.iterrows():
            data.append({
                "date": str(idx.date()),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        # Calculate basic stats
        closes = [d["close"] for d in data]
        returns = []
        for i in range(1, len(closes)):
            ret = (closes[i] - closes[i - 1]) / closes[i - 1] * 100
            returns.append(ret)

        return {
            "ticker": ticker_symbol,
            "ticker_name": ticker_name,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "total_records": len(data),
            "data": data,
            "stats": {
                "first_close": closes[0] if closes else 0,
                "last_close": closes[-1] if closes else 0,
                "total_return_pct": round(
                    ((closes[-1] - closes[0]) / closes[0]) * 100, 2
                ) if closes and closes[0] else 0,
                "avg_daily_return": round(sum(returns) / len(returns), 4) if returns else 0,
                "max_daily_gain": round(max(returns), 2) if returns else 0,
                "max_daily_loss": round(min(returns), 2) if returns else 0,
                "positive_days": sum(1 for r in returns if r > 0),
                "negative_days": sum(1 for r in returns if r < 0),
            },
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker_symbol}


def get_sector_performance(period: str = "1mo") -> Dict:
    """Get performance of NSE sectoral indices for sector rotation analysis."""
    if not HAS_YFINANCE:
        return {"error": "yfinance not installed"}

    sectors = {
        "NIFTY_50": "^NSEI",
        "BANK_NIFTY": "^NSEBANK",
        "NIFTY_IT": "^CNXIT",
    }

    results = {}
    for name, symbol in sectors.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                continue
            first = float(hist.iloc[0]["Close"])
            last = float(hist.iloc[-1]["Close"])
            change = ((last - first) / first) * 100

            results[name] = {
                "symbol": symbol,
                "period_start": str(hist.index[0].date()),
                "period_end": str(hist.index[-1].date()),
                "start_price": round(first, 2),
                "end_price": round(last, 2),
                "change_pct": round(change, 2),
                "trend": "BULLISH" if change > 2 else "BEARISH" if change < -2 else "FLAT",
            }
        except Exception:
            continue

    # Rank by performance
    ranked = sorted(results.items(), key=lambda x: -x[1].get("change_pct", 0))

    return {
        "period": period,
        "sectors": results,
        "top_sectors": [r[0] for r in ranked[:3]],
        "bottom_sectors": [r[0] for r in ranked[-3:]],
    }
