"""
Run the Vedic Astrology Engine.
Usage: python run.py
"""
import os
import sys
import uvicorn

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
