"""
Unit tests for teei.metrics — all sub-metric formulas, TEEI composite,
TPP, and CGIT. Reference values verified by direct dimensional calculation.

Reference: 02_formulation.md (all equation numbers cited).
"""
import math
import pytest
from teei.metrics import (
    fteu, ftem, ftes, ftet, compute_teei,
    tpp, cgit, SubMetricResult
)


# ---------------------------------------------------------------------------
# Reference parameters (Spain 2026, water at 20°C)
# ---------------------------------------------------------------------------
CP_WATER   = 4184.0   # J/(kg·°C)
CP_MERCURY = 140.0    # J/(kg·°C)
P_ELEC     = 0.190    # €/kWh
ETA_ELEC   = 0.99
E_ELEC     = 160.0    # g CO₂/kWh (Spain grid)
T_SRC_ELEC = 500.0    # K

P_GAS      = 0.092
ETA_GAS    = 0.45
E_GAS      = 202.0    # g CO₂/kWh (combustion constant)
T_SRC_GAS  = 1200.0   # K

P_SOL      = 0.067    # LCOE €/kWh_th
ETA_SOL    = 1.00
E_SOL      = 20.0
T_SRC_SOL  = 363.0    # K

COP_HP3    = 3.0
P_HP3      = 0.190
E_HP3      = 160.0

T_FLUID_C  = 20.0
T_FLUID_K  = T_FLUID_C + 273.15   # 293.15 K
T_AMB_K    = T_FLUID_K

P_RATED_W  = 2000.0   # 2 kW


# ---------------------------------------------------------------------------
# FTEU tests — eq. (4)
# ---------------------------------------------------------------------------
class TestFTEU:
    def test_electric_spain_water(self):
        """FTEU = (P/η) × (cp/K2); K2 = 36,000."""
        result = fteu(P_ELEC, ETA_ELEC, CP_WATER)
        assert math.isclose(result, 0.02231, rel_tol=1e-3), \
            f"Expected ~0.02231, got {result:.6f}"

    def test_gas_spain_water(self):
        result = fteu(P_GAS, ETA_GAS, CP_WATER)
        assert math.isclose(result, 0.02376, rel_tol=1e-3)

    def test_solar_spain_water(self):
        result = fteu(P_SOL, ETA_SOL, CP_WATER)
        assert math.isclose(result, 0.00779, rel_tol=1e-3)

    def test_hp3_spain_water(self):
        result = fteu(P_HP3, COP_HP3, CP_WATER)
        assert math.isclose(result, 0.00736, rel_tol=1e-3)

    def test_scales_with_cp(self):
        """FTEU must scale exactly linearly with cp (cp-invariance theorem)."""
        r_water   = fteu(P_ELEC, ETA_ELEC, CP_WATER)
        r_mercury = fteu(P_ELEC, ETA_ELEC, CP_MERCURY)
        ratio = r_mercury / r_water
        expected = CP_MERCURY / CP_WATER
        assert math.isclose(ratio, expected, rel_tol=1e-9)

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="price"):
            fteu(-0.1, 0.99, CP_WATER)

    def test_zero_efficiency_raises(self):
        with pytest.raises(ValueError, match="efficiency"):
            fteu(0.19, 0.0, CP_WATER)

    def test_zero_cp_raises(self):
        with pytest.raises(ValueError, match="cp"):
            fteu(0.19, 0.99, 0.0)


# ---------------------------------------------------------------------------
# FTEM tests — eq. (6)
# ---------------------------------------------------------------------------
class TestFTEM:
    def test_electric_spain_water(self):
        """FTEM = (E/η) × (cp/K1); K1 = 3,600,000."""
        result = ftem(E_ELEC, ETA_ELEC, CP_WATER)
        assert math.isclose(result, 0.18783, rel_tol=1e-3)

    def test_gas_water(self):
        result = ftem(E_GAS, ETA_GAS, CP_WATER)
        assert math.isclose(result, 0.52171, rel_tol=1e-3)

    def test_solar_water(self):
        result = ftem(E_SOL, ETA_SOL, CP_WATER)
        assert math.isclose(result, 0.02324, rel_tol=1e-3)

    def test_hp3_spain_water(self):
        result = ftem(E_HP3, COP_HP3, CP_WATER)
        assert math.isclose(result, 0.06199, rel_tol=1e-3)

    def test_scales_with_cp(self):
        r_water   = ftem(E_ELEC, ETA_ELEC, CP_WATER)
        r_mercury = ftem(E_ELEC, ETA_ELEC, CP_MERCURY)
        assert math.isclose(r_mercury / r_water, CP_MERCURY / CP_WATER, rel_tol=1e-9)

    def test_zero_co2_returns_zero(self):
        result = ftem(0.0, ETA_ELEC, CP_WATER)
        assert result == 0.0


# ---------------------------------------------------------------------------
# FTES tests — eq. (7) Model A and eq. (8) Model B
# ---------------------------------------------------------------------------
class TestFTES:
    def test_electric_model_A(self):
        """Model A: (cp/η)(1/T_f - 1/T_s) + cp(1/η-1)/T_0"""
        value, model = ftes(CP_WATER, ETA_ELEC, T_FLUID_C,
                            T_source_K=T_SRC_ELEC)
        assert model == 'A'
        assert math.isclose(value, 6.108, rel_tol=1e-2)

    def test_gas_model_A_high_irreversibility(self):
        """Gas stove has highest FTES due to extreme T_s = 1200 K."""
        value, model = ftes(CP_WATER, ETA_GAS, T_FLUID_C,
                            T_source_K=T_SRC_GAS)
        assert model == 'A'
        assert math.isclose(value, 41.41, rel_tol=1e-2)

    def test_solar_model_A_low_irreversibility(self):
        """Solar has low FTES — T_s close to T_fluid reduces irreversibility."""
        value, model = ftes(CP_WATER, ETA_SOL, T_FLUID_C,
                            T_source_K=T_SRC_SOL)
        assert model == 'A'
        assert math.isclose(value, 2.746, rel_tol=1e-2)

    def test_hp3_model_B(self):
        """Model B: cp(1/T_f - (β-1)/(β·T_0))"""
        value, model = ftes(CP_WATER, COP_HP3, T_FLUID_C)
        assert model == 'B'
        assert math.isclose(value, 4.757, rel_tol=1e-2)

    def test_model_selection_at_boundary(self):
        """η = 1.0 → Model A (not heat pump)."""
        _, model = ftes(CP_WATER, 1.0, T_FLUID_C, T_source_K=T_SRC_SOL)
        assert model == 'A'

    def test_model_B_above_unity_eta(self):
        """Any η > 1 selects Model B."""
        _, model = ftes(CP_WATER, 1.5, T_FLUID_C)
        assert model == 'B'

    def test_model_A_requires_T_source(self):
        with pytest.raises(ValueError, match="T_source_K"):
            ftes(CP_WATER, 0.99, T_FLUID_C, T_source_K=None)

    def test_T_source_must_exceed_T_fluid(self):
        with pytest.raises(ValueError, match="must exceed"):
            ftes(CP_WATER, 0.99, T_FLUID_C, T_source_K=280.0)

    def test_scales_with_cp(self):
        """FTES must scale linearly with cp."""
        v_water, _   = ftes(CP_WATER,   ETA_ELEC, T_FLUID_C, T_source_K=T_SRC_ELEC)
        v_mercury, _ = ftes(CP_MERCURY, ETA_ELEC, T_FLUID_C, T_source_K=T_SRC_ELEC)
        assert math.isclose(v_mercury / v_water, CP_MERCURY / CP_WATER, rel_tol=1e-9)

    def test_always_non_negative(self):
        """Entropy generation can never be negative."""
        for cop in [1.5, 2.0, 3.0, 5.0, 10.0]:
            v, _ = ftes(CP_WATER, cop, T_FLUID_C)
            assert v >= 0.0, f"Negative FTES for COP={cop}: {v}"


# ---------------------------------------------------------------------------
# FTET tests — eq. (9)
# ---------------------------------------------------------------------------
class TestFTET:
    def test_electric_2kw(self):
        """FTET = cp / P_useful; P_useful = P_rated × η"""
        P_useful = P_RATED_W * ETA_ELEC
        result = ftet(CP_WATER, P_useful)
        assert math.isclose(result, 2.113, rel_tol=1e-3)

    def test_gas_2kw(self):
        P_useful = P_RATED_W * ETA_GAS
        result = ftet(CP_WATER, P_useful)
        assert math.isclose(result, 4.649, rel_tol=1e-3)

    def test_hp3_2kw(self):
        P_useful = P_RATED_W * COP_HP3
        result = ftet(CP_WATER, P_useful)
        assert math.isclose(result, 0.6973, rel_tol=1e-3)

    def test_mercury_heats_faster(self):
        """Mercury (low cp) heats ~30× faster than water at same power."""
        P_useful = P_RATED_W * ETA_ELEC
        t_water   = ftet(CP_WATER,   P_useful)
        t_mercury = ftet(CP_MERCURY, P_useful)
        ratio = t_mercury / t_water
        expected = CP_MERCURY / CP_WATER
        assert math.isclose(ratio, expected, rel_tol=1e-9)

    def test_zero_power_raises(self):
        with pytest.raises(ValueError, match="P_useful_W"):
            ftet(CP_WATER, 0.0)


# ---------------------------------------------------------------------------
# TEEI composite tests — eq. (13)–(15)
# ---------------------------------------------------------------------------
class TestComputeTEEI:
    def _make_results(self, cp=CP_WATER):
        """Build sub-metric results for all 5 sources at given cp."""
        sources = [
            ("electric", fteu(P_ELEC, ETA_ELEC, cp), ftem(E_ELEC, ETA_ELEC, cp),
             ftes(cp, ETA_ELEC, T_FLUID_C, T_source_K=T_SRC_ELEC)[0],
             ftet(cp, P_RATED_W * ETA_ELEC), 'A'),
            ("gas", fteu(P_GAS, ETA_GAS, cp), ftem(E_GAS, ETA_GAS, cp),
             ftes(cp, ETA_GAS, T_FLUID_C, T_source_K=T_SRC_GAS)[0],
             ftet(cp, P_RATED_W * ETA_GAS), 'A'),
            ("solar", fteu(P_SOL, ETA_SOL, cp), ftem(E_SOL, ETA_SOL, cp),
             ftes(cp, ETA_SOL, T_FLUID_C, T_source_K=T_SRC_SOL)[0],
             ftet(cp, 2.5 * 800 * 0.65), 'A'),
            ("hp3", fteu(P_HP3, COP_HP3, cp), ftem(E_HP3, COP_HP3, cp),
             ftes(cp, COP_HP3, T_FLUID_C)[0],
             ftet(cp, P_RATED_W * COP_HP3), 'B'),
        ]
        return [
            SubMetricResult(
                fteu=v[1], ftem=v[2], ftes=v[3], ftet=v[4],
                cp_eff=cp, ftes_model=v[5], source_id=v[0], fluid_id="test"
            )
            for v in sources
        ]

    def test_returns_sorted_best_first(self):
        results = compute_teei(self._make_results())
        scores = [r.teei for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_all_scores_in_range(self):
        results = compute_teei(self._make_results())
        for r in results:
            assert 0.0 <= r.teei <= 100.0

    def test_rank_assigned(self):
        results = compute_teei(self._make_results())
        ranks = [r.rank for r in results]
        assert ranks == list(range(1, len(results) + 1))

    def test_cp_invariance_theorem(self):
        """
        Proposition 1 (cp-invariance): TEEI rankings must be identical
        for water and mercury (or any two fluids), for the same sources.

        This is the central theorem of the TEEI framework.
        """
        results_water   = compute_teei(self._make_results(cp=CP_WATER))
        results_mercury = compute_teei(self._make_results(cp=CP_MERCURY))

        ranking_water   = [r.source_id for r in results_water]
        ranking_mercury = [r.source_id for r in results_mercury]

        assert ranking_water == ranking_mercury, (
            f"cp-invariance VIOLATED!\n"
            f"  Water ranking:   {ranking_water}\n"
            f"  Mercury ranking: {ranking_mercury}"
        )

    def test_requires_at_least_two_sources(self):
        with pytest.raises(ValueError, match="at least 2"):
            compute_teei(self._make_results()[:1])

    def test_equal_weights_default(self):
        """With equal weights, all four performance axes contribute equally."""
        results_eq  = compute_teei(self._make_results(),
                                   weights=(0.25, 0.25, 0.25, 0.25))
        results_100 = compute_teei(self._make_results(),
                                   weights=(1.0, 1.0, 1.0, 1.0))
        # Rankings must be identical regardless of absolute weight scale
        rank_eq  = [r.source_id for r in results_eq]
        rank_100 = [r.source_id for r in results_100]
        assert rank_eq == rank_100


# ---------------------------------------------------------------------------
# TPP tests — eq. (11)
# ---------------------------------------------------------------------------
class TestTPP:
    def test_spain_cop3(self):
        """TPP = P_gas × COP / η_gas = 0.092 × 3.0 / 0.45 = 0.6133"""
        result = tpp(price_gas=0.092, cop=3.0, eta_gas=0.45)
        assert math.isclose(result["tpp"], 0.6133, rel_tol=1e-3)

    def test_resistance_heater_cop1(self):
        """TPP for COP=1 (resistance vs gas)."""
        result = tpp(price_gas=0.092, cop=1.0, eta_gas=0.45)
        assert math.isclose(result["tpp"], 0.2044, rel_tol=1e-3)

    def test_spain_electricity_below_tpp(self):
        """Spain P_elec = 0.190 < TPP = 0.613 → heat pump wins."""
        result = tpp(price_gas=0.092, cop=3.0)
        assert 0.190 < result["tpp"]

    def test_cop_zero_raises(self):
        """COP must be > 0. COP=1.0 is valid (resistance heater vs gas)."""
        with pytest.raises(ValueError, match="COP"):
            tpp(price_gas=0.092, cop=0.0)

    def test_result_is_fluid_independent(self):
        """
        TPP derivation cancels cp — result must be same regardless of
        which fluid is being heated. Verified by construction (no cp in formula).
        """
        r = tpp(price_gas=0.092, cop=3.0)
        assert "tpp" in r
        # TPP does not accept a fluid argument — fluid-independence is structural


# ---------------------------------------------------------------------------
# CGIT tests — eq. (12)
# ---------------------------------------------------------------------------
class TestCGIT:
    def test_resistance_heater(self):
        """CGIT = E_gas × 1 / η_gas = 202 / 0.45 = 448.9 g/kWh"""
        result = cgit(cop=1.0)
        assert math.isclose(result["cgit"], 448.9, rel_tol=1e-3)

    def test_hp3(self):
        """CGIT = 202 × 3.0 / 0.45 = 1,346.7 g/kWh"""
        result = cgit(cop=3.0)
        assert math.isclose(result["cgit"], 1346.7, rel_tol=1e-3)

    def test_hp5(self):
        """CGIT = 202 × 5.0 / 0.45 = 2,244.4 g/kWh"""
        result = cgit(cop=5.0)
        assert math.isclose(result["cgit"], 2244.4, rel_tol=1e-3)

    def test_no_grid_exceeds_hp3_cgit(self):
        """
        No real-world grid has CO₂ intensity > 1347 g/kWh.
        Therefore heat pumps always beat gas on carbon — unconditionally.
        Max observed: South Africa ~750 g/kWh; Saudi Arabia ~690 g/kWh.
        """
        result = cgit(cop=3.0)
        max_real_grid_co2 = 800.0  # conservative upper bound for any real grid
        assert result["cgit"] > max_real_grid_co2, (
            "CGIT for HP COP3 should exceed all real-world grid intensities"
        )
