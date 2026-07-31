"""Independent numerical checks for Q48 / T308."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import q48_e_phi_carrier_wobble as q48  # noqa: E402


RESULTS_PATH = HERE / "Q48_E_PHI_CARRIER_WOBBLE_RESULTS.json"
EVENTS_PATH = HERE / "Q48_E_PHI_CARRIER_WOBBLE_EVENTS.csv.gz"
VALIDATION_PATH = HERE / "Q48_E_PHI_CARRIER_WOBBLE_VALIDATION.json"
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_events() -> list[dict[str, str]]:
    with gzip.open(EVENTS_PATH, "rt", newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def raw_distance(
    connected: np.ndarray,
    source: dict[str, object],
    target: dict[str, object],
    quadrant: int,
) -> float:
    seed = int(source["seed"])
    pair = int(source["pair_index"])
    s0, s1 = int(source[f"q{quadrant}_start"]), int(
        source[f"q{quadrant}_end"]
    )
    t0, t1 = int(target[f"q{quadrant}_start"]), int(
        target[f"q{quadrant}_end"]
    )
    left = np.mean(
        connected[seed, s0 : s1 + 1, pair], axis=0, dtype=np.float64
    )
    right = np.mean(
        connected[seed, t0 : t1 + 1, pair], axis=0, dtype=np.float64
    )
    cosine = float(
        np.sum(left * right) / (np.linalg.norm(left) * np.linalg.norm(right))
    )
    return math.acos(float(np.clip(cosine, -1.0, 1.0))) / (2.0 * math.pi)


def main() -> None:
    result = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    rows = read_events()
    connected = np.load(q48.CONNECTED_PATH, mmap_mode="r")
    derived = np.load(q48.DERIVED_PATH)
    cycles, extraction = q48.extract_all_cycles(
        derived["closure"], derived["pairs"]
    )
    cycle_by_id = {int(row["cycle_id"]): row for row in cycles}

    left = 1.0 / math.e
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    right = 2.0 - phi
    x_three_eighths = 2.0 * (3.0 / 8.0 - left) / (right - left)

    values = np.asarray([float(row["delta_mean"]) for row in rows])
    carrier_mask = (values >= left) & (values <= right)
    carrier_rows = [row for row, keep in zip(rows, carrier_mask) if keep]
    carrier_x = np.asarray(
        [2.0 * (float(row["delta_mean"]) - left) / (right - left) for row in carrier_rows]
    )

    # Every carrier event plus the 25 largest and a deterministic broad sample.
    ranked = sorted(range(len(rows)), key=lambda i: values[i], reverse=True)
    rng = np.random.default_rng(480031)
    selected = set(ranked[:25])
    selected.update(np.flatnonzero(carrier_mask).tolist())
    selected.update(rng.choice(len(rows), size=250, replace=False).tolist())
    max_raw_error = 0.0
    max_local_x_error = 0.0
    for index in sorted(selected):
        row = rows[index]
        source = cycle_by_id[int(row["source_cycle_id"])]
        target = cycle_by_id[int(row["target_cycle_id"])]
        quadrants = [
            raw_distance(connected, source, target, quadrant)
            for quadrant in range(1, 5)
        ]
        for quadrant, calculated in enumerate(quadrants, 1):
            max_raw_error = max(
                max_raw_error, abs(calculated - float(row[f"delta_q{quadrant}"]))
            )
        mean = float(np.mean(quadrants))
        max_raw_error = max(max_raw_error, abs(mean - float(row["delta_mean"])))
        calculated_x = 2.0 * (mean - left) / (right - left)
        max_local_x_error = max(
            max_local_x_error, abs(calculated_x - float(row["local_x"]))
        )

    carriers_by_lineage = Counter(
        (int(row["seed"]), int(row["pair_index"])) for row in carrier_rows
    )
    carrier_values = np.asarray([float(row["delta_mean"]) for row in carrier_rows])
    near_ridge_fraction = float(
        np.mean(np.abs(carrier_x - x_three_eighths) <= 0.10)
    )
    level_counts = Counter(row["nearest_reversal_level"] for row in rows)

    checks = {
        "result_and_event_files_exist": RESULTS_PATH.exists() and EVENTS_PATH.exists(),
        "source_hashes_match": (
            sha256(q48.CONNECTED_PATH) == result["source"]["connected_sha256"]
            and sha256(q48.DERIVED_PATH) == result["source"]["derived_sha256"]
        ),
        "constant_left_matches": abs(left - result["geometry"]["left_one_over_e"])
        <= EPS,
        "constant_right_matches": abs(right - result["geometry"]["right_anti_phi"])
        <= EPS,
        "three_eighths_local_x_matches": abs(
            x_three_eighths - result["geometry"]["three_eighths_local_x"]
        )
        <= EPS,
        "cycle_count_matches": len(cycles)
        == result["source"]["cycles_extracted_full_range"],
        "eligible_lineages_match": extraction["eligible_lineages"]
        == result["source"]["eligible_lineages"],
        "event_count_matches": len(rows) == result["source"]["events_full_range"],
        "all_events_in_valid_half_turn_range": bool(
            np.all((values >= 0.0) & (values <= 0.5))
        ),
        "carrier_count_matches": len(carrier_rows) == result["carrier"]["events"],
        "carrier_seeds_match": len({int(row["seed"]) for row in carrier_rows})
        == result["carrier"]["seeds"],
        "carrier_lineages_match": len(carriers_by_lineage)
        == result["carrier"]["lineages"],
        "carrier_events_are_isolated_by_lineage": max(
            carriers_by_lineage.values(), default=0
        )
        == 1,
        "no_carrier_event_near_declared_ridge": near_ridge_fraction == 0.0,
        "carrier_median_local_x_matches": abs(
            float(np.median(carrier_x)) - result["carrier"]["median_local_x"]
        )
        <= EPS,
        "carrier_mean_matches": abs(
            float(np.mean(carrier_values))
            - result["carrier"]["movement_summary"]["mean"]
        )
        <= EPS,
        "reversal_level_counts_match": all(
            int(level_counts.get(label, 0))
            == int(result["descriptive_reversal_levels"]["counts"][label])
            for label in q48.REVERSAL_LABELS
        ),
        "raw_selected_event_recalculation": max_raw_error <= 1e-12,
        "raw_selected_local_x_recalculation": max_local_x_error <= 1e-10,
        "saved_verdict_is_not_supported": result["verdict"] == "NOT SUPPORTED",
        "all_substantive_gates_failed": result["gates"]["substantive_passes"] == 0,
    }
    passed = all(checks.values())
    validation = {
        "test": "Q48 / T308 validation",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "checked_raw_events": len(selected),
        "max_raw_movement_error": max_raw_error,
        "max_raw_local_x_error": max_local_x_error,
        "carrier_count": len(carrier_rows),
        "carrier_local_x": {
            "min": float(np.min(carrier_x)),
            "median": float(np.median(carrier_x)),
            "max": float(np.max(carrier_x)),
            "near_three_eighths_fraction": near_ridge_fraction,
        },
    }
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
