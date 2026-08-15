#!/usr/bin/env python3
"""Execute frozen T383 7.5-cycle / parent-pole comparison."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T382_ral_silver_detector_share" / "T382_DETECTOR_SHARE_RESULTS.json"
OUT = HERE / "T383_7p5_child_before_parent_pole"
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "T383_RESULTS.json"
TABLE = OUT / "T383_FIELD_PHASES.csv"
FIGURE = OUT / "T383_7P5_PARENT_POLE.svg"
REPORT = OUT / "T383_7P5_PARENT_POLE.html"

FIELDS = {20: "calibration", 25: "calibration", 63: "discovery", 160: "comparison", 400: "comparison",
          1000: "diagnostic", 2000: "diagnostic", 4000: "diagnostic"}
SEED = 383
N_RANDOM = 100000


def circular_distance_cycles(a: float, b: float) -> float:
    return abs(float(np.angle(np.exp(2j * np.pi * (a - b))))) / (2.0 * np.pi)


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    tau = float(source["parent"]["tau_us"])
    gamma = float(source["child"]["gamma_mhz_per_g"])
    phi_cycles = float(source["child"]["phi0_rad"]) / (2.0 * np.pi)

    discovery_field = 63.0
    t_star = (7.5 - phi_cycles) / (gamma * discovery_field)
    x_parent_star = 2.0 * (1.0 - math.exp(-t_star / tau))

    rows = []
    for field, role in FIELDS.items():
        cycles = gamma * field * t_star + phi_cycles
        fraction = cycles % 1.0
        distance = circular_distance_cycles(fraction, 0.5)
        native_child = 1.0 - math.cos(2.0 * np.pi * fraction)
        reverse_fraction = (-gamma * field * t_star + phi_cycles) % 1.0
        rows.append({"field_g": field, "role": role, "time_us": t_star, "parent_ara": x_parent_star,
                     "accumulated_child_cycles": cycles, "fractional_child_phase": fraction,
                     "distance_to_half_cycle": distance, "native_child_ara": native_child,
                     "projected_child_ara": native_child / 2.0,
                     "pole_score": -math.cos(2.0 * np.pi * fraction),
                     "reverse_fractional_phase": reverse_fraction,
                     "reverse_pole_score": -math.cos(2.0 * np.pi * reverse_fraction)})
    frame = pd.DataFrame(rows)
    frame.to_csv(TABLE, index=False)
    comparison = frame[frame.role == "comparison"].copy()

    h1_each = bool(np.all(np.abs(comparison.accumulated_child_cycles.to_numpy() - 7.5) <= 0.25))
    h1_pass = h1_each
    h2_each = bool(np.all(comparison.distance_to_half_cycle.to_numpy() <= 0.125))
    mean_vector = np.mean(np.exp(2j * np.pi * comparison.fractional_child_phase.to_numpy()))
    mean_fraction = float((np.angle(mean_vector) / (2.0 * np.pi)) % 1.0)
    reference_distances = {str(reference): circular_distance_cycles(mean_fraction, reference)
                           for reference in (0.0, 0.25, 0.5, 0.75)}
    mean_closest_half = reference_distances["0.5"] == min(reference_distances.values())
    mean_pole = float(comparison.pole_score.mean())
    mean_reverse = float(comparison.reverse_pole_score.mean())

    rng = np.random.default_rng(SEED)
    random_origins = rng.uniform(0.0, 1.0, N_RANDOM)
    field_array = comparison.field_g.to_numpy(dtype=float)
    random_scores = np.mean(-np.cos(2.0 * np.pi * (gamma * field_array[None, :] * t_star + random_origins[:, None])), axis=1)
    random_975 = float(np.quantile(random_scores, 0.975))
    beats_random = mean_pole > random_975
    beats_reverse = mean_pole > mean_reverse
    h2_pass = bool(h2_each and mean_closest_half and mean_pole > 0 and beats_random and beats_reverse)

    result = {
        "test": "T383 7.5 child cycles before parent pole",
        "status": "BOTH_REJECTED" if not h1_pass and not h2_pass else "H1_SUPPORTED" if h1_pass and not h2_pass else "H2_SUPPORTED" if h2_pass and not h1_pass else "BOTH_SUPPORTED",
        "discovery": {"field_g": discovery_field, "t_star_us": t_star, "parent_ara": x_parent_star,
                      "parent_completion_fraction": x_parent_star / 2.0, "child_cycles": 7.5},
        "h1_literal_count_invariance": {"pass": h1_pass, "tolerance_cycles": 0.25,
                                        "comparison_counts": comparison[["field_g", "accumulated_child_cycles"]].to_dict("records")},
        "h2_half_cycle_pole_lock": {"pass": h2_pass, "each_within_one_eighth_cycle": h2_each,
                                    "mean_fractional_phase": mean_fraction, "mean_closest_to_half": mean_closest_half,
                                    "mean_pole_score": mean_pole, "random_phase_97_5": random_975,
                                    "mean_reverse_pole_score": mean_reverse, "beats_random": beats_random,
                                    "beats_reverse": beats_reverse, "reference_distances_cycles": reference_distances},
        "claim_boundary": "The T382 child failed qualification. T383 tests only the frozen candidate geometry and cannot establish neutrino timing.",
        "artifacts": {"field_table": str(TABLE), "figure": str(FIGURE), "report": str(REPORT)},
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_figure(result, frame)
    make_report(result, frame)
    print(json.dumps(result, indent=2))


def make_figure(result: dict, frame: pd.DataFrame):
    comparison = frame[frame.role == "comparison"]
    display = frame[frame.role != "diagnostic"].copy()
    max_cycles = math.ceil(float(display.accumulated_child_cycles.max()) / 10.0) * 10.0
    bars = []
    colours = {"calibration": "#98a5b5", "discovery": "#e29a32", "comparison": "#3d79bd", "diagnostic": "#b9c0ca"}
    for i, row in enumerate(display.itertuples()):
        x = 125 + i * 125
        bar_h = 330 * row.accumulated_child_cycles / max_cycles
        bars.append(f'<rect x="{x}" y="{540-bar_h:.2f}" width="92" height="{bar_h:.2f}" fill="{colours[row.role]}"/><text x="{x+46}" y="565" class="small" text-anchor="middle">{row.field_g:g} G</text><text x="{x+46}" y="{525-bar_h:.2f}" class="small" text-anchor="middle">{row.accumulated_child_cycles:.2f}</text>')
    y_ticks = []
    for value in range(0, int(max_cycles) + 1, 10):
        y = 540 - 330 * value / max_cycles
        y_ticks.append(f'<line x1="90" y1="{y:.2f}" x2="755" y2="{y:.2f}" stroke="#e1e5eb"/><text x="80" y="{y+5:.2f}" class="small" text-anchor="end">{value}</text>')
    circle_bits = []
    cx, cy, radius = 1170, 345, 175
    for row in frame.itertuples():
        if row.role not in {"discovery", "comparison"}:
            continue
        angle = 2.0 * np.pi * row.fractional_child_phase
        x, y = cx + radius * math.cos(angle), cy - radius * math.sin(angle)
        colour = colours[row.role]
        circle_bits.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" stroke="{colour}" stroke-width="4"/><circle cx="{x:.2f}" cy="{y:.2f}" r="10" fill="{colour}"/><text x="{x+12:.2f}" y="{y-8:.2f}" class="small">{row.field_g:g} G · f={row.fractional_child_phase:.3f}</text>')
    gate_rows = []
    for i, (label, passed) in enumerate([("H1 same 7.5 accumulated cycles", result["h1_literal_count_invariance"]["pass"]),
                                         ("H2 same half-cycle child pole", result["h2_half_cycle_pole_lock"]["pass"])]):
        y = 760 + i * 85
        colour = "#198754" if passed else "#b43636"
        gate_rows.append(f'<text x="895" y="{y}" class="body">{label}</text><text x="1450" y="{y}" class="body" text-anchor="end" fill="{colour}">{"PASS" if passed else "FAIL"}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="980" viewBox="0 0 1600 980"><rect width="100%" height="100%" fill="#f6f8fb"/><style>.title{{font:700 34px Arial;fill:#17202b}}.heading{{font:700 22px Arial;fill:#17202b}}.body{{font:18px Arial;fill:#26313d}}.small{{font:14px Arial;fill:#596575}}.panel{{fill:white;stroke:#d4dbe5;stroke-width:2}}</style>
<text x="60" y="58" class="title">T383 — does the child retain the 7.5 / half-cycle landmark?</text><text x="60" y="88" class="body">Common parent coordinate xP={result['discovery']['parent_ara']:.6f} ({100*result['discovery']['parent_completion_fraction']:.3f}% of pole 2)</text>
<rect x="55" y="120" width="730" height="500" rx="14" class="panel"/><text x="90" y="157" class="heading">Accumulated child cycles at the same parent coordinate</text>{''.join(y_ticks)}<line x1="90" y1="210" x2="90" y2="540" stroke="#536170"/><line x1="90" y1="540" x2="755" y2="540" stroke="#536170"/>{''.join(bars)}<line x1="90" y1="{540-330*7.5/max_cycles:.2f}" x2="755" y2="{540-330*7.5/max_cycles:.2f}" stroke="#e29a32" stroke-dasharray="7 6"/><text x="745" y="{530-330*7.5/max_cycles:.2f}" class="small" text-anchor="end">7.5 discovery level</text><text x="420" y="600" class="small" text-anchor="middle">field and role: grey calibration · orange discovery · blue comparison</text><text x="58" y="375" class="small" transform="rotate(-90 58 375)" text-anchor="middle">accumulated child cycles</text>
<rect x="815" y="120" width="730" height="500" rx="14" class="panel"/><text x="850" y="157" class="heading">Fractional phase after whole cycles coarse-grain away</text><circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#8491a1" stroke-width="2"/><line x1="{cx-radius}" y1="{cy}" x2="{cx+radius}" y2="{cy}" stroke="#dce2ea"/><line x1="{cx}" y1="{cy-radius}" x2="{cx}" y2="{cy+radius}" stroke="#dce2ea"/>{''.join(circle_bits)}<text x="{cx+radius+12}" y="{cy+5}" class="small">0 / 1</text><text x="{cx-radius-12}" y="{cy+5}" class="small" text-anchor="end">0.5 child pole</text>
<rect x="55" y="660" width="1490" height="255" rx="14" class="panel"/><text x="90" y="705" class="heading">Frozen verdicts</text>{''.join(gate_rows)}<text x="90" y="885" class="small">Discovery run is excluded from confirmation. T382 child qualification already failed, so this is a geometry-only test.</text></svg>'''
    FIGURE.write_text(svg, encoding="utf-8")


def make_report(result: dict, frame: pd.DataFrame):
    rows = "".join(f"<tr><td>{r.field_g:g}</td><td>{r.role}</td><td>{r.accumulated_child_cycles:.6f}</td><td>{r.fractional_child_phase:.6f}</td><td>{r.native_child_ara:.6f}</td><td>{r.distance_to_half_cycle:.6f}</td></tr>" for r in frame.itertuples())
    report = f'''<!doctype html><html><head><meta charset="utf-8"><title>T383 7.5 test</title><style>body{{font:16px/1.5 Arial;background:#f4f6fa;color:#17202b}}main{{max-width:1280px;margin:auto}}.card{{background:white;border:1px solid #d8dee8;border-radius:12px;padding:22px;margin:18px 0}}table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;border-bottom:1px solid #e1e5eb;text-align:left}}img{{width:100%}}</style></head><body><main><h1>T383 — 7.5 child cycles before parent pole</h1><div class="card"><h2>Answer first</h2><p><b>{result['status']}</b>. Literal 7.5-cycle invariance: <b>{'PASS' if result['h1_literal_count_invariance']['pass'] else 'FAIL'}</b>. Half-cycle pole lock: <b>{'PASS' if result['h2_half_cycle_pole_lock']['pass'] else 'FAIL'}</b>.</p><p>{result['claim_boundary']}</p></div><div class="card"><img src="T383_7P5_PARENT_POLE.svg"></div><div class="card"><h2>All fields at the common parent coordinate</h2><table><tr><th>G</th><th>role</th><th>accumulated cycles</th><th>fractional phase</th><th>native child ARA</th><th>distance to 0.5</th></tr>{rows}</table></div><div class="card"><h2>Reproduce</h2><p>Run <code>t383_test_7p5_parent_pole.py</code> from the repository root.</p></div></main></body></html>'''
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
