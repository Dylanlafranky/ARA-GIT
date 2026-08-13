#!/usr/bin/env python3
"""Independent artifact and data-quality validation for T370B."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_vendor"))

import numpy as np
import pandas as pd
from pyhdf.SD import SD, SDC


RAW = HERE / "data" / "raw_full"
RESULTS = HERE / "T370B_MUON_PHASE_LINEAGE_RESULTS.json"
RUN_CSV = HERE / "T370B_MUON_PHASE_LINEAGE_RUNS.csv"
OUTPUT = HERE / "T370B_MUON_PHASE_LINEAGE_VALIDATION.json"
GAMMA = 0.013553896


def field(title: str) -> float | None:
    match = re.search(r"\bF=([0-9.]+)", title)
    return float(match.group(1)) if match else None


def text_field(handle: SD, name: str) -> str:
    values = np.asarray(handle.select(name)[:]).reshape(-1).tolist()
    return b"".join(values).decode("latin1").rstrip("\x00 ")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    frame = pd.read_csv(RUN_CSV)
    archive_selection = []
    raw_checks = []
    selected = set(frame.run)
    for path in sorted(RAW.rglob("*.nxs")):
        handle = SD(str(path), SDC.READ)
        title = text_field(handle, "title")
        count = int(np.asarray(handle.select("counts")[:], dtype=np.int64).sum())
        value = field(title)
        if title.startswith("LCB1-88 T=135.0 F=") and count > 0 and value is not None and 0 < value <= 520:
            archive_selection.append(path.stem)
        if path.stem in selected:
            row = next(item for item in result["runs"] if item["run"] == path.stem)
            raw_checks.append({
                "run": path.stem,
                "title_match": row["title"] == title,
                "count_match": row["raw_counts"] == count,
                "hash_match": row["sha256"] == sha256(path),
            })

    registered = sorted(frame.run.tolist())
    expected = frame.field_gauss.to_numpy() * GAMMA
    recomputed_relative = np.abs(frame.recovered_frequency_mhz.to_numpy() - expected) / expected
    duplicate = frame.loc[frame.field_gauss == 200, "recovered_frequency_mhz"].to_numpy()
    checks = {
        "complete_archive_has_100_nexus_runs": len(list(RAW.rglob("*.nxs"))) == 100,
        "selection_exactly_matches_frozen_rule": sorted(archive_selection) == registered,
        "all_raw_titles_counts_and_hashes_match": all(all(x[k] for k in ("title_match", "count_match", "hash_match")) for x in raw_checks) and len(raw_checks) == len(frame),
        "frequency_errors_recomputed": bool(np.allclose(recomputed_relative, frame.frequency_relative_error.to_numpy(), atol=1e-12)),
        "duplicate_200G_recomputed": bool(np.isclose(abs(duplicate[0] - duplicate[1]), result["duplicate_200G_frequency_difference_mhz"], atol=1e-12)),
        "development_and_holdout_counts_present": all(r["development_counts"] > r["holdout_counts"] > 0 for r in result["runs"]),
        "claim_boundary_present": "neutrino" in result["claim_boundary"].lower(),
    }
    validation = {
        "artifact": str(RESULTS),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "decision": "SHARE_WITH_CAVEATS" if all(checks.values()) else "NOT_READY",
        "caveats": [
            "The frozen all-run gate did not pass because the 520 G cadence was unresolved at 64 ns analysis sampling.",
            "Runs are repeated acquisitions from one sample/temperature family, not independent experiments.",
            "The neutrino branch is inferred from conservation and is not measured in the EMU archive.",
            "The result is a recovery of known muon-spin physics in ARA language, not a new ARA-only prediction.",
        ],
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
