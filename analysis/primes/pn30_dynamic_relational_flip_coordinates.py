"""Generate PN30 dynamic-flip ARA coordinates without calculating primality."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN30_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_FROZEN_COORDINATES.csv"
SUMMARY = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_COORDINATE_SUMMARY.json"
PAIRS = ((1, 13), (3, 11), (5, 9))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def completion(number: int, wave: int) -> Fraction:
    return Fraction(1) if number % wave == 0 else Fraction(2 * wave, number)


def normalized_phase(number: int, wave: int) -> Fraction:
    return Fraction(number % wave, wave)


def oriented_pair(number: int, left: int, right: int) -> dict:
    phase_left = normalized_phase(number, left)
    phase_right = normalized_phase(number, right)
    left_completion = completion(number, left)
    right_completion = completion(number, right)

    if phase_left < phase_right:
        phase_a, phase_b = left, right
        completion_a, completion_b = left_completion, right_completion
        orientation = f"{left}->{right}"
        tie = False
    elif phase_right < phase_left:
        phase_a, phase_b = right, left
        completion_a, completion_b = right_completion, left_completion
        orientation = f"{right}->{left}"
        tie = False
    else:
        phase_a, phase_b = left, right
        completion_a, completion_b = left_completion, right_completion
        orientation = "tie"
        tie = True

    dynamic_coordinate = (
        Fraction(1)
        if tie
        else Fraction(2) * completion_b / (completion_a + completion_b)
    )
    static_coordinate = Fraction(2) * right_completion / (left_completion + right_completion)
    return {
        "left_phase": phase_left,
        "right_phase": phase_right,
        "phase_a": phase_a,
        "phase_b": phase_b,
        "orientation": orientation,
        "tie": tie,
        "dynamic_coordinate": dynamic_coordinate,
        "static_coordinate": static_coordinate,
    }


def coordinates(number: int) -> dict:
    details = [oriented_pair(number, left, right) for left, right in PAIRS]
    dynamic_values = [item["dynamic_coordinate"] for item in details]
    static_values = [item["static_coordinate"] for item in details]

    dynamic_rung_0 = sum(dynamic_values, Fraction(0)) / 3
    dynamic_epsilon_0 = dynamic_rung_0 - 1
    dynamic_rung_1 = 1 + dynamic_epsilon_0 / 2
    dynamic_rung_2 = 1 + dynamic_epsilon_0 / 4
    dynamic_distance_2 = abs(dynamic_epsilon_0) / 4

    static_rung_0 = sum(static_values, Fraction(0)) / 3
    static_epsilon_0 = static_rung_0 - 1
    static_distance_2 = abs(static_epsilon_0) / 4

    row = {"number": number}
    for (left, right), item in zip(PAIRS, details):
        key = f"{left}_{right}"
        row.update({
            f"theta_{left}_fraction": str(item["left_phase"]),
            f"theta_{right}_fraction": str(item["right_phase"]),
            f"orientation_{key}": item["orientation"],
            f"phase_a_{key}": item["phase_a"],
            f"phase_b_{key}": item["phase_b"],
            f"tie_{key}": int(item["tie"]),
            f"x_dynamic_{key}_fraction": str(item["dynamic_coordinate"]),
            f"x_dynamic_{key}_decimal": f"{float(item['dynamic_coordinate']):.15g}",
            f"x_static_{key}_fraction": str(item["static_coordinate"]),
            f"x_static_{key}_decimal": f"{float(item['static_coordinate']):.15g}",
        })

    row.update({
        "dynamic_rung_0_fraction": str(dynamic_rung_0),
        "dynamic_rung_0_decimal": f"{float(dynamic_rung_0):.15g}",
        "dynamic_epsilon_0_fraction": str(dynamic_epsilon_0),
        "dynamic_epsilon_0_decimal": f"{float(dynamic_epsilon_0):.15g}",
        "dynamic_rung_1_fraction": str(dynamic_rung_1),
        "dynamic_rung_1_decimal": f"{float(dynamic_rung_1):.15g}",
        "dynamic_rung_2_fraction": str(dynamic_rung_2),
        "dynamic_rung_2_decimal": f"{float(dynamic_rung_2):.15g}",
        "dynamic_ridge_distance_2_fraction": str(dynamic_distance_2),
        "dynamic_ridge_distance_2_decimal": f"{float(dynamic_distance_2):.15g}",
        "static_rung_0_fraction": str(static_rung_0),
        "static_rung_0_decimal": f"{float(static_rung_0):.15g}",
        "static_epsilon_0_fraction": str(static_epsilon_0),
        "static_epsilon_0_decimal": f"{float(static_epsilon_0):.15g}",
        "static_ridge_distance_2_fraction": str(static_distance_2),
        "static_ridge_distance_2_decimal": f"{float(static_distance_2):.15g}",
        "unresolved_by_declared_children": int(
            all(number % wave != 0 for wave in (3, 5, 9, 11, 13))
        ),
    })
    return row


def main() -> None:
    for output in (COORDINATES, SUMMARY):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")
    manifest = json.loads(PROTOCOL_MANIFEST.read_text(encoding="utf-8"))
    if sha256(PROTOCOL) != manifest["protocol_sha256"]:
        raise RuntimeError("protocol hash mismatch")

    rows = [coordinates(number) for number in range(1001, 2000, 2)]
    with COORDINATES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    orientation_counts = {}
    for left, right in PAIRS:
        key = f"orientation_{left}_{right}"
        counts = {}
        for row in rows:
            counts[row[key]] = counts.get(row[key], 0) + 1
        orientation_counts[f"{left}_{right}"] = counts

    payload = {
        "test_id": "PN30/DYNAMIC-RELATIONAL-FLIP/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "coordinate_file": COORDINATES.name,
        "coordinate_file_sha256": sha256(COORDINATES),
        "row_count": len(rows),
        "number_range": {"low_inclusive": 1001, "high_inclusive": 1999, "parity": "odd"},
        "primality_computed": False,
        "orientation_counts": orientation_counts,
        "worked_examples": {
            str(number): coordinates(number) for number in (1001, 1003, 1005)
        },
    }
    SUMMARY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
