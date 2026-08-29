"""Build the bounded Data Analytics report artifact for T449."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T449_time_facing_children")
RESULTS = ROOT / "results"


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def main() -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    result = json.loads((RESULTS / "T449_RESULT.json").read_text(encoding="utf-8"))
    posthoc = json.loads((RESULTS / "T449_POSTHOC_RESULT.json").read_text(encoding="utf-8"))
    inversion_result = json.loads((RESULTS / "T449C_INVERSION_EVENT_RESULT.json").read_text(encoding="utf-8"))
    quality = json.loads((RESULTS / "T449_DATA_QUALITY.json").read_text(encoding="utf-8"))

    lag = pd.read_csv(RESULTS / "T449_lag_scan.csv")
    lag["lag_minutes"] = lag.lag_windows * 10

    history = pd.read_csv(RESULTS / "T449_binned_child_histories.csv")
    history_long = pd.concat(
        [
            history[["split", "hours_before", "windows"]].assign(series="C_A retention", value=history.ara_A_median),
            history[["split", "hours_before", "windows"]].assign(series="C_B traversal", value=history.ara_B_median),
        ],
        ignore_index=True,
    )

    modes = pd.read_csv(RESULTS / "T449_posthoc_common_differential_history.csv")
    modes_long = pd.concat(
        [
            modes[["hours_before", "windows"]].assign(series="common parent-facing mode", value=modes.common_median),
            modes[["hours_before", "windows"]].assign(series="differential child mode", value=modes.differential_median),
        ],
        ignore_index=True,
    )

    geometry = pd.read_csv(RESULTS / "T449_eligible_child_geometry.csv")
    holdout = geometry[geometry.split.eq("holdout")].copy()
    holdout["lifecycle_band"] = pd.cut(
        holdout.hours_to_collapse,
        bins=[0, 6, 24, 72, np.inf],
        labels=["final 6 h", "6–24 h", "24–72 h", ">72 h"],
        include_lowest=True,
    ).astype(str)
    # Deterministic bounded snapshot that preserves the full lifecycle ordering.
    if len(holdout) > 1200:
        sample_indices = np.linspace(0, len(holdout) - 1, 1200).round().astype(int)
        holdout = holdout.iloc[sample_indices].copy()
    phase = holdout[["source_file", "hours_to_collapse", "ara_A", "ara_B", "dominance", "lifecycle_band"]]

    direction = pd.read_csv(RESULTS / "T449_posthoc_directional_exchanges.csv")
    direction["null_lower"] = direction.null_2_5pct
    direction["null_upper"] = direction.null_97_5pct
    direction["interpretation"] = [
        "significant movement against frozen terminal-parent direction",
        "weak positive response inside shifted null",
    ]

    inversion_rates = pd.read_csv(RESULTS / "T449_inversion_rates_by_lifecycle.csv")
    inversion_rates = inversion_rates[inversion_rates.direction.ne("either inversion")].copy()
    inversion_behavior = pd.read_csv(RESULTS / "T449_inversion_behavior_deltas.csv")

    fly_modes = pd.read_csv(RESULTS / "T449_posthoc_common_differential_by_fly.csv")
    fly_modes = fly_modes.rename(
        columns={
            "rho_hours_common": "rho_common_mode",
            "rho_hours_differential": "rho_differential_mode",
        }
    )

    gates = pd.DataFrame(
        [
            {
                "gate": gate.split("_", 1)[0],
                "criterion": gate.split("_", 1)[1].replace("_", " "),
                "passed": int(bool(passed)),
                "result": "PASS" if passed else "FAIL",
            }
            for gate, passed in result["gates"].items()
        ]
    )

    qa = pd.DataFrame(quality["eligible_by_experiment"])
    qa["eligible_percent"] = 100 * qa.eligible_fraction
    qa["split"] = np.where(qa.experiment.eq("exp4"), "untouched holdout", "development")

    headline = [
        {
            "flies": quality["source_files"],
            "all_windows": quality["rows"],
            "eligible_percent": 100 * quality["eligible_fraction"],
            "frozen_lag_minutes": result["frozen_development_lag_minutes"],
            "holdout_coupling": result["holdout_median_coupling"],
            "sign_transfer_percent": 100 * result["holdout_fly_sign_fraction"],
            "common_mode_positive_flies": int(round(16 * posthoc["holdout_final72_common_mode_positive_fraction"])),
            "holdout_inversions": inversion_result["holdout_inversions"],
        }
    ]

    source_main = {
        "id": "princeton_lifetime",
        "label": "Princeton Drosophila lifetime behaviour dataset",
        "path": str(RESULTS / "T449_child_windows.csv"),
        "href": "https://doi.org/10.34770/1sab-8845",
        "query": {
            "language": "python",
            "description": "Read-only HTTP-range extraction of every source frame, converted to exact modal one-second states and consecutive ten-minute windows by the frozen T449 protocol.",
            "executed_at": timestamp,
            "tables_used": ["47 published individual HDF5 files", "analysis_data_index.csv"],
            "filters": ["primary windows require at least 80% resolved seconds, 300 valid adjacent transitions and at least two resolved states", "collapse and death withheld from coordinate construction"],
            "metric_definitions": [
                "C_A is mean chance-corrected same-state retention over 1, 10 and 60 second lags.",
                "C_B is one-second conditional transition entropy divided by log of the resolved-state count.",
                "Development fixes centres, scales and selected lag; experiment 4 is untouched until evaluation.",
            ],
        },
    }
    source_paper = {
        "id": "plos_methods",
        "label": "McKenzie-Smith et al. 2025 methods",
        "href": "https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012753",
        "query": {"language": "document", "description": "Peer-reviewed source for cohort, conditions, tracking, behaviour classification and lifecycle recording."},
    }
    source_analysis = {
        "id": "t449_analysis",
        "label": "Frozen T449 analysis and data-quality audit",
        "path": str(ROOT / "FROZEN_PROTOCOL.md"),
        "query": {
            "language": "python",
            "description": "Frozen confirmatory test plus explicitly post-frozen geometric decomposition.",
            "executed_at": timestamp,
            "tables_used": ["T449_RESULT.json", "T449_POSTHOC_RESULT.json", "T449C_INVERSION_EVENT_RESULT.json", "T449_DATA_QUALITY.json"],
        },
    }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "T449 time-facing fruit-fly children: local exchange, no directional handover",
        "description": "A same-rung ARA test of ten-minute temporal retention and traversal/renewal across 47 individual fruit-fly lifecycles.",
        "generatedAt": timestamp,
        "cards": [
            {"id": "flies", "description": "Published individuals reconstructed.", "dataset": "headline", "sourceId": "princeton_lifetime", "metrics": [{"label": "Flies", "field": "flies", "format": "number"}]},
            {"id": "windows", "description": "Consecutive ten-minute child windows.", "dataset": "headline", "sourceId": "princeton_lifetime", "metrics": [{"label": "10-min windows", "field": "all_windows", "format": "number"}]},
            {"id": "eligible", "description": "Windows meeting the frozen visibility and transition requirements.", "dataset": "headline", "sourceId": "princeton_lifetime", "metrics": [{"label": "Eligible", "field": "eligible_percent", "format": "number", "suffix": "%"}]},
            {"id": "lag", "description": "Lag selected from development only.", "dataset": "headline", "sourceId": "t449_analysis", "metrics": [{"label": "Frozen lag", "field": "frozen_lag_minutes", "format": "number", "suffix": " min"}]},
            {"id": "coupling", "description": "Median ordered holdout coupling at the frozen lag.", "dataset": "headline", "sourceId": "t449_analysis", "metrics": [{"label": "Holdout coupling", "field": "holdout_coupling", "format": "number"}]},
            {"id": "sign", "description": "Untouched individuals reproducing the inverse sign.", "dataset": "headline", "sourceId": "t449_analysis", "metrics": [{"label": "Sign transfer", "field": "sign_transfer_percent", "format": "number", "suffix": "%"}]},
        ],
        "charts": [
            {
                "id": "lag_scan",
                "title": "Lead–lag relation across ordered and disrupted histories",
                "subtitle": "The reproducible minimum is at zero minutes; chronological disruption weakens it, but reversal cannot establish a direction.",
                "type": "line",
                "dataset": "lag_scan",
                "sourceId": "t449_analysis",
                "encodings": {"x": {"field": "lag_minutes", "type": "quantitative", "label": "C_B lag relative to C_A (minutes)"}, "y": {"field": "median_correlation", "type": "quantitative", "label": "Median within-fly correlation"}, "color": {"field": "series", "type": "nominal", "label": "History/control"}},
                "layout": "full",
            },
            {
                "id": "lifecycle_history",
                "title": "Same children viewed from the lifecycle parent",
                "subtitle": "Both medians decline toward collapse; this is a slow common-mode gradient, not a universal landmark.",
                "type": "line",
                "dataset": "history_long",
                "sourceId": "princeton_lifetime",
                "encodings": {"x": {"field": "hours_before", "type": "quantitative", "label": "Hours remaining to author-indexed collapse"}, "y": {"field": "value", "type": "quantitative", "label": "ARA coordinate (0–2 display)"}, "color": {"field": "series", "type": "nominal", "label": "Child"}},
                "layout": "full",
            },
            {
                "id": "phase_plane",
                "title": "Untouched child-plane occupancy",
                "subtitle": "The broad fan is a gradient with individual asymmetry, not a required point at an ideal ridge.",
                "type": "scatter",
                "dataset": "phase_sample",
                "sourceId": "princeton_lifetime",
                "encodings": {"x": {"field": "ara_A", "type": "quantitative", "label": "C_A temporal retention (0–2)"}, "y": {"field": "ara_B", "type": "quantitative", "label": "C_B traversal/renewal (0–2)"}, "color": {"field": "lifecycle_band", "type": "nominal", "label": "Hours remaining band"}, "tooltip": [{"field": "source_file", "type": "nominal", "label": "Individual"}, {"field": "hours_to_collapse", "type": "quantitative", "label": "Hours remaining"}]},
                "layout": "full",
            },
            {
                "id": "mode_history",
                "title": "Parent-facing common mode versus child-difference mode",
                "subtitle": "The common mode carries the slow lifecycle gradient; the differential mode mostly records local child exchange.",
                "type": "line",
                "dataset": "mode_history",
                "sourceId": "t449_analysis",
                "encodings": {"x": {"field": "hours_before", "type": "quantitative", "label": "Hours remaining to collapse"}, "y": {"field": "value", "type": "quantitative", "label": "Development-robust coordinate"}, "color": {"field": "series", "type": "nominal", "label": "Geometric mode"}},
                "layout": "full",
            },
            {
                "id": "direction_split",
                "title": "Post-frozen exchange directions do not mean the same thing",
                "subtitle": "Retention→traversal is followed by significant motion against the frozen terminal-parent direction; the reverse branch is weak.",
                "type": "bar",
                "dataset": "direction_split",
                "sourceId": "t449_analysis",
                "encodings": {"x": {"field": "direction", "type": "nominal", "label": "Crossing direction"}, "y": {"field": "actual_median_parent_response", "type": "quantitative", "label": "Median next-parent response"}},
                "layout": "full",
            },
            {
                "id": "inversion_rate",
                "title": "Inversion frequency by lifecycle distance",
                "subtitle": "Both activity-state handover directions become more frequent in the final six hours, although the within-fly terminal enrichment remains suggestive rather than confirmed.",
                "type": "bar",
                "dataset": "inversion_rates",
                "sourceId": "t449_analysis",
                "encodings": {"x": {"field": "lifecycle_band", "type": "nominal", "label": "Hours remaining band"}, "y": {"field": "events_per_100_pairs", "type": "quantitative", "label": "Events per 100 adjacent eligible pairs"}, "color": {"field": "direction", "type": "nominal", "label": "Inversion direction"}},
                "layout": "full",
            },
            {
                "id": "inversion_behavior",
                "title": "Behaviour changes at each inversion direction",
                "subtitle": "Retention→traversal exchanges idle for locomotion; traversal→retention performs the opposing exchange after same-fly lifecycle-matched non-crossing movement is removed.",
                "type": "bar",
                "dataset": "inversion_behavior",
                "sourceId": "t449_analysis",
                "encodings": {"x": {"field": "feature", "type": "nominal", "label": "Classified behaviour share"}, "y": {"field": "median_fly_matched_residual", "type": "quantitative", "label": "Median fly residual share change"}, "color": {"field": "direction", "type": "nominal", "label": "Inversion direction"}},
                "layout": "full",
            },
            {
                "id": "coverage",
                "title": "Primary visibility varies by experiment",
                "subtitle": "Coverage is usable but materially incomplete and is never silently interpolated.",
                "type": "bar",
                "dataset": "qa_by_experiment",
                "sourceId": "princeton_lifetime",
                "encodings": {"x": {"field": "experiment", "type": "nominal", "label": "Experiment"}, "y": {"field": "eligible_percent", "type": "quantitative", "label": "Eligible ten-minute windows (%)"}, "color": {"field": "split", "type": "nominal", "label": "Analysis role"}},
                "layout": "full",
            },
        ],
        "tables": [
            {
                "id": "gates",
                "title": "Frozen confirmatory gates",
                "subtitle": "The test recovers chronological structure, not a directional handover.",
                "dataset": "gates",
                "sourceId": "t449_analysis",
                "defaultSort": {"field": "gate", "direction": "asc"},
                "columns": [{"field": "gate", "label": "Gate"}, {"field": "criterion", "label": "Frozen criterion"}, {"field": "result", "label": "Result"}],
                "layout": "full",
            },
            {
                "id": "direction_table",
                "title": "Directional exchange diagnostic",
                "subtitle": "Post-frozen: descriptive only and unable to change Q3.",
                "dataset": "direction_split",
                "sourceId": "t449_analysis",
                "defaultSort": {"field": "direction", "direction": "asc"},
                "density": "dense",
                "columns": [{"field": "direction", "label": "Direction"}, {"field": "events", "label": "Events", "format": "number"}, {"field": "actual_median_parent_response", "label": "Actual median response", "format": "number"}, {"field": "null_lower", "label": "Null 2.5%", "format": "number"}, {"field": "null_upper", "label": "Null 97.5%", "format": "number"}, {"field": "interpretation", "label": "Reading"}],
                "layout": "full",
            },
            {
                "id": "qa_table",
                "title": "Visibility by experiment",
                "subtitle": "All 47 flies remain represented despite unequal eligible fractions.",
                "dataset": "qa_by_experiment",
                "sourceId": "princeton_lifetime",
                "defaultSort": {"field": "experiment", "direction": "asc"},
                "columns": [{"field": "experiment", "label": "Experiment"}, {"field": "split", "label": "Role"}, {"field": "windows", "label": "Windows", "format": "number"}, {"field": "eligible_windows", "label": "Eligible", "format": "number"}, {"field": "eligible_percent", "label": "Eligible %", "format": "number"}],
                "layout": "full",
            },
        ],
        "sources": [source_main, source_paper, source_analysis],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T449 time-facing fruit-fly children: local exchange, no directional handover"},
            {"id": "summary", "type": "markdown", "sourceId": "t449_analysis", "body": "## Result first\n\n**T449 recovered a real local activity-state handover, but not the directional lifecycle/time handover named by its frozen gates.** Temporal retention and traversal/renewal invert at zero lag in all 16 untouched flies (median coupling -0.136; circular-shift p≈0.00050). Retention→traversal exchanges idle for locomotion, while traversal→retention performs the opposing exchange. Reversing time leaves the selected lag at zero, so this establishes a bidirectional handover inside the lifecycle parent rather than its time direction. The slower common mode of both children declines toward collapse in 15/16 holdout flies."},
            {"id": "metrics", "type": "metric-strip", "cardIds": ["flies", "windows", "eligible", "lag", "coupling", "sign"]},
            {"id": "address", "type": "markdown", "sourceId": "princeton_lifetime", "body": "## Who, what, when, where, why and how\n\n**Who:** 47 individual males: 31 development and 16 later/hotter untouched holdouts. **What:** independently measured ten-minute temporal retention C_A and traversal/renewal C_B. **When:** every pre-collapse child window, with collapse withheld until evaluation. **Where:** fly → ten-minute children → six-child hourly parent → lifecycle shadow. **Why:** test whether a time-ordered child turns before T448's coarser lifecycle parent. **How:** exact modal one-second states, frozen development scaling and lag, followed by untouched temporal and biological controls. The pair is a same-rung simple ARA cut, not yet a Di-ARA."},
            {"id": "lag_text", "type": "markdown", "body": "## Frozen chronological test\n\nOrdered histories retain more inverse structure than timestamp-shuffled or circularly shifted controls. The selected relation sits at zero minutes, however, so it describes immediate push/pull rather than a measurable lead. A true directional child should change sign or lag under reversal; this pair does not."},
            {"id": "lag_chart", "type": "chart", "chartId": "lag_scan", "layout": "full"},
            {"id": "gate_table", "type": "table", "tableId": "gates", "layout": "full"},
            {"id": "parent_text", "type": "markdown", "body": "## Parent view and child view are different cuts of the same history\n\nFrom the parent/lifecycle view, both children fall together toward collapse. Inside each ten-minute child sequence, their changes oppose one another. That is the main geometric result: a slow common-mode loss of organisation contains a faster same-rung exchange, rather than one coordinate simply becoming the other."},
            {"id": "history_chart", "type": "chart", "chartId": "lifecycle_history", "layout": "full"},
            {"id": "phase_chart", "type": "chart", "chartId": "phase_plane", "layout": "full"},
            {"id": "mode_chart", "type": "chart", "chartId": "mode_history", "layout": "full"},
            {"id": "posthoc_text", "type": "markdown", "sourceId": "t449_analysis", "body": "## Post-frozen diagnostic: the two crossing directions separate\n\nThis split was discovered after the gates and cannot rescue Q3. Retention→traversal crossings are followed by significant motion against the terminal-parent direction (median -0.0544; lower-tail p≈0.0020), while traversal→retention has a weak positive response inside its null. The strong branch is therefore more consistent with a movement/recovery excursion than the final lifecycle handover."},
            {"id": "direction_chart", "type": "chart", "chartId": "direction_split", "layout": "full"},
            {"id": "direction_table_block", "type": "table", "tableId": "direction_table", "layout": "full"},
            {"id": "inversion_event_text", "type": "markdown", "sourceId": "t449_analysis", "body": "## T449C: the inversion is a biological activity-state handover\n\nAcross 4,259 adjacent eligible holdout pairs, 1,607 sign inversions occurred. Retention→traversal has a matched median fly idle-share change of -0.0602 and locomotion change of +0.0385; traversal→retention has idle +0.0757 and locomotion -0.0414. All four fly-level sign-flip p-values are below 0.0024. Unresolved visibility does not rise materially in the first direction, making classifier loss an unlikely primary explanation."},
            {"id": "inversion_behavior_chart", "type": "chart", "chartId": "inversion_behavior", "layout": "full"},
            {"id": "inversion_rate_text", "type": "markdown", "sourceId": "t449_analysis", "body": "## The local handover is modulated by the slower lifecycle parent\n\nInversions rise from 36.3 per 100 valid adjacent pairs beyond 72 hours to 50.7 in the final six hours. Among the 13 flies observed in both bands, the median increase is 10.6 percentage points, but the exact two-sided sign-flip p≈0.0796 is not confirmatory. The enrichment is therefore a promising parent modulation, not yet a terminal-specific law."},
            {"id": "inversion_rate_chart", "type": "chart", "chartId": "inversion_rate", "layout": "full"},
            {"id": "quality_text", "type": "markdown", "sourceId": "princeton_lifetime", "body": "## Data quality\n\nSource keys, time arithmetic, one-second share closure, continuity and finite-coordinate checks all pass. The material caveat is visibility: 48.1% of windows meet the frozen 80% resolved-state rule, with substantial experiment and individual variation. Missing periods are not filled; unresolved share remains a modeled control."},
            {"id": "coverage_chart", "type": "chart", "chartId": "coverage", "layout": "full"},
            {"id": "qa_table_block", "type": "table", "tableId": "qa_table", "layout": "full"},
            {"id": "ara", "type": "markdown", "body": "## ARA reading\n\nThis is evidence that the local relationship is real and scale-dependent. It is not evidence that C_A or C_B is time itself, nor that their pair forms a complete Di-ARA. The parent-facing common mode is a candidate lifecycle/time shadow; the zero-lag child difference is exchange. A genuinely time-facing next child must carry a direction that changes under temporal reversal."},
            {"id": "next", "type": "markdown", "body": "## Recommended deeper biologic cut\n\nChange medium explicitly from categorical behaviour to continuous pose/kinematics while preserving the same ten-minute rung. Measure whole-body persistence, internal articulation renewal, and forward-minus-backward prediction error. Then freeze on development and ask whether the internal pose child turns before the whole-body behavioural parent on experiment 4. This targets direction rather than another occupancy proxy, but the medium change must be agreed before execution."},
        ],
    }

    for widget_type in ["cards", "charts", "tables"]:
        for widget in manifest[widget_type]:
            dataset = widget["dataset"]
            widget["source"] = {
                "id": widget.get("sourceId", "t449_analysis"),
                "label": "T449 bounded analytical snapshot",
                "path": str(RESULTS / "artifact.json"),
                "query": {
                    "language": "sql",
                    "sql": f"SELECT * FROM {dataset};",
                    "description": f"Return the complete bounded {dataset} dataset used by this widget.",
                    "executed_at": timestamp,
                    "tables_used": [dataset],
                    "metric_definitions": source_main["query"]["metric_definitions"],
                },
            }

    snapshot = {
        "version": 1,
        "generatedAt": timestamp,
        "status": "ready",
        "datasets": {
            "headline": headline,
            "lag_scan": records(lag[["lag_minutes", "median_correlation", "q25", "q75", "flies", "pairs", "series"]]),
            "history_long": records(history_long),
            "phase_sample": records(phase),
            "mode_history": records(modes_long),
            "direction_split": records(direction),
            "inversion_rates": records(inversion_rates),
            "inversion_behavior": records(inversion_behavior),
            "fly_modes": records(fly_modes),
            "gates": records(gates),
            "qa_by_experiment": records(qa),
        },
    }
    artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": [source_main, source_paper, source_analysis]}
    (RESULTS / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(json.dumps({"datasets": {key: len(value) for key, value in snapshot["datasets"].items()}, "blocks": len(manifest["blocks"])}, indent=2))


if __name__ == "__main__":
    main()
