"""Independent artifact validator for T363; does not import the scorer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PREFIX = "T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_"
HASHES = {
    "T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md": "6CA197872CBF3324CDCAE13E41BAB21C3EE75BD6A2B7D8DB1301275C3548806B",
    "T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md": "C746FAD21356EAE0A8B95DECABCE5F218DD667160BBC11B88AD13939E0D5BC80",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().map({"true": True, "false": False})


def main() -> None:
    result = json.loads((HERE / f"{PREFIX}RESULTS.json").read_text(encoding="utf-8"))
    dense = pd.read_csv(HERE / f"{PREFIX}TIMESERIES.csv")
    parent = pd.read_csv(HERE / f"{PREFIX}PARENT_WINDOWS.csv")
    controls = pd.read_csv(HERE / f"{PREFIX}CONTROLS.csv")
    events = pd.read_csv(HERE / f"{PREFIX}REPLICATION_EVENTS.csv")
    event_parents = pd.read_csv(HERE / f"{PREFIX}REPLICATION_PARENT_WINDOWS.csv")
    gates_saved = bool_series(pd.read_csv(HERE / f"{PREFIX}FROZEN_GATES.csv")["passed"]).tolist()
    source = pd.read_csv(HERE / f"{PREFIX}SOURCE_QA.csv")

    checks = [{"check": f"frozen hash {name}", "passed": sha256(HERE / name) == value} for name, value in HASHES.items()]
    main_time = float(result["main_slip_time_s"])
    release_index = int(np.argmax(dense["release_R"].to_numpy(float)))
    release_time = float(dense.iloc[release_index]["time_s"])
    release_error = abs(release_time - main_time)
    exclude = np.abs(dense["time_s"] - main_time) > 0.1
    r = float(np.corrcoef(dense.loc[exclude, "x_S"], dense.loc[exclude, "x_F"])[0, 1])
    physical_counts = dense["quadrant"].value_counts()
    physical_qualifying = int((physical_counts >= 0.005 * len(dense)).sum())
    relative = dense["time_to_slip_s"]
    pre = float(np.median(dense.loc[(relative >= -0.10) & (relative <= -0.02), "x_S"]))
    post = float(np.median(dense.loc[(relative >= 0.02) & (relative <= 0.10), "x_S"]))
    max_xf = float(dense.loc[np.abs(relative) <= 0.1, "x_F"].max())
    reconnect = dense.loc[(relative >= 0) & (relative <= 0.3) & (dense["x_F"] < 1), "time_to_slip_s"]
    reconnect_time = float(reconnect.iloc[0]) if len(reconnect) else None

    parent_counts = parent["quadrant"].value_counts()
    parent_qualifying = int((parent_counts >= 3).sum())
    handover = parent.loc[parent["parent_step"].idxmax()]
    handover_time = float(handover["end_position"])
    handover_error = abs(handover_time - main_time)
    release_parent = parent.iloc[int(np.argmin(np.abs(parent["end_position"] - release_time)))]
    release_percentile = float(np.mean(parent["parent_step"] <= release_parent["parent_step"]))

    shuffle_median = float(controls[controls["control"].str.startswith("time_shuffle")]["timing_error_s"].median())
    names = ["reversal", "storage_only", "signless_transfer", "wrong_marker_0.25", "wrong_marker_0.50", "wrong_marker_0.75"]
    control_errors = {name: float(controls.loc[controls["control"] == name, "timing_error_s"].iloc[0]) for name in names}

    child = bool_series(events["child_tension_pass"])
    parent_passes = bool_series(events["parent_pass"])
    child_all, child_dry, child_fluid = int(child.sum()), int(child[events["medium"] == "dry"].sum()), int(child[events["medium"] == "fluid"].sum())
    parent_all, parent_dry, parent_fluid = int(parent_passes.sum()), int(parent_passes[events["medium"] == "dry"].sum()), int(parent_passes[events["medium"] == "fluid"].sum())

    gates = [
        bool(bool_series(source["passed"]).all() and abs(r) < .98 and release_error <= .10),
        bool(physical_qualifying >= 3 and pre-post >= .25 and max_xf >= 1.5 and reconnect_time is not None and reconnect_time <= .30),
        bool(parent_qualifying >= 2 and handover_error <= .512 and release_percentile >= .99),
        bool(handover_error + 1e-9 < shuffle_median and all(handover_error + 1e-9 < value for value in control_errors.values())),
        bool(child_all >= 12 and child_dry >= 8 and child_fluid >= 4),
        bool(parent_all >= 12 and parent_dry >= 8 and parent_fluid >= 4),
    ]
    component_all = bool(
        (events["storage_drop"] >= .25).all()
        and (events["near_drop_max_x_F"] >= 1.5).all()
        and events["reconnect_relative_row"].notna().all()
    )
    checks += [
        {"check": "dense time key unique", "passed": bool(dense["time_s"].is_unique)},
        {"check": "dense coordinate ranges", "passed": bool(dense[["x_S","x_F"]].ge(0).all().all() and dense[["x_S","x_F"]].le(2).all().all())},
        {"check": "dense four child quadrants", "passed": set(physical_counts.index) == {"Ab","aB","bA","Ba"}},
        {"check": "parent natural key", "passed": bool(parent["end_index"].is_unique)},
        {"check": "15 unique replication events", "passed": len(events) == 15 and not events.duplicated(["medium","event"]).any()},
        {"check": "replication parent keys", "passed": not event_parents.duplicated(["medium","event","end_index"]).any()},
        {"check": "all 15 tension components retained", "passed": component_all},
        {"check": "six gates reproduce", "passed": gates == gates_saved},
        {"check": "overall verdict reproduces", "passed": result["all_gates_passed"] == all(gates)},
        {"check": "headline release timing", "passed": bool(np.isclose(release_error, result["release_slip_error_s"], atol=1e-12))},
    ]
    image = Image.open(HERE / f"{PREFIX}FIGURE.png")
    checks.append({"check": "figure readable", "passed": image.width >= 2000 and image.height >= 1500})
    passed = all(row["passed"] for row in checks)
    output = {
        "validation_status": "PASS" if passed else "FAIL",
        "checks_passed": int(sum(row["passed"] for row in checks)),
        "checks_total": len(checks),
        "gates": gates,
        "saved_gates": gates_saved,
        "component_diagnostic_all_15": component_all,
        "recomputed": {
            "release_slip_error_s": release_error, "raw_axis_r": r,
            "physical_qualifying_quadrants": physical_qualifying, "storage_drop": pre-post,
            "max_x_F": max_xf, "reconnect_time": reconnect_time,
            "parent_qualifying_quadrants": parent_qualifying, "parent_handover_error_s": handover_error,
            "release_parent_step_percentile": release_percentile,
            "replication_child": [child_all,child_dry,child_fluid],
            "replication_parent": [parent_all,parent_dry,parent_fluid],
        },
        "checks": checks,
    }
    (HERE / f"{PREFIX}VALIDATION.json").write_text(json.dumps(output,indent=2),encoding="utf-8")
    lines=["# T363 independent validation","",f"**Status:** **{output['validation_status']} — {output['checks_passed']}/{output['checks_total']} checks**","","| Check | Result |","|---|---|",*[f"| {r['check']} | {'PASS' if r['passed'] else 'FAIL'} |" for r in checks],"",f"Frozen gate vector: `{gates}`.",f"All-15 component diagnostic: `{component_all}`."]
    (HERE / f"{PREFIX}VALIDATION.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2))
    if not passed: raise SystemExit(1)


if __name__ == "__main__":
    main()
