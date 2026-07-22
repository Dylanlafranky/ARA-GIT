"""Validate PN32 durable recording and canonical propagation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "PN32_RECORDING_VALIDATION.json"


def check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    if OUTPUT.exists():
        prior = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if prior.get("status") != "FAIL":
            raise RuntimeError(f"refusing to overwrite successful {OUTPUT.name}")
    required = {
        "protocol": HERE / "PN32_DOUBLE_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md",
        "protocol_manifest": HERE / "PN32_PROTOCOL_FREEZE_MANIFEST.json",
        "coordinates": HERE / "PN32_DOUBLE_INFORMATION_LOCK_FROZEN_COORDINATES.csv",
        "broken_maps": HERE / "PN32_RELATION_BROKEN_PARENT_INDEXES.json",
        "coordinate_manifest": HERE / "PN32_COORDINATE_FREEZE_MANIFEST.json",
        "scored": HERE / "PN32_DOUBLE_INFORMATION_LOCK_SCORED.csv",
        "results": HERE / "PN32_DOUBLE_INFORMATION_LOCK_RESULTS.json",
        "validation": HERE / "PN32_DOUBLE_INFORMATION_LOCK_VALIDATION.json",
        "report": HERE / "PN32_DOUBLE_INFORMATION_LOCK_REPORT.md",
        "notebook": HERE / "PN32_DOUBLE_INFORMATION_LOCK_REPRODUCIBILITY.ipynb",
        "notebook_receipt": HERE / "PN32_NOTEBOOK_EXECUTION_VALIDATION.json",
    }
    checks = [check(f"required_file:{name}", path.exists(), str(path)) for name, path in required.items()]
    results = json.loads(required["results"].read_text(encoding="utf-8"))
    validation = json.loads(required["validation"].read_text(encoding="utf-8"))
    notebook = json.loads(required["notebook_receipt"].read_text(encoding="utf-8"))
    report = required["report"].read_text(encoding="utf-8")
    checks.extend([
        check("decision_null", results["status"] == "NULL", results["status"]),
        check("arithmetic_validation_pass", validation["all_checks_passed"], f"{validation['checks_passed']}/{validation['checks_total']}"),
        check("notebook_execution_pass", notebook["status"] == "PASS", notebook["status"]),
        check("child_replication_recorded", "0.2244" in report and "did not replicate" in report, "present"),
        check("closure_null_recorded", "0.9684" in report and "no prime/composite separation" in report, "present"),
        check("control_caveat_recorded", "not support-matched" in report and "mechanically raises TV" in report, "present"),
        check("no_prime_algorithm_claim", "does not generate or certify primes" in required["protocol"].read_text(encoding="utf-8"), "present"),
    ])

    propagation = {
        "claims": ROOT / "CLAIMS_STATUS.md",
        "axiomatic": ROOT / "ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md",
        "master_ledger": ROOT / "MASTER_PREDICTION_LEDGER.md",
        "ai_readme": ROOT / "FableConvo" / "README_FOR_AI.md",
        "canon": ROOT / "FableConvo" / "CANON_FOR_AI.md",
        "provenance": ROOT / "FableConvo" / "PROVENANCE_LEDGER.md",
        "prime_glossary": HERE / "PRIME_TEST_RELATIONAL_GLOSSARY.md",
        "prime_capstone": HERE / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md",
    }
    for name, path in propagation.items():
        content = path.read_text(encoding="utf-8")
        checks.append(check(
            f"canonical_propagation:{name}",
            "PN32" in content and "0.9684" in content,
            str(path),
        ))

    payload = {
        "validation_id": "PN32/RECORDING/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
