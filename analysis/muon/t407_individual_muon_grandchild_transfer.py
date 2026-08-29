#!/usr/bin/env python3
"""T407: transfer the proposed grandchild landmark to individual muon events."""

from __future__ import annotations

import csv
import hashlib
import json
import math
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
from scipy.optimize import minimize
from scipy.special import logsumexp


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T407_individual_muon_grandchild_transfer"
PROTOCOL = ROOT / "T407_INDIVIDUAL_MUON_GRANDCHILD_TRANSFER_PROTOCOL_2026-08-18.md"
SOURCE = ROOT / "T379_individual_muon_child" / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv"
LOWER, UPPER = 0.3, 10.0
CENTRES = {
    "M050": 0.50,
    "M0706": 0.7063064837018814,
    "M075": 0.75,
    "M100": 1.00,
    "M125": 1.25,
    "M150": 1.50,
}
PRIMARY = "M075"
SECONDARY = "M0706"
HALF_WIDTH = 0.05


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows() -> list[dict]:
    numeric = ["delay_us", "multiplicity", "Q", "x_mu", "depth"]
    rows = []
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            item = dict(row)
            for key in numeric:
                item[key] = float(item[key])
            item["event_index"] = int(item["event_index"])
            rows.append(item)
    return rows


class TimingModel:
    def __init__(self, centre: float | None):
        self.centre = centre
        self.mean: np.ndarray | None = None
        self.std: np.ndarray | None = None
        self.theta: np.ndarray | None = None

    def raw(self, rows: list[dict]) -> np.ndarray:
        base = np.column_stack(
            [
                np.log(np.maximum([r["Q"] for r in rows], 1e-12)),
                [r["multiplicity"] for r in rows],
                [r["depth"] for r in rows],
            ]
        )
        if self.centre is None:
            return base
        band = np.asarray([abs(r["x_mu"] - self.centre) <= HALF_WIDTH for r in rows], float)
        return np.column_stack([base, band])

    def design(self, rows: list[dict], fit: bool = False) -> np.ndarray:
        raw = self.raw(rows)
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

    def fit(self, rows: list[dict]) -> "TimingModel":
        X = self.design(rows, fit=True)
        delay = np.asarray([r["delay_us"] for r in rows], float)
        x0 = np.zeros(X.shape[1] + 1)
        x0[0] = math.log(1 / 2.1)
        x0[-1] = -3.0

        def objective(theta: np.ndarray) -> float:
            penalty = 1e-3 * float(np.sum(theta[1:-1] ** 2))
            return float(self.losses_for(theta, X, delay).sum() + penalty)

        res = minimize(objective, x0, method="L-BFGS-B", options={"maxiter": 800, "ftol": 1e-11})
        if not res.success:
            raise RuntimeError(f"Model fit failed: {res.message}")
        self.theta = np.asarray(res.x)
        return self

    def losses(self, rows: list[dict], delay: np.ndarray | None = None) -> np.ndarray:
        assert self.theta is not None
        X = self.design(rows)
        y = np.asarray([r["delay_us"] for r in rows], float) if delay is None else delay
        return self.losses_for(self.theta, X, y)

    def rate(self, rows: list[dict]) -> np.ndarray:
        assert self.theta is not None
        return np.exp(np.clip(self.design(rows) @ self.theta[:-1], -5.0, 3.5))

    def background_fraction(self) -> float:
        assert self.theta is not None
        return float(1.0 / (1.0 + np.exp(-self.theta[-1])))

    def band_coefficient(self) -> float | None:
        if self.centre is None:
            return None
        assert self.theta is not None
        return float(self.theta[-2])


def block_means(rows: list[dict], delta: np.ndarray) -> np.ndarray:
    blocks = []
    for filename in sorted({r["file"] for r in rows}):
        idx = np.asarray([i for i, r in enumerate(rows) if r["file"] == filename], int)
        for block in np.array_split(idx, 6):
            if len(block):
                blocks.append(float(delta[block].mean()))
    return np.asarray(blocks)


def block_bootstrap(rows: list[dict], delta: np.ndarray, seed: int, draws: int = 20_000) -> dict:
    blocks = block_means(rows, delta)
    rng = np.random.default_rng(seed)
    boot = blocks[rng.integers(0, len(blocks), size=(draws, len(blocks)))].mean(axis=1)
    return {
        "block_means": blocks.tolist(),
        "draws": draws,
        "mean": float(delta.mean()),
        "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
    }


def mixture_median(rate: np.ndarray, bg: float) -> np.ndarray:
    width = UPPER - LOWER
    lo = np.full_like(rate, LOWER, dtype=float)
    hi = np.full_like(rate, UPPER, dtype=float)
    norm = 1.0 - np.exp(-rate * width)
    for _ in range(55):
        mid = (lo + hi) / 2.0
        u = mid - LOWER
        cdf_exp = (1.0 - np.exp(-rate * u)) / norm
        cdf = (1.0 - bg) * cdf_exp + bg * u / width
        low_mask = cdf < 0.5
        lo[low_mask] = mid[low_mask]
        hi[~low_mask] = mid[~low_mask]
    return (lo + hi) / 2.0


def permutation_test(rows: list[dict], ordinary: TimingModel, candidate: TimingModel, observed: float, seed: int, draws: int = 2_000) -> dict:
    y = np.asarray([r["delay_us"] for r in rows], float)
    run_idx = {
        name: np.asarray([i for i, r in enumerate(rows) if r["file"] == name], int)
        for name in sorted({r["file"] for r in rows})
    }
    rng = np.random.default_rng(seed)
    deltas = np.empty(draws)
    for j in range(draws):
        yp = y.copy()
        for idx in run_idx.values():
            yp[idx] = rng.permutation(yp[idx])
        deltas[j] = float((ordinary.losses(rows, yp) - candidate.losses(rows, yp)).mean())
    return {
        "draws": draws,
        "mean": float(deltas.mean()),
        "ci95": [float(np.quantile(deltas, 0.025)), float(np.quantile(deltas, 0.975))],
        "p_upper_add_one": float((1 + np.sum(deltas >= observed)) / (draws + 1)),
    }


def event_rows(hold: list[dict], models: dict[str, TimingModel]) -> list[dict]:
    rates = {name: model.rate(hold) for name, model in models.items()}
    medians = {name: mixture_median(rates[name], models[name].background_fraction()) for name in models}
    out = []
    for i, row in enumerate(hold):
        out.append(
            {
                "file": row["file"],
                "event_index": row["event_index"],
                "x_mu": row["x_mu"],
                "actual_daughter_delay_us": row["delay_us"],
                "in_pure_0p75_band": abs(row["x_mu"] - 0.75) <= HALF_WIDTH,
                "in_observed_0p706_band": abs(row["x_mu"] - CENTRES[SECONDARY]) <= HALF_WIDTH,
                "ordinary_rate_per_us": float(rates["MG"][i]),
                "pure_band_rate_per_us": float(rates[PRIMARY][i]),
                "observed_band_rate_per_us": float(rates[SECONDARY][i]),
                "ordinary_predicted_median_us": float(medians["MG"][i]),
                "pure_band_predicted_median_us": float(medians[PRIMARY][i]),
                "observed_band_predicted_median_us": float(medians[SECONDARY][i]),
            }
        )
    return out


def make_figure(hold: list[dict], event_table: list[dict], results: dict) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10.5), constrained_layout=True)
    blue, gold, pink, ink, grey = "#4c83c3", "#d79a2b", "#b05c96", "#27313d", "#9aa5b1"

    ax = axes[0, 0]
    step = max(1, len(hold) // 1200)
    sampled = hold[::step]
    ax.scatter([r["x_mu"] for r in sampled], [r["delay_us"] for r in sampled], s=9, alpha=0.20, color=blue, edgecolors="none")
    ax.axvspan(0.70, 0.80, color=gold, alpha=0.14, label="pure 0.75±0.05")
    ax.axvline(CENTRES[SECONDARY], color=pink, ls="--", lw=1.8, label="observed child 0.7063")
    ax.set(xlim=(0, 2), ylim=(LOWER, UPPER), xlabel="incoming individual-muon ARA x_mu", ylabel="same event's daughter delay (µs)", title="Individual held-out muons and later daughter timing")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[0, 1]
    names = list(CENTRES)
    labels = [f"{CENTRES[n]:.3f}" for n in names]
    means = [results["models"][n]["bootstrap"]["mean"] for n in names]
    low = [means[i] - results["models"][n]["bootstrap"]["ci95"][0] for i, n in enumerate(names)]
    high = [results["models"][n]["bootstrap"]["ci95"][1] - means[i] for i, n in enumerate(names)]
    colors = [gold if n == PRIMARY else pink if n == SECONDARY else grey for n in names]
    ax.bar(labels, means, color=colors, edgecolor="white")
    ax.errorbar(labels, means, yerr=[low, high], fmt="none", ecolor=ink, capsize=3, lw=1)
    ax.axhline(0, color=ink, lw=1)
    ax.set(xlabel="candidate ARA band centre (±0.05)", ylabel="held-out NLL improvement over ordinary", title="Only positive values improve individual timing prediction")

    ax = axes[1, 0]
    edges = np.linspace(0, 2, 21)
    mids = (edges[:-1] + edges[1:]) / 2
    x = np.asarray([r["x_mu"] for r in hold])
    y = np.asarray([r["delay_us"] for r in hold])
    med, counts = [], []
    for left, right in zip(edges[:-1], edges[1:]):
        mask = (x >= left) & (x < right)
        med.append(float(np.median(y[mask])) if mask.any() else np.nan)
        counts.append(int(mask.sum()))
    ax.plot(mids, med, color=blue, marker="o", markersize=4, lw=1.5)
    ax.axvline(0.75, color=gold, ls=":", lw=2)
    ax.axvline(CENTRES[SECONDARY], color=pink, ls="--", lw=1.5)
    for xm, ym, n in zip(mids, med, counts):
        if np.isfinite(ym) and n >= 10:
            ax.text(xm, ym + 0.13, str(n), ha="center", fontsize=7, color=ink)
    ax.set(xlim=(0, 2), ylim=(0.3, 5.5), xlabel="incoming individual-muon ARA x_mu", ylabel="held-out median daughter delay (µs)", title="Median individual handover time by incoming ARA (labels are n)")

    ax = axes[1, 1]
    pure = [r for r in event_table if r["in_pure_0p75_band"]]
    outside = [r for r in event_table if not r["in_pure_0p75_band"]]
    key = lambda r: (r["file"], r["event_index"])
    examples = sorted(pure, key=key)[:6] + sorted(outside, key=key)[:6]
    yy = np.arange(len(examples))
    actual = [r["actual_daughter_delay_us"] for r in examples]
    pred = [r["pure_band_predicted_median_us"] for r in examples]
    ax.hlines(yy, np.minimum(actual, pred), np.maximum(actual, pred), color=grey, lw=1)
    ax.scatter(actual, yy, color=blue, s=45, label="observed daughter delay")
    ax.scatter(pred, yy, facecolor="white", edgecolor=gold, s=55, linewidth=1.5, label="model median")
    ax.set_yticks(yy, [f"{r['file'][-6:]} #{r['event_index']}" for r in examples], fontsize=8)
    ax.invert_yaxis()
    ax.set(xlim=(0, 10), xlabel="microseconds after incoming muon", ylabel="fixed-rule individual event", title="Twelve named individual events: distributional, not exact timing")
    ax.legend(frameon=False, fontsize=8)

    fig.suptitle("T407 — grandchild landmark transfer to individual stopped-muon events", fontsize=18, fontweight="bold")
    fig.savefig(OUT / "T407_INDIVIDUAL_MUON_GRANDCHILD_TRANSFER.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    cal = [r for r in rows if r["split"] == "calibration"]
    hold = [r for r in rows if r["split"] == "holdout"]
    if (len(cal), len(hold)) != (2396, 2109):
        raise RuntimeError(f"Unexpected T379 rows: calibration={len(cal)}, holdout={len(hold)}")

    models = {"MG": TimingModel(None).fit(cal)}
    for name, centre in CENTRES.items():
        models[name] = TimingModel(centre).fit(cal)
    ordinary_loss = models["MG"].losses(hold)

    model_results = {}
    for j, (name, centre) in enumerate(CENTRES.items()):
        loss = models[name].losses(hold)
        delta = ordinary_loss - loss
        boot = block_bootstrap(hold, delta, seed=407 + j)
        by_run = {}
        for filename in sorted({r["file"] for r in hold}):
            idx = np.asarray([i for i, r in enumerate(hold) if r["file"] == filename], int)
            by_run[filename] = {"n": int(len(idx)), "nll_improvement": float(delta[idx].mean())}
        band_mask = np.asarray([abs(r["x_mu"] - centre) <= HALF_WIDTH for r in hold])
        perm = permutation_test(hold, models["MG"], models[name], boot["mean"], seed=1407 + j)
        coefficient = models[name].band_coefficient()
        gates = {
            "G1_calibration_higher_hazard": bool(coefficient is not None and coefficient > 0),
            "G2_both_holdout_runs_positive": bool(all(v["nll_improvement"] > 0 for v in by_run.values())),
            "G3_bootstrap_ci_strictly_positive": bool(boot["ci95"][0] > 0),
            "G4_permutation_p_at_most_0p05": bool(perm["p_upper_add_one"] <= 0.05),
        }
        model_results[name] = {
            "centre": centre,
            "half_width": HALF_WIDTH,
            "calibration_standardised_log_hazard_coefficient": coefficient,
            "calibration_higher_hazard": gates["G1_calibration_higher_hazard"],
            "holdout_band_n": int(band_mask.sum()),
            "holdout_band_mean_delay_us": float(np.mean([r["delay_us"] for i, r in enumerate(hold) if band_mask[i]])),
            "holdout_band_median_delay_us": float(np.median([r["delay_us"] for i, r in enumerate(hold) if band_mask[i]])),
            "mean_nll": float(loss.mean()),
            "bootstrap": boot,
            "by_run": by_run,
            "permutation": perm,
            "gates": gates,
            "supported": bool(gates["G1_calibration_higher_hazard"] and gates["G2_both_holdout_runs_positive"] and gates["G3_bootstrap_ci_strictly_positive"]),
        }

    event_table = event_rows(hold, models)
    primary_supported = model_results[PRIMARY]["supported"]
    secondary_supported = model_results[SECONDARY]["supported"]
    if primary_supported:
        verdict = "PURE 0.75 BAND TRANSFERS TO INDIVIDUAL TIMING"
    elif secondary_supported:
        verdict = "ONLY THE OBSERVED 0.706 CHILD BAND TRANSFERS"
    else:
        verdict = "GRANDCHILD BAND TRANSFER NOT SUPPORTED"
    results = {
        "test": "T407 individual-muon grandchild transfer",
        "date": "2026-08-18",
        "protocol_sha256": sha256(PROTOCOL),
        "source_sha256": sha256(SOURCE),
        "verdict": verdict,
        "n_calibration": len(cal),
        "n_holdout": len(hold),
        "ordinary_mean_nll": float(ordinary_loss.mean()),
        "primary_model": PRIMARY,
        "secondary_model": SECONDARY,
        "models": model_results,
        "boundaries": [
            "Each row links an incoming stopped-muon candidate to one later charged-daughter pulse cluster.",
            "The archive does not directly observe either neutrino and is not spin-resolved.",
            "The T379 holdout was generated and inspected earlier in the project, so this is a frozen retrospective transfer rather than a pristine new holdout.",
            "A supported band changes an individual's timing distribution; it does not determine an exact decay timestamp.",
        ],
    }
    fields = list(event_table[0].keys())
    with (OUT / "T407_HOLDOUT_EVENT_SCORES.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(event_table)
    with (OUT / "T407_MODEL_SUMMARY.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["model", "centre", "holdout_band_n", "calibration_higher_hazard", "mean_nll", "nll_improvement", "ci95_low", "ci95_high", "permutation_p", "supported"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name, m in model_results.items():
            writer.writerow(
                {
                    "model": name,
                    "centre": m["centre"],
                    "holdout_band_n": m["holdout_band_n"],
                    "calibration_higher_hazard": m["calibration_higher_hazard"],
                    "mean_nll": m["mean_nll"],
                    "nll_improvement": m["bootstrap"]["mean"],
                    "ci95_low": m["bootstrap"]["ci95"][0],
                    "ci95_high": m["bootstrap"]["ci95"][1],
                    "permutation_p": m["permutation"]["p_upper_add_one"],
                    "supported": m["supported"],
                }
            )
    (OUT / "T407_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(hold, event_table, results)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
