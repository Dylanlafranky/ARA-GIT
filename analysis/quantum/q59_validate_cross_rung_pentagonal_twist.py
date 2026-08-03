"""Independent validator for Q59 cross-rung pentagonal-twist outputs."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
import warnings

import numpy as np


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_PROTOCOL_v1_FROZEN.md"
PROTOCOL_HASH = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_PROTOCOL_v1_FROZEN.sha256"
CALIBRATION = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_CALIBRATION_LOCK.json"
CALIBRATION_HASH = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_CALIBRATION_LOCK.sha256"
RESULTS = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_RESULTS.json"
PAIR_PROFILES = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_PAIR_PROFILES.csv.gz"
SEED_PROFILES = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_SEED_PROFILES.csv.gz"
SEED_ANGLES = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_SEED_ANGLES.csv"
GRID_SUMMARY = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_GRID_SUMMARY.csv"
NULL_ERRORS = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_NULL_ERRORS.npy"
OUTPUT = ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_VALIDATION.json"
CROSSINGS = {
    "greedy": ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_GREEDY_CROSSINGS.csv.gz",
    "landmax": ROOT / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_LANDMAX_CROSSINGS.csv.gz",
}
DATASETS = {
    "greedy": {
        "derived": ROOT / "public_data" / "q40_return_flow_inhomo_v1_greedy" / "q40_derived_cache.npz",
        "connected": ROOT / "public_data" / "q40_return_flow_inhomo_v1_greedy" / "q40_connected_cache.npy",
    },
    "landmax": {
        "derived": ROOT / "public_data" / "q41b_cadence_strand_inhomo_v1_landmax" / "q41b_derived_cache.npz",
        "connected": ROOT / "public_data" / "q41b_cadence_strand_inhomo_v1_landmax" / "q41b_connected_cache.npy",
    },
}
GRID = np.round(np.arange(0.2, 2.0, 0.2), 10)
BOOTSTRAPS = 10_000
PERMUTATIONS = 1_999
RANDOM_SEED = 590031
EPS = 1e-12
FIELDS = ("c00", "c11", "c22")
TARGETS = (72.0, 144.0)
MODELS = {
    "co_rotating_positive": {"A": 1, "B": 1},
    "co_rotating_negative": {"A": -1, "B": -1},
    "counter_rotating_A_positive": {"A": 1, "B": -1},
    "counter_rotating_B_positive": {"A": -1, "B": 1},
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def angle(parent: np.ndarray, child: np.ndarray) -> float:
    denominator = np.linalg.norm(parent) * np.linalg.norm(child)
    if denominator <= EPS:
        return float("nan")
    return float(np.degrees(np.arccos(np.clip(np.dot(parent, child) / denominator, -1, 1))))


def signed_angle(parent: np.ndarray, child: np.ndarray) -> float:
    pu = (parent[0] + parent[1]) / math.sqrt(2)
    cu = (child[0] + child[1]) / math.sqrt(2)
    return float(np.degrees(np.arctan2(cu * parent[2] - child[2] * pu, cu * pu + child[2] * parent[2])))


def circular_error(value: float, target: float) -> float:
    return abs((value - target + 180) % 360 - 180)


def bootstrap(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    output = np.empty(BOOTSTRAPS)
    for start in range(0, BOOTSTRAPS, 500):
        stop = min(start + 500, BOOTSTRAPS)
        indices = rng.integers(0, len(values), size=(stop - start, len(values)))
        output[start:stop] = np.median(values[indices], axis=1)
    return tuple(float(x) for x in np.quantile(output, [0.025, 0.975]))


def independent_null(pair_rows: list[dict], target: float) -> np.ndarray:
    by_seed: dict[int, list[dict]] = defaultdict(list)
    for row in pair_rows:
        if row["archive"] == "landmax" and row["family"] in {"one_turn_15", "two_turn_7_5"}:
            by_seed[int(row["seed"])].append(row)
    seeds = sorted(by_seed)
    all_angles = np.full((PERMUTATIONS, len(seeds), 18), np.nan, dtype=np.float32)
    rng = np.random.default_rng(RANDOM_SEED + 77)
    columns = [(phase, float(x)) for phase in ("A", "B") for x in GRID]
    cindex = {item: i for i, item in enumerate(columns)}
    for sidx, seed in enumerate(seeds):
        rows = by_seed[seed]
        pairs = sorted({int(row["pair"]) for row in rows})
        pindex = {pair: i for i, pair in enumerate(pairs)}
        families = {int(row["pair"]): row["family"] for row in rows}
        labels = np.asarray([families[pair] for pair in pairs])
        n_parent = int(np.sum(labels == "one_turn_15"))
        n_child = int(np.sum(labels == "two_turn_7_5"))
        values = np.full((len(pairs), 18, 3), np.nan)
        for row in rows:
            values[pindex[int(row["pair"])], cindex[(row["phase"], float(row["ara_x"]))]] = [float(row[f"median_{field}"]) for field in FIELDS]
        for start in range(0, PERMUTATIONS, 100):
            stop = min(start + 100, PERMUTATIONS)
            order = np.argsort(rng.random((stop - start, len(pairs))), axis=1)
            permuted = values[order]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                parent = np.nanmedian(permuted[:, :n_parent], axis=1)
                child = np.nanmedian(permuted[:, n_parent:n_parent + n_child], axis=1)
            dot = np.sum(parent * child, axis=2)
            denominator = np.linalg.norm(parent, axis=2) * np.linalg.norm(child, axis=2)
            cosine = np.divide(dot, denominator, out=np.full_like(dot, np.nan), where=denominator > EPS)
            all_angles[start:stop, sidx] = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        cells = np.nanmedian(all_angles, axis=1)
    return np.nanmean(np.abs(cells - target), axis=1)


def verify_source_interpolation() -> tuple[int, float]:
    checked = 0
    maximum = 0.0
    for archive, path in CROSSINGS.items():
        derived = np.load(DATASETS[archive]["derived"])
        closure = np.asarray(derived["closure"], dtype=np.float64)
        connected = np.load(DATASETS[archive]["connected"], mmap_mode="r")
        with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            for row_index, row in enumerate(reader):
                if row_index % 9973 != 0 or checked >= 128:
                    continue
                seed, pair = int(row["seed"]), int(row["pair"])
                line = closure[seed, :, pair]
                lo, hi = np.quantile(line[:250], [0.05, 0.95])
                x = 2 * (line - lo) / (hi - lo)
                start, stop = int(row["run_start"]), int(row["run_end"]) + 1
                xx = x[start:stop]
                values = np.asarray(connected[seed, start:stop, pair], dtype=np.float64)
                if xx[0] > xx[-1]:
                    xx, values = xx[::-1], values[::-1]
                unique, inverse = np.unique(xx, return_inverse=True)
                collapsed = np.stack([np.median(values[inverse == i], axis=0) for i in range(len(unique))])
                target_x = float(row["ara_x"])
                for index, (r, c) in enumerate(((0, 0), (1, 1), (2, 2))):
                    reconstructed = float(np.interp(target_x, unique, collapsed[:, r, c]))
                    maximum = max(maximum, abs(reconstructed - float(row[FIELDS[index]])))
                checked += 1
                if checked >= 128:
                    break
    return checked, maximum


def main() -> None:
    checks = {}
    protocol_actual = sha(PROTOCOL)
    protocol_expected = PROTOCOL_HASH.read_text(encoding="utf-8").split()[0]
    calibration_actual = sha(CALIBRATION)
    calibration_expected = CALIBRATION_HASH.read_text(encoding="utf-8").split()[0]
    checks["protocol_hash"] = protocol_actual == protocol_expected
    checks["calibration_hash"] = calibration_actual == calibration_expected
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    seed_profiles = read_csv(SEED_PROFILES)
    seed_angles = read_csv(SEED_ANGLES)
    grid_rows = read_csv(GRID_SUMMARY)

    profile_lookup = {
        (row["archive"], int(row["seed"]), row["family"], row["phase"], float(row["ara_x"])): row
        for row in seed_profiles
    }
    max_angle_error = 0.0
    for row in seed_angles:
        key = (row["archive"], int(row["seed"]), row["phase"], float(row["ara_x"]))
        parent = profile_lookup[(key[0], key[1], "one_turn_15", key[2], key[3])]
        child = profile_lookup[(key[0], key[1], "two_turn_7_5", key[2], key[3])]
        other = "B" if key[2] == "A" else "A"
        wrong = profile_lookup.get((key[0], key[1], "two_turn_7_5", other, key[3]))
        p = np.asarray([float(parent[f"median_{field}"]) for field in FIELDS])
        c = np.asarray([float(child[f"median_{field}"]) for field in FIELDS])
        max_angle_error = max(max_angle_error, abs(angle(p, c) - float(row["angle_deg"])), abs(signed_angle(p, c) - float(row["signed_angle_deg"])))
        if wrong is not None:
            w = np.asarray([float(wrong[f"median_{field}"]) for field in FIELDS])
            max_angle_error = max(max_angle_error, abs(angle(p, w) - float(row["wrong_phase_angle_deg"])))
    checks["all_seed_angles"] = max_angle_error <= 1e-10

    rng = np.random.default_rng(RANDOM_SEED + 1)
    max_grid_error = 0.0
    for row in grid_rows:
        selected = np.asarray([
            float(item["angle_deg"]) for item in seed_angles
            if item["archive"] == row["archive"] and item["phase"] == row["phase"] and float(item["ara_x"]) == float(row["ara_x"])
        ])
        median = float(np.median(selected))
        low, high = bootstrap(selected, rng)
        max_grid_error = max(max_grid_error, abs(median - float(row["median_angle_deg"])), abs(low - float(row["ci_low"])), abs(high - float(row["ci_high"])))
    checks["all_grid_medians_and_bootstraps"] = max_grid_error <= 1e-10

    greedy = [row for row in grid_rows if row["archive"] == "greedy"]
    target_errors = {target: np.mean([abs(float(row["median_angle_deg"]) - target) for row in greedy]) for target in TARGETS}
    selected_target = min(TARGETS, key=lambda target: (target_errors[target], target))
    model_errors = {
        model: np.mean([circular_error(float(row["median_signed_angle_deg"]), signs[row["phase"]] * selected_target) for row in greedy])
        for model, signs in MODELS.items()
    }
    selected_model = min(MODELS, key=lambda model: (model_errors[model], list(MODELS).index(model)))
    checks["calibration_selection"] = selected_target == calibration["selected_target_deg"] and selected_model == calibration["selected_signed_model"]

    checked_interpolations, interpolation_error = verify_source_interpolation()
    checks["source_interpolations"] = checked_interpolations >= 128 and interpolation_error <= 1e-10

    pair_rows = read_csv(PAIR_PROFILES)
    recalculated_null = independent_null(pair_rows, float(selected_target))
    stored_null = np.load(NULL_ERRORS)
    stored_quantiles = np.quantile(stored_null, [0.025, 0.5, 0.975])
    recalculated_quantiles = np.quantile(recalculated_null, [0.025, 0.5, 0.975])
    null_quantile_error = float(np.max(np.abs(recalculated_quantiles - stored_quantiles)))
    checks["independent_permutation_null_distribution"] = null_quantile_error <= 1.0
    observed = float(results["evaluation"]["permutation_null"]["observed_error_deg"])
    p = float((1 + np.sum(recalculated_null <= observed)) / (1 + len(recalculated_null)))
    stored_p = float(results["evaluation"]["permutation_null"]["one_sided_no_worse_than_null_probability"])
    checks["independent_permutation_probability"] = abs(p - stored_p) <= 0.03

    validation = {
        "test_id": "Q59-INDEPENDENT-VALIDATION-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "maximum_seed_angle_error": max_angle_error,
        "maximum_grid_or_bootstrap_error": max_grid_error,
        "sampled_source_interpolations": checked_interpolations,
        "maximum_source_interpolation_error": interpolation_error,
        "stored_null_quantiles": [float(x) for x in stored_quantiles],
        "recomputed_null_quantiles": [float(x) for x in recalculated_quantiles],
        "maximum_null_quantile_error": null_quantile_error,
        "recomputed_permutation_probability": p,
        "protocol_sha256": protocol_actual,
        "calibration_lock_sha256": calibration_actual,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
