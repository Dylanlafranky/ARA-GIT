"""PN1F development landscape: upward across opened sieve rungs, then down into p23.

Prime 29 is a protected target.  This module's explicit maximum sieve prime is 23.
See PN1F_BIDIRECTIONAL_LANDSCAPE_DEVELOPMENT_PROTOCOL.md.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from pn1_sieve_rung_test import generate_wheel
from pn1c_independent_validator import child_gap_cycle


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1F_BIDIRECTIONAL_LANDSCAPE_DEVELOPMENT_PROTOCOL.md"
PROTOCOL_SHA256 = "4ABCCB50E62780E41D9FF48455C1DC413926B9E5E527654E2B4F7108CAF004D7"

# This tuple is the executable contamination guard.  Do not add a later prime
# until a separately frozen transfer protocol explicitly opens it.
ALL_OPEN_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23)
DISPLAY_RUNGS = (5, 7, 11, 13, 17, 19, 23)
CORE_RUNGS = (11, 13, 17, 19, 23)
HIGH_RES_RUNGS = (13, 17, 19, 23)
MAX_ALLOWED_PRIME = 23

PLANE_BINS = 12
HIGH_RES_BINS = 24
DOWN_BINS = 12
DOWN_FOLDS = 8
GUARD_EVENTS = 4
ALPHA = 0.5
CHUNK = 1_000_000

EXPECTED_P23_PERIOD = 223_092_870
EXPECTED_P23_SLOTS = 36_495_360
EXPECTED_P23_GAP_SHA256 = "F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def array_hash(values: np.ndarray) -> str:
    digest = hashlib.sha256()
    for start in range(0, len(values), CHUNK):
        digest.update(values[start : start + CHUNK].tobytes(order="C"))
    return digest.hexdigest().upper()


def normalize(values: np.ndarray) -> np.ndarray:
    output = np.asarray(values, dtype=np.float64)
    total = float(output.sum())
    if total <= 0 or not np.all(np.isfinite(output)) or np.any(output < 0):
        raise AssertionError("Invalid probability array")
    return output / total


def relation_bin(left: np.ndarray | int, right: np.ndarray | int, bins: int) -> np.ndarray:
    left_values = np.asarray(left, dtype=np.float64)
    right_values = np.asarray(right, dtype=np.float64)
    coordinate = 2.0 * right_values / (left_values + right_values)
    return np.minimum((coordinate * bins / 2.0).astype(np.int64), bins - 1)


def relation_plane_counts(gaps: np.ndarray, bins: int) -> np.ndarray:
    counts = np.zeros((bins, bins), dtype=np.int64)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        first = np.take(gaps, index)
        second = np.take(gaps, (index + 1) % size)
        third = np.take(gaps, (index + 2) % size)
        row = relation_bin(first, second, bins)
        column = relation_bin(second, third, bins)
        counts += np.bincount(
            row * bins + column, minlength=bins * bins
        ).reshape(bins, bins)
    return counts


def relation_sequence(gaps: np.ndarray, bins: int) -> np.ndarray:
    values = np.empty(len(gaps), dtype=np.uint8)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        values[start:stop] = relation_bin(
            np.take(gaps, index), np.take(gaps, (index + 1) % size), bins
        ).astype(np.uint8)
    return values


def jsd_bits(first: np.ndarray, second: np.ndarray) -> float:
    p = normalize(first.ravel())
    q = normalize(second.ravel())
    midpoint = 0.5 * (p + q)

    def kl(values: np.ndarray) -> float:
        active = values > 0
        return float(np.sum(values[active] * np.log2(values[active] / midpoint[active])))

    return 0.5 * kl(p) + 0.5 * kl(q)


def plane_mutual_information(probability: np.ndarray) -> float:
    p = normalize(probability)
    row = p.sum(axis=1)
    column = p.sum(axis=0)
    expected = row[:, None] * column[None, :]
    active = p > 0
    return float(np.sum(p[active] * np.log2(p[active] / expected[active])))


def plane_entropy(probability: np.ndarray) -> float:
    p = normalize(probability)
    active = p > 0
    return float(-np.sum(p[active] * np.log2(p[active])))


def gap_alphabet(gaps: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    labels, counts = np.unique(gaps, return_counts=True)
    lookup = np.full(int(labels.max()) + 1, -1, dtype=np.int16)
    lookup[labels] = np.arange(len(labels), dtype=np.int16)
    return labels.astype(np.int32), counts.astype(np.int64), lookup


def gap_transition_counts(
    gaps: np.ndarray, labels: np.ndarray, lookup: np.ndarray
) -> np.ndarray:
    alphabet = len(labels)
    counts = np.zeros((alphabet, alphabet), dtype=np.int64)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        current = lookup[np.take(gaps, index)]
        following = lookup[np.take(gaps, (index + 1) % size)]
        counts += np.bincount(
            current.astype(np.int64) * alphabet + following.astype(np.int64),
            minlength=alphabet * alphabet,
        ).reshape(alphabet, alphabet)
    return counts


def projected_gap_model_planes(
    labels: np.ndarray,
    marginal_counts: np.ndarray,
    transition_counts: np.ndarray,
    bins: int,
) -> tuple[np.ndarray, np.ndarray]:
    marginal = marginal_counts.astype(np.float64) / marginal_counts.sum()
    row_totals = transition_counts.sum(axis=1, keepdims=True)
    transition = np.divide(
        transition_counts,
        row_totals,
        out=np.zeros_like(transition_counts, dtype=np.float64),
        where=row_totals > 0,
    )
    iid = np.zeros((bins, bins), dtype=np.float64)
    markov = np.zeros((bins, bins), dtype=np.float64)
    for ia, first_gap in enumerate(labels):
        if marginal[ia] == 0:
            continue
        for ib, second_gap in enumerate(labels):
            first_bin = int(relation_bin(int(first_gap), int(second_gap), bins))
            iid_ab = marginal[ia] * marginal[ib]
            markov_ab = marginal[ia] * transition[ia, ib]
            for ic, third_gap in enumerate(labels):
                second_bin = int(relation_bin(int(second_gap), int(third_gap), bins))
                iid[first_bin, second_bin] += iid_ab * marginal[ic]
                markov[first_bin, second_bin] += markov_ab * transition[ib, ic]
    return normalize(iid), normalize(markov)


def cosine(first: np.ndarray, second: np.ndarray) -> float:
    denominator = float(np.linalg.norm(first) * np.linalg.norm(second))
    return float(np.sum(first * second) / denominator) if denominator else 0.0


def generate_opened_gaps() -> tuple[dict[int, np.ndarray], dict[int, int], dict[int, int]]:
    if max(ALL_OPEN_PRIMES) != MAX_ALLOWED_PRIME or MAX_ALLOWED_PRIME != 23:
        raise RuntimeError("Protected-prime guard failed")
    gaps_by_rung: dict[int, np.ndarray] = {}
    periods: dict[int, int] = {}
    slots: dict[int, int] = {}
    parent_19 = None
    for rung in DISPLAY_RUNGS:
        primes = tuple(value for value in ALL_OPEN_PRIMES if value <= rung)
        if rung < 23:
            wheel = generate_wheel(primes)
            gaps_by_rung[rung] = wheel.gaps.copy()
            periods[rung] = int(wheel.period)
            slots[rung] = int(len(wheel.gaps))
            if rung == 19:
                parent_19 = wheel
        else:
            if parent_19 is None:
                raise AssertionError("Prime-19 parent was not generated")
            child_gaps = child_gap_cycle(parent_19.residues)
            gaps_by_rung[rung] = child_gaps
            periods[rung] = EXPECTED_P23_PERIOD
            slots[rung] = len(child_gaps)
    return gaps_by_rung, periods, slots


def upward_landscape(
    gaps_by_rung: dict[int, np.ndarray], periods: dict[int, int], slots: dict[int, int]
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, np.ndarray],
    dict[int, dict[str, np.ndarray]],
]:
    rung_rows: list[dict[str, object]] = []
    matrices_by_rung: dict[int, dict[str, np.ndarray]] = {}
    for rung in DISPLAY_RUNGS:
        gaps = gaps_by_rung[rung]
        labels, marginal_counts, lookup = gap_alphabet(gaps)
        transition_counts = gap_transition_counts(gaps, labels, lookup)
        ordered_counts = relation_plane_counts(gaps, PLANE_BINS)
        ordered = normalize(ordered_counts)
        iid, markov = projected_gap_model_planes(
            labels, marginal_counts, transition_counts, PLANE_BINS
        )
        residual = ordered - markov
        centers = (np.arange(PLANE_BINS) + 0.5) * 2.0 / PLANE_BINS
        row_grid, column_grid = np.meshgrid(centers, centers, indexing="ij")
        delta = column_grid - row_grid
        rung_rows.append(
            {
                "rung_prime": rung,
                "period": periods[rung],
                "slot_count": slots[rung],
                "gap_alphabet_size": len(labels),
                "occupied_plane_cells": int(np.count_nonzero(ordered_counts)),
                "plane_cell_count": PLANE_BINS**2,
                "ordered_entropy_bits": plane_entropy(ordered),
                "ordered_adjacent_mi_bits": plane_mutual_information(ordered),
                "ordered_vs_gap_iid_jsd_bits": jsd_bits(ordered, iid),
                "ordered_vs_gap_markov1_jsd_bits": jsd_bits(ordered, markov),
                "markov_residual_l2": float(np.linalg.norm(residual)),
                "mean_first_ara": float(np.sum(ordered * row_grid)),
                "mean_second_ara": float(np.sum(ordered * column_grid)),
                "mean_signed_child_step": float(np.sum(ordered * delta)),
                "mean_absolute_child_step": float(np.sum(ordered * np.abs(delta))),
                "rising_share": float(ordered[delta > 0].sum()),
                "equal_share": float(ordered[delta == 0].sum()),
                "falling_share": float(ordered[delta < 0].sum()),
            }
        )
        matrices_by_rung[rung] = {
            "ordered": ordered,
            "gap_iid": iid,
            "gap_markov1": markov,
            "markov_residual": residual,
        }
        if rung in HIGH_RES_RUNGS:
            high_counts = relation_plane_counts(gaps, HIGH_RES_BINS)
            high_iid, high_markov = projected_gap_model_planes(
                labels, marginal_counts, transition_counts, HIGH_RES_BINS
            )
            matrices_by_rung[rung].update(
                {
                    "ordered_24": normalize(high_counts),
                    "gap_iid_24": high_iid,
                    "gap_markov1_24": high_markov,
                    "markov_residual_24": normalize(high_counts) - high_markov,
                }
            )
        print(f"upward rung {rung} complete", flush=True)

    transition_rows: list[dict[str, object]] = []
    deformation_fields: list[np.ndarray] = []
    per_log_fields: list[np.ndarray] = []
    transition_labels: list[str] = []
    prior_deformation: np.ndarray | None = None
    for parent, child in zip(CORE_RUNGS[:-1], CORE_RUNGS[1:]):
        parent_matrix = matrices_by_rung[parent]
        child_matrix = matrices_by_rung[child]
        deformation = child_matrix["markov_residual"] - parent_matrix["markov_residual"]
        per_log = deformation / math.log(child)
        transition_fields = {
            "deformation": deformation,
            "per_log": per_log,
        }
        deformation_fields.append(deformation)
        per_log_fields.append(per_log)
        transition_labels.append(f"{parent}->{child}")
        transition_rows.append(
            {
                "transition": f"{parent}->{child}",
                "parent_prime": parent,
                "child_prime": child,
                "log_step": math.log(child),
                "ordered_plane_jsd_bits": jsd_bits(
                    parent_matrix["ordered"], child_matrix["ordered"]
                ),
                "markov_residual_cosine": cosine(
                    parent_matrix["markov_residual"], child_matrix["markov_residual"]
                ),
                "deformation_l2": float(np.linalg.norm(deformation)),
                "deformation_l1": float(np.sum(np.abs(deformation))),
                "deformation_per_log_l2": float(np.linalg.norm(per_log)),
                "cosine_with_previous_deformation": (
                    None if prior_deformation is None else cosine(prior_deformation, deformation)
                ),
                "angle_with_previous_deformation_degrees": (
                    None
                    if prior_deformation is None
                    else float(
                        np.degrees(
                            np.arccos(np.clip(cosine(prior_deformation, deformation), -1.0, 1.0))
                        )
                    )
                ),
            }
        )
        prior_deformation = transition_fields["deformation"]

    deformation_stack = np.stack([field.ravel() for field in deformation_fields])
    u, singular_values, vh = np.linalg.svd(deformation_stack, full_matrices=False)
    scores = u * singular_values[None, :]
    modes = vh.reshape(len(singular_values), PLANE_BINS, PLANE_BINS)
    for mode_index in range(len(singular_values)):
        flat = modes[mode_index].ravel()
        anchor = int(np.argmax(np.abs(flat)))
        if flat[anchor] < 0:
            modes[mode_index] *= -1
            scores[:, mode_index] *= -1
    energy = singular_values**2
    energy /= energy.sum()
    mode_rows: list[dict[str, object]] = []
    for transition_index, label in enumerate(transition_labels):
        for mode_index in range(len(singular_values)):
            mode_rows.append(
                {
                    "transition": label,
                    "mode": mode_index + 1,
                    "score": float(scores[transition_index, mode_index]),
                    "singular_value": float(singular_values[mode_index]),
                    "energy_fraction": float(energy[mode_index]),
                }
            )

    per_log_stack = np.stack([field.ravel() for field in per_log_fields])
    ul, sl, vhl = np.linalg.svd(per_log_stack, full_matrices=False)
    per_log_scores = ul * sl[None, :]
    per_log_modes = vhl.reshape(len(sl), PLANE_BINS, PLANE_BINS)
    for mode_index in range(len(sl)):
        flat = per_log_modes[mode_index].ravel()
        anchor = int(np.argmax(np.abs(flat)))
        if flat[anchor] < 0:
            per_log_modes[mode_index] *= -1
            per_log_scores[:, mode_index] *= -1

    saved = {
        "core_primes": np.asarray(CORE_RUNGS, dtype=np.int16),
        "transition_parent_primes": np.asarray(CORE_RUNGS[:-1], dtype=np.int16),
        "transition_child_primes": np.asarray(CORE_RUNGS[1:], dtype=np.int16),
        "ordered_12": np.stack([matrices_by_rung[p]["ordered"] for p in CORE_RUNGS]),
        "gap_iid_12": np.stack([matrices_by_rung[p]["gap_iid"] for p in CORE_RUNGS]),
        "gap_markov1_12": np.stack([matrices_by_rung[p]["gap_markov1"] for p in CORE_RUNGS]),
        "markov_residual_12": np.stack(
            [matrices_by_rung[p]["markov_residual"] for p in CORE_RUNGS]
        ),
        "deformation_12": np.stack(deformation_fields),
        "deformation_per_log_12": np.stack(per_log_fields),
        "deformation_modes_12": modes,
        "deformation_mode_scores": scores,
        "deformation_singular_values": singular_values,
        "deformation_energy_fractions": energy,
        "per_log_modes_12": per_log_modes,
        "per_log_mode_scores": per_log_scores,
        "per_log_singular_values": sl,
        "high_res_primes": np.asarray(HIGH_RES_RUNGS, dtype=np.int16),
        "ordered_24": np.stack([matrices_by_rung[p]["ordered_24"] for p in HIGH_RES_RUNGS]),
        "markov_residual_24": np.stack(
            [matrices_by_rung[p]["markov_residual_24"] for p in HIGH_RES_RUNGS]
        ),
    }
    return (
        pd.DataFrame(rung_rows),
        pd.DataFrame(transition_rows),
        pd.DataFrame(mode_rows),
        saved,
        matrices_by_rung,
    )


DOWN_MODEL_SPECS = {
    "current_B": DOWN_BINS,
    "B_plus_direction": DOWN_BINS * 3,
    "B_plus_distance": DOWN_BINS * 4,
    "B_plus_signed_step": DOWN_BINS * 7,
    "full_A_B": DOWN_BINS * DOWN_BINS,
}


def event_contexts(
    relation: np.ndarray,
    gaps: np.ndarray,
    indices: np.ndarray,
    gap_lookup: np.ndarray,
    gap_alphabet_size: int,
) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    size = len(relation)
    a = np.take(relation, (indices - 2) % size).astype(np.int64)
    b = np.take(relation, (indices - 1) % size).astype(np.int64)
    target = np.take(relation, indices % size).astype(np.int64)
    step = b - a
    direction = np.where(step < 0, 0, np.where(step == 0, 1, 2))
    absolute = np.abs(step)
    distance = np.where(absolute == 0, 0, np.where(absolute == 1, 1, np.where(absolute <= 3, 2, 3)))
    signed = np.where(
        step <= -4,
        0,
        np.where(
            step <= -2,
            1,
            np.where(
                step == -1,
                2,
                np.where(step == 0, 3, np.where(step == 1, 4, np.where(step <= 3, 5, 6))),
            ),
        ),
    )
    current_gap = np.take(gaps, indices % size)
    next_gap = np.take(gaps, (indices + 1) % size)
    current_gap_code = gap_lookup[current_gap].astype(np.int64)
    next_gap_code = gap_lookup[next_gap].astype(np.int64)
    contexts = {
        "current_B": b,
        "B_plus_direction": b * 3 + direction,
        "B_plus_distance": b * 4 + distance,
        "B_plus_signed_step": b * 7 + signed,
        "B_plus_shared_gap": b * gap_alphabet_size + current_gap_code,
        "full_A_B": a * DOWN_BINS + b,
    }
    return contexts, target, current_gap_code, next_gap_code


def count_event_range(
    relation: np.ndarray,
    gaps: np.ndarray,
    start: int,
    stop: int,
    gap_lookup: np.ndarray,
    gap_alphabet_size: int,
) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    model_sizes = dict(DOWN_MODEL_SPECS)
    model_sizes["B_plus_shared_gap"] = DOWN_BINS * gap_alphabet_size
    model_counts = {
        name: np.zeros((contexts, DOWN_BINS), dtype=np.int64)
        for name, contexts in model_sizes.items()
    }
    raw_transition = np.zeros((gap_alphabet_size, gap_alphabet_size), dtype=np.int64)
    raw_target = np.zeros((gap_alphabet_size, DOWN_BINS), dtype=np.int64)
    for chunk_start in range(start, stop, CHUNK):
        chunk_stop = min(chunk_start + CHUNK, stop)
        indices = np.arange(chunk_start, chunk_stop, dtype=np.int64)
        contexts, target, current_gap, next_gap = event_contexts(
            relation, gaps, indices, gap_lookup, gap_alphabet_size
        )
        for name, context in contexts.items():
            width = model_counts[name].shape[0]
            model_counts[name] += np.bincount(
                context * DOWN_BINS + target,
                minlength=width * DOWN_BINS,
            ).reshape(width, DOWN_BINS)
        raw_transition += np.bincount(
            current_gap * gap_alphabet_size + next_gap,
            minlength=gap_alphabet_size**2,
        ).reshape(gap_alphabet_size, gap_alphabet_size)
        raw_target += np.bincount(
            current_gap * DOWN_BINS + target,
            minlength=gap_alphabet_size * DOWN_BINS,
        ).reshape(gap_alphabet_size, DOWN_BINS)
    return model_counts, raw_transition, raw_target


def count_event_indices(
    relation: np.ndarray,
    gaps: np.ndarray,
    indices: np.ndarray,
    gap_lookup: np.ndarray,
    gap_alphabet_size: int,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    model_sizes = dict(DOWN_MODEL_SPECS)
    model_sizes["B_plus_shared_gap"] = DOWN_BINS * gap_alphabet_size
    contexts, target, current_gap, next_gap = event_contexts(
        relation, gaps, indices, gap_lookup, gap_alphabet_size
    )
    model_counts: dict[str, np.ndarray] = {}
    for name, context in contexts.items():
        width = model_sizes[name]
        model_counts[name] = np.bincount(
            context * DOWN_BINS + target, minlength=width * DOWN_BINS
        ).reshape(width, DOWN_BINS)
    raw_transition = np.bincount(
        current_gap * gap_alphabet_size + next_gap,
        minlength=gap_alphabet_size**2,
    ).reshape(gap_alphabet_size, gap_alphabet_size)
    return model_counts, raw_transition


def score_categorical(
    train_counts: np.ndarray, test_counts: np.ndarray
) -> dict[str, float | int]:
    probabilities = (train_counts.astype(np.float64) + ALPHA) / (
        train_counts.sum(axis=1, keepdims=True) + ALPHA * DOWN_BINS
    )
    sample_count = int(test_counts.sum())
    active = test_counts > 0
    cross_entropy = float(
        -np.sum(test_counts[active] * np.log2(probabilities[active])) / sample_count
    )
    predicted = np.argmax(probabilities, axis=1)
    top1 = float(test_counts[np.arange(len(predicted)), predicted].sum() / sample_count)
    probability_square = np.sum(probabilities**2, axis=1)
    brier_total = 0.0
    for target in range(DOWN_BINS):
        brier_total += float(
            np.sum(
                test_counts[:, target]
                * (probability_square - 2.0 * probabilities[:, target] + 1.0)
            )
        )
    active_rows = int(np.count_nonzero(train_counts.sum(axis=1)))
    return {
        "cross_entropy_bits": cross_entropy,
        "perplexity": 2.0**cross_entropy,
        "top1_accuracy": top1,
        "brier_score": brier_total / sample_count,
        "test_events": sample_count,
        "active_context_rows": active_rows,
        "active_conditional_df": active_rows * (DOWN_BINS - 1),
    }


def raw_gap_projected_probabilities(
    train_transition: np.ndarray, gap_labels: np.ndarray
) -> np.ndarray:
    alphabet = len(gap_labels)
    transition = (train_transition.astype(np.float64) + ALPHA) / (
        train_transition.sum(axis=1, keepdims=True) + ALPHA * alphabet
    )
    projected = np.zeros((alphabet, DOWN_BINS), dtype=np.float64)
    for current in range(alphabet):
        for following in range(alphabet):
            target = int(
                relation_bin(int(gap_labels[current]), int(gap_labels[following]), DOWN_BINS)
            )
            projected[current, target] += transition[current, following]
    return projected


def score_raw_gap_model(
    train_transition: np.ndarray,
    test_target_counts: np.ndarray,
    gap_labels: np.ndarray,
) -> dict[str, float | int]:
    probabilities = raw_gap_projected_probabilities(train_transition, gap_labels)
    sample_count = int(test_target_counts.sum())
    active = test_target_counts > 0
    cross_entropy = float(
        -np.sum(test_target_counts[active] * np.log2(probabilities[active])) / sample_count
    )
    predicted = np.argmax(probabilities, axis=1)
    top1 = float(
        test_target_counts[np.arange(len(predicted)), predicted].sum() / sample_count
    )
    probability_square = np.sum(probabilities**2, axis=1)
    brier_total = 0.0
    for target in range(DOWN_BINS):
        brier_total += float(
            np.sum(
                test_target_counts[:, target]
                * (probability_square - 2.0 * probabilities[:, target] + 1.0)
            )
        )
    active_rows = int(np.count_nonzero(train_transition.sum(axis=1)))
    return {
        "cross_entropy_bits": cross_entropy,
        "perplexity": 2.0**cross_entropy,
        "top1_accuracy": top1,
        "brier_score": brier_total / sample_count,
        "test_events": sample_count,
        "active_context_rows": active_rows,
        "active_conditional_df": active_rows * (len(gap_labels) - 1),
    }


def downward_decomposition(
    gaps: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    relation = relation_sequence(gaps, DOWN_BINS)
    gap_labels, _, gap_lookup = gap_alphabet(gaps)
    alphabet = len(gap_labels)
    size = len(gaps)
    boundaries = np.linspace(0, size, DOWN_FOLDS + 1, dtype=np.int64)
    fold_model_counts: list[dict[str, np.ndarray]] = []
    fold_raw_transition: list[np.ndarray] = []
    fold_raw_target: list[np.ndarray] = []
    for fold in range(DOWN_FOLDS):
        model_counts, raw_transition, raw_target = count_event_range(
            relation,
            gaps,
            int(boundaries[fold]),
            int(boundaries[fold + 1]),
            gap_lookup,
            alphabet,
        )
        fold_model_counts.append(model_counts)
        fold_raw_transition.append(raw_transition)
        fold_raw_target.append(raw_target)
        print(f"downward fold inventory {fold + 1}/{DOWN_FOLDS} complete", flush=True)

    model_names = list(fold_model_counts[0])
    global_model_counts = {
        name: sum((fold[name] for fold in fold_model_counts), start=np.zeros_like(fold_model_counts[0][name]))
        for name in model_names
    }
    global_raw_transition = sum(
        fold_raw_transition, start=np.zeros_like(fold_raw_transition[0])
    )

    score_rows: list[dict[str, object]] = []
    for fold in range(DOWN_FOLDS):
        start = int(boundaries[fold])
        stop = int(boundaries[fold + 1])
        guard_indices = np.concatenate(
            (
                np.arange(start - GUARD_EVENTS, start, dtype=np.int64) % size,
                np.arange(stop, stop + GUARD_EVENTS, dtype=np.int64) % size,
            )
        )
        guard_model, guard_raw = count_event_indices(
            relation, gaps, guard_indices, gap_lookup, alphabet
        )
        for name in model_names:
            train = global_model_counts[name] - fold_model_counts[fold][name] - guard_model[name]
            if np.any(train < 0):
                raise AssertionError("Negative guarded training count")
            metrics = score_categorical(train, fold_model_counts[fold][name])
            score_rows.append({"fold": fold + 1, "model": name, **metrics})
        raw_train = global_raw_transition - fold_raw_transition[fold] - guard_raw
        raw_metrics = score_raw_gap_model(
            raw_train, fold_raw_target[fold], gap_labels
        )
        score_rows.append(
            {"fold": fold + 1, "model": "raw_gap_markov1", **raw_metrics}
        )

    scores = pd.DataFrame(score_rows)
    summaries: list[dict[str, object]] = []
    base_ce = float(
        scores.loc[scores["model"] == "current_B", "cross_entropy_bits"].mean()
    )
    for name, group in scores.groupby("model", sort=False):
        mean_ce = float(group["cross_entropy_bits"].mean())
        summaries.append(
            {
                "model": name,
                "mean_cross_entropy_bits": mean_ce,
                "sd_cross_entropy_bits": float(group["cross_entropy_bits"].std(ddof=1)),
                "gain_vs_current_B_bits": base_ce - mean_ce,
                "relative_ce_reduction_vs_current_B": (base_ce - mean_ce) / base_ce,
                "mean_perplexity": float(group["perplexity"].mean()),
                "mean_top1_accuracy": float(group["top1_accuracy"].mean()),
                "mean_brier_score": float(group["brier_score"].mean()),
                "mean_active_context_rows": float(group["active_context_rows"].mean()),
                "mean_active_conditional_df": float(group["active_conditional_df"].mean()),
                "min_fold_gain_vs_current_B_bits": float(
                    np.min(
                        scores.loc[scores["model"] == "current_B", "cross_entropy_bits"].to_numpy()
                        - group.sort_values("fold")["cross_entropy_bits"].to_numpy()
                    )
                ),
            }
        )
    summary = pd.DataFrame(summaries).sort_values("mean_cross_entropy_bits")
    saved = {
        "gap_labels": gap_labels,
        "fold_boundaries": boundaries,
        "relation_bin_counts": np.bincount(relation, minlength=DOWN_BINS),
    }
    return scores, summary, saved


def make_upward_figure(
    rung_metrics: pd.DataFrame,
    transition_metrics: pd.DataFrame,
    mode_scores: pd.DataFrame,
    arrays: dict[str, np.ndarray],
    path: Path,
) -> None:
    width, height = 2400, 1500
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        candidate = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
        return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()

    title_font, panel_font = font(40, True), font(24, True)
    body_font, small_font = font(18), font(15)
    ink, muted, grid_color = "#202731", "#5d6878", "#d9dee6"
    blue, orange, olive = "#3479a9", "#a06d13", "#687b38"
    draw.text((60, 28), "PN1F upward cross-rung ARA relation landscape", fill=ink, font=title_font)
    draw.text(
        (60, 82),
        "Opened exact wheels only; 12x12 relation planes; ordered minus first-order raw-gap control in residual row; prime 29 unopened",
        fill=muted,
        font=body_font,
    )

    ordered = arrays["ordered_12"]
    residual = arrays["markov_residual_12"]
    vmax_ordered = float(np.max(ordered))
    vmax_residual = float(np.max(np.abs(residual)))

    def sequential_color(value: float) -> tuple[int, int, int]:
        fraction = min(max(value / vmax_ordered, 0.0), 1.0) ** 0.45
        low = np.array([247, 249, 252], dtype=float)
        high = np.array([36, 112, 158], dtype=float)
        return tuple(np.rint(low + fraction * (high - low)).astype(int))

    def diverging_color(value: float) -> tuple[int, int, int]:
        fraction = min(abs(value) / vmax_residual, 1.0) ** 0.55 if vmax_residual else 0.0
        neutral = np.array([247, 247, 244], dtype=float)
        endpoint = np.array([160, 109, 19] if value < 0 else [52, 121, 169], dtype=float)
        return tuple(np.rint(neutral + fraction * (endpoint - neutral)).astype(int))

    def heatmap(matrix: np.ndarray, x0: int, y0: int, color_function) -> None:
        cell = 25
        for row in range(PLANE_BINS):
            for column in range(PLANE_BINS):
                x = x0 + column * cell
                y = y0 + (PLANE_BINS - 1 - row) * cell
                draw.rectangle(
                    (x, y, x + cell - 1, y + cell - 1),
                    fill=color_function(float(matrix[row, column])),
                )
        draw.rectangle((x0 - 1, y0 - 1, x0 + PLANE_BINS * cell, y0 + PLANE_BINS * cell), outline="#667386", width=2)

    draw.text((60, 125), "Ordered local relation plane", fill=ink, font=panel_font)
    draw.text((60, 540), "Ordered plane minus Gap-Markov-1 projection", fill=ink, font=panel_font)
    base_x, gap_x, top_y, residual_y = 75, 465, 195, 610
    for index, prime in enumerate(CORE_RUNGS):
        x0 = base_x + index * gap_x
        slots = int(rung_metrics.loc[rung_metrics.rung_prime == prime, "slot_count"].iloc[0])
        draw.text((x0, 155), f"rung {prime}   N={slots:,}", fill=ink, font=body_font)
        heatmap(ordered[index], x0, top_y, sequential_color)
        heatmap(residual[index], x0, residual_y, diverging_color)
        draw.text((x0 + 60, top_y + 310), "next ARA position", fill=muted, font=small_font)
        draw.text((x0 + 60, residual_y + 310), "next ARA position", fill=muted, font=small_font)
    draw.text((25, top_y + 80), "current", fill=muted, font=small_font)
    draw.text((25, top_y + 100), "ARA", fill=muted, font=small_font)
    draw.text((25, residual_y + 80), "current", fill=muted, font=small_font)
    draw.text((25, residual_y + 100), "ARA", fill=muted, font=small_font)

    # Metric line chart.
    metric_plot = (90, 1080, 850, 1400)
    draw.text((90, 1025), "Residual relation structure by opened rung", fill=ink, font=panel_font)
    core_metrics = rung_metrics[rung_metrics.rung_prime.isin(CORE_RUNGS)]
    iid_values = core_metrics.ordered_vs_gap_iid_jsd_bits.to_numpy()
    markov_values = core_metrics.ordered_vs_gap_markov1_jsd_bits.to_numpy()
    metric_max = max(float(iid_values.max()), float(markov_values.max())) * 1.12
    for tick in range(5):
        value = metric_max * tick / 4
        y = int(metric_plot[3] - value / metric_max * (metric_plot[3] - metric_plot[1]))
        draw.line((metric_plot[0], y, metric_plot[2], y), fill=grid_color, width=1)
        draw.text((metric_plot[0] - 65, y - 8), f"{value:.3f}", fill=muted, font=small_font)
    draw.line((metric_plot[0], metric_plot[1], metric_plot[0], metric_plot[3]), fill=ink, width=2)
    draw.line((metric_plot[0], metric_plot[3], metric_plot[2], metric_plot[3]), fill=ink, width=2)
    x_points = np.linspace(metric_plot[0] + 20, metric_plot[2] - 20, len(CORE_RUNGS)).astype(int)
    for values, color_value, shape in ((iid_values, blue, "circle"), (markov_values, orange, "square")):
        points = []
        for x, value in zip(x_points, values):
            y = int(metric_plot[3] - value / metric_max * (metric_plot[3] - metric_plot[1]))
            points.append((x, y))
            if shape == "circle":
                draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=color_value, outline=ink)
            else:
                draw.rectangle((x - 6, y - 6, x + 6, y + 6), fill=color_value, outline=ink)
        draw.line(points, fill=color_value, width=4)
    for x, prime in zip(x_points, CORE_RUNGS):
        draw.text((x - 9, metric_plot[3] + 10), str(prime), fill=muted, font=small_font)
    draw.line((110, 1065, 145, 1065), fill=blue, width=4)
    draw.text((155, 1053), "ordered vs Gap-IID", fill=muted, font=small_font)
    draw.line((360, 1065, 395, 1065), fill=orange, width=4)
    draw.text((405, 1053), "ordered vs Gap-Markov-1", fill=muted, font=small_font)
    draw.text((310, 1425), "maximum sieve prime / rung", fill=muted, font=small_font)

    # Cross-rung mode score line chart.
    mode_plot = (1020, 1080, 2290, 1400)
    draw.text((1020, 1025), "Cross-rung deformation coordinates — neutral orientation", fill=ink, font=panel_font)
    first_three = mode_scores[mode_scores["mode"].isin((1, 2, 3))]
    score_max = float(np.max(np.abs(first_three["score"]))) * 1.15
    zero_y = int((mode_plot[1] + mode_plot[3]) / 2)
    draw.line((mode_plot[0], zero_y, mode_plot[2], zero_y), fill=ink, width=2)
    draw.line((mode_plot[0], mode_plot[1], mode_plot[0], mode_plot[3]), fill=ink, width=2)
    mode_colors = (blue, orange, olive)
    transition_labels = transition_metrics["transition"].tolist()
    transition_x = np.linspace(mode_plot[0] + 70, mode_plot[2] - 70, len(transition_labels)).astype(int)
    for mode in (1, 2, 3):
        subset = mode_scores[mode_scores["mode"] == mode]
        energy = float(subset["energy_fraction"].iloc[0])
        points = []
        for x, value in zip(transition_x, subset["score"]):
            y = int(zero_y - float(value) / score_max * (mode_plot[3] - mode_plot[1]) / 2)
            points.append((x, y))
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=mode_colors[mode - 1], outline=ink)
        draw.line(points, fill=mode_colors[mode - 1], width=4)
        legend_x = 1050 + (mode - 1) * 350
        draw.line((legend_x, 1065, legend_x + 35, 1065), fill=mode_colors[mode - 1], width=4)
        draw.text((legend_x + 45, 1053), f"mode {mode} ({energy:.1%})", fill=muted, font=small_font)
    for x, label in zip(transition_x, transition_labels):
        draw.text((x - 28, mode_plot[3] + 10), label, fill=muted, font=small_font)
    draw.text((1450, 1425), "opened sieve transition", fill=muted, font=small_font)
    image.save(path, format="PNG")


def make_downward_figure(summary: pd.DataFrame, path: Path) -> None:
    display_names = {
        "current_B": "current position B",
        "B_plus_direction": "B + arrival direction",
        "B_plus_distance": "B + arrival distance",
        "B_plus_signed_step": "B + signed step",
        "B_plus_shared_gap": "B + shared raw gap",
        "full_A_B": "full previous/current pair",
        "raw_gap_markov1": "raw-gap Markov-1",
    }
    ordered = summary.sort_values("mean_cross_entropy_bits", ascending=False).copy()
    ordered["label"] = ordered.model.map(display_names)
    width, height = 1950, 900
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        candidate = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
        return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()

    title_font, panel_font = font(38, True), font(23, True)
    body_font, small_font = font(18), font(15)
    ink, muted, grid_color = "#202731", "#5d6878", "#d9dee6"
    blue, orange, grey = "#3479a9", "#a06d13", "#9aa4b0"
    draw.text((55, 28), "PN1F downward prime-23 path decomposition", fill=ink, font=title_font)
    draw.text(
        (55, 80),
        "Eight contiguous folds with guarded boundaries; Jeffreys smoothing; development data only; prime 29 unopened",
        fill=muted,
        font=body_font,
    )
    left_plot = (360, 175, 910, 780)
    right_plot = (1330, 175, 1880, 780)
    draw.text((360, 125), "Eight-block prediction", fill=ink, font=panel_font)
    draw.text((1330, 125), "Information recovered over current B", fill=ink, font=panel_font)
    row_height = (left_plot[3] - left_plot[1]) / len(ordered)
    max_ce = float(ordered.mean_cross_entropy_bits.max()) * 1.1
    max_gain = max(abs(float(ordered.gain_vs_current_B_bits.min())), abs(float(ordered.gain_vs_current_B_bits.max()))) * 1.18
    zero_x = int((right_plot[0] + right_plot[2]) / 2)
    draw.line((left_plot[0], left_plot[1], left_plot[0], left_plot[3]), fill=ink, width=2)
    draw.line((zero_x, right_plot[1], zero_x, right_plot[3]), fill=ink, width=2)
    for index, row in enumerate(ordered.itertuples()):
        y0 = int(left_plot[1] + index * row_height + 8)
        y1 = int(left_plot[1] + (index + 1) * row_height - 8)
        centre_y = (y0 + y1) // 2
        draw.text((55, centre_y - 10), row.label, fill=ink, font=body_font)
        ce_x = int(left_plot[0] + row.mean_cross_entropy_bits / max_ce * (left_plot[2] - left_plot[0]))
        draw.rectangle((left_plot[0], y0, ce_x, y1), fill=blue, outline=ink)
        draw.text((ce_x + 10, centre_y - 9), f"{row.mean_cross_entropy_bits:.4f}", fill=muted, font=small_font)
        gain_x = int(zero_x + row.gain_vs_current_B_bits / max_gain * (right_plot[2] - right_plot[0]) / 2)
        draw.rectangle(
            (min(zero_x, gain_x), y0, max(zero_x, gain_x), y1),
            fill=orange if row.gain_vs_current_B_bits >= 0 else grey,
            outline=ink,
        )
        label_x = gain_x + 8 if row.gain_vs_current_B_bits >= 0 else gain_x - 130
        draw.text(
            (label_x, centre_y - 17),
            f"{row.gain_vs_current_B_bits:+.4f} bits\n{row.mean_active_context_rows:.0f} active rows",
            fill=muted,
            font=small_font,
        )
        draw.line((40, y1 + 7, 1900, y1 + 7), fill=grid_color, width=1)
    draw.text((500, 820), "cross-entropy (bits/read; lower is better; zero-based)", fill=muted, font=small_font)
    draw.text((1390, 820), "gain versus current-position model (bits/read)", fill=muted, font=small_font)
    image.save(path, format="PNG")


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    return value


def main() -> dict[str, object]:
    if file_hash(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("PN1F protocol hash mismatch")
    if 29 in ALL_OPEN_PRIMES or max(ALL_OPEN_PRIMES) != 23:
        raise RuntimeError("Protected prime was opened")

    gaps_by_rung, periods, slots = generate_opened_gaps()
    p23_hash = array_hash(gaps_by_rung[23])
    exact_checks = {
        "protocol_hash_matches": file_hash(PROTOCOL) == PROTOCOL_SHA256,
        "maximum_generated_prime_is_23": max(gaps_by_rung) == 23,
        "prime29_opened": False,
        "p23_period_matches": periods[23] == EXPECTED_P23_PERIOD,
        "p23_slot_count_matches": slots[23] == EXPECTED_P23_SLOTS,
        "p23_gap_sum_matches": int(gaps_by_rung[23].sum(dtype=np.int64)) == EXPECTED_P23_PERIOD,
        "p23_gap_hash_matches_pn1c_pn1d": p23_hash == EXPECTED_P23_GAP_SHA256,
        "all_gaps_positive_even": all(
            bool(np.all(gaps > 0) and np.all(gaps % 2 == 0))
            for gaps in gaps_by_rung.values()
        ),
    }
    if not all(value is False if key == "prime29_opened" else bool(value) for key, value in exact_checks.items()):
        raise AssertionError(f"Exact check failed: {exact_checks}")

    rung_metrics, transition_metrics, mode_scores, upward_arrays, _ = upward_landscape(
        gaps_by_rung, periods, slots
    )
    down_scores, down_summary, downward_arrays = downward_decomposition(gaps_by_rung[23])

    arrays = {**upward_arrays, **{f"down_{key}": value for key, value in downward_arrays.items()}}
    np.savez_compressed(HERE / "PN1F_BIDIRECTIONAL_MATRICES.npz", **arrays)
    rung_metrics.to_csv(HERE / "PN1F_RUNG_METRICS.csv", index=False)
    transition_metrics.to_csv(HERE / "PN1F_TRANSITION_METRICS.csv", index=False)
    mode_scores.to_csv(HERE / "PN1F_DEFORMATION_MODE_SCORES.csv", index=False)
    down_scores.to_csv(HERE / "PN1F_DOWNWARD_FOLD_SCORES.csv", index=False)
    down_summary.to_csv(HERE / "PN1F_DOWNWARD_MODEL_SUMMARY.csv", index=False)

    make_upward_figure(
        rung_metrics,
        transition_metrics,
        mode_scores,
        upward_arrays,
        HERE / "PN1F_UPWARD_LANDSCAPE.png",
    )
    make_downward_figure(down_summary, HERE / "PN1F_DOWNWARD_DECOMPOSITION.png")

    ordered_summary = down_summary.set_index("model")
    deformation_energy = upward_arrays["deformation_energy_fractions"]
    results: dict[str, object] = {
        "development_id": "PN1F/DEV/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DEVELOPMENT LANDSCAPE / NOT BLIND CONFIRMATION",
        "protocol_sha256": PROTOCOL_SHA256,
        "maximum_generated_prime": max(gaps_by_rung),
        "prime29_opened": False,
        "exact_checks": exact_checks,
        "upward": {
            "core_rungs": list(CORE_RUNGS),
            "transition_count": len(CORE_RUNGS) - 1,
            "deformation_mode_energy_fractions": deformation_energy.tolist(),
            "adjacent_deformation_cosines": transition_metrics[
                "cosine_with_previous_deformation"
            ].tolist(),
            "p23_ordered_vs_gap_iid_jsd_bits": float(
                rung_metrics.loc[rung_metrics.rung_prime == 23, "ordered_vs_gap_iid_jsd_bits"].iloc[0]
            ),
            "p23_ordered_vs_gap_markov1_jsd_bits": float(
                rung_metrics.loc[
                    rung_metrics.rung_prime == 23, "ordered_vs_gap_markov1_jsd_bits"
                ].iloc[0]
            ),
            "classification": "MAPPED ONLY — DYLAN ORIENTATION PENDING",
        },
        "downward": {
            "folds": DOWN_FOLDS,
            "guard_events_each_boundary": GUARD_EVENTS,
            "base_current_B_ce_bits": float(
                ordered_summary.loc["current_B", "mean_cross_entropy_bits"]
            ),
            "direction_gain_bits": float(
                ordered_summary.loc["B_plus_direction", "gain_vs_current_B_bits"]
            ),
            "distance_gain_bits": float(
                ordered_summary.loc["B_plus_distance", "gain_vs_current_B_bits"]
            ),
            "signed_step_gain_bits": float(
                ordered_summary.loc["B_plus_signed_step", "gain_vs_current_B_bits"]
            ),
            "shared_gap_gain_bits": float(
                ordered_summary.loc["B_plus_shared_gap", "gain_vs_current_B_bits"]
            ),
            "full_pair_gain_bits": float(
                ordered_summary.loc["full_A_B", "gain_vs_current_B_bits"]
            ),
            "raw_gap_markov1_gain_bits": float(
                ordered_summary.loc["raw_gap_markov1", "gain_vs_current_B_bits"]
            ),
            "best_model_by_cross_entropy": str(down_summary.iloc[0]["model"]),
        },
        "software": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "pillow": Image.__version__ if hasattr(Image, "__version__") else "unknown",
        },
    }
    (HERE / "PN1F_RESULTS.json").write_text(
        json.dumps(json_safe(results), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(json_safe(results), indent=2, allow_nan=False), flush=True)
    return results


if __name__ == "__main__":
    main()
