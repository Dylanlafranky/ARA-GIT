"""T454: direct contextual TE-ARA remaining-path forecasts."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T454_contextual_te_ara_remaining_path")
SOURCE = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T453_prospective_lifespan_4d_geometry\results\T453_PREFIX_STATES.csv")
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(454)
N_BOOT = 2000
SCALE_INTERVALS = 11.0
SCALE_HOURS = 31.6666666666667

LABELS = {
    "pure": "Pure 2 − A",
    "relational": "Relational 2 − (A + R)",
    "fixed_025": "Relational + fixed 0.25 child",
    "size_child": "Relational + measured size child/4",
    "rpl_child": "Relational + measured Rpl child/4",
    "reverse_control": "Reverse-sign relation control",
}
COLORS = {
    "pure": "#777777", "relational": "#3979c7", "fixed_025": "#a05fc7",
    "size_child": "#d57a22", "rpl_child": "#2f8f8b", "reverse_control": "#c24e4e",
}


def clip2(x):
    return np.clip(np.asarray(x, float), 0.0, 2.0)


def build_forecasts():
    p = pd.read_csv(SOURCE)
    p = p[p.split.isin(["holdout", "external"])].copy()
    p["target_generation_unbounded"] = 2.0 * p.remaining_divisions / SCALE_INTERVALS
    p["target_clock_unbounded"] = 2.0 * p.remaining_hours / SCALE_HOURS
    p["target_generation_bounded"] = clip2(p.target_generation_unbounded)
    p["target_clock_bounded"] = clip2(p.target_clock_unbounded)

    a = p.x_generation.to_numpy(float)
    r = p.ara_phase_gap.to_numpy(float)
    relational_base = a + r
    p["pred_pure"] = clip2(2.0 - a)
    p["pred_relational"] = clip2(2.0 - relational_base)
    p["pred_fixed_025"] = clip2(2.0 - (relational_base + 0.25))
    p["pred_size_child"] = clip2(2.0 - (relational_base + p.x_size.to_numpy(float) / 4.0))
    p["pred_rpl_child"] = clip2(2.0 - (relational_base + p.x_rpl.to_numpy(float) / 4.0))
    p["pred_reverse_control"] = clip2(2.0 - (a - r))
    return p


def score(forecasts):
    rows = []
    ledger = []
    models = ["pure", "relational", "fixed_025", "size_child", "rpl_child", "reverse_control"]
    for split in ["holdout", "external"]:
        for target_kind in ["generation", "clock"]:
            for bounded in [True, False]:
                target = f"target_{target_kind}_{'bounded' if bounded else 'unbounded'}"
                for model in models:
                    pred_col = f"pred_{model}"
                    sub = forecasts[forecasts.split == split].dropna(subset=[target, pred_col]).copy()
                    if len(sub) == 0:
                        continue
                    err = sub[pred_col] - sub[target]
                    cell_mae = pd.DataFrame({"cell": sub.cell_key, "ae": np.abs(err)}).groupby("cell").ae.mean()
                    rows.append({
                        "split": split, "target": target_kind, "bounded_target": bounded,
                        "model": model, "rows": len(sub), "cells": sub.cell_key.nunique(),
                        "cell_mean_mae": float(cell_mae.mean()), "cell_median_mae": float(cell_mae.median()),
                        "overall_mae": float(np.mean(np.abs(err))), "rmse": float(np.sqrt(np.mean(err**2))),
                        "bias": float(np.mean(err)),
                    })
                    for idx, row in sub.iterrows():
                        ledger.append({
                            "split": split, "target": target_kind, "bounded_target": bounded,
                            "model": model, "row_id": idx, "cell_key": row.cell_key,
                            "prefix_g1_count": row.prefix_g1_count,
                            "actual": row[target], "prediction": row[pred_col],
                        })
    return pd.DataFrame(rows), pd.DataFrame(ledger)


def bootstrap(ledger):
    comparisons = [
        ("pure", "relational"), ("relational", "fixed_025"),
        ("relational", "size_child"), ("relational", "rpl_child"),
        ("relational", "reverse_control"),
    ]
    rows = []
    for split in ["holdout", "external"]:
        for target in ["generation", "clock"]:
            for bounded in [True, False]:
                sub = ledger[(ledger.split == split) & (ledger.target == target) & (ledger.bounded_target == bounded)]
                for baseline, candidate in comparisons:
                    wide = sub[sub.model.isin([baseline, candidate])].pivot_table(index=["cell_key", "row_id"], columns="model", values=["actual", "prediction"])
                    if ("prediction", baseline) not in wide or ("prediction", candidate) not in wide:
                        continue
                    actual = wide[("actual", baseline)]
                    gain = np.abs(wide[("prediction", baseline)] - actual) - np.abs(wide[("prediction", candidate)] - actual)
                    per_cell = pd.DataFrame({"cell": [i[0] for i in wide.index], "gain": gain.to_numpy(float)}).groupby("cell").gain.mean().to_numpy(float)
                    boots = np.array([np.mean(RNG.choice(per_cell, len(per_cell), replace=True)) for _ in range(N_BOOT)])
                    rows.append({
                        "split": split, "target": target, "bounded_target": bounded,
                        "baseline": baseline, "candidate": candidate, "cells": len(per_cell),
                        "mean_mae_gain": float(np.mean(per_cell)), "ci_low": float(np.quantile(boots, .025)),
                        "ci_high": float(np.quantile(boots, .975)), "p_gain_positive": float(np.mean(boots > 0)),
                    })
    return pd.DataFrame(rows)


def get_metric(metrics, split, target, model, field="cell_mean_mae", bounded=True):
    row = metrics[(metrics.split == split) & (metrics.target == target) & (metrics.model == model) & (metrics.bounded_target == bounded)]
    return float(row.iloc[0][field]) if len(row) else np.nan


def improvement(metrics, split, target, baseline, candidate, bounded=True):
    b = get_metric(metrics, split, target, baseline, bounded=bounded)
    c = get_metric(metrics, split, target, candidate, bounded=bounded)
    return 100.0 * (b - c) / b if np.isfinite(b) and b else np.nan


def gates(metrics):
    h_rel = improvement(metrics, "holdout", "generation", "pure", "relational")
    child_imps = {m: improvement(metrics, "holdout", "generation", "relational", m) for m in ["fixed_025", "size_child", "rpl_child"]}
    winner = max(child_imps, key=lambda k: child_imps[k] if np.isfinite(child_imps[k]) else -np.inf)
    h_child = child_imps[winner]
    h_clock = improvement(metrics, "holdout", "clock", "pure", winner)
    e_rel = improvement(metrics, "external", "generation", "pure", "relational")
    e_size = improvement(metrics, "external", "generation", "relational", "size_child")
    reverse_h = get_metric(metrics, "holdout", "generation", "reverse_control") > get_metric(metrics, "holdout", "generation", "relational")
    reverse_e = get_metric(metrics, "external", "generation", "reverse_control") > get_metric(metrics, "external", "generation", "relational")
    rows = [
        ("G1", "Relational improves holdout remaining-generation MAE by ≥5% vs pure", h_rel, 5.0, h_rel >= 5),
        ("G2", f"Best frozen child ({winner}) improves holdout by ≥5% vs relational", h_child, 5.0, h_child >= 5),
        ("G3", f"Winning child ({winner}) improves holdout remaining-clock MAE by ≥5% vs pure", h_clock, 5.0, h_clock >= 5),
        ("G4", "Relational improves external remaining-generation MAE by ≥5% vs pure", e_rel, 5.0, e_rel >= 5),
        ("G5", "Size-child correction improves external MAE by ≥2% vs relational", e_size, 2.0, e_size >= 2),
        ("G6", "Reverse relation is worse than correct relation on both holdouts", float(reverse_h and reverse_e), 1.0, reverse_h and reverse_e),
    ]
    return pd.DataFrame(rows, columns=["gate", "statement", "observed", "threshold", "passed"]), winner, child_imps


def style(ax):
    ax.grid(alpha=.18); ax.spines[["top", "right"]].set_visible(False)


def plot_scores(metrics, gate_table):
    models = ["pure", "relational", "fixed_025", "size_child", "rpl_child", "reverse_control"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), constrained_layout=True)
    fig.suptitle("T454 — direct contextual TE-ARA forecasts; no fitted intercept can hide the 0.25", fontsize=17, fontweight="bold")
    for ax, split in zip(axes[:2], ["holdout", "external"]):
        sub = metrics[(metrics.split == split) & (metrics.target == "generation") & metrics.bounded_target].set_index("model")
        order = [m for m in models if m in sub.index]
        vals = [sub.loc[m, "cell_mean_mae"] for m in order]
        bars = ax.barh([LABELS[m] for m in order], vals, color=[COLORS[m] for m in order])
        for bar, v in zip(bars, vals): ax.text(v, bar.get_y()+bar.get_height()/2, f" {v:.3f}", va="center")
        ax.invert_yaxis(); ax.set(title=f"{split.title()} — remaining-generation share", xlabel="mean per-cell MAE on 0–2 share (lower is better)")
        style(ax)
    axes[2].axis("off"); axes[2].set_title("Frozen gates")
    for i, (_, row) in enumerate(gate_table.iterrows()):
        y = .92 - i*.15; color = "#2d8b57" if row.passed else "#c04b4b"
        axes[2].scatter(.05, y, s=130, color=color, transform=axes[2].transAxes)
        axes[2].text(.11, y, f"{row.gate} {'PASS' if row.passed else 'FAIL'} — {row.observed:.3g}", transform=axes[2].transAxes, va="center")
    fig.savefig(RESULTS / "T454_01_DIRECT_SCORECARD.png", dpi=180, facecolor="white"); plt.close(fig)


def plot_paths(forecasts):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), constrained_layout=True)
    fig.suptitle("What each TE-ARA allocation does to the unseen remaining path", fontsize=17, fontweight="bold")
    for ax, split in zip(axes, ["holdout", "external"]):
        sub = forecasts[forecasts.split == split].copy()
        sub["bin"] = pd.cut(sub.x_generation, np.linspace(0, 2, 11), include_lowest=True)
        truth = sub.groupby("bin", observed=True).agg(x=("x_generation", "mean"), y=("target_generation_bounded", "mean"))
        ax.plot(truth.x, truth.y, color="#111111", lw=3, marker="o", label="actual unseen remainder")
        for model in ["pure", "relational", "fixed_025", "size_child"] + (["rpl_child"] if split == "holdout" else []):
            curve = sub.groupby("bin", observed=True).agg(x=("x_generation", "mean"), y=(f"pred_{model}", "mean"))
            ax.plot(curve.x, curve.y, lw=2, marker="o", color=COLORS[model], label=LABELS[model])
        ax.axvline(1, color="#777", ls=":"); ax.axhline(1, color="#777", ls=":")
        ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.set(title=split.title(), xlabel="visible generation path A (0–2)", ylabel="unseen remaining-generation share (0–2)")
        ax.legend(frameon=False, fontsize=8); style(ax)
    fig.savefig(RESULTS / "T454_02_REMAINING_PATHS.png", dpi=180, facecolor="white"); plt.close(fig)


def plot_relation_and_child(forecasts):
    hold = forecasts[forecasts.split == "holdout"].copy()
    hold["pure_error"] = np.abs(hold.pred_pure - hold.target_generation_bounded)
    hold["rel_gain"] = hold.pure_error - np.abs(hold.pred_relational - hold.target_generation_bounded)
    hold["child_gain"] = np.abs(hold.pred_relational - hold.target_generation_bounded) - np.abs(hold.pred_size_child - hold.target_generation_bounded)
    fig, axes = plt.subplots(1, 3, figsize=(17, 5), constrained_layout=True)
    fig.suptitle("Where the relational and child terms help—or spend too much of the ledger", fontsize=17, fontweight="bold")
    sc = axes[0].scatter(hold.x_generation, hold.ara_phase_gap, c=hold.rel_gain, cmap="coolwarm", vmin=-.5, vmax=.5, s=42, alpha=.8)
    axes[0].axhline(0, color="#333", ls="--"); axes[0].axvline(1, color="#777", ls=":")
    axes[0].set(title="Relational correction", xlabel="generation A", ylabel="R_AB = clock − generation")
    cb=fig.colorbar(sc, ax=axes[0]); cb.set_label("MAE gain vs pure (positive helps)")
    sc2=axes[1].scatter(hold.x_size/4, hold.ara_phase_gap, c=hold.child_gain, cmap="coolwarm", vmin=-.5, vmax=.5, s=42, alpha=.8)
    axes[1].axvline(.25, color="#777", ls=":", label="child ridge → 0.25")
    axes[1].axhline(0, color="#333", ls="--"); axes[1].set(title="Measured size-child correction", xlabel="parent-facing size child x_size/4", ylabel="R_AB")
    axes[1].legend(frameon=False); cb2=fig.colorbar(sc2, ax=axes[1]); cb2.set_label("MAE gain vs relational")
    axes[2].hist(hold.x_size/4, bins=12, alpha=.7, color=COLORS["size_child"], label="size child/4")
    axes[2].hist(hold.x_rpl/4, bins=12, alpha=.65, color=COLORS["rpl_child"], label="Rpl child/4")
    axes[2].axvline(.25, color="#333", ls="--", label="fixed 0.25")
    axes[2].set(title="Were the children actually near 0.25?", xlabel="parent-facing child allocation", ylabel="prefix count")
    axes[2].legend(frameon=False)
    for ax in axes: style(ax)
    fig.savefig(RESULTS / "T454_03_RELATION_AND_CHILD_GEOMETRY.png", dpi=180, facecolor="white"); plt.close(fig)


def plot_individuals(forecasts):
    keys = forecasts[forecasts.split == "holdout"].groupby("cell_key").size().sort_values(ascending=False).head(4).index
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    fig.suptitle("Individual untouched cells — direct forecasts through each visible prefix", fontsize=17, fontweight="bold")
    for ax, key in zip(axes.ravel(), keys):
        sub = forecasts[forecasts.cell_key == key].sort_values("prefix_g1_count")
        ax.plot(sub.prefix_g1_count, sub.target_generation_bounded, color="#111", lw=3, marker="o", label="actual unseen remainder")
        for model in ["pure", "relational", "fixed_025", "size_child", "rpl_child"]:
            ax.plot(sub.prefix_g1_count, sub[f"pred_{model}"], lw=1.8, marker="o", ms=3, color=COLORS[model], label=LABELS[model])
        ax.set(title=key.replace("|", " / "), xlabel="G1 observations visible", ylabel="remaining-generation share (0–2)")
        style(ax)
    h,l=axes[0,0].get_legend_handles_labels(); fig.legend(h,l,loc="outside lower center",ncol=3,frameon=False)
    fig.savefig(RESULTS / "T454_04_INDIVIDUAL_PATHS.png", dpi=180, facecolor="white"); plt.close(fig)


def offset_sensitivity(forecasts):
    rows = []
    offsets = np.linspace(0, 1, 201)
    for split in ["holdout", "external"]:
        sub = forecasts[forecasts.split == split]
        for offset in offsets:
            pred = clip2(2.0 - (sub.x_generation + sub.ara_phase_gap + offset))
            ae = np.abs(pred - sub.target_generation_bounded)
            score = pd.DataFrame({"cell": sub.cell_key, "ae": ae}).groupby("cell").ae.mean().mean()
            rows.append({"split": split, "offset": offset, "cell_mean_mae": score})
    scan = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(11, 5.8), constrained_layout=True)
    for split, color in [("holdout", "#d27a20"), ("external", "#6b8e23")]:
        s = scan[scan.split == split]
        best = s.loc[s.cell_mean_mae.idxmin()]
        ax.plot(s.offset, s.cell_mean_mae, lw=2.5, color=color, label=f"{split}: minimum {best.offset:.2f}")
        ax.scatter([best.offset], [best.cell_mean_mae], color=color, s=65)
    ax.axvline(.25, color="#8d5ac7", ls="--", lw=2, label="predeclared 0.25")
    ax.set(title="Post-result sensitivity — is 0.25 a narrow landmark or part of a broad correction?", xlabel="constant contextual child allocation inserted inside 2 − (A + R + child)", ylabel="mean per-cell MAE (remaining-generation share)")
    ax.legend(frameon=False); style(ax)
    fig.savefig(RESULTS / "T454_05_POSTHOC_OFFSET_SENSITIVITY.png", dpi=180, facecolor="white"); plt.close(fig)
    return scan


def main():
    forecasts = build_forecasts()
    metrics, ledger = score(forecasts)
    boots = bootstrap(ledger)
    gate_table, winner, child_imps = gates(metrics)
    result = {
        "test": "T454", "frozen_before_results": True,
        "question": "Does contextual TE-ARA allocation predict unseen remaining lifespan more accurately than pure 2-x_A?",
        "holdout_relational_vs_pure_generation_improvement_pct": improvement(metrics,"holdout","generation","pure","relational"),
        "external_relational_vs_pure_generation_improvement_pct": improvement(metrics,"external","generation","pure","relational"),
        "best_holdout_child": winner,
        "holdout_child_improvements_vs_relational_pct": child_imps,
        "holdout_fixed_025_vs_pure_generation_improvement_pct": improvement(metrics,"holdout","generation","pure","fixed_025"),
        "external_fixed_025_vs_pure_generation_improvement_pct": improvement(metrics,"external","generation","pure","fixed_025"),
        "holdout_winner_clock_vs_pure_improvement_pct": improvement(metrics,"holdout","clock","pure",winner),
        "external_fixed_025_clock_vs_pure_improvement_pct": improvement(metrics,"external","clock","pure","fixed_025"),
        "external_size_child_vs_relational_improvement_pct": improvement(metrics,"external","generation","relational","size_child"),
        "gates_passed": int(gate_table.passed.sum()), "gates_total": len(gate_table),
    }
    if result["holdout_relational_vs_pure_generation_improvement_pct"] > 0 and result["external_relational_vs_pure_generation_improvement_pct"] > 0:
        result["assessment"] = "The signed relational correction improves the pure complement on both holdouts. Child correction remains separately determined by its frozen comparisons."
    else:
        result["assessment"] = "The contextual relational correction does not transfer as a general improvement over the pure complement."
    scan = offset_sensitivity(forecasts)
    forecasts.to_csv(RESULTS / "T454_DIRECT_FORECASTS.csv", index=False)
    metrics.to_csv(RESULTS / "T454_METRICS.csv", index=False)
    ledger.to_csv(RESULTS / "T454_PREDICTION_LEDGER.csv", index=False)
    boots.to_csv(RESULTS / "T454_BOOTSTRAP.csv", index=False)
    gate_table.to_csv(RESULTS / "T454_FROZEN_GATES.csv", index=False)
    scan.to_csv(RESULTS / "T454_POSTHOC_OFFSET_SENSITIVITY.csv", index=False)
    (RESULTS / "T454_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    plot_scores(metrics, gate_table); plot_paths(forecasts); plot_relation_and_child(forecasts); plot_individuals(forecasts)
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()
