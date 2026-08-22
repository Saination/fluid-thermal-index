# Changelog

All notable changes to `teei` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.1.0] — 2026-08

### Added
- Core sub-metrics: `fteu`, `ftem`, `ftes` (Model A and B), `ftet`
- Composite TEEI index with adjustable weights
- Policy scalars: `tpp` (Thermal Parity Price), `cgit` (Carbon Grid Intensity Threshold)
- High-level API: `calculate()`, `compare()`
- Fluid database: 15 fluids with cp, T_boil, single-phase range (NIST / ASHRAE / Perry's)
- Source database: 5 heating sources (electric, gas, solar, hp3, hp5)
- Country database: 20 countries with electricity price, gas price, grid CO₂ intensity
- Single-phase phase checker with 0.85 × T_boil safety margin
- cp-invariance theorem: proved and verified in tests
- 87 unit and integration tests (100% pass rate)
- 6 case studies: swimming pool, domestic DHW, restaurant, milk pasteurisation,
  brewery, aquaculture
- 51 publication-quality figures (300 DPI PNG)
- Interactive web calculator (GitHub Pages)
- GitHub Actions: quarterly price update, CI tests, Pages deploy

### Data sources
- EMBER API (CC BY 4.0) — grid CO₂ intensity, 215 countries
- Eurostat REST API — EU electricity and gas prices (quarterly)
- EIA API — US electricity prices (monthly)
- NIST WebBook — fluid thermophysical properties
- IPCC AR6 — natural gas combustion intensity (202 g CO₂/kWh, fixed)
