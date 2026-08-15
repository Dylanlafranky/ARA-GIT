#!/usr/bin/env python3
"""Independent arithmetic and artifact audit for T384.

This validator deliberately does not import the execution script. It rebuilds
the frozen gates from the emitted run table and checks the separately gated
7.5-cycle tail table.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
OUT = HERE / "T384_irrationality_information_lock"
RESULTS = OUT / "T384_RESULTS.json"
RUNS = OUT / "T384_RUN_METRICS.csv"
TAIL = OUT / "T384_7P5_TAIL_AUDIT.csv"
TARGET = OUT / "T384_INDEPENDENT_VALIDATION.json"

VALIDATION = ["EMU00066571", "EMU00066584"]
HOLDOUT = ["EMU00066578", "EMU00066579", "EMU00066580"]
METHODS = {
    "open_loop_t382", "linear_persistence", "state_only", "direction_only",
    "wrong_relation", "full_irrationality",
}


def row(frame: pd.DataFrame, run: str, method: str) -> pd.Series | None:
    hit = frame[(frame["run"] == run) & (frame["method"] == method)]
    return None if hit.empty else hit.iloc[0]


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    frame = pd.read_csv(RUNS)
    tail = pd.read_csv(TAIL)

    primary = [
        "recursive_rmse", "recursive_waveform_r", "recursive_direction_agreement",
        "navigator_rmse", "navigator_direction_agreement",
    ]
    expected_runs = set(VALIDATION + HOLDOUT)
    observed_methods = set(frame.loc[frame["run"].isin(expected_runs), "method"])
    observed_runs = set(frame.loc[frame["split"].isin(["validation", "holdout"]), "run"])

    def navigation(run: str) -> bool:
        full, state, direction = (
            row(frame, run, "full_irrationality"),
            row(frame, run, "state_only"),
            row(frame, run, "direction_only"),
        )
        return bool(
            full is not None and state is not None and direction is not None
            and full.navigator_rmse <= state.navigator_rmse - 0.05
            and full.navigator_rmse <= direction.navigator_rmse - 0.05
            and full.navigator_direction_agreement >= 0.75
        )

    def wrong_relation(run: str) -> bool:
        full, wrong = row(frame, run, "full_irrationality"), row(frame, run, "wrong_relation")
        return bool(full is not None and wrong is not None
                    and full.navigator_rmse <= wrong.navigator_rmse - 0.05)

    def restoration(run: str) -> bool:
        full = row(frame, run, "full_irrationality")
        return bool(full is not None and full.recursive_waveform_r >= 0.80
                    and full.recursive_rmse <= 0.30)

    def contribution(run: str) -> bool:
        full, direction = row(frame, run, "full_irrationality"), row(frame, run, "direction_only")
        return bool(
            full is not None and direction is not None
            and (full.recursive_rmse <= direction.recursive_rmse - 0.05
                 or full.recursive_direction_agreement >= direction.recursive_direction_agreement + 0.05)
        )

    nav = {run: navigation(run) for run in VALIDATION + HOLDOUT}
    wrong = {run: wrong_relation(run) for run in VALIDATION + HOLDOUT}
    restore = {run: restoration(run) for run in VALIDATION + HOLDOUT}
    contribution_map = {run: contribution(run) for run in VALIDATION + HOLDOUT}
    rebuilt = {
        "g1_observed_child_readability": bool(result["gates"]["g1_observed_child_readability"]),
        "g2_local_navigation": all(nav[r] for r in VALIDATION) and sum(nav[r] for r in HOLDOUT) >= 2,
        "g3_wrong_relation": all(wrong.values()),
        "g4_recursive_restoration": all(restore[r] for r in VALIDATION) and sum(restore[r] for r in HOLDOUT) >= 2,
        "g5_information_lock_contribution": all(contribution_map[r] for r in VALIDATION)
        and sum(contribution_map[r] for r in HOLDOUT) >= 2,
    }

    expected_tail = (
        (tail["snr"] >= 3.0)
        & (tail["amplitude_valid_fraction"] >= 0.75)
        & tail["observed_child_ara"].notna()
    )
    checks = {
        "expected_runs_present": observed_runs == expected_runs,
        "expected_methods_present": observed_methods == METHODS,
        "primary_metrics_finite": bool(np.isfinite(frame.loc[frame["run"].isin(expected_runs), primary].to_numpy(float)).all()),
        "frozen_gates_reproduced": all(bool(result["gates"][key]) == bool(value) for key, value in rebuilt.items()),
        "tail_gate_reproduced": bool((tail["admissible"].astype(bool).to_numpy() == expected_tail.to_numpy()).all()),
        "claim_boundary_present": bool(result.get("claim_boundary")),
        "no_supported_status_with_failed_gate": not (
            result["status"].endswith("SUPPORTED") and not all(rebuilt.values())
        ),
    }
    # The literal string NOT_SUPPORTED ends with SUPPORTED; use the exact status
    # in the final logical consistency check rather than suffix matching.
    checks["no_supported_status_with_failed_gate"] = not (
        result["status"] == "IRRATIONALITY_INFORMATION_LOCK_SUPPORTED"
        and not all(rebuilt.values())
    )

    output = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "rebuilt_gates": rebuilt,
        "by_run": {
            "navigation": nav,
            "wrong_relation": wrong,
            "restoration": restore,
            "contribution": contribution_map,
        },
        "tail_admissible_fields_recomputed": tail.loc[expected_tail, "field_g"].astype(float).tolist(),
    }
    TARGET.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
