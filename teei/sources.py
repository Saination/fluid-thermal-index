"""
Heating source parameter database for the TEEI framework.

Loads from data/sources.json. Provides source lookup, parameter
resolution, and useful thermal power calculation.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Optional, Union

from ._constants import SOLAR_COLLECTOR_EFFICIENCY, DEFAULT_SOLAR_IRRADIANCE

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_SOURCES_FILE = os.path.join(_DATA_DIR, "sources.json")


@lru_cache(maxsize=1)
def _load_database() -> Dict:
    """Load and cache the sources database from JSON."""
    path = os.path.abspath(_SOURCES_FILE)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Sources database not found at {path}. "
            "Ensure data/sources.json is present."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_sources() -> List[str]:
    """
    Return sorted list of all available source identifiers.

    Returns:
        List of source ID strings (e.g. ['electric', 'gas', 'hp3', 'hp5', 'solar']).
    """
    db = _load_database()
    return sorted(db["sources"].keys())


def get_source(source_id: str) -> Dict:
    """
    Retrieve the full metadata entry for a heating source.

    Args:
        source_id: Source identifier (e.g. 'electric', 'gas', 'solar', 'hp3', 'hp5').

    Returns:
        Dictionary with keys: name, efficiency, is_cop, co2_type, T_source_K,
        default_price_eur_kwh, default_P_rated_kW, note (if present).

    Raises:
        KeyError: If source_id is not in the database.
    """
    db = _load_database()
    sources = db["sources"]
    if source_id not in sources:
        available = sorted(sources.keys())
        raise KeyError(
            f"Source '{source_id}' not found. Available: {available}"
        )
    return sources[source_id]


def resolve_source_params(
    source: Union[str, Dict],
    price: Optional[float] = None,
    co2_intensity: Optional[float] = None,
) -> Dict:
    """
    Resolve all parameters for a heating source.

    Accepts either a source ID string (looked up in database) or a
    custom dictionary with explicit parameters.

    Args:
        source: Source ID string or dict with keys:
                  efficiency (float, required),
                  price (float, optional),
                  co2_intensity (float, optional),
                  T_source_K (float, optional),
                  name (str, optional).
        price: Override price [€/kWh]. Overrides database default AND
               any price in a dict source.
        co2_intensity: Override CO₂ intensity [g/kWh]. Overrides database.

    Returns:
        Dict with resolved keys:
          id, name, efficiency, is_cop, price, co2_intensity,
          T_source_K, co2_type.

    Raises:
        KeyError: If source string ID is not in database.
        ValueError: If required 'efficiency' key is missing from dict source.

    Examples:
        >>> resolve_source_params('electric', price=0.190, co2_intensity=160)
        {'id': 'electric', 'name': 'Electric resistance heater', ...}

        >>> resolve_source_params({'efficiency': 0.80, 'price': 0.15,
        ...                        'co2_intensity': 200, 'T_source_K': 450})
        {'id': 'custom', 'name': 'Custom source', ...}
    """
    if isinstance(source, str):
        entry = get_source(source)
        params = {
            "id": source,
            "name": entry["name"],
            "efficiency": entry["efficiency"],
            "is_cop": entry["is_cop"],
            "price": entry["default_price_eur_kwh"],
            "co2_intensity": None,           # will be set from country/grid
            "T_source_K": entry.get("T_source_K"),
            "co2_type": entry["co2_type"],
            "default_P_rated_kW": entry.get("default_P_rated_kW", 2.0),
            "default_solar_area_m2": entry.get("default_solar_area_m2", 2.5),
            "default_irradiance_W_m2": entry.get("default_irradiance_W_m2",
                                                  DEFAULT_SOLAR_IRRADIANCE),
        }
    elif isinstance(source, dict):
        if "efficiency" not in source:
            raise ValueError(
                "Custom source dict must include 'efficiency' key "
                "(thermal efficiency η or COP)."
            )
        params = {
            "id": source.get("id", "custom"),
            "name": source.get("name", "Custom source"),
            "efficiency": source["efficiency"],
            "is_cop": source.get("efficiency", 1.0) > 1.0,
            "price": source.get("price", 0.190),
            "co2_intensity": source.get("co2_intensity"),
            "T_source_K": source.get("T_source_K"),
            "co2_type": source.get("co2_type", "grid"),
            "default_P_rated_kW": source.get("P_rated_kW", 2.0),
            "default_solar_area_m2": source.get("solar_area_m2", 2.5),
            "default_irradiance_W_m2": source.get(
                "irradiance_W_m2", DEFAULT_SOLAR_IRRADIANCE
            ),
        }
    else:
        raise TypeError(
            f"source must be a string ID or dict, got {type(source).__name__}"
        )

    # Apply overrides
    if price is not None:
        params["price"] = price
    if co2_intensity is not None:
        params["co2_intensity"] = co2_intensity

    return params


def calc_p_useful(
    source_params: Dict,
    P_rated_kW: Optional[float] = None,
    solar_area_m2: Optional[float] = None,
    solar_irradiance_W_m2: Optional[float] = None,
) -> float:
    """
    Calculate useful thermal power delivered to the fluid [W].

    Args:
        source_params: Resolved source parameter dict from resolve_source_params().
        P_rated_kW: Rated input power [kW]. Overrides database default.
        solar_area_m2: Solar collector area [m²]. Solar sources only.
        solar_irradiance_W_m2: Solar irradiance [W/m²]. Solar sources only.

    Returns:
        Useful thermal power in Watts.

    Formulas:
        Conventional:  P_useful = P_rated × η
        Heat pump:     P_useful = P_rated × COP
        Solar thermal: P_useful = area × irradiance × η_collector (0.65)
    """
    sid = source_params.get("id", "")
    eta = source_params["efficiency"]

    if sid == "solar":
        area = solar_area_m2 or source_params.get("default_solar_area_m2", 2.5)
        irr = (solar_irradiance_W_m2
               or source_params.get("default_irradiance_W_m2", DEFAULT_SOLAR_IRRADIANCE))
        return area * irr * SOLAR_COLLECTOR_EFFICIENCY
    else:
        p_kw = P_rated_kW or source_params.get("default_P_rated_kW", 2.0) or 2.0
        return p_kw * 1000.0 * eta
