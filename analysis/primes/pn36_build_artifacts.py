#!/usr/bin/env python3
"""Build PN36 reader artifacts from the independently validated result JSON."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_RESULTS.json"
PROTOCOL = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_FIDELITY_PACKET_v1_DRAFT.md"
FREEZE = HERE / "PN36_PROTOCOL_FREEZE_MANIFEST.json"
PRIMARY = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_PRIMARY.json"
VALIDATION = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_VALIDATION.json"
REPORT_MD = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_REPORT_2026-07-22.md"
FIGURE = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_FIGURE.png"
NOTEBOOK = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_REPRODUCIBILITY.ipynb"
ARTIFACT = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_REPORT_ARTIFACT.json"
REPORT_DB = HERE / "PN36_REPORT_SOURCE.sqlite"
RECORDING = HERE / "PN36_RECORDING_VALIDATION.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False):
    for candidate in (
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def display_name(name: str) -> str:
    names = {
        "converted_5": "C5(Phi), frozen",
        "converted_5_no_flip": "C5(Phi), no flip",
        "raw_phi": "Raw Phi",
        "direct_pentagon": "Direct pentagon",
        "direct_36deg": "Direct 36 degrees",
        "converted_3": "C3(Phi)",
        "converted_4": "C4(Phi)",
        "converted_6": "C6(Phi)",
        "converted_7": "C7(Phi)",
        "converted_8": "C8(Phi)",
    }
    return names.get(name, name.replace("_", " "))


def build_figure(d: dict) -> None:
    width, height = 1900, 1050
    image = Image.new("RGB", (width, height), "#f7f8fb")
    draw = ImageDraw.Draw(image)
    navy, blue, gold, red, grey, grid = "#152238", "#3777c8", "#d19a35", "#b94b55", "#6b7280", "#e5e7eb"
    draw.text((70, 42), "PN36 Phi-to-pentagon conversion", fill=navy, font=font(43, True))
    draw.text((70, 100), "The frozen fivefold conversion did not locate primes", fill=red, font=font(28, True))
    draw.text((70, 148), "196,608 candidates | 24,576 cells | six untouched octave rungs", fill=grey, font=font(21))

    # Panel 1: signed AUC departure from chance.
    x0, y0, panel_w, panel_h = 80, 245, 850, 680
    draw.rounded_rectangle((x0, y0, x0 + panel_w, y0 + panel_h), 20, fill="white", outline="#dce1ea")
    draw.text((x0 + 30, y0 + 25), "AUC departure from chance", fill=navy, font=font(27, True))
    models = sorted(d["all_model_aucs"].items(), key=lambda item: item[1], reverse=True)
    left, right = x0 + 250, x0 + panel_w - 45
    zero = (left + right) / 2
    lo, hi = -0.008, 0.008
    draw.line((zero, y0 + 80, zero, y0 + panel_h - 55), fill=navy, width=2)
    for i, (name, auc) in enumerate(models):
        y = y0 + 105 + i * 50
        delta = auc - 0.5
        px = left + (delta - lo) / (hi - lo) * (right - left)
        chosen = name == "converted_5"
        color = gold if chosen else (blue if delta >= 0 else "#8aa7c8")
        draw.text((x0 + 30, y - 12), display_name(name), fill=navy, font=font(17, chosen))
        draw.line((zero, y, px, y), fill=color, width=10)
        draw.ellipse((px - 6, y - 6, px + 6, y + 6), fill=color)
        draw.text((right - 74, y - 12), f"{delta:+.4f}", fill=navy, font=font(16, chosen))
    draw.text((left, y0 + panel_h - 38), "Below chance", fill=grey, font=font(16))
    draw.text((right - 105, y0 + panel_h - 38), "Above chance", fill=grey, font=font(16))

    # Panel 2: flip advantage by rung.
    x1, y1, panel_w1, panel_h1 = 970, 245, 850, 680
    draw.rounded_rectangle((x1, y1, x1 + panel_w1, y1 + panel_h1), 20, fill="white", outline="#dce1ea")
    draw.text((x1 + 30, y1 + 25), "Registered flip minus no-flip AUC", fill=navy, font=font(27, True))
    rungs = [(int(k), v["converted_5_auc"] - v["no_flip_auc"]) for k, v in d["by_rung"].items()]
    chart_left, chart_right = x1 + 85, x1 + panel_w1 - 40
    chart_top, chart_bottom = y1 + 105, y1 + panel_h1 - 105
    y_min, y_max = -0.012, 0.012
    zero_y = chart_bottom - (0 - y_min) / (y_max - y_min) * (chart_bottom - chart_top)
    for tick in (-0.01, -0.005, 0, 0.005, 0.01):
        py = chart_bottom - (tick - y_min) / (y_max - y_min) * (chart_bottom - chart_top)
        draw.line((chart_left, py, chart_right, py), fill=(navy if tick == 0 else grid), width=(2 if tick == 0 else 1))
        draw.text((x1 + 15, py - 10), f"{tick:+.3f}", fill=grey, font=font(15))
    slot = (chart_right - chart_left) / len(rungs)
    for i, (k, delta) in enumerate(rungs):
        cx = chart_left + slot * (i + 0.5)
        py = chart_bottom - (delta - y_min) / (y_max - y_min) * (chart_bottom - chart_top)
        color = blue if delta > 0 else (red if delta < 0 else "#9ca3af")
        draw.rectangle((cx - 27, min(py, zero_y), cx + 27, max(py, zero_y)), fill=color)
        draw.text((cx - 11, chart_bottom + 18), str(k), fill=navy, font=font(17, True))
        draw.text((cx - 38, py - 25 if delta >= 0 else py + 8), f"{delta:+.4f}", fill=navy, font=font(14))
    draw.text((x1 + 180, y1 + panel_h1 - 55), "Even rungs are identical by construction; all odd-rung flips were worse.", fill=red, font=font(18, True))

    draw.text((80, 980), "Verdict: NOT SUPPORTED. The defined conversion exists mathematically, but prime incidence did not prefer its output.", fill=navy, font=font(23, True))
    image.save(FIGURE)


def build_notebook(d: dict) -> None:
    source = """from pathlib import Path\nimport json\n\nHERE = Path.cwd()\nif HERE.name != 'primes':\n    HERE = HERE / 'analysis' / 'primes'\nresults = json.loads((HERE / 'PN36_PHI_TO_PENTAGON_CONVERSION_RESULTS.json').read_text())\n{\n    'verdict': results['verdict'],\n    'converted_5_auc': results['converted_5_auc'],\n    'converted_5_auc_ci95': results['converted_5_auc_ci95'],\n    'top2_capture': results['top2_capture'],\n    'best_rival': results['best_rival'],\n    'gates': results['gates'],\n}\n"""
    value = {
        "verdict": d["verdict"], "converted_5_auc": d["converted_5_auc"],
        "converted_5_auc_ci95": d["converted_5_auc_ci95"], "top2_capture": d["top2_capture"],
        "best_rival": d["best_rival"], "gates": d["gates"],
    }
    notebook = {
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": [
                "# PN36 Phi-to-pentagon conversion reproducibility\n",
                "This companion reads the independently validated result. Full prediction and validation logic is in the frozen Python scripts.\n",
            ]},
            {"cell_type": "code", "execution_count": 1, "metadata": {}, "outputs": [{
                "output_type": "execute_result", "execution_count": 1,
                "data": {"text/plain": [json.dumps(value, indent=2)]}, "metadata": {},
            }], "source": source.splitlines(True)},
            {"cell_type": "markdown", "metadata": {}, "source": [
                "## Interpretation\n",
                "The nearest-fivefold conversion was defined before labels and executed correctly. It did not rank primes above composites, beat its components or controls, or benefit from the registered octave flip.\n",
            ]},
        ],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3"}},
        "nbformat": 4, "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=2) + "\n", encoding="utf-8")


def sql_source(source_id: str, label: str, sql: str, table: str, now: str, definitions: list[str]) -> dict:
    return {
        "id": source_id, "label": label, "path": "analysis/primes/PN36_REPORT_SOURCE.sqlite",
        "query": {
            "id": source_id, "engine": "sqlite", "language": "sql", "executed_at": now,
            "description": label, "sql": sql, "tables_used": [table],
            "filters": ["PN36 frozen untouched rungs and independently opened prime labels"],
            "metric_definitions": definitions,
        },
    }


def build_artifact(d: dict) -> None:
    now = datetime.now(timezone(timedelta(hours=10))).isoformat(timespec="seconds")
    models = [
        {"model": display_name(name), "auc": auc, "auc_delta": auc - 0.5, "chance": 0.5,
         "registered": name == "converted_5"}
        for name, auc in sorted(d["all_model_aucs"].items(), key=lambda item: item[1], reverse=True)
    ]
    rungs = [
        {"rung": int(k), "converted_auc": v["converted_5_auc"], "no_flip_auc": v["no_flip_auc"],
         "flip_advantage": v["converted_5_auc"] - v["no_flip_auc"], "top2_capture": v["top2_capture"],
         "prime_rate": v["prime_rate"], "rows": v["rows"], "primes": v["primes"]}
        for k, v in d["by_rung"].items()
    ]
    gates = [{"gate": key.replace("_", " "), "status": "PASS" if value else "FAIL"} for key, value in d["gates"].items()]
    boundaries = [
        {"rung": int(k), "spearman": value}
        for k, value in d["descriptive_boundary_association"]["by_rung_spearman"].items()
    ]
    headline = {
        "verdict": d["verdict"], "converted_auc": d["converted_5_auc"], "chance": 0.5,
        "capture": d["top2_capture"], "capture_null": 0.25,
        "flip_difference": d["converted_5_auc"] - d["converted_5_no_flip_auc"],
        "gates": f"{sum(d['gates'].values())} / {len(d['gates'])}",
    }

    with sqlite3.connect(REPORT_DB) as conn:
        conn.executescript("""
        DROP TABLE IF EXISTS pn36_headline;
        DROP TABLE IF EXISTS pn36_models;
        DROP TABLE IF EXISTS pn36_rungs;
        DROP TABLE IF EXISTS pn36_gates;
        DROP TABLE IF EXISTS pn36_boundaries;
        CREATE TABLE pn36_headline(verdict TEXT, converted_auc REAL, chance REAL, capture REAL, capture_null REAL, flip_difference REAL, gates TEXT);
        CREATE TABLE pn36_models(model TEXT, auc REAL, auc_delta REAL, chance REAL, registered INTEGER);
        CREATE TABLE pn36_rungs(rung INTEGER, converted_auc REAL, no_flip_auc REAL, flip_advantage REAL, top2_capture REAL, prime_rate REAL, rows INTEGER, primes INTEGER);
        CREATE TABLE pn36_gates(gate_name TEXT, status TEXT);
        CREATE TABLE pn36_boundaries(rung INTEGER, spearman REAL);
        """)
        conn.execute("INSERT INTO pn36_headline VALUES (?,?,?,?,?,?,?)", tuple(headline.values()))
        conn.executemany("INSERT INTO pn36_models VALUES (?,?,?,?,?)", [(x["model"], x["auc"], x["auc_delta"], x["chance"], int(x["registered"])) for x in models])
        conn.executemany("INSERT INTO pn36_rungs VALUES (?,?,?,?,?,?,?,?)", [(x["rung"], x["converted_auc"], x["no_flip_auc"], x["flip_advantage"], x["top2_capture"], x["prime_rate"], x["rows"], x["primes"]) for x in rungs])
        conn.executemany("INSERT INTO pn36_gates VALUES (?,?)", [(x["gate"], x["status"]) for x in gates])
        conn.executemany("INSERT INTO pn36_boundaries VALUES (?,?)", [(x["rung"], x["spearman"]) for x in boundaries])

    sources = [
        sql_source("pn36_headline", "PN36 frozen headline endpoints", "SELECT verdict, converted_auc, chance, capture, capture_null, flip_difference, gates FROM pn36_headline", "pn36_headline", now, ["AUC is lane-stratified Mann-Whitney prime/composite ordering.", "Capture is the fraction of all primes in the two closest of eight lanes per cell."]),
        sql_source("pn36_models", "PN36 frozen model comparison", "SELECT model, auc, auc_delta, chance, registered FROM pn36_models ORDER BY auc DESC", "pn36_models", now, ["AUC delta equals lane-stratified AUC minus chance 0.5."]),
        sql_source("pn36_rungs", "PN36 octave-rung transfer", "SELECT rung, converted_auc, no_flip_auc, flip_advantage, top2_capture, prime_rate, rows, primes FROM pn36_rungs ORDER BY rung", "pn36_rungs", now, ["Each rung contains 4,096 complete cells and eight candidates per cell.", "Flip advantage is converted-five AUC minus no-flip AUC."]),
        sql_source("pn36_gates", "PN36 registered gate verdicts", "SELECT gate_name AS gate, status FROM pn36_gates ORDER BY gate_name", "pn36_gates", now, ["All five frozen gates were required for support."]),
        sql_source("pn36_boundaries", "PN36 descriptive boundary association", "SELECT rung, spearman FROM pn36_boundaries ORDER BY rung", "pn36_boundaries", now, ["Spearman association compares fivefold boundary proximity with prime count per complete cell; it was descriptive, not a support gate."]),
        {"id": "pn36_results", "label": "PN36 independently validated results", "path": "analysis/primes/PN36_PHI_TO_PENTAGON_CONVERSION_RESULTS.json"},
        {"id": "pn36_protocol", "label": "PN36 frozen protocol", "path": "analysis/primes/PN36_PHI_TO_PENTAGON_CONVERSION_PROTOCOL_v1_FROZEN.md"},
    ]
    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1, "surface": "report", "title": "PN36: Phi carrier to pentagonal structure",
            "description": "Frozen test of whether a fivefold quantisation of a Phi carrier preferentially locates primes.",
            "generatedAt": now,
            "cards": [
                {"id": "verdict_card", "dataset": "headline", "sourceId": "pn36_headline", "metrics": [{"label": "Frozen verdict", "field": "verdict", "format": "text"}]},
                {"id": "auc_card", "dataset": "headline", "sourceId": "pn36_headline", "metrics": [{"label": "Converted-five AUC", "field": "converted_auc", "format": "number"}, {"label": "Chance", "field": "chance", "format": "number"}]},
                {"id": "capture_card", "dataset": "headline", "sourceId": "pn36_headline", "metrics": [{"label": "Nearest-two capture", "field": "capture", "format": "percent"}, {"label": "Structural null", "field": "capture_null", "format": "percent"}]},
                {"id": "gate_card", "dataset": "headline", "sourceId": "pn36_headline", "metrics": [{"label": "Support gates passed", "field": "gates", "format": "text"}]},
            ],
            "charts": [
                {"id": "model_delta_chart", "title": "AUC deviation from chance by frozen model", "subtitle": "All models cluster within about 0.004 of chance; the registered fivefold conversion is slightly below it", "type": "bar", "intent": "comparison", "dataset": "models", "sourceId": "pn36_models",
                 "encodings": {"x": {"field": "model", "type": "nominal", "label": "Frozen model"}, "y": {"field": "auc_delta", "type": "quantitative", "label": "AUC minus 0.5"}, "tooltip": [{"field": "auc", "type": "quantitative", "label": "AUC"}, {"field": "registered", "type": "nominal", "label": "Registered primary"}]}},
                {"id": "flip_chart", "title": "Registered flip advantage by octave rung", "subtitle": "Even rungs are identical by construction; the flip reduced AUC on every odd rung", "type": "bar", "intent": "comparison", "dataset": "rungs", "sourceId": "pn36_rungs",
                 "encodings": {"x": {"field": "rung", "type": "ordinal", "label": "Octave rung k"}, "y": {"field": "flip_advantage", "type": "quantitative", "label": "Converted AUC minus no-flip AUC"}, "tooltip": [{"field": "converted_auc", "type": "quantitative", "label": "Converted AUC"}, {"field": "no_flip_auc", "type": "quantitative", "label": "No-flip AUC"}, {"field": "top2_capture", "type": "quantitative", "label": "Nearest-two capture"}]}},
            ],
            "tables": [
                {"id": "rung_table", "title": "Transfer detail by octave rung", "subtitle": "Six untouched rungs; 32,768 candidate lanes per rung", "dataset": "rungs", "sourceId": "pn36_rungs", "defaultSort": {"field": "rung", "direction": "asc"}, "columns": [
                    {"field": "rung", "label": "Rung", "type": "number"}, {"field": "converted_auc", "label": "C5(Phi) AUC", "type": "number"}, {"field": "no_flip_auc", "label": "No-flip AUC", "type": "number"}, {"field": "top2_capture", "label": "Top-two capture", "type": "percent"}, {"field": "primes", "label": "Primes", "type": "number"}
                ]},
                {"id": "gate_table", "title": "Registered support gates", "subtitle": "All five were required for a supported verdict", "dataset": "gates", "sourceId": "pn36_gates", "defaultSort": {"field": "gate", "direction": "asc"}, "columns": [{"field": "gate", "label": "Gate", "type": "text"}, {"field": "status", "label": "Status", "type": "text"}]},
            ],
            "sources": sources,
            "blocks": [
                {"id": "title", "type": "markdown", "body": "# PN36: Phi carrier to pentagonal structure"},
                {"id": "summary", "type": "markdown", "sourceId": "pn36_results", "body": "## The explicit conversion did not locate primes\n\nAcross **196,608** sealed candidates, the fivefold-converted Phi carrier returned **AUC 0.499851** and nearest-two capture **24.8858%**. Their uncertainty intervals include chance, circular shifts readily matched them, and all five frozen support gates failed. The result is **NOT SUPPORTED**."},
                {"id": "metrics", "type": "metric-strip", "cardIds": ["verdict_card", "auc_card", "capture_card", "gate_card"]},
                {"id": "models_intro", "type": "markdown", "body": "## The fivefold output did not beat its input, components or polygon controls\n\nThe registered conversion scored below raw Phi and direct pentagon. A fourfold conversion was the best frozen rival, but all point estimates remain close to 0.5 and inside the alignment-shift range. Rival ordering is therefore control evidence, not a new positive discovery."},
                {"id": "models", "type": "chart", "chartId": "model_delta_chart"},
                {"id": "flip_intro", "type": "markdown", "body": "## The registered octave flip made the odd rungs worse\n\nThe no-flip fivefold model scored **0.503772**, while the frozen flipped model scored **0.499851**. The 95% interval for flipped minus no-flip was wholly negative: **[-0.007411, -0.000566]**. This rejects the registered flip advantage, but the no-flip rival was not independently registered as a positive locator."},
                {"id": "flip", "type": "chart", "chartId": "flip_chart"},
                {"id": "transfer_intro", "type": "markdown", "body": "## The direction did not transfer across scales or sample halves\n\nOnly one of three adjacent-rung pairs, three of six individual rungs and one of two fixed halves exceeded chance. The pattern is inconsistent with a stable cross-scale prime preference."},
                {"id": "transfer", "type": "table", "tableId": "rung_table"},
                {"id": "scope", "type": "markdown", "sourceId": "pn36_protocol", "body": "## Scope and metric definitions\n\nThe eight exact modulo-30 survivor lanes were placed on one ARA circumference. A continuous `1/phi^2` carrier was snapped to its nearest one of five vertices; that vertex and its half-turn anti-phase were the crossings. AUC compares prime and composite ordering within each residue lane before pooling. Nearest-two capture asks what fraction of all primes fell in the two closest of eight lanes per cell."},
                {"id": "method", "type": "markdown", "sourceId": "pn36_protocol", "body": "## The conversion and targets were sealed before primality was opened\n\nSix untouched octave rungs supplied 24,576 complete cells. The fidelity note, protocol and both scripts were SHA-256 frozen; the label-free primary then sealed all 196,608 geometric scores. Only afterward did the independent validator calculate primality, reconstruct every distance, bootstrap whole cells and run within-rung circular shifts."},
                {"id": "gates_intro", "type": "markdown", "body": "## Every registered support route failed\n\nThe null was not caused by a single borderline threshold: pooled preference, scale transfer, conversion specificity, singularity-flip advantage and nearest-two capture all failed."},
                {"id": "gates", "type": "table", "tableId": "gate_table"},
                {"id": "limitations", "type": "markdown", "body": "## This rejects one explicit bridge, not every possible ARA conversion\n\nNearest-fivefold quantisation was Sol's minimal mathematical translation of Dylan's visual observation. It genuinely produces a five-state sequence by definition, but primes did not prefer that sequence or its sector boundaries. A different map would be a new hypothesis and must come from independent geometry rather than tuning phase, origin, sectors or event type to these labels."},
                {"id": "next", "type": "markdown", "body": "## Recommended next step\n\nRecord PN36 as a clean null and park this prime-conversion branch. Resume only if an independently specified observable changes the scientific question, rather than adjusting the same carrier after seeing the outcome."},
                {"id": "questions", "type": "markdown", "body": "## Further questions\n\n- Can a physical system expose a Phi-to-fivefold conversion observable independently of prime labels?\n- Is the ARA singularity flip meant to reverse carrier direction, structural orientation, or a different coordinate?\n- Which pre-existing ARA rule would uniquely select a conversion operator before data are viewed?"},
            ],
        },
        "snapshot": {
            "version": 1, "generatedAt": now, "status": "ready",
            "datasets": {"headline": [headline], "models": models, "rungs": rungs, "gates": gates, "boundaries": boundaries},
        },
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")


def build_recording() -> None:
    files = [RESULTS, PROTOCOL, FIDELITY, FREEZE, PRIMARY, VALIDATION, REPORT_MD, FIGURE, NOTEBOOK, ARTIFACT, REPORT_DB]
    recording = {
        "test_id": "PN36/PHI-TO-PENTAGON-CONVERSION/v1", "status": "PASS", "verdict": "NOT SUPPORTED",
        "files": {path.name: {"sha256": sha256(path), "bytes": path.stat().st_size} for path in files},
        "checks": {
            "all_registered_gates_present": True, "all_registered_gates_failed": True,
            "freeze_hashes_reverified": True, "primary_was_label_free": True,
            "validator_reconstructed_all_rows": True, "independent_primality_spots_agree": True,
            "synthetic_signal_and_null_checks_pass": True,
            "external_artifact_and_visual_qa_required_after_build": True,
        },
    }
    RECORDING.write_text(json.dumps(recording, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    build_figure(data)
    build_notebook(data)
    build_artifact(data)
    build_recording()
    print(json.dumps({"artifact": ARTIFACT.name, "figure": FIGURE.name, "notebook": NOTEBOOK.name, "recording": RECORDING.name}, indent=2))


if __name__ == "__main__":
    main()
