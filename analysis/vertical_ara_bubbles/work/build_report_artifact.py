from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


TITLE = "Vertical ARA Bubble Handover Test"
SOURCE_ID = "zenodo-bubble-dynamics"


def read_csv(path):
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value):
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (TypeError, ValueError):
        return None


def main(results_dir: str, output_path: str):
    results = Path(results_dir)
    summary = json.loads((results / "vertical_ara_summary.json").read_text(encoding="utf-8"))
    events = read_csv(results / "vertical_ara_bubble_events.csv")
    targets = read_csv(results / "vertical_ara_target_results.csv")

    primary_events = [row for row in events if row["detector"] == "primary" and row["split"] in ("evaluation", "holdout")]
    scatter = []
    for row in primary_events:
        child_ratio = number(row["child_ratio"])
        scatter.append({
            "event": f'{row["video"]}:{row["frame"]}',
            "split": row["split"],
            "child_ratio": child_ratio,
            "log_child_ratio": math.log(child_ratio),
            "parent_ratio": number(row["parent_ratio"]),
            "closure": number(row["closure"]),
            "circularity_tension": number(row["circularity_tension"]),
            "settle_sec": number(row["settle_sec"]),
            "parent_life_sec": number(row["parent_life_sec"]),
            "amplitude": number(row["amplitude"]),
            "umf": number(row["umf"]),
        })

    holdout_tension = [
        row for row in targets
        if row["detector"] == "primary" and row["split"] == "holdout" and row["metric"] == "circularity_tension"
    ]
    label_map = {
        "one": "1",
        "sqrt2": "sqrt(2)",
        "three_halves": "1.5",
        "phi": "Phi",
        "two": "2",
        "free_evaluation_optimum": "Free optimum",
    }
    ratio_map = {
        "one": 1.0,
        "sqrt2": math.sqrt(2),
        "three_halves": 1.5,
        "phi": (1 + math.sqrt(5)) / 2,
        "two": 2.0,
    }
    target_table = []
    for row in holdout_tension:
        key = row["target"]
        target_table.append({
            "target": label_map[key],
            "ratio": number(row.get("fitted_ratio")) if key == "free_evaluation_optimum" else ratio_map[key],
            "holdout_rho": number(row["rho_expected_positive"]),
            "blocked_p": number(row["blocked_p_one_sided"]),
            "holdout_n": int(float(row["n"])),
        })

    detector_table = []
    for detector in ("strict", "primary", "broad"):
        event_summary = summary["event_summaries"][detector]
        detector_table.append({
            "detector": detector,
            "evaluation_events": event_summary["evaluation"]["events"],
            "holdout_events": event_summary["holdout"]["events"],
            "near_phi_both_legs": sum(event_summary[split]["near_phi_20pct_both_legs"] for split in ("calibration", "evaluation", "holdout")),
            "evaluation_min_child_ratio": event_summary["evaluation"]["child_ratio"]["min"],
            "holdout_min_child_ratio": event_summary["holdout"]["child_ratio"]["min"],
        })

    headline = [{
        "near_phi_broad": 0,
        "broad_total": sum(sum(summary["detector_counts"]["broad"].values()) for _ in [0]),
        "primary_evaluation": summary["detector_counts"]["primary"]["evaluation"],
        "primary_holdout": summary["detector_counts"]["primary"]["holdout"],
        "holdout_tension_rho": 0.44912280701754387,
        "holdout_settle_rho": -0.13892999754474641,
    }]

    source = {
        "id": SOURCE_ID,
        "label": "Bubble dynamics data for oscillating gas flow in a quasi-2D fluidized bed",
        "href": "https://doi.org/10.5281/zenodo.15102957",
        "query": {
            "sql": "SELECT * FROM read_csv_auto('results/vertical_ara_bubble_events.csv') WHERE detector = 'primary' AND split IN ('evaluation', 'holdout');\nSELECT * FROM read_csv_auto('results/vertical_ara_target_results.csv');",
            "description": "Thirty-five public 50 fps contour CSVs; direct lineages reconstructed from adjacent frames with a detector frozen on V01-V07.",
            "engine": "Python",
            "language": "python",
            "executed_at": "2026-08-01",
            "tables_used": ["Zenodo 10.5281/zenodo.15102957 data.zip — 35 CSV files"],
            "filters": [
                "Calibration V01-V07; evaluation V08-V28; untouched holdout V29-V35",
                "Primary detector: direct two-child-to-one-parent adjacent-frame lineages",
                "Near-Phi: both vertical legs within 20% of Phi",
            ],
            "metric_definitions": [
                "child ratio = larger child area / smaller child area",
                "parent ratio = parent area / larger child area",
                "vertical target distance = root-sum-square of log deviations of both ratios from the target",
                "circularity tension = mean absolute step change in parent circularity divided by median parent circularity",
                "settling time = first three-frame window within 10% of the final three-frame circularity median",
                "blocked p-values permute outcomes within video and test the frozen positive direction",
            ],
        },
    }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Technical report of a frozen direct-lineage test of Phi as a vertical ARA handover relation.",
        "generatedAt": "2026-08-01T00:00:00+10:00",
        "sources": [source],
        "cards": [
            {
                "id": "card-near-phi",
                "dataset": "headline",
                "metrics": [
                    {"label": "Near-Phi families", "field": "near_phi_broad", "format": "number"},
                    {"label": "broad total", "field": "broad_total", "format": "number"},
                ],
                "sourceId": SOURCE_ID,
            },
            {
                "id": "card-primary-samples",
                "dataset": "headline",
                "metrics": [
                    {"label": "Primary evaluation", "field": "primary_evaluation", "format": "number"},
                    {"label": "holdout", "field": "primary_holdout", "format": "number"},
                ],
                "sourceId": SOURCE_ID,
            },
            {
                "id": "card-holdout-directions",
                "dataset": "headline",
                "metrics": [
                    {"label": "Holdout tension rho", "field": "holdout_tension_rho", "format": "number", "signed": True},
                    {"label": "settling rho", "field": "holdout_settle_rho", "format": "number", "signed": True},
                ],
                "sourceId": SOURCE_ID,
            },
        ],
        "charts": [
            {
                "id": "chart-lineage-ratios",
                "title": "Direct-lineage area ratios",
                "description": "Primary evaluation and holdout events; each point is one two-child-to-one-parent family.",
                "type": "scatter",
                "dataset": "lineage_scatter",
                "encodings": {
                    "x": {"field": "log_child_ratio", "type": "quantitative", "title": "ln(larger child / smaller child)"},
                    "y": {"field": "parent_ratio", "type": "quantitative", "title": "parent / larger child"},
                    "color": {"field": "split", "type": "nominal", "title": "split"},
                },
                "sourceId": SOURCE_ID,
            },
        ],
        "tables": [
            {
                "id": "table-targets",
                "title": "Holdout tension comparison",
                "description": "Every fixed target ranks the holdout identically because all observed child ratios exceed the target range.",
                "dataset": "target_comparison",
                "columns": [
                    {"field": "target", "label": "Target", "type": "text"},
                    {"field": "ratio", "label": "Ratio", "type": "number", "format": "0.000"},
                    {"field": "holdout_rho", "label": "Holdout rho", "type": "number", "format": "0.000"},
                    {"field": "blocked_p", "label": "Blocked p", "type": "number", "format": "0.000"},
                    {"field": "holdout_n", "label": "n", "type": "number", "format": "0"},
                ],
                "defaultSort": {"field": "ratio", "direction": "asc"},
                "sourceId": SOURCE_ID,
            },
            {
                "id": "table-detectors",
                "title": "Lineage-detector sensitivity",
                "description": "Strict, primary and broad identity rules all miss the near-Phi neighbourhood.",
                "dataset": "detector_summary",
                "columns": [
                    {"field": "detector", "label": "Detector", "type": "text"},
                    {"field": "evaluation_events", "label": "Evaluation", "type": "number", "format": "0"},
                    {"field": "holdout_events", "label": "Holdout", "type": "number", "format": "0"},
                    {"field": "near_phi_both_legs", "label": "Near-Phi", "type": "number", "format": "0"},
                    {"field": "evaluation_min_child_ratio", "label": "Min eval ratio", "type": "number", "format": "0.00"},
                    {"field": "holdout_min_child_ratio", "label": "Min holdout ratio", "type": "number", "format": "0.00"},
                ],
                "defaultSort": {"field": "evaluation_events", "direction": "asc"},
                "sourceId": SOURCE_ID,
            },
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
            {"id": "technical-summary", "type": "markdown", "sourceId": SOURCE_ID, "body": "## Technical summary\n\n**The frozen bubble test does not support Phi as the specific vertical handover ratio in this dataset.** The primary detector recovered 58 evaluation and 19 untouched-holdout direct families, but none occupied the near-Phi neighbourhood. The registered settling-time association was weak in evaluation (rho = 0.087, p = 0.299) and reversed in holdout (rho = -0.139, p = 0.630). A holdout association with circularity tension was present (rho = 0.449, p = 0.026), but every target from 1 through 2 produced the same ranking. That is evidence for a generic size-asymmetry relation, not Phi specificity."},
            {"id": "headline-strip", "type": "metric-strip", "cardIds": ["card-near-phi", "card-primary-samples", "card-holdout-directions"]},
            {"id": "finding-ratios", "type": "markdown", "sourceId": SOURCE_ID, "body": "## The observed families are asymmetric absorptions, not golden closures\n\nThe conservative evaluation families had child-area ratios from 4.34 to 263.35 (median 31.99), while the parent-to-large-child ratio stayed near one (median 0.982). The new parent therefore usually retained the large child's scale while absorbing a much smaller contour. The chart uses the natural logarithm on the horizontal axis only to keep the full range visible."},
            {"id": "ratio-chart", "type": "chart", "chartId": "chart-lineage-ratios"},
            {"id": "finding-controls", "type": "markdown", "sourceId": SOURCE_ID, "body": "## The holdout smoothness signal cannot identify Phi\n\nFarther-from-target events had more parent circularity variation in the holdout, but all fixed targets received exactly rho = 0.449. Because every child ratio sat above the complete 1-to-2 comparison range, changing the target did not change event order. The free evaluation optimum for this outcome was 1.0, not Phi. This prevents the generic association from being claimed as a golden-ratio result."},
            {"id": "targets-table", "type": "table", "tableId": "table-targets"},
            {"id": "scope-definitions", "type": "markdown", "sourceId": SOURCE_ID, "body": "## Scope, data and definitions\n\nThe source contains 35 one-minute quasi-2D fluidized-bed runs sampled at 50 fps. V01-V07 calibrated identity reconstruction without inspecting Phi or outcomes; V08-V28 formed the evaluation set; V29-V35 were untouched holdouts. Vertical ARA was operationalized as a direct same-lineage scale transition: two tracked child bubbles at one slice becoming one persistent parent at the next. Temporal recurrence is the same branch followed across successive 0.02-second slices. Size is measured by observed 2D contour area."},
            {"id": "method", "type": "markdown", "sourceId": SOURCE_ID, "body": "## Frozen model and outcome tests\n\nFor each family, the two vertical legs were larger-child/smaller-child and parent/larger-child. Target distance was the root-sum-square of their logarithmic deviations from a proposed constant. Phi, 1, sqrt(2), 1.5 and 2 were fixed competitors; a free target was selected only on evaluation data. Parent settling, circularity tension and persistence were tested. One-sided p-values came from 5,000 outcome permutations blocked within video. Identity thresholds were checked with strict and broad detectors."},
            {"id": "robustness", "type": "markdown", "sourceId": SOURCE_ID, "body": "## Robustness checks strengthen the negative specificity result\n\nStrict, primary and broad detectors recovered 14, 103 and 249 total families respectively. None placed both vertical legs within 20% of Phi. The strict holdout was too small for inference, while the broad detector repeated the generic tension association and the same inability to distinguish constants. Parent persistence also failed the frozen direction in the primary holdout (rho = -0.398, p = 0.931)."},
            {"id": "detector-table", "type": "table", "tableId": "table-detectors"},
            {"id": "limitations", "type": "markdown", "body": "## What this result does and does not establish\n\nThis is a failed confirmatory test of the **area-ratio version** of the Phi handover hypothesis in one bubble population. It does not falsify Vertical ARA as a general same-lineage concept, nor does it test whether Phi lies in handover timing, boundary motion or a different phase coordinate. The source provides processed contours rather than merger-labelled video, so family identities are conservative inferences. Tracks are short at high flow, the geometry is quasi-2D, and the dataset scarcely samples balanced mergers."},
            {"id": "next-steps", "type": "markdown", "body": "## The next test needs controlled lineage ratios\n\nUse a coalescence dataset with labelled child-parent events and deliberately varied initial size ratios spanning 1 to 2, including dense coverage around Phi. Freeze the outcome as post-merger relaxation or re-separation before exposing results. Keep temporal handover and vertical scale inheritance as separate coordinates, then test whether one common Phi relation predicts both."},
            {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Does Phi belong to size closure, handover timing, or the boundary path connecting same-phase states?\n- Do controlled droplets or bubbles show a local optimum near Phi once the ratio neighbourhood is actually sampled?\n- Does the same frozen timing coordinate replicate in a second direct lineage such as erosion tributaries or a biological family tree?"},
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": "2026-08-01T00:00:00+10:00",
            "datasets": {
                "headline": headline,
                "lineage_scatter": scatter,
                "target_comparison": target_table,
                "detector_summary": detector_table,
            },
        },
        "sources": [source],
    }
    output = Path(output_path)
    output.write_text(json.dumps(artifact, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(artifact, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
