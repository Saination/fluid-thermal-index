"""
Physical and dimensional constants for the TEEI framework.

All constants are derived from SI definitions and unit conversions.
Documented in 02_formulation.md, Section 1.4.
"""

# ---------------------------------------------------------------------------
# Unit conversion constants
# ---------------------------------------------------------------------------

K1: float = 3_600_000.0
"""Joules per kWh (1 kWh = 3.6 × 10⁶ J).
Used for FTEM [g CO₂/kg·°C] = (E/η) × (cp / K1).
Also used for FTEU in €/kg·°C if preferred.
"""

K2: float = 36_000.0
"""Joules per kWh divided by 100 cents per euro (K1 / 100 = 36,000).
Used for FTEU [¢/kg·°C] = (P/η) × (cp / K2).

Derivation:
  FTEU [¢/kg·°C] = (P [€/kWh] / η) × (cp [J/kg·°C]) / (3,600,000 [J/kWh]) × 100 [¢/€]
                 = (P/η) × (cp / 36,000)
"""

KELVIN_OFFSET: float = 273.15
"""Offset to convert Celsius to Kelvin: T[K] = T[°C] + 273.15."""

# ---------------------------------------------------------------------------
# Reference carbon intensities (fixed by physical/chemical constants)
# ---------------------------------------------------------------------------

CO2_NATURAL_GAS: float = 202.0
"""Carbon intensity of natural gas combustion [g CO₂/kWh_fuel].
Source: IPCC AR6 Working Group III (2022), Chapter 9.
This is a physical constant of combustion chemistry and does not vary
by country or year (unlike grid electricity CO₂ intensity).
"""

CO2_SOLAR_LIFECYCLE: float = 20.0
"""Lifecycle carbon intensity of solar thermal energy [g CO₂/kWh_thermal].
Represents amortised manufacturing + installation + end-of-life.
Literature range: 15–30 g CO₂/kWh. Central estimate 20 used.
Source: Lamnatou et al. (2015), Renewable & Sustainable Energy Reviews.
"""

# ---------------------------------------------------------------------------
# Default source temperatures (Kelvin) for FTES Model A
# ---------------------------------------------------------------------------

T_SOURCE_ELECTRIC: float = 500.0
"""Effective surface temperature of electric resistance heating element [K].
Corresponds to approximately 227°C element surface temperature.
"""

T_SOURCE_GAS: float = 1200.0
"""Effective temperature of gas flame impingement on vessel [K].
Corresponds to ~927°C — representative of hot combustion gas
at point of contact with pot or boiler surface.
"""

T_SOURCE_SOLAR: float = 363.0
"""Peak fluid temperature in solar flat-plate collector [K].
Corresponds to ~90°C — typical maximum in domestic flat-plate systems.
"""

# ---------------------------------------------------------------------------
# Default solar parameters
# ---------------------------------------------------------------------------

SOLAR_COLLECTOR_EFFICIENCY: float = 0.65
"""Thermal efficiency of flat-plate solar collector (dimensionless).
Ratio of useful heat output to incident solar radiation.
Typical range for flat-plate collectors: 0.60–0.70.
"""

DEFAULT_SOLAR_IRRADIANCE: float = 800.0
"""Default solar irradiance [W/m²].
Representative of mid-latitude peak conditions (Spain, southern Europe).
"""
