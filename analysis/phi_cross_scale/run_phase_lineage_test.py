"""Frozen ARA same-phase octave-lineage calibration.

The inputs and evaluation rules are frozen in
FROZEN_PROTOCOL_PHASE_LINEAGE_2026-07-31.md.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
SEED = 20260731
N_SHUFFLES = 10_000

FAMILIES = {
    "Fibonacci": [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144],
    "Lucas": [1, 3, 4, 7, 11, 18, 29, 47, 76, 123],
    "F4": [1, 4, 5, 9, 14, 23, 37, 60, 97],
    "Double Fibonacci": [2, 4, 6, 10, 16, 26, 42, 68, 110],
    "F5": [1, 5, 6, 11, 17, 28, 45, 73],
    "F8": [1, 8, 9, 17, 26, 43, 69, 112],
}

PHI = (1 + math.sqrt(5)) / 2
DIRECT_LANDMARKS = {
    "sqrt(2)": math.sqrt(2),
    "1.5": 1.5,
    "phi": PHI,
    "2": 2.0,
    "e": math.e,
}
TWO_RUNG_LANDMARKS = {f"{name}^2": value**2 for name, value in DIRECT_LANDMARKS.items()}


def describe(errors: list[float]) -> dict[str, float | int]:
    return {
        "n": len(errors),
        "mean_absolute_error": statistics.fmean(errors),
        "median_absolute_error": statistics.median(errors),
        "max_absolute_error": max(errors),
    }


def median_direct_phi_error(values: list[int]) -> float:
    ratios = [values[i + 1] / values[i] for i in range(len(values) - 1)]
    return statistics.median(abs(ratio - PHI) for ratio in ratios)


def median_two_rung_phi2_error(values: list[int]) -> float:
    ratios = [values[i + 2] / values[i] for i in range(len(values) - 2)]
    return statistics.median(abs(ratio - PHI**2) for ratio in ratios)


adjacent_rows: list[dict[str, object]] = []
two_rung_rows: list[dict[str, object]] = []
triple_rows: list[dict[str, object]] = []

for family, values in FAMILIES.items():
    for i in range(len(values) - 1):
        child, parent = values[i], values[i + 1]
        adjacent_rows.append(
            {
                "family": family,
                "from_index": i,
                "to_index": i + 1,
                "child": child,
                "parent": parent,
                "ratio": parent / child,
                "abs_error_phi": abs(parent / child - PHI),
            }
        )

    for i in range(len(values) - 2):
        child, grandparent = values[i], values[i + 2]
        phase = "A" if i % 2 == 0 else "B"
        two_rung_rows.append(
            {
                "family": family,
                "phase": phase,
                "from_index": i,
                "to_index": i + 2,
                "child": child,
                "grandparent": grandparent,
                "ratio": grandparent / child,
                "abs_error_phi_squared": abs(grandparent / child - PHI**2),
            }
        )

        x0, x1, x2 = values[i : i + 3]
        triple_rows.append(
            {
                "family": family,
                "start_index": i,
                "x0": x0,
                "x1": x1,
                "x2": x2,
                "closure_residual": x2 - x1 - x0,
                "normalized_closure_residual": (x2 - x1 - x0) / x2,
            }
        )


direct_metrics = {
    name: describe([abs(float(row["ratio"]) - value) for row in adjacent_rows])
    for name, value in DIRECT_LANDMARKS.items()
}
two_rung_metrics = {
    name: describe([abs(float(row["ratio"]) - value) for row in two_rung_rows])
    for name, value in TWO_RUNG_LANDMARKS.items()
}
phase_metrics = {
    phase: describe(
        [
            float(row["abs_error_phi_squared"])
            for row in two_rung_rows
            if row["phase"] == phase
        ]
    )
    for phase in ("A", "B")
}

family_metrics: dict[str, dict[str, object]] = {}
for family in FAMILIES:
    family_adjacent = [row for row in adjacent_rows if row["family"] == family]
    family_two = [row for row in two_rung_rows if row["family"] == family]
    family_metrics[family] = {
        "direct_phi": describe([float(row["abs_error_phi"]) for row in family_adjacent]),
        "two_rung_phi_squared": describe(
            [float(row["abs_error_phi_squared"]) for row in family_two]
        ),
        "last_direct_ratio": float(family_adjacent[-1]["ratio"]),
        "last_two_rung_ratio": float(family_two[-1]["ratio"]),
    }


# Fixed-seed order-destruction control. Each shuffle preserves the values in every
# family but destroys their scale order.
rng = random.Random(SEED)
shuffle_direct: list[float] = []
shuffle_two: list[float] = []
for _ in range(N_SHUFFLES):
    shuffled_direct_errors: list[float] = []
    shuffled_two_errors: list[float] = []
    for values in FAMILIES.values():
        permuted = list(values)
        rng.shuffle(permuted)
        shuffled_direct_errors.extend(
            abs(permuted[i + 1] / permuted[i] - PHI)
            for i in range(len(permuted) - 1)
        )
        shuffled_two_errors.extend(
            abs(permuted[i + 2] / permuted[i] - PHI**2)
            for i in range(len(permuted) - 2)
        )
    shuffle_direct.append(statistics.median(shuffled_direct_errors))
    shuffle_two.append(statistics.median(shuffled_two_errors))

ordered_direct_median = float(direct_metrics["phi"]["median_absolute_error"])
ordered_two_median = float(two_rung_metrics["phi^2"]["median_absolute_error"])
shuffle_summary = {
    "seed": SEED,
    "n_shuffles": N_SHUFFLES,
    "ordered_direct_median_absolute_error": ordered_direct_median,
    "shuffle_direct_median_of_medians": statistics.median(shuffle_direct),
    "direct_empirical_p": (sum(x <= ordered_direct_median for x in shuffle_direct) + 1)
    / (N_SHUFFLES + 1),
    "ordered_two_rung_median_absolute_error": ordered_two_median,
    "shuffle_two_rung_median_of_medians": statistics.median(shuffle_two),
    "two_rung_empirical_p": (sum(x <= ordered_two_median for x in shuffle_two) + 1)
    / (N_SHUFFLES + 1),
}

results = {
    "status": "structural calibration; not independent discovery",
    "source": {
        "paper": "Swinton et al. (2016), Novel Fibonacci and non-Fibonacci structure in the sunflower",
        "doi": "10.1098/rsos.160091",
        "dataset_doi": "10.5061/dryad.f9k77",
    },
    "constants": {"phi": PHI, "phi_squared": PHI**2},
    "counts": {
        "families": len(FAMILIES),
        "adjacent_rung_ratios": len(adjacent_rows),
        "same_phase_two_rung_ratios": len(two_rung_rows),
        "recurrence_triples": len(triple_rows),
    },
    "direct_landmark_metrics": direct_metrics,
    "two_rung_landmark_metrics": two_rung_metrics,
    "phase_metrics_against_phi_squared": phase_metrics,
    "family_metrics": family_metrics,
    "recurrence": {
        "nonzero_residual_count": sum(
            int(row["closure_residual"] != 0) for row in triple_rows
        ),
        "max_absolute_normalized_residual": max(
            abs(float(row["normalized_closure_residual"])) for row in triple_rows
        ),
        "note": "Zero is entailed by selection of published Fibonacci-type families.",
    },
    "shuffle_control": shuffle_summary,
    "phase_label_swap_invariant": True,
}

(OUT_DIR / "phase_lineage_results.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)

for filename, rows in (
    ("phase_lineage_adjacent_ratios.csv", adjacent_rows),
    ("phase_lineage_two_rung_ratios.csv", two_rung_rows),
    ("phase_lineage_recurrence_triples.csv", triple_rows),
):
    with (OUT_DIR / filename).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def svg_line_chart() -> str:
    """Dependency-free, reviewable SVG of the frozen test."""

    width, height = 1400, 900
    panels = {
        "direct": (70, 100, 590, 300),
        "same": (740, 100, 590, 300),
        "rivals": (70, 510, 590, 290),
        "shuffle": (740, 510, 590, 290),
    }
    colors = {
        "Fibonacci": "#3366cc",
        "Lucas": "#dc3912",
        "F4": "#ff9900",
        "Double Fibonacci": "#109618",
        "F5": "#990099",
        "F8": "#0099c6",
    }

    def sx_log(value: float, x: float, w: float, lo: float = 1, hi: float = 144) -> float:
        return x + (math.log(value) - math.log(lo)) / (math.log(hi) - math.log(lo)) * w

    def sy(value: float, y: float, h: float, lo: float, hi: float) -> float:
        return y + h - (value - lo) / (hi - lo) * h

    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        "<style>"
        ".title{font:700 25px system-ui;fill:#172033}"
        ".subtitle{font:15px system-ui;fill:#5b6575}"
        ".panel{fill:#fbfcfe;stroke:#c8d0dc;stroke-width:1.5}"
        ".pt{stroke:white;stroke-width:1}"
        ".axis{stroke:#6b7280;stroke-width:1}"
        ".grid{stroke:#e2e8f0;stroke-width:1}"
        ".label{font:13px system-ui;fill:#344054}"
        ".small{font:11px system-ui;fill:#566070}"
        ".paneltitle{font:700 17px system-ui;fill:#172033}"
        "</style>",
        '<rect width="1400" height="900" fill="#f4f7fb"/>',
        '<text x="70" y="48" class="title">ARA same-phase octave lineage</text>',
        '<text x="70" y="75" class="subtitle">Sunflower Fibonacci-type calibration · child → parent → grandparent means ARA scale</text>',
    ]

    for x, y, w, h in panels.values():
        chunks.append(f'<rect class="panel" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>')

    # Direct adjacent-rung panel.
    x, y, w, h = panels["direct"]
    px, py, pw, ph = x + 58, y + 48, w - 85, h - 85
    chunks.append(f'<text x="{x+20}" y="{y+28}" class="paneltitle">Adjacent octave relation → φ</text>')
    for tick in (1.0, 1.5, 2.0, 3.0, 5.0):
        yy = sy(tick, py, ph, 0.8, 5.2)
        chunks.append(f'<line class="grid" x1="{px}" y1="{yy:.1f}" x2="{px+pw}" y2="{yy:.1f}"/>')
        chunks.append(f'<text class="small" x="{px-9}" y="{yy+4:.1f}" text-anchor="end">{tick:g}</text>')
    phi_y = sy(PHI, py, ph, 0.8, 5.2)
    chunks.append(f'<line x1="{px}" y1="{phi_y:.1f}" x2="{px+pw}" y2="{phi_y:.1f}" stroke="#111827" stroke-width="2"/>')
    chunks.append(f'<text class="small" x="{px+pw-4}" y="{phi_y-6:.1f}" text-anchor="end">φ = {PHI:.3f}</text>')
    for family, color in colors.items():
        rows = [row for row in adjacent_rows if row["family"] == family]
        points = " ".join(
            f'{sx_log(float(row["child"]), px, pw):.1f},{sy(float(row["ratio"]), py, ph, 0.8, 5.2):.1f}'
            for row in rows
        )
        chunks.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.8"/>')
        for row in rows:
            cx = sx_log(float(row["child"]), px, pw)
            cy = sy(float(row["ratio"]), py, ph, 0.8, 5.2)
            chunks.append(f'<circle class="pt" cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{color}"/>')
    chunks.append(f'<text class="label" x="{px+pw/2}" y="{y+h-16}" text-anchor="middle">lower scale (log axis)</text>')

    # Same-phase two-rung panel.
    x, y, w, h = panels["same"]
    px, py, pw, ph = x + 58, y + 48, w - 85, h - 85
    chunks.append(f'<text x="{x+20}" y="{y+28}" class="paneltitle">A→A and B→B two-rung relation → φ²</text>')
    for tick in (2, 3, 4, 6, 9):
        yy = sy(tick, py, ph, 1.5, 9.5)
        chunks.append(f'<line class="grid" x1="{px}" y1="{yy:.1f}" x2="{px+pw}" y2="{yy:.1f}"/>')
        chunks.append(f'<text class="small" x="{px-9}" y="{yy+4:.1f}" text-anchor="end">{tick:g}</text>')
    phi2_y = sy(PHI**2, py, ph, 1.5, 9.5)
    chunks.append(f'<line x1="{px}" y1="{phi2_y:.1f}" x2="{px+pw}" y2="{phi2_y:.1f}" stroke="#111827" stroke-width="2"/>')
    chunks.append(f'<text class="small" x="{px+pw-4}" y="{phi2_y-6:.1f}" text-anchor="end">φ² = {PHI**2:.3f}</text>')
    for row in two_rung_rows:
        cx = sx_log(float(row["child"]), px, pw)
        cy = sy(float(row["ratio"]), py, ph, 1.5, 9.5)
        color = "#2962a3" if row["phase"] == "A" else "#c26924"
        shape = (
            f'<circle class="pt" cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{color}"/>'
            if row["phase"] == "A"
            else f'<rect class="pt" x="{cx-4:.1f}" y="{cy-4:.1f}" width="8" height="8" fill="{color}"/>'
        )
        chunks.append(shape)
    chunks.append(f'<text class="small" x="{px+12}" y="{py+15}" fill="#2962a3">● Phase A</text>')
    chunks.append(f'<text class="small" x="{px+92}" y="{py+15}" fill="#c26924">■ Phase B</text>')
    chunks.append(f'<text class="label" x="{px+pw/2}" y="{y+h-16}" text-anchor="middle">same-phase child scale (log axis)</text>')

    # Rival bars.
    x, y, w, h = panels["rivals"]
    chunks.append(f'<text x="{x+20}" y="{y+28}" class="paneltitle">Frozen direct-ratio rivals</text>')
    names = list(DIRECT_LANDMARKS)
    vals = [float(direct_metrics[name]["median_absolute_error"]) for name in names]
    max_val = max(vals) * 1.12
    bx0, by0, bw, bh = x + 60, y + 55, w - 95, h - 100
    step = bw / len(names)
    for i, (name, value) in enumerate(zip(names, vals)):
        bar_h = value / max_val * bh
        fill = "#2e8b57" if name == "phi" else "#9ca3af"
        chunks.append(f'<rect x="{bx0+i*step+14:.1f}" y="{by0+bh-bar_h:.1f}" width="{step-28:.1f}" height="{bar_h:.1f}" fill="{fill}"/>')
        chunks.append(f'<text class="small" x="{bx0+(i+.5)*step:.1f}" y="{by0+bh+18}" text-anchor="middle">{name}</text>')
        chunks.append(f'<text class="small" x="{bx0+(i+.5)*step:.1f}" y="{by0+bh-bar_h-7:.1f}" text-anchor="middle">{value:.3f}</text>')
    chunks.append(f'<text class="small" x="{x+20}" y="{y+h-18}">Median absolute error; lower is better.</text>')

    # Shuffle control.
    x, y, w, h = panels["shuffle"]
    chunks.append(f'<text x="{x+20}" y="{y+28}" class="paneltitle">Order-destruction control</text>')
    ordered = ordered_direct_median
    shuffled = statistics.median(shuffle_direct)
    vals = [ordered, shuffled]
    labels = ["ordered scales", "10,000 shuffled orders"]
    max_val = max(vals) * 1.15
    bx0, by0, bw, bh = x + 80, y + 60, w - 140, h - 115
    for i, (label, value) in enumerate(zip(labels, vals)):
        bar_w = bw / 3
        left = bx0 + (i * 1.55 + 0.25) * bar_w
        bar_h = value / max_val * bh
        fill = "#2e8b57" if i == 0 else "#a8b5c6"
        chunks.append(f'<rect x="{left:.1f}" y="{by0+bh-bar_h:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{fill}"/>')
        chunks.append(f'<text class="small" x="{left+bar_w/2:.1f}" y="{by0+bh+18}" text-anchor="middle">{label}</text>')
        chunks.append(f'<text class="label" x="{left+bar_w/2:.1f}" y="{by0+bh-bar_h-8:.1f}" text-anchor="middle">{value:.4f}</text>')
    chunks.append(f'<text class="small" x="{x+20}" y="{y+h-18}">Empirical p = {shuffle_summary["direct_empirical_p"]:.5f}; recurrence selection makes this a calibration.</text>')

    # Family legend.
    legend_x = 78
    for i, (family, color) in enumerate(colors.items()):
        xx = legend_x + i * 205
        chunks.append(f'<circle cx="{xx}" cy="855" r="5" fill="{color}"/>')
        chunks.append(f'<text class="small" x="{xx+10}" y="859">{family}</text>')

    chunks.append("</svg>")
    return "\n".join(chunks)


svg = svg_line_chart()
(OUT_DIR / "phase_lineage_test.svg").write_text(svg, encoding="utf-8")
(OUT_DIR / "phase_lineage_test.html").write_text(
    """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARA same-phase octave lineage</title>
<style>
html,body{margin:0;background:#101318;color:#e7edf6;font-family:system-ui,sans-serif}
main{min-height:100vh;display:grid;place-items:center;padding:20px}
svg{width:min(96vw,1400px);height:auto;border-radius:14px;box-shadow:0 18px 60px #0008}
</style>
</head>
<body><main>"""
    + svg
    + """</main></body></html>""",
    encoding="utf-8",
)

print(json.dumps(results, indent=2))
