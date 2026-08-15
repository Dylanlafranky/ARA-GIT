"""Independent QA checks for T378's saved numerical artifact."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import t378_coherent_2017_holdout as t378


HERE = Path(__file__).resolve().parent
OUT = HERE / "T378_coherent_2017_holdout"
RESULT = OUT / "T378_results.json"
VALIDATION = OUT / "T378_validation.json"


def check(name, condition, detail):
    return {"name": name, "pass": bool(condition), "detail": detail}


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    yc = t378.load_grid("data_coincidence_beamOn.txt")
    ya = t378.load_grid("data_anticoincidence_beamOn.txt")
    bc = t378.load_grid("data_coincidence_beamOff.txt")
    ba = t378.load_grid("data_anticoincidence_beamOff.txt")
    rerun = t378.perform_fit(yc, ya)
    templates = rerun["templates"]
    params = rerun["full"]["params"]
    saved = np.asarray(result["fit"]["params"])
    boot = np.loadtxt(OUT / "T378_bootstrap.csv", delimiter=",", skiprows=1)
    timing = np.loadtxt(OUT / "T378_timing_components.csv", delimiter=",", skiprows=1)

    p_t = params[2] * templates[2].sum(axis=0)
    d_t = params[3] * templates[3].sum(axis=0)
    event = t378.equality_and_coordinate(t378.T_CENTERS, p_t, d_t)
    forced_sum = result["ara"]["x_prompt"] + result["ara"]["x_delayed"]
    checks = [
        check("released_primary_grid_shape", yc.shape == (12, 12), str(yc.shape)),
        check("released_control_grid_shape", bc.shape == (12, 12), str(bc.shape)),
        check("released_boundary_counts", [int(z.sum()) for z in [yc, ya, bc, ba]] == [547, 405, 209, 207], str([int(z.sum()) for z in [yc, ya, bc, ba]])),
        check("all_templates_normalized", np.allclose([z.sum() for z in templates], 1), str([float(z.sum()) for z in templates])),
        check("saved_fit_reproduces", np.allclose(params, saved, rtol=0, atol=1e-8), str((params - saved).tolist())),
        check("timing_export_has_12_rows", timing.shape == (12, 8), str(timing.shape)),
        check("bootstrap_has_1000_rows", boot.shape == (1000, 5), str(boot.shape)),
        check("both_branch_lower_bounds_positive", result["fit"]["prompt_ci95"][0] > 0 and result["fit"]["delayed_ci95"][0] > 0, str([result["fit"]["prompt_ci95"], result["fit"]["delayed_ci95"]])),
        check("handover_reproduces", abs(event["t_h_us"] - result["timing"]["t_h_us"]) < 1e-9 and abs(event["x_h"] - result["timing"]["x_h"]) < 1e-9, str(event)),
        check("ARA_sum_to_two_is_explicitly_forced", abs(forced_sum - 2) < 1e-12, f"{forced_sum:.16g}; bookkeeping only"),
        check("beamoff_does_not_resolve_prompt", result["beamoff_control"]["params"][2] == 0, str(result["beamoff_control"]["params"])),
        check("near_threshold_gates_remain_failed", not result["gates"]["G3_AIC_at_least_10_vs_each_single"] and not result["gates"]["G4_no_more_than_10_of_1000_permutations_as_good"], f"deltaAIC={result['fit']['delta_AIC_vs_prompt_only']:.6f}; permutations={result['permutation']['as_good']}/1000"),
    ]
    high = [c for c in checks if not c["pass"]]
    validation = {
        "artifact": str(RESULT),
        "overall_assessment": "SHARE WITH CAVEATS" if not high else "NEEDS REVISION",
        "checks": checks,
        "failed_checks": [c["name"] for c in high],
        "calculation_spot_checks": {
            "primary_counts_C_AC": [int(yc.sum()), int(ya.sum())],
            "control_counts_C_AC": [int(bc.sum()), int(ba.sum())],
            "fitted_signal_total": float(params[2] + params[3]),
            "fitted_background_total_in_C": float(params[0] + params[1]),
            "handover": event,
            "ARA_sum": forced_sum,
        },
        "methodology_caveats": [
            "The 2017 source releases count grids and timing PDFs but not ready-made flavor-specific CEvNS PE templates; the energy response is reconstructed from published physics and detector parameters.",
            "Both branches remain positive under low/high quenching-factor and time-only alternatives, but exact yield balance and x_H are model-dependent.",
            "The frozen pass thresholds were not relaxed after inspection: delta AIC missed 10 by 0.054 and 17/1000 chronology permutations were as good versus a maximum of 10.",
            "This is an ensemble known-decay crosswalk, not an event-linked prediction of a private muon decay.",
        ],
        "conclusion_boundary": "The holdout independently resolves prompt and delayed populations with correct order, but it does not pass every frozen high-stringency handover gate.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
