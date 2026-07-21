"""Independent validation for the sealed PN17 local-ridge prediction."""

from __future__ import annotations

import hashlib
import json
import math
from array import array
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN17_ONE_SHOT_LOCAL_RIDGE_PROTOCOL_v1_FROZEN.md"
FREEZE = HERE / "PN17_TARGET_FREEZE_MANIFEST.json"
PREDICTION = HERE / "PN17_ONE_SHOT_LOCAL_RIDGE_PREDICTION.json"
FIELD = HERE / "PN17_TARGET_COLLISION_FIELD_UINT16.bin"
OUTPUT = HERE / "PN17_ONE_SHOT_LOCAL_RIDGE_VALIDATION.json"
EXPECTED_PROTOCOL_SHA256 = "CCB9A0C8F793DE75DE98399DA4791975342921F2CEDC32688F08865EBB0C1644"


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


def miller_rabin_64(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small:
        if n % prime == 0:
            return n == prime
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % n == 0:
            continue
        x = pow(base, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def direct_trial_division(n: int, primes: list[int]) -> bool:
    for prime in primes:
        if prime * prime > n:
            break
        if n % prime == 0:
            return False
    return n >= 2


def check(label: str, observed, expected, checks: list[dict]) -> None:
    passed = observed == expected
    checks.append({"label": label, "passed": passed, "observed": observed, "expected": expected})


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN17 validation receipt already exists; refusing to overwrite")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    checks: list[dict] = []

    check("protocol hash", sha256(PROTOCOL), EXPECTED_PROTOCOL_SHA256, checks)
    check("freeze protocol hash", freeze["protocol_sha256"], EXPECTED_PROTOCOL_SHA256, checks)
    check("frozen primary script hash", sha256(HERE / "pn17_one_shot_local_ridge.py"), freeze["primary_script_sha256"], checks)
    check("frozen validator script hash", sha256(Path(__file__)), freeze["validator_script_sha256"], checks)
    check("prediction field hash", sha256(FIELD), prediction["target"]["collision_field_sha256"], checks)

    anchor = prediction["target"]["anchor"]
    window = prediction["window"]
    candidate = prediction["target"]["predicted_integer"]
    correction = prediction["target"]["correction"]
    ceiling = math.isqrt(anchor + window - 1)
    children = linear_sieve(ceiling)

    stored_field = array("H")
    stored_field.frombytes(FIELD.read_bytes())
    rebuilt = array("H", [0]) * window
    for child in children:
        first = (-anchor) % child
        offset = first
        while offset < window:
            rebuilt[offset] += 1
            offset += child

    check("collision field length", len(stored_field), window, checks)
    check("full collision field reconstruction", stored_field == rebuilt, True, checks)
    check("independent child count", len(children), prediction["target"]["child_count"], checks)
    check("independent child ceiling", children[-1], prediction["target"]["child_ceiling"], checks)

    rebuilt_correction = next(offset for offset in range(1, window) if rebuilt[offset] == 0)
    check("correction reconstructed", rebuilt_correction, correction, checks)
    check("candidate reconstructed", anchor + rebuilt_correction, candidate, checks)
    check("candidate collision count", rebuilt[correction], 0, checks)
    check("every prior offset has a child collision", all(rebuilt[offset] > 0 for offset in range(1, correction)), True, checks)

    mr_prime = miller_rabin_64(candidate)
    trial_prime = direct_trial_division(candidate, children)
    prior_mr = [value for value in range(anchor + 1, candidate) if miller_rabin_64(value)]
    check("candidate deterministic Miller-Rabin", mr_prime, True, checks)
    check("candidate independent trial division", trial_prime, True, checks)
    check("no earlier Miller-Rabin prime", prior_mr, [], checks)

    odd_candidates = sum((anchor + offset) % 2 == 1 for offset in range(1, correction + 1))
    p29 = math.prod([2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
    p29_candidates = sum(math.gcd(anchor + offset, p29) == 1 for offset in range(1, correction + 1))
    check("odd scan baseline count", odd_candidates, prediction["baselines"]["odd_scan_candidates_through_prediction"], checks)
    check("p29 wheel baseline count", p29_candidates, prediction["baselines"]["p29_wheel_candidates_through_prediction"], checks)

    development_expected = {
        100_000_000: 100_000_007,
        1_000_000_000: 1_000_000_007,
        10_000_000_000: 10_000_000_019,
        100_000_000_000: 100_000_000_003,
    }
    for row in prediction["development"]:
        expected = development_expected[row["anchor"]]
        check(f"development {row['anchor']} prediction", row["predicted_integer"], expected, checks)
        check(f"development {row['anchor']} independent primality", miller_rabin_64(row["predicted_integer"]), True, checks)

    receipt = {
        "test_id": "PN17/ONE-SHOT-LOCAL-INVERSE-RIDGE/INDEPENDENT-VALIDATION/v1",
        "prediction_packet_sha256": sha256(PREDICTION),
        "field_sha256": sha256(FIELD),
        "candidate": candidate,
        "correction": correction,
        "candidate_is_prime": mr_prime and trial_prime,
        "candidate_is_first_prime_above_anchor": mr_prime and not prior_mr,
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
