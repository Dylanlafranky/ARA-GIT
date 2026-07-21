"""Build the final PN19 artifact integrity manifest."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN19_COMPLETE_MANIFEST.json"
FILES = (
    "PN19_TWO_PARENT_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md",
    "PN19_TARGET_FREEZE_MANIFEST.json",
    "pn19_two_parent_information_lock.py",
    "PN19_TWO_PARENT_INFORMATION_LOCK_PREDICTION.json",
    "PN19_TARGET_PHASE_A_MASK.bin",
    "PN19_TARGET_PHASE_B_MASK.bin",
    "PN19_TARGET_INFORMATION_LOCK_MASK.bin",
    "validate_pn19_two_parent_information_lock.py",
    "PN19_TWO_PARENT_INFORMATION_LOCK_VALIDATION.json",
    "pn19_post_target_second_go_robustness.py",
    "PN19_POST_TARGET_SECOND_GO_ROBUSTNESS.json",
    "PN19_TWO_PARENT_INFORMATION_LOCK_REPORT.md",
    "pn19_build_and_execute_notebook.py",
    "PN19_TWO_PARENT_INFORMATION_LOCK.ipynb",
    "PN19_NOTEBOOK_EXECUTION_VALIDATION.json",
    "PN19_TWO_PARENT_INFORMATION_LOCK_FIGURE.png",
    "PRIME_TEST_RELATIONAL_GLOSSARY.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    prediction = json.loads((HERE / "PN19_TWO_PARENT_INFORMATION_LOCK_PREDICTION.json").read_text())
    validation = json.loads((HERE / "PN19_TWO_PARENT_INFORMATION_LOCK_VALIDATION.json").read_text())
    notebook_validation = json.loads((HERE / "PN19_NOTEBOOK_EXECUTION_VALIDATION.json").read_text())
    robustness = json.loads((HERE / "PN19_POST_TARGET_SECOND_GO_ROBUSTNESS.json").read_text())
    missing = [name for name in FILES if not (HERE / name).exists()]
    if missing:
        raise FileNotFoundError(missing)
    artifacts = [
        {"file": name, "bytes": (HERE / name).stat().st_size, "sha256": sha256(HERE / name)}
        for name in FILES
    ]
    payload = {
        "test_id": "PN19/TWO-PARENT-INFORMATION-LOCK/COMPLETE-MANIFEST/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "result": {
            "anchor": prediction["target"]["anchor"],
            "sealed_candidate": prediction["target"]["predicted_integer"],
            "correction": prediction["target"]["information_lock_offset"],
            "candidate_is_first_prime": validation["candidate_is_first_prime_above_anchor"],
            "independent_checks": f"{validation['passed_count']}/{validation['check_count']}",
            "fresh_target_second_go_success": validation["target_second_go_success"],
            "frozen_development_second_go_success_rate": validation["development_second_go_success_rate"],
            "post_target_phase_a_success_rate": robustness["overall"]["phase_a_success_rate"],
            "post_target_anchor_count": robustness["overall"]["anchor_count"],
        },
        "classification": (
            "Exact two-parent ARA crosswalk of an established segmented sieve; strong Phase A approximate locator, "
            "no demonstrated information or asymptotic speed compression."
        ),
        "all_independent_checks_passed": validation["all_passed"],
        "notebook_validation_passed": notebook_validation["validation_passed"],
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact_count": len(artifacts),
        "all_independent_checks_passed": payload["all_independent_checks_passed"],
        "notebook_validation_passed": payload["notebook_validation_passed"],
        "manifest_sha256": sha256(OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()
