"""Generate PN32 child/parent ARA locks and relation-broken controls without labels."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN32_DOUBLE_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md"
PROTOCOL_MANIFEST = HERE / "PN32_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN32_DOUBLE_INFORMATION_LOCK_FROZEN_COORDINATES.csv"
BROKEN_MAPS = HERE / "PN32_RELATION_BROKEN_PARENT_INDEXES.json"
SUMMARY = HERE / "PN32_DOUBLE_INFORMATION_LOCK_COORDINATE_SUMMARY.json"
WAVES = (3, 5, 9, 11, 13)
BROKEN_SEED = 32004
BROKEN_CONTROLS = 1_000
BLOCK_SIZE = 50


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


def order_groups(states: dict[int, dict]) -> list[tuple[int, ...]]:
    groups: dict[Fraction, list[int]] = {}
    for wave, state in states.items():
        groups.setdefault(state["forward"], []).append(wave)
    return [tuple(sorted(groups[distance])) for distance in sorted(groups)]


def order_text(groups: list[tuple[int, ...]]) -> str:
    return ">".join("+".join(str(wave) for wave in group) for group in groups)


def unique_order(groups: list[tuple[int, ...]]) -> tuple[int, ...] | None:
    if len(groups) != len(WAVES):
        return None
    return tuple(group[0] for group in groups)


def relative_permutation(child_order: tuple[int, ...], parent_order: tuple[int, ...]) -> str:
    parent_rank = {wave: rank + 1 for rank, wave in enumerate(parent_order)}
    return "-".join(str(parent_rank[wave]) for wave in child_order)


def rung_lock(number: int) -> dict:
    states = {wave: wave_state(number, wave) for wave in WAVES}
    groups = order_groups(states)
    return {
        "states": states,
        "groups": groups,
        "order_text": order_text(groups),
        "unique_order": unique_order(groups),
        "phase_a": "+".join(str(wave) for wave in groups[0]),
        "phase_b": "+".join(str(wave) for wave in groups[-1]),
    }


def coordinates(number: int) -> dict:
    child = rung_lock(number)
    parent = rung_lock(2 * number)
    unresolved = int(all(number % wave != 0 for wave in WAVES))
    if unresolved and (child["unique_order"] is None or parent["unique_order"] is None):
        raise RuntimeError(f"unexpected hard-control order tie at {number}")

    relation = "TIED"
    if child["unique_order"] is not None and parent["unique_order"] is not None:
        relation = relative_permutation(child["unique_order"], parent["unique_order"])

    row: dict[str, object] = {
        "number": number,
        "parent_number": 2 * number,
        "child_phase_a": child["phase_a"],
        "child_phase_b": child["phase_b"],
        "child_order": child["order_text"],
        "parent_phase_a": parent["phase_a"],
        "parent_phase_b": parent["phase_b"],
        "parent_order": parent["order_text"],
        "closure_relation": relation,
        "hex_lock_signature": "|".join((
            child["phase_a"], child["phase_b"], child["order_text"],
            parent["phase_a"], parent["phase_b"], parent["order_text"],
        )),
        "child_order_tied": int(child["unique_order"] is None),
        "parent_order_tied": int(parent["unique_order"] is None),
        "unresolved_by_five_children": unresolved,
    }
    for prefix, lock in (("child", child), ("parent", parent)):
        for wave in WAVES:
            state = lock["states"][wave]
            row.update({
                f"{prefix}_remainder_{wave}": state["remainder"],
                f"{prefix}_x_{wave}_fraction": str(state["position"]),
                f"{prefix}_x_{wave}_decimal": f"{float(state['position']):.15g}",
                f"{prefix}_handover_distance_{wave}_fraction": str(state["forward"]),
                f"{prefix}_handover_distance_{wave}_decimal": f"{float(state['forward']):.15g}",
                f"{prefix}_direction_{wave}": state["direction"],
            })
    return row


def broken_parent_maps(rows: list[dict]) -> list[list[int]]:
    rng = random.Random(BROKEN_SEED)
    controls = []
    for _ in range(BROKEN_CONTROLS):
        mapping = list(range(len(rows)))
        for start in range(0, len(rows), BLOCK_SIZE):
            eligible = [
                index for index in range(start, min(start + BLOCK_SIZE, len(rows)))
                if int(rows[index]["unresolved_by_five_children"])
            ]
            shuffled = eligible.copy()
            rng.shuffle(shuffled)
            for child_index, parent_index in zip(eligible, shuffled):
                mapping[child_index] = parent_index
        controls.append(mapping)
    return controls


def main() -> None:
    for output in (COORDINATES, BROKEN_MAPS, SUMMARY):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")
    manifest = json.loads(PROTOCOL_MANIFEST.read_text(encoding="utf-8"))
    if sha256(PROTOCOL) != manifest["protocol_sha256"]:
        raise RuntimeError("protocol hash mismatch")

    rows = [coordinates(number) for number in range(3001, 4000, 2)]
    with COORDINATES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    maps = broken_parent_maps(rows)
    BROKEN_MAPS.write_text(json.dumps({
        "test_id": "PN32/DOUBLE-INFORMATION-LOCK/v1",
        "seed": BROKEN_SEED,
        "control_count": BROKEN_CONTROLS,
        "block_size": BLOCK_SIZE,
        "row_count": len(rows),
        "parent_index_maps": maps,
    }, separators=(",", ":")) + "\n", encoding="utf-8")

    payload = {
        "test_id": "PN32/DOUBLE-INFORMATION-LOCK/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "coordinate_file": COORDINATES.name,
        "coordinate_file_sha256": sha256(COORDINATES),
        "broken_maps_file": BROKEN_MAPS.name,
        "broken_maps_file_sha256": sha256(BROKEN_MAPS),
        "row_count": len(rows),
        "number_range": {"low_inclusive": 3001, "high_inclusive": 3999, "parity": "odd"},
        "waves": list(WAVES),
        "parent_transform": "2N",
        "unresolved_row_count_unlabelled": sum(int(row["unresolved_by_five_children"]) for row in rows),
        "unresolved_rows_with_child_ties": sum(
            int(row["unresolved_by_five_children"]) * int(row["child_order_tied"]) for row in rows
        ),
        "unresolved_rows_with_parent_ties": sum(
            int(row["unresolved_by_five_children"]) * int(row["parent_order_tied"]) for row in rows
        ),
        "broken_controls": BROKEN_CONTROLS,
        "broken_seed": BROKEN_SEED,
        "broken_block_size": BLOCK_SIZE,
        "primality_computed": False,
        "sieve_used": False,
        "worked_examples": {str(number): coordinates(number) for number in (35, 36, 3001)},
    }
    SUMMARY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
