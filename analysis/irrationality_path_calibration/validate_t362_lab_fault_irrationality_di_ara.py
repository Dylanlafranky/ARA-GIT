"""Independent artifact validator for T362.

This recomputes the six verdict gates from emitted per-slice/per-window files.
It does not import the scoring program.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PREFIX = "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_"
EXPECTED_HASHES = {
    "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md": "34FB8445B4C49B421D5FAEE2FC75E8EE5386C827A8798F96C794EB89488DE8F8",
    "T362_LAB_FAULT_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md": "C015E113906130E10858807126F9A3EB3BBFA214C50739E043CFF785DCCB6299",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def metrics(actual: np.ndarray, predicted: np.ndarray) -> tuple[float, float, float]:
    rmse = float(np.sqrt(np.mean((predicted - actual) ** 2)))
    mae = float(np.mean(np.abs(predicted - actual)))
    keep = (np.abs(actual) > 1e-12) | (np.abs(predicted) > 1e-12)
    direction = float(np.mean(np.sign(actual[keep]) == np.sign(predicted[keep])))
    return rmse, mae, direction


def main() -> None:
    result = json.loads((HERE / f"{PREFIX}RESULTS.json").read_text(encoding="utf-8"))
    time_series = pd.read_csv(HERE / f"{PREFIX}TIMESERIES.csv")
    parent = pd.read_csv(HERE / f"{PREFIX}PARENT_WINDOWS.csv")
    controls = pd.read_csv(HERE / f"{PREFIX}CONTROLS.csv")
    predictors = pd.read_csv(HERE / f"{PREFIX}PREDICTORS.csv")
    prediction_path = pd.read_csv(HERE / f"{PREFIX}PREDICTION_PATH.csv")
    replication = pd.read_csv(HERE / f"{PREFIX}REPLICATION.csv")
    gates_saved = pd.read_csv(HERE / f"{PREFIX}FROZEN_GATES.csv")
    source_qa = pd.read_csv(HERE / f"{PREFIX}SOURCE_QA.csv")

    checks = []
    for name, expected in EXPECTED_HASHES.items():
        checks.append({"check": f"frozen hash {name}", "passed": sha256(HERE / name) == expected})

    main_time = float(result["main_slip_time_s"])
    exclude = np.abs(time_series["time_s"] - main_time) > 0.1
    raw_r = float(np.corrcoef(time_series.loc[exclude, "x_C"], time_series.loc[exclude, "x_M"])[0, 1])
    physical_counts = time_series["quadrant"].value_counts()
    physical_qualifying = int((physical_counts >= 0.01 * len(time_series)).sum())
    parent_counts = parent["quadrant"].value_counts()
    parent_qualifying = int((parent_counts >= 3).sum())
    handover_row = parent.loc[parent["parent_step"].idxmax()]
    timing_error = float(abs(handover_row["end_time_s"] - main_time))

    shuffle_median = float(controls[controls["control"].str.startswith("time_shuffle")]["timing_error_s"].median())
    named_errors = {
        name: float(controls.loc[controls["control"] == name, "timing_error_s"].iloc[0])
        for name in ["wrong_pair", "connection_only", "movement_only"]
    }

    actual = prediction_path["actual_next_signed_log_increment"].to_numpy(float)
    recomputed_predictors = []
    for name in ["two_axis_directional", "direction_blind", "connection_only", "movement_only", "wrong_pair", "persistence"]:
        recomputed_predictors.append((name, *metrics(actual, prediction_path[f"predicted_{name}"].to_numpy(float))))
    recomputed_predictors = pd.DataFrame(recomputed_predictors, columns=["method", "RMSE", "MAE", "direction_agreement"])
    primary = recomputed_predictors.query("method == 'two_axis_directional'").iloc[0]
    control_best = float(recomputed_predictors.query("method != 'two_axis_directional'")["RMSE"].min())
    main_index = int(np.argmax(time_series["signed_displacement_increment"].to_numpy(float)))
    main_path = prediction_path.loc[prediction_path["target_index"] == main_index]
    if len(main_path) != 1:
        raise AssertionError(f"expected one main-slip prediction row, got {len(main_path)}")
    main_risk = float(abs(main_path["predicted_two_axis_directional"].iloc[0]))
    risk_percentile = float(np.mean(np.abs(prediction_path["predicted_two_axis_directional"]) <= main_risk))

    dry = int(replication.query("medium == 'dry'")["final_20_percent"].sum())
    fluid = int(replication.query("medium == 'fluid'")["final_20_percent"].sum())
    all_replication = int(replication["final_20_percent"].sum())

    gates = [
        bool(source_qa["passed"].all() and abs(raw_r) < 0.98 and physical_qualifying >= 3),
        bool(parent_qualifying >= 2 and timing_error <= 1.024),
        # The wrong-pair timing equals the real timing to displayed and source
        # precision.  Require a genuine improvement beyond floating round-off.
        bool(timing_error + 1e-9 < shuffle_median and all(timing_error + 1e-9 < value for value in named_errors.values())),
        bool(primary["RMSE"] <= 0.9 * control_best and primary["direction_agreement"] >= 0.65),
        bool(risk_percentile >= 0.99),
        bool(all_replication >= 12 and dry >= 8 and fluid >= 4),
    ]
    saved = gates_saved["passed"].astype(str).str.lower().map({"true": True, "false": False}).tolist()
    checks.extend(
        [
            {"check": "time-series natural key", "passed": bool(time_series["time_s"].is_unique)},
            {"check": "parent natural key", "passed": bool(parent["end_index"].is_unique)},
            {"check": "four physical quadrants retained", "passed": set(physical_counts.index) == {"Ab", "aB", "bA", "Ba"}},
            {"check": "parent one-quadrant result retained", "passed": parent_counts.to_dict() == {"Ab": 341}},
            {"check": "prediction metrics reproduce summary", "passed": bool(np.allclose(recomputed_predictors[["RMSE", "MAE", "direction_agreement"]], predictors[["RMSE", "MAE", "direction_agreement"]], atol=1e-12))},
            {"check": "risk percentile reproduces headline", "passed": bool(np.isclose(risk_percentile, result["main_slip_risk_percentile"], atol=1e-12))},
            {"check": "six frozen gates reproduce", "passed": gates == saved},
            {"check": "overall verdict reproduces", "passed": bool(result["all_gates_passed"] == all(gates))},
        ]
    )
    image = Image.open(HERE / f"{PREFIX}FIGURE.png")
    checks.append({"check": "figure readable", "passed": image.width >= 2000 and image.height >= 1500})
    passed = bool(all(check["passed"] for check in checks))

    output = {
        "validation_status": "PASS" if passed else "FAIL",
        "checks_passed": int(sum(check["passed"] for check in checks)),
        "checks_total": len(checks),
        "recomputed_gates": gates,
        "saved_gates": saved,
        "recomputed": {
            "raw_axis_r": raw_r,
            "physical_qualifying_quadrants": physical_qualifying,
            "parent_qualifying_quadrants": parent_qualifying,
            "timing_error_s": timing_error,
            "shuffle_median_error_s": shuffle_median,
            "named_control_errors_s": named_errors,
            "risk_percentile": risk_percentile,
            "replication": {"all": all_replication, "dry": dry, "fluid": fluid},
        },
        "checks": checks,
    }
    (HERE / f"{PREFIX}VALIDATION.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    lines = [
        "# T362 independent validation",
        "",
        f"**Status:** **{output['validation_status']} — {output['checks_passed']}/{output['checks_total']} checks**",
        "",
        "| Check | Result |",
        "|---|---|",
        *[f"| {row['check']} | {'PASS' if row['passed'] else 'FAIL'} |" for row in checks],
        "",
        f"Recomputed gate vector: `{gates}`.",
    ]
    (HERE / f"{PREFIX}VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
