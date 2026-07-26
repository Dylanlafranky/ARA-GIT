"""Independent artifact-level validation for Q30."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_RESULTS.json"
TRIALS = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_TRIALS.csv"
LAG_CURVE = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_LAG_CURVE.csv"
EVENT_SAMPLE = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_EVENT_SAMPLE.csv"
PROTOCOL = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_PROTOCOL_v1_FROZEN.md"
FIGURE_PNG = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_GEOMETRY.png"
FIGURE_SVG = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_GEOMETRY.svg"
OUTPUT = HERE / "Q30_ARA15_35_OUT_OF_CUT_ROUTE_VALIDATION.json"
SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
Q27_CACHE = SOURCE_DIR / "q27_derived_cache.npz"
CONNECTED_CACHE = SOURCE_DIR / "q28_connected_cache.npy"
BOOTSTRAP_DRAWS = 2000
RNG_SEED = 30015
PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {value: index for index, value in enumerate(PAIRS)}
FLIP_MASKS = np.asarray(
    (
        (1.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
    ),
    dtype=np.float64,
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def pair(value: str) -> tuple[int, int]:
    first, second = value.split("-")
    return int(first), int(second)


def advantage(exact: float, control: float) -> float:
    return (control - exact) / control


def fit(source: np.ndarray, target: np.ndarray) -> tuple[float, float, int]:
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    source_norm_sq = float(source @ source)
    target_norm_sq = float(target @ target)
    transformed = FLIP_MASKS * source
    dots = transformed @ target
    alphas = np.maximum(0.0, dots / source_norm_sq)
    errors = np.sqrt(
        np.maximum(
            0.0,
            target_norm_sq
            - 2.0 * alphas * dots
            + alphas * alphas * source_norm_sq,
        )
        / target_norm_sq
    )
    index = int(np.argmin(errors))
    return float(errors[index]), float(alphas[index]), index


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    trial_rows = read_csv(TRIALS)
    lag_rows = read_csv(LAG_CURVE)
    samples = read_csv(EVENT_SAMPLE)
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object = None) -> None:
        if isinstance(detail, set):
            detail = sorted(detail)
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    for path in (
        RESULTS,
        TRIALS,
        LAG_CURVE,
        EVENT_SAMPLE,
        PROTOCOL,
        FIGURE_PNG,
        FIGURE_SVG,
    ):
        add(f"artifact exists: {path.name}", path.exists(), path.stat().st_size)

    add("test id", result["test_id"].startswith("Q30-ARA15-35"))
    add("event count", result["event_population"]["events"] == 76043)
    add("trial strata", result["event_population"]["trial_strata"] == 400)
    add("unique triangles nonzero", result["event_population"]["unique_pair_index_triangles"] > 0)
    add("lag rows 2x7x5", len(lag_rows) == 70, len(lag_rows))
    add("trial rows 400", len(trial_rows) == 400, len(trial_rows))
    add("event sample nonempty", 0 < len(samples) <= 1200, len(samples))
    add(
        "protocol hash",
        result["source"]["protocol_sha256"] == sha256(PROTOCOL),
        sha256(PROTOCOL),
    )
    add(
        "route definition retains 2+1.5",
        "2 plus" in result["route_definition"]["three_point_five"],
    )
    add(
        "phase B not identified",
        result["gates"]["R4_phase_b_identified"] is False,
    )

    grouped: dict[tuple[str, int], list[dict[str, str]]] = {}
    for row in lag_rows:
        grouped.setdefault((row["split"], int(row["lag"])), []).append(row)
        error = float(row["residual_error"])
        recovery = float(row["residual_recovery"])
        add(
            f"recovery identity {row['split']} l{row['lag']} {row['control']}",
            math.isclose(1.0 - error, recovery, abs_tol=2e-12),
        )
        add(
            f"bounded error {row['split']} l{row['lag']} {row['control']}",
            0.0 <= error <= 1.0 + 1e-12,
        )
    for key, rows in grouped.items():
        event_counts = {int(row["events"]) for row in rows}
        weights = {round(float(row["weight"]), 12) for row in rows}
        add(f"control event parity {key}", len(event_counts) == 1, event_counts)
        add(f"control weight parity {key}", len(weights) == 1, weights)

    later0 = {
        row["control"]: row
        for row in lag_rows
        if row["split"] == "opened_later_half" and int(row["lag"]) == 0
    }
    exact0 = float(later0["exact_closure"]["residual_error"])
    seed0 = float(later0["seed"]["residual_error"])
    time0 = float(later0["time"]["residual_error"])
    open0 = float(later0["open_edge"]["residual_error"])
    stored_adv = result["opened_later_half"]["lag0_relative_advantages"]
    add("lag0 advantage vs seed", math.isclose(stored_adv["vs_seed"], advantage(exact0, seed0), abs_tol=1e-12))
    add("lag0 advantage vs time", math.isclose(stored_adv["vs_time"], advantage(exact0, time0), abs_tol=1e-12))
    add("lag0 advantage vs open edge", math.isclose(stored_adv["vs_open_edge"], advantage(exact0, open0), abs_tol=1e-12))
    add("lag0 exact does not beat seed", exact0 > seed0)
    add("lag0 exact does not beat time", exact0 > time0)
    add(
        "lag0 recovery below frozen gate",
        float(later0["exact_closure"]["residual_recovery"]) < 0.10,
    )

    def pooled_late(control: str) -> float:
        selected = [
            row
            for row in lag_rows
            if row["split"] == "opened_later_half"
            and int(row["lag"]) in (4, 5, 6)
            and row["control"] == control
        ]
        numerator = sum(
            float(row["weight"]) * float(row["residual_error"])
            for row in selected
        )
        denominator = sum(float(row["weight"]) for row in selected)
        return numerator / denominator

    late_exact = pooled_late("exact_closure")
    late_seed = pooled_late("seed")
    late_time = pooled_late("time")
    stored_late = result["opened_later_half"]["late_lags_4_to_6"]
    add(
        "late exact aggregation",
        math.isclose(
            late_exact,
            stored_late["exact_closure"]["residual_error"],
            abs_tol=1e-12,
        ),
    )
    add("late exact beats seed weakly", late_exact < late_seed)
    add("late exact beats time weakly", late_exact < late_time)
    add(
        "late margin below frozen gate",
        advantage(late_exact, late_seed) < 0.05
        and advantage(late_exact, late_time) < 0.05,
    )

    triangle_ok = True
    decoy_ok = True
    for row in samples:
        source = pair(row["source_pair"])
        child = pair(row["child_pair"])
        closing = pair(row["closing_pair_1p5"])
        shared = int(row["shared_node"])
        source_other = int(row["source_other_node"])
        child_other = int(row["child_other_node"])
        if shared not in source or shared not in child:
            triangle_ok = False
        if set(closing) != {source_other, child_other}:
            triangle_ok = False
        if shared in closing:
            triangle_ok = False
        decoy = pair(row["open_edge_control"])
        if set(decoy) == set(closing) or shared in decoy:
            decoy_ok = False
    add("sample triangle closures exact", triangle_ok)
    add("sample topology controls nonclosing", decoy_ok)

    # Independently rebuild every saved sample from the derived public-source
    # caches. This does not import or call the Q30 runner.
    q27 = np.load(Q27_CACHE, allow_pickle=False)
    closure = np.asarray(q27["closure"], dtype=np.float32)
    edges = np.asarray(q27["edges"], dtype=np.int8)
    connected = np.load(CONNECTED_CACHE, mmap_mode="r")
    raw_differences = {
        "residual_fraction": [],
        "exact_error": [],
        "seed_error": [],
        "time_error": [],
        "open_error": [],
    }
    for row in samples:
        branch = 0 if row["branch"] == "c2" else 1
        seed = int(row["seed"])
        source_time = int(row["source_time"])
        origin_time = int(row["origin_time"])
        shared = int(row["shared_node"])
        source_pair = PAIR_TO_INDEX[pair(row["source_pair"])]
        closing_pair = PAIR_TO_INDEX[pair(row["closing_pair_1p5"])]
        decoy_pair = PAIR_TO_INDEX[pair(row["open_edge_control"])]
        active: list[int] = []
        for raw_u, raw_v in edges[branch, seed, source_time]:
            candidate = tuple(sorted((int(raw_u), int(raw_v))))
            if candidate in PAIR_TO_INDEX:
                active.append(PAIR_TO_INDEX[candidate])
        targets = [
            target
            for target in active
            if target != source_pair and shared in PAIRS[target]
        ]
        accumulations = np.asarray(
            [
                max(
                    0.0,
                    float(
                        closure[branch, seed, origin_time, target]
                        - closure[branch, seed, source_time, target]
                    ),
                )
                for target in targets
            ],
            dtype=np.float64,
        )
        child_vectors = np.asarray(
            [
                np.diag(
                    np.asarray(
                        connected[branch, seed, origin_time, target],
                        dtype=np.float64,
                    )
                )
                for target in targets
            ]
        )
        target_web = (
            np.sum(accumulations[:, None] * child_vectors, axis=0)
            / float(np.sum(accumulations))
        )
        source_vector = np.diag(
            np.asarray(
                connected[branch, seed, source_time, source_pair],
                dtype=np.float64,
            )
        )
        _, alpha, source_flip = fit(source_vector, target_web)
        residual = target_web - alpha * FLIP_MASKS[source_flip] * source_vector
        residual_fraction = float(np.linalg.norm(residual) / np.linalg.norm(target_web))
        exact_vector = np.diag(
            np.asarray(
                connected[branch, seed, origin_time, closing_pair],
                dtype=np.float64,
            )
        )
        displaced_seed = (seed + 37) % 100
        seed_vector = np.diag(
            np.asarray(
                connected[branch, displaced_seed, origin_time, closing_pair],
                dtype=np.float64,
            )
        )
        split_start = 2 if row["split"] == "development" else 252
        shifted = split_start + ((origin_time - split_start + 137) % 242)
        time_vector = np.diag(
            np.asarray(
                connected[branch, seed, shifted, closing_pair],
                dtype=np.float64,
            )
        )
        open_vector = np.diag(
            np.asarray(
                connected[branch, seed, origin_time, decoy_pair],
                dtype=np.float64,
            )
        )
        exact_error = fit(exact_vector, residual)[0]
        seed_error = fit(seed_vector, residual)[0]
        time_error = fit(time_vector, residual)[0]
        open_error = fit(open_vector, residual)[0]
        raw_differences["residual_fraction"].append(
            abs(residual_fraction - float(row["q28_residual_fraction"]))
        )
        raw_differences["exact_error"].append(
            abs(exact_error - float(row["exact_1p5_error"]))
        )
        raw_differences["seed_error"].append(
            abs(seed_error - float(row["seed_error"]))
        )
        raw_differences["time_error"].append(
            abs(time_error - float(row["time_error"]))
        )
        raw_differences["open_error"].append(
            abs(open_error - float(row["open_edge_error"]))
        )
    for name, values in raw_differences.items():
        maximum = max(values, default=math.inf)
        add(f"raw sample rebuild {name}", maximum < 2e-10, maximum)

    later_trials = [
        row for row in trial_rows if row["split"] == "opened_later_half"
    ]
    later_trials.sort(key=lambda row: (int(row["branch_index"]), int(row["seed"])))
    add("later trial rows 200", len(later_trials) == 200)
    rng = np.random.default_rng(RNG_SEED)
    counts = {
        "lag0_exact_beats_seed": 0,
        "lag0_exact_beats_time": 0,
        "late_exact_beats_seed": 0,
        "late_exact_beats_time": 0,
        "lag0_exact_beats_both": 0,
        "late_exact_beats_both": 0,
    }

    def sampled_error(indices: np.ndarray, control: str, late: bool) -> float:
        lags = (4, 5, 6) if late else (0,)
        numerator = 0.0
        denominator = 0.0
        for raw_index in indices:
            row = later_trials[int(raw_index)]
            for lag in lags:
                prefix = f"l{lag}_{control}"
                weight = float(row[f"{prefix}_weight"])
                error = float(row[f"{prefix}_error"])
                if math.isfinite(weight) and math.isfinite(error):
                    numerator += weight * error
                    denominator += weight
        return numerator / denominator

    for _ in range(BOOTSTRAP_DRAWS):
        indices = rng.integers(0, len(later_trials), size=len(later_trials))
        e0 = sampled_error(indices, "exact_closure", False)
        s0 = sampled_error(indices, "seed", False)
        t0 = sampled_error(indices, "time", False)
        el = sampled_error(indices, "exact_closure", True)
        sl = sampled_error(indices, "seed", True)
        tl = sampled_error(indices, "time", True)
        a = e0 < s0
        b = e0 < t0
        c = el < sl
        d = el < tl
        counts["lag0_exact_beats_seed"] += int(a)
        counts["lag0_exact_beats_time"] += int(b)
        counts["late_exact_beats_seed"] += int(c)
        counts["late_exact_beats_time"] += int(d)
        counts["lag0_exact_beats_both"] += int(a and b)
        counts["late_exact_beats_both"] += int(c and d)
    rebuilt_bootstrap = {
        key: value / BOOTSTRAP_DRAWS for key, value in counts.items()
    }
    for key, value in rebuilt_bootstrap.items():
        add(
            f"bootstrap {key}",
            math.isclose(value, result["bootstrap"][key], abs_tol=1e-12),
            value,
        )

    gates = result["gates"]
    add("R1 false", gates["R1_perpendicular_1p5_route"] is False)
    add("R2 false", gates["R2_crossed_rung_3p5_composite"] is False)
    add("R3 false", gates["R3_continuation_beyond_q29_cut"] is False)
    add(
        "verdict matches failed route",
        result["verdict"]
        == "FROZEN 1.5/3.5 TRIANGLE ROUTE NOT SUPPORTED ON THIS SOURCE",
    )

    passed = sum(bool(check["passed"]) for check in checks)
    validation = {
        "test_id": result["test_id"],
        "status": "PASS" if passed == len(checks) else "FAIL",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": validation["status"],
        "passed": passed,
        "total": len(checks),
    }, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
