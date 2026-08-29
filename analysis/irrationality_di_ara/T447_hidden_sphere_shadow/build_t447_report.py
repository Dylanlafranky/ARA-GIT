from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def sample_evenly(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    if len(frame) <= count:
        return frame.copy()
    return frame.iloc[np.linspace(0, len(frame) - 1, count, dtype=int)].copy()


def chart(chart_id: str, title: str, subtitle: str, chart_type: str, dataset: str, source_id: str, encodings: dict) -> dict:
    return {
        "id": chart_id,
        "title": title,
        "subtitle": subtitle,
        "type": chart_type,
        "dataset": dataset,
        "sourceId": source_id,
        "layout": "full",
        "encodings": encodings,
    }


def main() -> None:
    result = json.loads((RESULTS / "T447_RESULT.json").read_text(encoding="utf-8"))
    validation = json.loads((RESULTS / "T447_VALIDATION.json").read_text(encoding="utf-8"))
    history = pd.read_csv(RESULTS / "T447_SOURCE_HISTORY_SAMPLE.csv")
    holdout = pd.read_csv(RESULTS / "T447_HOLDOUT_RECONSTRUCTION_SAMPLE.csv")
    metrics = pd.read_csv(RESULTS / "T447_METHOD_METRICS.csv")
    shuffle = pd.read_csv(RESULTS / "T447_SHUFFLED_THIRD_CONTROLS.csv")
    axis_scan = pd.read_csv(RESULTS / "T447_AXIS_SCAN.csv")
    phi = pd.read_csv(RESULTS / "T447_PHI_DIRECTION_REFERENCE.csv")

    raw_mae = result["primary"]["raw_three_cut"]["mae"]
    two_mae = result["primary"]["two_cut"]["mae"]
    shuffle_mae = result["primary"]["shuffled_third_mae_median"]
    headline = pd.DataFrame(
        [
            {
                "raw_three_cut_mae": raw_mae,
                "two_cut_mae": two_mae,
                "raw_vs_two_improvement": two_mae / raw_mae,
                "shuffled_third_median_mae": shuffle_mae,
                "raw_vs_shuffle_improvement": shuffle_mae / raw_mae,
                "validation_pass_fraction": validation["checks_passed"] / validation["checks_total"],
            }
        ]
    )
    with sqlite3.connect(RESULTS / "T447_ANALYSIS.sqlite") as connection:
        headline.to_sql("report_headline", connection, if_exists="replace", index=False)
        pd.DataFrame(
            [
                {
                    "checks_passed": validation["checks_passed"],
                    "checks_total": validation["checks_total"],
                    "all_passed": validation["all_passed"],
                }
            ]
        ).to_sql("validation_summary", connection, if_exists="replace", index=False)

    history_display = sample_evenly(history, 300)
    component_rows: list[dict] = []
    for row in history_display.itertuples(index=False):
        for component in ["w", "x", "y", "z"]:
            component_rows.append(
                {
                    "time_s": row.time_s,
                    "component": component,
                    "ara_coordinate": 1.0 + getattr(row, component),
                    "split": row.split,
                }
            )
    component_history = pd.DataFrame(component_rows)

    pair_shadow = sample_evenly(history, 600)[["time_s", "x_ARA", "y_ARA", "z_ARA", "split"]].copy()
    max_time = float(pair_shadow["time_s"].max())
    pair_shadow["time_band"] = pd.cut(
        pair_shadow["time_s"],
        bins=[-np.inf, max_time / 3, 2 * max_time / 3, np.inf],
        labels=["early", "middle", "late"],
    ).astype(str)

    radius_hidden = sample_evenly(holdout, 600)[["time_s", "shadow_radius_r3", "true_abs_hidden_w", "pred_three_independent", "pred_two_equal_split"]].copy()
    prediction_rows: list[dict] = []
    residual_rows: list[dict] = []
    for row in sample_evenly(holdout, 300).itertuples(index=False):
        for method, value, error in [
            ("true hidden |w|", row.true_abs_hidden_w, 0.0),
            ("three independent cuts", row.pred_three_independent, row.three_abs_error),
            ("two-cut equal split", row.pred_two_equal_split, row.two_abs_error),
        ]:
            prediction_rows.append({"time_s": row.time_s, "method": method, "hidden_magnitude": value})
            residual_rows.append({"time_s": row.time_s, "method": method, "absolute_error": error})
    predictions = pd.DataFrame(prediction_rows)
    residuals = pd.DataFrame(residual_rows)

    method_accuracy = metrics.copy()
    method_accuracy["accuracy_digits"] = -np.log10(np.maximum(method_accuracy["mae"], 1e-18))
    method_accuracy["method_short"] = method_accuracy["method"].map(
        {
            "three independent cuts (x,y,z)": "3 independent, normalized",
            "two cuts (x,y), equal hidden split": "2 cuts, equal split",
            "two cuts + redundant x−y": "2 cuts + redundant x−y",
            "three independent cuts, raw recorded values": "3 independent, as recorded",
        }
    )

    shuffle_sorted = shuffle.sort_values("mae").reset_index(drop=True)
    shuffle_sorted["percentile"] = (np.arange(len(shuffle_sorted)) + 1) / len(shuffle_sorted)
    shuffle_sorted["series"] = "shuffled z control"

    ranks = metrics[["method", "independent_rank"]].drop_duplicates().copy()
    ranks["method_short"] = ranks["method"].map(
        {
            "three independent cuts (x,y,z)": "x,y,z",
            "two cuts (x,y), equal hidden split": "x,y",
            "two cuts + redundant x−y": "x,y,x−y",
            "three independent cuts, raw recorded values": "x,y,z raw",
        }
    )

    boundary_rows: list[dict] = []
    for row in sample_evenly(holdout, 400).itertuples(index=False):
        boundary_rows.extend(
            [
                {"time_s": row.time_s, "series": "hidden w on ARA scale", "value": row.hidden_w_ARA},
                {"time_s": row.time_s, "series": "hidden ridge", "value": 1.0},
            ]
        )
    boundary_history = pd.DataFrame(boundary_rows)

    bins = np.arange(0, 361, 10)
    counts, edges = np.histogram(phi["xy_tangent_angle_deg"], bins=bins)
    phi_hist = pd.DataFrame(
        {
            "angle_bin_start_deg": edges[:-1].astype(int),
            "angle_bin_label": [f"{int(a)}–{int(b)}°" for a, b in zip(edges[:-1], edges[1:])],
            "sample_count": counts,
        }
    )

    framework_map = pd.DataFrame(
        [
            {"level": 1, "geometry": "2D ARA cut", "coordinates": "x,y", "what_is_visible": "one flat relation plane", "what_is_missing": "z and w remain joined"},
            {"level": 2, "geometry": "3D visible shadow", "coordinates": "x,y,z", "what_is_visible": "depth inside the projected parent", "what_is_missing": "mirror sign of w"},
            {"level": 3, "geometry": "Full parent S3 identity", "coordinates": "w,x,y,z", "what_is_visible": "complete orientation state", "what_is_missing": "nothing in this calibration identity"},
            {"level": 4, "geometry": "Chronological branch", "coordinates": "ordered states", "what_is_visible": "which mirror side is occupied", "what_is_missing": "unavailable if no boundary encounter"},
        ]
    )

    source_euroc = {
        "id": "euroc_source",
        "label": "EuRoC MH_01_easy ground-truth state stream",
        "href": "https://projects.asl.ethz.ch/datasets/euroc-mav/",
        "query": {
            "language": "sql",
            "engine": "SQLite",
            "sql": "SELECT time_s, split, w, x, y, z, 1+w AS w_ARA, 1+x AS x_ARA, 1+y AS y_ARA, 1+z AS z_ARA FROM source_states ORDER BY timestamp_ns;",
            "description": "Read 36,382 ordered ground-truth rows; select timestamp and q_RS_w/x/y/z; normalize each quaternion for the primary geometry calibration.",
            "executed_at": result["generated_at"],
            "tables_used": ["MH_01_easy/mav0/state_groundtruth_estimate0/data.csv"],
            "filters": ["one physical identity", "strict source order", "first 70% development", "last 30% chronological holdout"],
            "metric_definitions": ["Every row is one ground-truth orientation sample at approximately 200 Hz.", "ARA display maps signed quaternion component u to 1+u on a 0–2 axis."],
        },
    }
    source_reconstruction = {
        "id": "t447_reconstruction",
        "label": "T447 hidden-coordinate reconstruction",
        "query": {
            "language": "sql",
            "engine": "SQLite",
            "sql": "SELECT * FROM holdout_reconstruction ORDER BY timestamp_ns;",
            "description": "Untouched later 30% with hidden |w| reconstructed from three independent cuts and two-cut controls.",
            "executed_at": result["generated_at"],
            "tables_used": ["holdout_reconstruction", "method_metrics"],
            "filters": ["10,915 chronological holdout samples", "w hidden from the reconstruction formula", "normalized primary and raw-recorded sensitivity"],
            "metric_definitions": ["Three-cut prediction is sqrt(max(0,R^2-x^2-y^2-z^2)).", "Two-cut baseline divides the unresolved z^2+w^2 budget equally.", "MAE is mean absolute difference between predicted and recorded |w|."],
        },
    }
    source_controls = {
        "id": "t447_controls",
        "label": "T447 rank and shuffled-event controls",
        "query": {
            "language": "sql",
            "engine": "SQLite",
            "sql": "SELECT * FROM shuffled_third_controls ORDER BY draw;",
            "description": "Two hundred frozen-seed permutations preserve z values while breaking their event linkage; matrix rank tests redundant versus independent third cuts.",
            "executed_at": result["generated_at"],
            "tables_used": ["shuffled_third_controls", "method_metrics"],
            "filters": ["seed 44720260829", "200 holdout permutations", "no value resampling"],
        },
    }
    source_axis = {
        "id": "t447_axis_scan",
        "label": "T447 descriptive all-axis boundary scan",
        "query": {
            "language": "sql",
            "engine": "SQLite",
            "sql": "SELECT * FROM axis_scan ORDER BY CASE hidden_component WHEN 'w' THEN 1 WHEN 'x' THEN 2 WHEN 'y' THEN 3 ELSE 4 END;",
            "description": "Post-primary descriptive scan hiding each quaternion coordinate in turn; it does not replace the frozen w verdict.",
            "executed_at": result["generated_at"],
            "tables_used": ["axis_scan"],
        },
    }
    source_validation = {
        "id": "t447_validation",
        "label": "T447 independent validation record",
        "query": {
            "language": "sql",
            "engine": "SQLite",
            "sql": "SELECT checks_passed, checks_total, all_passed FROM validation_summary;",
            "description": "Independent 27-check recomputation covering source identity, time order, geometry, ranks, controls, sensitivities, branch identifiability and visual outputs.",
            "executed_at": result["generated_at"],
            "tables_used": ["T447_VALIDATION.json"],
        },
    }

    cards = [
        {
            "id": "raw_mae",
            "description": "Hidden |w| error using the source values exactly as recorded and a development-only radius.",
            "dataset": "headline",
            "sourceId": "t447_reconstruction",
            "metrics": [
                {"label": "As-recorded three-cut MAE", "field": "raw_three_cut_mae", "format": "number"},
                {"label": "More accurate than two cuts", "field": "raw_vs_two_improvement", "format": "number", "unit": "×"},
            ],
        },
        {
            "id": "two_mae",
            "description": "Error when only x and y are visible and the unresolved z²+w² budget is split equally.",
            "dataset": "headline",
            "sourceId": "t447_reconstruction",
            "metrics": [{"label": "Two-cut MAE", "field": "two_cut_mae", "format": "number"}],
        },
        {
            "id": "shuffle_mae",
            "description": "Median error after preserving every z value but assigning it to the wrong event time.",
            "dataset": "headline",
            "sourceId": "t447_controls",
            "metrics": [
                {"label": "Shuffled-third median MAE", "field": "shuffled_third_median_mae", "format": "number"},
                {"label": "Event-linked improvement", "field": "raw_vs_shuffle_improvement", "format": "number", "unit": "×"},
            ],
        },
        {
            "id": "validation",
            "description": "Independent checks of source grain, formulas, controls, ranks, outputs and interpretation boundary.",
            "dataset": "headline",
            "sourceId": "t447_validation",
            "metrics": [{"label": "Validation checks passed", "field": "validation_pass_fraction", "format": "percent"}],
        },
    ]

    charts = [
        chart("component_history", "Four orientation coordinates through recorded time", "Each signed component is mapped to the same 0–2 ARA display; 1 is its zero ridge.", "line", "component_history", "euroc_source", {"x": {"field": "time_s", "type": "quantitative", "label": "Time since first sample (seconds)"}, "y": {"field": "ara_coordinate", "type": "quantitative", "label": "Component ARA coordinate (0–2)"}, "color": {"field": "component", "type": "nominal", "label": "Quaternion component"}}),
        chart("xy_shadow", "x/y ordinary ARA shadow", "One two-axis projection of the same moving identity; colour separates broad time thirds.", "scatter", "pair_shadow", "euroc_source", {"x": {"field": "x_ARA", "type": "quantitative", "label": "x ARA coordinate (0–2)"}, "y": {"field": "y_ARA", "type": "quantitative", "label": "y ARA coordinate (0–2)"}, "color": {"field": "time_band", "type": "nominal", "label": "Recorded time band"}, "tooltip": [{"field": "time_s", "type": "quantitative", "label": "Time (s)"}]}),
        chart("xz_shadow", "x/z ordinary ARA shadow", "A perpendicular two-axis view changes the visible curve without changing the identity.", "scatter", "pair_shadow", "euroc_source", {"x": {"field": "x_ARA", "type": "quantitative", "label": "x ARA coordinate (0–2)"}, "y": {"field": "z_ARA", "type": "quantitative", "label": "z ARA coordinate (0–2)"}, "color": {"field": "time_band", "type": "nominal", "label": "Recorded time band"}}),
        chart("yz_shadow", "y/z ordinary ARA shadow", "The third pair plane supplies another shadow of the same parent trajectory.", "scatter", "pair_shadow", "euroc_source", {"x": {"field": "y_ARA", "type": "quantitative", "label": "y ARA coordinate (0–2)"}, "y": {"field": "z_ARA", "type": "quantitative", "label": "z ARA coordinate (0–2)"}, "color": {"field": "time_band", "type": "nominal", "label": "Recorded time band"}}),
        chart("radius_hidden", "Visible shadow radius against hidden depth", "For the known S3 calibration, moving outward in the visible shadow leaves less hidden w depth.", "scatter", "radius_hidden", "t447_reconstruction", {"x": {"field": "shadow_radius_r3", "type": "quantitative", "label": "Visible shadow radius r3"}, "y": {"field": "true_abs_hidden_w", "type": "quantitative", "label": "Recorded hidden magnitude |w|"}, "tooltip": [{"field": "time_s", "type": "quantitative", "label": "Time (s)"}]}),
        chart("prediction_history", "Hidden depth through the untouched holdout", "The event-linked three-cut reconstruction lies on the recorded path; the two-cut guess remains displaced.", "line", "predictions", "t447_reconstruction", {"x": {"field": "time_s", "type": "quantitative", "label": "Recorded holdout time (seconds)"}, "y": {"field": "hidden_magnitude", "type": "quantitative", "label": "Hidden distance from ridge |w|"}, "color": {"field": "method", "type": "nominal", "label": "Observed or reconstructed series"}}),
        chart("residual_history", "Reconstruction error through holdout time", "The three-cut residual stays at numerical precision; the two-cut residual changes with the omitted z relation.", "line", "residuals", "t447_reconstruction", {"x": {"field": "time_s", "type": "quantitative", "label": "Recorded holdout time (seconds)"}, "y": {"field": "absolute_error", "type": "quantitative", "label": "Absolute hidden-magnitude error"}, "color": {"field": "method", "type": "nominal", "label": "Method"}}),
        chart("method_accuracy", "Accuracy supplied by each available cut", "Correct decimal orders are −log10(MAE); a redundant difference remains rank two.", "bar", "method_accuracy", "t447_reconstruction", {"x": {"field": "method_short", "type": "nominal", "label": "Visible information"}, "y": {"field": "accuracy_digits", "type": "quantitative", "label": "Correct decimal orders"}, "tooltip": [{"field": "mae", "type": "quantitative", "label": "MAE"}, {"field": "independent_rank", "type": "quantitative", "label": "Independent rank"}]}),
        chart("shuffle_ecdf", "Shuffled-third error distribution", "Every control keeps the correct z values but attaches them to the wrong moments.", "line", "shuffle_ecdf", "t447_controls", {"x": {"field": "mae", "type": "quantitative", "label": "Hidden |w| MAE"}, "y": {"field": "percentile", "type": "quantitative", "label": "Cumulative share of 200 controls"}}),
        chart("rank_comparison", "Independent information rank", "x−y is calculated from existing cuts and therefore does not create a third direction.", "bar", "ranks", "t447_controls", {"x": {"field": "method_short", "type": "nominal", "label": "Visible coordinate set"}, "y": {"field": "independent_rank", "type": "quantitative", "label": "Matrix rank"}}),
        chart("axis_boundary", "Boundary exposure when each coordinate is hidden", "The primary w view has no crossing; exploratory x and z views reach their projection boundaries.", "bar", "axis_scan", "t447_axis_scan", {"x": {"field": "hidden_component", "type": "nominal", "label": "Hidden coordinate"}, "y": {"field": "maximum_shadow_radius", "type": "quantitative", "label": "Maximum visible shadow radius"}, "tooltip": [{"field": "source_sign_changes", "type": "quantitative", "label": "Hidden sign crossings"}, {"field": "minimum_abs_hidden", "type": "quantitative", "label": "Minimum |hidden|"}]}),
        chart("branch_history", "Primary hidden w branch against its ridge", "The recorded path remains above the w=0 ridge throughout the holdout, so branch switching is not identifiable here.", "line", "boundary_history", "t447_reconstruction", {"x": {"field": "time_s", "type": "quantitative", "label": "Recorded holdout time (seconds)"}, "y": {"field": "value", "type": "quantitative", "label": "Hidden w ARA coordinate (0–2)"}, "color": {"field": "series", "type": "nominal", "label": "Hidden coordinate and ridge"}}),
        chart("phi_reference", "x/y tangent-angle distribution", "The archived 36°/Phi direction is a visible reference only; these component axes are not Mapping/Rung axes.", "bar", "phi_hist", "euroc_source", {"x": {"field": "angle_bin_label", "type": "nominal", "label": "x/y tangent-angle bin"}, "y": {"field": "sample_count", "type": "quantitative", "label": "Sample count"}}),
    ]

    tables = [
        {
            "id": "framework_table",
            "title": "Relational address inside the ARA framework",
            "subtitle": "Each row adds one type of information without renaming the lower-scale cut.",
            "dataset": "framework_map",
            "sourceId": "t447_reconstruction",
            "density": "spacious",
            "layout": "full",
            "defaultSort": {"field": "level", "direction": "asc"},
            "columns": [
                {"field": "level", "label": "Step", "format": "number"},
                {"field": "geometry", "label": "Geometry"},
                {"field": "coordinates", "label": "Coordinates"},
                {"field": "what_is_visible", "label": "What becomes visible"},
                {"field": "what_is_missing", "label": "What remains unresolved"},
            ],
        },
        {
            "id": "axis_table",
            "title": "Primary and exploratory hidden-axis scan",
            "subtitle": "Sign changes are boundary encounters; only w is the frozen primary coordinate in T447.",
            "dataset": "axis_scan",
            "sourceId": "t447_axis_scan",
            "density": "spacious",
            "layout": "full",
            "defaultSort": {"field": "hidden_component", "direction": "asc"},
            "columns": [
                {"field": "hidden_component", "label": "Hidden coordinate"},
                {"field": "visible_components", "label": "Visible shadow"},
                {"field": "source_sign_changes", "label": "Sign crossings", "format": "number"},
                {"field": "minimum_abs_hidden", "label": "Minimum |hidden|", "format": "number"},
                {"field": "maximum_shadow_radius", "label": "Maximum shadow radius", "format": "number"},
                {"field": "primary_or_exploratory", "label": "Status"},
            ],
        },
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": "# T447 — Recovering a hidden larger geometry from its shadow"},
        {"id": "technical_summary", "type": "markdown", "sourceId": "t447_reconstruction", "body": "## Three independent cuts recover hidden depth; the primary branch crossing remains unobserved\n\nOn the untouched later 30% of a real motion-capture trajectory, `(x,y,z)` recovered hidden `|w|` to **1.75×10⁻⁶ MAE on the values exactly as recorded** and to floating-point precision after the unit-quaternion normalization required by the known geometry. The two-cut estimate missed by **0.1443**, while a shuffled event-level third cut missed by **0.02859**. The architecture works, but this flight never reached the primary `w=0` ridge, so it does not yet test chronological branch switching or prove that physical time is `w`."},
        {"id": "headline_metrics", "type": "metric-strip", "cardIds": ["raw_mae", "two_mae", "shuffle_mae", "validation"]},
        {"id": "address", "type": "markdown", "body": "## Exact test address\n\n**Who:** one EuRoC `MH_01_easy` drone identity. **What:** hide quaternion `w` and compare two cuts, two cuts plus redundant `x−y`, and three independent cuts. **When:** first 70% development, later 30% untouched holdout, with recorded order preserved. **Where:** 2D ARA planes sit inside the visible `(x,y,z)` shadow of the full `(w,x,y,z)` parent. **Why/how:** test whether a real third direction recovers hidden depth and whether time order can select a mirror branch."},
        {"id": "history_result", "type": "markdown", "body": "## The identity moves through a narrow but structured part of the parent geometry\n\nThe four lines below are not four separate objects. They are four coordinates of one moving orientation identity, all placed on the same 0–2 display. Their different histories show why one perpendicular cut cannot stand in for the full parent."},
        {"id": "history_chart", "type": "chart", "chartId": "component_history", "layout": "full"},
        {"id": "planes_result", "type": "markdown", "body": "## Perpendicular ARA cuts show different curves of the same trajectory\n\nThe x/y, x/z and y/z planes look different because each omits different depth. Their agreement is relational rather than pictorial: the same timestamped state supplies every point."},
        {"id": "xy_chart", "type": "chart", "chartId": "xy_shadow", "layout": "full"},
        {"id": "xz_chart", "type": "chart", "chartId": "xz_shadow", "layout": "full"},
        {"id": "yz_chart", "type": "chart", "chartId": "yz_shadow", "layout": "full"},
        {"id": "depth_result", "type": "markdown", "sourceId": "t447_reconstruction", "body": "## The visible radius acts as the shadow of hidden depth\n\nIn this known S3 identity, moving outward in `(x,y,z)` necessarily leaves less distance in `w`. This is the clean geometric example of the effect we were looking for: the larger geometry is not directly drawn in the lower cut, but its boundary restricts every lower-cut point."},
        {"id": "radius_chart", "type": "chart", "chartId": "radius_hidden", "layout": "full"},
        {"id": "prediction_chart", "type": "chart", "chartId": "prediction_history", "layout": "full"},
        {"id": "prediction_explain", "type": "markdown", "body": "The black truth and three-cut reconstruction coincide across the later holdout. The two-cut estimate remains near 0.4 because x and y reveal only the combined hidden budget `z²+w²`; they cannot say how that budget is split."},
        {"id": "residual_chart", "type": "chart", "chartId": "residual_history", "layout": "full"},
        {"id": "controls_result", "type": "markdown", "sourceId": "t447_controls", "body": "## A derived third coordinate is not a third cut, and correct values need correct event linkage\n\nThe rank remains **2** for `(x,y,x−y)` because the third column is computed from the first two. Rank becomes **3** only with independent z. Shuffling z preserves every observed z value but destroys its connection to the matching x/y state, raising median MAE to **0.02859**."},
        {"id": "accuracy_chart", "type": "chart", "chartId": "method_accuracy", "layout": "full"},
        {"id": "rank_chart", "type": "chart", "chartId": "rank_comparison", "layout": "full"},
        {"id": "shuffle_chart", "type": "chart", "chartId": "shuffle_ecdf", "layout": "full"},
        {"id": "edge_result", "type": "markdown", "sourceId": "t447_axis_scan", "body": "## The primary w view approaches the edge but never crosses it\n\nAcross the complete flight, the visible shadow reached radius **0.985553**, while the smallest `|w|` was **0.169368**. There were no w sign changes. We can therefore recover distance from the hidden ridge but cannot honestly score branch selection in this primary view. The all-axis scan is exploratory: x crosses 4 times and z crosses 15 times, making z the clean frozen follow-up."},
        {"id": "branch_chart", "type": "chart", "chartId": "branch_history", "layout": "full"},
        {"id": "axis_chart", "type": "chart", "chartId": "axis_boundary", "layout": "full"},
        {"id": "axis_table_block", "type": "table", "tableId": "axis_table", "layout": "full"},
        {"id": "framework_result", "type": "markdown", "body": "## WHERE and HOW it fits into ARA\n\nA two-axis ARA remains a valid flat cut. The independent third cut expands it into a visible 3D shadow; the fourth coordinate is depth relative to the larger parent identity. The visible outer edge is the hidden coordinate's ridge. Recorded history is not needed for hidden magnitude, but it becomes necessary to distinguish `+|w|` from `−|w|` when the path encounters that ridge."},
        {"id": "framework_table_block", "type": "table", "tableId": "framework_table", "layout": "full"},
        {"id": "phi_result", "type": "markdown", "body": "## The old Phi/up-right direction remains a reference, not a recovered invariant\n\nThe 36° direction was not used to orient or fit this dataset. Quaternion x/y axes are not the archived Mapping/Rung axes, so the angle distribution below cannot validate or reject a universal Phi direction. Its job is to keep the old hypothesis visibly separated from what T447 actually measured."},
        {"id": "phi_chart", "type": "chart", "chartId": "phi_reference", "layout": "full"},
        {"id": "scope", "type": "markdown", "body": "## Scope, data and metric definitions\n\nThe source contains **36,382** ordered orientation states over **181.905 seconds**, at a median **0.005-second** interval. The hidden magnitude formula is `sqrt(max(0,R²−x²−y²−z²))`, with R fixed from development data. The normalized result is a geometry calibration; the as-recorded sensitivity carries the dataset's actual rounding and measurement precision. MAE is averaged over **10,915** untouched later samples."},
        {"id": "method", "type": "markdown", "body": "## Frozen method\n\nThe identity, hidden w coordinate, 70/30 chronological split, three-cut equation, two-cut equal-split baseline, redundant difference, 200 shuffled-z controls, branch rule, and interpretation limits were frozen before calculation. Source viability then added an explicitly labelled raw-recorded sensitivity and an exploratory all-axis scan; neither replaces the primary w verdict."},
        {"id": "validation_result", "type": "markdown", "sourceId": "t447_validation", "body": "## Independent validation passes 27 of 27 checks\n\nThe validator independently checked source columns, SHA-256, 36,382-row grain, strict timestamps, quaternion norms and continuity, the three- and two-cut formulas, matrix ranks, redundant equality, 200 controls, raw sensitivity, all-axis sign crossings, sample traceability and both geometry-first figures."},
        {"id": "limits", "type": "markdown", "body": "## What this result does not establish\n\nThis test does not show that physical time literally equals quaternion w, that every ARA identity is a mathematical S3, or that the 36°/Phi direction is universal. The three-cut normalized recovery is expected from the known quaternion constraint. Most importantly, this primary trajectory stays on one w branch, so the history-based mirror selection remains untested rather than failed."},
        {"id": "next", "type": "markdown", "body": "## Next: freeze z as hidden and test real branch handovers\n\nKeep the same physical identity and data source, hide z before calculation, seed one starting sign, and use only visible `(w,x,y)` plus chronological boundary encounters to predict the 15 recorded z crossings. Compare exact crossing order and timing with shuffled-time and reflected-branch controls."},
        {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Does the frozen branch rule recover z crossings without reading held-out z?\n- Do the 4 x crossings and 15 z crossings form nested child/parent handovers or only coordinate rotations?\n- After calibration, which real spacetime dataset supplies three independently measured cuts rather than a known quaternion identity?"},
    ]

    sources = [source_euroc, source_reconstruction, source_controls, source_axis, source_validation]
    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "T447 — Recovering a hidden larger geometry from its shadow",
            "description": "A real-data calibration of two cuts, a redundant third, three independent cuts, hidden depth, projection boundaries and chronological branch identifiability.",
            "generatedAt": result["generated_at"],
            "cards": cards,
            "charts": charts,
            "tables": tables,
            "sources": sources,
            "blocks": blocks,
        },
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": result["generated_at"],
            "datasets": {
                "headline": records(headline),
                "component_history": records(component_history),
                "pair_shadow": records(pair_shadow),
                "radius_hidden": records(radius_hidden),
                "predictions": records(predictions),
                "residuals": records(residuals),
                "method_accuracy": records(method_accuracy),
                "shuffle_ecdf": records(shuffle_sorted),
                "ranks": records(ranks),
                "axis_scan": records(axis_scan),
                "boundary_history": records(boundary_history),
                "phi_hist": records(phi_hist),
                "framework_map": records(framework_map),
            },
        },
        "sources": sources,
    }
    (RESULTS / "artifact.json").write_text(json.dumps(artifact, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"datasets": {k: len(v) for k, v in artifact["snapshot"]["datasets"].items()}, "charts": len(charts), "blocks": len(blocks)}, indent=2))


if __name__ == "__main__":
    main()
