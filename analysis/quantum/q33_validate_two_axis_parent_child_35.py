"""Independent validator for Q33.

This file intentionally does not import the primary analysis.  It reopens the
raw caches, reconstructs development scales, checks a bounded deterministic
sample of events, and recomputes the frozen gates from the saved event table.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_FIDELITY_v1.md"
Q27_CACHE = HERE / "public_data" / "q27_network_reconstruction" / "q27_derived_cache.npz"
Q28_CACHE = HERE / "public_data" / "q27_network_reconstruction" / "q28_connected_cache.npy"
RESULTS = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_RESULTS.json"
EVENTS = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_EVENTS.csv.gz"
TRIALS = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_TRIALS.csv"
OUTPUT = HERE / "Q33_TWO_AXIS_PARENT_CHILD_35_VALIDATION.json"

EXPECTED_HASHES = {
    "protocol_sha256": "c91afedc4a01b763b81940a0057929644ddde1806825afcdf21a7fced48f0a23",
    "fidelity_sha256": "b7a306b2fa02c9048d017c77768c6b6069dbd8b82e3f9db33d072bc6529ed620",
    "q27_cache_sha256": "660a59ff416b3938755fcde6b7c361bb46a2fe24bf8c2aaca0cfa63bbb80137c",
    "q28_cache_sha256": "6b73ac362d50453dad6ff76ea2a9102b04b24d5e9be596c46545cf5671ad4ef9",
}
PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
CONTROLS = ("topology", "seed", "time")
BACKWARD = 8
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def number(row: dict[str, str], field: str) -> float:
    raw = row.get(field, "")
    if raw in ("", "nan", "None"):
        return math.nan
    return float(raw)


def finite(rows: list[dict[str, str]], field: str) -> np.ndarray:
    values = np.asarray([number(row, field) for row in rows], dtype=np.float64)
    return values[np.isfinite(values)]


def latest_extreme(values: np.ndarray, time: int, mode: str) -> tuple[int, float]:
    start = time - BACKWARD
    segment = np.asarray(values[start : time + 1], dtype=np.float64)
    target = np.nanmax(segment) if mode == "max" else np.nanmin(segment)
    positions = np.flatnonzero(np.isclose(segment, target, rtol=0.0, atol=1e-12))
    position = int(positions[-1])
    return start + position, float(segment[position])


def active_pair_indices(edge_row: np.ndarray) -> tuple[int, ...]:
    return tuple(
        PAIR_TO_INDEX[tuple(sorted((int(u), int(v))))] for u, v in edge_row
    )


def endpoint_children(
    active: tuple[int, ...], source_pair: int
) -> tuple[int, int] | None:
    u, v = PAIRS[source_pair]
    if source_pair in active:
        return None
    child_u = [index for index in active if u in PAIRS[index]]
    child_v = [index for index in active if v in PAIRS[index]]
    if len(child_u) != 1 or len(child_v) != 1 or child_u[0] == child_v[0]:
        return None
    return child_u[0], child_v[0]


def angle_degrees(left: np.ndarray, right: np.ndarray) -> tuple[float, float]:
    left = np.asarray(left, dtype=np.float64).ravel()
    right = np.asarray(right, dtype=np.float64).ravel()
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator <= EPS:
        return math.nan, math.nan
    cosine = float(np.clip(np.dot(left, right) / denominator, -1.0, 1.0))
    angle = float(np.degrees(np.arccos(cosine)))
    return angle, min(angle, 180.0 - angle)


def close(left: float, right: float, tolerance: float = 2e-6) -> bool:
    return bool(
        (not np.isfinite(left) and not np.isfinite(right))
        or abs(left - right) <= tolerance
    )


def raw_sample_checks(
    rows: list[dict[str, str]],
    x_all: np.ndarray,
    energy_all: np.ndarray,
    energy_capacity: np.ndarray,
    edges_all: np.ndarray,
    connected: np.ndarray,
) -> dict[str, object]:
    evaluation = [row for row in rows if row["split"] == "evaluation"]
    if not evaluation:
        return {"sample_n": 0, "all_pass": False, "failures": ["no rows"]}
    positions = np.linspace(0, len(evaluation) - 1, 64, dtype=int)
    failures: list[str] = []
    for sample_number, position in enumerate(positions):
        row = evaluation[int(position)]
        branch = int(row["branch"])
        seed = int(row["seed"])
        time = int(row["time"])
        source = int(row["source_pair"])
        active = active_pair_indices(edges_all[branch, seed, time])
        children = endpoint_children(active, source)
        saved_children = (
            int(row["exact_child1_index"]),
            int(row["exact_child2_index"]),
        )
        if children != saved_children:
            failures.append(f"{sample_number}: topology")
            continue
        source_capacity = float(energy_capacity[branch, seed, source])
        rhos: list[float] = []
        origins: list[float] = []
        gains: list[float] = []
        movements: list[np.ndarray] = []
        crest_time, crest_x = latest_extreme(
            x_all[branch, seed, :, source], time, "max"
        )
        source_loss = float(
            energy_all[branch, seed, crest_time, source]
            - energy_all[branch, seed, time + 1, source]
        )
        source_movement = (
            np.asarray(connected[branch, seed, crest_time, source], dtype=np.float64)
            - np.asarray(connected[branch, seed, time + 1, source], dtype=np.float64)
        )
        for child in children:
            origin_time, origin_x = latest_extreme(
                x_all[branch, seed, :, child], time, "min"
            )
            rhos.append(
                float(energy_capacity[branch, seed, child] / source_capacity)
            )
            origins.append(origin_x)
            gains.append(
                max(
                    float(
                        energy_all[branch, seed, time + 1, child]
                        - energy_all[branch, seed, origin_time, child]
                    ),
                    0.0,
                )
            )
            movements.append(
                np.asarray(
                    connected[branch, seed, time + 1, child], dtype=np.float64
                )
                - np.asarray(
                    connected[branch, seed, origin_time, child], dtype=np.float64
                )
            )
        _, axial = angle_degrees(source_movement, movements[0] + movements[1])
        reconstructed = {
            "source_crest_time": float(crest_time),
            "source_crest_x": crest_x,
            "source_capacity": source_capacity,
            "source_energy_loss": source_loss,
            "exact_rho_mean": float(np.mean(rhos)),
            "exact_origin_x_mean": float(np.mean(origins)),
            "exact_origin_x_max": float(np.max(origins)),
            "exact_transfer_sum": float(sum(gains) / source_loss),
            "exact_combined_axial": float(axial),
        }
        for field, observed in reconstructed.items():
            saved = number(row, field)
            if not close(observed, saved):
                failures.append(
                    f"{sample_number}: {field} raw={observed} saved={saved}"
                )
    return {
        "sample_n": int(len(positions)),
        "failure_count": len(failures),
        "failures": failures[:20],
        "all_pass": not failures,
    }


def recompute_verdict(
    evaluation: list[dict[str, str]], results: dict[str, object]
) -> dict[str, object]:
    exact_rho = float(np.median(finite(evaluation, "exact_rho_mean")))
    exact_error = float(
        np.median(finite(evaluation, "exact_half_distance_mean"))
    )
    exact_origins = np.concatenate(
        [
            finite(evaluation, "exact_child1_origin_x"),
            finite(evaluation, "exact_child2_origin_x"),
        ]
    )
    eligibility = {
        "source_events_ge_5000": len(evaluation) >= 5000,
        "strata_ge_100": len(
            {(int(row["branch"]), int(row["seed"])) for row in evaluation}
        )
        >= 100,
        "exact_routes_ge_5000": 2 * len(evaluation) >= 5000,
    }
    for control in CONTROLS:
        eligibility[f"{control}_paired_events_ge_2000"] = (
            finite(evaluation, f"{control}_rho_mean").size >= 2000
        )
    half = {"pooled_median_capacity_in_040_060": 0.4 <= exact_rho <= 0.6}
    for branch, label in enumerate(("c2", "c4")):
        branch_rows = [
            row for row in evaluation if int(row["branch"]) == branch
        ]
        branch_median = float(np.median(finite(branch_rows, "exact_rho_mean")))
        half[f"{label}_median_capacity_in_035_065"] = (
            0.35 <= branch_median <= 0.65
        )
    for control in CONTROLS:
        control_error = float(
            np.median(finite(evaluation, f"{control}_half_distance_mean"))
        )
        half[f"exact_error_5pct_better_than_{control}"] = (
            1.0 - exact_error / control_error
        ) >= 0.05
        probability = float(
            results["evaluation_bootstrap"][control][
                "probability_exact_lower"
            ]
        )
        half[f"bootstrap_probability_ge_095_vs_{control}"] = (
            probability >= 0.95
        )
    both = finite(evaluation, "exact_both_origin_le_05")
    pole = {
        "median_child_origin_x_le_05": float(np.median(exact_origins)) <= 0.5,
        "both_child_origins_le_05_fraction_ge_050": float(np.mean(both)) >= 0.5,
    }
    eligible = all(eligibility.values())
    half_pass = all(half.values())
    pole_pass = all(pole.values())
    if not eligible:
        label = "INCONCLUSIVE"
    elif half_pass and pole_pass:
        label = "SUPPORTED INSIDE THIS SIMULATOR"
    elif not half_pass and 0.8 <= exact_rho <= 1.2:
        label = (
            "ORDERED HANDOVER, BUT Q32 CHILDREN ARE SAME-RUNG "
            "IN THIS ENERGY PROJECTION"
        )
    else:
        label = "CROSS-RUNG 3.5 PROJECTION NOT SUPPORTED BY THIS IMPLEMENTATION"
    return {
        "exact_capacity_median": exact_rho,
        "exact_half_distance_median": exact_error,
        "exact_child_origin_x_median": float(np.median(exact_origins)),
        "both_origin_fraction": float(np.mean(both)),
        "eligibility": eligibility,
        "half_capacity_gates": half,
        "backward_pole_gates": pole,
        "label": label,
    }


def main() -> None:
    observed_hashes = {
        "protocol_sha256": sha256(PROTOCOL),
        "fidelity_sha256": sha256(FIDELITY),
        "q27_cache_sha256": sha256(Q27_CACHE),
        "q28_cache_sha256": sha256(Q28_CACHE),
    }
    rows = read_csv(EVENTS)
    trial_rows = read_csv(TRIALS)
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    q27 = np.load(Q27_CACHE)
    h_all = np.asarray(q27["closure"], dtype=np.float32)
    edges_all = np.asarray(q27["edges"], dtype=np.int8)
    connected = np.load(Q28_CACHE, mmap_mode="r")
    h_capacity = np.quantile(
        np.asarray(h_all[:, :, :250, :], dtype=np.float64), 0.95, axis=2
    )
    x_all = np.divide(
        2.0 * h_all,
        h_capacity[:, :, None, :],
        out=np.full(h_all.shape, np.nan, dtype=np.float32),
        where=h_capacity[:, :, None, :] > EPS,
    )
    energy_all = np.sum(
        np.asarray(connected, dtype=np.float32) ** 2,
        axis=(-2, -1),
        dtype=np.float32,
    )
    energy_capacity = np.quantile(
        np.asarray(energy_all[:, :, :250, :], dtype=np.float64),
        0.95,
        axis=2,
    )

    evaluation = [row for row in rows if row["split"] == "evaluation"]
    development = [row for row in rows if row["split"] == "development"]
    raw = raw_sample_checks(
        rows, x_all, energy_all, energy_capacity, edges_all, connected
    )
    recomputed = recompute_verdict(evaluation, results)
    expected_verdict = results["frozen_verdict"]["label"]
    unique_keys = {
        (
            row["split"],
            row["branch"],
            row["seed"],
            row["time"],
            row["source_pair"],
        )
        for row in rows
    }
    checks = {
        "all_hashes_match": observed_hashes == EXPECTED_HASHES,
        "event_total_matches_results": len(rows)
        == int(results["splits"]["development"]["source_events"])
        + int(results["splits"]["evaluation"]["source_events"]),
        "development_rows_match": len(development)
        == int(results["splits"]["development"]["source_events"]),
        "evaluation_rows_match": len(evaluation)
        == int(results["splits"]["evaluation"]["source_events"]),
        "trial_rows_are_200_strata": len(trial_rows) == 200,
        "event_keys_unique": len(unique_keys) == len(rows),
        "raw_sample_reconstruction_passes": bool(raw["all_pass"]),
        "verdict_recomputes": recomputed["label"] == expected_verdict,
        "headline_capacity_matches": close(
            recomputed["exact_capacity_median"],
            float(
                results["splits"]["evaluation"]["routes"]["exact"][
                    "event_mean_capacity_ratio"
                ]["median"]
            ),
        ),
        "headline_origin_matches": close(
            recomputed["exact_child_origin_x_median"],
            float(
                results["splits"]["evaluation"]["routes"]["exact"][
                    "child_origin_x"
                ]["median"]
            ),
        ),
    }
    output = {
        "validator": "Q33-independent-validator-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "observed_hashes": observed_hashes,
        "expected_hashes": EXPECTED_HASHES,
        "checks": checks,
        "raw_sample": raw,
        "recomputed": recomputed,
        "saved_verdict": expected_verdict,
        "limitations": [
            "The validator shares the same cached source arrays, but not primary code.",
            "Bootstrap draws are checked through saved probabilities and gate logic; they are not redrawn.",
            "Validation establishes computational reproducibility, not physical replication.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "checks": checks}, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
