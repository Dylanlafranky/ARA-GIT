"""PN18 validator v1.1: mechanical JSON-safe repair after v1 receipt failure.

The frozen v1 validator completed its mathematical checks but failed while
serializing the million-bit child root into JSON. This validator preserves the
same calculations and stores a hash/bit-length descriptor for very large
integers instead of their decimal expansion.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from validate_pn18_recursive_teara_product_tree import (
    CHILD_ROOT_FILE,
    EXPECTED_PROTOCOL_SHA256,
    FREEZE,
    HERE,
    PREDICTION,
    PROTOCOL,
    direct_root_gcd_first,
    linear_sieve,
    miller_rabin_64,
    pair_product,
    segmented_first_quiet,
    sha256,
    trial_division,
)


AMENDMENT = HERE / "PN18_VALIDATOR_SERIALIZATION_AMENDMENT.json"
OUTPUT = HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE_VALIDATION.json"


def describe(value):
    if isinstance(value, int) and value.bit_length() > 256:
        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        return {
            "type": "large_integer_descriptor",
            "bit_length": value.bit_length(),
            "byte_length": len(raw),
            "sha256_big_endian": hashlib.sha256(raw).hexdigest().upper(),
        }
    return value


def check(label: str, observed, expected, checks: list[dict]) -> None:
    passed = observed == expected
    checks.append({
        "label": label,
        "passed": passed,
        "observed": describe(observed),
        "expected": describe(expected),
    })


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN18 validation receipt already exists; refusing to overwrite")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    target = prediction["target"]
    checks: list[dict] = []

    check("protocol hash", sha256(PROTOCOL), EXPECTED_PROTOCOL_SHA256, checks)
    check("freeze protocol hash", freeze["protocol_sha256"], EXPECTED_PROTOCOL_SHA256, checks)
    check("frozen primary script hash", sha256(HERE / "pn18_recursive_teara_product_tree.py"), freeze["primary_script_sha256"], checks)
    check("original frozen validator retained", sha256(HERE / "validate_pn18_recursive_teara_product_tree.py"), freeze["validator_script_sha256"], checks)
    check("v1.1 validator hash", sha256(Path(__file__)), amendment["replacement_validator_sha256"], checks)
    check("sealed prediction hash", sha256(PREDICTION), amendment["sealed_prediction_sha256_before_amendment"], checks)
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
        "test_id": "PN18/RECURSIVE-TEARA-PRODUCT-TREE/INDEPENDENT-VALIDATION/v1.1",
        "amendment": (
            "The pre-frozen v1 validator failed only while JSON-serializing the full child-root integer. "
            "v1.1 stores its bit length and SHA-256. The sealed prediction was not changed."
        ),
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
