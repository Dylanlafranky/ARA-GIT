"""Independent PN19 validator.

This file does not import the primary builder. It independently generates the
children, reconstructs both parents and the ordinary segmented-sieve control,
then opens target primality only after the prediction packet exists.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN19_TWO_PARENT_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md"
FREEZE = HERE / "PN19_TARGET_FREEZE_MANIFEST.json"
PREDICTION = HERE / "PN19_TWO_PARENT_INFORMATION_LOCK_PREDICTION.json"
PHASE_A_FILE = HERE / "PN19_TARGET_PHASE_A_MASK.bin"
PHASE_B_FILE = HERE / "PN19_TARGET_PHASE_B_MASK.bin"
LOCK_FILE = HERE / "PN19_TARGET_INFORMATION_LOCK_MASK.bin"
OUTPUT = HERE / "PN19_TWO_PARENT_INFORMATION_LOCK_VALIDATION.json"
EXPECTED_PROTOCOL_SHA256 = "DD093931EC3D7E206F642497742F5F140264577E3E72DA1364E97A0BB7E7A1F0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def linear_sieve(limit: int) -> list[int]:
    least = [0] * (limit + 1)
    primes: list[int] = []
    for value in range(2, limit + 1):
        if least[value] == 0:
            least[value] = value
            primes.append(value)
        for prime in primes:
            product = prime * value
            if product > limit or prime > least[value]:
                break
            least[product] = prime
    return primes


def independent_split(children: list[int]) -> tuple[list[int], list[int], dict]:
    total = math.fsum(math.log(value) for value in children)
    target = total / 2.0
    running = 0.0
    best_index = 1
    best_error = float("inf")
    for index in range(1, len(children)):
        running += math.log(children[index - 1])
        error = abs(running - target)
        if error < best_error:
            best_error = error
            best_index = index
    phase_a = children[:best_index]
    phase_b = children[best_index:]
    log_a = math.fsum(math.log(value) for value in phase_a)
    log_b = math.fsum(math.log(value) for value in phase_b)
    energy_a = 2.0 * log_a / (log_a + log_b)
    energy_b = 2.0 - energy_a
    return phase_a, phase_b, {
        "split_index": best_index,
        "phase_a_last_child": phase_a[-1],
        "phase_b_first_child": phase_b[0],
        "teara_phase_a": energy_a,
        "teara_phase_b": energy_b,
        "teara_total": energy_a + energy_b,
    }


def independent_parent_mask(anchor: int, window: int, children: list[int]) -> bytes:
    mask = bytearray(b"\x01") * window
    for prime_child in children:
        first_multiple = anchor + ((-anchor) % prime_child)
        while first_multiple < anchor + window:
            mask[first_multiple - anchor] = 0
            first_multiple += prime_child
    return bytes(mask)


def standard_segmented_mask(anchor: int, window: int, children: list[int]) -> bytes:
    composite = bytearray(window)
    for prime_child in children:
        first_offset = (-anchor) % prime_child
        for offset in range(first_offset, window, prime_child):
            composite[offset] = 1
    return bytes(0 if value else 1 for value in composite)


def first_positive(mask: bytes) -> int:
    return mask.index(1, 1)


def miller_rabin_64(number: int) -> bool:
    if number < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if number % prime == 0:
            return number == prime
    remainder = number - 1
    powers_of_two = 0
    while remainder % 2 == 0:
        powers_of_two += 1
        remainder //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % number == 0:
            continue
        witness = pow(base, remainder, number)
        if witness in (1, number - 1):
            continue
        for _ in range(powers_of_two - 1):
            witness = pow(witness, 2, number)
            if witness == number - 1:
                break
        else:
            return False
    return True


def trial_division(number: int, primes: list[int]) -> bool:
    for prime in primes:
        if prime * prime > number:
            break
        if number % prime == 0:
            return number == prime
    return number >= 2


def checked(label: str, observed, expected, checks: list[dict]) -> None:
    checks.append({
        "label": label,
        "passed": observed == expected,
        "observed": observed,
        "expected": expected,
    })


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN19 validation receipt already exists; refusing to overwrite")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    target = prediction["target"]
    anchor = target["anchor"]
    window = target["window"]
    candidate = target["predicted_integer"]
    correction = target["information_lock_offset"]
    checks: list[dict] = []

    checked("protocol hash", sha256(PROTOCOL), EXPECTED_PROTOCOL_SHA256, checks)
    checked("freeze protocol hash", freeze["protocol_sha256"], EXPECTED_PROTOCOL_SHA256, checks)
    checked("frozen primary hash", sha256(HERE / "pn19_two_parent_information_lock.py"), freeze["primary_script_sha256"], checks)
    checked("frozen validator hash", sha256(Path(__file__)), freeze["validator_script_sha256"], checks)
    checked("fresh target anchor", anchor, freeze["target_anchor"], checks)
    checked("frozen window", window, freeze["window"], checks)
    checked("phase A file hash", sha256(PHASE_A_FILE), target["phase_a_mask_sha256"], checks)
    checked("phase B file hash", sha256(PHASE_B_FILE), target["phase_b_mask_sha256"], checks)
    checked("information-lock file hash", sha256(LOCK_FILE), target["information_lock_mask_sha256"], checks)

    children = linear_sieve(math.isqrt(2 * anchor))
    phase_a_children, phase_b_children, split = independent_split(children)
    reconstructed_a = independent_parent_mask(anchor, window, phase_a_children)
    reconstructed_b = independent_parent_mask(anchor, window, phase_b_children)
    reconstructed_lock = bytes(a & b for a, b in zip(reconstructed_a, reconstructed_b))
    ordinary_mask = standard_segmented_mask(anchor, window, children)
    stored_a = PHASE_A_FILE.read_bytes()
    stored_b = PHASE_B_FILE.read_bytes()
    stored_lock = LOCK_FILE.read_bytes()

    checked("independent child count", len(children), target["child_count"], checks)
    checked("independent child ceiling", children[-1], target["child_ceiling"], checks)
    checked("independent split index", split["split_index"], target["split"]["split_index"], checks)
    checked("independent split A last child", split["phase_a_last_child"], target["split"]["phase_a_last_child"], checks)
    checked("independent split B first child", split["phase_b_first_child"], target["split"]["phase_b_first_child"], checks)
    checked("TE-ARA total equals two", abs(split["teara_total"] - 2.0) < 1e-15, True, checks)
    checked("phase A reconstruction byte exact", reconstructed_a == stored_a, True, checks)
    checked("phase B reconstruction byte exact", reconstructed_b == stored_b, True, checks)
    checked("information-lock reconstruction byte exact", reconstructed_lock == stored_lock, True, checks)
    checked("two-parent lock equals ordinary segmented sieve", reconstructed_lock == ordinary_mask, True, checks)
    checked("phase A first survivor", first_positive(reconstructed_a), target["phase_a_first_survivor_offset"], checks)
    checked("phase B first survivor", first_positive(reconstructed_b), target["phase_b_first_survivor_offset"], checks)
    checked("joint first survivor", first_positive(reconstructed_lock), correction, checks)
    checked("candidate reconstructed", anchor + correction, candidate, checks)

    candidate_mr = miller_rabin_64(candidate)
    candidate_trial = trial_division(candidate, children)
    earlier_primes = [value for value in range(anchor + 1, candidate) if miller_rabin_64(value)]
    checked("candidate deterministic Miller-Rabin", candidate_mr, True, checks)
    checked("candidate full trial division", candidate_trial, True, checks)
    checked("no earlier prime above anchor", earlier_primes, [], checks)

    expected_development = {
        100_000_000: 100_000_007,
        1_000_000_000: 1_000_000_007,
        10_000_000_000: 10_000_000_019,
        100_000_000_000: 100_000_000_003,
        400_000_000_000: 400_000_000_019,
        700_000_000_000: 700_000_000_009,
    }
    for row in prediction["development"]:
        expected = expected_development[row["anchor"]]
        checked(f"development {row['anchor']} exact", row["predicted_integer"], expected, checks)
        checked(f"development {row['anchor']} prime", miller_rabin_64(row["predicted_integer"]), True, checks)

    receipt = {
        "test_id": "PN19/TWO-PARENT-INFORMATION-LOCK/INDEPENDENT-VALIDATION/v1",
        "prediction_packet_sha256": sha256(PREDICTION),
        "candidate": candidate,
        "correction": correction,
        "candidate_is_prime": candidate_mr and candidate_trial,
        "candidate_is_first_prime_above_anchor": candidate_mr and not earlier_primes,
        "ordinary_segmented_sieve_correction": first_positive(ordinary_mask),
        "phase_a_first_survivor_offset": first_positive(reconstructed_a),
        "phase_b_first_survivor_offset": first_positive(reconstructed_b),
        "development_second_go_success_rate": prediction["development_second_go_success_rate"],
        "target_second_go_success": target["either_parent_is_second_go_success"],
        "method_classification": "exact segmented sieve factored into two log-balanced parent masks",
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "all_passed": all(item["passed"] for item in checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate": candidate,
        "correction": correction,
        "candidate_is_prime": receipt["candidate_is_prime"],
        "candidate_is_first_prime_above_anchor": receipt["candidate_is_first_prime_above_anchor"],
        "target_second_go_success": receipt["target_second_go_success"],
        "development_second_go_success_rate": receipt["development_second_go_success_rate"],
        "checks": f"{receipt['passed_count']}/{receipt['check_count']}",
    }, indent=2))


if __name__ == "__main__":
    main()
