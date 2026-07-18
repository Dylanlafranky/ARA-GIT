"""Independent reconstruction and validation for PN1E/DEV/v1.

This script does not import the PN1E primary analysis. Prime 29 is untouched.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1E_THIRD_MEMORY_EFFECTIVENESS_PROTOCOL.md"
PRIMARY_RESULTS = HERE / "PN1E_RESULTS.json"
PRIMARY_SCORES = HERE / "PN1E_EFFECTIVENESS_SCORES.csv"
OUTPUT = HERE / "PN1E_INDEPENDENT_VALIDATION.json"
PROTOCOL_SHA256 = "484B45190DCDC3823CDF6B2F644FCC87FCD925DA22B45321D2C334E56B8C77EB"
GAP_SHA256 = "F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C"
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19)
NEXT_PRIME = 23
PARENT_PERIOD = 9_699_690
CHILD_PERIOD = 223_092_870
CHILD_SLOTS = 36_495_360
ALPHA = 0.5
CHUNK = 600_000


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def reduced_residues() -> np.ndarray:
    period = math.prod(PRIMES)
    residues = np.arange(1, period, dtype=np.int64)
    for prime in PRIMES:
        residues = residues[residues % prime != 0]
    return residues


def child_gaps(parent: np.ndarray) -> np.ndarray:
    output = np.empty(CHILD_SLOTS, dtype=np.int32)
    cursor = 0
    first = None
    previous = None
    for lift in range(NEXT_PRIME):
        candidates = parent + lift * PARENT_PERIOD
        survivors = candidates[candidates % NEXT_PRIME != 0]
        if first is None:
            first = int(survivors[0])
            local = np.diff(survivors).astype(np.int32)
        else:
            local = np.empty(len(survivors), dtype=np.int32)
            local[0] = int(survivors[0]) - int(previous)
            local[1:] = np.diff(survivors).astype(np.int32)
        output[cursor : cursor + len(local)] = local
        cursor += len(local)
        previous = int(survivors[-1])
    if first is None or previous is None:
        raise AssertionError("No survivors")
    output[cursor] = CHILD_PERIOD + first - previous
    cursor += 1
    if cursor != CHILD_SLOTS:
        raise AssertionError(f"Child length {cursor} != {CHILD_SLOTS}")
    return output


def array_hash(values: np.ndarray) -> str:
    digest = hashlib.sha256()
    for start in range(0, len(values), CHUNK):
        digest.update(values[start : start + CHUNK].tobytes(order="C"))
    return digest.hexdigest().upper()


def relation_sequence(gaps: np.ndarray, bins: int) -> np.ndarray:
    size = len(gaps)
    following = np.roll(gaps, -1)
    coordinate = 2.0 * following.astype(np.float64) / (
        gaps.astype(np.float64) + following.astype(np.float64)
    )
    return np.minimum((coordinate * bins / 2.0).astype(np.int64), bins - 1).astype(np.uint8)


def fit_models(train: np.ndarray, bins: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    marginal_counts = np.bincount(train, minlength=bins).astype(np.float64)
    pair = np.zeros((bins, bins), dtype=np.float64)
    triple = np.zeros((bins, bins, bins), dtype=np.float64)
    for start in range(0, len(train) - 2, CHUNK):
        stop = min(start + CHUNK, len(train) - 2)
        a = train[start:stop].astype(np.int64)
        b = train[start + 1 : stop + 1].astype(np.int64)
        c = train[start + 2 : stop + 2].astype(np.int64)
        pair += np.bincount(b * bins + c, minlength=bins**2).reshape(bins, bins)
        triple += np.bincount(a * bins * bins + b * bins + c, minlength=bins**3).reshape(bins, bins, bins)
    marginal = (marginal_counts + ALPHA) / (marginal_counts.sum() + ALPHA * bins)
    first = (pair + ALPHA) / (pair.sum(axis=1, keepdims=True) + ALPHA * bins)
    second = (triple + ALPHA) / (triple.sum(axis=2, keepdims=True) + ALPHA * bins)
    return marginal, first, second


def score(test: np.ndarray, probabilities: tuple[np.ndarray, np.ndarray, np.ndarray]) -> dict[str, dict[str, float]]:
    marginal, first, second = probabilities
    names = ("ARA-IID", "ARA-Markov-1", "ARA-Markov-2")
    totals = {name: {"loss": 0.0, "brier": 0.0, "top1": 0, "top3": 0} for name in names}
    n = len(test) - 2
    for start in range(2, len(test), CHUNK):
        stop = min(start + CHUNK, len(test))
        target = test[start:stop].astype(np.int64)
        previous = test[start - 1 : stop - 1].astype(np.int64)
        earlier = test[start - 2 : stop - 2].astype(np.int64)
        matrices = {
            "ARA-IID": np.broadcast_to(marginal, (len(target), len(marginal))),
            "ARA-Markov-1": first[previous],
            "ARA-Markov-2": second[earlier, previous],
        }
        for name, matrix in matrices.items():
            actual = matrix[np.arange(len(target)), target]
            totals[name]["loss"] += float(-np.log2(actual).sum())
            totals[name]["brier"] += float(np.sum(matrix**2) - 2 * actual.sum() + len(target))
            totals[name]["top1"] += int(np.sum(np.argmax(matrix, axis=1) == target))
            top3 = np.argpartition(matrix, -3, axis=1)[:, -3:]
            totals[name]["top3"] += int(np.sum(np.any(top3 == target[:, None], axis=1)))
    return {
        name: {
            "cross_entropy_bits_per_reading": values["loss"] / n,
            "perplexity": 2.0 ** (values["loss"] / n),
            "brier_score": values["brier"] / n,
            "top1_accuracy": values["top1"] / n,
            "top3_accuracy": values["top3"] / n,
            "observations": n,
        }
        for name, values in totals.items()
    }


def tensor(values: np.ndarray, bins: int) -> np.ndarray:
    code = (
        values.astype(np.int64) * bins * bins
        + np.roll(values, -1).astype(np.int64) * bins
        + np.roll(values, -2).astype(np.int64)
    )
    counts = np.bincount(code, minlength=bins**3).reshape(bins, bins, bins)
    return counts.astype(np.float64) / len(values)


def entropy(probability: np.ndarray) -> float:
    probability = probability.ravel()
    active = probability > 0
    return float(-np.sum(probability[active] * np.log2(probability[active])))


def cmi_and_contexts(probability: np.ndarray) -> tuple[float, np.ndarray]:
    p_ab = probability.sum(axis=2)
    p_bc = probability.sum(axis=0)
    p_b = probability.sum(axis=(0, 2))
    contributions = np.zeros_like(p_ab)
    for a in range(probability.shape[0]):
        for b in range(probability.shape[1]):
            if p_ab[a, b] == 0:
                continue
            two = probability[a, b] / p_ab[a, b]
            one = p_bc[b] / p_b[b]
            active = two > 0
            contributions[a, b] = p_ab[a, b] * np.sum(two[active] * np.log2(two[active] / one[active]))
    return float(contributions.sum()), contributions


def raw_contribution_summary(gaps: np.ndarray, probability: np.ndarray) -> dict[str, object]:
    labels = np.unique(gaps)
    alphabet = len(labels)
    lookup = np.full(int(gaps.max()) + 1, 255, dtype=np.uint8)
    lookup[labels.astype(np.int64)] = np.arange(alphabet, dtype=np.uint8)
    inverse = lookup[gaps]
    counts = np.zeros(alphabet**4, dtype=np.int64)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        code = (
            np.take(inverse, index).astype(np.int64) * alphabet**3
            + np.take(inverse, (index + 1) % size).astype(np.int64) * alphabet**2
            + np.take(inverse, (index + 2) % size).astype(np.int64) * alphabet
            + np.take(inverse, (index + 3) % size).astype(np.int64)
        )
        counts += np.bincount(code, minlength=alphabet**4)

    p_ab = probability.sum(axis=2)
    p_bc = probability.sum(axis=0)
    p_b = probability.sum(axis=(0, 2))
    two = np.divide(
        probability,
        p_ab[:, :, None],
        out=np.zeros_like(probability),
        where=p_ab[:, :, None] > 0,
    )
    one = np.divide(
        p_bc,
        p_b[:, None],
        out=np.zeros_like(p_bc),
        where=p_b[:, None] > 0,
    )
    positive = 0.0
    negative = 0.0
    best = None
    best_value = -math.inf
    for code in np.flatnonzero(counts):
        remainder = int(code)
        i0, remainder = divmod(remainder, alphabet**3)
        i1, remainder = divmod(remainder, alphabet**2)
        i2, i3 = divmod(remainder, alphabet)
        raw = tuple(int(labels[i]) for i in (i0, i1, i2, i3))
        bins = []
        for left, right in zip(raw[:-1], raw[1:]):
            coordinate = 2.0 * right / (left + right)
            bins.append(min(int(coordinate * 6), 11))
        local = math.log2(two[bins[0], bins[1], bins[2]] / one[bins[1], bins[2]])
        contribution = int(counts[code]) / size * local
        if contribution > 0:
            positive += contribution
        else:
            negative += contribution
        if contribution > best_value:
            best_value = contribution
            best = raw
    return {
        "positive_bits": positive,
        "negative_bits": negative,
        "net_bits": positive + negative,
        "top_quadruple": list(best) if best is not None else None,
        "top_contribution_bits": best_value,
    }


def main() -> None:
    primary = json.loads(PRIMARY_RESULTS.read_text(encoding="utf-8"))
    primary_scores = pd.read_csv(PRIMARY_SCORES)
    gaps = child_gaps(reduced_residues())
    midpoint = len(gaps) // 2
    reconstructed_rows = []
    for bins in (8, 12, 16):
        values = relation_sequence(gaps, bins)
        directions = (
            ("half1_to_half2", values[:midpoint], values[midpoint:]),
            ("half2_to_half1", values[midpoint:], values[:midpoint]),
        )
        local = []
        for direction, train, test in directions:
            scored = score(test, fit_models(train, bins))
            for model, metrics in scored.items():
                row = {"bins": bins, "direction": direction, "model": model, **metrics}
                reconstructed_rows.append(row)
                local.append(row)
        for model in ("ARA-IID", "ARA-Markov-1", "ARA-Markov-2"):
            selected = [row for row in local if row["model"] == model]
            reconstructed_rows.append({
                "bins": bins,
                "direction": "mean",
                "model": model,
                **{
                    key: float(np.mean([float(row[key]) for row in selected]))
                    for key in (
                        "cross_entropy_bits_per_reading", "perplexity", "brier_score",
                        "top1_accuracy", "top3_accuracy", "observations"
                    )
                },
            })
    reconstructed = pd.DataFrame(reconstructed_rows).sort_values(["bins", "direction", "model"]).reset_index(drop=True)
    expected = primary_scores.sort_values(["bins", "direction", "model"]).reset_index(drop=True)
    numeric = [
        "cross_entropy_bits_per_reading", "perplexity", "brier_score",
        "top1_accuracy", "top3_accuracy", "observations"
    ]
    score_error = float(np.max(np.abs(reconstructed[numeric].to_numpy() - expected[numeric].to_numpy())))

    primary_sequence = relation_sequence(gaps, 12)
    probability = tensor(primary_sequence, 12)
    cmi, contributions = cmi_and_contexts(probability)
    raw = raw_contribution_summary(gaps, probability)
    reported = primary["attribution"]
    checks = {
        "protocol_hash_exact": file_hash(PROTOCOL) == PROTOCOL_SHA256,
        "prime29_remains_unopened": primary["data"]["prime29_opened"] is False,
        "gap_count_exact": len(gaps) == CHILD_SLOTS,
        "gap_period_exact": int(gaps.sum(dtype=np.int64)) == CHILD_PERIOD,
        "gap_hash_exact": array_hash(gaps) == GAP_SHA256,
        "all_primary_scores_reproduced": score_error < 1e-12,
        "empirical_cmi_reproduced": abs(cmi - reported["net_quadruple_contribution_bits"]) < 1e-12,
        "context_sum_equals_cmi": abs(float(contributions.sum()) - cmi) < 1e-12,
        "raw_sum_equals_cmi": abs(float(raw["net_bits"]) - cmi) < 1e-12,
        "positive_raw_mass_reproduced": abs(float(raw["positive_bits"]) - reported["positive_quadruple_contribution_bits"]) < 1e-12,
        "negative_raw_mass_reproduced": abs(float(raw["negative_bits"]) - reported["negative_quadruple_contribution_bits"]) < 1e-12,
        "top_quadruple_reproduced": raw["top_quadruple"] == [2, 4, 8, 6],
    }
    result = {
        "protocol": "PN1E/DEV/v1",
        "independent_route": "standalone p23 construction, vectorized relation encoding, direct held-out categorical scoring, event-count raw attribution",
        "prime29_opened": False,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "maximum_primary_score_absolute_error": score_error,
        "empirical_cmi_bits": cmi,
        "raw_attribution": raw,
        "interpretive_limit": "Confirms predictive usefulness on p23 development data, not exactly three waves or transfer to p29.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))
    if not result["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
