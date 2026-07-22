"""Hash PN33 coordinates before any prime-gap scoring."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL_FREEZE = HERE / "PN33_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN33_SEEDED_HEXAGON_FILL_COORDINATES.csv"
SUMMARY = HERE / "PN33_SEEDED_HEXAGON_FILL_COORDINATE_SUMMARY.json"
PRIME_BINARY = HERE / "PN33_TARGET_PRIME_GATES_UINT32.bin"
OUTPUT = HERE / "PN33_COORDINATE_FREEZE_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    protocol = json.loads(PROTOCOL_FREEZE.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if protocol["target_coordinates_calculated"]:
        raise RuntimeError("protocol manifest did not preserve the pre-coordinate firewall")
    if summary["gap_summaries_calculated"] or summary["target_outcomes_scored"]:
        raise RuntimeError("coordinate summary says outcomes were already calculated")
    payload = {
        "test_id": "PN33/SEEDED-HEXAGON-FILL/v1",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "coordinate_file": COORDINATES.name,
        "coordinate_file_sha256": sha256(COORDINATES),
        "coordinate_summary_file": SUMMARY.name,
        "coordinate_summary_sha256": sha256(SUMMARY),
        "prime_binary_file": PRIME_BINARY.name,
        "prime_binary_sha256": sha256(PRIME_BINARY),
        "prime_binary_count": summary["prime_binary_count"],
        "target_coordinates_calculated": True,
        "target_gap_summaries_calculated": False,
        "status": "COORDINATES FROZEN BEFORE SCORING",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

