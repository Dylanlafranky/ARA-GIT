"""PN1G frozen transfer from the prime-23 wheel to the prime-29 wheel.

The target wheel is aggregated as a stream.  Its billion-slot residue and gap
cycles are never materialized.  See PN1G_PRIME29_TRANSFER_PROTOCOL_v1_FROZEN.md.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from pn1_sieve_rung_test import generate_wheel


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1G_PRIME29_TRANSFER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "FC568F2D1913F163A81146A089F0D1F42981F7E9EFB5FAFBA5C097D92387732B"

SOURCE_PRIME = 23
TARGET_PRIME = 29
P19_PERIOD = 9_699_690
P19_SLOTS = 1_658_880
P23_PERIOD = 223_092_870
P23_SLOTS = 36_495_360
P23_GAP_SHA256 = "F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C"
P29_PERIOD = 6_469_693_230
P29_SLOTS = 1_021_870_080

BINS = 12
HIGH_BINS = 24
FOLDS = 8
GUARD_EVENTS = 4
ALPHA = 0.5
MAX_GAP = 256
CHUNK = 4_000_000

FROZEN_ORDER = (
    "B_plus_shared_gap",
    "raw_gap_markov1",
    "full_A_B",
    "B_plus_signed_step",
    "B_plus_distance",
    "B_plus_direction",
    "current_B",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalize(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    total = float(result.sum())
    if total <= 0 or np.any(result < 0) or not np.all(np.isfinite(result)):
        raise AssertionError("Invalid probability array")
    return result / total


def relation_bin(left: np.ndarray | int, right: np.ndarray | int, bins: int) -> np.ndarray:
    """Exact integer form of floor(x*bins/2), x=2*right/(left+right)."""
    left_array = np.asarray(left, dtype=np.int64)
    right_array = np.asarray(right, dtype=np.int64)
    result = (right_array * bins) // (left_array + right_array)
    return np.minimum(result, bins - 1).astype(np.int64, copy=False)


def cosine(first: np.ndarray, second: np.ndarray) -> float:
    denominator = float(np.linalg.norm(first) * np.linalg.norm(second))
    return float(np.sum(first * second) / denominator) if denominator else 0.0


def jsd_bits(first: np.ndarray, second: np.ndarray) -> float:
    p = normalize(first).ravel()
    q = normalize(second).ravel()
    midpoint = 0.5 * (p + q)

    def kl(values: np.ndarray) -> float:
        active = values > 0
        return float(np.sum(values[active] * np.log2(values[active] / midpoint[active])))

    return 0.5 * kl(p) + 0.5 * kl(q)


def plane_entropy(probability: np.ndarray) -> float:
    p = normalize(probability)
    active = p > 0
    return float(-np.sum(p[active] * np.log2(p[active])) / 1.0)


def plane_mutual_information(probability: np.ndarray) -> float:
    p = normalize(probability)
    row = p.sum(axis=1)
    column = p.sum(axis=0)
    expected = row[:, None] * column[None, :]
    active = p > 0
    return float(np.sum(p[active] * np.log2(p[active] / expected[active])))


def projected_gap_planes(
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
    for ia, first in enumerate(labels):
        for ib, second in enumerate(labels):
            first_bin = int(relation_bin(int(first), int(second), bins))
            iid_ab = marginal[ia] * marginal[ib]
            markov_ab = marginal[ia] * transition[ia, ib]
            if iid_ab == 0 and markov_ab == 0:
                continue
            for ic, third in enumerate(labels):
                second_bin = int(relation_bin(int(second), int(third), bins))
                iid[first_bin, second_bin] += iid_ab * marginal[ic]
                markov[first_bin, second_bin] += markov_ab * transition[ib, ic]
    return normalize(iid), normalize(markov)


MODEL_WIDTHS = {
    "current_B": BINS,
    "B_plus_direction": BINS * 3,
    "B_plus_distance": BINS * 4,
    "B_plus_signed_step": BINS * 7,
    "full_A_B": BINS * BINS,
    "B_plus_shared_gap": BINS * MAX_GAP,
}


class StreamAggregator:
    """Aggregate one complete child wheel from a sequential gap stream."""

    def __init__(self, expected_slots: int, downward: bool) -> None:
        self.expected_slots = int(expected_slots)
        self.downward = bool(downward)
        self.gap_count = 0
        self.gap_sum = 0
        self.gap_hash = hashlib.sha256()
        self.gap_counts = np.zeros(MAX_GAP, dtype=np.int64)
        self.gap_transitions = np.zeros((MAX_GAP, MAX_GAP), dtype=np.int64)
        self.ordered_12_counts = np.zeros((BINS, BINS), dtype=np.int64)
        self.ordered_24_counts = np.zeros((HIGH_BINS, HIGH_BINS), dtype=np.int64)
        self.previous_gap: int | None = None
        self.first_gap: int | None = None
        self.relation_count = 0
        self.previous_relation_12: int | None = None
        self.previous_relation_24: int | None = None
        self.first_relation_records: list[tuple[int, int, int, int]] = []
        self.tail_relation_12 = np.empty(0, dtype=np.int64)
        self.tail_current_gap = np.empty(0, dtype=np.int64)
        self.tail_next_gap = np.empty(0, dtype=np.int64)

        if self.downward:
            self.boundaries = np.linspace(0, self.expected_slots, FOLDS + 1, dtype=np.int64)
            self.fold_model_counts = {
                name: np.zeros((FOLDS, width, BINS), dtype=np.int64)
                for name, width in MODEL_WIDTHS.items()
            }
            self.guard_model_counts = {
                name: np.zeros((FOLDS, width, BINS), dtype=np.int64)
                for name, width in MODEL_WIDTHS.items()
            }
            self.fold_raw_transition = np.zeros(
                (FOLDS, MAX_GAP, MAX_GAP), dtype=np.int64
            )
            self.guard_raw_transition = np.zeros_like(self.fold_raw_transition)
            self.fold_raw_target = np.zeros((FOLDS, MAX_GAP, BINS), dtype=np.int64)
            self.guard_map: dict[int, list[int]] = defaultdict(list)
            for fold in range(FOLDS):
                start = int(self.boundaries[fold])
                stop = int(self.boundaries[fold + 1])
                guard_indices = np.concatenate(
                    (
                        np.arange(start - GUARD_EVENTS, start, dtype=np.int64),
                        np.arange(stop, stop + GUARD_EVENTS, dtype=np.int64),
                    )
                ) % self.expected_slots
                for index in guard_indices.tolist():
                    self.guard_map[int(index)].append(fold)

    def _accumulate_flat(
        self,
        destination: np.ndarray,
        fold: np.ndarray,
        context: np.ndarray,
        target: np.ndarray,
    ) -> None:
        width = destination.shape[1]
        key = fold * (width * BINS) + context * BINS + target
        destination += np.bincount(
            key, minlength=FOLDS * width * BINS
        ).reshape(FOLDS, width, BINS)

    @staticmethod
    def _contexts(a: np.ndarray, b: np.ndarray, current_gap: np.ndarray) -> dict[str, np.ndarray]:
        step = b - a
        direction = np.where(step < 0, 0, np.where(step == 0, 1, 2))
        absolute = np.abs(step)
        distance = np.where(
            absolute == 0,
            0,
            np.where(absolute == 1, 1, np.where(absolute <= 3, 2, 3)),
        )
        signed = np.where(
            step <= -4,
            0,
            np.where(
                step <= -2,
                1,
                np.where(
                    step == -1,
                    2,
                    np.where(
                        step == 0,
                        3,
                        np.where(step == 1, 4, np.where(step <= 3, 5, 6)),
                    ),
                ),
            ),
        )
        return {
            "current_B": b,
            "B_plus_direction": b * 3 + direction,
            "B_plus_distance": b * 4 + distance,
            "B_plus_signed_step": b * 7 + signed,
            "full_A_B": a * BINS + b,
            "B_plus_shared_gap": b * MAX_GAP + current_gap,
        }

    def _accumulate_guard_event(
        self,
        fold: int,
        contexts: dict[str, int],
        target: int,
        current_gap: int,
        next_gap: int,
    ) -> None:
        for name, context in contexts.items():
            self.guard_model_counts[name][fold, context, target] += 1
        self.guard_raw_transition[fold, current_gap, next_gap] += 1

    def _count_events(
        self,
        a: np.ndarray,
        b: np.ndarray,
        target: np.ndarray,
        current_gap: np.ndarray,
        next_gap: np.ndarray,
        event_indices: np.ndarray,
    ) -> None:
        if len(target) == 0:
            return
        if np.any(current_gap >= MAX_GAP) or np.any(next_gap >= MAX_GAP):
            raise AssertionError("MAX_GAP is too small for the observed wheel")
        folds = np.searchsorted(self.boundaries[1:], event_indices, side="right")
        contexts = self._contexts(a, b, current_gap)
        for name, values in contexts.items():
            self._accumulate_flat(self.fold_model_counts[name], folds, values, target)

        raw_key = folds * (MAX_GAP * MAX_GAP) + current_gap * MAX_GAP + next_gap
        self.fold_raw_transition += np.bincount(
            raw_key, minlength=FOLDS * MAX_GAP * MAX_GAP
        ).reshape(FOLDS, MAX_GAP, MAX_GAP)
        target_key = folds * (MAX_GAP * BINS) + current_gap * BINS + target
        self.fold_raw_target += np.bincount(
            target_key, minlength=FOLDS * MAX_GAP * BINS
        ).reshape(FOLDS, MAX_GAP, BINS)

        # Only 64 boundary-neighbour events are guards, so exact scalar updates
        # are cheaper and clearer than another billion-element mask.
        if len(event_indices) == 1:
            index_lookup = {int(event_indices[0]): 0}
        else:
            low = int(event_indices[0])
            high = int(event_indices[-1])
            index_lookup = {}
            for protected_index in self.guard_map:
                if low <= protected_index <= high:
                    position = int(np.searchsorted(event_indices, protected_index))
                    if position < len(event_indices) and int(event_indices[position]) == protected_index:
                        index_lookup[protected_index] = position
        for protected_index, position in index_lookup.items():
            scalar_contexts = {name: int(values[position]) for name, values in contexts.items()}
            for fold in self.guard_map.get(protected_index, []):
                self._accumulate_guard_event(
                    fold,
                    scalar_contexts,
                    int(target[position]),
                    int(current_gap[position]),
                    int(next_gap[position]),
                )

    def _consume_relation_records(
        self,
        relation_12: np.ndarray,
        relation_24: np.ndarray,
        current_gap: np.ndarray,
        next_gap: np.ndarray,
        indices: np.ndarray,
        count_plane_pairs: bool,
    ) -> None:
        if len(relation_12) == 0:
            return
        if len(self.first_relation_records) < 2:
            needed = 2 - len(self.first_relation_records)
            for index in range(min(needed, len(relation_12))):
                self.first_relation_records.append(
                    (
                        int(relation_12[index]),
                        int(relation_24[index]),
                        int(current_gap[index]),
                        int(next_gap[index]),
                    )
                )

        if count_plane_pairs:
            if self.previous_relation_12 is None:
                left_12 = relation_12[:-1]
                right_12 = relation_12[1:]
                left_24 = relation_24[:-1]
                right_24 = relation_24[1:]
            else:
                left_12 = np.concatenate(
                    (np.asarray([self.previous_relation_12], dtype=np.int64), relation_12[:-1])
                )
                right_12 = relation_12
                left_24 = np.concatenate(
                    (np.asarray([self.previous_relation_24], dtype=np.int64), relation_24[:-1])
                )
                right_24 = relation_24
            if len(right_12):
                self.ordered_12_counts += np.bincount(
                    left_12 * BINS + right_12, minlength=BINS * BINS
                ).reshape(BINS, BINS)
                self.ordered_24_counts += np.bincount(
                    left_24 * HIGH_BINS + right_24, minlength=HIGH_BINS * HIGH_BINS
                ).reshape(HIGH_BINS, HIGH_BINS)
            self.previous_relation_12 = int(relation_12[-1])
            self.previous_relation_24 = int(relation_24[-1])

        if self.downward:
            combined_relation = np.concatenate((self.tail_relation_12, relation_12))
            combined_current = np.concatenate((self.tail_current_gap, current_gap))
            combined_next = np.concatenate((self.tail_next_gap, next_gap))
            combined_indices = np.concatenate(
                (
                    np.full(len(self.tail_relation_12), -1, dtype=np.int64),
                    indices,
                )
            )
            # Tail indices are not needed as targets. Only the newly supplied
            # records (from position 2 onward) become target events.
            if len(combined_relation) >= 3:
                target_start = max(2, len(self.tail_relation_12))
                target_stop = len(combined_relation)
                self._count_events(
                    combined_relation[target_start - 2 : target_stop - 2],
                    combined_relation[target_start - 1 : target_stop - 1],
                    combined_relation[target_start:],
                    combined_current[target_start:],
                    combined_next[target_start:],
                    combined_indices[target_start:],
                )
            self.tail_relation_12 = combined_relation[-2:].copy()
            self.tail_current_gap = combined_current[-2:].copy()
            self.tail_next_gap = combined_next[-2:].copy()

    def consume_gaps(self, gaps: np.ndarray) -> None:
        gaps = np.asarray(gaps, dtype=np.int64)
        if len(gaps) == 0:
            return
        if np.any(gaps <= 0) or np.any(gaps % 2 != 0) or np.any(gaps >= MAX_GAP):
            raise AssertionError("Invalid streamed gap")
        if self.first_gap is None:
            self.first_gap = int(gaps[0])
        self.gap_hash.update(gaps.astype(np.int32, copy=False).tobytes(order="C"))
        self.gap_count += len(gaps)
        self.gap_sum += int(gaps.sum(dtype=np.int64))
        self.gap_counts += np.bincount(gaps, minlength=MAX_GAP)

        if self.previous_gap is None:
            transition_left = gaps[:-1]
            transition_right = gaps[1:]
            relation_indices = np.arange(0, len(gaps) - 1, dtype=np.int64)
        else:
            transition_left = np.concatenate(
                (np.asarray([self.previous_gap], dtype=np.int64), gaps[:-1])
            )
            transition_right = gaps
            relation_indices = np.arange(
                self.relation_count, self.relation_count + len(gaps), dtype=np.int64
            )
        if len(transition_right):
            self.gap_transitions += np.bincount(
                transition_left * MAX_GAP + transition_right,
                minlength=MAX_GAP * MAX_GAP,
            ).reshape(MAX_GAP, MAX_GAP)
            rel12 = relation_bin(transition_left, transition_right, BINS)
            rel24 = relation_bin(transition_left, transition_right, HIGH_BINS)
            self._consume_relation_records(
                rel12,
                rel24,
                transition_left,
                transition_right,
                relation_indices,
                count_plane_pairs=True,
            )
            self.relation_count += len(rel12)
        self.previous_gap = int(gaps[-1])

    def close_cycle(self) -> None:
        if self.gap_count != self.expected_slots:
            raise AssertionError(
                f"Expected {self.expected_slots} gaps, received {self.gap_count}"
            )
        if self.first_gap is None or self.previous_gap is None:
            raise AssertionError("Empty gap stream")
        current = np.asarray([self.previous_gap], dtype=np.int64)
        following = np.asarray([self.first_gap], dtype=np.int64)
        self.gap_transitions[self.previous_gap, self.first_gap] += 1
        rel12 = relation_bin(current, following, BINS)
        rel24 = relation_bin(current, following, HIGH_BINS)
        self._consume_relation_records(
            rel12,
            rel24,
            current,
            following,
            np.asarray([self.expected_slots - 1], dtype=np.int64),
            count_plane_pairs=True,
        )
        self.relation_count += 1
        if self.relation_count != self.expected_slots:
            raise AssertionError("Relation sequence did not close")
        if len(self.first_relation_records) < 2:
            raise AssertionError("Missing circular relation prefix")

        # The first repeated relation closes the relation plane and creates
        # event 0. The second creates event 1 but its plane edge was already
        # counted in the original sequence.
        for repeat_index, record in enumerate(self.first_relation_records[:2]):
            first12, first24, first_current, first_next = record
            self._consume_relation_records(
                np.asarray([first12], dtype=np.int64),
                np.asarray([first24], dtype=np.int64),
                np.asarray([first_current], dtype=np.int64),
                np.asarray([first_next], dtype=np.int64),
                np.asarray([repeat_index], dtype=np.int64),
                count_plane_pairs=repeat_index == 0,
            )

        if int(self.gap_transitions.sum()) != self.expected_slots:
            raise AssertionError("Gap transitions do not close")
        if int(self.ordered_12_counts.sum()) != self.expected_slots:
            raise AssertionError("12-bin relation plane does not close")
        if int(self.ordered_24_counts.sum()) != self.expected_slots:
            raise AssertionError("24-bin relation plane does not close")
        if self.downward:
            for name, counts in self.fold_model_counts.items():
                if int(counts.sum()) != self.expected_slots:
                    raise AssertionError(f"Downward event count failed for {name}")
            if int(self.fold_raw_transition.sum()) != self.expected_slots:
                raise AssertionError("Raw transition fold count failed")
            if int(self.fold_raw_target.sum()) != self.expected_slots:
                raise AssertionError("Raw target fold count failed")

    def output(self) -> dict[str, object]:
        return {
            "gap_count": self.gap_count,
            "gap_sum": self.gap_sum,
            "gap_sha256": self.gap_hash.hexdigest().upper(),
            "gap_counts": self.gap_counts,
            "gap_transitions": self.gap_transitions,
            "ordered_12_counts": self.ordered_12_counts,
            "ordered_24_counts": self.ordered_24_counts,
            "fold_model_counts": getattr(self, "fold_model_counts", None),
            "guard_model_counts": getattr(self, "guard_model_counts", None),
            "fold_raw_transition": getattr(self, "fold_raw_transition", None),
            "guard_raw_transition": getattr(self, "guard_raw_transition", None),
            "fold_raw_target": getattr(self, "fold_raw_target", None),
            "boundaries": getattr(self, "boundaries", None),
        }


def stream_child_wheel(
    parent_residues: np.ndarray,
    parent_period: int,
    new_prime: int,
    expected_slots: int,
    *,
    downward: bool,
    collect_residues: bool,
) -> tuple[dict[str, object], np.ndarray | None]:
    started = time.perf_counter()
    child_period = int(parent_period * new_prime)
    aggregator = StreamAggregator(expected_slots, downward=downward)
    collected = (
        np.empty(expected_slots, dtype=np.int32 if child_period < 2**31 else np.int64)
        if collect_residues
        else None
    )
    write_position = 0
    first_residue: int | None = None
    previous_residue: int | None = None
    parent = np.asarray(parent_residues)
    for lift in range(new_prime):
        offset = int(lift * parent_period)
        for start in range(0, len(parent), CHUNK):
            stop = min(start + CHUNK, len(parent))
            candidates = parent[start:stop].astype(np.int64, copy=False) + offset
            survivors = candidates[np.mod(candidates, new_prime) != 0]
            if len(survivors) == 0:
                continue
            if collected is not None:
                collected[write_position : write_position + len(survivors)] = survivors
            write_position += len(survivors)
            if first_residue is None:
                first_residue = int(survivors[0])
                previous_residue = first_residue
                survivors = survivors[1:]
            if len(survivors):
                gaps = np.diff(
                    np.concatenate(
                        (np.asarray([previous_residue], dtype=np.int64), survivors)
                    )
                )
                aggregator.consume_gaps(gaps)
                previous_residue = int(survivors[-1])
        print(
            f"stream p{new_prime}: lift {lift + 1}/{new_prime}, "
            f"survivors {write_position:,}, elapsed {time.perf_counter() - started:.1f}s",
            flush=True,
        )
    if first_residue is None or previous_residue is None:
        raise AssertionError("No child residues generated")
    closing_gap = first_residue + child_period - previous_residue
    aggregator.consume_gaps(np.asarray([closing_gap], dtype=np.int64))
    aggregator.close_cycle()
    if write_position != expected_slots:
        raise AssertionError(f"Child slot count {write_position} != {expected_slots}")
    print(
        f"stream p{new_prime}: complete in {time.perf_counter() - started:.1f}s",
        flush=True,
    )
    return aggregator.output(), collected


def independent_counts_from_gaps(gaps: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if np.any(gaps >= MAX_GAP):
        raise AssertionError("Independent calibration MAX_GAP failure")
    left = gaps.astype(np.int64, copy=False)
    right = np.roll(left, -1)
    transitions = np.bincount(
        left * MAX_GAP + right, minlength=MAX_GAP * MAX_GAP
    ).reshape(MAX_GAP, MAX_GAP)
    rel12 = relation_bin(left, right, BINS)
    rel24 = relation_bin(left, right, HIGH_BINS)
    ordered12 = np.bincount(
        rel12 * BINS + np.roll(rel12, -1), minlength=BINS * BINS
    ).reshape(BINS, BINS)
    ordered24 = np.bincount(
        rel24 * HIGH_BINS + np.roll(rel24, -1), minlength=HIGH_BINS * HIGH_BINS
    ).reshape(HIGH_BINS, HIGH_BINS)
    return transitions, ordered12, ordered24


def score_categorical(train: np.ndarray, test: np.ndarray) -> dict[str, float | int]:
    probabilities = (train.astype(np.float64) + ALPHA) / (
        train.sum(axis=1, keepdims=True) + ALPHA * BINS
    )
    sample_count = int(test.sum())
    active = test > 0
    cross_entropy = float(
        -np.sum(test[active] * np.log2(probabilities[active])) / sample_count
    )
    predicted = np.argmax(probabilities, axis=1)
    top1 = float(test[np.arange(len(predicted)), predicted].sum() / sample_count)
    probability_square = np.sum(probabilities**2, axis=1)
    brier = 0.0
    for target in range(BINS):
        brier += float(
            np.sum(test[:, target] * (probability_square - 2 * probabilities[:, target] + 1))
        )
    active_rows = int(np.count_nonzero(train.sum(axis=1)))
    return {
        "cross_entropy_bits": cross_entropy,
        "perplexity": 2**cross_entropy,
        "top1_accuracy": top1,
        "brier_score": brier / sample_count,
        "test_events": sample_count,
        "active_context_rows": active_rows,
        "active_conditional_df": active_rows * (BINS - 1),
    }


def raw_projected_probabilities(train: np.ndarray, labels: np.ndarray) -> np.ndarray:
    transition = (train.astype(np.float64) + ALPHA) / (
        train.sum(axis=1, keepdims=True) + ALPHA * len(labels)
    )
    projected = np.zeros((len(labels), BINS), dtype=np.float64)
    for current, first_gap in enumerate(labels):
        for following, second_gap in enumerate(labels):
            target = int(relation_bin(int(first_gap), int(second_gap), BINS))
            projected[current, target] += transition[current, following]
    return projected


def score_raw_gap(train: np.ndarray, test_target: np.ndarray, labels: np.ndarray) -> dict[str, float | int]:
    probabilities = raw_projected_probabilities(train, labels)
    sample_count = int(test_target.sum())
    active = test_target > 0
    cross_entropy = float(
        -np.sum(test_target[active] * np.log2(probabilities[active])) / sample_count
    )
    predicted = np.argmax(probabilities, axis=1)
    top1 = float(
        test_target[np.arange(len(predicted)), predicted].sum() / sample_count
    )
    probability_square = np.sum(probabilities**2, axis=1)
    brier = 0.0
    for target in range(BINS):
        brier += float(
            np.sum(
                test_target[:, target]
                * (probability_square - 2 * probabilities[:, target] + 1)
            )
        )
    active_rows = int(np.count_nonzero(train.sum(axis=1)))
    return {
        "cross_entropy_bits": cross_entropy,
        "perplexity": 2**cross_entropy,
        "top1_accuracy": top1,
        "brier_score": brier / sample_count,
        "test_events": sample_count,
        "active_context_rows": active_rows,
        "active_conditional_df": active_rows * (len(labels) - 1),
    }


def downward_scores(stream: dict[str, object], labels: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    fold_counts = stream["fold_model_counts"]
    guard_counts = stream["guard_model_counts"]
    if not isinstance(fold_counts, dict) or not isinstance(guard_counts, dict):
        raise AssertionError("Missing downward counts")
    rows: list[dict[str, object]] = []
    for name, counts in fold_counts.items():
        global_counts = counts.sum(axis=0)
        guards = guard_counts[name]
        for fold in range(FOLDS):
            train = global_counts - counts[fold] - guards[fold]
            if np.any(train < 0):
                raise AssertionError("Negative categorical training inventory")
            rows.append({"fold": fold + 1, "model": name, **score_categorical(train, counts[fold])})

    active = labels.astype(np.int64)
    fold_transition = np.asarray(stream["fold_raw_transition"])
    guard_transition = np.asarray(stream["guard_raw_transition"])
    fold_target = np.asarray(stream["fold_raw_target"])
    global_transition = fold_transition.sum(axis=0)
    for fold in range(FOLDS):
        train_full = global_transition - fold_transition[fold] - guard_transition[fold]
        train = train_full[np.ix_(active, active)]
        test_target = fold_target[fold, active, :]
        rows.append(
            {
                "fold": fold + 1,
                "model": "raw_gap_markov1",
                **score_raw_gap(train, test_target, labels),
            }
        )

    scores = pd.DataFrame(rows).sort_values(["fold", "model"]).reset_index(drop=True)
    base_by_fold = (
        scores[scores.model == "current_B"].set_index("fold")["cross_entropy_bits"]
    )
    summaries: list[dict[str, object]] = []
    for name, group in scores.groupby("model", sort=False):
        ordered = group.sort_values("fold")
        gains = base_by_fold.loc[ordered.fold].to_numpy() - ordered.cross_entropy_bits.to_numpy()
        mean_ce = float(ordered.cross_entropy_bits.mean())
        summaries.append(
            {
                "model": name,
                "mean_cross_entropy_bits": mean_ce,
                "sd_cross_entropy_bits": float(ordered.cross_entropy_bits.std(ddof=1)),
                "gain_vs_current_B_bits": float(base_by_fold.mean() - mean_ce),
                "relative_ce_reduction_vs_current_B": float((base_by_fold.mean() - mean_ce) / base_by_fold.mean()),
                "min_fold_gain_vs_current_B_bits": float(gains.min()),
                "mean_perplexity": float(ordered.perplexity.mean()),
                "mean_top1_accuracy": float(ordered.top1_accuracy.mean()),
                "mean_brier_score": float(ordered.brier_score.mean()),
                "mean_active_context_rows": float(ordered.active_context_rows.mean()),
                "mean_active_conditional_df": float(ordered.active_conditional_df.mean()),
            }
        )
    summary = pd.DataFrame(summaries).sort_values("mean_cross_entropy_bits").reset_index(drop=True)
    return scores, summary


def kendall_agreement(actual_order: list[str], expected_order: tuple[str, ...]) -> float:
    actual_rank = {name: index for index, name in enumerate(actual_order)}
    expected_rank = {name: index for index, name in enumerate(expected_order)}
    concordant = 0
    discordant = 0
    for index, left in enumerate(expected_order):
        for right in expected_order[index + 1 :]:
            expected_sign = expected_rank[left] - expected_rank[right]
            actual_sign = actual_rank[left] - actual_rank[right]
            if expected_sign * actual_sign > 0:
                concordant += 1
            else:
                discordant += 1
    return (concordant - discordant) / (concordant + discordant)


def draw_heatmap(
    draw: ImageDraw.ImageDraw,
    matrix: np.ndarray,
    box: tuple[int, int, int, int],
    limit: float,
) -> None:
    rows, columns = matrix.shape
    x0, y0, x1, y1 = box
    cell_width = (x1 - x0) / columns
    cell_height = (y1 - y0) / rows
    for row in range(rows):
        for column in range(columns):
            value = float(matrix[row, column])
            strength = min(abs(value) / limit, 1.0) if limit else 0.0
            if value >= 0:
                base = (42, 97, 160)
            else:
                base = (194, 132, 32)
            colour = tuple(int(248 + (channel - 248) * strength) for channel in base)
            left = int(x0 + column * cell_width)
            top = int(y0 + row * cell_height)
            right = int(x0 + (column + 1) * cell_width)
            bottom = int(y0 + (row + 1) * cell_height)
            draw.rectangle((left, top, right, bottom), fill=colour)
    draw.rectangle(box, outline="#263238", width=2)


def make_figure(
    p23_residual: np.ndarray,
    p29_residual: np.ndarray,
    deformation: np.ndarray,
    transition_metrics: dict[str, float],
    down_summary: pd.DataFrame,
    path: Path,
) -> None:
    width, height = 2100, 1400
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        candidate = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
        return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()

    title = font(42, True)
    panel = font(27, True)
    body = font(22)
    small = font(18)
    ink = "#263238"
    muted = "#607078"
    draw.text((70, 45), "PN1G — prime-29 frozen transfer", fill=ink, font=title)
    draw.text(
        (70, 102),
        "Neutral orientation; blue = above Gap-Markov-1, gold = below",
        fill=muted,
        font=body,
    )
    matrices = (("Prime 23 residual", p23_residual), ("Prime 29 residual", p29_residual), ("23 → 29 deformation", deformation))
    limit = max(float(np.max(np.abs(matrix))) for _, matrix in matrices)
    boxes = ((70, 210, 590, 730), (680, 210, 1200, 730), (1290, 210, 1810, 730))
    for (label, matrix), box in zip(matrices, boxes):
        draw.text((box[0], 165), label, fill=ink, font=panel)
        draw_heatmap(draw, matrix, box, limit)
        draw.text((box[0], box[3] + 12), "ARA bin at i →", fill=muted, font=small)

    metrics_y = 800
    draw.text((70, metrics_y), "Frozen upward checks", fill=ink, font=panel)
    metric_lines = [
        f"Residual cosine: {transition_metrics['residual_cosine']:.6f}   (pass ≥ 0.98)",
        f"Residual L2: {transition_metrics['p29_residual_l2']:.6f}   (p23 {transition_metrics['p23_residual_l2']:.6f})",
        f"Deformation cosine: {transition_metrics['deformation_cosine']:.6f}   (pass ≥ 0.98)",
        f"Leading mode energy: {100*transition_metrics['leading_mode_energy']:.3f}%   (pass ≥ 95%)",
    ]
    for index, line in enumerate(metric_lines):
        draw.text((70, metrics_y + 55 + index * 42), line, fill=ink, font=body)

    draw.text((1040, metrics_y), "Prime-29 downward cross-entropy", fill=ink, font=panel)
    ordered = down_summary.sort_values("mean_cross_entropy_bits", ascending=True)
    chart = (1040, metrics_y + 55, 1990, 1305)
    max_ce = float(ordered.mean_cross_entropy_bits.max()) * 1.05
    row_height = (chart[3] - chart[1]) / len(ordered)
    for index, row in enumerate(ordered.itertuples()):
        y0 = int(chart[1] + index * row_height + 6)
        y1 = int(chart[1] + (index + 1) * row_height - 6)
        bar_start = chart[0] + 315
        bar_end = int(bar_start + row.mean_cross_entropy_bits / max_ce * (chart[2] - bar_start))
        draw.text((chart[0], y0 + 6), str(row.model).replace("_", " "), fill=ink, font=small)
        draw.rectangle((bar_start, y0, bar_end, y1), fill="#2A61A0", outline="#173B63")
        draw.text((bar_end + 8, y0 + 6), f"{row.mean_cross_entropy_bits:.4f}", fill=ink, font=small)
    draw.text((1040, 1340), "Lower is better; exact predicted ordering is scored separately.", fill=muted, font=small)
    image.save(path)


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
    return value


def main() -> dict[str, object]:
    started = time.perf_counter()
    if file_hash(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("Frozen PN1G protocol hash mismatch")
    pn1f = np.load(HERE / "PN1F_BIDIRECTIONAL_MATRICES.npz")
    core_primes = pn1f["core_primes"]
    p23_index = int(np.where(core_primes == SOURCE_PRIME)[0][0])

    # Mandatory known-rung rehearsal with the exact target streaming code.
    p19 = generate_wheel((2, 3, 5, 7, 11, 13, 17, 19))
    if p19.period != P19_PERIOD or len(p19.residues) != P19_SLOTS:
        raise AssertionError("Prime-19 source wheel mismatch")
    calibration, p23_residues = stream_child_wheel(
        p19.residues,
        P19_PERIOD,
        SOURCE_PRIME,
        P23_SLOTS,
        downward=False,
        collect_residues=True,
    )
    if p23_residues is None:
        raise AssertionError("Prime-23 parent residues were not collected")
    p23_gaps = np.diff(
        np.concatenate(
            (p23_residues.astype(np.int64), np.asarray([int(p23_residues[0]) + P23_PERIOD]))
        )
    ).astype(np.int32)
    direct_transition, direct_ordered12, direct_ordered24 = independent_counts_from_gaps(p23_gaps)
    calibration_checks = {
        "p23_period_matches": int(calibration["gap_sum"]) == P23_PERIOD,
        "p23_slot_count_matches": int(calibration["gap_count"]) == P23_SLOTS,
        "p23_gap_hash_matches": str(calibration["gap_sha256"]) == P23_GAP_SHA256,
        "p23_stream_vs_direct_gap_transition_exact": bool(np.array_equal(calibration["gap_transitions"], direct_transition)),
        "p23_stream_vs_direct_ordered12_exact": bool(np.array_equal(calibration["ordered_12_counts"], direct_ordered12)),
        "p23_stream_vs_direct_ordered24_exact": bool(np.array_equal(calibration["ordered_24_counts"], direct_ordered24)),
        "p23_ordered12_matches_pn1f": bool(np.allclose(normalize(calibration["ordered_12_counts"]), pn1f["ordered_12"][p23_index], atol=1e-15, rtol=0)),
        "p23_ordered24_matches_pn1f": bool(np.allclose(normalize(calibration["ordered_24_counts"]), pn1f["ordered_24"][-1], atol=1e-15, rtol=0)),
    }
    if not all(calibration_checks.values()):
        raise AssertionError(f"Prime-23 calibration failed: {calibration_checks}")
    del p23_gaps, direct_transition, direct_ordered12, direct_ordered24
    print("PN1G calibration passed; opening prime 29 now", flush=True)

    target, _ = stream_child_wheel(
        p23_residues,
        P23_PERIOD,
        TARGET_PRIME,
        P29_SLOTS,
        downward=True,
        collect_residues=False,
    )
    del p23_residues

    gap_counts = np.asarray(target["gap_counts"])
    gap_transition_full = np.asarray(target["gap_transitions"])
    labels = np.flatnonzero(gap_counts).astype(np.int32)
    marginal_counts = gap_counts[labels]
    transition_counts = gap_transition_full[np.ix_(labels, labels)]
    ordered12 = normalize(target["ordered_12_counts"])
    ordered24 = normalize(target["ordered_24_counts"])
    iid12, markov12 = projected_gap_planes(labels, marginal_counts, transition_counts, BINS)
    iid24, markov24 = projected_gap_planes(labels, marginal_counts, transition_counts, HIGH_BINS)
    residual12 = ordered12 - markov12
    residual24 = ordered24 - markov24

    p23_residual12 = pn1f["markov_residual_12"][p23_index]
    p23_residual24 = pn1f["markov_residual_24"][-1]
    deformation12 = residual12 - p23_residual12
    deformation24 = residual24 - p23_residual24
    previous_deformation12 = pn1f["deformation_12"][-1]
    previous_deformation24 = pn1f["markov_residual_24"][-1] - pn1f["markov_residual_24"][-2]
    all_deformations = np.concatenate((pn1f["deformation_12"], deformation12[None, :, :]), axis=0)
    singular_values = np.linalg.svd(all_deformations.reshape(len(all_deformations), -1), compute_uv=False)
    energy = singular_values**2
    energy /= energy.sum()
    all_deformations24 = np.concatenate(
        (
            np.diff(pn1f["markov_residual_24"], axis=0),
            deformation24[None, :, :],
        ),
        axis=0,
    )
    singular_values24 = np.linalg.svd(
        all_deformations24.reshape(len(all_deformations24), -1), compute_uv=False
    )
    energy24 = singular_values24**2
    energy24 /= energy24.sum()

    p23_norm = float(np.linalg.norm(p23_residual12))
    p29_norm = float(np.linalg.norm(residual12))
    transition_metrics = {
        "residual_cosine": cosine(p23_residual12, residual12),
        "p23_residual_l2": p23_norm,
        "p29_residual_l2": p29_norm,
        "deformation_l2": float(np.linalg.norm(deformation12)),
        "deformation_cosine": cosine(previous_deformation12, deformation12),
        "deformation_turn_degrees": float(np.degrees(np.arccos(np.clip(cosine(previous_deformation12, deformation12), -1, 1)))),
        "leading_mode_energy": float(energy[0]),
        "residual_cosine_24": cosine(p23_residual24, residual24),
        "deformation_cosine_24": cosine(previous_deformation24, deformation24),
        "leading_mode_energy_24": float(energy24[0]),
        "ordered_plane_jsd_bits": jsd_bits(pn1f["ordered_12"][p23_index], ordered12),
    }

    down_fold_scores, down_summary = downward_scores(target, labels)
    actual_order = down_summary.model.tolist()
    kendall = kendall_agreement(actual_order, FROZEN_ORDER)
    exact_order = actual_order == list(FROZEN_ORDER)
    base_by_fold = down_fold_scores[down_fold_scores.model == "current_B"].set_index("fold")["cross_entropy_bits"]
    all_positive_every_fold = True
    for name in FROZEN_ORDER[:-1]:
        candidate = down_fold_scores[down_fold_scores.model == name].set_index("fold")["cross_entropy_bits"]
        if not bool(np.all(base_by_fold.loc[candidate.index].to_numpy() - candidate.to_numpy() > 0)):
            all_positive_every_fold = False
            break

    centers = (np.arange(BINS) + 0.5) * 2 / BINS
    row_grid, column_grid = np.meshgrid(centers, centers, indexing="ij")
    delta = column_grid - row_grid
    target_metrics = {
        "period": P29_PERIOD,
        "slot_count": int(target["gap_count"]),
        "gap_sum": int(target["gap_sum"]),
        "gap_sha256": str(target["gap_sha256"]),
        "gap_alphabet": labels.tolist(),
        "gap_alphabet_size": len(labels),
        "maximum_gap": int(labels.max()),
        "ordered_entropy_bits": plane_entropy(ordered12),
        "ordered_adjacent_mi_bits": plane_mutual_information(ordered12),
        "ordered_vs_gap_iid_jsd_bits": jsd_bits(ordered12, iid12),
        "ordered_vs_gap_markov1_jsd_bits": jsd_bits(ordered12, markov12),
        "mean_signed_child_step": float(np.sum(ordered12 * delta)),
        "mean_absolute_child_step": float(np.sum(ordered12 * np.abs(delta))),
        "rising_share": float(ordered12[delta > 0].sum()),
        "equal_share": float(ordered12[delta == 0].sum()),
        "falling_share": float(ordered12[delta < 0].sum()),
    }

    frozen_checks = {
        "U1_residual_shape_cosine_at_least_0_98": transition_metrics["residual_cosine"] >= 0.98,
        "U2_residual_l2_continues_contracting": 0 < p29_norm < p23_norm,
        "U3_deformation_cosine_at_least_0_98": transition_metrics["deformation_cosine"] >= 0.98,
        "U4_leading_mode_energy_at_least_0_95": transition_metrics["leading_mode_energy"] >= 0.95,
        "D1_exact_model_order": exact_order,
        "D1_all_nonbase_positive_each_fold": all_positive_every_fold,
    }
    exact_checks = {
        "protocol_hash_matches": file_hash(PROTOCOL) == PROTOCOL_SHA256,
        "calibration_all_passed": all(calibration_checks.values()),
        "p29_period_matches": int(target["gap_sum"]) == P29_PERIOD,
        "p29_slot_count_matches": int(target["gap_count"]) == P29_SLOTS,
        "p29_gap_transition_count_closes": int(gap_transition_full.sum()) == P29_SLOTS,
        "p29_ordered12_count_closes": int(np.asarray(target["ordered_12_counts"]).sum()) == P29_SLOTS,
        "p29_ordered24_count_closes": int(np.asarray(target["ordered_24_counts"]).sum()) == P29_SLOTS,
        "p29_all_gaps_positive_even": bool(np.all(labels > 0) and np.all(labels % 2 == 0)),
        "p29_residuals_sum_to_zero": bool(abs(float(residual12.sum())) < 1e-12 and abs(float(residual24.sum())) < 1e-12),
    }
    if not all(exact_checks.values()):
        raise AssertionError(f"Target exact checks failed: {exact_checks}")

    down_fold_scores.to_csv(HERE / "PN1G_DOWNWARD_FOLD_SCORES.csv", index=False)
    down_summary.to_csv(HERE / "PN1G_DOWNWARD_MODEL_SUMMARY.csv", index=False)
    pd.DataFrame(
        [{"metric": key, "value": value} for key, value in transition_metrics.items()]
    ).to_csv(HERE / "PN1G_UPWARD_TRANSFER_METRICS.csv", index=False)
    pd.DataFrame(
        [{"check": key, "passed": value} for key, value in frozen_checks.items()]
    ).to_csv(HERE / "PN1G_FROZEN_CHECKS.csv", index=False)
    saved_arrays = {
        "gap_labels": labels,
        "gap_counts": marginal_counts,
        "gap_transition_counts": transition_counts,
        "ordered_12_counts": np.asarray(target["ordered_12_counts"]),
        "ordered_24_counts": np.asarray(target["ordered_24_counts"]),
        "ordered_12": ordered12,
        "gap_iid_12": iid12,
        "gap_markov1_12": markov12,
        "residual_12": residual12,
        "deformation_12": deformation12,
        "ordered_24": ordered24,
        "gap_iid_24": iid24,
        "gap_markov1_24": markov24,
        "residual_24": residual24,
        "deformation_24": deformation24,
        "all_deformations_12": all_deformations,
        "deformation_singular_values": singular_values,
        "deformation_energy_fractions": energy,
        "all_deformations_24": all_deformations24,
        "deformation_singular_values_24": singular_values24,
        "deformation_energy_fractions_24": energy24,
        "fold_boundaries": np.asarray(target["boundaries"]),
        "fold_raw_transition_full": np.asarray(target["fold_raw_transition"]),
        "guard_raw_transition_full": np.asarray(target["guard_raw_transition"]),
        "fold_raw_target_full": np.asarray(target["fold_raw_target"]),
    }
    target_fold_counts = target["fold_model_counts"]
    target_guard_counts = target["guard_model_counts"]
    if not isinstance(target_fold_counts, dict) or not isinstance(target_guard_counts, dict):
        raise AssertionError("Downward inventories unavailable for saved audit packet")
    for model_name in MODEL_WIDTHS:
        saved_arrays[f"fold_model__{model_name}"] = np.asarray(target_fold_counts[model_name])
        saved_arrays[f"guard_model__{model_name}"] = np.asarray(target_guard_counts[model_name])
    np.savez_compressed(
        HERE / "PN1G_PRIME29_COUNTS_AND_MATRICES.npz",
        **saved_arrays,
    )
    make_figure(
        p23_residual12,
        residual12,
        deformation12,
        transition_metrics,
        down_summary,
        HERE / "PN1G_PRIME29_TRANSFER_FIGURE.png",
    )

    result = {
        "test_id": "PN1G/TRANSFER/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FROZEN NEXT-RUNG TRANSFER TEST — TARGET NOW OPEN",
        "protocol_sha256": PROTOCOL_SHA256,
        "source_prime": SOURCE_PRIME,
        "target_prime": TARGET_PRIME,
        "prime29_opened": True,
        "calibration_checks": calibration_checks,
        "exact_checks": exact_checks,
        "frozen_checks": frozen_checks,
        "frozen_check_pass_count": int(sum(frozen_checks.values())),
        "frozen_check_total": len(frozen_checks),
        "upward_transfer": transition_metrics,
        "downward_transfer": {
            "predicted_order": list(FROZEN_ORDER),
            "actual_order": actual_order,
            "exact_order_match": exact_order,
            "kendall_tau": kendall,
            "all_nonbase_positive_each_fold": all_positive_every_fold,
            "mean_scores": down_summary.to_dict(orient="records"),
        },
        "target_metrics": target_metrics,
        "runtime_seconds": time.perf_counter() - started,
        "software": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    (HERE / "PN1G_RESULTS.json").write_text(
        json.dumps(json_safe(result), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(json_safe(result), indent=2, allow_nan=False), flush=True)
    return result


if __name__ == "__main__":
    main()
