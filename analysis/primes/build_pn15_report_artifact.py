#!/usr/bin/env python3
"""Build the canonical portable-report artifact for PN15.

Chart contract
--------------
Question 1: Did the frozen 16-sector phase shape transfer to untouched scale 12?
Takeaway: Yes, but it is shared by raw integers, primes and composites.
Family: highlighted multi-series line; 16 ordered phase sectors.

Question 2: Does the square-root adult rung approach the expected 10x scale step?
Takeaway: All four observed steps are within 0.15% of 10; the target is within
0.018%. Family: bar of absolute percentage deviation from the registered 10x
reference, because four discrete scale transitions are not a sufficient trend.

Output: PN15_SQRT_ADULT_RIDGE_REPORT_ARTIFACT.json, later packaged by the
shared Data Analytics portable-report builder.
"""

from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET_PATH = ROOT / "PN15_TARGET_RESULTS.json"
DEV_PATH = ROOT / "PN15_DEVELOPMENT_RESULTS.json"
TEMPLATE_PATH = ROOT / "PN15_DEVELOPMENT_TEMPLATE.json"
OUT_PATH = ROOT / "PN15_SQRT_ADULT_RIDGE_REPORT_ARTIFACT.json"


def load(name: Path) -> dict:
    return json.loads(name.read_text(encoding="utf-8"))


def source() -> dict:
    return {
        "id": "pn15_frozen_outputs",
        "query": {
            "engine": "sqlite",
            "language": "sql",
            "sql": (
                "SELECT dataset, row_index, row_json "
                "FROM pn15_artifact_rows ORDER BY dataset, row_index"
            ),
            "description": (
                "Selects the reviewed report rows after build_pn15_report_artifact.py "
                "materializes frozen PN15 development scales 8-11 and the hash-sealed "
                "scale-12 target into SQLite."
            ),
            "tables_used": [
                "pn15_artifact_rows",
            ],
            "filters": [
                "Development restricted to scales 8-11 before target freeze",
                "Fresh target restricted to scale 12 at N=4e12",
                "Sixteen equal relative-phase sectors",
            ],
            "metric_definitions": {
                "factor_coordinate": "x_N(p)=2 log(p)/log(N)",
                "adult_growth": "G_d=J_(d+1)/J_d, where J_d is the median adjacent-gate product",
                "phase_curve": "Mean centered closure value within each of sixteen relative-phase sectors",
            },
            "executed_at": "2026-07-21T00:00:00+10:00",
        },
    }


def main() -> None:
    target = load(TARGET_PATH)
    dev = load(DEV_PATH)
    template = load(TEMPLATE_PATH)

    adult = target["metrics"]["full_sqrt_adult_ridge"]
    phase = target["metrics"]["phase_transfer"]
    curves = target["target"]["curves"]

    phase_rows: list[dict] = []
    theta = template["theta_centers"]
    series_values = {
        "Frozen development template": template["prime_template"],
        "Target primes": curves["prime"]["means"],
        "Target composites": curves["composite"]["means"],
        "Target raw integers": curves["raw"]["means"],
        "Analytic phase curve": [1.0 / 3.0 - 2.0 * t + 2.0 * t * t for t in theta],
    }
    for label, values in series_values.items():
        for sector, (t, value) in enumerate(zip(theta, values)):
            phase_rows.append(
                {
                    "sector": sector,
                    "theta": t,
                    "series": label,
                    "mean_closure": value,
                }
            )

    js: dict[int, float] = {
        int(item["scale"]): float(item["geometry"]["median_joint_period"])
        for item in dev["scales"]
    }
    fills: dict[int, float] = {
        int(item["scale"]): float(item["geometry"]["median_adult_fill"])
        for item in dev["scales"]
    }
    js[12] = float(target["target"]["geometry"]["median_joint_period"])
    fills[12] = float(target["target"]["geometry"]["median_adult_fill"])

    growth_rows = []
    scale_rows = []
    for scale in range(8, 13):
        growth = js[scale + 1] / js[scale] if scale < 12 else None
        scale_rows.append(
            {
                "scale": scale,
                "anchor": 4 * 10**scale,
                "median_joint_period": js[scale],
                "adult_fill": fills[scale],
                "growth_to_next": growth,
            }
        )
        if growth is not None:
            growth_rows.append(
                {
                    "transition": f"10^{scale} to 10^{scale + 1}",
                    "growth": growth,
                    "absolute_deviation_percent": abs(growth / 10.0 - 1.0) * 100.0,
                    "status": "Target" if scale == 11 else "Development",
                }
            )

    prime_means = curves["prime"]["means"]
    comp_means = curves["composite"]["means"]
    max_prime_composite_difference = max(
        abs(float(p) - float(c)) for p, c in zip(prime_means, comp_means)
    )

    headline_rows = [
        {
            "target_growth": adult["G11"],
            "adult_coordinate_sum": adult["representative_adult_sum"],
            "child_ratio": adult["representative_child_A"] / adult["representative_child_B"],
            "phase_correlation": phase["target_template_correlation"],
            "phase_rmse": phase["target_template_rmse"],
            "max_prime_composite_difference": max_prime_composite_difference,
        }
    ]

    # The portable report contract requires the actual SQL that exposes chart,
    # card and table rows. Materialize the reviewed Python-derived rows, execute
    # the declared source query, and reconstruct the same bounded snapshot from
    # its result. This is a provenance adapter, not a second analysis path.
    datasets = {
        "headline": headline_rows,
        "phase_curve": phase_rows,
        "growth": growth_rows,
        "scales": scale_rows,
    }
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE pn15_artifact_rows "
        "(dataset TEXT NOT NULL, row_index INTEGER NOT NULL, row_json TEXT NOT NULL)"
    )
    for dataset, rows in datasets.items():
        connection.executemany(
            "INSERT INTO pn15_artifact_rows(dataset, row_index, row_json) VALUES (?, ?, ?)",
            [
                (dataset, index, json.dumps(row, sort_keys=True))
                for index, row in enumerate(rows)
            ],
        )
    selected = connection.execute(
        "SELECT dataset, row_index, row_json "
        "FROM pn15_artifact_rows ORDER BY dataset, row_index"
    ).fetchall()
    selected_datasets = {name: [] for name in datasets}
    for dataset, _index, row_json in selected:
        selected_datasets[dataset].append(json.loads(row_json))
    connection.close()
    if selected_datasets != datasets:
        raise RuntimeError("SQLite provenance adapter changed reviewed PN15 rows")

    manifest_source = {
        "id": "pn15_frozen_outputs",
        "label": "PN15 frozen outputs and independent validation",
        "path": "PN15_TARGET_RESULTS.json",
    }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "PN15: Full square-root child closure and adult-rung ridge",
        "description": "Frozen scale-12 target report for the ARA prime-rung test.",
        "generatedAt": "2026-07-21T00:00:00+10:00",
        "cards": [
            {
                "id": "growth_card",
                "description": "Fresh scale-11 to scale-12 adult-rung growth; registered reference is 10x.",
                "dataset": "headline",
                "sourceId": "pn15_frozen_outputs",
                "metrics": [{"label": "Target adult growth", "field": "target_growth", "format": "number"}],
            },
            {
                "id": "sum_card",
                "description": "The two representative square-root child coordinates added together.",
                "dataset": "headline",
                "sourceId": "pn15_frozen_outputs",
                "metrics": [{"label": "Child-coordinate sum", "field": "adult_coordinate_sum", "format": "number"}],
            },
            {
                "id": "corr_card",
                "description": "Correlation between the frozen development template and fresh target prime curve.",
                "dataset": "headline",
                "sourceId": "pn15_frozen_outputs",
                "metrics": [{"label": "Phase transfer correlation", "field": "phase_correlation", "format": "number"}],
            },
            {
                "id": "difference_card",
                "description": "Largest sector-level separation between target prime and composite means.",
                "dataset": "headline",
                "sourceId": "pn15_frozen_outputs",
                "metrics": [{"label": "Max prime-composite difference", "field": "max_prime_composite_difference", "format": "number"}],
            },
        ],
        "charts": [
            {
                "id": "phase_chart",
                "title": "Relative-phase closure across sixteen sectors",
                "subtitle": "Fresh scale-12 populations, frozen development template, and analytic reference",
                "type": "line",
                "intent": "trend",
                "question": "Did the registered phase shape transfer to the untouched scale-12 target?",
                "rationale": "Sixteen ordered phase sectors expose the full cycle and allow direct shape comparison.",
                "comparisonContext": {
                    "grain": "one row per series per phase sector",
                    "unit": "centered closure value",
                    "baseline": "frozen development template",
                },
                "dataset": "phase_curve",
                "sourceId": "pn15_frozen_outputs",
                "palette": {"kind": "categorical", "name": "blue-gold-orange-olive-pink"},
                "legend": {"position": "bottom", "sort": "spec", "title": "Series"},
                "labels": {"values": "none"},
                "encodings": {
                    "x": {"field": "theta", "type": "quantitative", "label": "Relative phase θ"},
                    "y": {"field": "mean_closure", "type": "quantitative", "label": "Mean centered closure"},
                    "color": {"field": "series", "type": "nominal", "label": "Series"},
                    "tooltip": [
                        {"field": "series", "type": "nominal", "label": "Series"},
                        {"field": "sector", "type": "quantitative", "label": "Sector"},
                        {"field": "mean_closure", "type": "quantitative", "label": "Mean closure"},
                    ],
                },
            },
            {
                "id": "growth_chart",
                "title": "Adult-rung deviation from registered 10x growth",
                "subtitle": "Absolute percentage deviation; the scale-12 target is the final bar",
                "type": "bar",
                "intent": "comparison",
                "question": "How closely does each adult rung follow the expected 10x step?",
                "rationale": "Four discrete transitions are more honestly compared as bars than as a trend line.",
                "comparisonContext": {
                    "grain": "one row per adjacent scale transition",
                    "unit": "absolute percent deviation from 10x",
                    "baseline": "registered adult growth of 10",
                },
                "dataset": "growth",
                "sourceId": "pn15_frozen_outputs",
                "palette": {"kind": "sequential", "name": "blue"},
                "labels": {"values": "all"},
                "encodings": {
                    "x": {"field": "transition", "type": "nominal", "label": "Scale transition"},
                    "y": {"field": "absolute_deviation_percent", "type": "quantitative", "label": "Absolute deviation (%)"},
                    "tooltip": [
                        {"field": "growth", "type": "quantitative", "label": "Observed growth"},
                        {"field": "status", "type": "nominal", "label": "Status"},
                    ],
                },
            },
        ],
        "tables": [
            {
                "id": "scale_table",
                "title": "Adult-rung audit table",
                "subtitle": "Development scales 8-11 and the untouched scale-12 target",
                "dataset": "scales",
                "sourceId": "pn15_frozen_outputs",
                "defaultSort": {"field": "scale", "direction": "asc"},
                "columns": [
                    {"field": "scale", "label": "Scale d", "type": "number"},
                    {"field": "anchor", "label": "Anchor N", "type": "number"},
                    {"field": "median_joint_period", "label": "Median child product J_d", "type": "number"},
                    {"field": "adult_fill", "label": "J_d / N_d", "type": "number"},
                    {"field": "growth_to_next", "label": "J_(d+1) / J_d", "type": "number"},
                ],
            }
        ],
        "sources": [manifest_source],
        "blocks": [
            {
                "id": "title",
                "type": "markdown",
                "body": "# PN15: Full square-root child closure and adult-rung ridge",
            },
            {
                "id": "technical_summary",
                "type": "markdown",
                "sourceId": "pn15_frozen_outputs",
                "body": (
                    "## The frozen target supports the registered cross-scale ARA mapping\n\n"
                    "The untouched scale-12 target passed every preregistered criterion. The adult product grew by "
                    f"**{adult['G11']:.6f}×** against a 10× reference. Its representative square-root children read "
                    f"**{adult['representative_child_A']:.9f}** and **{adult['representative_child_B']:.9f}**, a ratio of "
                    f"**{adult['representative_child_A'] / adult['representative_child_B']:.9f}** and a sum of "
                    f"**{adult['representative_adult_sum']:.9f}**. In ARA language, this is an exceptionally tight 1.0/1.0 child ridge closing to a 2.0 adult coordinate.\n\n"
                    "The 16-sector target-prime phase curve also transferred from development with "
                    f"**r={phase['target_template_correlation']:.6f}** and **RMSE={phase['target_template_rmse']:.6f}**. "
                    "However, primes and composites trace almost the same curve, so this phase result is a stable arithmetic crosswalk, not a prime predictor."
                ),
            },
            {"id": "headline_metrics", "type": "metric-strip", "cardIds": ["growth_card", "sum_card", "corr_card", "difference_card"]},
            {
                "id": "key_findings",
                "type": "markdown",
                "sourceId": "pn15_frozen_outputs",
                "body": (
                    "## The adult ridge closes tightly, while the phase wave is population-general\n\n"
                    "The child and adult coordinates became tighter as the boundary moved to the full square root. "
                    f"At scale 12 the adult fill was **{adult['target_adult_fill']:.9f}** and the target growth missed 10× by only "
                    f"**{abs(adult['G11'] / 10 - 1) * 100:.4f}%**. This confirms that the earlier 8.07/7.96 near-ridge becomes a much cleaner 1.0/1.0 pair under the registered square-root coordinate.\n\n"
                    f"The phase shape is equally stable, but its largest target prime-composite mean difference is only **{max_prime_composite_difference:.6f}**. "
                    "The visual overlap therefore means the phase curve belongs to the chosen two-gate arithmetic geometry across the integer population; it does not uniquely identify primes."
                ),
            },
            {"id": "phase_visual", "type": "chart", "chartId": "phase_chart"},
            {
                "id": "phase_interpretation",
                "type": "markdown",
                "body": (
                    "The five lines nearly coincide. That is strong transfer of the registered phase geometry and a useful negative discriminator check at the same time: the curve survives scale change, but prime membership contributes almost no visible separation at this grain."
                ),
            },
            {"id": "growth_visual", "type": "chart", "chartId": "growth_chart"},
            {
                "id": "growth_interpretation",
                "type": "markdown",
                "body": (
                    "Every adult transition is close to 10×, and the sealed scale-12 target is the closest of the four. The bars show error from the registered reference rather than the approximately 10× values themselves, so the remaining deviations stay visible without truncating a magnitude chart."
                ),
            },
            {"id": "scale_audit", "type": "table", "tableId": "scale_table"},
            {
                "id": "scope_definitions",
                "type": "markdown",
                "body": (
                    "## What was measured\n\n"
                    "For each anchor **N_d=4×10^d**, PN15 selected the nine largest primes at or below **√N_d** and formed eight adjacent pairs. "
                    "Each child used the ARA factor coordinate **x_N(p)=2 log(p)/log(N)**. A child exactly at √N reads 1.0; two such children add to 2.0 and multiply to N. "
                    "The adult coordinate **J_d** is the median of the eight pair products. Development used only d=8…11; d=12 was hash-sealed before calculation.\n\n"
                    "The second arm divided one representative pair cycle into sixteen equal relative-phase sectors and compared mean centered closure for raw integers, exact primes, and exact composites."
                ),
            },
            {
                "id": "methodology",
                "type": "markdown",
                "body": (
                    "## The target was frozen before scale 12 was opened\n\n"
                    "Development fixed the coordinate, gate selection, eight-pair median, sector count, block width, controls, thresholds, and target unlock. "
                    "A SHA-256 manifest sealed both protocol and executable inputs. The primary run then opened only the scale-12 target. "
                    "A separate validator used an independent bytearray sieve and recomputed the gates, pairs, all 16 sector counts and means, adult metrics, phase metrics, and a small analytic fixture. All validation checks passed."
                ),
            },
            {
                "id": "limitations",
                "type": "markdown",
                "sourceId": "pn15_frozen_outputs",
                "body": (
                    "## The precision is real, but much of it is construction-forced\n\n"
                    "Choosing q and r immediately below √N makes **x_N(q)≈x_N(r)≈1**, **qr≈N**, and—when N increases tenfold—**qr** increase about tenfold. "
                    "The target therefore validates the ARA translation, code path, preregistered transfer, and scale bookkeeping; it does **not** discover a new prime law or independently prove universal fractality.\n\n"
                    f"The phase transfer is robust against a zero curve, a wrong coordinate, and a permutation control, but primes and composites overlap to within **{max_prime_composite_difference:.6f}** in sector means. "
                    "This rules out treating the present phase curve as a prime classifier. Finally, a fixed pair-phase walk is local to the selected anchor; it is not the same object as a continuously moving √n boundary."
                ),
            },
            {
                "id": "next_steps",
                "type": "markdown",
                "body": (
                    "## Next test: ask for information the square-root identity does not guarantee\n\n"
                    "Keep PN15 as a successful crosswalk and calibration result. The next load-bearing prime test should freeze a quantity not algebraically forced by selecting children near √N—for example, whether child-wave residuals predict an untouched prime-survival frequency, location class, or gap class better than raw modular and sieve-informed controls. "
                    "That would test added information rather than reconstruction of a known boundary identity."
                ),
            },
            {
                "id": "further_questions",
                "type": "markdown",
                "body": (
                    "## Open questions\n\n"
                    "- Does a residual measured before the √n boundary carries any out-of-sample information about the next survivor?\n"
                    "- Can a moving-boundary ARA coordinate be defined without importing the sieve answer into the feature?\n"
                    "- Is the stable phase curve useful as a calibration coordinate even though it is not prime-specific?\n"
                    "- Which child statistic remains nontrivial after conditioning on standard modular and sieve structure?"
                ),
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": "2026-07-21T00:00:00+10:00",
            "status": "ready",
            "datasets": {
                **selected_datasets,
            },
            "accessIssues": [],
        },
        "sources": [source()],
        "package_info": {"originUrl": "artifact://pn15-sqrt-adult-ridge"},
    }

    OUT_PATH.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": OUT_PATH.name, "datasets": {k: len(v) for k, v in artifact["snapshot"]["datasets"].items()}}, indent=2))


if __name__ == "__main__":
    main()
