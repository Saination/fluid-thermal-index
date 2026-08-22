"""
Case Study 02 — Domestic Hot Water (200 L/day, family of 4)
============================================================
Standard figures: 09-15  |  Unique figure: 16
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

# Country-specific cold water inlet temperatures
T_COLD = {"ES":14,"FR":12,"DE":10,"NO":6,"PL":9,"GB":11,"US":13,"IN":24,"AU":18,"BR":22}
T_TARGET = 60.0

CFG = {
    "label":        "CS02 — Domestic Hot Water (200 L/day, 10°C→60°C)",
    "cs_id":        "cs02",
    "fluid":        "water",
    "mass":         200,
    "T_start":      10.0,          # standard reference; sensitivity tested in fig 16
    "T_target":     T_TARGET,
    "P_rated":      3.0,
    "solar_area":   4.0,
    "solar_irr":    650.0,
    "days_per_year":365,
    "fig_offset":   8,
    "countries":    STD_COUNTRIES,
    "time_unit":    "min",
    "capex":        {"electric":300,"gas":800,"solar":2500,"hp3":1800,"hp5":2400},
    "maintenance":  {"electric":20,"gas":80,"solar":40,"hp3":50,"hp5":55},
    "capex_years":  15,
    "cost_note":    "Domestic water heater, 15-year lifespan",
}

print("=" * 60); print("Case Study 02 — Domestic Hot Water"); print("=" * 60)
saved, raw, teei_by_cc, fns = run(CFG, FIG_DIR)

# ── Fig 16: Country-specific T_cold effect on annual cost ─────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))
t_cold_range = np.linspace(4, 26, 50)
for src in SOURCES:
    costs = []
    for tc in t_cold_range:
        dt = T_TARGET - float(tc)
        r = calculate("water", src, country="ES", mass=200, delta_T=dt,
                      T_start=float(tc), P_rated=3.0, solar_area=4.0,
                      solar_irradiance=650.0, check_phase=False)
        costs.append(r.cost_total / 100 * 365)
    ax.plot(t_cold_range, costs, color=SOURCE_COLORS[src], lw=2.2, label=SOURCE_LABELS[src])

for cc in STD_COUNTRIES:
    tc = T_COLD[cc]
    ax.axvline(tc, color="gray", lw=0.6, ls=":", alpha=0.5)
    ax.text(tc+0.2, ax.get_ylim()[1]*0.02 if ax.get_ylim()[1]>0 else 5,
            fns["cnames"][cc][:2], fontsize=7.5, color="gray", rotation=90)

ax.set_xlabel("Cold water inlet temperature T_cold (°C)")
ax.set_ylabel("Annual energy cost (€/year)")
ax.set_title("CS02 — Annual DHW cost vs cold-water inlet temperature\n"
             "Spain prices | 200 L/day | target 60°C")
ax.legend(fontsize=9); ax.yaxis.grid(True, alpha=0.3, ls="--"); ax.set_axisbelow(True)
plt.tight_layout(); p = os.path.join(FIG_DIR,"fig16_cs02_tcold_sensitivity.png")
plt.savefig(p); plt.close(); print(f"  Fig 16 saved → {os.path.basename(p)}")
print("\nCase Study 02 complete ✓")
