"""Independent validation of PN22 using scalar arithmetic and bytearray sieve."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "PN22_ODD_LATTICE_ARA_CANDIDATE_RESULTS.json"
OUTPUT = HERE / "PN22_ODD_LATTICE_ARA_CANDIDATE_VALIDATION.json"
MAX_A = 1_000_000


def scalar_transform(value: int) -> int:
    numerator = 7 * value + 2
    ceiling = (numerator + 1) // 2
    return ceiling if ceiling % 2 else ceiling + 1


def byte_sieve(limit: int) -> bytearray:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (((limit - start) // value) + 1)
    return flags


def independent_perfect_powers(limit: int) -> list[int]:
    found = set()
    for base in range(2, limit + 1):
        if base * base > limit:
            break
        power = base * base
        while power <= limit:
            found.add(power)
            power *= base
    return sorted(found)


def add(checks: list[dict], label: str, passed: bool, observed: object) -> None:
    checks.append({"label": label, "passed": bool(passed), "observed": observed})


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("validation output exists; refusing overwrite")
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    candidates = [scalar_transform(value) for value in range(1, MAX_A + 1)]
    minimum, maximum = candidates[0], candidates[-1]
    flags = byte_sieve(maximum + 140)
    candidate_primes = sum(flags[value] for value in candidates)
    odd_values = list(range(minimum if minimum % 2 else minimum + 1, maximum + 1, 2))
    odd_primes = sum(flags[value] for value in odd_values)
    coprime_values = [value for value in range(minimum, maximum + 1) if math.gcd(value, 14) == 1]
    lane_values = [value for value in range(minimum, maximum + 1) if value % 14 in (1, 5, 9, 13)]
    perfect = independent_perfect_powers(MAX_A)
    perfect_candidates = [scalar_transform(value) for value in perfect]
    checks: list[dict] = []

    add(checks, "candidate count", len(candidates) == 1_000_000, len(candidates))
    add(checks, "candidate mapping is unique", len(set(candidates)) == len(candidates), len(set(candidates)))
    add(checks, "candidate set equals exact mod14 lanes", candidates == lane_values, len(lane_values))
    add(checks, "output residues", sorted(set(value % 14 for value in candidates)) == [1, 5, 9, 13], sorted(set(value % 14 for value in candidates)))
    add(checks, "candidate prime count", candidate_primes == result["primary"]["candidate_prime_count"], candidate_primes)
    add(checks, "all-odd count", len(odd_values) == result["primary"]["all_odd_count"], len(odd_values))
    add(checks, "all-odd prime rate", abs(odd_primes / len(odd_values) - result["primary"]["all_odd_prime_rate"]) < 1e-15, odd_primes / len(odd_values))
    add(checks, "coprime-to-14 count", len(coprime_values) == result["primary"]["coprime_to_14_count"], len(coprime_values))
    add(checks, "exact matched lift equals one", result["primary"]["candidate_lift_over_exact_lane"] == 1.0, result["primary"]["candidate_lift_over_exact_lane"])
    add(checks, "worked 27 maps to prime 97", scalar_transform(27) == 97 and bool(flags[97]), scalar_transform(27))
    add(checks, "worked 32 maps to prime 113", scalar_transform(32) == 113 and bool(flags[113]), scalar_transform(32))
    add(checks, "worked 34 maps to composite 121", scalar_transform(34) == 121 and not flags[121], scalar_transform(34))
    add(checks, "perfect-power input count", len(perfect) == result["subgroups"]["all_unique_perfect_powers"]["input_count"], len(perfect))
    add(checks, "perfect-power prime count", sum(flags[value] for value in perfect_candidates) == result["subgroups"]["all_unique_perfect_powers"]["candidate_prime_count"], sum(flags[value] for value in perfect_candidates))
    add(checks, "wheel-crosswalk decision", result["decision"]["wheel_crosswalk"] is True and result["decision"]["blind_target_authorized"] is False, result["decision"])

    inspected = [
        HERE / "PN22_ODD_LATTICE_ARA_CANDIDATE_PROTOCOL_v1_FROZEN.md",
        HERE / "pn22_odd_lattice_ara_candidate.py",
        RESULT_PATH,
    ]
    long_decimal = re.compile(r"(?<![0-9a-f])\d{25,}(?![0-9a-f])", re.IGNORECASE)
    exposed = {
        path.name: long_decimal.findall(path.read_text(encoding="utf-8"))
        for path in inspected
        if long_decimal.findall(path.read_text(encoding="utf-8"))
    }
    add(checks, "sealed target absent", not exposed, exposed)

    passed = sum(item["passed"] for item in checks)
    payload = {
        "validation_id": "PN22/ODD-LATTICE-ARA-CANDIDATE/INDEPENDENT/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total")}, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
