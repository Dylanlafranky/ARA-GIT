"""Correct PN33's endpoint moving-block bootstrap after an implementation audit.

The initial scorer bootstrapped *block medians*.  The frozen protocol instead
requires resampling 64-gap blocks, concatenating them to the original endpoint
length, and then taking the median.  This script implements that statistic
without materialising billions of individual resampled gaps: for each possible
median threshold it stores the count within every overlapping 64-gap block.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN33_SEEDED_HEXAGON_FILL_RESULTS.json"
VALIDATED_RESULTS = HERE / "PN33_SEEDED_HEXAGON_FILL_RESULTS_VALIDATED.json"
SUMMARY = HERE / "PN33_SEEDED_HEXAGON_FILL_COORDINATE_SUMMARY.json"
PRIME_BINARY = HERE / "PN33_TARGET_PRIME_GATES_UINT32.bin"
CORRECTED_RATIOS = HERE / "PN33_SEEDED_HEXAGON_FILL_BOOTSTRAP_RATIOS_CORRECTED.npy"
AUDIT = HERE / "PN33_MOVING_BLOCK_BOOTSTRAP_IMPLEMENTATION_AUDIT.json"

REPETITIONS = 10_000
BLOCK = 64
SEED = 33_001
BAND_WIDTH = 0.25


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def median_candidates(values: np.ndarray) -> np.ndarray:
    """Retain every plausible central value plus hard outer sentinels."""
    low, high = np.quantile(values, [0.05, 0.95])
    unique = np.unique(values)
    central = unique[(unique >= low) & (unique <= high)]
    return np.unique(np.concatenate(([unique[0]], central, [unique[-1]]))).astype(np.int64)


def rolling_counts(values: np.ndarray, candidates: np.ndarray, width: int) -> np.ndarray:
    """Count values <= each candidate in every overlapping window."""
    starts = len(values) - width + 1
    output = np.empty((starts, len(candidates)), dtype=np.uint8)
    for column, candidate in enumerate(candidates):
        indicator = (values <= candidate).astype(np.int32)
        prefix = np.empty(len(values) + 1, dtype=np.int64)
        prefix[0] = 0
        np.cumsum(indicator, out=prefix[1:])
        output[:, column] = prefix[width:] - prefix[:-width]
    return output


def moving_block_medians(
    values: np.ndarray,
    rng: np.random.Generator,
    repetitions: int,
) -> tuple[np.ndarray, dict]:
    """Return medians from exact-length moving-block resamples.

    Each resample draws overlapping blocks uniformly with replacement.  Full
    blocks are concatenated and the final selected block is truncated so the
    bootstrap series has exactly the same length as the observed endpoint.
    """
    n = len(values)
    if n < BLOCK:
        raise ValueError("endpoint shorter than the frozen block length")
    full_draws, remainder = divmod(n, BLOCK)
    draws = full_draws + int(remainder > 0)
    candidates = median_candidates(values)
    full_counts = rolling_counts(values, candidates, BLOCK)
    partial_counts = rolling_counts(values, candidates, remainder) if remainder else None
    start_count = len(values) - BLOCK + 1
    first_rank = (n - 1) // 2 + 1
    second_rank = n // 2 + 1
    medians = np.empty(repetitions, dtype=np.float64)
    boundary_hits = 0

    # Final-band draws are numerous; small batches bound the indexed tensor.
    batch_size = 20 if draws > 10_000 else 500
    for start in range(0, repetitions, batch_size):
        stop = min(start + batch_size, repetitions)
        indices = rng.integers(0, start_count, size=(stop - start, draws), dtype=np.int32)
        if full_draws:
            totals = full_counts[indices[:, :full_draws]].sum(axis=1, dtype=np.int64)
        else:
            totals = np.zeros((stop - start, len(candidates)), dtype=np.int64)
        if remainder:
            # A classical MBB truncates the final selected block to `remainder`.
            # Its start remains valid for a full block, so it is also valid here.
            totals += partial_counts[indices[:, -1]]
        first_idx = np.argmax(totals >= first_rank, axis=1)
        second_idx = np.argmax(totals >= second_rank, axis=1)
        no_first = ~np.any(totals >= first_rank, axis=1)
        no_second = ~np.any(totals >= second_rank, axis=1)
        if np.any(no_first) or np.any(no_second):
            raise RuntimeError("candidate range failed to contain a bootstrap median")
        boundary_hits += int(np.count_nonzero((first_idx == 0) | (second_idx == len(candidates) - 1)))
        medians[start:stop] = (candidates[first_idx] + candidates[second_idx]) / 2.0

    return medians, {
        "n": n,
        "block_length": BLOCK,
        "drawn_full_blocks": full_draws,
        "final_partial_length": remainder,
        "overlapping_start_count": start_count,
        "median_candidates": candidates.tolist(),
        "outer_sentinel_hits": boundary_hits,
        "observed_median": float(np.median(values)),
        "bootstrap_median_distribution": {
            str(value): int(count)
            for value, count in zip(*np.unique(medians, return_counts=True))
        },
    }


def main() -> None:
    for output in (VALIDATED_RESULTS, CORRECTED_RATIOS, AUDIT):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    scored = json.loads(RESULTS.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    primary_summary = next(item for item in summary["baselines"] if item["baseline_name"] == "primary")
    primary = next(item for item in scored["baselines"] if item["baseline_name"] == "primary")
    primes = np.fromfile(PRIME_BINARY, dtype="<u4")

    lo = int(primary_summary["baseline_prime_index"])
    hi = int(primary_summary["completion_prime_index"])
    gates = primes[lo + 1:hi + 1].astype(np.int64)
    gaps = gates - primes[lo:hi].astype(np.int64)
    increments = np.log1p(1.0 / (gates.astype(np.float64) - 1.0))
    x = 2.0 * np.cumsum(increments) / math.log(2.0)
    bands = np.minimum((x / BAND_WIDTH).astype(np.int16), 7)
    first = gaps[bands == 0]
    final = gaps[bands == 7]

    rng = np.random.default_rng(SEED)
    first_boot, first_detail = moving_block_medians(first, rng, REPETITIONS)
    final_boot, final_detail = moving_block_medians(final, rng, REPETITIONS)
    ratios = final_boot / first_boot
    interval = [float(value) for value in np.quantile(ratios, [0.025, 0.975])]
    point = float(np.median(final) / np.median(first))
    np.save(CORRECTED_RATIOS, ratios)

    contains_two = interval[0] <= 2.0 <= interval[1]
    excludes_one = interval[0] > 1.0
    doubling_pass = bool(primary["endpoint_adequate"] and contains_two and excludes_one)
    direction_pass = bool(primary["spearman_band_median_gap"] > 0)
    scale_direction_pass = bool(scored["decision"]["scale_checks_same_direction"])
    curve_pass = bool(primary["ara_log_mae"] <= 1.05 * primary["pnt_log_mae"])
    support = direction_pass and doubling_pass and curve_pass and scale_direction_pass
    closer_to_two = abs(point - 2.0) < abs(point - 1.0)
    if not primary["endpoint_adequate"]:
        status = "INCONCLUSIVE"
    elif support:
        status = "SUPPORTED SPACING EXPRESSION"
    elif direction_pass and closer_to_two:
        status = "SUGGESTIVE"
    elif primary["spearman_band_median_gap"] <= 0 or (not contains_two and not closer_to_two):
        status = "NOT SUPPORTED"
    else:
        status = "NULL"

    audit = {
        "test_id": "PN33/SEEDED-HEXAGON-FILL/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "finding": "Initial scorer resampled block medians rather than resampled consecutive gap blocks.",
        "original_results_file": RESULTS.name,
        "original_results_sha256": sha256(RESULTS),
        "original_interval": primary["endpoint_bootstrap_95_ci"],
        "original_status": scored["status"],
        "corrected_method": "10,000 exact-length moving-block resamples from all overlapping 64-gap starts; median after block concatenation",
        "seed": SEED,
        "point_ratio": point,
        "corrected_interval": interval,
        "corrected_contains_point": interval[0] <= point <= interval[1],
        "corrected_contains_two": contains_two,
        "corrected_excludes_one": excludes_one,
        "first_endpoint": first_detail,
        "final_endpoint": final_detail,
        "corrected_status": status,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    primary["endpoint_bootstrap_95_ci_initial_invalid_implementation"] = primary["endpoint_bootstrap_95_ci"]
    primary["endpoint_bootstrap_95_ci"] = interval
    primary["endpoint_final_first_median_ratio"] = point
    primary["doubling_contains_two"] = contains_two
    primary["doubling_excludes_one"] = excludes_one
    primary["bootstrap_implementation_audit"] = AUDIT.name
    scored["status"] = status
    scored["bootstrap_file"] = CORRECTED_RATIOS.name
    scored["bootstrap_file_sha256"] = sha256(CORRECTED_RATIOS)
    scored["methods"]["bootstrap_initial_implementation_invalid"] = (
        "PN33_SEEDED_HEXAGON_FILL_RESULTS.json resampled block medians; preserved for audit"
    )
    scored["methods"]["bootstrap"] = audit["corrected_method"]
    scored["methods"]["bootstrap_audit_file"] = AUDIT.name
    scored["decision"]["status"] = status
    scored["decision"]["primary_doubling_pass"] = doubling_pass
    scored["decision"]["bootstrap_corrected_after_implementation_audit"] = True
    scored["validated_results_created_utc"] = datetime.now(timezone.utc).isoformat()
    VALIDATED_RESULTS.write_text(json.dumps(scored, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "point_ratio": point,
        "corrected_95_ci": interval,
        "contains_two": contains_two,
        "contains_point": interval[0] <= point <= interval[1],
        "status": status,
        "first_bootstrap_medians": first_detail["bootstrap_median_distribution"],
        "final_bootstrap_medians": final_detail["bootstrap_median_distribution"],
    }, indent=2))


if __name__ == "__main__":
    main()
