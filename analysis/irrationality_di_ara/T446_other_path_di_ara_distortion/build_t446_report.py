from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


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


def sample_evenly(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    if len(frame) <= count:
        return frame.copy()
    indices = np.linspace(0, len(frame) - 1, count, dtype=int)
    return frame.iloc[indices].copy()


def main() -> None:
    result = json.loads((RESULTS / "T446_RESULT.json").read_text(encoding="utf-8"))
    path_draws = pd.read_csv(RESULTS / "T446_PATH_DRAWS.csv")
    transfer = pd.read_csv(RESULTS / "T446_TRANSFER_SUMMARY.csv")
    path_summary = pd.read_csv(RESULTS / "T446_PATH_SUMMARY.csv")
    central = pd.read_csv(RESULTS / "T446_CENTRAL_PATHS.csv")
    validation = json.loads((RESULTS / "T446_VALIDATION.json").read_text(encoding="utf-8"))
    generated_at = result["generated_at"]

    clean = transfer[transfer["holdout_pair"].isin(["AB", "AD"])].copy()
    selected_ad = clean[(clean["scenario"] == "selected_AC_-5.3d") & (clean["holdout_pair"] == "AD")].iloc[0]
    alternate_ad = clean[(clean["scenario"] == "alternate_AC_+7.9d") & (clean["holdout_pair"] == "AD")].iloc[0]
    headline = pd.DataFrame(
        [
            {
                "selected_terminal_ratio": selected_ad["distorted_to_straight_error_ratio_median"],
                "selected_terminal_improved_fraction": selected_ad["fraction_improved"],
                "selected_terminal_angle_reduction_deg": selected_ad["straight_angular_error_deg_median"] - selected_ad["distorted_angular_error_deg_median"],
                "alternate_terminal_ratio": alternate_ad["distorted_to_straight_error_ratio_median"],
                "validation_checks": validation["checks_passed"],
            }
        ]
    )

    path_metric_rows: list[dict] = []
    first = path_summary.iloc[0]
    path_metric_rows.append(
        {
            "path": "Known A/B",
            "scenario": "Known",
            "D": first["known_directness_D_median"],
            "G": first["known_turn_consistency_G_median"],
            "C": first["known_historical_circularity_C_median"],
            "signed_turn_deg": first["known_signed_net_turn_deg_median"],
        }
    )
    for _, row in path_summary.iterrows():
        label = "Other — selected AC" if row["scenario"] == "selected_AC_-5.3d" else "Other — alternate AC"
        path_metric_rows.append(
            {
                "path": label,
                "scenario": row["scenario"],
                "D": row["outcome_directness_D_median"],
                "G": row["outcome_turn_consistency_G_median"],
                "C": row["outcome_historical_circularity_C_median"],
                "signed_turn_deg": row["outcome_signed_net_turn_deg_median"],
            }
        )
    path_metrics = pd.DataFrame(path_metric_rows)

    transfer_display = clean[
        [
            "scenario",
            "holdout_pair",
            "holdout_role",
            "distortion_delta_deg_median",
            "distorted_to_straight_error_ratio_median",
            "fraction_improved",
            "straight_angular_error_deg_median",
            "distorted_angular_error_deg_median",
            "opposite_angular_error_deg_median",
        ]
    ].copy()
    transfer_display["scenario_label"] = transfer_display["scenario"].map(
        {"selected_AC_-5.3d": "Selected AC −5.3 d", "alternate_AC_+7.9d": "Alternate AC +7.9 d"}
    )
    transfer_display["holdout_label"] = transfer_display.apply(
        lambda row: f"{row['scenario_label']} — {row['holdout_pair']} ({'terminal' if row['holdout_pair'] == 'AD' else 'internal'})",
        axis=1,
    )
    transfer_display["scenario_order"] = transfer_display["scenario"].map(
        {"selected_AC_-5.3d": 1, "alternate_AC_+7.9d": 2}
    )
    transfer_display["pair_order"] = transfer_display["holdout_pair"].map({"AB": 1, "AD": 2})

    angular_rows: list[dict] = []
    for row in transfer_display.itertuples(index=False):
        for method, value in [
            ("Straight", row.straight_angular_error_deg_median),
            ("Transferred bend", row.distorted_angular_error_deg_median),
            ("Opposite bend", row.opposite_angular_error_deg_median),
        ]:
            angular_rows.append(
                {
                    "holdout_label": row.holdout_label,
                    "method": method,
                    "angular_error_deg": value,
                }
            )
    angular = pd.DataFrame(angular_rows)

    scatter_rows: list[pd.DataFrame] = []
    known = path_draws[path_draws["scenario"] == "selected_AC_-5.3d"][
        ["draw", "known_directness_D", "known_turn_consistency_G", "known_historical_circularity_C"]
    ].rename(
        columns={
            "known_directness_D": "D",
            "known_turn_consistency_G": "G",
            "known_historical_circularity_C": "C",
        }
    )
    known["path"] = "Known A/B"
    scatter_rows.append(sample_evenly(known, 100))
    for scenario, label in [
        ("selected_AC_-5.3d", "Other — selected AC"),
        ("alternate_AC_+7.9d", "Other — alternate AC"),
    ]:
        subset = path_draws[path_draws["scenario"] == scenario][
            ["draw", "outcome_directness_D", "outcome_turn_consistency_G", "outcome_historical_circularity_C"]
        ].rename(
            columns={
                "outcome_directness_D": "D",
                "outcome_turn_consistency_G": "G",
                "outcome_historical_circularity_C": "C",
            }
        )
        subset["path"] = label
        scatter_rows.append(sample_evenly(subset, 100))
    dg_scatter = pd.concat(scatter_rows, ignore_index=True)

    component_rows: list[dict] = []
    scenario_labels = {
        "known": "Known",
        "selected_AC_-5.3d": "Other selected AC",
        "alternate_AC_+7.9d": "Other alternate AC",
    }
    for row in central.itertuples(index=False):
        for component, value in [("A", row.A_arcsec2), ("B", row.B_arcsec2)]:
            component_rows.append(
                {
                    "relation": row.relation,
                    "point_order": row.point_order,
                    "series": f"{scenario_labels[row.scenario]} — {component}",
                    "component_value_arcsec2": value,
                }
            )
    component_histories = pd.DataFrame(component_rows)

    cards = [
        {
            "id": "selected_ratio",
            "description": "Terminal AD landing error after transferring the bend, divided by the straight-continuation error, using selected AC.",
            "dataset": "headline",
            "sourceId": "t446_transfer",
            "metrics": [{"label": "Selected-AC terminal ratio", "field": "selected_terminal_ratio", "format": "number"}],
        },
        {
            "id": "selected_fraction",
            "description": "Share of 2,000 local draws where the transferred bend improves terminal AD under selected AC.",
            "dataset": "headline",
            "sourceId": "t446_transfer",
            "metrics": [{"label": "Selected-AC draws improved", "field": "selected_terminal_improved_fraction", "format": "percent"}],
        },
        {
            "id": "angle_reduction",
            "description": "Median angular-error reduction for terminal AD under selected AC.",
            "dataset": "headline",
            "sourceId": "t446_transfer",
            "metrics": [{"label": "Terminal angle reduction", "field": "selected_terminal_angle_reduction_deg", "format": "number", "unit": "°"}],
        },
        {
            "id": "alternate_ratio",
            "description": "The same terminal ratio after shifting AC to its alternate reported +7.9 d solution.",
            "dataset": "headline",
            "sourceId": "t446_transfer",
            "metrics": [{"label": "Alternate-AC terminal ratio", "field": "alternate_terminal_ratio", "format": "number"}],
        },
    ]

    charts = [
        chart(
            "dg_plane",
            "Path directness and one-way turning consistency",
            "300 deterministic points sampled evenly from 2,000 correlated draws per path case; D=1 is direct and larger G means turns retain one handedness.",
            "scatter",
            "dg_scatter",
            "t446_path_draws",
            {
                "x": {"field": "D", "type": "quantitative", "label": "Directness D"},
                "y": {"field": "G", "type": "quantitative", "label": "Turn consistency G"},
                "color": {"field": "path", "type": "nominal", "label": "Path identity"},
                "tooltip": [
                    {"field": "draw", "type": "quantitative", "label": "Local draw"},
                    {"field": "C", "type": "quantitative", "label": "Historical circularity C"},
                ],
            },
        ),
        chart(
            "path_metrics",
            "Median path Irrationality Di-ARA metrics",
            "C=(1−D)G remains conservative: low G marks a kinked/cancelling path rather than a coherent circular arc.",
            "bar",
            "path_metrics_long",
            "t446_path",
            {
                "x": {"field": "path", "type": "nominal", "label": "Path case"},
                "y": {"field": "value", "type": "quantitative", "label": "Metric value (0–1)"},
                "color": {"field": "metric", "type": "nominal", "label": "D/G/C metric"},
            },
        ),
        chart(
            "error_ratio",
            "Transferred-bend landing error relative to straight continuation",
            "Values below 1 improve the held-out direction; AB is an internal interpolation, while AD is the terminal forward continuation.",
            "bar",
            "transfer",
            "t446_transfer",
            {
                "x": {"field": "holdout_label", "type": "nominal", "label": "AC solution and held-out relation"},
                "y": {"field": "distorted_to_straight_error_ratio_median", "type": "quantitative", "label": "Median distorted / straight error"},
                "color": {"field": "scenario_label", "type": "nominal", "label": "AC timing solution"},
                "tooltip": [
                    {"field": "fraction_improved", "type": "quantitative", "label": "Fraction improved"},
                    {"field": "distortion_delta_deg_median", "type": "quantitative", "label": "Median bend δ (°)"},
                ],
            },
        ),
        chart(
            "angular_error",
            "Angular error to the held-out outcome direction",
            "Straight, transferred-sign and opposite-sign controls are compared on identical Te-ARA residual lengths.",
            "bar",
            "angular",
            "t446_transfer",
            {
                "x": {"field": "holdout_label", "type": "nominal", "label": "AC solution and held-out relation"},
                "y": {"field": "angular_error_deg", "type": "quantitative", "label": "Median angular error (degrees)"},
                "color": {"field": "method", "type": "nominal", "label": "Direction construction"},
            },
        ),
        chart(
            "component_history",
            "A/B components across the child-ring order",
            "The x-axis is spatial relation order O→AC→AB→AD, not elapsed time; each series retains native arcsec² units.",
            "line",
            "component_histories",
            "t446_path",
            {
                "x": {"field": "relation", "type": "nominal", "label": "Spatial child relation order"},
                "y": {"field": "component_value_arcsec2", "type": "quantitative", "label": "A or B component (arcsec²)"},
                "color": {"field": "series", "type": "nominal", "label": "Path and component"},
                "tooltip": [{"field": "point_order", "type": "quantitative", "label": "Frozen spatial order"}],
            },
        ),
    ]

    tables = [
        {
            "id": "transfer_table",
            "title": "Held-out distortion-transfer summary",
            "subtitle": "Median results and draw-level improvement rates for both clean relations and both AC timing solutions.",
            "dataset": "transfer",
            "sourceId": "t446_transfer",
            "density": "spacious",
            "layout": "full",
            "defaultSort": {"field": "scenario_label", "direction": "asc"},
            "columns": [
                {"field": "scenario_label", "label": "AC solution"},
                {"field": "holdout_pair", "label": "Holdout"},
                {"field": "holdout_role", "label": "Topology"},
                {"field": "distortion_delta_deg_median", "label": "Bend δ (°)", "format": "number"},
                {"field": "distorted_to_straight_error_ratio_median", "label": "Error ratio", "format": "number"},
                {"field": "fraction_improved", "label": "Draws improved", "format": "percent"},
                {"field": "straight_angular_error_deg_median", "label": "Straight error (°)", "format": "number"},
                {"field": "distorted_angular_error_deg_median", "label": "Bent error (°)", "format": "number"},
            ],
        }
    ]

    sources = [
        {
            "id": "t446_path",
            "label": "T446 reviewed path-metric summary",
            "query": {
                "language": "sql",
                "engine": "SQLite",
                "sql": "SELECT * FROM path_summary ORDER BY scenario;",
                "description": "Validated T345 D/G/C summaries for the known and outcome-compatible spatial child-ring paths.",
                "executed_at": generated_at,
                "tables_used": ["path_summary", "central_paths"],
                "filters": ["one identity: WGD 2038−4008", "spatial order O→AC→AB→AD", "selected and alternate AC timing solutions"],
                "metric_definitions": [
                    "D is endpoint displacement divided by total open-path length.",
                    "G is absolute net signed turn divided by total absolute turn.",
                    "C=(1−D)G is conservative historical circularity, not proof of a Euclidean circle.",
                ],
            },
        },
        {
            "id": "t446_path_draws",
            "label": "T446 reviewed path-draw sample",
            "query": {
                "language": "sql",
                "engine": "SQLite",
                "sql": "SELECT draw, scenario, known_directness_D, known_turn_consistency_G, known_historical_circularity_C, outcome_directness_D, outcome_turn_consistency_G, outcome_historical_circularity_C FROM path_draws ORDER BY scenario, draw LIMIT 4000;",
                "description": "Correlated local draws used for the D/G plane; the report exposes a deterministic bounded sample.",
                "executed_at": generated_at,
                "tables_used": ["path_draws"],
                "filters": ["2,000 correlated local draws per AC scenario", "report scatter bounded to 100 deterministic points per displayed path case"],
            },
        },
        {
            "id": "t446_transfer",
            "label": "T446 reviewed held-out distortion transfer",
            "query": {
                "language": "sql",
                "engine": "SQLite",
                "sql": "SELECT * FROM transfer_summary ORDER BY scenario, CASE holdout_pair WHEN 'AC' THEN 1 WHEN 'AB' THEN 2 ELSE 3 END;",
                "description": "Validated leave-one-child-out bend and landing-error summaries.",
                "executed_at": generated_at,
                "tables_used": ["transfer_summary", "transfer_draws"],
                "filters": ["clean displayed holdouts AB and AD", "2,000 local draws", "selected AC −5.3 d and alternate AC +7.9 d"],
                "metric_definitions": [
                    "Error ratio is transferred-bend landing error divided by straight-continuation landing error; values below 1 improve direction reconstruction.",
                    "Fraction improved is the share of local draws with a lower transferred-bend landing error.",
                    "AD is terminal forward continuation; AB is internal-child interpolation because its removal joins non-adjacent AC and AD.",
                ],
            },
        },
        {
            "id": "t446_validation",
            "label": "T446 independent validation record",
            "query": {
                "language": "python",
                "engine": "Python",
                "description": "Independent 24-check recomputation of inputs, path metrics, topology, AC shift, transfer angles, summaries and output files.",
                "executed_at": generated_at,
                "tables_used": ["T446_VALIDATION.json"],
            },
        },
        {"id": "tdcosmo_ix", "label": "TDCOSMO IX pre-delay lens model", "href": "https://arxiv.org/abs/2202.11101"},
        {"id": "tdcosmo_xvi", "label": "TDCOSMO XVI time-delay measurement", "href": "https://arxiv.org/abs/2406.02683"},
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": "# T446 — Other-path Irrationality Di-ARA and distorted A/B continuation"},
        {
            "id": "summary",
            "type": "markdown",
            "sourceId": "t446_transfer",
            "body": "## The curvature transfer works for the forward continuation only under the selected AC solution\n\nThe corrected path test does recover a bend rather than merely an along/normal amount. For terminal AD, the selected AC solution gives a median bend of **22.9°**, cuts landing error to **0.593×** straight, and improves **73.2%** of 2,000 local draws; median angular error falls from **15.0° to 8.8°**. Shifting AC to its alternate reported +7.9 d solution changes the bend to **43.7°** and worsens landing to **1.901×** straight. The result is therefore promising but **AC-sign-sensitive, not confirmed**.",
        },
        {"id": "metrics", "type": "metric-strip", "cardIds": ["selected_ratio", "selected_fraction", "angle_reduction", "alternate_ratio"]},
        {
            "id": "anchor",
            "type": "markdown",
            "body": "## Exact relational anchor\n\n**Who/where:** the same WGD 2038−4008 lens and the same child relations as T445; no medium or identity changed. **What:** the unresolved Other section is tested with the original T345 path Irrationality Di-ARA—directness D, turn consistency G, and historical circularity C—then its bend is applied to the known A/B tangent. **When:** this cut is spatial reconstruction across child order `O → AC → AB → AD`, not elapsed time. **Why/how:** learn a bend from sibling children, hold one relation out, rotate its known tangent, and compare the landing with straight and opposite-sign controls.",
        },
        {
            "id": "path_result",
            "type": "markdown",
            "sourceId": "t446_path",
            "body": "## The Other path is more direct, but it is kinked rather than smoothly circular\n\nThe known path has median **D/G/C = 0.447/0.034/0.019**. The selected-AC Other has **0.631/0.062/0.022**; the alternate-AC Other has **0.715/0.227/0.064**. Thus the outcome-compatible path is more endpoint-directed, while low G shows that much of its curvature changes handedness and cancels. Calling it simply ‘straight’ or a clean circular arc would both discard the measured shape.",
        },
        {"id": "dg_block", "type": "chart", "chartId": "dg_plane", "layout": "full"},
        {
            "id": "dg_explain",
            "type": "markdown",
            "body": "The D/G plane separates three ideas that T445’s tangent/normal split could not: how directly the relation reaches its endpoint, whether successive turns keep one handedness, and how much conservative circular history survives both tests. The separated clouds confirm that the AC ambiguity changes the recovered shape, not merely one final coordinate.",
        },
        {"id": "metrics_block", "type": "chart", "chartId": "path_metrics", "layout": "full"},
        {
            "id": "continuation_result",
            "type": "markdown",
            "sourceId": "t446_transfer",
            "body": "## The forward child carries useful curvature under selected AC; the internal child does not\n\nAD is the only true forward continuation because `O → AC → AB` remains contiguous while AD is held out. Under selected AC, its transferred bend improves both landing distance and angle and beats the opposite-sign control in **99.65%** of draws. AB is different: removing it connects non-adjacent AC directly to AD, making it an internal interpolation. Its poor same-sign result is retained, but it is not treated as the same topology as terminal continuation.",
        },
        {"id": "error_block", "type": "chart", "chartId": "error_ratio", "layout": "full"},
        {
            "id": "error_explain",
            "type": "markdown",
            "body": "Read the dashed conceptual boundary at ratio 1: below it, the sibling-learned bend lands closer than the unbent path. The selected terminal bar is below 1; the alternate terminal bar rises well above it. That reversal is why the result cannot yet be promoted to a stable ARA recovery.",
        },
        {"id": "angle_block", "type": "chart", "chartId": "angular_error", "layout": "full"},
        {
            "id": "angle_explain",
            "type": "markdown",
            "body": "The opposite-sign control matters because a scalar curvature magnitude could look useful while its handedness is wrong. For selected terminal AD, the transferred sign gives **8.8°** median error versus **37.8°** for the opposite sign. The direction information is therefore non-trivial in that case, even though AC sensitivity prevents confirmation.",
        },
        {"id": "component_block", "type": "chart", "chartId": "component_history", "layout": "full"},
        {
            "id": "component_explain",
            "type": "markdown",
            "body": "This child-order view keeps A and B in native arcsec² and makes the scale boundary visible. It must not be read as a time series: it is the ordered spatial relation field used to obtain enough points for the path Di-ARA.",
        },
        {"id": "table_block", "type": "table", "tableId": "transfer_table", "layout": "full"},
        {
            "id": "definitions",
            "type": "markdown",
            "body": "## Definitions and comparison basis\n\n`D = endpoint displacement / total path length`. `G = |net signed turn| / total absolute turn`. `C = (1−D)G`. The bend δ is the wrapped difference between the sibling outcome turn and sibling known-path turn. The held-out step length and its forward/backward half-plane come from the Te-ARA residual; only its finer direction is reconstructed. Straight continuation is δ=0, and the opposite control uses −δ.",
        },
        {
            "id": "method",
            "type": "markdown",
            "body": "## Frozen design and topology audit\n\nThe identity, `O → AC → AB → AD` spatial order, T345 D/G/C equations, leave-one-child-out transfer, straight/opposite controls, 2,000 correlated T445 draws, and required AC ± timing sensitivity were frozen before calculation. The post-calculation topology audit did not rewrite that gate: it preserved the all-clean-pair result while separately labelling AD as terminal continuation and AB as internal interpolation.",
        },
        {
            "id": "validation_text",
            "type": "markdown",
            "sourceId": "t446_validation",
            "body": "## Independent validation passes 24 of 24 checks\n\nThe validator independently recovered the A→C→B→D astrometric order, recomputed D/G/C and the terminal bend, checked 6,000 input rows and 12,000 transfer rows, enforced held-out exclusion, verified unit directions and the exact 13.2-day AC sensitivity shift, reconciled summaries, checked topology labels, and confirmed both the selected improvement and alternate reversal.",
        },
        {
            "id": "limits",
            "type": "markdown",
            "body": "## What this does not establish\n\nThis is a spatial child-relation path, not chronological motion, one photon trajectory, a unique physical force, or a blind time-delay forecast. One individual pair has only one Other segment, so D=1 there is definitional and no turn is identifiable. Te-ARA supplies the residual length and forward/backward half-plane. The full TDCOSMO posterior is unavailable, so the uncertainty uses 2,000 correlated local approximations around published summaries. Most importantly, both clean transfer cuts depend on the unresolved AC sign.",
        },
        {
            "id": "next",
            "type": "markdown",
            "body": "## The next decisive test is more children or an independently fixed AC sign\n\nUse a lens with at least four non-origin child relations and fully resolved signed delays, then freeze a contiguous prefix, learn the path bend, and predict the next terminal child without using its residual direction. That would remove the current AC bottleneck and convert this from conditional curvature reconstruction toward a genuinely held-out directional forecast.",
        },
        {
            "id": "questions",
            "type": "markdown",
            "body": "## Further questions\n\n- Does the bend sign alternate across child parity, as the internal AB opposite-sign control hints, or is that only missing-node topology?\n- Does a better-sampled lens preserve the low-G kinked path or reveal a coherent curved child branch?\n- Can the held-out step’s half-plane also be inferred from pre-outcome geometry, removing the remaining Te-ARA directional input?",
        },
    ]

    path_metrics_long = path_metrics.melt(
        id_vars=["path", "scenario", "signed_turn_deg"],
        value_vars=["D", "G", "C"],
        var_name="metric",
        value_name="value",
    )
    datasets = {
        "headline": records(headline),
        "path_metrics_long": records(path_metrics_long),
        "dg_scatter": records(dg_scatter),
        "transfer": records(transfer_display),
        "angular": records(angular),
        "component_histories": records(component_histories),
    }
    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "T446 — Other-path Irrationality Di-ARA and distorted A/B continuation",
            "description": "A geometry-first test of whether the unresolved Other path supplies a bend that improves a known Te-ARA A/B continuation.",
            "generatedAt": generated_at,
            "cards": cards,
            "charts": charts,
            "tables": tables,
            "sources": sources,
            "blocks": blocks,
        },
        "snapshot": {"version": 1, "generatedAt": generated_at, "status": "ready", "datasets": datasets},
        "sources": sources,
    }
    (RESULTS / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(json.dumps({"artifact": str(RESULTS / "artifact.json"), "datasets": {key: len(value) for key, value in datasets.items()}}, indent=2))


if __name__ == "__main__":
    main()
