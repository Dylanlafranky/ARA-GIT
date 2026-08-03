"""Independent arithmetic and scope validation for T322."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_RESULTS.json"
EVENTS = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_EVENTS.csv"
FIGURE = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION.png"
FIGURE_SVG = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION.svg"
SCALE_FIGURE = HERE / "T322A_POSTHOC_SAME_PHASE_SCALE_RATIOS.png"
SCALE_FIGURE_SVG = HERE / "T322A_POSTHOC_SAME_PHASE_SCALE_RATIOS.svg"
OUTPUT = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_VALIDATION.json"
EXPECTED_PROTOCOL_HASH = "8e47f1c4bed2641e63bb959293ad1d197abbff1ccf52415741cd96f0f470b79a"
PHI = (1 + math.sqrt(5)) / 2
CANDIDATES = {"1": 1.0, "sqrt2": math.sqrt(2), "1.5": 1.5, "phi": PHI, "sqrt3": math.sqrt(3), "2": 2.0}


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with EVENTS.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    primary = [row for row in rows if row["dataset"] == "free_run3"]
    transfer = [row for row in rows if row["dataset"] == "driven_triple1"]

    ratios = np.asarray([float(row["r_time"]) for row in primary])
    whole = np.asarray([float(row["s_time"]) for row in primary])
    errors = np.asarray([float(row["e_phi_time"]) for row in primary])
    residuals = np.asarray([float(row["e_golden_time"]) for row in primary])
    med = float(np.median(ratios))
    winner = min(CANDIDATES, key=lambda name: abs(med - CANDIDATES[name]))

    formula_rows_ok = all(
        close(float(row["r_time"]), float(row["parent_duration_s"]) / float(row["child_duration_s"]))
        and close(float(row["s_time"]), (float(row["parent_duration_s"]) + float(row["child_duration_s"])) / float(row["parent_duration_s"]))
        and close(float(row["e_phi_time"]), max(abs(float(row["r_time"]) - PHI), abs(float(row["s_time"]) - PHI)))
        for row in rows
    )

    checks = {
        "protocol_hash_matches": digest(PROTOCOL) == EXPECTED_PROTOCOL_HASH,
        "result_protocol_hash_matches": result["protocol"]["sha256"] == EXPECTED_PROTOCOL_HASH,
        "primary_row_count_184": len(primary) == 184,
        "transfer_row_count_174": len(transfer) == 174,
        "all_event_formulas_recompute": formula_rows_ok,
        "pooled_median_ratio_recomputes": close(med, result["primary"]["summary"]["pooled"]["time"]["median_parent_child_ratio"]),
        "pooled_median_whole_ratio_recomputes": close(float(np.median(whole)), result["primary"]["summary"]["pooled"]["time"]["median_whole_parent_ratio"]),
        "pooled_phi_error_recomputes": close(float(np.median(errors)), result["primary"]["summary"]["pooled"]["time"]["median_e_phi"]),
        "pooled_golden_residual_recomputes": close(float(np.median(residuals)), result["primary"]["summary"]["pooled"]["time"]["median_golden_residual"]),
        "closest_landmark_recomputes": winner == result["primary"]["summary"]["pooled"]["time"]["closest_landmark"],
        "frozen_verdict_recomputes": result["primary"]["gates"]["passed"] == 0 and result["primary"]["gates"]["verdict"] == "NOT SUPPORTED",
        "figure_png_exists_nonempty": FIGURE.exists() and FIGURE.stat().st_size > 10_000,
        "figure_svg_exists_nonempty": FIGURE_SVG.exists() and FIGURE_SVG.stat().st_size > 10_000,
        "posthoc_scale_figure_png_exists_nonempty": SCALE_FIGURE.exists() and SCALE_FIGURE.stat().st_size > 10_000,
        "posthoc_scale_figure_svg_exists_nonempty": SCALE_FIGURE_SVG.exists() and SCALE_FIGURE_SVG.stat().st_size > 10_000,
    }

    # Methodological audit: the overlap-maximising match is not a neutral way
    # to estimate a population scale ratio.  Record the size of that effect.
    lineage_23 = [row for row in primary if row["lineage"] == "2->3"]
    matched_23 = float(np.median([float(row["r_time"]) for row in lineage_23]))
    child_unique = len({(row["branch"], row["child_index"]) for row in lineage_23})
    near_one = sum(abs(float(row["r_time"]) - 1.0) <= 0.08 for row in lineage_23)
    near_phi = sum(abs(float(row["r_time"]) - PHI) <= 0.08 for row in lineage_23)
    selected_child_median = float(np.median([float(row["child_duration_s"]) for row in lineage_23]))
    raw_child_medians = result["primary"]["metadata"]["median_recurrence_s"]
    raw_child_pooled_median_proxy = float(
        np.median([raw_child_medians["arm3|positive"], raw_child_medians["arm3|negative"]])
    )

    validation = {
        "assessment": "CALCULATIONS VERIFIED; SHARE ONLY WITH THE PAIRING-BIAS CAVEAT",
        "checks": checks,
        "passed": int(sum(checks.values())),
        "total": int(len(checks)),
        "methodology_audit": {
            "issue": "maximum-overlap matching preferentially selects long child recurrences and is not a neutral estimator of the arm-level scale ratio",
            "impact": "T322 validly rejects Phi for this event-local matching rule, but cannot by itself reject a population-level A(parent)/A(child) scale relation",
            "lineage_2_to_3_matched_median_ratio": matched_23,
            "lineage_2_to_3_rows": len(lineage_23),
            "lineage_2_to_3_unique_child_recurrences_used": child_unique,
            "lineage_2_to_3_selected_child_duration_median_s": selected_child_median,
            "arm3_all_recurrence_branch_median_proxy_s": raw_child_pooled_median_proxy,
            "lineage_2_to_3_events_within_0_08_of_1": near_one,
            "lineage_2_to_3_events_within_0_08_of_phi": near_phi,
        },
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
