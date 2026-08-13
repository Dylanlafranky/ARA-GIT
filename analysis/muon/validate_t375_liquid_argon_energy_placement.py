"""Independent saved-artifact checks for T375."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


HERE = Path(__file__).resolve().parent
EXPECTED_HASH = "1fcd0b3cac1d77c8968f2f520aad2450b4c2286ae75fb34407dab5a58f743382"


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    paths = {
        "protocol": HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_PROTOCOL_2026-08-13.md",
        "results": HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_RESULTS.json",
        "ladder": HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_LADDER.csv",
        "controls": HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_CONTROLS.csv",
        "figure": HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_FIGURE.png",
        "script": HERE / "t375_liquid_argon_energy_placement.py",
        "report": HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_REPORT_2026-08-13.md",
    }
    for label, path in paths.items():
        check(f"file exists: {label}", path.exists() and path.stat().st_size > 0, str(path))

    digest = hashlib.sha256(paths["protocol"].read_bytes()).hexdigest()
    check("protocol hash", digest == EXPECTED_HASH, digest)
    r = json.loads(paths["results"].read_text(encoding="utf-8"))
    check("same medium", r["medium_change"] is False, str(r["medium_change"]))
    check("same identity", r["identity_change"] is False, str(r["identity_change"]))
    check("target is 1.25", abs(r["target_x"] - 1.25) < 1e-12, str(r["target_x"]))
    check("frozen share stable", abs(r["target_prompt_share"] - 0.5032314472084726) < 1e-12, str(r["target_prompt_share"]))

    levels = np.asarray([1, 2, 3, 5, 12], dtype=float)
    ladder = r["ladder"]
    x = np.asarray([ladder[str(int(g))]["handover_x"] for g in levels])
    distance = abs(x - 1.25)
    check("five finite centres", np.all(np.isfinite(x)), str(x.tolist()))
    check("all four distances improve", np.all(np.diff(distance) < 0), str(distance.tolist()))
    rho = float(spearmanr(levels, distance).statistic)
    check("recomputed Spearman", abs(rho + 1.0) < 1e-12, str(rho))
    check("stored Spearman matches", abs(rho - r["primary_metrics"]["spearman_energy_groups_vs_distance_to_1_25"]) < 1e-12, str(r["primary_metrics"]["spearman_energy_groups_vs_distance_to_1_25"]))
    check("intermediates remain above ridge", np.all(x[1:4] >= 1.0), str(x[1:4].tolist()))
    check("three groups enter target neighbourhood", abs(x[2] - 1.25) < 0.03, str(x[2]))
    check("three crosses above and finer cuts remain below", x[2] > 1.25 and x[3] < 1.25 and x[4] < 1.25, str([x[2], x[3], x[4]]))
    check("twelve groups refine five-group distance", abs(x[4] - 1.25) < abs(x[3] - 1.25), str([abs(x[3] - 1.25), abs(x[4] - 1.25)]))
    check("primary gate passes", r["primary_metrics"]["primary_gate"] is True, str(r["primary_metrics"]["primary_gate"]))

    controls = r["energy_order_controls"]
    check("control levels 3,5,12", set(controls) == {"3", "5", "12"}, str(list(controls)))
    check("21 controls per level", all(len(v["controls"]) == 21 for v in controls.values()), str({k: len(v["controls"]) for k, v in controls.items()}))
    check("native rank 1 each level", all(v["native_rank_of_22_lower_is_better"] == 1 for v in controls.values()), str({k: v["native_rank_of_22_lower_is_better"] for k, v in controls.items()}))
    check("native beats median each level", all(v["native_better_than_median"] for v in controls.values()), str({k: v["native_better_than_median"] for k, v in controls.items()}))
    check("control gate passes", r["energy_order_control_gate"] is True, str(r["energy_order_control_gate"]))
    check("verdict matches", r["verdict"] == "PROGRESSIVE ENERGY-PLACEMENT MECHANISM SUPPORTED", r["verdict"])

    with paths["ladder"].open(newline="", encoding="utf-8") as f:
        ladder_rows = list(csv.DictReader(f))
    check("ladder CSV has five rows", len(ladder_rows) == 5, str(len(ladder_rows)))
    check("ladder CSV centres match", all(abs(float(row["handover_x"]) - ladder[row["energy_groups"]]["handover_x"]) < 1e-12 for row in ladder_rows), "all rows")

    with paths["controls"].open(newline="", encoding="utf-8") as f:
        control_rows = list(csv.DictReader(f))
    check("control CSV has 63 rows", len(control_rows) == 63, str(len(control_rows)))
    check("every control loses to native", all(float(row["permuted_minus_native_nll"]) > 0 for row in control_rows), "all rows")

    passed = sum(c["pass"] for c in checks)
    out = {"test": "T375", "passed": passed, "total": len(checks), "all_pass": passed == len(checks), "checks": checks}
    (HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_VALIDATION.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if out["all_pass"] else 1)


if __name__ == "__main__":
    main()
