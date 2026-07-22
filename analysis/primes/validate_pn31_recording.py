"""Validate PN31 durable recording and canonical propagation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "PN31_RECORDING_VALIDATION.json"


def check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    if OUTPUT.exists():
        prior = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if prior.get("status") != "FAIL":
            raise RuntimeError(f"refusing to overwrite successful {OUTPUT.name}")

    required = {
        "protocol": HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_PROTOCOL_v1_FROZEN.md",
        "protocol_manifest": HERE / "PN31_PROTOCOL_FREEZE_MANIFEST.json",
        "coordinates": HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_FROZEN_COORDINATES.csv",
        "coordinate_manifest": HERE / "PN31_COORDINATE_FREEZE_MANIFEST.json",
        "results": HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_RESULTS.json",
        "validation": HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_VALIDATION.json",
        "posthoc": HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_POSTHOC.json",
        "report": HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_REPORT.md",
        "notebook": HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_REPRODUCIBILITY.ipynb",
        "notebook_receipt": HERE / "PN31_NOTEBOOK_EXECUTION_VALIDATION.json",
    }
    checks = [check(f"required_file:{name}", path.exists(), str(path)) for name, path in required.items()]

    results = json.loads(required["results"].read_text(encoding="utf-8"))
    validation = json.loads(required["validation"].read_text(encoding="utf-8"))
    notebook = json.loads(required["notebook_receipt"].read_text(encoding="utf-8"))
    report = required["report"].read_text(encoding="utf-8")
    checks.extend([
        check("arithmetic_validation_pass", validation["all_checks_passed"], f"{validation['checks_passed']}/{validation['checks_total']}"),
        check("notebook_execution_pass", notebook["status"] == "PASS", notebook["status"]),
        check("wave_1_absent", results["population"]["wave_1_included"] is False and "Wave 1 was removed completely" in report, "absent"),
        check("fixed_pairs_absent", results["population"]["fixed_pairs_used"] is False and "no fixed pairs" in report.lower(), "absent"),
        check("phase_a_null_recorded", "0.5279" in report and "0.2941" in report, "headline present"),
        check("full_order_result_recorded", "0.6728" in report and "0.00390" in report, "headline present"),
        check("posthoc_fenced", "post-hoc" in report.lower() and "fresh replication" in report.lower(), "post-hoc fenced"),
        check("no_prime_algorithm_claim", "not a prime generator" in report.lower() and "certification" in report.lower(), "negative boundary present"),
    ])

    propagation = {
        "claims": ROOT / "CLAIMS_STATUS.md",
        "axiomatic": ROOT / "ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md",
        "ai_readme": ROOT / "FableConvo" / "README_FOR_AI.md",
        "canon": ROOT / "FableConvo" / "CANON_FOR_AI.md",
        "prime_glossary": HERE / "PRIME_TEST_RELATIONAL_GLOSSARY.md",
        "prime_capstone": HERE / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md",
        "pn30_followup": HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_REPORT.md",
    }
    for name, path in propagation.items():
        content = path.read_text(encoding="utf-8")
        checks.append(check(f"canonical_propagation:{name}", "PN31" in content and "0.00390" in content, str(path)))

    payload = {
        "validation_id": "PN31/RECORDING/v1",
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
