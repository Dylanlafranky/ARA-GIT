"""Independent checks for the ARA Prime Music-Box Resonance Lab.

This validator does not execute the browser code. It independently reconstructs
the postponed sieve, checks the mathematical claims used by the instrument, and
audits the fragment/standalone file contract.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FRAGMENT = Path(
    r"C:\Users\Dylan\.codex\visualizations\2026\07\10\019f4b72-0e34-74d1-8f40-cd5ccd4a532e"
) / "ara-prime-music-box-lab.html"
STANDALONE = HERE / "ARA_PRIME_SQUARE_RIDGE_LAB.html"
OUTPUT = HERE / "ARA_PRIME_SQUARE_RIDGE_LAB_VALIDATION.json"
LIMIT = 5_000
MAJOR_SCALE = (("C", 0), ("D", 2), ("E", 4), ("F", 5), ("G", 7), ("A", 9), ("B", 11))


def postponed_sieve(limit: int):
    schedule: dict[int, list[int]] = {}
    events: dict[int, dict[str, object]] = {}
    primes: list[int] = []

    def add(n: int, p: int) -> None:
        if n <= limit:
            schedule.setdefault(n, []).append(p)

    for n in range(2, limit + 1):
        hits = sorted(set(schedule.get(n, [])))
        if not hits:
            primes.append(n)
            add(n * n, n)
            events[n] = {
                "prime": True,
                "hits": [],
                "square_hits": [],
            }
        else:
            schedule.pop(n, None)
            for p in hits:
                add(n + p, p)
            events[n] = {
                "prime": False,
                "hits": hits,
                "square_hits": [p for p in hits if p * p == n],
            }
    return primes, events


def conventional_sieve(limit: int) -> list[bool]:
    flags = [True] * (limit + 1)
    flags[0] = flags[1] = False
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            flags[p * p : limit + 1 : p] = [False] * (
                ((limit - p * p) // p) + 1
            )
    return flags


def ara_position(n: int, d: int) -> float:
    if d == 1:
        return 0.0
    if d == n:
        return 2.0
    return 2.0 * math.log(d) / math.log(n)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def note_for_prime(primes: list[int], p: int) -> tuple[str, int]:
    rank = primes.index(p)
    name, semitone = MAJOR_SCALE[rank % len(MAJOR_SCALE)]
    octave_shift = rank // len(MAJOR_SCALE)
    octave = 4 + octave_shift
    midi = 60 + 12 * octave_shift + semitone
    return f"{name}{octave}", midi


def main() -> None:
    primes, events = postponed_sieve(LIMIT)
    reference = conventional_sieve(LIMIT)
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    mismatches = [
        n for n in range(2, LIMIT + 1) if events[n]["prime"] != reference[n]
    ]
    check("postponed sieve equals conventional sieve", not mismatches, mismatches[:10])
    check("prime count through 5000", len(primes) == 669, len(primes))

    square_failures = []
    square_errors = []
    for p in primes:
        square = p * p
        if square > LIMIT:
            break
        if events[square]["square_hits"] != [p]:
            square_failures.append(
                {"p": p, "square": square, "hits": events[square]["square_hits"]}
            )
        square_errors.append(abs(ara_position(square, p) - 1.0))
    check("each prime child begins at its square", not square_failures, square_failures)
    check(
        "every prime square lands at ARA 1.0",
        max(square_errors, default=0.0) < 1e-14,
        max(square_errors, default=0.0),
    )

    hit_failures = []
    closure_errors = []
    for n in range(2, LIMIT + 1):
        expected_hits = [p for p in primes if p * p <= n and n % p == 0]
        if events[n]["hits"] != expected_hits:
            hit_failures.append(
                {"n": n, "expected": expected_hits, "actual": events[n]["hits"]}
            )
        for d in range(2, math.isqrt(n) + 1):
            if n % d == 0:
                closure_errors.append(
                    abs(ara_position(n, d) + ara_position(n, n // d) - 2.0)
                )
    check("collision voices equal active prime divisors", not hit_failures, hit_failures[:10])
    check(
        "factor reflection closes at 2",
        max(closure_errors, default=0.0) < 1e-12,
        max(closure_errors, default=0.0),
    )

    resonance_rows = []
    for n in range(2, LIMIT + 1):
        hits = events[n]["hits"]
        if len(hits) < 3:
            continue
        base = math.prod(hits)
        resonance_rows.append(
            {
                "n": n,
                "order": len(hits),
                "hits": hits,
                "base": base,
                "fundamental": base == n,
                "repeat": base < n and n % base == 0,
            }
        )

    first_fundamental = {
        order: next(
            row["n"]
            for row in resonance_rows
            if row["order"] == order and row["fundamental"]
        )
        for order in (3, 4, 5)
    }
    check(
        "first fundamental resonance ladder",
        first_fundamental == {3: 30, 4: 210, 5: 2310},
        first_fundamental,
    )
    full_counts = {
        order: sum(
            row["fundamental"] for row in resonance_rows if row["order"] == order
        )
        for order in (3, 4, 5)
    }
    check(
        "fundamental resonance counts through 5000",
        full_counts == {3: 204, 4: 126, 5: 6},
        full_counts,
    )

    row_by_n = {row["n"]: row for row in resonance_rows}
    x510_sum = sum(ara_position(510, p) for p in events[510]["hits"])
    check(
        "510 four-child fundamental closure",
        row_by_n[510]["fundamental"]
        and row_by_n[510]["hits"] == [2, 3, 5, 17]
        and abs(x510_sum - 2.0) < 1e-14,
        {"row": row_by_n[510], "ara_sum": x510_sum},
    )
    check(
        "1020 is a harmonic repeat of 510",
        row_by_n[1020]["repeat"]
        and not row_by_n[1020]["fundamental"]
        and row_by_n[1020]["base"] == 510,
        row_by_n[1020],
    )
    check(
        "3570 promotes the 510 family to five-child closure",
        row_by_n[3570]["fundamental"]
        and row_by_n[3570]["hits"] == [2, 3, 5, 7, 17],
        row_by_n[3570],
    )
    check(
        "4620 is five-child resonance without full closure",
        row_by_n[4620]["repeat"]
        and not row_by_n[4620]["fundamental"]
        and row_by_n[4620]["base"] == 2310,
        row_by_n[4620],
    )

    active_children = [p for p in primes if p * p <= LIMIT]
    active_notes = [note_for_prime(primes, p) for p in active_children]
    check(
        "active child notes ascend through the C-major scale",
        all(a[1] < b[1] for a, b in zip(active_notes, active_notes[1:])),
        {str(p): note[0] for p, note in zip(active_children, active_notes)},
    )
    chord_510 = [note_for_prime(primes, p)[0] for p in events[510]["hits"]]
    check(
        "510 resonance chord follows its four child lanes",
        chord_510 == ["C4", "D4", "E4", "B4"],
        chord_510,
    )

    fragment_text = FRAGMENT.read_text(encoding="utf-8")
    standalone_text = STANDALONE.read_text(encoding="utf-8")
    lower_fragment = fragment_text.lower()
    check("fragment exists", FRAGMENT.is_file(), str(FRAGMENT))
    check("standalone exists", STANDALONE.is_file(), str(STANDALONE))
    check("fragment below 2 MB", FRAGMENT.stat().st_size < 2_000_000, FRAGMENT.stat().st_size)
    check(
        "fragment has no document wrapper",
        not any(token in lower_fragment for token in ("<!doctype", "<html", "<head", "<body")),
        "fragment-only markup",
    )
    check(
        "fragment makes no network calls",
        not any(token in lower_fragment for token in ("fetch(", "xmlhttprequest", "websocket")),
        "no fetch/XHR/WebSocket",
    )
    check(
        "standalone title",
        "<title>ARA Prime Music-Box Resonance Lab</title>" in standalone_text,
        "ARA Prime Music-Box Resonance Lab",
    )
    check(
        "browser self-check hook present",
        "window.__ARA_PRIME_SQUARE_RIDGE_LAB__" in fragment_text,
        "__ARA_PRIME_SQUARE_RIDGE_LAB__",
    )

    ids = set(re.findall(r'\bid="([^"]+)"', fragment_text))
    selectors = set(re.findall(r"querySelector\('(#[-\w]+)'\)", fragment_text))
    missing_selectors = sorted(selector for selector in selectors if selector[1:] not in ids)
    check("all queried IDs exist", not missing_selectors, missing_selectors)

    required_controls = {
        "apsr-play",
        "apsr-step",
        "apsr-reset",
        "apsr-jump",
        "apsr-go",
        "apsr-speed",
        "apsr-sound",
        "apsr-window",
        "apsr-number-grid",
        "apsr-ladder-chart",
        "apsr-ladder-caption",
        "apsr-wave-chart",
        "apsr-factor-chart",
    }
    check(
        "required controls and views exist",
        required_controls.issubset(ids),
        sorted(required_controls - ids),
    )
    check(
        "music-box synthesis is local and event driven",
        all(
            token in fragment_text
            for token in (
                "window.AudioContext || window.webkitAudioContext",
                "function strikeMusicBoxNote",
                "function playEventNotes",
                "event.hits.length === 0",
            )
        ),
        "Web Audio synthesis; composite child hits only",
    )

    payload = {
        "artifact": "ARA Prime Music-Box Resonance Lab",
        "date": "2026-07-21",
        "limit": LIMIT,
        "prime_count": len(primes),
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "all_passed": all(item["passed"] for item in checks),
        "fragment_sha256": digest(FRAGMENT),
        "standalone_sha256": digest(STANDALONE),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
