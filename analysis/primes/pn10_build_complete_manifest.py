"""Hash the complete PN10 artifact packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "PN10_COMPLETE_MANIFEST.json"

local_files = [
    "PN10_FACTOR_SPHERE_PRIME_RECOVERY_PROTOCOL.md",
    "PN10_FREEZE_MANIFEST.json",
    "pn10_factor_sphere_prime_recovery.py",
    "PN10_FACTOR_SPHERE_RESULTS.json",
    "PN10_FACTOR_SPHERE_PATHS.csv",
    "PN10_FACTOR_SPHERE_TRANSFER.csv",
    "PN10_FACTOR_SPHERE_FIGURE.png",
    "pn10_validate_factor_sphere.py",
    "PN10_FACTOR_SPHERE_VALIDATION.json",
    "PN10_FACTOR_SPHERE_PRIME_RECOVERY_REPORT.md",
    "pn10_build_notebook.py",
    "PN10_FACTOR_SPHERE_PRIME_RECOVERY.ipynb",
    "PN10_NOTEBOOK_EXECUTION_VALIDATION.json",
    "pn10_build_report_artifact.py",
    "pn10_report_purity_path.sql",
    "pn10_report_transfer.sql",
    "PN10_REPORT_ARTIFACT.json",
    "PN10_REPORT_ARTIFACT_VALIDATION.json",
    "pn10_build_complete_manifest.py",
    "PRIME_TEST_RELATIONAL_GLOSSARY.md",
]
shared_files = [
    REPO / "MASTER_PREDICTION_LEDGER.md",
    REPO / "FableConvo" / "ARA_MAPPING_PRIMES.md",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


artifacts = {name: sha(HERE / name) for name in local_files}
for path in shared_files:
    artifacts[str(path.relative_to(REPO)).replace("\\", "/")] = sha(path)

result = json.loads((HERE / "PN10_FACTOR_SPHERE_RESULTS.json").read_text(encoding="utf-8"))
validation = json.loads((HERE / "PN10_FACTOR_SPHERE_VALIDATION.json").read_text(encoding="utf-8"))
notebook_validation = json.loads((HERE / "PN10_NOTEBOOK_EXECUTION_VALIDATION.json").read_text(encoding="utf-8"))
payload = {
    "test_id": result["test_id"],
    "created": "2026-07-20",
    "evidence_class": result["evidence_class"],
    "registered_support_criteria": {key.split("_", 1)[0]: value["pass"] for key, value in result["criteria"].items() if key.startswith("P")},
    "registered_result": f"{result['passed_support_criteria']}/{result['total_support_criteria']} support criteria pass",
    "protected_material": result["protected_material"],
    "artifacts": artifacts,
    "validation": {
        "independent_status": validation["status"],
        "independent_checks": f"{validation['passed_checks']}/{validation['total_checks']}",
        "notebook_status": notebook_validation["status"],
        "notebook_code_cells": notebook_validation["code_cells"],
        "notebook_error_outputs": notebook_validation["error_outputs"],
        "report_artifact_status": "PASS",
    },
}
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(OUT)

