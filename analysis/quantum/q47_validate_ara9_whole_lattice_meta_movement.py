"""Independent QA for Q47 whole-lattice ARA9 meta-movement results."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
RAW_PATH = (
    HERE
    / "public_data"
    / "q39_information3_strongmax"
    / "q39_connected_cache.npy"
)
CYCLES_PATH = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_CYCLES.csv.gz"
EVENTS_PATH = HERE / "Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_EVENTS.csv.gz"
RESULTS_PATH = HERE / "Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_RESULTS.json"
OUTPUT_PATH = HERE / "Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_VALIDATION.json"
EPS = 1e-12


def digest(path: pathlib.Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def load_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def matrix_mean(
    raw: np.ndarray, row: dict[str, str], quadrant: int
) -> tuple[np.ndarray, float]:
    seed = int(row["seed"])
    pair = int(row["pair_index"])
    start = int(row[f"q{quadrant}_start"])
    stop = int(row[f"q{quadrant}_end"]) + 1
    value = np.asarray(raw[seed, start:stop, pair], dtype=np.float64).sum(axis=0)
    value /= stop - start
    return value, float(np.sqrt(np.square(value).sum()))


def distance(
    left: np.ndarray, left_norm: float, right: np.ndarray, right_norm: float
) -> float:
    if left_norm <= EPS or right_norm <= EPS:
        return math.nan
    cosine = float(np.square(left - right).sum())
    cosine = 1.0 - cosine / (2.0 * left_norm * right_norm)
    # The identity above is exact only for equal norms. Recalculate through
    # normalized vectors so the validator remains correct for unequal norms.
    cosine = float(
        np.multiply(left / left_norm, right / right_norm, dtype=np.float64).sum()
    )
    return math.acos(float(np.clip(cosine, -1.0, 1.0))) / (2.0 * math.pi)


def main() -> None:
    result = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    cycles = load_csv(CYCLES_PATH)
    events = load_csv(EVENTS_PATH)
    raw = np.load(RAW_PATH, mmap_mode="r")

    by_id = {row["cycle_id"]: row for row in cycles}
    sample_indices = sorted(
        set(
            np.linspace(0, len(events) - 1, 257, dtype=int).tolist()
            + np.argsort(
                np.array([float(row["delta_mean"]) for row in events])
            )[-32:].tolist()
        )
    )
    differences: list[float] = []
    quadrant_differences: list[float] = []
    for index in sample_indices:
        event = events[index]
        source = by_id[event["source_cycle_id"]]
        target = by_id[event["target_cycle_id"]]
        independent: list[float] = []
        for quadrant in range(1, 5):
            left, left_norm = matrix_mean(raw, source, quadrant)
            right, right_norm = matrix_mean(raw, target, quadrant)
            value = distance(left, left_norm, right, right_norm)
            stored = float(event[f"delta_q{quadrant}"])
            quadrant_differences.append(abs(value - stored))
            independent.append(value)
        stored_mean = float(event["delta_mean"])
        differences.append(abs(float(np.mean(independent)) - stored_mean))

    values = np.array([float(row["delta_mean"]) for row in events])
    reported = result["meta_step"]
    summary_differences = {
        "count": abs(len(values) - int(reported["count"])),
        "mean": abs(float(np.mean(values)) - float(reported["mean"])),
        "median": abs(float(np.median(values)) - float(reported["median"])),
        "p25": abs(float(np.percentile(values, 25)) - float(reported["p25"])),
        "p75": abs(float(np.percentile(values, 75)) - float(reported["p75"])),
        "min": abs(float(np.min(values)) - float(reported["min"])),
        "max": abs(float(np.max(values)) - float(reported["max"])),
    }

    high = [row for row in events if float(row["delta_mean"]) >= 0.1]
    high_at_seam = [
        row for row in high if int(row["source_start"]) in {250, 251}
    ]
    checks = {
        "raw_shape_matches": list(raw.shape)
        == result["source"]["connected_shape"],
        "raw_hash_matches": digest(RAW_PATH)
        == result["source"]["connected_sha256"],
        "cycle_hash_matches": digest(CYCLES_PATH)
        == result["source"]["cycles_sha256"],
        "event_count_matches": len(events)
        == int(result["population"]["adjacent_events"]),
        # The source cache is float32; independent operation ordering differs
        # from the main script at the low-billionth-turn level.
        "raw_recalculation_matches": max(quadrant_differences) <= 1e-8,
        "event_mean_matches": max(differences) <= 1e-8,
        "reported_summary_matches": max(summary_differences.values()) <= 1e-12,
        "all_distances_bounded": bool(np.all((values >= 0.0) & (values <= 0.5))),
    }
    validation = {
        "test_id": "Q47-ARA9-WHOLE-LATTICE-META-MOVEMENT-v1-validation",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "sampled_events": len(sample_indices),
        "max_raw_quadrant_difference": max(quadrant_differences),
        "max_event_mean_difference": max(differences),
        "summary_differences": summary_differences,
        "tail_diagnostic": {
            "events_ge_0_1_turn": len(high),
            "events_ge_0_1_fraction": len(high) / len(events),
            "events_ge_0_1_at_source_250_or_251": len(high_at_seam),
            "seam_fraction": len(high_at_seam) / len(high) if high else None,
        },
        "boundaries": [
            "Raw recalculation covers a deterministic stratified sample plus the 32 largest events.",
            "Summary and range checks cover all saved adjacent-cycle events.",
            "The seam concentration is descriptive and was not part of the frozen Phi gate.",
        ],
    }
    OUTPUT_PATH.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
