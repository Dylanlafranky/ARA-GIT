"""Generate PN29 ARA coordinates without calculating primality."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN29_RELATIONAL_THREE_RUNG_RIDGE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN29_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN29_RELATIONAL_THREE_RUNG_FROZEN_COORDINATES.csv"
SUMMARY = HERE / "PN29_RELATIONAL_THREE_RUNG_COORDINATE_SUMMARY.json"
PAIRS = ((1, 13), (3, 11), (5, 9))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def completion(number: int, wave: int) -> Fraction:
    return Fraction(1) if number % wave == 0 else Fraction(2 * wave, number)


def pair_coordinate(number: int, phase_a: int, phase_b: int) -> Fraction:
    a = completion(number, phase_a)
    b = completion(number, phase_b)
    return Fraction(2) * b / (a + b)


def coordinates(number: int) -> dict:
    pair_values = [pair_coordinate(number, a, b) for a, b in PAIRS]
    rung_0 = sum(pair_values, Fraction(0)) / 3
    epsilon_0 = rung_0 - 1
    rung_1 = 1 + epsilon_0 / 2
    rung_2 = 1 + epsilon_0 / 4
    distance_2 = abs(epsilon_0) / 4
    unresolved_by_declared_children = all(number % wave != 0 for wave in (3, 5, 9, 11, 13))
    return {
        "x_1_13_fraction": str(pair_values[0]),
        "x_1_13_decimal": f"{float(pair_values[0]):.15g}",
        "x_3_11_fraction": str(pair_values[1]),
        "x_3_11_decimal": f"{float(pair_values[1]):.15g}",
        "x_5_9_fraction": str(pair_values[2]),
        "x_5_9_decimal": f"{float(pair_values[2]):.15g}",
        "rung_0_fraction": str(rung_0),
        "rung_0_decimal": f"{float(rung_0):.15g}",
        "epsilon_0_fraction": str(epsilon_0),
        "epsilon_0_decimal": f"{float(epsilon_0):.15g}",
        "rung_1_fraction": str(rung_1),
        "rung_1_decimal": f"{float(rung_1):.15g}",
        "rung_2_fraction": str(rung_2),
        "rung_2_decimal": f"{float(rung_2):.15g}",
        "ridge_distance_2_fraction": str(distance_2),
        "ridge_distance_2_decimal": f"{float(distance_2):.15g}",
        "unresolved_by_declared_children": int(unresolved_by_declared_children),
    }


def main() -> None:
    for output in (COORDINATES, SUMMARY):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")
    manifest = json.loads(PROTOCOL_MANIFEST.read_text(encoding="utf-8"))
    if sha256(PROTOCOL) != manifest["protocol_sha256"]:
        raise RuntimeError("protocol hash mismatch")
    rows = []
    for number in range(15, 1000, 2):
        rows.append({"number": number, **coordinates(number)})
    with COORDINATES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "test_id": "PN29/RELATIONAL-THREE-RUNG-RIDGE/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "coordinate_file": COORDINATES.name,
        "coordinate_file_sha256": sha256(COORDINATES),
        "row_count": len(rows),
        "number_range": {"low_inclusive": 15, "high_inclusive": 999, "parity": "odd"},
        "primality_computed": False,
        "worked_example_35": {"number": 35, **coordinates(35)},
    }
    SUMMARY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
