#!/usr/bin/env python3
"""
scripts/fetch_eurostat.py
============================
Fetches residential electricity and gas prices for EU-27 countries
from the Eurostat REST API.

Datasets used:
  nrg_pc_204  - Electricity prices for household consumers
  nrg_pc_202  - Natural gas prices for household consumers

Output: data/eu_prices.json (intermediate file consumed by
        merge_countries.py)

Run standalone:
    python scripts/fetch_eurostat.py
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

EUROSTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "eu_prices.json")

# EU country codes tracked in our database (Eurostat uses same ISO codes)
EU_COUNTRIES = ["ES", "FR", "DE", "IT", "NL", "SE", "PT", "PL"]


def fetch_dataset(dataset: str, geo: str) -> float | None:
    """
    Fetch the latest price point for one dataset and country.

    Returns EUR/kWh, or None on failure.
    """
    try:
        resp = requests.get(
            f"{EUROSTAT_BASE}/{dataset}",
            params={
                "geo": geo,
                "format": "JSON",
                "lang": "EN",
                # Household consumption band, all taxes included
                "nrg_cons": "TOT_KWH",
                "currency": "EUR",
                "tax": "I_TAX",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        values = data.get("value", {})
        if not values:
            return None
        # Take the most recent time period's value
        latest_key = sorted(values.keys())[-1]
        return float(values[latest_key])
    except Exception as e:
        print(f"  [{geo}] {dataset} fetch failed: {e}")
        return None


def main():
    print("Fetching EU energy prices from Eurostat API...")
    results = {}

    for geo in EU_COUNTRIES:
        elec = fetch_dataset("nrg_pc_204", geo)
        gas = fetch_dataset("nrg_pc_202", geo)
        results[geo] = {"electricity_price": elec, "gas_price": gas}
        print(f"  [{geo}] electricity={elec}  gas={gas}")

    output = {
        "_meta": {
            "source": "Eurostat REST API (nrg_pc_204, nrg_pc_202)",
            "licence": "CC BY 4.0",
            "fetched": datetime.now(timezone.utc).isoformat(),
        },
        "prices": results,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nFetched {len(results)} EU countries.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
