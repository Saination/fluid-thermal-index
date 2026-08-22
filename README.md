# fluid-thermal-index

> **TEEI — Thermal Economic-Environmental Index**
> A fluid-parameterised, multi-dimensional framework for comparing heating sources
> across economic, environmental, thermodynamic, and temporal dimensions.

[![PyPI version](https://img.shields.io/pypi/v/teei.svg)](https://pypi.org/project/teei/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/Saination/fluid-thermal-index/actions/workflows/tests.yml/badge.svg)](https://github.com/Saination/fluid-thermal-index/actions)
[![Data](https://img.shields.io/badge/prices-Q3%202026-orange.svg)](data/countries.json)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Saination/fluid-thermal-index/blob/main/notebooks/01_swimming_pool.py)
[![Paper](https://img.shields.io/badge/paper-Applied%20Energy-red.svg)](#citation)

---

## What is TEEI?

TEEI computes **four sub-metrics** for any fluid heated by any source in any country:

| Metric | Name | Unit | Captures |
|--------|------|------|---------|
| **FTEU** | Fluid Thermal Economic Unit | ¢ / kg·°C | Cost per kg per degree |
| **FTEM** | Fluid Thermal Emission Metric | g CO₂ / kg·°C | Carbon per kg per degree |
| **FTES** | Fluid Thermal Entropy Score | J / kg·K² | Thermodynamic irreversibility |
| **FTET** | Fluid Thermal Energy Time | s / kg·°C | Time per kg per degree |

These combine into **TEEI** (0–100, higher = better) and two policy scalars:

- **TPP** (Thermal Parity Price) — electricity price at which a heat pump beats gas on cost [€/kWh]
- **CGIT** (Carbon Grid Intensity Threshold) — grid CO₂ intensity below which electric heating beats gas on carbon [g CO₂/kWh]

### The cp-invariance theorem (Proposition 1)

> All four sub-metrics scale linearly with the fluid's specific heat capacity cₚ.
> When normalised for source comparison, cₚ cancels exactly.
> **TEEI rankings are mathematically independent of which fluid is heated.**

This means: choose your optimal heating source before knowing the process fluid.
Proved analytically in [`docs/02_formulation.md`](docs/02_formulation.md) §5.

---

## Installation

```bash
pip install teei
```

**Zero mandatory dependencies — pure Python 3.9+.**

```bash
pip install teei[coolprop]   # accurate cp,eff via CoolProp (optional)
pip install teei[pandas]     # tabular output from compare()
pip install teei[dev]        # pytest + ruff for development
```

---

## Quick start

```python
from teei import calculate, compare, tpp, cgit

# Single calculation — 200 L water, 10→60°C, Spain
r = calculate("water", "electric", country="ES", mass=200.0, delta_T=50.0)
print(f"Cost: {r.cost_total/100:.2f} €  |  CO₂: {r.co2_total/1000:.2f} kg  |  Time: {r.t_total/60:.1f} min")
# Cost: 2.05 €  |  CO₂: 0.63 kg  |  Time: 216.0 min

# Compare all 5 sources — TEEI scores
results = compare("water", ["electric","gas","solar","hp3","hp5"], country="DE",
                  mass=200.0, delta_T=50.0)
for r in results:
    print(f"  {r.rank}. {r.source_id:<8}  TEEI={r.teei:.1f}  €/yr={r.cost_total/100*365:.0f}")

# Policy scalars
t = tpp(country="DE", cop=3.0)
print(f"TPP Germany COP3: {t['tpp']:.3f} €/kWh  →  HP wins: {t['hp_wins']}")

c = cgit(cop=1.0)
print(f"CGIT resistance: {c['cgit']:.0f} g/kWh")
```

---

## Key results (from case studies)

### Case Study 01 — Outdoor Swimming Pool (50,000 L, 15→28°C)

Heat pump COP 5 achieves the highest TEEI score in **all 8 countries** studied.
Time to heat is **geographically invariant** (FTET depends only on cₚ and P_useful, not country).
CO₂ from electric heating varies **25×** across countries (Norway 21 kg vs India 540 kg).

![TEEI Heatmap — Swimming Pool](notebooks/figures/fig01_teei_heatmap.png)

### Case Study 02 — Domestic Hot Water (200 L/day, family of 4)

Heat pump COP 5 wins in **all 10 countries**. Germany achieves payback in **1.6 years**.
Switching from gas boiler to HP COP 3 in Germany saves **1,409 kg CO₂/year** (74% reduction).

![TEEI Heatmap — Domestic Hot Water](notebooks/figures/fig09_dhw_teei_heatmap.png)

![Annual Cost](notebooks/figures/fig10_dhw_annual_cost.png)

![Break-even Payback](notebooks/figures/fig12_dhw_payback.png)

---

## Available fluids (15)

| Fluid ID | Name | cₚ (J/kg·°C) |
|----------|------|-------------|
| `water` | Water | 4,184 |
| `seawater` | Seawater (3.5% NaCl) | 3,900 |
| `milk` | Whole milk | 3,930 |
| `wort` | Brewery wort (~12°P) | 3,950 |
| `ethylene_glycol` | Ethylene glycol | 2,380 |
| `propylene_glycol` | Propylene glycol | 2,500 |
| `ethanol` | Ethanol | 2,440 |
| `glycerol` | Glycerol | 2,380 |
| `olive_oil` | Olive oil | 1,970 |
| `engine_oil` | Engine oil SAE 30 | 1,900 |
| `molten_salt` | Solar Salt (60/40) | 1,500 |
| `blood` | Human blood | 3,617 |
| `mercury` | Mercury | 140 |
| `ammonia` | Liquid ammonia | 4,700 |
| `liquid_hydrogen` | Liquid hydrogen | 14,300 |

---

## Available heating sources (5)

| Source ID | Description | η / COP | CO₂ basis |
|-----------|-------------|---------|-----------|
| `electric` | Electric resistance heater | η = 0.99 | Grid (country-specific) |
| `gas` | Gas stove / boiler | η = 0.45 | 202 g/kWh (fixed, IPCC AR6) |
| `solar` | Solar flat-plate thermal | LCOE-based | 20 g/kWh (lifecycle) |
| `hp3` | Heat pump COP 3 | COP = 3.0 | Grid (country-specific) |
| `hp5` | Heat pump COP 5 | COP = 5.0 | Grid (country-specific) |

Custom sources accepted as dicts: `calculate("water", {"efficiency": 2.8, "price": 0.18, "co2_intensity": 150.0}, ...)`

---

## Country database (20 countries, auto-updated quarterly)

Data auto-updated via GitHub Actions from:
- **[EMBER](https://ember-energy.org/data/)** — grid CO₂ intensity (CC BY 4.0, 215 countries)
- **[Eurostat REST API](https://ec.europa.eu/eurostat/)** — EU electricity + gas prices
- **[EIA API](https://www.eia.gov/)** — US electricity prices

```python
from teei import list_countries, get_country, database_info
print(database_info())   # version, update date, country count
print(get_country("DE")) # electricity_price, gas_price, grid_co2
```

---

## Repository structure

```
fluid-thermal-index/
│
├── teei/                   # Python package (pip install teei)
│   ├── __init__.py         # Public API: calculate, compare, tpp, cgit
│   ├── _constants.py       # K1=3,600,000  K2=36,000  CO₂ refs
│   ├── metrics.py          # FTEU, FTEM, FTES (Model A/B), FTET, TEEI, TPP, CGIT
│   ├── fluids.py           # 15-fluid cp database, resolve_cp()
│   ├── sources.py          # 5-source parameter database, calc_p_useful()
│   ├── countries.py        # 20-country price + CO₂ loader
│   └── phase_check.py      # Single-phase validity (0.85 × T_boil safety margin)
│
├── data/
│   ├── fluids.json         # Fluid database (NIST / ASHRAE / Perry's)
│   ├── sources.json        # Source parameters (Spain 2026 defaults)
│   └── countries.json      # 20 countries — auto-updated quarterly
│
├── tests/
│   ├── test_metrics.py     # Unit tests: FTEU, FTEM, FTES, FTET, TPP, CGIT
│   │                       # Includes cp-invariance theorem verification
│   └── test_integration.py # End-to-end tests: calculate(), compare()
│
├── notebooks/
│   ├── 01_swimming_pool.py        # Case Study 01 — 50,000 L pool, 8 countries
│   ├── 02_domestic_hot_water.py   # Case Study 02 — 200 L/day, 10 countries
│   ├── 03_restaurant_kitchen.py   # Case Study 03 — [TODO]
│   ├── 04_milk_pasteurisation.py  # Case Study 04 — [TODO]
│   ├── 05_brewery.py              # Case Study 05 — [TODO]
│   ├── 06_aquaculture.py          # Case Study 06 — [TODO]
│   └── figures/                   # All generated figures (PNG, 300 DPI)
│
├── scripts/                # GitHub Actions data pipeline
│   ├── fetch_ember.py      # EMBER API → CO₂ intensity
│   ├── fetch_eurostat.py   # Eurostat API → EU energy prices
│   ├── fetch_eia.py        # EIA API → US prices
│   └── merge_countries.py  # Merge all sources → countries.json
│
├── web/                    # Interactive calculator (GitHub Pages) [TODO]
│   ├── index.html
│   └── app.js
│
├── docs/
│   ├── 01_project_log.md   # Project history, novelty audit
│   ├── 02_formulation.md   # Full theory: all equations, proofs
│   ├── 03_references.md    # Literature + data source citations
│   └── 04_roadmap.md       # Publication strategy, timeline
│
├── .github/
│   └── workflows/
│       ├── tests.yml           # Run pytest on push
│       ├── update-prices.yml   # Quarterly data update (cron)
│       └── deploy-web.yml      # Deploy web tool to GitHub Pages
│
├── pyproject.toml          # Package config (setuptools, pytest, ruff)
├── CITATION.cff            # Machine-readable citation [TODO]
├── LICENSE                 # MIT
└── README.md               # This file
```

---

## Running the tests

```bash
git clone https://github.com/Saination/fluid-thermal-index.git
cd fluid-thermal-index
pip install -e ".[dev]"
pytest tests/ -v
```

Expected output: **87 passed** (includes cp-invariance theorem verification).

---

## Running the case studies

```bash
# Case Study 01 — Swimming pool
PYTHONPATH=. python notebooks/01_swimming_pool.py

# Case Study 02 — Domestic hot water
PYTHONPATH=. python notebooks/02_domestic_hot_water.py
```

Figures saved to `notebooks/figures/`. No Jupyter required.

---

## Customisation

### Change figure colours or font sizes

All colour and style settings are at the **top of each notebook script**:

```python
# In notebooks/01_swimming_pool.py or 02_domestic_hot_water.py

# ── Font sizes (lines ~30–40) ────────────────────────────────────────────────
plt.rcParams.update({
    "font.size":        11,    # ← change global font size here
    "axes.titlesize":   13,    # ← change title size here
    "savefig.dpi":      300,   # ← change output resolution here
})

# ── Source colours (lines ~42–49) ───────────────────────────────────────────
SOURCE_COLORS = {
    "electric": "#2a78d6",   # ← change electric heater colour
    "gas":      "#eb6834",   # ← change gas colour
    "solar":    "#1baf7a",   # ← change solar colour
    "hp3":      "#4a3aa7",   # ← change heat pump COP 3 colour
    "hp5":      "#eda100",   # ← change heat pump COP 5 colour
}
```

### Use your own energy prices

```python
# Override any country price or CO₂ intensity
r = calculate("water", "electric",
              price=0.25,        # €/kWh — your local electricity price
              co2=200.0,         # g CO₂/kWh — your grid intensity
              mass=200.0, delta_T=50.0)
```

### Add a custom heating source

```python
my_boiler = {
    "efficiency": 0.92,          # condensing gas boiler (92% efficient)
    "price":      0.085,         # €/kWh gas
    "co2_intensity": 202.0,      # g CO₂/kWh (natural gas)
    "T_source_K":  450.0,        # K — heat exchanger temperature
}
r = calculate("water", my_boiler, mass=200.0, delta_T=50.0)
```

---

## Citation

If you use this work in your research, please cite:

```bibtex
@article{teei2026,
  title   = {{TEEI}: A $c_p$-Invariant Multi-Dimensional Index for Comparing
             Fluid Heating Sources Across Economic, Environmental,
             Thermodynamic, and Temporal Dimensions},
  author  = {[AUTHORS — TO BE ADDED]},
  journal = {Applied Energy},
  year    = {2026},
  note    = {Under review},
  url     = {https://github.com/Saination/fluid-thermal-index}
}
```

---

## Data sources and attribution

| Source | Data provided | Licence |
|--------|--------------|---------|
| [EMBER](https://ember-energy.org) | Grid CO₂ intensity (215 countries) | CC BY 4.0 |
| [Eurostat](https://ec.europa.eu/eurostat/) | EU electricity + gas prices | CC BY 4.0 |
| [EIA](https://www.eia.gov/) | US electricity prices | Public domain |
| [NIST WebBook](https://webbook.nist.gov/) | Fluid thermophysical properties | Public domain |
| [IPCC AR6](https://www.ipcc.ch/report/ar6/wg3/) | Natural gas CO₂ intensity (202 g/kWh) | CC BY 4.0 |

---

## Licence

**MIT © 2026 TEEI Project.** See [LICENSE](LICENSE).
EMBER data used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
