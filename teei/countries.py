"""
Geographic energy price and grid CO₂ intensity database for TEEI.

Loads from data/countries.json. In v0.1 this is a static dataset
updated quarterly via GitHub Actions (see 04_roadmap.md Section 8.2).

In v0.2, direct API integration with EMBER, Eurostat, and EIA will
be added as an optional real-time update path.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Optional

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_COUNTRIES_FILE = os.path.join(_DATA_DIR, "countries.json")


@lru_cache(maxsize=1)
def _load_database() -> Dict:
    """Load and cache the countries database from JSON."""
    path = os.path.abspath(_COUNTRIES_FILE)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Countries database not found at {path}. "
            "Ensure data/countries.json is present."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_countries() -> List[str]:
    """
    Return sorted list of available country codes.

    Returns:
        List of ISO 3166-1 alpha-2 country codes
        (e.g. ['AU', 'BR', 'CN', 'DE', 'ES', ...]).
    """
    db = _load_database()
    return sorted(db["countries"].keys())


def get_country(country_code: str) -> Dict:
    """
    Retrieve energy price and CO₂ intensity data for a country.

    Args:
        country_code: ISO 3166-1 alpha-2 code (e.g. 'ES', 'DE', 'FR').
                      Case-insensitive.

    Returns:
        Dictionary with keys:
          name (str)                  — Country name
          electricity_price (float)   — Residential electricity price [€/kWh]
          gas_price (float)           — Residential gas price [€/kWh]
          grid_co2 (float)            — Grid CO₂ intensity [g CO₂/kWh]
          currency (str)              — Currency of prices
          data_year (int)             — Year of the price data

    Raises:
        KeyError: If country_code is not in the database.

    Examples:
        >>> c = get_country('ES')
        >>> c['electricity_price']
        0.19
        >>> c['grid_co2']
        160
    """
    db = _load_database()
    code = country_code.upper()
    countries = db["countries"]
    if code not in countries:
        available = sorted(countries.keys())
        raise KeyError(
            f"Country '{country_code}' not in database. "
            f"Available codes: {available}\n"
            "Add the country manually or run scripts/merge_countries.py "
            "to fetch from EMBER + Eurostat APIs."
        )
    entry = countries[code].copy()
    entry["code"] = code
    return entry


def resolve_energy_params(
    country_code: Optional[str],
    source_co2_type: str,
    override_price: Optional[float] = None,
    override_co2: Optional[float] = None,
    default_grid_co2: float = 400.0,
) -> Dict[str, float]:
    """
    Resolve the energy price and CO₂ intensity for a source in a country.

    Determines whether the source uses grid CO₂ (electricity-based) or
    fixed CO₂ (gas combustion, solar lifecycle) and returns the correct
    values for the source and country combination.

    Args:
        country_code: ISO country code (e.g. 'ES'). If None, uses override
                      values or falls back to defaults.
        source_co2_type: One of 'grid', 'gas', 'solar'.
          'grid'  → CO₂ from country database (varies by country).
          'gas'   → Fixed 202 g CO₂/kWh (combustion chemistry).
          'solar' → Fixed 20 g CO₂/kWh (lifecycle estimate).
        override_price: If given, overrides country electricity/gas price.
        override_co2: If given, overrides CO₂ intensity regardless of type.
        default_grid_co2: Fallback grid CO₂ intensity if no country provided
                          and source_co2_type is 'grid'. Default: 400 g/kWh.

    Returns:
        Dict with keys:
          'price' [€/kWh]      — Fuel or electricity price
          'co2'   [g CO₂/kWh] — Applicable carbon intensity

    Examples:
        >>> resolve_energy_params('ES', 'grid')
        {'price': 0.19, 'co2': 160}

        >>> resolve_energy_params('DE', 'gas')
        {'price': 0.11, 'co2': 202.0}

        >>> resolve_energy_params(None, 'grid', override_price=0.15, override_co2=300)
        {'price': 0.15, 'co2': 300}
    """
    from ._constants import CO2_NATURAL_GAS, CO2_SOLAR_LIFECYCLE

    # Fixed CO₂ values (not country-dependent)
    fixed_co2 = {
        "gas": CO2_NATURAL_GAS,
        "solar": CO2_SOLAR_LIFECYCLE,
    }

    # Determine base CO₂
    if source_co2_type in fixed_co2:
        co2_val = fixed_co2[source_co2_type]
    else:
        # Grid: country-specific
        if country_code is not None:
            country = get_country(country_code)
            co2_val = float(country["grid_co2"])
        else:
            co2_val = default_grid_co2

    # Determine base price
    if country_code is not None:
        country = get_country(country_code)
        if source_co2_type == "gas":
            price_val = float(country["gas_price"])
        else:
            # Electric, solar, heat pump → electricity price
            price_val = float(country["electricity_price"])
    else:
        # No country: caller must provide override_price or use source default
        price_val = 0.190  # reasonable fallback (Spain avg)

    # Apply overrides
    if override_price is not None:
        price_val = override_price
    if override_co2 is not None:
        co2_val = override_co2

    return {"price": price_val, "co2": co2_val}


def database_info() -> Dict:
    """
    Return metadata about the loaded country database.

    Returns:
        Dict with keys: version, updated, sources, country_count.
    """
    db = _load_database()
    meta = db.get("_meta", {})
    return {
        "version": meta.get("version", "unknown"),
        "updated": meta.get("updated", "unknown"),
        "sources": meta.get("sources", "unknown"),
        "country_count": len(db.get("countries", {})),
    }
