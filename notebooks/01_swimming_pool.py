"""
Case Study 01 — Outdoor Swimming Pool (50,000 L)
=================================================
Standard figures: 01-07  |  Unique figure: 08
Countries: ES FR DE NO PL GB US IN AU BR  (standard 10)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from teei import calculate, get_country
from notebooks.utils.standard_figures import (
    STYLE, SOURCES, SOURCE_COLORS, SOURCE_LABELS, STD_COUNTRIES, run)

plt.rcParams.update(STYLE)
FIG_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

CFG = {
    "label":        "CS01 — Outdoor Swimming Pool (50,000 L, water)",
    "cs_id":        "cs01",
    "fluid":        "water",
    "mass":         50_000,
    "T_start":      15.0,
    "T_target":     28.0,
    "P_rated":      10.0,
    "solar_area":   30.0,
    "solar_irr":    650.0,
    "days_per_year":365,
    "fig_offset":   0,
    "countries":    STD_COUNTRIES,
    "time_unit":    "h",
    "capex":        {"electric":2000,"gas":3000,"solar":12000,"hp3":8000,"hp5":11000},
    "maintenance":  {"electric":100,"gas":200,"solar":100,"hp3":150,"hp5":180},
    "capex_years":  15,
}

print("=" * 60)
print("Case Study 01 — Outdoor Swimming Pool"); print("=" * 60)
saved, raw, teei_by_cc, fns = run(CFG, FIG_DIR)

# ── Fig 08: Seasonal T_start sensitivity (Spain) ──────────────────────────────
t_starts = np.linspace(5, 22, 40); T_TARGET = 28.0
fig, ax = plt.subplots(figsize=(9, 5.5))
for src in SOURCES:
    costs = []
    for ts in t_starts:
        dt = T_TARGET - float(ts)
        if dt <= 0: costs.append(0.0); continue
        r = calculate("water", src, country="ES", mass=50000, delta_T=dt,
                      T_start=float(ts), P_rated=10.0, solar_area=30.0,
                      solar_irradiance=650.0, check_phase=False)
        costs.append(r.cost_total / 100)
    ax.plot(t_starts, costs, color=SOURCE_COLORS[src], lw=2.2, label=SOURCE_LABELS[src])
ax.axvline(15, color="gray", lw=1.2, ls="--", alpha=0.7, label="Spring reference (15°C)")
ax.axvline(8,  color="steelblue", lw=1.0, ls=":", alpha=0.6, label="Winter (8°C)")
ax.set_xlabel("Pool starting temperature T_start (°C)")
ax.set_ylabel("Cost to heat pool to 28°C (€ per fill)")
ax.set_title("CS01 — Seasonal sensitivity: cost to heat 50,000 L pool\nSpain | 10 kW | Solar 30 m²")
ax.legend(fontsize=9); ax.yaxis.grid(True, alpha=0.3, ls="--"); ax.set_axisbelow(True)
plt.tight_layout(); p = os.path.join(FIG_DIR,"fig08_cs01_seasonal_sensitivity.png")
plt.savefig(p); plt.close(); print(f"  Fig 08 saved → {os.path.basename(p)}")
print("\nCase Study 01 complete ✓")
