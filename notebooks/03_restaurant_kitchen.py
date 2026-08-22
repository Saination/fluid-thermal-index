"""
Case Study 03 — Restaurant / Commercial Kitchen (900 L/day)
===========================================================
Standard figures: 17-23  |  Unique figure: 24
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

COVERS_PER_DAY = 100; OPERATING_DAYS = 300

CFG = {
    "label":        "CS03 — Restaurant Kitchen (900 L/day, water, 10°C→75°C)",
    "cs_id":        "cs03",
    "fluid":        "water",
    "mass":         900,
    "T_start":      10.0,
    "T_target":     75.0,
    "P_rated":      20.0,
    "solar_area":   15.0,
    "solar_irr":    650.0,
    "days_per_year":OPERATING_DAYS,
    "fig_offset":   16,
    "countries":    STD_COUNTRIES,
    "time_unit":    "min",
    "capex":        {"electric":500,"gas":2000,"solar":8000,"hp3":5000,"hp5":7000},
    "maintenance":  {"electric":50,"gas":300,"solar":150,"hp3":200,"hp5":220},
    "capex_years":  10,
    "cost_note":    "Commercial kitchen system, 10-year lifespan",
}

print("=" * 60); print("Case Study 03 — Restaurant Kitchen"); print("=" * 60)
saved, raw, teei_by_cc, fns = run(CFG, FIG_DIR)

# ── Fig 24: Cost per cover (€ per customer) ───────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
x = np.arange(len(STD_COUNTRIES)); n = len(SOURCES); width = 0.15
offsets = np.linspace(-(n-1)/2*width, (n-1)/2*width, n)
for si, src in enumerate(SOURCES):
    cpc = [fns["ann_cost"](cc,src) / (COVERS_PER_DAY*OPERATING_DAYS)
           for cc in STD_COUNTRIES]
    ax.bar(x+offsets[si], cpc, width, color=SOURCE_COLORS[src],
           label=SOURCE_LABELS[src], alpha=0.88, edgecolor="white", lw=0.5)
ax.set_xticks(x)
ax.set_xticklabels([fns["cnames"][c] for c in STD_COUNTRIES], rotation=20, ha="right")
ax.set_ylabel("Hot water energy cost per customer (€)")
ax.set_title(f"CS03 — Cost per cover: hot water energy per customer served\n"
             f"{COVERS_PER_DAY} covers/day, {OPERATING_DAYS} days/yr, 900 L/day")
ax.legend(fontsize=9, loc="upper right")
ax.yaxis.grid(True, alpha=0.35, ls="--"); ax.set_axisbelow(True)
plt.tight_layout(); p = os.path.join(FIG_DIR,"fig24_cs03_cost_per_cover.png")
plt.savefig(p); plt.close(); print(f"  Fig 24 saved → {os.path.basename(p)}")
print("\nCase Study 03 complete ✓")
