"""Independent arithmetic and provenance checks for MX8 saved outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = json.loads(args.results.read_text(encoding="utf-8"))

    vertices = np.asarray(results["mathematical_identity"]["vertices_xyz"], dtype=float)
    gram = vertices @ vertices.T
    expected_gram = np.full((4, 4), -1.0)
    np.fill_diagonal(expected_gram, 3.0)
    distances = np.linalg.norm(vertices[:, None, :] - vertices[None, :, :], axis=-1)
    edge_values = distances[np.triu_indices(4, 1)]

    split = results["frozen_split"]
    development = set(split["development"])
    quarantine = set(split["quarantined_unused"])
    test = set(split["test"])
    split_disjoint = not (development & quarantine or development & test or quarantine & test)

    source = Path(results["source"]["directory"])
    hash_checks = {}
    for iteration, expected in results["source"]["sha256"].items():
        path = source / f"data{int(iteration):08d}.h5"
        observed = sha256(path)
        hash_checks[iteration] = {"expected": expected, "observed": observed, "match": observed == expected}

    rows = results["per_snapshot_error_sums"]
    target_sq = np.asarray([row["target_sq"] for row in rows], dtype=float)
    additive_sq = np.asarray([row["additive_error_sq"] for row in rows], dtype=float)
    relation_sq = np.asarray([row["relation_error_sq"] for row in rows], dtype=float)
    additive_l2 = float(np.sqrt(np.sum(additive_sq) / np.sum(target_sq)))
    relation_l2 = float(np.sqrt(np.sum(relation_sq) / np.sum(target_sq)))
    improvement = (additive_l2 - relation_l2) / additive_l2

    rng = np.random.default_rng(20260715)
    indices = rng.integers(0, len(rows), size=(10_000, len(rows)))
    boot_target = np.sum(target_sq[indices], axis=1)
    boot_additive = np.sqrt(np.sum(additive_sq[indices], axis=1) / boot_target)
    boot_relation = np.sqrt(np.sum(relation_sq[indices], axis=1) / boot_target)
    boot_improvement = (boot_additive - boot_relation) / boot_additive
    interval = np.percentile(boot_improvement, [2.5, 50.0, 97.5])

    # Independent exact Walsh/Hadamard reconstruction of an arbitrary four-route table.
    table = np.array([2.3, 0.7, 1.1, 4.2])
    x = np.array([1.0, 1.0, -1.0, -1.0])
    y = np.array([1.0, -1.0, 1.0, -1.0])
    relation = x * y
    basis = np.column_stack([np.ones(4), x, y, relation])
    coefficients = basis.T @ table / 4.0
    reconstructed = basis @ coefficients

    saved_gate = results["primary_relation_vs_additive_gate"]
    checks = {
        "tetrahedron_gram_exact": bool(np.allclose(gram, expected_gram, rtol=0, atol=0)),
        "six_edges_equal_2sqrt2": bool(np.allclose(edge_values, 2 * np.sqrt(2), rtol=1e-15, atol=1e-15)),
        "parity_closure_exact": bool(np.all(np.prod(vertices, axis=1) == 1)),
        "hadamard_four_route_reconstruction": bool(np.allclose(reconstructed, table, rtol=1e-15, atol=1e-15)),
        "frozen_splits_disjoint": bool(split_disjoint),
        "all_source_hashes_match": bool(all(item["match"] for item in hash_checks.values())),
        "saved_additive_relative_l2_reproduced": bool(
            np.isclose(additive_l2, results["models"]["additive"]["relative_l2"], rtol=1e-14, atol=0)
        ),
        "saved_relation_relative_l2_reproduced": bool(
            np.isclose(relation_l2, results["models"]["relation"]["relative_l2"], rtol=1e-14, atol=0)
        ),
        "saved_improvement_reproduced": bool(
            np.isclose(improvement, saved_gate["observed_relative_l2_improvement_fraction"], rtol=1e-11, atol=1e-16)
        ),
        "saved_bootstrap_interval_reproduced": bool(
            np.allclose(interval, saved_gate["bootstrap_improvement_p2_5_p50_p97_5"], rtol=1e-14, atol=0)
        ),
    }
    validation = {
        "test": "MX8 saved-output validation",
        "checks": checks,
        "all_checks_pass": bool(all(checks.values())),
        "recomputed": {
            "additive_relative_l2": additive_l2,
            "relation_relative_l2": relation_l2,
            "improvement_fraction": improvement,
            "bootstrap_interval": interval.tolist(),
            "tetrahedron_gram": gram.tolist(),
            "edge_lengths": edge_values.tolist(),
            "hadamard_coefficients_mu_alpha_beta_gamma": coefficients.tolist(),
            "hadamard_max_abs_reconstruction_error": float(np.max(np.abs(reconstructed - table))),
        },
        "source_hash_checks": hash_checks,
    }
    args.output.write_text(json.dumps(validation, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(validation, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
