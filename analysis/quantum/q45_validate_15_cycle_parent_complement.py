"""Independent validation for Q45 parent-complement shaping outputs."""

from __future__ import annotations

import csv
import gzip
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import h5py
import numpy as np

import q40_return_flow_relation_reversal_test as base
import q44_ara_mixing_prediction_test as q44
import q45_15_cycle_parent_complement_test as q45


OUTPUT = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_VALIDATION.json"
EPS = 1e-10


def numeric_delta(first, second) -> float:
    if isinstance(first, dict):
        return max(
            (numeric_delta(first[key], second[key]) for key in first),
            default=0.0,
        )
    if isinstance(first, list):
        return max(
            (numeric_delta(a, b) for a, b in zip(first, second)),
            default=0.0,
        )
    if isinstance(first, (int, float)) and not isinstance(first, bool):
        return abs(float(first) - float(second))
    return 0.0 if first == second else float("inf")


def read_lineages():
    numeric = {
        "seed",
        "pair",
        "development_period",
        "development_lag15_correlation",
        "development_phase_slope",
        "development_phase_intercept",
        "development_coordinate_coherence",
        "development_quadrant_occupancy",
        "constant_sse",
        "parent_sse",
        "wrong_sse",
        "lagged_sse",
        "parent_skill",
        "parent_over_wrong",
        "parent_over_lagged",
        "path_share_l",
        "path_share_c",
        "ara_x_l",
        "ara_x_c",
        "state_share_l",
        "movement_relation",
        "windows",
    }
    rows = []
    with gzip.open(q45.LINEAGES, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            for key in numeric:
                row[key] = float(row[key])
            row["seed"] = int(row["seed"])
            row["pair"] = int(row["pair"])
            row["windows"] = int(row["windows"])
            rows.append(row)
    return rows


def read_flow():
    rows = []
    with q45.FLOW_SEEDS.open("r", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            rows.append({key: int(value) if key == "seed" else float(value) for key, value in row.items()})
    return rows


def raw_cache_check():
    local_cache = np.load(q45.LOCAL_PRODUCT, mmap_mode="r")
    connected_cache = np.load(q45.CONNECTED, mmap_mode="r")
    max_local_difference = 0.0
    max_connected_difference = 0.0
    max_parent_difference = 0.0
    observations = 0
    samples = {
        0: ((0, 0), (249, 13), (499, 65)),
        37: ((0, 13), (249, 65), (499, 0)),
        99: ((0, 65), (249, 0), (499, 13)),
    }
    with h5py.File(q45.SOURCE, "r") as handle:
        for seed, locations in samples.items():
            group = handle[q44.locate_trial(handle, seed)]["two_qubit_dms"]
            for time_index, pair in locations:
                rho = np.asarray(
                    group[str(time_index)][base.PAIR_NAMES[pair]][()],
                    dtype=np.complex128,
                )[None, ...]
                expectation = np.einsum(
                    "nij,kji->nk", rho, base.OPS, optimize=True
                ).real
                a, b = expectation[:, :3], expectation[:, 3:6]
                tensor = expectation[:, 6:15].reshape(-1, 3, 3)[0]
                local = (a[:, :, None] * b[:, None, :])[0]
                connected = tensor - local
                cached_l = np.asarray(
                    local_cache[seed, time_index, pair], dtype=np.float64
                )
                cached_c = np.asarray(
                    connected_cache[seed, time_index, pair], dtype=np.float64
                )
                max_local_difference = max(
                    max_local_difference, float(np.max(np.abs(cached_l - local)))
                )
                max_connected_difference = max(
                    max_connected_difference,
                    float(np.max(np.abs(cached_c - connected))),
                )
                max_parent_difference = max(
                    max_parent_difference,
                    float(np.max(np.abs(cached_c + cached_l - tensor))),
                )
                observations += 1
    return {
        "observations": observations,
        "max_local_cache_difference": max_local_difference,
        "max_connected_cache_difference": max_connected_difference,
        "max_parent_reconstruction_difference": max_parent_difference,
    }


def main() -> None:
    recorded = json.loads(q45.RESULTS.read_text(encoding="utf-8"))
    rows = read_lineages()
    flow_rows = read_flow()
    lineage_recomputed = q45.summarize_lineages(rows)
    flow_recomputed = q45.summarize_flow(flow_rows)
    lineage_delta = numeric_delta(
        lineage_recomputed, recorded["lineage_summary"]
    )
    flow_delta = numeric_delta(flow_recomputed, recorded["flow_summary"])

    raw = raw_cache_check()
    qc = np.load(q45.LOCAL_QC, allow_pickle=False)["qc"]
    profiles = np.load(q45.PROFILES, allow_pickle=False)
    seeds = len({row["seed"] for row in rows})
    family_counts = {
        name: sum(row["family"] == name for row in rows)
        for name in ("two_turn_7_5", "one_turn_15")
    }

    checks = {
        "protocol_hash_matches": (
            q45.digest(q45.PROTOCOL, "sha256") == q45.PROTOCOL_SHA256
        ),
        "archive_hash_matches": (
            q45.digest(q45.ARCHIVE, "md5") == q45.ARCHIVE_MD5
        ),
        "lineage_count_matches": (
            len(rows) == recorded["eligibility"]["lineages"]
        ),
        "seed_count_matches": seeds == recorded["eligibility"]["seeds"],
        "family_counts_match": (
            family_counts == recorded["eligibility"]["family_counts"]
        ),
        "lineage_summary_recomputes": lineage_delta <= EPS,
        "flow_summary_recomputes": flow_delta <= EPS,
        "local_cache_matches_raw": (
            raw["max_local_cache_difference"] <= 1e-6
        ),
        "connected_cache_matches_raw": (
            raw["max_connected_cache_difference"] <= 1e-6
        ),
        "parent_reconstruction_matches_raw": (
            raw["max_parent_reconstruction_difference"] <= 2e-6
        ),
        "local_bloch_norms_physical": (
            float(np.max(qc[:, :2])) <= 1.0 + 1e-6
        ),
        "local_cache_has_no_nonfinite_values": int(np.sum(qc[:, 2])) == 0,
        "profiles_have_expected_shape": all(
            profiles[key].shape == (len(rows), q45.PHASE_BINS)
            for key in ("connected", "local", "parent")
        ),
        "figure_png_exists": (
            q45.FIGURE_PNG.exists() and q45.FIGURE_PNG.stat().st_size > 10_000
        ),
        "figure_svg_exists": (
            q45.FIGURE_SVG.exists() and q45.FIGURE_SVG.stat().st_size > 10_000
        ),
    }
    validation = {
        "test_id": q45.TEST_ID,
        "passed": all(checks.values()),
        "checks": checks,
        "maximum_numeric_difference": {
            "lineage_summary": lineage_delta,
            "flow_summary": flow_delta,
        },
        "raw_cache_check": raw,
        "quality": {
            "max_local_bloch_norm": float(np.max(qc[:, :2])),
            "nonfinite_local_product_values": int(np.sum(qc[:, 2])),
        },
        "artifacts_checked": [
            q45.PROTOCOL.name,
            q45.RESULTS.name,
            q45.LINEAGES.name,
            q45.FLOW_SEEDS.name,
            q45.PROFILES.name,
            q45.FIGURE_PNG.name,
            q45.FIGURE_SVG.name,
        ],
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
