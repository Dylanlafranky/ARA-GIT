"""Validate PN30's durable report, notebook receipt, and canonical propagation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "PN30_RECORDING_VALIDATION.json"


def check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    if OUTPUT.exists():
        prior = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if prior.get("status") != "FAIL":
            raise RuntimeError(f"refusing to overwrite successful {OUTPUT.name}")

    required = {
        "protocol": HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_PROTOCOL_v1_FROZEN.md",
        "protocol_manifest": HERE / "PN30_PROTOCOL_FREEZE_MANIFEST.json",
        "coordinates": HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_FROZEN_COORDINATES.csv",
        "coordinate_manifest": HERE / "PN30_COORDINATE_FREEZE_MANIFEST.json",
        "results": HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_RESULTS.json",
        "validation": HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_VALIDATION.json",
        "posthoc": HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_POSTHOC.json",
        "report": HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_REPORT.md",
        "notebook": HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_REPRODUCIBILITY.ipynb",
        "notebook_receipt": HERE / "PN30_NOTEBOOK_EXECUTION_VALIDATION.json",
        "pn29_amendment": HERE / "PN29_DYNAMIC_FLIP_AMENDMENT_2026-07-22.md",
    }
    checks = [check(f"required_file:{name}", path.exists(), str(path)) for name, path in required.items()]

    results = json.loads(required["results"].read_text(encoding="utf-8"))
    validation = json.loads(required["validation"].read_text(encoding="utf-8"))
    notebook_receipt = json.loads(required["notebook_receipt"].read_text(encoding="utf-8"))
    report = required["report"].read_text(encoding="utf-8")
    amendment = required["pn29_amendment"].read_text(encoding="utf-8")

    dynamic_unresolved = results["dynamic"]["prime_vs_unresolved_composite"]
    checks.extend([
        check("arithmetic_validation_pass", validation["all_checks_passed"], f"{validation['checks_passed']}/{validation['checks_total']}"),
        check("notebook_execution_pass", notebook_receipt["status"] == "PASS", notebook_receipt["status"]),
        check("unresolved_auc_recorded", "0.5663" in report, str(dynamic_unresolved["auc_prime_more_ridge_close"])),
        check("unresolved_p_recorded", "0.06199" in report, str(dynamic_unresolved["permutation"]["one_sided_p"])),
        check("static_control_recorded", "0.5301" in report, str(results["static_same_interval_control"]["prime_vs_unresolved_composite"]["auc_prime_more_ridge_close"])),
        check("posthoc_fenced", "post-hoc" in report.lower() and "requiring frozen replication" in report.lower(), "descriptive mechanism fenced"),
        check("no_generator_claim", "does not generate or certify primes" in report, "negative boundary present"),
        check("pn29_amendment_links_pn30", "PN30_DYNAMIC_RELATIONAL_FLIP_REPORT.md" in amendment, "link present"),
    ])

    propagation = {
        "claims": ROOT / "CLAIMS_STATUS.md",
        "axiomatic": ROOT / "ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md",
        "ai_readme": ROOT / "FableConvo" / "README_FOR_AI.md",
        "canon": ROOT / "FableConvo" / "CANON_FOR_AI.md",
        "prime_glossary": HERE / "PRIME_TEST_RELATIONAL_GLOSSARY.md",
        "prime_capstone": HERE / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md",
    }
    for name, path in propagation.items():
        content = path.read_text(encoding="utf-8")
        checks.append(check(f"canonical_propagation:{name}", "PN30" in content and "0.5663" in content, str(path)))

    payload = {
        "validation_id": "PN30/RECORDING/v1",
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
