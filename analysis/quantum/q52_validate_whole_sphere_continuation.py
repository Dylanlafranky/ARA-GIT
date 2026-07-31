"""Independent output validator for Q52.

This script does not regenerate the continuation trajectories.  It validates
the frozen protocol identity and independently recomputes the family/seed
classifications and ensemble gates from the emitted bin and seed tables.
"""

from __future__ import annotations

import ast
import csv
import gzip
import hashlib
import json
import math
import pathlib
from collections import defaultdict

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_RESULTS.json"
BINS = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_BINS.csv.gz"
SEEDS = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_SEEDS.csv"
FIGURE = HERE / "Q52_WHOLE_SPHERE_CONTINUATION.png"
OUTPUT = HERE / "Q52_WHOLE_SPHERE_CONTINUATION_VALIDATION.json"

EXPECTED_PROTOCOL_HASH = (
    "64146a33f9ffec9df87d777e11cabdb7a095f3e0527edb9049fec6d088ed73da"
)
EXPECTED_FAMILIES = (
    "fixed_A",
    "fixed_B",
    "alternating_AB",
    "alternating_BA",
    "random_520101",
    "random_520102",
    "random_520103",
    "random_520104",
)
ESTIMATORS = ("circle", "centroid", "extrema")
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    if math.isnan(a) and math.isnan(b):
        return True
    return math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)


def as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def read_bins() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with gzip.open(BINS, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            rows.append(
                {
                    "family": row["family"],
                    "estimator": row["estimator"],
                    "left": int(row["left"]),
                    "right": int(row["right"]),
                    "x": float(row["x"]),
                    "movement": float(row["mean_relative_movement"]),
                }
            )
    return rows


def read_seeds() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with SEEDS.open("r", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            parsed: dict[str, object] = dict(row)
            parsed["source_seed"] = int(row["source_seed"])
            parsed["eligible"] = as_bool(row["eligible"])
            for key in (
                "geometric_return",
                "active_return",
                "return_at_10pct",
                "return_at_50pct",
                "one_way_settling",
            ):
                parsed[key] = as_bool(row[key])
            parsed["witness_bin_indices"] = (
                ast.literal_eval(row["witness_bin_indices"])
                if row["witness_bin_indices"]
                else None
            )
            rows.append(parsed)
    return rows


def classify(rows: list[dict[str, object]]) -> dict[str, object]:
    ordered = sorted(rows, key=lambda row: int(row["left"]))
    x = np.asarray([float(row["x"]) for row in ordered], dtype=np.float64)
    movement = np.asarray(
        [float(row["movement"]) for row in ordered], dtype=np.float64
    )
    finite = np.isfinite(x) & np.isfinite(movement)
    historical = finite & np.asarray(
        [int(row["right"]) <= 250 for row in ordered]
    )
    extension = finite & np.asarray(
        [int(row["left"]) >= 500 for row in ordered]
    )
    baseline = (
        float(np.median(movement[historical])) if np.any(historical) else math.nan
    )
    witness: list[int] | None = None
    for low in np.flatnonzero(historical & (x <= 0.5)):
        later_high = np.flatnonzero(finite & (x >= 1.5) & (np.arange(len(x)) > low))
        if not later_high.size:
            continue
        high = int(later_high[0])
        later_low = np.flatnonzero(
            extension & (x <= 0.5) & (np.arange(len(x)) > high)
        )
        if later_low.size:
            witness = [int(low), high, int(later_low[0])]
            break

    geometric = witness is not None
    return_ratio = (
        float(movement[witness[2]] / baseline)
        if witness is not None and baseline > EPS
        else math.nan
    )
    active = geometric and math.isfinite(return_ratio) and return_ratio >= 0.25
    extension_indices = np.flatnonzero(extension)
    last = extension_indices[-3:] if extension_indices.size >= 3 else np.asarray([])
    final_x = float(np.median(x[last])) if last.size else math.nan
    final_ratio = (
        float(np.median(movement[last]) / baseline)
        if last.size and baseline > EPS
        else math.nan
    )
    settling = (
        not geometric
        and math.isfinite(final_x)
        and math.isfinite(final_ratio)
        and final_x >= 1.5
        and final_ratio <= 0.10
    )
    return {
        "finite_historical_bins": int(np.sum(historical)),
        "finite_extension_bins": int(np.sum(extension)),
        "baseline_movement": baseline,
        "geometric_return": bool(geometric),
        "active_return": bool(active),
        "return_movement_ratio": return_ratio,
        "return_at_10pct": bool(
            geometric and math.isfinite(return_ratio) and return_ratio >= 0.10
        ),
        "return_at_50pct": bool(
            geometric and math.isfinite(return_ratio) and return_ratio >= 0.50
        ),
        "witness_bin_indices": witness,
        "final_three_median_x": final_x,
        "final_three_movement_ratio": final_ratio,
        "one_way_settling": bool(settling),
        "minimum_x": float(np.nanmin(x)),
        "maximum_x": float(np.nanmax(x)),
    }


def bootstrap_source_clusters(
    seed_rows: list[dict[str, object]], key: str, seed: int
) -> dict[str, object]:
    by_source: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in seed_rows:
        if bool(row["eligible"]):
            by_source[int(row["source_seed"])].append(row)
    values = np.asarray(
        [
            np.mean([float(bool(row[key])) for row in rows])
            for _, rows in sorted(by_source.items())
        ],
        dtype=np.float64,
    )
    rng = np.random.default_rng(seed)
    chosen = rng.integers(0, values.size, size=(5000, values.size))
    draws = np.mean(values[chosen], axis=1)
    return {
        "source_seed_clusters": int(values.size),
        "fraction": float(np.mean(values)),
        "ci95": [float(value) for value in np.quantile(draws, [0.025, 0.975])],
    }


def main() -> None:
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    bins = read_bins()
    seeds = read_seeds()
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check(
        "protocol hash",
        sha256(PROTOCOL) == EXPECTED_PROTOCOL_HASH,
        sha256(PROTOCOL),
    )
    check(
        "result protocol hash",
        payload["frozen_protocol"]["sha256"] == EXPECTED_PROTOCOL_HASH,
        payload["frozen_protocol"]["sha256"],
    )
    check(
        "test identity",
        payload["test_id"] == "Q52-WHOLE-SPHERE-CONTINUATION-v1",
        payload["test_id"],
    )
    check(
        "family identity",
        tuple(payload["continuation"]["families"]) == EXPECTED_FAMILIES,
        payload["continuation"]["families"],
    )
    check(
        "bin table shape",
        len(bins) == 8 * 3 * 40,
        {"observed": len(bins), "expected": 960},
    )
    check(
        "seed table shape",
        len(seeds) == 8 * 50,
        {"observed": len(seeds), "expected": 400},
    )
    check(
        "figure emitted",
        FIGURE.is_file() and FIGURE.stat().st_size > 100_000,
        FIGURE.stat().st_size if FIGURE.is_file() else 0,
    )

    result_by_family = {
        row["family"]: row for row in payload["family_results"]
    }
    bin_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in bins:
        bin_groups[(str(row["family"]), str(row["estimator"]))].append(row)

    mismatches: list[dict[str, object]] = []
    independently_classified: dict[str, dict[str, object]] = {}
    for family in EXPECTED_FAMILIES:
        for estimator in ESTIMATORS:
            recomputed = classify(bin_groups[(family, estimator)])
            if estimator == "circle":
                expected = result_by_family[family]["primary"]
                independently_classified[family] = recomputed
            else:
                expected = result_by_family[family]["estimator_sensitivity"][
                    estimator
                ]
            for key, observed in recomputed.items():
                target = expected[key]
                if isinstance(observed, float):
                    matched = close(observed, float(target))
                else:
                    matched = observed == target
                if not matched:
                    mismatches.append(
                        {
                            "family": family,
                            "estimator": estimator,
                            "field": key,
                            "recomputed": observed,
                            "reported": target,
                        }
                    )
    check(
        "independent family classification",
        not mismatches,
        mismatches[:20],
    )

    seed_fraction_mismatches: list[dict[str, object]] = []
    for family in EXPECTED_FAMILIES:
        rows = [
            row
            for row in seeds
            if row["family"] == family and bool(row["eligible"])
        ]
        active = float(np.mean([float(bool(row["active_return"])) for row in rows]))
        settle = float(
            np.mean([float(bool(row["one_way_settling"])) for row in rows])
        )
        expected = result_by_family[family]
        if not close(active, float(expected["seed_active_return"]["fraction"])):
            seed_fraction_mismatches.append(
                {"family": family, "field": "active", "recomputed": active}
            )
        if not close(settle, float(expected["seed_settling"]["fraction"])):
            seed_fraction_mismatches.append(
                {"family": family, "field": "settle", "recomputed": settle}
            )
    check(
        "independent seed fractions",
        not seed_fraction_mismatches,
        seed_fraction_mismatches,
    )

    pooled_active = bootstrap_source_clusters(seeds, "active_return", 520152)
    pooled_settle = bootstrap_source_clusters(seeds, "one_way_settling", 520153)
    pooled_match = (
        close(
            pooled_active["fraction"],
            payload["pooled_source_seed_active_return"]["fraction"],
        )
        and all(
            close(left, right)
            for left, right in zip(
                pooled_active["ci95"],
                payload["pooled_source_seed_active_return"]["ci95"],
            )
        )
        and close(
            pooled_settle["fraction"],
            payload["pooled_source_seed_settling"]["fraction"],
        )
        and all(
            close(left, right)
            for left, right in zip(
                pooled_settle["ci95"],
                payload["pooled_source_seed_settling"]["ci95"],
            )
        )
    )
    check(
        "independent pooled bootstrap",
        pooled_match,
        {"active": pooled_active, "settle": pooled_settle},
    )

    eligible = [
        result_by_family[family]
        for family in EXPECTED_FAMILIES
        if bool(result_by_family[family]["eligible"])
    ]
    active = [row for row in eligible if row["primary"]["active_return"]]
    settling = [row for row in eligible if row["primary"]["one_way_settling"]]
    active_types = {
        (
            "fixed"
            if row["family"].startswith("fixed")
            else "alternating"
            if row["family"].startswith("alternating")
            else "random"
        )
        for row in active
    }
    complete_supported = (
        len(active) >= 5
        and active_types == {"fixed", "alternating", "random"}
        and pooled_active["ci95"][0] > 0.50
    )
    settling_supported = len(settling) >= 5 and pooled_settle["ci95"][0] > 0.50
    driver_dependent = len(active) >= 2 and len(settling) >= 2
    verdict = (
        "DRIVER-DEPENDENT"
        if driver_dependent
        else "COMPLETE 0→2→0 RETURN SUPPORTED"
        if complete_supported
        else "ONE-WAY SETTLING SUPPORTED"
        if settling_supported
        else "UNRESOLVED / MIXED"
    )
    check(
        "independent ensemble verdict",
        verdict == payload["verdict"],
        {"recomputed": verdict, "reported": payload["verdict"]},
    )

    maximum_reconstruction_error = float(
        payload["source_reconstruction"]["maximum_pair_reconstruction_error"]
    )
    maximum_norm_drift = max(
        float(row["norm_qc"]["maximum_absolute_norm_drift"])
        for row in payload["family_results"]
    )
    check(
        "slice-499 reconstruction gate",
        maximum_reconstruction_error <= 5e-6,
        maximum_reconstruction_error,
    )
    check(
        "continuation norm preservation",
        maximum_norm_drift <= 1e-10,
        maximum_norm_drift,
    )
    check(
        "local angle excluded from external score role",
        payload["continuation"]["local_rotation_role"]
        == "source machinery; absent from external ARA score",
        payload["continuation"]["local_rotation_role"],
    )

    validation = {
        "test_id": "Q52-WHOLE-SPHERE-CONTINUATION-VALIDATION-v1",
        "status": "PASS" if all(row["passed"] for row in checks) else "FAIL",
        "checks_passed": int(sum(bool(row["passed"]) for row in checks)),
        "checks_total": len(checks),
        "checks": checks,
        "independent_pooled_active_return": pooled_active,
        "independent_pooled_settling": pooled_settle,
        "interpretive_boundary": (
            "The frozen ensemble verdict is unresolved/mixed. Source-seed "
            "returns in mixed futures are descriptive heterogeneity, not a "
            "passed family-aggregate return gate."
        ),
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
