"""Independent validator for Q33B.

Reopens raw caches, reconstructs development scales and a deterministic raw
event sample, and recomputes the frozen routing gates without importing the
primary analysis.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_FIDELITY_v1.md"
Q27_CACHE = HERE / "public_data" / "q27_network_reconstruction" / "q27_derived_cache.npz"
Q28_CACHE = HERE / "public_data" / "q27_network_reconstruction" / "q28_connected_cache.npy"
RESULTS = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_RESULTS.json"
EVENTS = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_EVENTS.csv.gz"
TRIALS = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_TRIALS.csv"
OUTPUT = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_VALIDATION.json"

EXPECTED_HASHES = {
    "protocol_sha256": "780364be62feb97afe336b9cbf16511b832a998e07581e1877fa9a17f6f21a70",
    "fidelity_sha256": "43a6a2090669588632f76988c1fc18394c8c2950e856ea622116775c05ebd7a3",
    "q27_cache_sha256": "660a59ff416b3938755fcde6b7c361bb46a2fe24bf8c2aaca0cfa63bbb80137c",
    "q28_cache_sha256": "6b73ac362d50453dad6ff76ea2a9102b04b24d5e9be596c46545cf5671ad4ef9",
}
PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
COMPARATORS = ("sibling", "topology", "seed", "time")
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


def close(left: float, right: float, tolerance: float = 2e-6) -> bool:
    return bool(
        (not np.isfinite(left) and not np.isfinite(right))
        or abs(left - right) <= tolerance
    )


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


def boundary_order(
    candidates: tuple[int, int] | None, z_row: np.ndarray
) -> tuple[int, int] | None:
    if candidates is None:
        return None
    values = sorted((float(z_row[index]), int(index)) for index in candidates)
    if not np.all(np.isfinite([values[0][0], values[1][0]])):
        return None
    return values[0][1], values[1][1]


def matched_topology_pair(
    active: tuple[int, ...],
    source_pair: int,
    exact_children: tuple[int, int],
    z_row: np.ndarray,
) -> tuple[int, int] | None:
    source_nodes = set(PAIRS[source_pair])
    candidates = tuple(
        index for index in active if not source_nodes.intersection(PAIRS[index])
    )
    exact_z = [float(z_row[index]) for index in exact_children]
    assignments = []
    for first, second in itertools.permutations(candidates, 2):
        distance = abs(float(z_row[first]) - exact_z[0]) + abs(
            float(z_row[second]) - exact_z[1]
        )
        assignments.append((distance, first, second))
    if not assignments:
        return None
    _, first, second = min(assignments)
    return int(first), int(second)


def raw_sample(
    rows: list[dict[str, str]],
    h_all: np.ndarray,
    z_all: np.ndarray,
    h_scale: np.ndarray,
    edges_all: np.ndarray,
) -> dict[str, object]:
    evaluation = [row for row in rows if row["split"] == "evaluation"]
    positions = np.linspace(0, len(evaluation) - 1, 64, dtype=int)
    failures: list[str] = []
    for sample_number, position in enumerate(positions):
        row = evaluation[int(position)]
        branch = int(row["branch"])
        seed = int(row["seed"])
        time = int(row["time"])
        source = int(row["source_pair"])
        active = active_pair_indices(edges_all[branch, seed, time])
        exact_children = endpoint_children(active, source)
        exact_order = boundary_order(exact_children, z_all[branch, seed, time])
        if exact_order is None:
            failures.append(f"{sample_number}: missing exact order")
            continue
        if exact_order != (
            int(row["exact_child"]),
            int(row["sibling_child"]),
        ):
            failures.append(f"{sample_number}: exact/sibling selection")

        topology_pair = matched_topology_pair(
            active, source, exact_children, z_all[branch, seed, time]
        )
        topology_order = boundary_order(
            topology_pair, z_all[branch, seed, time]
        )
        if topology_order is None or topology_order[0] != int(
            row["topology_child"]
        ):
            failures.append(f"{sample_number}: topology selection")

        contexts = {
            "exact": (
                int(row["exact_seed"]),
                int(row["exact_time"]),
                int(row["exact_child"]),
            ),
            "sibling": (
                int(row["sibling_seed"]),
                int(row["sibling_time"]),
                int(row["sibling_child"]),
            ),
            "topology": (
                int(row["topology_seed"]),
                int(row["topology_time"]),
                int(row["topology_child"]),
            ),
            "seed": (
                int(row["seed_seed"]),
                int(row["seed_time"]),
                int(row["seed_child"]),
            )
            if row.get("seed_child", "")
            else None,
            "time": (
                int(row["time_seed"]),
                int(row["time_time"]),
                int(row["time_child"]),
            )
            if row.get("time_child", "")
            else None,
        }
        for label, context in contexts.items():
            if context is None:
                continue
            route_seed, route_time, child = context
            flow = float(
                (
                    h_all[branch, route_seed, route_time + 1, child]
                    - h_all[branch, route_seed, route_time, child]
                )
                / h_scale[branch, route_seed, child]
            )
            start_z = float(z_all[branch, route_seed, route_time, child])
            if not close(flow, number(row, f"{label}_flow")):
                failures.append(f"{sample_number}: {label} flow")
            if not close(start_z, number(row, f"{label}_start_z")):
                failures.append(f"{sample_number}: {label} start")
        if not (
            close(number(row, "structural_child_parent_weight"), 0.5)
            and close(number(row, "structural_path"), 3.5)
        ):
            failures.append(f"{sample_number}: structural coordinate")
    return {
        "sample_n": int(len(positions)),
        "failure_count": len(failures),
        "all_pass": not failures,
        "failures": failures[:20],
    }


def recompute_gates(
    evaluation: list[dict[str, str]], results: dict[str, object]
) -> dict[str, object]:
    eligibility = {
        "source_events_ge_5000": len(evaluation) >= 5000,
        "strata_ge_100": len(
            {(int(row["branch"]), int(row["seed"])) for row in evaluation}
        )
        >= 100,
    }
    exact_flow = finite(evaluation, "exact_flow")
    exact_positive = float(np.mean(exact_flow > 0))
    gates = {
        "pooled_exact_median_flow_positive": float(np.median(exact_flow)) > 0,
        "exact_positive_fraction_ge_055": exact_positive >= 0.55,
    }
    for branch, label in enumerate(("c2", "c4")):
        branch_rows = [
            row for row in evaluation if int(row["branch"]) == branch
        ]
        gates[f"{label}_median_exact_flow_positive"] = float(
            np.median(finite(branch_rows, "exact_flow"))
        ) > 0
    for comparator in COMPARATORS:
        comparator_flow = finite(evaluation, f"{comparator}_flow")
        eligibility[f"{comparator}_paired_ge_2000"] = comparator_flow.size >= 2000
        comparator_positive = float(np.mean(comparator_flow > 0))
        difference = finite(
            evaluation, f"exact_minus_{comparator}_flow"
        )
        gates[f"positive_fraction_advantage_ge_002_vs_{comparator}"] = (
            exact_positive - comparator_positive >= 0.02
        )
        gates[f"median_paired_flow_advantage_positive_vs_{comparator}"] = (
            float(np.median(difference)) > 0
        )
        gates[f"bootstrap_probability_ge_095_vs_{comparator}"] = float(
            results["evaluation_bootstrap"][comparator][
                "probability_exact_greater"
            ]
        ) >= 0.95
    eligible = all(eligibility.values())
    route_pass = all(gates.values())
    if not eligible:
        label = "INCONCLUSIVE"
    elif route_pass:
        label = "BOUNDARY-CHILD FLOW ROUTE SUPPORTED INSIDE THIS SIMULATOR"
    else:
        label = "BOUNDARY-CHILD FLOW ROUTE NOT SUPPORTED BY THIS IMPLEMENTATION"
    return {
        "exact_flow_median": float(np.median(exact_flow)),
        "exact_positive_fraction": exact_positive,
        "eligibility": eligibility,
        "routing_gates": gates,
        "label": label,
    }


def main() -> None:
    hashes = {
        "protocol_sha256": sha256(PROTOCOL),
        "fidelity_sha256": sha256(FIDELITY),
        "q27_cache_sha256": sha256(Q27_CACHE),
        "q28_cache_sha256": sha256(Q28_CACHE),
    }
    rows = read_csv(EVENTS)
    trials = read_csv(TRIALS)
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    q27 = np.load(Q27_CACHE)
    h_all = np.asarray(q27["closure"], dtype=np.float32)
    edges_all = np.asarray(q27["edges"], dtype=np.int8)
    h_scale = np.quantile(
        np.asarray(h_all[:, :, :250, :], dtype=np.float64), 0.95, axis=2
    )
    z_all = np.divide(
        h_all,
        h_scale[:, :, None, :],
        out=np.full(h_all.shape, np.nan, dtype=np.float32),
        where=h_scale[:, :, None, :] > EPS,
    )
    evaluation = [row for row in rows if row["split"] == "evaluation"]
    development = [row for row in rows if row["split"] == "development"]
    raw = raw_sample(rows, h_all, z_all, h_scale, edges_all)
    recomputed = recompute_gates(evaluation, results)
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
    saved_exact = results["splits"]["evaluation"]["routes"]["exact"]
    checks = {
        "hashes_match": hashes == EXPECTED_HASHES,
        "event_total_matches": len(rows)
        == int(results["splits"]["development"]["source_events"])
        + int(results["splits"]["evaluation"]["source_events"]),
        "development_rows_match": len(development)
        == int(results["splits"]["development"]["source_events"]),
        "evaluation_rows_match": len(evaluation)
        == int(results["splits"]["evaluation"]["source_events"]),
        "trial_rows_are_200": len(trials) == 200,
        "event_keys_unique": len(unique_keys) == len(rows),
        "raw_sample_passes": bool(raw["all_pass"]),
        "verdict_recomputes": recomputed["label"]
        == results["frozen_verdict"]["label"],
        "exact_median_matches": close(
            recomputed["exact_flow_median"],
            float(saved_exact["flow"]["median"]),
        ),
        "exact_positive_fraction_matches": close(
            recomputed["exact_positive_fraction"],
            float(saved_exact["positive_fraction"]),
        ),
        "structural_coordinate_is_fixed": (
            results["geometry"]["octave_projection"] == 0.5
            and results["geometry"]["complete_path"] == 3.5
            and results["geometry"]["scored_as_outcome"] is False
        ),
    }
    output = {
        "validator": "Q33B-independent-validator-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "hashes": hashes,
        "checks": checks,
        "raw_sample": raw,
        "recomputed": recomputed,
        "saved_verdict": results["frozen_verdict"]["label"],
        "limitations": [
            "The validator shares the source caches but not primary code.",
            "Saved bootstrap probabilities are gate-checked, not redrawn.",
            "Validation establishes reproducibility inside an already-open simulator.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "checks": checks}, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
