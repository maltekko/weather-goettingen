"""
Weather Agent - Daily Göttingen Noon Temperature Logger
Fetches the forecasted 12:00 CET temperature in Göttingen via the
Open-Meteo API, saves it to a local JSON log file, and pushes it to
GitHub Pages so the dashboard is publicly accessible.

Usage:
    python weather_agent.py
"""

import requests
import json
import os
import sys
import subprocess
from datetime import datetime
import pytz

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

# Göttingen coordinates
LATITUDE = 51.5333
LONGITUDE = 9.9333
TIMEZONE = "Europe/Berlin"

# Target forecast hour (12 = noon)
TARGET_HOUR = 12

# Number of days to keep in the log
MAX_DAYS = 7

# Log file location (same directory as this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "weather_log.json")


def get_noon_temperature() -> float:
    """
    Fetches today's forecasted temperature at 12:00 CET for Göttingen
    using the Open-Meteo free API (https://open-meteo.com).
    Returns the temperature in °C.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m",
        "timezone": TIMEZONE,
        "forecast_days": 1,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]

    berlin_tz = pytz.timezone(TIMEZONE)
    today = datetime.now(berlin_tz).strftime("%Y-%m-%d")
    target_time = f"{today}T{TARGET_HOUR:02d}:00"

    if target_time not in times:
        raise ValueError(
            f"Could not find forecast for {target_time} in API response. "
            f"Available times: {times}"
        )

    index = times.index(target_time)
    return temps[index]


def load_log() -> list:
    """Loads existing log entries from the JSON file."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_log(entries: list) -> None:
    """Saves log entries to the JSON file."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def record_temperature(temperature: float) -> None:
    """
    Appends today's temperature to the log file.
    If today already has an entry, it is overwritten (re-run safe).
    Keeps only the last MAX_DAYS entries.
    """
    berlin_tz = pytz.timezone(TIMEZONE)
    today = datetime.now(berlin_tz).strftime("%Y-%m-%d")
    today_label = datetime.now(berlin_tz).strftime("%d.%m.%Y")

    entries = load_log()

    # Remove existing entry for today if present (idempotent re-runs)
    entries = [e for e in entries if e["date"] != today]

    entries.append({
        "date": today,
        "date_label": today_label,
        "temperature_noon": round(temperature, 1),
        "recorded_at": datetime.now(berlin_tz).strftime("%H:%M"),
    })

    # Keep only the most recent MAX_DAYS entries
    entries = sorted(entries, key=lambda e: e["date"])[-MAX_DAYS:]

    save_log(entries)
    print(f"[OK] Logged {temperature:.1f} °C for {today_label} → {LOG_FILE}")


def push_to_github() -> None:
    """
    Commits the updated weather_log.json and pushes it to GitHub.
    Requires git to be installed and the repo to be initialised
    (run init_github.bat once to set this up).
    """
    berlin_tz = pytz.timezone(TIMEZONE)
    today_label = datetime.now(berlin_tz).strftime("%d.%m.%Y")
    commit_msg = f"weather update {today_label}"

    try:
        subprocess.run(["git", "add", "weather_log.json"], cwd=SCRIPT_DIR, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=SCRIPT_DIR, check=True)
        subprocess.run(["git", "push"], cwd=SCRIPT_DIR, check=True)
        print(f"[OK] Pushed to GitHub → https://maltekko.github.io/weather-goettingen/")
    except FileNotFoundError:
        print("[WARN] git not found — skipping GitHub push. Install git to enable sharing.")
    except subprocess.CalledProcessError as e:
        print(f"[WARN] GitHub push failed: {e}")


def main():
    try:
        print("Fetching noon temperature for Göttingen...")
        temperature = get_noon_temperature()
        print(f"Noon temperature: {temperature:.1f} °C")
        record_temperature(temperature)
        push_to_github()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[ERROR] Data error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
