#!/usr/bin/env python3
"""T370B: frozen in-band muon parent-phase lineage extension."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

import t370_polarized_muon_phase_handover as t370


HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw_full"
RUNS = [
    "EMU00066627", "EMU00066651", "EMU00066652", "EMU00066654", "EMU00066655",
    "EMU00066656", "EMU00066657", "EMU00066658", "EMU00066659",
    "EMU00066660", "EMU00066661", "EMU00066662", "EMU00066663",
    "EMU00066669",
]
GAMMA_MHZ_PER_G = 0.013553896
REQUIRED = 10

RESULTS = HERE / "T370B_MUON_PHASE_LINEAGE_RESULTS.json"
RUN_CSV = HERE / "T370B_MUON_PHASE_LINEAGE_RUNS.csv"
FIGURE = HERE / "T370B_MUON_PHASE_LINEAGE_FIGURE.svg"
REPORT = HERE / "T370B_MUON_PHASE_LINEAGE_REPORT_2026-08-12.md"
POSTHOC_520 = HERE / "T370B_520G_SAMPLING_DIAGNOSTIC.json"


def run_path(run: str) -> Path:
    matches = list(RAW.rglob(f"{run}.nxs"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one archive file for {run}, found {len(matches)}")
    return matches[0]


def copy_selected_runs() -> None:
    t370.DATA.mkdir(exist_ok=True)
    for run in RUNS:
        source = run_path(run)
        target = t370.DATA / source.name
        if not target.exists() or target.stat().st_size != source.stat().st_size:
            target.write_bytes(source.read_bytes())


def field_from_title(title: str) -> float:
    match = re.search(r"\bF=([0-9.]+)", title)
    if not match:
        raise ValueError(f"No field in title: {title}")
    return float(match.group(1))


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    xr = pd.Series(x).rank(method="average").to_numpy()
    yr = pd.Series(y).rank(method="average").to_numpy()
    return float(np.corrcoef(xr, yr)[0, 1])


def main() -> None:
    copy_selected_runs()
    t370.FREQUENCIES = np.arange(0.10, 7.8001, 0.01)
    t370.DECAYS = np.arange(0.0, 1.5001, 0.05)

    rows = []
    detailed = []
    for run in RUNS:
        result, _, _ = t370.analyse_run(run)
        field = field_from_title(result["title"])
        expected = GAMMA_MHZ_PER_G * field
        relative_error = abs(result["frequency_mhz"] - expected) / expected
        geometry_registered = result["circular_shift_better_count"] == 0
        ara_pass = bool(result["pass"] and geometry_registered)
        resolved = bool(ara_pass and relative_error <= 0.05)
        record = {
            **result,
            "field_gauss": field,
            "expected_frequency_mhz": expected,
            "frequency_relative_error": relative_error,
            "registered_detector_geometry_pass": geometry_registered,
            "ara_holdout_pass": ara_pass,
            "resolved_parent_phase_pass": resolved,
        }
        detailed.append(record)
        rows.append({
            "run": run,
            "field_gauss": field,
            "recovered_frequency_mhz": result["frequency_mhz"],
            "expected_frequency_mhz": expected,
            "frequency_relative_error": relative_error,
            "holdout_improvement_vs_no_phase": result["improvement_vs_no_phase"],
            "holdout_correlation": result["holdout_correlation"],
            "circular_shift_better_count": result["circular_shift_better_count"],
            "ara_holdout_pass": ara_pass,
            "resolved_parent_phase_pass": resolved,
        })

    frame = pd.DataFrame(rows).sort_values(["field_gauss", "run"])
    fields = frame.field_gauss.to_numpy()
    frequencies = frame.recovered_frequency_mhz.to_numpy()
    rank_correlation = spearman(fields, frequencies)
    slope = float(np.dot(fields, frequencies) / np.dot(fields, fields))
    slope_relative_error = abs(slope - GAMMA_MHZ_PER_G) / GAMMA_MHZ_PER_G
    duplicate_200 = frame.loc[frame.field_gauss == 200, "recovered_frequency_mhz"].to_numpy()
    duplicate_difference = float(abs(duplicate_200[0] - duplicate_200[1]))
    pass_count = int(frame.resolved_parent_phase_pass.sum())
    gates = {
        "resolved_runs_at_least_10_of_14": pass_count >= REQUIRED,
        "field_frequency_spearman_at_least_0_90": rank_correlation >= 0.90,
        "slope_within_5_percent": slope_relative_error <= 0.05,
        "duplicate_200G_within_0_10_mhz": duplicate_difference <= 0.10,
    }
    overall = all(gates.values())

    excluding_boundary = frame[frame.field_gauss < 520].copy()
    ex_fields = excluding_boundary.field_gauss.to_numpy()
    ex_frequencies = excluding_boundary.recovered_frequency_mhz.to_numpy()
    ex_spearman = spearman(ex_fields, ex_frequencies)
    ex_slope = float(np.dot(ex_fields, ex_frequencies) / np.dot(ex_fields, ex_fields))
    ex_slope_error = abs(ex_slope - GAMMA_MHZ_PER_G) / GAMMA_MHZ_PER_G
    posthoc_520 = json.loads(POSTHOC_520.read_text(encoding="utf-8")) if POSTHOC_520.exists() else None

    frame.to_csv(RUN_CSV, index=False)
    result = {
        "test": "T370B muon parent-phase lineage across an in-band field ladder",
        "status": "SUPPORTED_AS_CROSSWALK" if overall else "NOT_SUPPORTED",
        "source": {"doi": t370.SOURCE_DOI, "url": t370.SOURCE_URL},
        "selection": "Complete positive-count LCB1-88 T=135.0 acquisition family with 0 < F <= 520 G",
        "run_count": len(frame),
        "resolved_parent_phase_pass_count": pass_count,
        "required": REQUIRED,
        "field_frequency_spearman": rank_correlation,
        "recovered_slope_mhz_per_gauss": slope,
        "independent_slope_mhz_per_gauss": GAMMA_MHZ_PER_G,
        "slope_relative_error": slope_relative_error,
        "duplicate_200G_frequency_difference_mhz": duplicate_difference,
        "gates": gates,
        "overall_pass": overall,
        "diagnostics_not_part_of_frozen_gate": {
            "excluding_unresolved_520G": {
                "run_count": len(excluding_boundary),
                "field_frequency_spearman": ex_spearman,
                "recovered_slope_mhz_per_gauss": ex_slope,
                "slope_relative_error": ex_slope_error,
            },
            "520G_at_twice_time_resolution": posthoc_520,
        },
        "runs": detailed,
        "claim_boundary": (
            "A pass recovers the established precessing parent-spin relation in ARA geometry from raw counts. "
            "The neutrino pair remains an unobserved conservation-derived daughter complement."
        ),
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_svg(frame, result)
    make_report(frame, result)
    print(json.dumps({
        "status": result["status"],
        "pass_count": pass_count,
        "spearman": rank_correlation,
        "slope_relative_error": slope_relative_error,
    }, indent=2))


def make_svg(frame: pd.DataFrame, result: dict) -> None:
    width, height = 1500, 980
    left, top, plot_w, plot_h = 95, 155, 620, 580
    xmax = 550.0
    ymax = 7.8

    def sx(v): return left + plot_w * v / xmax
    def sy(v): return top + plot_h * (1.0 - v / ymax)

    expected_line = f"{sx(0):.1f},{sy(0):.1f} {sx(xmax):.1f},{sy(GAMMA_MHZ_PER_G*xmax):.1f}"
    points = []
    for row in frame.itertuples():
        cls = "pass" if row.resolved_parent_phase_pass else "fail"
        points.append(
            f'<circle cx="{sx(row.field_gauss):.1f}" cy="{sy(row.recovered_frequency_mhz):.1f}" r="8" class="{cls}"/>'
            f'<text x="{sx(row.field_gauss)+10:.1f}" y="{sy(row.recovered_frequency_mhz)-8:.1f}" class="tiny">{int(row.field_gauss)} G</text>'
        )

    qx, qy, qw, qh = 815, 155, 590, 580
    bars = []
    max_imp = max(0.12, float(frame.holdout_improvement_vs_no_phase.max()) * 1.1)
    for i, row in enumerate(frame.itertuples()):
        bw = qw / len(frame) * 0.63
        x = qx + (i + 0.18) * qw / len(frame)
        val = row.holdout_improvement_vs_no_phase
        h = qh * max(val, 0) / max_imp
        cls = "barpass" if row.ara_holdout_pass else "barfail"
        bars.append(
            f'<rect x="{x:.1f}" y="{qy+qh-h:.1f}" width="{bw:.1f}" height="{h:.1f}" class="{cls}"/>'
            f'<text x="{x+bw/2:.1f}" y="{qy+qh+20:.1f}" text-anchor="middle" class="tiny" transform="rotate(45 {x+bw/2:.1f} {qy+qh+20:.1f})">{int(row.field_gauss)}G</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>text{{font-family:Segoe UI,Arial,sans-serif;fill:#273142}}.bg{{fill:#f7f9fc}}.panel{{fill:#fff;stroke:#cfd7e3;stroke-width:1.5}}.grid{{stroke:#dce2eb;stroke-width:1}}.ridge{{stroke:#2f3947;stroke-width:1.4}}.expected{{fill:none;stroke:#d9902e;stroke-width:3}}.pass{{fill:#3f78bf;stroke:#255083;stroke-width:1.5}}.fail{{fill:#d96c5f;stroke:#8f352d;stroke-width:1.5}}.barpass{{fill:#5f89c9}}.barfail{{fill:#d98a7e}}.title{{font-size:23px;font-weight:650}}.sub{{font-size:15px;fill:#667085}}.tiny{{font-size:12px;fill:#566275}}.metric{{font-size:18px;font-weight:650}}</style>
<rect width="100%" height="100%" class="bg"/><text x="70" y="52" style="font-size:32px;font-weight:700">T370B — parent relation across the decay handover</text>
<text x="70" y="84" class="sub">Complete 135 K in-band field ladder · raw 96-detector counts · development before 3 µs · untouched holdout after 3 µs</text>
<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" class="panel"/><text x="{left}" y="{top-48}" class="title">ARA cadence recovered without using the field</text><text x="{left}" y="{top-22}" class="sub">Gold = independently expected parent-spin cadence · blue = pass · red = fail</text>
<line x1="{left}" y1="{sy(0):.1f}" x2="{left+plot_w}" y2="{sy(0):.1f}" class="ridge"/><line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" class="ridge"/><polyline points="{expected_line}" class="expected"/>{''.join(points)}
<text x="{left+plot_w/2}" y="{top+plot_h+55}" text-anchor="middle" class="sub">applied field (gauss)</text><text x="28" y="{top+plot_h/2}" text-anchor="middle" class="sub" transform="rotate(-90 28 {top+plot_h/2})">recovered parent cadence (MHz)</text>
<rect x="{qx}" y="{qy}" width="{qw}" height="{qh}" class="panel"/><text x="{qx}" y="{qy-48}" class="title">Untouched holdout gain</text><text x="{qx}" y="{qy-22}" class="sub">Improvement over a detector pattern with no moving parent phase</text>{''.join(bars)}
<text x="70" y="835" class="metric">Resolved runs: {result['resolved_parent_phase_pass_count']}/14 (required 10) · rank relation {result['field_frequency_spearman']:.3f} · slope error {100*result['slope_relative_error']:.2f}%</text>
<text x="70" y="873" class="sub">ARA reading: an opposing two-coordinate parent relation present before decay remains legible in the visible child distribution after the handover.</text>
<text x="70" y="904" class="sub">Post-hoc resolution check: failed 520 G point returned 7.060 MHz at 32 ns; independent expectation = 7.048 MHz.</text>
<text x="70" y="945" class="tiny">Source: ISIS EMU open data, DOI {t370.SOURCE_DOI}. The independent gold line is not used to fit the ARA cadence.</text></svg>'''
    FIGURE.write_text(svg, encoding="utf-8")


def make_report(frame: pd.DataFrame, result: dict) -> None:
    rows = "\n".join(
        f"| {r.run} | {r.field_gauss:.0f} | {r.recovered_frequency_mhz:.3f} | {r.expected_frequency_mhz:.3f} | {100*r.frequency_relative_error:.2f}% | {100*r.holdout_improvement_vs_no_phase:+.2f}% | {r.holdout_correlation:.3f} | {'PASS' if r.resolved_parent_phase_pass else 'FAIL'} |"
        for r in frame.itertuples()
    )
    text = f"""# T370B — Muon parent-phase lineage across an in-band field ladder

## Result

**{result['status'].replace('_', ' ')}** — {result['resolved_parent_phase_pass_count']} of 14 runs passed the frozen resolved-parent gate (required: 10).

The ARA circle was learned only from early raw detector counts. Its recovered
cadence then tracked the independently controlled field with Spearman
`{result['field_frequency_spearman']:.4f}` and a zero-intercept slope only
`{100*result['slope_relative_error']:.2f}%` from the independently known muon
rate. The duplicate 200 G acquisitions differed by
`{result['duplicate_200G_frequency_difference_mhz']:.3f} MHz`.

This registered verdict stays failed because the 520 G acquisition collapsed
at the frozen 64 ns analysis resolution and therefore broke the all-run rank
and slope gates. The other 13 runs had a near-perfect rank relation of
`{result['diagnostics_not_part_of_frozen_gate']['excluding_unresolved_520G']['field_frequency_spearman']:.4f}`
and their slope was
`{100*result['diagnostics_not_part_of_frozen_gate']['excluding_unresolved_520G']['slope_relative_error']:.3f}%`
from the independent value. A labelled post-hoc check at 32 ns recovered the
520 G cadence at `7.060 MHz` versus `7.048 MHz` expected and passed all four
holdout baselines plus the detector-rotation control. This diagnoses the frozen
failure as a resolution boundary, but it does not retroactively change the
registered verdict.

## Plain-language ARA reading

Before decay, the parent muon carries an opposing Phase A/Phase B directional
relation. We learned that circle from the first part of each acquisition and
then asked it to predict the later visible daughter pattern. When the cadence
of that fitted circle was placed beside the applied field only after fitting,
the two formed the registered parent lineage rather than an arbitrary slow
envelope.

The charged daughter therefore preserves readable information about the parent
relation through the handover. The unseen two-neutrino packet is the natural
opposite daughter branch in the stopped-parent frame, but this archive does not
measure it directly.

## Side-by-side translation

| ARA | Established muon description |
|---|---|
| Parent Phase A ↔ Phase B circle | Precessing polarized muon spin |
| Ridge crossing of the circle | Equal projection on the chosen detector cut |
| Visible child branch | Direction-dependent positron counts |
| Hidden complementary child | Combined two-neutrino energy/momentum packet |
| Parent cadence retained after handover | Positron angular distribution encodes the muon spin at decay |

## Frozen results

| Run | field G | ARA f MHz | expected f MHz | f error | holdout gain | corr. | resolved gate |
|---|---:|---:|---:|---:|---:|---:|---:|
{rows}

## Gates

{json.dumps(result['gates'], indent=2)}

## Boundary

This is a strong recovery/crosswalk of a known physical relation using the ARA
geometry on raw public data. It does not directly observe the neutrino branch,
demonstrate a new hidden field, or show that ARA predicts beyond the standard
precessing-spin description. A more decisive next rung would require a public
event-level polarized decay archive measuring the charged daughter energy and
direction together, or an ARA-only prediction frozen before a new field run.
"""
    REPORT.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
