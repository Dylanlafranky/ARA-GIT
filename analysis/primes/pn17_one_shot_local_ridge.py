"""Primary PN17 one-shot local child-field builder.

The target path deliberately contains no primality-test function and reads no
nearby-prime table. It constructs the lower-child collision field once and
seals the first quiet offset as the prediction.
"""

from __future__ import annotations

import hashlib
import json
import math
from array import array
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN17_ONE_SHOT_LOCAL_RIDGE_PROTOCOL_v1_FROZEN.md"
FREEZE = HERE / "PN17_TARGET_FREEZE_MANIFEST.json"
RESULT = HERE / "PN17_ONE_SHOT_LOCAL_RIDGE_PREDICTION.json"
FIELD = HERE / "PN17_TARGET_COLLISION_FIELD_UINT16.bin"
EXPECTED_PROTOCOL_SHA256 = "CCB9A0C8F793DE75DE98399DA4791975342921F2CEDC32688F08865EBB0C1644"

WINDOW = 65_536
TARGET_ANCHOR = 400_000_000_000
DEVELOPMENT = {
    100_000_000: 100_000_007,
    1_000_000_000: 1_000_000_007,
    10_000_000_000: 10_000_000_019,
    100_000_000_000: 100_000_000_003,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def eratosthenes(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [value for value in range(2, limit + 1) if sieve[value]]


def collision_field(anchor: int) -> tuple[list[int], array]:
    maximum = anchor + WINDOW - 1
    children = eratosthenes(math.isqrt(maximum))
    collisions = array("H", [0]) * WINDOW
    for child in children:
        start = (-anchor) % child
        for offset in range(start, WINDOW, child):
            collisions[offset] += 1
    return children, collisions


def first_quiet_offset(collisions: array) -> int:
    for offset in range(1, len(collisions)):
        if collisions[offset] == 0:
            return offset
    raise RuntimeError("No quiet ridge in the frozen 65,536-integer block")


def development_runs() -> list[dict]:
    rows = []
    for anchor, expected in DEVELOPMENT.items():
        children, collisions = collision_field(anchor)
        correction = first_quiet_offset(collisions)
        rows.append({
            "anchor": anchor,
            "child_ceiling": children[-1],
            "child_count": len(children),
            "correction": correction,
            "predicted_integer": anchor + correction,
            "established_development_control": expected,
            "matches_development_control": anchor + correction == expected,
            "anchor_collision_count": collisions[0],
        })
    return rows


def equal_gap_control() -> dict:
    path = HERE / "PN7C_R11_TARGET_GAPS.npz"
    gaps = np.load(path)["r11__gaps"].astype(np.int64)
    incoming = gaps[:-1]
    outgoing = gaps[1:]
    error = np.abs(incoming - outgoing)
    return {
        "source": path.name,
        "source_sha256": sha256(path),
        "events": int(outgoing.size),
        "exact_equal_gap_hit_rate": float(np.mean(error == 0)),
        "mean_absolute_gap_error": float(np.mean(error)),
        "median_absolute_gap_error": float(np.median(error)),
        "within_2_gap_units": float(np.mean(error <= 2)),
        "within_4_gap_units": float(np.mean(error <= 4)),
        "mean_actual_outgoing_gap": float(np.mean(outgoing)),
    }


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Frozen PN17 protocol hash mismatch")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["protocol_sha256"] != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("PN17 freeze manifest does not match the protocol")
    if sha256(Path(__file__)) != freeze["primary_script_sha256"]:
        raise RuntimeError("Primary script changed after target freeze")
    if RESULT.exists() or FIELD.exists():
        raise RuntimeError("PN17 target artifacts already exist; refusing to overwrite")

    development = development_runs()
    if not all(row["matches_development_control"] for row in development):
        raise RuntimeError("Development integrity failed; target remains unopened")

    children, collisions = collision_field(TARGET_ANCHOR)
    correction = first_quiet_offset(collisions)
    predicted = TARGET_ANCHOR + correction

    FIELD.write_bytes(collisions.tobytes())
    p29_primorial = math.prod([2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
    p29_candidates = sum(
        math.gcd(TARGET_ANCHOR + offset, p29_primorial) == 1
        for offset in range(1, correction + 1)
    )
    odd_candidates = sum((TARGET_ANCHOR + offset) % 2 == 1 for offset in range(1, correction + 1))

    payload = {
        "test_id": "PN17/ONE-SHOT-LOCAL-INVERSE-RIDGE/v1",
        "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": sha256(PROTOCOL),
        "freeze_manifest_sha256": sha256(FREEZE),
        "separation": (
            "Target candidate is the first zero of the lower-child collision field. "
            "No target primality-test function or nearby-prime table is present in the primary builder."
        ),
        "window": WINDOW,
        "development": development,
        "target": {
            "anchor": TARGET_ANCHOR,
            "search_diameter_reference": [0, 2 * TARGET_ANCHOR],
            "local_block_end": TARGET_ANCHOR + WINDOW - 1,
            "child_count": len(children),
            "child_ceiling": children[-1],
            "sqrt_block_end_floor": math.isqrt(TARGET_ANCHOR + WINDOW - 1),
            "anchor_collision_count": collisions[0],
            "correction": correction,
            "predicted_integer": predicted,
            "predicted_collision_count": collisions[correction],
            "preceding_collision_counts": list(collisions[max(0, correction - 8) : correction]),
            "collision_field_file": FIELD.name,
            "collision_field_sha256": sha256(FIELD),
            "collision_field_min": min(collisions),
            "collision_field_max": max(collisions),
            "quiet_offsets_in_block": sum(value == 0 for value in collisions[1:]),
        },
        "baselines": {
            "odd_scan_candidates_through_prediction": odd_candidates,
            "p29_wheel_candidates_through_prediction": p29_candidates,
            "full_child_phases_used": len(children),
            "standard_segmented_sieve_equivalence": True,
        },
        "equal_gap_falsification_control": equal_gap_control(),
        "claims_not_yet_opened": {
            "predicted_integer_is_prime": None,
            "predicted_integer_is_first_prime_above_anchor": None,
        },
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "anchor": TARGET_ANCHOR,
        "correction": correction,
        "sealed_prediction": predicted,
        "prediction_packet_sha256": sha256(RESULT),
        "target_primality_opened": False,
    }, indent=2))


if __name__ == "__main__":
    main()
