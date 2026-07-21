"""Validate the post-hoc prime resonance and information-lock examples.

Scope: exact integer arithmetic and the declared ARA factor coordinate only.
This is not a prospective prime-prediction test.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "ARA_PRIME_RESONANCE_LOCKS_VALIDATION.json"
LIMIT = 5_000
SCALE = (("C", 0), ("D", 2), ("E", 4), ("F", 5), ("G", 7), ("A", 9), ("B", 11))


def prime_flags(limit: int) -> list[bool]:
    flags = [True] * (limit + 1)
    flags[0] = flags[1] = False
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            flags[p * p : limit + 1 : p] = [False] * (((limit - p * p) // p) + 1)
    return flags


FLAGS = prime_flags(LIMIT)
PRIMES = [n for n in range(2, LIMIT + 1) if FLAGS[n]]


def factorization(n: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    value = n
    p = 2
    while p * p <= value:
        while value % p == 0:
            factors[p] = factors.get(p, 0) + 1
            value //= p
        p += 1
    if value > 1:
        factors[value] = factors.get(value, 0) + 1
    return factors


def active_children(n: int) -> list[int]:
    return [p for p in factorization(n) if p * p <= n]


def child_product(n: int) -> int:
    return math.prod(active_children(n))


def fundamental(n: int) -> bool:
    children = active_children(n)
    return len(children) >= 3 and math.prod(children) == n


def harmonic_repeat(n: int) -> bool:
    children = active_children(n)
    base = math.prod(children)
    return len(children) >= 3 and base < n and n % base == 0


def ara_position(n: int, d: int) -> float:
    return 2.0 * math.log(d) / math.log(n)


def divisor_count(n: int) -> int:
    return math.prod(exponent + 1 for exponent in factorization(n).values())


def note_for_prime(p: int) -> str:
    rank = PRIMES.index(p)
    name, _ = SCALE[rank % len(SCALE)]
    return f"{name}{4 + rank // len(SCALE)}"


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    first_by_voice: dict[int, int] = {}
    voice_counts: dict[int, int] = {}
    for n in range(2, LIMIT + 1):
        voices = len(active_children(n))
        voice_counts[voices] = voice_counts.get(voices, 0) + 1
        first_by_voice.setdefault(voices, n)
    check(
        "first audible collision-order ladder",
        {k: first_by_voice[k] for k in range(6)} == {0: 2, 1: 4, 2: 12, 3: 30, 4: 210, 5: 2310},
        {k: first_by_voice[k] for k in range(6)},
    )
    check(
        "voice-count population through 5000",
        voice_counts == {0: 669, 1: 1964, 2: 1270, 3: 808, 4: 281, 5: 7},
        voice_counts,
    )

    display_30 = [720, 1080, 1440, 1920, 2160, 2880, 3840, 4320, 7680]
    check(
        "display dimensions on the 30 repeat family",
        all(n % 30 == 0 for n in display_30),
        {str(n): n // 30 for n in display_30},
    )
    check("1680 lies on the 210 repeat family", 1680 == 8 * 210, 1680 // 210)
    shadow = {k * 510: k * 512 for k in range(2, 9)}
    check(
        "510 family has exact binary shadow relation",
        all(binary - resonance == 2 * k for k, (resonance, binary) in enumerate(shadow.items(), start=2)),
        shadow,
    )

    pair = {714: factorization(714), 715: factorization(715)}
    check(
        "714 and 715 are consecutive fundamental resonances",
        fundamental(714) and fundamental(715),
        pair,
    )
    sum_714 = sum(factorization(714))
    sum_715 = sum(factorization(715))
    check("Ruth-Aaron additive balance", sum_714 == sum_715 == 29, [sum_714, sum_715])
    first_seven = [2, 3, 5, 7, 11, 13, 17]
    check(
        "714-715 complementary first-seven-prime partition",
        sorted(factorization(714) | factorization(715)) == first_seven
        and set(factorization(714)).isdisjoint(factorization(715)),
        {"714": list(factorization(714)), "715": list(factorization(715))},
    )
    parent_17 = math.prod(first_seven)
    pair_positions = [ara_position(parent_17, 714), ara_position(parent_17, 715)]
    check(
        "714-715 close the 17-primorial diameter",
        714 * 715 == parent_17 == 510_510 and abs(sum(pair_positions) - 2.0) < 1e-14,
        {"parent": parent_17, "positions": pair_positions, "sqrt": math.sqrt(parent_17)},
    )
    check(
        "714-715 notes partition the first C-major octave",
        sorted(note_for_prime(p) for p in factorization(714) | factorization(715))
        == sorted(["C4", "D4", "E4", "F4", "G4", "A4", "B4"]),
        {str(n): [note_for_prime(p) for p in factorization(n)] for n in (714, 715)},
    )

    repeat_triple = (1274, 1275, 1276)
    repeated_children = {}
    closure_rows = {}
    for n in repeat_triple:
        factors = factorization(n)
        repeated = [p for p, exponent in factors.items() if exponent == 2]
        repeated_children[n] = repeated[0] if len(repeated) == 1 else None
        distinct_sum = sum(ara_position(n, p) for p in factors)
        echo = ara_position(n, repeated[0]) if len(repeated) == 1 else float("nan")
        closure_rows[n] = {"distinct_sum": distinct_sum, "echo": echo, "total": distinct_sum + echo}
    check(
        "1274-1276 share the p-squared-q-r repeat shape",
        repeated_children == {1274: 7, 1275: 5, 1276: 2}
        and all(harmonic_repeat(n) for n in repeat_triple),
        repeated_children,
    )
    check(
        "1274-1276 each have twelve divisors",
        [divisor_count(n) for n in repeat_triple] == [12, 12, 12],
        [divisor_count(n) for n in repeat_triple],
    )
    earlier_twelve_runs = [
        n for n in range(1, 1275) if divisor_count(n) == divisor_count(n + 1) == divisor_count(n + 2) == 12
    ]
    check("1274 is the first three-node twelve-divisor run", earlier_twelve_runs == [1274], earlier_twelve_runs)
    check(
        "multiplicity echo restores full ARA closure",
        all(abs(row["total"] - 2.0) < 1e-14 for row in closure_rows.values()),
        closure_rows,
    )

    lock_triple = (1885, 1886, 1887)
    lock_factors = {n: factorization(n) for n in lock_triple}
    check(
        "1885-1887 are consecutive fundamental three-child resonances",
        all(fundamental(n) and len(active_children(n)) == 3 for n in lock_triple),
        lock_factors,
    )
    all_lock_children = [p for n in lock_triple for p in lock_factors[n]]
    check(
        "1885-1887 retain nine separate child lanes",
        len(all_lock_children) == len(set(all_lock_children)) == 9,
        sorted(all_lock_children),
    )
    lock_parent = math.prod(lock_triple)
    parent_positions = [ara_position(lock_parent, n) for n in lock_triple]
    check(
        "three parents close one nine-child parent",
        lock_parent == 6_708_492_570
        and lock_parent == 1886**3 - 1886
        and lock_parent == math.prod(all_lock_children)
        and abs(sum(parent_positions) - 2.0) < 1e-14,
        {"parent": lock_parent, "positions": parent_positions},
    )
    runs_to_limit = [
        n
        for n in range(2, LIMIT - 1)
        if all(fundamental(k) and len(active_children(k)) == 3 for k in (n, n + 1, n + 2))
    ]
    check(
        "1885 is the only full three-by-three run through 5000",
        runs_to_limit == [1885],
        runs_to_limit,
    )

    payload = {
        "artifact": "ARA Prime Resonance Families and Information Locks",
        "date": "2026-07-21",
        "scope": "post-hoc exact arithmetic crosswalk",
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "all_passed": all(item["passed"] for item in checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
