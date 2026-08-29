#!/usr/bin/env python3
"""Build the canonical T406/T407 portable technical-report artifact."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
T406 = ROOT / "T406_grandchild_quarter_completion"
T407 = ROOT / "T407_individual_muon_grandchild_transfer"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def source(sid: str, label: str, path: str, language: str, description: str) -> dict:
    item = {
        "id": sid,
        "label": label,
        "path": path,
        "query": {
            "engine": "duckdb" if language in {"csv", "json"} else "file",
            "language": language,
            "description": description,
            "tables_used": [Path(path).name],
        },
    }
    if language == "csv":
        item["query"]["sql"] = f"SELECT * FROM read_csv_auto('{path}')"
    elif language == "json":
        item["query"]["sql"] = f"SELECT * FROM read_json_auto('{path}', format='auto')"
    return item


def main() -> None:
    r406 = json.loads((T406 / "T406_RESULTS.json").read_text(encoding="utf-8"))
    v406 = json.loads((T406 / "T406_VALIDATION.json").read_text(encoding="utf-8"))
    r407 = json.loads((T407 / "T407_RESULTS.json").read_text(encoding="utf-8"))
    v407 = json.loads((T407 / "T407_VALIDATION.json").read_text(encoding="utf-8"))
    splits_raw = read_csv(T406 / "T406_SPLIT_RESULTS.csv")
    models_raw = read_csv(T407 / "T407_MODEL_SUMMARY.csv")
    events_raw = read_csv(T407 / "T407_HOLDOUT_EVENT_SCORES.csv")

    splits = [
        {
            "salt": int(r["salt"]),
            "prompt_participation": float(r["prompt_participation"]),
            "observed_child_crest": float(r["observed_child_crest"]),
            "grandchild_ara": float(r["grandchild_ara"]),
            "loo_predicted_child_crest": float(r["loo_predicted_child_crest"]),
            "series": "primary salt 400" if int(r["salt"]) == 400 else "registered split",
        }
        for r in splits_raw
    ]
    models = [
        {
            "model": r["model"],
            "centre_label": f"{float(r['centre']):.3f}",
            "centre": float(r["centre"]),
            "holdout_band_n": int(r["holdout_band_n"]),
            "nll_improvement": float(r["nll_improvement"]),
            "ci95_low": float(r["ci95_low"]),
            "ci95_high": float(r["ci95_high"]),
            "permutation_p": float(r["permutation_p"]),
            "supported": r["supported"].lower() == "true",
        }
        for r in models_raw
    ]

    x = np.asarray([float(r["x_mu"]) for r in events_raw])
    y = np.asarray([float(r["actual_daughter_delay_us"]) for r in events_raw])
    edges = np.linspace(0, 2, 21)
    binned = []
    for left, right in zip(edges[:-1], edges[1:]):
        mask = (x >= left) & (x < right)
        if mask.any():
            binned.append(
                {
                    "bin_mid": float((left + right) / 2),
                    "median_delay_us": float(np.median(y[mask])),
                    "mean_delay_us": float(np.mean(y[mask])),
                    "n": int(mask.sum()),
                }
            )
    pure = [r for r in events_raw if r["in_pure_0p75_band"].lower() == "true"]
    outside = [r for r in events_raw if r["in_pure_0p75_band"].lower() != "true"]
    key = lambda r: (r["file"], int(r["event_index"]))
    example_raw = sorted(pure, key=key)[:6] + sorted(outside, key=key)[:6]
    examples = [
        {
            "event": f"{r['file'][-6:]} #{r['event_index']}",
            "actual_delay_us": float(r["actual_daughter_delay_us"]),
            "predicted_median_us": float(r["pure_band_predicted_median_us"]),
            "band": "0.75 band" if r["in_pure_0p75_band"].lower() == "true" else "outside band",
        }
        for r in example_raw
    ]

    gates = []
    for name, value in r406["gates"].items():
        gates.append({"test": "T406", "gate": name, "status": "PASS" if value else "FAIL"})
    for model in ("M075", "M0706"):
        for name, value in r407["models"][model]["gates"].items():
            gates.append({"test": f"T407 {model}", "gate": name, "status": "PASS" if value else "FAIL"})
    validation = [
        {"test": "T406", "status": v406["status"], "checks": len(v406["checks"])},
        {"test": "T407", "status": v407["status"], "checks": len(v407["checks"])},
    ]

    rel406_splits = "analysis/muon/T406_grandchild_quarter_completion/T406_SPLIT_RESULTS.csv"
    rel406_results = "analysis/muon/T406_grandchild_quarter_completion/T406_RESULTS.json"
    rel406_validation = "analysis/muon/T406_grandchild_quarter_completion/T406_VALIDATION.json"
    rel407_models = "analysis/muon/T407_individual_muon_grandchild_transfer/T407_MODEL_SUMMARY.csv"
    rel407_events = "analysis/muon/T407_individual_muon_grandchild_transfer/T407_HOLDOUT_EVENT_SCORES.csv"
    rel407_results = "analysis/muon/T407_individual_muon_grandchild_transfer/T407_RESULTS.json"
    rel407_validation = "analysis/muon/T407_individual_muon_grandchild_transfer/T407_VALIDATION.json"
    sources = [
        source("t406_splits", "T406 split results", rel406_splits, "csv", "Observed child crests, prompt participation, decompressed grandchild coordinates and leave-one-out predictions for 20 deterministic T400 splits."),
        source("t406_results", "T406 saved results", rel406_results, "json", "Frozen geometry, gates, verdict and evidence boundaries for the quarter-completion test."),
        source("t406_validation", "T406 independent validation", rel406_validation, "json", "Independent saved-artifact recomputation for T406."),
        source("t407_models", "T407 model summary", rel407_models, "csv", "Calibration direction, held-out timing score, uncertainty and permutation result for each frozen ARA band."),
        source("t407_events", "T407 individual holdout event scores", rel407_events, "csv", "2,109 event-linked stopped-muon records with observed charged-daughter delay and calibration-frozen timing predictions."),
        source("t407_results", "T407 saved results", rel407_results, "json", "Individual timing-transfer verdict, model diagnostics, gates and scope boundaries."),
        source("t407_validation", "T407 independent validation", rel407_validation, "json", "Independent integrity and arithmetic checks for T407."),
        source("t406_protocol", "T406 frozen protocol", "analysis/muon/T406_GRANDCHILD_QUARTER_COMPLETION_PROTOCOL_2026-08-18.md", "md", "Pre-run quarter-completion coordinates, gates and verdict logic."),
        source("t407_protocol", "T407 frozen protocol", "analysis/muon/T407_INDIVIDUAL_MUON_GRANDCHILD_TRANSFER_PROTOCOL_2026-08-18.md", "md", "Pre-run individual-muon timing-transfer models, controls and gates."),
    ]
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    charts = [
        {
            "id": "participation_crest", "title": "Prompt participation versus observed child crest", "subtitle": "20 deterministic T400 splits; pure parent and projected-grandchild references are fixed", "type": "scatter", "dataset": "splits", "sourceId": "t406_splits", "palette": {"kind": "categorical", "name": "blue-gold"},
            "referenceLines": [
                {"axis": "y", "value": 0.5, "label": "parent 0.5", "color": "neutral", "lineStyle": "dashed"},
                {"axis": "y", "value": 0.75, "label": "pure endpoint 0.75", "color": "neutral", "lineStyle": "solid"},
            ],
            "encodings": {
                "x": {"field": "prompt_participation", "type": "quantitative", "label": "Prompt participation q"},
                "y": {"field": "observed_child_crest", "type": "quantitative", "label": "Observed child release crest (ARA)"},
                "color": {"field": "series", "type": "nominal", "label": "Split type"},
                "tooltip": [
                    {"field": "salt", "type": "quantitative", "label": "Split salt"},
                    {"field": "grandchild_ara", "type": "quantitative", "label": "Decompressed x_G"},
                ],
            },
        },
        {
            "id": "grandchild_coordinate", "title": "Decompressed grandchild coordinate across splits", "subtitle": "The proposed full grandchild endpoint maps to x_G=2; observed values vary with participation", "type": "scatter", "dataset": "splits", "sourceId": "t406_splits", "palette": {"kind": "categorical", "name": "blue-gold"},
            "referenceLines": [{"axis": "y", "value": 2.0, "label": "proposed completion x_G=2", "color": "neutral", "lineStyle": "dashed"}],
            "encodings": {
                "x": {"field": "salt", "type": "quantitative", "label": "Deterministic split salt"},
                "y": {"field": "grandchild_ara", "type": "quantitative", "label": "Grandchild ARA x_G"},
                "color": {"field": "series", "type": "nominal", "label": "Split type"},
                "tooltip": [{"field": "observed_child_crest", "type": "quantitative", "label": "Observed child crest"}],
            },
        },
        {
            "id": "individual_scores", "title": "Individual timing score by frozen ARA band", "subtitle": "Positive held-out NLL improvement would beat ordinary prompt depth and strength", "type": "bar", "dataset": "models", "sourceId": "t407_models", "palette": {"kind": "single", "name": "blue"},
            "referenceLines": [{"axis": "y", "value": 0.0, "label": "no improvement", "color": "neutral", "lineStyle": "solid"}],
            "encodings": {
                "x": {"field": "centre_label", "type": "nominal", "label": "ARA band centre (±0.05)"},
                "y": {"field": "nll_improvement", "type": "quantitative", "label": "Held-out NLL improvement"},
                "tooltip": [
                    {"field": "holdout_band_n", "type": "quantitative", "label": "Band events"},
                    {"field": "ci95_low", "type": "quantitative", "label": "95% low"},
                    {"field": "ci95_high", "type": "quantitative", "label": "95% high"},
                    {"field": "permutation_p", "type": "quantitative", "label": "Permutation p"},
                ],
            },
        },
        {
            "id": "individual_delay_shape", "title": "Individual charged-daughter timing across incoming ARA", "subtitle": "Held-out medians in 0.1-wide x_mu bins; counts remain visible in the source data", "type": "line", "dataset": "binned", "sourceId": "t407_events", "palette": {"kind": "single", "name": "blue"},
            "referenceLines": [
                {"axis": "x", "value": 0.7063064837018814, "label": "observed child 0.706", "color": "neutral", "lineStyle": "dashed"},
                {"axis": "x", "value": 0.75, "label": "pure 0.75", "color": "neutral", "lineStyle": "solid"},
            ],
            "encodings": {
                "x": {"field": "bin_mid", "type": "quantitative", "label": "Incoming individual-muon ARA x_mu"},
                "y": {"field": "median_delay_us", "type": "quantitative", "label": "Median daughter delay (microseconds)"},
                "tooltip": [
                    {"field": "n", "type": "quantitative", "label": "Events"},
                    {"field": "mean_delay_us", "type": "quantitative", "label": "Mean delay (microseconds)"},
                ],
            },
        },
        {
            "id": "individual_examples", "title": "Observed versus predicted timing for named individual events", "subtitle": "Six earliest holdout events in the 0.75 band plus six earliest outside it", "type": "scatter", "dataset": "examples", "sourceId": "t407_events", "palette": {"kind": "categorical", "name": "blue-gold"},
            "encodings": {
                "x": {"field": "predicted_median_us", "type": "quantitative", "label": "Model-predicted median delay (microseconds)"},
                "y": {"field": "actual_delay_us", "type": "quantitative", "label": "Observed daughter delay (microseconds)"},
                "color": {"field": "band", "type": "nominal", "label": "0.75 band membership"},
                "tooltip": [{"field": "event", "type": "nominal", "label": "Event"}],
            },
        },
    ]
    tables = [
        {"id": "gates", "title": "Frozen interpretation gates", "subtitle": "T406 supports displacement compatibility; both T407 candidate bands fail prediction", "dataset": "gates", "sourceId": "t407_results", "defaultSort": {"field": "test", "direction": "asc"}, "columns": [
            {"field": "test", "label": "Test", "type": "text"}, {"field": "gate", "label": "Gate", "type": "text"}, {"field": "status", "label": "Result", "type": "text"},
        ]},
        {"id": "validation", "title": "Independent saved-output validation", "subtitle": "Both calculation pipelines passed integrity and arithmetic checks", "dataset": "validation", "sourceId": "t407_validation", "defaultSort": {"field": "test", "direction": "asc"}, "columns": [
            {"field": "test", "label": "Test", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}, {"field": "checks", "label": "Checks", "type": "number"},
        ]},
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": "# T406/T407 — Grandchild completion and individual-muon transfer"},
        {"id": "summary", "type": "markdown", "body": "## Technical summary\n\n**The proposed `0.5 + 0.25 = 0.75` construction is compatible with the primary population crest, but it is not a replicated fixed child point and it does not predict one muon's later decay timing through the tested incoming-pulse cut.** The primary crest is `0.706306`, only `0.043694` below the pure endpoint and equal to `82.52%` of the proposed quarter capacity (`x_G=1.650`). Yet only `7/20` split crests fall within `0.75±0.10`. Their displacement is almost perfectly predicted from participation, with leave-one-split-out median absolute error `0.00073`, but that relation is mediated by the equality boundary used to construct the coordinate.\n\nOn 2,109 event-linked held-out stopped muons, neither the pure `0.75±0.05` band nor the observed `0.706306±0.05` band improved charged-daughter timing over ordinary prompt strength, multiplicity and depth. This narrows the missing individual cut to a maturity/spin or neutral-sensitive relation rather than a static incoming upper/lower pulse ratio.", "sourceId": "t407_results"},
        {"id": "t406_result", "type": "markdown", "body": "## T406: the quarter is a parent-compatible reference, not a fixed observed child point\n\nThe primary observation passes the broad proximity gate, but the raw replication gate fails: `35%`, not the required `75%`, of valid splits lie within `0.75±0.10`. The median observed crest is `0.9483` and the full range is `0.6404–1.0578`. The correct verdict is **participation-displaced quarter-compatible**—stronger than coincidence with one point, weaker than identifying a universal `0.25` physical carrier.", "sourceId": "t406_results"},
        {"id": "participation_chart", "type": "chart", "chartId": "participation_crest"},
        {"id": "t406_decompressed", "type": "markdown", "body": "## Decompression exposes why the exact claim fails\n\nMapping `0.5→0` and `0.75→2` puts the primary result at `x_G=1.650`, not at the completion pole `2`. Across splits the values range well beyond that pole. Participation predicts those observed positions with tiny internal error, but the equality boundary carries the same ordering; this is a coordinate-response validation, not independent proof of the grandchild mechanism.", "sourceId": "t406_splits"},
        {"id": "grandchild_chart", "type": "chart", "chartId": "grandchild_coordinate"},
        {"id": "t407_result", "type": "markdown", "body": "## T407: the individual-muon transfer fails the frozen predictive gates\n\nBoth candidate bands pointed toward higher handover hazard in calibration. On holdout, the pure `0.75` model changed mean NLL by only `-0.0000028` and its 95% block interval was `[-0.0000151, +0.0000083]`. The observed `0.706306` band was worse (`-0.0005125`, interval `[-0.0019486, +0.0010149]`). Neither improved both held-out runs; neither survived the permutation gate. Negative values mean the added band was marginally worse than ordinary prompt geometry.", "sourceId": "t407_models"},
        {"id": "scores_chart", "type": "chart", "chartId": "individual_scores"},
        {"id": "delay_text", "type": "markdown", "body": "## The descriptive short delay near 0.75 is real but not unique predictive information\n\nThe `0.75±0.05` band contains `259` holdout events with median daughter delay `1.669 microseconds`; the `0.706306±0.05` band contains `213` with median `1.599 microseconds`. The timing curve therefore has visible structure. The model test shows that the same structure is already explained by prompt strength, multiplicity and detector depth, so it cannot be used as advance ARA information for an individual muon from this cut alone.", "sourceId": "t407_results"},
        {"id": "delay_chart", "type": "chart", "chartId": "individual_delay_shape"},
        {"id": "examples_text", "type": "markdown", "body": "## Individual rows remain stochastic around the population relation\n\nThe fixed-rule examples make the boundary visible: the model supplies an event-specific timing distribution, while actual daughter arrivals remain widely spread. A population crest or short median must not be translated into an exact neutrino-birth timestamp for one event.", "sourceId": "t407_events"},
        {"id": "examples_chart", "type": "chart", "chartId": "individual_examples"},
        {"id": "definitions", "type": "markdown", "body": "## Scope, identities and metric definitions\n\n- **T406 parent reference:** `0.5` on the corrected T404/T405 child coordinate.\n- **Projected grandchild capacity:** `0.25` at that parent scale; pure endpoint `0.75`.\n- **Decompressed coordinate:** `x_G = 2(x-0.5)/0.25`; pure completion is `x_G=2`.\n- **T407 individual coordinate:** `x_mu=2B/(A+B)` from the incoming event's gain-normalized lower versus total prompt counter relation.\n- **Outcome:** time to the same event's later charged-daughter pulse cluster, observed from `0.30–10.0 microseconds`.\n\nT406 and T407 therefore use related ARA logic but not identical physical axes: the first is a population timing child; the second is an individual incoming detector relation.", "sourceId": "t407_protocol"},
        {"id": "method", "type": "markdown", "body": "## Methodology and robustness\n\nT406 froze the `0.75` endpoint before calculation, scored all 20 valid registered splits and used leave-one-split-out monotone interpolation without recentering any value to `0.75`. T407 froze the `0.75` and `0.706306` bands before fitting, trained only on the two T379 calibration runs, and scored two separate holdout runs with a truncated exponential-plus-uniform timing likelihood. Chronological block bootstrap and within-run delay permutation tested uncertainty and alignment. Controls at `0.50`, `1.00`, `1.25` and `1.50` were reported without selecting a replacement landmark.", "sourceId": "t407_protocol"},
        {"id": "gates_table_block", "type": "table", "tableId": "gates"},
        {"id": "limits", "type": "markdown", "body": "## Limitations and uncertainty\n\nThe participation result is internally precise but structurally mediated by the coordinate's equality boundary. T407 is external at the detector/archive level, yet its holdout had been generated and inspected earlier in the project, so this is not a pristine new prospective holdout. Most importantly, QuarkNet links the incoming stopped-muon candidate to a later charged daughter but does not directly observe either neutrino and does not resolve an individual spin trajectory. Failure here rejects this static incoming-pulse landmark as the missing clock; it does not reject population handover geometry or a different phase/maturity cut.", "sourceId": "t407_results"},
        {"id": "validation_block", "type": "table", "tableId": "validation"},
        {"id": "next", "type": "markdown", "body": "## Recommended next step\n\nKeep the T406 result as a **parent-compatible, participation-displaced hypothesis**. For individual prediction, freeze a genuinely dynamic pre-decay input—spin phase/maturity, charged-daughter direction relative to polarization, or independently reconstructed missing momentum—and test it on a new event-linked holdout. Do not reuse `0.75` as a universal event clock unless that new measurement independently restores it."},
        {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Does an event-linked spin or polarization phase provide the missing pre-decay maturity axis?\n- Can a neutral-sensitive archive distinguish the joint neutrino pair rather than only the charged daughter?\n- Does participation displacement learned in one source predict the child crest of a genuinely independent source without rebuilding the equality boundary?"},
    ]

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1, "surface": "report", "title": "T406/T407 — Grandchild completion and individual-muon transfer", "description": "Frozen test of the proposed 0.5+0.25 endpoint followed by event-linked individual stopped-muon timing transfer.", "generatedAt": generated,
            "cards": [], "charts": charts, "tables": tables, "sources": sources, "blocks": blocks,
        },
        "snapshot": {
            "version": 1, "generatedAt": generated, "status": "ready",
            "datasets": {"splits": splits, "models": models, "binned": binned, "examples": examples, "gates": gates, "validation": validation},
            "accessIssues": [],
        },
        "sources": sources,
    }
    (T407 / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(T407 / "artifact.json")


if __name__ == "__main__":
    main()

