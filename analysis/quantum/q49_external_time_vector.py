"""Q49 / T309 external centreline time-vector test.

The measured object is the centreline carrying complete internally rotating
phase-plane cycles through time. Internal turn size and quadrant-flip
distances are not loaded.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import pathlib
from collections import defaultdict

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q39_information3_strongmax"
DERIVED_PATH = DATA / "q39_derived_cache.npz"
FIDELITY_PATH = HERE / "Q49_EXTERNAL_TIME_VECTOR_FIDELITY_PACKET_v1.md"
PROTOCOL_PATH = HERE / "Q49_EXTERNAL_TIME_VECTOR_PROTOCOL_v1_FROZEN.md"
RESULTS_PATH = HERE / "Q49_EXTERNAL_TIME_VECTOR_RESULTS.json"
EVENTS_PATH = HERE / "Q49_EXTERNAL_TIME_VECTOR_EVENTS.csv.gz"
CENTRES_PATH = HERE / "Q49_EXTERNAL_TIME_VECTOR_CENTRES.csv.gz"
FIGURE_PATH = HERE / "Q49_EXTERNAL_TIME_VECTOR.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LEFT = 1.0 / math.e
RIGHT = PHI - 1.0
WIDTH = RIGHT - LEFT
THREE_EIGHTHS = 3.0 / 8.0
THREE_EIGHTHS_LOCAL_X = 2.0 * (THREE_EIGHTHS - LEFT) / WIDTH
ARC_STARTS = np.mod(LEFT + np.arange(4) / 4.0, 1.0)
ARC_NAMES = ["declared", "rotated_1", "rotated_2", "rotated_3"]
PRIMARY_THRESHOLD = 0.01
SENSITIVITY_THRESHOLDS = [0.0, 0.005, 0.01, 0.02, 0.05]
BOOTSTRAP_DRAWS = 5_000
BOOTSTRAP_SEED = 490030
SHUFFLE_DRAWS = 5_000
SHUFFLE_SEED = 490031
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quadrant_labels(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    labels = np.empty(u.shape, dtype=np.int8)
    labels[(u >= 0) & (v >= 0)] = 0
    labels[(u < 0) & (v >= 0)] = 1
    labels[(u < 0) & (v < 0)] = 2
    labels[(u >= 0) & (v < 0)] = 3
    return labels


def coordinates(
    line: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, float, float] | None:
    """Exact Q39 development-calibrated state/change plane."""
    development = np.asarray(line[:250], dtype=np.float64)
    flow = np.diff(development)
    lo, hi = np.quantile(development, [0.05, 0.95])
    centre, radius = (lo + hi) / 2.0, (hi - lo) / 2.0
    scale = float(np.quantile(np.abs(flow), 0.95))
    if not np.isfinite(radius) or not np.isfinite(scale):
        return None
    if radius <= EPS or scale <= EPS:
        return None
    u = (np.asarray(line[:-1], dtype=np.float64) - centre) / radius
    v = np.diff(np.asarray(line, dtype=np.float64)) / scale
    labels = quadrant_labels(u, v)
    dev_plane = u[:249] + 1j * v[:249]
    finite = np.isfinite(dev_plane.real) & np.isfinite(dev_plane.imag)
    if np.mean(finite) < 0.95:
        return None
    valid = dev_plane[finite]
    turns = np.angle(np.conj(valid[:-1]) * valid[1:])
    turns = turns[np.isfinite(turns) & (np.abs(turns) > 1e-10)]
    if not turns.size:
        return None
    signed_turn = float(np.mean(np.sign(turns)))
    direction = 1 if signed_turn >= 0 else -1
    coherence = abs(signed_turn)
    occupancy = min(float(np.mean(labels[:249] == q)) for q in range(4))
    return u, v, labels, direction, coherence, occupancy


def label_runs(labels: np.ndarray) -> list[tuple[int, int, int]]:
    selected = np.asarray(labels, dtype=np.int8)
    output: list[tuple[int, int, int]] = []
    start = 0
    for index in range(1, len(selected) + 1):
        if index == len(selected) or selected[index] != selected[start]:
            output.append((int(selected[start]), start, index - 1))
            start = index
    return output


def circle_fit(
    u: np.ndarray, v: np.ndarray
) -> tuple[np.ndarray, float, float] | None:
    design = np.column_stack((2.0 * u, 2.0 * v, np.ones(u.size)))
    target = u * u + v * v
    solution, _, rank, _ = np.linalg.lstsq(design, target, rcond=None)
    if rank < 3:
        return None
    centre = np.asarray(solution[:2], dtype=np.float64)
    radius_sq = float(solution[2] + np.dot(centre, centre))
    if radius_sq <= EPS or not np.isfinite(radius_sq):
        return None
    radius = math.sqrt(radius_sq)
    radial = np.sqrt((u - centre[0]) ** 2 + (v - centre[1]) ** 2)
    residual = float(np.median(np.abs(radial - radius)) / radius)
    return centre, radius, residual


def extract_centres(
    closure: np.ndarray, pairs: np.ndarray
) -> tuple[list[dict[str, int | float | str]], dict[str, int]]:
    rows: list[dict[str, int | float | str]] = []
    eligible_lineages = 0
    rejected_fits = 0
    for seed in range(closure.shape[0]):
        for pair_index in range(closure.shape[2]):
            coord = coordinates(closure[seed, :, pair_index])
            if coord is None:
                continue
            u, v, labels, direction, coherence, occupancy = coord
            if coherence < 0.80 or occupancy < 0.05:
                continue
            eligible_lineages += 1
            visits = label_runs(labels)
            cycle_index = 0
            index = 0
            while index <= len(visits) - 4:
                window = visits[index : index + 4]
                quadrants = [entry[0] for entry in window]
                lengths = [entry[2] - entry[1] + 1 for entry in window]
                expected = [
                    (quadrants[0] + direction * step) % 4 for step in range(4)
                ]
                if min(lengths) < 2 or quadrants != expected:
                    index += 1
                    continue
                start, end = window[0][1], window[-1][2]
                points_u = np.asarray(u[start : end + 1], dtype=np.float64)
                points_v = np.asarray(v[start : end + 1], dtype=np.float64)
                fit = circle_fit(points_u, points_v)
                if fit is None:
                    rejected_fits += 1
                    index += 4
                    continue
                centre, radius, residual = fit
                centroid = np.asarray(
                    [np.mean(points_u), np.mean(points_v)], dtype=np.float64
                )
                extrema = np.asarray(
                    [
                        (np.min(points_u) + np.max(points_u)) / 2.0,
                        (np.min(points_v) + np.max(points_v)) / 2.0,
                    ],
                    dtype=np.float64,
                )
                a, b = (int(value) for value in pairs[pair_index])
                rows.append(
                    {
                        "centre_id": len(rows),
                        "seed": seed,
                        "pair_index": pair_index,
                        "pair": f"({a}, {b})",
                        "lineage_cycle_index": cycle_index,
                        "start": start,
                        "end": end,
                        "length": end - start + 1,
                        "direction": direction,
                        "development_circulation": coherence,
                        "development_min_quadrant_occupancy": occupancy,
                        "circle_u": float(centre[0]),
                        "circle_v": float(centre[1]),
                        "centroid_u": float(centroid[0]),
                        "centroid_v": float(centroid[1]),
                        "extrema_u": float(extrema[0]),
                        "extrema_v": float(extrema[1]),
                        "radius": radius,
                        "circle_fit_residual": residual,
                    }
                )
                cycle_index += 1
                index += 4
    return rows, {
        "eligible_lineages": eligible_lineages,
        "rejected_circle_fits": rejected_fits,
    }


def heading(vector: np.ndarray) -> float:
    return float((math.atan2(float(vector[1]), float(vector[0])) / (2.0 * math.pi)) % 1.0)


def circular_distance(a: float | np.ndarray, b: float) -> float | np.ndarray:
    delta = np.abs(np.asarray(a) - b)
    return np.minimum(delta, 1.0 - delta)


def in_arc(values: np.ndarray, start: float, width: float = WIDTH) -> np.ndarray:
    return np.mod(values - start, 1.0) <= width


def local_x(values: np.ndarray) -> np.ndarray:
    return 2.0 * np.mod(values - LEFT, 1.0) / WIDTH


def build_events(
    centres: list[dict[str, int | float | str]]
) -> list[dict[str, int | float | str]]:
    grouped: dict[tuple[int, int], list[dict[str, int | float | str]]] = defaultdict(
        list
    )
    for row in centres:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    events: list[dict[str, int | float | str]] = []
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["start"]))
        for index in range(1, len(rows) - 1):
            previous, current, following = rows[index - 1 : index + 2]
            radii = np.asarray(
                [
                    float(previous["radius"]),
                    float(current["radius"]),
                    float(following["radius"]),
                ]
            )
            output: dict[str, int | float | str] = {
                "event_id": len(events),
                "seed": int(current["seed"]),
                "pair_index": int(current["pair_index"]),
                "pair": str(current["pair"]),
                "lineage_cycle_index": int(current["lineage_cycle_index"]),
                "previous_start": int(previous["start"]),
                "current_start": int(current["start"]),
                "current_end": int(current["end"]),
                "following_start": int(following["start"]),
                "radius_mean": float(np.mean(radii)),
                "circle_fit_residual": float(current["circle_fit_residual"]),
            }
            if int(current["end"]) < 250:
                output["stratum"] = "development"
            elif int(current["start"]) >= 250:
                output["stratum"] = "evaluation"
            else:
                output["stratum"] = "transition"
            for estimator in ("circle", "centroid", "extrema"):
                left = np.asarray(
                    [
                        float(previous[f"{estimator}_u"]),
                        float(previous[f"{estimator}_v"]),
                    ]
                )
                right = np.asarray(
                    [
                        float(following[f"{estimator}_u"]),
                        float(following[f"{estimator}_v"]),
                    ]
                )
                vector = right - left
                movement = float(np.linalg.norm(vector) / np.mean(radii))
                angle = heading(vector) if movement > EPS else math.nan
                output[f"{estimator}_du"] = float(vector[0])
                output[f"{estimator}_dv"] = float(vector[1])
                output[f"{estimator}_strength"] = movement
                output[f"{estimator}_heading"] = angle
                output[f"{estimator}_in_declared_arc"] = int(
                    math.isfinite(angle)
                    and bool(in_arc(np.asarray([angle]), LEFT)[0])
                )
                output[f"{estimator}_local_x"] = (
                    float(local_x(np.asarray([angle]))[0])
                    if math.isfinite(angle)
                    and bool(in_arc(np.asarray([angle]), LEFT)[0])
                    else math.nan
                )
            events.append(output)
    return events


def arc_occupancy(
    events: list[dict[str, int | float | str]],
    estimator: str,
    threshold: float,
    stratum: str | None = None,
) -> dict[str, object]:
    selected = [
        row
        for row in events
        if float(row[f"{estimator}_strength"]) >= threshold
        and math.isfinite(float(row[f"{estimator}_heading"]))
        and (stratum is None or str(row["stratum"]) == stratum)
    ]
    headings = np.asarray(
        [float(row[f"{estimator}_heading"]) for row in selected], dtype=np.float64
    )
    counts = [
        int(np.sum(in_arc(headings, float(start)))) for start in ARC_STARTS
    ]
    fractions = [count / headings.size if headings.size else math.nan for count in counts]
    return {
        "events": int(headings.size),
        "counts": dict(zip(ARC_NAMES, counts)),
        "fractions": dict(zip(ARC_NAMES, fractions)),
        "winner": ARC_NAMES[int(np.argmax(counts))] if headings.size else None,
    }


def seed_bootstrap(
    events: list[dict[str, int | float | str]],
    estimator: str = "circle",
    threshold: float = PRIMARY_THRESHOLD,
) -> dict[str, object]:
    by_seed: dict[int, list[list[int]]] = defaultdict(lambda: [[], [], [], []])
    totals: dict[int, int] = defaultdict(int)
    for row in events:
        if float(row[f"{estimator}_strength"]) < threshold:
            continue
        value = float(row[f"{estimator}_heading"])
        if not math.isfinite(value):
            continue
        seed = int(row["seed"])
        totals[seed] += 1
        for index, start in enumerate(ARC_STARTS):
            by_seed[seed][index].append(int(bool(in_arc(np.asarray([value]), float(start))[0])))
    seeds = np.asarray(sorted(totals), dtype=np.int16)
    count_matrix = np.asarray(
        [[sum(by_seed[int(seed)][i]) for i in range(4)] for seed in seeds],
        dtype=np.int32,
    )
    total_vector = np.asarray([totals[int(seed)] for seed in seeds], dtype=np.int32)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    differences = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    wins = np.empty(BOOTSTRAP_DRAWS, dtype=bool)
    for draw in range(BOOTSTRAP_DRAWS):
        chosen = rng.integers(0, seeds.size, size=seeds.size)
        counts = np.sum(count_matrix[chosen], axis=0)
        total = int(np.sum(total_vector[chosen]))
        fractions = counts / total
        difference = float(fractions[0] - np.max(fractions[1:]))
        differences[draw] = difference
        wins[draw] = difference > 0.0
    return {
        "draws": BOOTSTRAP_DRAWS,
        "seed": BOOTSTRAP_SEED,
        "seeds": int(seeds.size),
        "probability_declared_beats_strongest_control": float(np.mean(wins)),
        "declared_minus_strongest_control_median": float(np.median(differences)),
        "ci95": [
            float(np.quantile(differences, 0.025)),
            float(np.quantile(differences, 0.975)),
        ],
    }


def traversal_counts(values: np.ndarray) -> tuple[int, int, int, int]:
    inside = in_arc(values, LEFT)
    x = local_x(values)
    runs = increasing = decreasing = 0
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
            increasing += int(
                any(
                    block[i] <= 0.25 and np.any(block[i + 1 :] >= 1.75)
                    for i in range(block.size - 1)
                )
            )
            decreasing += int(
                any(
                    block[i] >= 1.75 and np.any(block[i + 1 :] <= 0.25)
                    for i in range(block.size - 1)
                )
            )
        start = end
    return runs, increasing, decreasing, increasing + decreasing


def ordered_summary(
    events: list[dict[str, int | float | str]],
    estimator: str = "circle",
    threshold: float = PRIMARY_THRESHOLD,
) -> tuple[dict[str, int], dict[tuple[int, int], np.ndarray]]:
    grouped: dict[tuple[int, int], list[dict[str, int | float | str]]] = defaultdict(
        list
    )
    for row in events:
        if float(row[f"{estimator}_strength"]) >= threshold:
            grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    arrays: dict[tuple[int, int], np.ndarray] = {}
    runs = increasing = decreasing = total = 0
    traversing: set[tuple[int, int]] = set()
    for key, rows in grouped.items():
        rows.sort(key=lambda row: int(row["current_start"]))
        values = np.asarray([float(row[f"{estimator}_heading"]) for row in rows])
        arrays[key] = values
        r, inc, dec, both = traversal_counts(values)
        runs += r
        increasing += inc
        decreasing += dec
        total += both
        if both:
            traversing.add(key)
    return (
        {
            "carrier_runs_length_at_least_3": runs,
            "increasing_full_half_traversals": increasing,
            "decreasing_full_half_traversals": decreasing,
            "full_half_traversals": total,
            "traversing_lineages": len(traversing),
        },
        arrays,
    )


def shuffled_null(arrays: dict[tuple[int, int], np.ndarray]) -> dict[str, object]:
    relevant = {
        key: values
        for key, values in arrays.items()
        if int(np.sum(in_arc(values, LEFT))) >= 3
    }
    totals = np.zeros(SHUFFLE_DRAWS, dtype=np.int32)
    rng = np.random.default_rng(SHUFFLE_SEED)
    for draw in range(SHUFFLE_DRAWS):
        total = 0
        for values in relevant.values():
            _, _, _, traversals = traversal_counts(rng.permutation(values))
            total += traversals
        totals[draw] = total
    return {
        "draws": SHUFFLE_DRAWS,
        "seed": SHUFFLE_SEED,
        "relevant_lineages": len(relevant),
        "mean": float(np.mean(totals)),
        "p95": float(np.quantile(totals, 0.95)),
        "p99": float(np.quantile(totals, 0.99)),
        "max": int(np.max(totals)),
    }


def three_eighths_diagnostic(
    events: list[dict[str, int | float | str]]
) -> dict[str, object]:
    headings = np.asarray(
        [
            float(row["circle_heading"])
            for row in events
            if float(row["circle_strength"]) >= PRIMARY_THRESHOLD
        ]
    )
    centres = np.mod(THREE_EIGHTHS + np.arange(4) / 4.0, 1.0)
    half_width = 0.01
    counts = [
        int(np.sum(circular_distance(headings, float(centre)) <= half_width))
        for centre in centres
    ]
    return {
        "three_eighths": THREE_EIGHTHS,
        "three_eighths_local_x": THREE_EIGHTHS_LOCAL_X,
        "window_half_width_turns": half_width,
        "comparison_centres": centres.tolist(),
        "counts": counts,
        "fractions": [count / headings.size for count in counts],
        "winner_index": int(np.argmax(counts)),
    }


def invariance_checks() -> dict[str, object]:
    theta = 0.731
    rotation = np.asarray(
        [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
    )
    centres = np.asarray([[0.2, -0.4], [0.8, 0.1], [1.7, 0.5]])
    vector = centres[2] - centres[0]
    base = heading(vector)
    translated = heading((centres + np.asarray([9.0, -4.0]))[2] - (centres + np.asarray([9.0, -4.0]))[0])
    rotated = heading((centres @ rotation.T)[2] - (centres @ rotation.T)[0])
    expected_rotated = (base + theta / (2.0 * math.pi)) % 1.0
    return {
        "translation_heading_error": float(circular_distance(base, translated)),
        "rotation_heading_error": float(circular_distance(rotated, expected_rotated)),
        "pass": bool(
            circular_distance(base, translated) <= 1e-12
            and circular_distance(rotated, expected_rotated) <= 1e-12
        ),
    }


def write_csv_gz(
    path: pathlib.Path, rows: list[dict[str, int | float | str]]
) -> None:
    with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(
    centres: list[dict[str, int | float | str]],
    events: list[dict[str, int | float | str]],
    results: dict[str, object],
) -> None:
    if plt is None:
        return
    plt.style.use("seaborn-v0_8-whitegrid")
    eligible = [
        row for row in events if float(row["circle_strength"]) >= PRIMARY_THRESHOLD
    ]
    headings = np.asarray([float(row["circle_heading"]) for row in eligible])

    grouped_centres: dict[tuple[int, int], list[dict[str, int | float | str]]] = defaultdict(list)
    for row in centres:
        grouped_centres[(int(row["seed"]), int(row["pair_index"]))].append(row)
    sample_key = max(
        grouped_centres,
        key=lambda key: max(
            (
                float(row["circle_strength"])
                for row in events
                if int(row["seed"]) == key[0] and int(row["pair_index"]) == key[1]
            ),
            default=0.0,
        ),
    )
    sample = sorted(grouped_centres[sample_key], key=lambda row: int(row["start"]))
    sample_u = np.asarray([float(row["circle_u"]) for row in sample])
    sample_v = np.asarray([float(row["circle_v"]) for row in sample])

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(
        "Q49 — external centreline carrying the complete quantum ARA circle",
        fontsize=18,
        weight="bold",
    )

    ax = axes[0, 0]
    ax.plot(sample_u, sample_v, "-o", ms=3, lw=1.2, color="#4d78a8")
    ax.scatter(sample_u[0], sample_v[0], s=80, color="#2b8a68", label="first centre")
    ax.scatter(sample_u[-1], sample_v[-1], s=80, color="#bd5c4b", label="last centre")
    ax.set(
        xlabel="whole-circle centre u",
        ylabel="whole-circle centre v",
        title=f"Example external centreline: seed {sample_key[0]}, pair {sample_key[1]}",
    )
    ax.axis("equal")
    ax.legend()

    ax = axes[0, 1]
    bins = np.linspace(0.0, 1.0, 73)
    ax.hist(headings, bins=bins, color="#587fa9", alpha=0.86)
    ax.axvspan(LEFT, RIGHT, color="#e1a034", alpha=0.28, label="1/e → full Phi arc")
    ax.axvline(THREE_EIGHTHS, color="#b75d0b", ls="--", lw=2, label="3/8")
    ax.axvline(LEFT, color="#333333", lw=1.5)
    ax.axvline(RIGHT, color="#333333", lw=1.5)
    ax.set(
        xlim=(0, 1),
        xlabel="external centreline heading (full turns)",
        ylabel="eligible tangent events",
        title="Heading distribution — internal rotation removed",
    )
    ax.legend()

    ax = axes[1, 0]
    occupancy = results["primary_occupancy"]["fractions"]
    values = [occupancy[name] for name in ARC_NAMES]
    ax.bar(
        ARC_NAMES,
        values,
        color=["#df9e2e", "#7794ae", "#7794ae", "#7794ae"],
    )
    ax.axhline(WIDTH, color="#333333", ls="--", label="uniform expectation")
    ax.set(
        ylabel="heading fraction inside matched arc",
        title="Declared directional arc versus quarter-turn controls",
    )
    ax.legend()

    ax = axes[1, 1]
    strengths = np.asarray([float(row["circle_strength"]) for row in events])
    all_headings = np.asarray([float(row["circle_heading"]) for row in events])
    ax.scatter(
        all_headings,
        strengths,
        s=5,
        alpha=0.12,
        color="#4d78a8",
        rasterized=True,
    )
    ax.axvspan(LEFT, RIGHT, color="#e1a034", alpha=0.24)
    ax.axhline(PRIMARY_THRESHOLD, color="#333333", ls="--", label="primary movement floor")
    ax.set(
        xlim=(0, 1),
        yscale="log",
        xlabel="external centreline heading (full turns)",
        ylabel="centre movement / circle radius",
        title="Direction versus strength of whole-circle translation",
    )
    ax.legend()

    fig.text(
        0.5,
        0.012,
        (
            f"Directional path: {results['verdicts']['directional_path']} · "
            f"Ordered wobble: {results['verdicts']['ordered_wobble']} · "
            f"n={len(eligible):,} eligible tangents"
        ),
        ha="center",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.96))
    fig.savefig(FIGURE_PATH, dpi=180)
    plt.close(fig)


def main() -> None:
    derived = np.load(DERIVED_PATH)
    centres, extraction = extract_centres(derived["closure"], derived["pairs"])
    events = build_events(centres)

    primary = arc_occupancy(events, "circle", PRIMARY_THRESHOLD)
    bootstrap = seed_bootstrap(events)
    sensitivity: dict[str, object] = {}
    for threshold in SENSITIVITY_THRESHOLDS:
        sensitivity[str(threshold)] = {
            estimator: arc_occupancy(events, estimator, threshold)
            for estimator in ("circle", "centroid", "extrema")
        }
    strata = {
        stratum: arc_occupancy(events, "circle", PRIMARY_THRESHOLD, stratum)
        for stratum in ("development", "transition", "evaluation")
    }
    estimator_primary = {
        estimator: arc_occupancy(events, estimator, PRIMARY_THRESHOLD)
        for estimator in ("circle", "centroid", "extrema")
    }
    ordered, arrays = ordered_summary(events)
    null = shuffled_null(arrays)
    diagnostic = three_eighths_diagnostic(events)
    invariance = invariance_checks()

    g0 = bool(
        invariance["pass"]
        and all(
            0.0 <= float(row["circle_heading"]) < 1.0
            for row in events
            if math.isfinite(float(row["circle_heading"]))
        )
    )
    primary_fractions = primary["fractions"]
    g1 = bool(
        primary["winner"] == "declared"
        and bootstrap["probability_declared_beats_strongest_control"] >= 0.95
    )
    g2 = bool(
        strata["development"]["winner"] == "declared"
        and strata["evaluation"]["winner"] == "declared"
        and all(
            estimator_primary[estimator]["winner"] == "declared"
            for estimator in ("circle", "centroid", "extrema")
        )
    )
    g3 = bool(
        ordered["full_half_traversals"] >= 5
        and ordered["traversing_lineages"] >= 5
        and ordered["increasing_full_half_traversals"] >= 1
        and ordered["decreasing_full_half_traversals"] >= 1
    )
    g4 = bool(
        ordered["full_half_traversals"] >= 5
        and ordered["full_half_traversals"] > null["p99"]
    )
    if not g0:
        directional_verdict = ordered_verdict = "INVALID"
    else:
        directional_verdict = (
            "SUPPORTED" if g1 and g2 else "MIXED" if g1 or g2 else "NOT SUPPORTED"
        )
        ordered_verdict = "SUPPORTED" if g3 and g4 else "NOT SUPPORTED"

    fit_residuals = np.asarray(
        [float(row["circle_fit_residual"]) for row in centres]
    )
    eligible_strengths = np.asarray(
        [
            float(row["circle_strength"])
            for row in events
            if float(row["circle_strength"]) >= PRIMARY_THRESHOLD
        ]
    )
    results: dict[str, object] = {
        "test": "Q49 / T309 external quantum time-vector",
        "construct_fidelity": {
            "status": "EXACT ENOUGH TO TEST",
            "identity": "complete internally rotating circle",
            "measured_axis": "external centreline tangent through time",
            "forbidden_proxy_loaded": False,
        },
        "source": {
            "derived_path": str(DERIVED_PATH),
            "derived_sha256": sha256(DERIVED_PATH),
            "derived_shape": list(derived["closure"].shape),
            "centres": len(centres),
            "tangent_events": len(events),
            **extraction,
        },
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "fidelity_sha256": sha256(FIDELITY_PATH),
        "geometry": {
            "left_one_over_e": LEFT,
            "right_full_phi_mod_one": RIGHT,
            "arc_width_turns": WIDTH,
            "arc_width_degrees": WIDTH * 360.0,
            "matched_arc_starts": ARC_STARTS.tolist(),
            "three_eighths": THREE_EIGHTHS,
            "three_eighths_local_x": THREE_EIGHTHS_LOCAL_X,
        },
        "circle_fit": {
            "median_relative_radial_residual": float(np.median(fit_residuals)),
            "p75_relative_radial_residual": float(np.quantile(fit_residuals, 0.75)),
            "p95_relative_radial_residual": float(np.quantile(fit_residuals, 0.95)),
            "max_relative_radial_residual": float(np.max(fit_residuals)),
        },
        "movement": {
            "primary_threshold_relative_radius": PRIMARY_THRESHOLD,
            "eligible_events": int(eligible_strengths.size),
            "eligible_fraction": float(eligible_strengths.size / len(events)),
            "median_eligible_strength": float(np.median(eligible_strengths)),
            "p95_eligible_strength": float(np.quantile(eligible_strengths, 0.95)),
            "max_eligible_strength": float(np.max(eligible_strengths)),
        },
        "primary_occupancy": primary,
        "seed_cluster_bootstrap": bootstrap,
        "time_strata": strata,
        "estimator_sensitivity_primary_threshold": estimator_primary,
        "threshold_sensitivity": sensitivity,
        "ordered": ordered,
        "shuffled_null": null,
        "three_eighths_diagnostic": diagnostic,
        "invariance": invariance,
        "gates": {
            "G0_correct_object_and_invariance": g0,
            "G1_declared_arc_wins": g1,
            "G2_strata_and_estimators": g2,
            "G3_ordered_traversal": g3,
            "G4_order_beats_shuffle": g4,
        },
        "verdicts": {
            "directional_path": directional_verdict,
            "ordered_wobble": ordered_verdict,
        },
        "boundaries": [
            "Deterministic simulator, not quantum hardware.",
            "Centreline lives in the Q39 two-coordinate state/change plane, not literal physical space.",
            "Circle-centre movement is newly calculated, but the underlying source is opened.",
            "Near-zero centre movements are excluded from the primary heading population.",
            "Matched rotated arcs test directional specificity inside the same coordinate system.",
        ],
    }

    write_csv_gz(CENTRES_PATH, centres)
    write_csv_gz(EVENTS_PATH, events)
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(centres, events, results)
    print(
        json.dumps(
            {
                "verdicts": results["verdicts"],
                "gates": results["gates"],
                "primary_occupancy": primary,
                "bootstrap": bootstrap,
                "ordered": ordered,
                "three_eighths": diagnostic,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
