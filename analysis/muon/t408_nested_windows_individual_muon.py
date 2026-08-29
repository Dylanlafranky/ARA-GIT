#!/usr/bin/env python3
"""T408: nested population-derived windows tested on individual muon events."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", r"F:\SystemFormulaFolder\.matplotlib_cache")

PKG = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
if PKG.exists():
    sys.path.insert(0, str(PKG))

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T408_nested_windows_individual_muon"
PROTOCOL = ROOT / "T408_NESTED_WINDOWS_INDIVIDUAL_MUON_PROTOCOL_2026-08-18.md"
EVENT_SOURCE = ROOT / "T379_individual_muon_child" / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv"
CURVE_SOURCE = ROOT / "T400_nested_child_window_population_to_event" / "T400_LOCAL_CHILD_CURVE.csv"
T400_RESULTS = ROOT / "T400_nested_child_window_population_to_event" / "T400_RESULTS.json"

PURE_X = 0.75
OBS_X = 0.7063064837018814
L2 = 0.01


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_events() -> list[dict]:
    numeric = ["delay_us", "multiplicity", "q1", "q2", "q3", "q4", "Q", "x_mu", "depth"]
    out = []
    with EVENT_SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            item = dict(row)
            for key in numeric:
                item[key] = float(item[key])
            item["event_index"] = int(item["event_index"])
            out.append(item)
    return out


def load_windows() -> dict:
    t400 = json.loads(T400_RESULTS.read_text(encoding="utf-8"))
    curve = []
    with CURVE_SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            curve.append((float(row["local_child_ara"]), float(row["time_us"])))
    curve.sort()
    xx = np.asarray([x for x, _ in curve], float)
    tt = np.asarray([t for _, t in curve], float)
    if not np.all(np.diff(xx) > 0):
        raise RuntimeError("T400 local child ARA is not strictly increasing")
    interp = lambda x: float(np.interp(x, xx, tt))
    left = float(t400["primary_population"]["left_time_us"])
    right = float(t400["primary_population"]["right_time_us"])
    return {
        "parent": [left, right],
        "pure": [interp(0.5), interp(PURE_X)],
        "observed": [interp(0.5), interp(OBS_X)],
        "t_at_0p5": interp(0.5),
        "t_at_0p75": interp(PURE_X),
        "t_at_0p706306": interp(OBS_X),
    }


def safe_child(q_left: float, q_right: float) -> tuple[float, float]:
    denom = q_left + q_right
    if denom <= 1e-12:
        return 1.0, 0.0
    return 2.0 * q_right / denom, 1.0


def add_geometry(rows: list[dict], windows: dict) -> list[dict]:
    p0, p1 = windows["parent"]
    g75_0, g75_1 = windows["pure"]
    g706_0, g706_1 = windows["observed"]
    out = []
    for row in rows:
        item = dict(row)
        x_a, present_a = safe_child(item["q1"], item["q2"])
        x_b, present_b = safe_child(item["q3"], item["q4"])
        sa, sb = x_a - 1.0, x_b - 1.0
        item.update(
            {
                "x_A": x_a,
                "x_B": x_b,
                "present_A": present_a,
                "present_B": present_b,
                "child_mean_signed": 0.5 * (sa + sb),
                "child_difference": sa - sb,
                "child_product": sa * sb,
                "child_abs_A": abs(sa),
                "child_abs_B": abs(sb),
                "in_parent_window": p0 <= item["delay_us"] <= p1,
                "y_pure": int(g75_0 <= item["delay_us"] <= g75_1),
                "y_observed": int(g706_0 <= item["delay_us"] <= g706_1),
            }
        )
        out.append(item)
    return out


def wrong_children(row: dict) -> tuple[float, float, float, float]:
    x_13, p_13 = safe_child(row["q1"], row["q3"])
    x_24, p_24 = safe_child(row["q2"], row["q4"])
    return x_13, p_13, x_24, p_24


def raw_features(rows: list[dict], kind: str) -> np.ndarray:
    ordinary = np.column_stack(
        [
            np.log(np.maximum([r["Q"] for r in rows], 1e-12)),
            [r["multiplicity"] for r in rows],
            [r["depth"] for r in rows],
        ]
    )
    if kind == "MG":
        return ordinary
    signed = np.asarray([r["x_mu"] - 1.0 for r in rows], float)
    depth = np.asarray([r["depth"] for r in rows], float)
    parent = np.column_stack([ordinary, signed, np.abs(signed), signed * depth])
    if kind == "MP":
        return parent
    if kind == "MN":
        child = np.column_stack(
            [
                [r["present_A"] for r in rows],
                [r["present_B"] for r in rows],
                [r["child_mean_signed"] for r in rows],
                [r["child_difference"] for r in rows],
                [r["child_product"] for r in rows],
                [r["child_abs_A"] for r in rows],
                [r["child_abs_B"] for r in rows],
            ]
        )
        return np.column_stack([parent, child])
    if kind == "MW":
        vals = []
        for row in rows:
            x1, p1, x2, p2 = wrong_children(row)
            s1, s2 = x1 - 1.0, x2 - 1.0
            vals.append([p1, p2, 0.5 * (s1 + s2), s1 - s2, s1 * s2, abs(s1), abs(s2)])
        return np.column_stack([parent, np.asarray(vals, float)])
    raise ValueError(kind)


@dataclass
class LogisticModel:
    kind: str
    mean: np.ndarray | None = None
    std: np.ndarray | None = None
    beta: np.ndarray | None = None

    def design(self, rows: list[dict], fit: bool = False) -> np.ndarray:
        raw = raw_features(rows, self.kind)
        if fit:
            self.mean = raw.mean(axis=0)
            self.std = raw.std(axis=0)
            self.std[self.std < 1e-9] = 1.0
        assert self.mean is not None and self.std is not None
        return np.column_stack([np.ones(len(rows)), (raw - self.mean) / self.std])

    @staticmethod
    def losses_for(beta: np.ndarray, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        eta = np.clip(X @ beta, -30, 30)
        return np.logaddexp(0.0, eta) - y * eta

    def fit(self, rows: list[dict], outcome: str) -> "LogisticModel":
        X = self.design(rows, fit=True)
        y = np.asarray([r[outcome] for r in rows], float)
        rate = np.clip(y.mean(), 1e-6, 1 - 1e-6)
        x0 = np.zeros(X.shape[1])
        x0[0] = math.log(rate / (1 - rate))

        def objective(beta: np.ndarray) -> float:
            penalty = L2 * float(np.sum(beta[1:] ** 2))
            return float(self.losses_for(beta, X, y).sum() + penalty)

        res = minimize(objective, x0, method="L-BFGS-B", options={"maxiter": 1000, "ftol": 1e-12})
        if not res.success:
            raise RuntimeError(f"{outcome}/{self.kind} fit failed: {res.message}")
        self.beta = np.asarray(res.x, float)
        return self

    def predict(self, rows: list[dict]) -> np.ndarray:
        assert self.beta is not None
        eta = np.clip(self.design(rows) @ self.beta, -30, 30)
        return 1.0 / (1.0 + np.exp(-eta))

    def losses(self, rows: list[dict], outcome: str, override: np.ndarray | None = None) -> np.ndarray:
        assert self.beta is not None
        y = np.asarray([r[outcome] for r in rows], float) if override is None else override
        return self.losses_for(self.beta, self.design(rows), y)


def auc_score(y: np.ndarray, p: np.ndarray) -> float:
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    ranks = rankdata(p, method="average")
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def blocks(rows: list[dict]) -> list[np.ndarray]:
    out = []
    for filename in sorted({r["file"] for r in rows}):
        idx = [i for i, r in enumerate(rows) if r["file"] == filename]
        idx.sort(key=lambda i: rows[i]["event_index"])
        for block in np.array_split(np.asarray(idx, int), 6):
            if len(block):
                out.append(block)
    return out


def bootstrap(rows: list[dict], delta: np.ndarray, seed: int, draws: int = 20_000) -> dict:
    block_values = np.asarray([float(delta[idx].mean()) for idx in blocks(rows)], float)
    rng = np.random.default_rng(seed)
    boot = block_values[rng.integers(0, len(block_values), size=(draws, len(block_values)))].mean(axis=1)
    return {
        "draws": draws,
        "block_means": block_values.tolist(),
        "mean": float(delta.mean()),
        "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
    }


def permutation(rows: list[dict], mp: LogisticModel, mn: LogisticModel, outcome: str, observed: float, seed: int, draws: int = 5_000) -> dict:
    y = np.asarray([r[outcome] for r in rows], float)
    run_idx = {
        name: np.asarray([i for i, r in enumerate(rows) if r["file"] == name], int)
        for name in sorted({r["file"] for r in rows})
    }
    rng = np.random.default_rng(seed)
    values = np.empty(draws)
    for j in range(draws):
        yp = y.copy()
        for idx in run_idx.values():
            yp[idx] = rng.permutation(yp[idx])
        values[j] = float((mp.losses(rows, outcome, yp) - mn.losses(rows, outcome, yp)).mean())
    return {
        "draws": draws,
        "mean": float(values.mean()),
        "ci95": [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))],
        "p_upper_add_one": float((1 + np.sum(values >= observed)) / (draws + 1)),
    }


def evaluate_window(cal: list[dict], hold: list[dict], outcome: str, seed: int) -> tuple[dict, dict[str, LogisticModel], dict[str, np.ndarray]]:
    models = {kind: LogisticModel(kind).fit(cal, outcome) for kind in ("MG", "MP", "MN", "MW")}
    losses = {kind: model.losses(hold, outcome) for kind, model in models.items()}
    probs = {kind: model.predict(hold) for kind, model in models.items()}
    y = np.asarray([r[outcome] for r in hold], int)
    primary_delta = losses["MP"] - losses["MN"]
    boot = bootstrap(hold, primary_delta, seed)
    perm = permutation(hold, models["MP"], models["MN"], outcome, boot["mean"], seed + 1000)
    by_run = {}
    for filename in sorted({r["file"] for r in hold}):
        idx = np.asarray([i for i, r in enumerate(hold) if r["file"] == filename], int)
        by_run[filename] = {
            "n": int(len(idx)),
            "positive": int(y[idx].sum()),
            "MP_minus_MN_logloss": float(primary_delta[idx].mean()),
            "model_logloss": {kind: float(losses[kind][idx].mean()) for kind in losses},
        }
    summary = {}
    for kind in models:
        summary[kind] = {
            "mean_logloss": float(losses[kind].mean()),
            "auc": auc_score(y, probs[kind]),
            "brier": float(np.mean((probs[kind] - y) ** 2)),
        }
    gates = {
        "G1_sample_size": bool(len(cal) >= 50 and len(hold) >= 50 and sum(r[outcome] for r in cal) >= 20 and y.sum() >= 20),
        "G2_both_holdout_runs_positive": bool(all(v["MP_minus_MN_logloss"] > 0 for v in by_run.values())),
        "G3_bootstrap_ci_strictly_positive": bool(boot["ci95"][0] > 0),
        "G4_nested_beats_wrong_lineage": bool(summary["MN"]["mean_logloss"] < summary["MW"]["mean_logloss"]),
        "G5_permutation_p_at_most_0p05": bool(perm["p_upper_add_one"] <= 0.05),
    }
    return (
        {
            "n_calibration": len(cal),
            "n_holdout": len(hold),
            "positive_calibration": int(sum(r[outcome] for r in cal)),
            "positive_holdout": int(y.sum()),
            "positive_rate_calibration": float(np.mean([r[outcome] for r in cal])),
            "positive_rate_holdout": float(y.mean()),
            "models": summary,
            "contrasts": {
                "MG_minus_MP": float((losses["MG"] - losses["MP"]).mean()),
                "MP_minus_MN": boot,
                "MN_minus_MW": float(summary["MW"]["mean_logloss"] - summary["MN"]["mean_logloss"]),
            },
            "by_run": by_run,
            "permutation": perm,
            "gates": gates,
            "supported": bool(all(gates.values())),
        },
        models,
        probs,
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def binary_loss(y: int, probability: float) -> float:
    p = float(np.clip(probability, 1e-12, 1 - 1e-12))
    return float(-(y * math.log(p) + (1 - y) * math.log(1 - p)))


def saved_diagnostics(event_scores: list[dict]) -> tuple[list[dict], list[dict]]:
    block_rows = []
    for filename in sorted({r["file"] for r in event_scores}):
        run = sorted((r for r in event_scores if r["file"] == filename), key=lambda r: r["event_index"])
        for block_number, idx in enumerate(np.array_split(np.arange(len(run)), 6), start=1):
            part = [run[int(i)] for i in idx]
            block_rows.append(
                {
                    "file": filename,
                    "block": block_number,
                    "n": len(part),
                    "pure_positive": sum(r["actual_in_pure_small_window"] for r in part),
                    "pure_positive_rate": float(np.mean([r["actual_in_pure_small_window"] for r in part])),
                    "pure_parent_minus_nested_logloss": float(np.mean([r["pure_parent_minus_nested_logloss"] for r in part])),
                    "observed_positive": sum(r["actual_in_observed_small_window"] for r in part),
                    "observed_positive_rate": float(np.mean([r["actual_in_observed_small_window"] for r in part])),
                    "observed_parent_minus_nested_logloss": float(np.mean([r["observed_parent_minus_nested_logloss"] for r in part])),
                }
            )
    topology_rows = []
    for present_a, present_b, label in ((1, 1, "both pairs"), (1, 0, "A only"), (0, 1, "B only"), (0, 0, "neither pair")):
        part = [r for r in event_scores if r["present_A"] == present_a and r["present_B"] == present_b]
        if not part:
            continue
        topology_rows.append(
            {
                "topology": label,
                "n": len(part),
                "pure_positive": sum(r["actual_in_pure_small_window"] for r in part),
                "pure_positive_rate": float(np.mean([r["actual_in_pure_small_window"] for r in part])),
                "observed_positive": sum(r["actual_in_observed_small_window"] for r in part),
                "observed_positive_rate": float(np.mean([r["actual_in_observed_small_window"] for r in part])),
                "mean_nested_probability_pure": float(np.mean([r["nested_probability_pure"] for r in part])),
                "mean_nested_probability_observed": float(np.mean([r["nested_probability_observed"] for r in part])),
            }
        )
    return block_rows, topology_rows


def make_figure(all_hold: list[dict], parent_hold: list[dict], event_scores: list[dict], windows: dict, results: dict) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 11), constrained_layout=True)
    blue, gold, pink, olive, ink, grey = "#4c83c3", "#d79a2b", "#b05c96", "#6f8f4e", "#27313d", "#9aa5b1"

    ax = axes[0, 0]
    step = max(1, len(all_hold) // 1600)
    sampled = all_hold[::step]
    ax.scatter([r["x_mu"] for r in sampled], [r["delay_us"] for r in sampled], s=8, alpha=0.18, color=blue, edgecolors="none")
    p0, p1 = windows["parent"]
    g0, g75 = windows["pure"]
    _, g706 = windows["observed"]
    ax.axhspan(p0, p1, color=blue, alpha=0.06, label="larger parent window")
    ax.axhspan(g0, g75, color=gold, alpha=0.20, label="small pure 0.5→0.75 window")
    ax.axhline(g706, color=pink, ls="--", lw=1.8, label="observed 0.706 endpoint")
    ax.set(xlim=(0, 2), ylim=(0.3, 3.0), xlabel="incoming parent ARA x_mu", ylabel="linked daughter delay (microseconds)", title="Individual muons against the two frozen time windows")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0, 1]
    labels, values, low, high, colors = [], [], [], [], []
    for outcome, color in (("pure", gold), ("observed", pink)):
        item = results[outcome]
        mean = item["contrasts"]["MP_minus_MN"]["mean"]
        ci = item["contrasts"]["MP_minus_MN"]["ci95"]
        labels.append(outcome)
        values.append(mean)
        low.append(mean - ci[0])
        high.append(ci[1] - mean)
        colors.append(color)
    ax.bar(labels, values, color=colors, edgecolor="white")
    ax.errorbar(labels, values, yerr=[low, high], fmt="none", color=ink, capsize=5)
    ax.axhline(0, color=ink, lw=1)
    ax.set(ylabel="holdout log-loss improvement: parent minus nested", title="Does child geometry improve individual window classification?")

    ax = axes[1, 0]
    pure_scores = event_scores
    x_a = np.asarray([r["x_A"] for r in pure_scores])
    x_b = np.asarray([r["x_B"] for r in pure_scores])
    y = np.asarray([r["actual_in_pure_small_window"] for r in pure_scores], bool)
    ax.scatter(x_a[~y], x_b[~y], s=18, alpha=0.24, color=grey, edgecolors="none", label="elsewhere in parent window")
    ax.scatter(x_a[y], x_b[y], s=24, alpha=0.58, facecolor="none", edgecolor=olive, linewidth=1, label="inside small window")
    ax.axvline(1, color=ink, lw=0.8)
    ax.axhline(1, color=ink, lw=0.8)
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="upper-pair child ARA x_A", ylabel="lower-pair child ARA x_B", title="Decompressed child geometry in held-out parent-window events")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    positives = [r for r in event_scores if r["actual_in_pure_small_window"]]
    negatives = [r for r in event_scores if not r["actual_in_pure_small_window"]]
    key = lambda r: (r["file"], r["event_index"])
    examples = sorted(positives, key=key)[:6] + sorted(negatives, key=key)[:6]
    yy = np.arange(len(examples))
    probs = [r["nested_probability_pure"] for r in examples]
    actual = [r["actual_in_pure_small_window"] for r in examples]
    ax.barh(yy, probs, color=[olive if a else grey for a in actual], alpha=0.82)
    ax.axvline(results["pure"]["positive_rate_holdout"], color=gold, ls="--", lw=1.7, label="holdout base rate")
    ax.set_yticks(yy, [f"{r['file'][-6:]} #{r['event_index']} | t={r['delay_us']:.3f}" for r in examples], fontsize=8)
    ax.invert_yaxis()
    ax.set(xlim=(0, 1), xlabel="calibration-frozen nested probability", title="Fixed-rule named individual muons (green = actually in small window)")
    ax.legend(frameon=False, fontsize=8)

    fig.suptitle("T408 — nested parent and grandchild windows in individual stopped muons", fontsize=18, fontweight="bold")
    fig.savefig(OUT / "T408_NESTED_WINDOWS_INDIVIDUAL_MUON.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    windows = load_windows()
    rows = add_geometry(load_events(), windows)
    cal_all = [r for r in rows if r["split"] == "calibration"]
    hold_all = [r for r in rows if r["split"] == "holdout"]
    cal = [r for r in cal_all if r["in_parent_window"]]
    hold = [r for r in hold_all if r["in_parent_window"]]
    if (len(cal_all), len(hold_all)) != (2396, 2109):
        raise RuntimeError("Unexpected T379 source counts")

    pure, pure_models, pure_probs = evaluate_window(cal, hold, "y_pure", 408)
    observed, observed_models, observed_probs = evaluate_window(cal, hold, "y_observed", 1408)
    verdict = (
        "PRIMARY NESTED INDIVIDUAL RELATION SUPPORTED"
        if pure["supported"]
        else "ONLY SECONDARY OBSERVED WINDOW SUPPORTED"
        if observed["supported"]
        else "NESTED INDIVIDUAL WINDOW RELATION NOT SUPPORTED"
    )
    results = {
        "test": "T408 nested windows in individual muons",
        "date": "2026-08-18",
        "protocol_sha256": sha256(PROTOCOL),
        "event_source_sha256": sha256(EVENT_SOURCE),
        "curve_source_sha256": sha256(CURVE_SOURCE),
        "verdict": verdict,
        "windows_us": windows,
        "all_event_counts": {"calibration": len(cal_all), "holdout": len(hold_all)},
        "parent_window_counts": {"calibration": len(cal), "holdout": len(hold)},
        "pure": pure,
        "observed": observed,
        "boundaries": [
            "The larger and smaller outcome windows are transferred from T400; they are not fitted to T379 delays.",
            "The four-counter child decomposition uses only the incoming prompt cluster and calibration-only gain normalization.",
            "The linked later signal is a charged-daughter candidate, not a direct observation of either neutrino.",
            "A positive classifier changes an event-level probability; it cannot identify an exact deterministic neutrino-birth instant.",
        ],
    }

    event_scores = []
    for i, row in enumerate(hold):
        y_pure = row["y_pure"]
        y_observed = row["y_observed"]
        pure_parent_loss = binary_loss(y_pure, float(pure_probs["MP"][i]))
        pure_nested_loss = binary_loss(y_pure, float(pure_probs["MN"][i]))
        observed_parent_loss = binary_loss(y_observed, float(observed_probs["MP"][i]))
        observed_nested_loss = binary_loss(y_observed, float(observed_probs["MN"][i]))
        event_scores.append(
            {
                "file": row["file"],
                "event_index": row["event_index"],
                "delay_us": row["delay_us"],
                "x_parent": row["x_mu"],
                "x_A": row["x_A"],
                "x_B": row["x_B"],
                "present_A": int(row["present_A"]),
                "present_B": int(row["present_B"]),
                "actual_in_pure_small_window": y_pure,
                "actual_in_observed_small_window": y_observed,
                "ordinary_probability_pure": float(pure_probs["MG"][i]),
                "parent_probability_pure": float(pure_probs["MP"][i]),
                "nested_probability_pure": float(pure_probs["MN"][i]),
                "wrong_lineage_probability_pure": float(pure_probs["MW"][i]),
                "nested_probability_observed": float(observed_probs["MN"][i]),
                "pure_parent_minus_nested_logloss": pure_parent_loss - pure_nested_loss,
                "observed_parent_minus_nested_logloss": observed_parent_loss - observed_nested_loss,
            }
        )
    block_rows, topology_rows = saved_diagnostics(event_scores)
    results["descriptive_diagnostics"] = {
        "worst_pure_block": min(block_rows, key=lambda r: r["pure_parent_minus_nested_logloss"]),
        "worst_observed_block": min(block_rows, key=lambda r: r["observed_parent_minus_nested_logloss"]),
        "topologies": topology_rows,
        "boundary": "These diagnostics explain the frozen uncertainty result; they are not additional confirmation gates.",
    }
    write_csv(OUT / "T408_HOLDOUT_EVENT_SCORES.csv", event_scores)
    write_csv(OUT / "T408_BLOCK_DIAGNOSTICS.csv", block_rows)
    write_csv(OUT / "T408_TOPOLOGY_DIAGNOSTICS.csv", topology_rows)
    write_csv(
        OUT / "T408_WINDOWS.csv",
        [
            {"window": name, "left_us": bounds[0], "right_us": bounds[1], "width_us": bounds[1] - bounds[0]}
            for name, bounds in (("parent", windows["parent"]), ("pure", windows["pure"]), ("observed", windows["observed"]))
        ],
    )
    model_rows = []
    for outcome_name, item in (("pure", pure), ("observed", observed)):
        for model_name, model in item["models"].items():
            model_rows.append({"outcome": outcome_name, "model": model_name, **model})
    write_csv(OUT / "T408_MODEL_SUMMARY.csv", model_rows)
    (OUT / "T408_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(hold_all, hold, event_scores, windows, results)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
