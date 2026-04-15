# Financial Astrology Engine

A simple FastAPI project for Vedic astrology chart calculations.

## Features
- FastAPI backend
- `/chart` endpoint for birth chart calculations
- `/transits` endpoint for current transit calculations
- Automatic latitude/longitude lookup from place name
- Automatic timezone detection, including U.S. timezones and DST
- Sidereal planet positions using Swiss Ephemeris

## Project Structure

```text
financial_astrology_project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── core.py
│   └── chart_service.py
├── requirements.txt
└── README.md
```

## Install

```bash
pip3 install -r requirements.txt
```

## Run

```bash
python3 -m uvicorn app.main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001/docs
```

## Example birth chart request

```json
{
  "name": "Test Ujjain",
  "date": "1995-05-10",
  "time": "14:30",
  "place": "Ujjain, Madhya Pradesh, India",
  "ayanamsa": "lahiri"
}
```

## Example U.S. request

```json
{
  "name": "Denver Test",
  "date": "1990-01-01",
  "time": "12:00",
  "place": "Denver, Colorado, USA",
  "ayanamsa": "lahiri"
}
```

## Notes
- If `latitude`, `longitude`, or `timezone_offset_minutes` are not provided, the API derives them from `place`.
- For best geocoding results, use full place names like `City, State, Country`.
- If a geocoding request fails, try a more specific place name.
