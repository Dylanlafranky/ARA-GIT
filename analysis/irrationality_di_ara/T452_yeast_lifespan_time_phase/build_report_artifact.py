"""Build the canonical bounded report artifact for T452."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T452_yeast_lifespan_time_phase")
RESULTS = ROOT / "results"


def records(frame):
    return json.loads(frame.replace({np.nan: None, np.inf: None, -np.inf: None}).to_json(orient="records"))


def curve_dataset(summary, metric, cohorts=None):
    d = summary[summary.metric.eq(metric)].copy()
    if cohorts is not None:
        d = d[d.cohort.isin(cohorts)]
    d = d[["grid_A", "cohort", "median", "q25", "q75", "n"]].sort_values(["cohort", "grid_A"])
    return records(d)


def main():
    timestamp = datetime.now(timezone.utc).isoformat()
    result = json.loads((RESULTS / "T452_RESULT.json").read_text(encoding="utf-8"))
    cells = pd.read_csv(RESULTS / "T452_CELL_SUMMARY.csv")
    cohort = pd.read_csv(RESULTS / "T452_COHORT_SUMMARY.csv")
    gen = pd.read_csv(RESULTS / "T452_GENERATION_CURVES.csv")
    rate = pd.read_csv(RESULTS / "T452_INTERVAL_CURVES.csv")
    transfer = pd.read_csv(RESULTS / "T452_TRANSFER_METRICS.csv")
    landmarks = pd.read_csv(RESULTS / "T452_HANDOVER_LANDMARKS.csv")
    shuffles = pd.read_csv(RESULTS / "T452_SHUFFLE_TESTS.csv")
    witnesses = pd.read_csv(RESULTS / "T452_WITNESS_RELATIONSHIPS.csv")

    shadow = transfer[transfer.metric.eq("time_shadow")].set_index("comparison")
    local = transfer[transfer.metric.eq("local_time_rate")].set_index("comparison")
    lm = landmarks.set_index("cohort")
    sh = shuffles.set_index("cohort")

    headline = [
        {
            "cells": int(len(cells)),
            "generation_rows": int(result["source_generation_rows"]),
            "holdout_shadow_correlation": float(shadow.loc["development_vs_holdout", "correlation"]),
            "external_shadow_correlation": float(shadow.loc["development_vs_external", "correlation"]),
            "development_crossing_A": float(lm.loc["development", "local_rate_upcrossing_A"]),
            "holdout_crossing_A": float(lm.loc["holdout", "local_rate_upcrossing_A"]),
            "external_crossing_A": float(lm.loc["external", "local_rate_upcrossing_A"]),
            "holdout_shuffle_p": float(sh.loc["holdout", "empirical_p_upper"]),
            "gates_passed": int(result["gates_passed"]),
            "gates_total": int(result["gates_total"]),
        }
    ]

    gate_rows = pd.DataFrame(
        [{"gate": name.replace("_", " "), "passed": int(passed), "result": "PASS" if passed else "FAIL"} for name, passed in result["gates"].items()]
    )

    witness_bar = witnesses.dropna().copy()
    witness_bar["label"] = witness_bar.cohort + " — " + witness_bar.witness.map(
        {
            "log_size_change": "size change",
            "log_rpl13a_concentration_change": "Rpl13A concentration change",
            "log_rpl13a_total_change": "total Rpl13A change",
        }
    )

    hold_cells = cells[cells.cohort.eq("holdout")].sort_values(["observed_g1_count", "cell_id"])
    example_ids = [hold_cells.iloc[0].cell_id, hold_cells.iloc[len(hold_cells) // 2].cell_id, hold_cells.iloc[-1].cell_id]
    examples = hold_cells[hold_cells.cell_id.isin(example_ids)].copy()

    source_data = {
        "id": "yeast_s1_workbook",
        "label": "Janssens and Veenhoff 2016 S1 single-cell life-history workbook",
        "href": "https://doi.org/10.1371/journal.pone.0167394",
        "query": {
            "language": "python",
            "description": "The published S1 workbook was parsed without imputation. Phase A uses generation order only; Phase B uses recorded cumulative hours only. Population curves interpolate each individual to the frozen 0–2 grid before taking medians.",
            "executed_at": timestamp,
            "tables_used": ["S1 File Table a", "S1 File Table b", "S1 File Table c", "S1 File Table d", "S1 File Table e"],
            "filters": ["at least three aligned G1 observations", "positive first-to-last observed span", "no role or scale refit on experiment 9 or experiments 1–6"],
            "metric_definitions": [
                "Maturity A = 2 × ordered generation index ÷ final ordered generation index.",
                "Elapsed time B = 2 × cumulative hours ÷ first-to-last observed G1 hours.",
                "Remaining time B = 2 − elapsed time B; signed time shadow = elapsed time B − maturity A.",
                "Local time rate = division interval ÷ the same cell's mean division interval.",
                "Local time child ARA = 2r/(1+r), a monotone display map with r=1 at ARA ridge 1.",
            ],
        },
    }
    source_paper = {
        "id": "yeast_paper",
        "label": "The Natural Variation in Lifespans of Single Yeast Cells Is Related to Variation in Cell Size, Ribosomal Protein, and Division Time",
        "href": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5132237/",
        "query": {
            "language": "document",
            "description": "Peer-reviewed source for organism, microfluidic conditions, 20-minute imaging, G1 measurement, death definition, omitted terminal image, cohort differences, Rpl13A interpretation, and Senescence Entry Point context.",
        },
    }

    cards = [
        {"id": "cells", "description": "All eligible published mother-cell life histories across both datasets.", "dataset": "headline", "sourceId": "yeast_s1_workbook", "metrics": [{"label": "Cells", "field": "cells", "format": "number"}]},
        {"id": "holdout_r", "description": "Interior time-shadow curve correlation; experiment 9 was untouched.", "dataset": "headline", "sourceId": "yeast_s1_workbook", "metrics": [{"label": "Holdout shadow r", "field": "holdout_shadow_correlation", "format": "number"}]},
        {"id": "external_r", "description": "Interior time-shadow correlation on the separate 119-cell/device cohort.", "dataset": "headline", "sourceId": "yeast_s1_workbook", "metrics": [{"label": "External shadow r", "field": "external_shadow_correlation", "format": "number"}]},
        {"id": "cross_dev", "description": "Development median local division-time child crosses its equal-rate ridge.", "dataset": "headline", "sourceId": "yeast_s1_workbook", "metrics": [{"label": "Development crossing A", "field": "development_crossing_A", "format": "number"}]},
        {"id": "cross_hold", "description": "Untouched experiment-9 crossing on the same maturity scale.", "dataset": "headline", "sourceId": "yeast_s1_workbook", "metrics": [{"label": "Holdout crossing A", "field": "holdout_crossing_A", "format": "number"}]},
        {"id": "cross_ext", "description": "Separate-platform crossing on the same maturity scale.", "dataset": "headline", "sourceId": "yeast_s1_workbook", "metrics": [{"label": "External crossing A", "field": "external_crossing_A", "format": "number"}]},
    ]

    def line_chart(chart_id, title, subtitle, dataset, y_label):
        return {
            "id": chart_id,
            "title": title,
            "subtitle": subtitle,
            "type": "line",
            "dataset": dataset,
            "sourceId": "yeast_s1_workbook",
            "encodings": {
                "x": {"field": "grid_A", "type": "quantitative", "label": "Reproductive maturity A (0–2)"},
                "y": {"field": "median", "type": "quantitative", "label": y_label},
                "color": {"field": "cohort", "type": "nominal", "label": "Frozen cohort"},
                "tooltip": [
                    {"field": "q25", "type": "quantitative", "label": "25th percentile"},
                    {"field": "q75", "type": "quantitative", "label": "75th percentile"},
                    {"field": "n", "type": "quantitative", "label": "Cells"},
                ],
            },
            "layout": "full",
        }

    charts = [
        {
            "id": "raw_lifespan",
            "title": "Observed reproductive span in generations and hours",
            "subtitle": "One point per mother cell; hours cover first to last numeric G1, not the omitted death image.",
            "type": "scatter",
            "dataset": "cells",
            "sourceId": "yeast_s1_workbook",
            "encodings": {
                "x": {"field": "observed_g1_count", "type": "quantitative", "label": "Observed G1 measurements"},
                "y": {"field": "lifespan_hours_observed", "type": "quantitative", "label": "First-to-last observed G1 span (hours)"},
                "color": {"field": "cohort", "type": "nominal", "label": "Frozen cohort"},
                "tooltip": [{"field": "cell_id", "type": "nominal", "label": "Cell"}, {"field": "experiment", "type": "nominal", "label": "Experiment"}],
            },
            "layout": "full",
        },
        line_chart("elapsed_phase", "Elapsed clock phase against generation-built maturity", "The dashed pure line is described in the adjacent text; all three medians bow below equal progress.", "elapsed_curve", "Elapsed clock B (0–2)"),
        line_chart("te_sum", "Counter-traversing TE-ARA allocation", "Pure same-slice closure is A maturity + B remaining = 2; values above 2 are a signed distortion, not extra energy.", "te_sum_curve", "A maturity + B remaining-time"),
        line_chart("time_shadow", "Signed clock-time shadow across reproductive maturity", "B_elapsed − A; both endpoints are forced to zero and are not evidence.", "shadow_curve", "Signed time shadow"),
        line_chart("local_rate", "Local division-time child across reproductive maturity", "Raw division interval divided by the same cell's mean; equal-rate ridge is 1.", "rate_curve", "Division interval ÷ cell mean"),
        line_chart("local_ara", "Local division-time child on the ARA 0–2 display", "The monotone reciprocal map 2r/(1+r) puts equal rate at ridge 1 without changing order.", "rate_ara_curve", "Local time child ARA"),
        line_chart("size_witness", "Cell-size witness across reproductive maturity", "Area relative to each cell's first observed G1; measured independently of clock time.", "size_curve", "Cell area ÷ starting area"),
        line_chart("rpl_concentration", "Rpl13A-GFP concentration witness", "Only experiments 7–9 measured this channel; the external cohort is correctly absent.", "rpl_concentration_curve", "Concentration ÷ starting value"),
        line_chart("rpl_total", "Derived total Rpl13A-GFP abundance witness", "Cell area × average concentration, relative to the first observed G1.", "rpl_total_curve", "Area × concentration fold"),
        {
            "id": "witness_alignment",
            "title": "Same-maturity witness alignment with the local time child",
            "subtitle": "Descriptive correlations of population-median change curves; shared late-life curvature can inflate them.",
            "type": "bar",
            "dataset": "witness_alignment",
            "sourceId": "yeast_s1_workbook",
            "encodings": {"x": {"field": "label", "type": "nominal", "label": "Cohort and witness"}, "y": {"field": "same_A_curve_correlation_with_local_time_rate", "type": "quantitative", "label": "Curve correlation"}},
            "layout": "full",
        },
    ]

    tables = [
        {
            "id": "cohort_scope",
            "title": "Frozen cohort scope and raw lifespan summary",
            "subtitle": "Development, same-platform holdout, and different-platform external cohort remain separate throughout.",
            "dataset": "cohort_summary",
            "sourceId": "yeast_s1_workbook",
            "defaultSort": {"field": "cohort", "direction": "asc"},
            "columns": [
                {"field": "cohort", "label": "Role"}, {"field": "cells", "label": "Cells", "format": "number"},
                {"field": "median_observed_g1", "label": "Median G1 count", "format": "number"},
                {"field": "median_lifespan_hours", "label": "Median observed hours", "format": "number"},
                {"field": "median_mean_interval_hours", "label": "Median mean interval h", "format": "number"},
                {"field": "median_late_minus_early_rate", "label": "Median late−early rate", "format": "number"},
            ],
            "layout": "full",
        },
        {
            "id": "transfer_table",
            "title": "Frozen curve-transfer metrics",
            "subtitle": "Correlations use only interior A=0.10–1.90, excluding the two forced zero endpoints.",
            "dataset": "transfer",
            "sourceId": "yeast_s1_workbook",
            "defaultSort": {"field": "comparison", "direction": "asc"},
            "columns": [
                {"field": "metric", "label": "Curve"}, {"field": "comparison", "label": "Comparison"},
                {"field": "correlation", "label": "Correlation", "format": "number"}, {"field": "rmse", "label": "RMSE", "format": "number"},
                {"field": "mae", "label": "MAE", "format": "number"}, {"field": "grid_points", "label": "Interior points", "format": "number"},
            ],
            "layout": "full",
        },
        {
            "id": "landmark_table",
            "title": "Ridge crossing and shadow-minimum landmarks",
            "subtitle": "The local-rate crossing and accumulated-shadow minimum are related but not identical measurements.",
            "dataset": "landmarks",
            "sourceId": "yeast_s1_workbook",
            "defaultSort": {"field": "cohort", "direction": "asc"},
            "columns": [
                {"field": "cohort", "label": "Role"}, {"field": "local_rate_upcrossing_A", "label": "Rate crosses 1 at A", "format": "number"},
                {"field": "time_shadow_minimum_A", "label": "Shadow minimum A", "format": "number"}, {"field": "time_shadow_minimum", "label": "Shadow depth", "format": "number"},
            ],
            "layout": "full",
        },
        {
            "id": "shuffle_table",
            "title": "Within-cell interval-order controls",
            "subtitle": "Each shuffle preserves every interval, total hours, and division count but destroys age order.",
            "dataset": "shuffles",
            "sourceId": "yeast_s1_workbook",
            "defaultSort": {"field": "cohort", "direction": "asc"},
            "columns": [
                {"field": "cohort", "label": "Role"}, {"field": "cells", "label": "Cells", "format": "number"},
                {"field": "observed_median_late_minus_early", "label": "Observed late−early", "format": "number"},
                {"field": "null_q95", "label": "Shuffle 95%", "format": "number"}, {"field": "empirical_p_upper", "label": "Empirical p", "format": "number"},
            ],
            "layout": "full",
        },
        {
            "id": "gate_table",
            "title": "Frozen gate ledger",
            "subtitle": "Gate outcomes preserve the pre-result contract; the report still prioritizes full curves and limitations.",
            "dataset": "gates",
            "sourceId": "yeast_s1_workbook",
            "defaultSort": {"field": "gate", "direction": "asc"},
            "columns": [{"field": "gate", "label": "Frozen gate"}, {"field": "result", "label": "Result"}],
            "layout": "full",
        },
        {
            "id": "individual_examples",
            "title": "Deterministic untouched-cell examples",
            "subtitle": "Shortest, median, and longest experiment-9 reproductive spans; full trajectories are in the supporting PNG.",
            "dataset": "examples",
            "sourceId": "yeast_s1_workbook",
            "defaultSort": {"field": "observed_g1_count", "direction": "asc"},
            "columns": [
                {"field": "cell_id", "label": "Cell"}, {"field": "observed_g1_count", "label": "G1 count", "format": "number"},
                {"field": "lifespan_hours_observed", "label": "Observed hours", "format": "number"},
                {"field": "shadow_min_A", "label": "Own shadow minimum A", "format": "number"}, {"field": "late_minus_early_rate", "label": "Own late−early rate", "format": "number"},
            ],
            "layout": "full",
        },
    ]

    sources = [source_data, source_paper]
    blocks = [
        {"id": "title", "type": "markdown", "body": "# Yeast lifespan Phase A–B reconstruction"},
        {"id": "summary", "type": "markdown", "sourceId": "yeast_s1_workbook", "body": "## Technical summary\n\n**A generation-built maturity phase and a clock-built time phase recover the same bowed interior path in three frozen cohorts.** The untouched experiment-9 time-shadow curve correlates `0.985` with development, and the separate 119-cell/platform cohort also correlates `0.985`. The local division-time child crosses its equal-rate ridge at maturity `A=1.455` in development, `1.404` in the holdout, and `1.453` externally. Within-cell interval shuffling cannot reproduce the late-versus-early rise (`p=1/2001` for both validation cohorts). This is strong evidence for a transferable **completed-lifespan handover geometry**, not evidence that the coordinate is time itself or that death can yet be predicted prospectively."},
        {"id": "metrics", "type": "metric-strip", "cardIds": [c["id"] for c in cards]},
        {"id": "address", "type": "markdown", "body": "## The exact ARA address used\n\nThe **parent identity** is one mother cell's observed reproductive lifespan/time relation. **Child Phase A** is reproductive maturity built only from ordered generation count. **Child Phase B** is clock traversal built only from recorded hours. Cell area and Rpl13A are lower children/witnesses; division interval is the local construction of the clock child and is therefore not independent confirmation. The elapsed display uses both coordinates rising `0→2`; the counter-traversing view uses remaining time falling `2→0`. They are algebraically equivalent, so chart orientation cannot manufacture the result."},
        {"id": "raw_text", "type": "markdown", "sourceId": "yeast_s1_workbook", "body": "## Raw hours and generations remain visibly distinct\n\nA long reproductive lifespan can arise from more observed divisions, longer intervals, or both. The scatter preserves those raw quantities before normalization. The numeric endpoint is the last observed G1 before the omitted death image, so the analysis does not claim an exact physical-death timestamp."},
        {"id": "raw_chart", "type": "chart", "chartId": "raw_lifespan", "layout": "full"},
        {"id": "scope_table_block", "type": "table", "tableId": "cohort_scope", "layout": "full"},
        {"id": "phase_text", "type": "markdown", "sourceId": "yeast_s1_workbook", "body": "## The counter-phase relation produces a stable bowed shadow\n\nEqual normalized progress would follow `B_elapsed=A`, equivalently `A+B_remaining=2`. Instead, reproductive maturity runs ahead of elapsed-time fraction through most of the observed life: `B_elapsed−A` is negative and the counter-phase sum is above 2. Every path is forced to start and end on the reference, so those endpoints carry no evidence. The interior depth and its cross-cohort replication carry the result."},
        {"id": "elapsed_chart", "type": "chart", "chartId": "elapsed_phase", "layout": "full"},
        {"id": "te_chart", "type": "chart", "chartId": "te_sum", "layout": "full"},
        {"id": "shadow_chart", "type": "chart", "chartId": "time_shadow", "layout": "full"},
        {"id": "transfer_table_block", "type": "table", "tableId": "transfer_table", "layout": "full"},
        {"id": "child_text", "type": "markdown", "sourceId": "yeast_s1_workbook", "body": "## A local time child turns through its ridge near A≈1.4–1.46\n\nThe local child is each division interval divided by that cell's own mean. It stays below the equal-rate ridge through early and middle life, crosses upward late, and then rises sharply. The reciprocal `2r/(1+r)` panel is only the same positive ratio on a bounded ARA display. Shuffling interval order preserves every interval and endpoint yet destroys the rise, so this landmark is not a consequence of lifespan normalization alone."},
        {"id": "rate_chart", "type": "chart", "chartId": "local_rate", "layout": "full"},
        {"id": "rate_ara_chart", "type": "chart", "chartId": "local_ara", "layout": "full"},
        {"id": "landmark_table_block", "type": "table", "tableId": "landmark_table", "layout": "full"},
        {"id": "shuffle_table_block", "type": "table", "tableId": "shuffle_table", "layout": "full"},
        {"id": "witness_text", "type": "markdown", "sourceId": "yeast_s1_workbook", "body": "## Independent biological children turn with the late-life clock slowdown\n\nCell area rises throughout life and accelerates late in all three cohorts. Rpl13A-GFP concentration generally falls, while derived total abundance begins rising as the enlarging cell outweighs that dilution. Their median change curves align with the local clock child, including holdout correlations of `0.597` for size change, `0.757` for concentration change, and `0.842` for total-abundance change. These are independent measurements but still descriptive witnesses: shared late-life curvature and common aging mechanisms can produce alignment without making any witness identical to Time."},
        {"id": "size_chart", "type": "chart", "chartId": "size_witness", "layout": "full"},
        {"id": "rplc_chart", "type": "chart", "chartId": "rpl_concentration", "layout": "full"},
        {"id": "rplt_chart", "type": "chart", "chartId": "rpl_total", "layout": "full"},
        {"id": "witness_align_chart", "type": "chart", "chartId": "witness_alignment", "layout": "full"},
        {"id": "science", "type": "markdown", "sourceId": "yeast_paper", "body": "## Scientific crosswalk: this resembles late-life replicative senescence\n\nThe source study already reports that division times lengthen, cell size increases, Rpl13A concentration changes with replicative age, and individual cells can enter a late-life **Senescence Entry Point (SEP)** identified from an elbow in cell-cycle duration. T452 did not import the authors' SEP calls. It independently constructed an ARA maturity/time relation and recovered a population ridge crossing in the same biological territory. The ARA contribution here is the shared normalized relational geometry and its transfer across cohorts; the existence of late-life division slowdown is established biology, not a new discovery."},
        {"id": "methods", "type": "markdown", "sourceId": "yeast_s1_workbook", "body": "## Method and robustness\n\nExperiments 7–8 (`n=94`) define all population curves. Experiment 9 (`n=12`) remains an untouched same-device holdout. Experiments 1–6 (`n=119`) use a different microfluidic design and mixed GFP strains and form an external core-geometry test. Each individual is interpolated to a fixed `0–2` maturity grid before cohort medians are calculated. Curve correlations exclude `A<0.10` and `A>1.90`. Two thousand deterministic within-cell shuffles preserve every interval, number of divisions, and total observed hours. Six prewritten gates passed, but the complete curves and uncertainty remain primary."},
        {"id": "gate_table_block", "type": "table", "tableId": "gate_table", "layout": "full"},
        {"id": "individual_text", "type": "markdown", "sourceId": "yeast_s1_workbook", "body": "## Population geometry does not erase individual asymmetry\n\nThe holdout contains only 12 cells and individual paths are much less smooth than the median. The deterministic short, median, and long examples are retained below; the supporting individual figure shows their full phase paths, shadows, local rates, size, and fluorescence. A landmark near `1.4–1.46` is a population ridge, not a speed limit every cell must hit exactly."},
        {"id": "individual_table_block", "type": "table", "tableId": "individual_examples", "layout": "full"},
        {"id": "limits", "type": "markdown", "body": "## What the result does not establish\n\n- The analysis uses each completed observed span to scale both axes, so it cannot yet predict death from partial life data.\n- The two endpoint closures are mathematical consequences of normalization.\n- The last numeric G1 precedes the omitted death image; terminal time has an unresolved gap of up to the observation process and cell-specific terminal interval.\n- The external cohort differs in device and GFP strains; its strong transfer supports the core shape but does not isolate which biological mechanism causes it.\n- Rpl13A exists only for experiments 7–9.\n- A transferable time-facing shadow is not proof of a universal Time wave, subjective time, or a new physical law."},
        {"id": "next", "type": "markdown", "body": "## Recommended next test\n\nFreeze the development `A≈1.455` crossing and the full shadow/rate curves, then attempt a **partial-life forecast**: use only observations available up to successive maturity fractions to predict the onset of sustained `r>1` and the remaining number of divisions on untouched cells. That would test whether this completed-life geometry carries prospective information. In parallel, repeat the same relational construction on a second organism or single-cell lifespan source with an explicit birth and death timestamp; only a cross-scale transfer can begin the proposed broader time-wave comparison."},
        {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Does the ridge crossing predict a cell-specific SEP when the author's per-cell elbow method is reconstructed?\n- Does a three-cut witness using size, concentration, and total abundance improve partial-life prediction beyond division intervals alone?\n- How much does the unrecorded terminal interval move the shadow minimum and ridge crossing?\n- Does the same curve survive a genuinely different species after only scale and orientation are declared?"},
    ]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "Yeast lifespan Phase A–B reconstruction",
        "description": "Generation-built maturity versus clock-built traversal across 225 published single yeast lifespans.",
        "generatedAt": timestamp,
        "cards": cards,
        "charts": charts,
        "tables": tables,
        "sources": sources,
        "blocks": blocks,
    }

    # The portable report contract requires every rendered widget to expose
    # the exact bounded snapshot query behind it, in addition to the workbook
    # provenance carried by sourceId.
    for widget_group in (cards, charts, tables):
        for widget in widget_group:
            dataset = widget["dataset"]
            widget["source"] = {
                "id": f"t452_{dataset}",
                "label": f"T452 reviewed snapshot — {dataset}",
                "href": "https://doi.org/10.1371/journal.pone.0167394",
                "query": {
                    "language": "sql",
                    "sql": f"SELECT * FROM {dataset};",
                    "description": f"Return the complete reviewed {dataset} rows embedded in this T452 report snapshot.",
                    "executed_at": timestamp,
                    "tables_used": [dataset],
                    "filters": source_data["query"]["filters"],
                    "metric_definitions": source_data["query"]["metric_definitions"],
                },
            }

    datasets = {
        "headline": headline,
        "cells": records(cells[["cohort", "experiment", "cell_id", "observed_g1_count", "lifespan_hours_observed", "mean_division_interval_hours"]]),
        "cohort_summary": records(cohort),
        "transfer": records(transfer),
        "landmarks": records(landmarks),
        "shuffles": records(shuffles),
        "gates": records(gate_rows),
        "examples": records(examples),
        "elapsed_curve": curve_dataset(gen, "time_elapsed_B"),
        "te_sum_curve": curve_dataset(gen, "te_ara_sum"),
        "shadow_curve": curve_dataset(gen, "time_shadow"),
        "rate_curve": curve_dataset(rate, "local_time_rate"),
        "rate_ara_curve": curve_dataset(rate, "local_time_ara"),
        "size_curve": curve_dataset(gen, "size_fold"),
        "rpl_concentration_curve": curve_dataset(gen, "rpl13a_concentration_fold", ["development", "holdout"]),
        "rpl_total_curve": curve_dataset(gen, "rpl13a_total_fold", ["development", "holdout"]),
        "witness_alignment": records(witness_bar[["label", "cohort", "witness", "same_A_curve_correlation_with_local_time_rate"]]),
    }

    snapshot = {"version": 1, "generatedAt": timestamp, "status": "ready", "datasets": datasets}
    artifact = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
    (RESULTS / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(json.dumps({"blocks": len(blocks), "charts": len(charts), "tables": len(tables), "datasets": {k: len(v) for k, v in datasets.items()}}, indent=2))


if __name__ == "__main__":
    main()
