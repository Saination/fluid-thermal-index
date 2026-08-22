"""
Core TEEI sub-metric and composite index calculations.

All equations are referenced by number to 02_formulation.md.

Sub-metrics (absolute values per unit fluid mass per unit temperature rise):
  FTEU  — Fluid Thermal Economic Unit    [¢ / kg·°C]   (eq. 4)
  FTEM  — Fluid Thermal Emission Metric  [g CO₂/kg·°C]  (eq. 6)
  FTES  — Fluid Thermal Entropy Score    [J / kg·K²]    (eq. 7 / 8)
  FTET  — Fluid Thermal Energy Time      [s / kg·°C]    (eq. 9)

Policy scalars (fluid-invariant by the cp-invariance theorem):
  TPP   — Thermal Parity Price           [€/kWh]        (eq. 11)
  CGIT  — Carbon Grid Intensity Threshold [g CO₂/kWh]   (eq. 12)

Composite:
  TEEI  — Thermal Economic-Environmental Index [0–100]   (eq. 15)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple
import math

from ._constants import (
    K1, K2, KELVIN_OFFSET,
    T_SOURCE_ELECTRIC, T_SOURCE_GAS, T_SOURCE_SOLAR,
    SOLAR_COLLECTOR_EFFICIENCY,
)


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SubMetricResult:
    """
    Raw (un-normalised) sub-metric values for one source–fluid combination.

    All values are per unit mass (1 kg) per unit temperature rise (1 °C),
    representing the *unit rate* of each quantity.
    """
    fteu: float
    """Fluid Thermal Economic Unit [¢/kg·°C]. Cost to heat 1 kg by 1°C."""

    ftem: float
    """Fluid Thermal Emission Metric [g CO₂/kg·°C]. CO₂ to heat 1 kg by 1°C."""

    ftes: float
    """Fluid Thermal Entropy Score [J/kg·K²]. Entropy generated per kg per °C."""

    ftet: float
    """Fluid Thermal Energy Time [s/kg·°C]. Time to heat 1 kg by 1°C."""

    cp_eff: float
    """Effective specific heat used [J/kg·°C]."""

    ftes_model: str
    """'A' for conventional heater (η ≤ 1) or 'B' for heat pump (COP > 1)."""

    source_id: str = ""
    """Identifier of the heating source."""

    fluid_id: str = ""
    """Identifier of the fluid."""


@dataclass
class JobResult(SubMetricResult):
    """
    Extended result including total values for a specific heating job
    (mass m kg, temperature rise delta_T °C).
    """
    mass: float = 1.0
    """Mass of fluid heated [kg]."""

    delta_T: float = 1.0
    """Temperature rise [°C]."""

    t_total: float = 0.0
    """Total heating time [s] = FTET × mass × delta_T."""

    cost_total: float = 0.0
    """Total cost [¢] = FTEU × mass × delta_T."""

    co2_total: float = 0.0
    """Total CO₂ emissions [g] = FTEM × mass × delta_T."""

    single_phase: bool = True
    """True if the heating job stays within the single-phase liquid range."""

    country: Optional[str] = None
    """ISO 3166-1 alpha-2 country code, if geographic data was used."""


@dataclass
class ComparisonResult(JobResult):
    """
    Full result including normalised TEEI scores, populated by compare().
    Only meaningful when computed as part of a multi-source comparison.
    """
    perf_fteu: float = 0.0
    """Cost performance score [0–100]. Higher = cheaper."""

    perf_ftem: float = 0.0
    """Carbon performance score [0–100]. Higher = cleaner."""

    perf_ftes: float = 0.0
    """Entropy performance score [0–100]. Higher = more reversible."""

    perf_ftet: float = 0.0
    """Speed performance score [0–100]. Higher = faster."""

    teei: float = 0.0
    """Composite TEEI score [0–100]. Higher = better overall."""

    rank: int = 0
    """Rank among compared sources (1 = best TEEI)."""


# ---------------------------------------------------------------------------
# Individual sub-metric functions
# ---------------------------------------------------------------------------

def fteu(price: float, efficiency: float, cp: float) -> float:
    """
    Fluid Thermal Economic Unit [¢/kg·°C].  (Formulation eq. 4)

    Cost in euro-cents to raise 1 kg of fluid by 1°C.

    Args:
        price: Fuel or electricity price [€/kWh].
        efficiency: Thermal efficiency η (0–1 for conventional heaters)
                    or COP (>1 for heat pumps). Must be > 0.
        cp: Effective specific heat of fluid [J/kg·°C]. Must be > 0.

    Returns:
        FTEU value in ¢/kg·°C.

    Examples:
        >>> fteu(0.190, 0.99, 4184)   # Spain electric, water
        0.022305...
        >>> fteu(0.190, 3.00, 4184)   # Spain HP COP3, water
        0.007368...
    """
    if efficiency <= 0:
        raise ValueError(f"efficiency must be > 0, got {efficiency}")
    if cp <= 0:
        raise ValueError(f"cp must be > 0, got {cp}")
    if price < 0:
        raise ValueError(f"price must be >= 0, got {price}")
    return (price / efficiency) * (cp / K2)


def ftem(co2_intensity: float, efficiency: float, cp: float) -> float:
    """
    Fluid Thermal Emission Metric [g CO₂/kg·°C].  (Formulation eq. 6)

    Carbon dioxide emitted to raise 1 kg of fluid by 1°C.

    Args:
        co2_intensity: Carbon intensity of the energy source [g CO₂/kWh].
        efficiency: Thermal efficiency η or COP. Must be > 0.
        cp: Effective specific heat of fluid [J/kg·°C]. Must be > 0.

    Returns:
        FTEM value in g CO₂/kg·°C.

    Examples:
        >>> ftem(160.0, 0.99, 4184)   # Spain grid, electric heater, water
        0.18783...
        >>> ftem(202.0, 0.45, 4184)   # Natural gas, stove, water
        0.52171...
    """
    if efficiency <= 0:
        raise ValueError(f"efficiency must be > 0, got {efficiency}")
    if cp <= 0:
        raise ValueError(f"cp must be > 0, got {cp}")
    if co2_intensity < 0:
        raise ValueError(f"co2_intensity must be >= 0, got {co2_intensity}")
    return (co2_intensity / efficiency) * (cp / K1)


def ftes(
    cp: float,
    efficiency: float,
    T_fluid_C: float,
    T_source_K: Optional[float] = None,
    T_ambient_C: Optional[float] = None,
) -> Tuple[float, str]:
    """
    Fluid Thermal Entropy Score [J/kg·K²].  (Formulation eq. 7 or 8)

    Entropy generated per kg of fluid per °C of temperature rise.
    Captures thermodynamic irreversibility of the heating process.

    Two models are selected automatically:
      - Model A (conventional, η ≤ 1): uses source temperature T_source_K.
        FTES = (cp/η)(1/T_f − 1/T_s) + cp(1/η − 1)/T_0
      - Model B (heat pump, η = COP > 1): no source temperature needed.
        FTES = cp(1/T_f − (β−1)/(β·T_0))

    Args:
        cp: Effective specific heat [J/kg·°C]. Must be > 0.
        efficiency: η for conventional heaters (0 < η ≤ 1), or
                    COP = β for heat pumps (β > 1).
        T_fluid_C: Fluid starting temperature [°C].
        T_source_K: Effective source temperature [K]. Required for Model A
                    (conventional heaters). Ignored for Model B.
        T_ambient_C: Ambient temperature [°C]. Defaults to T_fluid_C
                     (isothermal ambient assumption).

    Returns:
        Tuple of (ftes_value [J/kg·K²], model_used ['A' or 'B']).

    Raises:
        ValueError: If Model A is selected but T_source_K is not provided,
                    or if T_source_K <= T_fluid_K (source must be hotter).
    """
    if cp <= 0:
        raise ValueError(f"cp must be > 0, got {cp}")
    if efficiency <= 0:
        raise ValueError(f"efficiency must be > 0, got {efficiency}")

    T_f = T_fluid_C + KELVIN_OFFSET
    T_0 = (T_ambient_C + KELVIN_OFFSET) if T_ambient_C is not None else T_f

    if efficiency > 1.0:
        # Model B — heat pump
        beta = efficiency
        value = cp * (1.0 / T_f - (beta - 1.0) / (beta * T_0))
        return max(0.0, value), 'B'
    else:
        # Model A — conventional heater
        if T_source_K is None:
            raise ValueError(
                "T_source_K is required for conventional heaters (efficiency ≤ 1). "
                "Provide the effective source temperature in Kelvin."
            )
        if T_source_K <= T_f:
            raise ValueError(
                f"Source temperature T_source_K={T_source_K} K must exceed "
                f"fluid temperature T_fluid={T_f:.2f} K."
            )
        eta = efficiency
        term1 = (cp / eta) * (1.0 / T_f - 1.0 / T_source_K)
        term2 = cp * (1.0 / eta - 1.0) / T_0
        return max(0.0, term1 + term2), 'A'


def ftet(cp: float, P_useful_W: float) -> float:
    """
    Fluid Thermal Energy Time [s/kg·°C].  (Formulation eq. 9)

    Time required to raise 1 kg of fluid by 1°C at the given useful
    thermal power delivered to the fluid.

    Args:
        cp: Effective specific heat [J/kg·°C]. Must be > 0.
        P_useful_W: Useful thermal power delivered to the fluid [W]. Must be > 0.
                    For conventional heaters: P_rated_W × η
                    For heat pumps:           P_rated_W × COP
                    For solar thermal:        area_m2 × irradiance_W_m2 × η_collector

    Returns:
        FTET value in s/kg·°C.

    Examples:
        >>> ftet(4184, 2000 * 0.99)   # water, 2 kW electric heater
        2.1131...
        >>> ftet(4184, 2000 * 3.0)    # water, 2 kW HP COP3
        0.6973...
    """
    if cp <= 0:
        raise ValueError(f"cp must be > 0, got {cp}")
    if P_useful_W <= 0:
        raise ValueError(f"P_useful_W must be > 0, got {P_useful_W}")
    return cp / P_useful_W


def p_useful(
    efficiency: float,
    P_rated_kW: float = 2.0,
    solar_area_m2: float = 2.5,
    solar_irradiance_W_m2: float = 800.0,
    source_id: str = "",
) -> float:
    """
    Compute useful thermal power delivered to the fluid [W].

    Args:
        efficiency: η (conventional) or COP (heat pump).
        P_rated_kW: Rated electrical or gas input power [kW].
        solar_area_m2: Solar collector area [m²] (solar sources only).
        solar_irradiance_W_m2: Solar irradiance [W/m²] (solar sources only).
        source_id: Source identifier; if 'solar' uses area × irradiance formula.

    Returns:
        Useful thermal power in Watts.
    """
    if source_id == "solar":
        return solar_area_m2 * solar_irradiance_W_m2 * SOLAR_COLLECTOR_EFFICIENCY
    return P_rated_kW * 1000.0 * efficiency


# ---------------------------------------------------------------------------
# Policy scalars
# ---------------------------------------------------------------------------

def tpp(
    price_gas: float,
    cop: float,
    eta_gas: float = 0.45,
) -> dict:
    """
    Thermal Parity Price [€/kWh electricity].  (Formulation eq. 11)

    The electricity price at which a heat pump (COP = β) becomes
    economically equivalent to a gas source. Result is fluid-independent
    (cp cancels exactly — see cp-invariance theorem, Proposition 1).

    Args:
        price_gas: Gas fuel price [€/kWh].
        cop: Coefficient of Performance of the heat pump (> 1).
        eta_gas: Thermal efficiency of the gas appliance (default 0.45
                 for a typical gas stove/boiler).

    Returns:
        Dict with keys:
          'tpp':         Thermal Parity Price [€/kWh]
          'formula':     String showing the calculation
          'interpretation': Human-readable decision rule

    Examples:
        >>> tpp(0.092, 3.0)
        {'tpp': 0.6133..., ...}
    """
    if cop <= 0:
        raise ValueError(f"COP must be > 0, got {cop}")
    # cop = 1.0 is valid: represents an electric resistance heater vs gas
    if eta_gas <= 0 or eta_gas > 1:
        raise ValueError(f"eta_gas must be in (0, 1], got {eta_gas}")

    value = price_gas * cop / eta_gas
    return {
        "tpp": round(value, 6),
        "formula": f"TPP = {price_gas} × {cop} / {eta_gas} = {value:.4f} €/kWh",
        "interpretation": (
            f"If local electricity price < {value:.4f} €/kWh → "
            f"heat pump (COP {cop}) is cheaper than gas."
        ),
    }


def cgit(
    cop: float,
    co2_gas: float = 202.0,
    eta_gas: float = 0.45,
) -> dict:
    """
    Carbon Grid Intensity Threshold [g CO₂/kWh grid].  (Formulation eq. 12)

    The grid CO₂ intensity below which electric heating beats gas
    combustion on carbon emissions. Result is fluid-independent.

    Args:
        cop: COP of the heat pump (use 1.0 for resistance heating).
        co2_gas: Carbon intensity of gas combustion [g CO₂/kWh].
                 Default: 202.0 (IPCC AR6).
        eta_gas: Efficiency of gas appliance (default 0.45).

    Returns:
        Dict with keys:
          'cgit':   Carbon Grid Intensity Threshold [g CO₂/kWh]
          'formula': Calculation string
          'note':   Key implications

    Examples:
        >>> cgit(1.0)   # resistance heater
        {'cgit': 448.9..., ...}
        >>> cgit(3.0)   # heat pump COP 3
        {'cgit': 1346.7..., ...}
    """
    if cop <= 0:
        raise ValueError(f"cop must be > 0, got {cop}")
    if eta_gas <= 0 or eta_gas > 1:
        raise ValueError(f"eta_gas must be in (0, 1], got {eta_gas}")

    value = co2_gas * cop / eta_gas
    device = "resistance heater" if abs(cop - 1.0) < 0.01 else f"heat pump COP {cop}"
    return {
        "cgit": round(value, 2),
        "formula": f"CGIT = {co2_gas} × {cop} / {eta_gas} = {value:.2f} g CO₂/kWh",
        "note": (
            f"Countries with grid CO₂ < {value:.0f} g/kWh benefit from "
            f"switching from gas to {device} on carbon grounds."
        ),
    }


# ---------------------------------------------------------------------------
# Composite TEEI (requires multi-source comparison)
# ---------------------------------------------------------------------------

def _normalise(values: Sequence[float]) -> List[float]:
    """
    Normalise a sequence to [0, 1] where 0 = best (lowest), 1 = worst (highest).
    If all values are equal, returns 1.0 for all (best performance).
    """
    mn, mx = min(values), max(values)
    if math.isclose(mn, mx, rel_tol=1e-9):
        return [1.0] * len(values)
    return [(v - mn) / (mx - mn) for v in values]


def _perf_score(norm_value: float) -> float:
    """Convert normalised value [0=best,1=worst] to performance score [0=worst,100=best]."""
    return round(100.0 * (1.0 - norm_value), 2)


def compute_teei(
    results: List[SubMetricResult],
    weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25),
) -> List[ComparisonResult]:
    """
    Compute normalised TEEI scores across a set of sub-metric results.

    TEEI is meaningful only in a comparative context. Scores are normalised
    against the best and worst source in the provided set.

    This function implements the cp-invariance theorem: because all
    sub-metrics scale linearly with cp, the cp values cancel in
    normalisation and the rankings are fluid-independent.

    Args:
        results: List of SubMetricResult (or JobResult) objects from
                 individual source calculations. Must contain ≥ 2 sources
                 for meaningful normalisation.
        weights: Tuple (w_cost, w_carbon, w_entropy, w_speed).
                 Need not sum to 1; they are normalised internally.
                 Default: equal weighting (0.25, 0.25, 0.25, 0.25).

    Returns:
        List of ComparisonResult, sorted by TEEI score (best first).
        Each object has perf_fteu, perf_ftem, perf_ftes, perf_ftet,
        teei, and rank populated.

    Raises:
        ValueError: If results list has fewer than 2 sources.
    """
    if len(results) < 2:
        raise ValueError(
            "compute_teei requires at least 2 sources for meaningful "
            f"normalisation. Got {len(results)}."
        )

    w1, w2, w3, w4 = weights
    w_total = w1 + w2 + w3 + w4
    if w_total <= 0:
        raise ValueError("Sum of weights must be > 0.")

    # Extract metric vectors
    fteu_vals = [r.fteu for r in results]
    ftem_vals = [r.ftem for r in results]
    ftes_vals = [r.ftes for r in results]
    ftet_vals = [r.ftet for r in results]

    # Normalise each metric (0 = best, 1 = worst)
    n_fteu = _normalise(fteu_vals)
    n_ftem = _normalise(ftem_vals)
    n_ftes = _normalise(ftes_vals)
    n_ftet = _normalise(ftet_vals)

    # Build ComparisonResult objects
    comparison = []
    for i, r in enumerate(results):
        pf = _perf_score(n_fteu[i])
        pm = _perf_score(n_ftem[i])
        pe = _perf_score(n_ftes[i])
        pt = _perf_score(n_ftet[i])
        score = round((w1 * pf + w2 * pm + w3 * pe + w4 * pt) / w_total, 2)

        # Copy all fields from r into a ComparisonResult
        base = r.__dict__.copy() if hasattr(r, '__dict__') else {}
        cr = ComparisonResult(
            fteu=r.fteu, ftem=r.ftem, ftes=r.ftes, ftet=r.ftet,
            cp_eff=r.cp_eff, ftes_model=r.ftes_model,
            source_id=r.source_id, fluid_id=r.fluid_id,
            mass=getattr(r, 'mass', 1.0),
            delta_T=getattr(r, 'delta_T', 1.0),
            t_total=getattr(r, 't_total', r.ftet * getattr(r, 'mass', 1.0) * getattr(r, 'delta_T', 1.0)),
            cost_total=getattr(r, 'cost_total', r.fteu * getattr(r, 'mass', 1.0) * getattr(r, 'delta_T', 1.0)),
            co2_total=getattr(r, 'co2_total', r.ftem * getattr(r, 'mass', 1.0) * getattr(r, 'delta_T', 1.0)),
            single_phase=getattr(r, 'single_phase', True),
            country=getattr(r, 'country', None),
            perf_fteu=pf, perf_ftem=pm, perf_ftes=pe, perf_ftet=pt,
            teei=score,
        )
        comparison.append(cr)

    # Sort best → worst and assign ranks
    comparison.sort(key=lambda x: x.teei, reverse=True)
    for rank, cr in enumerate(comparison, start=1):
        cr.rank = rank

    return comparison
