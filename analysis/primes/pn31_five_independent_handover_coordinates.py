"""Generate PN31 independent child-wave coordinates without prime labels."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN31_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_FROZEN_COORDINATES.csv"
SUMMARY = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_COORDINATE_SUMMARY.json"
WAVES = (3, 5, 9, 11, 13)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def wave_state(number: int, wave: int) -> dict:
    remainder = number % wave
    position = Fraction(2 * remainder, wave)
    forward = Fraction(0) if remainder == 0 else Fraction(2) - position
    if remainder == 0:
        direction = "on"
    elif position < 1:
        direction = "leaving"
    elif position == 1:
        direction = "ridge"
    else:
        direction = "approaching"
    return {
        "remainder": remainder,
        "position": position,
        "forward": forward,
        "direction": direction,
    }


def grouped_order(states: dict[int, dict]) -> str:
    groups = {}
    for wave, state in states.items():
        groups.setdefault(state["forward"], []).append(wave)
    ordered = []
    for distance in sorted(groups):
        members = "+".join(str(wave) for wave in sorted(groups[distance]))
        ordered.append(members)
    return ">".join(ordered)


def coordinates(number: int) -> dict:
    states = {wave: wave_state(number, wave) for wave in WAVES}
    phase_a_distance = min(state["forward"] for state in states.values())
    phase_a_waves = tuple(
        wave for wave in WAVES if states[wave]["forward"] == phase_a_distance
    )
    row = {"number": number}
    for wave in WAVES:
        state = states[wave]
        row.update({
            f"remainder_{wave}": state["remainder"],
            f"x_{wave}_fraction": str(state["position"]),
            f"x_{wave}_decimal": f"{float(state['position']):.15g}",
            f"handover_distance_{wave}_fraction": str(state["forward"]),
            f"handover_distance_{wave}_decimal": f"{float(state['forward']):.15g}",
            f"direction_{wave}": state["direction"],
        })
    row.update({
        "phase_a_waves": "+".join(str(wave) for wave in phase_a_waves),
        "phase_a_tie_count": len(phase_a_waves),
        "phase_a_distance_fraction": str(phase_a_distance),
        "phase_a_distance_decimal": f"{float(phase_a_distance):.15g}",
        "five_wave_order": grouped_order(states),
        "approaching_count": sum(state["direction"] == "approaching" for state in states.values()),
        "leaving_count": sum(state["direction"] == "leaving" for state in states.values()),
        "on_handover_count": sum(state["direction"] == "on" for state in states.values()),
        "unresolved_by_five_children": int(all(number % wave != 0 for wave in WAVES)),
    })
    return row


def main() -> None:
    for output in (COORDINATES, SUMMARY):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")
    manifest = json.loads(PROTOCOL_MANIFEST.read_text(encoding="utf-8"))
    if sha256(PROTOCOL) != manifest["protocol_sha256"]:
        raise RuntimeError("protocol hash mismatch")

    rows = [coordinates(number) for number in range(2001, 3000, 2)]
    with COORDINATES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "test_id": "PN31/FIVE-INDEPENDENT-HANDOVER/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "coordinate_file": COORDINATES.name,
        "coordinate_file_sha256": sha256(COORDINATES),
        "row_count": len(rows),
        "number_range": {"low_inclusive": 2001, "high_inclusive": 2999, "parity": "odd"},
        "waves": list(WAVES),
        "wave_1_included": False,
        "fixed_pairs_used": False,
        "primality_computed": False,
        "worked_examples": {str(number): coordinates(number) for number in (35, 36, 45, 2001)},
    }
    SUMMARY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
