#!/usr/bin/env python3
"""
scripts/fetch_ember.py
========================
Fetches grid CO2 intensity for all countries in data/countries.json
from the EMBER API (https://ember-energy.org/data/api/).

EMBER data is licensed CC BY 4.0 - free for any use including
academic publication, provided attribution is given.

Output: data/co2_intensity.json (intermediate file consumed by
        merge_countries.py)

Run standalone:
    python scripts/fetch_ember.py
"""
import json
import os
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

EMBER_API_BASE = "https://api.ember-energy.org/v1/carbon-intensity/yearly"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COUNTRIES_FILE = os.path.join(DATA_DIR, "countries.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "co2_intensity.json")


def load_country_codes():
    """Load the list of country codes currently tracked."""
    with open(COUNTRIES_FILE) as f:
        db = json.load(f)
    return list(db["countries"].keys())


def fetch_co2_for_country(code: str) -> float | None:
    """
    Fetch the latest grid CO2 intensity for one country from EMBER.

    Returns g CO2/kWh, or None if the request fails or country not found.
    """
    try:
        resp = requests.get(
            EMBER_API_BASE,
            params={
                "entity_code": code,
                "series": "Carbon intensity of electricity generation",
                "is_aggregate_series": "false",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("data"):
            print(f"  [{code}] No data returned")
            return None
        # Most recent year's value
        latest = sorted(data["data"], key=lambda x: x["date"])[-1]
        return float(latest["value"])
    except Exception as e:
        print(f"  [{code}] Fetch failed: {e}")
        return None


def main():
    print("Fetching grid CO2 intensity from EMBER API...")
    codes = load_country_codes()
    results = {}

    for code in codes:
        val = fetch_co2_for_country(code)
        if val is not None:
            results[code] = val
            print(f"  [{code}] {val:.1f} g CO2/kWh")

    output = {
        "_meta": {
            "source": "EMBER API (https://ember-energy.org/data/api/)",
            "licence": "CC BY 4.0",
            "fetched": datetime.now(timezone.utc).isoformat(),
        },
        "co2_intensity": results,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nFetched {len(results)}/{len(codes)} countries.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
