"""Q47 retrospective whole-lattice ARA9 meta-movement test."""

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
CONNECTED_PATH = DATA / "q39_connected_cache.npy"
CYCLES_PATH = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_CYCLES.csv.gz"
PROTOCOL_PATH = HERE / "Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_PROTOCOL_v1_FROZEN.md"
RESULTS_PATH = HERE / "Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_RESULTS.json"
EVENTS_PATH = HERE / "Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_EVENTS.csv.gz"
FIGURE_PATH = HERE / "Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT.png"

PHI_LOW = (3.0 - math.sqrt(5.0)) / 2.0
CANDIDATES = {
    "recurrence": 0.0,
    "eighth": 1.0 / 8.0,
    "quarter": 1.0 / 4.0,
    "third": 1.0 / 3.0,
    "three_eighths": 3.0 / 8.0,
    "phi_inverse_square": PHI_LOW,
    "two_fifths": 2.0 / 5.0,
    "sqrt2_minus_1": math.sqrt(2.0) - 1.0,
    "opposition": 1.0 / 2.0,
}
BOOTSTRAP_DRAWS = 5_000
BOOTSTRAP_SEED = 470030
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_cycles() -> list[dict[str, str]]:
    with gzip.open(CYCLES_PATH, "rt", newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def mean_state(
    connected: np.ndarray, row: dict[str, str], quadrant: int
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
    cosine = float(np.clip(cosine, -1.0, 1.0))
    return float(math.acos(cosine) / (2.0 * math.pi))


def event_row(
    connected: np.ndarray,
    first: dict[str, str],
    second: dict[str, str],
    lag: int,
) -> dict[str, float | int | str] | None:
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
    return {
        "seed": int(first["seed"]),
        "pair_index": int(first["pair_index"]),
        "pair": first["pair"],
        "source_cycle_id": int(first["cycle_id"]),
        "target_cycle_id": int(second["cycle_id"]),
        "source_start": int(first["q1_start"]),
        "target_start": int(second["q1_start"]),
        "cycle_lag": lag,
        "delta_q1": distances[0],
        "delta_q2": distances[1],
        "delta_q3": distances[2],
        "delta_q4": distances[3],
        "delta_mean": float(np.mean(distances)),
        "magnitude_mean": float(np.mean(magnitudes)),
        "magnitude_min": float(np.min(magnitudes)),
    }


def build_events(
    connected: np.ndarray, cycles: list[dict[str, str]], lag: int
) -> list[dict[str, float | int | str]]:
    grouped: dict[tuple[int, int], list[dict[str, str]]] = defaultdict(list)
    for row in cycles:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    events: list[dict[str, float | int | str]] = []
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row["q1_start"]))
        for index in range(len(rows) - lag):
            result = event_row(connected, rows[index], rows[index + lag], lag)
            if result is not None:
                events.append(result)
    return events


def candidate_scores(values: np.ndarray) -> dict[str, float]:
    return {
        name: float(np.median(np.abs(values - value)))
        for name, value in CANDIDATES.items()
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


def seed_cluster_bootstrap(events: list[dict[str, float | int | str]]) -> dict[str, object]:
    indices_by_seed: dict[int, np.ndarray] = {}
    event_seeds = np.array([int(row["seed"]) for row in events], dtype=np.int16)
    values = np.array([float(row["delta_mean"]) for row in events], dtype=np.float64)
    seeds = np.unique(event_seeds)
    for seed in seeds:
        indices_by_seed[int(seed)] = np.flatnonzero(event_seeds == seed)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    differences = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for draw in range(BOOTSTRAP_DRAWS):
        sampled = rng.choice(seeds, size=seeds.size, replace=True)
        chosen = np.concatenate([indices_by_seed[int(seed)] for seed in sampled])
        sample = values[chosen]
        phi_error = np.median(np.abs(sample - PHI_LOW))
        three_eighths_error = np.median(np.abs(sample - 3.0 / 8.0))
        differences[draw] = phi_error - three_eighths_error
    return {
        "draws": BOOTSTRAP_DRAWS,
        "seeds": int(seeds.size),
        "phi_minus_three_eighths_median": float(np.median(differences)),
        "ci95": [
            float(np.quantile(differences, 0.025)),
            float(np.quantile(differences, 0.975)),
        ],
        "probability_phi_better": float(np.mean(differences < 0.0)),
    }


def magnitude_quartiles(
    values: np.ndarray, magnitudes: np.ndarray
) -> list[dict[str, object]]:
    edges = np.quantile(magnitudes, [0.0, 0.25, 0.5, 0.75, 1.0])
    output: list[dict[str, object]] = []
    for index in range(4):
        if index < 3:
            mask = (magnitudes >= edges[index]) & (magnitudes < edges[index + 1])
        else:
            mask = (magnitudes >= edges[index]) & (magnitudes <= edges[index + 1])
        subset = values[mask]
        scores = candidate_scores(subset)
        output.append(
            {
                "quartile": index + 1,
                "lower": float(edges[index]),
                "upper": float(edges[index + 1]),
                "events": int(subset.size),
                "delta": summary(subset),
                "winner": min(scores, key=scores.get),
                "candidate_errors": scores,
            }
        )
    return output


def write_events(events: list[dict[str, float | int | str]]) -> None:
    fieldnames = list(events[0])
    with gzip.open(EVENTS_PATH, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)


def make_figure(
    values: np.ndarray,
    scores: dict[str, float],
    quadrant_scores: dict[str, dict[str, float]],
    magnitudes: np.ndarray,
) -> None:
    if plt is None:
        return
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("Q47 — ARA⁹ whole-lattice meta movement", fontsize=18, weight="bold")

    ax = axes[0, 0]
    ax.hist(values, bins=70, color="#537fb3", alpha=0.85)
    for name, color in (
        ("three_eighths", "#d28a20"),
        ("phi_inverse_square", "#8e5ab5"),
        ("quarter", "#5a9d62"),
        ("opposition", "#333333"),
    ):
        ax.axvline(CANDIDATES[name], color=color, lw=2, label=name.replace("_", " "))
    ax.set(xlabel="whole-lattice same-phase advance (turns)", ylabel="events")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ordered = sorted(scores, key=scores.get)
    ax.barh(
        [name.replace("_", " ") for name in ordered],
        [scores[name] for name in ordered],
        color=["#8e5ab5" if name == "phi_inverse_square" else "#8aa2b8" for name in ordered],
    )
    ax.invert_yaxis()
    ax.set(xlabel="median absolute error (lower is better)", title="Fixed-candidate comparison")

    ax = axes[1, 0]
    quadrants = [f"q{index}" for index in range(1, 5)]
    x = np.arange(4)
    width = 0.36
    ax.bar(
        x - width / 2,
        [quadrant_scores[q]["three_eighths"] for q in quadrants],
        width,
        label="3/8",
        color="#d28a20",
    )
    ax.bar(
        x + width / 2,
        [quadrant_scores[q]["phi_inverse_square"] for q in quadrants],
        width,
        label="Phi^-2",
        color="#8e5ab5",
    )
    ax.set_xticks(x, quadrants)
    ax.set(ylabel="median absolute error", title="Same internal phase across parent cycles")
    ax.legend()

    ax = axes[1, 1]
    hb = ax.hexbin(magnitudes, values, gridsize=55, mincnt=1, cmap="Blues")
    ax.axhline(PHI_LOW, color="#8e5ab5", lw=2, label="Phi^-2")
    ax.axhline(3.0 / 8.0, color="#d28a20", lw=2, label="3/8")
    ax.set(
        xlabel="mean whole-lattice Frobenius magnitude",
        ylabel="meta advance (turns)",
        title="Movement versus connection magnitude",
    )
    ax.legend()
    fig.colorbar(hb, ax=ax, label="event count")

    fig.text(
        0.01,
        0.01,
        "Source: Q39 public pure_strongmax simulator; complete 3×3 connected matrices, not cell counts.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(FIGURE_PATH, dpi=180)
    plt.close(fig)


def main() -> None:
    connected = np.load(CONNECTED_PATH, mmap_mode="r")
    cycles = read_cycles()
    events = build_events(connected, cycles, lag=1)
    lag2_events = build_events(connected, cycles, lag=2)
    if not events:
        raise RuntimeError("No Q47 events were produced")

    values = np.array([float(row["delta_mean"]) for row in events])
    magnitudes = np.array([float(row["magnitude_mean"]) for row in events])
    scores = candidate_scores(values)
    winner = min(scores, key=scores.get)
    quadrant_scores = {
        f"q{quadrant}": candidate_scores(
            np.array([float(row[f"delta_q{quadrant}"]) for row in events])
        )
        for quadrant in range(1, 5)
    }
    quadrant_summaries = {
        f"q{quadrant}": summary(
            np.array([float(row[f"delta_q{quadrant}"]) for row in events])
        )
        for quadrant in range(1, 5)
    }
    bootstrap = seed_cluster_bootstrap(events)
    gate_p1 = winner == "phi_inverse_square"
    gate_p2 = bootstrap["probability_phi_better"] >= 0.95
    gate_p3 = all(
        quadrant_scores[f"q{quadrant}"]["phi_inverse_square"]
        < quadrant_scores[f"q{quadrant}"]["three_eighths"]
        for quadrant in range(1, 5)
    )
    gates_passed = int(gate_p1) + int(gate_p2) + int(gate_p3)
    if gates_passed == 3:
        verdict = "SUPPORTED IN OPENED SIMULATOR"
    elif gates_passed == 2:
        verdict = "MIXED / SUGGESTIVE"
    else:
        verdict = "NOT SUPPORTED"

    lag2_values = np.array([float(row["delta_mean"]) for row in lag2_events])
    results = {
        "test_id": "Q47-ARA9-WHOLE-LATTICE-META-MOVEMENT-v1",
        "date": "2026-07-30",
        "status": "retrospective opened-source test",
        "verdict": verdict,
        "gates": {
            "P1_phi_unique_pooled_winner": bool(gate_p1),
            "P2_bootstrap_phi_beats_three_eighths_95pct": bool(gate_p2),
            "P3_phi_beats_three_eighths_all_quadrants": bool(gate_p3),
            "passed": gates_passed,
            "total": 3,
        },
        "source": {
            "cycles_path": str(CYCLES_PATH),
            "cycles_sha256": sha256(CYCLES_PATH),
            "connected_path": str(CONNECTED_PATH),
            "connected_sha256": sha256(CONNECTED_PATH),
            "connected_shape": list(connected.shape),
            "connected_dtype": str(connected.dtype),
            "protocol_path": str(PROTOCOL_PATH),
            "protocol_sha256": sha256(PROTOCOL_PATH),
        },
        "population": {
            "q39_cycles": len(cycles),
            "adjacent_events": len(events),
            "lag2_events": len(lag2_events),
            "seeds": len({int(row["seed"]) for row in events}),
            "lineages": len(
                {(int(row["seed"]), int(row["pair_index"])) for row in events}
            ),
        },
        "meta_step": summary(values),
        "candidate_values": CANDIDATES,
        "candidate_errors": scores,
        "winner": winner,
        "phi_minus_three_eighths_error": (
            scores["phi_inverse_square"] - scores["three_eighths"]
        ),
        "quadrant_summaries": quadrant_summaries,
        "quadrant_candidate_errors": quadrant_scores,
        "seed_cluster_bootstrap": bootstrap,
        "magnitude": summary(magnitudes),
        "magnitude_quartiles": magnitude_quartiles(values, magnitudes),
        "lag2_control": {
            "meta_step": summary(lag2_values),
            "candidate_errors": candidate_scores(lag2_values),
            "winner": min(candidate_scores(lag2_values), key=candidate_scores(lag2_values).get),
        },
        "boundaries": [
            "The source is a deterministic simulator, not quantum hardware.",
            "The source was already open before Q47.",
            "All connected matrices are exactly diagonal, so general off-axis transport is not tested.",
            "The geodesic is the shortest whole-state orientation distance and does not recover winding beyond half a turn.",
            "A fixed-value match would locate a descriptive meta-step, not establish a universal constant.",
        ],
        "artifacts": {
            "events": str(EVENTS_PATH),
            "figure": str(FIGURE_PATH) if plt is not None else None,
        },
    }
    write_events(events)
    make_figure(values, scores, quadrant_scores, magnitudes)
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
