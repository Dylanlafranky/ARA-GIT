"""Independent validation for PN20 one-rung/two-child development audit."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
BRANCH_PATH = HERE / "PN20_BRANCH_TWO_CHILD_DEVELOPMENT.json"
DIRECTIONAL_PATH = HERE / "PN20_DIRECTIONAL_TWO_CHILD_DEVELOPMENT.json"
NUMERIC_PATH = HERE / "PN20_ONE_RUNG_DEVELOPMENT.json"
OUTPUT = HERE / "PN20_ONE_RUNG_TWO_CHILD_VALIDATION.json"


def sieve(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (((limit - start) // value) + 1)
    return [value for value, prime in enumerate(flags) if prime]


def independently_prime(number: int, primes: list[int]) -> bool:
    if number < 2:
        return False
    for prime in primes:
        if prime * prime > number:
            return True
        if number % prime == 0:
            return number == prime
    raise RuntimeError("independent prime table too short")


def independently_next_prime(anchor: int, primes: list[int]) -> int:
    candidate = anchor + 1
    if candidate > 2 and candidate % 2 == 0:
        candidate += 1
    while not independently_prime(candidate, primes):
        candidate += 2
    return candidate


def independent_paid_gates(anchor: int, primes: list[int]) -> list[int]:
    boundary = int(anchor ** 0.45)
    eligible = [prime for prime in primes if prime <= boundary]
    return list(reversed(eligible[-9:]))


def independent_branch_state(anchor: int, primes: list[int]) -> dict:
    left = []
    right = []
    for gate in independent_paid_gates(anchor, primes):
        axis = 2.0 * (anchor % gate) / gate
        if axis <= 1.0:
            left.append((axis, gate))
        else:
            right.append((2.0 - axis, gate))
    if not left or not right:
        return {"valid": False}
    progress_a, gate_a = max(left)
    progress_b, gate_b = max(right)
    phase_ab = (progress_a + progress_b) / 2.0
    return {
        "valid": True,
        "gate_a": gate_a,
        "gate_b": gate_b,
        "progress_a": progress_a,
        "progress_b": progress_b,
        "phase_ab": phase_ab,
        "phase_ba": 2.0 - phase_ab,
    }


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance


def check(checks: list[dict], label: str, passed: bool, detail: str) -> None:
    checks.append({"label": label, "passed": bool(passed), "detail": detail})


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("validation artifact already exists; refusing overwrite")
    branch = json.loads(BRANCH_PATH.read_text(encoding="utf-8"))
    directional = json.loads(DIRECTIONAL_PATH.read_text(encoding="utf-8"))
    numeric = json.loads(NUMERIC_PATH.read_text(encoding="utf-8"))
    max_anchor = max(row["anchor"] for row in branch["rows"])
    prime_limit = max(math.isqrt(2 * max_anchor) + 100, int((2 * max_anchor) ** 0.45) + 100)
    primes = sieve(prime_limit)
    checks: list[dict] = []

    check(checks, "seven development anchors", len(branch["rows"]) == 7, str(len(branch["rows"])))
    check(
        checks,
        "all three artifacts declare development only",
        all("development" in payload["status"] for payload in (branch, directional, numeric)),
        "status fields inspected",
    )
    check(
        checks,
        "branch summary exact count independently visible",
        branch["summary"]["exact_next_primes"] == 0,
        str(branch["summary"]["exact_next_primes"]),
    )
    check(
        checks,
        "directional summary exact count",
        directional["summary"]["exact_next_primes"] == 0,
        str(directional["summary"]["exact_next_primes"]),
    )
    check(
        checks,
        "numeric formulas never exact except constant-three variant once",
        numeric["formula_summary"]["three_minus_ab"]["exact_count"] == 0
        and numeric["formula_summary"]["two_ab_over_two_minus_ab_plus_one"]["exact_count"] == 1,
        json.dumps(numeric["formula_summary"]),
    )

    all_states_match = True
    all_truth_match = True
    all_te_ara = True
    independent_exact = 0
    independent_prime_predictions = 0
    for row in branch["rows"]:
        for key, anchor in (("landmark_1", row["anchor"]), ("landmark_2", 2 * row["anchor"])):
            expected = independent_branch_state(anchor, primes)
            observed = row[key]
            state_match = (
                expected["valid"] == observed["valid_two_branch_state"]
                and expected["gate_a"] == observed["phase_a_child"]["gate"]
                and expected["gate_b"] == observed["phase_b_child"]["gate"]
                and close(expected["progress_a"], observed["phase_a_child"]["progress_to_ridge"])
                and close(expected["progress_b"], observed["phase_b_child"]["progress_to_ridge"])
                and close(expected["phase_ab"], observed["phase_ab"])
                and close(expected["phase_ba"], observed["phase_ba"])
            )
            all_states_match &= state_match
            all_te_ara &= close(observed["phase_ab"] + observed["phase_ba"], 2.0)
        truth = independently_next_prime(row["anchor"], primes)
        all_truth_match &= truth == row["true_next_prime"]
        independent_exact += row["predicted_integer"] == truth
        if row["predicted_integer"] is not None:
            independent_prime_predictions += independently_prime(row["predicted_integer"], primes)

    check(checks, "independent branch states match", all_states_match, "two landmarks per anchor")
    check(checks, "AB plus BA equals pure TE-ARA two", all_te_ara, "14 landmark states")
    check(checks, "independent next-prime labels match", all_truth_match, "seven anchors")
    check(checks, "independent exact prediction count", independent_exact == 0, str(independent_exact))
    check(
        checks,
        "independent prime prediction count",
        independent_prime_predictions == 1,
        str(independent_prime_predictions),
    )

    samples = (0.1, 0.5, 1.0, 1.5, 1.9)
    identity_ok = all(close((2.0 * value / 2.0) - value + 1.0, 1.0) for value in samples)
    check(checks, "written confirmation expression is identity", identity_ok, str(samples))

    audited_files = [
        HERE / "pn20_one_rung_development.py",
        NUMERIC_PATH,
        HERE / "pn20_directional_two_child_development.py",
        DIRECTIONAL_PATH,
        HERE / "pn20_branch_two_child_development.py",
        BRANCH_PATH,
        HERE / "PN20_ONE_RUNG_TWO_CHILD_DEVELOPMENT_REPORT.md",
    ]
    # The sealed anchor has 26 decimal digits.  Twenty-digit decimal tails can
    # legitimately appear in JSON float serializations, so audit 25+ digits.
    long_decimal = re.compile(r"(?<![0-9a-f])\d{25,}(?![0-9a-f])", re.IGNORECASE)
    exposed = {}
    for path in audited_files:
        matches = long_decimal.findall(path.read_text(encoding="utf-8"))
        if matches:
            exposed[path.name] = matches
    check(
        checks,
        "no raw 25-plus-digit fresh anchor in PN20 artifacts",
        not exposed,
        json.dumps(exposed),
    )

    passed = sum(item["passed"] for item in checks)
    payload = {
        "validation_id": "PN20/ONE-RUNG-TWO-CHILD/INDEPENDENT-VALIDATION/v1",
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
