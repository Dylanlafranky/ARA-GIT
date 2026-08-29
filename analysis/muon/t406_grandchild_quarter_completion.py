#!/usr/bin/env python3
"""T406: test the proposed 0.5 + 0.25 grandchild completion."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", r"F:\SystemFormulaFolder\.matplotlib_cache")

PKG = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
if PKG.exists():
    sys.path.insert(0, str(PKG))

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T406_grandchild_quarter_completion"
PROTOCOL = ROOT / "T406_GRANDCHILD_QUARTER_COMPLETION_PROTOCOL_2026-08-18.md"
SOURCE = ROOT / "T405_parent_landmark_child_distortion" / "T405_SPLIT_PARTICIPATION.csv"
PRIMARY_SALT = 400
PARENT = 0.5
CAPACITY = 0.25
PURE = PARENT + CAPACITY


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows() -> list[dict]:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    clean = []
    for row in rows:
        if row["valid"].lower() != "true" or row["fit_success"].lower() != "true":
            continue
        clean.append(
            {
                "salt": int(row["salt"]),
                "prompt_participation": float(row["prompt_participation"]),
                "delayed_participation": float(row["delayed_participation"]),
                "observed_child_crest": float(row["population_local_mode"]),
                "left_time_us": float(row["left_time_us"]),
                "right_time_us": float(row["right_time_us"]),
            }
        )
    return clean


def monotone_loo(rows: list[dict]) -> list[dict]:
    q = np.asarray([r["prompt_participation"] for r in rows])
    x = np.asarray([r["observed_child_crest"] for r in rows])
    output = []
    for i in range(len(rows)):
        keep = np.arange(len(rows)) != i
        order = np.argsort(q[keep])
        qt = q[keep][order]
        xt = x[keep][order]
        qi = q[i]
        if qi < qt[0]:
            slope = (xt[1] - xt[0]) / (qt[1] - qt[0])
            pred = xt[0] + slope * (qi - qt[0])
            mode = "low extrapolation"
        elif qi > qt[-1]:
            slope = (xt[-1] - xt[-2]) / (qt[-1] - qt[-2])
            pred = xt[-1] + slope * (qi - qt[-1])
            mode = "high extrapolation"
        else:
            pred = np.interp(qi, qt, xt)
            mode = "interpolation"
        output.append(
            {
                "salt": rows[i]["salt"],
                "prompt_participation": float(qi),
                "observed_child_crest": float(x[i]),
                "loo_predicted_child_crest": float(pred),
                "absolute_error": float(abs(pred - x[i])),
                "prediction_mode": mode,
            }
        )
    return output


def make_figure(rows: list[dict], loo: list[dict], results: dict) -> None:
    q = np.asarray([r["prompt_participation"] for r in rows])
    x = np.asarray([r["observed_child_crest"] for r in rows])
    xg = 2.0 * (x - PARENT) / CAPACITY
    primary = next(r for r in rows if r["salt"] == PRIMARY_SALT)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    blue, gold, ink, pink = "#4c83c3", "#d79a2b", "#27313d", "#b05c96"

    ax = axes[0, 0]
    order = np.argsort(q)
    ax.plot(q[order], x[order], color=blue, lw=1.5, alpha=0.7)
    ax.scatter(q, x, s=48, color=blue, edgecolor="white", linewidth=0.8)
    ax.scatter(
        [primary["prompt_participation"]], [primary["observed_child_crest"]],
        s=110, color=gold, edgecolor=ink, linewidth=1.2, zorder=5, label="primary salt 400",
    )
    ax.axhline(PARENT, color=ink, ls="--", lw=1.2, label="parent reference 0.5")
    ax.axhline(PURE, color=gold, ls=":", lw=2, label="pure 0.75 endpoint")
    ax.fill_between([q.min(), q.max()], PURE - 0.1, PURE + 0.1, color=gold, alpha=0.08)
    ax.set(
        xlabel="prompt participation q",
        ylabel="observed child release crest (ARA)",
        title="Observed child crest changes with branch participation",
    )
    ax.legend(frameon=False, fontsize=9)

    ax = axes[0, 1]
    ax.axvspan(PARENT, PURE, color=gold, alpha=0.12, label="projected grandchild capacity 0.25")
    ax.axvline(PARENT, color=ink, ls="--", lw=1.5)
    ax.axvline(PURE, color=gold, ls=":", lw=2)
    y = np.linspace(0.12, 0.88, len(rows))
    ax.scatter(x, y, c=q, cmap="Blues", s=55, edgecolor="white", linewidth=0.7)
    ax.scatter([primary["observed_child_crest"]], [0.5], s=120, color=pink, edgecolor=ink, zorder=5)
    ax.annotate(
        f"primary 0.7063\ncompletion fraction {results['primary']['completion_fraction']:.3f}",
        (primary["observed_child_crest"], 0.5), xytext=(1.08, 0.64),
        arrowprops={"arrowstyle": "->", "color": ink}, fontsize=9,
    )
    ax.set(xlim=(0.4, 1.15), ylim=(0, 1), xlabel="parent-projected child ARA", ylabel="split index (jittered)", title="Pure landmark versus observed split crests")
    ax.set_yticks([])
    ax.legend(frameon=False, loc="lower right", fontsize=9)

    ax = axes[1, 0]
    ax.hist(xg, bins=np.linspace(0, 5, 16), color=blue, alpha=0.75, edgecolor="white")
    ax.axvline(2, color=gold, ls=":", lw=2, label="proposed completion x_G=2")
    ax.axvline(results["primary"]["grandchild_ara"], color=pink, ls="--", lw=2, label=f"primary x_G={results['primary']['grandchild_ara']:.3f}")
    ax.set(xlabel="decompressed grandchild ARA x_G", ylabel="valid deterministic splits", title="The raw grandchild coordinate is not fixed at 2")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[1, 1]
    obs = np.asarray([r["observed_child_crest"] for r in loo])
    pred = np.asarray([r["loo_predicted_child_crest"] for r in loo])
    lo, hi = min(obs.min(), pred.min()) - 0.03, max(obs.max(), pred.max()) + 0.03
    ax.plot([lo, hi], [lo, hi], color=ink, ls="--", lw=1.2, label="perfect prediction")
    ax.scatter(obs, pred, color=blue, s=55, edgecolor="white", linewidth=0.7)
    ax.set(xlim=(lo, hi), ylim=(lo, hi), xlabel="observed child crest", ylabel="leave-one-split-out prediction", title="Participation predicts the displaced position")
    ax.text(0.04, 0.94, f"median |error| = {results['loo_prediction']['median_absolute_error']:.4f}", transform=ax.transAxes, va="top", fontsize=10)
    ax.legend(frameon=False, fontsize=9)

    fig.suptitle("T406 — parent 0.5 + projected grandchild 0.25", fontsize=18, fontweight="bold")
    fig.savefig(OUT / "T406_GRANDCHILD_QUARTER_COMPLETION.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    if len(rows) != 20:
        raise RuntimeError(f"Expected 20 valid splits, got {len(rows)}")
    primary = next(r for r in rows if r["salt"] == PRIMARY_SALT)
    x = np.asarray([r["observed_child_crest"] for r in rows])
    q = np.asarray([r["prompt_participation"] for r in rows])
    loo = monotone_loo(rows)
    loo_errors = np.asarray([r["absolute_error"] for r in loo])
    rho, p = spearmanr(q, x)

    primary_fraction = (primary["observed_child_crest"] - PARENT) / CAPACITY
    raw_in_band = np.abs(x - PURE) <= 0.10
    gates = {
        "G1_primary_within_0p10_of_0p75": bool(abs(primary["observed_child_crest"] - PURE) <= 0.10),
        "G2_at_least_75pct_splits_within_0p10": bool(raw_in_band.mean() >= 0.75),
        "G3_positive_spearman": bool(rho > 0),
        "G4_loo_median_absolute_error_at_most_0p05": bool(np.median(loo_errors) <= 0.05),
    }
    if all(gates.values()):
        verdict = "FIXED QUARTER-COMPLETION SUPPORTED"
    elif gates["G1_primary_within_0p10_of_0p75"] and gates["G3_positive_spearman"] and gates["G4_loo_median_absolute_error_at_most_0p05"]:
        verdict = "PARTICIPATION-DISPLACED QUARTER-COMPATIBLE"
    else:
        verdict = "NOT SUPPORTED"

    results = {
        "test": "T406 grandchild quarter completion",
        "date": "2026-08-18",
        "protocol_sha256": sha256(PROTOCOL),
        "source_sha256": sha256(SOURCE),
        "verdict": verdict,
        "geometry": {"parent_reference": PARENT, "projected_grandchild_capacity": CAPACITY, "pure_endpoint": PURE},
        "primary": {
            "salt": PRIMARY_SALT,
            "observed_child_crest": primary["observed_child_crest"],
            "displacement_from_pure_endpoint": primary["observed_child_crest"] - PURE,
            "completion_fraction": primary_fraction,
            "grandchild_ara": 2.0 * primary_fraction,
        },
        "replication": {
            "valid_splits": len(rows),
            "raw_in_0p75_plusminus_0p10": int(raw_in_band.sum()),
            "raw_fraction_in_band": float(raw_in_band.mean()),
            "median_observed_child_crest": float(np.median(x)),
            "observed_range": [float(x.min()), float(x.max())],
        },
        "participation": {"spearman_rho": float(rho), "spearman_p": float(p)},
        "loo_prediction": {
            "median_absolute_error": float(np.median(loo_errors)),
            "mean_absolute_error": float(np.mean(loo_errors)),
            "maximum_absolute_error": float(np.max(loo_errors)),
        },
        "gates": gates,
        "boundaries": [
            "The 0.75 endpoint is a frozen geometric proposal, not fitted from these split crests.",
            "The participation relation is structurally mediated by the fitted equality boundary and is not independent physical confirmation.",
            "A participation-predictable displacement cannot by itself prove that the underlying carrier is a projected grandchild of weight 0.25.",
        ],
    }
    for row in rows:
        row["completion_fraction"] = (row["observed_child_crest"] - PARENT) / CAPACITY
        row["grandchild_ara"] = 2.0 * row["completion_fraction"]
        row["within_0p75_plusminus_0p10"] = abs(row["observed_child_crest"] - PURE) <= 0.10
    loo_by_salt = {r["salt"]: r for r in loo}
    merged = [{**r, **{k: v for k, v in loo_by_salt[r["salt"]].items() if k not in r}} for r in rows]
    with (OUT / "T406_SPLIT_RESULTS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(merged[0].keys()))
        writer.writeheader()
        writer.writerows(merged)
    (OUT / "T406_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(rows, loo, results)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
