from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from t394_native_pair_and_release import (
    N_TRUTH,
    SEED,
    sample_michel_x,
    sample_va_z,
    splitmix64,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "T395_information3_parent_child_lock"
OUT.mkdir(exist_ok=True)
PROTOCOL = HERE / "T395_INFORMATION3_PARENT_CHILD_LOCK_PROTOCOL_2026-08-15.md"

PARENT_CANDIDATES = [8, 16, 32, 64]
CHILD_BINS = 128
SMOOTHING = 0.5
BOOTSTRAP_SEED = 395
N_BLOCKS = 200
N_BOOT = 5000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def split_masks(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    buckets = (splitmix64(np.arange(n, dtype=np.uint64)) % np.uint64(10)).astype(int)
    return buckets <= 4, (buckets >= 5) & (buckets <= 6), buckets >= 7


def fit_conditional(
    parent: np.ndarray,
    child: np.ndarray,
    parent_bins: int,
) -> dict[str, np.ndarray | int | float]:
    counts, parent_edges, child_edges = np.histogram2d(
        parent,
        child,
        bins=[parent_bins, CHILD_BINS],
        range=[[0.0, 1.0], [0.0, 2.0]],
    )
    probs = (counts + SMOOTHING) / (
        counts.sum(axis=1, keepdims=True) + SMOOTHING * CHILD_BINS
    )
    centers = (child_edges[:-1] + child_edges[1:]) / 2.0
    means = probs @ centers
    p_lower = probs[:, centers < 1.0].sum(axis=1)
    return {
        "parent_bins": parent_bins,
        "parent_edges": parent_edges,
        "child_edges": child_edges,
        "probs": probs,
        "means": means,
        "p_lower": p_lower,
    }


def score_conditional(
    model: dict[str, np.ndarray | int | float],
    parent: np.ndarray,
    child: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    parent_edges = np.asarray(model["parent_edges"])
    child_edges = np.asarray(model["child_edges"])
    probs = np.asarray(model["probs"])
    p_idx = np.clip(np.searchsorted(parent_edges, parent, side="right") - 1, 0, len(parent_edges) - 2)
    c_idx = np.clip(np.searchsorted(child_edges, child, side="right") - 1, 0, len(child_edges) - 2)
    width = child_edges[1] - child_edges[0]
    density = probs[p_idx, c_idx] / width
    predicted_mean = np.asarray(model["means"])[p_idx]
    probability_lower = np.asarray(model["p_lower"])[p_idx]
    return -np.log(density), predicted_mean, probability_lower


def fit_unconditional(child: np.ndarray) -> dict[str, np.ndarray]:
    counts, edges = np.histogram(child, bins=CHILD_BINS, range=(0.0, 2.0))
    probs = (counts + SMOOTHING) / (counts.sum() + SMOOTHING * CHILD_BINS)
    centers = (edges[:-1] + edges[1:]) / 2.0
    return {
        "edges": edges,
        "probs": probs,
        "mean": np.array([float(probs @ centers)]),
        "p_lower": np.array([float(probs[centers < 1.0].sum())]),
    }


def score_unconditional(
    model: dict[str, np.ndarray], child: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    edges = model["edges"]
    probs = model["probs"]
    idx = np.clip(np.searchsorted(edges, child, side="right") - 1, 0, len(edges) - 2)
    width = edges[1] - edges[0]
    nll = -np.log(probs[idx] / width)
    mean = np.full_like(child, model["mean"][0])
    p_lower = np.full_like(child, model["p_lower"][0])
    return nll, mean, p_lower


def phase_space_nll(parent: np.ndarray) -> np.ndarray:
    low = 2.0 * (1.0 - parent) / (2.0 - parent)
    high = 2.0 / (2.0 - parent)
    return np.log(high - low)


def bootstrap_gain(diff: np.ndarray) -> tuple[float, float]:
    blocks = np.array_split(diff, N_BLOCKS)
    block_means = np.asarray([block.mean() for block in blocks])
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    boot = np.empty(N_BOOT)
    for i in range(N_BOOT):
        boot[i] = block_means[rng.integers(0, N_BLOCKS, N_BLOCKS)].mean()
    return tuple(float(v) for v in np.quantile(boot, [0.025, 0.975]))


def direction_brier(probability_lower: np.ndarray, child: np.ndarray) -> float:
    target = (child < 1.0).astype(float)
    return float(np.mean((probability_lower - target) ** 2))


def main() -> None:
    rng = np.random.default_rng(SEED)
    parent = sample_michel_x(rng, N_TRUTH)
    x_nue = sample_va_z(rng, parent)
    x_anumu = 2.0 - parent - x_nue
    neutral = 2.0 - parent
    child = 2.0 * x_nue / neutral
    cal, val, hold = split_masks(N_TRUTH)

    # Gate A: exact nested-coordinate composition.
    exact_nue = neutral * child / 2.0
    exact_anumu = neutral * (2.0 - child) / 2.0
    exact_errors = {
        "max_abs_nu_e_error": float(np.max(np.abs(exact_nue - x_nue))),
        "max_abs_anti_nu_mu_error": float(np.max(np.abs(exact_anumu - x_anumu))),
        "max_abs_total_closure_error": float(
            np.max(np.abs(parent + exact_nue + exact_anumu - 2.0))
        ),
    }

    validation_rows: list[dict[str, float | int]] = []
    fitted: dict[int, dict[str, np.ndarray | int | float]] = {}
    for bins in PARENT_CANDIDATES:
        model = fit_conditional(parent[cal], child[cal], bins)
        fitted[bins] = model
        nll, mean, p_lower = score_conditional(model, parent[val], child[val])
        validation_rows.append(
            {
                "parent_bins": bins,
                "mean_nll": float(nll.mean()),
                "child_mae": float(np.mean(np.abs(mean - child[val]))),
                "direction_brier": direction_brier(p_lower, child[val]),
            }
        )
    winner = int(min(validation_rows, key=lambda row: row["mean_nll"])["parent_bins"])
    model = fitted[winner]

    unconditional = fit_unconditional(child[cal])
    cond_nll, cond_mean, cond_p_lower = score_conditional(model, parent[hold], child[hold])
    unc_nll, unc_mean, unc_p_lower = score_unconditional(unconditional, child[hold])

    shuffled_rng = np.random.default_rng(BOOTSTRAP_SEED)
    shuffled_child = child[cal].copy()
    shuffled_rng.shuffle(shuffled_child)
    shuffled_model = fit_conditional(parent[cal], shuffled_child, winner)
    shuf_nll, shuf_mean, shuf_p_lower = score_conditional(
        shuffled_model, parent[hold], child[hold]
    )

    reversed_nll, _, _ = score_conditional(model, parent[hold], 2.0 - child[hold])
    ps_nll = phase_space_nll(parent[hold])

    neutral_hold = neutral[hold]
    true_nue = x_nue[hold]
    true_anumu = x_anumu[hold]
    pred_nue = neutral_hold * cond_mean / 2.0
    pred_anumu = neutral_hold * (2.0 - cond_mean) / 2.0
    unc_nue = neutral_hold * unc_mean / 2.0
    unc_anumu = neutral_hold * (2.0 - unc_mean) / 2.0
    symmetric_nue = neutral_hold / 2.0
    symmetric_anumu = neutral_hold / 2.0

    gain = unc_nll - cond_nll
    ci_low, ci_high = bootstrap_gain(gain)
    n_hold = int(hold.sum())

    models = {
        "conditional_information_lock": {
            "mean_nll": float(cond_nll.mean()),
            "child_mae": float(np.mean(np.abs(cond_mean - child[hold]))),
            "direction_brier": direction_brier(cond_p_lower, child[hold]),
            "nu_e_absolute_mae": float(np.mean(np.abs(pred_nue - true_nue))),
            "anti_nu_mu_absolute_mae": float(np.mean(np.abs(pred_anumu - true_anumu))),
        },
        "unconditional_child": {
            "mean_nll": float(unc_nll.mean()),
            "child_mae": float(np.mean(np.abs(unc_mean - child[hold]))),
            "direction_brier": direction_brier(unc_p_lower, child[hold]),
            "nu_e_absolute_mae": float(np.mean(np.abs(unc_nue - true_nue))),
            "anti_nu_mu_absolute_mae": float(np.mean(np.abs(unc_anumu - true_anumu))),
        },
        "parent_shuffled": {
            "mean_nll": float(shuf_nll.mean()),
            "child_mae": float(np.mean(np.abs(shuf_mean - child[hold]))),
            "direction_brier": direction_brier(shuf_p_lower, child[hold]),
        },
        "identity_reversed": {"mean_nll": float(reversed_nll.mean())},
        "phase_space": {"mean_nll": float(ps_nll.mean())},
        "symmetric_point": {
            "nu_e_absolute_mae": float(np.mean(np.abs(symmetric_nue - true_nue))),
            "anti_nu_mu_absolute_mae": float(
                np.mean(np.abs(symmetric_anumu - true_anumu))
            ),
        },
    }

    result = {
        "test_id": "T395-information3-parent-child-lock",
        "protocol_sha256": sha256(PROTOCOL),
        "source_class": "frozen Standard-Model V-A truth crosswalk",
        "seed": SEED,
        "n": N_TRUTH,
        "split": {
            "calibration": int(cal.sum()),
            "validation": int(val.sum()),
            "holdout": n_hold,
        },
        "coordinates": {
            "parent": "P=x_e; N=2-P",
            "child": "C=2*x_nu_e/N; anti_child=2-C",
            "composed": "x_nu_e=N*C/2; x_anti_nu_mu=N*(2-C)/2",
        },
        "gate_A_exact_composition": {
            **exact_errors,
            "pass": bool(max(exact_errors.values()) < 1e-12),
            "classification": "coordinate identity; not independent evidence",
        },
        "validation_model_selection": validation_rows,
        "selected_parent_bins": winner,
        "holdout_models": models,
        "primary_information_gain_nats_per_event": float(gain.mean()),
        "primary_gain_ci95": [ci_low, ci_high],
        "primary_gate_pass": bool(ci_low > 0.0),
        "claim_boundary": (
            "A positive gate is a parent-to-child statistical lock in the frozen "
            "truth model. It is not direct neutrino observation or individual "
            "pre-decay timing."
        ),
    }

    (OUT / "T395_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    with (OUT / "T395_VALIDATION_GRID.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validation_rows[0]))
        writer.writeheader()
        writer.writerows(validation_rows)

    # Parent-bin curve and holdout reconstruction sample for reproducibility.
    p_edges = np.asarray(model["parent_edges"])
    p_centers = (p_edges[:-1] + p_edges[1:]) / 2.0
    with (OUT / "T395_PARENT_CHILD_CURVE.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["parent_x_e", "predicted_child_y_nu_e", "predicted_probability_y_nu_e_lt_1"])
        for row in zip(p_centers, np.asarray(model["means"]), np.asarray(model["p_lower"])):
            writer.writerow(row)

    sample_positions = np.linspace(0, n_hold - 1, 20000, dtype=int)
    hold_indices = np.flatnonzero(hold)[sample_positions]
    with (OUT / "T395_HOLDOUT_SAMPLE.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "parent_x_e",
            "true_child_y_nu_e",
            "predicted_child_y_nu_e",
            "true_x_nu_e",
            "predicted_x_nu_e",
            "true_x_anti_nu_mu",
            "predicted_x_anti_nu_mu",
        ])
        for idx, pos in zip(hold_indices, sample_positions):
            writer.writerow([
                parent[idx],
                child[idx],
                cond_mean[pos],
                x_nue[idx],
                pred_nue[pos],
                x_anumu[idx],
                pred_anumu[pos],
            ])

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
