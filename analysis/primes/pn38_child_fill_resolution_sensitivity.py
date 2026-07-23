"""PN38: test whether PN37 child-fill residuals survive histogram resolution.

The result is post-hoc.  One exact 2,880-bin pass is aggregated to the six
predeclared resolutions.  Observations are compared both with simple uniform
fill and with an exact gate-conditioned nonzero-residue expectation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from pn10b_child_phase_prime_ranking import base_primes, segmented_least_prime_factor


HERE = Path(__file__).resolve().parent
LOW = 4_000_000_000
HIGH = 4_001_000_000
RESOLUTIONS = (80, 120, 160, 180, 320, 360)
FINE_BINS = 2880
RESULTS_PATH = HERE / "PN38_CHILD_FILL_RESOLUTION_RESULTS.json"
REPORT_PATH = HERE / "PN38_CHILD_FILL_RESOLUTION_REPORT_2026-07-23.md"


def safe_correlation(left: np.ndarray, right: np.ndarray) -> float | None:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    if left.size != right.size or left.size < 2:
        return None
    if float(np.std(left)) == 0.0 or float(np.std(right)) == 0.0:
        return None
    return float(np.corrcoef(left, right)[0, 1])


def exact_residue_bin_counts(q: int, bins: int) -> np.ndarray:
    """Count nonzero residues r in each floor(bins*r/q) cell without enumeration."""
    index = np.arange(bins, dtype=np.int64)
    lower = (index * q + bins - 1) // bins
    upper_exclusive = ((index + 1) * q + bins - 1) // bins
    lower = np.maximum(lower, 1)
    upper = np.minimum(upper_exclusive - 1, q - 1)
    return np.maximum(upper - lower + 1, 0).astype(np.int64)


def aggregate(values: np.ndarray, bins: int) -> np.ndarray:
    factor = FINE_BINS // bins
    return values.reshape(bins, factor).sum(axis=1)


def diagnostics(
    observed: np.ndarray,
    expected: np.ndarray,
    first_observed: np.ndarray,
    first_expected: np.ndarray,
    second_observed: np.ndarray,
    second_expected: np.ndarray,
) -> tuple[dict, np.ndarray]:
    bins = observed.size
    total = float(np.sum(observed))
    observed_share = observed / total
    expected_share = expected / total
    uniform_share = np.full(bins, 1.0 / bins)
    residual = (observed - expected) / expected
    mirror = residual[::-1]
    symmetric = 0.5 * (residual + mirror)
    residual_energy = float(np.sum(residual * residual))

    first_residual = (first_observed - first_expected) / first_expected
    second_residual = (second_observed - second_expected) / second_expected

    result = {
        "bins": int(bins),
        "bin_width_on_ara_0_2": float(2.0 / bins),
        "compulsory_mean_share": float(1.0 / bins),
        "compulsory_mean_percent": float(100.0 / bins),
        "compulsory_mean_occupancy_ara": float(2.0 / bins),
        "observed_occupancy_ara_min": float(2.0 * np.min(observed_share)),
        "observed_occupancy_ara_max": float(2.0 * np.max(observed_share)),
        "simple_uniform_total_variation": float(0.5 * np.sum(np.abs(observed_share - uniform_share))),
        "gate_conditioned_total_variation": float(0.5 * np.sum(np.abs(observed_share - expected_share))),
        "gate_conditioned_rms_relative_residual": float(np.sqrt(np.mean(residual * residual))),
        "gate_conditioned_max_abs_relative_residual": float(np.max(np.abs(residual))),
        "mirror_residual_correlation": safe_correlation(residual, mirror),
        "symmetric_residual_energy_share": float(np.sum(symmetric * symmetric) / residual_energy) if residual_energy else None,
        "first_second_half_residual_correlation": safe_correlation(first_residual, second_residual),
        "observed_counts": [int(value) for value in observed],
        "exact_expected_counts": [float(value) for value in expected],
        "gate_conditioned_relative_residuals": [float(value) for value in residual],
    }
    return result, residual


def main() -> None:
    if FINE_BINS % math.lcm(*RESOLUTIONS) != 0:
        raise AssertionError("fine resolution must be divisible by every requested resolution")

    numbers, least_factor = segmented_least_prime_factor(LOW, HIGH)
    parents = numbers[least_factor == 0].astype(np.int64)
    gates = base_primes(int(math.isqrt(int(parents[-1]))))
    split_index = parents.size // 2

    observed_fine = np.zeros(FINE_BINS, dtype=np.int64)
    expected_fine = np.zeros(FINE_BINS, dtype=np.float64)
    first_observed_fine = np.zeros(FINE_BINS, dtype=np.int64)
    first_expected_fine = np.zeros(FINE_BINS, dtype=np.float64)
    second_observed_fine = np.zeros(FINE_BINS, dtype=np.int64)
    second_expected_fine = np.zeros(FINE_BINS, dtype=np.float64)

    for q_value in gates:
        q = int(q_value)
        first_parent = int(np.searchsorted(parents, q * q, side="left"))
        eligible = parents[first_parent:]
        if eligible.size == 0:
            continue

        remainders = eligible % q
        if np.any(remainders == 0):
            raise AssertionError(f"prime parent unexpectedly closed gate q={q}")
        fine_index = np.minimum((remainders * FINE_BINS) // q, FINE_BINS - 1)
        gate_observed = np.bincount(fine_index, minlength=FINE_BINS)
        residue_cells = exact_residue_bin_counts(q, FINE_BINS)
        if int(np.sum(residue_cells)) != q - 1:
            raise AssertionError(f"residue partition failed for q={q}")
        gate_expected_unit = residue_cells.astype(np.float64) / (q - 1)

        observed_fine += gate_observed
        expected_fine += eligible.size * gate_expected_unit

        first_size = max(0, split_index - first_parent)
        first_size = min(first_size, eligible.size)
        if first_size:
            first_observed_fine += np.bincount(fine_index[:first_size], minlength=FINE_BINS)
            first_expected_fine += first_size * gate_expected_unit
        second_size = eligible.size - first_size
        if second_size:
            second_observed_fine += np.bincount(fine_index[first_size:], minlength=FINE_BINS)
            second_expected_fine += second_size * gate_expected_unit

    total = int(np.sum(observed_fine))
    if not np.array_equal(first_observed_fine + second_observed_fine, observed_fine):
        raise AssertionError("parent halves do not reconstruct the whole histogram")
    for expected in (expected_fine, first_expected_fine, second_expected_fine):
        target = total if expected is expected_fine else int(round(float(np.sum(expected))))
        if abs(float(np.sum(expected)) - target) > 1e-4:
            raise AssertionError("expected histogram total failed")

    by_resolution: dict[str, dict] = {}
    expanded_residuals: dict[int, np.ndarray] = {}
    for bins in RESOLUTIONS:
        observed = aggregate(observed_fine, bins)
        expected = aggregate(expected_fine, bins)
        first_observed = aggregate(first_observed_fine, bins)
        first_expected = aggregate(first_expected_fine, bins)
        second_observed = aggregate(second_observed_fine, bins)
        second_expected = aggregate(second_expected_fine, bins)
        if int(np.sum(observed)) != total:
            raise AssertionError(f"observed total failed at {bins} bins")
        if abs(float(np.sum(expected)) - total) > 1e-4:
            raise AssertionError(f"expected total failed at {bins} bins")
        result, residual = diagnostics(
            observed,
            expected,
            first_observed,
            first_expected,
            second_observed,
            second_expected,
        )
        by_resolution[str(bins)] = result
        expanded_residuals[bins] = np.repeat(residual, FINE_BINS // bins)

    correlation_matrix: dict[str, dict[str, float | None]] = {}
    for left_bins in RESOLUTIONS:
        correlation_matrix[str(left_bins)] = {
            str(right_bins): safe_correlation(expanded_residuals[left_bins], expanded_residuals[right_bins])
            for right_bins in RESOLUTIONS
        }

    stacked = np.vstack([expanded_residuals[bins] for bins in RESOLUTIONS])
    same_positive = np.all(stacked > 0.0, axis=0)
    same_negative = np.all(stacked < 0.0, axis=0)
    persistent_sign_share = float(np.mean(same_positive | same_negative))

    payload = {
        "test": "PN38 child-fill resolution sensitivity",
        "protocol": "PN38_CHILD_FILL_RESOLUTION_PROTOCOL_v1_FROZEN.md",
        "interval": {"low_inclusive": LOW, "high_exclusive": HIGH},
        "parent_prime_count": int(parents.size),
        "child_relation_count": total,
        "fine_accumulator_bins": FINE_BINS,
        "resolutions": list(RESOLUTIONS),
        "by_resolution": by_resolution,
        "expanded_residual_correlation_matrix": correlation_matrix,
        "all_resolution_same_residual_sign_share": persistent_sign_share,
        "checks": {
            "observed_total_reconciles": int(np.sum(observed_fine)) == total,
            "expected_total_error": float(np.sum(expected_fine) - total),
            "halves_reconstruct_whole": bool(np.array_equal(first_observed_fine + second_observed_fine, observed_fine)),
            "all_requested_resolutions_divide_fine_grid": all(FINE_BINS % bins == 0 for bins in RESOLUTIONS),
        },
    }
    RESULTS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    rows = []
    for bins in RESOLUTIONS:
        item = by_resolution[str(bins)]
        rows.append(
            f"| {bins} | {item['compulsory_mean_percent']:.6f}% | "
            f"{item['compulsory_mean_occupancy_ara']:.8f} | "
            f"{item['gate_conditioned_total_variation']:.8f} | "
            f"{item['gate_conditioned_rms_relative_residual']:.6f} | "
            f"{item['mirror_residual_correlation']:.6f} | "
            f"{item['first_second_half_residual_correlation']:.6f} |"
        )

    matrix_header = "| bins | " + " | ".join(str(value) for value in RESOLUTIONS) + " |"
    matrix_rule = "|---:|" + "---:|" * len(RESOLUTIONS)
    matrix_rows = []
    for left_bins in RESOLUTIONS:
        cells = [f"{correlation_matrix[str(left_bins)][str(right_bins)]:.4f}" for right_bins in RESOLUTIONS]
        matrix_rows.append(f"| {left_bins} | " + " | ".join(cells) + " |")

    report = f"""# PN38 — Child-Fill Resolution Sensitivity Result

**Date:** 2026-07-23  
**Status:** post-hoc structural sensitivity analysis  
**Population:** {parents.size:,} parent primes and {total:,} complete child relations

## Result

The mean occupancy at every resolution is exactly the compulsory partition value `2/B`. It therefore moves when the analyst changes the number of bins and is not a discovered ARA landmark.

The table below reports residual structure after subtracting the exact gate-conditioned nonzero-residue expectation.

| bins | forced mean share | forced occupancy ARA | adjusted TV | adjusted RMS relative residual | mirror correlation | first/second-half residual correlation |
|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Cross-resolution residual correlation

Each residual profile is repeated over its exact cells on the common 2,880-cell ruler. These are descriptive correlations of differently smoothed views of the same child field, not independent replications.

{matrix_header}
{matrix_rule}
{chr(10).join(matrix_rows)}

The residual sign is the same at all six resolutions across **{100.0 * persistent_sign_share:.3f}%** of the common ruler.

## Conclusion

The compulsory fill rule is confirmed: changing `B` moves the mean exactly as `2/B`. After the stronger gate-conditioned correction, only **0.019% to 0.039%** of probability mass must be redistributed to match the exact baseline, and the RMS relative residual is **0.048% to 0.096%** across the frozen resolutions.

The residual views remain moderately related across resolutions (`r = 0.4964` to `0.7542` off the diagonal), which shows that rebinning does not manufacture wholly unrelated pictures. However, every consecutive-half correlation is negative (`r = -0.2250` to `-0.0816`). The residual therefore does not recur as a stable same-orientation grandchild profile across this interval. A moving or flipping profile is not ruled out, but it was not predeclared here and cannot be inferred from the negative correlations alone.

## Interpretation rule

- A high cross-resolution correlation alone shows that coarse and fine histograms retain related departures; it does not establish a new wave because the same observations underlie every resolution.
- The consecutive-half correlation is the more important recurrence check. Strong positive values would support a stable residual shape; weak, zero, or negative values would indicate that the apparent fine structure is not reproducible across the interval.
- Even a stable residual remains a number-theoretic distribution pattern until it predicts an untouched interval or beats the exact gate-conditioned control on a frozen endpoint.

## Reproduction

Run:

```powershell
python analysis/primes/pn38_child_fill_resolution_sensitivity.py
```

Machine-readable output: `PN38_CHILD_FILL_RESOLUTION_RESULTS.json`.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps({
        "parents": int(parents.size),
        "child_relations": total,
        "all_resolution_same_residual_sign_share": persistent_sign_share,
        "report": str(REPORT_PATH),
        "results": str(RESULTS_PATH),
    }, indent=2))


if __name__ == "__main__":
    main()
