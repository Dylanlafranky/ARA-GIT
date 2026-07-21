"""Validate the PN1-PN23 closure record and canonical-document propagation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUTPUT = HERE / "PRIME_THREAD_CLOSURE_VALIDATION_2026-07-21.json"


def factor(number: int) -> list[int]:
    factors: list[int] = []
    remaining = number
    divisor = 2
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors.append(divisor)
            remaining //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remaining > 1:
        factors.append(remaining)
    return factors


def main(*, check_only: bool = False) -> None:
    if OUTPUT.exists() and not check_only:
        raise RuntimeError(
            f"refusing to overwrite {OUTPUT.name}; use --check-only to rerun without changing the frozen receipt"
        )

    paths = {
        "capstone": HERE / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md",
        "claims": ROOT / "CLAIMS_STATUS.md",
        "axiomatic": ROOT / "ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md",
        "foundations": ROOT / "ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md",
        "geometry_foundation": ROOT / "ARA_FOUNDATION_THE_GEOMETRY_BENEATH.md",
        "ledger": ROOT / "MASTER_PREDICTION_LEDGER.md",
        "canon": ROOT / "FableConvo" / "CANON_FOR_AI.md",
        "ai_readme": ROOT / "FableConvo" / "README_FOR_AI.md",
        "index": ROOT / "INDEX.md",
        "prime_glossary": HERE / "PRIME_TEST_RELATIONAL_GLOSSARY.md",
        "pn22_results": HERE / "PN22_ODD_LATTICE_ARA_CANDIDATE_RESULTS.json",
        "pn23_results": HERE / "PN23_ANTI_PAIR_FRACTAL_LIFT_RESULTS.json",
        "pn23_validation": HERE / "PN23_ANTI_PAIR_FRACTAL_LIFT_VALIDATION.json",
    }
    texts = {
        name: path.read_text(encoding="utf-8")
        for name, path in paths.items()
        if path.suffix.lower() == ".md"
    }
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    for name, path in paths.items():
        check(f"required_file:{name}", path.exists(), str(path.relative_to(ROOT)))

    capstone = texts["capstone"]
    for number in range(1, 24):
        check(f"capstone_mentions_PN{number}", f"PN{number}" in capstone, "lineage PN1-PN23")

    ledger = texts["ledger"]
    for number in range(242, 250):
        marker = f"### T{number} -"
        check(f"ledger_unique_T{number}", ledger.count(marker) == 1, f"count={ledger.count(marker)}")

    propagated = {
        "claims": "Prime-thread capstone status (21 July 2026" in texts["claims"],
        "axiomatic": "# Part IX — Prime-factor and wheel-sieve subset" in texts["axiomatic"],
        "foundations": "#### 5.4.4 Prime wheel anti-pairs" in texts["foundations"],
        "geometry_foundation": "Arithmetic audit, 21 July 2026" in texts["geometry_foundation"],
        "canon": "Prime-thread closure fence (21 July 2026)" in texts["canon"],
        "ai_readme": "21 Jul prime-thread closure amendment" in texts["ai_readme"],
        "index": "Looking for the completed prime-number exploration?" in texts["index"],
        "prime_glossary": "## PN20–PN23 compression and closure terms" in texts["prime_glossary"],
    }
    for name, passed in propagated.items():
        check(f"canonical_propagation:{name}", passed, "closure fence present")

    for theorem in (25, 26, 27):
        check(
            f"axiomatic_theorem_{theorem}",
            texts["axiomatic"].count(f"### Theorem {theorem} —") == 1,
            "exactly one numbered theorem",
        )

    pn22 = json.loads(paths["pn22_results"].read_text(encoding="utf-8"))
    pn23 = json.loads(paths["pn23_results"].read_text(encoding="utf-8"))
    pn23_validation = json.loads(paths["pn23_validation"].read_text(encoding="utf-8"))
    check("pn22_exact_wheel_crosswalk", pn22["decision"]["wheel_crosswalk"] is True, "matched lane equality")
    check("pn22_no_blind_target", pn22["decision"]["blind_target_authorized"] is False, "fresh target not authorized")
    check("pn23_all_rungs_pass", pn23["decision"]["all_rungs_pass"] is True, "development plus held-out p17")
    check("pn23_final_pair_count", pn23["decision"]["final_stored_pair_representatives"] == 46080, "46,080 pairs")
    check("pn23_final_residue_count", pn23["decision"]["final_reconstructed_residues"] == 92160, "92,160 residues")
    check("pn23_independent_40_of_40", pn23_validation["checks_passed"] == pn23_validation["checks_total"] == 40, "40/40")

    check("spontaneous_written_formula", (97008 // 2 + 97008 + 2 * 97008) // 2 + 1 == 169765, "parentheses retained")
    check("spontaneous_written_formula_factors", factor(169765) == [5, 19, 1787], str(factor(169765)))
    check("spontaneous_no_outer_division_factors", factor(339529) == [163, 2083], str(factor(339529)))
    check("spontaneous_2n_plus_1_prime", factor(194017) == [194017], "trial division factor list")

    forbidden_promotions = [
        "ARA proves a new prime theorem",
        "ARA predicts every prime in three operations",
        "PN23 proves universal physical fractality",
    ]
    for phrase in forbidden_promotions:
        check(f"forbidden_promotion_absent:{phrase}", phrase not in capstone, "capstone fence")

    passed = sum(item["pass"] for item in checks)
    payload = {
        "validation_id": "PRIME-THREAD-CLOSURE-DOCS/2026-07-21/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    if not check_only:
        OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "checks_passed": passed,
        "checks_total": len(checks),
        "failures": [item for item in checks if not item["pass"]],
    }, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="rerun all checks without overwriting the frozen JSON receipt",
    )
    args = parser.parse_args()
    main(check_only=args.check_only)
