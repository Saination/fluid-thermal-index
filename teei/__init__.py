"""
TEEI — Thermal Economic-Environmental Index
============================================

A fluid-parameterised, multi-dimensional framework for comparing
heating sources across economic, environmental, thermodynamic,
and temporal dimensions.

Quick start
-----------
>>> from teei import calculate, compare, tpp, cgit

# Unit-rate metrics for one source–fluid pair
>>> r = calculate('water', 'electric', country='ES', mass=1.0, delta_T=80)
>>> print(f"Cost:    {r.cost_total:.4f} cents")
>>> print(f"CO₂:     {r.co2_total:.4f} g")
>>> print(f"Time:    {r.t_total:.1f} s")

# Compare all sources and get TEEI scores
>>> results = compare('water', ['electric','gas','solar','hp3','hp5'], country='ES',
...                   mass=1.0, delta_T=80)
>>> for r in results:
...     print(f"{r.rank}. {r.source_id:<8} TEEI={r.teei:.1f}")

# Policy scalars
>>> print(tpp(country='ES', cop=3.0))
>>> print(cgit(cop=3.0))

Reference
---------
Formulation document: docs/02_formulation.md
cp-invariance theorem: docs/02_formulation.md §5
"""
from __future__ import annotations

__version__ = "0.1.0"
__author__  = "TEEI Project"
__license__ = "MIT"

from typing import Dict, List, Optional, Tuple, Union

from .metrics import (
    SubMetricResult,
    JobResult,
    ComparisonResult,
    fteu as _fteu,
    ftem as _ftem,
    ftes as _ftes,
    ftet as _ftet,
    p_useful as _p_useful,
    compute_teei,
    tpp as _tpp_core,
    cgit as _cgit_core,
)
from .fluids import resolve_cp
from .sources import resolve_source_params, calc_p_useful
from .countries import resolve_energy_params
from .phase_check import check as _phase_check, PhaseChangeError


# ---------------------------------------------------------------------------
# Primary public functions
# ---------------------------------------------------------------------------

def calculate(
    fluid: Union[str, float],
    source: Union[str, Dict],
    country: Optional[str] = None,
    mass: float = 1.0,
    delta_T: float = 1.0,
    T_start: float = 20.0,
    P_rated: float = 2.0,
    solar_area: float = 2.5,
    solar_irradiance: float = 800.0,
    price: Optional[float] = None,
    co2: Optional[float] = None,
    T_ambient: Optional[float] = None,
    check_phase: bool = True,
) -> JobResult:
    """
    Calculate all TEEI sub-metrics for a single fluid–source combination.

    This is the primary calculation function. It resolves fluid properties,
    source parameters, and country energy data, runs the single-phase
    validity check, then computes FTEU, FTEM, FTES, FTET and job totals.

    Note: The ``teei`` score field of the returned JobResult is NOT
    populated here (it requires a comparative context). Use compare()
    to obtain TEEI scores for multiple sources simultaneously.

    Args:
        fluid: Fluid identifier string (e.g. ``'water'``, ``'milk'``)
               OR a direct cp value in J/(kg·°C) as a float.
        source: Heating source identifier string (e.g. ``'electric'``,
                ``'gas'``, ``'solar'``, ``'hp3'``, ``'hp5'``)
                OR a custom dict with at minimum ``{'efficiency': float}``.
        country: ISO 3166-1 alpha-2 country code (e.g. ``'ES'``, ``'DE'``).
                 If given, electricity/gas price and grid CO₂ are loaded
                 from the country database. Overridden by explicit
                 ``price`` and ``co2`` arguments.
        mass: Mass of fluid to heat [kg]. Default 1.0 kg.
        delta_T: Temperature rise [°C]. Default 1.0°C (gives unit rates).
        T_start: Starting fluid temperature [°C]. Default 20.0°C.
        P_rated: Rated input power of heating system [kW]. Default 2.0 kW.
                 Not used for solar (uses solar_area × solar_irradiance).
        solar_area: Solar collector area [m²]. Default 2.5 m².
        solar_irradiance: Solar irradiance [W/m²]. Default 800 W/m².
        price: Explicit fuel/electricity price [€/kWh]. Overrides country.
        co2: Explicit CO₂ intensity [g CO₂/kWh]. Overrides country.
        T_ambient: Ambient temperature [°C] for FTES calculation.
                   Defaults to T_start (isothermal ambient assumption).
        check_phase: If True (default), raise PhaseChangeError when
                     T_start + delta_T exits the single-phase range.
                     Set False to skip the check (e.g. for custom fluids).

    Returns:
        JobResult with all sub-metrics and job totals populated.
        The ``teei`` field is None — use compare() for TEEI scores.

    Raises:
        PhaseChangeError: If check_phase=True and the job exits the
                         single-phase region.
        KeyError: If fluid or source string ID is not in the database.
        ValueError: If numeric parameters are out of valid range.

    Examples:
        >>> r = calculate('water', 'electric', country='ES',
        ...               mass=200.0, delta_T=40.0)
        >>> f"{r.cost_total:.2f} ¢"
        '178.44 ¢'

        >>> r = calculate('milk', 'hp3', country='DE',
        ...               mass=500.0, delta_T=52.0, P_rated=3.0)
        >>> f"{r.t_total/60:.1f} min"
        '18.0 min'
    """
    # 1. Resolve fluid cp
    cp = resolve_cp(fluid, T_start_C=T_start,
                    T_end_C=T_start + delta_T)

    # 2. Resolve source parameters
    src = resolve_source_params(source)
    src_id = src["id"]

    # 3. Resolve energy price and CO₂
    energy = resolve_energy_params(
        country_code=country,
        source_co2_type=src["co2_type"],
        override_price=price,
        override_co2=co2,
    )
    resolved_price = energy["price"]
    resolved_co2 = energy["co2"]

    # 4. Single-phase check
    T_target = T_start + delta_T
    phase_result = _phase_check(fluid, T_start, T_target_C=T_target)
    if check_phase and not phase_result.valid:
        raise PhaseChangeError(
            phase_result.warning or
            f"Phase change detected for {fluid} at T_target={T_target}°C."
        )

    # 5. Compute sub-metrics
    v_fteu = _fteu(resolved_price, src["efficiency"], cp)
    v_ftem = _ftem(resolved_co2, src["efficiency"], cp)

    T_src_K = src.get("T_source_K")
    T_amb = T_ambient if T_ambient is not None else T_start
    v_ftes, ftes_model = _ftes(
        cp=cp,
        efficiency=src["efficiency"],
        T_fluid_C=T_start,
        T_source_K=T_src_K,
        T_ambient_C=T_amb,
    )

    P_use = calc_p_useful(
        source_params=src,
        P_rated_kW=P_rated,
        solar_area_m2=solar_area,
        solar_irradiance_W_m2=solar_irradiance,
    )
    v_ftet = _ftet(cp, P_use)

    # 6. Job totals
    t_total   = v_ftet * mass * delta_T
    cost_tot  = v_fteu * mass * delta_T
    co2_tot   = v_ftem * mass * delta_T

    # 7. Build result
    fluid_id = fluid if isinstance(fluid, str) else f"custom_cp{cp:.0f}"
    return JobResult(
        fteu=v_fteu,
        ftem=v_ftem,
        ftes=v_ftes,
        ftet=v_ftet,
        cp_eff=cp,
        ftes_model=ftes_model,
        source_id=src_id,
        fluid_id=fluid_id,
        mass=mass,
        delta_T=delta_T,
        t_total=t_total,
        cost_total=cost_tot,
        co2_total=co2_tot,
        single_phase=phase_result.valid,
        country=country,
    )


def compare(
    fluid: Union[str, float],
    sources: List[Union[str, Dict]],
    country: Optional[str] = None,
    mass: float = 1.0,
    delta_T: float = 1.0,
    T_start: float = 20.0,
    P_rated: float = 2.0,
    solar_area: float = 2.5,
    solar_irradiance: float = 800.0,
    price: Optional[float] = None,
    co2: Optional[float] = None,
    weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25),
    check_phase: bool = True,
) -> List[ComparisonResult]:
    """
    Compare multiple heating sources and return TEEI scores.

    Calls calculate() for each source, then normalises sub-metrics
    across the comparison set and computes the composite TEEI score
    (eq. 15 of the formulation document).

    Because all sub-metrics scale linearly with cp (the cp-invariance
    theorem, Proposition 1), the TEEI rankings returned are independent
    of which fluid was specified. Absolute values (total cost, total CO₂,
    total time) do depend on cp.

    Args:
        fluid: Fluid ID string or direct cp [J/(kg·°C)].
        sources: List of source ID strings or custom dicts.
                 Must contain at least 2 sources.
        country: ISO country code for automatic price/CO₂ lookup.
        mass: Mass of fluid [kg].
        delta_T: Temperature rise [°C].
        T_start: Starting fluid temperature [°C].
        P_rated: Rated input power [kW].
        solar_area: Solar collector area [m²].
        solar_irradiance: Solar irradiance [W/m²].
        price: Explicit price override [€/kWh].
        co2: Explicit CO₂ intensity override [g/kWh].
        weights: Tuple (w_cost, w_carbon, w_entropy, w_speed).
                 Values need not sum to 1; normalised internally.
        check_phase: Raise PhaseChangeError on phase change. Default True.

    Returns:
        List of ComparisonResult, sorted best → worst by TEEI score.
        Each result has teei, rank, perf_fteu/ftem/ftes/ftet populated.

    Raises:
        ValueError: If fewer than 2 sources are provided.
        PhaseChangeError: If check_phase=True and phase change detected.

    Examples:
        >>> results = compare('water',
        ...     ['electric', 'gas', 'solar', 'hp3', 'hp5'],
        ...     country='ES', mass=1.0, delta_T=80)
        >>> for r in results:
        ...     print(f"{r.rank}. {r.source_id:<8}  TEEI={r.teei:.1f}")
        1. hp5       TEEI=87.5
        2. solar     TEEI=78.3
        ...

        >>> # cp-invariance: same ranking for mercury
        >>> results_hg = compare('mercury',
        ...     ['electric', 'gas', 'solar', 'hp3', 'hp5'],
        ...     country='ES', mass=1.0, delta_T=80)
        >>> [r.source_id for r in results] == [r.source_id for r in results_hg]
        True
    """
    if len(sources) < 2:
        raise ValueError(
            f"compare() requires at least 2 sources, got {len(sources)}. "
            "TEEI normalisation is only meaningful across multiple sources."
        )

    raw: List[JobResult] = []
    for src in sources:
        r = calculate(
            fluid=fluid, source=src, country=country,
            mass=mass, delta_T=delta_T, T_start=T_start,
            P_rated=P_rated, solar_area=solar_area,
            solar_irradiance=solar_irradiance,
            price=price, co2=co2,
            check_phase=check_phase,
        )
        raw.append(r)

    return compute_teei(raw, weights=weights)


# ---------------------------------------------------------------------------
# Policy scalars (public wrappers)
# ---------------------------------------------------------------------------

def tpp(
    country: Optional[str] = None,
    cop: float = 3.0,
    source_gas: str = "gas",
    price_gas: Optional[float] = None,
) -> Dict:
    """
    Thermal Parity Price [€/kWh electricity].

    The electricity price at which a heat pump (COP = cop) becomes
    economically equivalent to a gas source. If electricity is cheaper
    than the TPP in a given country, the heat pump wins on cost.

    Result is fluid-independent (cp cancels — cp-invariance theorem).

    Args:
        country: ISO country code for automatic gas price lookup.
        cop: Heat pump Coefficient of Performance. Default 3.0.
        source_gas: Gas source ID in database. Default 'gas'.
        price_gas: Explicit gas price [€/kWh]. Overrides country lookup.

    Returns:
        Dict with keys: tpp, formula, interpretation, local_elec_price,
        hp_wins (bool), country.

    Examples:
        >>> tpp(country='ES', cop=3.0)
        {'tpp': 0.6133, ..., 'hp_wins': True}
        >>> tpp(country='DE', cop=3.0)
        {'tpp': 0.7333, ..., 'hp_wins': True}
    """
    from .sources import get_source

    src = get_source(source_gas)
    eta_gas = src["efficiency"]

    if price_gas is None:
        if country is not None:
            energy = resolve_energy_params(country, "gas")
            price_gas = energy["price"]
        else:
            price_gas = src["default_price_eur_kwh"]

    result = _tpp_core(price_gas=price_gas, cop=cop, eta_gas=eta_gas)

    # Add local electricity price comparison
    local_elec = None
    if country is not None:
        energy_elec = resolve_energy_params(country, "grid")
        local_elec = energy_elec["price"]

    result["local_elec_price"] = local_elec
    result["hp_wins"] = (local_elec < result["tpp"]) if local_elec else None
    result["country"] = country

    return result


def cgit(
    cop: float = 1.0,
    co2_gas: float = 202.0,
    eta_gas: float = 0.45,
) -> Dict:
    """
    Carbon Grid Intensity Threshold [g CO₂/kWh grid].

    The grid CO₂ intensity below which electric heating (resistance or
    heat pump) beats gas combustion on carbon emissions. Fluid-independent.

    Args:
        cop: COP of heat pump. Use 1.0 for resistance heater (default).
        co2_gas: Gas combustion intensity [g CO₂/kWh]. Default 202.0.
        eta_gas: Gas appliance efficiency. Default 0.45.

    Returns:
        Dict with keys: cgit, formula, note, country_comparison.

    Examples:
        >>> cgit(cop=1.0)   # resistance heater
        {'cgit': 448.9, ...}
        >>> cgit(cop=3.0)   # heat pump COP 3
        {'cgit': 1346.7, ...}
    """
    from .countries import _load_database

    result = _cgit_core(cop=cop, co2_gas=co2_gas, eta_gas=eta_gas)

    # Add country comparison
    try:
        db = _load_database()
        threshold = result["cgit"]
        comparison = {}
        for code, data in db["countries"].items():
            grid = data.get("grid_co2", 0)
            comparison[code] = {
                "name": data["name"],
                "grid_co2": grid,
                "should_electrify": grid < threshold,
            }
        result["country_comparison"] = comparison
    except Exception:
        result["country_comparison"] = {}

    return result


# ---------------------------------------------------------------------------
# Convenience re-exports
# ---------------------------------------------------------------------------
from .fluids import list_fluids, get_fluid, resolve_cp
from .sources import list_sources, get_source
from .countries import list_countries, get_country, database_info
from .phase_check import check as phase_check, PhaseChangeError
from .metrics import (
    SubMetricResult, JobResult, ComparisonResult,
    fteu, ftem, ftes, ftet, compute_teei,
)

__all__ = [
    # High-level API
    "calculate", "compare", "tpp", "cgit",
    # Low-level metric functions
    "fteu", "ftem", "ftes", "ftet", "compute_teei",
    # Data access
    "list_fluids", "get_fluid", "resolve_cp",
    "list_sources", "get_source",
    "list_countries", "get_country", "database_info",
    # Phase check
    "phase_check", "PhaseChangeError",
    # Result types
    "SubMetricResult", "JobResult", "ComparisonResult",
]
