"""Q48 proxy test.

Construct-invalid for Dylan's intended external time-extrusion vector: this
script measures internal parent-to-parent turning amount. Retained for
provenance and reproducibility only.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import pathlib
from collections import Counter, defaultdict

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q39_information3_strongmax"
CONNECTED_PATH = DATA / "q39_connected_cache.npy"
DERIVED_PATH = DATA / "q39_derived_cache.npz"
Q39_CYCLES_PATH = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_CYCLES.csv.gz"
Q47_EVENTS_PATH = HERE / "Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_EVENTS.csv.gz"
PROTOCOL_PATH = HERE / "Q48_E_PHI_CARRIER_WOBBLE_PROTOCOL_v1_FROZEN.md"
RESULTS_PATH = HERE / "Q48_E_PHI_CARRIER_WOBBLE_RESULTS.json"
EVENTS_PATH = HERE / "Q48_E_PHI_CARRIER_WOBBLE_EVENTS.csv.gz"
FIGURE_PATH = HERE / "Q48_E_PHI_CARRIER_WOBBLE.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LEFT = 1.0 / math.e
RIGHT = 2.0 - PHI
MIDPOINT = (LEFT + RIGHT) / 2.0
THREE_EIGHTHS = 3.0 / 8.0
THREE_EIGHTHS_X = 2.0 * (THREE_EIGHTHS - LEFT) / (RIGHT - LEFT)
REVERSAL_LEVELS = np.asarray([0.0, 1 / 8, 1 / 4, 3 / 8, 1 / 2])
REVERSAL_LABELS = ["0", "1/8", "1/4", "3/8", "1/2"]
EPS = 1e-12
NULL_DRAWS = 5_000
NULL_SEED = 480030


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
    """Exact Q39 ARA coordinate, including its frozen development calibration."""
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
    valid_plane = dev_plane[finite]
    turn = np.angle(np.conj(valid_plane[:-1]) * valid_plane[1:])
    turn = turn[np.isfinite(turn) & (np.abs(turn) > 1e-10)]
    if not turn.size:
        return None
    signed_turn = float(np.mean(np.sign(turn)))
    direction = 1 if signed_turn >= 0 else -1
    coherence = abs(signed_turn)
    occupancy = min(float(np.mean(labels[:249] == q)) for q in range(4))
    return u, v, labels, direction, coherence, occupancy


def label_runs(
    labels: np.ndarray, first: int = 0, last: int = 498
) -> list[tuple[int, int, int]]:
    selected = np.asarray(labels[first : last + 1], dtype=np.int8)
    output: list[tuple[int, int, int]] = []
    start = 0
    for index in range(1, len(selected) + 1):
        if index == len(selected) or selected[index] != selected[start]:
            output.append((int(selected[start]), first + start, first + index - 1))
            start = index
    return output


def extract_all_cycles(
    closure: np.ndarray, pairs: np.ndarray
) -> tuple[list[dict[str, int | float | str]], dict[str, int]]:
    cycles: list[dict[str, int | float | str]] = []
    eligible = 0
    for seed in range(closure.shape[0]):
        for pair_index in range(closure.shape[2]):
            coord = coordinates(closure[seed, :, pair_index])
            if coord is None:
                continue
            _, _, labels, direction, coherence, occupancy = coord
            if coherence < 0.80 or occupancy < 0.05:
                continue
            eligible += 1
            visits = label_runs(labels)
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
                a, b = (int(value) for value in pairs[pair_index])
                row: dict[str, int | float | str] = {
                    "cycle_id": len(cycles),
                    "seed": seed,
                    "pair_index": pair_index,
                    "pair": f"({a}, {b})",
                    "direction": direction,
                    "development_circulation": coherence,
                    "development_min_quadrant_occupancy": occupancy,
                }
                for quadrant, (_, start, end) in enumerate(window, 1):
                    row[f"q{quadrant}_start"] = start
                    row[f"q{quadrant}_end"] = end
                    row[f"q{quadrant}_length"] = end - start + 1
                cycles.append(row)
                index += 4
    return cycles, {"eligible_lineages": eligible}


def mean_state(
    connected: np.ndarray, row: dict[str, object], quadrant: int
) -> tuple[np.ndarray, float]:
    seed = int(row["seed"])
    pair = int(row["pair_index"])
    start = int(row[f"q{quadrant}_start"])
    end = int(row[f"q{quadrant}_end"])
    matrix = np.mean(
        connected[seed, start : end + 1, pair],
        axis=0,
        dtype=np.float64,
    )
    magnitude = float(np.linalg.norm(matrix))
    return matrix, magnitude


def meta_distance(
    left: np.ndarray, left_norm: float, right: np.ndarray, right_norm: float
) -> float:
    if left_norm <= EPS or right_norm <= EPS:
        return math.nan
    cosine = float(np.sum(left * right) / (left_norm * right_norm))
    return float(math.acos(float(np.clip(cosine, -1.0, 1.0))) / (2.0 * math.pi))


def event_row(
    connected: np.ndarray,
    first: dict[str, object],
    second: dict[str, object],
) -> dict[str, int | float | str] | None:
    distances: list[float] = []
    magnitudes: list[float] = []
    for quadrant in range(1, 5):
        left, left_norm = mean_state(connected, first, quadrant)
        right, right_norm = mean_state(connected, second, quadrant)
        distance = meta_distance(left, left_norm, right, right_norm)
        if not math.isfinite(distance):
            return None
        distances.append(distance)
        magnitudes.extend((left_norm, right_norm))
    movement = float(np.mean(distances))
    local_x = 2.0 * (movement - LEFT) / (RIGHT - LEFT)
    source_start = int(first["q1_start"])
    target_start = int(second["q1_start"])
    target_end = int(second["q4_end"])
    if target_end < 250:
        stratum = "development"
    elif source_start <= 251:
        stratum = "evaluation_opening"
    else:
        stratum = "evaluation_later"
    nearest_index = int(np.argmin(np.abs(REVERSAL_LEVELS - movement)))
    return {
        "seed": int(first["seed"]),
        "pair_index": int(first["pair_index"]),
        "pair": str(first["pair"]),
        "source_cycle_id": int(first["cycle_id"]),
        "target_cycle_id": int(second["cycle_id"]),
        "source_start": source_start,
        "target_start": target_start,
        "stratum": stratum,
        "delta_q1": distances[0],
        "delta_q2": distances[1],
        "delta_q3": distances[2],
        "delta_q4": distances[3],
        "delta_mean": movement,
        "local_x": local_x,
        "in_carrier": int(LEFT <= movement <= RIGHT),
        "nearest_reversal_level": REVERSAL_LABELS[nearest_index],
        "nearest_reversal_error": float(
            abs(movement - REVERSAL_LEVELS[nearest_index])
        ),
        "magnitude_mean": float(np.mean(magnitudes)),
        "magnitude_min": float(np.min(magnitudes)),
    }


def build_events(
    connected: np.ndarray, cycles: list[dict[str, object]]
) -> list[dict[str, int | float | str]]:
    grouped: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in cycles:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    events: list[dict[str, int | float | str]] = []
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["q1_start"]))
        for first, second in zip(rows[:-1], rows[1:]):
            result = event_row(connected, first, second)
            if result is not None:
                events.append(result)
    return events


def read_q39_cycles() -> list[dict[str, object]]:
    with gzip.open(Q39_CYCLES_PATH, "rt", newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def read_q47_events() -> list[dict[str, str]]:
    with gzip.open(Q47_EVENTS_PATH, "rt", newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def carrier_runs(
    values: np.ndarray,
) -> tuple[int, int, int, int, list[dict[str, object]]]:
    inside = (values >= LEFT) & (values <= RIGHT)
    run_count = 0
    increasing = 0
    decreasing = 0
    ridge_crossings = 0
    details: list[dict[str, object]] = []
    start = 0
    while start < values.size:
        if not inside[start]:
            start += 1
            continue
        end = start + 1
        while end < values.size and inside[end]:
            end += 1
        block = values[start:end]
        if block.size >= 3:
            run_count += 1
            x = 2.0 * (block - LEFT) / (RIGHT - LEFT)
            inc = any(
                x[i] <= 0.25 and np.any(x[i + 1 :] >= 1.75)
                for i in range(x.size - 1)
            )
            dec = any(
                x[i] >= 1.75 and np.any(x[i + 1 :] <= 0.25)
                for i in range(x.size - 1)
            )
            increasing += int(inc)
            decreasing += int(dec)
            crossings = int(
                np.sum(((x[:-1] - 1.0) * (x[1:] - 1.0) <= 0.0))
            )
            ridge_crossings += crossings
            details.append(
                {
                    "start_index": start,
                    "end_index": end - 1,
                    "length": int(block.size),
                    "min_x": float(np.min(x)),
                    "max_x": float(np.max(x)),
                    "increasing_full_half": bool(inc),
                    "decreasing_full_half": bool(dec),
                    "ridge_crossings": crossings,
                }
            )
        start = end
    return run_count, increasing, decreasing, ridge_crossings, details


def ordered_summary(
    events: list[dict[str, int | float | str]]
) -> tuple[dict[str, object], dict[tuple[int, int], np.ndarray]]:
    grouped: dict[tuple[int, int], list[dict[str, int | float | str]]] = defaultdict(
        list
    )
    for row in events:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    arrays: dict[tuple[int, int], np.ndarray] = {}
    details: list[dict[str, object]] = []
    runs = increasing = decreasing = crossings = 0
    traversing_lineages: set[tuple[int, int]] = set()
    for key, rows in grouped.items():
        rows.sort(key=lambda row: int(row["source_start"]))
        values = np.asarray([float(row["delta_mean"]) for row in rows])
        arrays[key] = values
        r, inc, dec, cross, found = carrier_runs(values)
        runs += r
        increasing += inc
        decreasing += dec
        crossings += cross
        if inc or dec:
            traversing_lineages.add(key)
        for item in found:
            item.update({"seed": key[0], "pair_index": key[1]})
            details.append(item)
    return (
        {
            "carrier_runs_length_at_least_3": runs,
            "increasing_full_half_traversals": increasing,
            "decreasing_full_half_traversals": decreasing,
            "full_half_traversals": increasing + decreasing,
            "traversing_lineages": len(traversing_lineages),
            "ridge_crossings_inside_runs": crossings,
            "run_details": details,
        },
        arrays,
    )


def shuffled_null(
    arrays: dict[tuple[int, int], np.ndarray],
) -> dict[str, object]:
    relevant = {
        key: values
        for key, values in arrays.items()
        if np.sum((values >= LEFT) & (values <= RIGHT)) >= 3
    }
    totals = np.zeros(NULL_DRAWS, dtype=np.int32)
    if relevant:
        rng = np.random.default_rng(NULL_SEED)
        for draw in range(NULL_DRAWS):
            total = 0
            for values in relevant.values():
                shuffled = rng.permutation(values)
                _, increasing, decreasing, _, _ = carrier_runs(shuffled)
                total += increasing + decreasing
            totals[draw] = total
    return {
        "draws": NULL_DRAWS,
        "seed": NULL_SEED,
        "lineages_capable_of_length3_carrier_run": len(relevant),
        "mean": float(np.mean(totals)),
        "p95": float(np.quantile(totals, 0.95)),
        "p99": float(np.quantile(totals, 0.99)),
        "max": int(np.max(totals)),
        "nonzero_fraction": float(np.mean(totals > 0)),
    }


def summary(values: np.ndarray) -> dict[str, float | int]:
    return {
        "count": int(values.size),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p25": float(np.quantile(values, 0.25)),
        "p75": float(np.quantile(values, 0.75)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }


def write_events(events: list[dict[str, int | float | str]]) -> None:
    with gzip.open(EVENTS_PATH, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(events[0]))
        writer.writeheader()
        writer.writerows(events)


def make_figure(
    events: list[dict[str, int | float | str]], results: dict[str, object]
) -> None:
    if plt is None:
        return
    plt.style.use("seaborn-v0_8-whitegrid")
    values = np.asarray([float(row["delta_mean"]) for row in events])
    starts = np.asarray([int(row["source_start"]) for row in events])
    in_carrier = (values >= LEFT) & (values <= RIGHT)
    high = values >= 0.05

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(
        "Q48 — quantum parent movement versus the 1/e ↔ anti-Phi carrier",
        fontsize=18,
        weight="bold",
    )

    ax = axes[0, 0]
    ax.scatter(starts, values, s=5, alpha=0.13, color="#426eaa", rasterized=True)
    ax.axhspan(LEFT, RIGHT, color="#efad3c", alpha=0.28, label="proposed carrier")
    ax.axhline(THREE_EIGHTHS, color="#b45f06", lw=1.8, ls="--", label="3/8")
    ax.set(
        xlabel="source time slice",
        ylabel="complete-parent movement (turns)",
        title="All extracted parent-to-parent events",
    )
    ax.legend()

    ax = axes[0, 1]
    high_values = values[high]
    if high_values.size:
        ax.hist(high_values, bins=np.linspace(0.05, 0.5, 46), color="#638db9")
    for value, label in zip(REVERSAL_LEVELS[1:], REVERSAL_LABELS[1:]):
        ax.axvline(value, color="#333333", lw=1.2, ls="--")
        ax.text(value, ax.get_ylim()[1] * 0.91, label, rotation=90, ha="right")
    ax.axvspan(LEFT, RIGHT, color="#efad3c", alpha=0.28)
    ax.set(
        xlabel="movement (turns)",
        ylabel="events",
        title="Sparse transition tail and four-strand closure levels",
    )

    ax = axes[1, 0]
    carrier_rows = [row for row in events if int(row["in_carrier"]) == 1]
    if carrier_rows:
        x = np.asarray([float(row["local_x"]) for row in carrier_rows])
        y = np.arange(1, len(carrier_rows) + 1)
        ax.scatter(x, y, s=45, color="#7b4fa3")
    ax.axvline(0, color="#333333", lw=1.2)
    ax.axvline(1, color="#2a8c67", lw=2, label="exact local ridge")
    ax.axvline(
        THREE_EIGHTHS_X, color="#b45f06", lw=1.7, ls="--", label="3/8"
    )
    ax.axvline(2, color="#333333", lw=1.2)
    ax.set(
        xlim=(-0.1, 2.1),
        xlabel="local carrier ARA: 1/e = 0, anti-Phi = 2",
        ylabel="carrier event index",
        title=f"Observed carrier occupants (n={len(carrier_rows)})",
    )
    ax.legend()

    ax = axes[1, 1]
    counts = results["descriptive_reversal_levels"]["counts"]
    ax.bar(
        REVERSAL_LABELS,
        [counts[label] for label in REVERSAL_LABELS],
        color=["#9aabba", "#6e93b5", "#5c82a7", "#d99b34", "#47596a"],
    )
    ax.set(
        xlabel="nearest ideal k/8 four-strand level",
        ylabel="events",
        title="All events: discrete closure-state comparison",
    )
    ax.set_yscale("symlog", linthresh=1)

    note = (
        f"Carrier events: {results['carrier']['events']} · "
        f"ordered full half-traversals: "
        f"{results['ordered']['full_half_traversals']} · "
        f"verdict: {results['verdict']}"
    )
    fig.text(0.5, 0.012, note, ha="center", fontsize=11)
    fig.tight_layout(rect=(0, 0.035, 1, 0.96))
    fig.savefig(FIGURE_PATH, dpi=180)
    plt.close(fig)


def main() -> None:
    connected = np.load(CONNECTED_PATH, mmap_mode="r")
    derived = np.load(DERIVED_PATH)
    closure = derived["closure"]
    pairs = derived["pairs"]

    # G0: independently rebuild the frozen Q47 evaluation-only events.
    frozen_cycles = read_q39_cycles()
    reproduced_q47 = build_events(connected, frozen_cycles)
    saved_q47 = read_q47_events()
    reproduced_q47_max = max(float(row["delta_mean"]) for row in reproduced_q47)
    saved_q47_max = max(float(row["delta_mean"]) for row in saved_q47)

    all_cycles, extraction = extract_all_cycles(closure, pairs)
    events = build_events(connected, all_cycles)
    values = np.asarray([float(row["delta_mean"]) for row in events])
    carrier = [row for row in events if int(row["in_carrier"]) == 1]
    carrier_values = np.asarray(
        [float(row["delta_mean"]) for row in carrier], dtype=np.float64
    )
    carrier_x = np.asarray(
        [float(row["local_x"]) for row in carrier], dtype=np.float64
    )
    carrier_seeds = {int(row["seed"]) for row in carrier}
    carrier_lineages = {
        (int(row["seed"]), int(row["pair_index"])) for row in carrier
    }
    ordered, lineage_arrays = ordered_summary(events)
    null = shuffled_null(lineage_arrays)

    g0 = bool(
        len(reproduced_q47) == len(saved_q47)
        and abs(reproduced_q47_max - saved_q47_max) <= 1e-9
        and np.all((values >= 0.0) & (values <= 0.5))
    )
    g1 = bool(
        len(carrier) >= 20
        and len(carrier_lineages) >= 10
        and len(carrier_seeds) >= 10
    )
    g2 = bool(
        int(ordered["full_half_traversals"]) >= 5
        and int(ordered["traversing_lineages"]) >= 5
        and int(ordered["increasing_full_half_traversals"]) >= 1
        and int(ordered["decreasing_full_half_traversals"]) >= 1
    )
    g3 = bool(
        int(ordered["full_half_traversals"]) >= 5
        and float(ordered["full_half_traversals"]) > float(null["p99"])
    )
    if carrier_x.size:
        near_three_eighths = float(
            np.mean(np.abs(carrier_x - THREE_EIGHTHS_X) <= 0.10)
        )
        carrier_median_x = float(np.median(carrier_x))
    else:
        near_three_eighths = 0.0
        carrier_median_x = math.nan
    g4 = bool(
        carrier_x.size > 0
        and near_three_eighths >= 0.20
        and abs(carrier_median_x - 1.0) <= 0.20
    )

    substantive = sum((g1, g2, g3, g4))
    if not g0:
        verdict = "INVALID"
    elif substantive == 4:
        verdict = "SUPPORTED"
    elif substantive >= 2:
        verdict = "MIXED"
    else:
        verdict = "NOT SUPPORTED"

    level_counts = Counter(str(row["nearest_reversal_level"]) for row in events)
    high_rows = [row for row in events if float(row["delta_mean"]) >= 0.05]
    high_level_counts = Counter(
        str(row["nearest_reversal_level"]) for row in high_rows
    )
    strongest = sorted(events, key=lambda row: float(row["delta_mean"]), reverse=True)[
        :25
    ]
    strata: dict[str, object] = {}
    for name in ("development", "evaluation_opening", "evaluation_later"):
        subset = np.asarray(
            [
                float(row["delta_mean"])
                for row in events
                if str(row["stratum"]) == name
            ]
        )
        strata[name] = summary(subset) if subset.size else {"count": 0}

    results: dict[str, object] = {
        "test": "Q48 / T308 e-to-anti-Phi quantum carrier wobble",
        "construct_fidelity": {
            "status": "PROXY TEST - CONSTRUCT INVALID FOR THE INTENDED CLAIM",
            "proxy_measured": "internal parent-to-parent turning amount",
            "intended_object": (
                "external/meta vector carrying the complete rotating circle "
                "forward through time"
            ),
            "ara_claim_verdict": "UNTESTED",
        },
        "status": "retrospective opened deterministic simulator",
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "source": {
            "connected_sha256": sha256(CONNECTED_PATH),
            "derived_sha256": sha256(DERIVED_PATH),
            "connected_shape": list(connected.shape),
            "connected_dtype": str(connected.dtype),
            "cycles_extracted_full_range": len(all_cycles),
            "events_full_range": len(events),
            **extraction,
        },
        "geometry": {
            "left_one_over_e": LEFT,
            "right_anti_phi": RIGHT,
            "interval_width": RIGHT - LEFT,
            "exact_midpoint": MIDPOINT,
            "three_eighths": THREE_EIGHTHS,
            "three_eighths_local_x": THREE_EIGHTHS_X,
            "three_eighths_minus_midpoint": THREE_EIGHTHS - MIDPOINT,
        },
        "g0_reproduction": {
            "pass": g0,
            "q47_saved_events": len(saved_q47),
            "q47_reproduced_events": len(reproduced_q47),
            "q47_saved_max": saved_q47_max,
            "q47_reproduced_max": reproduced_q47_max,
            "max_absolute_difference": abs(reproduced_q47_max - saved_q47_max),
            "all_movements_in_0_to_half_turn": bool(
                np.all((values >= 0.0) & (values <= 0.5))
            ),
        },
        "all_events": summary(values),
        "strata": strata,
        "carrier": {
            "events": len(carrier),
            "fraction_all_events": len(carrier) / len(events),
            "seeds": len(carrier_seeds),
            "lineages": len(carrier_lineages),
            "movement_summary": (
                summary(carrier_values) if carrier_values.size else {"count": 0}
            ),
            "local_x_summary": (
                summary(carrier_x) if carrier_x.size else {"count": 0}
            ),
            "near_three_eighths_local_0_10_fraction": near_three_eighths,
            "median_local_x": carrier_median_x,
            "rows": carrier,
        },
        "ordered": ordered,
        "shuffled_null": null,
        "descriptive_reversal_levels": {
            "levels": dict(zip(REVERSAL_LABELS, REVERSAL_LEVELS.tolist())),
            "counts": {
                label: int(level_counts.get(label, 0)) for label in REVERSAL_LABELS
            },
            "high_event_threshold": 0.05,
            "high_event_count": len(high_rows),
            "high_event_counts": {
                label: int(high_level_counts.get(label, 0))
                for label in REVERSAL_LABELS
            },
        },
        "strongest_events": strongest,
        "gates": {
            "G0_reproduction_and_geometry": g0,
            "G1_carrier_occupancy": g1,
            "G2_ordered_traversal": g2,
            "G3_order_beats_shuffle": g3,
            "G4_three_eighths_empirical_ridge": g4,
            "substantive_passes": substantive,
        },
        "verdict": verdict,
        "boundaries": [
            "The source is a deterministic simulator, not quantum hardware.",
            "The source and Q47 evaluation result were already open.",
            "Q48 newly opens the development-half parent movement.",
            "The observable is a movement amount, not an absolute spatial heading.",
            "The matrices are exactly diagonal, so general off-axis transport is absent.",
        ],
    }

    write_events(events)
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(events, results)
    print(json.dumps({"verdict": verdict, "gates": results["gates"]}, indent=2))
    print(
        json.dumps(
            {
                "cycles": len(all_cycles),
                "events": len(events),
                "carrier": results["carrier"],
                "ordered": ordered,
                "null": null,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
