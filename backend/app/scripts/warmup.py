"""
WeatherGPT Production Backend Pre-Demo Warmup Script (SIH PS 26068)
Usage:
  python backend/app/scripts/warmup.py
  python backend/app/scripts/warmup.py --url https://your-backend.onrender.com
  python backend/app/scripts/warmup.py --interval 600  # Run in loop every 10 min
"""

import sys
import time
import argparse
import requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_URL = "https://weathergpt-backend.onrender.com"

def warm_up_backend(base_url: str):
    base_url = base_url.rstrip("/")
    print(f"\n=======================================================")
    print(f">> Warming up WeatherGPT Backend at: {base_url}")
    print(f"=======================================================")

    endpoints = [
        {"name": "Health Check (Container Wakeup)", "path": "/health", "expected": 200},
        {"name": "Current Weather (OpenWeather & DB Cache)", "path": "/weather/current?lat=22.5726&lon=88.3639", "expected": 200},
        {"name": "Active Alerts (PostGIS Spatial Engine)", "path": "/alerts/active?lat=22.5726&lon=88.3639&radius_km=100", "expected": 200},
        {"name": "Location Search Autocomplete", "path": "/locations/search?q=Kolkata", "expected": 200},
    ]

    all_ok = True
    for ep in endpoints:
        target = f"{base_url}{ep['path']}"
        start = time.time()
        try:
            resp = requests.get(target, timeout=60) # Allow up to 60s for Render cold start
            elapsed = time.time() - start
            if resp.status_code == ep["expected"]:
                print(f"  [PASS] {ep['name']}: {resp.status_code} OK ({elapsed:.2f}s)")
            else:
                print(f"  [WARN] {ep['name']}: Unexpected status {resp.status_code} ({elapsed:.2f}s)")
                all_ok = False
        except requests.exceptions.Timeout:
            print(f"  [FAIL] {ep['name']}: Timed out after 60s (Cold start may still be spinning up)")
            all_ok = False
        except Exception as e:
            print(f"  [FAIL] {ep['name']}: Error -> {e}")
            all_ok = False

    if all_ok:
        print("\n>> SUCCESS: WeatherGPT backend is 100% warmed up, cached, and ready for judges!")
    else:
        print("\n>> WARNING: Some endpoints had issues. Check Render dashboard logs.")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Warm up WeatherGPT deployed backend before judging.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Base URL of deployed backend")
    parser.add_argument("--interval", type=int, default=0, help="Loop interval in seconds (0 = run once)")
    args = parser.parse_args()

    if args.interval > 0:
        print(f"🔁 Running recurring warmup every {args.interval} seconds (Press Ctrl+C to stop)...")
        while True:
            try:
                warm_up_backend(args.url)
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nWarmup loop stopped.")
                break
    else:
        warm_up_backend(args.url)


if __name__ == "__main__":
    main()
