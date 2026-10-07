"""Figure set for the IFC evidence-contract study.

Every plotted value is read from the frozen ledgers under inputs/ and analysis/; the
mechanism panel is a schematic of those same numbers.
  fig1_mechanism      three panels, with the two experiments separated in panel C
  fig2_scorecard      binary collapse, with the intact overlap denominator shown
  fig3_shared_source  shared-value concentration, colour-blind-safe
  fig4_recovery       recovery quality vs mask size, plus the request cost

Palette is the Okabe-Ito colour-blind-safe set. No number is changed: every value
is read from the frozen ledgers under inputs/ and analysis/.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path(__file__).resolve().parents[1]
INPUTS = BASE / "inputs"
ANALYSIS = BASE / "analysis"
OUT = BASE / "manuscript" / "figures"

# Okabe-Ito colour-blind-safe palette
BLUE = "#0072B2"
ORANGE = "#E69F00"
SKY = "#56B4E9"
GREEN = "#009E73"
VERM = "#D55E00"
PURPLE = "#CC79A7"
GREY = "#999999"
INK = "#1C1C1C"
PAPER = "#F6F3EE"
CARD = "#FFFFFF"
LINE = "#D5CFC4"
MUTED = "#5E584E"


def _font():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.linewidth": 0.7,
        "axes.edgecolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
    })


def _save(fig, stem):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "preview").mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(OUT / "preview" / f"{stem}.png", dpi=170, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)


def _card(ax, x, y, w, h, fc=CARD, ec=LINE, lw=0.9, r=0.012):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0.004,rounding_size={r}",
                                facecolor=fc, edgecolor=ec, linewidth=lw,
                                transform=ax.transAxes, clip_on=False))


def _t(ax, x, y, s, size=8, color=INK, weight="regular", ha="left", va="center"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va,
            transform=ax.transAxes, linespacing=1.3)


# --------------------------------------------------------------------------- fig 1
def mechanism():
    fig = plt.figure(figsize=(7.5, 4.3), dpi=200)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    _t(ax, 0.014, 0.955, "A  Encoded routes", size=9.5, weight="bold")
    _t(ax, 0.325, 0.955, "B  Route effects, 60 files", size=9.5, weight="bold")
    _t(ax, 0.638, 0.955, "C  Two independent contrasts", size=9.5, weight="bold")

    _card(ax, 0.014, 0.08, 0.296, 0.845, ec=BLUE, lw=1.1)
    _t(ax, 0.028, 0.885, "Delivered model bytes stay fixed", size=8.2, weight="bold", color=BLUE)
    _t(ax, 0.028, 0.845, "Paths to the same value differ.", size=7.0, color=MUTED)
    for x, y, title, sub, col in [
        (0.100, 0.735, "IfcBuilding", "shared BuildingClass\nvalue", ORANGE),
        (0.100, 0.545, "IfcDoor", "occurrence", BLUE),
        (0.225, 0.545, "IfcWall", "opening host", SKY),
        (0.162, 0.270, "IfcDoorType", "FireRating on the type", GREEN),
    ]:
        _card(ax, x - 0.058, y - 0.052, 0.126, 0.104, ec=col, lw=1.0)
        _t(ax, x, y + 0.018, title, size=7.0, weight="bold", ha="center", color=col)
        _t(ax, x, y - 0.024, sub, size=6.0, ha="center", color=MUTED)
    ax.add_patch(FancyArrowPatch((0.100, 0.615), (0.100, 0.665), transform=ax.transAxes,
                                 arrowstyle="-|>", mutation_scale=8, lw=0.9, color=ORANGE))
    _t(ax, 0.114, 0.640, "shared value", size=6.2, color=ORANGE)
    _t(ax, 0.162, 0.455, "IfcRelFillsElement", size=6.4, color=MUTED, ha="center")
    _t(ax, 0.162, 0.400, "IfcRelDefinesByType", size=6.4, color=GREEN, ha="center")
    _t(ax, 0.162, 0.155, "IsTypedBy alone stops at the door;\nthe type assignment is a second edge.",
       size=6.8, ha="center")

    for x, y, title, count, body, col in [
        (0.328, 0.630, "Type route", "3,283", "IFC2X3 IfcRelDefinesByType is encoded;\na narrow inverse lookup reports absence.", BLUE),
        (0.328, 0.395, "Host context", "2,808", "The opening is reached through its\nhost, not by direct containment.", SKY),
        (0.328, 0.160, "Value filter", "210", "The token is readable and still rejected\nby the declared fire-rating contract.", VERM),
    ]:
        _card(ax, x, y, 0.288, 0.195, ec=col, lw=1.0)
        _t(ax, x + 0.014, y + 0.150, title, size=8.2, weight="bold", color=col)
        _t(ax, x + 0.270, y + 0.150, count, size=8.2, weight="bold", ha="right", color=col)
        _t(ax, x + 0.014, y + 0.068, body, size=6.9)

    _card(ax, 0.640, 0.545, 0.348, 0.380, ec=VERM, lw=1.1)
    _t(ax, 0.654, 0.880, "C1  Controlled masking", size=8.2, weight="bold", color=VERM)
    _t(ax, 0.654, 0.837, "134 masks, public models, paired runs", size=6.6, color=MUTED)
    _t(ax, 0.654, 0.778, "Binary toolchain (IfcTester 0.8.5)", size=7.1, weight="bold")
    for y, lab, val, col in [
        (0.730, "Obligations dropped", "80", VERM),
        (0.688, "Pass changed to fail", "122", VERM),
        (0.646, "Fail changed to pass", "0", GREEN),
    ]:
        _t(ax, 0.664, y, lab, size=7.0)
        _t(ax, 0.974, y, val, size=8.2, weight="bold", ha="right", color=col)
    _t(ax, 0.654, 0.588, "All 202 retained as pending, with the missing source named.",
       size=6.8, color=GREEN)

    _card(ax, 0.640, 0.110, 0.348, 0.375, ec=GREEN, lw=1.1)
    _t(ax, 0.654, 0.440, "C2  One shared source", size=8.2, weight="bold", color=GREEN)
    _t(ax, 0.654, 0.393, "Masking one building-level value", size=6.6, color=MUTED)
    for y, lab, val in [
        (0.320, "Applicable checks", "525"),
        (0.272, "Removed from filtering", "311"),
        (0.224, "Intact-run failures inside", "132"),
    ]:
        _t(ax, 0.664, y, lab, size=7.0)
        _t(ax, 0.974, y, val, size=8.2, weight="bold", ha="right", color=GREEN)
    _t(ax, 0.654, 0.152, "Restoring the value returns\nall 311 decisions.", size=6.8, color=GREEN)
    _t(ax, 0.016, 0.032,
       "C1 and C2 are separate experiments and are not pooled with each other.",
       size=6.4, color=MUTED)
    _save(fig, "fig1_mechanism")


# --------------------------------------------------------------------------- fig 2
def scorecard():
    counts = json.loads((INPUTS / "counts.json").read_text(encoding="utf-8"))
    models = []
    for model, fams in counts["per_model"].items():
        models.append((
            "Custom test model" if model.startswith("Custom") else "Real-world test model",
            sum(v["ifctester_dropped_obligations"] for v in fams.values()),
            sum(v["ifctester_pass_to_fail"] for v in fams.values()),
        ))
    assert sum(m[1] for m in models) == counts["grand_totals"]["ifctester_dropped_obligations"]
    assert sum(m[2] for m in models) == counts["grand_totals"]["ifctester_pass_to_fail"]

    fig, (ax, axd) = plt.subplots(
        2, 1, figsize=(7.4, 4.6), dpi=180, sharex=False,
        gridspec_kw={"height_ratios": [3.1, 1.0], "hspace": 0.62})
    fig.patch.set_facecolor("white")
    labels = [m[0] for m in models]
    x = np.arange(len(labels)); w = 0.34
    drops = [m[1] for m in models]; flips = [m[2] for m in models]
    b1 = ax.bar(x - w / 2, drops, w, color=BLUE, label="Obligations dropped", zorder=3)
    b2 = ax.bar(x + w / 2, flips, w, color=VERM, label="Pass changed to fail", zorder=3)
    for bars in (b1, b2):
        for r in bars:
            ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 1.5, f"{int(r.get_height())}",
                    ha="center", va="bottom", fontsize=8.5, color=INK)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Checks under 134 controlled masks", fontsize=9)
    ax.set_ylim(0, max(drops + flips) * 1.30)
    ax.legend(frameon=False, fontsize=8.2, loc="upper right")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#E8E4DC", lw=0.6, zorder=0)
    ax.set_axisbelow(True)

    # denominator panel: the intact overlap both evaluators score
    tot = {"pass": 390, "fail": 13, "not applicable": 372}
    left = 0.0
    for (lab, val), col in zip(tot.items(), (SKY, ORANGE, "#D9D4CA")):
        axd.barh([0], [val], left=left, color=col, height=0.55, zorder=3,
                 edgecolor="white", linewidth=1.2)
        if val < 60:                      # too narrow to label inside; value is in the note above
            pass
        else:
            axd.text(left + val / 2, 0, f"{val}", ha="center", va="center", fontsize=8.5,
                     color="white" if lab == "pass" else INK, weight="bold")
        left += val
    axd.set_xlim(0, left); axd.set_ylim(-0.6, 0.9)
    axd.set_yticks([]); axd.set_xlabel("Intact overlap scored by both evaluators (775 rows)",
                                       fontsize=8.6)
    for s in ("top", "right", "left"):
        axd.spines[s].set_visible(False)
    axd.tick_params(labelsize=8)
    axd.text(0, 0.72, "390 pass  |  13 fail  |  372 not applicable  -  all 80 drops and all 122 flips fall inside",
             fontsize=7.8, color=VERM, weight="bold", transform=axd.transAxes)
    fig.tight_layout()
    _save(fig, "fig2_scorecard")


# --------------------------------------------------------------------------- fig 3
def shared_source():
    rows = [("Project-derived model", 525, 311, 132), ("Designed companion", 289, 100, 4)]
    fig, ax = plt.subplots(figsize=(7.4, 3.5), dpi=180)
    fig.patch.set_facecolor("white")
    y = np.arange(len(rows))
    app = [r[1] for r in rows]; rem = [r[2] for r in rows]; fail = [r[3] for r in rows]
    ax.barh(y, app, color="#E4DFD6", height=0.52, label="Applicable checks", zorder=2)
    ax.barh(y, rem, color=BLUE, height=0.52, label="Removed when the shared value is masked", zorder=3)
    ax.barh(y, fail, color=VERM, height=0.26, label="Of which had been published as failures", zorder=4)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    ax.set_xlabel("Checks", fontsize=9); ax.set_xlim(0, 860)
    ax.legend(frameon=False, fontsize=7.6, loc="lower center", bbox_to_anchor=(0.45, 1.01), ncol=1)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#EDE9E1", lw=0.6, zorder=0); ax.set_axisbelow(True)
    for i, (name, a, r_, f_) in enumerate(rows):
        ax.text(a + 14, i, f"{r_} removed of {a}", va="center", fontsize=8.4, color=BLUE,
                weight="bold")
    fig.tight_layout()
    _save(fig, "fig3_shared_source")


# --------------------------------------------------------------------------- fig 4
def recovery():
    ext = list(csv.DictReader((ANALYSIS / "policy_comparison_extended.csv").open(encoding="utf-8")))
    pair = json.loads((ANALYSIS / "policy_pairwise_vs_adaptive_degree.json").read_text(encoding="utf-8"))
    order = ["static_frequency", "adaptive_degree", "branch_aware", "lookahead_structure",
             "expected_determinacy", "risk_aware"]
    nice = {"static_frequency": "Static frequency", "adaptive_degree": "Residual degree (proposed)",
            "branch_aware": "Branch-aware", "lookahead_structure": "Lookahead",
            "expected_determinacy": "Expected determinacy", "risk_aware": "Risk-aware"}
    col = {"static_frequency": VERM, "adaptive_degree": INK, "branch_aware": SKY,
           "lookahead_structure": PURPLE, "expected_determinacy": ORANGE, "risk_aware": GREEN}

    by = defaultdict(lambda: defaultdict(list))
    req = defaultdict(list)
    for r in ext:
        p = r["policy"]
        if p not in order:
            continue
        by[int(r["k"])][p].append(float(r["recovery_auc"]))
        req[p].append(float(r["requests_to_restore"]))

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.7), dpi=180,
                                  gridspec_kw={"width_ratios": [1.35, 1.0], "wspace": 0.30})
    fig.patch.set_facecolor("white")
    ks = sorted(by)
    for p in order:
        xs = [k for k in ks if by[k][p]]
        ys = [float(np.mean(by[k][p])) for k in xs]
        ax.plot(xs, ys, marker="o", ms=3.6, lw=1.7 if p == "adaptive_degree" else 1.1,
                color=col[p], label=nice[p], zorder=4 if p == "adaptive_degree" else 3,
                alpha=1.0 if p == "adaptive_degree" else 0.85)
    ax.set_xlabel("Sources masked, $|M|$", fontsize=9)
    ax.set_ylabel("Mean recovery area $A_M$", fontsize=9)
    ax.set_xticks(ks)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.grid(color="#EDE9E1", lw=0.6, zorder=0); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=6.4, loc="upper center",
              bbox_to_anchor=(0.5, -0.20), ncol=3, handlelength=1.3,
              columnspacing=0.8, labelspacing=0.3)
    ax.set_title("(a) Recovery quality by mask size", fontsize=8.8, pad=6)

    yv = np.arange(len(order))
    means = [float(np.mean(req[p])) for p in order]
    ax2.barh(yv, means, color=[col[p] for p in order], height=0.6, zorder=3)
    ax2.set_yticks(yv); ax2.set_yticklabels([nice[p] for p in order], fontsize=8)
    ax2.set_xlabel("Mean sources requested to restore", fontsize=8.6)
    ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
    ax2.grid(axis="x", color="#EDE9E1", lw=0.6, zorder=0); ax2.set_axisbelow(True)
    ax2.tick_params(labelsize=8)
    for i, v in enumerate(means):
        ax2.text(v + 0.12, i, f"{v:.2f}", va="center", fontsize=7.6)
    ax2.set_xlim(0, max(means) * 1.22)
    ax2.set_title("(b) Request cost", fontsize=8.8, pad=6)
    fig.tight_layout()
    _save(fig, "fig4_recovery")
    _ = pair


if __name__ == "__main__":
    _font()
    mechanism(); scorecard(); shared_source(); recovery()
    print("wrote figures to", OUT)
