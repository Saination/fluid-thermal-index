#!/usr/bin/env python3
"""
scripts/merge_countries.py
=============================
Merges data from fetch_ember.py, fetch_eurostat.py, and fetch_eia.py
into the canonical data/countries.json used by the teei package.

Priority order (highest wins on conflict):
  1. Freshly fetched EMBER data (grid CO2)
  2. Freshly fetched Eurostat data (EU prices)
  3. Freshly fetched EIA data (US price)
  4. Existing countries.json value (fallback if fetch failed)

Also writes data/update_log.json recording what changed and when.

Run standalone (after running the three fetch_*.py scripts):
    python scripts/merge_countries.py
"""
import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COUNTRIES_FILE = os.path.join(DATA_DIR, "countries.json")
CO2_FILE = os.path.join(DATA_DIR, "co2_intensity.json")
EU_PRICES_FILE = os.path.join(DATA_DIR, "eu_prices.json")
US_PRICES_FILE = os.path.join(DATA_DIR, "us_prices.json")
UPDATE_LOG_FILE = os.path.join(DATA_DIR, "update_log.json")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default or {}
    with open(path) as f:
        return json.load(f)


def main():
    print("Merging country data sources...")

    countries_db = load_json(COUNTRIES_FILE)
    co2_data = load_json(CO2_FILE).get("co2_intensity", {})
    eu_prices = load_json(EU_PRICES_FILE).get("prices", {})
    us_prices = load_json(US_PRICES_FILE).get("prices", {})

    changes = []
    today = datetime.now(timezone.utc)
    year_q = f"{today.year}-Q{(today.month - 1) // 3 + 1}"

    for code, entry in countries_db["countries"].items():
        # Update grid CO2 from EMBER
        if code in co2_data:
            old = entry.get("grid_co2")
            new = round(co2_data[code], 1)
            if old != new:
                changes.append(f"{code}: grid_co2 {old} -> {new}")
                entry["grid_co2"] = new

        # Update EU prices from Eurostat
        if code in eu_prices:
            p = eu_prices[code]
            if p.get("electricity_price") is not None:
                old = entry.get("electricity_price")
                new = round(p["electricity_price"], 3)
                if old != new:
                    changes.append(f"{code}: electricity_price {old} -> {new}")
                    entry["electricity_price"] = new
            if p.get("gas_price") is not None:
                old = entry.get("gas_price")
                new = round(p["gas_price"], 3)
                if old != new:
                    changes.append(f"{code}: gas_price {old} -> {new}")
                    entry["gas_price"] = new

        # Update US price from EIA
        if code in us_prices:
            p = us_prices[code]
            if p.get("electricity_price") is not None:
                old = entry.get("electricity_price")
                new = round(p["electricity_price"], 3)
                if old != new:
                    changes.append(f"{code}: electricity_price {old} -> {new}")
                    entry["electricity_price"] = new

        entry["data_year"] = today.year

    # Update metadata
    countries_db["_meta"]["version"] = year_q
    countries_db["_meta"]["updated"] = today.strftime("%Y-%m-%d")

    with open(COUNTRIES_FILE, "w") as f:
        json.dump(countries_db, f, indent=2)

    # Write update log (keep last 20 entries)
    log = load_json(UPDATE_LOG_FILE, default={"history": []})
    log["history"].append({
        "date": today.isoformat(),
        "version": year_q,
        "changes": changes,
        "changes_count": len(changes),
    })
    log["history"] = log["history"][-20:]   # keep last 20 updates

    with open(UPDATE_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

    print(f"\nMerge complete. {len(changes)} values changed.")
    for c in changes:
        print(f"  {c}")
    print(f"\nUpdated: {COUNTRIES_FILE}")
    print(f"Log:     {UPDATE_LOG_FILE}")


if __name__ == "__main__":
    main()
