"""Independent replay validator for PN1G's saved aggregate inventories."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1G_PRIME29_TRANSFER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "FC568F2D1913F163A81146A089F0D1F42981F7E9EFB5FAFBA5C097D92387732B"
RESULT_PATH = HERE / "PN1G_RESULTS.json"
ARRAY_PATH = HERE / "PN1G_PRIME29_COUNTS_AND_MATRICES.npz"
PN1F_PATH = HERE / "PN1F_BIDIRECTIONAL_MATRICES.npz"

PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
PERIOD = math.prod(PRIMES)
SLOTS = math.prod(prime - 1 for prime in PRIMES)
FIRST_RUN_P29_GAP_SHA256 = "92646B2A27C0836D0D99B49B83C3982FC9FE604E3A9780F2DC8FDDBB99DF8A2C"
BINS = 12
HIGH_BINS = 24
FOLDS = 8
ALPHA = 0.5
MAX_GAP = 256
EXPECTED_ORDER = (
    "B_plus_shared_gap",
    "raw_gap_markov1",
    "full_A_B",
    "B_plus_signed_step",
    "B_plus_distance",
    "B_plus_direction",
    "current_B",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    return values / values.sum()


def coordinate_bin(left: int, right: int, bins: int) -> int:
    return min((right * bins) // (left + right), bins - 1)


def projected_planes(
    labels: np.ndarray,
    marginal_counts: np.ndarray,
    transition_counts: np.ndarray,
    bins: int,
) -> tuple[np.ndarray, np.ndarray]:
    marginal = marginal_counts.astype(np.float64) / marginal_counts.sum()
    transition = transition_counts.astype(np.float64)
    transition /= transition.sum(axis=1, keepdims=True)
    iid = np.zeros((bins, bins), dtype=np.float64)
    markov = np.zeros((bins, bins), dtype=np.float64)
    for ia in range(len(labels)):
        for ib in range(len(labels)):
            first_bin = coordinate_bin(int(labels[ia]), int(labels[ib]), bins)
            for ic in range(len(labels)):
                second_bin = coordinate_bin(int(labels[ib]), int(labels[ic]), bins)
                iid[first_bin, second_bin] += marginal[ia] * marginal[ib] * marginal[ic]
                markov[first_bin, second_bin] += (
                    marginal[ia] * transition[ia, ib] * transition[ib, ic]
                )
    return normalize(iid), normalize(markov)


def cosine(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.sum(first * second) / (np.linalg.norm(first) * np.linalg.norm(second)))


def categorical_score(train: np.ndarray, test: np.ndarray) -> dict[str, float | int]:
    probability = (train.astype(np.float64) + ALPHA) / (
        train.sum(axis=1, keepdims=True) + ALPHA * BINS
    )
    events = int(test.sum())
    active = test > 0
    ce = float(-np.sum(test[active] * np.log2(probability[active])) / events)
    predicted = np.argmax(probability, axis=1)
    top1 = float(test[np.arange(len(predicted)), predicted].sum() / events)
    square = np.sum(probability**2, axis=1)
    brier = 0.0
    for target in range(BINS):
        brier += float(
            np.sum(test[:, target] * (square - 2 * probability[:, target] + 1))
        )
    rows = int(np.count_nonzero(train.sum(axis=1)))
    return {
        "cross_entropy_bits": ce,
        "perplexity": 2**ce,
        "top1_accuracy": top1,
        "brier_score": brier / events,
        "test_events": events,
        "active_context_rows": rows,
        "active_conditional_df": rows * (BINS - 1),
    }


def raw_score(
    train: np.ndarray,
    test_target: np.ndarray,
    labels: np.ndarray,
) -> dict[str, float | int]:
    probability_gap = (train.astype(np.float64) + ALPHA) / (
        train.sum(axis=1, keepdims=True) + ALPHA * len(labels)
    )
    probability_target = np.zeros((len(labels), BINS), dtype=np.float64)
    for current, left in enumerate(labels):
        for following, right in enumerate(labels):
            target = coordinate_bin(int(left), int(right), BINS)
            probability_target[current, target] += probability_gap[current, following]
    events = int(test_target.sum())
    active = test_target > 0
    ce = float(
        -np.sum(test_target[active] * np.log2(probability_target[active])) / events
    )
    predicted = np.argmax(probability_target, axis=1)
    top1 = float(
        test_target[np.arange(len(predicted)), predicted].sum() / events
    )
    square = np.sum(probability_target**2, axis=1)
    brier = 0.0
    for target in range(BINS):
        brier += float(
            np.sum(
                test_target[:, target]
                * (square - 2 * probability_target[:, target] + 1)
            )
        )
    rows = int(np.count_nonzero(train.sum(axis=1)))
    return {
        "cross_entropy_bits": ce,
        "perplexity": 2**ce,
        "top1_accuracy": top1,
        "brier_score": brier / events,
        "test_events": events,
        "active_context_rows": rows,
        "active_conditional_df": rows * (len(labels) - 1),
    }


def independent_downward(arrays: np.lib.npyio.NpzFile) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    model_names = tuple(
        key.split("__", 1)[1]
        for key in arrays.files
        if key.startswith("fold_model__")
    )
    for model in model_names:
        folds = arrays[f"fold_model__{model}"]
        guards = arrays[f"guard_model__{model}"]
        global_counts = folds.sum(axis=0)
        for fold in range(FOLDS):
            train = global_counts - folds[fold] - guards[fold]
            if np.any(train < 0):
                raise AssertionError("Negative saved categorical training count")
            rows.append(
                {
                    "fold": fold + 1,
                    "model": model,
                    **categorical_score(train, folds[fold]),
                }
            )

    labels = arrays["gap_labels"].astype(np.int64)
    transitions = arrays["fold_raw_transition_full"]
    guards = arrays["guard_raw_transition_full"]
    targets = arrays["fold_raw_target_full"]
    global_transition = transitions.sum(axis=0)
    for fold in range(FOLDS):
        train_full = global_transition - transitions[fold] - guards[fold]
        train = train_full[np.ix_(labels, labels)]
        test = targets[fold, labels, :]
        rows.append(
            {
                "fold": fold + 1,
                "model": "raw_gap_markov1",
                **raw_score(train, test, labels),
            }
        )
    scores = pd.DataFrame(rows).sort_values(["fold", "model"]).reset_index(drop=True)
    base = scores[scores.model == "current_B"].set_index("fold")["cross_entropy_bits"]
    summaries: list[dict[str, object]] = []
    for model, group in scores.groupby("model", sort=False):
        group = group.sort_values("fold")
        mean_ce = float(group.cross_entropy_bits.mean())
        gains = base.loc[group.fold].to_numpy() - group.cross_entropy_bits.to_numpy()
        summaries.append(
            {
                "model": model,
                "mean_cross_entropy_bits": mean_ce,
                "gain_vs_current_B_bits": float(base.mean() - mean_ce),
                "min_fold_gain_vs_current_B_bits": float(gains.min()),
            }
        )
    summary = pd.DataFrame(summaries).sort_values("mean_cross_entropy_bits").reset_index(drop=True)
    return scores, summary


def main() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    arrays = np.load(ARRAY_PATH)
    pn1f = np.load(PN1F_PATH)
    labels = arrays["gap_labels"].astype(np.int64)
    gap_counts = arrays["gap_counts"].astype(np.int64)
    transition_counts = arrays["gap_transition_counts"].astype(np.int64)
    ordered12_counts = arrays["ordered_12_counts"].astype(np.int64)
    ordered24_counts = arrays["ordered_24_counts"].astype(np.int64)

    arithmetic_checks = {
        "protocol_hash": sha256(PROTOCOL) == PROTOCOL_SHA256,
        "primorial": PERIOD == 6_469_693_230,
        "totient": SLOTS == 1_021_870_080,
        "marginal_count": int(gap_counts.sum()) == SLOTS,
        "weighted_gap_sum": int(np.sum(labels * gap_counts)) == PERIOD,
        "transition_count": int(transition_counts.sum()) == SLOTS,
        "transition_rows_match_marginal": bool(np.array_equal(transition_counts.sum(axis=1), gap_counts)),
        "transition_columns_match_marginal": bool(np.array_equal(transition_counts.sum(axis=0), gap_counts)),
        "ordered12_count": int(ordered12_counts.sum()) == SLOTS,
        "ordered24_count": int(ordered24_counts.sum()) == SLOTS,
        "labels_positive_even": bool(np.all(labels > 0) and np.all(labels % 2 == 0)),
        "gap_hash_matches_first_exhaustive_run": str(result["target_metrics"]["gap_sha256"]) == FIRST_RUN_P29_GAP_SHA256,
    }

    ordered12 = normalize(ordered12_counts)
    ordered24 = normalize(ordered24_counts)
    iid12, markov12 = projected_planes(labels, gap_counts, transition_counts, BINS)
    iid24, markov24 = projected_planes(labels, gap_counts, transition_counts, HIGH_BINS)
    residual12 = ordered12 - markov12
    residual24 = ordered24 - markov24
    core = pn1f["core_primes"]
    p23_index = int(np.where(core == 23)[0][0])
    p23_residual12 = pn1f["markov_residual_12"][p23_index]
    p23_residual24 = pn1f["markov_residual_24"][-1]
    deformation12 = residual12 - p23_residual12
    deformation24 = residual24 - p23_residual24
    prior12 = pn1f["deformation_12"][-1]
    prior24 = pn1f["markov_residual_24"][-1] - pn1f["markov_residual_24"][-2]
    stack12 = np.concatenate((pn1f["deformation_12"], deformation12[None]), axis=0)
    s12 = np.linalg.svd(stack12.reshape(len(stack12), -1), compute_uv=False)
    e12 = s12**2 / np.sum(s12**2)
    stack24 = np.concatenate((np.diff(pn1f["markov_residual_24"], axis=0), deformation24[None]), axis=0)
    s24 = np.linalg.svd(stack24.reshape(len(stack24), -1), compute_uv=False)
    e24 = s24**2 / np.sum(s24**2)

    recomputed = {
        "residual_cosine": cosine(p23_residual12, residual12),
        "p23_residual_l2": float(np.linalg.norm(p23_residual12)),
        "p29_residual_l2": float(np.linalg.norm(residual12)),
        "deformation_l2": float(np.linalg.norm(deformation12)),
        "deformation_cosine": cosine(prior12, deformation12),
        "leading_mode_energy": float(e12[0]),
        "residual_cosine_24": cosine(p23_residual24, residual24),
        "deformation_cosine_24": cosine(prior24, deformation24),
        "leading_mode_energy_24": float(e24[0]),
    }
    upward_checks = {
        "saved_ordered12": bool(np.allclose(ordered12, arrays["ordered_12"], atol=1e-15, rtol=0)),
        "saved_ordered24": bool(np.allclose(ordered24, arrays["ordered_24"], atol=1e-15, rtol=0)),
        "saved_iid12": bool(np.allclose(iid12, arrays["gap_iid_12"], atol=1e-15, rtol=0)),
        "saved_markov12": bool(np.allclose(markov12, arrays["gap_markov1_12"], atol=1e-15, rtol=0)),
        "saved_iid24": bool(np.allclose(iid24, arrays["gap_iid_24"], atol=1e-15, rtol=0)),
        "saved_markov24": bool(np.allclose(markov24, arrays["gap_markov1_24"], atol=1e-15, rtol=0)),
        "saved_residual12": bool(np.allclose(residual12, arrays["residual_12"], atol=1e-15, rtol=0)),
        "saved_deformation12": bool(np.allclose(deformation12, arrays["deformation_12"], atol=1e-15, rtol=0)),
        "residuals_zero_sum": abs(float(residual12.sum())) < 1e-12 and abs(float(residual24.sum())) < 1e-12,
        "U1": recomputed["residual_cosine"] >= 0.98,
        "U2": 0 < recomputed["p29_residual_l2"] < recomputed["p23_residual_l2"],
        "U3": recomputed["deformation_cosine"] >= 0.98,
        "U4": recomputed["leading_mode_energy"] >= 0.95,
        "headline_metrics_match": all(
            abs(float(result["upward_transfer"][key]) - value) < 1e-12
            for key, value in recomputed.items()
        ),
    }

    saved_scores = pd.read_csv(HERE / "PN1G_DOWNWARD_FOLD_SCORES.csv").sort_values(["fold", "model"]).reset_index(drop=True)
    replay_scores, replay_summary = independent_downward(arrays)
    metric_columns = (
        "cross_entropy_bits",
        "perplexity",
        "top1_accuracy",
        "brier_score",
        "test_events",
        "active_context_rows",
        "active_conditional_df",
    )
    downward_checks = {
        "model_fold_rows_match": bool(np.array_equal(saved_scores[["fold", "model"]].to_numpy(), replay_scores[["fold", "model"]].to_numpy())),
        "all_fold_metrics_match": all(
            np.allclose(saved_scores[column], replay_scores[column], atol=1e-12, rtol=0)
            for column in metric_columns
        ),
        "exact_order": replay_summary.model.tolist() == list(EXPECTED_ORDER),
        "all_nonbase_positive_each_fold": all(
            float(replay_summary.loc[replay_summary.model == model, "min_fold_gain_vs_current_B_bits"].iloc[0]) > 0
            for model in EXPECTED_ORDER[:-1]
        ),
        "each_model_has_slot_total": all(
            int(arrays[f"fold_model__{model}"].sum()) == SLOTS
            for model in EXPECTED_ORDER if model != "raw_gap_markov1"
        ),
        "each_guard_has_eight_events": all(
            np.all(arrays[f"guard_model__{model}"].sum(axis=(1, 2)) == 8)
            for model in EXPECTED_ORDER if model != "raw_gap_markov1"
        ),
        "raw_fold_total": int(arrays["fold_raw_transition_full"].sum()) == SLOTS,
        "raw_target_total": int(arrays["fold_raw_target_full"].sum()) == SLOTS,
        "raw_guards_eight_each": bool(np.all(arrays["guard_raw_transition_full"].sum(axis=(1, 2)) == 8)),
    }

    with Image.open(HERE / "PN1G_PRIME29_TRANSFER_FIGURE.png") as image:
        figure_size = image.size
    artifact_checks = {
        "figure_size": figure_size == (2100, 1400),
        "result_prime_opened": result["prime29_opened"] is True,
        "all_primary_checks_recorded_pass": result["frozen_check_pass_count"] == result["frozen_check_total"] == 6,
    }
    all_checks = {**arithmetic_checks, **upward_checks, **downward_checks, **artifact_checks}
    validation = {
        "validation_id": "PN1G/INDEPENDENT/1",
        "overall": "PASS" if all(all_checks.values()) else "FAIL",
        "arithmetic_checks": arithmetic_checks,
        "upward_checks": upward_checks,
        "downward_checks": downward_checks,
        "artifact_checks": artifact_checks,
        "recomputed_upward_metrics": recomputed,
        "recomputed_downward_order": replay_summary.model.tolist(),
        "check_count": len(all_checks),
        "passed_check_count": int(sum(bool(value) for value in all_checks.values())),
    }
    (HERE / "PN1G_INDEPENDENT_VALIDATION.json").write_text(
        json.dumps(validation, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, indent=2, allow_nan=False))
    if validation["overall"] != "PASS":
        raise AssertionError("PN1G independent validation failed")
    return validation


if __name__ == "__main__":
    main()
