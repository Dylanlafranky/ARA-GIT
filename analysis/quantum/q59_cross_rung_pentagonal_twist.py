"""Q59 frozen directional cross-rung pentagonal-twist test.

The full connected-correlation matrix direction is compared between the Q42
one-turn-15 parent cadence and two-turn-7.5 child cadence at fixed local ARA
coordinates. Greedy calibrates the pentagonal route and handedness; Landmax is
loaded only after the calibration lock has been written and hashed.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import pathlib
import warnings
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
TEST_ID = "Q59-CROSS-RUNG-PENTAGONAL-TWIST-v1"
PROTOCOL = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_PROTOCOL_v1_FROZEN.md"
PROTOCOL_HASH = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_PROTOCOL_v1_FROZEN.sha256"
CALIBRATION = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_CALIBRATION_LOCK.json"
CALIBRATION_HASH = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_CALIBRATION_LOCK.sha256"
RESULTS = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_RESULTS.json"
PAIR_PROFILES = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_PAIR_PROFILES.csv.gz"
SEED_PROFILES = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_SEED_PROFILES.csv.gz"
SEED_ANGLES = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_SEED_ANGLES.csv"
GRID_SUMMARY = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_GRID_SUMMARY.csv"
NULL_ERRORS = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_NULL_ERRORS.npy"
FIGURE_PNG = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST.png"
FIGURE_SVG = HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST.svg"
CROSSINGS = {
    "greedy": HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_GREEDY_CROSSINGS.csv.gz",
    "landmax": HERE / "Q59_CROSS_RUNG_PENTAGONAL_TWIST_LANDMAX_CROSSINGS.csv.gz",
}

GRID = np.round(np.arange(0.2, 2.0, 0.2), 10)
PENTAGON_TARGETS = (72.0, 144.0)
LANDMARKS = {
    "identical": 0.0,
    "hexagon edge": 60.0,
    "pentagon edge": 72.0,
    "perpendicular": 90.0,
    "pentagon interior": 108.0,
    "hexagon diagonal": 120.0,
    "golden angle": 137.507764,
    "pentagon diagonal": 144.0,
    "inverted": 180.0,
}
TOLERANCE = 8.0
SIGNED_TOLERANCE = 10.0
BOOTSTRAP_DRAWS = 10_000
PERMUTATION_DRAWS = 1_999
RANDOM_SEED = 590031
EPS = 1e-12

DATASETS = {
    "greedy": {
        "derived": HERE / "public_data" / "q40_return_flow_inhomo_v1_greedy" / "q40_derived_cache.npz",
        "connected": HERE / "public_data" / "q40_return_flow_inhomo_v1_greedy" / "q40_connected_cache.npy",
    },
    "landmax": {
        "derived": HERE / "public_data" / "q41b_cadence_strand_inhomo_v1_landmax" / "q41b_derived_cache.npz",
        "connected": HERE / "public_data" / "q41b_cadence_strand_inhomo_v1_landmax" / "q41b_connected_cache.npy",
    },
}

BLUE = "#537DB8"
GOLD = "#D99B31"
INK = "#17212B"
MID = "#687684"
LIGHT = "#DCE4EC"
GRID_COLOR = "#D9E0E7"
BG = "#FAFBFC"


def digest(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"No rows for {path.name}")
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def safe_correlation(a: np.ndarray, b: np.ndarray) -> float:
    left = np.asarray(a, dtype=np.float64).ravel()
    right = np.asarray(b, dtype=np.float64).ravel()
    if left.size < 3 or right.size != left.size:
        return float("nan")
    left = left - np.mean(left)
    right = right - np.mean(right)
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    if denominator <= EPS:
        return float("nan")
    return float(np.dot(left, right) / denominator)


def lag_coordinate_correlation(u: np.ndarray, v: np.ndarray, lag: int) -> float:
    if lag <= 0 or lag >= len(u) - 2:
        return float("nan")
    first = np.column_stack((u[:-lag], v[:-lag]))
    second = np.column_stack((u[lag:], v[lag:]))
    return safe_correlation(first, second)


def cadence_family(u: np.ndarray, v: np.ndarray) -> str:
    selected_u = np.asarray(u[250:499], dtype=np.float64)
    selected_v = np.asarray(v[250:499], dtype=np.float64)
    theta = np.unwrap(np.arctan2(selected_v, selected_u))
    sample = np.arange(len(theta), dtype=np.float64)
    slope, _intercept = np.polyfit(sample, theta, 1)
    period = float(2 * np.pi / abs(slope))
    lag_15 = lag_coordinate_correlation(selected_u, selected_v, 15)
    if 7.35 <= period <= 7.65 and lag_15 >= 0.95:
        return "two_turn_7_5"
    if 14.8 <= period <= 15.2 and lag_15 >= 0.95:
        return "one_turn_15"
    return "other"


def quadrant_labels(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    labels = np.empty(u.shape, dtype=np.int8)
    labels[(u >= 0) & (v >= 0)] = 0
    labels[(u < 0) & (v >= 0)] = 1
    labels[(u < 0) & (v < 0)] = 2
    labels[(u >= 0) & (v < 0)] = 3
    return labels


def coordinates(line: np.ndarray):
    development = np.asarray(line[:250], dtype=np.float64)
    flow = np.diff(development)
    lo, hi = np.quantile(development, [0.05, 0.95])
    centre, radius = (lo + hi) / 2, (hi - lo) / 2
    scale = float(np.quantile(np.abs(flow), 0.95))
    if not np.isfinite(radius) or not np.isfinite(scale) or radius <= EPS or scale <= EPS:
        return None
    u = (np.asarray(line[:-1], dtype=np.float64) - centre) / radius
    v = np.diff(np.asarray(line, dtype=np.float64)) / scale
    labels = quadrant_labels(u, v)
    dev_plane = u[:249] + 1j * v[:249]
    finite = np.isfinite(dev_plane.real) & np.isfinite(dev_plane.imag)
    if np.mean(finite) < 0.95:
        return None
    valid = dev_plane[finite]
    turn = np.angle(np.conj(valid[:-1]) * valid[1:])
    turn = turn[np.isfinite(turn) & (np.abs(turn) > 1e-10)]
    if not turn.size:
        return None
    signed_turn = float(np.mean(np.sign(turn)))
    coherence = abs(signed_turn)
    occupancy = min(float(np.mean(labels[:249] == q)) for q in range(4))
    return u, v, coherence, occupancy


def fill_zero_signs(signs: np.ndarray) -> np.ndarray:
    signs = np.asarray(signs, dtype=np.int8).copy()
    previous = 0
    for index in range(len(signs)):
        if signs[index]:
            previous = int(signs[index])
        elif previous:
            signs[index] = previous
    following = 0
    for index in range(len(signs) - 1, -1, -1):
        if signs[index]:
            following = int(signs[index])
        elif following:
            signs[index] = following
    return signs


def transition_runs(line: np.ndarray, first: int = 250, last: int = 497) -> list[dict]:
    delta = np.diff(np.asarray(line, dtype=np.float64))
    signs = fill_zero_signs(np.sign(delta[first:last + 1]))
    output = []
    start = 0
    for index in range(1, len(signs) + 1):
        if index == len(signs) or signs[index] != signs[start]:
            output.append({"sign": int(signs[start]), "start": int(first + start), "end": int(first + index - 1)})
            start = index
    return [item for item in output if item["sign"] != 0]


def run_positions(x: np.ndarray, run: dict) -> np.ndarray:
    return np.asarray(x[run["start"]:run["end"] + 2], dtype=np.float64)


def qualifying_half(values: np.ndarray, run: dict) -> bool:
    transitions = run["end"] - run["start"] + 1
    return bool(transitions >= 3 and np.min(values) <= 0.5 and np.max(values) >= 1.5)


def interpolate_matrix_at_grid(
    coordinate: np.ndarray,
    matrices: np.ndarray,
    run: dict,
) -> dict[float, np.ndarray]:
    start = int(run["start"])
    stop = int(run["end"] + 2)
    x = np.asarray(coordinate[start:stop], dtype=np.float64)
    values = np.asarray(matrices[start:stop], dtype=np.float64).reshape(-1, 9)
    finite = np.isfinite(x) & np.all(np.isfinite(values), axis=1)
    x, values = x[finite], values[finite]
    if len(x) < 2:
        return {}
    if x[0] > x[-1]:
        x, values = x[::-1], values[::-1]
    unique, inverse = np.unique(x, return_inverse=True)
    if len(unique) < 2:
        return {}
    collapsed = np.vstack([
        np.median(values[inverse == index], axis=0)
        for index in range(len(unique))
    ])
    output = {}
    for value in GRID:
        if unique[0] - 1e-12 <= value <= unique[-1] + 1e-12:
            vector = np.asarray([
                np.interp(value, unique, collapsed[:, column])
                for column in range(9)
            ])
            output[float(value)] = vector.reshape(3, 3)
    return output


def extract_archive(archive: str) -> tuple[list[dict], dict]:
    paths = DATASETS[archive]
    if not paths["derived"].exists() or not paths["connected"].exists():
        raise RuntimeError(f"Missing source cache for {archive}")
    derived = np.load(paths["derived"])
    closure = np.asarray(derived["closure"], dtype=np.float32)
    connected = np.load(paths["connected"], mmap_mode="r")
    rows: list[dict] = []
    eligible = 0
    family_counts = defaultdict(int)
    cycle_count = 0
    offdiag_max = 0.0
    xy_max = 0.0
    for seed in range(closure.shape[0]):
        seed_matrices = np.asarray(connected[seed], dtype=np.float64)
        offdiag = seed_matrices[..., [0, 0, 1, 1, 2, 2], [1, 2, 0, 2, 0, 1]]
        offdiag_max = max(offdiag_max, float(np.max(np.abs(offdiag))))
        xy_max = max(xy_max, float(np.max(np.abs(seed_matrices[..., 0, 0] - seed_matrices[..., 1, 1]))))
        for pair in range(closure.shape[2]):
            line = np.asarray(closure[seed, :, pair], dtype=np.float64)
            coordinate_info = coordinates(line)
            if coordinate_info is None:
                continue
            u, v, coherence, occupancy = coordinate_info
            if coherence < 0.80 or occupancy < 0.05:
                continue
            eligible += 1
            family = cadence_family(u, v)
            family_counts[family] += 1
            lo, hi = np.quantile(line[:250], [0.05, 0.95])
            if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo <= EPS:
                continue
            x = 2 * (line - lo) / (hi - lo)
            matrices = seed_matrices[:, pair]
            runs = transition_runs(line)
            index = 0
            cycle = 0
            while index < len(runs) - 1:
                forward_run, return_run = runs[index], runs[index + 1]
                if forward_run["sign"] <= 0 or return_run["sign"] >= 0:
                    index += 1
                    continue
                if not (
                    qualifying_half(run_positions(x, forward_run), forward_run)
                    and qualifying_half(run_positions(x, return_run), return_run)
                ):
                    index += 1
                    continue
                for phase, run in (("A", forward_run), ("B", return_run)):
                    interpolated = interpolate_matrix_at_grid(x, matrices, run)
                    for grid_x, matrix in sorted(interpolated.items()):
                        rows.append({
                            "archive": archive,
                            "seed": seed,
                            "pair": pair,
                            "family": family,
                            "cycle": cycle,
                            "phase": phase,
                            "ara_x": grid_x,
                            "c00": float(matrix[0, 0]),
                            "c11": float(matrix[1, 1]),
                            "c22": float(matrix[2, 2]),
                            "run_start": int(run["start"]),
                            "run_end": int(run["end"] + 1),
                        })
                cycle += 1
                cycle_count += 1
                index += 2
    inventory = {
        "archive": archive,
        "source_shapes": {"closure": list(closure.shape), "connected": list(connected.shape)},
        "eligible_lineages": eligible,
        "family_lineages": dict(family_counts),
        "qualifying_cycles": cycle_count,
        "crossing_rows": len(rows),
        "offdiagonal_max_abs": offdiag_max,
        "max_abs_cxx_minus_cyy": xy_max,
        "source_hashes": {key: digest(path) for key, path in paths.items()},
    }
    return rows, inventory


VECTOR_FIELDS = ("c00", "c11", "c22")


def aggregate_profiles(crossings: list[dict]) -> tuple[list[dict], list[dict]]:
    grouped: dict[tuple, list[np.ndarray]] = defaultdict(list)
    for row in crossings:
        key = (row["archive"], row["seed"], row["pair"], row["family"], row["phase"], float(row["ara_x"]))
        grouped[key].append(np.asarray([row[field] for field in VECTOR_FIELDS], dtype=np.float64))
    pair_rows = []
    for key, values in sorted(grouped.items()):
        data = np.vstack(values)
        med = np.median(data, axis=0)
        avg = np.mean(data, axis=0)
        pair_rows.append({
            "archive": key[0], "seed": key[1], "pair": key[2],
            "family": key[3], "phase": key[4], "ara_x": key[5],
            "cycles": len(values),
            **{f"median_{field}": float(med[i]) for i, field in enumerate(VECTOR_FIELDS)},
            **{f"mean_{field}": float(avg[i]) for i, field in enumerate(VECTOR_FIELDS)},
        })
    seed_grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in pair_rows:
        key = (row["archive"], row["seed"], row["family"], row["phase"], float(row["ara_x"]))
        seed_grouped[key].append(row)
    seed_rows = []
    for key, rows in sorted(seed_grouped.items()):
        med_data = np.asarray([[row[f"median_{field}"] for field in VECTOR_FIELDS] for row in rows])
        mean_data = np.asarray([[row[f"mean_{field}"] for field in VECTOR_FIELDS] for row in rows])
        med = np.median(med_data, axis=0)
        avg = np.mean(mean_data, axis=0)
        seed_rows.append({
            "archive": key[0], "seed": key[1], "family": key[2],
            "phase": key[3], "ara_x": key[4], "pairs": len(rows),
            **{f"median_{field}": float(med[i]) for i, field in enumerate(VECTOR_FIELDS)},
            **{f"mean_{field}": float(avg[i]) for i, field in enumerate(VECTOR_FIELDS)},
        })
    return pair_rows, seed_rows


def vector_from(row: dict, prefix: str = "median") -> np.ndarray:
    return np.asarray([row[f"{prefix}_{field}"] for field in VECTOR_FIELDS], dtype=np.float64)


def frobenius_angle(parent: np.ndarray, child: np.ndarray) -> float:
    denominator = float(np.linalg.norm(parent) * np.linalg.norm(child))
    if denominator <= EPS:
        return float("nan")
    cosine = float(np.clip(np.dot(parent, child) / denominator, -1.0, 1.0))
    return float(np.degrees(np.arccos(cosine)))


def signed_plane_angle(parent: np.ndarray, child: np.ndarray) -> float:
    parent_u = float((parent[0] + parent[1]) / math.sqrt(2))
    child_u = float((child[0] + child[1]) / math.sqrt(2))
    parent_v, child_v = float(parent[2]), float(child[2])
    if math.hypot(parent_u, parent_v) <= EPS or math.hypot(child_u, child_v) <= EPS:
        return float("nan")
    cross = child_u * parent_v - child_v * parent_u
    dot = child_u * parent_u + child_v * parent_v
    return float(np.degrees(np.arctan2(cross, dot)))


def make_seed_angles(seed_profiles: list[dict]) -> list[dict]:
    lookup = {
        (row["archive"], row["seed"], row["family"], row["phase"], row["ara_x"]): row
        for row in seed_profiles
    }
    output = []
    for archive, seed in sorted({(row["archive"], row["seed"]) for row in seed_profiles}):
        for phase in ("A", "B"):
            other = "B" if phase == "A" else "A"
            for grid_x in GRID:
                parent = lookup.get((archive, seed, "one_turn_15", phase, float(grid_x)))
                child = lookup.get((archive, seed, "two_turn_7_5", phase, float(grid_x)))
                wrong_child = lookup.get((archive, seed, "two_turn_7_5", other, float(grid_x)))
                if parent is None or child is None:
                    continue
                p = vector_from(parent)
                c = vector_from(child)
                pa = vector_from(parent, "mean")
                ca = vector_from(child, "mean")
                wrong = vector_from(wrong_child) if wrong_child is not None else np.full(3, np.nan)
                output.append({
                    "archive": archive,
                    "seed": seed,
                    "phase": phase,
                    "ara_x": float(grid_x),
                    "parent_pairs": int(parent["pairs"]),
                    "child_pairs": int(child["pairs"]),
                    "parent_norm": float(np.linalg.norm(p)),
                    "child_norm": float(np.linalg.norm(c)),
                    "angle_deg": frobenius_angle(p, c),
                    "signed_angle_deg": signed_plane_angle(p, c),
                    "wrong_phase_angle_deg": frobenius_angle(p, wrong),
                    "mean_robustness_angle_deg": frobenius_angle(pa, ca),
                })
    if not output:
        raise RuntimeError("No matched seed angles")
    return output


def bootstrap_median(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if not len(values):
        return float("nan"), float("nan")
    medians = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for start in range(0, BOOTSTRAP_DRAWS, 500):
        stop = min(start + 500, BOOTSTRAP_DRAWS)
        indices = rng.integers(0, len(values), size=(stop - start, len(values)))
        medians[start:stop] = np.median(values[indices], axis=1)
    return tuple(float(x) for x in np.quantile(medians, [0.025, 0.975]))


def circular_error(value: float | np.ndarray, target: float | np.ndarray):
    difference = (np.asarray(value) - np.asarray(target) + 180.0) % 360.0 - 180.0
    return np.abs(difference)


def bootstrap_whole_grid_phase(
    seed_angles: list[dict],
    archive: str,
    phase: str,
    rng: np.random.Generator,
) -> tuple[float, float]:
    selected = [row for row in seed_angles if row["archive"] == archive and row["phase"] == phase]
    seeds = sorted({int(row["seed"]) for row in selected})
    lookup = {(int(row["seed"]), float(row["ara_x"])): float(row["angle_deg"]) for row in selected}
    matrix = np.asarray([[lookup.get((seed, float(x)), np.nan) for x in GRID] for seed in seeds])
    draws = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for start in range(0, BOOTSTRAP_DRAWS, 500):
        stop = min(start + 500, BOOTSTRAP_DRAWS)
        indices = rng.integers(0, len(seeds), size=(stop - start, len(seeds)))
        sampled = matrix[indices]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            cell_medians = np.nanmedian(sampled, axis=1)
            draws[start:stop] = np.nanmedian(cell_medians, axis=1)
    return tuple(float(x) for x in np.quantile(draws, [0.025, 0.975]))


def summarize_grid(seed_angles: list[dict], target: float | None, rng_seed: int) -> list[dict]:
    rng = np.random.default_rng(rng_seed)
    output = []
    for archive in ("greedy", "landmax"):
        for phase in ("A", "B"):
            for grid_x in GRID:
                selected = [
                    row for row in seed_angles
                    if row["archive"] == archive and row["phase"] == phase and row["ara_x"] == float(grid_x)
                ]
                if not selected:
                    continue
                values = np.asarray([row["angle_deg"] for row in selected])
                wrong = np.asarray([row["wrong_phase_angle_deg"] for row in selected])
                signed = np.asarray([row["signed_angle_deg"] for row in selected])
                robust = np.asarray([row["mean_robustness_angle_deg"] for row in selected])
                ci_low, ci_high = bootstrap_median(values, rng)
                median = float(np.nanmedian(values))
                nearest = min(LANDMARKS, key=lambda name: abs(median - LANDMARKS[name]))
                output.append({
                    "archive": archive,
                    "phase": phase,
                    "ara_x": float(grid_x),
                    "n_seeds": len(selected),
                    "median_angle_deg": median,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "median_signed_angle_deg": float(np.nanmedian(signed)),
                    "median_wrong_phase_angle_deg": float(np.nanmedian(wrong)),
                    "median_mean_robustness_angle_deg": float(np.nanmedian(robust)),
                    "nearest_landmark": nearest,
                    "nearest_landmark_angle": LANDMARKS[nearest],
                    "target_error_deg": abs(median - target) if target is not None else float("nan"),
                    "inside_target_band": int(abs(median - target) <= TOLERANCE) if target is not None else 0,
                    "minimum_parent_norm": float(min(row["parent_norm"] for row in selected)),
                    "minimum_child_norm": float(min(row["child_norm"] for row in selected)),
                })
    return output


SIGNED_MODELS = {
    "co_rotating_positive": {"A": 1, "B": 1},
    "co_rotating_negative": {"A": -1, "B": -1},
    "counter_rotating_A_positive": {"A": 1, "B": -1},
    "counter_rotating_B_positive": {"A": -1, "B": 1},
}


def calibrate(greedy_grid: list[dict], protocol_hash: str) -> dict:
    rows = [row for row in greedy_grid if row["archive"] == "greedy"]
    target_errors = {
        str(int(target)): float(np.mean([abs(row["median_angle_deg"] - target) for row in rows]))
        for target in PENTAGON_TARGETS
    }
    selected_target = min(PENTAGON_TARGETS, key=lambda target: (target_errors[str(int(target))], target))
    model_errors = {}
    for model, signs in SIGNED_MODELS.items():
        model_errors[model] = float(np.mean([
            circular_error(row["median_signed_angle_deg"], signs[row["phase"]] * selected_target)
            for row in rows
        ]))
    selected_model = min(SIGNED_MODELS, key=lambda model: (model_errors[model], list(SIGNED_MODELS).index(model)))
    return {
        "test_id": TEST_ID,
        "created_before_landmax_load": True,
        "created_at": datetime.now(ZoneInfo("Australia/Brisbane")).isoformat(),
        "protocol_sha256": protocol_hash,
        "calibration_archive": "greedy",
        "replication_archive_not_yet_loaded": "landmax",
        "target_candidate_mean_absolute_errors_deg": target_errors,
        "selected_target_deg": selected_target,
        "signed_model_mean_circular_errors_deg": model_errors,
        "selected_signed_model": selected_model,
        "selected_signed_targets_deg": {
            phase: sign * selected_target
            for phase, sign in SIGNED_MODELS[selected_model].items()
        },
        "tolerance_deg": TOLERANCE,
        "signed_tolerance_deg": SIGNED_TOLERANCE,
    }


def family_label_null(pair_rows: list[dict], target: float) -> tuple[np.ndarray, float]:
    selected_rows = [row for row in pair_rows if row["archive"] == "landmax" and row["family"] in {"one_turn_15", "two_turn_7_5"}]
    by_seed: dict[int, list[dict]] = defaultdict(list)
    for row in selected_rows:
        by_seed[int(row["seed"])].append(row)
    seeds = sorted(by_seed)
    draw_seed_angles = np.full((PERMUTATION_DRAWS, len(seeds), 18), np.nan, dtype=np.float32)
    rng = np.random.default_rng(RANDOM_SEED + 77)
    columns = [(phase, float(x)) for phase in ("A", "B") for x in GRID]
    for seed_index, seed in enumerate(seeds):
        rows = by_seed[seed]
        pairs = sorted({int(row["pair"]) for row in rows})
        family_by_pair = {int(row["pair"]): row["family"] for row in rows}
        labels = np.asarray([family_by_pair[pair] for pair in pairs])
        n_parent = int(np.sum(labels == "one_turn_15"))
        n_child = int(np.sum(labels == "two_turn_7_5"))
        if n_parent == 0 or n_child == 0:
            continue
        values = np.full((len(pairs), 18, 3), np.nan, dtype=np.float64)
        pair_index = {pair: index for index, pair in enumerate(pairs)}
        column_index = {key: index for index, key in enumerate(columns)}
        for row in rows:
            cidx = column_index[(row["phase"], float(row["ara_x"]))]
            values[pair_index[int(row["pair"])], cidx] = [row[f"median_{field}"] for field in VECTOR_FIELDS]
        for start in range(0, PERMUTATION_DRAWS, 100):
            stop = min(start + 100, PERMUTATION_DRAWS)
            order = np.argsort(rng.random((stop - start, len(pairs))), axis=1)
            shuffled = values[order]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                parent = np.nanmedian(shuffled[:, :n_parent], axis=1)
                child = np.nanmedian(shuffled[:, n_parent:n_parent + n_child], axis=1)
            dot = np.sum(parent * child, axis=2)
            denominator = np.linalg.norm(parent, axis=2) * np.linalg.norm(child, axis=2)
            cosine = np.divide(dot, denominator, out=np.full_like(dot, np.nan), where=denominator > EPS)
            draw_seed_angles[start:stop, seed_index] = np.degrees(np.arccos(np.clip(cosine, -1, 1))).astype(np.float32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        draw_cells = np.nanmedian(draw_seed_angles, axis=1)
    errors = np.nanmean(np.abs(draw_cells - target), axis=1).astype(np.float64)
    return errors, float(np.mean(np.isfinite(draw_cells)))


def evaluate(grid_rows: list[dict], seed_angles: list[dict], calibration: dict, null_errors: np.ndarray, inventory: dict) -> dict:
    target = float(calibration["selected_target_deg"])
    phase_checks = {}
    strict = []
    phase_rng = np.random.default_rng(RANDOM_SEED + 2)
    for phase in ("A", "B"):
        cells = sorted([row for row in grid_rows if row["archive"] == "landmax" and row["phase"] == phase], key=lambda row: row["ara_x"])
        whole_median = float(np.median([row["median_angle_deg"] for row in cells]))
        nearest = min(LANDMARKS, key=lambda name: abs(whole_median - LANDMARKS[name]))
        item = {
            "cells_inside_target_band": int(sum(row["inside_target_band"] for row in cells)),
            "mean_absolute_target_error_deg": float(np.mean([row["target_error_deg"] for row in cells])),
            "whole_grid_median_deg": whole_median,
            "nearest_landmark": nearest,
            "nearest_landmark_angle_deg": LANDMARKS[nearest],
            "nearest_is_selected_target": bool(abs(LANDMARKS[nearest] - target) <= 1e-12),
            "whole_grid_seed_bootstrap_95_ci_deg": list(
                bootstrap_whole_grid_phase(seed_angles, "landmax", phase, phase_rng)
            ),
        }
        phase_checks[phase] = item
        strict.extend([
            item["cells_inside_target_band"] >= 7,
            item["mean_absolute_target_error_deg"] <= TOLERANCE,
            item["nearest_is_selected_target"],
        ])
    signed_targets = calibration["selected_signed_targets_deg"]
    landmax_cells = [row for row in grid_rows if row["archive"] == "landmax"]
    signed_errors = np.asarray([
        circular_error(row["median_signed_angle_deg"], float(signed_targets[row["phase"]]))
        for row in landmax_cells
    ])
    signed_check = {
        "mean_circular_error_deg": float(np.mean(signed_errors)),
        "cells_within_10_deg": int(np.sum(signed_errors <= SIGNED_TOLERANCE)),
        "cells_total": len(signed_errors),
    }
    strict.extend([
        signed_check["mean_circular_error_deg"] <= SIGNED_TOLERANCE,
        signed_check["cells_within_10_deg"] >= 14,
    ])
    cross_archive = {}
    for phase in ("A", "B"):
        greedy = {row["ara_x"]: row["median_angle_deg"] for row in grid_rows if row["archive"] == "greedy" and row["phase"] == phase}
        landmax = {row["ara_x"]: row["median_angle_deg"] for row in grid_rows if row["archive"] == "landmax" and row["phase"] == phase}
        cross_archive[phase] = float(np.mean([abs(greedy[x] - landmax[x]) for x in GRID]))
        strict.append(cross_archive[phase] <= 10.0)
    same_error = float(np.mean([abs(row["median_angle_deg"] - target) for row in landmax_cells]))
    wrong_error = float(np.mean([abs(row["median_wrong_phase_angle_deg"] - target) for row in landmax_cells]))
    same_phase_control = {
        "same_phase_mean_absolute_error_deg": same_error,
        "wrong_phase_mean_absolute_error_deg": wrong_error,
        "same_phase_better": same_error < wrong_error,
    }
    strict.append(same_phase_control["same_phase_better"])
    finite_null = null_errors[np.isfinite(null_errors)]
    permutation_p = float((1 + np.sum(finite_null <= same_error)) / (1 + len(finite_null)))
    permutation = {
        "draws": int(len(finite_null)),
        "observed_error_deg": same_error,
        "null_median_error_deg": float(np.median(finite_null)),
        "null_95_interval_deg": [float(x) for x in np.quantile(finite_null, [0.025, 0.975])],
        "one_sided_no_worse_than_null_probability": permutation_p,
    }
    strict.append(permutation_p <= 0.01)
    minimum_parent = min(row["parent_norm"] for row in seed_angles)
    minimum_child = min(row["child_norm"] for row in seed_angles)
    minimum_seeds = min(row["n_seeds"] for row in grid_rows)
    data_gate = {
        "minimum_matched_seeds": int(minimum_seeds),
        "minimum_parent_norm": float(minimum_parent),
        "minimum_child_norm": float(minimum_child),
        "maximum_source_offdiagonal_abs": float(max(item["offdiagonal_max_abs"] for item in inventory.values())),
        "maximum_abs_cxx_minus_cyy": float(max(item["max_abs_cxx_minus_cyy"] for item in inventory.values())),
    }
    data_gate["passed"] = bool(
        minimum_seeds >= 50
        and minimum_parent > EPS
        and minimum_child > EPS
        and data_gate["maximum_source_offdiagonal_abs"] <= EPS
        and data_gate["maximum_abs_cxx_minus_cyy"] <= EPS
    )
    return {
        "data_gate": data_gate,
        "phase_checks": phase_checks,
        "signed_check": signed_check,
        "cross_archive_mean_absolute_difference_deg": cross_archive,
        "same_phase_control": same_phase_control,
        "permutation_null": permutation,
        "strict_components": [bool(x) for x in strict],
        "strict_support": bool(data_gate["passed"] and all(strict)),
    }


def plot_figure(grid_rows: list[dict], calibration: dict, evaluation: dict) -> None:
    target = float(calibration["selected_target_deg"])
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 10.5), facecolor=BG)
    colors = {"greedy": BLUE, "landmax": GOLD}
    markers = {"greedy": "o", "landmax": "s"}
    for phase, axis in zip(("A", "B"), axes[0]):
        for name, value in LANDMARKS.items():
            if value in {target, 0.0, 180.0}:
                continue
            axis.axhline(value, color=LIGHT, linewidth=0.8, linestyle=":" if value != 90 else "--", zorder=0)
        axis.axhspan(target - TOLERANCE, target + TOLERANCE, color="#F5DCA9", alpha=0.45, zorder=0)
        axis.axhline(target, color=INK, linewidth=2, linestyle="--", label=f"locked target {target:.0f}°")
        for archive in ("greedy", "landmax"):
            rows = sorted([row for row in grid_rows if row["archive"] == archive and row["phase"] == phase], key=lambda row: row["ara_x"])
            x = np.asarray([row["ara_x"] for row in rows])
            y = np.asarray([row["median_angle_deg"] for row in rows])
            low = np.asarray([row["ci_low"] for row in rows])
            high = np.asarray([row["ci_high"] for row in rows])
            axis.plot(x, y, marker=markers[archive], color=colors[archive], linewidth=2.2, label=archive)
            axis.fill_between(x, low, high, color=colors[archive], alpha=0.12)
        axis.set_title(f"Phase {phase}: parent/child correlation-space angle", loc="left", fontweight="bold")
        axis.set_xlabel("local ARA coordinate x")
        axis.set_ylabel("unsigned angle (degrees)")
        axis.set_xticks(GRID)
        axis.set_ylim(-5, 185)
        axis.legend(frameon=False, ncol=3, fontsize=9)
    axis = axes[1, 0]
    for phase, marker in (("A", "o"), ("B", "s")):
        rows = sorted([row for row in grid_rows if row["archive"] == "landmax" and row["phase"] == phase], key=lambda row: row["ara_x"])
        axis.plot([row["ara_x"] for row in rows], [row["median_signed_angle_deg"] for row in rows], marker=marker, linewidth=2.2, label=f"Phase {phase}", color=BLUE if phase == "A" else GOLD)
        axis.axhline(float(calibration["selected_signed_targets_deg"][phase]), color=BLUE if phase == "A" else GOLD, linestyle="--", linewidth=1.4)
    axis.axhline(0, color=INK, linewidth=1)
    axis.set_title("Landmax signed child-to-parent twist", loc="left", fontweight="bold")
    axis.set_xlabel("local ARA coordinate x")
    axis.set_ylabel("signed angle (degrees)")
    axis.set_xticks(GRID)
    axis.set_ylim(-185, 185)
    axis.legend(frameon=False)
    axis = axes[1, 1]
    landmax = [row for row in grid_rows if row["archive"] == "landmax"]
    errors = {name: float(np.mean([abs(row["median_angle_deg"] - value) for row in landmax])) for name, value in LANDMARKS.items()}
    ordered = sorted(errors, key=errors.get)
    bar_colors = [GOLD if abs(LANDMARKS[name] - target) <= EPS else LIGHT for name in ordered]
    bars = axis.barh(ordered, [errors[name] for name in ordered], color=bar_colors, edgecolor=INK, linewidth=0.7)
    axis.invert_yaxis()
    axis.set_title("Landmax error to predeclared angular landmarks", loc="left", fontweight="bold")
    axis.set_xlabel("mean absolute error (degrees; lower is better)")
    axis.grid(axis="x", color=GRID_COLOR)
    axis.grid(axis="y", visible=False)
    for bar, name in zip(bars, ordered):
        axis.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, f"{errors[name]:.1f}°", va="center", fontsize=9, color=INK)
    fig.suptitle("Q59 — cross-rung pentagonal twist", x=0.055, y=0.985, ha="left", fontsize=19, fontweight="bold", color=INK)
    status = "SUPPORTED" if evaluation["strict_support"] else "NOT SUPPORTED"
    fig.text(0.055, 0.947, f"Greedy calibration → untouched Landmax replication · {status} · full connected-matrix direction", ha="left", fontsize=11, color=MID)
    fig.text(0.055, 0.015, "Source: Zenodo 10.5281/zenodo.16753415 · 100 seeds/archive · fixed x=0.2…1.8 · 95% seed-bootstrap intervals", fontsize=9, color=MID)
    fig.tight_layout(rect=(0.04, 0.045, 0.99, 0.93))
    fig.savefig(FIGURE_PNG, dpi=180, facecolor=BG)
    fig.savefig(FIGURE_SVG, facecolor=BG)
    plt.close(fig)


def main() -> None:
    protocol_hash = digest(PROTOCOL)
    expected_hash = PROTOCOL_HASH.read_text(encoding="utf-8").split()[0]
    if protocol_hash != expected_hash:
        raise RuntimeError("Frozen protocol hash mismatch")

    # Calibration archive only. Landmax is deliberately not opened before lock.
    greedy_crossings, greedy_inventory = extract_archive("greedy")
    write_csv(CROSSINGS["greedy"], greedy_crossings)
    greedy_pairs, greedy_seeds = aggregate_profiles(greedy_crossings)
    greedy_angles = make_seed_angles(greedy_seeds)
    greedy_grid_unscored = summarize_grid(greedy_angles, None, RANDOM_SEED)
    calibration = calibrate(greedy_grid_unscored, protocol_hash)
    CALIBRATION.write_text(json.dumps(calibration, indent=2), encoding="utf-8")
    calibration_hash = digest(CALIBRATION)
    CALIBRATION_HASH.write_text(f"{calibration_hash}  {CALIBRATION.name}\n", encoding="utf-8")

    # Untouched replication archive is loaded only after the lock exists.
    landmax_crossings, landmax_inventory = extract_archive("landmax")
    write_csv(CROSSINGS["landmax"], landmax_crossings)
    landmax_pairs, landmax_seeds = aggregate_profiles(landmax_crossings)
    pair_rows = greedy_pairs + landmax_pairs
    seed_rows = greedy_seeds + landmax_seeds
    seed_angles = greedy_angles + make_seed_angles(landmax_seeds)
    target = float(calibration["selected_target_deg"])
    grid_rows = summarize_grid(seed_angles, target, RANDOM_SEED + 1)
    null_errors, null_finite_fraction = family_label_null(landmax_pairs, target)
    np.save(NULL_ERRORS, null_errors)
    inventory = {"greedy": greedy_inventory, "landmax": landmax_inventory}
    evaluation = evaluate(grid_rows, seed_angles, calibration, null_errors, inventory)

    write_csv(PAIR_PROFILES, pair_rows)
    write_csv(SEED_PROFILES, seed_rows)
    write_csv(SEED_ANGLES, seed_angles)
    write_csv(GRID_SUMMARY, grid_rows)
    plot_figure(grid_rows, calibration, evaluation)

    results = {
        "test_id": TEST_ID,
        "status": "SUPPORTED" if evaluation["strict_support"] else "NOT SUPPORTED",
        "question": "At the same local ARA coordinate, is parent/child connected-correlation direction separated by a 72° or 144° pentagonal twist?",
        "protocol_sha256": protocol_hash,
        "calibration_lock_sha256": calibration_hash,
        "calibration": calibration,
        "inventory": inventory,
        "evaluation": evaluation,
        "null_finite_cell_fraction": null_finite_fraction,
        "source": {"doi": "10.5281/zenodo.16753415", "branch": "c2_2local connectivity"},
        "coordinate": {"grid": GRID.tolist(), "angle": "acos(<Cp,Cc>F/(||Cp||F||Cc||F)) in degrees"},
        "outputs": {
            "greedy_crossings": str(CROSSINGS["greedy"]),
            "landmax_crossings": str(CROSSINGS["landmax"]),
            "pair_profiles": str(PAIR_PROFILES),
            "seed_profiles": str(SEED_PROFILES),
            "seed_angles": str(SEED_ANGLES),
            "grid_summary": str(GRID_SUMMARY),
            "null_errors": str(NULL_ERRORS),
            "figure_png": str(FIGURE_PNG),
            "figure_svg": str(FIGURE_SVG),
        },
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": results["status"],
        "selected_target_deg": target,
        "selected_signed_model": calibration["selected_signed_model"],
        "phase_checks": evaluation["phase_checks"],
        "signed_check": evaluation["signed_check"],
        "cross_archive": evaluation["cross_archive_mean_absolute_difference_deg"],
        "same_phase_control": evaluation["same_phase_control"],
        "permutation_null": evaluation["permutation_null"],
        "data_gate": evaluation["data_gate"],
    }, indent=2))


if __name__ == "__main__":
    main()
