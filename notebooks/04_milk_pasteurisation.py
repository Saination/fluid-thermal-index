"""
Case Study 04 — SME Milk Pasteurisation (5,000 L/day)
======================================================
Standard figures: 25-31  |  Unique figure: 32
Countries: ES FR DE NO PL GB US IN AU BR  (standard 10)
Fluid: MILK (cp = 3,930 J/kg·°C) — demonstrates cp-invariance
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

CP_MILK  = resolve_cp("milk");  CP_WATER = resolve_cp("water")
DAILY_L  = 5000; OP_DAYS = 250

CFG = {
    "label":        f"CS04 — Milk Pasteurisation HTST (5,000 L/day, milk, 4°C→72°C)",
    "cs_id":        "cs04",
    "fluid":        "milk",
    "mass":         DAILY_L,
    "T_start":      4.0,
    "T_target":     72.0,
    "P_rated":      30.0,
    "solar_area":   20.0,
    "solar_irr":    650.0,
    "days_per_year":OP_DAYS,
    "fig_offset":   24,
    "countries":    STD_COUNTRIES,
    "time_unit":    "min",
    "capex":        {"electric":1500,"gas":4000,"solar":12000,"hp3":8000,"hp5":11000},
    "maintenance":  {"electric":100,"gas":400,"solar":200,"hp3":300,"hp5":350},
    "capex_years":  10,
    "cost_note":    "SME dairy, HTST heat exchanger, 10-year lifespan",
}

print("=" * 60); print("Case Study 04 — Milk Pasteurisation"); print("=" * 60)
print(f"  Fluid: milk  cp={CP_MILK} J/kg·°C  "
      f"({(1-CP_MILK/CP_WATER)*100:.1f}% lower than water cp={CP_WATER})")
saved, raw, teei_by_cc, fns = run(CFG, FIG_DIR)

# ── Fig 32: cp-invariance — milk vs water FTEU comparison ────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

# Left: FTEU bar chart, milk vs water side by side
ax = axes[0]
xi = np.arange(len(SOURCES)); w = 0.35
for fi, (fid, cp_v, col) in enumerate([("milk",CP_MILK,"#eb6834"),
                                        ("water",CP_WATER,"#2a78d6")]):
    vals = [calculate(fid, src, country="ES", mass=1, delta_T=1,
                      check_phase=False).fteu * 1e3 for src in SOURCES]
    ax.bar(xi + fi*w - w/2, vals, w, color=col, alpha=0.85,
           label=f"{fid.capitalize()} (cp={cp_v:,})", edgecolor="white")
ax.set_xticks(xi)
ax.set_xticklabels([SOURCE_LABELS[s] for s in SOURCES], fontsize=9)
ax.set_ylabel("FTEU × 10³  (milli-cents/kg·°C)")
ax.set_title("FTEU: milk vs water — same source rankings\ndifferent absolute values")
ax.legend(fontsize=9); ax.yaxis.grid(True, alpha=0.3, ls="--"); ax.set_axisbelow(True)
ax.text(0.5,-0.15, f"Milk FTEU = {CP_MILK/CP_WATER:.4f} × Water FTEU  "
        f"(ratio = cp_milk/cp_water = {CP_MILK}/{CP_WATER})",
        transform=ax.transAxes, ha="center", fontsize=9, color="gray")

# Right: TEEI ranking table — identical for both fluids
ax = axes[1]
from teei import compare
rank_milk  = [r.source_id for r in compare("milk","electric gas solar hp3 hp5".split(),
              country="ES", mass=1, delta_T=1, check_phase=False)]
rank_water = [r.source_id for r in compare("water","electric gas solar hp3 hp5".split(),
              country="ES", mass=1, delta_T=1, check_phase=False)]
for si, (rm, rw) in enumerate(zip(rank_milk, rank_water)):
    pos_m = "electric gas solar hp3 hp5".split().index(rm) + 1
    pos_w = "electric gas solar hp3 hp5".split().index(rw) + 1
    ax.text(0.25, si, f"{pos_m}. {SOURCE_LABELS[rm]}", ha="left", va="center",
            fontsize=11, color=SOURCE_COLORS[rm], fontweight="bold",
            transform=ax.get_yaxis_transform())
    ax.text(0.75, si, f"{pos_w}. {SOURCE_LABELS[rw]}", ha="left", va="center",
            fontsize=11, color=SOURCE_COLORS[rw], fontweight="bold",
            transform=ax.get_yaxis_transform())
ax.text(0.25, -0.8, "Milk ranking", ha="left", fontsize=10, fontweight="bold",
        color="#eb6834", transform=ax.get_yaxis_transform())
ax.text(0.75, -0.8, "Water ranking", ha="left", fontsize=10, fontweight="bold",
        color="#2a78d6", transform=ax.get_yaxis_transform())
ax.set_ylim(-1.5, len(SOURCES))
ax.set_xlim(0, 1); ax.axis("off")
ax.set_title("TEEI rankings: identical for milk and water\nProposition 1 confirmed ✓")
match = rank_milk == rank_water
ax.text(0.5, len(SOURCES)+0.3, "✓ Rankings identical" if match else "✗ Mismatch",
        ha="center", fontsize=12, color="green" if match else "red",
        fontweight="bold", transform=ax.get_yaxis_transform())

fig.suptitle("CS04 — cp-invariance theorem: milk vs water (Spain, equal weights)",
             fontsize=12, fontweight="bold")
plt.tight_layout(); p = os.path.join(FIG_DIR,"fig32_cs04_cp_invariance.png")
plt.savefig(p); plt.close(); print(f"  Fig 32 saved → {os.path.basename(p)}")

cpl_best = {cc: fns["ann_cost"](cc,teei_by_cc[cc][0].source_id)/(DAILY_L*OP_DAYS)
            for cc in STD_COUNTRIES}
print("\nKey findings — cost per litre processed (best source):")
for cc in STD_COUNTRIES:
    b = teei_by_cc[cc][0].source_id
    print(f"  {fns['cnames'][cc]:<14} → {SOURCE_LABELS[b]:<22} "
          f"{cpl_best[cc]*100:.4f} ¢/litre")
print(f"\ncp ratio milk/water = {CP_MILK/CP_WATER:.6f}  "
      f"(milk is {(1-CP_MILK/CP_WATER)*100:.2f}% cheaper to heat per kg)")
print("\nCase Study 04 complete ✓")
