#!/usr/bin/env python3
"""T380: frozen same-scale child cut of the T379 QuarkNet events."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

_BOOT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_BOOT_ROOT / "_vendor"))

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "T379_individual_muon_child" / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv"
PROTOCOL = ROOT / "T380_SAME_SCALE_MUON_CHILD_CUT_PROTOCOL_2026-08-14.md"
EXPECTED_PROTOCOL_SHA256 = "de8ac09efd8c2dc884bc469871a5e29920e010982f79dfca20acf4cccfdc4b06"
OUT = ROOT / "T380_same_scale_muon_child"
LOWER = 0.3
UPPER = 10.0


def protocol_hash() -> str:
    return hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()


def load_rows() -> list[dict]:
    rows: list[dict] = []
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            q = np.array([float(raw[f"q{i}"]) for i in range(1, 5)], float)
            if not np.all(np.isfinite(q)) or not np.all(q > 0):
                continue
            total = float(q.sum())
            upper = float(q[0] + q[1])
            lower = float(q[2] + q[3])
            row = {
                "split": raw["split"],
                "file": raw["file"],
                "event_index": int(raw["event_index"]),
                "delay_us": float(raw["delay_us"]),
                "q1": float(q[0]), "q2": float(q[1]), "q3": float(q[2]), "q4": float(q[3]),
                "Q": total,
                "depth": 2.0 * float(np.dot(np.arange(4), q)) / (3.0 * total),
                "x_parent": 2.0 * lower / total,
            }
            add_pair_features(row, q, "child", ((0, 1), (2, 3)))
            add_pair_features(row, q, "wrong13_24", ((0, 2), (1, 3)))
            add_pair_features(row, q, "wrong14_23", ((0, 3), (1, 2)))
            rows.append(row)
    return rows


def add_pair_features(row: dict, q: np.ndarray, prefix: str, pairs: tuple[tuple[int, int], tuple[int, int]]) -> None:
    (a, b), (c, d) = pairs
    x1 = 2.0 * float(q[b]) / float(q[a] + q[b])
    x2 = 2.0 * float(q[d]) / float(q[c] + q[d])
    s1, s2 = x1 - 1.0, x2 - 1.0
    common = 0.5 * (s1 + s2)
    mismatch = 0.5 * (s1 - s2)
    row.update({
        f"{prefix}_x1": x1,
        f"{prefix}_x2": x2,
        f"{prefix}_common": common,
        f"{prefix}_mismatch": mismatch,
        f"{prefix}_abs_mismatch": abs(mismatch),
        f"{prefix}_coupling": 1.0 - abs(mismatch),
        f"{prefix}_interaction": s1 * s2,
    })


class Model:
    def __init__(self, kind: str):
        self.kind = kind
        self.mean: np.ndarray | None = None
        self.std: np.ndarray | None = None
        self.theta: np.ndarray | None = None

    def raw(self, rows: list[dict]) -> np.ndarray:
        n = len(rows)
        if self.kind == "M0":
            return np.empty((n, 0))
        base = np.column_stack([
            np.log(np.maximum([r["Q"] for r in rows], 1e-12)),
            [r["depth"] for r in rows],
        ])
        if self.kind == "MG":
            return base
        parent = np.column_stack([
            base,
            [r["x_parent"] - 1.0 for r in rows],
            [abs(r["x_parent"] - 1.0) for r in rows],
            [(r["x_parent"] - 1.0) * r["depth"] for r in rows],
        ])
        if self.kind == "MP":
            return parent
        prefix = {
            "MC": "child",
            "MW13_24": "wrong13_24",
            "MW14_23": "wrong14_23",
        }.get(self.kind)
        if prefix:
            return np.column_stack([
                parent,
                [r[f"{prefix}_common"] for r in rows],
                [r[f"{prefix}_mismatch"] for r in rows],
                [r[f"{prefix}_abs_mismatch"] for r in rows],
                [r[f"{prefix}_interaction"] for r in rows],
            ])
        raise ValueError(self.kind)

    def design(self, rows: list[dict], fit: bool = False) -> np.ndarray:
        raw = self.raw(rows)
        if raw.shape[1] == 0:
            return np.ones((len(rows), 1))
        if fit:
            self.mean = raw.mean(axis=0)
            self.std = raw.std(axis=0)
            self.std[self.std < 1e-9] = 1.0
        assert self.mean is not None and self.std is not None
        return np.column_stack([np.ones(len(rows)), (raw - self.mean) / self.std])

    @staticmethod
    def losses_for(theta: np.ndarray, X: np.ndarray, delay: np.ndarray) -> np.ndarray:
        width = UPPER - LOWER
        beta, gamma = theta[:-1], theta[-1]
        eta = np.clip(X @ beta, -5.0, 3.5)
        lam = np.exp(eta)
        u = np.clip(delay - LOWER, 0, width)
        log_norm = np.log(-np.expm1(-lam * width))
        log_exp = eta - lam * u - log_norm
        bg = 1.0 / (1.0 + np.exp(-gamma))
        return -logsumexp(
            np.vstack([np.log1p(-bg) + log_exp, np.log(bg) - math.log(width) + np.zeros_like(log_exp)]),
            axis=0,
        )

    def fit(self, rows: list[dict]) -> "Model":
        X = self.design(rows, fit=True)
        delay = np.asarray([r["delay_us"] for r in rows], float)
        x0 = np.zeros(X.shape[1] + 1)
        x0[0] = math.log(1 / 2.1)
        x0[-1] = -3.0

        def objective(theta: np.ndarray) -> float:
            loss = self.losses_for(theta, X, delay)
            return float(loss.sum() + 1e-3 * np.sum(theta[1:-1] ** 2))

        res = minimize(objective, x0, method="L-BFGS-B", options={"maxiter": 900, "ftol": 1e-11})
        if not res.success:
            print(f"WARNING {self.kind}: {res.message}", flush=True)
        self.theta = np.asarray(res.x)
        return self

    def losses(self, rows: list[dict], delay_override: np.ndarray | None = None) -> np.ndarray:
        assert self.theta is not None
        X = self.design(rows)
        delay = np.asarray([r["delay_us"] for r in rows], float) if delay_override is None else delay_override
        return self.losses_for(self.theta, X, delay)


def block_bootstrap(rows: list[dict], delta: np.ndarray, seed: int = 380, nboot: int = 10_000) -> dict:
    blocks: list[float] = []
    for filename in sorted({r["file"] for r in rows}):
        idx = np.array([i for i, r in enumerate(rows) if r["file"] == filename], int)
        for block in np.array_split(idx, 6):
            if len(block):
                blocks.append(float(delta[block].mean()))
    arr = np.asarray(blocks)
    rng = np.random.default_rng(seed)
    boot = arr[rng.integers(0, len(arr), size=(nboot, len(arr)))].mean(axis=1)
    return {
        "n_blocks": len(blocks),
        "block_means": blocks,
        "mean": float(delta.mean()),
        "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
    }


def evaluate(rows: list[dict]) -> tuple[dict, dict[str, Model], dict[str, np.ndarray]]:
    cal = [r for r in rows if r["split"] == "calibration"]
    hold = [r for r in rows if r["split"] == "holdout"]
    if (len(cal), len(hold)) != (682, 572):
        raise RuntimeError(f"Frozen cohort changed: calibration={len(cal)}, holdout={len(hold)}")
    kinds = ("M0", "MG", "MP", "MC", "MW13_24", "MW14_23")
    models = {kind: Model(kind).fit(cal) for kind in kinds}
    losses = {kind: models[kind].losses(hold) for kind in kinds}
    delta = losses["MP"] - losses["MC"]
    boot = block_bootstrap(hold, delta)

    by_run = {}
    for filename in sorted({r["file"] for r in hold}):
        idx = np.array([i for i, r in enumerate(hold) if r["file"] == filename], int)
        by_run[filename] = {
            "n": int(len(idx)),
            "mean_nll": {kind: float(losses[kind][idx].mean()) for kind in kinds},
            "delta_MP_minus_MC": float(delta[idx].mean()),
        }

    rng = np.random.default_rng(380)
    original_delay = np.asarray([r["delay_us"] for r in hold], float)
    run_indices = {
        filename: np.array([i for i, r in enumerate(hold) if r["file"] == filename], int)
        for filename in sorted({r["file"] for r in hold})
    }
    perm_deltas = []
    for _ in range(1000):
        perm = original_delay.copy()
        for idx in run_indices.values():
            perm[idx] = rng.permutation(perm[idx])
        perm_deltas.append(float((models["MP"].losses(hold, perm) - models["MC"].losses(hold, perm)).mean()))
    perm = np.asarray(perm_deltas)
    perm_q975 = float(np.quantile(perm, 0.975))

    mean_nll = {kind: float(losses[kind].mean()) for kind in kinds}
    gates = {
        "positive_in_both_holdout_runs": all(v["delta_MP_minus_MC"] > 0 for v in by_run.values()),
        "bootstrap_ci_above_zero": boot["ci95"][0] > 0,
        "beats_both_wrong_pairings": mean_nll["MC"] < mean_nll["MW13_24"] and mean_nll["MC"] < mean_nll["MW14_23"],
        "exceeds_permutation_q97_5": boot["mean"] > perm_q975,
    }
    supported = all(gates.values())

    correlations = {}
    for field in ("child_x1", "child_x2", "child_common", "child_mismatch", "child_coupling", "x_parent", "depth", "Q"):
        for target in ("delay_us", "depth", "x_parent"):
            if field == target:
                continue
            rho, p = spearmanr([r[field] for r in hold], [r[target] for r in hold])
            correlations[f"{field}_vs_{target}"] = {"rho": float(rho), "p": float(p)}

    quadrant_rows = []
    for name, condition in (
        ("UU: xU<1, xL<1", lambda r: r["child_x1"] < 1 and r["child_x2"] < 1),
        ("UL: xU<1, xL>=1", lambda r: r["child_x1"] < 1 and r["child_x2"] >= 1),
        ("LU: xU>=1, xL<1", lambda r: r["child_x1"] >= 1 and r["child_x2"] < 1),
        ("LL: xU>=1, xL>=1", lambda r: r["child_x1"] >= 1 and r["child_x2"] >= 1),
    ):
        subset = [r for r in hold if condition(r)]
        quadrant_rows.append({
            "quadrant": name,
            "n": len(subset),
            "share": len(subset) / len(hold),
            "mean_delay_us": float(np.mean([r["delay_us"] for r in subset])) if subset else None,
            "median_delay_us": float(np.median([r["delay_us"] for r in subset])) if subset else None,
        })

    coordinate_summary = {}
    for split_name, subset in (("calibration", cal), ("holdout", hold)):
        coordinate_summary[split_name] = {}
        for field in ("child_x1", "child_x2", "child_common", "child_mismatch", "child_coupling", "x_parent", "depth", "Q"):
            values = np.asarray([r[field] for r in subset], float)
            coordinate_summary[split_name][field] = {
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "q05": float(np.quantile(values, 0.05)),
                "q95": float(np.quantile(values, 0.95)),
            }

    result = {
        "protocol_sha256": protocol_hash(),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "n_calibration": len(cal),
        "n_holdout": len(hold),
        "mean_nll": mean_nll,
        "delta_MP_minus_MC": boot,
        "by_run": by_run,
        "permutation": {
            "replicates": len(perm),
            "mean": float(perm.mean()),
            "ci95": [float(np.quantile(perm, 0.025)), float(np.quantile(perm, 0.975))],
            "q97_5": perm_q975,
        },
        "gates": gates,
        "verdict": "SUPPORTED" if supported else "NOT SUPPORTED",
        "correlations": correlations,
        "coordinate_summary": coordinate_summary,
        "quadrants": quadrant_rows,
        "data_boundary": "The later electron is measured; neutrinos are co-created but not directly observed.",
    }
    return result, models, losses


def save_rows(rows: list[dict]) -> None:
    fields = [
        "split", "file", "event_index", "delay_us", "q1", "q2", "q3", "q4", "Q", "depth", "x_parent",
        "child_x1", "child_x2", "child_common", "child_mismatch", "child_abs_mismatch", "child_coupling", "child_interaction",
        "wrong13_24_x1", "wrong13_24_x2", "wrong14_23_x1", "wrong14_23_x2",
    ]
    with (OUT / "T380_SAME_SCALE_MUON_CHILD_EVENTS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


def heatmap_rows(hold: list[dict], bins: int = 10) -> list[dict]:
    edges = np.linspace(0, 2, bins + 1)
    output = []
    for i in range(bins):
        for j in range(bins):
            subset = [r for r in hold if edges[i] <= r["child_x1"] < (edges[i + 1] if i < bins - 1 else edges[i + 1] + 1e-9)
                      and edges[j] <= r["child_x2"] < (edges[j + 1] if j < bins - 1 else edges[j + 1] + 1e-9)]
            if not subset:
                continue
            output.append({
                "xU_bin": f"{0.5*(edges[i]+edges[i+1]):.1f}",
                "xL_bin": f"{0.5*(edges[j]+edges[j+1]):.1f}",
                "xU_center": float(0.5 * (edges[i] + edges[i + 1])),
                "xL_center": float(0.5 * (edges[j] + edges[j + 1])),
                "n": len(subset),
                "mean_delay_us": float(np.mean([r["delay_us"] for r in subset])),
                "median_delay_us": float(np.median([r["delay_us"] for r in subset])),
            })
    return output


def make_qa_figure(rows: list[dict], result: dict) -> None:
    hold = [r for r in rows if r["split"] == "holdout"]
    grid = heatmap_rows(hold)
    fig = plt.figure(figsize=(16, 12), constrained_layout=True)
    gs = fig.add_gridspec(2, 2)

    ax = fig.add_subplot(gs[0, 0])
    sc = ax.scatter([r["child_x1"] for r in hold], [r["child_x2"] for r in hold],
                    c=[r["delay_us"] for r in hold], s=18, alpha=0.55, cmap="viridis")
    ax.axvline(1, color="#e1a43c", linestyle="--"); ax.axhline(1, color="#e1a43c", linestyle="--")
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="upper child ARA xU = 2q2/(q1+q2)",
           ylabel="lower child ARA xL = 2q4/(q3+q4)", title=f"Held-out same-scale child plane (n={len(hold)})")
    fig.colorbar(sc, ax=ax, label="later linked daughter delay (microseconds)")

    ax = fig.add_subplot(gs[0, 1])
    labels = ["M0", "MG", "MP", "MC", "wrong 13/24", "wrong 14/23"]
    vals = [result["mean_nll"][k] for k in ("M0", "MG", "MP", "MC", "MW13_24", "MW14_23")]
    ax.bar(labels, vals, color=["#9aa5b1", "#769dc7", "#6086ae", "#42b883", "#c78383", "#b76f8f"])
    ax.set_ylabel("held-out mean negative log likelihood (lower is better)")
    ax.set_title("Prospective daughter-time score")
    ax.tick_params(axis="x", rotation=18)
    for i, value in enumerate(vals): ax.text(i, value, f"{value:.6f}", ha="center", va="bottom", fontsize=8)

    ax = fig.add_subplot(gs[1, 0])
    run_names = list(result["by_run"])
    run_delta = [result["by_run"][name]["delta_MP_minus_MC"] for name in run_names]
    ax.bar([n.replace("6845.2020.", "") for n in run_names], run_delta, color=["#5c8ec5", "#8a6bb8"])
    ax.axhline(0, color="#222", linewidth=1)
    ax.set_ylabel("MP - MC mean NLL (positive favors child cut)")
    ax.set_title(f"Each untouched holdout run; pooled={result['delta_MP_minus_MC']['mean']:+.7f}")
    for i, value in enumerate(run_delta): ax.text(i, value, f"{value:+.7f}", ha="center", va="bottom" if value >= 0 else "top")

    ax = fig.add_subplot(gs[1, 1])
    x = [r["x_parent"] for r in hold]
    y = [r["child_common"] for r in hold]
    ax.scatter(x, y, s=14, alpha=0.35, color="#8066b2")
    ax.axvline(1, color="#3aa66f", linestyle="--"); ax.axhline(0, color="#e1a43c", linestyle="--")
    rho = result["correlations"]["child_common_vs_x_parent"]["rho"]
    ax.set(xlim=(0, 2), xlabel="parent ARA xP", ylabel="same-scale shared child direction C",
           title=f"Child cut versus parent cut (Spearman rho={rho:+.3f})")

    fig.suptitle(f"T380 — same-scale muon child cut: {result['verdict']}", fontsize=20, fontweight="bold")
    fig.savefig(OUT / "T380_SAME_SCALE_MUON_CHILD_CUT_FIGURE.png", dpi=180)
    fig.savefig(OUT / "T380_SAME_SCALE_MUON_CHILD_CUT_FIGURE.svg")
    plt.close(fig)


def build_artifact(rows: list[dict], result: dict) -> dict:
    hold = [r for r in rows if r["split"] == "holdout"]
    sample = hold  # 572 reviewed rows; bounded and all are shown.
    scatter = [{
        "event": f"{r['file'][-6:]}-{r['event_index']}",
        "run": r["file"],
        "xU": round(r["child_x1"], 8),
        "xL": round(r["child_x2"], 8),
        "delay_us": round(r["delay_us"], 8),
        "parent_x": round(r["x_parent"], 8),
        "depth": round(r["depth"], 8),
        "coupling": round(r["child_coupling"], 8),
    } for r in sample]
    model_rows = [{
        "model": label,
        "mean_nll": result["mean_nll"][key],
        "role": role,
        "features": features,
    } for key, label, role, features in (
        ("M0", "M0 memoryless", "baseline", "intercept"),
        ("MG", "MG ordinary", "baseline", "total pulse + depth"),
        ("MP", "MP parent", "baseline", "ordinary + parent ARA"),
        ("MC", "MC same-scale child", "actual", "parent + C, D, |D|, interaction"),
        ("MW13_24", "wrong 13/24", "comparison", "wrong same-sized pair cut"),
        ("MW14_23", "wrong 14/23", "comparison", "wrong same-sized pair cut"),
    )]
    run_rows = [{
        "run": name.replace("6845.2020.", ""),
        "n": item["n"],
        "delta": item["delta_MP_minus_MC"],
        "MP_nll": item["mean_nll"]["MP"],
        "MC_nll": item["mean_nll"]["MC"],
    } for name, item in result["by_run"].items()]
    gate_rows = [{"gate": key.replace("_", " "), "passed": value} for key, value in result["gates"].items()]
    summary_rows = [{
        "verdict": result["verdict"],
        "n_calibration": result["n_calibration"],
        "n_holdout": result["n_holdout"],
        "delta": result["delta_MP_minus_MC"]["mean"],
        "ci_low": result["delta_MP_minus_MC"]["ci95"][0],
        "ci_high": result["delta_MP_minus_MC"]["ci95"][1],
        "gates_passed": sum(result["gates"].values()),
    }]
    source = {
        "id": "quarknet_t379_events",
        "label": "QuarkNet detector 6845 event-linked T379 reduction",
        "path": "analysis/muon/T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv",
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "sql": "SELECT *, 2*q2/(q1+q2) AS xU, 2*q4/(q3+q4) AS xL FROM read_csv_auto('analysis/muon/T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv') WHERE q1>0 AND q2>0 AND q3>0 AND q4>0",
            "description": "Select four-counter event-linked candidates and construct both adjacent same-scale child cuts.",
            "tables_used": ["analysis/muon/T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv"],
            "filters": ["q1>0", "q2>0", "q3>0", "q4>0"],
            "metric_definitions": ["xU=2*q2/(q1+q2)", "xL=2*q4/(q3+q4)"],
        },
    }
    result_source = {
        "id": "t380_frozen_results",
        "label": "T380 frozen same-scale child scoring output",
        "path": "analysis/muon/T380_same_scale_muon_child/T380_SAME_SCALE_MUON_CHILD_CUT_RESULTS.json",
        "query": {
            "engine": "duckdb",
            "language": "sql",
            "sql": "SELECT * FROM read_json_auto('analysis/muon/T380_same_scale_muon_child/T380_SAME_SCALE_MUON_CHILD_CUT_RESULTS.json')",
            "description": "Read the frozen T380 prospective scores, run splits, uncertainty and gate results.",
            "tables_used": ["analysis/muon/T380_same_scale_muon_child/T380_SAME_SCALE_MUON_CHILD_CUT_RESULTS.json"],
            "metric_definitions": ["delta=held-out mean NLL(MP)-mean NLL(MC); positive favors the same-scale child cut"],
        },
    }
    delta = result["delta_MP_minus_MC"]["mean"]
    ci = result["delta_MP_minus_MC"]["ci95"]
    verdict_plain = "The same-scale child cut passed every frozen gate." if result["verdict"] == "SUPPORTED" else "The same-scale child cut did not pass every frozen gate."
    blocks = [
        {"id": "title", "type": "markdown", "body": "# T380 — Same-scale muon child cut"},
        {"id": "summary", "type": "markdown", "sourceId": result_source["id"], "body": (
            "## Technical summary\n\n"
            f"**{verdict_plain}** The prospective parent-minus-child score was **{delta:+.7f} NLL per held-out event** "
            f"with a chronological-block 95% interval of **{ci[0]:+.7f} to {ci[1]:+.7f}**. "
            f"The analysis used {result['n_calibration']} calibration and {result['n_holdout']} untouched holdout four-counter events. "
            "This is a deeper cut of the same detector data, not an independent archive replication."
        )},
        {"id": "metrics", "type": "metric-strip", "cardIds": ["gate_card", "delta_card", "sample_card"]},
        {"id": "plane_intro", "type": "markdown", "sourceId": source["id"], "body": (
            "## The two same-scale children occupy a full 0–2 × 0–2 plane\n\n"
            "Each point is one untouched incoming muon. The horizontal coordinate cuts counters 1–2 at their own scale; "
            "the vertical coordinate independently cuts counters 3–4. Both ridges are at 1. The daughter delay is retained "
            "as tooltip evidence only and never entered either coordinate."
        )},
        {"id": "plane_chart", "type": "chart", "chartId": "child_plane"},
        {"id": "score_intro", "type": "markdown", "sourceId": result_source["id"], "body": (
            "## Prospective scoring decides whether the deeper cut adds information\n\n"
            "Lower negative log likelihood is better. `MP` already knows ordinary pulse geometry and the old parent cut. "
            "The registered test is whether `MC` improves beyond `MP`, while also beating two equally complex wrong pairings."
        )},
        {"id": "score_chart", "type": "chart", "chartId": "model_score"},
        {"id": "run_intro", "type": "markdown", "sourceId": result_source["id"], "body": (
            "## The effect must repeat in both untouched runs\n\n"
            "Positive values favor the same-scale child model. Separate run scores prevent a pooled average from hiding a sign reversal."
        )},
        {"id": "run_chart", "type": "chart", "chartId": "run_delta"},
        {"id": "gate_intro", "type": "markdown", "sourceId": result_source["id"], "body": (
            "## Frozen gate audit\n\n"
            "Support required two positive run effects, an interval wholly above zero, dominance over both wrong pairings, "
            "and an observed increment above the 97.5th percentile of within-run outcome permutations."
        )},
        {"id": "gate_table", "type": "table", "tableId": "gate_audit"},
        {"id": "definitions", "type": "markdown", "body": (
            "## Scope, data and metric definitions\n\n"
            "The medium and source are unchanged from T379: four stacked solid-plastic scintillators in QuarkNet detector 6845. "
            "Only the cut changed. `xU=2q2/(q1+q2)` and `xL=2q4/(q3+q4)` are the two child-scale coordinates. "
            "Their shared direction is `C=((xU-1)+(xL-1))/2`; mismatch is `D=((xU-1)-(xL-1))/2`; "
            "coupling is `K=1-|D|`. The visible outcome is the delay to the later linked charged-electron candidate."
        )},
        {"id": "methods", "type": "markdown", "body": (
            "## Frozen methodology\n\n"
            "February 11–12 fixed calibration and March 17–18 fixed holdout. Every model used the same truncated-exponential plus "
            "uniform-background likelihood over 0.3–10 microseconds. The child model added `C`, `D`, `|D|` and their signed "
            "interaction after all parent terms. Uncertainty used 12 chronological blocks; the permutation control shuffled outcomes only within run."
        )},
        {"id": "limitations", "type": "markdown", "body": (
            "## Limitations and robustness boundary\n\n"
            "This test directly measures the later electron, not either neutrino. The four prompt values are detector projections, "
            "not a complete internal-state measurement. The cohort is the previously opened fourfold subset of T379, so this is a "
            "registered deeper cut rather than an independent replication. A negative result would reject this cut as an individual countdown, "
            "not the previously observed population-scale handover."
        )},
        {"id": "next", "type": "markdown", "body": (
            "## Recommended next step\n\n"
            "If supported, freeze the same coordinate on another four-layer detector before expanding the feature set. If not supported, "
            "stop subdividing these four prompt amplitudes: the missing child state would require a genuinely new event-linked measurement "
            "such as spin/polarisation, local field, stopping material, or charged-daughter direction/energy."
        )},
        {"id": "questions", "type": "markdown", "body": (
            "## Further questions\n\n"
            "Would the same-scale cut replicate in a detector with resolved stopping material? Does a spin-sensitive child coordinate "
            "add information that pulse geometry cannot? Can daughter energy or direction identify the otherwise hidden branch without using future timing?"
        )},
    ]
    cards = [
        {"id": "gate_card", "dataset": "summary", "sourceId": result_source["id"], "description": "All four frozen support gates must pass.",
         "metrics": [{"label": "Frozen gates passed", "field": "gates_passed", "format": "number"}]},
        {"id": "delta_card", "dataset": "summary", "sourceId": result_source["id"], "description": "Positive means the child cut improves held-out timing prediction beyond the parent cut.",
         "metrics": [{"label": "MP − MC NLL", "field": "delta", "format": "number", "signed": True},
                     {"label": "CI low", "field": "ci_low", "format": "number", "signed": True},
                     {"label": "CI high", "field": "ci_high", "format": "number", "signed": True}]},
        {"id": "sample_card", "dataset": "summary", "sourceId": result_source["id"], "description": "Four-counter incoming muon / later electron event pairs.",
         "metrics": [{"label": "Held-out events", "field": "n_holdout", "format": "number"},
                     {"label": "Calibration", "field": "n_calibration", "format": "number"}]},
    ]
    charts = [
        {"id": "child_plane", "title": "Same-scale child ARA plane", "subtitle": f"Untouched holdout events, n={len(scatter)}; ridge lines are xU=1 and xL=1",
         "type": "scatter", "intent": "relationship", "question": "Where do the two adjacent child cuts jointly sit?",
         "rationale": "A scatter plot preserves each event and shows joint occupancy across both 0–2 child axes.",
         "dataset": "scatter", "sourceId": source["id"], "layout": "full",
         "encodings": {"x": {"field": "xU", "type": "quantitative", "label": "Upper child ARA xU", "unit": "ARA 0–2"},
                       "y": {"field": "xL", "type": "quantitative", "label": "Lower child ARA xL", "unit": "ARA 0–2"},
                       "color": {"field": "run", "type": "nominal", "label": "Holdout run"},
                       "tooltip": [{"field": "event", "label": "Event"}, {"field": "delay_us", "label": "Later daughter delay", "unit": "microseconds"},
                                   {"field": "parent_x", "label": "Parent ARA"}, {"field": "coupling", "label": "Child coupling K"}]},
         "combinationRationale": "Color distinguishes the two independent holdout days without encoding the future daughter time.",
         "referenceLines": [{"axis": "x", "value": 1, "label": "upper child ridge", "lineStyle": "dashed", "color": "neutral"},
                            {"axis": "y", "value": 1, "label": "lower child ridge", "lineStyle": "dashed", "color": "neutral"}]},
        {"id": "model_score", "title": "Held-out daughter-time model score", "subtitle": "Mean negative log likelihood per event; lower is better",
         "type": "bar", "intent": "comparison", "question": "Does the same-scale child cut beat parent and wrong-pair controls?",
         "rationale": "Bars provide a direct model-by-model score comparison on one common likelihood scale.",
         "dataset": "models", "sourceId": result_source["id"], "layout": "full",
         "encodings": {"x": {"field": "model", "type": "nominal", "label": "Frozen model"},
                       "y": {"field": "mean_nll", "type": "quantitative", "label": "Mean held-out NLL"},
                       "tooltip": [{"field": "features", "label": "Features"}, {"field": "role", "label": "Role"}]},
         "valueFormat": "number"},
        {"id": "run_delta", "title": "Same-scale child increment in each holdout run", "subtitle": "MP − MC mean NLL; positive favors the child cut",
         "type": "bar", "intent": "comparison", "question": "Does the effect keep the same sign on both holdout days?",
         "rationale": "Separate bars expose run-to-run sign changes hidden by a pooled score.",
         "dataset": "runs", "sourceId": result_source["id"], "layout": "full",
         "encodings": {"x": {"field": "run", "type": "nominal", "label": "Holdout run"},
                       "y": {"field": "delta", "type": "quantitative", "label": "MP − MC mean NLL"},
                       "tooltip": [{"field": "n", "label": "Events"}, {"field": "MP_nll", "label": "MP NLL"}, {"field": "MC_nll", "label": "MC NLL"}]},
         "referenceLines": [{"axis": "y", "value": 0, "label": "no improvement", "lineStyle": "solid", "color": "neutral"}],
         "valueFormat": "number"},
    ]
    tables = [{
        "id": "gate_audit", "title": "Frozen support gates", "subtitle": f"{sum(result['gates'].values())} of {len(result['gates'])} passed",
        "dataset": "gates", "sourceId": result_source["id"], "defaultSort": {"field": "gate", "direction": "asc"}, "density": "spacious", "layout": "full",
        "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "passed", "label": "Passed", "type": "text"}],
    }]
    return {
        "surface": "report",
        "manifest": {
            "version": 1, "surface": "report", "title": "T380 — Same-scale muon child cut",
            "description": "Prospective deeper-cut test of adjacent QuarkNet counter-pair ARA relations.",
            "generatedAt": "2026-08-14T00:00:00+10:00",
            "blocks": blocks, "cards": cards, "charts": charts, "tables": tables, "sources": [source, result_source],
        },
        "snapshot": {
            "version": 1, "generatedAt": "2026-08-14T00:00:00+10:00", "status": "ready",
            "datasets": {"summary": summary_rows, "scatter": scatter, "heatmap": heatmap_rows(hold), "models": model_rows,
                         "runs": run_rows, "gates": gate_rows, "quadrants": result["quadrants"]},
        },
        "sources": [source, result_source],
    }


def validate_outputs(rows: list[dict], result: dict) -> dict:
    checks = {
        "protocol_hash_matches": protocol_hash() == EXPECTED_PROTOCOL_SHA256,
        "source_exists": SOURCE.exists(),
        "calibration_count": sum(r["split"] == "calibration" for r in rows) == 682,
        "holdout_count": sum(r["split"] == "holdout" for r in rows) == 572,
        "all_child_coordinates_in_0_2": all(0 <= r["child_x1"] <= 2 and 0 <= r["child_x2"] <= 2 for r in rows),
        "all_delays_in_window": all(LOWER <= r["delay_us"] <= UPPER for r in rows),
        "all_models_finite": all(np.isfinite(v) for v in result["mean_nll"].values()),
        "result_verdict_matches_gates": (result["verdict"] == "SUPPORTED") == all(result["gates"].values()),
    }
    return {"status": "passed" if all(checks.values()) else "failed", "checks": checks}


def main() -> None:
    if protocol_hash() != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"Frozen protocol changed: {protocol_hash()}")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    result, _, _ = evaluate(rows)
    save_rows(rows)
    make_qa_figure(rows, result)
    validation = validate_outputs(rows, result)
    (OUT / "T380_SAME_SCALE_MUON_CHILD_CUT_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (OUT / "T380_SAME_SCALE_MUON_CHILD_CUT_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (OUT / "artifact.json").write_text(json.dumps(build_artifact(rows, result), indent=2), encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "n": [result["n_calibration"], result["n_holdout"]],
        "delta": result["delta_MP_minus_MC"],
        "mean_nll": result["mean_nll"],
        "by_run": result["by_run"],
        "permutation": result["permutation"],
        "gates": result["gates"],
        "validation": validation["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
