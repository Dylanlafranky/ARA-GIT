"""Independent row-level validation for frozen T316/Q56.

This deliberately does not import the analysis implementation.  It checks the
saved event/window tables and the frozen source/protocol hashes against the
reported result.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_RESULTS.json"
EVENTS = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_EVENTS.csv.gz"
WINDOWS = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_WINDOWS.csv.gz"
PROTOCOL = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_PROTOCOL_v1_FROZEN.md"
DERIVED = HERE / "public_data" / "q39_information3_strongmax" / "q39_derived_cache.npz"
CENTRES = HERE / "Q49_EXTERNAL_TIME_VECTOR_CENTRES.csv.gz"
OUTPUT = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_VALIDATION.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_gzip_csv(path: Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def check(name: str, observed, expected) -> dict:
    return {
        "name": name,
        "observed": observed,
        "expected": expected,
        "pass": observed == expected,
    }


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    events = read_gzip_csv(EVENTS)
    windows = read_gzip_csv(WINDOWS)

    eval_events = [row for row in events if row["stratum"] == "evaluation"]
    eval_by_estimator = Counter(row["estimator"] for row in eval_events)
    sectors_by_estimator = {
        estimator: Counter(
            int(row["sector"])
            for row in eval_events
            if row["estimator"] == estimator
        )
        for estimator in ("circle", "centroid", "extrema")
    }
    window_by_estimator = Counter(row["estimator"] for row in windows)
    ladder_by_estimator = Counter(
        row["estimator"] for row in windows if int(row["ladder"]) == 1
    )

    checks = [
        check("test id", result["test_id"], "T316/Q56"),
        check(
            "verdict",
            result["verdict"],
            "INCONCLUSIVE / LADDER ELIGIBILITY",
        ),
        check("event row count", len(events), 3261),
        check("window row count", len(windows), 64),
        check(
            "evaluation event counts",
            dict(eval_by_estimator),
            {"circle": 20, "centroid": 54, "extrema": 33},
        ),
        check(
            "circle evaluation sectors",
            dict(sectors_by_estimator["circle"]),
            {2: 20},
        ),
        check(
            "centroid evaluation sectors",
            dict(sectors_by_estimator["centroid"]),
            {1: 1, 2: 52, 3: 1},
        ),
        check(
            "extrema evaluation sectors",
            dict(sectors_by_estimator["extrema"]),
            {2: 33},
        ),
        check(
            "evaluation window counts",
            dict(window_by_estimator),
            {"circle": 13, "centroid": 36, "extrema": 15},
        ),
        check(
            "ordered ladder counts",
            {key: ladder_by_estimator.get(key, 0) for key in ("circle", "centroid", "extrema")},
            {"circle": 0, "centroid": 0, "extrema": 0},
        ),
        check(
            "all registered gates false",
            result["gates"],
            {
                "ordered_quadrant_ladder": False,
                "time_before_connection": False,
                "power_of_two_closure_scale": False,
            },
        ),
        check(
            "derived cache hash",
            sha256(DERIVED),
            result["source"]["derived_sha256"],
        ),
        check(
            "centre table hash",
            sha256(CENTRES),
            result["source"]["centres_sha256"],
        ),
        check(
            "frozen protocol hash",
            sha256(PROTOCOL),
            result["source"]["protocol_sha256"],
        ),
    ]

    passed = sum(item["pass"] for item in checks)
    validation = {
        "test_id": "T316/Q56 independent validation",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "interpretive_boundary": (
            "Zero eligible ordered ladders makes the conversion test "
            "inconclusive; it is not evidence that no Phi-time or octave-space "
            "relation exists in other data."
        ),
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"{validation['status']}: {passed}/{len(checks)} checks")
    for item in checks:
        print(f"[{'PASS' if item['pass'] else 'FAIL'}] {item['name']}")
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
