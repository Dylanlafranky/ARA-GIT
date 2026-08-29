"""Deterministic data-quality checks for the final exact-modal T449 dataset."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T449_time_facing_children")
RESULTS = ROOT / "results"


def main() -> None:
    data = pd.read_csv(RESULTS / "T449_child_windows.csv")
    qa = json.loads((RESULTS / "T449_extraction_qa.json").read_text(encoding="utf-8"))
    key_duplicates = int(data.duplicated(["source_file", "child_window_index"]).sum())
    share_columns = [column for column in data if column.startswith("share_")]
    share_error = (data[share_columns].sum(axis=1) - 1).abs()
    expected_midpoint = (data.child_window_index + 0.5) / 6
    midpoint_error = (data.child_midpoint_hours - expected_midpoint).abs()
    collapse_error = (data.hours_to_collapse - (data.collapse_hour - data.child_midpoint_hours)).abs()
    contiguous_failures = []
    for name, group in data.groupby("source_file"):
        observed = group.child_window_index.sort_values().to_numpy(dtype=int)
        if not np.array_equal(observed, np.arange(len(observed))):
            contiguous_failures.append(name)
    eligible = data[data.eligible.eq(1)]
    finite_eligible = eligible[["C_A_retention", "C_B_traversal"]].notna().all(axis=1)
    holdout = data[data.experiment.eq("exp4")]
    final6 = holdout[(holdout.hours_to_collapse > 0) & (holdout.hours_to_collapse <= 6)]
    earlier = holdout[(holdout.hours_to_collapse > 24) & (holdout.hours_to_collapse <= 72)]
    by_experiment = (
        data.groupby("experiment")
        .eligible.agg(windows="size", eligible_windows="sum", eligible_fraction="mean")
        .reset_index()
        .to_dict(orient="records")
    )
    extraction_bytes = int(sum(int(row["bytes_fetched"]) for row in qa))
    result = {
        "source_files": int(data.source_file.nunique()),
        "rows": int(len(data)),
        "columns": int(len(data.columns)),
        "experiments": sorted(data.experiment.unique().tolist()),
        "duplicate_source_window_keys": key_duplicates,
        "files_with_noncontiguous_window_indices": contiguous_failures,
        "max_state_share_closure_error": float(share_error.max()),
        "max_child_midpoint_formula_error_hours": float(midpoint_error.max()),
        "max_hours_to_collapse_formula_error_hours": float(collapse_error.max()),
        "nonpositive_pre_collapse_midpoints": int((data.hours_to_collapse <= 0).sum()),
        "eligible_rows": int(len(eligible)),
        "eligible_fraction": float(len(eligible) / len(data)),
        "eligible_rows_with_finite_primary_coordinates_fraction": float(finite_eligible.mean()),
        "eligible_files": int(eligible.source_file.nunique()),
        "development_files": int(eligible[eligible.experiment.ne("exp4")].source_file.nunique()),
        "holdout_files": int(eligible[eligible.experiment.eq("exp4")].source_file.nunique()),
        "eligible_by_experiment": by_experiment,
        "holdout_final6_eligible_fraction": float(final6.eligible.mean()),
        "holdout_24_to_72h_eligible_fraction": float(earlier.eligible.mean()),
        "holdout_final6_windows": int(len(final6)),
        "holdout_24_to_72h_windows": int(len(earlier)),
        "network_range_requests": int(sum(int(row["requests"]) for row in qa)),
        "network_bytes_fetched": extraction_bytes,
        "network_mebibytes_fetched": extraction_bytes / 2**20,
        "quality_status": "usable with material visibility caveat",
        "blocking_issues": [],
        "material_caveats": [
            "Only windows with at least 80% resolved one-second states are primary-analysis eligible.",
            "Eligibility varies substantially by fly and experiment; unresolved share remains a modeled control.",
            "Behaviour classification is an observational shadow, not a direct molecular clock.",
            "Collapse is author-indexed and used only for retrospective evaluation.",
        ],
    }
    if key_duplicates or contiguous_failures or not finite_eligible.all():
        result["quality_status"] = "blocked"
        result["blocking_issues"].append("Primary key, continuity, or finite-coordinate check failed.")
    (RESULTS / "T449_DATA_QUALITY.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
