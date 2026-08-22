"""
Fluid thermophysical property database for the TEEI framework.

Loads from data/fluids.json. Provides cp lookup, cp_eff calculation,
and fluid metadata retrieval.

All cp values are in J/(kg·°C) at approximately 20°C, 1 atm,
unless stated otherwise in the database entry.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Optional, Union

# Path to bundled data file
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_FLUIDS_FILE = os.path.join(_DATA_DIR, "fluids.json")


@lru_cache(maxsize=1)
def _load_database() -> Dict:
    """Load and cache the fluids database from JSON."""
    path = os.path.abspath(_FLUIDS_FILE)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Fluids database not found at {path}. "
            "Ensure the 'data/fluids.json' file is present in the package."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_fluids() -> List[str]:
    """
    Return a sorted list of all available fluid identifiers.

    Returns:
        List of fluid ID strings (e.g. ['ammonia', 'blood', 'ethanol', ...]).

    Examples:
        >>> list_fluids()[:3]
        ['ammonia', 'blood', 'engine_oil']
    """
    db = _load_database()
    return sorted(db["fluids"].keys())


def get_fluid(fluid_id: str) -> Dict:
    """
    Retrieve the full metadata entry for a fluid.

    Args:
        fluid_id: Fluid identifier string (e.g. 'water', 'milk').
                  Case-sensitive. Use list_fluids() to see available IDs.

    Returns:
        Dictionary with keys: name, cp, T_min_C, T_max_C, T_boil_C,
        density_kg_m3, cp_variation_pct, source, note (if present).

    Raises:
        KeyError: If fluid_id is not in the database.

    Examples:
        >>> f = get_fluid('water')
        >>> f['cp']
        4184.0
        >>> f['T_boil_C']
        100.0
    """
    db = _load_database()
    fluids = db["fluids"]
    if fluid_id not in fluids:
        available = sorted(fluids.keys())
        raise KeyError(
            f"Fluid '{fluid_id}' not found in database. "
            f"Available fluids: {available}"
        )
    return fluids[fluid_id]


def resolve_cp(fluid: Union[str, float], T_start_C: float = 20.0,
               T_end_C: Optional[float] = None) -> float:
    """
    Resolve the effective specific heat capacity for a fluid.

    Accepts either a fluid ID string (looked up in the database) or
    a direct numeric cp value [J/(kg·°C)].

    For v0.1, this returns the database reference cp value (measured at
    ~20°C). For fluids where cp variation over the heating range is
    significant (> 5%), a UserWarning is issued recommending CoolProp.

    Args:
        fluid: Fluid ID string (e.g. 'water') or cp value in J/(kg·°C).
        T_start_C: Starting temperature [°C]. Used for future CoolProp
                   integration and range checking. Default 20°C.
        T_end_C: Ending temperature [°C]. Optional; used for range
                 checking against single-phase limits.

    Returns:
        Effective specific heat capacity [J/(kg·°C)].

    Raises:
        ValueError: If a numeric cp value ≤ 0 is provided.
        KeyError: If a string fluid_id is not in the database.

    Examples:
        >>> resolve_cp('water')
        4184.0
        >>> resolve_cp(4184.0)
        4184.0
        >>> resolve_cp('milk')
        3930.0
    """
    import warnings

    if isinstance(fluid, (int, float)):
        cp_val = float(fluid)
        if cp_val <= 0:
            raise ValueError(f"cp must be > 0, got {cp_val}")
        return cp_val

    # String lookup
    entry = get_fluid(fluid)
    cp_val = entry["cp"]

    # Warn if cp variation over operating range may be significant
    variation_pct = entry.get("cp_variation_pct", 0.0)
    if variation_pct > 5.0:
        warnings.warn(
            f"Fluid '{fluid}' has cp variation of ~{variation_pct:.0f}% "
            f"over its single-phase range. For high-accuracy calculations, "
            f"consider using CoolProp to compute cp_eff via numerical "
            f"integration (see 02_formulation.md eq. 3). "
            f"Current value: {cp_val} J/(kg·°C) at reference temperature.",
            UserWarning,
            stacklevel=2,
        )

    return cp_val


def get_boiling_point(fluid: Union[str, float]) -> Optional[float]:
    """
    Return the boiling point of a fluid at 1 atm [°C].

    Args:
        fluid: Fluid ID string or numeric cp value. If numeric, returns None
               (boiling point unknown for custom fluids).

    Returns:
        Boiling point in °C, or None for custom cp values.
    """
    if isinstance(fluid, (int, float)):
        return None
    entry = get_fluid(fluid)
    return entry.get("T_boil_C")


def get_cp_variation(fluid: Union[str, float]) -> float:
    """
    Return the approximate cp variation percentage over the single-phase range.

    Args:
        fluid: Fluid ID string or numeric cp value (returns 0.0 for numeric).

    Returns:
        Percentage variation of cp over the stated single-phase range.
        0.0 if unknown or numeric input.
    """
    if isinstance(fluid, (int, float)):
        return 0.0
    entry = get_fluid(fluid)
    return entry.get("cp_variation_pct", 0.0)
