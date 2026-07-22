"""Freeze the PN32 protocol before any coordinates or labels are produced."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN32_DOUBLE_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md"
OUTPUT = HERE / "PN32_PROTOCOL_FREEZE_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    payload = {
        "test_id": "PN32/DOUBLE-INFORMATION-LOCK/v1",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "labels_known": False,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
