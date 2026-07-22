"""Build the durable PN34 report, figure, executed notebook and MCP artifact source."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN34_FILL_RANK_BUDGET_RESULTS.json"
VALIDATION = HERE / "PN34_FILL_RANK_BUDGET_VALIDATION.json"
DEVELOPMENT = HERE / "PN34_FILL_RANK_BUDGET_DEVELOPMENT.json"
REPORT = HERE / "PN34_FILL_RANK_BUDGET_REPORT_2026-07-22.md"
FIGURE = HERE / "PN34_FILL_RANK_BUDGET_FIGURE.png"
NOTEBOOK = HERE / "PN34_FILL_RANK_BUDGET_REPRODUCIBILITY.ipynb"
NOTEBOOK_RECEIPT = HERE / "PN34_NOTEBOOK_EXECUTION_VALIDATION.json"
ARTIFACT = HERE / "PN34_FILL_RANK_BUDGET_REPORT_ARTIFACT.json"
RECORDING = HERE / "PN34_RECORDING_VALIDATION.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False):
    options = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in options:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def pct(value: float, digits: int = 3) -> str:
    return f"{100 * value:.{digits}f}%"


def make_figure(results: dict) -> None:
    image = Image.new("RGB", (1800, 1180), "#f7f9fc")
    draw = ImageDraw.Draw(image)
    navy, blue, gold, red, gray, dark = "#10243e", "#3777c7", "#d6a33b", "#bd3d4a", "#718096", "#17212b"
    draw.text((70, 45), "PN34 remaining-fill rank budget", font=font(48, True), fill=navy)
    draw.text((70, 108), "Fresh 6,000-anchor prospective test; predicted versus observed coverage", font=font(26), fill=gray)

    # Panel A: predicted and observed top-one coverage.
    x0, y0, x1, y1 = 80, 190, 850, 650
    draw.rounded_rectangle((x0, y0, x1, y1), 20, fill="white", outline="#dce3ec", width=2)
    draw.text((x0 + 28, y0 + 24), "A. First-reading calibration", font=font(30, True), fill=dark)
    plot_left, plot_top, plot_right, plot_bottom = x0 + 95, y0 + 100, x1 - 35, y1 - 75
    low_axis, high_axis = 0.90, 0.97
    for tick in (0.90, 0.92, 0.94, 0.96):
        yy = plot_bottom - (tick - low_axis) / (high_axis - low_axis) * (plot_bottom - plot_top)
        draw.line((plot_left, yy, plot_right, yy), fill="#e8edf3", width=2)
        draw.text((plot_left - 78, yy - 13), f"{100*tick:.0f}%", font=font(20), fill=gray)
    cohorts = results["cohorts"]
    group_width = (plot_right - plot_left) / 3
    for idx, row in enumerate(cohorts):
        centre = plot_left + (idx + 0.5) * group_width
        for offset, value, color in ((-34, row["predicted_top1"], blue), (34, row["observed_top1"], gold)):
            height = (value - low_axis) / (high_axis - low_axis) * (plot_bottom - plot_top)
            draw.rectangle((centre + offset - 26, plot_bottom - height, centre + offset + 26, plot_bottom), fill=color)
            draw.text((centre + offset, plot_bottom - height - 25), f"{100*value:.2f}", font=font(18, True), fill=color, anchor="mm")
        draw.text((centre, plot_bottom + 34), row["cohort"].title(), font=font(22, True), fill=dark, anchor="mm")
    draw.rectangle((x0 + 475, y0 + 32, x0 + 500, y0 + 55), fill=blue)
    draw.text((x0 + 512, y0 + 30), "Predicted", font=font(20), fill=dark)
    draw.rectangle((x0 + 615, y0 + 32, x0 + 640, y0 + 55), fill=gold)
    draw.text((x0 + 652, y0 + 30), "Observed", font=font(20), fill=dark)

    # Panel B: errors by depth and registered thresholds.
    x0, y0, x1, y1 = 900, 190, 1720, 650
    draw.rounded_rectangle((x0, y0, x1, y1), 20, fill="white", outline="#dce3ec", width=2)
    draw.text((x0 + 28, y0 + 24), "B. Absolute calibration error", font=font(30, True), fill=dark)
    rows = []
    for cohort in cohorts:
        for depth, error in enumerate(cohort["absolute_errors"], 1):
            rows.append((f"{cohort['cohort'].title()} / {depth}", 100 * error, depth))
    max_error = 0.9
    left, top, right, bottom = x0 + 170, y0 + 95, x1 - 45, y1 - 45
    row_h = (bottom - top) / len(rows)
    thresholds = {1: 1.5, 2: 0.5, 3: 0.15}
    for idx, (label, value, depth) in enumerate(rows):
        yy = top + (idx + 0.5) * row_h
        draw.text((left - 15, yy), label, font=font(18), fill=dark, anchor="rm")
        end = left + min(value / max_error, 1) * (right - left)
        draw.rectangle((left, yy - 9, end, yy + 9), fill=(blue if depth == 1 else gold if depth == 2 else "#5b9b78"))
        draw.text((end + 8, yy), f"{value:.03f} pp", font=font(17, True), fill=dark, anchor="lm")
    draw.text((x0 + 28, y1 - 32), "All 9 registered error thresholds passed.", font=font(21, True), fill="#2d7a54")

    # Panel C: benchmark log loss.
    x0, y0, x1, y1 = 80, 705, 850, 1090
    draw.rounded_rectangle((x0, y0, x1, y1), 20, fill="white", outline="#dce3ec", width=2)
    draw.text((x0 + 28, y0 + 24), "C. Top-one probability benchmark", font=font(30, True), fill=dark)
    bench = results["benchmark_top1"]
    labels = [("Fill prior", bench["fill_prior"]["log_loss"], blue), ("Flat PN26", bench["flat_pn26_prior"]["log_loss"], gray), ("Conditional PNT", bench["conditional_pnt_prior"]["log_loss"], red)]
    left, top, right, bottom = x0 + 185, y0 + 95, x1 - 55, y1 - 60
    max_v = 0.26
    row_h = (bottom - top) / 3
    for idx, (label, value, color) in enumerate(labels):
        yy = top + (idx + 0.5) * row_h
        draw.text((left - 15, yy), label, font=font(22, True), fill=dark, anchor="rm")
        end = left + value / max_v * (right - left)
        draw.rectangle((left, yy - 18, end, yy + 18), fill=color)
        draw.text((end + 12, yy), f"{value:.6f}", font=font(21, True), fill=dark, anchor="lm")
    draw.text((x0 + 28, y1 - 34), "Fill beat the frozen flat prior by 0.62% on log loss.", font=font(20), fill=gray)

    # Panel D: verdict and boundary.
    x0, y0, x1, y1 = 900, 705, 1720, 1090
    draw.rounded_rectangle((x0, y0, x1, y1), 20, fill="white", outline="#dce3ec", width=2)
    draw.text((x0 + 28, y0 + 24), "D. Formal reading", font=font(30, True), fill=dark)
    draw.text((x0 + 34, y0 + 102), "PARTIAL SUPPORT", font=font(42, True), fill=gold)
    notes = [
        "9 / 9 calibration thresholds passed",
        "6 / 6 rank-budget thresholds passed",
        "1 scale-order endpoint failed",
        "No within-cohort miss classifier was tested",
        "The calculation still retains the omitted prime gates",
    ]
    for idx, note in enumerate(notes):
        yy = y0 + 180 + idx * 47
        draw.ellipse((x0 + 38, yy - 7, x0 + 52, yy + 7), fill=(red if idx == 2 else blue))
        draw.text((x0 + 70, yy), note, font=font(22), fill=dark, anchor="lm")
    image.save(FIGURE)


def markdown_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code_cell(source: str, namespace: dict, count: int) -> dict:
    output = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(output):
            exec(compile(source, f"<PN34 notebook cell {count}>", "exec"), namespace)
    except Exception as exc:
        error = exc
    outputs = []
    if output.getvalue():
        outputs.append({"name": "stdout", "output_type": "stream", "text": output.getvalue().splitlines(keepends=True)})
    if error is not None:
        outputs.append({"ename": type(error).__name__, "evalue": str(error), "output_type": "error", "traceback": [f"{type(error).__name__}: {error}"]})
    return {"cell_type": "code", "execution_count": count, "metadata": {}, "outputs": outputs, "source": source.splitlines(keepends=True)}


def make_notebook() -> None:
    sources = [
        """from pathlib import Path\nimport csv, hashlib, json, math\nHERE = Path(r'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\primes')\nresults = json.loads((HERE/'PN34_FILL_RANK_BUDGET_RESULTS.json').read_text())\nvalidation = json.loads((HERE/'PN34_FILL_RANK_BUDGET_VALIDATION.json').read_text())\nprimary = json.loads((HERE/'PN34_FILL_RANK_BUDGET_PRIMARY.json').read_text())\nprint('Test:', results['test_id'])\nprint('Sealed rows:', primary['row_count'])\nprint('Prediction hash valid:', hashlib.sha256((HERE/primary['prediction_file']).read_bytes()).hexdigest() == primary['prediction_sha256'])\n""",
        """for row in results['cohorts']:\n    print(row['cohort'],\n          'x_B=', round(row['remaining_fill_x'], 6),\n          'top1 predicted/observed=', f\"{row['predicted_top1']:.4%}/{row['observed_top1']:.4%}\",\n          'top2=', f\"{row['predicted_top2']:.4%}/{row['observed_top2']:.4%}\",\n          'top3=', f\"{row['predicted_top3']:.4%}/{row['observed_top3']:.4%}\")\n""",
        """for row in results['cohorts']:\n    assert all(row['calibration_passes'])\n    assert all(row['budget_passes'])\nprint('Calibration checks:', 9, '/', 9)\nprint('Budget checks:', 6, '/', 6)\nprint('Predicted order:', results['predicted_scale_order'])\nprint('Observed order:', results['observed_scale_order'])\nprint('Direction endpoint:', 'PASS' if results['direction_pass'] else 'FAIL')\n""",
        """for name, values in results['benchmark_top1'].items():\n    print(name, 'Brier=', f\"{values['brier']:.9f}\", 'log loss=', f\"{values['log_loss']:.9f}\")\nfill = results['benchmark_top1']['fill_prior']['log_loss']\nflat = results['benchmark_top1']['flat_pn26_prior']['log_loss']\nprint('Fill log-loss improvement over flat:', f\"{(flat-fill)/flat:.3%}\")\n""",
        """scientific = {'registered_calibration_thresholds_pass', 'registered_rank_budgets_pass', 'registered_scale_direction_pass'}\nimplementation = {k:v for k,v in validation['checks'].items() if k not in scientific}\nassert all(implementation.values())\nassert validation['checks']['registered_scale_direction_pass'] is False\nprint('Implementation/reconstruction checks:', sum(implementation.values()), '/', len(implementation), 'PASS')\nprint('Formal verdict: PARTIAL SUPPORT because the registered scale-order endpoint failed.')\nprint('Boundary:', results['scientific_boundary'])\n""",
    ]
    namespace: dict = {}
    cells = [markdown_cell("""# PN34 remaining-fill rank budget\n\nThis executed notebook audits the frozen PN34 bridge. It reads sealed predictions and independently validated truth; it does not refit the coordinate.\n""")]
    for count, source in enumerate(sources, 1):
        cells.append(code_cell(source, namespace, count))
    cells.append(markdown_cell("""## Plain-language result\n\nThe untested Phase B gate density predicted how often PN26's first, second and third quiet readings would be needed. All nine calibration tolerances passed on 6,000 fresh anchors. The exact middle-to-high ordering did not, so this is partial support for a population rank budget, not a rule that identifies the individual miss.\n"""))
    notebook = {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
    errors = [out for cell in cells if cell.get("cell_type") == "code" for out in cell["outputs"] if out["output_type"] == "error"]
    receipt = {"validation_id": "PN34/NOTEBOOK-EXECUTION/v1", "created_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS" if not errors else "FAIL", "code_cells_executed": len(sources), "code_cells_total": len(sources), "failures": errors}
    NOTEBOOK_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if errors:
        raise RuntimeError(errors)


def make_report(results: dict, validation: dict) -> None:
    cohorts = results["cohorts"]
    fill = results["benchmark_top1"]["fill_prior"]
    flat = results["benchmark_top1"]["flat_pn26_prior"]
    pnt = results["benchmark_top1"]["conditional_pnt_prior"]
    lines = [
        "# PN34 — remaining-fill rank budget",
        "",
        "**Run:** 22 July 2026  ",
        "**Formal status:** **PARTIAL SUPPORT**  ",
        "**Fresh test:** 6,000 prospectively frozen anchors across three previously unused scales  ",
        "**Implementation/reconstruction:** all non-endpoint checks passed",
        "",
        "## Answer first",
        "",
        "Yes—the useful relation is real, but it is a **population rank-budget rule**, not an individual prime cheat.",
        "",
        "PN34 combined PN26's complete Phase A quiet-state locator with the PN33 inverse-density fill of the omitted Phase B parent. Without fitting to the fresh labels, it predicted how often the true next prime would appear in the first, first two and first three Phase A quiet states. All **9/9 calibration tolerances** and all **6/6 rank-budget thresholds** passed.",
        "",
        "Full support was blocked by one deliberately strict endpoint: predicted first-reading success increased low → middle → high, while the observed middle and high cohorts swapped by only **0.20 percentage points**. The formal verdict is therefore partial support.",
        "",
        "| Scale | Remaining fill x_B | Top 1 predicted | Top 1 observed | Top 2 predicted | Top 2 observed | Top 3 predicted | Top 3 observed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in cohorts:
        lines.append(f"| {row['cohort']} | {row['remaining_fill_x']:.6f} | {pct(row['predicted_top1'])} | {pct(row['observed_top1'])} | {pct(row['predicted_top2'])} | {pct(row['observed_top2'])} | {pct(row['predicted_top3'])} | {pct(row['observed_top3'])} |")
    lines += [
        "",
        "## What the bridge means in plain language",
        "",
        "PN26 first removes every position struck by the complete lower Phase A parent. Its remaining quiet positions are strong prime candidates. Phase B is the omitted upper band of factor gates that can still turn some of those candidates into composites.",
        "",
        "PN34 measured the unresolved Phase B thinning as",
        "",
        "```text",
        "R_B = product over Phase B of p/(p-1)",
        "x_B = 2 log(R_B)/log(2)",
        "first-reading prior = 1/R_B = 2^(-x_B/2)",
        "top-k coverage = 1 - (1 - first-reading prior)^k",
        "```",
        "",
        "Plainly: if the omitted parent is small, most Phase A quiet states survive it and the first reading is usually enough. The residual failure probability tells us how quickly a second and third reading close the ranked list.",
        "",
        "## Fresh rank counts",
        "",
        "| Scale | Rank 1 | Rank 2 | Rank 3 | Beyond rank 3 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in cohorts:
        counts = row["rank_counts_1_2_3_over3"]
        lines.append(f"| {row['cohort']} | {counts[0]:,} | {counts[1]:,} | {counts[2]:,} | {counts[3]:,} |")
    lines += [
        "",
        "Across all three scales, two readings exceeded 99% coverage and three reached at least 99.9%. The fresh data contained three cases beyond rank three, so the construction remains an extremely short ranked approximation rather than a universal three-state identity.",
        "",
        "## Benchmark reading",
        "",
        f"The fill prior's top-one log loss was `{fill['log_loss']:.9f}`, versus `{flat['log_loss']:.9f}` for the frozen pooled PN26 prior and `{pnt['log_loss']:.9f}` for the simple conditional PNT prior. That is only a `{(flat['log_loss']-fill['log_loss'])/flat['log_loss']:.2%}` improvement over the already-strong flat prior, but a `{(pnt['log_loss']-fill['log_loss'])/pnt['log_loss']:.2%}` improvement over the tested PNT conditional approximation.",
        "",
        "The comparison matters: most predictive power still comes from PN26's complete Phase A parent. PN34 adds a small but coherent scale-aware calibration layer.",
        "",
        "## Why the greater-than-1.5 shortcut is not the rule",
        "",
        "The prospectively successful coordinate was not `max child > 1.5`. The relevant remaining-fill readings were only `0.134–0.216`. Earlier direct five-wave threshold checks rejected true primes and hard composites at almost the same rate. The successful object is the **complete omitted-parent density**, not one child's largest local coordinate.",
        "",
        "## Scientific boundary",
        "",
        "PN34 supports:",
        "",
        "- a prospective bridge from PN33-style fill to PN26 rank depth;",
        "- a no-fit population prior that calibrated all nine fresh scale/depth cells; and",
        "- the interpretation that the omitted upper parent supplies the residual correction budget.",
        "",
        "PN34 does not support:",
        "",
        "- identifying which individual first candidate is composite;",
        "- skipping construction of the lower/upper prime-gate parents;",
        "- constant-cost prime generation or certification;",
        "- improved asymptotic complexity; or",
        "- new number theory beyond an ARA crosswalk to conditional sieve density.",
        "",
        "## Validation and uncertainty",
        "",
        f"The prediction file was sealed before truth was opened. Independent reconstruction reproduced every candidate and prior at all three scales. Prime truth came from separately constructed segmented masks with deterministic Miller–Rabin spot checks. The validation receipt recorded `{validation['passed']}/{validation['total']}` total checks; the sole false check is the registered scientific scale-order endpoint, not an implementation mismatch.",
        "",
        "At the high scale, the predicted three-reading coverage (`99.9906%`) sat slightly above the observed Wilson interval because two of 2,000 anchors fell beyond rank three. This is another reason to retain the partial verdict and not overstate the population formula as exact.",
        "",
        "## Recommended next step",
        "",
        "Keep PN34 as the population-budget explanation for PN26. The next genuinely new target would require an anchor-varying, pre-label coordinate derived from the omitted parent that separates the rare rank-1 misses **within one scale**. Without that, the fill prior tells us how many readings to keep, not which reading wins.",
        "",
        "## Artifacts",
        "",
        "- Fidelity packet and frozen protocol: `PN34_FILL_RANK_BUDGET_FIDELITY_PACKET_v1_DRAFT.md`, `PN34_FILL_RANK_BUDGET_PROTOCOL_v1_FROZEN.md`",
        "- Frozen predictions: `PN34_FILL_RANK_BUDGET_PREDICTIONS.csv`",
        "- Results and validation: `PN34_FILL_RANK_BUDGET_RESULTS.json`, `PN34_FILL_RANK_BUDGET_VALIDATION.json`",
        "- Validated rows: `PN34_FILL_RANK_BUDGET_VALIDATED_ROWS.csv`",
        "- Figure and notebook: `PN34_FILL_RANK_BUDGET_FIGURE.png`, `PN34_FILL_RANK_BUDGET_REPRODUCIBILITY.ipynb`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_artifact(results: dict) -> None:
    depth_rows = []
    cohort_rows = []
    for row in results["cohorts"]:
        cohort_rows.append({
            "cohort": row["cohort"].title(),
            "fill_x": row["remaining_fill_x"],
            "phase_a_children": row["phase_a_count"],
            "phase_b_children": row["phase_b_count"],
            "rank1": row["rank_counts_1_2_3_over3"][0],
            "rank2": row["rank_counts_1_2_3_over3"][1],
            "rank3": row["rank_counts_1_2_3_over3"][2],
            "over3": row["rank_counts_1_2_3_over3"][3],
        })
        for depth in (1, 2, 3):
            key = f"{row['cohort'].title()} / {depth}"
            depth_rows.extend([
                {"cohort_depth": key, "cohort": row["cohort"].title(), "depth": depth, "series": "Predicted", "coverage_percent": 100 * row[f"predicted_top{depth}"]},
                {"cohort_depth": key, "cohort": row["cohort"].title(), "depth": depth, "series": "Observed", "coverage_percent": 100 * row[f"observed_top{depth}"]},
            ])
    benchmark_rows = [
        {"method": "Fill prior", "log_loss": results["benchmark_top1"]["fill_prior"]["log_loss"]},
        {"method": "Flat PN26 prior", "log_loss": results["benchmark_top1"]["flat_pn26_prior"]["log_loss"]},
        {"method": "Conditional PNT", "log_loss": results["benchmark_top1"]["conditional_pnt_prior"]["log_loss"]},
    ]
    manifest = {
        "version": 1,
        "surface": "report",
        "title": "PN34: Remaining-fill rank budget",
        "description": "Prospective technical report joining PN33 fill with PN26 ranked prime candidates.",
        "generatedAt": "2026-07-22T20:09:00+10:00",
        "cards": [
            {"id": "calibration_card", "dataset": "headline", "sourceId": "pn34_results", "metrics": [{"label": "Calibration cells passed", "field": "calibration", "format": "text"}]},
            {"id": "budget_card", "dataset": "headline", "sourceId": "pn34_results", "metrics": [{"label": "Rank-budget thresholds passed", "field": "budgets", "format": "text"}]},
            {"id": "direction_card", "dataset": "headline", "sourceId": "pn34_results", "metrics": [{"label": "Scale-order endpoint", "field": "direction", "format": "text"}]},
            {"id": "benchmark_card", "dataset": "headline", "sourceId": "pn34_results", "metrics": [{"label": "Log-loss gain vs flat", "field": "flat_gain_percent", "format": "number"}]},
        ],
        "charts": [
            {"id": "coverage_chart", "title": "Predicted and observed rank coverage", "subtitle": "All nine calibration tolerances passed on 6,000 fresh anchors", "type": "bar", "intent": "comparison", "dataset": "coverage", "sourceId": "pn34_results", "legend": {"position": "bottom", "title": "Series"}, "encodings": {"x": {"field": "cohort_depth", "type": "nominal", "label": "Scale / retained readings"}, "y": {"field": "coverage_percent", "type": "quantitative", "label": "Coverage (%)"}, "color": {"field": "series", "type": "nominal", "label": "Series"}, "tooltip": [{"field": "cohort", "type": "nominal", "label": "Scale"}, {"field": "depth", "type": "quantitative", "label": "Readings"}, {"field": "coverage_percent", "type": "quantitative", "label": "Coverage (%)"}]}},
            {"id": "benchmark_chart", "title": "Top-one probability log loss", "subtitle": "The scale-aware fill prior improved only slightly on the strong frozen flat prior", "type": "bar", "intent": "comparison", "dataset": "benchmarks", "sourceId": "pn34_results", "encodings": {"x": {"field": "method", "type": "nominal", "label": "Method"}, "y": {"field": "log_loss", "type": "quantitative", "label": "Log loss"}, "tooltip": [{"field": "log_loss", "type": "quantitative", "label": "Log loss"}]}},
        ],
        "tables": [
            {"id": "rank_table", "title": "Fresh candidate-rank counts", "subtitle": "2,000 deterministic anchors at each previously unused scale", "dataset": "cohorts", "sourceId": "pn34_rows", "defaultSort": {"field": "phase_a_children", "direction": "asc"}, "columns": [{"field": "cohort", "label": "Scale", "type": "text"}, {"field": "fill_x", "label": "Remaining fill x_B", "type": "number"}, {"field": "phase_a_children", "label": "Phase A children", "type": "number"}, {"field": "phase_b_children", "label": "Phase B children", "type": "number"}, {"field": "rank1", "label": "Rank 1", "type": "number"}, {"field": "rank2", "label": "Rank 2", "type": "number"}, {"field": "rank3", "label": "Rank 3", "type": "number"}, {"field": "over3", "label": "Beyond 3", "type": "number"}]},
        ],
        "sources": [
            {"id": "pn34_results", "label": "PN34 sealed predictions and independently scored results", "path": "analysis/primes/PN34_FILL_RANK_BUDGET_RESULTS.json"},
            {"id": "pn34_rows", "label": "PN34 independently validated candidate rows", "path": "analysis/primes/PN34_FILL_RANK_BUDGET_VALIDATED_ROWS.csv"},
            {"id": "pn34_protocol", "label": "PN34 frozen protocol", "path": "analysis/primes/PN34_FILL_RANK_BUDGET_PROTOCOL_v1_FROZEN.md"},
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# PN34: Remaining-fill rank budget"},
            {"id": "technical_summary", "type": "markdown", "sourceId": "pn34_results", "body": "## The fill coordinate calibrated rank depth, but not the individual miss\n\nOn 6,000 fresh anchors, all **9/9 calibration tolerances** and **6/6 rank-budget thresholds** passed. The fill prior predicted first-reading success within **0.06–0.79 percentage points** and correctly kept two readings above 99% and three at or above 99.9% in every cohort. One registered endpoint failed: middle and high first-reading order swapped by 0.20 points. Formal verdict: **partial support**."},
            {"id": "headline_metrics", "type": "metric-strip", "cardIds": ["calibration_card", "budget_card", "direction_card", "benchmark_card"]},
            {"id": "coverage_intro", "type": "markdown", "body": "## Predicted and observed coverage stayed close across all three depths\n\nThe chart pairs the frozen population prior with the opened coverage at each scale and rank depth. The near-overlap supports the budget interpretation: Phase B's remaining inverse density tells us how many Phase A quiet readings to retain. It does not reveal which particular first reading will fail."},
            {"id": "coverage", "type": "chart", "chartId": "coverage_chart"},
            {"id": "coverage_note", "type": "markdown", "body": "The high-scale top-three prediction was slightly above its observed Wilson interval because two of 2,000 anchors fell beyond rank three. The registered absolute-error tolerance still passed, but this tail miss reinforces the partial rather than exact reading."},
            {"id": "rank_table_intro", "type": "markdown", "body": "## Three readings remained nearly complete, not universally complete\n\nOnly three of 6,000 fresh anchors required more than three Phase A quiet states. That is excellent ranked compression, but it directly falsifies any universal three-state claim."},
            {"id": "rank_table", "type": "table", "tableId": "rank_table"},
            {"id": "benchmark_intro", "type": "markdown", "body": "## The new calibration layer adds a small gain over PN26's flat prior\n\nMost predictive power comes from the complete Phase A parent. The fill coordinate reduced log loss by only **0.62%** versus the frozen pooled PN26 prior, although it materially beat the tested conditional PNT approximation. This is a coherent scale correction, not a new prime algorithm."},
            {"id": "benchmark", "type": "chart", "chartId": "benchmark_chart"},
            {"id": "definitions", "type": "markdown", "body": "## The metric is the omitted parent's unresolved fill\n\nFor Phase B, **R_B = product p/(p-1)** and **x_B = 2 log(R_B)/log 2**. The first-reading prior is **1/R_B = 2^(-x_B/2)**; top-k coverage is **1-(1-1/R_B)^k**. The successful fresh readings were x_B=0.134–0.216, so the earlier `max child > 1.5` cutoff is not this rule."},
            {"id": "method", "type": "markdown", "sourceId": "pn34_protocol", "body": "## Predictions were sealed before fresh truth was opened\n\nThe frozen primary builder sampled 2,000 anchors at each of three unused scales, reconstructed PN26's cumulative-log parent split, sealed three candidates, and attached the no-fit fill prior without a primality routine. The validator independently rebuilt the parent, segmented prime truth and deterministic Miller–Rabin checks. Every freeze and reconstruction check passed."},
            {"id": "limitations", "type": "markdown", "body": "## This calibrates search depth; it does not select the winner\n\nThe fill coordinate is constant inside each cohort. It therefore cannot distinguish a rank-1 hit from a rank-1 miss at the same scale. Constructing R_B also retains every omitted prime gate, so PN34 supplies neither constant-cost computation nor asymptotic speedup. Its number-theoretic content is a crosswalk to conditional sieve density."},
            {"id": "next", "type": "markdown", "body": "## Next test: require a varying pre-label residual inside one scale\n\nResume only if an anchor-varying statistic can be defined from the omitted parent before labels and can rank the rare first-state misses within a single cohort. Compare it against raw residues and upper-band sieve controls. Until then, retain PN34 as the population-budget explanation for PN26."},
            {"id": "questions", "type": "markdown", "body": "## Open questions\n\n- Can the omitted parent be compressed into an anchor-varying residual without reconstructing all its gates?\n- Do the three beyond-rank-3 cases share a pre-label upper-band relation?\n- Does the small fill-versus-flat log-loss gain persist on another disjoint set of scales?"},
        ],
    }
    fill_ll = results["benchmark_top1"]["fill_prior"]["log_loss"]
    flat_ll = results["benchmark_top1"]["flat_pn26_prior"]["log_loss"]
    snapshot = {
        "version": 1,
        "generatedAt": "2026-07-22T20:09:00+10:00",
        "status": "ready",
        "datasets": {
            "headline": [{"calibration": "9 / 9", "budgets": "6 / 6", "direction": "FAIL", "flat_gain_percent": 100 * (flat_ll - fill_ll) / flat_ll}],
            "coverage": depth_rows,
            "benchmarks": benchmark_rows,
            "cohorts": cohort_rows,
        },
    }
    ARTIFACT.write_text(json.dumps({"surface": "report", "manifest": manifest, "snapshot": snapshot}, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    outputs = (REPORT, FIGURE, NOTEBOOK, NOTEBOOK_RECEIPT, ARTIFACT, RECORDING)
    for path in outputs:
        if path.exists():
            raise RuntimeError(f"refusing to overwrite {path.name}")
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    make_figure(results)
    make_notebook()
    make_report(results, validation)
    make_artifact(results)
    checks = {
        "report_exists": REPORT.exists(),
        "figure_exists": FIGURE.exists(),
        "figure_dimensions": Image.open(FIGURE).size == (1800, 1180),
        "notebook_execution_pass": json.loads(NOTEBOOK_RECEIPT.read_text())["status"] == "PASS",
        "artifact_has_report_surface": json.loads(ARTIFACT.read_text())["surface"] == "report",
        "artifact_has_two_charts": len(json.loads(ARTIFACT.read_text())["manifest"]["charts"]) == 2,
        "report_states_partial_support": "**PARTIAL SUPPORT**" in REPORT.read_text(encoding="utf-8"),
        "report_preserves_individual_boundary": "not an individual prime cheat" in REPORT.read_text(encoding="utf-8"),
    }
    receipt = {"validation_id": "PN34/RECORDING/v1", "created_utc": datetime.now(timezone.utc).isoformat(), "checks": checks, "passed": sum(checks.values()), "total": len(checks), "all_passed": all(checks.values()), "hashes": {path.name: sha256(path) for path in outputs if path.exists() and path != RECORDING}}
    RECORDING.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
