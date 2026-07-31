"""Independent validator and post-result diagnostics for Q49.

This script does not import the primary Q49 implementation. It reconstructs
the external centreline tangents from the saved per-cycle centres, checks a
deterministic sample of circle centres against the immutable Q39 source, and
recalculates the headline occupancies and seed-cluster bootstrap.
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


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS_PATH = ROOT / "Q49_EXTERNAL_TIME_VECTOR_RESULTS.json"
CENTRES_PATH = ROOT / "Q49_EXTERNAL_TIME_VECTOR_CENTRES.csv.gz"
EVENTS_PATH = ROOT / "Q49_EXTERNAL_TIME_VECTOR_EVENTS.csv.gz"
VALIDATION_PATH = ROOT / "Q49_EXTERNAL_TIME_VECTOR_VALIDATION.json"
SOURCE_PATH = (
    ROOT
    / "public_data"
    / "q39_information3_strongmax"
    / "q39_derived_cache.npz"
)

LEFT = 1.0 / math.e
RIGHT = ((1.0 + math.sqrt(5.0)) / 2.0) % 1.0
WIDTH = (RIGHT - LEFT) % 1.0
ARC_STARTS = np.mod(LEFT + np.arange(4) / 4.0, 1.0)
PRIMARY_THRESHOLD = 0.01
BOOTSTRAP_DRAWS = 5_000
BOOTSTRAP_SEED = 490_030
EPS = 1e-12

INT_FIELDS = {
    "centre_id",
    "seed",
    "pair_index",
    "lineage_cycle_index",
    "start",
    "end",
    "length",
    "direction",
}


def file_hash(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_gzip_csv(path: pathlib.Path) -> list[dict[str, int | float | str]]:
    output: list[dict[str, int | float | str]] = []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            row: dict[str, int | float | str] = {}
            for key, value in raw.items():
                if key in INT_FIELDS:
                    row[key] = int(value)
                elif key in {"pair", "stratum"}:
                    row[key] = value
                else:
                    try:
                        row[key] = float(value)
                    except (TypeError, ValueError):
                        row[key] = value
            output.append(row)
    return output


def heading(du: float, dv: float) -> float:
    return float((math.atan2(dv, du) / (2.0 * math.pi)) % 1.0)


def circular_distance(a: float | np.ndarray, b: float | np.ndarray) -> np.ndarray:
    delta = np.abs(np.asarray(a) - np.asarray(b))
    return np.minimum(delta, 1.0 - delta)


def inside_arc(values: np.ndarray, start: float) -> np.ndarray:
    return np.mod(values - start, 1.0) <= WIDTH


def reconstruct_events(
    centres: list[dict[str, int | float | str]]
) -> list[dict[str, int | float | str]]:
    grouped: dict[tuple[int, int], list[dict[str, int | float | str]]] = defaultdict(
        list
    )
    for row in centres:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)

    events: list[dict[str, int | float | str]] = []
    for key, rows in grouped.items():
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
            event: dict[str, int | float | str] = {
                "seed": key[0],
                "pair_index": key[1],
                "current_start": int(current["start"]),
                "current_end": int(current["end"]),
                "circle_fit_residual": float(current["circle_fit_residual"]),
            }
            if int(current["end"]) < 250:
                event["stratum"] = "development"
            elif int(current["start"]) >= 250:
                event["stratum"] = "evaluation"
            else:
                event["stratum"] = "transition"

            for estimator in ("circle", "centroid", "extrema"):
                du = float(following[f"{estimator}_u"]) - float(
                    previous[f"{estimator}_u"]
                )
                dv = float(following[f"{estimator}_v"]) - float(
                    previous[f"{estimator}_v"]
                )
                strength = math.hypot(du, dv) / float(np.mean(radii))
                event[f"{estimator}_strength"] = strength
                event[f"{estimator}_heading"] = (
                    heading(du, dv) if strength > EPS else math.nan
                )
            events.append(event)
    return events


def occupancy(
    events: list[dict[str, int | float | str]],
    estimator: str = "circle",
    threshold: float = PRIMARY_THRESHOLD,
    stratum: str | None = None,
) -> dict[str, object]:
    values = np.asarray(
        [
            float(row[f"{estimator}_heading"])
            for row in events
            if float(row[f"{estimator}_strength"]) >= threshold
            and (stratum is None or row["stratum"] == stratum)
            and math.isfinite(float(row[f"{estimator}_heading"]))
        ],
        dtype=np.float64,
    )
    counts = np.asarray(
        [int(np.sum(inside_arc(values, float(start)))) for start in ARC_STARTS],
        dtype=np.int64,
    )
    fractions = counts / values.size if values.size else np.full(4, np.nan)
    return {
        "events": int(values.size),
        "counts": counts.tolist(),
        "fractions": fractions.tolist(),
        "winner_index": int(np.argmax(counts)) if values.size else None,
    }


def seed_bootstrap(
    events: list[dict[str, int | float | str]]
) -> dict[str, object]:
    by_seed: dict[int, np.ndarray] = defaultdict(lambda: np.zeros(4, dtype=np.int64))
    totals: dict[int, int] = defaultdict(int)
    for row in events:
        if float(row["circle_strength"]) < PRIMARY_THRESHOLD:
            continue
        value = float(row["circle_heading"])
        if not math.isfinite(value):
            continue
        seed = int(row["seed"])
        totals[seed] += 1
        for index, start in enumerate(ARC_STARTS):
            by_seed[seed][index] += int(bool(inside_arc(np.asarray([value]), start)[0]))

    seeds = sorted(totals)
    count_matrix = np.asarray([by_seed[seed] for seed in seeds], dtype=np.int64)
    total_vector = np.asarray([totals[seed] for seed in seeds], dtype=np.int64)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    differences = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for draw in range(BOOTSTRAP_DRAWS):
        selected = rng.integers(0, len(seeds), size=len(seeds))
        fractions = count_matrix[selected].sum(axis=0) / total_vector[selected].sum()
        differences[draw] = float(fractions[0] - np.max(fractions[1:]))
    return {
        "draws": BOOTSTRAP_DRAWS,
        "seed": BOOTSTRAP_SEED,
        "seeds": len(seeds),
        "probability_declared_beats_strongest_control": float(
            np.mean(differences > 0)
        ),
        "median_difference": float(np.median(differences)),
        "ci95": np.quantile(differences, [0.025, 0.975]).tolist(),
    }


def check_circle_centres(
    centres: list[dict[str, int | float | str]], sample_size: int = 1_000
) -> dict[str, object]:
    source = np.load(SOURCE_PATH, allow_pickle=False)
    closure = source["closure"]
    indices = np.linspace(0, len(centres) - 1, sample_size, dtype=int)
    centre_errors: list[float] = []
    radius_errors: list[float] = []
    residual_errors: list[float] = []

    for selected in indices:
        row = centres[int(selected)]
        line = np.asarray(
            closure[int(row["seed"]), :, int(row["pair_index"])],
            dtype=np.float64,
        )
        development = line[:250]
        flow = np.diff(development)
        lo, hi = np.quantile(development, [0.05, 0.95])
        mid = (lo + hi) / 2.0
        scale_u = (hi - lo) / 2.0
        scale_v = float(np.quantile(np.abs(flow), 0.95))
        u = (line[:-1] - mid) / scale_u
        v = np.diff(line) / scale_v
        start, end = int(row["start"]), int(row["end"])
        selected_u = u[start : end + 1]
        selected_v = v[start : end + 1]
        design = np.column_stack(
            (2.0 * selected_u, 2.0 * selected_v, np.ones(selected_u.size))
        )
        target = selected_u * selected_u + selected_v * selected_v
        solution, _, _, _ = np.linalg.lstsq(design, target, rcond=None)
        centre = solution[:2]
        radius = math.sqrt(float(solution[2] + np.dot(centre, centre)))
        radial = np.hypot(selected_u - centre[0], selected_v - centre[1])
        residual = float(np.median(np.abs(radial - radius)) / radius)

        centre_errors.append(
            math.hypot(
                float(row["circle_u"]) - float(centre[0]),
                float(row["circle_v"]) - float(centre[1]),
            )
        )
        radius_errors.append(abs(float(row["radius"]) - radius))
        residual_errors.append(
            abs(float(row["circle_fit_residual"]) - residual)
        )

    return {
        "sampled_centres": sample_size,
        "max_centre_error": max(centre_errors),
        "max_radius_error": max(radius_errors),
        "max_residual_error": max(residual_errors),
    }


def diagnostics(
    events: list[dict[str, int | float | str]]
) -> dict[str, object]:
    by_threshold: dict[str, object] = {}
    for threshold in (0.005, 0.01, 0.02, 0.05, 0.10):
        by_threshold[str(threshold)] = {
            estimator: occupancy(events, estimator, threshold)
            for estimator in ("circle", "centroid", "extrema")
        }

    by_stratum_threshold: dict[str, object] = {}
    for stratum in ("development", "transition", "evaluation"):
        by_stratum_threshold[stratum] = {
            str(threshold): {
                estimator: occupancy(
                    events, estimator, threshold, stratum=stratum
                )
                for estimator in ("circle", "centroid", "extrema")
            }
            for threshold in (0.005, 0.01, 0.02, 0.05, 0.10)
        }

    selected = [
        row for row in events if float(row["circle_strength"]) >= PRIMARY_THRESHOLD
    ]
    event_counts: dict[int, int] = defaultdict(int)
    seed_arc_counts: dict[int, np.ndarray] = defaultdict(
        lambda: np.zeros(4, dtype=np.int64)
    )
    for row in selected:
        seed = int(row["seed"])
        event_counts[seed] += 1
        value = float(row["circle_heading"])
        for index, start in enumerate(ARC_STARTS):
            seed_arc_counts[seed][index] += int(
                bool(inside_arc(np.asarray([value]), start)[0])
            )
    weights = np.asarray(list(event_counts.values()), dtype=np.float64)
    effective_seed_count = float(weights.sum() ** 2 / np.sum(weights**2))
    top_seeds = []
    for seed, count in sorted(
        event_counts.items(), key=lambda item: item[1], reverse=True
    )[:12]:
        counts = seed_arc_counts[seed]
        top_seeds.append(
            {
                "seed": seed,
                "events": count,
                "fractions": (counts / count).tolist(),
                "winner_index": int(np.argmax(counts)),
            }
        )

    disagreements: dict[str, object] = {}
    for other in ("centroid", "extrema"):
        differences = np.asarray(
            [
                circular_distance(
                    float(row["circle_heading"]), float(row[f"{other}_heading"])
                )
                for row in events
                if float(row["circle_strength"]) >= PRIMARY_THRESHOLD
                and float(row[f"{other}_strength"]) >= PRIMARY_THRESHOLD
                and math.isfinite(float(row["circle_heading"]))
                and math.isfinite(float(row[f"{other}_heading"]))
            ],
            dtype=np.float64,
        )
        disagreements[other] = {
            "events": int(differences.size),
            "median_turn_difference": float(np.median(differences)),
            "p90_turn_difference": float(np.quantile(differences, 0.90)),
            "fraction_within_0.05_turn": float(np.mean(differences <= 0.05)),
        }

    return {
        "threshold_sensitivity": by_threshold,
        "stratum_threshold_sensitivity": by_stratum_threshold,
        "primary_seed_count": len(event_counts),
        "primary_effective_seed_count": effective_seed_count,
        "top_seeds_by_event_count": top_seeds,
        "centre_estimator_heading_disagreement": disagreements,
    }


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return bool(abs(a - b) <= tolerance)


def main() -> None:
    saved = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    centres = load_gzip_csv(CENTRES_PATH)
    saved_events = load_gzip_csv(EVENTS_PATH)
    events = reconstruct_events(centres)

    primary = occupancy(events)
    bootstrap = seed_bootstrap(events)
    circle_check = check_circle_centres(centres)
    saved_primary = saved["primary_occupancy"]
    saved_bootstrap = saved["seed_cluster_bootstrap"]

    max_saved_heading_error = 0.0
    max_saved_strength_error = 0.0
    for recalculated, written in zip(events, saved_events, strict=True):
        max_saved_heading_error = max(
            max_saved_heading_error,
            float(
                circular_distance(
                    float(recalculated["circle_heading"]),
                    float(written["circle_heading"]),
                )
            ),
        )
        max_saved_strength_error = max(
            max_saved_strength_error,
            abs(
                float(recalculated["circle_strength"])
                - float(written["circle_strength"])
            ),
        )

    checks = {
        "source_hash_matches": file_hash(SOURCE_PATH)
        == saved["source"]["derived_sha256"],
        "centre_row_count_matches": len(centres) == saved["source"]["centres"],
        "event_row_count_matches": len(events) == saved["source"]["tangent_events"],
        "written_event_row_count_matches": len(saved_events) == len(events),
        "primary_counts_match": primary["counts"]
        == [
            saved_primary["counts"][name]
            for name in ("declared", "rotated_1", "rotated_2", "rotated_3")
        ],
        "primary_fractions_match": all(
            close(float(a), float(b))
            for a, b in zip(
                primary["fractions"],
                [
                    saved_primary["fractions"][name]
                    for name in (
                        "declared",
                        "rotated_1",
                        "rotated_2",
                        "rotated_3",
                    )
                ],
                strict=True,
            )
        ),
        "bootstrap_probability_matches": close(
            bootstrap["probability_declared_beats_strongest_control"],
            saved_bootstrap["probability_declared_beats_strongest_control"],
        ),
        "saved_event_headings_match": max_saved_heading_error <= 1e-12,
        "saved_event_strengths_match": max_saved_strength_error <= 1e-12,
        "sampled_raw_circle_centres_match": circle_check["max_centre_error"]
        <= 1e-10,
        "sampled_raw_circle_radii_match": circle_check["max_radius_error"]
        <= 1e-10,
    }

    output = {
        "validation_status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "recomputed_primary": primary,
        "recomputed_seed_cluster_bootstrap": bootstrap,
        "raw_source_circle_fit_check": circle_check,
        "saved_event_max_errors": {
            "heading_turns": max_saved_heading_error,
            "strength": max_saved_strength_error,
        },
        "post_result_diagnostics": diagnostics(events),
        "interpretation_boundary": (
            "Validation establishes deterministic reproduction and diagnoses "
            "the frozen Q49 result. Post-result threshold and stratum analyses "
            "are exploratory and cannot change the frozen verdict."
        ),
    }
    VALIDATION_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "validation_status": output["validation_status"],
                "checks": checks,
                "recomputed_primary": primary,
                "recomputed_seed_cluster_bootstrap": bootstrap,
                "raw_source_circle_fit_check": circle_check,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
