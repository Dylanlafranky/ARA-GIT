"""Independent, result-file-based QA checks for T452."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T452_yeast_lifespan_time_phase")
RESULTS = ROOT / "results"


def corr(a, b):
    return float(np.corrcoef(np.asarray(a, float), np.asarray(b, float))[0, 1])


def crossing(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    for i in range(1, len(x)):
        if x[i] >= 0.5 and y[i - 1] < 1 <= y[i]:
            return float(x[i - 1] + (1 - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1]))
    return float("nan")


def main():
    generation = pd.read_csv(RESULTS / "T452_GENERATION_STATES.csv")
    interval = pd.read_csv(RESULTS / "T452_INTERVAL_CHILDREN.csv")
    cells = pd.read_csv(RESULTS / "T452_CELL_SUMMARY.csv")
    gen_curves = pd.read_csv(RESULTS / "T452_GENERATION_CURVES.csv")
    rate_curves = pd.read_csv(RESULTS / "T452_INTERVAL_CURVES.csv")
    recorded = json.loads((RESULTS / "T452_RESULT.json").read_text(encoding="utf-8"))

    checks = {}
    checks["225_unique_cells"] = len(cells) == 225 and cells.cell_id.nunique() == 225
    checks["frozen_cohort_counts_94_12_119"] = cells.groupby("cohort").size().to_dict() == {"development": 94, "external": 119, "holdout": 12}
    checks["generation_grain_unique"] = not generation.duplicated(["cohort", "cell_id", "generation_observation"]).any()
    checks["interval_grain_unique"] = not interval.duplicated(["cohort", "cell_id", "interval_index"]).any()
    checks["all_cells_have_at_least_three_G1"] = bool((cells.observed_g1_count >= 3).all())
    checks["all_spans_positive"] = bool((cells.lifespan_hours_observed > 0).all())
    checks["interval_counts_reconcile"] = int(cells.observed_division_intervals.sum()) == len(interval)
    checks["generation_counts_reconcile"] = int(cells.observed_g1_count.sum()) == len(generation)

    # Recompute every generation-state formula from the saved raw hours/counts.
    expected_a = 2 * (generation.generation_observation - 1) / (generation.observed_g1_count - 1)
    expected_b = 2 * generation.hours_elapsed / generation.lifespan_hours_observed
    checks["maturity_formula_all_rows"] = bool(np.allclose(generation.maturity_A, expected_a, atol=1e-12))
    checks["elapsed_formula_all_rows"] = bool(np.allclose(generation.time_elapsed_B, expected_b, atol=1e-12))
    checks["remaining_formula_all_rows"] = bool(np.allclose(generation.time_remaining_B, 2 - expected_b, atol=1e-12))
    checks["shadow_formula_all_rows"] = bool(np.allclose(generation.time_shadow, expected_b - expected_a, atol=1e-12))
    checks["counter_phase_identity_all_rows"] = bool(np.allclose(generation.te_ara_sum + generation.time_shadow, 2, atol=1e-12))

    first = generation[generation.generation_observation.eq(1)]
    last = generation[generation.generation_observation.eq(generation.observed_g1_count)]
    checks["forced_endpoints_exactly_close"] = bool(np.allclose(first.time_shadow, 0) and np.allclose(last.time_shadow, 0))

    # Independently recompute headline transfer correlations from saved median curves.
    shadow = gen_curves[(gen_curves.metric.eq("time_shadow")) & gen_curves.grid_A.between(0.10, 1.90)]
    wide_shadow = shadow.pivot(index="grid_A", columns="cohort", values="median")
    hold_r = corr(wide_shadow.development, wide_shadow.holdout)
    ext_r = corr(wide_shadow.development, wide_shadow.external)
    checks["holdout_shadow_r_matches"] = abs(hold_r - recorded["curve_transfer"][0]["correlation"]) < 1e-12
    checks["external_shadow_r_matches"] = abs(ext_r - recorded["curve_transfer"][1]["correlation"]) < 1e-12

    crossing_values = {}
    rate = rate_curves[rate_curves.metric.eq("local_time_rate")]
    for cohort, group in rate.groupby("cohort"):
        group = group.sort_values("grid_A")
        crossing_values[cohort] = crossing(group.grid_A, group["median"])
    checks["crossings_match"] = all(abs(crossing_values[c] - recorded[f"{c}_crossing_A"]) < 1e-12 for c in crossing_values)

    # Verify the order-control conclusions without reusing analysis code.
    shuffle = pd.read_csv(RESULTS / "T452_SHUFFLE_TESTS.csv").set_index("cohort")
    checks["holdout_observed_above_shuffle_95"] = bool(shuffle.loc["holdout", "observed_median_late_minus_early"] > shuffle.loc["holdout", "null_q95"])
    checks["external_observed_above_shuffle_95"] = bool(shuffle.loc["external", "observed_median_late_minus_early"] > shuffle.loc["external", "null_q95"])
    checks["minimum_empirical_p_is_resolution_limit"] = bool(np.allclose(shuffle.empirical_p_upper, 1 / 2001))

    html = RESULTS / "T452_YEAST_LIFESPAN_TIME_PHASE_REPORT.html"
    html_text = html.read_text(encoding="utf-8")
    checks["portable_html_exists_and_is_self_contained"] = html.stat().st_size > 500_000 and "portable-artifact" in html_text.lower()
    checks["report_contains_core_caveats"] = all(
        phrase in html_text
        for phrase in ["two endpoint closures", "cannot yet predict death", "omitted death image", "not proof of a universal Time wave"]
    )

    failures = [name for name, passed in checks.items() if not passed]
    validation = {
        "assessment": "Share with caveats" if not failures else "Needs revision",
        "checks_passed": int(sum(checks.values())),
        "checks_total": len(checks),
        "failed_checks": failures,
        "checks": checks,
        "independently_recomputed": {
            "holdout_shadow_correlation": hold_r,
            "external_shadow_correlation": ext_r,
            "crossings_A": crossing_values,
        },
        "required_caveats": [
            "Completed-life normalization uses the future terminal boundary and is not prospective prediction.",
            "The first and last shadow values are forced to zero.",
            "The numeric workbook stops at the last G1 before the omitted death image.",
            "The holdout contains 12 cells; the external cohort strengthens the core curve but lacks fluorescence.",
            "Portable HTML passed structural/payload verification; browser interaction was not verified because Chromium was unavailable.",
        ],
    }
    (RESULTS / "T452_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
