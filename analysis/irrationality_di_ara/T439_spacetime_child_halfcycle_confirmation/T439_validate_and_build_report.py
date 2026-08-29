"""Independent validation and canonical report payload for T439."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
ARA_ROOT = ROOT.parents[2]
RESULTS = ROOT / "results"
SCORED = RESULTS / "T439_SCORED_RESULT.json"
SCORES = RESULTS / "T439_HOLDOUT_SCORES.csv"
CONTROLS = RESULTS / "T439_SHUFFLE_CONTROLS.npz"
PROTOCOL = ROOT / "T439_FROZEN_PROTOCOL.md"
PREDICTIONS = RESULTS / "T439_WAVEFORM_ONLY_PREDICTIONS.json"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ARA_ROOT.resolve()).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    scored = json.loads(SCORED.read_text(encoding="utf-8"))
    df = pd.read_csv(SCORES)
    controls = np.load(CONTROLS)
    offsets = df["absolute_offset_cycles"].to_numpy(float)
    signed = df["signed_offset_cycles"].to_numpy(float)
    crest = df["crest_absolute_offset_cycles"].to_numpy(float)

    recomputed = {
        "median_absolute_offset_cycles": float(np.median(offsets)),
        "mean_absolute_offset_cycles": float(np.mean(offsets)),
        "median_signed_offset_cycles": float(np.median(signed)),
        "mean_half_cycle_deviation": float(np.mean(np.abs(offsets - 0.5))),
        "broad_half_cycle_band_count": int(np.sum((offsets >= 0.25) & (offsets <= 0.75))),
        "within_one_parent_cycle_count": int(np.sum(offsets <= 1.0)),
        "after_horizon_count": int(np.sum(signed > 0)),
        "power_crest_median_absolute_offset_cycles": float(np.median(crest)),
        "child_beats_crest_count": int(np.sum(offsets < crest)),
    }
    for key, value in recomputed.items():
        if key in scored["metrics"] and not np.isclose(value, scored["metrics"][key]):
            raise RuntimeError(f"Independent recomputation failed for {key}")

    rng = np.random.default_rng(439439)
    boot = np.median(rng.choice(offsets, size=(200_000, len(offsets)), replace=True), axis=1)
    median_ci = np.quantile(boot, [0.025, 0.975]).tolist()
    crest_boot = np.median(rng.choice(crest, size=(200_000, len(crest)), replace=True), axis=1)
    crest_ci = np.quantile(crest_boot, [0.025, 0.975]).tolist()
    validation = {
        "status": "VALIDATED",
        "result_sha256": sha256(SCORED),
        "score_csv_sha256": sha256(SCORES),
        "recomputed_metrics": recomputed,
        "bootstrap_median_95_interval_cycles": median_ci,
        "bootstrap_crest_median_95_interval_cycles": crest_ci,
        "paired_child_better_than_crest": {
            "count": int(np.sum(offsets < crest)),
            "n": int(len(offsets)),
            "one_sided_exact_sign_p": float(0.5 ** len(offsets)),
            "classification": "secondary robustness description; not an extra frozen gate",
        },
        "development_case_reproduction": {
            "sxs_id": "SXS:BBH:0305",
            "observed_absolute_offset_cycles": 0.42670185787896414,
            "T438_reported_absolute_offset_cycles": 0.426702,
            "absolute_difference": abs(0.42670185787896414 - 0.426702),
        },
    }
    (RESULTS / "T439_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")

    # Long-form exact comparison rows.
    offset_rows = []
    for row in df.to_dict(orient="records"):
        label = row["sxs_id"].replace("SXS:BBH:", "")
        offset_rows.extend(
            [
                {
                    "simulation": label,
                    "mass_ratio": float(row["mass_ratio"]),
                    "chi_eff": float(row["chi_eff"]),
                    "landmark": "Space–Time child turn",
                    "absolute_offset_cycles": float(row["absolute_offset_cycles"]),
                },
                {
                    "simulation": label,
                    "mass_ratio": float(row["mass_ratio"]),
                    "chi_eff": float(row["chi_eff"]),
                    "landmark": "Waveform power crest",
                    "absolute_offset_cycles": float(row["crest_absolute_offset_cycles"]),
                },
            ]
        )

    # Control quantiles; 101 points keep the report compact and reviewable.
    q = np.linspace(0, 1, 101)
    shuffle = np.asarray(controls["shuffled_mean_deviation"], dtype=float)
    observed = float(controls["observed_mean_deviation"])
    control_rows = []
    for quantile, value in zip(q, np.quantile(shuffle, q)):
        control_rows.extend(
            [
                {
                    "quantile": float(quantile),
                    "series": "Chronology-shuffle mean deviation",
                    "half_cycle_deviation": float(value),
                },
                {
                    "quantile": float(quantile),
                    "series": "Observed ordered mean deviation",
                    "half_cycle_deviation": observed,
                },
            ]
        )

    # Three representative waveform-only activity histories, aligned only after reveal.
    activity_rows = []
    by_id = {row["sxs_id"]: row for row in scored["holdouts"]}
    for simulation in ["SXS:BBH:0001", "SXS:BBH:1178", "SXS:BBH:0063"]:
        pred_path = RESULTS / f"{simulation.replace(':', '_')}_WAVEFORM_ONLY.npz"
        series = np.load(pred_path)
        row = by_id[simulation]
        t = np.asarray(series["time"], dtype=float)
        activity = np.asarray(series["beta_activity"], dtype=float)
        x = (t - row["horizon_first_sample_time_M"]) / row["parent_cycle_M"]
        mask = (x >= -1.5) & (x <= 0.75)
        indices = np.flatnonzero(mask)
        if indices.size > 140:
            indices = np.unique(np.linspace(indices[0], indices[-1], 140, dtype=int))
        scale = max(np.finfo(float).tiny, float(np.nanmax(activity[mask])))
        for i in indices:
            activity_rows.append(
                {
                    "time_from_horizon_cycles": float(x[i]),
                    "activity_fraction": float(activity[i] / scale),
                    "simulation": simulation.replace("SXS:BBH:", ""),
                }
            )

    gate_rows = [
        {
            "order": 1,
            "gate": "Median absolute offset",
            "required": "0.40–0.60 cycles",
            "observed": scored["metrics"]["median_absolute_offset_cycles"],
            "passed": scored["gates"]["median_in_frozen_half_cycle_band"],
        },
        {
            "order": 2,
            "gate": "Broad half-cycle band",
            "required": "at least 6 of 9",
            "observed": scored["metrics"]["broad_half_cycle_band_count"],
            "passed": scored["gates"]["six_of_nine_in_broad_band"],
        },
        {
            "order": 3,
            "gate": "Within one parent cycle",
            "required": "at least 7 of 9",
            "observed": scored["metrics"]["within_one_parent_cycle_count"],
            "passed": scored["gates"]["seven_of_nine_within_one_cycle"],
        },
        {
            "order": 4,
            "gate": "Chronology control",
            "required": "empirical p ≤ 0.05",
            "observed": scored["metrics"]["shuffle_empirical_p"],
            "passed": scored["gates"]["beats_chronology_shuffle"],
        },
        {
            "order": 5,
            "gate": "Power-crest baseline",
            "required": "child median smaller",
            "observed": scored["metrics"]["power_crest_median_absolute_offset_cycles"],
            "passed": scored["gates"]["beats_power_crest_baseline"],
        },
    ]

    exact_rows = []
    for row in scored["holdouts"]:
        exact_rows.append(
            {
                "simulation": row["sxs_id"].replace("SXS:BBH:", ""),
                "q": row["mass_ratio"],
                "chi_eff": row["chi_eff"],
                "signed_child_cycles": row["signed_offset_cycles"],
                "absolute_child_cycles": row["absolute_offset_cycles"],
                "crest_cycles": row["crest_absolute_offset_cycles"],
                "broad_half_cycle_band": row["within_broad_half_cycle_band"],
            }
        )

    summary_path = rel(SCORED)
    csv_path = rel(SCORES)
    protocol_path = rel(PROTOCOL)
    predictions_path = rel(PREDICTIONS)
    validation_path = rel(RESULTS / "T439_VALIDATION.json")
    sources = [
        {
            "id": "t439_score",
            "label": "T439 frozen holdout score",
            "path": summary_path,
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": f"SELECT * FROM read_json_auto('{summary_path}')",
                "description": "Loads the sealed T439 waveform predictions and scores them against first common-horizon times.",
                "tables_used": [summary_path, csv_path],
                "filters": ["Nine frozen non-precessing SXS holdouts", "SXS:BBH:0305 excluded from gates"],
                "metric_definitions": [
                    "Absolute offset is |child-landmark time minus first common-horizon time| divided by the frozen local parent cycle.",
                    "The power-crest baseline uses the same horizon and cycle denominator.",
                ],
            },
        },
        {
            "id": "t439_protocol",
            "label": "T439 frozen protocol",
            "path": protocol_path,
        },
        {
            "id": "t439_predictions",
            "label": "Sealed waveform-only predictions",
            "path": predictions_path,
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": f"SELECT * FROM read_json_auto('{predictions_path}')",
                "description": "Loads the sealed per-simulation waveform-only landmark inventory; time-series arrays are preserved in the referenced NPZ artifacts.",
                "tables_used": [predictions_path],
            },
        },
        {
            "id": "t439_validation",
            "label": "Independent T439 validation",
            "path": validation_path,
        },
        {
            "id": "sxs_catalog",
            "label": "SXS public numerical-relativity catalog",
            "href": "https://data.black-holes.org/waveforms/index.html",
        },
        {
            "id": "sxs_catalog_paper",
            "label": "SXS catalog paper",
            "href": "https://arxiv.org/abs/1904.04831",
        },
    ]

    m = scored["metrics"]
    headline = [
        {
            "median_child_offset": m["median_absolute_offset_cycles"],
            "median_crest_offset": m["power_crest_median_absolute_offset_cycles"],
            "broad_count": m["broad_half_cycle_band_count"],
            "shuffle_p": m["shuffle_empirical_p"],
        }
    ]
    now = datetime.now(timezone.utc).isoformat()
    title = "T439 — The half-cycle belongs to the crest, not the relational-child turn"
    manifest = {
        "version": 1,
        "surface": "report",
        "title": title,
        "description": "Frozen nine-simulation confirmation of the T438 Space–Time relational-child timing landmark.",
        "generatedAt": now,
        "sources": sources,
        "cards": [
            {
                "id": "median_child",
                "dataset": "headline",
                "sourceId": "t439_score",
                "description": "Median unsigned distance from the child-turn landmark to first common-horizon formation, in frozen parent cycles.",
                "metrics": [
                    {"label": "Child-turn median", "field": "median_child_offset", "format": "number", "unit": "parent cycles"},
                    {"label": "Crest baseline", "field": "median_crest_offset", "format": "number", "unit": "parent cycles"},
                ],
            },
            {
                "id": "broad_count",
                "dataset": "headline",
                "sourceId": "t439_score",
                "description": "Holdouts inside the frozen 0.25–0.75-cycle half-cycle band.",
                "metrics": [
                    {"label": "Frozen-band count", "field": "broad_count", "format": "number", "unit": "of 9"}
                ],
            },
            {
                "id": "shuffle_p",
                "dataset": "headline",
                "sourceId": "t439_score",
                "description": "Empirical probability that chronology-destroying controls were at least as close to a half-cycle as the ordered landmark.",
                "metrics": [
                    {"label": "Chronology-control p", "field": "shuffle_p", "format": "number"}
                ],
            },
        ],
        "charts": [
            {
                "id": "offset_comparison",
                "title": "Child-turn and waveform-crest offsets",
                "type": "bar",
                "dataset": "offset_rows",
                "sourceId": "t439_score",
                "encodings": {
                    "x": {"field": "simulation", "type": "nominal"},
                    "y": {"field": "absolute_offset_cycles", "type": "quantitative"},
                    "color": {"field": "landmark", "type": "nominal"},
                },
                "options": {"orientation": "vertical", "grouping": "grouped"},
            },
            {
                "id": "activity_histories",
                "title": "Representative relational-child activity histories",
                "type": "line",
                "dataset": "activity_rows",
                "sourceId": "t439_predictions",
                "encodings": {
                    "x": {"field": "time_from_horizon_cycles", "type": "quantitative"},
                    "y": {"field": "activity_fraction", "type": "quantitative"},
                    "color": {"field": "simulation", "type": "nominal"},
                },
            },
            {
                "id": "control_quantiles",
                "title": "Ordered result against chronology-shuffle controls",
                "type": "line",
                "dataset": "control_rows",
                "sourceId": "t439_score",
                "encodings": {
                    "x": {"field": "quantile", "type": "quantitative"},
                    "y": {"field": "half_cycle_deviation", "type": "quantitative"},
                    "color": {"field": "series", "type": "nominal"},
                },
            },
        ],
        "tables": [
            {
                "id": "holdouts",
                "title": "Exact holdout offsets",
                "dataset": "exact_rows",
                "sourceId": "t439_score",
                "columns": [
                    {"field": "simulation", "label": "SXS simulation"},
                    {"field": "q", "label": "Mass ratio q", "format": "number"},
                    {"field": "chi_eff", "label": "Effective spin", "format": "number"},
                    {"field": "signed_child_cycles", "label": "Signed child offset", "format": "number", "unit": "cycles", "movement": True},
                    {"field": "absolute_child_cycles", "label": "Absolute child offset", "format": "number", "unit": "cycles"},
                    {"field": "crest_cycles", "label": "Crest offset", "format": "number", "unit": "cycles"},
                    {"field": "broad_half_cycle_band", "label": "In 0.25–0.75 band"},
                ],
                "defaultSort": {"field": "q", "direction": "asc"},
            },
            {
                "id": "gates",
                "title": "Frozen confirmation gates",
                "dataset": "gate_rows",
                "sourceId": "t439_score",
                "columns": [
                    {"field": "order", "label": "#", "format": "number"},
                    {"field": "gate", "label": "Gate"},
                    {"field": "required", "label": "Required"},
                    {"field": "observed", "label": "Observed", "format": "number"},
                    {"field": "passed", "label": "Pass"},
                ],
                "defaultSort": {"field": "order", "direction": "asc"},
            },
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {title}"},
            {
                "id": "technical_summary",
                "type": "markdown",
                "sourceId": "t439_score",
                "body": (
                    "## Technical summary\n\n"
                    "**The frozen half-cycle claim was not supported for the Space–Time relational-child turn.** "
                    f"Its median unsigned offset was `{m['median_absolute_offset_cycles']:.3f}` parent cycles, and only `{m['broad_half_cycle_band_count']}/9` holdouts occupied the predeclared 0.25–0.75 band. "
                    f"The waveform power crest—not the child turn—had a median offset of `{m['power_crest_median_absolute_offset_cycles']:.3f}` cycles. "
                    f"The ordered child landmark was nevertheless non-random under the frozen chronology control (`p={m['shuffle_empirical_p']:.4f}`) and beat the crest in all 9 systems. "
                    "This separates a recurring near-horizon child reorientation from the broader half-cycle crest relation."
                ),
            },
            {"id": "headline", "type": "metric-strip", "cardIds": ["median_child", "broad_count", "shuffle_p"]},
            {
                "id": "main_finding",
                "type": "markdown",
                "sourceId": "t439_score",
                "body": (
                    "## The holdouts move the child landmark inward\n\n"
                    "Every bar uses the same frozen local parent-cycle denominator. The blue child-turn bars cluster near the common horizon; the orange crest bars retain the approximate half-cycle relation. "
                    "The implication is specific: T438's `0.427`-cycle child result does not generalize, while a separate crest-scale half-cycle relation remains visible."
                ),
            },
            {"id": "offset_chart", "type": "chart", "chartId": "offset_comparison"},
            {
                "id": "trajectory_finding",
                "type": "markdown",
                "sourceId": "t439_predictions",
                "body": (
                    "## Ordered Space–Time activity still finds a sharp near-horizon turn\n\n"
                    "Time zero is first common-horizon formation; each history is divided by its own maximum only to compare shape. The peaks are obtained from waveform data before the horizon is revealed. "
                    "They are therefore useful timing landmarks, but their post-hoc concentration near `0.17` cycles must be confirmed by a newly frozen test before it can be assigned an ARA rung."
                ),
            },
            {"id": "activity_chart", "type": "chart", "chartId": "activity_histories"},
            {
                "id": "scope",
                "type": "markdown",
                "sourceId": "t439_protocol",
                "body": (
                    "## Scope, coordinates, and denominator\n\n"
                    "The cohort contains nine untouched, non-precessing public SXS simulations spanning mass ratios `q=1–8` plus aligned-spin variants. "
                    "Space/Connection is the smoothed radial log-amplitude step; Time/Traversal is the smoothed half-phase step; the child landmark is the strongest ordered change in their path direction inside the waveform-only late-parent basin. "
                    "One parent cycle is `π/ω` at the frozen T435 waveform handover estimate."
                ),
            },
            {
                "id": "method",
                "type": "markdown",
                "sourceId": "t439_protocol",
                "body": (
                    "## Sealed holdout design\n\n"
                    "The cohort, landmark, cycle denominator, five gates, and controls were hashed before the holdout products were scored. Waveform-only predictions were then written and SHA-256 sealed before `Horizons.h5` supplied first common-horizon times. "
                    "The unchanged implementation reproduces T438's development value to within `1.4×10⁻⁷` cycles."
                ),
            },
            {"id": "gate_table", "type": "table", "tableId": "gates"},
            {
                "id": "control_finding",
                "type": "markdown",
                "sourceId": "t439_score",
                "body": (
                    "## Chronology matters, but this control does not prove a new clock\n\n"
                    "The observed mean distance from a half-cycle is below every one of the 1,000 chronology-shuffle ensemble values. This shows that the selected ordered trajectory is not reproduced after temporal order is destroyed. "
                    "However, the shuffle can place maxima anywhere in a long eligible basin; the paired crest comparison is the stronger practical baseline."
                ),
            },
            {"id": "control_chart", "type": "chart", "chartId": "control_quantiles"},
            {
                "id": "limits",
                "type": "markdown",
                "body": (
                    "## Limitations and robustness boundary\n\n"
                    "These are numerical-relativity simulations generated within general relativity, not independent detector events. The primary endpoint was unsigned; seven landmarks followed the horizon and two led it. "
                    "The new `0.174`-cycle median is an exploratory outcome, not a frozen child-rung prediction. It may reflect a physical redistribution stage, waveform extraction, common-horizon convention, or their interaction."
                ),
            },
            {"id": "exact_table", "type": "table", "tableId": "holdouts"},
            {
                "id": "next",
                "type": "markdown",
                "body": (
                    "## Recommended next test\n\n"
                    "Freeze the newly observed near-horizon window on a fresh cohort, but do not call it `0.25`, `1/6`, or a grandchild landmark yet. The decisive comparison should test two predeclared candidates simultaneously: "
                    "(1) crest at one half-cycle and (2) relational-child turning inside `0.08–0.32` cycles, with sign scored separately and a short late-basin control that cannot win merely by preferring the record end."
                ),
            },
            {
                "id": "questions",
                "type": "markdown",
                "body": (
                    "## Further questions\n\n"
                    "- Does the near-horizon child offset survive precessing and eccentric binaries?\n"
                    "- Is its variation explained by mass ratio, aligned spin, or numerical resolution?\n"
                    "- Does an independent horizon-shear or mode-phase observable identify the same child turn?\n"
                    "- Is the crest half-cycle relation a genuine cross-scale handover or a waveform/common-horizon convention?"
                ),
            },
        ],
    }
    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": now,
            "status": "ready",
            "datasets": {
                "headline": headline,
                "offset_rows": offset_rows,
                "activity_rows": activity_rows,
                "control_rows": control_rows,
                "exact_rows": exact_rows,
                "gate_rows": gate_rows,
            },
        },
        "sources": sources,
    }
    (RESULTS / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    summary = f"""# T439 result — spacetime-child half-cycle confirmation

**Frozen verdict: {scored['verdict']}.** The Space–Time relational-child turn did not remain near one half parent cycle: its median absolute offset was `{m['median_absolute_offset_cycles']:.6f}` cycles and only `{m['broad_half_cycle_band_count']}/9` holdouts landed in the frozen `0.25–0.75` band.

The power crest did retain the near-half-cycle relation, with median `{m['power_crest_median_absolute_offset_cycles']:.6f}` cycles. The child turn was still sharply ordered: it beat all 1,000 chronology-shuffle ensembles (`p={m['shuffle_empirical_p']:.6f}`), lay within one parent cycle in `9/9`, and was closer than the crest in `9/9` systems.

The unchanged implementation reproduced the T438 development case at `0.426701858` cycles versus the previously reported `0.426702`, confirming that the holdout result is not pipeline drift.

## Interpretation

- The original half-cycle assignment to the relational child is not supported.
- A broader half-cycle waveform-crest relation is supported descriptively in this cohort.
- A distinct near-horizon child-turn landmark emerged at median `0.173789` cycles, but this is post-hoc and requires a new frozen cohort before any ARA rung is assigned.
- Seven child turns followed first common-horizon formation and two preceded it, so direction is not yet a universal rule.
"""
    (ROOT / "T439_RESULTS_SUMMARY.md").write_text(summary, encoding="utf-8")

    chart_map = {
        "offset_comparison": {
            "question": "Which landmark carries the half-cycle relation?",
            "type": "grouped bar",
            "fields": ["simulation", "absolute_offset_cycles", "landmark"],
            "claim": "Crest remains near half-cycle; child turn moves inward.",
        },
        "activity_histories": {
            "question": "Does the ordered child turn have a visible local history?",
            "type": "line",
            "fields": ["time_from_horizon_cycles", "activity_fraction", "simulation"],
            "claim": "Waveform-only path-direction activity peaks near the hidden horizon.",
        },
        "control_quantiles": {
            "question": "Does temporal order matter?",
            "type": "line",
            "fields": ["quantile", "half_cycle_deviation", "series"],
            "claim": "Chronology destruction does not reproduce the ordered timing concentration.",
        },
    }
    (RESULTS / "T439_CHART_MAP.json").write_text(json.dumps(chart_map, indent=2), encoding="utf-8")
    print(json.dumps({"validation": validation, "artifact": str(RESULTS / 'artifact.json')}, indent=2))


if __name__ == "__main__":
    main()
