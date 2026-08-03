"""Q58 frozen same-gradient vertical Phi-pillar test.

The Q42 determinant-derived ARA coordinate is held fixed while an independent
unnormalised connected-matrix magnitude is compared between the registered
one-turn-15 parent cadence and two-turn-7.5 child cadence families.
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

import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
TEST_ID = "Q58-SAME-GRADIENT-VERTICAL-PHI-PILLAR-v1"
PROTOCOL = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_PROTOCOL_v1_FROZEN.md"
PROTOCOL_HASH = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_PROTOCOL_v1_FROZEN.sha256"
RESULTS = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_RESULTS.json"
CROSSINGS = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_CROSSINGS.csv.gz"
PAIR_PROFILES = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_PAIR_PROFILES.csv.gz"
SEED_RATIOS = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_SEED_RATIOS.csv"
GRID_SUMMARY = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_GRID_SUMMARY.csv"
FIGURE_PNG = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR.png"
FIGURE_SVG = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR.svg"

GRID = np.round(np.arange(0.2, 2.0, 0.2), 10)
PHI = (1 + math.sqrt(5)) / 2
LANDMARKS = {
    "1": 1.0,
    "sqrt2": math.sqrt(2),
    "1.5": 1.5,
    "phi": PHI,
    "sqrt3": math.sqrt(3),
    "2": 2.0,
}
PHI_TOLERANCE = 0.08
EPS = 1e-12
BOOTSTRAP_DRAWS = 10_000
PERMUTATION_DRAWS = 9_999
RANDOM_SEED = 580031

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
MID = "#647180"
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
    kwargs = {"mode": "wt", "newline": "", "encoding": "utf-8"}
    with opener(path, **kwargs) as stream:
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
    direction = 1 if signed_turn >= 0 else -1
    coherence = abs(signed_turn)
    occupancy = min(float(np.mean(labels[:249] == q)) for q in range(4))
    return u, v, labels, direction, coherence, occupancy


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


def nearest_landmark(value: float) -> tuple[str, float]:
    name = min(LANDMARKS, key=lambda key: abs(value - LANDMARKS[key]))
    return name, float(abs(value - LANDMARKS[name]))


def bootstrap_median(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if not len(values):
        return float("nan"), float("nan")
    medians = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    chunk = 500
    for start in range(0, BOOTSTRAP_DRAWS, chunk):
        stop = min(start + chunk, BOOTSTRAP_DRAWS)
        indices = rng.integers(0, len(values), size=(stop - start, len(values)))
        medians[start:stop] = np.median(values[indices], axis=1)
    return tuple(float(x) for x in np.quantile(medians, [0.025, 0.975]))


def interpolate_at_grid(
    coordinate: np.ndarray,
    magnitude: np.ndarray,
    run: dict,
) -> dict[float, float]:
    """Interpolate magnitude at fixed x without extrapolation."""
    start = int(run["start"])
    stop = int(run["end"] + 2)
    x = np.asarray(coordinate[start:stop], dtype=np.float64)
    m = np.asarray(magnitude[start:stop], dtype=np.float64)
    finite = np.isfinite(x) & np.isfinite(m)
    x, m = x[finite], m[finite]
    if len(x) < 2:
        return {}
    if x[0] > x[-1]:
        x, m = x[::-1], m[::-1]
    unique, inverse = np.unique(x, return_inverse=True)
    if len(unique) < 2:
        return {}
    collapsed = np.asarray(
        [np.median(m[inverse == index]) for index in range(len(unique))],
        dtype=np.float64,
    )
    output = {}
    for value in GRID:
        if unique[0] - 1e-12 <= value <= unique[-1] + 1e-12:
            output[float(value)] = float(np.interp(value, unique, collapsed))
    return output


def extract_crossings() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    inventory = {}
    for archive, paths in DATASETS.items():
        if not paths["derived"].exists() or not paths["connected"].exists():
            raise RuntimeError(f"Missing source cache for {archive}")
        derived = np.load(paths["derived"])
        closure = np.asarray(derived["closure"], dtype=np.float32)
        connected = np.load(paths["connected"], mmap_mode="r")
        eligible = 0
        family_counts = defaultdict(int)
        cycle_count = 0
        for seed in range(closure.shape[0]):
            for pair in range(closure.shape[2]):
                line = np.asarray(closure[seed, :, pair], dtype=np.float64)
                coordinate_info = coordinates(line)
                if coordinate_info is None:
                    continue
                u, v, _labels, _direction, coherence, occupancy = coordinate_info
                if coherence < 0.80 or occupancy < 0.05:
                    continue
                eligible += 1
                family = cadence_family(u, v)
                family_counts[family] += 1
                development = line[:250]
                lo, hi = np.quantile(development, [0.05, 0.95])
                if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo <= EPS:
                    continue
                x = 2 * (line - lo) / (hi - lo)
                matrices = np.asarray(connected[seed, :, pair], dtype=np.float64)
                frobenius = np.linalg.norm(matrices, axis=(1, 2))
                spectral = np.linalg.svd(matrices, compute_uv=False)[:, 0]
                runs = transition_runs(line)
                index = 0
                cycle = 0
                while index < len(runs) - 1:
                    forward_run = runs[index]
                    return_run = runs[index + 1]
                    if forward_run["sign"] <= 0 or return_run["sign"] >= 0:
                        index += 1
                        continue
                    forward_raw = run_positions(x, forward_run)
                    return_raw = run_positions(x, return_run)
                    if not (
                        qualifying_half(forward_raw, forward_run)
                        and qualifying_half(return_raw, return_run)
                    ):
                        index += 1
                        continue
                    for phase, run in (("A", forward_run), ("B", return_run)):
                        f_values = interpolate_at_grid(x, frobenius, run)
                        s_values = interpolate_at_grid(x, spectral, run)
                        for grid_x in sorted(set(f_values) & set(s_values)):
                            rows.append(
                                {
                                    "archive": archive,
                                    "seed": seed,
                                    "pair": pair,
                                    "family": family,
                                    "cycle": cycle,
                                    "phase": phase,
                                    "ara_x": grid_x,
                                    "frobenius": f_values[grid_x],
                                    "spectral": s_values[grid_x],
                                    "run_start": int(run["start"]),
                                    "run_end": int(run["end"] + 1),
                                }
                            )
                    cycle += 1
                    cycle_count += 1
                    index += 2
        inventory[archive] = {
            "eligible_lineages": eligible,
            "family_lineages": dict(family_counts),
            "qualifying_cycles": cycle_count,
            "crossing_rows": int(sum(row["archive"] == archive for row in rows)),
        }
    return rows, inventory


def aggregate_profiles(crossings: list[dict]) -> tuple[list[dict], list[dict]]:
    grouped: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    for row in crossings:
        key = (
            row["archive"], row["seed"], row["pair"], row["family"],
            row["phase"], float(row["ara_x"]),
        )
        grouped[key].append((float(row["frobenius"]), float(row["spectral"])))
    pair_rows = []
    for key, values in sorted(grouped.items()):
        data = np.asarray(values, dtype=np.float64)
        pair_rows.append(
            {
                "archive": key[0], "seed": key[1], "pair": key[2],
                "family": key[3], "phase": key[4], "ara_x": key[5],
                "cycles": len(values),
                "frobenius": float(np.median(data[:, 0])),
                "spectral": float(np.median(data[:, 1])),
            }
        )
    seed_grouped: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    for row in pair_rows:
        key = (
            row["archive"], row["seed"], row["family"], row["phase"],
            float(row["ara_x"]),
        )
        seed_grouped[key].append((float(row["frobenius"]), float(row["spectral"])))
    seed_profiles = []
    for key, values in sorted(seed_grouped.items()):
        data = np.asarray(values, dtype=np.float64)
        seed_profiles.append(
            {
                "archive": key[0], "seed": key[1], "family": key[2],
                "phase": key[3], "ara_x": key[4], "pairs": len(values),
                "frobenius": float(np.median(data[:, 0])),
                "spectral": float(np.median(data[:, 1])),
            }
        )
    return pair_rows, seed_profiles


def make_ratios(seed_profiles: list[dict]) -> list[dict]:
    lookup = {
        (row["archive"], row["seed"], row["family"], row["phase"], row["ara_x"]): row
        for row in seed_profiles
    }
    ratios = []
    archives = sorted({row["archive"] for row in seed_profiles})
    seeds = sorted({(row["archive"], row["seed"]) for row in seed_profiles})
    for archive, seed in seeds:
        for phase in ("A", "B"):
            for grid_x in GRID:
                parent = lookup.get((archive, seed, "one_turn_15", phase, float(grid_x)))
                child = lookup.get((archive, seed, "two_turn_7_5", phase, float(grid_x)))
                if parent is None or child is None:
                    continue
                if child["frobenius"] <= EPS or child["spectral"] <= EPS:
                    continue
                other_phase = "B" if phase == "A" else "A"
                wrong_child = lookup.get(
                    (archive, seed, "two_turn_7_5", other_phase, float(grid_x))
                )
                ratios.append(
                    {
                        "archive": archive,
                        "seed": seed,
                        "phase": phase,
                        "ara_x": float(grid_x),
                        "parent_pairs": int(parent["pairs"]),
                        "child_pairs": int(child["pairs"]),
                        "parent_frobenius": float(parent["frobenius"]),
                        "child_frobenius": float(child["frobenius"]),
                        "ratio_frobenius": float(parent["frobenius"] / child["frobenius"]),
                        "reciprocal_frobenius": float(child["frobenius"] / parent["frobenius"]),
                        "parent_spectral": float(parent["spectral"]),
                        "child_spectral": float(child["spectral"]),
                        "ratio_spectral": float(parent["spectral"] / child["spectral"]),
                        "wrong_phase_frobenius": (
                            float(parent["frobenius"] / wrong_child["frobenius"])
                            if wrong_child is not None and wrong_child["frobenius"] > EPS
                            else float("nan")
                        ),
                    }
                )
    if not archives or not ratios:
        raise RuntimeError("No matched parent/child seed ratios")
    return ratios


def summarize_grid(ratios: list[dict], rng: np.random.Generator) -> list[dict]:
    output = []
    for archive in sorted({row["archive"] for row in ratios}):
        for phase in ("A", "B"):
            for grid_x in GRID:
                selected = [
                    row for row in ratios
                    if row["archive"] == archive
                    and row["phase"] == phase
                    and abs(row["ara_x"] - grid_x) < 1e-9
                ]
                values = np.asarray([row["ratio_frobenius"] for row in selected])
                spectral = np.asarray([row["ratio_spectral"] for row in selected])
                wrong = np.asarray([row["wrong_phase_frobenius"] for row in selected])
                finite = values[np.isfinite(values)]
                if not len(finite):
                    median = lo = hi = float("nan")
                    landmark, landmark_error = "none", float("nan")
                else:
                    median = float(np.median(finite))
                    lo, hi = bootstrap_median(finite, rng)
                    landmark, landmark_error = nearest_landmark(median)
                output.append(
                    {
                        "archive": archive,
                        "phase": phase,
                        "ara_x": float(grid_x),
                        "seeds": int(len(finite)),
                        "median_ratio_frobenius": median,
                        "ci95_low": lo,
                        "ci95_high": hi,
                        "abs_phi_error": float(abs(median - PHI)) if np.isfinite(median) else float("nan"),
                        "inside_phi_band": int(abs(median - PHI) <= PHI_TOLERANCE) if np.isfinite(median) else 0,
                        "nearest_landmark": landmark,
                        "nearest_landmark_error": landmark_error,
                        "parent_over_child": int(median > 1) if np.isfinite(median) else 0,
                        "median_ratio_spectral": float(np.nanmedian(spectral)),
                        "median_wrong_phase_frobenius": float(np.nanmedian(wrong)),
                        "minimum_child_frobenius": float(min(row["child_frobenius"] for row in selected)) if selected else float("nan"),
                    }
                )
    return output


def family_label_null(pair_rows: list[dict], observed_ratios: list[dict]) -> dict:
    """Permutation control preserving pair-family counts within seed/archive."""
    rng = np.random.default_rng(RANDOM_SEED + 2)
    columns = [(phase, float(x)) for phase in ("A", "B") for x in GRID]
    by_seed: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in pair_rows:
        by_seed[(row["archive"], int(row["seed"]))].append(row)
    observed = {}
    null = {}
    for archive in sorted({row["archive"] for row in pair_rows}):
        archive_observed = [
            abs(float(row["ratio_frobenius"]) - PHI)
            for row in observed_ratios if row["archive"] == archive
            and np.isfinite(row["ratio_frobenius"])
        ]
        observed_error = float(np.mean(archive_observed))
        error_sum = np.zeros(PERMUTATION_DRAWS, dtype=np.float64)
        error_count = np.zeros(PERMUTATION_DRAWS, dtype=np.int64)
        used_seeds = 0
        for (seed_archive, seed), rows in sorted(by_seed.items()):
            if seed_archive != archive:
                continue
            pair_ids = sorted({int(row["pair"]) for row in rows})
            labels_by_pair = {}
            values_by_key = {}
            for row in rows:
                labels_by_pair[int(row["pair"])] = row["family"]
                values_by_key[(int(row["pair"]), row["phase"], float(row["ara_x"]))] = float(row["frobenius"])
            labels = np.asarray([labels_by_pair[pair] for pair in pair_ids], dtype=object)
            n_parent = int(np.sum(labels == "one_turn_15"))
            n_child = int(np.sum(labels == "two_turn_7_5"))
            if n_parent == 0 or n_child == 0:
                continue
            values = np.full((len(pair_ids), len(columns)), np.nan, dtype=np.float64)
            for p_index, pair in enumerate(pair_ids):
                for c_index, (phase, grid_x) in enumerate(columns):
                    values[p_index, c_index] = values_by_key.get((pair, phase, grid_x), np.nan)
            used_seeds += 1
            chunk = 128
            for start in range(0, PERMUTATION_DRAWS, chunk):
                stop = min(start + chunk, PERMUTATION_DRAWS)
                size = stop - start
                order = np.argsort(rng.random((size, len(pair_ids))), axis=1)
                parent_values = values[order[:, :n_parent], :]
                child_values = values[order[:, n_parent:n_parent + n_child], :]
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    parent_median = np.nanmedian(parent_values, axis=1)
                    child_median = np.nanmedian(child_values, axis=1)
                ratio = parent_median / child_median
                finite = np.isfinite(ratio) & (child_median > EPS)
                errors = np.where(finite, np.abs(ratio - PHI), 0.0)
                error_sum[start:stop] += np.sum(errors, axis=1)
                error_count[start:stop] += np.sum(finite, axis=1)
        null_errors = error_sum / np.maximum(error_count, 1)
        p_value = float((1 + np.sum(null_errors <= observed_error)) / (PERMUTATION_DRAWS + 1))
        observed[archive] = observed_error
        null[archive] = {
            "permutations": PERMUTATION_DRAWS,
            "used_seeds": used_seeds,
            "observed_mean_abs_phi_error": observed_error,
            "null_median_mean_abs_phi_error": float(np.median(null_errors)),
            "null_ci95": [float(x) for x in np.quantile(null_errors, [0.025, 0.975])],
            "p_observed_no_worse_than_null": p_value,
        }
    return null


def evaluate(grid_rows: list[dict], ratios: list[dict]) -> dict:
    archives = sorted({row["archive"] for row in grid_rows})
    phase_checks = {}
    data_gate_cells = []
    minimum_denominator = float("inf")
    for archive in archives:
        phase_checks[archive] = {}
        for phase in ("A", "B"):
            cells = sorted(
                [row for row in grid_rows if row["archive"] == archive and row["phase"] == phase],
                key=lambda row: row["ara_x"],
            )
            medians = np.asarray([row["median_ratio_frobenius"] for row in cells])
            whole_values = np.asarray([
                row["ratio_frobenius"] for row in ratios
                if row["archive"] == archive and row["phase"] == phase
            ])
            whole_median = float(np.nanmedian(whole_values))
            nearest, nearest_error = nearest_landmark(whole_median)
            phase_checks[archive][phase] = {
                "grid_cells": len(cells),
                "inside_phi_band_cells": int(sum(row["inside_phi_band"] for row in cells)),
                "mean_abs_phi_error_of_cell_medians": float(np.nanmean(np.abs(medians - PHI))),
                "parent_over_child_cells": int(sum(row["parent_over_child"] for row in cells)),
                "whole_grid_median_ratio": whole_median,
                "whole_grid_nearest_landmark": nearest,
                "whole_grid_nearest_landmark_error": nearest_error,
                "minimum_seed_count": int(min(row["seeds"] for row in cells)),
            }
            data_gate_cells.extend(row["seeds"] >= 50 for row in cells)
            minimum_denominator = min(
                minimum_denominator,
                min(row["minimum_child_frobenius"] for row in cells),
            )
    cross_archive_mae = {}
    for phase in ("A", "B"):
        left = {
            row["ara_x"]: row["median_ratio_frobenius"]
            for row in grid_rows if row["archive"] == archives[0] and row["phase"] == phase
        }
        right = {
            row["ara_x"]: row["median_ratio_frobenius"]
            for row in grid_rows if row["archive"] == archives[1] and row["phase"] == phase
        }
        cross_archive_mae[phase] = float(np.mean([abs(left[x] - right[x]) for x in GRID]))
    data_gate = bool(
        all(data_gate_cells)
        and np.isfinite(minimum_denominator)
        and minimum_denominator > EPS
    )
    strict_components = []
    for archive in archives:
        for phase in ("A", "B"):
            item = phase_checks[archive][phase]
            strict_components.extend([
                item["inside_phi_band_cells"] >= 7,
                item["mean_abs_phi_error_of_cell_medians"] <= PHI_TOLERANCE,
                item["whole_grid_nearest_landmark"] == "phi",
                item["parent_over_child_cells"] >= 8,
            ])
    strict_components.extend(cross_archive_mae[phase] <= PHI_TOLERANCE for phase in ("A", "B"))
    strict_support = bool(data_gate and all(strict_components))
    return {
        "data_gate_passed": data_gate,
        "minimum_child_frobenius": minimum_denominator,
        "phase_checks": phase_checks,
        "cross_archive_grid_mae": cross_archive_mae,
        "strict_support": strict_support,
        "verdict": (
            "STRICTLY SUPPORTED" if strict_support
            else "NOT SUPPORTED" if data_gate
            else "NOT TESTABLE ON Q42"
        ),
    }


def make_figure(grid_rows: list[dict], evaluation: dict) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    figure, axes = plt.subplots(2, 2, figsize=(13.2, 9.0), facecolor=BG)
    colors = {"greedy": BLUE, "landmax": GOLD}
    for phase, axis in zip(("A", "B"), axes[0]):
        for archive in ("greedy", "landmax"):
            rows = sorted(
                [row for row in grid_rows if row["phase"] == phase and row["archive"] == archive],
                key=lambda row: row["ara_x"],
            )
            x = np.asarray([row["ara_x"] for row in rows])
            y = np.asarray([row["median_ratio_frobenius"] for row in rows])
            lo = np.asarray([row["ci95_low"] for row in rows])
            hi = np.asarray([row["ci95_high"] for row in rows])
            axis.plot(x, y, marker="o", color=colors[archive], linewidth=2.2, label=archive)
            axis.fill_between(x, lo, hi, color=colors[archive], alpha=0.14)
        axis.axhspan(PHI - PHI_TOLERANCE, PHI + PHI_TOLERANCE, color=MID, alpha=0.08)
        axis.axhline(PHI, color=INK, linestyle="--", linewidth=1.4, label="phi")
        for name, value in LANDMARKS.items():
            if name == "phi":
                continue
            axis.axhline(value, color=LIGHT, linewidth=0.8, zorder=0)
            axis.text(
                0.992, value, name, transform=axis.get_yaxis_transform(),
                ha="right", va="bottom", fontsize=7.5, color=MID,
            )
        axis.set_title(f"Phase {phase}: parent / child Frobenius magnitude", loc="left", fontweight="bold")
        axis.set_xlabel("matched local ARA coordinate")
        axis.set_ylabel("one-turn-15 / two-turn-7.5")
        axis.set_xticks(GRID)
        axis.set_ylim(0.95, 2.5)
        axis.grid(axis="both", color=GRID_COLOR, linewidth=0.7, alpha=0.7)
        axis.legend(frameon=False, ncol=3, loc="upper right")
    for phase, axis in zip(("A", "B"), axes[1]):
        for archive in ("greedy", "landmax"):
            rows = sorted(
                [row for row in grid_rows if row["phase"] == phase and row["archive"] == archive],
                key=lambda row: row["ara_x"],
            )
            x = np.asarray([row["ara_x"] for row in rows])
            primary = np.asarray([row["median_ratio_frobenius"] for row in rows])
            wrong = np.asarray([row["median_wrong_phase_frobenius"] for row in rows])
            axis.plot(x, np.abs(primary - PHI), marker="o", color=colors[archive], linewidth=2, label=f"{archive} same-phase")
            axis.plot(x, np.abs(wrong - PHI), marker="s", markerfacecolor="none", color=colors[archive], linestyle=":", linewidth=1.5, label=f"{archive} wrong-phase")
        axis.axhline(PHI_TOLERANCE, color=INK, linestyle="--", linewidth=1.2, label="0.08 band")
        axis.set_title(f"Phase {phase}: absolute distance from Phi", loc="left", fontweight="bold")
        axis.set_xlabel("matched local ARA coordinate")
        axis.set_ylabel("absolute Phi error")
        axis.set_xticks(GRID)
        axis.set_ylim(bottom=0)
        axis.grid(axis="both", color=GRID_COLOR, linewidth=0.7, alpha=0.7)
        axis.legend(frameon=False, fontsize=8, ncol=2, loc="upper right")
    figure.suptitle(
        f"Q58 — same-gradient vertical Phi-pillar ({evaluation['verdict']})",
        x=0.06, ha="left", fontsize=17, fontweight="bold", color=INK,
    )
    figure.text(
        0.06, 0.935,
        "Fixed x=0.2…1.8 · unnormalised connected-matrix magnitude · 95% seed-bootstrap intervals",
        color=MID, fontsize=10,
    )
    figure.text(
        0.06, 0.02,
        "Source: Zenodo 10.5281/zenodo.16753415; Q42 public greedy and landmax archives. Family comparison is population-level, not event genealogy.",
        color=MID, fontsize=8.5,
    )
    figure.tight_layout(rect=(0.04, 0.055, 0.99, 0.91))
    figure.savefig(FIGURE_PNG, dpi=180, facecolor=figure.get_facecolor())
    figure.savefig(FIGURE_SVG, facecolor=figure.get_facecolor())
    plt.close(figure)


def main() -> None:
    if not PROTOCOL.exists():
        raise RuntimeError(f"Missing frozen protocol: {PROTOCOL}")
    protocol_sha = digest(PROTOCOL)
    PROTOCOL_HASH.write_text(f"{protocol_sha}  {PROTOCOL.name}\n", encoding="utf-8")
    crossings, inventory = extract_crossings()
    pair_rows, seed_profiles = aggregate_profiles(crossings)
    ratios = make_ratios(seed_profiles)
    rng = np.random.default_rng(RANDOM_SEED)
    grid_rows = summarize_grid(ratios, rng)
    evaluation = evaluate(grid_rows, ratios)
    permutation = family_label_null(pair_rows, ratios)

    write_csv(CROSSINGS, crossings)
    write_csv(PAIR_PROFILES, pair_rows)
    write_csv(SEED_RATIOS, ratios)
    write_csv(GRID_SUMMARY, grid_rows)
    make_figure(grid_rows, evaluation)

    output = {
        "test_id": TEST_ID,
        "date": "2026-07-31",
        "protocol_sha256": protocol_sha,
        "status": evaluation["verdict"],
        "question": "At identical local ARA x, is parent/child unnormalised connected magnitude Phi-like for A-to-A and B-to-B?",
        "definitions": {
            "ara_x": "2*(cuberoot(abs(det(C)))-h05)/(h95-h05), development 0..249",
            "vertical_primary": "Frobenius norm of the unnormalised connected-correlation matrix C",
            "vertical_robustness": "spectral norm of C",
            "ratio_direction": "one_turn_15 / two_turn_7_5",
            "fixed_grid": GRID.tolist(),
            "phi": PHI,
            "phi_tolerance": PHI_TOLERANCE,
        },
        "inventory": inventory,
        "counts": {
            "crossing_rows": len(crossings),
            "pair_profiles": len(pair_rows),
            "seed_ratios": len(ratios),
        },
        "evaluation": evaluation,
        "family_label_permutation": permutation,
        "grid_summary": grid_rows,
        "artifacts": {
            "crossings": str(CROSSINGS),
            "pair_profiles": str(PAIR_PROFILES),
            "seed_ratios": str(SEED_RATIOS),
            "grid_summary": str(GRID_SUMMARY),
            "figure_png": str(FIGURE_PNG),
            "figure_svg": str(FIGURE_SVG),
        },
        "claim_boundary": (
            "Population-level comparison of Q42 cadence families at matched local ARA coordinates; "
            "not individual genealogy, universal Phi scaling, literal energy, or a new quantum law."
        ),
    }
    RESULTS.write_text(json.dumps(output, indent=2, allow_nan=True), encoding="utf-8")
    print(json.dumps({
        "status": evaluation["verdict"],
        "protocol_sha256": protocol_sha,
        "counts": output["counts"],
        "data_gate": evaluation["data_gate_passed"],
        "phase_checks": evaluation["phase_checks"],
        "cross_archive_grid_mae": evaluation["cross_archive_grid_mae"],
        "permutation": permutation,
    }, indent=2))


if __name__ == "__main__":
    main()
