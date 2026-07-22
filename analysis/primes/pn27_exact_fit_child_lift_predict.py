"""Freeze PN27 ARA predictions without calculating or reading primality labels."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN27_EXACT_FIT_CHILD_LIFT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN27_PROTOCOL_FREEZE_MANIFEST.json"
PREDICTIONS = HERE / "PN27_EXACT_FIT_CHILD_LIFT_FROZEN_PREDICTIONS.csv"
PREDICTION_SUMMARY = HERE / "PN27_EXACT_FIT_CHILD_LIFT_PREDICTION_SUMMARY.json"

WAVES = (1, 3, 5, 9, 11, 13)
RANGES = (
    ("low", 73_000_000, 73_500_000, 27001, 27101),
    ("middle", 73_000_000_000, 73_000_500_000, 27002, 27102),
    ("high", 730_000_000_000, 730_000_500_000, 27003, 27103),
)
N_PER_PARITY = 10_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def largest_exact_wave(number: int) -> int:
    """Largest declared child-wave label that divides number exactly."""
    return max(wave for wave in WAVES if number % wave == 0)


def prediction(number: int) -> dict:
    phase_a = largest_exact_wave(number)
    phase_b = 14 - phase_a
    phase_b_completion = Fraction(2 * phase_b, number)
    child_deficit = 1 - phase_b_completion
    child_identity = phase_a + 2 * phase_b
    upper_reference = number + child_identity
    upper_position = Fraction(number, upper_reference)
    upper_deficit = 1 - upper_position
    predicted = upper_reference + 1
    return {
        "phase_a": phase_a,
        "phase_b": phase_b,
        "phase_a_completion": "1",
        "phase_b_completion_fraction": str(phase_b_completion),
        "phase_b_completion_decimal": f"{float(phase_b_completion):.15g}",
        "child_deficit_fraction": str(child_deficit),
        "child_deficit_decimal": f"{float(child_deficit):.15g}",
        "child_identity": child_identity,
        "upper_reference": upper_reference,
        "upper_position_fraction": str(upper_position),
        "upper_position_decimal": f"{float(upper_position):.15g}",
        "upper_deficit_fraction": str(upper_deficit),
        "upper_deficit_decimal": f"{float(upper_deficit):.15g}",
        "crossing_step": 1,
        "offset": predicted - number,
        "predicted_candidate": predicted,
    }


def parity_range(low: int, high: int, parity: str) -> range:
    wanted = 1 if parity == "odd" else 0
    start = low if low % 2 == wanted else low + 1
    return range(start, high, 2)


def main() -> None:
    for output in (PREDICTIONS, PREDICTION_SUMMARY):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite frozen artifact: {output.name}")

    manifest = json.loads(PROTOCOL_MANIFEST.read_text(encoding="utf-8"))
    if sha256(PROTOCOL) != manifest["protocol_sha256"]:
        raise RuntimeError("protocol hash does not match the freeze manifest")

    rows: list[dict] = []
    for scale, low, high, odd_seed, even_seed in RANGES:
        for parity, seed in (("odd", odd_seed), ("even", even_seed)):
            anchors = sorted(
                random.Random(seed).sample(parity_range(low, high, parity), N_PER_PARITY)
            )
            for number in anchors:
                row = {
                    "test_id": "PN27/EXACT-FIT-CHILD-LIFT/v1",
                    "scale": scale,
                    "parity": parity,
                    "anchor": number,
                    "sampling_seed": seed,
                }
                row.update(prediction(number))
                rows.append(row)

    fieldnames = list(rows[0])
    with PREDICTIONS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    example = prediction(35)
    summary = {
        "test_id": "PN27/EXACT-FIT-CHILD-LIFT/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "prediction_file": PREDICTIONS.name,
        "prediction_file_sha256": sha256(PREDICTIONS),
        "row_count": len(rows),
        "odd_primary_rows": sum(row["parity"] == "odd" for row in rows),
        "even_control_rows": sum(row["parity"] == "even" for row in rows),
        "primality_computed": False,
        "nearby_prime_labels_read": False,
        "protected_87_bit_anchor_used": False,
        "worked_example_35": {"anchor": 35, **example},
    }
    PREDICTION_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
