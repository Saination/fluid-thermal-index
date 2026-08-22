# GITHUB_NOTES.md
## fluid-thermal-index — Repository Setup Checklist

Everything needed before the repository goes public.
Check off items as completed.

---

## 1. Repository setup (one-time)

- [ ] Create GitHub account / organisation (suggested: `teei-project`)
- [ ] Create repository: `fluid-thermal-index` (public, MIT licence)
- [ ] Add `Saination` placeholder in README_GitHub.md → actual GitHub username
- [ ] Rename `README_GitHub.md` → `README.md` (replaces the current dev README)
- [ ] Create `LICENSE` file (MIT) — copy from https://opensource.org/license/mit
- [ ] Create `CITATION.cff` (see template below)
- [ ] Add `CHANGELOG.md` starting at v0.1.0
- [ ] Set default branch to `main`

### CITATION.cff template
```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
type: software
title: "fluid-thermal-index: TEEI — Thermal Economic-Environmental Index"
version: 0.1.0
date-released: "2026-XX-XX"
license: MIT
repository-code: "https://github.com/Saination/fluid-thermal-index"
authors:
  - family-names: "[SURNAME]"
    given-names: "[FIRST NAME]"
    affiliation: "[INSTITUTION]"
keywords:
  - thermal economics
  - heat pump
  - specific heat capacity
  - LCOH
  - cp-invariance
  - TEEI
```

---

## 2. Files to collect and add to the repository

### Already built — copy these directly:

```
teei/                        ← Python package (7 files) ✓
  __init__.py
  _constants.py
  metrics.py
  fluids.py
  sources.py
  phase_check.py
  countries.py

data/                        ← JSON databases ✓
  fluids.json
  sources.json
  countries.json

tests/                       ← 87 tests ✓
  __init__.py
  test_metrics.py
  test_integration.py

notebooks/                   ← Case studies ✓
  01_swimming_pool.py         (8 figures generated)
  02_domestic_hot_water.py    (8 figures generated)
  figures/                    (16 PNG files, 300 DPI)

docs/                        ← Documentation ✓
  01_project_log.md
  02_formulation.md          (K2 = 36,000 corrected)
  03_references.md
  04_roadmap.md

pyproject.toml               ✓
README_GitHub.md             ✓  (rename to README.md)
GITHUB_NOTES.md              ← This file
```

### Still to build (mark when done):

```
notebooks/
  03_restaurant_kitchen.py   ← [ ] Case Study 03
  04_milk_pasteurisation.py  ← [ ] Case Study 04
  05_brewery.py              ← [ ] Case Study 05
  06_aquaculture.py          ← [ ] Case Study 06

scripts/                     ← [ ] GitHub Actions data pipeline
  fetch_ember.py
  fetch_eurostat.py
  fetch_eia.py
  merge_countries.py

.github/workflows/           ← [ ] GitHub Actions YAML files
  tests.yml
  update-prices.yml
  deploy-web.yml

web/                         ← [ ] Interactive calculator (GitHub Pages)
  index.html
  app.js

LICENSE                      ← [ ] MIT licence text
CITATION.cff                 ← [ ] Machine-readable citation
CHANGELOG.md                 ← [ ] Version history
```

---

## 3. GitHub Actions workflows (YAML files to create)

### tests.yml — run pytest on every push
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --tb=short
```

### update-prices.yml — quarterly data refresh
```yaml
name: Update country price data
on:
  schedule:
    - cron: '0 0 1 */3 *'   # 1 Jan, 1 Apr, 1 Jul, 1 Oct
  workflow_dispatch:          # allow manual trigger
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install requests
      - run: python scripts/fetch_ember.py
      - run: python scripts/fetch_eurostat.py
      - run: python scripts/fetch_eia.py
        env: { EIA_API_KEY: ${{ secrets.EIA_KEY }} }
      - run: python scripts/merge_countries.py
      - name: Commit updated data
        run: |
          git config user.email "action@github.com"
          git config user.name "GitHub Action"
          git add data/countries.json data/update_log.json
          git diff --staged --quiet || \
            git commit -m "auto: update country prices + CO₂ ($(date +%Y-%m-%d))"
          git push
```

### deploy-web.yml — deploy interactive calculator to GitHub Pages
```yaml
name: Deploy web tool
on:
  push:
    branches: [main]
    paths: ['web/**', 'data/**']
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with: { path: web/ }
      - uses: actions/deploy-pages@v4
        id: deployment
```

---

## 4. Secrets to add in GitHub repository settings

```
Settings → Secrets and variables → Actions → New repository secret

EIA_KEY          ← EIA API key (free, from https://www.eia.gov/opendata/register.php)
PYPI_API_TOKEN   ← PyPI token for pip publish (when ready to publish package)
```

---

## 5. PyPI publication (when ready)

```bash
# Test on TestPyPI first
pip install build twine
python -m build
twine upload --repository testpypi dist/*

# Then publish to real PyPI
twine upload dist/*
```

Update README.md badge from
`[![PyPI version](https://img.shields.io/pypi/v/teei.svg)](https://pypi.org/project/teei/)`
to show real version once published.

---

## 6. Web tool (GitHub Pages)

The interactive calculator (`web/`) should be the widget we built in claude.ai,
exported as a standalone HTML + JS file. Checklist:

- [ ] Export the TEEI widget as `web/index.html` (self-contained)
- [ ] Bundle `data/countries.json` + `data/fluids.json` into the page
- [ ] Add "last updated" timestamp from `data/update_log.json`
- [ ] Enable GitHub Pages: Settings → Pages → Source: main branch, /web folder
- [ ] Update README badge URL once page is live

---

## 7. Paper submission checklist (Applied Energy)

- [ ] Paper draft complete (see 04_roadmap.md for structure)
- [ ] All 6 case studies complete (4 remaining)
- [ ] Figures at 300 DPI, single-column (8.5 cm) and double-column (17.5 cm) widths
- [ ] Proposition 1 (cp-invariance) formally stated with full proof
- [ ] Supplementary material: full country database table
- [ ] Cover letter written
- [ ] Graphical abstract prepared (Applied Energy requires one)
- [ ] Highlights (5 bullet points, ≤85 chars each) — draft below:

```
• TEEI: a four-dimensional metric comparing heating sources across cost,
  carbon, entropy, and time for any fluid
• cp-invariance theorem: source rankings are mathematically independent
  of fluid choice
• TPP and CGIT give country-specific economic and carbon tipping points
• Heat pump COP 5 achieves highest TEEI in all 10 countries studied
• Open-source Python package teei with 20-country live price database
```

- [ ] ORCID IDs for all authors
- [ ] Funding statement
- [ ] Declaration of competing interests
- [ ] Data availability statement (link to GitHub repository)

---

## 8. Things to not forget

| Item | Status | Note |
|------|--------|------|
| K₂ = 36,000 (not 36,000,000) | ✓ Fixed | In `_constants.py` and `02_formulation.md` |
| COP sources are hp3 and hp5 | ✓ | COP=1.0 is only a `tpp()` formula edge case |
| Single-phase scope | ✓ | Phase check in `phase_check.py`, 0.85 × T_boil margin |
| cp,eff for variable-cp fluids | ✓ Defined | CoolProp integration deferred to v0.2 |
| "micro-economics" → "micro-scale techno-economic" | ✓ | Throughout paper and docs |
| EMBER data attribution | ☐ | CC BY 4.0 — must appear in paper + web tool |
| CGIT for HP always > any real grid | ✓ | Verified in tests (CGIT HP3 = 1,347 g/kWh) |
| All 87 tests passing | ✓ | Run `pytest tests/ -v` to verify |
| Solar LCOE assumption | ☐ | €0.067/kWh — update annually; document in paper |
| Country T_cold variations | ✓ | In Case Study 02; document source in paper |
| Payback calculation excludes maintenance diff | ☐ | Note this limitation in paper |
| Figure numbering for paper | ☐ | Figs 1–N still to be assigned in LaTeX |
| Graphical abstract (Applied Energy) | ☐ | Prepare separately |

---

*Last updated: August 2026*
