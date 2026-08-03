from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz"
PROTOCOL = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_PROTOCOL_v1_FROZEN.md"
SEEDS = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_SEEDS.csv"
RESULTS = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_RESULTS.json"
OUTPUT = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_VALIDATION.json"
CHILD = "two_turn_7_5"
PARENT = "one_turn_15"
PHI = (1 + math.sqrt(5)) / 2
ATOL = 1e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def close(a: float, b: float, atol: float = ATOL) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=atol)


def independent_recompute() -> dict[tuple[str, int], dict[str, float]]:
    cycles = defaultdict(lambda: {"forward": [], "return": []})
    with gzip.open(SOURCE, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["family"] not in {CHILD, PARENT}:
                continue
            key = (row["archive"], int(row["seed"]), row["pair"], row["family"])
            cycles[key]["forward"].append(float(row["forward_duration"]))
            cycles[key]["return"].append(float(row["return_duration"]))

    pair_balanced = defaultdict(lambda: {"forward": [], "return": []})
    for (archive, seed, _pair, family), values in cycles.items():
        key = (archive, seed, family)
        pair_balanced[key]["forward"].append(statistics.median(values["forward"]))
        pair_balanced[key]["return"].append(statistics.median(values["return"]))

    tier = {}
    for key, values in pair_balanced.items():
        tier[key] = (
            statistics.median(values["forward"]),
            statistics.median(values["return"]),
        )

    keys = {(archive, seed) for archive, seed, family in tier if family == PARENT}
    keys &= {(archive, seed) for archive, seed, family in tier if family == CHILD}
    out = {}
    for archive, seed in sorted(keys):
        pf, pr = tier[(archive, seed, PARENT)]
        cf, cr = tier[(archive, seed, CHILD)]
        r_a, r_b = pf / cf, pr / cr
        p_a = 2 * pf / (pf + pr)
        c_a = 2 * cf / (cf + cr)
        p_b, c_b = 2 - p_a, 2 - c_a
        out[(archive, seed)] = {
            "parent_forward_duration": pf,
            "parent_return_duration": pr,
            "child_forward_duration": cf,
            "child_return_duration": cr,
            "r_A": r_a,
            "s_A": 1 + 1 / r_a,
            "r_B": r_b,
            "s_B": 1 + 1 / r_b,
            "P_A": p_a,
            "P_B": p_b,
            "C_A": c_a,
            "C_B": c_b,
            "h_A": 2 - p_a + 0.5 * c_a,
            "h_B": 2 - p_b + 0.5 * c_b,
            "h_A_local_control": 2 - p_a + c_a,
            "h_B_local_control": 2 - p_b + c_b,
        }
    return out


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    computed = independent_recompute()
    delivered = {}
    with SEEDS.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            delivered[(row["archive"], int(row["seed"]))] = row

    errors = []
    if set(computed) != set(delivered):
        errors.append("seed key mismatch")
    numeric_fields = list(next(iter(computed.values())))
    max_abs_difference = 0.0
    for key in sorted(set(computed) & set(delivered)):
        for field in numeric_fields:
            difference = abs(computed[key][field] - float(delivered[key][field]))
            max_abs_difference = max(max_abs_difference, difference)
            if difference > ATOL:
                errors.append(f"{key} {field}: {difference}")

    archive_median_checks = {}
    for archive in sorted({key[0] for key in computed}):
        archive_median_checks[archive] = {}
        for field in ("r_A", "s_A", "r_B", "s_B", "h_A", "h_B"):
            median = statistics.median(
                values[field] for key, values in computed.items() if key[0] == archive
            )
            recorded = results["summary"][archive]["metrics"][field]["median"]
            archive_median_checks[archive][field] = {
                "recomputed": median,
                "recorded": recorded,
                "match": close(median, recorded),
            }
            if not close(median, recorded):
                errors.append(f"summary mismatch {archive} {field}")

    max_identity_error = max(
        max(
            abs(values["P_A"] + values["P_B"] - 2),
            abs(values["C_A"] + values["C_B"] - 2),
            abs(values["h_A"] + values["h_B"] - 3),
        )
        for values in computed.values()
    )
    if max_identity_error > ATOL:
        errors.append(f"forced identity error {max_identity_error}")
    if results["frozen_protocol_sha256"] != sha256(PROTOCOL):
        errors.append("protocol hash mismatch")
    if results["source_sha256"] != sha256(SOURCE):
        errors.append("source hash mismatch")
    if results["gates"]["ratio"]["status"] != "NOT SUPPORTED":
        errors.append("ratio verdict mismatch")
    if results["gates"]["additive"]["status"] != "NOT SUPPORTED":
        errors.append("additive verdict mismatch")
    for figure in (
        ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION.png",
        ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION.svg",
    ):
        if not figure.exists() or figure.stat().st_size == 0:
            errors.append(f"missing figure {figure.name}")

    validation = {
        "test_id": "Q57",
        "status": "PASS" if not errors else "FAIL",
        "independent_seed_rows": len(computed),
        "max_seed_value_abs_difference": max_abs_difference,
        "max_forced_identity_error": max_identity_error,
        "archive_median_checks": archive_median_checks,
        "phi_reference": PHI,
        "protocol_sha256": sha256(PROTOCOL),
        "source_sha256": sha256(SOURCE),
        "errors": errors[:50],
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
