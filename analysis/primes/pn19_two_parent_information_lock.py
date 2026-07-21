"""Primary PN19 two-parent information-lock builder.

The target path contains no primality-test function and reads no nearby-prime
label. Every lower child is folded into one of two log-balanced parent masks;
their intersection seals the first joint survivor.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN19_TWO_PARENT_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md"
FREEZE = HERE / "PN19_TARGET_FREEZE_MANIFEST.json"
RESULT = HERE / "PN19_TWO_PARENT_INFORMATION_LOCK_PREDICTION.json"
PHASE_A_FILE = HERE / "PN19_TARGET_PHASE_A_MASK.bin"
PHASE_B_FILE = HERE / "PN19_TARGET_PHASE_B_MASK.bin"
LOCK_FILE = HERE / "PN19_TARGET_INFORMATION_LOCK_MASK.bin"
EXPECTED_PROTOCOL_SHA256 = "DD093931EC3D7E206F642497742F5F140264577E3E72DA1364E97A0BB7E7A1F0"

WINDOW = 65_536
TARGET_ANCHOR = 900_000_000_000
DEVELOPMENT = {
    100_000_000: 100_000_007,
    1_000_000_000: 1_000_000_007,
    10_000_000_000: 10_000_000_019,
    100_000_000_000: 100_000_000_003,
    400_000_000_000: 400_000_000_019,
    700_000_000_000: 700_000_000_009,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def eratosthenes(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for child_prime in range(2, math.isqrt(limit) + 1):
        if sieve[child_prime]:
            start = child_prime * child_prime
            count = ((limit - start) // child_prime) + 1
            sieve[start : limit + 1 : child_prime] = b"\x00" * count
    return [value for value in range(2, limit + 1) if sieve[value]]


def split_log_balanced(children: list[int]) -> tuple[list[int], list[int], dict]:
    weights = [math.log(child) for child in children]
    total = math.fsum(weights)
    half = total / 2.0
    prefix = 0.0
    best_cut = 1
    best_error = float("inf")
    for index, weight in enumerate(weights[:-1], start=1):
        prefix += weight
        error = abs(prefix - half)
        if error < best_error:
            best_error = error
            best_cut = index
    phase_a = children[:best_cut]
    phase_b = children[best_cut:]
    log_a = math.fsum(math.log(child) for child in phase_a)
    log_b = math.fsum(math.log(child) for child in phase_b)
    energy_a = 2.0 * log_a / (log_a + log_b)
    energy_b = 2.0 - energy_a
    return phase_a, phase_b, {
        "split_index": best_cut,
        "phase_a_child_count": len(phase_a),
        "phase_b_child_count": len(phase_b),
        "phase_a_first_child": phase_a[0],
        "phase_a_last_child": phase_a[-1],
        "phase_b_first_child": phase_b[0],
        "phase_b_last_child": phase_b[-1],
        "phase_a_log_weight": log_a,
        "phase_b_log_weight": log_b,
        "teara_phase_a": energy_a,
        "teara_phase_b": energy_b,
        "teara_total": energy_a + energy_b,
        "absolute_log_weight_mismatch": abs(log_a - log_b),
        "relative_log_weight_mismatch": abs(log_a - log_b) / (log_a + log_b),
    }


def survivor_mask(anchor: int, children: list[int]) -> bytearray:
    mask = bytearray(b"\x01") * WINDOW
    for child_prime in children:
        start = (-anchor) % child_prime
        if start >= WINDOW:
            continue
        count = ((WINDOW - 1 - start) // child_prime) + 1
        mask[start:WINDOW:child_prime] = b"\x00" * count
    return mask


def first_positive_survivor(mask: bytes | bytearray) -> int:
    try:
        return mask.index(1, 1)
    except ValueError as exc:
        raise RuntimeError("No positive survivor in the frozen window") from exc


def mask_sha256(mask: bytes | bytearray) -> str:
    return hashlib.sha256(bytes(mask)).hexdigest().upper()


def run_anchor(anchor: int, available_children: list[int]) -> tuple[dict, bytes, bytes, bytes]:
    started = time.perf_counter()
    reference_endpoint = 2 * anchor
    child_limit = math.isqrt(reference_endpoint)
    child_count = bisect.bisect_right(available_children, child_limit)
    children = available_children[:child_count]
    phase_a_children, phase_b_children, split = split_log_balanced(children)

    phase_a_started = time.perf_counter()
    phase_a = survivor_mask(anchor, phase_a_children)
    phase_a_seconds = time.perf_counter() - phase_a_started
    phase_b_started = time.perf_counter()
    phase_b = survivor_mask(anchor, phase_b_children)
    phase_b_seconds = time.perf_counter() - phase_b_started
    lock = bytes(a_value & b_value for a_value, b_value in zip(phase_a, phase_b))

    first_a = first_positive_survivor(phase_a)
    first_b = first_positive_survivor(phase_b)
    first_lock = first_positive_survivor(lock)
    before = range(1, first_lock)
    a_only_before = [offset for offset in before if phase_a[offset] and not phase_b[offset]]
    b_only_before = [offset for offset in before if phase_b[offset] and not phase_a[offset]]

    row = {
        "anchor": anchor,
        "window": WINDOW,
        "reference_endpoint": reference_endpoint,
        "child_limit_floor_sqrt_2n": child_limit,
        "child_count": len(children),
        "child_ceiling": children[-1],
        "split": split,
        "phase_a_first_survivor_offset": first_a,
        "phase_b_first_survivor_offset": first_b,
        "information_lock_offset": first_lock,
        "predicted_integer": anchor + first_lock,
        "phase_a_is_second_go_success": first_a == first_lock,
        "phase_b_is_second_go_success": first_b == first_lock,
        "either_parent_is_second_go_success": first_a == first_lock or first_b == first_lock,
        "phase_a_only_false_survivors_before_lock": len(a_only_before),
        "phase_b_only_false_survivors_before_lock": len(b_only_before),
        "phase_a_only_offsets_before_lock": a_only_before[:64],
        "phase_b_only_offsets_before_lock": b_only_before[:64],
        "phase_a_survivor_count": sum(phase_a),
        "phase_b_survivor_count": sum(phase_b),
        "joint_survivor_count": sum(lock),
        "phase_a_survivor_density": sum(phase_a) / WINDOW,
        "phase_b_survivor_density": sum(phase_b) / WINDOW,
        "joint_survivor_density": sum(lock) / WINDOW,
        "phase_a_collision_density": 1.0 - (sum(phase_a) / WINDOW),
        "phase_b_collision_density": 1.0 - (sum(phase_b) / WINDOW),
        "phase_a_mask_sha256": mask_sha256(phase_a),
        "phase_b_mask_sha256": mask_sha256(phase_b),
        "information_lock_mask_sha256": mask_sha256(lock),
        "phase_a_mask_seconds": phase_a_seconds,
        "phase_b_mask_seconds": phase_b_seconds,
        "total_primary_seconds": time.perf_counter() - started,
        "stored_parent_and_relation_bytes": WINDOW * 3,
        "standard_single_mask_bytes": WINDOW,
        "child_list_uint32_bytes": len(children) * 4,
    }
    return row, bytes(phase_a), bytes(phase_b), lock


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Frozen PN19 protocol hash mismatch")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["protocol_sha256"] != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("PN19 freeze manifest does not match the protocol")
    if freeze["target_anchor"] != TARGET_ANCHOR or freeze["window"] != WINDOW:
        raise RuntimeError("PN19 target configuration differs from the frozen manifest")
    if sha256(Path(__file__)) != freeze["primary_script_sha256"]:
        raise RuntimeError("PN19 primary script changed after target freeze")
    target_artifacts = (RESULT, PHASE_A_FILE, PHASE_B_FILE, LOCK_FILE)
    if any(path.exists() for path in target_artifacts):
        raise RuntimeError("PN19 target artifacts already exist; refusing to overwrite")

    maximum_limit = math.isqrt(2 * TARGET_ANCHOR)
    available_children = eratosthenes(maximum_limit)
    development: list[dict] = []
    for anchor, expected in DEVELOPMENT.items():
        row, _, _, _ = run_anchor(anchor, available_children)
        row["established_development_control"] = expected
        row["matches_development_control"] = row["predicted_integer"] == expected
        development.append(row)
    if not all(row["matches_development_control"] for row in development):
        raise RuntimeError("Development integrity failed; target remains unopened")

    target, phase_a, phase_b, lock = run_anchor(TARGET_ANCHOR, available_children)
    PHASE_A_FILE.write_bytes(phase_a)
    PHASE_B_FILE.write_bytes(phase_b)
    LOCK_FILE.write_bytes(lock)
    target["phase_a_mask_file"] = PHASE_A_FILE.name
    target["phase_b_mask_file"] = PHASE_B_FILE.name
    target["information_lock_mask_file"] = LOCK_FILE.name

    payload = {
        "test_id": "PN19/TWO-PARENT-INFORMATION-LOCK/v1",
        "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": sha256(PROTOCOL),
        "freeze_manifest_sha256": sha256(FREEZE),
        "separation": (
            "The target is the first intersection of two predeclared log-balanced parent survivor masks. "
            "The primary builder contains no target primality-test function and reads no nearby-target prime label."
        ),
        "method_control": (
            "The joint lock is an established segmented sieve factored into two complete parent masks."
        ),
        "development": development,
        "development_second_go_success_rate": (
            sum(row["either_parent_is_second_go_success"] for row in development) / len(development)
        ),
        "target": target,
        "claims_not_yet_opened": {
            "predicted_integer_is_prime": None,
            "predicted_integer_is_first_prime_above_anchor": None,
        },
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "anchor": TARGET_ANCHOR,
        "phase_a_first_offset": target["phase_a_first_survivor_offset"],
        "phase_b_first_offset": target["phase_b_first_survivor_offset"],
        "information_lock_offset": target["information_lock_offset"],
        "sealed_prediction": target["predicted_integer"],
        "development_second_go_success_rate": payload["development_second_go_success_rate"],
        "prediction_packet_sha256": sha256(RESULT),
        "target_primality_opened": False,
    }, indent=2))


if __name__ == "__main__":
    main()
