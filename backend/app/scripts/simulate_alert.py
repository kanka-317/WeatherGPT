#!/usr/bin/env python3
"""Simulate triggering a live official weather alert for WeatherGPT demo (SIH PS 26068).

Usage:
  python -m app.scripts.simulate_alert
  or directly: python backend/app/scripts/simulate_alert.py
"""

from datetime import datetime, timedelta, timezone
import json
import sys
import httpx

BACKEND_URL = "http://127.0.0.1:8000"

NADIA_SIMULATION_ALERT = {
    "location_name": "Nadia",
    "lat": 23.4710,
    "lon": 88.5565,
    "type": "Heavy Rain & Waterlogging Warning",
    "severity": "Severe",
    "message": (
        "IMD Doppler Weather Radar detects active squall lines converging over Nadia district. "
        "Intense precipitation (65-115 mm) expected across Krishnanagar, Ranaghat, and Santipur blocks "
        "over the next 18 hours. Farmers strictly advised to drain water from vegetable plots and hold all irrigation."
    ),
    "source": "IMD Regional Meteorological Centre Alipore",
    "valid_until": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
}


def trigger_live_alert():
    url = f"{BACKEND_URL}/alerts/ingest"
    print(f"[*] Triggering live alert to {url}...")
    print(f"[*] Target Location: {NADIA_SIMULATION_ALERT['location_name']} (Severity: {NADIA_SIMULATION_ALERT['severity']})")

    try:
        response = httpx.post(url, json=NADIA_SIMULATION_ALERT, timeout=10.0)
        if response.status_code == 201:
            data = response.json()
            print("\n[SUCCESS] Alert ingested successfully!")
            print(f"  Alert ID    : {data.get('id')}")
            print(f"  Type        : {data.get('type')}")
            print(f"  Severity    : {data.get('severity')}")
            print(f"  Location    : {data.get('location_name')} ({data.get('lat')}, {data.get('lon')})")
            print(f"  Broadcast   : Pushed in real-time to all connected WebSocket clients on /ws/alerts")
            print("\nCheck your browser dashboard - the Nadia marker will glow ORANGE/RED and a live toast will appear!")
        else:
            print(f"[ERROR] Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Could not connect to {url}: {e}")
        print("Ensure the FastAPI backend is running before launching this simulation.")


if __name__ == "__main__":
    trigger_live_alert()
