# TEEI — Theory and Formulation
## Thermal Economic-Environmental Index for Fluid Heating Systems

**Version:** 0.2 | **Last updated:** August 2026

---

## 1. Physical foundation

### 1.1 The thermal primitive

The calorie (cal) is defined as the heat required to raise 1 gram of
water by 1°C at ~15°C. In SI units:

    1 cal = 4.184 J

For any single-phase liquid of mass m [kg] heated by ΔT [°C], the
sensible thermal energy required is:

    Q = m · c_p · ΔT        [J]                               (1)

where c_p is the isobaric specific heat capacity [J/kg·°C].
This is the fundamental relation on which all TEEI sub-metrics rest.

### 1.2 Single-phase scope (agreed boundary)

**The TEEI framework is defined exclusively for single-phase sensible-heat
processes.** The working fluid must remain in the liquid state throughout
the heating process. Phase change (boiling, condensation, freezing) is
explicitly excluded.

**Validity condition:**

    T_start < T_target < 0.85 · T_boil(P)                    (2)

where T_boil(P) is the boiling point at operating pressure P.

**Rationale:** Phase change introduces latent heat L that is typically
5–20× larger than c_p·ΔT for practical ΔT values and does not follow
the linear c_p scaling that underpins the cp-invariance theorem.
The single-phase constraint is satisfied by the vast majority of
domestic, commercial, and SME heating applications.

### 1.3 Effective specific heat for variable c_p

Within the single-phase range, c_p varies with temperature. For most
industrial liquids this variation is 1–5% over typical operating ranges
(water: <1% over 0–100°C; glycols: ~3%; oils: ~5%). A single effective
value is defined as the mean over the operating range:

    c_p,eff = (1/ΔT) × ∫[T₁ to T₁+ΔT] c_p(T) dT            (3)

**In all formulae that follow, c_p denotes c_p,eff.** The cp-invariance
theorem (Section 5) holds identically with this substitution.

For practical calculations, c_p,eff is well approximated by evaluating
c_p at the arithmetic mean temperature T_mean = T₁ + ΔT/2.

### 1.4 Unit conversion constants

Three dimensional constants appear throughout the TEEI sub-metric
formulae. They are fixed by physics and unit choices:

| Constant | Value | Origin |
|----------|-------|--------|
| K₁ = 3,600,000 | J/kWh | 1 kWh = 3.6 × 10⁶ J |
| K₂ = 36,000 | J/kWh ÷ 100 ¢/€ | K₁ ÷ 100 (converts € to ¢) |
| K₃ = 3,600,000 | J/kWh (same as K₁) | Used for mass-based CO₂ metric |

---

## 2. Primary sub-metrics

### 2.1 FTEU — Fluid Thermal Economic Unit

**Definition:** Cost in euro-cents to raise 1 kg of fluid by 1°C, given
a heating source with fuel price P and thermal efficiency η.

    FTEU = (P / η) · (c_p / 36,000)                              (4)

    FTEU [¢/kg·°C] = (P [€/kWh] / η [-]) · (c_p [J/kg·°C] / 36,000)

| Symbol | Meaning | Unit |
|--------|---------|------|
| P | Fuel or electricity price | €/kWh |
| η | Thermal efficiency (≤1) or COP (>1 for heat pumps) | — |
| c_p | Effective specific heat of fluid | J/kg·°C |

**Total cost for a heating job:**

    Cost_total = FTEU × m × ΔT     [euro-cents]              (5)

**Notes:**
- For heat pumps: η = COP (e.g., COP 3 → η = 3.0, giving P/η = P/3)
- For solar thermal: P is the amortised LCOE [€/kWh_th]; η = 1.0
  (efficiency already embedded in the LCOE calculation)
- Relation to LCOH: FTEU = LCOH × c_p / K₂ (direct rescaling)

---

### 2.2 FTEM — Fluid Thermal Emission Metric

**Definition:** CO₂ emitted (grams) to raise 1 kg of fluid by 1°C.

    FTEM = (E / η) · (c_p / K₁)                              (6)

    FTEM [g CO₂/kg·°C] = (E [g CO₂/kWh] / η [-]) · (c_p [J/kg·°C] / 3,600,000)

| Symbol | Meaning | Unit |
|--------|---------|------|
| E | Carbon intensity of energy source | g CO₂/kWh |
| η | Thermal efficiency or COP | — |
| c_p | Effective specific heat of fluid | J/kg·°C |

**Reference carbon intensities:**

| Source | E (g CO₂/kWh) | Basis |
|--------|-------------|-------|
| Natural gas combustion | 202 | IPCC AR6, constant (combustion chemistry) |
| Solar thermal (lifecycle) | 15–30 (use 20) | Literature range, see references |
| Grid electricity | Country-specific | EMBER API; varies 30–750 g/kWh |

**Note:** Grid CO₂ intensity is the most geographically sensitive parameter
in the entire TEEI framework. It varies by a factor of ~25 across countries
(France ~50 g/kWh nuclear-heavy vs Poland ~700 g/kWh coal-heavy in 2026).

---

### 2.3 FTES — Fluid Thermal Entropy Score

**Definition:** Entropy generated per kg of fluid per °C of temperature
rise, capturing thermodynamic irreversibility of the heating process.

Two models are required depending on device type:

**Model A — Conventional heater (η ≤ 1):**

    FTES = (c_p/η) · (1/T_f − 1/T_s) + c_p · (1/η − 1) / T_0   (7)

| Symbol | Meaning | Unit |
|--------|---------|------|
| T_f | Fluid temperature (start, in Kelvin) | K |
| T_s | Effective source temperature | K |
| T_0 | Ambient temperature (≈ T_f for most cases) | K |
| η | Thermal efficiency | — |

Term 1: irreversibility from finite temperature difference (T_s >> T_f)
Term 2: irreversibility from heat losses to surroundings (1-η fraction)

**Model B — Heat pump (COP = β = η):**

    FTES = c_p · (1/T_f − (β − 1)/(β · T_0))                  (8)

The heat pump draws heat from the environment (at T_0) and delivers it
to the fluid (at T_f). No T_s is required because the driving
thermodynamic potential is the COP, not a source flame temperature.

**Output unit:** J / kg·K²

**Reference source temperatures (fixed per source type):**

| Source | T_s (K) | T_s (°C) | Physical basis |
|--------|--------|---------|---------------|
| Electric resistance heater | 500 | 227 | Heater element surface temperature |
| Gas stove / burner | 1,200 | 927 | Effective hot gas impingement |
| Solar flat-plate collector | 363 | 90 | Peak collector fluid temperature |
| Heat pump | N/A | N/A | Uses Model B (COP-based) |

**Relation to Bejan EGM:** FTES is a rearrangement of Bejan's entropy
generation number N_s = Ṡ_gen / (ṁ · c_p), expressed per unit mass per
unit temperature rise for direct comparison across sources.

**Physical interpretation:** The gas stove has the highest FTES because
it burns at ~1,200 K to heat fluid at ~293 K — an enormous temperature
ratio that generates entropy regardless of economic cost. The heat pump
has the lowest FTES because it operates near the fluid temperature,
minimising the irreversibility of the thermodynamic lift.

---

### 2.4 FTET — Fluid Thermal Energy Time

**Definition:** Time required to raise 1 kg of fluid by 1°C given the
rated power of the heating system.

    FTET = c_p / P_useful                                      (9)

    FTET [s/kg·°C] = c_p [J/kg·°C] / P_useful [W]

where P_useful [W] is the useful thermal power delivered to the fluid:

| Source type | P_useful | Notes |
|------------|---------|-------|
| Conventional heater | P_rated [W] × η | P_rated is electrical/gas input power |
| Heat pump | P_rated [W] × COP | COP multiplies rated electrical input |
| Solar thermal | A [m²] × G [W/m²] × η_col | A = area, G = irradiance, η_col ≈ 0.65 |

**Total time for a heating job:**

    t_total = FTET × m × ΔT = m · c_p · ΔT / P_useful         (10)

**Output unit:** s/kg·°C

**Key insight:** FTET scales directly with c_p. Mercury (c_p = 140 J/kg·°C)
heats ~30× faster than water (c_p = 4,184 J/kg·°C) at the same input power.
Liquid hydrogen (c_p = 14,300 J/kg·°C) takes ~3.4× longer than water.
This is the thermal inertia of the fluid made economically concrete.

---

## 3. Derived policy scalars

These two quantities are derived analytically by setting sub-metrics
equal across sources. Both cancel c_p exactly (cp-invariance) and are
therefore fluid-independent — they depend only on source parameters.

### 3.1 TPP — Thermal Parity Price

**Definition:** The electricity price at which a heat pump (COP = β)
becomes economically equivalent to a gas source (efficiency η_gas),
derived by setting FTEU_heatpump = FTEU_gas:

    (P_elec / β) · (c_p / 36,000) = (P_gas / η_gas) · (c_p / 36,000)

c_p and K₂ cancel on both sides, giving:

    TPP = P_gas × β / η_gas                                   (11)

    TPP [€/kWh electricity]

**Decision rule:** If local electricity price P_elec < TPP → prefer
heat pump on cost. If P_elec > TPP → gas is cheaper.

**Reference values (Spain 2026, P_gas = €0.092/kWh):**

| COP | η_gas | TPP | Spain P_elec | Decision |
|-----|-------|-----|-------------|---------|
| 3.0 | 0.45 | €0.613/kWh | €0.190 | Heat pump wins ✓ |
| 5.0 | 0.45 | €1.022/kWh | €0.190 | Heat pump wins ✓✓ |
| 1.0 (resistance) | 0.45 | €0.204/kWh | €0.190 | Resistance just wins ✓ |

### 3.2 CGIT — Carbon Grid Intensity Threshold

**Definition:** The grid CO₂ intensity below which electric heating
(resistance or heat pump) beats gas combustion on FTEM, derived by
setting FTEM_electric = FTEM_gas:

    (E_grid / β) · (c_p / K₁) = (E_gas / η_gas) · (c_p / K₁)

c_p and K₁ cancel, giving:

    CGIT = E_gas × β / η_gas                                   (12)

    CGIT [g CO₂/kWh grid electricity]

**Reference values (E_gas = 202 g CO₂/kWh):**

| Device | β / η_gas | CGIT | Implication |
|--------|----------|------|-------------|
| Resistance heater | 1.0/0.45 | 449 g/kWh | Countries below 449 g/kWh should electrify resistance heating |
| Heat pump COP 3 | 3.0/0.45 | 1,347 g/kWh | No grid on earth reaches this → HP always beats gas on carbon |
| Heat pump COP 5 | 5.0/0.45 | 2,244 g/kWh | As above, even more definitively |

**Policy significance:** CGIT for resistance heating (449 g CO₂/kWh) is
the single most policy-relevant number in the framework. Every country
with a grid cleaner than 449 g/kWh should be replacing gas boilers with
electric resistance heaters on carbon grounds alone. Spain (160), France
(50), Germany (350), UK (180), India (700 — approaching threshold) are
instructive comparators.

---

## 4. The TEEI composite index

### 4.1 Normalisation

For a set of n heating sources evaluated on a given fluid and
operating condition, each sub-metric x_i (i = 1..n) is normalised:

    x_i_norm = (x_i − x_min) / (x_max − x_min)               (13)

x_min, x_max are the minimum and maximum values across all n sources.
Result: x_i_norm ∈ [0, 1] where 0 = best, 1 = worst.

Performance score (higher = better):

    perf_i = 100 · (1 − x_i_norm)                             (14)

### 4.2 Composite formula

    TEEI = (w₁ · perf_FTEU + w₂ · perf_FTEM + w₃ · perf_FTES + w₄ · perf_FTET)
           ──────────────────────────────────────────────────────────────────────   (15)
                              w₁ + w₂ + w₃ + w₄

w₁, w₂, w₃, w₄ are user-defined weights for cost, carbon, entropy, speed.
Default: equal weighting w₁ = w₂ = w₃ = w₄ = 0.25.
Output: TEEI ∈ [0, 100]. Higher is better.

---

## 5. The cp-invariance theorem

### 5.1 Statement (Proposition 1)

**For any set of heating sources evaluated under the TEEI framework,
the normalised performance scores — and therefore the TEEI rankings —
are independent of the specific heat capacity c_p of the fluid being
heated, provided c_p (or c_p,eff) is constant over the heating range
and no phase change occurs.**

### 5.2 Proof

Step 1 — confirm linear scaling. From equations (4), (6), (7), (8), (9):

    FTEU = (P/η) · (c_p / 36,000)            ∝  c_p  (linear)
    FTEM = (E/η) · (c_p / K₁)            ∝  c_p  (linear)
    FTES_A = (c_p/η)(1/T_f − 1/T_s) + c_p(1/η−1)/T₀    ∝  c_p  (c_p factors from both terms)
    FTES_B = c_p · (1/T_f − (β−1)/(β·T₀))              ∝  c_p  (direct factor)
    FTET = c_p / P_useful                 ∝  c_p  (linear)

All four sub-metrics scale as: x_i = c_p · f_i, where f_i depends only
on source parameters (P, η, E, T_s, β, P_useful) and temperatures
(T_f, T_0) — not on the fluid.

Step 2 — show normalisation cancels c_p. For any metric x:

    x_i_norm = (x_i − x_min) / (x_max − x_min)
             = (c_p · f_i − c_p · f_min) / (c_p · f_max − c_p · f_min)
             = c_p · (f_i − f_min) / [c_p · (f_max − f_min)]
             = (f_i − f_min) / (f_max − f_min)                 ■

c_p cancels exactly. Therefore perf_i = 100(1 − x_i_norm) is also
c_p-independent, and so is TEEI (equation 15).   QED.

### 5.3 Corollary: fluid-invariance of TPP and CGIT

TPP and CGIT are derived by setting two FTEU or FTEM values equal.
Since c_p appears identically on both sides, it cancels in the equality,
confirming that TPP and CGIT are fluid-independent by construction.

### 5.4 Practical implications

1. **Source selection decouples from fluid selection.** The optimal
   heating source for a process can be determined before the process
   fluid is specified.

2. **Country databases store one row per country.** No fluid-specific
   columns are needed — c_p is irrelevant to source ranking.

3. **Absolute values DO scale with c_p.** The total cost to heat
   50,000 L of pool water (c_p ≈ c_water) is ~30× higher than to heat
   the same mass of mercury. But the ranking electric < gas < solar
   (on cost) does not change.

### 5.5 Boundary conditions

Theorem holds when:
- c_p is approximately constant → use c_p,eff if needed (eq. 3)
- No phase change occurs (single-phase scope, Section 1.2)
- The same temperature T_f applies to all sources (same process)

Theorem does NOT hold when:
- Phase change occurs (latent heat L is fluid-specific and non-linear)
- c_p varies significantly AND varies differently across fluid regions
  such that c_p,eff cannot be defined consistently
- Comparing sources at fundamentally different operating temperatures
  (rare in practice)

---

## 6. Dimensional summary

| Metric | Type | Formula | Unit | Scales with c_p | Fluid-independent? |
|--------|------|---------|------|----------------|-------------------|
| FTEU | Sub-metric | (P/η)·(c_p/K₂) | ¢/kg·°C | Yes, linear | Absolute: No; Ranking: Yes |
| FTEM | Sub-metric | (E/η)·(c_p/K₁) | g CO₂/kg·°C | Yes, linear | Absolute: No; Ranking: Yes |
| FTES | Sub-metric | Model A or B | J/kg·K² | Yes, linear | Absolute: No; Ranking: Yes |
| FTET | Sub-metric | c_p / P_useful | s/kg·°C | Yes, linear | Absolute: No; Ranking: Yes |
| TEEI | Composite | Eq. (15) | 0–100 | No (cancels) | Yes — fully |
| TPP | Policy scalar | P_gas × β / η_gas | €/kWh | Cancels | Yes — fully |
| CGIT | Policy scalar | E_gas × β / η_gas | g CO₂/kWh | Cancels | Yes — fully |

---

## 7. Reference data

### 7.1 Fluids — c_p at ~20°C, 1 atm (single-phase reference)

| Fluid | c_p (J/kg·°C) | T range for TEEI | Source |
|-------|-------------|-----------------|--------|
| Water | 4,184 | 0–100°C (excl. boiling) | NIST |
| Seawater (3.5% NaCl) | 3,900 | 0–100°C | Millero & Leung (1976) |
| Whole milk | 3,930 | 4–80°C | ASHRAE |
| Human blood | 3,617 | 36–42°C | Duck (1990) |
| Wort (mash, ~12 °P) | ~3,950 | 60–80°C | Geiger (1999) |
| Ethanol | 2,440 | 0–78°C (excl. boiling) | NIST |
| Glycerol | 2,380 | 20–100°C | Perry's |
| Ethylene glycol | 2,380 | −13–100°C | ASHRAE |
| Propylene glycol | 2,500 | 0–100°C | ASHRAE |
| Olive oil | 1,970 | 0–200°C | Moura et al. (2012) |
| Engine oil (SAE 30) | 1,900 | 20–150°C | Incropera et al. |
| Molten salt (NaNO₃/KNO₃ 60/40) | 1,500 | 220–550°C | Bradshaw & Mehos |
| Mercury | 140 | −39–357°C (excl. boiling) | NIST |
| Liquid ammonia | 4,700 | −77–(excl. boil at atm) | NIST |
| Liquid hydrogen | 14,300 | −259–(excl. boil) | NIST |

### 7.2 Heating sources — reference parameters

| Source | P (€/kWh) | η or COP | E (g CO₂/kWh) | T_s (K) | FTES model |
|--------|----------|---------|-------------|--------|-----------|
| Electric resistance | 0.190* | 0.99 | Grid* | 500 | Model A |
| Gas stove/burner | 0.092* | 0.45 | 202 | 1,200 | Model A |
| Solar flat-plate | 0.067† | 1.00 | 20 | 363 | Model A |
| Heat pump COP 3 | 0.190* | 3.00 | Grid* | — | Model B |
| Heat pump COP 5 | 0.190* | 5.00 | Grid* | — | Model B |

*Country-specific; auto-loaded from EMBER/Eurostat APIs.
†Amortised LCOE: system cost €2,000, 20-year life, 1,500 kWh_th/year (Spain).

---

*Formulation document version 0.2. August 2026.*

---

## 8. Validated scope and known boundary (added August 2026)

### 8.1 Confirmed scope: single batch/instantaneous heating events

Sections 1-7 above define the TEEI framework for a single heating event:
a fixed mass of fluid raised from T_start to T_target once, at a given
rated power. All six case studies (docs/01_project_log.md) and the
package's `calculate()`/`compare()` functions operate within this scope.

This scope has now been validated against real published benchmarks
(see docs/03_references.md, Section E, and `notebooks/08_validation.py`)
that are matched to it — tankless (zero-standby-loss) water heaters,
instantaneous solar collector efficiency curves, and lab-tested heat
pump COP at matched temperature lift. All four validations show gaps of
0-9%, within normal engineering tolerance.

### 8.2 Known boundary: NOT validated for 24-hour storage-tank cycling

The framework does NOT include a standby heat-loss term and is therefore
not directly applicable, without extension, to systems where fluid is
heated once and then held at temperature for extended periods with
continuous reheat cycling (e.g. a conventional storage-tank water heater
sitting idle between draws). An initial validation attempt against a
storage-tank benchmark (US DOE 10 CFR 430 Subpart B Appendix E) showed
a 25-32% underestimate, consistent with the missing standby-loss term,
not a formula error - see `notebooks/08_validation.py` Part E and
docs/01_project_log.md for the full account.

### 8.3 Future extension (not yet implemented)

A storage-tank extension would add an additive term to the energy
balance:

    Q_standby = UA · (T_tank - T_ambient) · t_hold

where UA is the tank's overall heat-loss coefficient [W/K] and t_hold is
the holding duration [s]. This is a straightforward, well-understood
addition (standard in water-heater engineering) but is explicitly out of
scope for the current release and does not affect the validity of the
cp-invariance theorem (Section 5) or any of the six case studies, all of
which model batch/instantaneous events.
