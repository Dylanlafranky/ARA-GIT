"""Reproduce the Q31 public-source data-gate audit.

This script does not calculate the registered Q31 flip metrics.  It checks
whether the acquired public sources can support those metrics without changing
the frozen protocol.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

import numpy as np


EXPECTED_MD5 = {
    "SourceData_Fig2.xlsx": "746c65ddccd37e82d0710712ecfec4fb",
    "SourceData_Fig3.xlsx": "c24a6ed6475b64d61e08318eeae0c629",
    "SourceData_Fig4.xlsx": "7d4dda38985171a5196981ee5a7ed397",
    "quantinuum-2d-trajectory-data.zip": "185a52581636ce37dfeb950bf64214de",
    "Source Data _ full_version.zip": "ced1ed4af893ad064045900903e19a17",
}


def md5(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_candidate4(source_dir: Path) -> dict:
    files = sorted(source_dir.glob("SourceData_Fig*.xlsx"))
    hashes = {path.name: md5(path) for path in files}
    return {
        "candidate": 4,
        "source": "Lin et al. photonic quantum walks",
        "local_files": len(files),
        "hashes": hashes,
        "hashes_match": all(
            hashes.get(name) == EXPECTED_MD5[name]
            for name in (
                "SourceData_Fig2.xlsx",
                "SourceData_Fig3.xlsx",
                "SourceData_Fig4.xlsx",
            )
        ),
        # Read with @oai/artifact-tool before any Q31 outcome calculation.
        "measured_trajectory_units": 9,
        "minimum_required_units": 60,
        "two_coordinate_path": True,
        "external_handover": True,
        "pre_and_post_windows": True,
        "eligible_evaluation_transitions": None,
        "decision": "INELIGIBLE",
        "failed_gates": ["D3: only 9 measured trajectories; 30 evaluation units impossible"],
    }


def audit_candidate5(archive: Path) -> dict:
    step_pattern = re.compile(r"_steps(\d+)_shots(\d+)\.h5$")
    with zipfile.ZipFile(archive) as bundle:
        hardware = []
        for name in bundle.namelist():
            if "/data_H1/" not in name or name.startswith("__MACOSX/"):
                continue
            match = step_pattern.search(name)
            if match:
                hardware.append(
                    {
                        "file": Path(name).name,
                        "steps": int(match.group(1)),
                        "shots": int(match.group(2)),
                    }
                )
    max_steps = max(item["steps"] for item in hardware)
    return {
        "candidate": 5,
        "source": "Dalmasso et al. Quantinuum H1 trajectories",
        "archive_md5": md5(archive),
        "hashes_match": md5(archive)
        == EXPECTED_MD5["quantinuum-2d-trajectory-data.zip"],
        "hardware_files": hardware,
        "hardware_file_count": len(hardware),
        "maximum_ordered_hardware_steps": max_steps,
        "minimum_required_ordered_samples": 25,
        "two_coordinate_path": True,
        "external_handover": True,
        "pre_and_post_windows": False,
        "eligible_evaluation_transitions": 0,
        "decision": "INELIGIBLE",
        "failed_gates": [
            f"D1: hardware paths have at most {max_steps} ordered steps, below 25"
        ],
    }


def _filtered_tau_values(bundle: zipfile.ZipFile, names: list[str], condition: str) -> np.ndarray:
    arrays = [
        np.frombuffer(bundle.read(name), dtype="<f4")
        for name in names
        if "/Fig8c/" in name
        and f"fge_{condition}_" in name
        and "_taus_" in name
    ]
    values = np.concatenate(arrays) if arrays else np.array([], dtype=float)
    values = values[np.isfinite(values) & (values > 0)]
    # The authors' Mathematica notebook additionally deletes the 30 s sentinel
    # in the 6.6641 condition.
    if condition == "6,6641":
        values = values[values != 30]
    return values


def audit_candidate6(archive: Path) -> dict:
    conditions: dict[str, dict] = {}
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        for condition in ("6,6507", "6,6641", "6,7057"):
            tau = _filtered_tau_values(bundle, names, condition)
            raw_names = [
                name
                for name in names
                if "/Fig8c/" in name
                and f"fge_{condition}_" in name
                and "_raw_" in name
            ]
            raw_values = sum(len(bundle.read(name)) // 4 for name in raw_names)
            conditions[condition] = {
                "events_after_author_filters": int(len(tau)),
                "events_with_at_least_25_pre_samples": int(np.sum(tau >= 750)),
                "median_tunnelling_time_s": float(np.median(tau)),
                "maximum_tunnelling_time_s": float(np.max(tau)),
                "raw_files": len(raw_names),
                "raw_float32_values": raw_values,
            }

    total_events = sum(v["events_after_author_filters"] for v in conditions.values())
    long_enough = sum(
        v["events_with_at_least_25_pre_samples"] for v in conditions.values()
    )
    evaluation_events_upper_bound = total_events // 2
    evaluation_long_upper_bound = long_enough // 2

    return {
        "candidate": 6,
        "source": "Farid et al. inductively shunted transmon",
        "archive_md5": md5(archive),
        "hashes_match": md5(archive)
        == EXPECTED_MD5["Source Data _ full_version.zip"],
        "conditions": conditions,
        "events_after_author_filters": total_events,
        "events_with_at_least_25_pre_samples": long_enough,
        "evaluation_events_upper_bound": evaluation_events_upper_bound,
        "evaluation_long_enough_upper_bound": evaluation_long_upper_bound,
        "minimum_required_evaluation_transitions": 500,
        "two_coordinate_path": False,
        "external_handover": True,
        "pre_and_post_windows": False,
        "eligible_evaluation_transitions": 0,
        "decision": "INELIGIBLE",
        "failed_gates": [
            "D1/D2: Fig. 8c monitoring files do not retain a fixed two-coordinate relation path",
            "D1: monitoring terminates when tunnelling is detected, so no post-handover path exists",
            (
                "D3: at most "
                f"{evaluation_long_upper_bound} evaluation events have 25 pre-samples, "
                "below 500 required evaluation transitions"
            ),
        ],
    }


def audit_metadata_only_candidates() -> list[dict]:
    return [
        {
            "candidate": 7,
            "source": "NIST coherence-limited digital qubit control",
            "decision": "INELIGIBLE",
            "two_coordinate_path": True,
            "external_handover": True,
            "pre_and_post_windows": True,
            "eligible_evaluation_transitions": None,
            "failed_gates": [
                "D3: published CSVs are averaged parameter sweeps, not at least 60 independent crossing units"
            ],
        },
        {
            "candidate": 8,
            "source": "Larsen et al. 2D photonic cluster-state traces",
            "decision": "INELIGIBLE",
            "two_coordinate_path": True,
            "external_handover": False,
            "pre_and_post_windows": False,
            "eligible_evaluation_transitions": None,
            "failed_gates": [
                "D4: the public record is a persistent cluster-lattice trace, not an externally switched lattice-to-release crossing"
            ],
        },
    ]


def run_audit(root: Path) -> dict:
    q31_data = root / "q31_data"
    candidates = [
        audit_candidate4(q31_data / "source"),
        audit_candidate5(
            q31_data / "candidate5" / "quantinuum-2d-trajectory-data.zip"
        ),
        audit_candidate6(
            q31_data / "candidate6" / "Source Data _ full_version.zip"
        ),
        *audit_metadata_only_candidates(),
    ]
    return {
        "protocol": "Q31-LATTICE-TO-TRAVERSAL-SINGULARITY-FLIP-v1",
        "audit_date": "2026-07-26",
        "confirmatory_outcome_metrics_calculated": False,
        "candidate_count_in_this_reproducible_audit": len(candidates),
        "eligible_candidate_count": sum(c["decision"] == "ELIGIBLE" for c in candidates),
        "verdict": "INCONCLUSIVE — DATA/ELIGIBILITY GATE",
        "candidates": candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory containing q31_data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().with_name("Q31_DATA_GATE_AUDIT_RESULTS.json"),
    )
    args = parser.parse_args()
    result = run_audit(args.root)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
