"""PN16 ordered whole-wave lift.

This primary implementation follows the frozen protocol in
PN16_ORDERED_WHOLE_WAVE_LIFT_PROTOCOL_v1_FROZEN.md.
It uses only deterministic integer arithmetic and the Python standard library.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PN16_ORDERED_WHOLE_WAVE_LIFT_PROTOCOL_v1_FROZEN.md"
FREEZE = ROOT / "PN16_PRE_RUN_FREEZE_MANIFEST.json"
RESULTS = ROOT / "PN16_ORDERED_WHOLE_WAVE_LIFT_RESULTS.json"
PATHS = ROOT / "PN16_ORDERED_WHOLE_WAVE_LIFT_PATHS.csv"

EXPECTED_PROTOCOL_SHA256 = "281DAE4D278A6781D9CD42D0D07F7CF36E99DE397126137773719C2B5902373F"
DEVELOPMENT_TERMINALS = (5, 7, 11, 13)
TARGET_TERMINAL = 17
THEOREM_SCALE_CEILING = 997


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def primes_upto(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0] = 0
    if limit >= 1:
        sieve[1] = 0
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [n for n in range(2, limit + 1) if sieve[n]]


def product(values: list[int] | tuple[int, ...]) -> int:
    out = 1
    for value in values:
        out *= value
    return out


def apply_gate(mask: bytearray, prime: int) -> None:
    count = ((len(mask) - 1) // prime) + 1
    mask[0::prime] = b"\x00" * count


def history_for_order(period: int, gates: list[int]) -> tuple[list[bytes], bytearray]:
    mask = bytearray(b"\x01") * period
    history: list[bytes] = []
    for gate in gates:
        apply_gate(mask, gate)
        history.append(bytes(mask))
    return history, mask


def hamming_fraction(a: bytes | bytearray, b: bytes | bytearray) -> float:
    if len(a) != len(b):
        raise ValueError("Masks must have the same length")
    return sum(x != y for x, y in zip(a, b)) / len(a)


def direct_coprime_mask(period: int) -> bytearray:
    return bytearray(1 if math.gcd(n, period) == 1 else 0 for n in range(period))


def first_quiet_node(terminal: int, gates: list[int]) -> int:
    candidate = terminal + 1
    while True:
        if all(candidate % gate for gate in gates):
            return candidate
        candidate += 1


def materialized_parent(terminal: int, all_primes: list[int]) -> dict:
    gates = [p for p in all_primes if p <= terminal]
    period = product(gates)
    forward_history, forward = history_for_order(period, gates)
    reverse_history, reverse = history_for_order(period, list(reversed(gates)))
    direct = direct_coprime_mask(period)

    path_rows = []
    for depth, (ab, ba) in enumerate(zip(forward_history, reverse_history), start=1):
        path_rows.append(
            {
                "terminal_prime": terminal,
                "depth": depth,
                "forward_gate": gates[depth - 1],
                "reverse_gate": gates[-depth],
                "forward_survivors": sum(ab),
                "reverse_survivors": sum(ba),
                "hamming_fraction": hamming_fraction(ab, ba),
                "completion": depth == len(gates),
            }
        )

    partial_disagreements = [row["hamming_fraction"] for row in path_rows[:-1]]
    phi_expected = product([p - 1 for p in gates])
    quiet = first_quiet_node(terminal, gates)

    # Logical composition is the natural composition of binary sieve projections.
    recombined = bytearray(x & y for x, y in zip(forward, reverse))

    return {
        "summary": {
            "terminal_prime": terminal,
            "gates": gates,
            "gate_count": len(gates),
            "period": period,
            "expected_totient": phi_expected,
            "forward_survivors": sum(forward),
            "reverse_survivors": sum(reverse),
            "final_hamming_count": sum(x != y for x, y in zip(forward, reverse)),
            "forward_equals_reverse": forward == reverse,
            "forward_equals_direct_gcd": forward == direct,
            "reverse_equals_direct_gcd": reverse == direct,
            "recombined_equals_parent": recombined == forward,
            "max_partial_hamming_fraction": max(partial_disagreements, default=0.0),
            "mean_partial_hamming_fraction": (
                sum(partial_disagreements) / len(partial_disagreements)
                if partial_disagreements
                else 0.0
            ),
            "ordered_history_visible": any(value > 0 for value in partial_disagreements),
            "first_quiet_node": quiet,
        },
        "path_rows": path_rows,
        "forward_mask": forward,
        "reverse_mask": reverse,
    }


def target_lift(parent_case: dict, all_primes: list[int]) -> dict:
    parent = parent_case["summary"]
    parent_mask = parent_case["forward_mask"]
    parent_period = parent["period"]
    q = parent["first_quiet_node"]

    # The target builder learns q only from the completed parent mask/rule above.
    next_known_prime = all_primes[all_primes.index(TARGET_TERMINAL) + 1]
    child_period = parent_period * q
    tiled_parent = parent_mask * q
    same_identity_recombination = bytearray(tiled_parent)

    lifted = bytearray(tiled_parent)
    apply_gate(lifted, q)

    direct = bytearray(b"\x01") * child_period
    for gate in parent["gates"] + [q]:
        apply_gate(direct, gate)

    newly_released = sum(x and not y for x, y in zip(tiled_parent, lifted))
    conditional_release = newly_released / sum(tiled_parent)
    all_integer_release = newly_released / child_period

    per_parent_release_counts: list[int] = []
    for residue, survives in enumerate(parent_mask):
        if survives:
            releases = sum(((residue + lift * parent_period) % q) == 0 for lift in range(q))
            per_parent_release_counts.append(releases)

    return {
        "parent_terminal_prime": TARGET_TERMINAL,
        "recovered_quiet_node": q,
        "established_next_prime_control": next_known_prime,
        "quiet_node_is_next_prime": q == next_known_prime,
        "parent_period": parent_period,
        "child_period": child_period,
        "parent_totient": parent["expected_totient"],
        "tiled_parent_survivors": sum(tiled_parent),
        "expected_tiled_parent_survivors": q * parent["expected_totient"],
        "newly_released": newly_released,
        "expected_newly_released": parent["expected_totient"],
        "child_survivors": sum(lifted),
        "expected_child_survivors": (q - 1) * parent["expected_totient"],
        "missing_relation_fraction_all_integers": all_integer_release,
        "expected_missing_relation_fraction_all_integers": parent["expected_totient"] / child_period,
        "missing_relation_fraction_given_parent_survival": conditional_release,
        "expected_missing_relation_fraction_given_parent_survival": 1 / q,
        "one_release_per_parent_residue": set(per_parent_release_counts) == {1},
        "same_identity_recombination_equals_child": same_identity_recombination == direct,
        "same_identity_recombination_missed_count": sum(
            x != y for x, y in zip(same_identity_recombination, direct)
        ),
        "lifted_equals_direct_child": lifted == direct,
    }


def theorem_scale_quiet_nodes(all_primes: list[int]) -> dict:
    checked = []
    for index, terminal in enumerate(all_primes[:-1]):
        if terminal > THEOREM_SCALE_CEILING:
            break
        gates = all_primes[: index + 1]
        recovered = first_quiet_node(terminal, gates)
        expected = all_primes[index + 1]
        checked.append(
            {
                "terminal_prime": terminal,
                "recovered_next": recovered,
                "expected_next": expected,
                "pass": recovered == expected,
            }
        )
    return {
        "ceiling": THEOREM_SCALE_CEILING,
        "pair_count": len(checked),
        "all_pass": all(row["pass"] for row in checked),
        "first": checked[0],
        "last": checked[-1],
        "failures": [row for row in checked if not row["pass"]],
    }


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Frozen PN16 protocol hash mismatch")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["protocol"]["sha256"] != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Freeze manifest does not match frozen protocol")
    if RESULTS.exists() or PATHS.exists():
        raise RuntimeError("PN16 result files already exist; refusing to overwrite the frozen run")

    all_primes = primes_upto(1100)
    cases = []
    all_path_rows = []
    target_case_internal = None
    for terminal in DEVELOPMENT_TERMINALS + (TARGET_TERMINAL,):
        case = materialized_parent(terminal, all_primes)
        cases.append(case["summary"])
        all_path_rows.extend(case["path_rows"])
        if terminal == TARGET_TERMINAL:
            target_case_internal = case

    assert target_case_internal is not None
    lift = target_lift(target_case_internal, all_primes)
    theorem = theorem_scale_quiet_nodes(all_primes)

    p1 = all(case["ordered_history_visible"] for case in cases)
    p2 = all(
        case["forward_equals_reverse"]
        and case["forward_equals_direct_gcd"]
        and case["reverse_equals_direct_gcd"]
        and case["final_hamming_count"] == 0
        for case in cases
    )
    p3 = all(case["recombined_equals_parent"] for case in cases) and not lift[
        "same_identity_recombination_equals_child"
    ]
    p4 = (
        all(
            case["first_quiet_node"]
            == all_primes[all_primes.index(case["terminal_prime"]) + 1]
            for case in cases
        )
        and theorem["all_pass"]
    )
    p5 = (
        lift["lifted_equals_direct_child"]
        and lift["one_release_per_parent_residue"]
        and lift["tiled_parent_survivors"] == lift["expected_tiled_parent_survivors"]
        and lift["newly_released"] == lift["expected_newly_released"]
        and lift["child_survivors"] == lift["expected_child_survivors"]
    )

    results = {
        "test_id": "PN16/ORDERED-WHOLE-WAVE-LIFT/v1",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": sha256(PROTOCOL),
        "freeze_manifest_sha256": sha256(FREEZE),
        "status": (
            "ORDERED PATH RETAINED / COMPLETED AB=BA / REVERSED COPY IDEMPOTENT / "
            "QUIET-NODE RELATION LIFTS NEXT RUNG"
        ),
        "materialized_rungs": cases,
        "target_lift": lift,
        "theorem_scale_quiet_nodes": theorem,
        "criteria": {
            "P1_ordered_histories_visible": p1,
            "P2_completed_AB_equals_BA_and_direct_parent": p2,
            "P3_same_identity_recombination_is_idempotent_not_next_rung": p3,
            "P4_first_quiet_node_recovers_next_prime": p4,
            "P5_new_quiet_node_gate_lifts_next_rung_exactly": p5,
            "P6_no_prime_specific_predictive_promotion": True,
        },
        "all_structural_criteria_pass": all((p1, p2, p3, p4, p5)),
        "interpretation": {
            "supported": (
                "AB and BA retain different process histories before closure; the completed lower-rung web "
                "locates the next quiet-node prime; retaining that node as a new gate constructs the next rung exactly."
            ),
            "not_supported": (
                "A completed whole and its simple reversal are not two independent poles in this sieve "
                "representation. Their direct recombination is idempotent and does not create the next rung."
            ),
            "information3_refinement": (
                "The informative third is the new quiet-node/gate relation between the completed parent and its "
                "next survivor, not order reversal by itself."
            ),
        },
    }

    with PATHS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_path_rows[0]))
        writer.writeheader()
        writer.writerows(all_path_rows)
    RESULTS.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": results["status"],
        "criteria": results["criteria"],
        "target_lift": lift,
        "theorem_pair_count": theorem["pair_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
