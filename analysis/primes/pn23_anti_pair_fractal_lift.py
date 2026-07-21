"""PN23 exact recursive anti-pair compression test for wheel-sieve lifts."""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN23_ANTI_PAIR_FRACTAL_LIFT_RESULTS.json"
SUMMARY = HERE / "PN23_ANTI_PAIR_FRACTAL_LIFT_RUNGS.csv"
PATHS = HERE / "PN23_ANTI_PAIR_FRACTAL_LIFT_WORKED_PATHS.csv"
START_MODULUS = 14
GATES = (3, 5, 11, 13, 17)
HOLDOUT_GATE = 17


def direct_residues(modulus: int) -> list[int]:
    return [value for value in range(1, modulus) if math.gcd(value, modulus) == 1]


def pair_representatives(residues: list[int], modulus: int) -> list[int]:
    residue_set = set(residues)
    for value in residues:
        if modulus - value not in residue_set:
            raise AssertionError(f"missing anti-partner for {value} modulo {modulus}")
    return [value for value in residues if value < modulus - value]


def lift_rung(modulus: int, gate: int, representatives: list[int], phase: str) -> tuple[dict, list[int], list[dict]]:
    if math.gcd(modulus, gate) != 1:
        raise ValueError(f"gate {gate} already divides modulus {modulus}")
    inverse = pow(modulus, -1, gate)
    new_modulus = modulus * gate
    next_representatives: set[int] = set()
    collision_failures: list[str] = []
    exact_ridge_failures: list[str] = []
    duplicate_child_representatives = 0
    direct_ridge_count = 0
    max_ridge_error = 0.0
    worked_paths: list[dict] = []

    for parent_index, representative in enumerate(representatives):
        opposite = modulus - representative
        killed_a = (-representative * inverse) % gate
        killed_b = gate - 1 - killed_a

        actual_killed_a = [
            copy for copy in range(gate)
            if (representative + copy * modulus) % gate == 0
        ]
        actual_killed_b = [
            copy for copy in range(gate)
            if (opposite + copy * modulus) % gate == 0
        ]
        if actual_killed_a != [killed_a]:
            collision_failures.append(
                f"M={modulus}, p={gate}, r={representative}: A predicted {killed_a}, actual {actual_killed_a}"
            )
        if actual_killed_b != [killed_b]:
            collision_failures.append(
                f"M={modulus}, p={gate}, r={representative}: B predicted {killed_b}, actual {actual_killed_b}"
            )

        if killed_a + killed_b != gate - 1:
            exact_ridge_failures.append(
                f"M={modulus}, p={gate}, r={representative}: {killed_a}+{killed_b}!={gate-1}"
            )
        x_a = 2.0 * killed_a / (gate - 1)
        x_b = 2.0 * killed_b / (gate - 1)
        ridge_error = abs((x_a + x_b) / 2.0 - 1.0)
        max_ridge_error = max(max_ridge_error, ridge_error)
        if killed_a == killed_b == (gate - 1) // 2:
            direct_ridge_count += 1

        # Fractal compression step: carry only the A-side adult lane. Every
        # surviving copy determines its B-side partner by reflection in Mp.
        pair_children: set[int] = set()
        branch_a_survivors: list[int] = []
        for copy in range(gate):
            if copy == killed_a:
                continue
            survivor = representative + copy * modulus
            branch_a_survivors.append(survivor)
            child_representative = min(survivor, new_modulus - survivor)
            if child_representative in next_representatives:
                duplicate_child_representatives += 1
            next_representatives.add(child_representative)
            pair_children.add(child_representative)

        if len(pair_children) != gate - 1:
            collision_failures.append(
                f"M={modulus}, p={gate}, r={representative}: produced {len(pair_children)} child pairs"
            )

        if modulus == START_MODULUS and gate == GATES[0] or parent_index < 3:
            branch_b_survivors = [
                opposite + copy * modulus
                for copy in range(gate)
                if copy != killed_b
            ]
            worked_paths.append({
                "phase": phase,
                "parent_modulus": modulus,
                "gate": gate,
                "new_modulus": new_modulus,
                "parent_representative_A": representative,
                "reconstructed_parent_B": opposite,
                "killed_copy_A": killed_a,
                "predicted_killed_copy_B": killed_b,
                "x_A": x_a,
                "x_B": x_b,
                "ridge_mean": (x_a + x_b) / 2.0,
                "direct_ridge": killed_a == killed_b,
                "killed_value_A": representative + killed_a * modulus,
                "killed_value_B": opposite + killed_b * modulus,
                "A_survivors": branch_a_survivors,
                "B_survivors_for_audit_only": branch_b_survivors,
                "next_pair_representatives_from_A_only": sorted(pair_children),
            })

    next_representatives_list = sorted(next_representatives)
    predicted_residues = sorted(
        next_representatives_list
        + [new_modulus - value for value in next_representatives_list]
    )
    direct = direct_residues(new_modulus)
    direct_representatives = pair_representatives(direct, new_modulus)
    missing_residues = sorted(set(direct) - set(predicted_residues))
    extra_residues = sorted(set(predicted_residues) - set(direct))
    missing_representatives = sorted(set(direct_representatives) - set(next_representatives_list))
    extra_representatives = sorted(set(next_representatives_list) - set(direct_representatives))
    expected_pair_count = len(representatives) * (gate - 1)

    checks = {
        "all_A_collisions_exact": not any("A predicted" in failure for failure in collision_failures),
        "all_B_collisions_exact": not any("B predicted" in failure for failure in collision_failures),
        "exact_integer_ridge_identity": not exact_ridge_failures,
        "pair_growth_exact": len(next_representatives_list) == expected_pair_count,
        "no_duplicate_child_representatives": duplicate_child_representatives == 0,
        "residue_reconstruction_exact": predicted_residues == direct,
        "representative_reconstruction_exact": next_representatives_list == direct_representatives,
    }
    row = {
        "phase": phase,
        "parent_modulus": modulus,
        "gate": gate,
        "new_modulus": new_modulus,
        "parent_residue_count": 2 * len(representatives),
        "parent_pair_count": len(representatives),
        "expected_child_pair_count": expected_pair_count,
        "child_pair_count": len(next_representatives_list),
        "child_residue_count": len(predicted_residues),
        "direct_residue_count": len(direct),
        "direct_ridge_count": direct_ridge_count,
        "coarse_pair_ridge_count": len(representatives),
        "max_ridge_error": max_ridge_error,
        "collision_failure_count": len(collision_failures),
        "integer_ridge_failure_count": len(exact_ridge_failures),
        "missing_residue_count": len(missing_residues),
        "extra_residue_count": len(extra_residues),
        "missing_representative_count": len(missing_representatives),
        "extra_representative_count": len(extra_representatives),
        "duplicate_child_representatives": duplicate_child_representatives,
        "stored_lane_compression_ratio": len(direct) / len(next_representatives_list),
        "checks": checks,
        "pass": all(checks.values()),
        "failure_examples": (collision_failures + exact_ridge_failures)[:10],
        "missing_residue_examples": missing_residues[:10],
        "extra_residue_examples": extra_residues[:10],
    }
    return row, next_representatives_list, worked_paths


def write_summary(rows: list[dict]) -> None:
    fields = [
        "phase", "parent_modulus", "gate", "new_modulus",
        "parent_residue_count", "parent_pair_count",
        "expected_child_pair_count", "child_pair_count",
        "child_residue_count", "direct_residue_count",
        "direct_ridge_count", "coarse_pair_ridge_count",
        "max_ridge_error", "collision_failure_count",
        "integer_ridge_failure_count", "missing_residue_count",
        "extra_residue_count", "missing_representative_count",
        "extra_representative_count", "duplicate_child_representatives",
        "stored_lane_compression_ratio", "pass",
    ]
    with SUMMARY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


def write_paths(rows: list[dict]) -> None:
    fields = [
        "phase", "parent_modulus", "gate", "new_modulus",
        "parent_representative_A", "reconstructed_parent_B",
        "killed_copy_A", "predicted_killed_copy_B", "x_A", "x_B",
        "ridge_mean", "direct_ridge", "killed_value_A", "killed_value_B",
        "A_survivors", "B_survivors_for_audit_only",
        "next_pair_representatives_from_A_only",
    ]
    with PATHS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                field: json.dumps(row[field]) if isinstance(row[field], list) else row[field]
                for field in fields
            })


def main() -> None:
    for output in (RESULTS, SUMMARY, PATHS):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    starting_residues = direct_residues(START_MODULUS)
    representatives = pair_representatives(starting_residues, START_MODULUS)
    modulus = START_MODULUS
    rung_rows: list[dict] = []
    worked_paths: list[dict] = []

    for gate in GATES:
        phase = "held_out" if gate == HOLDOUT_GATE else "development"
        row, representatives, samples = lift_rung(modulus, gate, representatives, phase)
        rung_rows.append(row)
        worked_paths.extend(samples)
        modulus *= gate

    development_pass = all(row["pass"] for row in rung_rows if row["phase"] == "development")
    held_out_rows = [row for row in rung_rows if row["phase"] == "held_out"]
    held_out_pass = len(held_out_rows) == 1 and held_out_rows[0]["pass"]
    all_pass = development_pass and held_out_pass

    payload = {
        "test_id": "PN23/ANTI-PAIR-FRACTAL-LIFT/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": "PN23_ANTI_PAIR_FRACTAL_LIFT_PROTOCOL_v1_FROZEN.md",
        "status": "PASS — LOSSLESS RECURSIVE ANTI-PAIR COMPRESSION" if all_pass else "FAIL",
        "question": (
            "Can one stored adult representative per reversible residue pair reconstruct both child branches "
            "exactly at every wheel rung?"
        ),
        "starting_state": {
            "modulus": START_MODULUS,
            "residues": starting_residues,
            "anti_pairs": [[value, START_MODULUS - value] for value in pair_representatives(starting_residues, START_MODULUS)],
            "stored_representatives": pair_representatives(starting_residues, START_MODULUS),
        },
        "frozen_ladder": {
            "development_gates": list(GATES[:-1]),
            "held_out_gate": HOLDOUT_GATE,
            "moduli": [START_MODULUS] + [row["new_modulus"] for row in rung_rows],
        },
        "rungs": rung_rows,
        "worked_paths": worked_paths,
        "decision": {
            "development_pass": development_pass,
            "held_out_pass": held_out_pass,
            "all_rungs_pass": all_pass,
            "rule_changes_after_freeze": 0,
            "final_modulus": modulus,
            "final_stored_pair_representatives": len(representatives),
            "final_reconstructed_residues": 2 * len(representatives),
            "compression_vs_individual_residue_lanes": 2.0,
            "fresh_87_bit_anchor_used": False,
            "prime_locator_claim_supported": False,
            "interpretation": (
                "The same anti-pair rule is a lossless recursive coordinate system for the wheel sieve. "
                "It halves the stored residue lanes and exposes an exact ARA=1 pair ridge, but each new prime "
                "gate still creates p-1 child pairs per parent pair. This is an exact CRT/wheel crosswalk, not "
                "a constant-cost next-prime shortcut."
            ),
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(rung_rows)
    write_paths(worked_paths)
    print(json.dumps({
        "status": payload["status"],
        "ladder": payload["frozen_ladder"],
        "rungs": [
            {
                key: row[key]
                for key in (
                    "phase", "parent_modulus", "gate", "new_modulus",
                    "parent_pair_count", "child_pair_count", "direct_ridge_count",
                    "max_ridge_error", "stored_lane_compression_ratio", "pass",
                )
            }
            for row in rung_rows
        ],
        "decision": payload["decision"],
    }, indent=2))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
