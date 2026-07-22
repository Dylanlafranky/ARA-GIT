"""Seal the complete PN33 artifact set after independent validation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN33_COMPLETE_MANIFEST.json"

FILES = [
    "PN33_SEEDED_HEXAGON_FILL_FIDELITY_PACKET_v1_DRAFT.md",
    "PN33_SEEDED_HEXAGON_FILL_TEST_STRUCTURE_v1_DRAFT.md",
    "PN33_SEEDED_HEXAGON_FILL_PROTOCOL_v1_FROZEN.md",
    "PN33_PROTOCOL_FREEZE_MANIFEST.json",
    "pn33_seeded_hexagon_fill_coordinates.py",
    "pn33_freeze_coordinates.py",
    "PN33_SEEDED_HEXAGON_FILL_COORDINATES.csv",
    "PN33_SEEDED_HEXAGON_FILL_COORDINATE_SUMMARY.json",
    "PN33_TARGET_PRIME_GATES_UINT32.bin",
    "PN33_COORDINATE_FREEZE_MANIFEST.json",
    "pn33_score_seeded_hexagon_fill.py",
    "PN33_SEEDED_HEXAGON_FILL_SCORED_GAPS.csv.gz",
    "PN33_SEEDED_HEXAGON_FILL_BANDS.csv",
    "PN33_SEEDED_HEXAGON_FILL_ORDER_BROKEN_LOG_MAE.npz",
    "PN33_SEEDED_HEXAGON_FILL_RESULTS.json",
    "pn33_correct_moving_block_bootstrap.py",
    "PN33_SEEDED_HEXAGON_FILL_BOOTSTRAP_RATIOS_CORRECTED.npy",
    "PN33_MOVING_BLOCK_BOOTSTRAP_IMPLEMENTATION_AUDIT.json",
    "PN33_SEEDED_HEXAGON_FILL_RESULTS_VALIDATED.json",
    "validate_pn33_seeded_hexagon_fill.py",
    "PN33_SEEDED_HEXAGON_FILL_VALIDATION.json",
    "pn33_render_seeded_hexagon_fill.py",
    "PN33_SEEDED_HEXAGON_FILL_FIGURE.png",
    "PN33_SEEDED_HEXAGON_FILL_REPORT_2026-07-22.md",
    "build_pn33_reproducibility_notebook.py",
    "PN33_SEEDED_HEXAGON_FILL_REPRODUCIBILITY.ipynb",
    "PN33_NOTEBOOK_EXECUTION_VALIDATION.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    missing = [name for name in FILES if not (HERE / name).exists()]
    if missing:
        raise FileNotFoundError(missing)
    validation = json.loads((HERE / "PN33_SEEDED_HEXAGON_FILL_VALIDATION.json").read_text(encoding="utf-8"))
    result = json.loads((HERE / "PN33_SEEDED_HEXAGON_FILL_RESULTS_VALIDATED.json").read_text(encoding="utf-8"))
    if not validation["all_checks_pass"]:
        raise RuntimeError("independent validation is not green")
    payload = {
        "test_id": "PN33/SEEDED-HEXAGON-FILL/v1",
        "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "status": result["status"],
        "ara_specific_residual_support": result["decision"]["ara_specific_residual_support"],
        "independent_validation_passed": True,
        "file_count": len(FILES),
        "files": {
            name: {"bytes": (HERE / name).stat().st_size, "sha256": sha256(HERE / name)}
            for name in FILES
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": OUTPUT.name,
        "file_count": payload["file_count"],
        "status": payload["status"],
        "independent_validation_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
