#!/usr/bin/env python3
"""
scripts/fetch_eia.py
=======================
Fetches average US residential electricity price from the EIA API.

Requires a free API key from:
  https://www.eia.gov/opendata/register.php
Passed via the EIA_API_KEY environment variable
(set as a GitHub Actions secret named EIA_KEY).

Output: data/us_prices.json (intermediate file consumed by
        merge_countries.py)

Run standalone:
    EIA_API_KEY=your_key python scripts/fetch_eia.py
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

EIA_BASE = "https://api.eia.gov/v2/electricity/retail-sales/data"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "us_prices.json")


def fetch_us_price(api_key: str) -> float | None:
    """
    Fetch the latest national average US residential electricity price.

    Returns USD/kWh (converted from cents/kWh), or None on failure.
    """
    try:
        resp = requests.get(
            EIA_BASE,
            params={
                "api_key": api_key,
                "frequency": "monthly",
                "data[0]": "price",
                "facets[sectorid][]": "RES",
                "facets[stateid][]": "US",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": 1,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("response", {}).get("data", [])
        if not rows:
            return None
        # EIA reports price in cents/kWh
        cents_per_kwh = float(rows[0]["price"])
        return cents_per_kwh / 100.0
    except Exception as e:
        print(f"  EIA fetch failed: {e}")
        return None


def main():
    api_key = os.environ.get("EIA_API_KEY")
    if not api_key:
        print("WARNING: EIA_API_KEY not set. Skipping US price update.")
        print("Get a free key at: https://www.eia.gov/opendata/register.php")
        output = {
            "_meta": {
                "source": "EIA API (skipped - no API key)",
                "fetched": datetime.now(timezone.utc).isoformat(),
            },
            "prices": {},
        }
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)
        return

    print("Fetching US electricity price from EIA API...")
    price = fetch_us_price(api_key)

    if price is not None:
        print(f"  [US] electricity = ${price:.4f}/kWh")
        results = {"US": {"electricity_price": price}}
    else:
        results = {}

    output = {
        "_meta": {
            "source": "EIA API (retail-sales, residential, national average)",
            "licence": "Public domain (US government data)",
            "fetched": datetime.now(timezone.utc).isoformat(),
        },
        "prices": results,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
