"""Independent validation for PN1D/DEV/v1.

This file deliberately does not import the PN1D development script.  It
reconstructs the prime-23 wheel, relation sequence, model tensors and scale
strata through a separate implementation.  It also cross-checks the spatial
rank result with held-out truncated SVD rather than the primary NMF routine.
Prime 29 is never constructed or read.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1D_THIRD_COMPONENT_DEVELOPMENT_PROTOCOL.md"
PRIMARY = HERE / "PN1D_RESULTS.json"
MATRICES = HERE / "PN1D_MATRICES.npz"
OUTPUT = HERE / "PN1D_INDEPENDENT_VALIDATION.json"
SVD_OUTPUT = HERE / "PN1D_INDEPENDENT_SVD_CROSSFIT.csv"

PROTOCOL_SHA256 = "9D6F2EFC3774B84F04AFBCCEBD0782F3B02F62A53A783712408112F5642A60DF"
GAP_SHA256 = "F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C"
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19)
NEXT_PRIME = 23
PARENT_PERIOD = 9_699_690
CHILD_PERIOD = 223_092_870
CHILD_SLOTS = 36_495_360
PLANE_BINS = 24
SEQUENCE_BINS = 12
CHUNK = 750_000


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def reduced_residues() -> np.ndarray:
    residues = np.arange(1, math.prod(PRIMES), dtype=np.int64)
    for prime in PRIMES:
        residues = residues[residues % prime != 0]
    return residues


def construct_child_gaps(parent: np.ndarray) -> np.ndarray:
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
        raise AssertionError("No child residues")
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


def normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    total = float(values.sum())
    if total <= 0:
        raise ValueError("Cannot normalize empty mass")
    return values / total


def relation_bins(left: np.ndarray | int, right: np.ndarray | int, bins: int) -> np.ndarray:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    position = 2.0 * right / (left + right)
    return np.minimum((position * bins / 2.0).astype(np.int64), bins - 1)


def relation_sequence(gaps: np.ndarray, bins: int) -> np.ndarray:
    size = len(gaps)
    output = np.empty(size, dtype=np.uint8)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        output[start:stop] = relation_bins(
            np.take(gaps, index), np.take(gaps, (index + 1) % size), bins
        ).astype(np.uint8)
    return output


def plane_counts(values: np.ndarray, start: int, stop: int) -> np.ndarray:
    counts = np.zeros((PLANE_BINS, PLANE_BINS), dtype=np.int64)
    size = len(values)
    for chunk_start in range(start, stop, CHUNK):
        chunk_stop = min(chunk_start + CHUNK, stop)
        index = np.arange(chunk_start, chunk_stop, dtype=np.int64)
        row = np.take(values, index % size).astype(np.int64)
        column = np.take(values, (index + 1) % size).astype(np.int64)
        counts += np.bincount(
            row * PLANE_BINS + column, minlength=PLANE_BINS**2
        ).reshape(PLANE_BINS, PLANE_BINS)
    return counts


def sequence_tensor(values: np.ndarray, start: int, stop: int) -> np.ndarray:
    counts = np.zeros((SEQUENCE_BINS, SEQUENCE_BINS, SEQUENCE_BINS), dtype=np.int64)
    size = len(values)
    for chunk_start in range(start, stop, CHUNK):
        chunk_stop = min(chunk_start + CHUNK, stop)
        index = np.arange(chunk_start, chunk_stop, dtype=np.int64)
        a = np.take(values, index % size).astype(np.int64)
        b = np.take(values, (index + 1) % size).astype(np.int64)
        c = np.take(values, (index + 2) % size).astype(np.int64)
        code = a * SEQUENCE_BINS**2 + b * SEQUENCE_BINS + c
        counts += np.bincount(code, minlength=SEQUENCE_BINS**3).reshape(
            SEQUENCE_BINS, SEQUENCE_BINS, SEQUENCE_BINS
        )
    return counts


def cmi_bits(values: np.ndarray) -> float:
    p = normalize(values)
    pab = p.sum(axis=2)
    pbc = p.sum(axis=0)
    pb = p.sum(axis=(0, 2))
    expected = pab[:, :, None] * pbc[None, :, :] / pb[None, :, None]
    active = p > 0
    return float(np.sum(p[active] * np.log2(p[active] / expected[active])))


def jsd_bits(first: np.ndarray, second: np.ndarray) -> float:
    first = normalize(first.ravel())
    second = normalize(second.ravel())
    midpoint = 0.5 * (first + second)

    def kl(values: np.ndarray) -> float:
        active = values > 0
        return float(np.sum(values[active] * np.log2(values[active] / midpoint[active])))

    return 0.5 * kl(first) + 0.5 * kl(second)


def gap_model_tensor(
    labels: np.ndarray,
    marginal: np.ndarray,
    transition: np.ndarray | None,
) -> np.ndarray:
    """Project four successive gap states into three successive ARA relations."""
    output = np.zeros((SEQUENCE_BINS,) * 3, dtype=np.float64)
    for ia, a in enumerate(labels):
        for ib, b in enumerate(labels):
            pab = marginal[ia] * (marginal[ib] if transition is None else transition[ia, ib])
            if pab == 0:
                continue
            x0 = int(relation_bins(int(a), int(b), SEQUENCE_BINS))
            for ic, c in enumerate(labels):
                pabc = pab * (marginal[ic] if transition is None else transition[ib, ic])
                if pabc == 0:
                    continue
                x1 = int(relation_bins(int(b), int(c), SEQUENCE_BINS))
                for id_value, d in enumerate(labels):
                    probability = pabc * (
                        marginal[id_value] if transition is None else transition[ic, id_value]
                    )
                    if probability:
                        x2 = int(relation_bins(int(c), int(d), SEQUENCE_BINS))
                        output[x0, x1, x2] += probability
    return normalize(output)


def exact_gap_models(gaps: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    labels, inverse, counts = np.unique(gaps, return_inverse=True, return_counts=True)
    alphabet = len(labels)
    marginal = counts.astype(np.float64) / len(gaps)
    following = np.roll(inverse, -1)
    transition_counts = np.bincount(
        inverse * alphabet + following, minlength=alphabet**2
    ).reshape(alphabet, alphabet)
    transition = transition_counts / transition_counts.sum(axis=1, keepdims=True)
    return (
        gap_model_tensor(labels, marginal, None),
        gap_model_tensor(labels, marginal, transition),
    )


def span_boundaries(gaps: np.ndarray) -> tuple[int, int]:
    histogram = np.zeros(512, dtype=np.int64)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        spans = (
            np.take(gaps, index).astype(np.int64)
            + np.take(gaps, (index + 1) % size).astype(np.int64)
            + np.take(gaps, (index + 2) % size).astype(np.int64)
        )
        histogram += np.bincount(spans, minlength=len(histogram))[: len(histogram)]
    cumulative = np.cumsum(histogram)
    return (
        int(np.searchsorted(cumulative, len(gaps) / 3, side="left")),
        int(np.searchsorted(cumulative, 2 * len(gaps) / 3, side="left")),
    )


def scale_strata(gaps: np.ndarray, boundaries: tuple[int, int]) -> np.ndarray:
    counts = np.zeros((3, PLANE_BINS, PLANE_BINS), dtype=np.int64)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        a = np.take(gaps, index).astype(np.int64)
        b = np.take(gaps, (index + 1) % size).astype(np.int64)
        c = np.take(gaps, (index + 2) % size).astype(np.int64)
        stratum = np.digitize(a + b + c, boundaries, right=True)
        row = relation_bins(a, b, PLANE_BINS)
        column = relation_bins(b, c, PLANE_BINS)
        code = stratum * PLANE_BINS**2 + row * PLANE_BINS + column
        counts += np.bincount(code, minlength=3 * PLANE_BINS**2).reshape(
            3, PLANE_BINS, PLANE_BINS
        )
    return np.stack([normalize(matrix) for matrix in counts])


def svd_crossfit(first: np.ndarray, second: np.ndarray) -> pd.DataFrame:
    first = normalize(first)
    second = normalize(second)

    def heldout(train: np.ndarray, test: np.ndarray, rank: int) -> float:
        u, singular, vt = np.linalg.svd(train, full_matrices=False)
        reconstruction = (u[:, :rank] * singular[:rank]) @ vt[:rank]
        reconstruction = np.clip(reconstruction, 0.0, None)
        return jsd_bits(test, reconstruction)

    rows = []
    for rank in range(1, 7):
        forward = heldout(first, second, rank)
        reverse = heldout(second, first, rank)
        rows.append(
            {
                "rank": rank,
                "half1_svd_to_half2_jsd_bits": forward,
                "half2_svd_to_half1_jsd_bits": reverse,
                "mean_heldout_jsd_bits": 0.5 * (forward + reverse),
            }
        )
    return pd.DataFrame(rows)


def close(first: np.ndarray | float, second: np.ndarray | float, tolerance: float = 1e-12) -> bool:
    return bool(np.allclose(first, second, rtol=0.0, atol=tolerance))


def main() -> None:
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    saved = np.load(MATRICES)

    parent = reduced_residues()
    gaps = construct_child_gaps(parent)
    fine = relation_sequence(gaps, PLANE_BINS)
    coarse = relation_sequence(gaps, SEQUENCE_BINS)
    half = len(gaps) // 2

    plane_first = plane_counts(fine, 0, half)
    plane_second = plane_counts(fine, half, len(fine))
    empirical = normalize(sequence_tensor(coarse, 0, len(coarse)))
    empirical_first = normalize(sequence_tensor(coarse, 0, half))
    empirical_second = normalize(sequence_tensor(coarse, half, len(coarse)))
    iid, markov = exact_gap_models(gaps)
    boundaries = span_boundaries(gaps)
    strata = scale_strata(gaps, boundaries)

    svd = svd_crossfit(plane_first, plane_second)
    svd.to_csv(SVD_OUTPUT, index=False)
    rank2 = svd.loc[svd["rank"] == 2].iloc[0]
    rank3 = svd.loc[svd["rank"] == 3].iloc[0]
    svd_rank3_both = bool(
        rank3["half1_svd_to_half2_jsd_bits"] < rank2["half1_svd_to_half2_jsd_bits"]
        and rank3["half2_svd_to_half1_jsd_bits"] < rank2["half2_svd_to_half1_jsd_bits"]
    )

    metrics = {
        "empirical_cmi_bits": cmi_bits(empirical),
        "iid_overlap_cmi_bits": cmi_bits(iid),
        "markov_overlap_cmi_bits": cmi_bits(markov),
        "empirical_excess_over_iid_bits": cmi_bits(empirical) - cmi_bits(iid),
        "empirical_excess_over_markov_bits": cmi_bits(empirical) - cmi_bits(markov),
        "empirical_jsd_from_iid_bits": jsd_bits(empirical, iid),
        "empirical_jsd_from_markov_bits": jsd_bits(empirical, markov),
        "half1_cmi_bits": cmi_bits(empirical_first),
        "half2_cmi_bits": cmi_bits(empirical_second),
    }
    primary_third = primary["third_step"]
    checks = {
        "protocol_hash_exact": file_hash(PROTOCOL) == PROTOCOL_SHA256,
        "prime29_remains_unopened": primary.get("prime29_opened") is False,
        "child_count_exact": len(gaps) == CHILD_SLOTS,
        "child_period_exact": int(gaps.sum()) == CHILD_PERIOD,
        "gap_hash_exact": array_hash(gaps) == GAP_SHA256,
        "empirical_tensor_exact": close(empirical, saved["empirical_sequence_tensor"]),
        "iid_tensor_exact": close(iid, saved["iid_sequence_tensor"]),
        "markov_tensor_exact": close(markov, saved["markov_sequence_tensor"]),
        "scale_boundaries_exact": list(boundaries)
        == primary["scale_strata"]["span_boundaries_upper_inclusive"],
        "scale_strata_exact": close(strata, saved["scale_strata"]),
        "empirical_cmi_exact": close(metrics["empirical_cmi_bits"], primary_third["empirical_cmi_bits"]),
        "iid_cmi_exact": close(metrics["iid_overlap_cmi_bits"], primary_third["iid_overlap_cmi_bits"]),
        "markov_cmi_exact": close(metrics["markov_overlap_cmi_bits"], primary_third["markov_overlap_cmi_bits"]),
        "excess_over_markov_positive": metrics["empirical_excess_over_markov_bits"] > 0,
        "svd_rank3_improves_both_directions": svd_rank3_both,
    }
    result = {
        "protocol": "PN1D/DEV/v1",
        "independent_route": (
            "standalone p23 reconstruction; exact tensors and strata; "
            "held-out truncated-SVD spatial cross-check"
        ),
        "prime29_opened": False,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "third_step_metrics": metrics,
        "independent_svd": {
            "rank3_improves_both_directions": svd_rank3_both,
            "rank2_mean_heldout_jsd_bits": float(rank2["mean_heldout_jsd_bits"]),
            "rank3_mean_heldout_jsd_bits": float(rank3["mean_heldout_jsd_bits"]),
            "rank2_to_rank3_gain_bits": float(
                rank2["mean_heldout_jsd_bits"] - rank3["mean_heldout_jsd_bits"]
            ),
        },
        "interpretive_limit": (
            "Validates a stable third representational component and residual "
            "third-step dependence on p23 development data. It does not establish "
            "that the data contain exactly three modes or three physical waves."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
