"""Independent structural validation for the PN10B post-hoc geometry outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "PN10B_EVENT_GEOMETRY_RESULTS.json"
TRACES = ROOT / "PN10B_EVENT_CENTERED_TRACES.csv"
LANDMARKS = ROOT / "PN10B_CHILD_LANDMARK_COUNTS.csv"
EXAMPLES = ROOT / "PN10B_PRIME_CHILD_EXAMPLES.csv"
NEIGHBORHOODS = ROOT / "PN10B_EXAMPLE_NEIGHBORHOODS.csv"
FIGURE = ROOT / "PN10B_EVENT_GEOMETRY_FIGURE.png"
OUTPUT = ROOT / "PN10B_EVENT_GEOMETRY_VALIDATION.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def check(name: str, passed: bool, detail: str) -> dict[str, str | bool]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    with TRACES.open(newline="", encoding="utf-8") as handle:
        traces = list(csv.DictReader(handle))
    with LANDMARKS.open(newline="", encoding="utf-8") as handle:
        landmarks = list(csv.DictReader(handle))
    with EXAMPLES.open(newline="", encoding="utf-8") as handle:
        examples = list(csv.DictReader(handle))
    with NEIGHBORHOODS.open(newline="", encoding="utf-8") as handle:
        neighborhoods = list(csv.DictReader(handle))

    checks: list[dict[str, str | bool]] = []
    scope = results["scope"]
    checks.append(check("raw interval row count", scope["raw_integer_count"] == 1_000_000, str(scope)))
    checks.append(
        check(
            "known PN10B fresh counts",
            scope["prime_count"] == 45_166
            and scope["c090_survivor_count"] == 54_275
            and scope["c090_survivor_composite_count"] == 9_109,
            str(scope),
        )
    )
    checks.append(check("two event profiles and 65 offsets", len(traces) == 130, f"rows={len(traces)}"))

    zero = [row for row in traces if row["event"] == "prime_center" and int(row["offset"]) == 0]
    zero_ok = len(zero) == 1 and all(
        abs(float(zero[0][field]) - 1.0) < 1e-15
        for field in ("prime_rate", "survivor_rate", "parent_progress_mean", "parent_progress_median")
    )
    checks.append(check("prime event is exact parent ridge", zero_ok, str(zero[0] if zero else None)))

    odd_rows = [row for row in traces if row["event"] == "prime_center" and int(row["offset"]) % 2 != 0]
    odd_ok = all(float(row["prime_rate"]) == 0.0 for row in odd_rows)
    checks.append(check("odd offsets around odd primes are composite", odd_ok, f"rows={len(odd_rows)}"))

    closure_errors = [abs(float(row["phase_a"]) + float(row["phase_b"]) - 2.0) for row in examples]
    formula_errors = []
    for row in examples:
        q = int(row["gate_q"])
        r = int(row["remainder"])
        formula_errors.append(abs(float(row["phase_a"]) - 2.0 * r / q))
    checks.append(
        check(
            "example A+B closure and modular formula",
            max(closure_errors) < 1e-14 and max(formula_errors) < 1e-14,
            f"max_closure={max(closure_errors):.3g}; max_formula={max(formula_errors):.3g}",
        )
    )
    checks.append(check("five examples by nine gates", len(examples) == 45, f"rows={len(examples)}"))
    valid_neighborhood_rows = all(
        abs(int(row["n"]) - int(row["center_prime"])) == abs(int(row["offset"]))
        and int(row["n"]) - int(row["center_prime"]) == int(row["offset"])
        for row in neighborhoods
    )
    checks.append(
        check(
            "example neighborhoods stay inside the interval and preserve signed offsets",
            len(neighborhoods) == 156 and valid_neighborhood_rows,
            f"rows={len(neighborhoods)}; signed_offsets_valid={valid_neighborhood_rows}",
        )
    )

    landmark_totals: dict[str, int] = {}
    for row in landmarks:
        landmark_totals[row["population"]] = landmark_totals.get(row["population"], 0) + int(row["count"])
    expected = {"prime": 45_166 * 9, "survivor_composite": 9_109 * 9}
    checks.append(check("landmark bins exhaust both populations", landmark_totals == expected, str(landmark_totals)))

    pooled_prime_mean = results["node_distributions"]["prime"]["pooled_child_phase_a"]["mean"]
    centroid_prime_mean = results["node_distributions"]["prime"]["child_centroid"]["mean"]
    checks.append(
        check(
            "pooled A mean equals mean node centroid",
            abs(pooled_prime_mean - centroid_prime_mean) < 1e-14,
            f"pooled={pooled_prime_mean}; centroid={centroid_prime_mean}",
        )
    )

    with Image.open(FIGURE) as image:
        figure_ok = image.size == (1660, 1220) and image.mode == "RGB"
        figure_detail = f"size={image.size}; mode={image.mode}"
    checks.append(check("figure dimensions and mode", figure_ok, figure_detail))
    checks.append(
        check(
            "frozen registered verdict preserved",
            results["registered_pn10b_verdict_unchanged"] == "NULL"
            and results["status"] == "post_hoc_descriptive_only",
            f"status={results['status']}; verdict={results['registered_pn10b_verdict_unchanged']}",
        )
    )

    failures = [item for item in checks if not item["passed"]]
    output = {
        "validator": "independent structural and arithmetic spot-check",
        "passed": not failures,
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "checks": checks,
        "artifact_sha256": {
            path.name: sha256(path)
            for path in (RESULTS, TRACES, LANDMARKS, EXAMPLES, NEIGHBORHOODS, FIGURE)
        },
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
