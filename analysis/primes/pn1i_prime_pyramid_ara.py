"""PN1I opened-rung prime-gate, pyramid and plain-ARA development tests.

This script is hard-limited to generated wheels through prime 23. Prime 29 is
used only through saved PN1F/PN1G aggregate outputs. The sealed prime-31 target
is never generated or inspected.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pn1_sieve_rung_test import generate_wheel


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1I_PRIME_PYRAMID_ARA_DEVELOPMENT_PROTOCOL.md"
RESULTS = HERE / "PN1I_RESULTS.json"
GATE_CSV = HERE / "PN1I_GATE_METRICS.csv"
LOCK_CSV = HERE / "PN1I_LOCK_MODEL_SCORES.csv"
LOCK_SUMMARY_CSV = HERE / "PN1I_LOCK_SUMMARY.csv"
BASE_CSV = HERE / "PN1I_BASE_ARA_CROSSWALK.csv"
MATRICES = HERE / "PN1I_MATRICES.npz"
GATE_FIGURE = HERE / "PN1I_PRIME_GATE_ARA_FIGURE.png"
LOCK_FIGURE = HERE / "PN1I_PYRAMID_LOCK_FIGURE.png"

PROTOCOL_SHA256 = "B713DAB0803545F201F2C712303E1C5E11BABC4538740381421AFF1BCBBE9F5C"
ALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23)
TRANSITION_PRIMES = (7, 11, 13, 17, 19, 23)
MAX_GENERATED_PRIME = 23
ARA_BINS = 12
FOLDS = 8
SMOOTHING = 0.5
ORDER_NULLS = 32
LOCK_NULLS = 16
SEED = 20260717

INK = "#17212b"
BLUE = "#2878B5"
BLUE_LIGHT = "#A9CBE5"
GOLD = "#D5A021"
ORANGE = "#E67E22"
OLIVE = "#6B7D32"
GREY = "#89939D"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def array_hash(*arrays: np.ndarray) -> str:
    digest = hashlib.sha256()
    for values in arrays:
        data = np.ascontiguousarray(values)
        digest.update(str(data.dtype).encode("ascii"))
        digest.update(np.asarray(data.shape, dtype=np.int64).tobytes())
        for start in range(0, len(data), 1_000_000):
            digest.update(data[start : start + 1_000_000].tobytes(order="C"))
    return digest.hexdigest().upper()


def normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    total = float(values.sum())
    if total <= 0 or np.any(values < 0) or not np.all(np.isfinite(values)):
        raise AssertionError("Invalid nonnegative count/probability array")
    return values / total


def entropy_bits(probability: np.ndarray) -> float:
    probability = normalize(probability)
    active = probability > 0
    return float(-np.sum(probability[active] * np.log2(probability[active])))


def mutual_information_bits(counts: np.ndarray) -> float:
    joint = normalize(counts)
    row = joint.sum(axis=1, keepdims=True)
    column = joint.sum(axis=0, keepdims=True)
    expected = row @ column
    active = joint > 0
    return float(np.sum(joint[active] * np.log2(joint[active] / expected[active])))


def transition_counts(sequence: np.ndarray, state_count: int) -> np.ndarray:
    sequence = np.asarray(sequence, dtype=np.int64)
    following = np.roll(sequence, -1)
    keys = sequence * state_count + following
    return np.bincount(keys, minlength=state_count * state_count).reshape(state_count, state_count)


def ara_bins(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    left_float = np.asarray(left, dtype=np.float64)
    right_float = np.asarray(right, dtype=np.float64)
    coordinate = 2.0 * right_float / (left_float + right_float)
    bins = np.minimum((coordinate * ARA_BINS / 2.0).astype(np.int64), ARA_BINS - 1)
    return coordinate, bins


def shuffled_mi(
    sequence: np.ndarray,
    state_count: int,
    count: int,
    rng: np.random.Generator,
) -> np.ndarray:
    values = np.empty(count, dtype=np.float64)
    for index in range(count):
        shuffled = rng.permutation(sequence)
        values[index] = mutual_information_bits(transition_counts(shuffled, state_count))
    return values


def spearman(values_x: np.ndarray, values_y: np.ndarray) -> float:
    rank_x = pd.Series(values_x).rank(method="average").to_numpy(dtype=np.float64)
    rank_y = pd.Series(values_y).rank(method="average").to_numpy(dtype=np.float64)
    return float(np.corrcoef(rank_x, rank_y)[0, 1])


def gate_inventory(next_prime: int) -> dict[str, np.ndarray | int | bool | str]:
    parent_primes = tuple(prime for prime in ALL_PRIMES if prime < next_prime)
    if next_prime > MAX_GENERATED_PRIME or parent_primes[-1] >= next_prime:
        raise AssertionError("PN1I generation boundary violated")
    parent = generate_wheel(parent_primes)
    residues = parent.residues.astype(np.int64, copy=False)
    parent_slots = len(residues)
    inverse = pow(parent.period % next_prime, -1, next_prime)
    excluded_lift = np.mod(-residues * inverse, next_prime).astype(np.int16)
    excluded_values = residues + excluded_lift.astype(np.int64) * parent.period
    deletion_exact = bool(np.all(excluded_values % next_prime == 0))

    left_gap = np.roll(parent.gaps, 1).astype(np.int32, copy=False)
    right_gap = parent.gaps.astype(np.int32, copy=False)
    merged_gap = (left_gap + right_gap).astype(np.int32)

    parent_index = np.arange(parent_slots, dtype=np.int64)
    excluded_rank = excluded_lift.astype(np.int64) * parent_slots + parent_index
    ordered_rank = np.sort(excluded_rank)
    rank_steps = np.diff(np.concatenate((ordered_rank, ordered_rank[:1] + next_prime * parent_slots)))
    no_adjacent_deletions = bool(np.all(rank_steps > 1))

    expected_child_slots = (next_prime - 1) * parent_slots
    return {
        "next_prime": next_prime,
        "parent_prime": parent.max_prime,
        "parent_period": parent.period,
        "parent_slots": parent_slots,
        "child_period": parent.period * next_prime,
        "child_slots": expected_child_slots,
        "base_width": next_prime - 1,
        "period_inverse_mod_prime": inverse,
        "residues": residues,
        "excluded_lift": excluded_lift,
        "excluded_values": excluded_values,
        "left_gap": left_gap,
        "right_gap": right_gap,
        "merged_gap": merged_gap,
        "deletion_exact": deletion_exact,
        "one_deletion_per_parent": len(excluded_lift) == parent_slots,
        "no_adjacent_deletions": no_adjacent_deletions,
        "event_sha256": array_hash(residues, excluded_lift, left_gap, right_gap),
    }


def gate_metrics(
    inventory: dict[str, np.ndarray | int | bool | str],
    rng: np.random.Generator,
) -> tuple[dict[str, object], dict[str, np.ndarray]]:
    next_prime = int(inventory["next_prime"])
    excluded_lift = np.asarray(inventory["excluded_lift"], dtype=np.int64)
    left_gap = np.asarray(inventory["left_gap"], dtype=np.int64)
    right_gap = np.asarray(inventory["right_gap"], dtype=np.int64)
    coordinate, coordinate_bin = ara_bins(left_gap, right_gap)

    branch_counts = np.bincount(excluded_lift, minlength=next_prime)
    branch_probability = normalize(branch_counts)
    uniform = np.full(next_prime, 1.0 / next_prime)
    branch_tv = 0.5 * float(np.abs(branch_probability - uniform).sum())
    branch_transition = transition_counts(excluded_lift, next_prime)
    branch_mi = mutual_information_bits(branch_transition)
    branch_null = shuffled_mi(excluded_lift, next_prime, ORDER_NULLS, rng)

    ara_hist = np.bincount(coordinate_bin, minlength=ARA_BINS)
    ara_transition = transition_counts(coordinate_bin, ARA_BINS)
    ara_mi = mutual_information_bits(ara_transition)
    ara_null = shuffled_mi(coordinate_bin, ARA_BINS, ORDER_NULLS, rng)
    ara_probability = normalize(ara_hist)
    binned_reverse_diagnostic = 0.5 * float(np.abs(ara_probability - ara_probability[::-1]).sum())
    gap_labels = np.unique(np.concatenate((left_gap, right_gap)))
    left_code = np.searchsorted(gap_labels, left_gap)
    right_code = np.searchsorted(gap_labels, right_gap)
    pair_counts = np.bincount(
        left_code * len(gap_labels) + right_code,
        minlength=len(gap_labels) ** 2,
    ).reshape(len(gap_labels), len(gap_labels))
    reflection_error = 0.5 * float(np.abs(pair_counts - pair_counts.T).sum()) / float(pair_counts.sum())
    inverse = int(inventory["period_inverse_mod_prime"])
    internal_delta = np.mod(np.diff(excluded_lift), next_prime)
    internal_expected = np.mod(-right_gap[:-1] * inverse, next_prime)
    internal_gate_step_exact = bool(np.array_equal(internal_delta, internal_expected))
    seam_raw_delta = int((excluded_lift[0] - excluded_lift[-1]) % next_prime)
    seam_expected_with_next_lift = int((-right_gap[-1] * inverse) % next_prime)
    seam_holonomy = int((seam_raw_delta - seam_expected_with_next_lift) % next_prime)
    branch_joint = normalize(branch_transition)
    branch_independent = branch_joint.sum(axis=1, keepdims=True) @ branch_joint.sum(axis=0, keepdims=True)

    tolerance = 1e-12
    row = {
        "parent_prime": int(inventory["parent_prime"]),
        "child_prime": next_prime,
        "parent_period": int(inventory["parent_period"]),
        "parent_slots": int(inventory["parent_slots"]),
        "child_period": int(inventory["child_period"]),
        "child_slots": int(inventory["child_slots"]),
        "base_width": int(inventory["base_width"]),
        "deletion_fraction": 1.0 / next_prime,
        "deletion_exact": bool(inventory["deletion_exact"]),
        "one_deletion_per_parent": bool(inventory["one_deletion_per_parent"]),
        "no_adjacent_deletions": bool(inventory["no_adjacent_deletions"]),
        "internal_gate_step_exact": internal_gate_step_exact,
        "seam_holonomy_lift_shift": seam_holonomy,
        "q_traversal_holonomy_closes": bool((next_prime * seam_holonomy) % next_prime == 0),
        "event_sha256": str(inventory["event_sha256"]),
        "gate_branch_tv_from_uniform": branch_tv,
        "gate_branch_entropy_bits": entropy_bits(branch_counts),
        "gate_branch_entropy_fraction": entropy_bits(branch_counts) / math.log2(next_prime),
        "gate_phase_transition_mi_bits": branch_mi,
        "gate_phase_shuffle_mean_mi_bits": float(branch_null.mean()),
        "gate_phase_shuffle_max_mi_bits": float(branch_null.max()),
        "gate_phase_order_exceeds_all_shuffles": bool(branch_mi > branch_null.max()),
        "gate_phase_shuffle_p_upper": float((1 + np.sum(branch_null >= branch_mi)) / (ORDER_NULLS + 1)),
        "plain_ara_mean": float(coordinate.mean()),
        "plain_ara_below_ridge_share": float(np.mean(coordinate < 1.0 - tolerance)),
        "plain_ara_at_ridge_share": float(np.mean(np.abs(coordinate - 1.0) <= tolerance)),
        "plain_ara_above_ridge_share": float(np.mean(coordinate > 1.0 + tolerance)),
        "plain_ara_mean_abs_distance_from_ridge": float(np.mean(np.abs(coordinate - 1.0))),
        "plain_ara_entropy_12_bits": entropy_bits(ara_hist),
        "plain_ara_reflection_tv": reflection_error,
        "plain_ara_binned_reverse_tv_diagnostic": binned_reverse_diagnostic,
        "plain_ara_transition_mi_bits": ara_mi,
        "plain_ara_shuffle_mean_mi_bits": float(ara_null.mean()),
        "plain_ara_shuffle_max_mi_bits": float(ara_null.max()),
        "plain_ara_order_exceeds_all_shuffles": bool(ara_mi > ara_null.max()),
        "plain_ara_shuffle_p_upper": float((1 + np.sum(ara_null >= ara_mi)) / (ORDER_NULLS + 1)),
    }
    matrices = {
        "branch_counts": branch_counts,
        "branch_transition": branch_transition,
        "branch_residual": branch_joint - branch_independent,
        "ara_hist": ara_hist,
        "ara_transition": ara_transition,
        "coordinate_bin": coordinate_bin,
    }
    return row, matrices


def encode(values: np.ndarray) -> tuple[np.ndarray, int, np.ndarray]:
    labels, inverse = np.unique(values, return_inverse=True)
    return inverse.astype(np.int64), len(labels), labels


def score_categorical(
    states: np.ndarray,
    state_count: int,
    target: np.ndarray,
    folds: np.ndarray,
) -> dict[str, object]:
    target_count = ARA_BINS
    key = folds * (state_count * target_count) + states * target_count + target
    counts = np.bincount(
        key,
        minlength=FOLDS * state_count * target_count,
    ).reshape(FOLDS, state_count, target_count)
    total = counts.sum(axis=0)
    fold_losses: list[float] = []
    fold_sizes: list[int] = []
    active_states: list[int] = []
    for fold in range(FOLDS):
        test = counts[fold].astype(np.float64)
        train = (total - counts[fold]).astype(np.float64)
        probability = (train + SMOOTHING) / (
            train.sum(axis=1, keepdims=True) + SMOOTHING * target_count
        )
        test_size = int(test.sum())
        loss = -float(np.sum(test * np.log2(probability))) / test_size
        fold_losses.append(loss)
        fold_sizes.append(test_size)
        active_states.append(int(np.sum(train.sum(axis=1) > 0)))
    mean_loss = float(np.average(fold_losses, weights=fold_sizes))
    return {
        "mean_cross_entropy_bits": mean_loss,
        "fold_cross_entropy_bits": fold_losses,
        "mean_active_states": float(np.mean(active_states)),
        "state_count": state_count,
    }


def score_lock_models(
    inventory: dict[str, np.ndarray | int | bool | str],
    rng: np.random.Generator,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    next_prime = int(inventory["next_prime"])
    left_gap = np.asarray(inventory["left_gap"], dtype=np.int64)
    right_gap = np.asarray(inventory["right_gap"], dtype=np.int64)
    merged_gap = np.asarray(inventory["merged_gap"], dtype=np.int64)
    gate = np.asarray(inventory["excluded_lift"], dtype=np.int64)
    _, coordinate_bin = ara_bins(left_gap, right_gap)
    size = len(coordinate_bin)
    folds = np.minimum(np.arange(size, dtype=np.int64) * FOLDS // size, FOLDS - 1)

    left_code, left_states, _ = encode(left_gap)
    right_code, right_states, _ = encode(right_gap)
    merged_code, merged_states, _ = encode(merged_gap)
    pair_code = left_code * right_states + right_code
    pair_states = left_states * right_states
    pair_gate_code = pair_code * next_prime + gate
    pair_gate_states = pair_states * next_prime
    model_states = {
        "marginal": (np.zeros(size, dtype=np.int64), 1),
        "left_gap": (left_code, left_states),
        "right_gap": (right_code, right_states),
        "merged_sum": (merged_code, merged_states),
        "ordered_pair": (pair_code, pair_states),
        "gate_branch": (gate, next_prime),
        "pair_plus_gate": (pair_gate_code, pair_gate_states),
    }

    rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    for lag in (1, 2):
        target = np.roll(coordinate_bin, -lag)
        scored = {
            name: score_categorical(states, state_count, target, folds)
            for name, (states, state_count) in model_states.items()
        }
        baseline_loss = float(scored["marginal"]["mean_cross_entropy_bits"])
        baseline_folds = np.asarray(scored["marginal"]["fold_cross_entropy_bits"], dtype=np.float64)
        for name, score in scored.items():
            losses = np.asarray(score["fold_cross_entropy_bits"], dtype=np.float64)
            gains = baseline_folds - losses
            rows.append(
                {
                    "child_prime": next_prime,
                    "lag": lag,
                    "model": name,
                    "mean_cross_entropy_bits": float(score["mean_cross_entropy_bits"]),
                    "gain_vs_marginal_bits": baseline_loss - float(score["mean_cross_entropy_bits"]),
                    "min_fold_gain_vs_marginal_bits": float(gains.min()),
                    "mean_active_states": float(score["mean_active_states"]),
                    "declared_state_count": int(score["state_count"]),
                }
            )

        single_names = ("left_gap", "right_gap", "merged_sum")
        best_single_loss = min(float(scored[name]["mean_cross_entropy_bits"]) for name in single_names)
        pair_loss = float(scored["ordered_pair"]["mean_cross_entropy_bits"])
        gate_loss = float(scored["gate_branch"]["mean_cross_entropy_bits"])
        pair_gate_loss = float(scored["pair_plus_gate"]["mean_cross_entropy_bits"])
        single_fold_losses = np.stack(
            [np.asarray(scored[name]["fold_cross_entropy_bits"], dtype=np.float64) for name in single_names]
        )
        best_single_fold = single_fold_losses.min(axis=0)
        pair_fold = np.asarray(scored["ordered_pair"]["fold_cross_entropy_bits"], dtype=np.float64)
        gate_fold = np.asarray(scored["gate_branch"]["fold_cross_entropy_bits"], dtype=np.float64)
        pair_gate_fold = np.asarray(scored["pair_plus_gate"]["fold_cross_entropy_bits"], dtype=np.float64)
        pair_synergy = best_single_loss - pair_loss
        gate_increment = min(pair_loss, gate_loss) - pair_gate_loss

        summary: dict[str, object] = {
            "child_prime": next_prime,
            "lag": lag,
            "event_count": size,
            "pair_gain_beyond_best_single_bits": pair_synergy,
            "pair_min_fold_gain_beyond_best_single_bits": float((best_single_fold - pair_fold).min()),
            "gate_increment_beyond_pair_or_gate_bits": gate_increment,
            "gate_min_fold_increment_bits": float((np.minimum(pair_fold, gate_fold) - pair_gate_fold).min()),
        }

        if lag == 2:
            null_pair = np.empty(LOCK_NULLS, dtype=np.float64)
            null_gate = np.empty(LOCK_NULLS, dtype=np.float64)
            for null_index in range(LOCK_NULLS):
                null_target = rng.permutation(target)
                null_scored = {
                    name: score_categorical(*model_states[name], null_target, folds)
                    for name in (*single_names, "ordered_pair", "gate_branch", "pair_plus_gate")
                }
                null_best_single = min(
                    float(null_scored[name]["mean_cross_entropy_bits"]) for name in single_names
                )
                null_pair_loss = float(null_scored["ordered_pair"]["mean_cross_entropy_bits"])
                null_gate_loss = float(null_scored["gate_branch"]["mean_cross_entropy_bits"])
                null_pair_gate_loss = float(null_scored["pair_plus_gate"]["mean_cross_entropy_bits"])
                null_pair[null_index] = null_best_single - null_pair_loss
                null_gate[null_index] = min(null_pair_loss, null_gate_loss) - null_pair_gate_loss
            summary.update(
                {
                    "pair_null_mean_bits": float(null_pair.mean()),
                    "pair_null_max_bits": float(null_pair.max()),
                    "pair_exceeds_all_target_permutations": bool(pair_synergy > null_pair.max()),
                    "pair_null_p_upper": float((1 + np.sum(null_pair >= pair_synergy)) / (LOCK_NULLS + 1)),
                    "gate_null_mean_bits": float(null_gate.mean()),
                    "gate_null_max_bits": float(null_gate.max()),
                    "gate_exceeds_all_target_permutations": bool(gate_increment > null_gate.max()),
                    "gate_null_p_upper": float((1 + np.sum(null_gate >= gate_increment)) / (LOCK_NULLS + 1)),
                }
            )
        summaries.append(summary)
    return rows, summaries


def load_base_crosswalk(gate_frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    rung = pd.read_csv(HERE / "PN1F_RUNG_METRICS.csv")
    rung = rung[rung["rung_prime"] >= 7].copy().reset_index(drop=True)
    p29 = json.loads((HERE / "PN1G_RESULTS.json").read_text(encoding="utf-8"))
    target = p29["target_metrics"]
    rung.loc[len(rung)] = {
        "rung_prime": 29,
        "period": target["period"],
        "slot_count": target["slot_count"],
        "gap_alphabet_size": target["gap_alphabet_size"],
        "occupied_plane_cells": np.nan,
        "plane_cell_count": 144,
        "ordered_entropy_bits": target["ordered_entropy_bits"],
        "ordered_adjacent_mi_bits": target["ordered_adjacent_mi_bits"],
        "ordered_vs_gap_iid_jsd_bits": target["ordered_vs_gap_iid_jsd_bits"],
        "ordered_vs_gap_markov1_jsd_bits": target["ordered_vs_gap_markov1_jsd_bits"],
    }
    rung = rung.sort_values("rung_prime").reset_index(drop=True)
    rung["base_width"] = rung["rung_prime"] - 1

    pn1f_arrays = np.load(HERE / "PN1F_BIDIRECTIONAL_MATRICES.npz")
    residual_l2 = {
        int(prime): float(np.linalg.norm(matrix))
        for prime, matrix in zip(pn1f_arrays["core_primes"], pn1f_arrays["markov_residual_12"])
    }
    p29_arrays = np.load(HERE / "PN1G_PRIME29_COUNTS_AND_MATRICES.npz")
    residual_l2[29] = float(np.linalg.norm(p29_arrays["residual_12"]))
    rung["markov_residual_l2"] = rung["rung_prime"].map(residual_l2)

    down23 = pd.read_csv(HERE / "PN1F_DOWNWARD_MODEL_SUMMARY.csv").set_index("model")
    down29 = pd.read_csv(HERE / "PN1G_DOWNWARD_MODEL_SUMMARY.csv").set_index("model")
    visible_gain = {
        23: float(down23.loc["full_A_B", "gain_vs_current_B_bits"]),
        29: float(down29.loc["full_A_B", "gain_vs_current_B_bits"]),
    }
    shared_gain = {
        23: float(down23.loc["B_plus_shared_gap", "gain_vs_current_B_bits"]),
        29: float(down29.loc["B_plus_shared_gap", "gain_vs_current_B_bits"]),
    }
    rung["visible_full_pair_gain_bits"] = rung["rung_prime"].map(visible_gain)
    rung["shared_child_gain_bits"] = rung["rung_prime"].map(shared_gain)
    rung["below_visible_surplus_bits"] = rung["shared_child_gain_bits"] - rung["visible_full_pair_gain_bits"]

    gate_subset = gate_frame[
        [
            "child_prime",
            "gate_phase_transition_mi_bits",
            "plain_ara_transition_mi_bits",
            "plain_ara_mean_abs_distance_from_ridge",
        ]
    ]
    rung = rung.merge(gate_subset, left_on="rung_prime", right_on="child_prime", how="left")
    rung = rung.drop(columns=["child_prime"])

    core_residual = rung.dropna(subset=["markov_residual_l2"])
    summary = {
        "base_width_vs_child_adjacent_ara_mi_spearman": spearman(
            rung["base_width"].to_numpy(), rung["ordered_adjacent_mi_bits"].to_numpy()
        ),
        "child_adjacent_ara_mi_strictly_decreases": bool(
            np.all(np.diff(rung["ordered_adjacent_mi_bits"].to_numpy()) < 0)
        ),
        "base_width_vs_markov_residual_l2_spearman": spearman(
            core_residual["base_width"].to_numpy(), core_residual["markov_residual_l2"].to_numpy()
        ),
        "markov_residual_l2_strictly_decreases": bool(
            np.all(np.diff(core_residual["markov_residual_l2"].to_numpy()) < 0)
        ),
        "p23_to_p29_visible_gain_change_bits": visible_gain[29] - visible_gain[23],
        "p23_to_p29_shared_child_gain_change_bits": shared_gain[29] - shared_gain[23],
        "p23_to_p29_below_visible_change_bits": (
            shared_gain[29] - visible_gain[29]
        ) - (shared_gain[23] - visible_gain[23]),
    }
    return rung, summary


def make_gate_figure(
    gate_frame: pd.DataFrame,
    matrices_by_prime: dict[int, dict[str, np.ndarray]],
) -> None:
    primes = gate_frame["child_prime"].to_numpy(dtype=int)
    hist = np.stack([normalize(matrices_by_prime[int(prime)]["ara_hist"]) for prime in primes])
    residual = matrices_by_prime[23]["branch_residual"]
    limit = float(np.max(np.abs(residual)))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    image = axes[0, 0].imshow(residual, cmap="RdBu_r", vmin=-limit, vmax=limit, origin="lower")
    axes[0, 0].set_title("Prime-23 gate-branch transition residual")
    axes[0, 0].set_xlabel("Next excluded lift")
    axes[0, 0].set_ylabel("Current excluded lift")
    fig.colorbar(image, ax=axes[0, 0], shrink=0.78, label="Observed minus independent probability")

    image2 = axes[0, 1].imshow(hist, aspect="auto", cmap="Blues", origin="lower")
    axes[0, 1].set_title("Plain gate ARA coordinate distributions")
    axes[0, 1].set_xlabel("ARA bin on 0–2")
    axes[0, 1].set_ylabel("Child prime")
    axes[0, 1].set_yticks(np.arange(len(primes)), primes)
    axes[0, 1].set_xticks([0, 5.5, 11], ["0", "1.0 ridge", "2"])
    fig.colorbar(image2, ax=axes[0, 1], shrink=0.78, label="Event share")

    below = gate_frame["plain_ara_below_ridge_share"].to_numpy()
    ridge = gate_frame["plain_ara_at_ridge_share"].to_numpy()
    above = gate_frame["plain_ara_above_ridge_share"].to_numpy()
    axes[1, 0].bar(primes, below, color=BLUE, label="Below 1.0")
    axes[1, 0].bar(primes, ridge, bottom=below, color=GOLD, label="At 1.0")
    axes[1, 0].bar(primes, above, bottom=below + ridge, color=BLUE_LIGHT, edgecolor=BLUE, label="Above 1.0")
    axes[1, 0].set_title("Plain ARA ridge decomposition")
    axes[1, 0].set_xlabel("Child prime")
    axes[1, 0].set_ylabel("Share of gate events")
    axes[1, 0].set_xticks(primes)
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].legend(frameon=False, ncol=3, fontsize=9)

    observed = gate_frame["gate_phase_transition_mi_bits"].to_numpy()
    control = gate_frame["gate_phase_shuffle_max_mi_bits"].to_numpy()
    axes[1, 1].plot(primes, observed, color=BLUE, marker="o", linewidth=2, label="Observed order")
    axes[1, 1].plot(primes, control, color=GREY, marker="s", linestyle="--", linewidth=1.8, label="Largest shuffled control")
    axes[1, 1].set_title("Prime-gate branch transition information")
    axes[1, 1].set_xlabel("Child prime")
    axes[1, 1].set_ylabel("Mutual information (bits/event)")
    axes[1, 1].set_xticks(primes)
    axes[1, 1].legend(frameon=False)
    axes[1, 1].grid(axis="y", color="#D9DEE3", linewidth=0.7)

    fig.suptitle("PN1I prime-gate and plain-ARA opened-rung analysis", color=INK, fontsize=16)
    fig.savefig(GATE_FIGURE, dpi=180, facecolor="white")
    plt.close(fig)


def make_lock_figure(
    base_frame: pd.DataFrame,
    lock_frame: pd.DataFrame,
    lock_summary: pd.DataFrame,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)

    axes[0, 0].plot(
        base_frame["base_width"],
        base_frame["ordered_adjacent_mi_bits"],
        color=BLUE,
        marker="o",
        linewidth=2,
    )
    for _, row in base_frame.iterrows():
        axes[0, 0].annotate(f"p{int(row.rung_prime)}", (row.base_width, row.ordered_adjacent_mi_bits), xytext=(3, 4), textcoords="offset points", fontsize=8)
    axes[0, 0].set_title("Child-wheel adjacent ARA information")
    axes[0, 0].set_xlabel("Admissible base width q−1")
    axes[0, 0].set_ylabel("Mutual information (bits/event)")
    axes[0, 0].grid(axis="y", color="#D9DEE3", linewidth=0.7)

    residual = base_frame.dropna(subset=["markov_residual_l2"])
    axes[0, 1].plot(
        residual["base_width"],
        residual["markov_residual_l2"],
        color=ORANGE,
        marker="o",
        linewidth=2,
    )
    for _, row in residual.iterrows():
        axes[0, 1].annotate(f"p{int(row.rung_prime)}", (row.base_width, row.markov_residual_l2), xytext=(3, 4), textcoords="offset points", fontsize=8)
    axes[0, 1].set_title("Ordered-minus-Markov parent residual")
    axes[0, 1].set_xlabel("Admissible base width q−1")
    axes[0, 1].set_ylabel("Residual L2")
    axes[0, 1].grid(axis="y", color="#D9DEE3", linewidth=0.7)

    lag2 = lock_frame[(lock_frame["lag"] == 2) & (lock_frame["model"].isin(["left_gap", "right_gap", "merged_sum", "ordered_pair", "pair_plus_gate"]))]
    colors = {
        "left_gap": GREY,
        "right_gap": BLUE_LIGHT,
        "merged_sum": OLIVE,
        "ordered_pair": BLUE,
        "pair_plus_gate": GOLD,
    }
    for model, group in lag2.groupby("model"):
        group = group.sort_values("child_prime")
        axes[1, 0].plot(group["child_prime"], group["gain_vs_marginal_bits"], marker="o", linewidth=1.8, color=colors[model], label=model.replace("_", " "))
    axes[1, 0].set_title("Two-step ARA continuation models")
    axes[1, 0].set_xlabel("Child prime")
    axes[1, 0].set_ylabel("Held-out gain over marginal (bits/event)")
    axes[1, 0].set_xticks(sorted(lag2["child_prime"].unique()))
    axes[1, 0].grid(axis="y", color="#D9DEE3", linewidth=0.7)
    axes[1, 0].legend(frameon=False, fontsize=8, ncol=2)

    p23 = lock_summary[(lock_summary["child_prime"] == 23) & (lock_summary["lag"] == 2)].iloc[0]
    labels = ["Pair beyond\nbest single", "Gate beyond\npair or gate"]
    observed = [p23.pair_gain_beyond_best_single_bits, p23.gate_increment_beyond_pair_or_gate_bits]
    controls = [p23.pair_null_max_bits, p23.gate_null_max_bits]
    positions = np.arange(2)
    width = 0.36
    axes[1, 1].bar(positions - width / 2, observed, width, color=BLUE, label="Observed")
    axes[1, 1].bar(positions + width / 2, controls, width, color=GREY, label="Largest target permutation")
    axes[1, 1].axhline(0, color=INK, linewidth=0.8)
    axes[1, 1].set_xticks(positions, labels)
    axes[1, 1].set_title("Prime-23 two-step information-lock deltas")
    axes[1, 1].set_ylabel("Held-out cross-entropy improvement (bits/event)")
    axes[1, 1].legend(frameon=False)
    axes[1, 1].grid(axis="y", color="#D9DEE3", linewidth=0.7)

    fig.suptitle("PN1I maximum-base and double-pyramid tests", color=INK, fontsize=16)
    fig.savefig(LOCK_FIGURE, dpi=180, facecolor="white")
    plt.close(fig)


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def main() -> dict[str, object]:
    started = time.perf_counter()
    if file_hash(PROTOCOL) != PROTOCOL_SHA256:
        raise AssertionError("PN1I development protocol hash mismatch")
    if max(TRANSITION_PRIMES) != MAX_GENERATED_PRIME:
        raise AssertionError("Unexpected generation boundary")

    gate_rows: list[dict[str, object]] = []
    lock_rows: list[dict[str, object]] = []
    lock_summaries: list[dict[str, object]] = []
    matrices_by_prime: dict[int, dict[str, np.ndarray]] = {}
    exact_checks: dict[str, bool] = {}

    for next_prime in TRANSITION_PRIMES:
        print(f"PN1I opened transition into p{next_prime}")
        inventory = gate_inventory(next_prime)
        rng = np.random.default_rng(SEED + next_prime)
        gate_row, matrices = gate_metrics(inventory, rng)
        model_rows, summaries = score_lock_models(inventory, rng)
        gate_rows.append(gate_row)
        lock_rows.extend(model_rows)
        lock_summaries.extend(summaries)
        matrices_by_prime[next_prime] = matrices
        exact_checks[f"p{next_prime}_deletion_exact"] = bool(inventory["deletion_exact"])
        exact_checks[f"p{next_prime}_one_deletion_per_parent"] = bool(inventory["one_deletion_per_parent"])
        exact_checks[f"p{next_prime}_no_adjacent_deletions"] = bool(inventory["no_adjacent_deletions"])
        exact_checks[f"p{next_prime}_internal_gate_step"] = bool(gate_row["internal_gate_step_exact"])
        exact_checks[f"p{next_prime}_seam_holonomy_is_one_lift"] = int(gate_row["seam_holonomy_lift_shift"]) == 1
        exact_checks[f"p{next_prime}_slot_recurrence"] = int(inventory["child_slots"]) == (
            next_prime - 1
        ) * int(inventory["parent_slots"])

    gate_frame = pd.DataFrame(gate_rows).sort_values("child_prime")
    lock_frame = pd.DataFrame(lock_rows).sort_values(["child_prime", "lag", "mean_cross_entropy_bits"])
    lock_summary_frame = pd.DataFrame(lock_summaries).sort_values(["child_prime", "lag"])
    base_frame, base_summary = load_base_crosswalk(gate_frame)

    gate_frame.to_csv(GATE_CSV, index=False)
    lock_frame.to_csv(LOCK_CSV, index=False)
    lock_summary_frame.to_csv(LOCK_SUMMARY_CSV, index=False)
    base_frame.to_csv(BASE_CSV, index=False)

    np.savez_compressed(
        MATRICES,
        gate_primes=np.asarray(TRANSITION_PRIMES, dtype=np.int16),
        gate_ara_hist_12=np.stack([matrices_by_prime[p]["ara_hist"] for p in TRANSITION_PRIMES]),
        gate_ara_transition_12=np.stack([matrices_by_prime[p]["ara_transition"] for p in TRANSITION_PRIMES]),
        p23_gate_branch_counts=matrices_by_prime[23]["branch_counts"],
        p23_gate_branch_transition=matrices_by_prime[23]["branch_transition"],
        p23_gate_branch_residual=matrices_by_prime[23]["branch_residual"],
    )

    make_gate_figure(gate_frame, matrices_by_prime)
    make_lock_figure(base_frame, lock_frame, lock_summary_frame)

    lag2 = lock_summary_frame[lock_summary_frame["lag"] == 2]
    plain_mean_error = np.abs(gate_frame["plain_ara_mean"] - 1.0)
    parent_mi = pd.read_csv(HERE / "PN1F_RUNG_METRICS.csv").set_index("rung_prime")["ordered_adjacent_mi_bits"]
    parent_mi_error = np.asarray(
        [
            abs(float(row.plain_ara_transition_mi_bits) - float(parent_mi.loc[int(row.parent_prime)]))
            for row in gate_frame.itertuples()
        ]
    )
    result: dict[str, object] = {
        "development_id": "PN1I/DEVELOPMENT/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DEVELOPMENT COMPLETE — OPENED RUNGS ONLY",
        "protocol_sha256": PROTOCOL_SHA256,
        "maximum_generated_prime": MAX_GENERATED_PRIME,
        "prime29_use": "saved aggregate PN1F/PN1G outputs only",
        "prime31_accessed": False,
        "exact_checks": exact_checks,
        "exact_check_pass_count": int(sum(exact_checks.values())),
        "exact_check_total": len(exact_checks),
        "test_A_prime_gate_circle": {
            "ordered_beyond_all_shuffles_count": int(gate_frame["gate_phase_order_exceeds_all_shuffles"].sum()),
            "transition_count": len(gate_frame),
            "metrics": gate_frame.to_dict(orient="records"),
        },
        "test_B_maximum_base": base_summary,
        "test_C_double_pyramid_lock": {
            "lag2_pair_positive_count": int(np.sum(lag2["pair_gain_beyond_best_single_bits"] > 0)),
            "lag2_pair_all_folds_positive_count": int(np.sum(lag2["pair_min_fold_gain_beyond_best_single_bits"] > 0)),
            "lag2_pair_exceeds_null_count": int(np.sum(lag2["pair_exceeds_all_target_permutations"])),
            "lag2_gate_positive_count": int(np.sum(lag2["gate_increment_beyond_pair_or_gate_bits"] > 0)),
            "lag2_gate_all_folds_positive_count": int(np.sum(lag2["gate_min_fold_increment_bits"] > 0)),
            "lag2_gate_exceeds_null_count": int(np.sum(lag2["gate_exceeds_all_target_permutations"])),
            "transition_count": len(lag2),
            "summary": lock_summary_frame.to_dict(orient="records"),
        },
        "test_D_plain_ara": {
            "maximum_absolute_mean_error_from_ridge": float(plain_mean_error.max()),
            "maximum_reflection_tv": float(gate_frame["plain_ara_reflection_tv"].max()),
            "maximum_parent_ara_mi_identity_error": float(parent_mi_error.max()),
            "ordered_beyond_all_shuffles_count": int(gate_frame["plain_ara_order_exceeds_all_shuffles"].sum()),
            "transition_count": len(gate_frame),
        },
        "outputs": {
            "gate_metrics_csv": GATE_CSV.name,
            "lock_scores_csv": LOCK_CSV.name,
            "lock_summary_csv": LOCK_SUMMARY_CSV.name,
            "base_crosswalk_csv": BASE_CSV.name,
            "matrices_npz": MATRICES.name,
            "gate_figure": GATE_FIGURE.name,
            "lock_figure": LOCK_FIGURE.name,
        },
        "runtime_seconds": time.perf_counter() - started,
        "software": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "matplotlib": matplotlib.__version__,
        },
    }
    RESULTS.write_text(json.dumps(json_safe(result), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "exact_checks": f'{result["exact_check_pass_count"]}/{result["exact_check_total"]}',
        "gate_ordered": f'{result["test_A_prime_gate_circle"]["ordered_beyond_all_shuffles_count"]}/{len(gate_frame)}',
        "lag2_pair_positive": f'{result["test_C_double_pyramid_lock"]["lag2_pair_positive_count"]}/{len(lag2)}',
        "lag2_gate_positive": f'{result["test_C_double_pyramid_lock"]["lag2_gate_positive_count"]}/{len(lag2)}',
        "plain_ara_ordered": f'{result["test_D_plain_ara"]["ordered_beyond_all_shuffles_count"]}/{len(gate_frame)}',
        "runtime_seconds": result["runtime_seconds"],
    }, indent=2))
    return result


if __name__ == "__main__":
    main()
