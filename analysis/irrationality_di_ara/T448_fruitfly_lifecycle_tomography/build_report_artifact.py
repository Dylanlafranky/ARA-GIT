"""Build the bounded Data Analytics report artifact for T448."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T448_fruitfly_lifecycle_tomography")
RESULTS = ROOT / "results"


def records(frame):
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def main():
    timestamp = datetime.now(timezone.utc).isoformat()
    point = json.loads((RESULTS / "T448_RESULT.json").read_text(encoding="utf-8"))
    direction = json.loads((RESULTS / "T448B_RESULT.json").read_text(encoding="utf-8"))
    point_metrics = pd.read_csv(RESULTS / "T448_holdout_metrics.csv")
    point_metrics["auc_above_chance"] = point_metrics.auc - 0.5
    hourly = pd.read_csv(RESULTS / "T448_hourly_states_with_geometry.csv")
    dynamic = pd.read_csv(RESULTS / "T448B_24h_directional_states.csv")
    vectors = pd.read_csv(RESULTS / "T448B_holdout_terminal_vectors.csv")

    scope = (
        hourly.groupby("experiment")
        .agg(flies=("source_file", "nunique"), fly_hours=("hour_index", "size"), median_collapse_hour=("collapse_hour", "median"), min_collapse_hour=("collapse_hour", "min"), max_collapse_hour=("collapse_hour", "max"))
        .reset_index()
    )
    scope["split"] = np.where(scope.experiment.eq("exp4"), "untouched holdout", "development")

    dynamic_hold = dynamic[(dynamic.split.eq("holdout")) & (dynamic.hours_to_collapse > 0) & (dynamic.hours_to_collapse <= 72)].copy()
    dynamic_hold["hours_bin"] = pd.cut(dynamic_hold.hours_to_collapse, np.arange(0, 75, 3))
    dynamic_hold["hours_remaining"] = dynamic_hold.hours_bin.map(lambda x: x.mid).astype(float)
    histories = (
        dynamic_hold.groupby("hours_remaining", observed=True)[["parallel_progress", "perpendicular_residual", "alignment_cosine"]]
        .median()
        .reset_index()
        .melt(id_vars="hours_remaining", var_name="series", value_name="value")
    )
    histories["series"] = histories.series.map(
        {
            "parallel_progress": "parallel progress",
            "perpendicular_residual": "perpendicular distortion",
            "alignment_cosine": "alignment cosine",
        }
    )

    gates = []
    for label, passed in point["gates"].items():
        gates.append({"test": "T448 fixed terminal point", "gate": label, "passed": int(bool(passed)), "result": "PASS" if passed else "FAIL"})
    for label, passed in direction["gates"].items():
        gates.append({"test": "T448B 24 h direction", "gate": label, "passed": int(bool(passed)), "result": "PASS" if passed else "FAIL"})
    gates = pd.DataFrame(gates)

    headline = [
        {
            "flies": point["data_quality"]["flies"],
            "fly_hours": point["data_quality"]["rows"],
            "point_gates_passed": int(sum(point["gates"].values())),
            "direction_gates_passed": int(sum(direction["gates"].values())),
            "direction_progress": direction["actual_mean_parallel_progress"],
            "direction_shift95": direction["shift_95pct"],
            "direction_auc": direction["projection_auc"],
            "dominant_cut_auc": max(direction["single_axis_signed_aucs"].values()),
        }
    ]

    source_main = {
        "id": "princeton_lifetime",
        "label": "Princeton Drosophila lifetime behaviour dataset",
        "path": str(RESULTS / "hourly_lifecycle_states.csv"),
        "href": "https://doi.org/10.34770/1sab-8845",
        "query": {
            "language": "python",
            "description": "Read-only HTTP-range extraction of the published individual HDF5 behaviour labels, aggregated to complete fly-hours by the frozen T448 protocol.",
            "executed_at": timestamp,
            "tables_used": ["47 published individual HDF5 files", "analysis/data_index.csv", "four humidity/temperature logs"],
            "filters": ["complete one-hour windows before author-index collapse", "unstereotyped and on-edge labels excluded from the four-part biological composition"],
            "metric_definitions": [
                "T448 point distance is Euclidean distance in three shared-scale isometric log-ratio coordinates to the development final-six-hour median.",
                "T448B parallel progress is the projection of each fly's 24-hour state displacement onto the development median terminal displacement direction.",
                "Every holdout score uses experiment 4 without rotation, centering, scale or threshold refitting.",
            ],
        },
    }
    source_paper = {
        "id": "plos_methods",
        "label": "McKenzie-Smith et al. 2025 methods and biological interpretation",
        "href": "https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012753",
        "query": {"language": "document", "description": "Peer-reviewed source for cohort, conditions, tracking/classification method and known circadian/lifelong trends."},
    }
    source_code = {
        "id": "official_code",
        "label": "Official analysis code and experiment index",
        "href": "https://github.com/shaevitz-lab/long-timescale-analysis",
        "path": str(ROOT / "source" / "analysis_data_index.csv"),
        "query": {"language": "csv", "description": "Author-supplied per-fly death and collapse landmarks plus environment logs."},
    }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "Fruit-fly lifecycle tomography: point failure, directional handover",
        "description": "A geometry-first ARA technical report following 47 individual fruit flies through accelerated life-to-collapse recordings.",
        "generatedAt": timestamp,
        "cards": [
            {"id": "flies", "description": "Published individuals successfully reconstructed.", "dataset": "headline", "sourceId": "princeton_lifetime", "metrics": [{"label": "Flies", "field": "flies", "format": "number"}]},
            {"id": "hours", "description": "Complete individual pre-collapse fly-hours.", "dataset": "headline", "sourceId": "princeton_lifetime", "metrics": [{"label": "Fly-hours", "field": "fly_hours", "format": "number"}]},
            {"id": "point_pass", "description": "Frozen fixed-point gates passed.", "dataset": "headline", "sourceId": "princeton_lifetime", "metrics": [{"label": "Point gates", "field": "point_gates_passed", "format": "number"}]},
            {"id": "direction_pass", "description": "Frozen 24-hour direction gates passed.", "dataset": "headline", "sourceId": "princeton_lifetime", "metrics": [{"label": "Direction gates", "field": "direction_gates_passed", "format": "number"}]},
            {"id": "direction_auc", "description": "Holdout AUROC for signed three-coordinate direction.", "dataset": "headline", "sourceId": "princeton_lifetime", "metrics": [{"label": "Direction AUROC", "field": "direction_auc", "format": "number"}]},
        ],
        "charts": [
            {
                "id": "point_auc",
                "title": "Fixed terminal-point AUROC by cut",
                "subtitle": "Only traversal↔maintenance is above chance; the all-cut point distance is 0.397.",
                "type": "bar",
                "dataset": "point_metrics",
                "sourceId": "princeton_lifetime",
                "encodings": {"x": {"field": "label", "type": "nominal", "label": "Cut or projection"}, "y": {"field": "auc", "type": "quantitative", "label": "AUROC"}},
                "layout": "full",
            },
            {
                "id": "point_win",
                "title": "Same-fly final-six-hour paired win rate",
                "subtitle": "Controls are exactly 24 hours earlier, preserving circadian phase.",
                "type": "bar",
                "dataset": "point_metrics",
                "sourceId": "princeton_lifetime",
                "encodings": {"x": {"field": "label", "type": "nominal", "label": "Cut or projection"}, "y": {"field": "paired_win_rate", "type": "quantitative", "label": "Paired win rate"}},
                "layout": "full",
            },
            {
                "id": "direction_history",
                "title": "Directional lifecycle histories on untouched flies",
                "subtitle": "Parallel progress rises near collapse while perpendicular distortion remains substantial.",
                "type": "line",
                "dataset": "direction_history",
                "sourceId": "princeton_lifetime",
                "encodings": {"x": {"field": "hours_remaining", "type": "quantitative", "label": "Hours remaining"}, "y": {"field": "value", "type": "quantitative", "label": "Shared robust units"}, "color": {"field": "series", "type": "nominal", "label": "Directional quantity"}},
                "layout": "full",
            },
            {
                "id": "terminal_arrows",
                "title": "Holdout terminal displacement by individual",
                "subtitle": "The common downward participation↔idle component is visible despite branch spread.",
                "type": "scatter",
                "dataset": "individual_vectors",
                "sourceId": "princeton_lifetime",
                "encodings": {"x": {"field": "delta24_w_action_intake", "type": "quantitative", "label": "Δ24 action↔intake"}, "y": {"field": "delta24_w_participation_quiescence", "type": "quantitative", "label": "Δ24 participation↔idle"}, "tooltip": [{"field": "source_file", "type": "nominal", "label": "Individual"}]},
                "layout": "full",
            },
            {
                "id": "gate_counts",
                "title": "Frozen gate outcomes",
                "subtitle": "The fixed-point test fails; two directional gates pass without multi-cut superiority.",
                "type": "bar",
                "dataset": "gates",
                "sourceId": "princeton_lifetime",
                "encodings": {"x": {"field": "gate", "type": "nominal", "label": "Frozen gate"}, "y": {"field": "passed", "type": "quantitative", "label": "Pass = 1"}, "color": {"field": "test", "type": "nominal", "label": "Test"}},
                "layout": "full",
            },
        ],
        "tables": [
            {
                "id": "scope_table",
                "title": "Cohort scope by experiment",
                "subtitle": "Experiment 4 is the later, hotter untouched holdout.",
                "dataset": "scope",
                "sourceId": "princeton_lifetime",
                "defaultSort": {"field": "experiment", "direction": "asc"},
                "density": "dense",
                "columns": [
                    {"field": "experiment", "label": "Experiment"},
                    {"field": "split", "label": "Role"},
                    {"field": "flies", "label": "Flies", "format": "number"},
                    {"field": "fly_hours", "label": "Fly-hours", "format": "number"},
                    {"field": "median_collapse_hour", "label": "Median collapse h", "format": "number"},
                    {"field": "min_collapse_hour", "label": "Min", "format": "number"},
                    {"field": "max_collapse_hour", "label": "Max", "format": "number"},
                ],
                "layout": "full",
            },
            {
                "id": "gate_table",
                "title": "Every frozen gate",
                "subtitle": "Results are retained even when later diagnostics reveal a better geometry.",
                "dataset": "gates",
                "sourceId": "princeton_lifetime",
                "defaultSort": {"field": "test", "direction": "asc"},
                "columns": [{"field": "test", "label": "Test"}, {"field": "gate", "label": "Gate"}, {"field": "result", "label": "Result"}],
                "layout": "full",
            },
        ],
        "sources": [source_main, source_paper, source_code],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# Fruit-fly lifecycle tomography: point failure, directional handover"},
            {"id": "summary", "type": "markdown", "sourceId": "princeton_lifetime", "body": "## Technical summary\n\n**A universal terminal point failed, but a separately frozen one-cycle terminal direction transferred.** T448 reconstructed 5,147 complete hours from 47 individual males without using lifespan as an input. All fixed-point gates failed. T448B compared each fly with itself exactly 24 hours earlier: terminal progress exceeded the shifted 95% limit (0.377 vs 0.209; p≈0.0005), 84.0% of observations aligned positively, and median cosine was 0.464. The full direction did not beat participation↔idle alone, so this is not yet multi-cut superiority or a sphere result."},
            {"id": "metrics", "type": "metric-strip", "cardIds": ["flies", "hours", "point_pass", "direction_pass", "direction_auc"]},
            {"id": "scope_text", "type": "markdown", "sourceId": "plos_methods", "body": "## Scope, data and relational address\n\nThe source follows males from 2–3 days post-eclosion under nutrient-limited sucrose-agarose and warm conditions until death. The measured address is individual fly → hourly four-part behaviour → three independent balance cuts → lifecycle shadow → author-index collapse. Experiments 1–3 develop the geometry; experiment 4 remains the hard holdout."},
            {"id": "scope_table_block", "type": "table", "tableId": "scope_table", "layout": "full"},
            {"id": "point_text", "type": "markdown", "sourceId": "princeton_lifetime", "body": "## T448: the fixed terminal point is the wrong transferred geometry\n\nThe holdout terminal points often pass beyond the development terminal centre, especially on participation↔idle. Euclidean distance therefore interprets correct-direction overshoot as failure. This was not known before freezing T448 and cannot be used to relabel its gates."},
            {"id": "point_auc_block", "type": "chart", "chartId": "point_auc", "layout": "full"},
            {"id": "point_win_block", "type": "chart", "chartId": "point_win", "layout": "full"},
            {"id": "direction_text", "type": "markdown", "sourceId": "princeton_lifetime", "body": "## T448B: a same-fly one-cycle direction survives the regime change\n\nThe follow-up freezes each development fly's final-six-hour displacement relative to itself 24 hours earlier, holding circadian phase constant. The later/hotter holdout follows that direction more strongly than 2,000 shifted fake endpoints. Perpendicular displacement remains large, so the shared object is a branch direction with distortion, not a narrow universal line."},
            {"id": "direction_chart", "type": "chart", "chartId": "direction_history", "layout": "full"},
            {"id": "arrows_chart", "type": "chart", "chartId": "terminal_arrows", "layout": "full"},
            {"id": "ara_text", "type": "markdown", "body": "## ARA interpretation\n\nTraversal, grooming/maintenance, proboscis/intake and idle/quiescence form a closed four-part composition with three independent balances. The terminal cloud has a 4.58:1 largest-to-smallest standard-deviation ratio, so several disks reveal real distortion; they do not prove a sphere. The transferable direction is dominated by participation→quiescence. The other cuts remain useful for branch character but did not add holdout discrimination."},
            {"id": "gates_chart", "type": "chart", "chartId": "gate_counts", "layout": "full"},
            {"id": "gates_table_block", "type": "table", "tableId": "gate_table", "layout": "full"},
            {"id": "method", "type": "markdown", "sourceId": "princeton_lifetime", "body": "## Methodology and robustness\n\nBehaviour labels were aggregated into complete one-hour windows. Four parts were converted to an orthonormal isometric log-ratio basis, robustly centred on development only, and mapped with one shared 0–2 scale. Exact 24-hour same-fly controls preserve Zeitgeber phase. Core coordinates have zero missing cells; environment matched 99.864% of hours. Unstereotyped and edge shares remain QA controls outside the lifecycle identity."},
            {"id": "limits", "type": "markdown", "sourceId": "official_code", "body": "## Limitations\n\nThe official `Collapse` column is sometimes earlier than recorded death, but its operational definition is not detailed in the paper. Classifier and endpoint are both observation-derived, so this is behavioural precursor/reconstruction evidence, not molecular prediction. Aging, starvation, heat and humidity are entangled. T448B's 24-hour cut requires at least one full prior cycle and does not establish that the displacement is time itself."},
            {"id": "next", "type": "markdown", "body": "## Recommended next step\n\nUse the 14 tracked body points to split the dominant participation↔idle direction into whole-body translation, internal limb/postural motion, gait failure and micro-movement during nominal idle. Freeze the same one-cycle direction and test whether a posture child turns before the coarse behavioural parent on untouched flies."},
            {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Does the terminal direction transfer under normal food and temperature?\n- Which posture child first carries the participation→quiescence displacement?\n- Is the strong perpendicular component stable individual asymmetry, environmental distortion, or multiple terminal branches?\n- Can a shorter lag than 24 hours retain direction while increasing useful warning time?"},
        ],
    }

    # Every renderable widget carries the exact bounded-snapshot query it uses.
    for widget_type in ["cards", "charts", "tables"]:
        for widget in manifest[widget_type]:
            dataset = widget["dataset"]
            widget["source"] = {
                "id": "princeton_lifetime",
                "label": "T448 bounded analytical snapshot",
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
            "point_metrics": records(point_metrics[["metric", "label", "auc", "paired_win_rate", "median_control_minus_terminal", "pairs"]]),
            "direction_history": records(histories),
            "individual_vectors": records(vectors),
            "gates": records(gates),
            "scope": records(scope),
        },
    }
    artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": [source_main, source_paper, source_code]}
    (RESULTS / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(json.dumps({"datasets": {key: len(value) for key, value in snapshot["datasets"].items()}, "blocks": len(manifest["blocks"])}, indent=2))


if __name__ == "__main__":
    main()
