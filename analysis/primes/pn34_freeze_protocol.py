"""Freeze PN34 protocol and implementations before any fresh targets exist."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN34_PROTOCOL_FREEZE_MANIFEST.json"
FILES = (
    "PN34_FILL_RANK_BUDGET_FIDELITY_PACKET_v1_DRAFT.md",
    "PN34_FILL_RANK_BUDGET_PROTOCOL_v1_FROZEN.md",
    "pn34_fill_rank_budget_primary.py",
    "validate_pn34_fill_rank_budget.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    payload = {
        "test_id": "PN34/FILL-RANK-BUDGET/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FROZEN BEFORE FRESH TARGET CONSTRUCTION",
        "files": {name: sha256(HERE / name) for name in FILES},
        "parameters": {
            "target_ranges": [
                ["low", 89_000_000, 89_500_000, 34001],
                ["middle", 89_000_000_000, 89_000_500_000, 34002],
                ["high", 8_900_000_000_000, 8_900_000_500_000, 34003],
            ],
            "rows_per_cohort": 2000,
            "maximum_offset": 4096,
            "ranked_candidates": 3,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
