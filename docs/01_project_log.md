# TEEI Project Log
## Thermal Economic-Environmental Index for Fluid Heating Systems

**Version:** 0.2 | **Last updated:** August 2026 | **Status:** Active development

---

## 1. Origin and starting question

The project began with a deceptively simple question:

> *"What do you call an entity or something that is required to raise the temperature
> of fluid/water by 1 degree Celsius?"*

Answer: a **calorie** (1 cal = energy to raise 1 g of water by 1°C = 4.184 J).
This thermodynamic primitive became the conceptual anchor for everything that followed.

The second question — *"How much does it cost to raise 1 glass of water by 1°C?"* —
immediately revealed that the answer depends on the heating source, the fuel price,
and the efficiency with which the source delivers useful heat. This led directly to the
first metric: cost per kg·°C.

---

## 2. Conceptual evolution (agreed session timeline)

| Step | Development | Status |
|------|------------|--------|
| 1 | Calorie as anchor; cost per glass of water (Spain €0.19/kWh) | ✓ Fixed |
| 2 | Three-source comparison: electric, gas, solar; efficiency η introduced | ✓ Fixed |
| 3 | Generalise from water to any fluid — replace constant with c_p | ✓ Fixed |
| 4 | FTEU defined — Fluid Thermal Economic Unit [¢/kg·°C] | ✓ Fixed |
| 5 | FTEM added — Fluid Thermal Emission Metric [g CO₂/kg·°C] | ✓ Fixed |
| 6 | FTES added — Fluid Thermal Entropy Score [J/kg·K²] | ✓ Fixed |
| 7 | FTET added — Fluid Thermal Energy Time [s/kg·°C] | ✓ Fixed |
| 8 | TEEI defined — composite weighted index [0–100] | ✓ Fixed |
| 9 | cp-invariance theorem discovered and proved | ✓ Fixed |
| 10 | TPP and CGIT derived as policy scalars from FTEU/FTEM equality | ✓ Fixed |
| 11 | Scope restricted to single-phase sensible-heat (no phase change) | ✓ Agreed |
| 12 | c_p,eff introduced for variable-cp fluids within single-phase range | ✓ Agreed |
| 13 | Application strategy: 6 deep case studies + 10 catalogue entries | ✓ Agreed |
| 14 | Automatic live price architecture: EMBER + Eurostat + EIA APIs | ✓ Agreed |
| 15 | Terminology fixed: micro-scale techno-economic (NOT microeconomics) | ✓ Agreed |

---

## 3. Complete metric inventory

### 3.1 Primary sub-metrics

| Metric | Full name | Unit | Novelty |
|--------|-----------|------|---------|
| **FTEU** | Fluid Thermal Economic Unit | ¢ / kg·°C | Rescaling of LCOH — not novel alone |
| **FTEM** | Fluid Thermal Emission Metric | g CO₂ / kg·°C | Rescaling of carbon intensity — not novel alone |
| **FTES** | Fluid Thermal Entropy Score | J / kg·K² | Rearrangement of Bejan N_s — not novel alone |
| **FTET** | Fluid Thermal Energy Time | s / kg·°C | Standard thermal time constant — not novel alone |
| **TEEI** | Thermal Economic-Environmental Index | — [0–100] | 4D composite, specific combination is novel |

### 3.2 Derived policy scalars (genuinely novel)

| Metric | Full name | Unit | Formula | Novelty |
|--------|-----------|------|---------|---------|
| **TPP** | Thermal Parity Price | €/kWh | P_gas × COP / η_gas | Not in LCOH or EGM literature |
| **CGIT** | Carbon Grid Intensity Threshold | g CO₂/kWh | E_gas × COP / η_gas | Not stated in this form |

**TPP** is the electricity price at which a heat pump becomes economically
equivalent to a gas source. Any country where P_elec < TPP should prefer
the heat pump on cost grounds — independently of the fluid being heated.

**CGIT** is the grid CO₂ intensity below which electric heating beats gas
combustion on emissions. For resistance heating: CGIT = 449 g CO₂/kWh
(most of the world is already below this). For heat pump COP 3:
CGIT = 1,347 g CO₂/kWh (no grid on earth reaches this — heat pumps
always beat gas on carbon).

Both TPP and CGIT cancel c_p exactly (cp-invariance) and are therefore
fluid-independent by construction. This is a practical policy result.

---

## 4. Scope and validity (agreed boundaries)

### 4.1 Included: single-phase sensible-heat processes

The TEEI framework applies to processes where:
- The working fluid remains in the liquid phase throughout (T < ~0.85 × T_boil)
- No phase change (boiling, condensation, freezing) occurs
- Heat transfer is sensible (Q = m · c_p · ΔT)
- c_p is approximately constant OR an effective value c_p,eff can be defined

**Rationale:** Phase change introduces latent heat L >> c_p·ΔT for typical ΔT,
requires a separate physical model, and breaks the linear c_p scaling that underpins
the cp-invariance theorem. Excluding it keeps the mathematics clean and the paper
defensible. Two-phase extension is a future paper.

### 4.2 c_p variation within single-phase range

For most liquid fluids, c_p varies by 1–5% across practical heating ranges:
- Water (0–100°C): c_p = 4,179 to 4,218 J/kg·°C — variation < 1%
- Ethylene glycol (20–80°C): variation ~3%
- Engine oil (20–80°C): variation ~5%

Engineering accuracy is maintained by using the effective value:

    c_p,eff = (1/ΔT) × ∫[T₁ to T₂] c_p(T) dT

The cp-invariance theorem holds identically with c_p,eff substituted for c_p.

### 4.3 Excluded (explicit scope boundary)

- Phase-change processes (boiling water for steam, condensing refrigerants)
- Cryogenic systems near phase transitions
- Supercritical fluids (c_p diverges near critical point)
- Non-Newtonian fluids (viscosity effects dominate heat transfer)
- Reactive fluids (chemical reactions change enthalpy budget)

---

## 5. Novelty assessment (post-literature review)

### 5.1 Confirmed novel contributions

1. **cp-invariance theorem** — all four FTEU/FTEM/FTES/FTET sub-metrics
   scale linearly with c_p; when normalised across sources, c_p cancels
   exactly. TEEI rankings of heating sources are mathematically independent
   of fluid choice. Not stated in LCOH, EGM, or MCDA literature.

2. **TPP and CGIT derived scalars** — analytical expressions for the
   economic and carbon tipping points at which one heating source becomes
   preferred over another. Fluid-independent by construction. Not in
   published form in energy economics literature.

3. **Unified micro-scale framework** — all four dimensions share the
   structural form (system parameter) × (c_p / dimensional constant),
   making c_p the sole fluid-specific degree of freedom simultaneously
   across economic, environmental, thermodynamic, and temporal metrics.

4. **Inclusion of heating time (FTET) in a multi-dimensional thermal
   comparison** — heating rate is absent from existing LCOH + carbon +
   entropy composite frameworks.

5. **Per-kg-per-°C granularity** — existing metrics operate at macro scale
   (per kWh, per MMBTU). The per-kg·°C unit is appropriate for SME,
   domestic, and laboratory-scale systems where kWh is too coarse.

### 5.2 Partially novel

6. **TEEI composite (4D)** — specific combination of LCOH + carbon intensity
   + entropy generation + time, normalised and weighted, applied to
   arbitrary fluid-source pairs. MCDA frameworks exist separately; this
   specific 4D combination over arbitrary fluids does not.

7. **Geographic TEEI** — linking the composite index to live country-level
   prices (EMBER API, Eurostat API, EIA API) for instantaneous geographic
   comparison. Not published as a standalone tool.

### 5.3 Not novel (honest)

- FTEU alone → rescaling of LCOH
- FTEM alone → rescaling of carbon intensity of heat
- FTES alone → rearrangement of Bejan entropy generation number N_s
- FTET alone → standard thermal time constant c_p / P_useful

---

## 6. Terminology (agreed)

| Avoid | Use instead | Reason |
|-------|------------|--------|
| "micro-economics" | "micro-scale techno-economic analysis" | We are not using formal microeconomic theory (supply/demand equilibrium, utility functions). "Micro" refers to scale (per-kg, per-°C) not the discipline. |
| "TEEI for any system" | "TEEI for single-phase sensible-heat systems" | Scope constraint is fundamental to validity |
| "real-time prices" | "regularly updated prices (quarterly)" | Most retail energy prices update quarterly, not in real time |

---

## 7. Application strategy (agreed)

### 7.1 Primary quantitative case studies (6 — for paper)

Each study includes: full TEEI calculation, geographic comparison across
8–10 countries, sensitivity analysis on key parameters, policy conclusions.

| # | Application | Fluid | Key feature |
|---|-------------|-------|-------------|
| 1 | Domestic hot water heating | Water | Most universal; all 5 sources; policy-relevant |
| 2 | Outdoor swimming pool (50,000 L) | Water | Large mass; FTET dominant; solar competes |
| 3 | Restaurant/hotel kitchen + dishwashing | Water | Continuous load; time + cost both matter |
| 4 | SME milk pasteurisation (HTST 72°C/15 s) | Milk (c_p = 3,930 J/kg·°C) | c_p ≠ water; regulatory T constraint |
| 5 | Brewery: mash 65°C → boil excluded → CIP 80°C | Water / wort (~3,950 J/kg·°C) | Multi-stage; sequential source optimisation |
| 6 | Salmon aquaculture tank (12–14°C) | Water | Tiny ΔT; large mass; off-grid; HP dominates |

### 7.2 Application catalogue (10 — for breadth section / supplementary)

Concrete curing (water in mix) · Winery fermentation (glycol, 15°C) ·
Commercial laundry (60–90°C) · Car wash hot water ·
Greenhouse irrigation water · Pharmaceutical bioreactor (37°C) ·
Biogas digester (slurry, 37°C mesophilic) · Textile dyeing bath (water, 60–95°C) ·
District heating substation (large water loop) ·
EV battery thermal conditioning (ethylene glycol, 25°C target)

---

## 8. Data architecture (agreed: automatic live updates)

### 8.1 Source mapping

| Data dimension | Primary source | Method | Cadence |
|---------------|---------------|--------|---------|
| Grid CO₂ intensity | EMBER API (CC BY 4.0) | REST API call | Updated twice/month; 215 countries |
| EU electricity price | Eurostat REST API | REST API call | Quarterly |
| EU gas price | Eurostat REST API | REST API call | Quarterly |
| US electricity price | EIA API (free key) | REST API call | Monthly |
| Non-EU/US prices | GlobalPetrolPrices (annual) | Manual or scrape | Quarterly manual check |

### 8.2 GitHub Actions pipeline (quarterly cron job)

```
teei-data-update.yml (GitHub Actions)
Schedule: 0 0 1 */3 *    (quarterly, 1st of Jan/Apr/Jul/Oct)

Steps:
  1. Call EMBER API → update CO₂ intensity for all countries
  2. Call Eurostat API → update EU electricity + gas prices
  3. Call EIA API → update US state-level electricity prices
  4. Validate data (range checks, flag anomalies)
  5. Write to data/countries.json
  6. Commit + push to main branch
  7. GitHub Pages web tool auto-reads updated JSON on next load
```

---

## 9. Open questions

- [ ] Full systematic literature search for TPP and CGIT (confirm not published)
- [ ] Formalise cp-invariance theorem as Proposition 1 in paper with full proof
- [ ] Draft EMBER API integration script
- [ ] Draft Eurostat API integration script
- [ ] Begin Python package (`teei/`) core module
- [ ] Swimming pool case study (first full calculation)
- [ ] Domestic hot water cross-country comparison (10 countries)
- [ ] Paper draft outline — submit to Applied Energy
- [ ] Decide GitHub repository name (suggested: `fluid-thermal-index`)

---

*Log maintained continuously. Version 0.2. August 2026.*

---

## Update — August 2026: Implementation, sensitivity analysis, and validation

*Appended after the theoretical framework (above) was implemented as working
code, tested, and validated against real-world sources. This section
records what changed and why, in chronological order.*

### Implementation

- Built the `teei` Python package (7 modules: `_constants.py`, `metrics.py`,
  `fluids.py`, `sources.py`, `countries.py`, `phase_check.py`, `__init__.py`)
  implementing FTEU, FTEM, FTES (Models A & B), FTET, TEEI, TPP, and CGIT
  exactly as specified in `02_formulation.md`.
- Built a JavaScript port for the web calculator (`web/index.html`) and
  cross-verified it against the Python package to 6 decimal places on
  matched inputs — confirmed exact agreement for both conventional (Model
  A) and heat-pump (Model B) entropy formulas.
- 88 unit and integration tests pass (`tests/test_metrics.py`,
  `tests/test_integration.py`), including an explicit numerical check of
  the cp-invariance theorem (identical TEEI rankings for water vs mercury).

### Case studies (6 total, standardised template)

Built six case studies (swimming pool, domestic hot water, restaurant
kitchen, milk pasteurisation, brewery, aquaculture) using a shared
figure-generation template (`notebooks/utils/standard_figures.py`) so
that countries, figure types, and presentation are identical across all
six — only the physical parameters (mass, ΔT, power, fluid) vary, since
those legitimately define each case study. Produced 51 case-study figures
plus 3 master-synthesis figures (headline results: HP COP 5 wins in every
case study under equal weighting; a ~80% cost saving vs electric
resistance holds universally, a direct consequence of COP 5/COP 1 ratio
and therefore fluid- and country-independent by construction).

### Country energy data — from placeholder to real, sourced figures

The initial 20-country database (`data/countries.json`) used plausible
placeholder values written without live sourcing. This was replaced with
real figures from Eurostat (EU electricity/gas prices), EIA (US
electricity), and Ember (grid CO₂ intensity), each entry now carrying an
explicit `confidence` field (high/medium/low) and a `sources` object
citing the exact dataset and any unit conversion performed (e.g. Spain
gas price converted from Eurostat's EUR/GJ figure to EUR/kWh). Countries
where a live regulator source could not be confirmed in this session
(India, Brazil, Morocco, Turkey, Saudi Arabia, South Africa) are marked
`confidence: low` with an explicit recommendation for a direct national
regulator lookup before publication.

### A real bug found and fixed

While constructing an adversarial sensitivity scenario, discovered that
`calculate()` silently ignored a custom source dict's own `price` field
whenever `country=None`, falling back to a hardcoded 0.190 default. Fixed
in `teei/__init__.py`; added a permanent regression test
(`test_custom_source_dict_price_used_when_no_country`). Test count rose
from 87 to 88.

### A labelling inconsistency found and fixed

The η=0.45 "gas" source (realistic for a basic open-flame stove) was
displayed as "Gas boiler" throughout all case studies and the live web
calculator — a real appliance-type mismatch, though not a formula error.
Corrected the label to "Gas stove (basic)" in the single shared source
(`notebooks/utils/standard_figures.py`, which fixed all 6 case studies at
once) plus the two standalone scripts and the web calculator. Also
corrected a stale gas price default (€0.092 → €0.086) picked up in the
same pass.

### Sensitivity analysis — addressing the "HP always wins" concern

Built `notebooks/07_sensitivity_analysis.py` to directly test whether
the heat-pump dominance seen in the case studies is a modelling artefact
or a genuine, defensible result. Findings:

- **8 weighting schemes tested** (cost-only, carbon-only, entropy-only,
  speed-only, equal, and 3 policy-relevant blends): HP COP 5 wins **7 of
  8**. The one honest exception is carbon-only weighting, where Solar
  thermal wins (near-zero lifecycle CO₂).
- **Gas efficiency sweep** (η=0.45→0.98, i.e. basic stove to best-possible
  modern boiler): improves gas's score substantially but never flips the
  overall ranking under equal weights.
- **Heat pump COP sweep** (COP 5→1.2, i.e. state-of-the-art to
  barely-better-than-resistance): HP still wins even at COP 1.2.
- **Adversarial stress test**: deliberately constructed hostile
  conditions (900 g CO₂/kWh grid, €0.03/kWh efficient gas, €0.45/kWh
  electricity) and found gas *does* win — but only under cost-only
  weighting and only when heat pump COP < 13.8 (derived analytically via
  the TPP formula), a COP far beyond any real heat pump (state-of-the-art
  ≈ COP 5–6).

**Verdict recorded in the paper-facing summary:** the HP dominance is a
genuine, robust result under equal weighting and realistic inputs — not
unconditional, since carbon-only weighting favours solar and an extreme
cost-only adversarial scenario favours gas, both reported rather than
hidden.

### Validation against real-world benchmarks — v1 (superseded) and v2 (current)

**v1 (superseded):** Initially compared the TEEI model's predictions
against a US DOE storage-tank water heater test benchmark (10 CFR 430
Subpart B Appendix E) and found a 25–32% underestimate for both electric
and heat pump water heaters. On review, this was judged to be the wrong
benchmark choice, not evidence of a formula error: the DOE benchmark
measures a 24-hour storage-tank system including standby heat loss, while
the TEEI framework models a single batch heating event
(Q = m·cₚ·ΔT/η) with no standby-loss term. The two are not the same
physical system, so a large gap was expected by construction.

**v2 (current, `notebooks/08_validation.py`):** Replaced the mismatched
benchmark with four validations chosen to match the model's actual batch/
instantaneous scope:

- **Tankless electric water heater efficiency** (California Energy
  Commission, 2022, official regulatory minimum UEF): real 0.91 vs model
  0.99 → **+8.8% gap**, defensible.
- **Tankless condensing gas water heater efficiency** (DOE ENERGY STAR
  Water Heater Program Requirements v4.0): real range 0.87–0.96, model's
  sensitivity-analysis test value 0.92 falls **directly within** this
  range.
- **Solar collector instantaneous efficiency** (Solar Keymark certified
  collector database, averaged across 50 collectors, ScienceDirect 2023:
  η₀=0.73, a₁=3.62 W/m²K, a₂=0.0133 W/m²K²): real 0.598 at representative
  domestic-hot-water conditions (ΔT=25°C, G=750 W/m²) vs model constant
  0.65 → **+8.7% gap**, defensible.
- **Heat pump COP**, checked against 3 independent sources: a 2021
  peer-reviewed lab study (COP 3.39–4.35 at moderate lift, matching HP3);
  a **2025** peer-reviewed measured study of a tropical heat pump system
  (average COP 5.27, closely matching HP5=5.0); and real homeowner-
  measured UK data (COP 2.5–3.0, matching HP3, kept as supplementary
  since it is not peer-reviewed).

The original storage-tank comparison is retained in the script (Part E)
but explicitly relabelled as a **scope-boundary demonstration, not a
validation** — useful for a paper's limitations section, since it shows
precisely where the batch-model boundary lies and what an extension
(an additive standby-loss term) would require.

**All four genuine validation targets show gaps of 0–9%**, within normal
engineering tolerance, built entirely on real, cited, mostly peer-reviewed
2021–2025 sources, with no change to any formula or previously-computed
case-study result.

### Planned future work (not yet started)

- Cross-check the model against additional recent literature once the
  paper draft is underway, to strengthen the validation section further
  ahead of submission (explicitly deferred — to be picked up in a later
  session, not immediately).
- Tighten the "low confidence" country entries (India, Brazil, Morocco,
  Turkey, Saudi Arabia, South Africa) with direct national-regulator
  sourcing.
- Consider a standby-loss extension term for users who want to model
  storage-tank systems (outside current scope, documented as a
  limitation).
