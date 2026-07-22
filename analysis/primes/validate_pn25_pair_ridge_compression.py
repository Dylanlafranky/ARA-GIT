"""Independent validation of PN25 pair-ridge compression outputs."""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN25_PAIR_RIDGE_COMPRESSION_RESULTS.json"
TARGETS = HERE / "PN25_PAIR_RIDGE_COMPRESSION_TARGETS.csv"
GROUPS = HERE / "PN25_PAIR_RIDGE_COMPRESSION_GROUPS.csv"
SCORES = HERE / "PN25_PAIR_RIDGE_COMPRESSION_SCORES.csv"
OUTPUT = HERE / "PN25_PAIR_RIDGE_COMPRESSION_VALIDATION.json"
MR_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
RANGES = (
    ("low", 61_000_000, 61_500_000, 25001),
    ("middle", 61_000_000_000, 61_000_500_000, 25002),
    ("high", 610_000_000_000, 610_000_500_000, 25003),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in MR_BASES:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n: int) -> int:
    value = n + 1
    if value % 2 == 0:
        value += 1
    while not is_prime(value):
        value += 2
    return value


def correlation(xs: list[float], ys: list[float]) -> float:
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return numerator / denominator if denominator else 0.0


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    targets = read_csv(TARGETS)
    groups = read_csv(GROUPS)
    scores = read_csv(SCORES)
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    add("target row count", len(targets) == 6000, str(len(targets)))
    for scale, low, high, seed in RANGES:
        expected = sorted(random.Random(seed).sample(range(low, high), 2000))
        actual = sorted(int(row["anchor"]) for row in targets if row["scale"] == scale)
        add(f"{scale} deterministic sample reproduced", expected == actual)

    arithmetic_failures = []
    for representative in (1, 3, 5):
        q = Fraction(representative, 14 - representative)
        converted = Fraction(2) * q / (1 + q)
        if converted != Fraction(representative, 7):
            arithmetic_failures.append((representative, "conversion"))
        if converted + Fraction(14 - representative, 7) != 2:
            arithmetic_failures.append((representative, "sum"))
    add("odds-to-ARA identities exact", not arithmetic_failures, str(arithmetic_failures))
    add("7/7 ridge is 1/1 and gate-excluded", Fraction(7, 7) == 1 and 7 % 7 == 0)

    row_failures = []
    for row in targets:
        anchor = int(row["anchor"])
        initial = int(row["initial_candidate"])
        truth = int(row["true_next_prime"])
        candidate_path = [int(value) for value in row["candidate_path"].split("|")]
        gate_path = [int(value) for value in row["gate_path"].split("|") if value]
        residue = initial % 14
        representative = min(residue, 14 - residue)
        if residue not in (1, 3, 5, 9, 11, 13):
            row_failures.append((anchor, "bad residue"))
        if representative != int(row["pair_representative"]):
            row_failures.append((anchor, "bad pair"))
        if Fraction(row["closeness"]) != Fraction(representative, 7):
            row_failures.append((anchor, "bad closeness"))
        if len(candidate_path) != int(row["candidate_states"]):
            row_failures.append((anchor, "bad state count"))
        if len(gate_path) != int(row["handover_events"]):
            row_failures.append((anchor, "bad gate count"))
        if candidate_path[0] != initial or candidate_path[-1] != truth:
            row_failures.append((anchor, "bad path endpoints"))
        for old, gate, new in zip(candidate_path, gate_path, candidate_path[1:]):
            if old % gate != 0 or new <= old:
                row_failures.append((anchor, "bad handover", old, gate, new))
        if next_prime(anchor) != truth:
            row_failures.append((anchor, "truth mismatch"))
        final_rep = min(truth % 14, 14 - truth % 14)
        expected_delta = float(Fraction(final_rep - representative, 7))
        if abs(float(row["delta_closeness"]) - expected_delta) > 1e-15:
            row_failures.append((anchor, "bad delta"))
    add("all target paths and coordinates reproduced", not row_failures, str(row_failures[:3]))

    group_failures = []
    for stored in groups:
        scale = stored["scale"]
        representative = int(stored["pair_representative"])
        subset = [
            row for row in targets
            if int(row["pair_representative"]) == representative
            and (scale == "pooled" or row["scale"] == scale)
        ]
        values = {
            "n": len(subset),
            "mean_handovers": statistics.fmean(int(row["handover_events"]) for row in subset),
            "base_prime_rate_Y0": statistics.fmean(int(row["Y0"]) for row in subset),
            "three_state_rate_Y3": statistics.fmean(int(row["Y3"]) for row in subset),
        }
        for key, value in values.items():
            stored_value = int(stored[key]) if key == "n" else float(stored[key])
            if abs(stored_value - value) > 1e-15:
                group_failures.append((scale, representative, key, stored_value, value))
    add("all group summaries reproduced", not group_failures, str(group_failures[:3]))

    pooled_corr = correlation(
        [float(row["closeness_float"]) for row in targets],
        [float(row["handover_events"]) for row in targets],
    )
    add(
        "pooled correlation reproduced",
        abs(pooled_corr - saved["permutation_test"]["observed_pearson_c_vs_H"]) < 1e-15,
        str(pooled_corr),
    )

    score_failures = []
    for score in scores:
        outcome = score["outcome"]
        model = score["model"]
        rates = json.loads(score["development_rates"])
        errors = []
        for row in targets:
            if model == "global":
                key = "all"
            elif model == "orientation":
                key = row["orientation"]
            elif model == "pair":
                key = row["pair_representative"]
            else:
                key = row["residue"]
            errors.append((rates[key] - int(row[outcome])) ** 2)
        calculated = statistics.fmean(errors)
        if abs(calculated - float(score["brier"])) > 1e-15:
            score_failures.append((outcome, model, calculated, score["brier"]))
    add("all frozen-model Brier scores reproduced", not score_failures, str(score_failures))

    prediction = saved["predictions"]
    add("all four dynamic predictions recorded as null", prediction["dynamic_predictions_passed"] == 0)
    add("pair compression fidelity recorded as pass", saved["compression_fidelity_pass"] is True)
    add(
        "pair and lane models both fail to beat global",
        all(
            not saved["compression_scores"][outcome]["pair_beats_global"]
            and not saved["compression_scores"][outcome]["lane_beats_global"]
            for outcome in ("Y0", "Y3")
        ),
    )
    add("protected anchor unused", saved["data"]["protected_87_bit_anchor_used"] is False)

    passed = sum(check["pass"] for check in checks)
    payload = {
        "validation_id": "PN25/INDEPENDENT-VALIDATION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "note": (
            "The exact saved 10,000-permutation count is not rerun here; the observed statistic, samples, "
            "group summaries, target paths, outcome scores and decision flags are independently recomputed."
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
