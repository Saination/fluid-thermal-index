"""
utils/standard_figures.py
==========================
Shared template that generates the 7 standard figures for any TEEI case study.
Every case study calls this, then adds its own unique 8th figure.

Standard figure set (fig_offset + 1 … fig_offset + 7):
  +1  TEEI heatmap           (10 countries × 5 sources)
  +2  Preparation / heat-up time (minutes or hours)
  +3  Annual energy cost      (€/year, all sources × countries)
  +4  Annual CO₂              (kg/year)
  +5  Levelised total cost    (energy + maintenance + CAPEX/capex_years)
  +6  Break-even payback      (HP COP3 and HP COP5 vs electric)
  +7  Pareto scatter          (cost vs CO₂, country panels)

The unique 8th figure is written inside each individual case study script.
"""

from __future__ import annotations
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from teei import calculate, compare, get_country

# ── Shared style (applied once by the caller via plt.rcParams) ────────────────
STYLE = {
    "font.family":       "sans-serif",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
    "savefig.dpi":       300,
    "savefig.bbox":      "tight",
    "savefig.facecolor": "white",
}

# ── Fixed palette (same across every figure in every case study) ──────────────
SOURCE_COLORS = {
    "electric": "#2a78d6",
    "gas":      "#eb6834",
    "solar":    "#1baf7a",
    "hp3":      "#4a3aa7",
    "hp5":      "#eda100",
}
SOURCE_LABELS = {
    "electric": "Electric heater",
    "gas":      "Gas boiler",
    "solar":    "Solar thermal",
    "hp3":      "Heat pump COP 3",
    "hp5":      "Heat pump COP 5",
}
SOURCES = ["electric", "gas", "solar", "hp3", "hp5"]

# ── Standard 10-country set (fixed across ALL case studies) ───────────────────
STD_COUNTRIES = ["ES", "FR", "DE", "NO", "PL", "GB", "US", "IN", "AU", "BR"]

# ── Default CAPEX and maintenance (overridable per case study) ────────────────
DEFAULT_CAPEX = {
    "electric": 300,
    "gas":      800,
    "solar":    2500,
    "hp3":      1800,
    "hp5":      2400,
}
DEFAULT_MAINTENANCE = {
    "electric": 20,
    "gas":      80,
    "solar":    40,
    "hp3":      50,
    "hp5":      55,
}


def run(
    cfg: dict,
    fig_dir: str,
) -> list[str]:
    """
    Generate standard figures 1-7 for one case study.

    Parameters
    ----------
    cfg : dict with keys
        label          str   — e.g. "CS03 — Restaurant / Commercial Kitchen"
        cs_id          str   — e.g. "cs03"  (used in filenames)
        fluid          str   — fluid ID in TEEI database
        mass           float — kg per heating event
        T_start        float — starting temperature [°C]
        T_target       float — target temperature [°C]
        P_rated        float — rated input power [kW]
        solar_area     float — solar collector area [m²]
        solar_irr      float — solar irradiance [W/m²]
        days_per_year  int   — operating days per year
        fig_offset     int   — starting figure number (e.g. 1 for CS01, 9 for CS02)
        countries      list  — optional override; defaults to STD_COUNTRIES
        capex          dict  — optional override of DEFAULT_CAPEX
        maintenance    dict  — optional override of DEFAULT_MAINTENANCE
        capex_years    int   — amortisation period for CAPEX (default 15)
        time_unit      str   — 'min' or 'h' for fig+2 axis label
        cost_note      str   — optional note appended to fig+5 footnote

    fig_dir : str
        Directory where PNG files are saved.

    Returns
    -------
    list of str — paths to the 7 saved figures.
    """
    # ── Unpack config ──────────────────────────────────────────────────────────
    label        = cfg["label"]
    cs_id        = cfg["cs_id"]
    fluid        = cfg["fluid"]
    mass         = float(cfg["mass"])
    T_start      = float(cfg["T_start"])
    T_target     = float(cfg["T_target"])
    delta_T      = T_target - T_start
    P_rated      = float(cfg["P_rated"])
    solar_area   = float(cfg["solar_area"])
    solar_irr    = float(cfg.get("solar_irr", 650.0))
    days         = int(cfg["days_per_year"])
    fig_offset   = int(cfg["fig_offset"])
    countries    = cfg.get("countries", STD_COUNTRIES)
    capex        = {**DEFAULT_CAPEX,       **cfg.get("capex",       {})}
    maint        = {**DEFAULT_MAINTENANCE, **cfg.get("maintenance", {})}
    capex_yrs    = int(cfg.get("capex_years", 15))
    time_unit    = cfg.get("time_unit", "min")
    cost_note    = cfg.get("cost_note", "")
    weights      = (0.25, 0.25, 0.25, 0.25)

    cnames       = {c: get_country(c)["name"] for c in countries}
    n_countries  = len(countries)
    n_sources    = len(SOURCES)

    # ── Compute all raw metrics ────────────────────────────────────────────────
    raw = {}
    for cc in countries:
        raw[cc] = {}
        for src in SOURCES:
            raw[cc][src] = calculate(
                fluid, src, country=cc,
                mass=mass, delta_T=delta_T, T_start=T_start,
                P_rated=P_rated, solar_area=solar_area,
                solar_irradiance=solar_irr,
                check_phase=False,   # caller validates; avoids errors at 85%×T_boil
            )

    # ── TEEI comparison ────────────────────────────────────────────────────────
    teei_by_cc = {}
    for cc in countries:
        teei_by_cc[cc] = compare(
            fluid, SOURCES, country=cc,
            mass=mass, delta_T=delta_T, T_start=T_start,
            P_rated=P_rated, solar_area=solar_area,
            solar_irradiance=solar_irr,
            weights=weights, check_phase=False,
        )

    teei_matrix = np.zeros((n_countries, n_sources))
    for ci, cc in enumerate(countries):
        for r in teei_by_cc[cc]:
            si = SOURCES.index(r.source_id)
            teei_matrix[ci, si] = r.teei

    # ── Helper lambdas ─────────────────────────────────────────────────────────
    def ann_cost(cc, src):
        return raw[cc][src].cost_total / 100 * days           # €/yr

    def ann_co2(cc, src):
        return raw[cc][src].co2_total / 1000 * days           # kg/yr

    def ann_total(cc, src):
        return ann_cost(cc, src) + maint[src] + capex[src] / capex_yrs

    def heat_time(cc, src):
        t = raw[cc][src].t_total
        return t / 60 if time_unit == "min" else t / 3600

    def payback(cc, baseline="electric", upgrade="hp3"):
        extra  = capex[upgrade] - capex[baseline]
        saving = ann_cost(cc, baseline) - ann_cost(cc, upgrade)
        if extra <= 0: return 0.0
        if saving <= 0: return float("inf")
        return extra / saving

    # ── Shared bar chart setup ─────────────────────────────────────────────────
    x       = np.arange(n_countries)
    width   = 0.15
    offsets = np.linspace(-(n_sources-1)/2*width, (n_sources-1)/2*width, n_sources)

    saved = []

    # ── FIGURE +1: TEEI heatmap ───────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 5.5))
    im = ax.imshow(teei_matrix, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")
    for ci in range(n_countries):
        for si in range(n_sources):
            sc = teei_matrix[ci, si]
            col = "black" if 30 < sc < 80 else "white"
            ax.text(si, ci, f"{sc:.0f}", ha="center", va="center",
                    fontsize=10, fontweight="bold", color=col)
    ax.set_xticks(range(n_sources))
    ax.set_xticklabels([SOURCE_LABELS[s] for s in SOURCES], rotation=25, ha="right")
    ax.set_yticks(range(n_countries))
    ax.set_yticklabels([cnames[c] for c in countries])
    ax.set_title(f"TEEI Scores — {label}  (0 = worst, 100 = best within each country)")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02).set_label(
        "TEEI score", rotation=270, labelpad=14)
    plt.tight_layout()
    p = os.path.join(fig_dir, f"fig{fig_offset+1:02d}_{cs_id}_teei_heatmap.png")
    plt.savefig(p); plt.close(); saved.append(p)
    print(f"  Fig {fig_offset+1:02d} saved → {os.path.basename(p)}")

    # ── FIGURE +2: Heating / prep time ───────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5))
    for si, src in enumerate(SOURCES):
        times = [heat_time(cc, src) for cc in countries]
        ax.bar(x + offsets[si], times, width, color=SOURCE_COLORS[src],
               label=SOURCE_LABELS[src], alpha=0.88, edgecolor="white", lw=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([cnames[c] for c in countries], rotation=20, ha="right")
    ax.set_ylabel(f"Heating time ({time_unit})")
    ax.set_title(f"Heating time — {label}  |  P_rated = {P_rated} kW")
    ax.legend(fontsize=9, loc="upper right")
    ax.yaxis.grid(True, alpha=0.35, linestyle="--"); ax.set_axisbelow(True)
    plt.tight_layout()
    p = os.path.join(fig_dir, f"fig{fig_offset+2:02d}_{cs_id}_heat_time.png")
    plt.savefig(p); plt.close(); saved.append(p)
    print(f"  Fig {fig_offset+2:02d} saved → {os.path.basename(p)}")

    # ── FIGURE +3: Annual energy cost ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5))
    for si, src in enumerate(SOURCES):
        ax.bar(x + offsets[si], [ann_cost(cc, src) for cc in countries],
               width, color=SOURCE_COLORS[src], label=SOURCE_LABELS[src],
               alpha=0.88, edgecolor="white", lw=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([cnames[c] for c in countries], rotation=20, ha="right")
    ax.set_ylabel("Annual energy cost (€/year)")
    ax.set_title(f"Annual energy cost — {label}  ({days} operating days/year)")
    ax.legend(fontsize=9, loc="upper right")
    ax.yaxis.grid(True, alpha=0.35, linestyle="--"); ax.set_axisbelow(True)
    plt.tight_layout()
    p = os.path.join(fig_dir, f"fig{fig_offset+3:02d}_{cs_id}_annual_cost.png")
    plt.savefig(p); plt.close(); saved.append(p)
    print(f"  Fig {fig_offset+3:02d} saved → {os.path.basename(p)}")

    # ── FIGURE +4: Annual CO₂ ─────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5))
    for si, src in enumerate(SOURCES):
        ax.bar(x + offsets[si], [ann_co2(cc, src) for cc in countries],
               width, color=SOURCE_COLORS[src], label=SOURCE_LABELS[src],
               alpha=0.88, edgecolor="white", lw=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([cnames[c] for c in countries], rotation=20, ha="right")
    ax.set_ylabel("Annual CO₂ emissions (kg/year)")
    ax.set_title(f"Annual CO₂ — {label}")
    ax.legend(fontsize=9, loc="upper right")
    ax.yaxis.grid(True, alpha=0.35, linestyle="--"); ax.set_axisbelow(True)
    plt.tight_layout()
    p = os.path.join(fig_dir, f"fig{fig_offset+4:02d}_{cs_id}_annual_co2.png")
    plt.savefig(p); plt.close(); saved.append(p)
    print(f"  Fig {fig_offset+4:02d} saved → {os.path.basename(p)}")

    # ── FIGURE +5: Levelised total annual cost ────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for si, src in enumerate(SOURCES):
        ax.bar(x + offsets[si], [ann_total(cc, src) for cc in countries],
               width, color=SOURCE_COLORS[src], label=SOURCE_LABELS[src],
               alpha=0.88, edgecolor="white", lw=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([cnames[c] for c in countries], rotation=20, ha="right")
    ax.set_ylabel("Levelised annual cost (€/year)")
    ax.set_title(f"Levelised total cost — {label}\n"
                 f"Energy + maintenance + CAPEX/{capex_yrs} yr amortisation")
    ax.legend(fontsize=9, loc="upper right")
    ax.yaxis.grid(True, alpha=0.35, linestyle="--"); ax.set_axisbelow(True)
    capex_str = "  ·  ".join(
        f"{SOURCE_LABELS[s].split()[0]} €{capex[s]:,}" for s in SOURCES)
    note = f"CAPEX: {capex_str}"
    if cost_note:
        note += f"  |  {cost_note}"
    fig.text(0.01, -0.03, note, fontsize=8, color="gray")
    plt.tight_layout()
    p = os.path.join(fig_dir, f"fig{fig_offset+5:02d}_{cs_id}_levelised_cost.png")
    plt.savefig(p, bbox_inches="tight"); plt.close(); saved.append(p)
    print(f"  Fig {fig_offset+5:02d} saved → {os.path.basename(p)}")

    # ── FIGURE +6: Break-even payback ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 5))
    x2   = np.arange(n_countries)
    pb3  = [min(payback(cc, "electric", "hp3"), 30.0) for cc in countries]
    pb5  = [min(payback(cc, "electric", "hp5"), 30.0) for cc in countries]
    ax.bar(x2 - 0.2, pb3, 0.38, color="#4a3aa7", alpha=0.85,
           label=f"HP COP 3  (ΔCAPEX = €{capex['hp3']-capex['electric']:,})")
    ax.bar(x2 + 0.2, pb5, 0.38, color="#eda100", alpha=0.85,
           label=f"HP COP 5  (ΔCAPEX = €{capex['hp5']-capex['electric']:,})")
    for i, (y3, y5) in enumerate(zip(pb3, pb5)):
        if y3 < 30:
            ax.text(i - 0.2, y3 + 0.3, f"{y3:.1f}", ha="center",
                    fontsize=8, fontweight="bold", color="#4a3aa7")
        if y5 < 30:
            ax.text(i + 0.2, y5 + 0.3, f"{y5:.1f}", ha="center",
                    fontsize=8, fontweight="bold", color="#a07000")
    ax.axhline(10, color="gray", lw=1.2, linestyle="--", alpha=0.6,
               label="10-year reference")
    ax.set_xticks(x2)
    ax.set_xticklabels([cnames[c] for c in countries], rotation=20, ha="right")
    ax.set_ylabel("Simple payback period (years)")
    ax.set_ylim(0, 33)
    ax.set_title(f"HP upgrade payback — {label}  (vs electric baseline)")
    ax.legend(fontsize=9, loc="upper right")
    ax.yaxis.grid(True, alpha=0.3, linestyle="--"); ax.set_axisbelow(True)
    plt.tight_layout()
    p = os.path.join(fig_dir, f"fig{fig_offset+6:02d}_{cs_id}_payback.png")
    plt.savefig(p); plt.close(); saved.append(p)
    print(f"  Fig {fig_offset+6:02d} saved → {os.path.basename(p)}")

    # ── FIGURE +7: Pareto scatter (cost vs CO₂) for 4 representative countries
    fig, axes = plt.subplots(2, 5, figsize=(16, 7), sharex=False, sharey=False)
    axes = axes.flatten()
    handles = [mpatches.Patch(color=SOURCE_COLORS[s], label=SOURCE_LABELS[s])
               for s in SOURCES]
    for ci, cc in enumerate(countries):
        ax = axes[ci]
        for src in SOURCES:
            cost = ann_cost(cc, src)
            co2  = ann_co2(cc, src)
            ax.scatter(cost, co2, color=SOURCE_COLORS[src],
                       s=110, zorder=5, edgecolors="white", lw=0.8)
            ax.annotate(src, (cost, co2), textcoords="offset points",
                        xytext=(5, 3), fontsize=8, color=SOURCE_COLORS[src])
        ax.set_title(cnames[cc], fontsize=10, fontweight="bold")
        ax.set_xlabel("Cost (€/yr)", fontsize=8)
        ax.set_ylabel("CO₂ (kg/yr)", fontsize=8)
        ax.tick_params(labelsize=7.5)
        ax.grid(True, alpha=0.22, linestyle="--"); ax.set_axisbelow(True)
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=9,
               bbox_to_anchor=(0.5, -0.04), framealpha=0.9)
    fig.suptitle(f"Cost vs CO₂ — {label}  (ideal: bottom-left corner)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    p = os.path.join(fig_dir, f"fig{fig_offset+7:02d}_{cs_id}_pareto.png")
    plt.savefig(p, bbox_inches="tight"); plt.close(); saved.append(p)
    print(f"  Fig {fig_offset+7:02d} saved → {os.path.basename(p)}")

    return saved, raw, teei_by_cc, {
        "ann_cost": ann_cost, "ann_co2": ann_co2,
        "ann_total": ann_total, "heat_time": heat_time,
        "payback": payback, "cnames": cnames,
    }
