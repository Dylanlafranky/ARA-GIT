"""Independent saved-artifact checks for T374."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / "external_data" / "coherent_argon_3903810"
EXPECTED_HASH = "96186d69e2f1a54cba582d15e7c5d809720f6ce1c47ae21ad2dcceda52019c3a"
PROFILE_GATE = 1.920729410347062


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    protocol = HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_PROTOCOL_2026-08-13.md"
    results_path = HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_RESULTS.json"
    cuts_path = HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_CUTS.csv"
    controls_path = HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_CONTROLS.csv"
    figure_path = HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_FIGURE.png"
    script_path = HERE / "t374_liquid_argon_axis_consistency.py"

    for p in (protocol, results_path, cuts_path, controls_path, figure_path, script_path):
        check(f"file exists: {p.name}", p.exists() and p.stat().st_size > 0, str(p))

    digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    check("frozen protocol hash", digest == EXPECTED_HASH, digest)

    r = json.loads(results_path.read_text(encoding="utf-8"))
    check("same medium declared", r["medium_change"] is False, str(r["medium_change"]))
    check("same identity declared", r["identity_change"] is False, str(r["identity_change"]))
    check("target frozen at 1.25", abs(r["target_handover_x"] - 1.25) < 1e-12, str(r["target_handover_x"]))
    check("target share stable", abs(r["target_prompt_share"] - 0.5032314472084726) < 1e-9, str(r["target_prompt_share"]))
    check("template reconstruction retained", r["signal_decomposition_nrmse"] < 0.10, str(r["signal_decomposition_nrmse"]))

    raw = np.loadtxt(DATA / "datanobkgsub.txt")
    check("source rows are 12x8x10", raw.shape == (960, 4), str(raw.shape))
    check("source count is 3752", abs(float(raw[:, 3].sum()) - 3752.0) < 1e-9, str(raw[:, 3].sum()))

    cuts = r["cuts"]
    check("all seven cuts retained", len(cuts) == 7, str(list(cuts)))
    check("full 3d near recorded value", abs(cuts["full_3d"]["handover_x"] - 1.2388301917891118) < 1e-6, str(cuts["full_3d"]["handover_x"]))
    check("energy-time on movement side", 1.0 <= cuts["energy_time"]["handover_x"] <= 1.5, str(cuts["energy_time"]["handover_x"]))
    check("f90-time reaches far pole", cuts["f90_time"]["handover_x"] > 1.99, str(cuts["f90_time"]["handover_x"]))
    check("time-only reaches far pole", cuts["time_only"]["handover_x"] > 1.99, str(cuts["time_only"]["handover_x"]))
    check("primary exact target compatible", all(cuts[n]["profile_delta_nll_at_1_25"] <= PROFILE_GATE for n in ("energy_time", "f90_time")), str([cuts[n]["profile_delta_nll_at_1_25"] for n in ("energy_time", "f90_time")]))
    check("axis consistency correctly fails", r["main_axis_consistency_gate"] is False, str(r["main_axis_consistency_gate"]))

    controls = r["arrival_order_controls"]
    check("four time-bearing controls retained", len(controls) == 4, str(list(controls)))
    check("nine shifts per time-bearing cut", all(len(v["controls"]) == 9 for v in controls.values()), str({k: len(v["controls"]) for k, v in controls.items()}))
    check("native rank 1 in every control", all(v["native_rank_of_10_lower_is_better"] == 1 for v in controls.values()), str({k: v["native_rank_of_10_lower_is_better"] for k, v in controls.items()}))
    check("native beats every shifted NLL", all(all(row["shifted_minus_native_nll"] > 0 for row in v["controls"]) for v in controls.values()), "all 36 differences positive")
    check("arrival-order gate correctly passes", r["arrival_order_control_gate"] is True, str(r["arrival_order_control_gate"]))
    check("verdict matches gates", r["verdict"] == "LIQUID-PARENT 1.25 LEAD NOT AXIS-CONSISTENT", r["verdict"])

    with cuts_path.open(newline="", encoding="utf-8") as f:
        cut_rows = list(csv.DictReader(f))
    check("cut CSV has seven rows", len(cut_rows) == 7, str(len(cut_rows)))
    check("cut CSV matches JSON centres", all(abs(float(row["handover_x"]) - cuts[row["cut"]]["handover_x"]) < 1e-12 for row in cut_rows), "all rows")

    with controls_path.open(newline="", encoding="utf-8") as f:
        control_rows = list(csv.DictReader(f))
    check("control CSV has 36 rows", len(control_rows) == 36, str(len(control_rows)))
    check("control CSV differences positive", all(float(row["shifted_minus_native_nll"]) > 0 for row in control_rows), "all rows")

    passed = sum(c["pass"] for c in checks)
    validation = {
        "test": "T374",
        "validator": "independent saved-artifact recomputation and consistency checks",
        "passed": passed,
        "total": len(checks),
        "all_pass": passed == len(checks),
        "checks": checks,
    }
    (HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_VALIDATION.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))
    raise SystemExit(0 if validation["all_pass"] else 1)


if __name__ == "__main__":
    main()
