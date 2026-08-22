"""
Case Study 05 — Brewery Mash Heating (500 L wort)
==================================================
Standard figures: 33-39  |  Unique figure: 40
Countries: ES FR DE NO PL GB US IN AU BR  (standard 10)
Fluid: WORT (cp=3,950 J/kg·°C) — mash stage only (boil excluded)
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

CP_WORT = resolve_cp("wort"); CP_WATER = resolve_cp("water")
BREW_DAYS = 200

# CIP parameters (for unique figure)
CIP_MASS=300; CIP_TSTART=15; CIP_TEND=80; CIP_DT=65

CFG = {
    "label":        "CS05 — Brewery Mash Heating (500 L wort, 20°C→65°C)",
    "cs_id":        "cs05",
    "fluid":        "wort",
    "mass":         500,
    "T_start":      20.0,
    "T_target":     65.0,
    "P_rated":      15.0,
    "solar_area":   10.0,
    "solar_irr":    650.0,
    "days_per_year":BREW_DAYS,
    "fig_offset":   32,
    "countries":    STD_COUNTRIES,
    "time_unit":    "min",
    "capex":        {"electric":500,"gas":2500,"solar":5000,"hp3":4000,"hp5":5500},
    "maintenance":  {"electric":50,"gas":250,"solar":120,"hp3":180,"hp5":200},
    "capex_years":  10,
    "cost_note":    "Craft brewery, mash tun, 10-year lifespan",
}

print("=" * 60); print("Case Study 05 — Brewery (Mash Stage)"); print("=" * 60)
print(f"  NOTE: Boiling stage excluded — single-phase scope (T_target=65°C < T_boil)")
saved, raw, teei_by_cc, fns = run(CFG, FIG_DIR)

# ── Fig 40: Two-stage stacked (mash + CIP) for all countries ─────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
x = np.arange(len(STD_COUNTRIES)); n=len(SOURCES); w=0.15
offsets = np.linspace(-(n-1)/2*w,(n-1)/2*w,n)

raw_cip = {}
for cc in STD_COUNTRIES:
    raw_cip[cc] = {}
    for src in SOURCES:
        raw_cip[cc][src] = calculate("water", src, country=cc,
            mass=CIP_MASS, delta_T=CIP_DT, T_start=CIP_TSTART,
            P_rated=15.0, solar_area=10.0, solar_irradiance=650.0,
            check_phase=False)

for ax_idx, (metric, ylabel, title_suffix) in enumerate([
        ("cost","€/brew day","Cost per brew day"),
        ("time","minutes","Heating time per brew day")]):
    ax = axes[ax_idx]
    for si, src in enumerate(SOURCES):
        if metric == "cost":
            mash_v = [raw[cc][src].cost_total/100 for cc in STD_COUNTRIES]
            cip_v  = [raw_cip[cc][src].cost_total/100 for cc in STD_COUNTRIES]
        else:
            mash_v = [raw[cc][src].t_total/60 for cc in STD_COUNTRIES]
            cip_v  = [raw_cip[cc][src].t_total/60 for cc in STD_COUNTRIES]
        ax.bar(x+offsets[si], mash_v, w, color=SOURCE_COLORS[src],
               alpha=0.88, edgecolor="white", lw=0.5,
               label=SOURCE_LABELS[src] if ax_idx==0 else "")
        ax.bar(x+offsets[si], cip_v,  w, bottom=mash_v,
               color=SOURCE_COLORS[src], alpha=0.45, edgecolor="white", lw=0.5,
               hatch="///")
    ax.set_xticks(x)
    ax.set_xticklabels([fns["cnames"][c] for c in STD_COUNTRIES], rotation=20, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{title_suffix}\n(solid = mash wort, hatched = CIP water)")
    ax.yaxis.grid(True, alpha=0.3, ls="--"); ax.set_axisbelow(True)

axes[0].legend(fontsize=8, loc="upper right")
from matplotlib.patches import Patch
axes[1].legend(handles=[
    Patch(facecolor="gray", alpha=0.88, label=f"Mash: 500L wort, 20→65°C"),
    Patch(facecolor="gray", alpha=0.45, hatch="///", label=f"CIP:  300L water, 15→80°C"),
], fontsize=8, loc="upper right")
fig.suptitle("CS05 — Brewery two-stage heating: mash + CIP (all 10 countries)",
             fontsize=12, fontweight="bold")
plt.tight_layout(); p = os.path.join(FIG_DIR,"fig40_cs05_two_stage.png")
plt.savefig(p, bbox_inches="tight"); plt.close(); print(f"  Fig 40 saved → {os.path.basename(p)}")

print(f"\ncp ratio wort/water = {CP_WORT/CP_WATER:.6f}  "
      f"(wort is {(1-CP_WORT/CP_WATER)*100:.2f}% cheaper to heat per kg than water)")
print("\nCase Study 05 complete ✓")
