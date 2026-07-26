"""Independent validation for Q29 unclassified-component exploration."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np


SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
Q27_CACHE = SOURCE_DIR / "q27_derived_cache.npz"
CONNECTED_CACHE = SOURCE_DIR / "q28_connected_cache.npy"
RESULTS = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_RESULTS.json"
TRIALS = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_TRIALS.csv"
LAG_CURVE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_LAG_CURVE.csv"
EVENT_SAMPLE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_EVENT_SAMPLE.csv"
MODES = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_MODES.csv"
AXIS_TRIALS = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_SURFER_TRIALS.csv"
AXIS_LAG_CURVE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_SURFER_LAG_CURVE.csv"
AXIS_ROUTE_SAMPLE = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_AXIS_ROUTE_SAMPLE.csv"
OUTPUT = HERE / "Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_VALIDATION.json"

PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
FLIP_MASKS = np.asarray(
    (
        (1.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
    ),
    dtype=np.float64,
)
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def active_pair_indices(edge_row: np.ndarray) -> list[int]:
    output: list[int] = []
    for raw_u, raw_v in edge_row:
        pair = tuple(sorted((int(raw_u), int(raw_v))))
        if pair in PAIR_TO_INDEX:
            output.append(PAIR_TO_INDEX[pair])
    return output


def independent_fit(source: np.ndarray, target: np.ndarray) -> tuple[float, int, float]:
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    source_norm_sq = float(np.dot(source, source))
    target_norm_sq = float(np.dot(target, target))
    best = (math.inf, -1, math.nan)
    for flip_index, mask in enumerate(FLIP_MASKS):
        transformed = mask * source
        alpha = max(0.0, float(np.dot(transformed, target)) / source_norm_sq)
        residual = target - alpha * transformed
        error = float(np.linalg.norm(residual) / math.sqrt(target_norm_sq))
        if error < best[0]:
            best = (error, flip_index, alpha)
    return best


def close(left: float, right: float, tolerance: float = 2e-6) -> bool:
    return bool(abs(left - right) <= tolerance)


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    trial_rows = read_csv(TRIALS)
    lag_rows = read_csv(LAG_CURVE)
    event_rows = read_csv(EVENT_SAMPLE)
    mode_rows = read_csv(MODES)
    axis_trial_rows = read_csv(AXIS_TRIALS)
    axis_lag_rows = read_csv(AXIS_LAG_CURVE)
    axis_route_rows = read_csv(AXIS_ROUTE_SAMPLE)

    q27 = np.load(Q27_CACHE, allow_pickle=False)
    closure = np.asarray(q27["closure"], dtype=np.float32)
    edges = np.asarray(q27["edges"], dtype=np.int8)
    connected = np.load(CONNECTED_CACHE, mmap_mode="r")

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check(
        "test id",
        results["test_id"]
        == "Q29-ARA9-UNCLASSIFIED-COMPONENT-SURFER-EXPLORATION-v1",
        results["test_id"],
    )
    check(
        "exploratory class",
        "exploratory" in results["test_class"],
        results["test_class"],
    )
    check(
        "no Phase-B classification",
        "PHASE-B" not in results["descriptive_lean"].upper(),
        results["descriptive_lean"],
    )
    check(
        "descriptive lean",
        results["descriptive_lean"]
        == (
            "LOCAL SIGNED Z-AXIS HANDOVER MEMORY; "
            "NO STABLE COUNTERPART DETECTED"
        ),
        results["descriptive_lean"],
    )
    check(
        "connected shape",
        tuple(connected.shape) == (2, 100, 500, 66, 3, 3),
        list(connected.shape),
    )
    check(
        "connected cache hash",
        sha256(CONNECTED_CACHE)
        == results["source_checks"]["q28_connected_cache_sha256"],
        results["source_checks"]["q28_connected_cache_sha256"],
    )
    check(
        "Q27 cache hash",
        sha256(Q27_CACHE) == results["source_checks"]["q27_cache_sha256"],
        results["source_checks"]["q27_cache_sha256"],
    )
    check(
        "source diagonal",
        float(results["source_checks"]["maximum_off_diagonal"]) == 0.0,
        results["source_checks"]["maximum_off_diagonal"],
    )
    check(
        "event count",
        int(results["pooled"]["events"]) == 76043,
        results["pooled"]["events"],
    )
    check(
        "split events add to pooled",
        sum(int(row["events"]) for row in results["splits"].values())
        == int(results["pooled"]["events"]),
        results["splits"],
    )
    check(
        "trial rows",
        len(trial_rows) == 400,
        len(trial_rows),
    )
    check(
        "axis trial rows",
        len(axis_trial_rows) == 400,
        len(axis_trial_rows),
    )
    check(
        "full lag curve rows",
        len(lag_rows) == 21,
        len(lag_rows),
    )
    check(
        "axis lag curve rows",
        len(axis_lag_rows) == 18,
        len(axis_lag_rows),
    )

    sample_indices = np.linspace(
        0,
        len(event_rows) - 1,
        32,
        dtype=int,
    )
    maximum_fit_difference = 0.0
    maximum_fraction_difference = 0.0
    maximum_z_difference = 0.0
    dominant_axes: set[str] = set()
    positive_child_counts: set[int] = set()
    for sample_index in sample_indices:
        row = event_rows[int(sample_index)]
        branch = 0 if row["branch_label"] == "c2" else 1
        seed = int(row["seed"])
        time = int(row["time"])
        source_pair = PAIR_TO_INDEX[
            tuple(sorted(int(value) for value in row["source_pair"].split("-")))
        ]
        endpoint = int(row["endpoint"])
        active = active_pair_indices(edges[branch, seed, time])
        local_targets = [
            target
            for target in active
            if target != source_pair and endpoint in PAIRS[target]
        ]
        accumulations = np.asarray(
            [
                max(
                    0.0,
                    float(
                        closure[branch, seed, time + 2, target]
                        - closure[branch, seed, time, target]
                    ),
                )
                for target in local_targets
            ],
            dtype=np.float64,
        )
        positive_child_counts.add(int(np.count_nonzero(accumulations > 0)))
        total = float(np.sum(accumulations))
        child_vectors = np.diagonal(
            np.asarray(
                connected[branch, seed, time + 2, local_targets],
                dtype=np.float64,
            ),
            axis1=1,
            axis2=2,
        )
        target = np.sum(accumulations[:, None] * child_vectors, axis=0) / total
        source = np.diag(
            np.asarray(connected[branch, seed, time, source_pair], dtype=np.float64)
        )
        fit_error, flip_index, alpha = independent_fit(source, target)
        residual = target - alpha * FLIP_MASKS[flip_index] * source
        target_norm = float(np.linalg.norm(target))
        residual_fraction = float(np.linalg.norm(residual) / target_norm)
        residual_z_scaled = float(residual[2] / target_norm)
        maximum_fit_difference = max(
            maximum_fit_difference,
            abs(fit_error - float(row["q28_fit_error"])),
        )
        maximum_fraction_difference = max(
            maximum_fraction_difference,
            abs(residual_fraction - float(row["residual_fraction"])),
        )
        maximum_z_difference = max(
            maximum_z_difference,
            abs(residual_z_scaled - float(row["residual_z_scaled"])),
        )
        dominant_axes.add(("x", "y", "z")[int(np.argmax(np.abs(residual)))])

    check(
        "independent Q28 fit reconstruction",
        maximum_fit_difference < 2e-6,
        maximum_fit_difference,
    )
    check(
        "independent residual-fraction reconstruction",
        maximum_fraction_difference < 2e-6,
        maximum_fraction_difference,
    )
    check(
        "independent signed-z reconstruction",
        maximum_z_difference < 2e-6,
        maximum_z_difference,
    )
    check(
        "sample residual dominant axis",
        dominant_axes == {"z"},
        sorted(dominant_axes),
    )
    check(
        "sample has one positive accumulating child",
        positive_child_counts == {1},
        sorted(positive_child_counts),
    )
    check(
        "pooled has one positive accumulating child",
        close(float(results["pooled"]["positive_child_count"]), 1.0, 1e-12),
        results["pooled"]["positive_child_count"],
    )
    check(
        "pooled residual axis concentration",
        float(results["pooled"]["residual_largest_axis_share"]) > 0.94,
        results["pooled"]["residual_largest_axis_share"],
    )
    check(
        "mode weights only z",
        all(
            row["residual_dominant_axis"] == "z"
            or abs(float(row["weight"])) < 1e-14
            for row in mode_rows
        ),
        "nonzero modes inspected",
    )
    for split in ("development", "opened_later_half"):
        share = sum(
            float(row["weight_share"])
            for row in mode_rows
            if row["split"] == split
        )
        check(f"{split} mode shares sum to one", close(share, 1.0, 2e-9), share)

    axis_by_key = {
        (row["control"], int(row["lag"])): row for row in axis_lag_rows
    }
    exact_lag1 = float(axis_by_key[("exact", 1)]["axis_error"])
    seed_lag1 = float(axis_by_key[("seed", 1)]["axis_error"])
    time_lag1 = float(axis_by_key[("time", 1)]["axis_error"])
    check(
        "lag-1 exact axis recurrence beats seed",
        exact_lag1 < seed_lag1,
        [exact_lag1, seed_lag1],
    )
    check(
        "lag-1 exact axis recurrence beats time",
        exact_lag1 < time_lag1,
        [exact_lag1, time_lag1],
    )
    check(
        "lag-1 exact advantage is material",
        exact_lag1 < 0.5 * min(seed_lag1, time_lag1),
        [exact_lag1, seed_lag1, time_lag1],
    )
    exact_lag6 = float(axis_by_key[("exact", 6)]["axis_error"])
    seed_lag6 = float(axis_by_key[("seed", 6)]["axis_error"])
    time_lag6 = float(axis_by_key[("time", 6)]["axis_error"])
    check(
        "axis recurrence fades by lag 6",
        abs(exact_lag6 - np.mean([seed_lag6, time_lag6])) < 0.01,
        [exact_lag6, seed_lag6, time_lag6],
    )
    axis_pooled = results["axis_native_surfer"]["pooled"]
    check(
        "pooled axis exact beats seed",
        float(axis_pooled["exact_error"]) < float(axis_pooled["seed_error"]),
        [axis_pooled["exact_error"], axis_pooled["seed_error"]],
    )
    check(
        "pooled axis exact beats time",
        float(axis_pooled["exact_error"]) < float(axis_pooled["time_error"]),
        [axis_pooled["exact_error"], axis_pooled["time_error"]],
    )
    check(
        "opened bootstrap exact below both controls",
        results["axis_native_surfer"]["bootstrap_opened_later_half"][
            "exact_error_below_seed"
        ]
        == 1.0
        and results["axis_native_surfer"]["bootstrap_opened_later_half"][
            "exact_error_below_time"
        ]
        == 1.0,
        results["axis_native_surfer"]["bootstrap_opened_later_half"],
    )
    check(
        "exact endpoint association beats controls",
        float(axis_pooled["exact_shares_source_endpoint"])
        > float(axis_pooled["seed_shares_source_endpoint"])
        and float(axis_pooled["exact_shares_source_endpoint"])
        > float(axis_pooled["time_shares_source_endpoint"]),
        [
            axis_pooled["exact_shares_source_endpoint"],
            axis_pooled["seed_shares_source_endpoint"],
            axis_pooled["time_shares_source_endpoint"],
        ],
    )
    check(
        "partner persistence does not beat both controls",
        not (
            float(axis_pooled["exact_partner_persistence"])
            > float(axis_pooled["seed_partner_persistence"])
            and float(axis_pooled["exact_partner_persistence"])
            > float(axis_pooled["time_partner_persistence"])
        ),
        [
            axis_pooled["exact_partner_persistence"],
            axis_pooled["seed_partner_persistence"],
            axis_pooled["time_partner_persistence"],
        ],
    )
    check(
        "route-sample jitter bounded",
        max(abs(int(row["time_jitter"])) for row in axis_route_rows) <= 3,
        max(abs(int(row["time_jitter"])) for row in axis_route_rows),
    )
    check(
        "route-sample matched candidates positive",
        min(int(row["matched_candidate_count"]) for row in axis_route_rows) >= 1,
        min(int(row["matched_candidate_count"]) for row in axis_route_rows),
    )
    check(
        "route-sample errors bounded",
        all(0.0 <= float(row["axis_error"]) <= 1.0 for row in axis_route_rows),
        len(axis_route_rows),
    )
    check(
        "boundary states opened source",
        "already fully opened" in results["boundary"],
        results["boundary"],
    )
    check(
        "boundary rejects hidden physical wave",
        "does not establish a hidden physical wave" in results["boundary"],
        results["boundary"],
    )

    passed = sum(int(row["passed"]) for row in checks)
    validation = {
        "test_id": "Q29-ARA9-UNCLASSIFIED-COMPONENT-VALIDATION-v1",
        "date": "2026-07-26",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
