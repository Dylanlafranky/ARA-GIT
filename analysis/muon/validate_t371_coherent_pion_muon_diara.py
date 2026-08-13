"""Independent artifact and arithmetic validation for T371."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = Path(r"F:\SystemFormulaFolder\external_data\coherent_csi_2110_07730\anc")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    r = json.loads((HERE / "T371_COHERENT_PION_MUON_DIARA_RESULTS.json").read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["all_source_hashes"] = all(sha(DATA / name) == digest for name, digest in r["hashes_sha256"].items())

    c = np.loadtxt(DATA / "dataBeamOnC.txt")
    a = np.loadtxt(DATA / "dataBeamOnAC.txt")
    selected = lambda z: (z[:, 0] >= 0) & (z[:, 0] < 60) & (z[:, 1] >= 0) & (z[:, 1] < 6)
    checks["event_counts"] = int(selected(c).sum()) == r["event_counts"]["beam_coincident"] == 1578 and int(selected(a).sum()) == r["event_counts"]["anti_coincident"] == 1295

    x = r["ara_compression"]
    checks["ara_arithmetic"] = abs(x["x_prompt"] + x["x_delayed"] - 2) < 1e-12
    checks["both_intervals_positive"] = r["fit"]["prompt_ci95"][0] > 0 and r["fit"]["delayed_ci95"][0] > 0
    checks["single_branch_aic"] = r["fit"]["delta_aic_vs_prompt_only"] >= 10 and r["fit"]["delta_aic_vs_delayed_only"] >= 10
    checks["order_controls"] = r["permutation"]["as_good_as_chronological"] <= 10 and r["fit"]["delta_aic_vs_swapped_order"] > 10
    checks["timing_order"] = r["timing"]["delayed_peak_us"] > r["timing"]["prompt_peak_us"]
    checks["leave_one_out"] = all(z["prompt"] > 0 and z["delayed"] > 0 for z in r["leave_one_out"])
    checks["all_registered_gates"] = all(r["gates"].values())
    checks["artifacts_present"] = all((HERE / name).exists() for name in [
        "T371_COHERENT_PION_MUON_DIARA_FIGURE.png",
        "T371_COHERENT_PION_MUON_DIARA_FIGURE.svg",
        "T371_COHERENT_PION_MUON_DIARA_COMPONENTS.csv",
        "T371_COHERENT_PION_MUON_DIARA_REPORT_2026-08-13.md",
    ])

    with (HERE / "T371_COHERENT_PION_MUON_DIARA_COMPONENTS.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    checks["component_rows"] = len(rows) == 12

    verdict = "PASS" if all(checks.values()) else "FAIL"
    out = {"test": "T371", "validation": verdict, "checks": checks}
    (HERE / "T371_COHERENT_PION_MUON_DIARA_VALIDATION.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    if verdict != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

