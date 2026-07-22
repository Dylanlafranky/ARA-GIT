"""Freeze PN28 three-child residual predictions without primality labels."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN28_PROTOCOL_FREEZE_MANIFEST.json"
PREDICTIONS = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_FROZEN_PREDICTIONS.csv"
SUMMARY = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_PREDICTION_SUMMARY.json"

WAVES = (1, 3, 5, 9, 11, 13)
PAIRS = ((1, 13), (3, 11), (5, 9))
RANGES = (
    ("low", 83_000_000, 83_500_000, 28001, 28101),
    ("middle", 83_000_000_000, 83_000_500_000, 28002, 28102),
    ("high", 830_000_000_000, 830_000_500_000, 28003, 28103),
)
N_PER_PARITY = 10_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def completion(number: int, wave: int) -> Fraction:
    return Fraction(1) if number % wave == 0 else Fraction(2 * wave, number)


def imbalance(number: int, phase_a: int, phase_b: int) -> Fraction:
    value_a = completion(number, phase_a)
    value_b = completion(number, phase_b)
    return (value_b - value_a) / (value_a + value_b)


def round_half_away(value: Fraction) -> int:
    if value < 0:
        return -round_half_away(-value)
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


def prediction(number: int) -> dict:
    phase_a = max(wave for wave in WAVES if number % wave == 0)
    phase_b = 14 - phase_a
    base_candidate = number + phase_a + 2 * phase_b + 1
    differences = [imbalance(number, left, right) for left, right in PAIRS]
    epsilon_0 = sum(differences, Fraction(0)) / 3
    child_coordinate = 1 + epsilon_0
    epsilon_2 = 4 * epsilon_0
    integer_adjustment = round_half_away(epsilon_2)
    corrected_candidate = base_candidate + integer_adjustment
    return {
        "phase_a": phase_a,
        "phase_b": phase_b,
        "base_offset": base_candidate - number,
        "base_candidate": base_candidate,
        "d_1_13_fraction": str(differences[0]),
        "d_1_13_decimal": f"{float(differences[0]):.15g}",
        "d_3_11_fraction": str(differences[1]),
        "d_3_11_decimal": f"{float(differences[1]):.15g}",
        "d_5_9_fraction": str(differences[2]),
        "d_5_9_decimal": f"{float(differences[2]):.15g}",
        "child_coordinate_fraction": str(child_coordinate),
        "child_coordinate_decimal": f"{float(child_coordinate):.15g}",
        "epsilon_0_fraction": str(epsilon_0),
        "epsilon_0_decimal": f"{float(epsilon_0):.15g}",
        "epsilon_2_fraction": str(epsilon_2),
        "epsilon_2_decimal": f"{float(epsilon_2):.15g}",
        "integer_adjustment": integer_adjustment,
        "corrected_offset": corrected_candidate - number,
        "corrected_candidate": corrected_candidate,
    }


def parity_range(low: int, high: int, parity: str) -> range:
    wanted = 1 if parity == "odd" else 0
    start = low if low % 2 == wanted else low + 1
    return range(start, high, 2)


def main() -> None:
    for output in (PREDICTIONS, SUMMARY):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite frozen artifact: {output.name}")
    manifest = json.loads(PROTOCOL_MANIFEST.read_text(encoding="utf-8"))
    if sha256(PROTOCOL) != manifest["protocol_sha256"]:
        raise RuntimeError("protocol hash mismatch")

    rows: list[dict] = []
    for scale, low, high, odd_seed, even_seed in RANGES:
        for parity, seed in (("odd", odd_seed), ("even", even_seed)):
            anchors = sorted(random.Random(seed).sample(parity_range(low, high, parity), N_PER_PARITY))
            for number in anchors:
                row = {
                    "test_id": "PN28/THREE-CHILD-RESIDUAL-LIFT/v1",
                    "scale": scale,
                    "parity": parity,
                    "anchor": number,
                    "sampling_seed": seed,
                }
                row.update(prediction(number))
                rows.append(row)

    with PREDICTIONS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    example = prediction(35)
    payload = {
        "test_id": "PN28/THREE-CHILD-RESIDUAL-LIFT/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "prediction_file": PREDICTIONS.name,
        "prediction_file_sha256": sha256(PREDICTIONS),
        "row_count": len(rows),
        "odd_rows": sum(row["parity"] == "odd" for row in rows),
        "even_rows": sum(row["parity"] == "even" for row in rows),
        "primality_computed": False,
        "nearby_prime_labels_read": False,
        "protected_87_bit_anchor_used": False,
        "worked_example_35": {"anchor": 35, **example},
    }
    SUMMARY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
