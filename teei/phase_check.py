"""
Single-phase validity checker for the TEEI framework.

The TEEI framework is defined exclusively for single-phase sensible-heat
processes. This module validates that a given heating job remains within
the liquid phase throughout, based on the fluid's boiling point.

Validity condition (Formulation doc eq. 2):
    T_start < T_target < 0.85 × T_boil(P_atm)

The 0.85 safety factor provides a conservative margin below the boiling
point to avoid flash evaporation, local boiling, and c_p divergence
near saturation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from .fluids import get_boiling_point, get_fluid


SINGLE_PHASE_MARGIN: float = 0.85
"""
Safety factor applied to the boiling point.
T_target must stay below SINGLE_PHASE_MARGIN × T_boil.
Default: 0.85 (conservative; covers most practical heating scenarios).
"""


@dataclass
class PhaseCheckResult:
    """Result of a single-phase validity check."""
    valid: bool
    """True if the heating job remains in the single-phase liquid region."""

    T_start_C: float
    """Fluid starting temperature [°C]."""

    T_target_C: float
    """Target (end) temperature [°C]."""

    T_boil_C: Optional[float]
    """Boiling point of the fluid at 1 atm [°C]. None for custom cp inputs."""

    T_limit_C: Optional[float]
    """Maximum allowable temperature = SINGLE_PHASE_MARGIN × T_boil [°C].
    None if T_boil is unknown."""

    warning: Optional[str]
    """Human-readable warning message if valid is False or close to limit."""

    def __str__(self) -> str:
        status = "✓ Single-phase" if self.valid else "✗ Phase change risk"
        msg = f"{status}: T_start={self.T_start_C}°C, T_target={self.T_target_C}°C"
        if self.T_limit_C is not None:
            msg += f", T_limit={self.T_limit_C:.1f}°C"
        if self.warning:
            msg += f"\n  Warning: {self.warning}"
        return msg


def check(
    fluid: Union[str, float],
    T_start_C: float,
    T_target_C: Optional[float] = None,
    delta_T: Optional[float] = None,
    margin: float = SINGLE_PHASE_MARGIN,
) -> PhaseCheckResult:
    """
    Validate that a heating job remains within the single-phase liquid range.

    Provide either T_target_C or delta_T (not both). If both are provided,
    T_target_C takes precedence.

    Args:
        fluid: Fluid ID string or numeric cp value.
               For numeric cp, boiling point is unknown → returns valid=True
               with a note that no check was possible.
        T_start_C: Starting temperature of the fluid [°C].
        T_target_C: Target (end) temperature [°C]. Provide this OR delta_T.
        delta_T: Temperature rise [°C]. Provide this OR T_target_C.
        margin: Safety factor applied to boiling point (default 0.85).
                T_target must be < margin × T_boil.

    Returns:
        PhaseCheckResult with valid, T_boil_C, T_limit_C, and warning fields.

    Raises:
        ValueError: If neither T_target_C nor delta_T is provided, or if
                    T_start_C >= T_target_C.

    Examples:
        >>> check('water', T_start_C=20, delta_T=70)
        PhaseCheckResult(valid=True, ...)

        >>> check('water', T_start_C=20, delta_T=85)
        PhaseCheckResult(valid=False, warning='T_target 105°C exceeds ...')

        >>> check('ethanol', T_start_C=20, T_target_C=70)
        PhaseCheckResult(valid=False, warning='T_target 70°C is above ...')
    """
    # Resolve target temperature
    if T_target_C is None and delta_T is None:
        raise ValueError("Provide either T_target_C or delta_T.")
    if T_target_C is None:
        T_target_C = T_start_C + delta_T

    if T_start_C >= T_target_C:
        raise ValueError(
            f"T_start_C ({T_start_C}) must be less than T_target_C ({T_target_C}). "
            "TEEI models heating (positive ΔT) only."
        )

    # Custom numeric cp — no boiling point available
    if isinstance(fluid, (int, float)):
        return PhaseCheckResult(
            valid=True,
            T_start_C=T_start_C,
            T_target_C=T_target_C,
            T_boil_C=None,
            T_limit_C=None,
            warning=(
                "Boiling point unknown for custom cp input. "
                "Ensure T_target is well below the fluid's boiling point."
            ),
        )

    # Database lookup
    entry = get_fluid(fluid)
    T_boil = entry.get("T_boil_C")
    T_min = entry.get("T_min_C", -273.15)
    T_limit = margin * T_boil if T_boil is not None else None

    warning = None
    valid = True

    # Check lower bound
    if T_start_C < T_min:
        valid = False
        warning = (
            f"T_start {T_start_C}°C is below the minimum single-phase "
            f"temperature for {entry['name']} ({T_min}°C). "
            f"Fluid may be solid or in a different phase."
        )

    # Check upper bound against hard boiling point
    elif T_boil is not None and T_target_C >= T_boil:
        valid = False
        warning = (
            f"T_target {T_target_C}°C meets or exceeds the boiling point of "
            f"{entry['name']} ({T_boil}°C at 1 atm). Phase change will occur. "
            f"TEEI is defined for single-phase sensible-heat only."
        )

    # Check against conservative limit (margin × T_boil)
    elif T_limit is not None and T_target_C > T_limit:
        valid = False
        warning = (
            f"T_target {T_target_C}°C exceeds the recommended single-phase "
            f"limit of {T_limit:.1f}°C ({margin*100:.0f}% of boiling point "
            f"{T_boil}°C for {entry['name']}). Risk of local boiling and "
            f"c_p divergence. Reduce T_target or use pressurised system."
        )

    # Near-limit advisory (within 10°C of margin limit)
    elif T_limit is not None and T_target_C > T_limit - 10:
        warning = (
            f"T_target {T_target_C}°C is within 10°C of the recommended "
            f"single-phase limit ({T_limit:.1f}°C). Proceed with caution."
        )

    return PhaseCheckResult(
        valid=valid,
        T_start_C=T_start_C,
        T_target_C=T_target_C,
        T_boil_C=T_boil,
        T_limit_C=T_limit,
        warning=warning,
    )


def assert_single_phase(
    fluid: Union[str, float],
    T_start_C: float,
    T_target_C: Optional[float] = None,
    delta_T: Optional[float] = None,
) -> None:
    """
    Raise PhaseChangeError if the heating job exits the single-phase region.

    Convenience wrapper around check() for use inside calculate().

    Raises:
        PhaseChangeError: If check() returns valid=False.
    """
    result = check(fluid, T_start_C, T_target_C, delta_T)
    if not result.valid:
        raise PhaseChangeError(result.warning or "Phase change detected.")


class PhaseChangeError(ValueError):
    """
    Raised when a heating job exits the single-phase liquid region.

    The TEEI framework is defined only for single-phase sensible-heat
    processes. Use check() for a non-raising version.
    """
    pass
