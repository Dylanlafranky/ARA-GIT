"""Independent validation of the sealed PN18 recursive product-tree result."""

from __future__ import annotations

import hashlib
import json
import math
from array import array
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE_PROTOCOL_v1_FROZEN.md"
FREEZE = HERE / "PN18_TARGET_FREEZE_MANIFEST.json"
PREDICTION = HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE_PREDICTION.json"
CHILD_ROOT_FILE = HERE / "PN18_TARGET_CHILD_PRODUCT_ROOT.bin"
OUTPUT = HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE_VALIDATION.json"
EXPECTED_PROTOCOL_SHA256 = "5D989C96641C91676DFADD6277AE4DA06037ABAABA2018D3028DBD6EE3EA40FF"
P29_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
P29_PRIMORIAL = math.prod(P29_PRIMES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def linear_sieve(limit: int) -> list[int]:
    least = array("I", [0]) * (limit + 1)
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


def pair_product(values: list[int]) -> int:
    current = list(values)
    while len(current) > 1:
        current = [
            current[index] * current[index + 1] if index + 1 < len(current) else current[index]
            for index in range(0, len(current), 2)
        ]
    return current[0] if current else 1


def miller_rabin_64(n: int) -> bool:
    if n < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % prime == 0:
            return n == prime
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % n == 0:
            continue
        x = pow(base, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def trial_division(n: int, primes: list[int]) -> bool:
    for prime in primes:
        if prime * prime > n:
            break
        if n % prime == 0:
            return False
    return n >= 2


def segmented_first_quiet(anchor: int, window: int, children: list[int]) -> tuple[int, bytearray]:
    collisions = bytearray(window)
    for prime in children:
        offset = (-anchor) % prime
        for position in range(offset, window, prime):
            collisions[position] = 1
    correction = next(offset for offset in range(1, window) if collisions[offset] == 0)
    return correction, collisions


def direct_root_gcd_first(anchor: int, window: int, root: int) -> tuple[int, int]:
    rank = 0
    for offset in range(1, window):
        candidate = anchor + offset
        if math.gcd(candidate, P29_PRIMORIAL) != 1:
            continue
        rank += 1
        if math.gcd(candidate, root) == 1:
            return offset, rank
    raise RuntimeError("No direct-GCD quiet candidate in block")


def check(label: str, observed, expected, checks: list[dict]) -> None:
    passed = observed == expected
    checks.append({"label": label, "passed": passed, "observed": observed, "expected": expected})


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN18 validation receipt already exists; refusing to overwrite")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    target = prediction["target"]
    checks: list[dict] = []

    check("protocol hash", sha256(PROTOCOL), EXPECTED_PROTOCOL_SHA256, checks)
    check("freeze protocol hash", freeze["protocol_sha256"], EXPECTED_PROTOCOL_SHA256, checks)
    check("frozen primary script hash", sha256(HERE / "pn18_recursive_teara_product_tree.py"), freeze["primary_script_sha256"], checks)
    check("frozen validator script hash", sha256(Path(__file__)), freeze["validator_script_sha256"], checks)
    check("prediction child-root hash", sha256(CHILD_ROOT_FILE), target["child_root_sha256"], checks)

    anchor = target["anchor"]
    window = target["window"]
    candidate = target["predicted_integer"]
    correction = target["correction"]
    limit = math.isqrt(anchor + window - 1)
    children = linear_sieve(limit)
    independent_root = pair_product(children)
    stored_root = int.from_bytes(CHILD_ROOT_FILE.read_bytes(), "big")

    check("fresh anchor remained frozen", anchor, freeze["target_anchor"], checks)
    check("frozen window", window, freeze["window"], checks)
    check("independent child count", len(children), target["child_count"], checks)
    check("independent child ceiling", children[-1], target["child_ceiling"], checks)
    check("independent child root equals stored root", independent_root, stored_root, checks)
    check("root bit length", independent_root.bit_length(), target["child_root_bit_length"], checks)
    check("root byte length", len(CHILD_ROOT_FILE.read_bytes()), target["child_root_byte_length"], checks)

    direct_correction, direct_rank = direct_root_gcd_first(anchor, window, independent_root)
    sieve_correction, collisions = segmented_first_quiet(anchor, window, children)
    check("direct root-GCD correction", direct_correction, correction, checks)
    check("direct p29 candidate rank", direct_rank, target["p29_candidate_rank_through_prediction"], checks)
    check("independent segmented-sieve correction", sieve_correction, correction, checks)
    check("candidate reconstructed", anchor + correction, candidate, checks)
    check("candidate has no lower-child collision", collisions[correction], 0, checks)
    check("all earlier offsets have a child collision", all(collisions[offset] for offset in range(1, correction)), True, checks)

    mr_prime = miller_rabin_64(candidate)
    trial_prime = trial_division(candidate, children)
    earlier_mr_primes = [value for value in range(anchor + 1, candidate) if miller_rabin_64(value)]
    check("candidate deterministic Miller-Rabin", mr_prime, True, checks)
    check("candidate full trial division", trial_prime, True, checks)
    check("no earlier Miller-Rabin prime", earlier_mr_primes, [], checks)

    expected_development = {
        100_000_000: 100_000_007,
        1_000_000_000: 1_000_000_007,
        10_000_000_000: 10_000_000_019,
        100_000_000_000: 100_000_000_003,
        400_000_000_000: 400_000_000_019,
    }
    for row in prediction["development"]:
        expected = expected_development[row["anchor"]]
        check(f"development {row['anchor']} exact", row["predicted_integer"], expected, checks)
        check(f"development {row['anchor']} primality", miller_rabin_64(row["predicted_integer"]), True, checks)

    one_bit_odd_bytes = ((limit - 1) // 2 + 7) // 8
    check("uint32 child-list bytes", len(children) * 4, target["child_list_uint32_bytes"], checks)
    check("one-bit odd sieve bytes", one_bit_odd_bytes, target["one_bit_odd_sieve_bytes"], checks)
    check("PN17 collision-field reference bytes", window * 2, target["pn17_collision_field_bytes"], checks)

    receipt = {
        "test_id": "PN18/RECURSIVE-TEARA-PRODUCT-TREE/INDEPENDENT-VALIDATION/v1",
        "prediction_packet_sha256": sha256(PREDICTION),
        "child_root_sha256": sha256(CHILD_ROOT_FILE),
        "candidate": candidate,
        "correction": correction,
        "candidate_is_prime": mr_prime and trial_prime,
        "candidate_is_first_prime_above_anchor": mr_prime and not earlier_mr_primes,
        "independent_direct_root_gcd_correction": direct_correction,
        "independent_segmented_sieve_correction": sieve_correction,
        "method_classification": "established primorial/product-tree/batch-GCD primality crosswalk",
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
        "checks": f"{receipt['passed_count']}/{receipt['check_count']}",
    }, indent=2))


if __name__ == "__main__":
    main()
