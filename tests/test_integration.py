"""
Integration tests for teei.calculate() and teei.compare() high-level API,
plus fluids, sources, countries, and phase_check modules.
"""
import math
import pytest
import teei
from teei import calculate, compare, tpp, cgit, phase_check
from teei.phase_check import PhaseChangeError


# ---------------------------------------------------------------------------
# calculate() integration tests
# ---------------------------------------------------------------------------
class TestCalculate:
    def test_basic_water_electric_spain(self):
        r = calculate("water", "electric", country="ES",
                      mass=1.0, delta_T=1.0)
        assert math.isclose(r.fteu, 0.02231, rel_tol=1e-3)
        assert math.isclose(r.ftem, 0.18783, rel_tol=1e-3)
        assert r.ftes > 0
        assert r.ftet > 0
        assert r.single_phase is True
        assert r.source_id == "electric"
        assert r.fluid_id == "water"
        assert r.country == "ES"

    def test_job_totals_scale_with_mass_and_dt(self):
        """cost_total = FTEU × mass × delta_T"""
        r = calculate("water", "electric", country="ES",
                      mass=200.0, delta_T=40.0)
        expected_cost = r.fteu * 200.0 * 40.0
        assert math.isclose(r.cost_total, expected_cost, rel_tol=1e-9)
        expected_time = r.ftet * 200.0 * 40.0
        assert math.isclose(r.t_total, expected_time, rel_tol=1e-9)

    def test_custom_cp_float(self):
        """Accept a direct cp float instead of fluid string."""
        r = calculate(4184.0, "electric", country="ES")
        assert math.isclose(r.cp_eff, 4184.0)

    def test_custom_source_dict(self):
        """Accept a custom source dict with explicit parameters."""
        custom = {
            "efficiency": 2.5,
            "price": 0.20,
            "co2_intensity": 180.0,
            "T_source_K": None,   # will use Model B (COP > 1)
        }
        r = calculate("water", custom, mass=1.0, delta_T=1.0)
        assert r.ftes_model == "B"

    def test_price_override(self):
        """Explicit price overrides country database value."""
        r_country  = calculate("water", "electric", country="ES")
        r_override = calculate("water", "electric", country="ES", price=0.30)
        assert r_override.fteu > r_country.fteu

    def test_co2_override(self):
        r_country  = calculate("water", "electric", country="ES")
        r_override = calculate("water", "electric", country="ES", co2=300.0)
        assert r_override.ftem > r_country.ftem

    def test_phase_check_blocks_boiling(self):
        """Water at 20°C + 90°C rise = 110°C → above boiling point."""
        with pytest.raises(PhaseChangeError):
            calculate("water", "electric", country="ES",
                      T_start=20.0, delta_T=90.0, check_phase=True)

    def test_phase_check_disabled(self):
        """With check_phase=False, no error even above boiling point."""
        r = calculate("water", "electric", country="ES",
                      T_start=20.0, delta_T=90.0, check_phase=False)
        assert r is not None

    def test_solar_uses_area_irradiance_for_time(self):
        """Solar FTET depends on collector area × irradiance, not P_rated."""
        r_small = calculate("water", "solar", country="ES",
                            solar_area=1.0, solar_irradiance=800.0)
        r_large = calculate("water", "solar", country="ES",
                            solar_area=4.0, solar_irradiance=800.0)
        # Larger area → more power → lower FTET (faster heating)
        assert r_large.ftet < r_small.ftet

    def test_teei_score_is_none(self):
        """calculate() does not populate teei — requires compare()."""
        r = calculate("water", "electric", country="ES")
        # JobResult does not have a teei attribute at all
        assert not hasattr(r, "teei") or getattr(r, "teei", "sentinel") == "sentinel"


# ---------------------------------------------------------------------------
# compare() integration tests
# ---------------------------------------------------------------------------
class TestCompare:
    ALL_SOURCES = ["electric", "gas", "solar", "hp3", "hp5"]

    def test_returns_sorted_list(self):
        results = compare("water", self.ALL_SOURCES, country="ES")
        assert len(results) == 5
        scores = [r.teei for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_ranks_are_sequential(self):
        results = compare("water", self.ALL_SOURCES, country="ES")
        assert [r.rank for r in results] == list(range(1, 6))

    def test_all_source_ids_present(self):
        results = compare("water", self.ALL_SOURCES, country="ES")
        ids = {r.source_id for r in results}
        assert ids == set(self.ALL_SOURCES)

    def test_cp_invariance_water_vs_mercury(self):
        """
        THE KEY THEOREM: Rankings must be identical for water and mercury.
        Verifies Proposition 1 (cp-invariance) end-to-end.
        """
        r_water   = compare("water",   self.ALL_SOURCES, country="ES",
                            check_phase=False)
        r_mercury = compare("mercury", self.ALL_SOURCES, country="ES",
                            check_phase=False)

        ranking_water   = [r.source_id for r in r_water]
        ranking_mercury = [r.source_id for r in r_mercury]

        assert ranking_water == ranking_mercury, (
            f"cp-invariance FAILED in compare()!\n"
            f"  water:   {ranking_water}\n"
            f"  mercury: {ranking_mercury}"
        )

    def test_requires_two_sources(self):
        with pytest.raises(ValueError, match="at least 2"):
            compare("water", ["electric"])

    def test_weight_cost_only_ranks_by_fteu(self):
        """With all weight on cost, cheapest FTEU source must rank #1."""
        results = compare("water", self.ALL_SOURCES, country="ES",
                          weights=(1.0, 0.0, 0.0, 0.0))
        best = results[0]
        # HP5 has lowest FTEU (P/COP is smallest)
        assert best.source_id == "hp5"

    def test_weight_carbon_only_ranks_by_ftem(self):
        """With all weight on carbon, solar must rank first (lowest FTEM)."""
        results = compare("water", self.ALL_SOURCES, country="ES",
                          weights=(0.0, 1.0, 0.0, 0.0))
        best = results[0]
        assert best.source_id == "solar"

    def test_weight_speed_only_ranks_by_ftet(self):
        """With all weight on speed, HP5 must rank first (highest useful power)."""
        results = compare("water", self.ALL_SOURCES, country="ES",
                          weights=(0.0, 0.0, 0.0, 1.0))
        best = results[0]
        assert best.source_id == "hp5"

    def test_gas_worst_on_carbon(self):
        """Gas must rank last when only carbon is weighted."""
        results = compare("water", self.ALL_SOURCES, country="ES",
                          weights=(0.0, 1.0, 0.0, 0.0))
        assert results[-1].source_id == "gas"

    def test_germany_different_from_france(self):
        """
        Sanity check: TEEI absolute scores differ between DE and FR
        because grid CO₂ intensities differ (350 vs 52 g/kWh).
        Rankings may or may not differ — but scores must differ.
        """
        de = compare("water", self.ALL_SOURCES, country="DE")
        fr = compare("water", self.ALL_SOURCES, country="FR")
        de_scores = {r.source_id: r.teei for r in de}
        fr_scores = {r.source_id: r.teei for r in fr}
        # Scores should not all be identical
        assert de_scores != fr_scores


# ---------------------------------------------------------------------------
# Fluid database tests
# ---------------------------------------------------------------------------
class TestFluids:
    def test_list_fluids_not_empty(self):
        fluids = teei.list_fluids()
        assert len(fluids) >= 10

    def test_water_in_list(self):
        assert "water" in teei.list_fluids()

    def test_get_fluid_water(self):
        f = teei.get_fluid("water")
        assert f["cp"] == 4184.0
        assert f["T_boil_C"] == 100.0

    def test_get_fluid_unknown_raises(self):
        with pytest.raises(KeyError, match="not found"):
            teei.get_fluid("unobtanium")

    def test_resolve_cp_string(self):
        assert teei.resolve_cp("water") == 4184.0

    def test_resolve_cp_float(self):
        assert teei.resolve_cp(3000.0) == 3000.0

    def test_resolve_cp_negative_raises(self):
        with pytest.raises(ValueError):
            teei.resolve_cp(-100.0)


# ---------------------------------------------------------------------------
# Phase check tests
# ---------------------------------------------------------------------------
class TestPhaseCheck:
    def test_water_safe_range(self):
        # T_target = 20 + 50 = 70°C — well below 0.85×100 = 85°C limit
        r = phase_check("water", T_start_C=20, delta_T=50)
        assert r.valid is True
        assert r.warning is None

    def test_water_above_boiling(self):
        r = phase_check("water", T_start_C=20, delta_T=85)
        assert r.valid is False
        assert "boiling" in r.warning.lower() or "phase" in r.warning.lower()

    def test_water_above_safety_margin(self):
        """0.85 × 100°C = 85°C limit. T_target = 87°C should fail."""
        r = phase_check("water", T_start_C=10, delta_T=77)
        assert r.valid is False

    def test_water_below_safety_margin(self):
        """T_target = 80°C < 85°C limit → valid."""
        r = phase_check("water", T_start_C=20, delta_T=60)
        assert r.valid is True

    def test_ethanol_near_boiling(self):
        """Ethanol boils at 78.4°C. T_target = 70°C → should fail margin check."""
        r = phase_check("ethanol", T_start_C=20, delta_T=50)
        # 0.85 × 78.4 = 66.6°C limit; T_target = 70°C → invalid
        assert r.valid is False

    def test_custom_cp_no_boiling_check(self):
        """Custom cp float has no known boiling point — returns valid with warning."""
        r = phase_check(4184.0, T_start_C=20, delta_T=200)
        assert r.valid is True
        assert r.T_boil_C is None
        assert r.warning is not None

    def test_t_start_equals_t_target_raises(self):
        with pytest.raises(ValueError, match="T_start"):
            phase_check("water", T_start_C=50, T_target_C=50)


# ---------------------------------------------------------------------------
# Countries database tests
# ---------------------------------------------------------------------------
class TestCountries:
    def test_list_countries(self):
        countries = teei.list_countries()
        assert "ES" in countries
        assert "DE" in countries
        assert len(countries) >= 15

    def test_get_spain(self):
        c = teei.get_country("ES")
        assert c["name"] == "Spain"
        assert c["electricity_price"] > 0
        assert c["gas_price"] > 0
        assert c["grid_co2"] > 0

    def test_case_insensitive(self):
        c1 = teei.get_country("ES")
        c2 = teei.get_country("es")
        assert c1["name"] == c2["name"]

    def test_unknown_country_raises(self):
        with pytest.raises(KeyError, match="not in database"):
            teei.get_country("XX")

    def test_database_info(self):
        info = teei.database_info()
        assert "version" in info
        assert info["country_count"] >= 15

    def test_france_lower_co2_than_poland(self):
        fr = teei.get_country("FR")
        pl = teei.get_country("PL")
        assert fr["grid_co2"] < pl["grid_co2"]


# ---------------------------------------------------------------------------
# TPP and CGIT with country context
# ---------------------------------------------------------------------------
class TestPolicyScalarsWithCountry:
    def test_tpp_spain(self):
        result = tpp(country="ES", cop=3.0)
        assert math.isclose(result["tpp"], 0.6133, rel_tol=1e-2)
        assert result["hp_wins"] is True  # Spain P_elec 0.19 < TPP 0.61

    def test_tpp_includes_local_price(self):
        result = tpp(country="DE", cop=3.0)
        assert result["local_elec_price"] is not None
        assert result["country"] == "DE"

    def test_cgit_with_countries(self):
        result = cgit(cop=1.0)
        assert "country_comparison" in result
        assert "ES" in result["country_comparison"]
        # Spain grid_co2 (160) < CGIT (449) → should electrify
        assert result["country_comparison"]["ES"]["should_electrify"] is True
        # Poland grid_co2 (695) > CGIT (449) → gas still wins on carbon
        assert result["country_comparison"]["PL"]["should_electrify"] is False
