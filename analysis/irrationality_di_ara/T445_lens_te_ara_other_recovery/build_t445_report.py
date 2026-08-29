from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def chart(chart_id, title, subtitle, chart_type, dataset, encodings):
    return {
        "id": chart_id,
        "title": title,
        "subtitle": subtitle,
        "type": chart_type,
        "dataset": dataset,
        "sourceId": "t445_analysis",
        "layout": "full",
        "encodings": encodings,
    }


def main() -> None:
    summary = json.loads((RESULTS / "T445_SUMMARY.json").read_text(encoding="utf-8"))
    decomposition = pd.read_csv(RESULTS / "T445_DECOMPOSITION.csv")
    paths = pd.read_csv(RESULTS / "T445_CONTROLLED_PATH.csv")
    source_lock = pd.read_csv(RESULTS / "T445_SOURCE_LOCK.csv")
    uncertainty = pd.read_csv(RESULTS / "T445_UNCERTAINTY_SUMMARY.csv")
    global_fit = pd.read_csv(RESULTS / "T445_GLOBAL_CLEAN_FIT.csv")
    generated_at = summary["generated_at"]

    global_values = dict(zip(global_fit["measurement"], global_fit["value"]))
    clean = decomposition[decomposition["pair"].isin(["AB", "AD"])].copy()
    headline = pd.DataFrame(
        [
            {
                "source_rms_mas": 1000 * summary["quality"]["source_rms_arcsec"],
                "blind_delay_pairs": 2,
                "outside_path": int((~clean["within_fitted_shear_path"]).sum()),
                "shared_lambda": global_values["shared_lambda_fit"],
                "shared_lambda_p": global_values["shared_lambda_p_value"],
                "mean_parallel_percent": 100 * clean["parallel_fraction"].mean(),
                "mean_normal_percent": 100 * clean["perpendicular_fraction"].mean(),
            }
        ]
    )

    delay_rows = []
    for row in decomposition.itertuples(index=False):
        for series, value in [
            ("pre-delay reconstruction", row.model_delay_days),
            ("published pre-delay prediction", row.published_prediction_days),
            ("later observed delay", row.observed_delay_days),
        ]:
            delay_rows.append(
                {
                    "pair": row.pair,
                    "blind_status": row.blind_status,
                    "series": series,
                    "delay_days": value,
                    "observed_sigma_days": row.observed_delay_sigma_days,
                }
            )
    delays = pd.DataFrame(delay_rows)

    lambda_rows = []
    for row in decomposition.itertuples(index=False):
        lambda_rows.extend(
            [
                {"pair": row.pair, "series": "fitted shear endpoint", "lambda": 1.0, "blind_status": row.blind_status},
                {"pair": row.pair, "series": "outcome-required", "lambda": row.total_match_lambda, "blind_status": row.blind_status},
            ]
        )
    lambda_frame = pd.DataFrame(lambda_rows)

    native_rows = []
    for row in decomposition.itertuples(index=False):
        for component, value in [
            ("geometric A / traversal", row.geometric_a_arcsec2),
            ("model potential B / connection", row.potential_b_arcsec2),
            ("Te-ARA solved B_eff", row.observed_required_b_arcsec2),
            ("model total", row.model_total_dphi_arcsec2),
            ("observed-required total", row.observed_dphi_arcsec2),
        ]:
            native_rows.append({"pair": row.pair, "component": component, "fermat_arcsec2": value, "blind_status": row.blind_status})
    native = pd.DataFrame(native_rows)

    ara_rows = []
    other_rows = []
    for row in decomposition.itertuples(index=False):
        ara_rows.extend(
            [
                {
                    "pair": row.pair,
                    "point": "pre-delay fitted",
                    "traversal_ara": row.model_traversal_ara,
                    "connection_ara": row.model_connection_ara,
                    "blind_status": row.blind_status,
                },
                {
                    "pair": row.pair,
                    "point": "later outcome required",
                    "traversal_ara": row.observed_traversal_ara,
                    "connection_ara": row.observed_connection_ara,
                    "blind_status": row.blind_status,
                },
            ]
        )
        other_rows.extend(
            [
                {
                    "pair": row.pair,
                    "other_component": "along known line / movement",
                    "ara_coordinate": row.other_movement_ara,
                    "native_residual_arcsec2": row.parallel_residual_arcsec2,
                    "blind_status": row.blind_status,
                },
                {
                    "pair": row.pair,
                    "other_component": "normal to line / curvature",
                    "ara_coordinate": row.other_connection_ara,
                    "native_residual_arcsec2": row.perpendicular_residual_arcsec2,
                    "blind_status": row.blind_status,
                },
            ]
        )
    ara = pd.DataFrame(ara_rows)
    other = pd.DataFrame(other_rows)

    source_mean_x = source_lock["source_x_arcsec"].mean()
    source_mean_y = source_lock["source_y_arcsec"].mean()
    source_offsets = source_lock.assign(
        source_dx_mas=1000 * (source_lock["source_x_arcsec"] - source_mean_x),
        source_dy_mas=1000 * (source_lock["source_y_arcsec"] - source_mean_y),
    )
    path_only = paths[paths["point_type"] == "path"].sort_values(["pair", "lambda"]).copy()

    detail_columns = [
        "pair",
        "blind_status",
        "model_delay_days",
        "observed_delay_days",
        "observed_delay_sigma_days",
        "total_match_lambda",
        "parallel_fraction",
        "perpendicular_fraction",
        "other_movement_ara",
        "other_connection_ara",
    ]
    detail = decomposition[detail_columns].copy()
    detail["parallel_percent"] = 100 * detail.pop("parallel_fraction")
    detail["perpendicular_percent"] = 100 * detail.pop("perpendicular_fraction")

    sources = [
        {
            "id": "t445_analysis",
            "label": "T445 reviewed SQLite outputs from WGD 2038−4008",
            "href": "https://github.com/TDCOSMO/WGD2038-4008",
            "query": {
                "language": "sql",
                "engine": "SQLite",
                "sql": "SELECT * FROM decomposition ORDER BY CASE pair WHEN 'AB' THEN 1 WHEN 'AC' THEN 2 ELSE 3 END;",
                "description": "Report-input query over the independently validated T445 decomposition table.",
                "executed_at": generated_at,
                "tables_used": ["decomposition", "controlled_path", "source_lock", "global_clean_fit"],
                "filters": [
                    "one fixed identity: WGD 2038−4008",
                    "clean primary outcomes: AB and AD",
                    "AC retained but labelled model-informed sign",
                    "external cosmology fixed at H0=70 km/s/Mpc and Omega_m=0.3",
                ],
                "metric_definitions": [
                    "A is the delay-blind geometric Fermat contribution; B is the lens-potential contribution.",
                    "B_eff is solved by Te-ARA as observed differential Fermat potential minus A.",
                    "Lambda scales only the named external-shear component from absent (0) to fitted (1); it is not time.",
                    "Parallel/normal shares are conditional on holding A fixed in the Te-ARA solve; their 0–2 normalization is secondary to native arcsec².",
                ],
            },
        },
        {"id": "tdcosmo_ix", "label": "TDCOSMO IX pre-delay lens model", "href": "https://arxiv.org/abs/2202.11101"},
        {"id": "tdcosmo_xvi", "label": "TDCOSMO XVI later time-delay measurement", "href": "https://arxiv.org/abs/2406.02683"},
        {"id": "gaia_gral_x", "label": "Gaia GraL X component astrometry", "href": "https://cdsarc.cds.unistra.fr/viz-bin/cat/J/A+A/707/A345"},
    ]

    cards = [
        {"id": "source_lock", "description": "RMS separation of the four independently back-projected source locations.", "dataset": "headline", "sourceId": "t445_analysis", "metrics": [{"label": "Source lock RMS", "field": "source_rms_mas", "format": "number", "unit": "mas"}]},
        {"id": "outside", "description": "Clean blind outcomes lying outside the 0≤λ≤1 named shear path.", "dataset": "headline", "sourceId": "t445_analysis", "metrics": [{"label": "Beyond known path", "field": "outside_path", "format": "number", "unit": "/ 2"}]},
        {"id": "shared_lambda", "description": "Best one-coordinate shear scaling fitted jointly to AB and AD.", "dataset": "headline", "sourceId": "t445_analysis", "metrics": [{"label": "Shared λ", "field": "shared_lambda", "format": "number"}]},
        {"id": "shared_p", "description": "Observational-covariance-only compatibility of a single shared shear scaling.", "dataset": "headline", "sourceId": "t445_analysis", "metrics": [{"label": "Shared-λ p", "field": "shared_lambda_p", "format": "number"}]},
        {"id": "along", "description": "Mean conditional residual share aligned with the known coupling line for clean pairs.", "dataset": "headline", "sourceId": "t445_analysis", "metrics": [{"label": "Along-line share", "field": "mean_parallel_percent", "format": "number", "unit": "%"}]},
        {"id": "normal", "description": "Mean conditional residual share normal to the known coupling line for clean pairs.", "dataset": "headline", "sourceId": "t445_analysis", "metrics": [{"label": "Normal share", "field": "mean_normal_percent", "format": "number", "unit": "%"}]},
    ]

    charts = [
        chart(
            "source_lock_chart",
            "Four image paths lock to one source",
            "Offsets are in milliarcseconds around the recovered source mean; labels use TDCOSMO component identities.",
            "scatter",
            "source_offsets",
            {
                "x": {"field": "source_dx_mas", "type": "quantitative", "label": "Source x offset (mas)"},
                "y": {"field": "source_dy_mas", "type": "quantitative", "label": "Source y offset (mas)"},
                "color": {"field": "tdcosmo_component", "type": "nominal", "label": "Back-projected image"},
                "tooltip": [
                    {"field": "gaia_component", "type": "nominal", "label": "Gaia label"},
                    {"field": "source_offset_mas", "type": "quantitative", "label": "Radial offset (mas)"},
                ],
            },
        ),
        chart(
            "delay_bridge",
            "Pre-delay geometry reproduces the published blind model",
            "The later observation was not used to fit the lens; AC is shown but is not a clean blind sign test.",
            "bar",
            "delays",
            {
                "x": {"field": "pair", "type": "nominal", "label": "TDCOSMO image pair"},
                "y": {"field": "delay_days", "type": "quantitative", "label": "Signed delay (days)"},
                "color": {"field": "series", "type": "nominal", "label": "Measurement stage"},
                "tooltip": [
                    {"field": "blind_status", "type": "nominal", "label": "Blind status"},
                    {"field": "observed_sigma_days", "type": "quantitative", "label": "Observed σ (days)"},
                ],
            },
        ),
        chart(
            "native_path",
            "Known external shear traces a straight A/B relation",
            "λ is a controlled coupling amplitude, not time. Each line runs from no shear to the fitted shear.",
            "line",
            "path_only",
            {
                "x": {"field": "geometric_a_arcsec2", "type": "quantitative", "label": "Geometric A / traversal (arcsec²)"},
                "y": {"field": "potential_b_arcsec2", "type": "quantitative", "label": "Potential B / connection (arcsec²)"},
                "color": {"field": "pair", "type": "nominal", "label": "Image pair"},
                "tooltip": [
                    {"field": "lambda", "type": "quantitative", "label": "Shear λ"},
                    {"field": "total_dphi_arcsec2", "type": "quantitative", "label": "A+B (arcsec²)"},
                ],
            },
        ),
        chart(
            "lambda_required",
            "The clean outcomes lie beyond—and disagree along—the known path",
            "The fitted named coupling ends at λ=1. AB requires 11.47 and AD 2.54; a shared λ=1.51 fits poorly at the 5% boundary under observation-only covariance.",
            "bar",
            "lambda_required",
            {
                "x": {"field": "pair", "type": "nominal", "label": "TDCOSMO image pair"},
                "y": {"field": "lambda", "type": "quantitative", "label": "Coupling coordinate λ"},
                "color": {"field": "series", "type": "nominal", "label": "Endpoint"},
                "tooltip": [{"field": "blind_status", "type": "nominal", "label": "Blind status"}],
            },
        ),
        chart(
            "native_decomposition",
            "Te-ARA solves the missing Phase-B amount in native units",
            "A is frozen from delay-blind geometry. B_eff is the potential-side amount required by the later delay.",
            "bar",
            "native",
            {
                "x": {"field": "pair", "type": "nominal", "label": "TDCOSMO image pair"},
                "y": {"field": "fermat_arcsec2", "type": "quantitative", "label": "Differential Fermat potential (arcsec²)"},
                "color": {"field": "component", "type": "nominal", "label": "Term"},
                "tooltip": [{"field": "blind_status", "type": "nominal", "label": "Blind status"}],
            },
        ),
        chart(
            "ara_pair",
            "The same fitted and outcome-required relations on the ARA 0–2 plane",
            "Each point is a contribution share with x+y=2 by definition; location along the ridge is informative, not the ridge itself.",
            "scatter",
            "ara",
            {
                "x": {"field": "traversal_ara", "type": "quantitative", "label": "Traversal share ARA (0–2)"},
                "y": {"field": "connection_ara", "type": "quantitative", "label": "Connection share ARA (0–2)"},
                "color": {"field": "point", "type": "nominal", "label": "Stage"},
                "tooltip": [
                    {"field": "pair", "type": "nominal", "label": "Pair"},
                    {"field": "blind_status", "type": "nominal", "label": "Blind status"},
                ],
            },
        ),
        chart(
            "other_split",
            "Conditional coarse Other is movement-heavy, with a smaller normal remainder",
            "This 0–2 split is conditional on Te-ARA holding A fixed; it does not independently identify a new physical identity.",
            "bar",
            "other",
            {
                "x": {"field": "pair", "type": "nominal", "label": "TDCOSMO image pair"},
                "y": {"field": "ara_coordinate", "type": "quantitative", "label": "Conditional Other ARA (0–2)"},
                "color": {"field": "other_component", "type": "nominal", "label": "Residual direction"},
                "tooltip": [
                    {"field": "native_residual_arcsec2", "type": "quantitative", "label": "Signed residual (arcsec²)"},
                    {"field": "blind_status", "type": "nominal", "label": "Blind status"},
                ],
            },
        ),
    ]

    tables = [
        {
            "id": "detail_table",
            "title": "Pair-level native results and conditional residual shares",
            "subtitle": "AB and AD are the clean blind outcomes; AC is retained as a labelled diagnostic only.",
            "dataset": "detail",
            "sourceId": "t445_analysis",
            "density": "dense",
            "layout": "full",
            "columns": [
                {"field": "pair", "label": "Pair"},
                {"field": "blind_status", "label": "Status"},
                {"field": "model_delay_days", "label": "Model delay (d)", "format": "number"},
                {"field": "observed_delay_days", "label": "Observed delay (d)", "format": "number"},
                {"field": "observed_delay_sigma_days", "label": "Observed σ (d)", "format": "number"},
                {"field": "total_match_lambda", "label": "Required λ", "format": "number"},
                {"field": "parallel_percent", "label": "Along line (%)", "format": "number"},
                {"field": "perpendicular_percent", "label": "Normal (%)", "format": "number"},
                {"field": "other_movement_ara", "label": "Other movement (0–2)", "format": "number"},
                {"field": "other_connection_ara", "label": "Other curvature (0–2)", "format": "number"},
            ],
        },
        {
            "id": "uncertainty_table",
            "title": "Local uncertainty intervals",
            "subtitle": "16th/50th/84th percentiles from 2,000 accepted local draws per pair; not a replacement for the missing full posterior.",
            "dataset": "uncertainty",
            "sourceId": "t445_analysis",
            "density": "dense",
            "layout": "full",
            "columns": [
                {"field": "pair", "label": "Pair"},
                {"field": "metric", "label": "Metric"},
                {"field": "q16", "label": "q16", "format": "number"},
                {"field": "median", "label": "Median", "format": "number"},
                {"field": "q84", "label": "q84", "format": "number"},
            ],
        },
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": "# T445 — Te-ARA solve and circle/line Other recovery in WGD 2038−4008"},
        {
            "id": "summary",
            "type": "markdown",
            "sourceId": "t445_analysis",
            "body": "## The procedure works as a diagnostic, but it does not yet identify a unique Other\n\nA delay-blind reconstruction locks the four images to one source at **2.51 mas RMS** and independently reproduces the old blind model delays to within **0.74 days**. The later clean AB and AD outcomes both lie beyond the fitted external-shear path, but at incompatible distances: **λ=11.47** and **λ=2.54**. Their conditional residuals are mostly aligned with the known line (**83.9%** and **78.9%**) while retaining smaller normal components (**16.1%** and **21.1%**). This validates the three-stage measurement grammar; it does not name the unresolved relation or prove a new time law.",
        },
        {"id": "metrics", "type": "metric-strip", "cardIds": ["source_lock", "outside", "shared_lambda", "shared_p", "along", "normal"]},
        {
            "id": "anchor",
            "type": "markdown",
            "sourceId": "tdcosmo_ix",
            "body": "## Identity and cut anchor\n\n**Who/where:** one quadruply imaged quasar, WGD 2038−4008. The four light paths are children of one source–lens–observer identity; the foreground lens is the connection-heavy parent; external shear is the named coupling. **What:** A is the geometric/traversal Fermat term and B the potential/connection term. **When:** the lens model predates the delay measurement; λ is controlled coupling strength, not chronological time. **Why/how:** solve B_eff from the later delay, then compare it with the frozen A/B path and split the remainder into line-aligned and normal components.",
        },
        {"id": "source_lock_text", "type": "markdown", "sourceId": "gaia_gral_x", "body": "## The pre-delay geometry is internally coherent\n\nThe Gaia and TDCOSMO letter conventions differ. The delay-blind Fermat ordering fixes the crosswalk as TDCOSMO A/B/C/D = Gaia C/B/A/D. With that identity correction, all four image positions back-project to one source well inside the frozen 20 mas ceiling."},
        {"id": "source_lock_chart_block", "type": "chart", "chartId": "source_lock_chart", "layout": "full"},
        {"id": "bridge_text", "type": "markdown", "sourceId": "tdcosmo_xvi", "body": "## The conventional science bridge is recovered before ARA interpretation\n\nThe reconstruction gives AB −4.79 d, AC −10.06 d, and AD −24.93 d, matching the published pre-delay model values −5.0, −10.0, and −24.2 d. The later observed outcomes are −12.4, −5.3, and −33.3 d. AC had its sign selected partly using model ordering, so AB and AD remain the primary clean test."},
        {"id": "delay_chart_block", "type": "chart", "chartId": "delay_bridge", "layout": "full"},
        {"id": "path_text", "type": "markdown", "sourceId": "t445_analysis", "body": "## The named coupling is a line, not the full route\n\nScaling external shear from absent to fitted produces an essentially perfectly straight path in the native A/B plane. That is the line-pole behaviour expected for this single controlled coordinate. The informative failure is relational: neither clean outcome occurs inside λ∈[0,1], and one shared extension of the line does not fit both (best λ=1.51, χ²=3.85 for 1 degree of freedom, p=0.0497 using observational covariance only)."},
        {"id": "native_path_block", "type": "chart", "chartId": "native_path", "layout": "full"},
        {"id": "lambda_block", "type": "chart", "chartId": "lambda_required", "layout": "full"},
        {"id": "teara_text", "type": "markdown", "sourceId": "t445_analysis", "body": "## Te-ARA supplies the first landmark by solving the opposite phase\n\nThe later delay supplies the total differential Fermat potential. Holding the independently reconstructed A term fixed gives B_eff = Δφ_obs − A. This is a legitimate conditional cut, but it also means the outcome residual is vertical in the A/B plane by construction; tangent/normal percentages must therefore be read as conditional geometry rather than an independently observed two-dimensional Other."},
        {"id": "native_decomp_block", "type": "chart", "chartId": "native_decomposition", "layout": "full"},
        {"id": "ara_text", "type": "markdown", "sourceId": "t445_analysis", "body": "## The 0–2 views preserve the relational shape without replacing the physics\n\nThe fitted and outcome-required A/B terms are normalized by total absolute participation, so each point lies on x+y=2 by definition. The movement/curvature split uses the same rule on |r_parallel| and |r_perpendicular|. For the clean pairs it is movement-heavy—AB (1.68, 0.32), AD (1.58, 0.42)—with a persistent smaller normal remainder."},
        {"id": "ara_pair_block", "type": "chart", "chartId": "ara_pair", "layout": "full"},
        {"id": "other_block", "type": "chart", "chartId": "other_split", "layout": "full"},
        {"id": "detail_table_block", "type": "table", "tableId": "detail_table", "layout": "full"},
        {"id": "uncertainty_text", "type": "markdown", "sourceId": "t445_analysis", "body": "## Uncertainty and robustness\n\nTwo thousand correlated delay draws and local lens-parameter draws were accepted per pair. AB and AD retain the same signed line-aligned and normal directions across their central 68% intervals. However, the original repository’s linked full-posterior Drive folder now returns 404, so this is a local covariance approximation around published marginal summaries—not the authors’ full posterior. The fitted-endpoint disagreement itself is not decisive (χ²=4.09 for 2 degrees of freedom, p=0.129 before adding model uncertainty)."},
        {"id": "uncertainty_table_block", "type": "table", "tableId": "uncertainty_table", "layout": "full"},
        {"id": "method", "type": "markdown", "body": "## Frozen methodology and audit trail\n\nThe identity, scale, lens family, cosmology, coupling ablation, A/B definitions, delay-leakage rule, and interpretation boundary were frozen first. The measured delay never enters the astrometric fit. Independent validation passed 17/17 checks: source locking, component sums, crosswalk, pre-delay prediction recovery, Te-ARA algebra, λ recovery, covariance, draw counts, SQLite extracts, and static leakage inspection."},
        {"id": "limits", "type": "markdown", "body": "## What this does not establish\n\nThe normal residual cannot be named as a new force, time component, or unique ARA identity. It can contain missing mass-profile freedom, external convergence, cosmology, microlensing/time-delay systematics, and the limitations of reconstructing a multivariate posterior from marginal summaries. Because λ is a counterfactual coupling coordinate, this is a completed-handover reconstruction—not a movie of time."},
        {"id": "next", "type": "markdown", "body": "## Recommended next test\n\nKeep this identity and add a second independently constrained coupling coordinate—preferably mass-sheet/external convergence or mass-profile slope—so the known relation becomes a two-dimensional surface rather than a forced line. Then freeze that surface before applying the later delay. A residual normal to the full surface would be a materially stronger Information³ lock on an unresolved Other."},
        {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Does a retrieved full posterior widen the shared-λ compatibility enough to erase the normal remainder?\n- Does adding external convergence collapse AB and AD onto one common coupling surface?\n- Can the same three-stage procedure recover a deliberately hidden coupling in another real lens without a label crosswalk ambiguity?"},
    ]

    datasets = {
        "headline": records(headline),
        "source_offsets": records(source_offsets),
        "delays": records(delays),
        "path_only": records(path_only),
        "lambda_required": records(lambda_frame),
        "native": records(native),
        "ara": records(ara),
        "other": records(other),
        "detail": records(detail),
        "uncertainty": records(uncertainty),
    }
    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "T445 — Lens Te-ARA and coarse Other recovery",
            "description": "A delay-blind ARA reconstruction of one real quadruply imaged quasar, with a controlled external-shear path and conditional Other decomposition.",
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
    print(json.dumps({"artifact": str(RESULTS / "artifact.json"), "datasets": {k: len(v) for k, v in datasets.items()}}, indent=2))


if __name__ == "__main__":
    main()
