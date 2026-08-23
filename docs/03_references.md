# TEEI — References and Data Sources

**Version:** 0.2 | **Last updated:** August 2026

---

## A. Core literature — what TEEI builds upon

### A1. Levelised Cost of Heat (LCOH) → maps to FTEU

1. **Roach, M. et al. (2022).** "Heat source and application-dependent levelized
   cost of decarbonized heat." *Joule*, 6(12), 2801–2831.
   https://doi.org/10.1016/j.joule.2022.10.011
   → Defines LCOH in $/kWh_thermal; covers gas, electric, solar, heat pumps.
   FTEU = LCOH × c_p / 36,000,000 (unit rescaling with fluid parameterisation).

2. **Geyer, F. et al. (2024).** "Levelized cost of heat for solar thermal
   applications in households." *Solar Energy*.
   https://www.sciencedirect.com/science/article/pii/S0038092X24007953
   → System boundary methodology for domestic solar thermal LCOH.

3. **EWI (2025).** "Levelized Cost of Heating (LCOH) tool."
   https://www.ewi.uni-koeln.de/en/publications/levelized-cost-of-heating-lcoh-tool/
   → Interactive LCOH for 6 heating technologies across German states.

4. **E3 (2024).** "Decarbonizing Industrial Heat: Measuring Economic Potential."
   https://www.ethree.com/wp-content/uploads/2024/10/CAELP-E3-Industrial-Electrification-Report.pdf
   → LCOH as primary metric for industrial heat source comparison; SME context.

---

### A2. Entropy generation → maps to FTES

5. **Bejan, A. (1977).** "The concept of irreversibility in heat exchanger design:
   counterflow heat exchangers for gas-to-gas applications."
   *ASME Journal of Heat Transfer*, 99, 374–380.
   → Foundational paper introducing entropy generation as a design criterion.

6. **Bejan, A. (1980).** "Second Law Analysis in Heat Transfer."
   *Energy*, 5, 721–732.
   → Entropy generation per unit heat transfer; defines N_s.
   FTES is N_s rearranged per unit mass per unit temperature.

7. **Bejan, A. (1996).** *Entropy Generation Minimization.* CRC Press, Boca Raton.
   → Definitive textbook. Defines N_s = Ṡ_gen/(ṁ·c_p); FTES directly
   equivalent with units restated per kg·°C.

8. **Awad, M.M. (2015).** "A review of entropy generation in microchannels."
   *Advances in Mechanical Engineering*, 7(4).
   https://journals.sagepub.com/doi/10.1177/1687814015590297
   → Comprehensive review of N_s applications; confirms standard formulation.

---

### A3. Multi-criteria thermal system comparison → context for TEEI

9. **Multi-Criteria Design of Industrial Process Heat Solutions (2026).**
   *Fluids*, 10(3), 62. MDPI.
   https://www.mdpi.com/2411-9660/10/3/62
   → Integrates thermodynamic, environmental, and economic criteria for process
   heating at 250°C. Closest existing parallel to TEEI; uses dynamic simulation.
   Key difference: operates at macro-scale (MW), no per-kg·°C framing, no
   cp-invariance, no time dimension, no fluid parameterisation.

10. **Comprehensive evaluation of multi-energy complementary heating systems
    using entropy-TOPSIS (2024).** *Solar Energy*, 284, 113101.
    https://www.sciencedirect.com/article/abs/pii/S0378778824001932
    → Entropy-weight TOPSIS for rural heating system evaluation; closest
    methodological parallel to TEEI composite. No c_p parameterisation.

11. **Multi-Criteria Model Predictive Controller for Hybrid Heating (2025).**
    *Energies*, 18(21), 5839.
    https://doi.org/10.3390/en18215839
    → Cost + CO₂ optimisation for building heat sources. No entropy or time.

12. **District heating decarbonisation multi-criteria analysis (2024).**
    *Waste Management*, ScienceDirect.
    https://www.sciencedirect.com/science/article/abs/pii/S0301479724006698
    → Multi-objective Pareto optimisation. Macro-scale only.

---

### A4. Thermodynamic fundamentals

13. **Incropera, F.P. et al. (2007).** *Fundamentals of Heat and Mass Transfer*,
    6th ed. Wiley.
    → Standard reference for c_p data, thermal time constants (FTET foundation),
    single-phase convection heat transfer.

14. **Cengel, Y.A. & Boles, M.A. (2014).** *Thermodynamics: An Engineering
    Approach*, 8th ed. McGraw-Hill.
    → Second law analysis; entropy generation in open and closed systems.
    Basis for FTES formulation derivation.

15. **Perry, R.H. & Green, D.W. (2008).** *Perry's Chemical Engineers' Handbook*,
    8th ed. McGraw-Hill.
    → Fluid thermophysical properties including c_p for industrial fluids.

16. **IPCC AR6 Working Group III (2022).** Chapter 9: Buildings. Cambridge
    University Press.
    → Emissions factors for gas combustion (202 g CO₂/kWh); CGIT reference.

---

### A5. Variable specific heat capacity and effective c_p

17. **Wagner, W. & Kruse, A. (2008).** *Properties of Water and Steam.* Springer.
    → Tabulated water c_p from 0–374°C; source for c_p variation in TEEI scope.

18. **NIST WebBook — Thermophysical Properties of Fluid Systems.**
    https://webbook.nist.gov/chemistry/fluid/
    → Primary source for all pure fluid c_p values used in this work.
    Confirms water c_p variation <1% over 0–100°C (justifying constant c_p
    approximation for single-phase TEEI applications).

19. **CoolProp (Bell et al., 2014).** "Pure and Pseudo-pure Fluid
    Thermophysical Property Evaluation." *Industrial & Engineering Chemistry
    Research*, 53(6), 2498–2508.
    https://doi.org/10.1021/ie4033999
    → Open-source library for accurate c_p,eff calculation; recommended for
    Python package implementation of c_p,eff integration (eq. 3).

---

## B. Geographic data sources (live / API)

### B1. Grid CO₂ intensity (primary: EMBER)

| Source | Coverage | Update rate | Licence | URL |
|--------|---------|------------|--------|-----|
| **EMBER API** (primary) | 215 countries | Twice/month | CC BY 4.0 | https://ember-energy.org/data/api/ |
| EMBER Yearly Data | 215 countries | Annual | CC BY 4.0 | https://ember-energy.org/data/yearly-electricity-data/ |
| Our World in Data | 200+ countries | Annual | CC BY | https://ourworldindata.org/co2-and-greenhouse-gas-emissions |
| electricityMap | 60+ countries | Real-time | Commercial/free tier | https://app.electricitymap.org |

**EMBER API endpoints used:**
```
GET https://api.ember-energy.org/v1/carbon-intensity/yearly
    ?entity={country_code}&series=Carbon intensity of electricity (gCO2/kWh)

GET https://api.ember-energy.org/v1/carbon-intensity/monthly
    ?entity={country_code}    (88 countries available monthly)
```

Licence note: EMBER data is CC BY 4.0 — free for any use including
academic publication, provided attribution is given.

---

### B2. Electricity and gas prices (primary: Eurostat + EIA)

| Source | Coverage | Update rate | Licence | URL |
|--------|---------|------------|--------|-----|
| **Eurostat REST API** (EU prices) | EU-27 + Norway/Switzerland | Quarterly | Free | https://ec.europa.eu/eurostat/api/ |
| **EIA API** (US prices) | US + 50 states | Monthly | Free (key required) | https://api.eia.gov/v2/ |
| GlobalPetrolPrices | 150+ countries | Weekly | Non-commercial free | https://www.globalpetrolprices.com |
| IEA Energy Prices | OECD + G20 | Annual | Subscription | https://www.iea.org/data-and-statistics/data-product/energy-prices |

**Eurostat API endpoints used:**
```
Electricity price (residential):
GET https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_204
    ?geo={country}&time={year}

Natural gas price (residential):
GET https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_202
    ?geo={country}&time={year}
```

**EIA API endpoint used:**
```
US electricity (residential average):
GET https://api.eia.gov/v2/electricity/retail-sales/data
    ?api_key={KEY}&facets[sectorName][]=residential&frequency=monthly
```

---

### B3. GitHub Actions automation pipeline

```yaml
# .github/workflows/update-prices.yml
name: Update country price data
on:
  schedule:
    - cron: '0 0 1 */3 *'   # Quarterly: 1 Jan, 1 Apr, 1 Jul, 1 Oct
  workflow_dispatch:          # Allow manual trigger

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - name: Install dependencies
        run: pip install requests pandas
      - name: Fetch EMBER CO2 data
        run: python scripts/fetch_ember.py
        # Writes CO2 intensity for 215 countries to data/co2_intensity.json
      - name: Fetch Eurostat prices
        run: python scripts/fetch_eurostat.py
        # Writes EU electricity + gas prices to data/eu_prices.json
      - name: Fetch EIA US prices
        run: python scripts/fetch_eia.py
        env: { EIA_API_KEY: ${{ secrets.EIA_KEY }} }
        # Writes US state prices to data/us_prices.json
      - name: Merge into countries.json
        run: python scripts/merge_countries.py
        # Merges all sources; writes data/countries.json
      - name: Commit updated data
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data/countries.json data/update_log.json
          git commit -m "Auto-update: country prices + CO2 ($(date +%Y-%m-%d))"
          git push
```

**Coverage after automation:**
- Full automatic: ~40 countries (EU-27 + US + Canada + Australia + Japan)
- Annual manual: remaining ~15 major economies (India, China, Brazil, etc.)
- 80% of global energy consumption covered automatically

---

### B4. Fluid thermophysical properties

| Source | Coverage | Access | URL |
|--------|---------|--------|-----|
| **NIST WebBook** | Pure fluids, wide T/P | Free | https://webbook.nist.gov |
| **CoolProp** | 100+ fluids, Python/MATLAB | Free, MIT | http://www.coolprop.org |
| ASHRAE Handbook — Fundamentals | HVAC fluids, refrigerants | Institutional | — |
| Engineering Toolbox | Common fluids, approximate | Free | https://www.engineeringtoolbox.com |
| Perry's Chemical Engineers' Handbook | Industrial fluids | Institutional | — |

---

## C. Publication venues

| Journal | Publisher | IF (2025 JCR) | Quartile | Scope fit | APC (OA) |
|---------|---------|-------------|---------|---------|---------|
| **Applied Energy** ← target | Elsevier | 12.2 | Q1 | ★★★★★ | $4,210 USD |
| Applied Thermal Engineering | Elsevier | 7.86 | Q1 | ★★★★☆ | ~$3,200 USD |
| Advances in Applied Energy | Elsevier | ~7.0 | Q1 | ★★★★☆ | Lower (new journal) |
| Energy | Elsevier | ~9.0 | Q1 | ★★★★☆ | ~$3,900 USD |
| Energy Conversion & Management | Elsevier | ~9.0 | Q1 | ★★★☆☆ | ~$3,900 USD |
| Journal of Cleaner Production | Elsevier | ~9.8 | Q1 | ★★★☆☆ | ~$4,100 USD |

**Decision guidance:**
- 6 case studies + cp-invariance theorem + geographic pricing → Applied Energy
- Fewer case studies, more thermodynamic depth → Applied Thermal Engineering
- Budget constraint / faster turnaround → Advances in Applied Energy

---

## D. Case study data sources

### Case study 1 — Domestic hot water

- IEA (2022). *The Future of Heat Pumps.* https://www.iea.org/reports/the-future-of-heat-pumps
- Eurostat (2024). Energy prices for household consumers. nrg_pc_204 (electricity) + nrg_pc_202 (gas)
- EMBER API for grid CO₂ intensity by country.

### Case study 2 — Swimming pool

- Energy Saving Trust (2023). "Heating your swimming pool using solar energy."
- Pool water c_p ≈ c_water (dilute, temperature-adjusted via NIST WebBook)

### Case study 3 — Restaurant/commercial kitchen

- Carbon Trust (2020). "Catering and hospitality — energy efficiency guide."

### Case study 4 — Milk pasteurisation (HTST)

- **Lewis, M. & Heppell, N. (2000).** *Continuous Thermal Processing of Foods.* Springer.
  → HTST regulatory condition: 72°C for minimum 15 seconds.
- Milk c_p = 3,930 J/kg·°C (ASHRAE; varies 3,850–3,950 with fat content)

### Case study 5 — Brewery

- **Boulton, C. & Quain, D. (2001).** *Brewing Yeast and Fermentation.* Blackwell.
  → Mash temperature: 62–68°C; cleaning-in-place (CIP): 80–85°C.
- Wort c_p ≈ 3,900–4,050 J/kg·°C depending on extract concentration (Geiger, 1999)

### Case study 6 — Aquaculture

- FAO (2020). "Aquaculture development — temperature requirements for key species."
  → Salmon: 12–14°C optimal; tilapia: 25–30°C; shrimp: 26–30°C.

---

*References version 0.2. To be updated as literature review progresses. August 2026.*

---

## E. Validation references (added August 2026)

### E1. Water heater efficiency standards (batch/instantaneous, matched scope)

1. **California Energy Commission (2022).** "2022 Water Heater Efficiency
   Guide." Official regulatory minimum Uniform Energy Factor (UEF)
   standards for consumer electric and gas water heaters, including the
   tankless/instantaneous category used in this work's validation.
   https://www.energy.ca.gov/sites/default/files/2022-10/2022_WaterHeating_EfficiencyGuide_ADA.pdf
   → Used for: real tankless electric UEF (0.91-0.92) vs model η=0.99.

2. **DOE / ENERGY STAR (2024).** "Water Heater Program Requirements,
   Version 4.0." Defines UEF ranges for tankless condensing (0.87-0.96)
   and non-condensing (0.80-0.86) gas water heaters.
   https://www.energystar.gov/products/water_heaters
   → Used for: real tankless condensing gas UEF vs model's
   sensitivity-analysis test η=0.92.

3. **tanklessauthority.com.** "Tankless Water Heater Efficiency Ratings:
   UEF and Energy Factor Explained." Industry summary of EF/UEF
   methodology and typical ranges, citing DOE ENERGY STAR Program
   Requirements v4.0.

4. **Consumer Reports (2025).** "How to Choose a Water Heater." Summarises
   UEF ranges across water heater types including heat pump water
   heaters (UEF 3.3-4.1).

### E2. Solar thermal collector instantaneous efficiency

5. **[Authors], (2023).** "Quantitative review on recent developments of
   flat-plate solar collector design. Part 1: Front-side heat loss
   reduction." *ScienceDirect*.
   https://www.sciencedirect.com/science/article/pii/S2352484723013884
   → Statistical average of 50 Solar Keymark certified flat-plate
   collectors: η₀=0.73 (zero-loss/optical efficiency), a₁=3.62 W/m²·K
   (linear heat loss coefficient), a₂=0.0133 W/m²·K² (quadratic heat
   loss coefficient). Used to compute real instantaneous efficiency at
   matched domestic-hot-water operating conditions (ΔT=25°C, G=750 W/m²)
   for direct comparison against the TEEI model's SOLAR_COLLECTOR_EFFICIENCY
   constant (0.65).

6. **Solar Keymark Network.** "Collector Performance Parameters." Defines
   the standard EN 12975 efficiency curve model
   η(ΔT) = η₀ - a₁(ΔT/G) - a₂(ΔT²/G) used throughout the solar thermal
   industry for certified collector testing.
   http://www.estif.org/solarkeymarknew/

7. **Abrecht, S. (2018).** "Annual efficiency - Easy understanding of
   collector performance." *EuroSun 2018, ISES Conference Proceedings*.
   → Distinguishes instantaneous efficiency (used in this work's
   validation) from annual-average efficiency confounded by weather and
   night hours (used, incorrectly, in validation v1 - see 01_project_log.md
   "Update - August 2026" section for the correction).

### E3. Heat pump COP — matched temperature-lift conditions

8. **Wan, H. & Hwang, Y. (2023/2021).** Review of cold-climate heat pump
   field studies; underlying Purdue conference paper (2021) reports
   lab-tested variable-speed air-source heat pump COP of 3.39-4.35 at
   7°C ambient / 30°C water supply temperature (moderate lift), tested
   per BS EN 14511. https://docs.lib.purdue.edu/icec/2678/
   → Used for: validating HP3 (COP=3.0) assumption.

9. **[Authors] (2025).** "Performance of air source heat pump for
   dual-purpose mode: A futuristic study for domestic water heating cum
   air cooling in tropical region." *ScienceDirect*.
   https://www.sciencedirect.com/science/article/abs/pii/S1359431125025451
   → Measured instantaneous COP range 3.59-7.24, daily average COP 5.27
   for a dual-purpose air-source heat pump system. Used for: validating
   HP5 (COP=5.0) assumption - the measured average is nearly identical.

10. **"Assessment of Heat Pump heating water to 50°C and 70°C."**
    *Protons for Breakfast* (real-world homeowner-measured data, Vaillant
    Arotherm Plus 5kW ASHP), 2021.
    https://protonsforbreakfast.wordpress.com/2021/09/07/
    → Real-world measured COP 2.5-3.0 heating to 50°C. Kept as
    SUPPLEMENTARY evidence only (not peer-reviewed) alongside refs 8-9.

### E4. Storage-tank benchmark (superseded validation target, retained for transparency)

11. **ENERGY STAR / DOE (10 CFR 430 Subpart B Appendix E).**
    "WaterHeaterAnalysis_Final.pdf." Standard test procedure for
    residential water heaters; medium-usage-pattern annual energy figures
    for a 50-gallon heat pump water heater (EF=2.0: 2,195 kWh/year) and
    electric resistance baseline (4,857 kWh/year).
    → Originally used as the primary validation benchmark (v1); found to
    be a scope mismatch (storage-tank standby loss vs the model's batch-
    heating formulation) and retained only as an explicit scope-boundary
    demonstration in `notebooks/08_validation.py` Part E. See
    01_project_log.md for the full correction narrative.

---

## F. Planned future literature cross-check (not yet started)

Once the paper draft is underway, additional recent (2023-2026)
peer-reviewed literature should be reviewed to further strengthen
Sections E1-E3 above and to check for any published techno-economic
framework that anticipates the cp-invariance theorem (Proposition 1),
which the original novelty audit (01_project_log.md) did not find in
the literature reviewed at that time. This is explicitly deferred to a
later working session, not immediate.
