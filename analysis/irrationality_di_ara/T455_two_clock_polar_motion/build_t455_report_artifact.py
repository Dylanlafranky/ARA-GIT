"""Build the bounded geometry-first Data Analytics report artifact for T455."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records", date_format="iso"))


def split_name(date: pd.Series) -> pd.Series:
    return np.select(
        [date.le("2008-12-31"), date.between("2009-01-01", "2016-12-31")],
        ["development", "validation"],
        default="holdout",
    )


def main() -> None:
    generated = datetime.now(timezone.utc).isoformat()
    result = json.loads((RESULTS / "T455_RESULT.json").read_text(encoding="utf-8"))
    windows = pd.read_csv(RESULTS / "T455_SCALE_WINDOWS.csv", parse_dates=["start_date", "end_date"])
    metrics = pd.read_csv(RESULTS / "T455_FORECAST_METRICS.csv")
    controls = pd.read_csv(RESULTS / "T455_FALSE_TIME_CONTROLS.csv")
    bootstrap = pd.read_csv(RESULTS / "T455_BLOCK_BOOTSTRAP.csv")
    geometry = pd.read_csv(RESULTS / "T455_SCALE_GEOMETRY.csv")
    quadrants = pd.read_csv(RESULTS / "T455_QUADRANT_OCCUPANCY.csv")
    spectrum = pd.read_csv(RESULTS / "T455_POLAR_SPECTRUM.csv")
    seasonal = pd.read_csv(RESULTS / "T455_POSTHOC_SEASONAL_AUDIT.csv")
    transfer = pd.read_csv(RESULTS / "T455_LEAVE_ONE_SCALE_OUT.csv")
    gates = pd.read_csv(RESULTS / "T455_FROZEN_GATES.csv")
    similarity = pd.read_csv(RESULTS / "T455_COEFFICIENT_SIMILARITY.csv")

    daily = windows[windows.scale_days.eq(1)].copy()
    daily["year"] = daily.end_date.dt.year
    clock_yearly = daily.groupby("year", as_index=False).agg(
        mean_lod_ms=("lod", lambda x: 1000 * x.mean()),
        mean_clock_ridge_nano=("clock_ridge_nano", "mean"),
        min_clock_ara=("clock_ara", "min"),
        max_clock_ara=("clock_ara", "max"),
    )

    pole_path = windows[windows.scale_days.eq(30)][
        ["end_date", "pole_x", "pole_y", "pole_radius"]
    ].copy()
    pole_path["split"] = split_name(pole_path.end_date)
    pole_path["observation"] = pole_path.end_date.dt.strftime("%Y-%m-%d")

    diara = windows[windows.scale_days.isin([30, 90])][
        ["end_date", "scale_days", "pole_amount_ara", "pole_traversal_ara", "pole_turn_rad", "pole_displacement"]
    ].dropna().copy()
    diara["grain"] = diara.scale_days.astype(str) + " days"
    diara["split"] = split_name(diara.end_date)
    diara["observation"] = diara.end_date.dt.strftime("%Y-%m-%d")

    geometry_plot = geometry.copy()
    geometry_plot["grain"] = geometry_plot.scale_days.astype(str) + " days"

    quadrant_plot = quadrants[
        quadrants.scale_days.isin([30, 90]) & quadrants.split.eq("holdout")
    ].copy()
    quadrant_plot["grain"] = quadrant_plot.scale_days.astype(str) + " days"
    quadrant_plot["fraction_pct"] = 100 * quadrant_plot.fraction

    hold = metrics[metrics.split.eq("holdout")].copy()
    clock = hold[hold.model.eq("clock_only")][["scale_days", "horizon_windows", "mae"]].rename(
        columns={"mae": "clock_mae"}
    )
    improvement = hold[hold.model.isin(["clock_pole_diara", "full_child"])].merge(
        clock, on=["scale_days", "horizon_windows"]
    )
    improvement["improvement_pct"] = 100 * (improvement.clock_mae - improvement.mae) / improvement.clock_mae
    improvement["grain"] = improvement.scale_days.astype(str) + " days"
    improvement["series"] = improvement.model.map(
        {"clock_pole_diara": "Di-ARA child", "full_child": "raw + Di-ARA child"}
    ) + ", " + improvement.horizon_windows.astype(str) + " window"

    controls_plot = controls[
        controls.candidate_model.eq("clock_pole_diara") & controls.horizon_windows.eq(4)
    ].copy()
    controls_plot["grain"] = controls_plot.scale_days.astype(str) + " days"
    controls_plot["control_label"] = controls_plot.control.map(
        {
            "real_pole_child": "live child",
            "pole_shift_365d": "child shifted 365d",
            "reversed_chronology": "reversed chronology",
            "reflected_traversal": "reflected traversal",
            "year_block_permuted": "year blocks permuted",
        }
    ).fillna(controls_plot.control)

    seasonal_plot = seasonal.copy()
    seasonal_plot["grain"] = seasonal_plot.scale_days.astype(str) + " days"
    seasonal_plot["series"] = seasonal_plot.horizon_windows.astype(str) + " window"

    bootstrap_plot = bootstrap[
        bootstrap.candidate_model.eq("clock_pole_diara") & bootstrap.horizon_windows.eq(4)
    ].copy()
    bootstrap_plot["grain"] = bootstrap_plot.scale_days.astype(str) + " days"
    bootstrap_plot["mean_gain_microseconds"] = 1e6 * bootstrap_plot.mean_mae_gain_seconds
    bootstrap_plot["ci_low_microseconds"] = 1e6 * bootstrap_plot.ci_low
    bootstrap_plot["ci_high_microseconds"] = 1e6 * bootstrap_plot.ci_high

    top_spectrum = spectrum.nlargest(12, "relative_power").sort_values("period_days").copy()
    top_spectrum["period_label"] = top_spectrum.period_days.round(1).astype(str) + " days"

    transfer_pivot = transfer.pivot_table(
        index="omitted_scale_days", columns="model", values="mae", aggfunc="first"
    ).reset_index()
    transfer_pivot["improvement_pct"] = 100 * (
        transfer_pivot.clock_only - transfer_pivot.full_child
    ) / transfer_pivot.clock_only
    transfer_pivot["grain"] = transfer_pivot.omitted_scale_days.astype(str) + " days"

    gates["result"] = np.where(gates.passed.astype(str).str.lower().eq("true"), "PASS", "FAIL")
    similarity["scale_pair"] = similarity.scale_a.astype(str) + "d vs " + similarity.scale_b.astype(str) + "d"

    headline = pd.DataFrame(
        [
            {
                "daily_observations": result["source_rows_1984_onward"],
                "clock_ridge_max_nano": 1e9 * result["max_abs_exact_clock_ara_from_ridge"],
                "dominant_pole_period_days": float(spectrum.loc[spectrum.relative_power.idxmax(), "period_days"]),
                "positive_four_window_scales": int((improvement[(improvement.model.eq("clock_pole_diara")) & improvement.horizon_windows.eq(4)].improvement_pct > 0).sum()),
                "positive_transfer_scales": result["positive_transfer_scales"],
                "frozen_gates_passed": result["gates_passed"],
            }
        ]
    )

    source_iers = {
        "id": "iers_eop_c04",
        "label": "IERS Earth Orientation Parameters C04 daily series",
        "path": str(ROOT / "source" / "eopc04_20u24.1962-now.csv"),
        "href": "https://datacenter.iers.org/products/eop/long-term/c04_20u24/csv/",
        "query": {
            "language": "python",
            "description": "Official daily x/y polar motion, UT1−UTC and length-of-day observations; filtered to 1984 onward with no interpolation.",
            "executed_at": generated,
            "tables_used": ["eopc04_20u24.1962-now.csv"],
            "filters": ["date >= 1984-01-01", "complete x_pole, y_pole and LOD"],
            "metric_definitions": [
                "Exact clock ARA = 2s/(1+s), s=(86400+LOD)/86400.",
                "Pole amount ARA = 2r/(1+r), r=current displacement/previous displacement.",
                "Pole traversal ARA = 1 + wrapped signed heading change/pi.",
            ],
        },
    }
    source_analysis = {
        "id": "t455_analysis",
        "label": "Frozen T455 protocol, causal forecast ledger and controls",
        "path": str(ROOT / "FROZEN_PROTOCOL.md"),
        "query": {
            "language": "python",
            "description": "Frozen multi-grain ARA construction, chronological development/validation/holdout prediction, false-time controls, block bootstrap and post-result same-season diagnostic.",
            "executed_at": generated,
            "tables_used": [
                "T455_SCALE_WINDOWS.csv",
                "T455_FORECAST_LEDGER.csv",
                "T455_FALSE_TIME_CONTROLS.csv",
                "T455_POSTHOC_SEASONAL_AUDIT.csv",
            ],
        },
    }

    title = "T455 — Two Clocks and Geographic Polar Motion"
    charts = [
        {
            "id": "clock_ridge",
            "title": "Exact Earth-clock ridge displacement by year",
            "subtitle": "The full 0–2 coordinate is effectively 1.0; nanounit magnification makes the real LOD variation visible.",
            "type": "line",
            "dataset": "clock_yearly",
            "sourceId": "iers_eop_c04",
            "encodings": {
                "x": {"field": "year", "type": "quantitative", "label": "Calendar year"},
                "y": {"field": "mean_clock_ridge_nano", "type": "quantitative", "label": "Mean (clock ARA − 1) × 10⁹"},
            },
            "layout": "full",
        },
        {
            "id": "pole_path",
            "title": "Geographic polar-motion path at the 30-day grain",
            "subtitle": "The visible orbit is the parent-facing spatial path from which the relational amount and traversal children are cut.",
            "type": "scatter",
            "dataset": "pole_path",
            "sourceId": "iers_eop_c04",
            "encodings": {
                "x": {"field": "pole_x", "type": "quantitative", "label": "IERS x polar motion (arcseconds)"},
                "y": {"field": "pole_y", "type": "quantitative", "label": "IERS y polar motion (arcseconds)"},
                "color": {"field": "split", "type": "nominal", "label": "Chronological role"},
                "tooltip": [
                    {"field": "observation", "type": "nominal", "label": "Window end"},
                    {"field": "pole_radius", "type": "quantitative", "label": "Pole radius (arcseconds)"},
                ],
            },
            "layout": "full",
        },
        {
            "id": "diara_plane",
            "title": "Pole amount and signed traversal at coarse grains",
            "subtitle": "Amount remains ridge-facing while signed traversal occupies the lower half at 30 and 90 days.",
            "type": "scatter",
            "dataset": "diara_plane",
            "sourceId": "t455_analysis",
            "encodings": {
                "x": {"field": "pole_amount_ara", "type": "quantitative", "label": "Pole amount ARA (0–2)"},
                "y": {"field": "pole_traversal_ara", "type": "quantitative", "label": "Signed traversal ARA (0–2)"},
                "color": {"field": "grain", "type": "nominal", "label": "Grain"},
                "tooltip": [
                    {"field": "observation", "type": "nominal", "label": "Window end"},
                    {"field": "split", "type": "nominal", "label": "Role"},
                ],
            },
            "layout": "full",
        },
        {
            "id": "traversal_scale",
            "title": "Median pole traversal coordinate across grains",
            "subtitle": "Validation and holdout converge at the coarse grains; the daily cut remains a noisier lower-scale expression.",
            "type": "line",
            "dataset": "geometry",
            "sourceId": "t455_analysis",
            "encodings": {
                "x": {"field": "scale_days", "type": "quantitative", "label": "Grain (days)"},
                "y": {"field": "median_traversal_ara", "type": "quantitative", "label": "Median traversal ARA (0–2)"},
                "color": {"field": "split", "type": "nominal", "label": "Chronological role"},
            },
            "layout": "full",
        },
        {
            "id": "quadrants",
            "title": "Holdout quadrant occupancy at 30 and 90 days",
            "subtitle": "The occupied lower quadrants are the children of this directional cut, not missing sections that must be filled.",
            "type": "bar",
            "dataset": "quadrants",
            "sourceId": "t455_analysis",
            "encodings": {
                "x": {"field": "quadrant", "type": "nominal", "label": "Amount/traversal quadrant"},
                "y": {"field": "fraction_pct", "type": "quantitative", "label": "Holdout windows (%)"},
                "color": {"field": "grain", "type": "nominal", "label": "Grain"},
            },
            "layout": "full",
        },
        {
            "id": "forecast_improvement",
            "title": "Holdout forecast improvement over clock-only",
            "subtitle": "The Di-ARA child is more stable than the raw-plus-relational full child, especially beyond one window.",
            "type": "bar",
            "dataset": "forecast_improvement",
            "sourceId": "t455_analysis",
            "encodings": {
                "x": {"field": "grain", "type": "nominal", "label": "Grain"},
                "y": {"field": "improvement_pct", "type": "quantitative", "label": "MAE improvement over clock-only (%)"},
                "color": {"field": "series", "type": "nominal", "label": "Candidate and horizon"},
            },
            "layout": "full",
        },
        {
            "id": "false_time_controls",
            "title": "Four-window Di-ARA false-time controls",
            "subtitle": "The 365-day shift preserves the broad gain, identifying an annual parent carrier rather than a uniquely live handover.",
            "type": "bar",
            "dataset": "controls_h4",
            "sourceId": "t455_analysis",
            "encodings": {
                "x": {"field": "grain", "type": "nominal", "label": "Grain"},
                "y": {"field": "improvement_vs_clock_pct", "type": "quantitative", "label": "Improvement over clock-only (%)"},
                "color": {"field": "control_label", "type": "nominal", "label": "Pole history/control"},
            },
            "layout": "full",
        },
        {
            "id": "seasonal_residual",
            "title": "Live Di-ARA gain beyond the same-season baseline",
            "subtitle": "A residual remains, strongest at 90 days, but this diagnostic was designed after the frozen result.",
            "type": "line",
            "dataset": "seasonal_audit",
            "sourceId": "t455_analysis",
            "encodings": {
                "x": {"field": "scale_days", "type": "quantitative", "label": "Grain (days)"},
                "y": {"field": "diara_improvement_over_season_pct", "type": "quantitative", "label": "Improvement over clock + same-season (%)"},
                "color": {"field": "series", "type": "nominal", "label": "Forecast horizon"},
            },
            "layout": "full",
        },
        {
            "id": "spectrum",
            "title": "Strongest geographic-pole spectral periods",
            "subtitle": "The largest independent spectral peak is 361.65 days, matching the coarse traversal-cycle reconstruction.",
            "type": "bar",
            "dataset": "spectrum",
            "sourceId": "iers_eop_c04",
            "encodings": {
                "x": {"field": "period_label", "type": "nominal", "label": "Period"},
                "y": {"field": "relative_power", "type": "quantitative", "label": "Relative spectral power"},
            },
            "layout": "full",
        },
    ]

    tables = [
        {
            "id": "geometry_table",
            "title": "Scale geometry and implied cycle",
            "subtitle": "The median signed turn is converted back into the cycle length implied at each grain.",
            "dataset": "geometry",
            "sourceId": "t455_analysis",
            "defaultSort": {"field": "scale_days", "direction": "asc"},
            "columns": [
                {"field": "scale_days", "label": "Grain (days)", "format": "number"},
                {"field": "split", "label": "Role"},
                {"field": "median_amount_ara", "label": "Median amount ARA", "format": "number"},
                {"field": "median_traversal_ara", "label": "Median traversal ARA", "format": "number"},
                {"field": "negative_turn_fraction", "label": "Negative-turn fraction", "format": "number"},
                {"field": "implied_cycle_days_from_median_turn", "label": "Implied cycle (days)", "format": "number"},
            ],
            "layout": "full",
        },
        {
            "id": "bootstrap_table",
            "title": "Four-window Di-ARA block bootstrap",
            "subtitle": "Positive values mean lower absolute LOD error than the clock-only model.",
            "dataset": "bootstrap_h4",
            "sourceId": "t455_analysis",
            "defaultSort": {"field": "grain", "direction": "asc"},
            "columns": [
                {"field": "grain", "label": "Grain"},
                {"field": "mean_gain_microseconds", "label": "Mean MAE gain (µs)", "format": "number"},
                {"field": "ci_low_microseconds", "label": "95% block CI low (µs)", "format": "number"},
                {"field": "ci_high_microseconds", "label": "95% block CI high (µs)", "format": "number"},
                {"field": "p_gain_positive", "label": "Bootstrap positive fraction", "format": "number"},
            ],
            "layout": "full",
        },
        {
            "id": "gates_table",
            "title": "Frozen gates",
            "subtitle": "These gates constrain the prospective claim; they do not erase descriptive geometry below them.",
            "dataset": "gates",
            "sourceId": "t455_analysis",
            "defaultSort": {"field": "gate", "direction": "asc"},
            "columns": [
                {"field": "gate", "label": "Gate"},
                {"field": "statement", "label": "Frozen statement"},
                {"field": "observed", "label": "Observed", "format": "number"},
                {"field": "threshold", "label": "Threshold"},
                {"field": "result", "label": "Result"},
            ],
            "layout": "full",
        },
        {
            "id": "similarity_table",
            "title": "Cross-grain coefficient direction",
            "subtitle": "Thirty- and 90-day models are strongly aligned; daily coefficients point in a different direction.",
            "dataset": "similarity",
            "sourceId": "t455_analysis",
            "defaultSort": {"field": "cosine_similarity", "direction": "desc"},
            "columns": [
                {"field": "scale_pair", "label": "Scale pair"},
                {"field": "cosine_similarity", "label": "Cosine similarity", "format": "number"},
            ],
            "layout": "full",
        },
    ]

    cards = [
        {"id": "observations", "description": "Official daily observations used after the frozen start date.", "dataset": "headline", "sourceId": "iers_eop_c04", "metrics": [{"label": "Daily observations", "field": "daily_observations", "format": "number"}]},
        {"id": "ridge", "description": "Largest exact two-clock displacement from the ARA ridge, magnified by one billion.", "dataset": "headline", "sourceId": "iers_eop_c04", "metrics": [{"label": "Max |ARA−1| × 10⁹", "field": "clock_ridge_max_nano", "format": "number"}]},
        {"id": "period", "description": "Largest independent geographic-pole spectral peak.", "dataset": "headline", "sourceId": "iers_eop_c04", "metrics": [{"label": "Dominant pole period", "field": "dominant_pole_period_days", "format": "number", "suffix": " days"}]},
        {"id": "horizon", "description": "Grains where the Di-ARA child improves the four-window holdout forecast.", "dataset": "headline", "sourceId": "t455_analysis", "metrics": [{"label": "Positive h=4 grains", "field": "positive_four_window_scales", "format": "number", "suffix": "/4"}]},
        {"id": "transfer", "description": "Omitted grains with positive leave-one-scale-out transfer.", "dataset": "headline", "sourceId": "t455_analysis", "metrics": [{"label": "Positive transfer grains", "field": "positive_transfer_scales", "format": "number", "suffix": "/4"}]},
        {"id": "gates", "description": "Prospective full-child gates passed under the frozen protocol.", "dataset": "headline", "sourceId": "t455_analysis", "metrics": [{"label": "Frozen gates", "field": "frozen_gates_passed", "format": "number", "suffix": "/6"}]},
    ]

    blocks = [
        {"id": "title", "type": "markdown", "body": f"# {title}"},
        {"id": "summary", "type": "markdown", "sourceId": "t455_analysis", "body": "## Technical summary\n\n**T455 recovered a scale-coherent annual geographic-pole traversal wave, but did not confirm the full pole state as a scale-invariant live predictor of Earth-clock timing.** The exact SI-day/Earth-rotation relation sits within 2.07×10⁻⁸ of the ARA ridge. At 30 and 90 days, pole amount remains ridge-facing while signed traversal occupies a stable lower branch whose implied cycle converges near one year. The relational Di-ARA child improves four-window holdout forecasts at all four grains, but shifting that child by 365 days preserves nearly the same broad gain. The current result is therefore an annual parent carrier with a smaller, post-result live-state residual—not yet Time itself or a confirmed universal handover."},
        {"id": "metrics", "type": "metric-strip", "cardIds": ["observations", "ridge", "period", "horizon", "transfer", "gates"]},
        {"id": "address", "type": "markdown", "sourceId": "iers_eop_c04", "body": "## Who, what, when, where, why and how\n\n**Who:** Earth as the parent identity. **What:** the exact relation between an SI atomic day and the observed Earth-rotation day, plus geographic polar motion as a candidate child. **When:** daily observations from 1984-01-01 to 2026-07-29, cut into 1-, 7-, 30- and 90-day grains. **Where:** parent two-clock ridge → pole-displacement amount/traversal child. **Why:** test whether one relational child retains geometry and prospective value when the observational grain changes. **How:** frozen chronological splits, exact 0–2 ARA transforms, causal forecasts, false-time controls, block bootstrap and a separately labelled post-result seasonal diagnostic."},
        {"id": "clock_text", "type": "markdown", "body": "## Parent two-clock ridge\n\nThe clock coordinate is not min–max scaled. It is the exact ratio of observed rotation-day length to 86,400 SI seconds, mapped by 2s/(1+s). Because those clocks differ by milliseconds, their coordinate is necessarily very close to 1.0. The magnified graph shows real variation without pretending that nanounit motion fills the whole ARA."},
        {"id": "clock_chart", "type": "chart", "chartId": "clock_ridge", "layout": "full"},
        {"id": "geometry_text", "type": "markdown", "body": "## Geographic-pole child geometry\n\nThe spatial pole path is cut into two independent relational coordinates. Amount compares consecutive displacement magnitudes; traversal records the signed turn between consecutive displacement vectors. This is the pole Irrationality Di-ARA used here. It is not a relabelled clock coordinate and it is not assumed to be Time."},
        {"id": "pole_chart", "type": "chart", "chartId": "pole_path", "layout": "full"},
        {"id": "diara_chart", "type": "chart", "chartId": "diara_plane", "layout": "full"},
        {"id": "scale_text", "type": "markdown", "body": "## Scale invariance and occupied children\n\nThe daily cut is noisy and fills all four quadrants. At 30 and 90 days the signed-turn child becomes almost completely one-sided while amount continues to cross its ridge. The two coarse cuts independently imply a roughly annual cycle and share coefficient direction. This is the requested scale result: not identical values at every grain, but a stable parent-facing geometry that becomes clearer when the child is viewed at a compatible scale."},
        {"id": "traversal_chart", "type": "chart", "chartId": "traversal_scale", "layout": "full"},
        {"id": "quadrant_chart", "type": "chart", "chartId": "quadrants", "layout": "full"},
        {"id": "geometry_table_block", "type": "table", "tableId": "geometry_table", "layout": "full"},
        {"id": "spectrum_chart", "type": "chart", "chartId": "spectrum", "layout": "full"},
        {"id": "forecast_text", "type": "markdown", "body": "## Prospective timing test\n\nThe raw-plus-relational full child is unstable across grains and fails the primary transfer claim. The Di-ARA-only child is cleaner: its four-window forecasts improve over clock-only at every grain. That pattern is statistically positive under moving-block resampling, but it does not by itself identify a live handover."},
        {"id": "forecast_chart", "type": "chart", "chartId": "forecast_improvement", "layout": "full"},
        {"id": "bootstrap_table_block", "type": "table", "tableId": "bootstrap_table", "layout": "full"},
        {"id": "controls_text", "type": "markdown", "body": "## False-time controls locate the annual parent\n\nA pole child shifted by 365 days performs almost as well as the live child. Reversing chronological order generally destroys the gain, while reflecting traversal is not consistently worse until the coarsest grain. The information is time-ordered and seasonal, but its live orientation is not yet uniquely locked."},
        {"id": "controls_chart", "type": "chart", "chartId": "false_time_controls", "layout": "full"},
        {"id": "posthoc_text", "type": "markdown", "body": "## Post-result same-season diagnostic\n\nAfter seeing the frozen result, a clock-plus-365-day baseline was added explicitly as a diagnostic. The live Di-ARA child still reduces error slightly at short grains and by about 4–5.5% at 90 days. This residual is a strong T456 hypothesis, but it cannot change T455's frozen verdict."},
        {"id": "seasonal_chart", "type": "chart", "chartId": "seasonal_residual", "layout": "full"},
        {"id": "scope", "type": "markdown", "body": "## Scope definitions\n\nThe parent target is mean length-of-day in a future same-grain window. The geographic-pole child is a relation between consecutive pole displacements, not the absolute location of True North and not the geomagnetic pole. Geographic polar motion is the rotation axis moving relative to Earth's crust; magnetic north is a different medium and remains deferred. Development ends in 2008, validation covers 2009–2016 and untouched holdout begins in 2017."},
        {"id": "methodology", "type": "markdown", "body": "## Methodology\n\nAll coordinates retain their own 0–2 identity. The two-clock coordinate uses the exact day-length ratio. Pole amount uses consecutive displacement magnitude ratio. Pole traversal uses wrapped signed heading change. Ridge models use development-only standardisation and fixed regularisation. Forecasts are causal at 1, 2 and 4 windows. Controls shift the pole by 365 days, reverse chronology, reflect traversal and permute year blocks. Uncertainty uses moving blocks sized to approximately one year at each grain."},
        {"id": "gates_block", "type": "table", "tableId": "gates_table", "layout": "full"},
        {"id": "similarity_block", "type": "table", "tableId": "similarity_table", "layout": "full"},
        {"id": "limitations", "type": "markdown", "body": "## Limitations and robustness\n\nThe annual carrier is expected in polar motion, so recovering it validates the cut but is not a new physical law. Raw pole coordinates overfit when combined with the relational child. Daily heading changes are noise-sensitive. The 90-day seasonal audit has only 39 holdout rows, so its percentage gain is less precise despite block-positive intervals. T455 does not include atmospheric or oceanic angular momentum, seasonal harmonics, measurement-error propagation or magnetic-pole observations. The post-result seasonal comparison is exploratory by construction."},
        {"id": "next", "type": "markdown", "body": "## Next steps\n\nFreeze T456 around the live-minus-same-season question. Give the baseline explicit annual and semiannual terms, retain the same four grains, and compare the current pole Di-ARA with the one-year-prior pole Di-ARA. Then add published atmospheric and oceanic angular-momentum excitation as named sibling children. A live timing child should improve the residual forecast across grains and preserve signed traversal orientation after those parent and sibling effects are removed."},
        {"id": "questions", "type": "markdown", "body": "## Questions this leaves open\n\nIs the residual 90-day gain a true live pole-to-rotation transfer, or another unmodelled seasonal child? Does traversal orientation remain necessary after atmospheric and oceanic excitation is included? Does the annual parent split into a geographic-pole child and a genuinely timing-facing sibling, or is the pole only a spatial shadow of a larger Earth-system relation?"},
    ]

    for widget in [*cards, *charts, *tables]:
        dataset = widget["dataset"]
        widget["source"] = {
            "id": widget.get("sourceId", "t455_analysis"),
            "label": "T455 bounded analytical snapshot",
            "path": str(RESULTS / "artifact.json"),
            "query": {
                "language": "sql",
                "sql": f"SELECT * FROM {dataset};",
                "description": f"Return the complete bounded {dataset} dataset used by this widget.",
                "executed_at": generated,
                "tables_used": [dataset],
                "metric_definitions": source_iers["query"]["metric_definitions"],
            },
        }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": title,
        "description": "Frozen, scale-linked ARA test of two clocks and geographic polar motion using official daily IERS observations.",
        "generatedAt": generated,
        "sources": [source_iers, source_analysis],
        "cards": cards,
        "charts": charts,
        "tables": tables,
        "blocks": blocks,
    }
    snapshot = {
        "version": 1,
        "generatedAt": generated,
        "status": "ready",
        "datasets": {
            "headline": records(headline),
            "clock_yearly": records(clock_yearly),
            "pole_path": records(pole_path),
            "diara_plane": records(diara),
            "geometry": records(geometry_plot),
            "quadrants": records(quadrant_plot),
            "forecast_improvement": records(improvement),
            "controls_h4": records(controls_plot),
            "seasonal_audit": records(seasonal_plot),
            "bootstrap_h4": records(bootstrap_plot),
            "spectrum": records(top_spectrum),
            "transfer": records(transfer_pivot),
            "gates": records(gates),
            "similarity": records(similarity),
        },
    }
    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": snapshot,
        "sources": [source_iers, source_analysis],
    }
    path = RESULTS / "artifact.json"
    path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(path)
    print(f"datasets={len(snapshot['datasets'])}; bytes={path.stat().st_size}")


if __name__ == "__main__":
    main()
