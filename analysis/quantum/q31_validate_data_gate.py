"""Independent checks for the Q31 data-gate result."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "q31_data"


def file_md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    failures: list[str] = []

    expected = {
        DATA / "source" / "SourceData_Fig2.xlsx": "746c65ddccd37e82d0710712ecfec4fb",
        DATA / "source" / "SourceData_Fig3.xlsx": "c24a6ed6475b64d61e08318eeae0c629",
        DATA / "source" / "SourceData_Fig4.xlsx": "7d4dda38985171a5196981ee5a7ed397",
        DATA
        / "candidate5"
        / "quantinuum-2d-trajectory-data.zip": "185a52581636ce37dfeb950bf64214de",
        DATA
        / "candidate6"
        / "Source Data _ full_version.zip": "ced1ed4af893ad064045900903e19a17",
    }
    for path, wanted in expected.items():
        observed = file_md5(path)
        if observed != wanted:
            failures.append(f"MD5 mismatch: {path.name}: {observed} != {wanted}")

    h1_archive = DATA / "candidate5" / "quantinuum-2d-trajectory-data.zip"
    with zipfile.ZipFile(h1_archive) as bundle:
        h1_names = [
            name
            for name in bundle.namelist()
            if "/data_H1/" in name
            and name.endswith(".h5")
            and not name.startswith("__MACOSX/")
        ]
    if len(h1_names) != 5:
        failures.append(f"Expected 5 H1 hardware files, observed {len(h1_names)}")
    h1_steps = sorted(
        int(name.split("_steps", 1)[1].split("_", 1)[0]) for name in h1_names
    )
    if h1_steps != [10, 14, 14, 16, 18]:
        failures.append(f"Unexpected H1 step counts: {h1_steps}")

    fluxon_archive = DATA / "candidate6" / "Source Data _ full_version.zip"
    condition_counts: dict[str, tuple[int, int]] = {}
    with zipfile.ZipFile(fluxon_archive) as bundle:
        names = bundle.namelist()
        for condition in ("6,6507", "6,6641", "6,7057"):
            arrays = [
                np.frombuffer(bundle.read(name), dtype="<f4")
                for name in names
                if "/Fig8c/" in name
                and f"fge_{condition}_" in name
                and "_taus_" in name
            ]
            values = np.concatenate(arrays)
            values = values[np.isfinite(values) & (values > 0)]
            if condition == "6,6641":
                values = values[values != 30]
            condition_counts[condition] = (
                int(len(values)),
                int(np.sum(values >= 750)),
            )

    if condition_counts != {
        "6,6507": (64, 51),
        "6,6641": (51, 45),
        "6,7057": (85, 48),
    }:
        failures.append(f"Unexpected fluxon counts: {condition_counts}")

    result = json.loads(
        (ROOT / "Q31_DATA_GATE_AUDIT_RESULTS.json").read_text(encoding="utf-8")
    )
    if result["eligible_candidate_count"] != 0:
        failures.append("Audit claims an eligible source")
    if result["confirmatory_outcome_metrics_calculated"] is not False:
        failures.append("Audit incorrectly claims outcome metrics were calculated")
    if result["verdict"] != "INCONCLUSIVE — DATA/ELIGIBILITY GATE":
        failures.append(f"Unexpected verdict: {result['verdict']}")

    candidate6 = next(c for c in result["candidates"] if c["candidate"] == 6)
    for key, wanted in {
        "events_after_author_filters": 200,
        "events_with_at_least_25_pre_samples": 144,
        "evaluation_long_enough_upper_bound": 72,
    }.items():
        if candidate6[key] != wanted:
            failures.append(f"Candidate 6 {key}: {candidate6[key]} != {wanted}")

    forbidden_outcome_keys = {
        "C",
        "T",
        "x",
        "short_memory",
        "long_return",
        "te_ara_closure",
        "flip_supported",
    }
    serialized = json.dumps(result)
    for key in forbidden_outcome_keys:
        if f'"{key}"' in serialized:
            failures.append(f"Outcome key unexpectedly present: {key}")

    report = (
        ROOT / "Q31_LATTICE_TO_TRAVERSAL_DATA_GATE_REPORT_2026-07-26.md"
    ).read_text(encoding="utf-8")
    ledger = (ROOT.parents[1] / "MASTER_PREDICTION_LEDGER.md").read_text(
        encoding="utf-8"
    )
    if "**INCONCLUSIVE — DATA/ELIGIBILITY GATE**" not in report:
        failures.append("Report verdict missing")
    if "**STATUS: INCONCLUSIVE — DATA/ELIGIBILITY GATE**" not in ledger:
        failures.append("Ledger status was not updated")

    if failures:
        print("Q31 DATA-GATE VALIDATION: FAIL")
        for failure in failures:
            print("-", failure)
        raise SystemExit(1)

    print("Q31 DATA-GATE VALIDATION: PASS")
    print("Checks passed: 5 hashes, 5 H1 files, 3 fluxon strata, result boundary, ledger")
    print("Condition counts:", condition_counts)
    print("Confirmatory outcome metrics calculated: False")


if __name__ == "__main__":
    main()
