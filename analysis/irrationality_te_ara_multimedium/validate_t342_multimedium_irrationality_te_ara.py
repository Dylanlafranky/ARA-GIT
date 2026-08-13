#!/usr/bin/env python3
"""Independent output validator for frozen test T342.

This deliberately does not import the analysis runner.  It reconstructs the
reported transition metrics, null probabilities, eligibility gates, source
hashes and final verdict from the exported artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STEM = "T342_MULTIMEDIUM_IRRATIONALITY_TE_ARA"
PROTOCOL = HERE / f"{STEM}_PROTOCOL_v1_FROZEN.md"
ADDENDUM = HERE / f"{STEM}_COMPUTATIONAL_ADDENDUM_v1_FROZEN.md"
SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
QUADRANTS = HERE / f"{STEM}_QUADRANTS.csv"
TRANSITIONS = HERE / f"{STEM}_TRANSITIONS.csv"
NULLS = HERE / f"{STEM}_NULLS.csv"
SAMPLE = HERE / f"{STEM}_EVENT_SAMPLE.csv"
MANIFEST = HERE / f"{STEM}_SOURCE_MANIFEST.json"
RESULTS = HERE / f"{STEM}_RESULTS.json"
OUTPUT = HERE / f"{STEM}_VALIDATION.json"

SECTORS = [
    "contracting_reverse",
    "expanding_reverse",
    "expanding_forward",
    "contracting_forward",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tol: float = 1e-11) -> bool:
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)


def transition_metrics(rows: list[dict[str, str]]) -> dict[str, float | int]:
    idx = {name: i for i, name in enumerate(SECTORS)}
    matrix = [[0] * 4 for _ in range(4)]
    for row in rows:
        matrix[idx[row["from_sector"]]][idx[row["to_sector"]]] += int(row["count"])

    total = sum(map(sum, matrix))
    same = sum(matrix[i][i] for i in range(4))
    adjacent = diagonal = clockwise = counterclockwise = 0
    for i in range(4):
        for j in range(4):
            if i == j:
                continue
            step = (j - i) % 4
            if step in (1, 3):
                adjacent += matrix[i][j]
                if step == 1:
                    clockwise += matrix[i][j]
                else:
                    counterclockwise += matrix[i][j]
            elif step == 2:
                diagonal += matrix[i][j]

    row_sums = [sum(r) for r in matrix]
    col_sums = [sum(matrix[i][j] for i in range(4)) for j in range(4)]
    mutual = 0.0
    for i in range(4):
        for j in range(4):
            n = matrix[i][j]
            if n:
                p = n / total
                mutual += p * math.log(p / ((row_sums[i] / total) * (col_sums[j] / total)))
    entropy_next = -sum((n / total) * math.log(n / total) for n in col_sums if n)
    nmi = mutual / entropy_next if entropy_next else 0.0
    changed = adjacent + diagonal
    return {
        "transitions": total,
        "changed_transitions": changed,
        "adjacent_transitions": adjacent,
        "diagonal_transitions": diagonal,
        "adjacency_fraction": adjacent / changed if changed else float("nan"),
        "same_sector_fraction": same / total if total else float("nan"),
        "clockwise_adjacent": clockwise,
        "counterclockwise_adjacent": counterclockwise,
        "normalized_mutual_information": nmi,
    }


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    summary_rows = read_csv(SUMMARY)
    quadrant_rows = read_csv(QUADRANTS)
    transition_rows = read_csv(TRANSITIONS)
    null_rows = read_csv(NULLS)
    sample_rows = read_csv(SAMPLE)

    check("protocol hash", sha256(PROTOCOL) == manifest["protocol_sha256"], sha256(PROTOCOL))
    check("addendum hash", sha256(ADDENDUM) == manifest["computational_addendum_sha256"], sha256(ADDENDUM))

    missing = []
    mismatched = []
    for domain, group in manifest["sources"].items():
        for item in group["files"]:
            path = REPO / item["path"]
            if not path.exists():
                missing.append(str(path))
            elif sha256(path) != item["sha256"]:
                mismatched.append(str(path))
    check("source files present", not missing, missing)
    check("source hashes reproduce", not mismatched, mismatched)

    summary = {(r["domain"], r["split"]): r for r in summary_rows}
    quadrants: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    transitions: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    nulls: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in quadrant_rows:
        quadrants[(row["domain"], row["split"])].append(row)
    for row in transition_rows:
        transitions[(row["domain"], row["split"])].append(row)
    for row in null_rows:
        nulls[(row["domain"], row["split"])].append(row)

    metric_failures = []
    gate_failures = []
    for key, reported in summary.items():
        got = transition_metrics(transitions[key])
        for field, value in got.items():
            actual = float(reported[field])
            if isinstance(value, int):
                okay = int(actual) == value
            else:
                okay = close(actual, float(value))
            if not okay:
                metric_failures.append({"key": key, "field": field, "reported": actual, "recomputed": value})

        reps = nulls[key]
        obs_a = float(got["adjacency_fraction"])
        obs_n = float(got["normalized_mutual_information"])
        p_a = (1 + sum(float(r["adjacency_fraction"]) >= obs_a for r in reps)) / (len(reps) + 1)
        p_n = (1 + sum(float(r["normalized_mutual_information"]) >= obs_n for r in reps)) / (len(reps) + 1)
        shares = [float(r["share"]) for r in quadrants[key]]
        coverage = len(shares) == 4 and min(shares) >= 0.01
        eligible = int(got["transitions"]) >= 1000 and int(got["changed_transitions"]) >= 100 and len(shares) == 4
        passed = eligible and coverage and p_a < 0.05 and p_n < 0.05
        gate_values = {
            "adjacency_shuffle_p": p_a,
            "nmi_shuffle_p": p_n,
            "coverage_pass": coverage,
            "eligible": eligible,
            "grammar_pass": passed,
        }
        for field, value in gate_values.items():
            reported_value: object
            if isinstance(value, bool):
                reported_value = reported[field].strip().lower() == "true"
                okay = reported_value == value
            else:
                reported_value = float(reported[field])
                okay = close(float(reported_value), float(value))
            if not okay:
                gate_failures.append({"key": key, "field": field, "reported": reported_value, "recomputed": value})

    check("transition metrics reproduce", not metric_failures, metric_failures[:20])
    check("null p-values and gates reproduce", not gate_failures, gate_failures[:20])
    check("exactly 1,000 nulls per domain/split", all(len(v) == 1000 for v in nulls.values()), {str(k): len(v) for k, v in nulls.items() if len(v) != 1000})

    closure_errors = []
    for row in sample_rows:
        x = float(row["x_radial_ara"])
        y = float(row["y_angular_ara"])
        if not close(x + (2.0 - x), 2.0) or not close(y + (2.0 - y), 2.0):
            closure_errors.append({"domain": row["domain"], "x": x, "y": y})
    check("sample TE-ARA closure identities", not closure_errors, closure_errors[:10])

    holdout = [r for r in summary_rows if r["split"] == "holdout"]
    eligible_count = sum(r["eligible"].lower() == "true" for r in holdout)
    passing_count = sum(r["grammar_pass"].lower() == "true" for r in holdout)
    support = eligible_count >= 5 and passing_count / eligible_count >= 0.70
    verdict = "SUPPORTED" if support else ("PARTIAL / DOMAIN-SPECIFIC" if passing_count >= 2 else "NOT SUPPORTED")
    check("eligible count", eligible_count == int(results["eligible_domains"]), {"recomputed": eligible_count, "reported": results["eligible_domains"]})
    check("passing count", passing_count == int(results["passing_domains"]), {"recomputed": passing_count, "reported": results["passing_domains"]})
    check("primary verdict", verdict == results["primary_verdict"], {"recomputed": verdict, "reported": results["primary_verdict"]})

    result_holdout = {r["domain"]: r for r in results["domain_holdout"]}
    result_mismatches = []
    for row in holdout:
        other = result_holdout.get(row["domain"])
        if other is None:
            result_mismatches.append({"domain": row["domain"], "reason": "missing from results JSON"})
            continue
        for field in ("eligible", "coverage_pass", "grammar_pass"):
            csv_value = row[field].lower() == "true"
            if bool(other[field]) != csv_value:
                result_mismatches.append({"domain": row["domain"], "field": field, "csv": csv_value, "json": other[field]})
        for field in ("adjacency_fraction", "normalized_mutual_information", "adjacency_shuffle_p", "nmi_shuffle_p"):
            if not close(float(row[field]), float(other[field])):
                result_mismatches.append({"domain": row["domain"], "field": field, "csv": row[field], "json": other[field]})
    check("results JSON matches holdout summary", not result_mismatches, result_mismatches)

    required = [
        HERE / f"{STEM}_FIGURE.png",
        HERE / f"{STEM}_EXPLORER.html",
        HERE / f"{STEM}_REPORT_2026-08-05.md",
    ]
    check("required report and visual artifacts", all(p.exists() and p.stat().st_size > 0 for p in required), [str(p) for p in required])

    passed = all(item["pass"] for item in checks)
    output = {
        "validator": "independent exported-artifact reconstruction; does not import runner",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "recomputed_primary": {
            "eligible_domains": eligible_count,
            "passing_domains": passing_count,
            "cross_domain_support": support,
            "verdict": verdict,
        },
    }
    OUTPUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
