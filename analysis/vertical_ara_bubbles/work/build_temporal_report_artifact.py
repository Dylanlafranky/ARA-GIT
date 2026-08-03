from __future__ import annotations

import json
import math
import sys
from pathlib import Path


TITLE = "Vertical ARA Temporal Handover Test"
SOURCE_ID = "zenodo-bubble-temporal-trajectories"


def main(results_dir: str, output_path: str) -> None:
    results = Path(results_dir)
    summary = json.loads((results / "temporal_ara_summary.json").read_text(encoding="utf-8"))
    label_map = {
        "one": "1",
        "sqrt2": "sqrt(2)",
        "three_halves": "1.5",
        "phi": "Phi",
        "two": "2",
        "free_calibration": "Free calibration",
    }

    joint_targets = []
    direct_targets = []
    for split in ("evaluation", "holdout"):
        for name, record in summary["splits"][split]["targets"].items():
            joint_targets.append({
                "split": split,
                "target": label_map[name],
                "target_value": record["target_value"],
                "mean_distance": record["mean_distance"],
                "median_distance": record["median_distance"],
                "windows": record["windows"],
            })
        for name, record in summary["post_protocol_audit"][split]["direct_targets"].items():
            direct_targets.append({
                "split": split,
                "target": label_map[name],
                "target_value": record["target_value"],
                "mean_distance": record["mean_direct_distance"],
                "median_distance": record["median_direct_distance"],
                "windows": summary["splits"][split]["windows"],
            })

    equality_rows = []
    for split in ("evaluation", "holdout"):
        audit = summary["post_protocol_audit"][split]
        equality_rows.extend([
            {
                "split": split,
                "sequence": "Observed adjacent",
                "mean_equality_residual": audit["golden_equality_mean"],
                "median_equality_residual": audit["golden_equality_median"],
            },
            {
                "split": split,
                "sequence": "Within-track shift",
                "mean_equality_residual": audit["golden_equality_shift_mean"],
                "median_equality_residual": audit["golden_equality_shift_median"],
            },
        ])

    outcome_rows = []
    for split in ("evaluation", "holdout"):
        for name in ("one", "sqrt2", "three_halves", "phi", "two", "phi_shift_control", "phi_nonoverlap"):
            record = summary["outcomes"][split][name]
            outcome_rows.append({
                "split": split,
                "coordinate": label_map.get(name, name.replace("_", " ")),
                "rho": record["future_turn_spearman"],
                "one_sided_p": record["future_turn_one_sided_p"],
                "windows": record["inference_windows"],
            })

    headline = [{
        "eligible_windows": summary["diagnostics"]["eligible_windows"],
        "evaluation_windows": summary["splits"]["evaluation"]["windows"],
        "holdout_windows": summary["splits"]["holdout"]["windows"],
        "joint_free_target": summary["free_target_calibration"],
        "direct_free_target": summary["direct_free_target_calibration"],
        "evaluation_phi_rho": summary["outcomes"]["evaluation"]["phi"]["future_turn_spearman"],
        "evaluation_phi_p": summary["outcomes"]["evaluation"]["phi"]["future_turn_one_sided_p"],
    }]

    source = {
        "id": SOURCE_ID,
        "label": "Bubble dynamics data for oscillating gas flow in a quasi-2D fluidized bed",
        "href": "https://doi.org/10.5281/zenodo.15102957",
        "query": {
            "sql": "SELECT * FROM read_csv_auto('results/temporal_ara_target_results.csv');\nSELECT * FROM read_csv_auto('results/temporal_ara_window_sample.csv');",
            "description": "Five-slice windows reconstructed from public 50 fps tracker-assigned bubble centroids; target summaries and a deterministic review sample are retained locally.",
            "engine": "DuckDB",
            "language": "sql",
            "executed_at": "2026-08-01",
            "tables_used": [
                "Zenodo 10.5281/zenodo.15102957 — 35 contour CSV files",
                "results/temporal_ara_target_results.csv",
                "results/temporal_ara_window_sample.csv",
            ],
            "filters": [
                "Calibration V01-V07; evaluation V08-V28; untouched holdout V29-V35",
                "One tracker ID across five consecutive 0.02-second slices",
                "First two centroid steps at least 0.0005 m",
                "At most 250 deterministic windows per video for blocked permutation inference",
            ],
            "metric_definitions": [
                "joint distance = root-sum-square log distance of (a+b)/a and a/b from one target",
                "direct distance = absolute log distance of a/b from one target",
                "golden equality residual = absolute log of ((a+b)/a)/(a/b)",
                "future turn tension = angle between two reserved future displacement vectors divided by pi",
                "negative adjacent-minus-shift difference means consecutive slices lie closer to the tested relation",
            ],
        },
    }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": TITLE,
        "description": "Frozen and audited test of Phi in movement between successive observations of one bubble lineage.",
        "generatedAt": "2026-08-01T00:00:00+10:00",
        "sources": [source],
        "cards": [
            {
                "id": "card-windows",
                "dataset": "headline",
                "metrics": [
                    {"label": "Eligible windows", "field": "eligible_windows", "format": "number"},
                    {"label": "holdout", "field": "holdout_windows", "format": "number"},
                ],
                "sourceId": SOURCE_ID,
            },
            {
                "id": "card-targets",
                "dataset": "headline",
                "metrics": [
                    {"label": "Joint free target", "field": "joint_free_target", "format": "number"},
                    {"label": "direct free target", "field": "direct_free_target", "format": "number"},
                ],
                "sourceId": SOURCE_ID,
            },
            {
                "id": "card-outcome",
                "dataset": "headline",
                "metrics": [
                    {"label": "Evaluation Phi rho", "field": "evaluation_phi_rho", "format": "number", "signed": True},
                    {"label": "one-sided p", "field": "evaluation_phi_p", "format": "number"},
                ],
                "sourceId": SOURCE_ID,
            },
        ],
        "charts": [
            {
                "id": "chart-direct-targets",
                "title": "Direct movement-ratio distance",
                "description": "The fair one-coordinate audit places evaluation nearest sqrt(2) and holdout nearest 1.5; Phi is nearby but not best.",
                "type": "bar",
                "dataset": "direct_targets",
                "encodings": {
                    "x": {"field": "target", "type": "nominal", "title": "Frozen target"},
                    "y": {"field": "mean_distance", "type": "quantitative", "title": "Mean |ln(step ratio / target)|"},
                    "color": {"field": "split", "type": "nominal", "title": "Data split"},
                },
                "sourceId": SOURCE_ID,
            },
            {
                "id": "chart-equality",
                "title": "Golden-equality residual by temporal pairing",
                "description": "Adjacent slices approach the golden equality more closely than nonlocal movements from the same tracks in both evaluation and holdout.",
                "type": "bar",
                "dataset": "equality_comparison",
                "encodings": {
                    "x": {"field": "split", "type": "nominal", "title": "Data split"},
                    "y": {"field": "mean_equality_residual", "type": "quantitative", "title": "Mean golden-equality residual"},
                    "color": {"field": "sequence", "type": "nominal", "title": "Pairing"},
                },
                "sourceId": SOURCE_ID,
            },
        ],
        "tables": [
            {
                "id": "table-joint-targets",
                "title": "Frozen joint-ruler comparison",
                "description": "Phi is best among fixed landmarks, but the ruler's two equalities have Phi as their unique algebraic fixed point.",
                "dataset": "joint_targets",
                "columns": [
                    {"field": "split", "label": "Split", "type": "text"},
                    {"field": "target", "label": "Target", "type": "text"},
                    {"field": "target_value", "label": "Value", "type": "number", "format": "0.000000"},
                    {"field": "mean_distance", "label": "Mean joint distance", "type": "number", "format": "0.000000"},
                    {"field": "median_distance", "label": "Median", "type": "number", "format": "0.000000"},
                    {"field": "windows", "label": "Windows", "type": "number", "format": "0"},
                ],
                "defaultSort": {"field": "mean_distance", "direction": "asc"},
                "sourceId": SOURCE_ID,
            },
            {
                "id": "table-outcomes",
                "title": "Future directional-tension tests",
                "description": "The registered Phi effect is weak and does not survive the non-overlapping evaluation check.",
                "dataset": "outcomes",
                "columns": [
                    {"field": "split", "label": "Split", "type": "text"},
                    {"field": "coordinate", "label": "Coordinate", "type": "text"},
                    {"field": "rho", "label": "Spearman rho", "type": "number", "format": "0.0000"},
                    {"field": "one_sided_p", "label": "One-sided p", "type": "number", "format": "0.0000"},
                    {"field": "windows", "label": "Windows", "type": "number", "format": "0"},
                ],
                "defaultSort": {"field": "one_sided_p", "direction": "asc"},
                "sourceId": SOURCE_ID,
            },
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {TITLE}"},
            {"id": "summary", "type": "markdown", "sourceId": SOURCE_ID, "body": "## Technical summary\n\n**Measuring change between slices recovers the golden fixed-point construction, but does not establish Phi as the physical step ratio.** Across 152,780 eligible same-identity windows, the frozen two-relation ruler fitted 1.607795 and selected Phi over every other fixed landmark in evaluation and holdout. Yet that equation has Phi as its unique algebraic fixed point. A declared audit using the same one-coordinate loss for every target fitted 1.416072 on calibration, selected sqrt(2) in evaluation and 1.5 in holdout. The registered consequence also failed: Phi proximity did not reliably predict smoother later motion."},
            {"id": "metrics", "type": "metric-strip", "cardIds": ["card-windows", "card-targets", "card-outcome"]},
            {"id": "measurement", "type": "markdown", "sourceId": SOURCE_ID, "body": "## The temporal object\n\nOne tracker ID was followed through five consecutive 0.02-second slices. The first two centroid displacements defined the handover. Two later displacements, sharing no step with the predictor, defined future turn tension. This directly tests Dylan's clarification that Phi belongs to movement—the relation between recorded states—not the area ratio of different bubble identities."},
            {"id": "audit-chart-intro", "type": "markdown", "sourceId": SOURCE_ID, "body": "## The fair direct-ratio audit does not select Phi\n\nThe direct audit uses only |ln((larger step / smaller step) / target)|, giving every candidate landmark the same ruler. Evaluation lies closest to sqrt(2), while holdout lies closest to 1.5. Phi remains in the nearby band but is not the target-specific winner."},
            {"id": "direct-chart", "type": "chart", "chartId": "chart-direct-targets"},
            {"id": "joint-result", "type": "markdown", "sourceId": SOURCE_ID, "body": "## What the golden joint ruler did recover\n\nFor the frozen pair q_whole=(a+b)/a and q_lineage=a/b, the calibration-only free target was 1.607795. Phi had mean joint distance 0.408533 in evaluation and 0.425979 in holdout, lower than every other fixed target. Whole-video bootstrap intervals for Phi minus each fixed competitor stayed below zero. This is a clean recovery of the golden fixed-point geometry, but the fixed point is partly supplied by the equal-ratio equation itself."},
            {"id": "joint-table", "type": "table", "tableId": "table-joint-targets"},
            {"id": "adjacency", "type": "markdown", "sourceId": SOURCE_ID, "body": "## Real neighbouring slices approach the fixed point\n\nThe golden-equality residual was lower for true consecutive movement than for the frozen circular-shift control. Adjacent-minus-shift was -0.037828 in evaluation (95% whole-video interval -0.045615 to -0.030207) and -0.061808 in holdout (-0.071712 to -0.049482). This establishes a real temporal-continuity relation. It is not uniquely golden, because adjacency improved every landmark and improved target 1 most strongly."},
            {"id": "equality-chart", "type": "chart", "chartId": "chart-equality"},
            {"id": "outcome", "type": "markdown", "sourceId": SOURCE_ID, "body": "## The reduced-temporal-tension consequence failed\n\nThe frozen prediction was that greater distance from Phi would precede greater future turning. Evaluation gave rho=0.00961, p=0.3535; the non-overlapping evaluation subset gave rho=-0.03595, p=0.9524. Holdout remained weak at rho=0.03583, p=0.09358. The shifted-Phi control was stronger than the real Phi coordinate, pointing to broad track-state persistence rather than a golden low-tension mechanism."},
            {"id": "outcomes-table", "type": "table", "tableId": "table-outcomes"},
            {"id": "method", "type": "markdown", "sourceId": SOURCE_ID, "body": "## Method and validation\n\nThe earlier split was retained: V01-V07 calibration, V08-V28 evaluation, V29-V35 untouched holdout. Steps below 0.0005 m were excluded as sub-resolution. All 152,780 windows contributed descriptive distances. Permutation inference used at most 250 deterministic windows per video and 5,000 within-video outcome permutations; uncertainty used 5,000 whole-video bootstrap resamples. A separate validation script checks counts, split coverage, fixed-target ordering, direct-audit ordering, adjacency controls and the failed future-tension gates."},
            {"id": "limitations", "type": "markdown", "body": "## Measurement boundary\n\nThe source contains segmented centroids and tracker-assigned identities rather than raw field motion. Fixed 50-fps sampling can determine the observed step-ratio band, and pixel quantization hides smaller movements. The result therefore concerns this sampled trajectory representation. The two-equation Phi result is algebraic plus empirical proximity; it must not be reported as a newly measured universal constant."},
            {"id": "next", "type": "markdown", "body": "## Next decisive test\n\nUse raw or multi-cadence trajectories of the same physical path. Freeze the prediction that a genuine Phi handover remains stable when the path is resampled at several reasonable time intervals, while a cadence-created sqrt(2)-to-1.5 band moves. Keep three independent gates: joint golden equality, direct movement ratio and a future-tension consequence."},
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
                "joint_targets": joint_targets,
                "direct_targets": direct_targets,
                "equality_comparison": equality_rows,
                "outcomes": outcome_rows,
            },
        },
        "sources": [source],
    }
    output = Path(output_path)
    output.write_text(json.dumps(artifact, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(artifact, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
