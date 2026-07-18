"""Independent reconstruction and validation for T228 / PN1C/v1.

This deliberately does not import pn1c_compression_test.py.  It builds reduced
residues by repeated array filtering, stores the complete child gap cycle, and
counts circular triples in indexed chunks.  That route is materially different
from the primary lift-stream accumulator.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1C_COMPRESSION_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "PN1C_COMPRESSION_RESULTS.json"
ARCHIVE = HERE / "PN1C_TARGET_AND_PREDICTIONS.npz"
SCORES = HERE / "PN1C_MODEL_SCORES.csv"
OUTPUT = HERE / "PN1C_INDEPENDENT_VALIDATION.json"
PROTOCOL_SHA256 = "7DAA061BA790B12461ED60136FD9C50F3A36C10BED472819CFCC08B4B3462DBF"
PARENT_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19)
NEXT_PRIME = 23
PARENT_PERIOD = 9_699_690
CHILD_PERIOD = 223_092_870
CHILD_SLOTS = 36_495_360
FINE_BINS = 24
COUNT_CHUNK = 1_000_000


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def reduced_residues(primes: tuple[int, ...]) -> tuple[int, np.ndarray]:
    period = math.prod(primes)
    residues = np.arange(1, period, dtype=np.int64)
    for prime in primes:
        residues = residues[residues % prime != 0]
    return period, residues


def circular_gaps(period: int, residues: np.ndarray) -> np.ndarray:
    gaps = np.empty(len(residues), dtype=np.int32)
    gaps[:-1] = np.diff(residues).astype(np.int32)
    gaps[-1] = period + int(residues[0]) - int(residues[-1])
    return gaps


def child_gap_cycle(parent_residues: np.ndarray) -> np.ndarray:
    gaps = np.empty(CHILD_SLOTS, dtype=np.int32)
    cursor = 0
    first: int | None = None
    previous: int | None = None
    for lift in range(NEXT_PRIME):
        candidates = parent_residues + lift * PARENT_PERIOD
        survivors = candidates[candidates % NEXT_PRIME != 0]
        if first is None:
            first = int(survivors[0])
            local = np.diff(survivors).astype(np.int32)
        else:
            local = np.empty(len(survivors), dtype=np.int32)
            local[0] = int(survivors[0]) - int(previous)
            local[1:] = np.diff(survivors).astype(np.int32)
        gaps[cursor : cursor + len(local)] = local
        cursor += len(local)
        previous = int(survivors[-1])
    if first is None or previous is None:
        raise AssertionError("No child survivors")
    gaps[cursor] = CHILD_PERIOD + first - previous
    cursor += 1
    if cursor != CHILD_SLOTS:
        raise AssertionError(f"Independent gap count {cursor} != {CHILD_SLOTS}")
    return gaps


def gap_hash(gaps: np.ndarray) -> str:
    digest = hashlib.sha256()
    for start in range(0, len(gaps), COUNT_CHUNK):
        digest.update(gaps[start : start + COUNT_CHUNK].tobytes(order="C"))
    return digest.hexdigest().upper()


def relation_bins(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    coordinate = 2.0 * right.astype(np.float64) / (
        left.astype(np.float64) + right.astype(np.float64)
    )
    return np.minimum((coordinate * (FINE_BINS / 2.0)).astype(np.int64), FINE_BINS - 1)


def count_range(gaps: np.ndarray, start: int, stop: int) -> np.ndarray:
    counts = np.zeros((FINE_BINS, FINE_BINS), dtype=np.int64)
    size = len(gaps)
    for chunk_start in range(start, stop, COUNT_CHUNK):
        chunk_stop = min(chunk_start + COUNT_CHUNK, stop)
        index = np.arange(chunk_start, chunk_stop, dtype=np.int64)
        first = np.take(gaps, index % size)
        second = np.take(gaps, (index + 1) % size)
        third = np.take(gaps, (index + 2) % size)
        row = relation_bins(first, second)
        column = relation_bins(second, third)
        counts += np.bincount(
            row * FINE_BINS + column, minlength=FINE_BINS**2
        ).reshape(FINE_BINS, FINE_BINS)
    return counts


def normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    return values / values.sum()


def jsd_bits(first: np.ndarray, second: np.ndarray) -> float:
    first = normalize(first.ravel())
    second = normalize(second.ravel())
    midpoint = 0.5 * (first + second)

    def kl(values: np.ndarray) -> float:
        active = values > 0
        return float(np.sum(values[active] * np.log2(values[active] / midpoint[active])))

    return 0.5 * kl(first) + 0.5 * kl(second)


def pair_jsd(target: np.ndarray, prediction: np.ndarray) -> float:
    return 0.5 * (
        jsd_bits(target.sum(axis=0), prediction.sum(axis=0))
        + jsd_bits(target.sum(axis=1), prediction.sum(axis=1))
    )


def decode(parent: np.ndarray, assignment: np.ndarray, groups: int) -> np.ndarray:
    parent = normalize(parent)
    coarse = np.zeros((groups, groups), dtype=np.float64)
    np.add.at(
        coarse,
        (assignment[:, None], assignment[None, :]),
        parent,
    )
    sizes = np.bincount(assignment, minlength=groups)
    decoded = np.empty_like(parent)
    for row in range(FINE_BINS):
        for column in range(FINE_BINS):
            decoded[row, column] = coarse[assignment[row], assignment[column]] / (
                sizes[assignment[row]] * sizes[assignment[column]]
            )
    return normalize(decoded)


def parent_relation(gaps: np.ndarray) -> np.ndarray:
    return count_range(gaps, 0, len(gaps))


def dct_prediction(parent: np.ndarray, retained: int) -> np.ndarray:
    points = np.arange(FINE_BINS, dtype=np.float64)
    frequencies = np.arange(FINE_BINS, dtype=np.float64)[:, None]
    basis = np.cos(math.pi * (points + 0.5) * frequencies / FINE_BINS)
    basis[0] *= math.sqrt(1.0 / FINE_BINS)
    basis[1:] *= math.sqrt(2.0 / FINE_BINS)
    coefficients = basis @ normalize(parent) @ basis.T
    coefficients[retained:, :] = 0.0
    coefficients[:, retained:] = 0.0
    decoded = np.clip(basis.T @ coefficients @ basis, 0.0, None)
    return normalize(decoded)


def gap_process_models(gaps: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[tuple[int, int, int, float]]]:
    labels, inverse, counts = np.unique(gaps, return_inverse=True, return_counts=True)
    alphabet = len(labels)
    marginal = counts.astype(np.float64) / len(gaps)
    following = np.roll(inverse, -1)
    transition_counts = np.bincount(
        inverse * alphabet + following, minlength=alphabet**2
    ).reshape(alphabet, alphabet)
    transition = transition_counts / transition_counts.sum(axis=1, keepdims=True)

    def project(markov: bool) -> np.ndarray:
        output = np.zeros((FINE_BINS, FINE_BINS), dtype=np.float64)
        for ia, a in enumerate(labels):
            for ib, b in enumerate(labels):
                ab = marginal[ia] * (transition[ia, ib] if markov else marginal[ib])
                for ic, c in enumerate(labels):
                    probability = ab * (transition[ib, ic] if markov else marginal[ic])
                    row = min(int((2.0 * b / (a + b)) * FINE_BINS / 2.0), FINE_BINS - 1)
                    column = min(int((2.0 * c / (b + c)) * FINE_BINS / 2.0), FINE_BINS - 1)
                    output[row, column] += probability
        return normalize(output)

    codes = inverse * alphabet**2 + np.roll(inverse, -1) * alphabet + np.roll(inverse, -2)
    triple_counts = np.bincount(codes, minlength=alphabet**3)
    order = np.lexsort((np.arange(len(triple_counts)), -triple_counts))[:9]
    selected = triple_counts[order].astype(np.float64) / len(gaps)
    constellation = np.full(
        (FINE_BINS, FINE_BINS), (1.0 - selected.sum()) / FINE_BINS**2
    )
    details: list[tuple[int, int, int, float]] = []
    for code, probability in zip(order, selected, strict=True):
        ia = int(code // alphabet**2)
        remainder = int(code % alphabet**2)
        ib, ic = divmod(remainder, alphabet)
        a, b, c = int(labels[ia]), int(labels[ib]), int(labels[ic])
        row = min(int((2.0 * b / (a + b)) * FINE_BINS / 2.0), FINE_BINS - 1)
        column = min(int((2.0 * c / (b + c)) * FINE_BINS / 2.0), FINE_BINS - 1)
        constellation[row, column] += probability
        details.append((a, b, c, float(probability)))
    return project(False), project(True), normalize(constellation), details


def learned_assignment() -> tuple[np.ndarray, list[int]]:
    pooled = np.zeros((FINE_BINS, FINE_BINS), dtype=np.int64)
    for final_prime in (13, 17, 19):
        primes = PARENT_PRIMES[: PARENT_PRIMES.index(final_prime) + 1]
        period, residues = reduced_residues(primes)
        pooled += parent_relation(circular_gaps(period, residues))
    weights = pooled.sum(axis=0) + pooled.sum(axis=1)
    cumulative = np.cumsum(weights, dtype=np.float64) / weights.sum()
    cuts: list[int] = []
    previous = 0
    groups = 5
    for group_index in range(1, groups):
        raw = int(np.searchsorted(cumulative, group_index / groups, side="left") + 1)
        cut = min(max(raw, previous + 1), FINE_BINS - (groups - group_index))
        cuts.append(cut)
        previous = cut
    return np.digitize(np.arange(FINE_BINS), cuts), cuts


def prediction_key(model: str) -> str:
    return "prediction_" + model.replace(" ", "_").replace("-", "_")


def main() -> None:
    checks: dict[str, bool] = {}
    checks["protocol_hash_matches"] = file_hash(PROTOCOL) == PROTOCOL_SHA256
    period, parent_residues = reduced_residues(PARENT_PRIMES)
    checks["parent_period_exact"] = period == PARENT_PERIOD
    checks["parent_residue_count_exact"] = len(parent_residues) == 1_658_880
    parent_gaps = circular_gaps(period, parent_residues)
    checks["parent_gap_sum_exact"] = int(parent_gaps.sum(dtype=np.int64)) == PARENT_PERIOD

    child_gaps = child_gap_cycle(parent_residues)
    checks["child_gap_count_exact"] = len(child_gaps) == CHILD_SLOTS
    checks["child_gap_sum_exact"] = int(child_gaps.sum(dtype=np.int64)) == CHILD_PERIOD
    checks["child_gaps_positive_even"] = bool(
        np.all(child_gaps > 0) and np.all(child_gaps % 2 == 0)
    )
    child_hash = gap_hash(child_gaps)
    target_counts = count_range(child_gaps, 0, CHILD_SLOTS)
    midpoint = CHILD_SLOTS // 2
    half_counts = np.stack(
        (count_range(child_gaps, 0, midpoint), count_range(child_gaps, midpoint, CHILD_SLOTS))
    )

    with np.load(ARCHIVE) as archive:
        saved = {key: archive[key] for key in archive.files}
    checks["target_counts_equal_archive"] = np.array_equal(target_counts, saved["target_counts"])
    checks["half_counts_equal_archive"] = np.array_equal(half_counts, saved["target_half_counts"])
    checks["parent_counts_equal_archive"] = np.array_equal(
        parent_relation(parent_gaps), saved["parent_counts"]
    )

    parent_counts = parent_relation(parent_gaps)
    ara_assignment = np.arange(FINE_BINS) * 6 // FINE_BINS
    centers = 2.0 * (np.arange(FINE_BINS) + 0.5) / FINE_BINS
    log_values = np.log(centers / (2.0 - centers))
    log_edges = math.log(32.0) * (2.0 * np.arange(1, 6) / 6.0 - 1.0)
    log_assignment = np.digitize(log_values, log_edges)
    learned, learned_cuts = learned_assignment()
    iid, markov, constellation, constellation_details = gap_process_models(parent_gaps)
    independent_predictions = {
        "ARA-linear-6": decode(parent_counts, ara_assignment, 6),
        "Log-ratio-6": decode(parent_counts, log_assignment, 6),
        "DCT-6": dct_prediction(parent_counts, 6),
        "Learned-quantile-5": decode(parent_counts, learned, 5),
        "Gap-IID": iid,
        "Top-9 constellations": constellation,
        "Uniform": np.full((FINE_BINS, FINE_BINS), 1.0 / FINE_BINS**2),
        "Gap-Markov": markov,
        "Exact parent relation": normalize(parent_counts),
    }
    prediction_errors = {
        model: float(np.max(np.abs(prediction - saved[prediction_key(model)])))
        for model, prediction in independent_predictions.items()
    }
    checks["all_predictions_reconstructed"] = max(prediction_errors.values()) <= 2e-15

    target_probability = normalize(target_counts)
    score_table = pd.read_csv(SCORES)
    metric_errors: dict[str, dict[str, float]] = {}
    for _, row in score_table.iterrows():
        model = str(row["model"])
        prediction = independent_predictions[model]
        metric_errors[model] = {
            "jsd_bits": abs(jsd_bits(target_probability, prediction) - float(row["jsd_bits"])),
            "pair_jsd_mean_bits": abs(
                pair_jsd(target_probability, prediction) - float(row["pair_jsd_mean_bits"])
            ),
        }
    max_metric_error = max(
        value for model_errors in metric_errors.values() for value in model_errors.values()
    )
    checks["all_metrics_recomputed"] = max_metric_error <= 2e-15

    with RESULTS.open("r", encoding="utf-8") as handle:
        results = json.load(handle)
    checks["gap_hash_matches_results"] = child_hash == results["target"]["gap_sha256"]
    eligible = score_table[score_table["eligible_primary"]].sort_values("jsd_bits")
    independent_winner = str(eligible.iloc[0]["model"])
    checks["primary_winner_recovered"] = independent_winner == "Gap-IID"
    checks["primary_failure_recovered"] = not bool(results["summary"]["primary_claim_pass"])

    validation = {
        "test_id": "T228 / PN1C/v1 independent validation",
        "method": (
            "Standalone repeated-modulus residue filtering; materialized child gap cycle; "
            "indexed circular chunk counts; standalone model and metric reconstruction."
        ),
        "protocol_sha256": file_hash(PROTOCOL),
        "target_gap_sha256": child_hash,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "max_prediction_abs_error": max(prediction_errors.values()),
        "prediction_abs_errors": prediction_errors,
        "max_metric_abs_error": max_metric_error,
        "metric_abs_errors": metric_errors,
        "learned_boundary_bins": learned_cuts,
        "top_constellations": constellation_details,
        "independent_primary_winner": independent_winner,
        "script_sha256": file_hash(Path(__file__)),
    }
    with OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(validation, handle, indent=2, allow_nan=False)
    print(json.dumps(validation, indent=2))
    if not validation["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
