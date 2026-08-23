# TEEI — Project Roadmap
## Venue, Deliverable, Architecture, and Timeline

**Version:** 0.2 | **Last updated:** August 2026

---

## 1. What are we building?

**Three integrated deliverables in one public GitHub repository.**

```
fluid-thermal-index/              ← Repository name (recommended)
│
├── README.md                     ← Project overview, badges, quick-start
├── CITATION.cff                  ← Machine-readable paper citation
├── LICENSE                       ← MIT licence
├── CHANGELOG.md                  ← Version history
│
├── paper/                        ← LaTeX source of the Applied Energy paper
│   ├── main.tex
│   ├── supplementary.tex
│   └── figures/
│
├── data/                         ← Automatically updated datasets
│   ├── countries.json            ← 40-country: elec price, gas price, CO₂
│   ├── fluids.json               ← 15+ fluids with c_p, T_range, source
│   ├── sources.json              ← Heating source parameters
│   └── update_log.json           ← When data was last fetched + from where
│
├── teei/                         ← Python package (pip install teei)
│   ├── __init__.py
│   ├── metrics.py                ← FTEU, FTEM, FTES, FTET, TEEI, TPP, CGIT
│   ├── fluids.py                 ← Fluid c_p database + c_p,eff calculation
│   ├── countries.py              ← Geographic price + CO₂ loader
│   ├── sources.py                ← Heating source definitions + validation
│   └── phase_check.py           ← Single-phase validity check (eq. 2)
│
├── scripts/                      ← Data pipeline (GitHub Actions)
│   ├── fetch_ember.py
│   ├── fetch_eurostat.py
│   ├── fetch_eia.py
│   └── merge_countries.py
│
├── notebooks/                    ← Jupyter case study notebooks
│   ├── 01_domestic_hot_water.ipynb
│   ├── 02_swimming_pool.ipynb
│   ├── 03_restaurant_kitchen.ipynb
│   ├── 04_milk_pasteurisation.ipynb
│   ├── 05_brewery.ipynb
│   └── 06_aquaculture.ipynb
│
├── web/                          ← Interactive calculator (GitHub Pages)
│   ├── index.html
│   ├── app.js                    ← TEEI widget (vanilla JS, Chart.js)
│   └── data/ → symlink to ../data/
│
├── .github/
│   └── workflows/
│       ├── update-prices.yml     ← Quarterly price/CO₂ update
│       ├── tests.yml             ← Run tests on push
│       └── deploy-web.yml        ← Deploy web tool to GitHub Pages
│
└── docs/
    ├── 01_project_log.md         ← This project log
    ├── 02_formulation.md         ← Theory and formulation
    ├── 03_references.md          ← Literature and data sources
    └── 04_roadmap.md             ← This roadmap
```

---

## 2. Publication strategy

### 2.1 Primary target: Applied Energy (Elsevier)

| Parameter | Value |
|-----------|-------|
| Impact Factor (2025 JCR) | 12.2 |
| Quartile | Q1 |
| Acceptance rate | ~35–45% |
| APC (open access) | $4,210 USD |
| First decision | Days to ~2 weeks |

**Why Applied Energy is the right venue:**
- Scope explicitly covers: thermal systems, techno-economic analysis,
  optimal use of energy resources, analysis of energy processes
- Publishes framework papers that bridge research and implementation
- Readership includes engineers and planners — exactly who uses TEEI
- Multi-country geographic case studies align with their policy appetite

**What the paper must demonstrate to pass desk review:**
1. Novelty clearly stated — cp-invariance theorem as Proposition 1
2. Results transferable beyond one configuration — geographic TEEI proves this
3. Realistic cost assumptions with sensitivity analysis — TPP/CGIT quantify this
4. Practical energy-systems consequence — 6 case studies demonstrate this

### 2.2 Fallback journals

| If... | Use... |
|-------|--------|
| Reviewers want deeper heat transfer engineering | Applied Thermal Engineering (IF 7.86) |
| APC is a constraint | Advances in Applied Energy (lower APC, new Elsevier OA journal) |
| Broader scope preferred | Energy (Elsevier, IF ~9.0) |

### 2.3 Paper structure (Applied Energy)

```
Title: TEEI: A cp-Invariant Multi-Dimensional Index for Comparing
       Fluid Heating Sources Across Economic, Environmental,
       Thermodynamic, and Temporal Dimensions

Abstract (250 words)

1. Introduction
   1.1 The problem: fragmented heating source comparison
   1.2 Gap in existing literature
   1.3 Contributions of this paper

2. Methodology
   2.1 Physical foundation and scope (single-phase sensible-heat)
   2.2 Effective specific heat c_p,eff for variable-cp fluids
   2.3 Sub-metric definitions: FTEU, FTEM, FTES, FTET
   2.4 Derived policy scalars: TPP and CGIT
   2.5 TEEI composite formulation
   2.6 Proposition 1: cp-invariance theorem (with full proof)
   2.7 Corollary: fluid-invariance of TPP and CGIT

3. Geographic parameterisation
   3.1 Country price and CO₂ database (methodology)
   3.2 EMBER API for grid CO₂ intensity
   3.3 Eurostat + EIA APIs for energy prices
   3.4 Automated quarterly update pipeline
   3.5 Sensitivity: price volatility and CO₂ trend impact on TEEI

4. Case studies (6 quantitative studies, 8–10 countries each)
   4.1 Domestic hot water heating
   4.2 Outdoor swimming pool (50,000 L)
   4.3 Commercial kitchen and dishwashing
   4.4 SME milk pasteurisation (HTST, 72°C/15 s)
   4.5 Brewery — three-stage heating
   4.6 Salmon aquaculture tank

5. Results and discussion
   5.1 TEEI rankings across countries — who should switch to heat pumps?
   5.2 TPP analysis: economic tipping points for 40 countries
   5.3 CGIT analysis: carbon tipping points vs current grid intensity
   5.4 Decarbonisation pathways — TEEI projection to 2035 grid CO₂ targets
   5.5 Application catalogue overview (10 domains, supplementary)

6. Open-source tool
   6.1 Python package teei (pip install teei)
   6.2 Interactive web calculator (URL)
   6.3 Reproducibility: Binder/Colab links for each case study notebook

7. Conclusions

Appendix A: Proof of Proposition 1 (cp-invariance) — full version
Appendix B: Full country database (40 countries, tabulated)
Appendix C: Fluid c_p database with temperature ranges
```

---

## 3. Deliverable 1 — Python package (`pip install teei`)

### 3.1 Core API

```python
from teei import TEEI, TPP, CGIT

# Single calculation
result = TEEI(
    fluid='water',          # string (lookup from fluids.json) or float (c_p value)
    source='heat_pump_3',   # string (lookup from sources.json) or dict
    country='ES',           # ISO 3166-1 alpha-2; auto-loads price + CO₂
    mass=1.0,               # kg
    delta_T=80,             # °C temperature rise
    T_start=20,             # °C starting fluid temperature
    P_rated=2.0,            # kW rated input power
    weights=(0.25, 0.25, 0.25, 0.25)  # (w_cost, w_carbon, w_entropy, w_time)
)

# All outputs
print(result.fteu)     # ¢/kg·°C
print(result.ftem)     # g CO₂/kg·°C
print(result.ftes)     # J/kg·K²
print(result.ftet)     # s/kg·°C
print(result.teei)     # 0–100 score
print(result.t_total)  # total time in seconds
print(result.cp_eff)   # effective c_p used [J/kg·°C]
print(result.valid)    # True if single-phase check passes

# Policy scalars (fluid-independent)
tpp = TPP(source_gas='gas_stove', cop=3.0, country='ES')
# → TPP = €0.613/kWh; Spain electricity = €0.190 → heat pump wins

cgit = CGIT(source_electric='resistance', country='ES')
# → CGIT = 449 g CO₂/kWh; Spain grid = 160 g → electric wins on carbon

# Batch comparison across countries
from teei import compare_countries
df = compare_countries(
    fluid='water', source_list=['electric', 'gas', 'solar', 'hp3', 'hp5'],
    countries=['ES', 'DE', 'FR', 'NO', 'PL', 'IN', 'US', 'GB'],
    mass=200, delta_T=40, P_rated=3.0
)
# Returns pandas DataFrame with FTEU/FTEM/FTES/FTET/TEEI for each combo
```

### 3.2 Single-phase validation

```python
from teei.phase_check import is_single_phase

check = is_single_phase(fluid='water', T_start=20, T_target=95, pressure=1.0)
# → True (95°C < 100°C boiling point at 1 atm)
# → raises SinglePhaseWarning if T_target > 0.85 × T_boil
# → raises PhaseChangeError if T_target > T_boil
```

### 3.3 c_p,eff calculation

```python
from teei.fluids import cp_eff

cp = cp_eff(fluid='water', T_start=20, T_target=80)
# Uses CoolProp integration of c_p(T) from 20 to 80°C
# → 4,187 J/kg·°C (vs 4,182 at 20°C: ~0.1% difference for water)
```

---

## 4. Deliverable 2 — Interactive web calculator

**Stack:** Vanilla HTML + JavaScript + Chart.js. No framework, no server.
**Hosting:** GitHub Pages (free, auto-deploys on push to `main`).
**URL:** `https://[username].github.io/fluid-thermal-index/`

**Features:**
- Country dropdown → auto-loads electricity price, gas price, grid CO₂
- Fluid selector (15+ fluids) + custom c_p input field
- Source selector + power/area sliders
- Single-phase validity indicator (green/red based on T_start + ΔT)
- All five TEEI output cards (FTEU, FTEM, FTES, FTET, TEEI)
- TPP and CGIT policy scalar displays
- Radar chart (4 axes: cost, carbon, entropy, speed)
- Time comparison bars (all sources ranked by FTET)
- Full ranking table
- "Data last updated" timestamp from update_log.json

---

## 5. Deliverable 3 — Jupyter case study notebooks

Six notebooks, one per case study. Each:
- Installs `teei` package automatically
- Loads country data via API or bundled JSON
- Runs full TEEI calculation with sensitivity analysis
- Produces all paper figures (matplotlib/seaborn)
- Exports figures as PDF + SVG for LaTeX

**Zero-install access:** Each notebook has a Binder badge and a Google Colab badge in the README. Reviewers can run the full analysis in a browser with no local installation.

---

## 6. Data architecture (agreed: automatic live updates)

### 6.1 countries.json schema

```json
{
  "version": "2026-Q3",
  "updated": "2026-10-01",
  "source": "EMBER + Eurostat + EIA",
  "countries": {
    "ES": {
      "name": "Spain",
      "electricity_price": 0.190,
      "gas_price": 0.092,
      "grid_co2": 160,
      "currency": "EUR",
      "sources": {
        "electricity": "Eurostat nrg_pc_204 2026-H1",
        "gas": "Eurostat nrg_pc_202 2026-H1",
        "co2": "EMBER 2026-Q2"
      }
    },
    "DE": { "name": "Germany", "electricity_price": 0.325, "gas_price": 0.110, "grid_co2": 350, ... },
    "FR": { "name": "France", "electricity_price": 0.200, "gas_price": 0.095, "grid_co2": 52, ... },
    "NO": { "name": "Norway", "electricity_price": 0.105, "gas_price": 0.088, "grid_co2": 28, ... },
    "PL": { "name": "Poland", "electricity_price": 0.185, "gas_price": 0.075, "grid_co2": 695, ... },
    "IN": { "name": "India", "electricity_price": 0.080, "gas_price": 0.045, "grid_co2": 708, ... },
    "US": { "name": "USA (avg)", "electricity_price": 0.155, "gas_price": 0.055, "grid_co2": 370, ... },
    "GB": { "name": "United Kingdom", "electricity_price": 0.245, "gas_price": 0.100, "grid_co2": 180, ... }
  }
}
```

### 6.2 Automation pipeline (summary)

| Step | Script | Source | Cadence |
|------|--------|--------|---------|
| 1 | fetch_ember.py | EMBER API | Twice/month (automated quarterly) |
| 2 | fetch_eurostat.py | Eurostat REST API | Quarterly |
| 3 | fetch_eia.py | EIA API | Monthly (automated quarterly) |
| 4 | merge_countries.py | Merge + validate | Quarterly (GitHub Actions cron) |
| 5 | GitHub Actions push | Auto-commit to repo | After merge step |
| 6 | GitHub Pages deploy | Auto-deploy web tool | After commit |

---

## 7. Honest expert advice (consolidated)

### On the paper
**Write the paper around the cp-invariance theorem.** That is the proof-based
mathematical contribution that will survive peer review. Every case study
should demonstrate either TPP, CGIT, or the cp-invariance corollary in a
concrete setting. A paper without the theorem is a software paper; a paper
with the theorem is a methods paper in a top journal.

**Do not call it microeconomics.** Call it micro-scale techno-economic analysis.
The paper operates in applied energy economics with a thermodynamic foundation —
that is the accurate description and the one reviewers will accept.

### On the web tool
**Build it before submission.** Applied Energy reviewers in 2026 expect
interactive tools to be live, not described. A working URL in the paper is
stronger than any figure.

### On the Python package
**v0.1 must be on PyPI before submission.** Minimum: core TEEI calculation,
geographic country loader, and the cp_eff function. Case study notebooks
must run cleanly on the submitted version.

### On scope
**Defend the single-phase boundary aggressively.** It is not a limitation;
it is a deliberate and well-justified scope choice that covers >90% of
practical heating applications. State it early in the paper and explain
why two-phase is a separate problem.

---

## 8. Timeline (proposed)

| Phase | Deliverable | Target |
|-------|------------|--------|
| 0 — Now | Docs + GitHub repo setup | Week 1 |
| 1 | Python package v0.1 (core metrics, no geo) | Week 2 |
| 2 | Country JSON + EMBER/Eurostat API scripts | Week 3 |
| 3 | Python package v0.2 (geographic mode + TPP/CGIT) | Week 4 |
| 4 | Case studies 1 + 2 (domestic hot water + pool) | Week 5–6 |
| 5 | Case studies 3 + 4 (restaurant + pasteurisation) | Week 7–8 |
| 6 | Case studies 5 + 6 (brewery + aquaculture) | Week 9–10 |
| 7 | Web tool (interactive calculator, GitHub Pages) | Week 11 |
| 8 | Paper draft (all sections) | Week 12–14 |
| 9 | Internal review + revision | Week 15–16 |
| 10 | Submit to Applied Energy | Week 17 |

---

*Roadmap version 0.2. August 2026.*

---

## Update — August 2026: status after implementation, sensitivity, and validation

The Python package, 6 case studies, sensitivity analysis, and validation
(v2) are all complete — see docs/01_project_log.md "Update — August 2026"
for the full account. Remaining before paper submission:

- [ ] Fill in CITATION.cff author details (left for manual completion)
- [ ] Tighten "low confidence" country data entries (India, Brazil,
      Morocco, Turkey, Saudi Arabia, South Africa)
- [ ] Additional literature cross-check once paper draft is underway
      (explicitly deferred, not immediate)
- [ ] Draft the paper itself — outline discussed separately with the
      author before writing begins
