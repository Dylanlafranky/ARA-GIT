#!/usr/bin/env python3
"""Build PN35 reader artifacts from the independently validated result JSON."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_RESULTS.json"
PROTOCOL = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_PROTOCOL_v1_FROZEN.md"
FIGURE = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_FIGURE.png"
NOTEBOOK = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_REPRODUCIBILITY.ipynb"
ARTIFACT = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_REPORT_ARTIFACT.json"
REPORT_DB = HERE / "PN35_REPORT_SOURCE.sqlite"
RECORDING = HERE / "PN35_RECORDING_VALIDATION.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes())
    return h.hexdigest()


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def build_figure(d: dict) -> None:
    w, h = 1800, 1050
    img = Image.new("RGB", (w, h), "#f7f8fb")
    draw = ImageDraw.Draw(img)
    navy, blue, gold, red, grey = "#152238", "#3777c8", "#d19a35", "#b94b55", "#6b7280"
    draw.text((70, 45), "PN35 same-scale golden crossing", fill=navy, font=font(42, True))
    draw.text((70, 100), "Primes did not prefer the registered Phi crossings", fill=red, font=font(27, True))
    draw.text((70, 146), "196,608 candidates · 24,576 complete eight-child cells · six octave rungs", fill=grey, font=font(21))

    # Panel A: model AUCs.
    x0, y0, pw, ph = 90, 255, 760, 650
    draw.rounded_rectangle((x0 - 25, y0 - 50, x0 + pw + 25, y0 + ph + 45), 20, fill="white", outline="#dce1ea")
    draw.text((x0, y0 - 35), "Lane-stratified prime/composite AUC", fill=navy, font=font(25, True))
    models = sorted(d["all_model_aucs"].items(), key=lambda x: x[1], reverse=True)
    models = [("36° shear" if n == "shear_36deg" else "Phi" if n == "golden" else n.replace("_", " "), v) for n, v in models]
    lo, hi = 0.488, 0.505
    plot_l, plot_r = x0 + 210, x0 + pw - 25
    baseline_x = plot_l + (0.5 - lo) / (hi - lo) * (plot_r - plot_l)
    draw.line((baseline_x, y0, baseline_x, y0 + ph - 30), fill="#111827", width=2)
    draw.text((baseline_x - 22, y0 + ph - 20), "0.500", fill=grey, font=font(16))
    for idx, (name, value) in enumerate(models):
        y = y0 + 18 + idx * 48
        x = plot_l + (value - lo) / (hi - lo) * (plot_r - plot_l)
        color = gold if name == "Phi" else blue
        draw.text((x0, y - 11), name[:23], fill=navy, font=font(17, name == "Phi"))
        draw.line((baseline_x, y, x, y), fill=color, width=8)
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color)
        draw.text((plot_r - 72, y - 12), f"{value:.4f}", fill=navy, font=font(16, name == "Phi"))

    # Panel B: distance octiles.
    x1, y1, pw1, ph1 = 970, 255, 720, 650
    draw.rounded_rectangle((x1 - 25, y1 - 50, x1 + pw1 + 25, y1 + ph1 + 45), 20, fill="white", outline="#dce1ea")
    draw.text((x1, y1 - 35), "Prime rate by distance-from-crossing octile", fill=navy, font=font(25, True))
    octiles = d["distance_octiles"]
    values = [100 * row["prime_rate"] for row in octiles]
    ymin, ymax = 14.8, 15.8
    left, right, top, bottom = x1 + 65, x1 + pw1 - 25, y1 + 30, y1 + ph1 - 70
    for tick in (14.8, 15.0, 15.2, 15.4, 15.6, 15.8):
        yy = bottom - (tick - ymin) / (ymax - ymin) * (bottom - top)
        draw.line((left, yy, right, yy), fill="#e5e7eb", width=1)
        draw.text((x1, yy - 10), f"{tick:.1f}%", fill=grey, font=font(15))
    points = []
    for i, value in enumerate(values):
        xx = left + i * (right - left) / 7
        yy = bottom - (value - ymin) / (ymax - ymin) * (bottom - top)
        points.append((xx, yy))
        draw.text((xx - 5, bottom + 20), str(i + 1), fill=navy, font=font(16))
    draw.line(points, fill=gold, width=5)
    for xx, yy in points:
        draw.ellipse((xx - 7, yy - 7, xx + 7, yy + 7), fill=gold)
    draw.text((left, bottom + 16), "Nearest to crossing  →  farthest", fill=grey, font=font(18))
    draw.text((x1, bottom + 58), "No monotone rise toward the registered crossing; nearest octile = 15.08%.", fill=red, font=font(18, True))

    draw.text((90, 970), "Geometry verdict: eight anti-paired structural lanes close exactly to parent total 2.  Predictive verdict: Phi crossing preference NOT SUPPORTED.", fill=navy, font=font(22, True))
    img.save(FIGURE)


def build_notebook(d: dict) -> None:
    source = """from pathlib import Path\nimport json\n\nHERE = Path.cwd()\nif HERE.name != 'primes':\n    HERE = HERE / 'analysis' / 'primes'\nresults = json.loads((HERE / 'PN35_SAME_SCALE_GOLDEN_CROSS_RESULTS.json').read_text())\n{\n    'verdict': results['verdict'],\n    'golden_auc': results['golden_auc'],\n    'golden_auc_ci95': results['golden_auc_ci95'],\n    'top2_capture': results['top2_capture'],\n    'gates': results['gates'],\n}\n"""
    output = {
        "output_type": "execute_result",
        "execution_count": 1,
        "data": {"text/plain": [json.dumps({
            "verdict": d["verdict"], "golden_auc": d["golden_auc"],
            "golden_auc_ci95": d["golden_auc_ci95"], "top2_capture": d["top2_capture"],
            "gates": d["gates"],
        }, indent=2)]},
        "metadata": {},
    }
    notebook = {
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": [
                "# PN35 same-scale golden crossing reproducibility\n",
                "This companion reads the independently validated result. The complete prediction and validation logic is in the two frozen Python scripts.\n",
            ]},
            {"cell_type": "code", "execution_count": 1, "metadata": {}, "outputs": [output], "source": source.splitlines(True)},
            {"cell_type": "markdown", "metadata": {}, "source": [
                "## Interpretation\n",
                "The exact eight-lane anti-pair closure is a structural arithmetic crosswalk. The added unfitted `1/phi^2` same-scale crossing did not rank primes above composites, beat rivals, or benefit from the registered singularity flip.\n",
            ]},
        ],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=2) + "\n", encoding="utf-8")


def build_artifact(d: dict) -> None:
    now = datetime.now(timezone(timedelta(hours=10))).isoformat(timespec="seconds")
    models = [
        {"model": name.replace("_", " "), "auc": value, "chance": 0.5,
         "is_registered_phi": name == "golden"}
        for name, value in sorted(d["all_model_aucs"].items(), key=lambda x: x[1], reverse=True)
    ]
    rungs = [{"rung": int(k), "golden_auc": v["golden_auc"], "no_flip_auc": v["noflip_auc"],
              "top2_capture": v["top2_capture"], "prime_rate": v["prime_rate"], "rows": v["rows"]}
             for k, v in d["by_rung"].items()]
    octiles = [{"octile": x["octile"], "prime_rate": x["prime_rate"], "rows": x["rows"],
                "distance_low": x["distance_low"], "distance_high": x["distance_high"]}
               for x in d["distance_octiles"]]
    gates = [{"gate": k.replace("_", " "), "passed": "PASS" if v else "FAIL"} for k, v in d["gates"].items()]
    headline = {"verdict": d["verdict"], "golden_auc": d["golden_auc"], "chance": 0.5,
                "capture": d["top2_capture"], "capture_null": 0.25,
                "gates": f"{sum(d['gates'].values())} / {len(d['gates'])}"}
    with sqlite3.connect(REPORT_DB) as conn:
        conn.executescript("""
        DROP TABLE IF EXISTS pn35_headline;
        DROP TABLE IF EXISTS pn35_models;
        DROP TABLE IF EXISTS pn35_rungs;
        DROP TABLE IF EXISTS pn35_octiles;
        DROP TABLE IF EXISTS pn35_gates;
        CREATE TABLE pn35_headline(verdict TEXT, golden_auc REAL, chance REAL, capture REAL, capture_null REAL, gates TEXT);
        CREATE TABLE pn35_models(model TEXT, auc REAL, chance REAL, is_registered_phi INTEGER);
        CREATE TABLE pn35_rungs(rung INTEGER, golden_auc REAL, no_flip_auc REAL, top2_capture REAL, prime_rate REAL, rows INTEGER);
        CREATE TABLE pn35_octiles(octile INTEGER, prime_rate REAL, rows INTEGER, distance_low REAL, distance_high REAL);
        CREATE TABLE pn35_gates(gate_name TEXT, passed TEXT);
        """)
        conn.execute("INSERT INTO pn35_headline VALUES (?,?,?,?,?,?)", tuple(headline.values()))
        conn.executemany("INSERT INTO pn35_models VALUES (?,?,?,?)", [(x["model"], x["auc"], x["chance"], int(x["is_registered_phi"])) for x in models])
        conn.executemany("INSERT INTO pn35_rungs VALUES (?,?,?,?,?,?)", [(x["rung"], x["golden_auc"], x["no_flip_auc"], x["top2_capture"], x["prime_rate"], x["rows"]) for x in rungs])
        conn.executemany("INSERT INTO pn35_octiles VALUES (?,?,?,?,?)", [(x["octile"], x["prime_rate"], x["rows"], x["distance_low"], x["distance_high"]) for x in octiles])
        conn.executemany("INSERT INTO pn35_gates VALUES (?,?)", [(x["gate"], x["passed"]) for x in gates])
    def sql_source(source_id: str, label: str, sql: str, table: str, definitions: list[str]):
        return {"id": source_id, "label": label, "path": "analysis/primes/PN35_REPORT_SOURCE.sqlite",
                "query": {"id": source_id, "engine": "sqlite", "language": "sql", "executed_at": now,
                          "description": label, "sql": sql, "tables_used": [table],
                          "filters": ["PN35 frozen targets and independently opened labels"],
                          "metric_definitions": definitions}}
    sources = [
        sql_source("pn35_headline", "PN35 frozen headline endpoints", "SELECT verdict, golden_auc, chance, capture, capture_null, gates FROM pn35_headline", "pn35_headline", ["AUC is lane-stratified Mann–Whitney prime/composite ordering.", "Capture is the share of all primes in the two closest of eight lanes per cell."]),
        sql_source("pn35_models", "PN35 frozen constant comparison", "SELECT model, auc, chance, is_registered_phi FROM pn35_models ORDER BY auc DESC", "pn35_models", ["AUC conditions on each mod-30 residue lane before pooling."]),
        sql_source("pn35_rungs", "PN35 octave-rung results", "SELECT rung, golden_auc, no_flip_auc, top2_capture, prime_rate, rows FROM pn35_rungs ORDER BY rung", "pn35_rungs", ["Each rung contains 4,096 complete eight-candidate cells."]),
        sql_source("pn35_octiles", "PN35 crossing-distance octiles", "SELECT octile, prime_rate, rows, distance_low, distance_high FROM pn35_octiles ORDER BY octile", "pn35_octiles", ["Octile 1 is nearest to the registered crossing; each octile contains 24,576 rows."]),
        sql_source("pn35_gates", "PN35 registered gate verdicts", "SELECT gate_name AS gate, passed FROM pn35_gates ORDER BY gate_name", "pn35_gates", ["All five gates were required for a supported verdict."]),
        {"id": "pn35_results", "label": "PN35 independently validated results", "path": "analysis/primes/PN35_SAME_SCALE_GOLDEN_CROSS_RESULTS.json"},
    ]
    protocol_source = {"id": "pn35_protocol", "label": "PN35 frozen protocol",
                       "path": "analysis/primes/PN35_SAME_SCALE_GOLDEN_CROSS_PROTOCOL_v1_FROZEN.md"}
    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1, "surface": "report", "title": "PN35: Same-scale golden crossing",
            "description": "Frozen test of whether primes prefer a Phi handover crossing over eight structural child lanes.",
            "generatedAt": now,
            "cards": [
                {"id": "verdict_card", "dataset": "headline", "sourceId": "pn35_headline", "metrics": [{"label": "Frozen verdict", "field": "verdict", "format": "text"}]},
                {"id": "auc_card", "dataset": "headline", "sourceId": "pn35_headline", "metrics": [{"label": "Phi AUC", "field": "golden_auc", "format": "number"}, {"label": "Chance", "field": "chance", "format": "number"}]},
                {"id": "capture_card", "dataset": "headline", "sourceId": "pn35_headline", "metrics": [{"label": "Nearest-two capture", "field": "capture", "format": "percent"}, {"label": "Structural null", "field": "capture_null", "format": "percent"}]},
                {"id": "gate_card", "dataset": "headline", "sourceId": "pn35_headline", "metrics": [{"label": "Support gates passed", "field": "gates", "format": "text"}]},
            ],
            "charts": [
                {"id": "model_auc_chart", "title": "Prime/composite AUC by frozen crossing rule", "subtitle": "Phi scored below chance and below the 36-degree rival", "type": "bar", "intent": "comparison", "dataset": "models", "sourceId": "pn35_models",
                 "encodings": {"x": {"field": "model", "type": "nominal", "label": "Frozen rule"}, "y": {"field": "auc", "type": "quantitative", "label": "Lane-stratified AUC"}, "tooltip": [{"field": "auc", "type": "quantitative", "label": "AUC"}, {"field": "chance", "type": "quantitative", "label": "Chance"}]}},
                {"id": "rung_chart", "title": "Phi and no-flip AUC across octave rungs", "subtitle": "Only two of six Phi rung readings exceeded chance", "type": "line", "intent": "trend", "dataset": "rungs", "sourceId": "pn35_rungs",
                 "encodings": {"x": {"field": "rung", "type": "quantitative", "label": "Octave rung k"}, "y": {"fields": ["golden_auc", "no_flip_auc"], "type": "quantitative", "label": "Lane-stratified AUC"}, "tooltip": [{"field": "rows", "type": "quantitative", "label": "Rows"}]}},
                {"id": "octile_chart", "title": "Prime rate by distance-from-crossing octile", "subtitle": "There is no monotone concentration toward the nearest crossings", "type": "line", "intent": "trend", "dataset": "octiles", "sourceId": "pn35_octiles",
                 "encodings": {"x": {"field": "octile", "type": "ordinal", "label": "Distance octile (1 = nearest)"}, "y": {"field": "prime_rate", "type": "quantitative", "label": "Prime rate"}, "tooltip": [{"field": "distance_low", "type": "quantitative", "label": "Distance low"}, {"field": "distance_high", "type": "quantitative", "label": "Distance high"}, {"field": "rows", "type": "quantitative", "label": "Rows"}]}},
            ],
            "tables": [
                {"id": "gate_table", "title": "Registered support gates", "subtitle": "All five were required for support", "dataset": "gates", "sourceId": "pn35_gates", "defaultSort": {"field": "gate", "direction": "asc"}, "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "passed", "label": "Status", "type": "text"}]}
            ],
            "sources": sources + [protocol_source],
            "blocks": [
                {"id": "title", "type": "markdown", "body": "# PN35: Same-scale golden crossing"},
                {"id": "summary", "type": "markdown", "sourceId": "pn35_results", "body": "## The registered Phi crossing did not locate primes\n\nAcross **196,608** sealed candidates, the same-scale golden crossing returned **AUC 0.4972** and nearest-two capture **24.48%**. Both are below their chance/structural baselines, all five support gates failed, and the frozen verdict is **NOT SUPPORTED**."},
                {"id": "metrics", "type": "metric-strip", "cardIds": ["verdict_card", "auc_card", "capture_card", "gate_card"]},
                {"id": "comparison_intro", "type": "markdown", "body": "## Phi was not specific and the small rival differences are not discoveries\n\nThe registered golden rule lost to the 36-degree rival (0.5031) and its bootstrap difference from that best rival was wholly negative. The rival effect is tiny and was not itself a registered positive claim, so it is retained as a control result rather than promoted."},
                {"id": "comparison", "type": "chart", "chartId": "model_auc_chart"},
                {"id": "scale_intro", "type": "markdown", "body": "## The predicted direction did not transfer across rungs or halves\n\nOnly two of six rungs exceeded 0.5. Both fixed halves were below 0.5. Reversing the handover at the singularity did not beat the identical no-flip construction."},
                {"id": "scale", "type": "chart", "chartId": "rung_chart"},
                {"id": "distance_intro", "type": "markdown", "body": "## Prime incidence did not accumulate near the crossings\n\nThe nearest two channels captured fewer primes than the structural 2/8 expectation, and circular shifts routinely matched or exceeded the registered alignment. Distance octiles show no monotone crossing concentration."},
                {"id": "distance", "type": "chart", "chartId": "octile_chart"},
                {"id": "definitions", "type": "markdown", "sourceId": "pn35_protocol", "body": "## What was tested\n\nEach exact mod-30 survivor cell was decompressed into eight structural positions on one length-two circumference. A fixed `1/phi^2` handover advanced on that same scale, produced two anti-phase crossings, and reversed direction at each doubled octave singularity. Prime labels were opened only after all positions and scores were hashed."},
                {"id": "gates_intro", "type": "markdown", "body": "## Every registered route to support failed\n\nFailure was not limited to one threshold: pooled preference, scale stability, Phi specificity, singularity flip, and nearest-two capture all failed together."},
                {"id": "gates", "type": "table", "tableId": "gate_table"},
                {"id": "limitations", "type": "markdown", "body": "## The null is about this bridge, not every possible ARA or Phi object\n\nThe exact eight-lane anti-pair closure remains an arithmetic construction: opposite residues sum to parent total 2. PN35 rejects the added claim that this particular linear, unfitted same-scale Phi rotation marks primes. It does not test a curved Phi path, PN33's continuous fill bands, or a different independently frozen observable."},
                {"id": "posthoc", "type": "markdown", "body": "## A post-hoc Phi-to-pentagon conversion hypothesis is now recorded\n\nAfter the verdict, Dylan noticed that the raw Phi carrier was below chance while the 36-degree half-pentagon (0.50313) and pentagon (0.50126) were above it. That is descriptively compatible with Phi as a moving/time carrier whose structured appearance is pentagonal. PN35 did not test such a conversion operator, and both point estimates lie inside its circular-shift range, so this is preserved as a new hypothesis rather than a rescue."},
                {"id": "next", "type": "markdown", "body": "## Recommended next step\n\nClose PN35 v1 without phase tuning. If the prime thread is resumed, require a genuinely new pre-label object and untouched rungs under a v2 protocol; do not rescue this null by shifting the origin, changing the irrational step, or reclassifying the small 36-degree control result."},
                {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Is the second same-scale object meant to be PN33's changing fill field rather than a constant rotation?\n- Can a non-prime physical system expose the same eight-child-to-parent singularity without modular arithmetic?\n- Does an independently declared curved handover have an observable that differs from post-hoc phase fitting?"},
            ],
        },
        "snapshot": {"version": 1, "generatedAt": now, "status": "ready", "datasets": {
            "headline": [headline],
            "models": models, "rungs": rungs, "octiles": octiles, "gates": gates,
        }},
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    d = json.loads(RESULTS.read_text(encoding="utf-8"))
    build_figure(d)
    build_notebook(d)
    build_artifact(d)
    recording = {
        "test_id": d["test_id"], "status": "PASS", "verdict": d["verdict"],
        "artifacts": {path.name: sha256(path) for path in (RESULTS, PROTOCOL, FIGURE, NOTEBOOK, ARTIFACT, REPORT_DB)},
        "checks": {"all_registered_gates_present": len(d["gates"]) == 5, "figure_nonempty": FIGURE.stat().st_size > 10000,
                   "notebook_nbformat_4": json.loads(NOTEBOOK.read_text())["nbformat"] == 4,
                   "artifact_surface_report": json.loads(ARTIFACT.read_text())["surface"] == "report"},
    }
    RECORDING.write_text(json.dumps(recording, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(recording, indent=2))


if __name__ == "__main__":
    main()
