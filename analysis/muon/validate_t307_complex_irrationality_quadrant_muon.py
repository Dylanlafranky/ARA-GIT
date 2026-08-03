#!/usr/bin/env python3
"""Independent artifact-level validation for T307."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
RESULT = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_RESULTS.json"
SERIES = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_SERIES.csv"
STEPS = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_STEPS.csv"
PREDICTION = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_PREDICTION.csv"
RADIAL = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_RADIAL.csv"
FIGURE = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON.png"
OUT = HERE / "T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_VALIDATION.json"

PAIRS = [
    "parent_phi_time_vs_e",
    "child_anti_phi_vs_e",
    "control_phi_time_vs_sqrt2",
    "control_e_vs_sqrt2",
    "control_phi_time_vs_pi3",
    "control_e_vs_pi3",
    "control_sqrt2_vs_pi3",
]
FAMILIES = ["beam7", "beam7_cycle23", "beam7_decay"]
STATES = [
    "contracting_reverse",
    "contracting_forward",
    "expanding_reverse",
    "expanding_forward",
]
PRIMARY = "parent_phi_time_vs_e"


def check(name: str, passed: bool, detail: object) -> dict:
    return {"name": name, "pass": bool(passed), "detail": detail}


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    series = pd.read_csv(SERIES)
    steps = pd.read_csv(STEPS)
    prediction = pd.read_csv(PREDICTION)
    radial = pd.read_csv(RADIAL)
    checks = []

    expected_series = len(PAIRS) * len(FAMILIES) * 768
    expected_steps = len(PAIRS) * len(FAMILIES) * 767
    expected_prediction = len(PAIRS) * len(FAMILIES) * 5 + len(FAMILIES) * 3
    expected_radial = len(PAIRS) * len(FAMILIES) * 7
    row_counts = {
        "series": len(series),
        "steps": len(steps),
        "prediction": len(prediction),
        "radial": len(radial),
    }
    checks.append(
        check(
            "declared row counts",
            row_counts
            == {
                "series": expected_series,
                "steps": expected_steps,
                "prediction": expected_prediction,
                "radial": expected_radial,
            },
            row_counts,
        )
    )

    unique = {
        "series": not series.duplicated(["pair", "family", "n"]).any(),
        "steps": not steps.duplicated(["pair", "family", "n_from", "n_to"]).any(),
        "prediction": not prediction.duplicated(["pair", "family", "method"]).any(),
        "radial": not radial.duplicated(["pair", "family", "lag"]).any(),
    }
    checks.append(check("unique declared grains", all(unique.values()), unique))

    max_q_error = 0.0
    max_log_error = 0.0
    max_delta_error = 0.0
    count_mismatch = {}
    for pair in PAIRS:
        for family in FAMILIES:
            z_part = series[(series.pair == pair) & (series.family == family)].sort_values("n")
            s_part = steps[(steps.pair == pair) & (steps.family == family)].sort_values("n_from")
            z = z_part.u.to_numpy() + 1j * z_part.v.to_numpy()
            valid = s_part.valid.to_numpy(dtype=bool)
            q = z[1:][valid] / z[:-1][valid]
            stored = s_part.q_real.to_numpy()[valid] + 1j * s_part.q_imag.to_numpy()[valid]
            max_q_error = max(max_q_error, float(np.max(np.abs(q - stored))))
            max_log_error = max(
                max_log_error,
                float(np.max(np.abs(np.log(np.abs(q)) - s_part.log_s.to_numpy()[valid]))),
            )
            angular = np.angle(np.exp(1j * (np.angle(q) - s_part.delta_rad.to_numpy()[valid])))
            max_delta_error = max(max_delta_error, float(np.max(np.abs(angular))))
            observed = s_part[s_part.valid].quadrant.value_counts().to_dict()
            recorded = result["step_stats"][f"{pair}|{family}"]["quadrant_counts"]
            count_mismatch[f"{pair}|{family}"] = {
                state: int(observed.get(state, 0)) - int(recorded.get(state, 0))
                for state in STATES + ["boundary"]
            }
    checks.append(
        check(
            "complex q/log/phase recomputation",
            max_q_error <= 5e-10 and max_log_error <= 2e-11 and max_delta_error <= 2e-11,
            {"q": max_q_error, "log_s": max_log_error, "delta": max_delta_error},
        )
    )
    checks.append(
        check(
            "quadrant counts reconcile",
            all(all(value == 0 for value in item.values()) for item in count_mismatch.values()),
            count_mismatch,
        )
    )

    g1_families = []
    for family in FAMILIES:
        part = steps[(steps.pair == PRIMARY) & (steps.family == family)]
        valid_fraction = float(part.valid.mean())
        all_four = all(int((part.quadrant == state).sum()) > 0 for state in STATES)
        if valid_fraction >= 0.90 and all_four:
            g1_families.append(family)
    g1 = len(g1_families) >= 2

    g2_families = []
    for family in FAMILIES:
        part = prediction[(prediction.pair == PRIMARY) & (prediction.family == family)]
        errors = {row.method: float(row.normalized_mae) for row in part.itertuples()}
        ara_row = part[part.method == "ara_quadrant"].iloc[0]
        if (
            errors["ara_quadrant"] < errors["persistence"]
            and errors["ara_quadrant"] < errors["global_ratio"]
            and errors["ara_quadrant"] < errors["affine_ar2"]
            and errors["ara_quadrant"] < float(ara_row.shuffle_p05)
        ):
            g2_families.append(family)
    g2 = len(g2_families) >= 2

    g3_families = []
    for family in FAMILIES:
        part = prediction[(prediction.family == family) & prediction.pair.isin(PAIRS)]
        improvements = part.groupby("pair").ara_improvement_over_best_fixed.first()
        if str(improvements.idxmax()) == PRIMARY:
            g3_families.append(family)
    g3 = len(g3_families) >= 2

    g4_families = []
    for family in FAMILIES:
        intact = float(
            prediction[
                (prediction.pair == PRIMARY)
                & (prediction.family == family)
                & (prediction.method == "ara_quadrant")
            ].normalized_mae.iloc[0]
        )
        broken = prediction[
            prediction.pair.str.startswith("broken_primary_shift_")
            & (prediction.family == family)
        ].normalized_mae.astype(float)
        if len(broken) == 3 and bool((intact < broken).all()):
            g4_families.append(family)
    g4 = len(g4_families) >= 2
    gate_recount = {
        "G1": g1,
        "G1_families": g1_families,
        "G2": g2,
        "G2_families": g2_families,
        "G3": g3,
        "G3_families": g3_families,
        "G4": g4,
        "G4_families": g4_families,
    }
    recorded_gates = result["gates"]
    gate_match = (
        g1 == recorded_gates["G1_four_quadrant_coordinate"]
        and g1_families == recorded_gates["G1_passing_families"]
        and g2 == recorded_gates["G2_ordered_lineage"]
        and g2_families == recorded_gates["G2_passing_families"]
        and g3 == recorded_gates["G3_primary_specificity"]
        and g3_families == recorded_gates["G3_primary_winner_families"]
        and g4 == recorded_gates["G4_intact_vs_broken"]
        and g4_families == recorded_gates["G4_passing_families"]
    )
    checks.append(check("frozen gate recount", gate_match, gate_recount))

    observed_winners = {
        str(pair): {str(name): int(count) for name, count in group.winner.value_counts().items()}
        for pair, group in radial.groupby("pair")
    }
    observed_winners["__all_pairs__"] = {
        str(name): int(count) for name, count in radial.winner.value_counts().items()
    }
    checks.append(
        check(
            "radial winner counts reconcile",
            observed_winners == result["radial_winner_counts"],
            observed_winners,
        )
    )

    primary = series[series.pair == PRIMARY]
    contracting = []
    expanding = []
    for family in FAMILIES:
        amplitudes = primary[primary.family == family].sort_values("n").amplitude.to_numpy()
        for lag in [1, 2, 4, 8, 16, 32, 64]:
            ratios = amplitudes[lag:] / amplitudes[:-lag]
            contracting.extend(ratios[ratios < 1.0])
            expanding.extend(ratios[ratios > 1.0])
    med_c = float(np.median(contracting))
    med_e = float(np.median(expanding))
    recorded_post = result["post_hoc_primary_pooled_radial"]
    post_match = (
        abs(med_c - recorded_post["observed_median_contracting"]) <= 2e-11
        and abs(med_e - recorded_post["observed_median_expanding"]) <= 2e-11
    )
    checks.append(
        check(
            "post-hoc pooled radial medians reconcile",
            post_match,
            {"contracting": med_c, "expanding": med_e},
        )
    )

    with Image.open(FIGURE) as image:
        figure_detail = {"width": image.width, "height": image.height, "mode": image.mode}
    checks.append(
        check(
            "figure is readable PNG",
            figure_detail == {"width": 2400, "height": 1700, "mode": "RGB"},
            figure_detail,
        )
    )

    output = {
        "test": "T307 independent artifact validation",
        "passed": all(item["pass"] for item in checks),
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"passed": output["passed"], "checks": f'{output["checks_passed"]}/{output["checks_total"]}'}, indent=2))


if __name__ == "__main__":
    main()
