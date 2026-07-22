"""Validate PN26's durable artifact and documentation chain."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "PN26_RECORDING_VALIDATION.json"
REQUIRED = (
    "PN26_DOMINANT_PARENT_RIDGE_LOCATOR_PROTOCOL_v1_FROZEN.md",
    "PN26_TARGET_FREEZE_MANIFEST.json",
    "pn26_dominant_parent_ridge_locator.py",
    "PN26_DOMINANT_PARENT_RIDGE_PREDICTIONS.csv",
    "PN26_DOMINANT_PARENT_RIDGE_PRIMARY.json",
    "validate_pn26_dominant_parent_ridge_locator.py",
    "PN26_DOMINANT_PARENT_RIDGE_VALIDATION.json",
    "PN26_VALIDATOR_AMENDMENT_v1_1.md",
    "PN26_VALIDATOR_AMENDMENT_FREEZE_v1_1.json",
    "validate_pn26_dominant_parent_ridge_locator_v1_1.py",
    "PN26_DOMINANT_PARENT_RIDGE_VALIDATED_ROWS_V1_1.csv",
    "PN26_DOMINANT_PARENT_RIDGE_VALIDATION_V1_1.json",
    "PN26_DOMINANT_PARENT_RIDGE_LOCATOR_REPORT.md",
    "build_pn26_notebook.py",
    "PN26_DOMINANT_PARENT_RIDGE_LOCATOR_REPRODUCIBILITY.ipynb",
    "PN26_NOTEBOOK_EXECUTION_VALIDATION.json",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    missing = [name for name in REQUIRED if not (HERE / name).exists()]
    add("all PN26 artifacts exist", not missing, str(missing))

    freeze = json.loads((HERE / "PN26_TARGET_FREEZE_MANIFEST.json").read_text(encoding="utf-8"))
    primary = json.loads((HERE / "PN26_DOMINANT_PARENT_RIDGE_PRIMARY.json").read_text(encoding="utf-8"))
    failed_v1 = json.loads((HERE / "PN26_DOMINANT_PARENT_RIDGE_VALIDATION.json").read_text(encoding="utf-8"))
    corrected = json.loads((HERE / "PN26_DOMINANT_PARENT_RIDGE_VALIDATION_V1_1.json").read_text(encoding="utf-8"))
    notebook = json.loads((HERE / "PN26_NOTEBOOK_EXECUTION_VALIDATION.json").read_text(encoding="utf-8"))
    report = (HERE / "PN26_DOMINANT_PARENT_RIDGE_LOCATOR_REPORT.md").read_text(encoding="utf-8")
    pooled = next(row for row in corrected["summaries"] if row["cohort"] == "pooled")

    add("sealed prediction hash preserved", sha(HERE / primary["prediction_file"]) == primary["prediction_sha256"])
    add("freeze protocol hash preserved", sha(HERE / "PN26_DOMINANT_PARENT_RIDGE_LOCATOR_PROTOCOL_v1_FROZEN.md") == freeze["hashes"]["protocol_sha256"])
    add("original validator failure preserved", failed_v1["status"] == "IMPLEMENTATION FAILURE")
    add("corrected validation classified partial", corrected["status"] == "PARTIAL DOMINANT-PARENT SUPPORT")
    add("corrected validation passed 16/16", corrected["checks_passed"] == corrected["checks_total"] == 16)
    add("top1 rate exact", abs(pooled["phase_a_top1_rate"] - 5639 / 6000) < 1e-15)
    add("top2 rate exact", abs(pooled["phase_a_top2_rate"] - 5979 / 6000) < 1e-15)
    add("top3 rate exact", abs(pooled["phase_a_top3_rate"] - 5998 / 6000) < 1e-15)
    add("rank tail preserved", pooled["rank_counts"] == {"1": 5639, "2": 340, "3": 19, "4": 1, "5": 1})
    add("frozen control failure retained", corrected["registered_predictions"]["P4_top3_beats_p29_by_50pp"] is False)
    add("3.5 frame kept nonpredictive", corrected["cross_rung_frame"]["variance"] == 0.0 and "does not supply" in report)
    add("notebook executed cleanly", notebook["status"] == "PASS" and notebook["code_cells_executed"] == notebook["code_cells_total"])
    add("report states hidden child counts", "780, 17,045 and 48,817" in report)
    add("protected anchor remains unused", primary["protected_87_bit_anchor_used"] is False and corrected["protected_87_bit_anchor_used"] is False)

    docs = {
        ROOT / "CLAIMS_STATUS.md": "PN1–PN26",
        ROOT / "ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md": "Theorem 30",
        ROOT / "ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md": "#### 5.4.7",
        HERE / "PRIME_TEST_RELATIONAL_GLOSSARY.md": "Dominant parent quiet state",
        HERE / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md": "| PN26 |",
    }
    for path, needle in docs.items():
        add(f"{path.name} records PN26", needle in path.read_text(encoding="utf-8"))

    passed = sum(check["pass"] for check in checks)
    payload = {
        "validation_id": "PN26/RECORDING-VALIDATION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "sha256": {name: sha(HERE / name) for name in REQUIRED if (HERE / name).exists()},
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
