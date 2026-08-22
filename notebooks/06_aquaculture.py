"""
Case Study 06 — Salmon Aquaculture Tank (500,000 L seawater)
=============================================================
Standard figures: 41-47  |  Unique figure: 48
Countries: ES FR DE NO PL GB US IN AU BR  (standard 10)
Fluid: SEAWATER (cp=3,900 J/kg·°C), tiny ΔT=3°C, enormous mass
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from teei import calculate, resolve_cp
from notebooks.utils.standard_figures import (
    STYLE, SOURCES, SOURCE_COLORS, SOURCE_LABELS, STD_COUNTRIES, run)

plt.rcParams.update(STYLE)
FIG_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

CP_SEA = resolve_cp("seawater")

CFG = {
    "label":        "CS06 — Salmon Aquaculture (500,000 L seawater, 10°C→13°C)",
    "cs_id":        "cs06",
    "fluid":        "seawater",
    "mass":         500_000,
    "T_start":      10.0,
    "T_target":     13.0,
    "P_rated":      100.0,
    "solar_area":   50.0,
    "solar_irr":    400.0,     # reduced — winter average in Nordic regions
    "days_per_year":365,
    "fig_offset":   40,
    "countries":    STD_COUNTRIES,
    "time_unit":    "h",
    "capex":        {"electric":5000,"gas":15000,"solar":50000,"hp3":30000,"hp5":40000},
    "maintenance":  {"electric":200,"gas":600,"solar":500,"hp3":500,"hp5":600},
    "capex_years":  15,
    "cost_note":    "Industrial RAS salmon farm, 15-year lifespan",
}

print("=" * 60); print("Case Study 06 — Salmon Aquaculture"); print("=" * 60)
print(f"  Fluid: seawater  cp={CP_SEA} J/kg·°C  |  ΔT=3°C  |  Mass=500,000 kg")
print(f"  Solar irradiance reduced to {CFG['solar_irr']} W/m² (Nordic winter average)")
saved, raw, teei_by_cc, fns = run(CFG, FIG_DIR)

# ── Fig 48: Species ΔT comparison (annual cost, Norway, HP COP3) ──────────────
SPECIES = [
    ("Atlantic salmon", 10.0, 13.0, "#2a78d6"),
    ("Sea trout",       10.0, 15.0, "#1baf7a"),
    ("Turbot",          15.0, 18.0, "#4a3aa7"),
    ("Tilapia",         22.0, 28.0, "#eb6834"),
    ("Pacific shrimp",  20.0, 26.0, "#eda100"),
]
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

# Left: annual cost by species, all sources, Norway
ax = axes[0]
xi = np.arange(len(SPECIES)); w = 0.15; n = len(SOURCES)
off = np.linspace(-(n-1)/2*w,(n-1)/2*w,n)
for si, src in enumerate(SOURCES):
    costs = []
    for sp_name, ts, tt, _ in SPECIES:
        dt = tt - ts
        r = calculate("seawater", src, country="NO", mass=500000,
                      delta_T=dt, T_start=ts, P_rated=100.0, solar_area=50.0,
                      solar_irradiance=400.0, check_phase=False)
        costs.append(r.cost_total/100*365/1000)  # € thousands
    ax.bar(xi+off[si], costs, w, color=SOURCE_COLORS[src],
           label=SOURCE_LABELS[src], alpha=0.88, edgecolor="white", lw=0.5)
ax.set_xticks(xi)
ax.set_xticklabels([sp[0] for sp in SPECIES], rotation=15, ha="right")
ax.set_ylabel("Annual heating cost (€ thousands/year)")
ax.set_title("Annual cost by species — Norway\n500,000 L tank, 100 kW system")
ax.legend(fontsize=8, loc="upper left"); ax.yaxis.grid(True, alpha=0.3, ls="--"); ax.set_axisbelow(True)

# Right: ΔT vs annual cost sensitivity line plot
ax = axes[1]
dt_range = np.linspace(1, 15, 40)
for src in ["hp3","hp5","electric","gas"]:
    costs = []
    for dt in dt_range:
        r = calculate("seawater", src, country="NO", mass=500000,
                      delta_T=float(dt), T_start=10.0, P_rated=100.0,
                      solar_area=50.0, solar_irradiance=400.0, check_phase=False)
        costs.append(r.cost_total/100*365/1000)
    ax.plot(dt_range, costs, color=SOURCE_COLORS[src], lw=2.2, label=SOURCE_LABELS[src])
for sp_name, ts, tt, col in SPECIES:
    ax.axvline(tt-ts, color=col, lw=1.0, ls=":", alpha=0.7)
    ax.text(tt-ts+0.15, 0.5, sp_name.split()[0], fontsize=8, color=col,
            rotation=90, va="bottom")
ax.set_xlabel("Required ΔT (°C)")
ax.set_ylabel("Annual cost (€ thousands/year)")
ax.set_title("Annual cost vs required ΔT — Norway\n500,000 L seawater, 100 kW")
ax.legend(fontsize=8); ax.yaxis.grid(True, alpha=0.3, ls="--"); ax.set_axisbelow(True)

fig.suptitle("CS06 — Aquaculture: species ΔT comparison (Norway)",
             fontsize=12, fontweight="bold")
plt.tight_layout(); p = os.path.join(FIG_DIR,"fig48_cs06_species_comparison.png")
plt.savefig(p, bbox_inches="tight"); plt.close(); print(f"  Fig 48 saved → {os.path.basename(p)}")

print(f"\ncs06: tiny ΔT={CFG['T_target']-CFG['T_start']}°C but 500,000 kg → significant annual cost")
for cc in STD_COUNTRIES:
    b = teei_by_cc[cc][0].source_id
    ac = fns["ann_cost"](cc,b)/1000
    print(f"  {fns['cnames'][cc]:<14} → {SOURCE_LABELS[b]:<22} €{ac:.0f}k/yr")
print("\nCase Study 06 complete ✓")
