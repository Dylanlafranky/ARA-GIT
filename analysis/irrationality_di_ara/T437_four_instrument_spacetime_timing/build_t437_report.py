"""Build the T437 visual audit, local HTML, and Data Analytics artifact payload."""

from __future__ import annotations

import base64
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PREDICTION_NPZ = RESULTS / "T437_WAVEFORM_ONLY_FOUR_INSTRUMENT_CLOCKS.npz"
PREDICTION_JSON = RESULTS / "T437_WAVEFORM_ONLY_FOUR_INSTRUMENT_CLOCKS.json"
SCORE_JSON = RESULTS / "T437_SCORED_RESULT.json"
FIGURE = RESULTS / "T437_FOUR_INSTRUMENT_TIMING_AUDIT.png"
HTML = RESULTS / "T437_FOUR_INSTRUMENT_TIMING_REPORT.html"
ARTIFACT = RESULTS / "T437_ARTIFACT_PAYLOAD.json"

COLORS = {
    "state": "#38bdf8",
    "path/history": "#f59e0b",
    "dynamic": "#ef4444",
    "rationality": "#a78bfa",
    "baseline": "#94a3b8",
    "physics crosswalk": "#22c55e",
    "horizon": "#f8fafc",
}


def downsample_indices(length: int, maximum: int) -> np.ndarray:
    if length <= maximum:
        return np.arange(length)
    return np.unique(np.linspace(0, length - 1, maximum).round().astype(int))


def timing_rows(score: dict) -> list[dict]:
    rows = []
    for row in score["timing_comparison"] + score["controls"]:
        item = dict(row)
        item["status"] = "within one cycle" if item["within_one_parent_cycle"] else "outside one cycle"
        rows.append(item)
    return rows


def make_figure(data: np.lib.npyio.NpzFile, prediction: dict, score: dict) -> None:
    plt.style.use("dark_background")
    fig, axes = plt.subplots(3, 2, figsize=(18, 16), constrained_layout=True)
    fig.patch.set_facecolor("#07111f")
    for ax in axes.flat:
        ax.set_facecolor("#0d1726")
        ax.grid(color="#334155", alpha=0.35)
        ax.tick_params(colors="#cbd5e1")
        for spine in ax.spines.values():
            spine.set_color("#475569")

    actual = float(score["actual_common_horizon_time_M"])
    cycle = float(score["local_parent_cycle_M"])
    t = data["waveform_time"]
    amp = data["waveform_amplitude"]
    relation = data["relation_ara"]
    zoom = (t >= 3350) & (t <= 3750)

    ax = axes[0, 0]
    ax.plot(t[zoom], amp[zoom] / np.max(amp[zoom]), color="#e2e8f0", lw=2.0, label="waveform amplitude")
    ax.plot(t[zoom], relation[zoom] / 2.0, color="#64748b", lw=1.3, alpha=0.8, label="parent relation / 2")
    ax.axvline(actual, color=COLORS["horizon"], ls="--", lw=2.0, label="common horizon")
    for row in score["timing_comparison"][:4]:
        ax.axvline(float(row["predicted_time_M"]), color=COLORS[row["instrument"]], lw=1.8, alpha=0.9, label=row["instrument"])
    ax.set_title("Where each ARA instrument placed the handover", fontsize=14, weight="bold")
    ax.set_xlabel("simulation time / M")
    ax.set_ylabel("display-normalised coordinate")
    ax.legend(fontsize=8, ncol=2, loc="upper left")

    ax = axes[0, 1]
    primary = score["timing_comparison"][:6]
    names = [r["instrument"].replace("path/history", "path") for r in primary]
    errors = [float(r["signed_error_M"]) for r in primary]
    colors = [COLORS.get(r["instrument"], "#94a3b8") for r in primary]
    bars = ax.barh(names[::-1], errors[::-1], color=colors[::-1])
    ax.axvline(0, color="#f8fafc", lw=1.2)
    ax.axvspan(-cycle, cycle, color="#22c55e", alpha=0.12, label="within one parent cycle")
    for bar, value in zip(bars, errors[::-1]):
        ax.text(value + (4 if value >= 0 else -4), bar.get_y() + bar.get_height()/2, f"{value:+.1f} M", va="center", ha="left" if value >= 0 else "right", fontsize=9)
    ax.set_title("Signed timing error", fontsize=14, weight="bold")
    ax.set_xlabel("predicted time − common-horizon time / M")
    ax.legend(fontsize=9)

    ax = axes[1, 0]
    st = data["state_time"]
    mask = (st >= 3350) & (st <= 3710) & np.isfinite(data["state_x_L"])
    ax.plot(st[mask], data["state_x_L"][mask], color=COLORS["state"], lw=2, label="state x_L (radius)")
    ax.plot(st[mask], data["state_x_C"][mask], color="#14b8a6", lw=1.4, label="state x_C (orientation)")
    ax.axhline(1, color="#f8fafc", ls="--", lw=1)
    ax.axvline(actual, color=COLORS["horizon"], ls=":", lw=2)
    ax.axvline(float(prediction["state_clock"]["time_M"]), color=COLORS["state"], ls="--", lw=2)
    ax.set_ylim(-0.05, 2.05)
    ax.set_title("State Irr-Di-ARA: one-parent-cycle radius relation", fontsize=14, weight="bold")
    ax.set_xlabel("simulation time / M")
    ax.set_ylabel("independent ARA coordinate / 0–2")
    ax.legend(fontsize=9)

    ax = axes[1, 1]
    pt = data["path_time"]
    mask = (pt >= 3350) & (pt <= 3710)
    ax.plot(pt[mask], data["path_x_P"][mask], color="#60a5fa", lw=1.5, label="x_P address openness")
    ax.plot(pt[mask], data["path_x_R"][mask], color=COLORS["path/history"], lw=1.5, label="x_R residual")
    ax.plot(pt[mask], data["path_rho"][mask], color="#22c55e", lw=1.3, label="closure coherence rho")
    ax.axhline(1, color="#f8fafc", ls="--", lw=1)
    ax.axvline(actual, color=COLORS["horizon"], ls=":", lw=2)
    ax.axvline(float(prediction["path_history_clock"]["time_M"]), color=COLORS["path/history"], ls="--", lw=2)
    ax.set_ylim(-0.05, 2.05)
    ax.set_title("Path/history Irr-Di-ARA: causal past-only reads", fontsize=14, weight="bold")
    ax.set_xlabel("simulation time / M")
    ax.set_ylabel("coordinate / 0–2 (rho / 0–1)")
    ax.legend(fontsize=9)

    ax = axes[2, 0]
    rt = data["rational_time"]
    mask = (rt >= 3350) & (rt <= 3710)
    ax.plot(rt[mask], data["rational_x_P"][mask], color="#60a5fa", lw=1.5, label="reverse x_P")
    ax.plot(rt[mask], data["rational_x_R"][mask], color=COLORS["rationality"], lw=1.5, label="reverse x_R")
    ax.plot(rt[mask], data["rational_rho"][mask], color="#22c55e", lw=1.3, label="reverse rho")
    ax.axhline(1, color="#f8fafc", ls="--", lw=1)
    ax.axvline(actual, color=COLORS["horizon"], ls=":", lw=2)
    ax.axvline(float(prediction["experimental_rationality_clock"]["time_M"]), color=COLORS["rationality"], ls="--", lw=2)
    ax.set_ylim(-0.05, 2.05)
    ax.set_title("Experimental Rationality: future support read backward", fontsize=14, weight="bold")
    ax.set_xlabel("forward-time anchor / M")
    ax.set_ylabel("coordinate / 0–2 (rho / 0–1)")
    ax.legend(fontsize=9)

    ax = axes[2, 1]
    psel = (pt >= 3350) & (pt <= 3710)
    rsel = (rt >= 3350) & (rt <= 3710)
    ax.plot(data["path_x_P"][psel], data["path_x_R"][psel], color=COLORS["path/history"], lw=1.0, alpha=0.65, label="path/history")
    ax.plot(data["rational_x_P"][rsel], data["rational_x_R"][rsel], color=COLORS["rationality"], lw=1.0, alpha=0.65, label="reverse Rationality")
    ax.scatter([prediction["path_history_clock"]["x_P"]], [prediction["path_history_clock"]["x_R"]], color=COLORS["path/history"], s=85, edgecolor="white", zorder=5)
    ax.scatter([prediction["experimental_rationality_clock"]["x_P"]], [prediction["experimental_rationality_clock"]["x_R"]], color=COLORS["rationality"], s=85, edgecolor="white", zorder=5)
    ax.axvline(1, color="#f8fafc", ls="--", lw=1)
    ax.axhline(1, color="#f8fafc", ls="--", lw=1)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Same path boundary viewed from opposite time support", fontsize=14, weight="bold")
    ax.set_xlabel("x_P: reused 0 → open 2")
    ax.set_ylabel("x_R: determined 0 → unresolved 2")
    ax.legend(fontsize=9)

    fig.suptitle("T437 — four ARA timing instruments on one black-hole merger", fontsize=24, weight="bold", color="#f8fafc")
    fig.savefig(FIGURE, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)


def build_payload(data: np.lib.npyio.NpzFile, prediction: dict, score: dict) -> dict:
    timing = timing_rows(score)
    primary = timing[:6]
    # Keep the native artifact compact enough for in-app rendering while the
    # full-resolution NPZ and static audit remain available locally.
    state_idx = downsample_indices(len(data["state_time"]), 120)
    path_idx = downsample_indices(len(data["path_time"]), 120)
    rational_idx = downsample_indices(len(data["rational_time"]), 120)

    state_history = []
    for i in state_idx:
        if not np.isfinite(data["state_x_L"][i]):
            continue
        for series, field in (("state x_L", "state_x_L"), ("state x_C", "state_x_C")):
            state_history.append({"time_M": float(data["state_time"][i]), "series": series, "coordinate": float(data[field][i])})
    path_history = []
    for i in path_idx:
        for series, field in (("x_P openness", "path_x_P"), ("x_R residual", "path_x_R"), ("rho coherence", "path_rho")):
            path_history.append({"time_M": float(data["path_time"][i]), "series": series, "coordinate": float(data[field][i])})
    rational_history = []
    for i in rational_idx:
        for series, field in (("reverse x_P", "rational_x_P"), ("reverse x_R", "rational_x_R"), ("reverse rho", "rational_rho")):
            rational_history.append({"time_M": float(data["rational_time"][i]), "series": series, "coordinate": float(data[field][i])})
    plane = []
    for method, idx, xp, xr, tm in (
        ("causal path/history", path_idx, data["path_x_P"], data["path_x_R"], data["path_time"]),
        ("reverse Rationality", rational_idx, data["rational_x_P"], data["rational_x_R"], data["rational_time"]),
    ):
        for i in idx:
            plane.append({"method": method, "time_M": float(tm[i]), "x_P": float(xp[i]), "x_R": float(xr[i])})

    sources = [
        {
            "id": "sxs0305",
            "label": "SXS:BBH:0305 Lev6 waveform",
            "href": "https://zenodo.org/records/13182440",
            "query": {
                "description": "T437 reads the sealed T435 waveform-only artifact; common-horizon time is opened only by the scorer.",
                "language": "Python",
                "tables_used": ["T435_WAVEFORM_ONLY_PREDICTION.npz", "T435_SCORED_RESULT.json"],
                "metric_definitions": [
                    "Signed error is predicted time minus first common-horizon time in simulation mass units M.",
                    "One-cycle success requires absolute error no greater than 11.3710 M.",
                ],
            },
        },
        {
            "id": "t437",
            "label": "T437 sealed prediction and scorer",
            "query": {
                "description": "Four independently defined ARA clocks, sealed before horizon scoring.",
                "language": "Python",
                "tables_used": ["T437_WAVEFORM_ONLY_FOUR_INSTRUMENT_CLOCKS.npz", "T437_SCORED_RESULT.json"],
            },
        },
    ]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "T437 — Four ARA timing instruments on one black-hole merger",
        "description": "State, path/history, dynamic and reverse-facing Rationality timing on SXS:BBH:0305.",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "cards": [],
        "charts": [
            {
                "id": "error_chart", "title": "Absolute timing error by instrument", "subtitle": "Only the state/power-crest crosswalk falls within one local parent cycle.", "type": "bar", "intent": "comparison", "dataset": "timing_errors", "sourceId": "t437",
                "encodings": {"x": {"field": "clock", "type": "nominal", "label": "Clock"}, "y": {"field": "absolute_error_M", "type": "quantitative", "label": "Absolute error", "unit": "M"}, "color": {"field": "status", "type": "nominal", "label": "One-cycle gate"}},
                "xAxisTitle": "Timing instrument", "yAxisTitle": "Absolute error / M", "layout": "full", "maxRows": 20,
            },
            {
                "id": "state_chart", "title": "State Irrationality Di-ARA coordinates", "subtitle": "The radial ridge read is the waveform-power crest, not an independent landmark.", "type": "line", "intent": "trend", "dataset": "state_history", "sourceId": "t437",
                "encodings": {"x": {"field": "time_M", "type": "quantitative", "label": "Simulation time", "unit": "M"}, "y": {"field": "coordinate", "type": "quantitative", "label": "ARA coordinate"}, "color": {"field": "series", "type": "nominal", "label": "Coordinate"}},
                "xAxisTitle": "Simulation time / M", "yAxisTitle": "Independent ARA coordinate / 0–2", "layout": "full", "maxRows": 1200,
            },
            {
                "id": "path_chart", "title": "Causal path/history Irrationality Di-ARA", "subtitle": "The path geometry remains coherent but selects a much earlier boundary.", "type": "line", "intent": "trend", "dataset": "path_history", "sourceId": "t437",
                "encodings": {"x": {"field": "time_M", "type": "quantitative", "label": "Simulation time", "unit": "M"}, "y": {"field": "coordinate", "type": "quantitative", "label": "Coordinate"}, "color": {"field": "series", "type": "nominal", "label": "Coordinate"}},
                "xAxisTitle": "Simulation time / M", "yAxisTitle": "Coordinate / 0–2 (rho / 0–1)", "layout": "full", "maxRows": 1600,
            },
            {
                "id": "rational_chart", "title": "Reverse-facing Rationality reconstruction", "subtitle": "Reading the settled waveform backward did not localize the common horizon.", "type": "line", "intent": "trend", "dataset": "rational_history", "sourceId": "t437",
                "encodings": {"x": {"field": "time_M", "type": "quantitative", "label": "Forward-time anchor", "unit": "M"}, "y": {"field": "coordinate", "type": "quantitative", "label": "Coordinate"}, "color": {"field": "series", "type": "nominal", "label": "Coordinate"}},
                "xAxisTitle": "Forward-time anchor / M", "yAxisTitle": "Coordinate / 0–2 (rho / 0–1)", "layout": "full", "maxRows": 1600,
            },
            {
                "id": "plane_chart", "title": "Path boundary from forward and reverse support", "subtitle": "Both views occupy a narrow determined/coherent band; neither supplied a specific event clock.", "type": "scatter", "intent": "relationship", "dataset": "path_plane", "sourceId": "t437",
                "encodings": {"x": {"field": "x_P", "type": "quantitative", "label": "Address openness"}, "y": {"field": "x_R", "type": "quantitative", "label": "Unresolved residual"}, "color": {"field": "method", "type": "nominal", "label": "Support direction"}, "tooltip": ["@{field=time_M; type=quantitative; label=Time; unit=M}"]},
                "xAxisTitle": "x_P / reused 0 → open 2", "yAxisTitle": "x_R / determined 0 → unresolved 2", "layout": "full", "maxRows": 1200,
            },
        ],
        "tables": [
            {
                "id": "timing_table", "title": "All primary clocks and controls", "subtitle": "Retrospective and causal clocks are kept distinct.", "dataset": "timing_all", "sourceId": "t437", "defaultSort": {"field": "absolute_error_M", "direction": "asc"}, "density": "spacious",
                "columns": [
                    {"field": "clock", "label": "Clock", "type": "text"},
                    {"field": "support", "label": "Support", "type": "text"},
                    {"field": "predicted_time_M", "label": "Predicted / M", "format": "number"},
                    {"field": "signed_error_M", "label": "Signed error / M", "format": "number", "movement": True},
                    {"field": "absolute_error_M", "label": "Absolute error / M", "format": "number"},
                    {"field": "error_parent_cycles", "label": "Parent cycles", "format": "number"},
                    {"field": "status", "label": "Gate", "type": "text"},
                ],
            }
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T437 — Four ARA timing instruments on one black-hole merger"},
            {"id": "summary", "type": "markdown", "body": "## Technical Summary\n\nThe state cut localized the event to 7.25 M (0.64 parent cycles), but its selected read is exactly the waveform-power maximum and is therefore a standard crest crosswalk. The causal path/history clock missed by 173.39 M, the unchanged dynamic clock by 99.24 M, and the experimental reverse Rationality reconstruction by 200.53 M. The proposed reverse-facing explanation is not supported by this implementation."},
            {"id": "error_block", "type": "chart", "chartId": "error_chart"},
            {"id": "state_finding", "type": "markdown", "body": "## State Result\n\nThe one-parent-cycle radius relation approaches its ridge at the amplitude crest. This improves on the T435 median clock, but it does not add an independent ARA landmark: changing from total power to the state radius coordinate restates the same crest relation."},
            {"id": "state_block", "type": "chart", "chartId": "state_chart"},
            {"id": "path_finding", "type": "markdown", "body": "## Path/History Result\n\nThe retained history is extremely coherent, yet the open-to-reused boundary occurs repeatedly and does not single out common-horizon formation. On this nearly deterministic chirp, support openness and local predictability describe the path but do not provide the missing event-time relation."},
            {"id": "path_block", "type": "chart", "chartId": "path_chart"},
            {"id": "rational_finding", "type": "markdown", "body": "## Reverse Rationality Result\n\nThe future-supported reverse read is a valid retrospective test of the user's settled-event idea, but its frozen boundary appears roughly 200.53 M early. Reversing support improves the internal distance compared with the causal path read, yet that lower geometric distance is not event specificity."},
            {"id": "rational_block", "type": "chart", "chartId": "rational_chart"},
            {"id": "plane_block", "type": "chart", "chartId": "plane_chart"},
            {"id": "table_block", "type": "table", "tableId": "timing_table"},
            {"id": "method", "type": "markdown", "body": "## Scope, Data and Method\n\nAll clocks use the sealed T435 SXS:BBH:0305 waveform-only artifact. State compares radius one local parent cycle apart. Path/history uses 128-sample past-only windows. Dynamic is imported unchanged from failed T436. Rationality uses 128 future samples read backward. The first common horizon is opened only by the separate scorer."},
            {"id": "limits", "type": "markdown", "body": "## Limitations and Robustness\n\nOnly one local SXS collision is available. Hashing prevents within-test retuning but does not turn historically known data into blind discovery. A quarter-record state control also fell within one cycle, so one-event timing proximity is not specific. Chronology shuffling strongly damaged both path distances, confirming that those instruments retain real order even though their selected clocks were wrong."},
            {"id": "next", "type": "markdown", "body": "## Next Step\n\nDo not tune another clock on BBH:0305. Acquire several additional SXS waveforms, freeze the state/crest crosswalk and path coordinates on a development subset, then test untouched mass-ratio/spin systems. The unresolved ARA question is whether a cross-instrument relation predicts the offset between common-horizon formation and the amplitude crest across systems."},
        ],
    }

    metric_row = [{
        "state_error": float(primary[0]["absolute_error_M"]), "state_cycles": float(primary[0]["error_parent_cycles"]),
        "path_error": float(primary[1]["absolute_error_M"]), "path_cycles": float(primary[1]["error_parent_cycles"]),
        "dynamic_error": float(primary[2]["absolute_error_M"]), "dynamic_cycles": float(primary[2]["error_parent_cycles"]),
        "rationality_error": float(primary[3]["absolute_error_M"]), "rationality_cycles": float(primary[3]["error_parent_cycles"]),
    }]
    snapshot = {
        "version": 1,
        "status": "ready",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "datasets": {
            "primary_timing": metric_row,
            "timing_errors": primary,
            "timing_all": timing,
            "state_history": state_history,
            "path_history": path_history,
            "rational_history": rational_history,
            "path_plane": plane,
        },
    }

    dataset_labels = {
        "timing_errors": "T437 primary timing errors",
        "timing_all": "T437 primary clocks and controls",
        "state_history": "T437 state coordinate history",
        "path_history": "T437 causal path/history coordinates",
        "rational_history": "T437 reverse Rationality coordinates",
        "path_plane": "T437 forward/reverse path plane",
    }

    def source_for(dataset: str) -> dict:
        filename = f"T437_ARTIFACT_{dataset.upper()}.csv"
        path = (RESULTS / filename).as_posix()
        return {
            "id": f"{dataset}_source",
            "label": dataset_labels[dataset],
            "path": str(RESULTS / filename),
            "query": {
                "engine": "DuckDB",
                "sql": f"SELECT * FROM read_csv_auto('{path}', header=true)",
                "description": f"Reviewed rows for {dataset_labels[dataset]}.",
                "language": "SQL",
                "tables_used": [filename],
            },
        }

    generated_sources = []
    for chart in manifest["charts"]:
        chart.pop("sourceId", None)
        chart["source"] = source_for(chart["dataset"])
        generated_sources.append(chart["source"])
    for table in manifest["tables"]:
        table.pop("sourceId", None)
        table["source"] = source_for(table["dataset"])
        generated_sources.append(table["source"])
    unique_generated = {item["id"]: item for item in generated_sources}
    sources.extend(unique_generated.values())
    return {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}


def write_snapshot_csvs(payload: dict) -> None:
    for dataset, rows in payload["snapshot"]["datasets"].items():
        if dataset == "primary_timing" or not rows:
            continue
        path = RESULTS / f"T437_ARTIFACT_{dataset.upper()}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


def make_html(score: dict) -> None:
    image_b64 = base64.b64encode(FIGURE.read_bytes()).decode("ascii")
    rows = timing_rows(score)
    table_rows = "".join(
        f"<tr><td>{r['clock']}</td><td>{r['support']}</td><td>{r['predicted_time_M']:.3f}</td>"
        f"<td>{r['signed_error_M']:+.3f}</td><td>{r['error_parent_cycles']:.3f}</td><td>{r['status']}</td></tr>"
        for r in sorted(rows, key=lambda x: x["absolute_error_M"])
    )
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>T437 four ARA clocks</title>
<style>body{{margin:0;background:#07111f;color:#e2e8f0;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1500px;margin:auto;padding:32px}}h1{{font-size:34px}}.callout{{background:#0d1726;border:1px solid #334155;border-radius:14px;padding:20px;margin:18px 0}}img{{width:100%;border-radius:14px;border:1px solid #334155}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #334155;text-align:left}}th{{color:#7dd3fc}}code{{color:#fbbf24}}</style></head><body><main>
<h1>T437 — Four ARA timing instruments on one black-hole merger</h1>
<div class='callout'><b>Outcome:</b> state landed within one parent cycle, but exactly at the ordinary waveform-power crest. Path/history, dynamic and reverse Rationality did not reconstruct common-horizon timing. This is one-event calibration, not population proof.</div>
<img src='data:image/png;base64,{image_b64}' alt='T437 six-panel visual audit'>
<h2>Clock comparison</h2><table><thead><tr><th>Clock</th><th>Support</th><th>Predicted / M</th><th>Signed error / M</th><th>Parent cycles</th><th>Gate</th></tr></thead><tbody>{table_rows}</tbody></table>
<h2>ARA reading</h2><p>The path/history and reverse Rationality coordinates retain chronology: shuffling makes their geometric distances much worse. But their best internal boundary is not the black-hole common horizon. On this signal, <code>rho≈1</code> across much of the chirp and <code>x_P=1</code> is crossed repeatedly, so the instrument records a coherent evolving path without uniquely locating the merger handover.</p>
<h2>Method boundary</h2><p>The fourth clock genuinely tested the settled-event idea by using later waveform samples in reverse. It is retrospective and therefore was never compared as a live forecast. Its failure means “read the resolved event backward using the same path boundary” is insufficient—not that every possible Rationality coordinate is ruled out.</p>
<h2>Recommended next move</h2><p>Do not fit BBH:0305 again. Add several SXS systems and freeze a cross-system test of the offset between the common horizon and the state/power crest. That distinguishes a transferable ARA timing relation from a single-waveform crosswalk.</p>
</main></body></html>"""
    HTML.write_text(html, encoding="utf-8")


def main() -> None:
    data = np.load(PREDICTION_NPZ)
    prediction = json.loads(PREDICTION_JSON.read_text(encoding="utf-8"))
    score = json.loads(SCORE_JSON.read_text(encoding="utf-8"))
    make_figure(data, prediction, score)
    payload = build_payload(data, prediction, score)
    write_snapshot_csvs(payload)
    ARTIFACT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    make_html(score)
    print(json.dumps({"figure": str(FIGURE), "html": str(HTML), "artifact": str(ARTIFACT)}, indent=2))


if __name__ == "__main__":
    main()
