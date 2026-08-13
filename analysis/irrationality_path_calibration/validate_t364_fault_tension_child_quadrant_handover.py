"""Independent artifact validation for T364; does not import the run script."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
STEM = "T364_FAULT_TENSION_CHILD_QUADRANT_HANDOVER"


def main() -> None:
    result = json.loads((HERE / f"{STEM}_RESULTS.json").read_text(encoding="utf-8"))
    dense = pd.read_csv(HERE / f"{STEM}_DENSE_TIMESERIES.csv")
    events = pd.read_csv(HERE / f"{STEM}_REPLICATION_EVENTS.csv")
    controls = pd.read_csv(HERE / f"{STEM}_CONTROLS.csv")

    active = dense["active_Ab_child"].astype(bool).to_numpy()
    expected_u = 2 * (dense["x_S"].to_numpy(float) - 1)
    expected_v = 2 * (dense["x_F"].to_numpy(float) - 1)
    expected_h = np.divide(
        2 * expected_v,
        expected_u + expected_v,
        out=np.full(len(dense), np.nan),
        where=active & ((expected_u + expected_v) > 1e-15),
    )
    observed_h = dense["child_handover"].to_numpy(float)
    finite = np.isfinite(expected_h)

    tests = {
        "dense child u formula": bool(np.allclose(dense["child_u"], expected_u)),
        "dense child v formula": bool(np.allclose(dense["child_v"], expected_v)),
        "dense handover formula": bool(np.allclose(observed_h[finite], expected_h[finite])),
        "dense crossing within 10 ms": abs(float(result["dense"]["child_cross_lag_s"])) <= 0.010,
        "dense child ridge": abs(float(result["dense"]["child_handover_at_cross"]) - 1) <= 0.02,
        "fifteen directed replication crossings": bool(
            len(events) == 15
            and ((events["child_handover_before"] < 1) & (events["child_handover_after"] >= 1)).all()
        ),
        "fifteen crossings within one cadence": bool((events["child_cross_relative_row"].abs() <= 16).all()),
        "history open at all event cuts": bool((events["history_x_R_near_event"] > 1).all()),
        "history later reclosure retained": bool(
            ((events["history_reclose_relative_row"] > 0) & (events["history_reclose_relative_row"] <= 160)).all()
        ),
        "real dense alignment beats controls": bool(
            controls.loc[controls["control"] == "real slip", "nearest_crossing_error_s"].iloc[0]
            < controls.loc[controls["control"] != "real slip", "nearest_crossing_error_s"].min()
        ),
        "figure exists": bool((HERE / f"{STEM}_FIGURE.png").stat().st_size > 100_000),
    }
    passed = int(sum(tests.values()))
    payload = {"validation": "PASS" if passed == len(tests) else "FAIL", "passed": passed, "total": len(tests), "checks": tests}
    (HERE / f"{STEM}_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# T364 independent validation",
        "",
        f"**Verdict:** **{payload['validation']} — {passed}/{len(tests)} checks**",
        "",
    ]
    lines.extend(f"- {'PASS' if value else 'FAIL'} — {name}" for name, value in tests.items())
    (HERE / f"{STEM}_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if passed != len(tests):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

