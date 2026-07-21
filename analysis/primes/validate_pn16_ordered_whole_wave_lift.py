"""Independent validator for PN16.

This file intentionally does not import the primary PN16 implementation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PN16_ORDERED_WHOLE_WAVE_LIFT_PROTOCOL_v1_FROZEN.md"
FREEZE = ROOT / "PN16_PRE_RUN_FREEZE_MANIFEST.json"
RESULTS = ROOT / "PN16_ORDERED_WHOLE_WAVE_LIFT_RESULTS.json"
PATHS = ROOT / "PN16_ORDERED_WHOLE_WAVE_LIFT_PATHS.csv"
OUTPUT = ROOT / "PN16_ORDERED_WHOLE_WAVE_LIFT_VALIDATION.json"
EXPECTED_PROTOCOL_SHA256 = "281DAE4D278A6781D9CD42D0D07F7CF36E99DE397126137773719C2B5902373F"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def prime_list(limit: int) -> list[int]:
    out = []
    for n in range(2, limit + 1):
        if all(n % p for p in out if p * p <= n):
            out.append(n)
    return out


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for divisor in range(3, math.isqrt(n) + 1, 2):
        if n % divisor == 0:
            return False
    return True


def make_direct(period: int) -> bytearray:
    return bytearray(math.gcd(n, period) == 1 for n in range(period))


def filter_history(period: int, gates: list[int]) -> list[bytearray]:
    survivors = bytearray(b"\x01") * period
    histories = []
    for gate in gates:
        # Independent path: scan the current survivor set rather than slice-assigning multiples.
        survivors = bytearray(value and (index % gate != 0) for index, value in enumerate(survivors))
        histories.append(survivors)
    return histories


def next_survivor(terminal: int, gates: list[int]) -> int:
    n = terminal + 1
    while not all(n % gate for gate in gates):
        n += 1
    return n


def close(value, expected, label: str, checks: list[dict], tol: float = 1e-12) -> None:
    if isinstance(value, float) or isinstance(expected, float):
        passed = math.isclose(float(value), float(expected), rel_tol=tol, abs_tol=tol)
    else:
        passed = value == expected
    checks.append({"label": label, "passed": passed, "observed": value, "expected": expected})


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("Validation receipt already exists; refusing to overwrite")
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    path_rows = list(csv.DictReader(PATHS.open(encoding="utf-8")))
    checks: list[dict] = []

    close(digest(PROTOCOL), EXPECTED_PROTOCOL_SHA256, "frozen protocol hash", checks)
    close(freeze["protocol"]["sha256"], EXPECTED_PROTOCOL_SHA256, "freeze manifest protocol hash", checks)
    close(payload["protocol_sha256"], EXPECTED_PROTOCOL_SHA256, "result protocol hash", checks)

    all_primes = prime_list(1100)
    terminals = [5, 7, 11, 13, 17]
    target_parent = None
    for terminal, stored in zip(terminals, payload["materialized_rungs"]):
        gates = [p for p in all_primes if p <= terminal]
        period = math.prod(gates)
        phi = math.prod(p - 1 for p in gates)
        forward_history = filter_history(period, gates)
        reverse_history = filter_history(period, list(reversed(gates)))
        forward = forward_history[-1]
        reverse = reverse_history[-1]
        direct = make_direct(period)
        partial = [
            sum(a != b for a, b in zip(ab, ba)) / period
            for ab, ba in zip(forward_history[:-1], reverse_history[:-1])
        ]
        recovered = next_survivor(terminal, gates)

        close(stored["period"], period, f"p{terminal} period", checks)
        close(stored["expected_totient"], phi, f"p{terminal} totient", checks)
        close(sum(forward), phi, f"p{terminal} forward survivor count", checks)
        close(sum(reverse), phi, f"p{terminal} reverse survivor count", checks)
        close(forward, reverse, f"p{terminal} completed AB equals BA", checks)
        close(forward, direct, f"p{terminal} completed identity equals gcd mask", checks)
        close(stored["max_partial_hamming_fraction"], max(partial), f"p{terminal} max path disagreement", checks)
        close(
            stored["mean_partial_hamming_fraction"],
            sum(partial) / len(partial),
            f"p{terminal} mean path disagreement",
            checks,
        )
        close(stored["first_quiet_node"], recovered, f"p{terminal} quiet node", checks)
        close(recovered, all_primes[all_primes.index(terminal) + 1], f"p{terminal} next-prime control", checks)
        if terminal == 17:
            target_parent = direct

    close(len(path_rows), sum(len([p for p in all_primes if p <= t]) for t in terminals), "path CSV row count", checks)

    assert target_parent is not None
    lift = payload["target_lift"]
    q = next_survivor(17, [2, 3, 5, 7, 11, 13, 17])
    parent_period = 510510
    child_period = parent_period * q
    tiled = target_parent * q
    independently_lifted = bytearray(
        value and (index % q != 0) for index, value in enumerate(tiled)
    )
    direct_child = make_direct(child_period)
    releases = sum(a and not b for a, b in zip(tiled, independently_lifted))

    close(q, 19, "target quiet node recovered without supplied p19", checks)
    close(lift["child_period"], child_period, "target child period", checks)
    close(lift["tiled_parent_survivors"], sum(tiled), "target tiled parent survivors", checks)
    close(lift["newly_released"], releases, "target newly released count", checks)
    close(releases, 92160, "one newly released lift per p17 residue", checks)
    close(independently_lifted, direct_child, "independent lift equals full direct p19 gcd mask", checks)
    close(sum(independently_lifted), 1658880, "p19 totient", checks)
    close(lift["missing_relation_fraction_given_parent_survival"], 1 / 19, "conditional missing relation fraction", checks)
    close(lift["same_identity_recombination_missed_count"], releases, "reversed-copy closure missing count", checks)
    close(lift["same_identity_recombination_equals_child"], False, "reversed-copy closure is not next rung", checks)

    theorem_failures = []
    theorem_pairs = 0
    for index, terminal in enumerate(all_primes[:-1]):
        if terminal > 997:
            break
        gates = all_primes[: index + 1]
        recovered = next_survivor(terminal, gates)
        expected = terminal + 1
        while not is_prime(expected):
            expected += 1
        theorem_pairs += 1
        if recovered != expected:
            theorem_failures.append({"terminal": terminal, "recovered": recovered, "expected": expected})
    close(theorem_pairs, payload["theorem_scale_quiet_nodes"]["pair_count"], "theorem-scale pair count", checks)
    close(theorem_failures, [], "all theorem-scale quiet nodes equal independently tested next primes", checks)

    criteria = payload["criteria"]
    close(criteria["P1_ordered_histories_visible"], True, "P1 reconstructed", checks)
    close(criteria["P2_completed_AB_equals_BA_and_direct_parent"], True, "P2 reconstructed", checks)
    close(criteria["P3_same_identity_recombination_is_idempotent_not_next_rung"], True, "P3 reconstructed", checks)
    close(criteria["P4_first_quiet_node_recovers_next_prime"], True, "P4 reconstructed", checks)
    close(criteria["P5_new_quiet_node_gate_lifts_next_rung_exactly"], True, "P5 reconstructed", checks)

    receipt = {
        "test_id": "PN16/ORDERED-WHOLE-WAVE-LIFT/INDEPENDENT-VALIDATION/v1",
        "primary_results_sha256": digest(RESULTS),
        "path_csv_sha256": digest(PATHS),
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "all_passed": all(item["passed"] for item in checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, default=lambda x: "<binary mask matched>") + "\n", encoding="utf-8")
    print(json.dumps({key: receipt[key] for key in ("check_count", "passed_count", "all_passed")}, indent=2))


if __name__ == "__main__":
    main()
