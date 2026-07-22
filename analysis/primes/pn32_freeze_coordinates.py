"""Freeze PN32 coordinates and relation-broken maps before label reveal."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
COORDINATES = HERE / "PN32_DOUBLE_INFORMATION_LOCK_FROZEN_COORDINATES.csv"
BROKEN_MAPS = HERE / "PN32_RELATION_BROKEN_PARENT_INDEXES.json"
SUMMARY = HERE / "PN32_DOUBLE_INFORMATION_LOCK_COORDINATE_SUMMARY.json"
OUTPUT = HERE / "PN32_COORDINATE_FREEZE_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    coordinate_hash = sha256(COORDINATES)
    broken_hash = sha256(BROKEN_MAPS)
    if coordinate_hash != summary["coordinate_file_sha256"]:
        raise RuntimeError("coordinate summary hash mismatch")
    if broken_hash != summary["broken_maps_file_sha256"]:
        raise RuntimeError("broken-map summary hash mismatch")
    payload = {
        "test_id": "PN32/DOUBLE-INFORMATION-LOCK/v1",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "coordinate_file": COORDINATES.name,
        "coordinate_file_sha256": coordinate_hash,
        "broken_maps_file": BROKEN_MAPS.name,
        "broken_maps_file_sha256": broken_hash,
        "labels_known": False,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
