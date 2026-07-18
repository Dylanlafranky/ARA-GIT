"""PN3A opened-data diagnostic of the adult sieve path.

This script does not retune PN3 and does not access the prime-31 PN1H wheel.
It reconstructs the first post-p29 divisor for every candidate in the already
opened PN3 decimal-rung windows, then measures the full survival/release path
and the transfer of the diagonal child coordinate into that adult path.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN3A_ADULT_SIEVE_PATH_DIAGNOSTIC_PROTOCOL.md"
PN3_PACKET = HERE / "PN3_STANDALONE_ARA_TARGET_PACKET.npz"
PN3_DEV_SUMMARY = HERE / "PN3_STANDALONE_ARA_DEVELOPMENT_SUMMARY.json"

RESULTS_PATH = HERE / "PN3A_ADULT_SIEVE_PATH_RESULTS.json"
CURVES_PATH = HERE / "PN3A_ADULT_SIEVE_CURVES.csv"
TRANSFER_PATH = HERE / "PN3A_ADULT_STAGE_TRANSFER.csv"
SURFACES_PATH = HERE / "PN3A_ADULT_CHILD_SURFACES.csv"
DATA_PATH = HERE / "PN3A_ADULT_SIEVE_DIAGNOSTIC_DATA.npz"
SURVIVAL_FIGURE = HERE / "PN3A_ADULT_SIEVE_SURVIVAL_RELEASE.png"
COUPLING_FIGURE = HERE / "PN3A_ADULT_CHILD_COUPLING.png"

WINDOWS = {
    "r6": (1_000_000, 1_010_000),
    "r7": (10_000_000, 10_100_000),
    "r8": (100_000_000, 101_000_000),
    "r9": (1_000_000_000, 1_010_000_000),
}
SMALL_PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=np.int64)
CONTEXT_MARGIN = 2_000
CHILD_BINS = 12
ADULT_STAGES = 12
SHRINKAGE = 64.0
PERMUTATIONS = 100
PERMUTATION_SEED = 20260718
LOCATION_BLOCKS = 40

INK = (37, 42, 46)
MUTED = (100, 108, 115)
GRID = (220, 224, 227)
PAPER = (250, 250, 248)
BLUE = (48, 104, 162)
BLUE_OPEN = (153, 188, 220)
ORANGE = (211, 124, 52)
ORANGE_OPEN = (239, 191, 145)
NEUTRAL = (86, 91, 95)
RUNG_COLORS = {
    "r6": (174, 201, 225),
    "r7": (113, 161, 202),
    "r8": (61, 119, 174),
    "r9": (30, 75, 120),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(json_ready(payload), indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path.name}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def simple_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            sieve[prime * prime :: prime] = False
    return np.flatnonzero(sieve).astype(np.int64)


def p29_candidate_mask(low: int, high: int) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    for prime in SMALL_PRIMES:
        start = (-low) % int(prime)
        mask[start:: int(prime)] = False
    return mask


def candidate_geometry(low: int, high: int) -> dict[str, np.ndarray]:
    extended_low = low - CONTEXT_MARGIN
    extended_high = high + CONTEXT_MARGIN
    candidates = np.flatnonzero(p29_candidate_mask(extended_low, extended_high)).astype(np.int64) + extended_low
    gaps = np.diff(candidates).astype(np.uint8)
    indices = np.arange(2, len(candidates) - 2, dtype=np.int64)
    numbers = candidates[indices]
    indices = indices[(numbers >= low) & (numbers < high)]
    numbers = candidates[indices]
    gm1 = gaps[indices - 1]
    g0 = gaps[indices]
    gp1 = gaps[indices + 1]
    x_current = 2.0 * g0.astype(float) / (gm1.astype(float) + g0.astype(float))
    x_next = 2.0 * gp1.astype(float) / (g0.astype(float) + gp1.astype(float))
    diagonal = (x_current + x_next) / 2.0
    perpendicular = (x_next - x_current) / 2.0
    u_bin = np.minimum((np.clip(diagonal, 0.0, 2.0 - np.finfo(float).eps) * CHILD_BINS / 2.0).astype(np.uint8), CHILD_BINS - 1)
    v_bin = np.minimum((np.clip(perpendicular, -1.0, 1.0 - np.finfo(float).eps) + 1.0).astype(float) * CHILD_BINS / 2.0, CHILD_BINS - 1).astype(np.uint8)
    return {
        "numbers": numbers,
        "right_numbers": candidates[indices + 1],
        "gm1": gm1,
        "g0": g0,
        "gp1": gp1,
        "u_bin": u_bin,
        "v_bin": v_bin,
    }


def segmented_smallest_factor(low: int, high: int) -> tuple[np.ndarray, np.ndarray]:
    limit = math.isqrt(high - 1)
    primes = simple_primes(limit)
    active_primes = primes[primes > 29]
    smallest = np.zeros(high - low, dtype=np.uint16)
    for prime_value in active_primes:
        prime = int(prime_value)
        start = max(prime * prime, ((low + prime - 1) // prime) * prime)
        if start >= high:
            continue
        view = smallest[start - low :: prime]
        empty = view == 0
        view[empty] = prime
    return smallest, active_primes


def first_edge_death(candidate_death: np.ndarray) -> np.ndarray:
    left = candidate_death[:-1]
    right = candidate_death[1:]
    both_zero = (left == 0) & (right == 0)
    left_effective = np.where(left == 0, np.iinfo(np.uint16).max, left)
    right_effective = np.where(right == 0, np.iinfo(np.uint16).max, right)
    death = np.minimum(left_effective, right_effective).astype(np.uint16)
    death[both_zero] = 0
    return death


def adult_stage(death: np.ndarray, high: int) -> np.ndarray:
    stage = np.full(len(death), ADULT_STAGES, dtype=np.uint8)
    composite = death > 0
    denominator = math.log(math.sqrt(high - 1) / 31.0)
    progress = np.log(death[composite].astype(float) / 31.0) / denominator
    stage[composite] = np.minimum((np.clip(progress, 0.0, 1.0 - np.finfo(float).eps) * ADULT_STAGES).astype(np.uint8), ADULT_STAGES - 1)
    return stage


def reconstruct_rung(name: str, low: int, high: int, packet: Any, dev_summary: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    geometry = candidate_geometry(low, high)
    # R7/R8 PN3 edge rates were taken as subwindows of larger opened child
    # intervals, so they include the edge beginning at the last in-window
    # candidate. R6 and the sealed R9 packet stop one edge earlier.
    include_terminal_edge = name in ("r7", "r8")
    factor_high = high + CONTEXT_MARGIN if include_terminal_edge else high
    smallest, primes = segmented_smallest_factor(low, factor_high)
    death = smallest[geometry["numbers"] - low].astype(np.uint16)
    if include_terminal_edge:
        terminal_right_death = smallest[int(geometry["right_numbers"][-1]) - low]
        edge_death = first_edge_death(np.concatenate([death, np.array([terminal_right_death], dtype=np.uint16)]))
    else:
        edge_death = first_edge_death(death)
    del smallest
    labels = (death == 0).astype(np.uint8)
    edge_labels = (edge_death == 0).astype(np.uint8)

    checks: dict[str, Any] = {}
    if name == "r9":
        checks["numbers_match_packet"] = bool(np.array_equal(geometry["numbers"], packet["candidate_numbers"]))
        checks["labels_match_packet"] = bool(np.array_equal(labels, packet["candidate_labels"]))
        checks["gm1_match_packet"] = bool(np.array_equal(geometry["gm1"], packet["candidate_gm1"]))
        checks["g0_match_packet"] = bool(np.array_equal(geometry["g0"], packet["candidate_g0"]))
        checks["gp1_match_packet"] = bool(np.array_equal(geometry["gp1"], packet["candidate_gp1"]))
        checks["edge_labels_match_packet"] = bool(np.array_equal(edge_labels, packet["edge_labels"]))
    else:
        recorded = dev_summary["rung_rates"][name]
        checks["candidate_count_match_summary"] = len(labels) == int(recorded["candidate_events"])
        checks["candidate_positive_match_summary"] = int(labels.sum()) == int(recorded["candidate_positives"])
        checks["edge_count_match_summary"] = len(edge_labels) == int(recorded["edge_events"])
        checks["edge_positive_match_summary"] = int(edge_labels.sum()) == int(recorded["edge_positives"])
    if not all(checks.values()):
        failed = [key for key, value in checks.items() if not value]
        raise AssertionError(f"{name} reconstruction failed: {failed}")

    rung = {
        "name": name,
        "low": low,
        "high": high,
        "primes": primes,
        "candidate_death": death,
        "edge_death": edge_death,
        "u_bin": geometry["u_bin"],
        "v_bin": geometry["v_bin"],
    }
    summary = {
        "candidate_events": len(labels),
        "candidate_primes": int(labels.sum()),
        "candidate_terminal_survival": float(labels.mean()),
        "edge_events": len(edge_labels),
        "prime_pairs": int(edge_labels.sum()),
        "edge_terminal_survival": float(edge_labels.mean()),
        "maximum_sieve_prime": int(primes[-1]),
        "checks": checks,
    }
    return rung, summary


def survival_curve(rung: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidate_death = rung["candidate_death"]
    edge_death = rung["edge_death"]
    maximum = int(rung["primes"][-1])
    candidate_death_counts = np.bincount(candidate_death.astype(np.int64), minlength=maximum + 1)
    edge_death_counts = np.bincount(edge_death.astype(np.int64), minlength=maximum + 1)
    candidate_alive = len(candidate_death)
    edge_alive = len(edge_death)
    product = 1.0
    rows = [{
        "rung": rung["name"],
        "q": 29,
        "log_q": math.log(29.0),
        "candidate_survival": 1.0,
        "edge_survival": 1.0,
        "candidate_cumulative_release": 0.0,
        "edge_cumulative_release": 0.0,
        "candidate_deaths_at_q": 0,
        "edge_deaths_at_q": 0,
        "candidate_hazard": 0.0,
        "edge_hazard": 0.0,
        "independence_product": 1.0,
        "independence_product_squared": 1.0,
    }]
    for prime_value in rung["primes"]:
        prime = int(prime_value)
        candidate_deaths = int(candidate_death_counts[prime])
        edge_deaths = int(edge_death_counts[prime])
        candidate_before = candidate_alive
        edge_before = edge_alive
        candidate_alive -= candidate_deaths
        edge_alive -= edge_deaths
        product *= 1.0 - 1.0 / prime
        rows.append({
            "rung": rung["name"],
            "q": prime,
            "log_q": math.log(float(prime)),
            "candidate_survival": candidate_alive / len(candidate_death),
            "edge_survival": edge_alive / len(edge_death),
            "candidate_cumulative_release": 1.0 - candidate_alive / len(candidate_death),
            "edge_cumulative_release": 1.0 - edge_alive / len(edge_death),
            "candidate_deaths_at_q": candidate_deaths,
            "edge_deaths_at_q": edge_deaths,
            "candidate_hazard": candidate_deaths / candidate_before if candidate_before else 0.0,
            "edge_hazard": edge_deaths / edge_before if edge_before else 0.0,
            "independence_product": product,
            "independence_product_squared": product * product,
        })
    terminal = rows[-1]
    divergence_onset: dict[str, Any] = {}
    for label, exact_key, reference_key in (
        ("candidate", "candidate_survival", "independence_product"),
        ("edge", "edge_survival", "independence_product_squared"),
    ):
        divergence_onset[label] = {}
        for threshold in (0.01, 0.05, 0.10, 0.20):
            hit = next(
                (
                    row
                    for row in rows
                    if abs(row[reference_key] - row[exact_key]) / row[exact_key] >= threshold
                ),
                None,
            )
            divergence_onset[label][f"relative_{int(threshold * 100)}pct"] = None if hit is None else {
                "q": int(hit["q"]),
                "normalized_log_progress": math.log(float(hit["q"]) / 31.0)
                / math.log(float(terminal["q"]) / 31.0),
            }
    summary = {
        "candidate_product_terminal": terminal["independence_product"],
        "edge_product_squared_terminal": terminal["independence_product_squared"],
        "candidate_product_relative_error": (terminal["independence_product"] - terminal["candidate_survival"]) / terminal["candidate_survival"],
        "edge_product_relative_error": (terminal["independence_product_squared"] - terminal["edge_survival"]) / terminal["edge_survival"],
        "candidate_cumulative_hazard": -math.log(terminal["candidate_survival"]),
        "edge_cumulative_hazard": -math.log(terminal["edge_survival"]),
        "candidate_product_hazard": -math.log(terminal["independence_product"]),
        "edge_product_hazard": -math.log(terminal["independence_product_squared"]),
        "divergence_onset": divergence_onset,
    }
    return rows, summary


def fit_stage_lookup(state: np.ndarray, stage: np.ndarray, state_count: int) -> tuple[np.ndarray, np.ndarray]:
    global_counts = np.bincount(stage.astype(np.int64), minlength=ADULT_STAGES + 1).astype(float) + 0.5
    global_probability = global_counts / global_counts.sum()
    counts = np.zeros((state_count, ADULT_STAGES + 1), dtype=float)
    np.add.at(counts, (state.astype(np.int64), stage.astype(np.int64)), 1.0)
    totals = counts.sum(axis=1)
    probabilities = (counts + SHRINKAGE * global_probability[None, :]) / (totals[:, None] + SHRINKAGE)
    return global_probability, probabilities


def multiclass_log_loss(probabilities: np.ndarray, stage: np.ndarray) -> float:
    selected = probabilities[np.arange(len(stage)), stage.astype(np.int64)] if probabilities.ndim == 2 else probabilities[stage.astype(np.int64)]
    return float(-np.mean(np.log2(np.clip(selected, 1e-15, 1.0))))


def state_view(rung: dict[str, Any], entity: str, model: str) -> np.ndarray:
    count = len(rung["candidate_death"]) if entity == "candidate" else len(rung["edge_death"])
    u_state = rung["u_bin"][:count].astype(np.int64)
    v_state = rung["v_bin"][:count].astype(np.int64)
    if model == "u":
        return u_state
    if model == "v":
        return v_state
    if model == "uv":
        return u_state * CHILD_BINS + v_state
    raise KeyError(model)


def stage_view(rung: dict[str, Any], entity: str) -> np.ndarray:
    death = rung["candidate_death"] if entity == "candidate" else rung["edge_death"]
    return adult_stage(death, rung["high"])


def permutation_null(
    state: np.ndarray,
    stage: np.ndarray,
    baseline_loss: float,
    conditional_probability: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    boundaries = np.linspace(0, len(state), LOCATION_BLOCKS + 1, dtype=np.int64)
    output = np.empty(PERMUTATIONS, dtype=float)
    for permutation in range(PERMUTATIONS):
        shuffled = state.copy()
        for block in range(LOCATION_BLOCKS):
            rng.shuffle(shuffled[boundaries[block] : boundaries[block + 1]])
        probabilities = conditional_probability[shuffled, :]
        output[permutation] = baseline_loss - multiclass_log_loss(probabilities, stage)
    return output


def transfer_diagnostics(rungs: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    primary_permutations: dict[str, Any] = {}
    rng = np.random.default_rng(PERMUTATION_SEED)
    transfers = [("r6", "r7", False), ("r7", "r8", True), ("r8", "r9", True)]
    for train_name, test_name, primary in transfers:
        train = rungs[train_name]
        test = rungs[test_name]
        for entity in ("candidate", "edge"):
            train_stage = stage_view(train, entity)
            test_stage = stage_view(test, entity)
            global_probability, _ = fit_stage_lookup(np.zeros(len(train_stage), dtype=np.uint8), train_stage, 1)
            baseline_loss = multiclass_log_loss(global_probability, test_stage)
            for model in ("u", "v", "uv"):
                train_state = state_view(train, entity, model)
                test_state = state_view(test, entity, model)
                state_count = CHILD_BINS if model in ("u", "v") else CHILD_BINS * CHILD_BINS
                _, conditional_probability = fit_stage_lookup(train_state, train_stage, state_count)
                model_loss = multiclass_log_loss(conditional_probability[test_state, :], test_stage)
                gain = baseline_loss - model_loss
                row: dict[str, Any] = {
                    "train_rung": train_name,
                    "test_rung": test_name,
                    "primary_transfer": primary,
                    "entity": entity,
                    "model": model,
                    "test_events": len(test_stage),
                    "baseline_loss_bits": baseline_loss,
                    "model_loss_bits": model_loss,
                    "gain_bits_per_event": gain,
                    "permutation_mean_gain": "",
                    "permutation_lower_95": "",
                    "permutation_upper_95": "",
                    "permutation_p_ge_observed": "",
                }
                if primary and model in ("u", "v"):
                    null = permutation_null(test_state, test_stage, baseline_loss, conditional_probability, rng)
                    p_value = (1.0 + float(np.sum(null >= gain))) / (PERMUTATIONS + 1.0)
                    row.update({
                        "permutation_mean_gain": float(null.mean()),
                        "permutation_lower_95": float(np.quantile(null, 0.025)),
                        "permutation_upper_95": float(np.quantile(null, 0.975)),
                        "permutation_p_ge_observed": p_value,
                    })
                    key = f"{train_name}_to_{test_name}__{entity}__{model}"
                    primary_permutations[key] = {
                        "observed_gain": gain,
                        "null_mean": float(null.mean()),
                        "null_lower_95": float(np.quantile(null, 0.025)),
                        "null_upper_95": float(np.quantile(null, 0.975)),
                        "p_ge_observed": p_value,
                    }
                rows.append(row)
    return rows, primary_permutations


def selected_thresholds(primes: np.ndarray, count: int = 24) -> np.ndarray:
    desired = np.geomspace(31.0, float(primes[-1]), count)
    indices = np.searchsorted(primes, desired, side="right") - 1
    indices = np.clip(indices, 0, len(primes) - 1)
    return np.unique(primes[indices]).astype(np.int64)


def adult_child_surfaces(rung: dict[str, Any]) -> list[dict[str, Any]]:
    edge_death = rung["edge_death"]
    thresholds = selected_thresholds(rung["primes"])
    rows: list[dict[str, Any]] = []
    count = len(edge_death)
    for axis in ("u", "v"):
        state = state_view(rung, "edge", axis)
        starting = np.bincount(state, minlength=CHILD_BINS).astype(float)
        for threshold_index, threshold_value in enumerate(thresholds):
            threshold = int(threshold_value)
            alive = (edge_death == 0) | (edge_death > threshold)
            alive_by_state = np.bincount(state[alive], minlength=CHILD_BINS).astype(float)
            survival = np.divide(alive_by_state, starting, out=np.full(CHILD_BINS, np.nan), where=starting > 0)
            global_survival = float(alive.mean())
            redistribution = np.log2(np.clip(survival, 1e-15, 1.0) / global_survival)
            progress = math.log(threshold / 31.0) / math.log(float(rung["primes"][-1]) / 31.0)
            for state_index in range(CHILD_BINS):
                if axis == "u":
                    coordinate_low = 2.0 * state_index / CHILD_BINS
                    coordinate_high = 2.0 * (state_index + 1) / CHILD_BINS
                else:
                    coordinate_low = -1.0 + 2.0 * state_index / CHILD_BINS
                    coordinate_high = -1.0 + 2.0 * (state_index + 1) / CHILD_BINS
                rows.append({
                    "rung": rung["name"],
                    "entity": "edge",
                    "axis": axis,
                    "axis_bin": state_index,
                    "coordinate_low": coordinate_low,
                    "coordinate_high": coordinate_high,
                    "starting_events": int(starting[state_index]),
                    "threshold_index": threshold_index,
                    "threshold_q": threshold,
                    "adult_progress": progress,
                    "conditional_survival": float(survival[state_index]),
                    "global_survival": global_survival,
                    "redistribution_log2": float(redistribution[state_index]),
                })
    return rows


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def draw_dashed_line(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: tuple[int, int, int], width: int = 3) -> None:
    for first, second in zip(points[:-1], points[1:]):
        x0, y0 = first
        x1, y1 = second
        distance = math.hypot(x1 - x0, y1 - y0)
        if distance == 0:
            continue
        segments = max(1, int(distance / 10))
        for segment in range(segments):
            if segment % 2:
                continue
            start = segment / segments
            end = min(1.0, (segment + 1) / segments)
            draw.line((x0 + (x1 - x0) * start, y0 + (y1 - y0) * start, x0 + (x1 - x0) * end, y0 + (y1 - y0) * end), fill=fill, width=width)


def draw_line_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    series: list[dict[str, Any]],
    y_label: str,
    y_range: tuple[float, float] = (0.0, 1.0),
) -> None:
    left, top, right, bottom = box
    title_font = font(20, True)
    small_font = font(14)
    draw.text((left, top), title, fill=INK, font=title_font)
    draw.text((left, top + 27), subtitle, fill=MUTED, font=small_font)
    plot = (left + 70, top + 65, right - 15, bottom - 55)
    px0, py0, px1, py1 = plot
    for tick in range(6):
        value = y_range[0] + (y_range[1] - y_range[0]) * tick / 5
        y = py1 - (py1 - py0) * tick / 5
        draw.line((px0, y, px1, y), fill=GRID, width=1)
        draw.text((px0 - 58, y - 8), f"{value:.1f}", fill=MUTED, font=small_font)
    draw.line((px0, py0, px0, py1), fill=INK, width=2)
    draw.line((px0, py1, px1, py1), fill=INK, width=2)
    all_x = [point[0] for item in series for point in item["points"]]
    minimum_x = math.log(min(all_x))
    maximum_x = math.log(max(all_x))
    for exponent in range(math.ceil(math.log10(min(all_x))), math.floor(math.log10(max(all_x))) + 1):
        value = 10**exponent
        x = px0 + (math.log(value) - minimum_x) / (maximum_x - minimum_x) * (px1 - px0)
        draw.line((x, py1, x, py1 + 6), fill=INK, width=1)
        draw.text((x - 18, py1 + 10), f"1e{exponent}", fill=MUTED, font=small_font)
    for item in series:
        points = []
        for x_value, y_value in item["points"]:
            x = px0 + (math.log(x_value) - minimum_x) / (maximum_x - minimum_x) * (px1 - px0)
            y = py1 - (y_value - y_range[0]) / (y_range[1] - y_range[0]) * (py1 - py0)
            points.append((x, y))
        if item.get("dashed"):
            draw_dashed_line(draw, points, item["color"], item.get("width", 3))
        else:
            draw.line(points, fill=item["color"], width=item.get("width", 3), joint="curve")
    legend_x = px0 + 6
    legend_y = py0 + 4
    for item in series:
        draw.line((legend_x, legend_y + 7, legend_x + 24, legend_y + 7), fill=item["color"], width=3)
        draw.text((legend_x + 31, legend_y), item["label"], fill=INK, font=small_font)
        legend_x += 105 if len(item["label"]) < 8 else 155
        if legend_x > px1 - 140:
            legend_x = px0 + 6
            legend_y += 20
    draw.text((left + 5, (py0 + py1) / 2 - 8), y_label, fill=MUTED, font=small_font)
    draw.text(((px0 + px1) / 2 - 45, bottom - 25), "Sieve threshold q (log scale)", fill=MUTED, font=small_font)


def draw_stage_bars(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, candidate: np.ndarray, edge: np.ndarray) -> None:
    left, top, right, bottom = box
    draw.text((left, top), title, fill=INK, font=font(20, True))
    draw.text((left, top + 27), "R9 share released in each normalized log-sieve stage; final class survives", fill=MUTED, font=font(14))
    px0, py0, px1, py1 = left + 60, top + 70, right - 15, bottom - 55
    maximum = max(candidate.max(), edge.max()) * 1.12
    for tick in range(5):
        value = maximum * tick / 4
        y = py1 - (py1 - py0) * tick / 4
        draw.line((px0, y, px1, y), fill=GRID, width=1)
        draw.text((px0 - 52, y - 7), f"{value:.2f}", fill=MUTED, font=font(13))
    group_width = (px1 - px0) / len(candidate)
    bar_width = group_width * 0.32
    for index in range(len(candidate)):
        center = px0 + (index + 0.5) * group_width
        for offset, value, color in ((-bar_width, candidate[index], BLUE), (0, edge[index], ORANGE)):
            x0 = center + offset
            y0 = py1 - value / maximum * (py1 - py0)
            draw.rectangle((x0, y0, x0 + bar_width, py1), fill=color, outline=INK, width=1)
        label = "S" if index == ADULT_STAGES else str(index)
        draw.text((center - 5, py1 + 8), label, fill=MUTED, font=font(12))
    draw.line((px0, py1, px1, py1), fill=INK, width=2)
    draw.text((px0, py0 - 20), "Candidate", fill=INK, font=font(13))
    draw.rectangle((px0 + 72, py0 - 17, px0 + 86, py0 - 3), fill=BLUE)
    draw.text((px0 + 105, py0 - 20), "Pair", fill=INK, font=font(13))
    draw.rectangle((px0 + 137, py0 - 17, px0 + 151, py0 - 3), fill=ORANGE)
    draw.text(((px0 + px1) / 2 - 48, bottom - 24), "Adult death stage", fill=MUTED, font=font(14))


def signed_color(value: float, maximum: float) -> tuple[int, int, int]:
    if not math.isfinite(value) or maximum <= 0:
        return (235, 235, 232)
    strength = min(1.0, abs(value) / maximum)
    endpoint = BLUE if value < 0 else ORANGE
    return tuple(int(PAPER[channel] + (endpoint[channel] - PAPER[channel]) * (0.12 + 0.88 * strength)) for channel in range(3))


def draw_heatmap(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    rows: list[dict[str, Any]],
    axis: str,
    shared_maximum: float,
) -> None:
    left, top, right, bottom = box
    draw.text((left, top), title, fill=INK, font=font(20, True))
    draw.text((left, top + 27), "R9 pair survival redistribution, log2(conditional/global)", fill=MUTED, font=font(14))
    axis_rows = [row for row in rows if row["axis"] == axis]
    threshold_indices = sorted({int(row["threshold_index"]) for row in axis_rows})
    values = np.full((CHILD_BINS, len(threshold_indices)), np.nan)
    counts = np.zeros(CHILD_BINS, dtype=int)
    for row in axis_rows:
        state_index = int(row["axis_bin"])
        counts[state_index] = int(row["starting_events"])
        if counts[state_index] >= 100:
            values[state_index, int(row["threshold_index"])] = float(row["redistribution_log2"])
    maximum = shared_maximum
    px0, py0, px1, py1 = left + 72, top + 67, right - 20, bottom - 55
    cell_width = (px1 - px0) / values.shape[1]
    cell_height = (py1 - py0) / values.shape[0]
    for row_index in range(CHILD_BINS):
        for column_index in range(values.shape[1]):
            x0 = px0 + column_index * cell_width
            y0 = py1 - (row_index + 1) * cell_height
            color = signed_color(float(values[row_index, column_index]), maximum)
            draw.rectangle((x0, y0, x0 + cell_width + 1, y0 + cell_height + 1), fill=color)
    draw.rectangle((px0, py0, px1, py1), outline=INK, width=2)
    for tick in (0, len(threshold_indices) // 2, len(threshold_indices) - 1):
        x = px0 + (tick + 0.5) * cell_width
        draw.text((x - 8, py1 + 8), f"{tick / max(1, len(threshold_indices)-1):.1f}", fill=MUTED, font=font(12))
    for tick in (0, 5, 11):
        y = py1 - (tick + 0.5) * cell_height
        if axis == "u":
            label = f"{(tick + 0.5) * 2 / CHILD_BINS:.1f}"
        else:
            label = f"{-1 + (tick + 0.5) * 2 / CHILD_BINS:.1f}"
        draw.text((px0 - 34, y - 7), label, fill=MUTED, font=font(12))
    draw.text(((px0 + px1) / 2 - 50, bottom - 24), "Normalized adult progress", fill=MUTED, font=font(14))
    draw.text((left + 4, (py0 + py1) / 2 - 8), axis.upper(), fill=MUTED, font=font(14))
    draw.text((px0, py0 - 18), f"blue negative   neutral zero   orange positive   shared scale +/-{maximum:.3f}", fill=MUTED, font=font(12))


def draw_transfer_bars(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, transfer_rows: list[dict[str, Any]], entity: str) -> None:
    left, top, right, bottom = box
    draw.text((left, top), title, fill=INK, font=font(20, True))
    draw.text((left, top + 27), "Baseline minus child adult-stage log loss; positive transfers information", fill=MUTED, font=font(14))
    selected = [row for row in transfer_rows if row["entity"] == entity and row["primary_transfer"]]
    transfer_order = [("r7", "r8"), ("r8", "r9")]
    model_order = ["u", "v", "uv"]
    values = {(row["train_rung"], row["test_rung"], row["model"]): float(row["gain_bits_per_event"]) for row in selected}
    maximum = max(abs(value) for value in values.values()) * 1.2 or 1e-6
    px0, py0, px1, py1 = left + 70, top + 70, right - 20, bottom - 60
    zero = (py0 + py1) / 2
    draw.line((px0, zero, px1, zero), fill=INK, width=2)
    for fraction in (-1.0, -0.5, 0.5, 1.0):
        y = zero - fraction * (py1 - py0) / 2
        draw.line((px0, y, px1, y), fill=GRID, width=1)
        draw.text((px0 - 62, y - 7), f"{fraction * maximum:+.1e}", fill=MUTED, font=font(11))
    group_width = (px1 - px0) / len(transfer_order)
    colors = {"u": BLUE, "v": ORANGE, "uv": NEUTRAL}
    for group_index, transfer in enumerate(transfer_order):
        center = px0 + (group_index + 0.5) * group_width
        bar_width = group_width * 0.16
        for model_index, model in enumerate(model_order):
            value = values[(transfer[0], transfer[1], model)]
            x0 = center + (model_index - 1.5) * bar_width
            y = zero - value / maximum * (py1 - py0) / 2
            draw.rectangle((x0, min(zero, y), x0 + bar_width * 0.86, max(zero, y)), fill=colors[model], outline=INK, width=1)
            draw.text((x0 - 2, y - 16 if value >= 0 else y + 3), f"{value:+.1e}", fill=INK, font=font(10))
        draw.text((center - 28, py1 + 12), f"{transfer[0].upper()}->{transfer[1].upper()}", fill=MUTED, font=font(13))
    legend_x = px0
    for model in model_order:
        draw.rectangle((legend_x, py0 - 18, legend_x + 14, py0 - 4), fill=colors[model])
        draw.text((legend_x + 20, py0 - 21), model.upper(), fill=INK, font=font(12))
        legend_x += 75


def make_figures(curve_rows: list[dict[str, Any]], rungs: dict[str, dict[str, Any]], transfer_rows: list[dict[str, Any]], surface_rows: list[dict[str, Any]]) -> None:
    image = Image.new("RGB", (1600, 1180), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((45, 24), "PN3A adult sieve survival and release", fill=INK, font=font(31, True))
    draw.text((45, 64), "Opened PN3 decimal-rung windows; p29-wheel candidates; exact arithmetic reconstruction", fill=MUTED, font=font(17))
    panels = [(45, 105, 785, 590), (815, 105, 1555, 590), (45, 625, 785, 1135), (815, 625, 1555, 1135)]
    candidate_series = []
    edge_series = []
    for name in WINDOWS:
        selected = [row for row in curve_rows if row["rung"] == name]
        candidate_series.append({"label": name.upper(), "color": RUNG_COLORS[name], "points": [(int(row["q"]), float(row["candidate_survival"])) for row in selected], "width": 4 if name == "r9" else 3})
        edge_series.append({"label": name.upper(), "color": RUNG_COLORS[name], "points": [(int(row["q"]), float(row["edge_survival"])) for row in selected], "width": 4 if name == "r9" else 3})
    r9_curve = [row for row in curve_rows if row["rung"] == "r9"]
    candidate_series.append({"label": "product", "color": NEUTRAL, "points": [(int(row["q"]), float(row["independence_product"])) for row in r9_curve], "dashed": True})
    edge_series.append({"label": "product^2", "color": NEUTRAL, "points": [(int(row["q"]), float(row["independence_product_squared"])) for row in r9_curve], "dashed": True})
    draw_line_panel(draw, panels[0], "Candidate survival across sieve rungs", "Fraction of p29-wheel candidates still alive after threshold q", candidate_series, "Survival")
    draw_line_panel(draw, panels[1], "Prime-pair survival across sieve rungs", "Fraction of adjacent candidate pairs with both endpoints still alive", edge_series, "Survival")
    release_series = [
        {"label": "Candidate", "color": BLUE, "points": [(int(row["q"]), float(row["candidate_cumulative_release"])) for row in r9_curve]},
        {"label": "Pair", "color": ORANGE, "points": [(int(row["q"]), float(row["edge_cumulative_release"])) for row in r9_curve]},
    ]
    draw_line_panel(draw, panels[2], "R9 cumulative release", "Complement of exact survival in [1,000,000,000, 1,010,000,000)", release_series, "Released")
    candidate_stage = np.bincount(stage_view(rungs["r9"], "candidate"), minlength=ADULT_STAGES + 1) / len(rungs["r9"]["candidate_death"])
    edge_stage = np.bincount(stage_view(rungs["r9"], "edge"), minlength=ADULT_STAGES + 1) / len(rungs["r9"]["edge_death"])
    draw_stage_bars(draw, panels[3], "R9 adult death-stage distribution", candidate_stage, edge_stage)
    image.save(SURVIVAL_FIGURE)

    image = Image.new("RGB", (1600, 1180), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((45, 24), "PN3A adult-child coupling", fill=INK, font=font(31, True))
    draw.text((45, 64), "Diagonal U and perpendicular V measured against the full sieve-death path", fill=MUTED, font=font(17))
    panels = [(45, 105, 785, 590), (815, 105, 1555, 590), (45, 625, 785, 1135), (815, 625, 1555, 1135)]
    eligible_surface_values = [
        abs(float(row["redistribution_log2"]))
        for row in surface_rows
        if int(row["starting_events"]) >= 100 and math.isfinite(float(row["redistribution_log2"]))
    ]
    shared_maximum = float(np.quantile(eligible_surface_values, 0.98)) or 1.0
    draw_heatmap(draw, panels[0], "Diagonal child coordinate U", surface_rows, "u", shared_maximum)
    draw_heatmap(draw, panels[1], "Perpendicular child coordinate V", surface_rows, "v", shared_maximum)
    draw_transfer_bars(draw, panels[2], "Candidate adult-stage transfer", transfer_rows, "candidate")
    draw_transfer_bars(draw, panels[3], "Prime-pair adult-stage transfer", transfer_rows, "edge")
    image.save(COUPLING_FIGURE)


def run() -> dict[str, Any]:
    protocol_sha = sha256_file(PROTOCOL)
    packet_sha = sha256_file(PN3_PACKET)
    packet = np.load(PN3_PACKET, allow_pickle=False)
    dev_summary = json.loads(PN3_DEV_SUMMARY.read_text(encoding="utf-8"))

    rungs: dict[str, dict[str, Any]] = {}
    rung_summaries: dict[str, Any] = {}
    calibration_checks: dict[str, Any] = {}
    for name, (low, high) in WINDOWS.items():
        rung, summary = reconstruct_rung(name, low, high, packet, dev_summary)
        rungs[name] = rung
        rung_summaries[name] = summary
        calibration_checks[name] = summary["checks"]

    curve_rows: list[dict[str, Any]] = []
    for name, rung in rungs.items():
        rows, curve_summary = survival_curve(rung)
        curve_rows.extend(rows)
        rung_summaries[name].update(curve_summary)

    euler_mertens_factor = math.exp(float(np.euler_gamma)) / 2.0
    for summary in rung_summaries.values():
        candidate_correction = summary["candidate_terminal_survival"] / summary["candidate_product_terminal"]
        edge_correction = summary["edge_terminal_survival"] / summary["edge_product_squared_terminal"]
        summary["post_result_established_crosswalk"] = {
            "candidate_actual_over_product": candidate_correction,
            "euler_mertens_factor_exp_gamma_over_2": euler_mertens_factor,
            "candidate_relative_difference_from_euler_mertens": candidate_correction / euler_mertens_factor - 1.0,
            "edge_actual_over_product_squared": edge_correction,
            "euler_mertens_factor_squared": euler_mertens_factor * euler_mertens_factor,
            "edge_relative_difference_from_squared_factor": edge_correction / (euler_mertens_factor * euler_mertens_factor) - 1.0,
        }

    transfer_rows, permutation_summary = transfer_diagnostics(rungs)
    surface_rows = adult_child_surfaces(rungs["r9"])

    write_csv(CURVES_PATH, curve_rows)
    write_csv(TRANSFER_PATH, transfer_rows)
    write_csv(SURFACES_PATH, surface_rows)
    np.savez_compressed(
        DATA_PATH,
        **{
            f"{name}__{field}": rung[field]
            for name, rung in rungs.items()
            for field in ("candidate_death", "edge_death", "u_bin", "v_bin")
        },
    )
    make_figures(curve_rows, rungs, transfer_rows, surface_rows)

    primary = [row for row in transfer_rows if row["primary_transfer"]]
    primary_lookup = {
        f"{row['train_rung']}_to_{row['test_rung']}__{row['entity']}__{row['model']}": row
        for row in primary
    }
    diagonal_supported = all(
        float(primary_lookup[f"{train}_to_{test}__edge__u"]["gain_bits_per_event"]) > 0
        and float(primary_lookup[f"{train}_to_{test}__edge__u"]["gain_bits_per_event"])
        > float(primary_lookup[f"{train}_to_{test}__edge__v"]["gain_bits_per_event"])
        for train, test in (("r7", "r8"), ("r8", "r9"))
    )
    results = {
        "test_id": "PN3A/ADULT-SIEVE-PATH/DEVELOPMENT-v1",
        "evidence_class": "opened-data structural diagnostic; not blind confirmation",
        "protocol_sha256": protocol_sha,
        "pn3_packet_sha256": packet_sha,
        "p31_accessed": False,
        "parameters": {
            "child_bins": CHILD_BINS,
            "adult_stages": ADULT_STAGES,
            "shrinkage": SHRINKAGE,
            "permutations": PERMUTATIONS,
            "permutation_seed": PERMUTATION_SEED,
            "location_blocks": LOCATION_BLOCKS,
        },
        "calibration_checks": calibration_checks,
        "rung_summaries": rung_summaries,
        "primary_transfer": primary_lookup,
        "permutation_summary": permutation_summary,
        "diagonal_rule_supported_on_both_edge_transfers": diagonal_supported,
        "outputs": {
            "curves_csv": CURVES_PATH,
            "transfer_csv": TRANSFER_PATH,
            "surfaces_csv": SURFACES_PATH,
            "diagnostic_data_npz": DATA_PATH,
            "survival_figure": SURVIVAL_FIGURE,
            "coupling_figure": COUPLING_FIGURE,
        },
    }
    write_json(RESULTS_PATH, results)
    results["output_hashes"] = {
        path.name: sha256_file(path)
        for path in (CURVES_PATH, TRANSFER_PATH, SURFACES_PATH, DATA_PATH, SURVIVAL_FIGURE, COUPLING_FIGURE)
    }
    write_json(RESULTS_PATH, results)
    return results


def render_existing() -> None:
    archive = np.load(DATA_PATH, allow_pickle=False)
    rungs = {
        name: {
            "name": name,
            "low": low,
            "high": high,
            "candidate_death": archive[f"{name}__candidate_death"],
            "edge_death": archive[f"{name}__edge_death"],
            "u_bin": archive[f"{name}__u_bin"],
            "v_bin": archive[f"{name}__v_bin"],
        }
        for name, (low, high) in WINDOWS.items()
    }
    curve_rows = read_csv(CURVES_PATH)
    for row in curve_rows:
        for key in row:
            if key not in ("rung",):
                row[key] = float(row[key])
    transfer_rows = read_csv(TRANSFER_PATH)
    for row in transfer_rows:
        row["primary_transfer"] = row["primary_transfer"] == "True"
        row["gain_bits_per_event"] = float(row["gain_bits_per_event"])
    surface_rows = read_csv(SURFACES_PATH)
    make_figures(curve_rows, rungs, transfer_rows, surface_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--figures-only", action="store_true")
    args = parser.parse_args()
    if args.figures_only:
        render_existing()
        print(json.dumps({"survival_figure": str(SURVIVAL_FIGURE), "coupling_figure": str(COUPLING_FIGURE)}, indent=2))
        return
    results = run()
    print(json.dumps({
        "test_id": results["test_id"],
        "r9_candidate_survival": results["rung_summaries"]["r9"]["candidate_terminal_survival"],
        "r9_edge_survival": results["rung_summaries"]["r9"]["edge_terminal_survival"],
        "r9_candidate_product_relative_error": results["rung_summaries"]["r9"]["candidate_product_relative_error"],
        "r9_edge_product_relative_error": results["rung_summaries"]["r9"]["edge_product_relative_error"],
        "diagonal_rule_supported": results["diagonal_rule_supported_on_both_edge_transfers"],
        "results_path": str(RESULTS_PATH),
    }, indent=2))


if __name__ == "__main__":
    main()
