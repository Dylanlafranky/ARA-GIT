"""Q54 / T314 recorded-transmon external ARA return test.

The target is the movement of successive whole Ramsey-I/Q circle centres,
not the internal Ramsey phase turn.  The protocol was frozen before these
centres or their headings were calculated.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


HERE = Path(__file__).resolve().parent
DATA = Path(
    r"F:\SystemFormulaFolder\external_data\quantum"
    r"\zenodo_ist_transmon_2023\subset"
)
MANIFEST_PATH = DATA / "Q54_ZENODO_SUBSET_MANIFEST.json"
PROTOCOL_PATH = HERE / "Q54_RECORDED_TRANSMON_EXTERNAL_RETURN_PROTOCOL_v1_FROZEN.md"
PROFILE_PATH = HERE / "Q54_RECORDED_TRANSMON_SOURCE_PROFILE.json"
RESULTS_PATH = HERE / "Q54_RECORDED_TRANSMON_EXTERNAL_RETURN_RESULTS.json"
CENTRES_PATH = HERE / "Q54_RECORDED_TRANSMON_CENTRES.csv.gz"
EVENTS_PATH = HERE / "Q54_RECORDED_TRANSMON_EVENTS.csv.gz"
FIGURE_PATH = HERE / "Q54_RECORDED_TRANSMON_EXTERNAL_RETURN.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LEFT = 1.0 / math.e
RIGHT = PHI - 1.0
WIDTH = RIGHT - LEFT
ARC_STARTS = np.mod(LEFT + np.arange(4, dtype=np.float64) / 4.0, 1.0)
ARC_NAMES = ["declared", "rotated_1", "rotated_2", "rotated_3"]

LATE_POINTS = 20
ANCHOR_POINTS = 5
MIN_CYCLE_POINTS = 6
MIN_PHASE_SPAN = 1.8 * math.pi
MIN_RADIUS_FRACTION = 0.20
MAX_RADIAL_RESIDUAL = 0.25
MIN_MOVEMENT = 0.01
END_LOW = 0.25
END_HIGH = 1.75
MID_LOW = 0.50
MID_HIGH = 1.50
BOOTSTRAP_DRAWS = 5_000
SHUFFLE_DRAWS = 5_000
BOOTSTRAP_SEED = 540031
SHUFFLE_SEED = 540032
EPS = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def numeric_vectors(path: Path) -> list[np.ndarray]:
    vectors: list[np.ndarray] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        try:
            values = np.asarray([float(value) for value in line.split()], dtype=np.float64)
        except ValueError:
            continue
        vectors.append(values)
    return vectors


def parse_t2(path: Path) -> dict[str, object]:
    vectors = numeric_vectors(path)
    if len(vectors) < 4:
        raise ValueError("fewer than four numeric vectors")
    repeat_coordinate = vectors[0]
    delay = vectors[1]
    repeats = repeat_coordinate.size
    if len(vectors) != 2 + 2 * repeats:
        raise ValueError(
            f"expected {2 + 2 * repeats} vectors from repeat coordinate, "
            f"found {len(vectors)}"
        )
    i_rows = np.vstack(vectors[2 : 2 + repeats])
    q_rows = np.vstack(vectors[2 + repeats : 2 + 2 * repeats])
    if i_rows.shape != q_rows.shape or i_rows.shape[1] != delay.size:
        raise ValueError(
            f"I/Q/delay shape mismatch: {i_rows.shape}, {q_rows.shape}, {delay.shape}"
        )
    return {
        "repeat_coordinate": repeat_coordinate,
        "delay": delay,
        "i": i_rows,
        "q": q_rows,
    }


def discover_files() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    profile: list[dict[str, object]] = []
    parsed: list[dict[str, object]] = []
    paths = sorted((DATA / "Fig6").rglob("T2_*.txt"))
    seen_hashes: set[str] = set()
    for path in paths:
        rel = path.relative_to(DATA).as_posix()
        device = next(
            (part for part in path.parts if part in {"Device A", "Device B", "Device C"}),
            "unknown",
        )
        digest = sha256(path)
        duplicate = digest in seen_hashes
        seen_hashes.add(digest)
        row: dict[str, object] = {
            "path": str(path),
            "relative_path": rel,
            "device": device,
            "sha256": digest,
            "duplicate": duplicate,
        }
        try:
            data = parse_t2(path)
            delay = np.asarray(data["delay"])
            i_rows = np.asarray(data["i"])
            q_rows = np.asarray(data["q"])
            finite = bool(
                np.all(np.isfinite(delay))
                and np.all(np.isfinite(i_rows))
                and np.all(np.isfinite(q_rows))
            )
            increasing = bool(np.all(np.diff(delay) > 0))
            complete = bool(
                delay.size == 101
                and i_rows.shape[0] >= 9
                and finite
                and increasing
                and not duplicate
            )
            primary = bool(device in {"Device B", "Device C"} and complete)
            row.update(
                {
                    "delay_points": int(delay.size),
                    "repeats": int(i_rows.shape[0]),
                    "finite": finite,
                    "strictly_increasing_delay": increasing,
                    "schema_complete": complete,
                    "primary": primary,
                    "parse_error": None,
                }
            )
            parsed.append({**row, **data})
        except Exception as exc:  # schema failure is recorded, never hidden
            row.update(
                {
                    "delay_points": None,
                    "repeats": None,
                    "finite": False,
                    "strictly_increasing_delay": False,
                    "schema_complete": False,
                    "primary": False,
                    "parse_error": str(exc),
                }
            )
        profile.append(row)
    return profile, parsed


def intrinsic_trace(
    i_rows: np.ndarray,
    q_rows: np.ndarray,
    estimator: str,
) -> tuple[np.ndarray, dict[str, float | int | bool]]:
    raw = np.asarray(i_rows, dtype=np.float64) + 1j * np.asarray(
        q_rows, dtype=np.float64
    )
    if estimator == "mean":
        z = np.mean(raw, axis=0)
    elif estimator == "median":
        z = np.median(raw.real, axis=0) + 1j * np.median(raw.imag, axis=0)
    else:
        raise ValueError(estimator)
    origin = np.mean(z[-LATE_POINTS:])
    centred = z - origin
    anchor = np.mean(centred[:ANCHOR_POINTS])
    if abs(anchor) <= EPS:
        raise ValueError("near-zero intrinsic orientation anchor")
    rotated = centred * np.exp(-1j * np.angle(anchor))
    phase = np.unwrap(np.angle(rotated))
    slope = float(np.median(np.diff(phase)))
    conjugated = slope < 0
    if conjugated:
        rotated = np.conj(rotated)
        phase = np.unwrap(np.angle(rotated))
        slope = float(np.median(np.diff(phase)))
    return rotated, {
        "origin_i": float(origin.real),
        "origin_q": float(origin.imag),
        "anchor_angle_turns": float((np.angle(anchor) / (2.0 * math.pi)) % 1.0),
        "conjugated": conjugated,
        "median_phase_step": slope,
    }


def circle_fit(points: np.ndarray) -> tuple[complex, float, float] | None:
    u = np.asarray(points.real, dtype=np.float64)
    v = np.asarray(points.imag, dtype=np.float64)
    design = np.column_stack((2.0 * u, 2.0 * v, np.ones(u.size)))
    target = u * u + v * v
    solution, _, rank, _ = np.linalg.lstsq(design, target, rcond=None)
    if rank < 3:
        return None
    centre = complex(float(solution[0]), float(solution[1]))
    radius_sq = float(solution[2] + centre.real**2 + centre.imag**2)
    if radius_sq <= EPS or not np.isfinite(radius_sq):
        return None
    radius = math.sqrt(radius_sq)
    radial = np.abs(points - centre)
    residual = float(np.median(np.abs(radial - radius)) / radius)
    return centre, radius, residual


def extract_circles(
    z: np.ndarray,
    delay: np.ndarray,
    file_row: dict[str, object],
    estimator: str,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    phase = np.unwrap(np.angle(z))
    start_phase = float(phase[0])
    maximum_phase = float(np.max(phase))
    crossing_indices = [0]
    k = 1
    previous = 0
    while start_phase + k * 2.0 * math.pi <= maximum_phase + EPS:
        candidates = np.flatnonzero(
            (np.arange(phase.size) > previous)
            & (phase >= start_phase + k * 2.0 * math.pi)
        )
        if not candidates.size:
            break
        previous = int(candidates[0])
        crossing_indices.append(previous)
        k += 1

    rows: list[dict[str, object]] = []
    first_radius: float | None = None
    rejection_counts: dict[str, int] = defaultdict(int)
    for cycle_index, (start, end) in enumerate(
        zip(crossing_indices[:-1], crossing_indices[1:])
    ):
        points = z[start : end + 1]
        phase_span = float(phase[end] - phase[start])
        if points.size < MIN_CYCLE_POINTS:
            rejection_counts["too_few_points"] += 1
            continue
        if phase_span < MIN_PHASE_SPAN:
            rejection_counts["short_phase_span"] += 1
            continue
        fit = circle_fit(points)
        if fit is None:
            rejection_counts["fit_failure"] += 1
            continue
        centre, radius, residual = fit
        if first_radius is None:
            first_radius = radius
        if radius < MIN_RADIUS_FRACTION * first_radius:
            rejection_counts["below_radius_floor"] += 1
            continue
        if residual > MAX_RADIAL_RESIDUAL:
            rejection_counts["above_residual_ceiling"] += 1
            continue
        centroid = complex(float(np.mean(points.real)), float(np.mean(points.imag)))
        extrema = complex(
            float((np.min(points.real) + np.max(points.real)) / 2.0),
            float((np.min(points.imag) + np.max(points.imag)) / 2.0),
        )
        rows.append(
            {
                "centre_id": -1,
                "relative_path": file_row["relative_path"],
                "device": file_row["device"],
                "estimator": estimator,
                "cycle_index": cycle_index,
                "start_index": start,
                "end_index": end,
                "start_delay": float(delay[start]),
                "end_delay": float(delay[end]),
                "points": int(points.size),
                "phase_span": phase_span,
                "circle_i": centre.real,
                "circle_q": centre.imag,
                "centroid_i": centroid.real,
                "centroid_q": centroid.imag,
                "extrema_i": extrema.real,
                "extrema_q": extrema.imag,
                "radius": radius,
                "circle_fit_residual": residual,
            }
        )
    return rows, {
        "phase_range": float(maximum_phase - start_phase),
        "candidate_cycles": max(0, len(crossing_indices) - 1),
        "retained_cycles": len(rows),
        "rejections": dict(rejection_counts),
    }


def heading(value: complex) -> float:
    return float((math.atan2(value.imag, value.real) / (2.0 * math.pi)) % 1.0)


def circular_distance(a: float | np.ndarray, b: float) -> float | np.ndarray:
    delta = np.abs(np.asarray(a) - b)
    return np.minimum(delta, 1.0 - delta)


def in_arc(values: np.ndarray, start: float) -> np.ndarray:
    return np.mod(values - start, 1.0) <= WIDTH


def local_x(values: np.ndarray, start: float) -> np.ndarray:
    return 2.0 * np.mod(values - start, 1.0) / WIDTH


def build_events(centres: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in centres:
        grouped[(str(row["relative_path"]), str(row["estimator"]))].append(row)
    events: list[dict[str, object]] = []
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["cycle_index"]))
        for index in range(1, len(rows) - 1):
            previous, current, following = rows[index - 1 : index + 2]
            consecutive = bool(
                int(current["cycle_index"]) == int(previous["cycle_index"]) + 1
                and int(following["cycle_index"]) == int(current["cycle_index"]) + 1
            )
            radii = np.asarray(
                [
                    float(previous["radius"]),
                    float(current["radius"]),
                    float(following["radius"]),
                ],
                dtype=np.float64,
            )
            output: dict[str, object] = {
                "event_id": len(events),
                "relative_path": current["relative_path"],
                "device": current["device"],
                "estimator": current["estimator"],
                "cycle_index": int(current["cycle_index"]),
                "consecutive_centres": consecutive,
                "radius_mean": float(np.mean(radii)),
                "circle_fit_residual": float(current["circle_fit_residual"]),
                "current_delay": float(
                    (float(current["start_delay"]) + float(current["end_delay"])) / 2.0
                ),
            }
            for centre_name in ("circle", "centroid", "extrema"):
                left = complex(
                    float(previous[f"{centre_name}_i"]),
                    float(previous[f"{centre_name}_q"]),
                )
                right = complex(
                    float(following[f"{centre_name}_i"]),
                    float(following[f"{centre_name}_q"]),
                )
                vector = right - left
                strength = float(abs(vector) / np.mean(radii))
                angle = heading(vector) if abs(vector) > EPS else math.nan
                output[f"{centre_name}_di"] = float(vector.real)
                output[f"{centre_name}_dq"] = float(vector.imag)
                output[f"{centre_name}_strength"] = strength
                output[f"{centre_name}_heading"] = angle
            events.append(output)
    return events


def selected_events(
    events: list[dict[str, object]],
    estimator: str,
    centre_name: str = "circle",
    primary_only: bool = True,
) -> list[dict[str, object]]:
    output = []
    for row in events:
        if str(row["estimator"]) != estimator:
            continue
        if primary_only and str(row["device"]) not in {"Device B", "Device C"}:
            continue
        if not bool(row["consecutive_centres"]):
            continue
        if float(row[f"{centre_name}_strength"]) < MIN_MOVEMENT:
            continue
        if not math.isfinite(float(row[f"{centre_name}_heading"])):
            continue
        output.append(row)
    return output


def arc_summary(
    events: list[dict[str, object]],
    estimator: str,
    device: str | None = None,
    centre_name: str = "circle",
) -> dict[str, object]:
    selected = selected_events(events, estimator, centre_name)
    if device is not None:
        selected = [row for row in selected if str(row["device"]) == device]
    headings = np.asarray(
        [float(row[f"{centre_name}_heading"]) for row in selected], dtype=np.float64
    )
    counts = np.asarray(
        [np.sum(in_arc(headings, float(start))) for start in ARC_STARTS], dtype=int
    )
    total = int(headings.size)
    fractions = counts / total if total else np.full(4, np.nan)
    return {
        "events": total,
        "counts": dict(zip(ARC_NAMES, counts.tolist())),
        "fractions": dict(zip(ARC_NAMES, fractions.tolist())),
        "winner": ARC_NAMES[int(np.argmax(counts))] if total else None,
    }


def file_bootstrap(
    events: list[dict[str, object]], estimator: str, centre_name: str = "circle"
) -> dict[str, object]:
    selected = selected_events(events, estimator, centre_name)
    by_file: dict[str, list[float]] = defaultdict(list)
    for row in selected:
        by_file[str(row["relative_path"])].append(float(row[f"{centre_name}_heading"]))
    files = sorted(by_file)
    counts = np.zeros((len(files), 4), dtype=np.int32)
    totals = np.zeros(len(files), dtype=np.int32)
    for index, name in enumerate(files):
        values = np.asarray(by_file[name])
        totals[index] = values.size
        counts[index] = [
            int(np.sum(in_arc(values, float(start)))) for start in ARC_STARTS
        ]
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    differences = np.full(BOOTSTRAP_DRAWS, np.nan, dtype=np.float64)
    if files:
        for draw in range(BOOTSTRAP_DRAWS):
            chosen = rng.integers(0, len(files), size=len(files))
            draw_counts = np.sum(counts[chosen], axis=0)
            total = int(np.sum(totals[chosen]))
            if total:
                fractions = draw_counts / total
                differences[draw] = fractions[0] - np.max(fractions[1:])
    finite = differences[np.isfinite(differences)]
    return {
        "draws": BOOTSTRAP_DRAWS,
        "seed": BOOTSTRAP_SEED,
        "files": len(files),
        "probability_declared_beats_strongest_control": (
            float(np.mean(finite > 0)) if finite.size else math.nan
        ),
        "declared_minus_strongest_control_median": (
            float(np.median(finite)) if finite.size else math.nan
        ),
        "ci95": (
            [float(np.quantile(finite, 0.025)), float(np.quantile(finite, 0.975))]
            if finite.size
            else [math.nan, math.nan]
        ),
    }


def sequence_counts(values: np.ndarray, arc_start: float) -> dict[str, int]:
    """Count ordered endpoint alternations and returns inside one arc.

    NaN values and headings outside the arc end a contiguous run.
    """
    inside = np.isfinite(values) & in_arc(values, arc_start)
    x = local_x(values, arc_start)
    half_low_high = 0
    half_high_low = 0
    return_low_high_low = 0
    return_high_low_high = 0
    runs = 0
    start = 0
    while start < values.size:
        if not inside[start]:
            start += 1
            continue
        end = start + 1
        while end < values.size and inside[end]:
            end += 1
        block = x[start:end]
        if block.size >= 3:
            runs += 1
            endpoints: list[str] = []
            current: str | None = None
            crossed_mid = False
            for value in block:
                if MID_LOW <= value <= MID_HIGH:
                    crossed_mid = True
                endpoint = (
                    "low" if value <= END_LOW else "high" if value >= END_HIGH else None
                )
                if endpoint is None:
                    continue
                if current is None:
                    current = endpoint
                    endpoints.append(endpoint)
                    crossed_mid = False
                    continue
                if endpoint == current:
                    continue
                if not crossed_mid:
                    continue
                if current == "low":
                    half_low_high += 1
                else:
                    half_high_low += 1
                current = endpoint
                endpoints.append(endpoint)
                crossed_mid = False
                if len(endpoints) >= 3 and endpoints[-3] == endpoints[-1]:
                    if endpoints[-1] == "low":
                        return_low_high_low += 1
                    else:
                        return_high_low_high += 1
        start = end
    return {
        "runs": runs,
        "half_low_high": half_low_high,
        "half_high_low": half_high_low,
        "half_total": half_low_high + half_high_low,
        "return_low_high_low": return_low_high_low,
        "return_high_low_high": return_high_low_high,
        "return_total": return_low_high_low + return_high_low_high,
    }


def file_sequences(
    events: list[dict[str, object]],
    estimator: str,
    centre_name: str = "circle",
) -> dict[str, np.ndarray]:
    all_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        if str(row["estimator"]) != estimator:
            continue
        if str(row["device"]) not in {"Device B", "Device C"}:
            continue
        all_rows[str(row["relative_path"])].append(row)
    arrays: dict[str, np.ndarray] = {}
    for name, rows in all_rows.items():
        rows.sort(key=lambda row: int(row["cycle_index"]))
        values = []
        previous_index: int | None = None
        for row in rows:
            index = int(row["cycle_index"])
            if previous_index is not None and index != previous_index + 1:
                values.append(math.nan)
            eligible = bool(
                row["consecutive_centres"]
                and float(row[f"{centre_name}_strength"]) >= MIN_MOVEMENT
                and math.isfinite(float(row[f"{centre_name}_heading"]))
            )
            values.append(
                float(row[f"{centre_name}_heading"]) if eligible else math.nan
            )
            previous_index = index
        arrays[name] = np.asarray(values, dtype=np.float64)
    return arrays


def traversal_summary(
    arrays: dict[str, np.ndarray], arc_start: float
) -> dict[str, object]:
    total = {
        "runs": 0,
        "half_low_high": 0,
        "half_high_low": 0,
        "half_total": 0,
        "return_low_high_low": 0,
        "return_high_low_high": 0,
        "return_total": 0,
    }
    half_files: set[str] = set()
    return_files: set[str] = set()
    by_file: dict[str, dict[str, int]] = {}
    for name, values in arrays.items():
        counts = sequence_counts(values, arc_start)
        by_file[name] = counts
        for key in total:
            total[key] += counts[key]
        if counts["half_total"]:
            half_files.add(name)
        if counts["return_total"]:
            return_files.add(name)
    return {
        **total,
        "half_files": len(half_files),
        "return_files": len(return_files),
        "by_file": by_file,
    }


def shuffled_null(
    arrays: dict[str, np.ndarray], arc_start: float
) -> dict[str, object]:
    rng = np.random.default_rng(SHUFFLE_SEED + int(round(arc_start * 1_000_000)))
    half = np.zeros(SHUFFLE_DRAWS, dtype=np.int32)
    returns = np.zeros(SHUFFLE_DRAWS, dtype=np.int32)
    for draw in range(SHUFFLE_DRAWS):
        half_total = 0
        return_total = 0
        for values in arrays.values():
            shuffled = values.copy()
            finite_indices = np.flatnonzero(np.isfinite(shuffled))
            shuffled[finite_indices] = rng.permutation(shuffled[finite_indices])
            counts = sequence_counts(shuffled, arc_start)
            half_total += counts["half_total"]
            return_total += counts["return_total"]
        half[draw] = half_total
        returns[draw] = return_total
    return {
        "draws": SHUFFLE_DRAWS,
        "seed": SHUFFLE_SEED + int(round(arc_start * 1_000_000)),
        "half": {
            "mean": float(np.mean(half)),
            "p95": float(np.quantile(half, 0.95)),
            "p99": float(np.quantile(half, 0.99)),
            "max": int(np.max(half)),
        },
        "return": {
            "mean": float(np.mean(returns)),
            "p95": float(np.quantile(returns, 0.95)),
            "p99": float(np.quantile(returns, 0.99)),
            "max": int(np.max(returns)),
        },
    }


def intrinsic_invariance(
    i_rows: np.ndarray, q_rows: np.ndarray
) -> dict[str, object]:
    base, _ = intrinsic_trace(i_rows, q_rows, "mean")
    angle = 0.731
    translation = complex(9.2, -4.7)
    scale = 3.25
    raw = i_rows + 1j * q_rows
    transformed = scale * raw * np.exp(1j * angle) + translation
    changed, _ = intrinsic_trace(transformed.real, transformed.imag, "mean")
    normalized_base = base / max(float(np.max(np.abs(base))), EPS)
    normalized_changed = changed / max(float(np.max(np.abs(changed))), EPS)
    error = float(np.max(np.abs(normalized_base - normalized_changed)))
    return {
        "translation_rotation_scale_max_error": error,
        "pass": bool(error <= 1e-10),
    }


def write_csv_gz(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(
    parsed: list[dict[str, object]],
    centres: list[dict[str, object]],
    events: list[dict[str, object]],
    results: dict[str, object],
) -> None:
    if plt is None:
        return
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(
        "Q54 — recorded transmon whole-circle external ARA return",
        fontsize=18,
        weight="bold",
    )

    primary_mean = [
        row
        for row in centres
        if row["estimator"] == "mean"
        and row["device"] in {"Device B", "Device C"}
    ]
    by_file: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in primary_mean:
        by_file[str(row["relative_path"])].append(row)
    example_name = max(by_file, key=lambda name: len(by_file[name])) if by_file else None
    ax = axes[0, 0]
    if example_name is not None:
        source = next(
            row for row in parsed if row["relative_path"] == example_name
        )
        z, _ = intrinsic_trace(
            np.asarray(source["i"]), np.asarray(source["q"]), "mean"
        )
        ax.plot(z.real, z.imag, color="#91a8bb", lw=1.4, label="recorded mean I/Q")
        rows = sorted(by_file[example_name], key=lambda row: int(row["cycle_index"]))
        c = np.asarray(
            [
                complex(float(row["circle_i"]), float(row["circle_q"]))
                for row in rows
            ]
        )
        ax.plot(
            c.real,
            c.imag,
            "o-",
            color="#d8901d",
            lw=2,
            ms=4,
            label="successive whole-circle centres",
        )
        ax.set_title(f"Example hardware lineage: {Path(example_name).name}")
        ax.legend()
    else:
        ax.text(0.5, 0.5, "No retained primary circles", ha="center", va="center")
    ax.set_xlabel("intrinsic I")
    ax.set_ylabel("intrinsic Q")
    ax.axis("equal")

    selected = selected_events(events, "mean")
    headings = np.asarray([float(row["circle_heading"]) for row in selected])
    ax = axes[0, 1]
    ax.hist(headings, bins=np.linspace(0, 1, 73), color="#587fa9", alpha=0.86)
    for index, start in enumerate(ARC_STARTS):
        ax.axvspan(
            start,
            min(start + WIDTH, 1.0),
            color="#e0a13b" if index == 0 else "#9aa7b2",
            alpha=0.25 if index == 0 else 0.10,
        )
        if start + WIDTH > 1.0:
            ax.axvspan(
                0.0,
                start + WIDTH - 1.0,
                color="#9aa7b2",
                alpha=0.10,
            )
    ax.axvline(LEFT, color="#333333", lw=1.5, label="1/e pole")
    ax.axvline(RIGHT, color="#b86f18", lw=1.5, label="Phi pole")
    ax.set(
        xlim=(0, 1),
        xlabel="external whole-circle heading (turns)",
        ylabel="eligible tangent events",
        title="Declared directional arc and matched rotations",
    )
    ax.legend()

    ax = axes[1, 0]
    traversal = results["traversal"]
    half_values = [
        traversal[name]["observed"]["half_total"] for name in ARC_NAMES
    ]
    return_values = [
        traversal[name]["observed"]["return_total"] for name in ARC_NAMES
    ]
    x = np.arange(4)
    ax.bar(x - 0.18, half_values, width=0.36, color="#4d84b4", label="half")
    ax.bar(x + 0.18, return_values, width=0.36, color="#d89328", label="return")
    ax.axhline(
        traversal["declared"]["shuffle"]["half"]["p99"],
        color="#4d84b4",
        ls="--",
        alpha=0.7,
        label="declared shuffled half p99",
    )
    ax.axhline(
        traversal["declared"]["shuffle"]["return"]["p99"],
        color="#d89328",
        ls=":",
        alpha=0.9,
        label="declared shuffled return p99",
    )
    ax.set_xticks(x, ARC_NAMES, rotation=18)
    ax.set_ylabel("ordered events")
    ax.set_title("Active half-traversals and full returns")
    ax.legend()
    if not results["gates"]["G0_valid_hardware_object"]:
        ax.text(
            0.5,
            0.5,
            "INVALID OBJECT\nonly 1 eligible primary tangent",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            color="#7a2633",
            bbox={"facecolor": "white", "edgecolor": "#7a2633", "alpha": 0.92},
        )

    ax = axes[1, 1]
    labels = [
        "B mean",
        "C mean",
        "B median",
        "C median",
    ]
    matrix = []
    for estimator in ("mean", "median"):
        for device in ("Device B", "Device C"):
            summary = results["arc_occupancy"][estimator][device]
            matrix.append([summary["fractions"][name] for name in ARC_NAMES])
    data = np.asarray(matrix, dtype=float)
    image = ax.imshow(data, aspect="auto", cmap="Blues", vmin=0, vmax=max(0.5, np.nanmax(data)))
    ax.set_yticks(np.arange(4), labels)
    ax.set_xticks(np.arange(4), ARC_NAMES, rotation=18)
    ax.set_title("Arc occupancy by device and repeat estimator")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            label = f"{data[i, j]:.3f}" if np.isfinite(data[i, j]) else "N/A"
            ax.text(j, i, label, ha="center", va="center")
    fig.colorbar(image, ax=ax, shrink=0.8, label="event fraction")

    fig.text(
        0.012,
        0.012,
        (
            f"Path: {results['verdicts']['directional_path']} · "
            f"Half: {results['verdicts']['active_half_reversal']} · "
            f"Full return: {results['verdicts']['full_active_return']} · "
            f"Zenodo 10.5281/zenodo.8004359"
        ),
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig(FIGURE_PATH, dpi=190)
    plt.close(fig)


def main() -> None:
    profile, parsed = discover_files()
    PROFILE_PATH.write_text(
        json.dumps(
            {
                "source": {
                    "doi": "10.5281/zenodo.8004359",
                    "manifest": str(MANIFEST_PATH),
                    "manifest_sha256": sha256(MANIFEST_PATH),
                },
                "files": profile,
                "summary": {
                    "discovered": len(profile),
                    "parsed": sum(row["parse_error"] is None for row in profile),
                    "duplicates": sum(bool(row["duplicate"]) for row in profile),
                    "primary": sum(bool(row["primary"]) for row in profile),
                    "primary_by_device": {
                        device: sum(
                            bool(row["primary"]) and row["device"] == device
                            for row in profile
                        )
                        for device in ("Device B", "Device C")
                    },
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    centres: list[dict[str, object]] = []
    extraction_profile: dict[str, object] = {}
    invariance: dict[str, object] | None = None
    for file_row in parsed:
        if not bool(file_row["schema_complete"]):
            continue
        for estimator in ("mean", "median"):
            z, orientation = intrinsic_trace(
                np.asarray(file_row["i"]),
                np.asarray(file_row["q"]),
                estimator,
            )
            rows, details = extract_circles(
                z,
                np.asarray(file_row["delay"]),
                file_row,
                estimator,
            )
            for row in rows:
                row["centre_id"] = len(centres)
                row.update(
                    {
                        "origin_i": orientation["origin_i"],
                        "origin_q": orientation["origin_q"],
                        "anchor_angle_turns": orientation["anchor_angle_turns"],
                        "conjugated": orientation["conjugated"],
                    }
                )
                centres.append(row)
            extraction_profile[f"{file_row['relative_path']}::{estimator}"] = {
                **orientation,
                **details,
            }
        if invariance is None and bool(file_row["primary"]):
            invariance = intrinsic_invariance(
                np.asarray(file_row["i"]), np.asarray(file_row["q"])
            )
    if invariance is None:
        invariance = {"translation_rotation_scale_max_error": math.nan, "pass": False}

    events = build_events(centres)
    occupancy: dict[str, object] = {}
    bootstraps: dict[str, object] = {}
    arrays_by_estimator: dict[str, dict[str, np.ndarray]] = {}
    traversal: dict[str, object] = {}
    for estimator in ("mean", "median"):
        occupancy[estimator] = {
            "pooled": arc_summary(events, estimator),
            "Device B": arc_summary(events, estimator, "Device B"),
            "Device C": arc_summary(events, estimator, "Device C"),
        }
        bootstraps[estimator] = file_bootstrap(events, estimator)
        arrays = file_sequences(events, estimator)
        arrays_by_estimator[estimator] = arrays
        if estimator == "mean":
            for name, start in zip(ARC_NAMES, ARC_STARTS):
                traversal[name] = {
                    "observed": traversal_summary(arrays, float(start)),
                    "shuffle": shuffled_null(arrays, float(start)),
                }

    primary_occupancy = occupancy["mean"]["pooled"]
    b_occupancy = occupancy["mean"]["Device B"]
    c_occupancy = occupancy["mean"]["Device C"]
    median_occupancy = occupancy["median"]["pooled"]
    bootstrap = bootstraps["mean"]
    declared = traversal["declared"]
    control_half_max = max(
        traversal[name]["observed"]["half_total"] for name in ARC_NAMES[1:]
    )
    control_return_max = max(
        traversal[name]["observed"]["return_total"] for name in ARC_NAMES[1:]
    )

    eligible_by_file: dict[str, int] = defaultdict(int)
    for row in selected_events(events, "mean"):
        eligible_by_file[str(row["relative_path"])] += 1

    g0 = bool(
        invariance["pass"]
        and sum(count >= 3 for count in eligible_by_file.values()) >= 5
    )
    g1 = bool(
        primary_occupancy["winner"] == "declared"
        and float(bootstrap["probability_declared_beats_strongest_control"]) >= 0.95
    )
    g2 = bool(
        declared["observed"]["half_total"] >= 5
        and declared["observed"]["half_files"] >= 5
        and declared["observed"]["half_low_high"] > 0
        and declared["observed"]["half_high_low"] > 0
        and declared["observed"]["half_total"] > control_half_max
        and declared["observed"]["half_total"] > declared["shuffle"]["half"]["p99"]
    )
    g3 = bool(
        declared["observed"]["return_total"] >= 3
        and declared["observed"]["return_files"] >= 3
        and declared["observed"]["return_low_high_low"] > 0
        and declared["observed"]["return_high_low_high"] > 0
        and declared["observed"]["return_total"] > control_return_max
        and declared["observed"]["return_total"]
        > declared["shuffle"]["return"]["p99"]
    )
    g4_path = bool(
        b_occupancy["winner"] == "declared"
        and c_occupancy["winner"] == "declared"
        and median_occupancy["winner"] == "declared"
    )
    median_traversal = traversal_summary(
        arrays_by_estimator["median"], float(ARC_STARTS[0])
    )
    g4_half = bool(g4_path and median_traversal["half_total"] > 0)
    g4_return = bool(g4_path and median_traversal["return_total"] > 0)

    directional = (
        "SUPPORTED"
        if g0 and g1 and g4_path
        else "MIXED"
        if g0 and (g1 or g4_path)
        else "NOT SUPPORTED"
        if g0
        else "INVALID"
    )
    half = "SUPPORTED" if g0 and g2 and g4_half else "NOT SUPPORTED" if g0 else "INVALID"
    full = (
        "SUPPORTED" if g0 and g3 and g4_return else "NOT SUPPORTED" if g0 else "INVALID"
    )

    results: dict[str, object] = {
        "test": "Q54 / T314 recorded transmon external ARA return",
        "frozen_protocol": str(PROTOCOL_PATH),
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "source": {
            "doi": "10.5281/zenodo.8004359",
            "manifest_path": str(MANIFEST_PATH),
            "manifest_sha256": sha256(MANIFEST_PATH),
            "source_profile_path": str(PROFILE_PATH),
            "primary_devices": ["Device B", "Device C"],
            "development_device": "Device A",
            "primary_files": sum(bool(row["primary"]) for row in profile),
        },
        "geometry": {
            "left_one_over_e": LEFT,
            "right_phi_minus_one": RIGHT,
            "arc_width_turns": WIDTH,
            "arc_width_degrees": WIDTH * 360.0,
            "arc_starts": ARC_STARTS.tolist(),
            "arc_names": ARC_NAMES,
        },
        "fixed_parameters": {
            "late_points": LATE_POINTS,
            "anchor_points": ANCHOR_POINTS,
            "minimum_cycle_points": MIN_CYCLE_POINTS,
            "minimum_phase_span_radians": MIN_PHASE_SPAN,
            "minimum_radius_fraction": MIN_RADIUS_FRACTION,
            "maximum_radial_residual": MAX_RADIAL_RESIDUAL,
            "minimum_movement_over_radius": MIN_MOVEMENT,
            "endpoint_low": END_LOW,
            "endpoint_high": END_HIGH,
            "middle_band": [MID_LOW, MID_HIGH],
        },
        "population": {
            "centres_all": len(centres),
            "centres_primary_mean": len(primary_mean := [
                row
                for row in centres
                if row["estimator"] == "mean"
                and row["device"] in {"Device B", "Device C"}
            ]),
            "events_all": len(events),
            "eligible_primary_mean": len(selected_events(events, "mean")),
            "eligible_primary_files": len(eligible_by_file),
            "files_with_at_least_three_eligible": sum(
                count >= 3 for count in eligible_by_file.values()
            ),
        },
        "extraction_profile": extraction_profile,
        "invariance": invariance,
        "arc_occupancy": occupancy,
        "bootstrap": bootstraps,
        "traversal": traversal,
        "median_declared_traversal": median_traversal,
        "gates": {
            "G0_valid_hardware_object": g0,
            "G1_declared_directional_location": g1,
            "G2_active_half_traversal": g2,
            "G3_full_active_return": g3,
            "G4_path_device_estimator_replication": g4_path,
            "G4_half_estimator_replication": g4_half,
            "G4_return_estimator_replication": g4_return,
        },
        "verdicts": {
            "directional_path": directional,
            "active_half_reversal": half,
            "full_active_return": full,
        },
        "boundaries": [
            "The measured vector is circle-centre movement in an intrinsic recorded I/Q plane, not literal spatial travel.",
            "Each delay point is a repeated hardware preparation/measurement, not one uninterrupted single-shot trajectory.",
            "Device A was opened for source profiling and cannot contribute to the primary verdict.",
            "A full-return failure cannot be rescued by parent-ridge averaging, T1, or forced flux-jump resets.",
        ],
    }
    RESULTS_PATH.write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_csv_gz(CENTRES_PATH, centres)
    write_csv_gz(EVENTS_PATH, events)
    make_figure(parsed, centres, events, results)
    print(
        json.dumps(
            {
                "verdicts": results["verdicts"],
                "gates": results["gates"],
                "population": results["population"],
                "primary_occupancy": primary_occupancy,
                "declared_traversal": declared,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
