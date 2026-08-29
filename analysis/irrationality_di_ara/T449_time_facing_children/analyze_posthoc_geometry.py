"""Post-frozen T449 geometry decomposition; cannot alter T449 qualifications."""

from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).with_name(".mplconfig")))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T449_time_facing_children")
RESULTS = ROOT / "results"
SPEC = importlib.util.spec_from_file_location("t449_primary", ROOT / "analyze_time_children.py")
PRIMARY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(PRIMARY)


def rank_correlation(a: pd.Series, b: pd.Series) -> float:
    ar = a.rank(method="average").to_numpy(dtype=float)
    br = b.rank(method="average").to_numpy(dtype=float)
    if len(ar) < 4 or np.std(ar) <= 1e-12 or np.std(br) <= 1e-12:
        return math.nan
    return float(np.corrcoef(ar, br)[0, 1])


def configure() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#f7f9fc",
            "axes.facecolor": "#ffffff",
            "savefig.facecolor": "#f7f9fc",
            "text.color": "#18212f",
            "axes.labelcolor": "#18212f",
            "axes.edgecolor": "#667085",
            "xtick.color": "#344054",
            "ytick.color": "#344054",
            "grid.color": "#d0d5dd",
            "font.size": 10,
            "axes.titleweight": "bold",
        }
    )


def main() -> None:
    configure()
    result = json.loads((RESULTS / "T449_RESULT.json").read_text(encoding="utf-8"))
    geometry = pd.read_csv(RESULTS / "T449_eligible_child_geometry.csv")
    geometry["common_parent_mode"] = (geometry.z_A + geometry.z_B) / 2
    geometry["differential_child_mode"] = (geometry.z_A - geometry.z_B) / 2

    hold = geometry[
        geometry.split.eq("holdout")
        & geometry.hours_to_collapse.gt(0)
        & geometry.hours_to_collapse.le(72)
    ].copy()
    fly_rows = []
    for name, group in hold.groupby("source_file"):
        fly_rows.append(
            {
                "source_file": name,
                "windows": len(group),
                "rho_hours_common": rank_correlation(group.hours_to_collapse, group.common_parent_mode),
                "rho_hours_differential": rank_correlation(group.hours_to_collapse, group.differential_child_mode),
            }
        )
    fly_modes = pd.DataFrame(fly_rows)

    binned = hold.copy()
    binned["bin"] = pd.cut(binned.hours_to_collapse, np.arange(0, 75, 3), include_lowest=True)
    binned = (
        binned.groupby("bin", observed=True)
        .agg(
            common_median=("common_parent_mode", "median"),
            common_q25=("common_parent_mode", lambda x: x.quantile(0.25)),
            common_q75=("common_parent_mode", lambda x: x.quantile(0.75)),
            differential_median=("differential_child_mode", "median"),
            differential_q25=("differential_child_mode", lambda x: x.quantile(0.25)),
            differential_q75=("differential_child_mode", lambda x: x.quantile(0.75)),
            windows=("source_file", "size"),
        )
        .reset_index()
    )
    binned["hours_before"] = binned.bin.map(lambda x: float(x.mid))

    dev_lags = pd.read_csv(RESULTS / "T449_development_fly_lags.csv")
    hold_lags = pd.read_csv(RESULTS / "T449_holdout_fly_lags.csv")
    flank_rows = []
    for split, frame in [("development", dev_lags), ("holdout", hold_lags)]:
        pivot = frame[frame.lag_windows.isin([-1, 1])].pivot(
            index="source_file", columns="lag_windows", values="correlation"
        ).dropna()
        for name, row in pivot.iterrows():
            flank_rows.append(
                {
                    "split": split,
                    "source_file": name,
                    "corr_minus10": row[-1],
                    "corr_plus10": row[1],
                    "plus_minus_minus": row[1] - row[-1],
                }
            )
    flank = pd.DataFrame(flank_rows)

    exchanges = pd.read_csv(RESULTS / "T449_holdout_exchanges.csv")
    response = pd.read_csv(RESULTS / "T449_exchange_parent_response.csv")
    parent = pd.read_csv(PRIMARY.T448_RESULTS / "T448B_24h_directional_states.csv")
    parent = parent[parent.split.eq("holdout")]
    direction_rows = []
    direction_nulls = {}
    for from_side, to_side in [("retention", "traversal"), ("traversal", "retention")]:
        event_cut = exchanges[exchanges.from_side.eq(from_side) & exchanges.to_side.eq(to_side)]
        response_cut = response[response.from_side.eq(from_side) & response.to_side.eq(to_side)]
        fly_response = response_cut.groupby("source_file").parent_delta_after_minus_before.median()
        actual = float(fly_response.median())
        null = PRIMARY.exchange_shift_null(event_cut, parent)
        key = f"{from_side}_to_{to_side}"
        direction_nulls[key] = null
        direction_rows.append(
            {
                "direction": f"{from_side} → {to_side}",
                "events": int(len(response_cut)),
                "flies": int(fly_response.size),
                "actual_median_parent_response": actual,
                "null_2_5pct": float(np.quantile(null, 0.025)),
                "null_5pct": float(np.quantile(null, 0.05)),
                "null_50pct": float(np.quantile(null, 0.50)),
                "null_95pct": float(np.quantile(null, 0.95)),
                "null_97_5pct": float(np.quantile(null, 0.975)),
                "lower_tail_p": float((1 + np.sum(null <= actual)) / (len(null) + 1)),
                "upper_tail_p": float((1 + np.sum(null >= actual)) / (len(null) + 1)),
            }
        )
    direction = pd.DataFrame(direction_rows)

    fly_modes.to_csv(RESULTS / "T449_posthoc_common_differential_by_fly.csv", index=False)
    binned.drop(columns="bin").to_csv(RESULTS / "T449_posthoc_common_differential_history.csv", index=False)
    flank.to_csv(RESULTS / "T449_posthoc_flank_asymmetry.csv", index=False)
    direction.to_csv(RESULTS / "T449_posthoc_directional_exchanges.csv", index=False)

    blue, orange, purple, grey, pink = "#2f6bff", "#f28e2b", "#8f63d3", "#667085", "#d84a78"
    fig, axes = plt.subplots(1, 3, figsize=(19, 6), constrained_layout=True)
    axes[0].plot(binned.hours_before, binned.common_median, color=blue, lw=2.3, label="common parent-facing mode")
    axes[0].fill_between(binned.hours_before, binned.common_q25, binned.common_q75, color=blue, alpha=0.15)
    axes[0].plot(binned.hours_before, binned.differential_median, color=orange, lw=2.3, label="differential child mode")
    axes[0].fill_between(binned.hours_before, binned.differential_q25, binned.differential_q75, color=orange, alpha=0.15)
    axes[0].axhline(0, color=grey, ls=":")
    axes[0].invert_xaxis()
    axes[0].set(title="Slow common mode versus child asymmetry", xlabel="hours before collapse", ylabel="development-standardized mode")
    axes[0].legend()
    sorted_fly = fly_modes.sort_values("rho_hours_common")
    y = np.arange(len(sorted_fly))
    axes[1].barh(y - 0.18, sorted_fly.rho_hours_common, height=0.35, color=blue, label="common mode")
    axes[1].barh(y + 0.18, sorted_fly.rho_hours_differential, height=0.35, color=orange, label="differential mode")
    axes[1].axvline(0, color=grey, ls=":")
    axes[1].set(title="Lifecycle ordering within each untouched fly", xlabel="Spearman correlation with hours remaining", ylabel="holdout fly")
    axes[1].set_yticks([])
    axes[1].legend()
    dynamic = PRIMARY.add_differences(geometry, "C_A_retention", "C_B_traversal")
    local = dynamic[dynamic.split.eq("holdout")].dropna(subset=["dA", "dB"])
    local = local.sample(min(5000, len(local)), random_state=PRIMARY.RNG_SEED)
    axes[2].scatter(local.dA, local.dB, s=7, alpha=0.18, color=purple)
    axes[2].axhline(0, color=grey, ls=":")
    axes[2].axvline(0, color=grey, ls=":")
    axes[2].set(title="Ten-minute changes form the local push–pull", xlabel="change in C_A retention", ylabel="change in C_B traversal")
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.suptitle("T449 post-frozen reading — local anti-phase rides a slower common lifecycle gradient", fontsize=18)
    fig.savefig(RESULTS / "T449_09_parent_common_child_differential.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(19, 6), constrained_layout=True)
    values = direction.actual_median_parent_response.to_numpy()
    axes[0].bar(direction.direction, values, color=[orange, blue])
    axes[0].axhline(0, color=grey, ls=":")
    axes[0].set(title="The two crossing directions are not equivalent", ylabel="following minus preceding parent progress")
    axes[0].tick_params(axis="x", rotation=18)
    for index, row in direction.iterrows():
        key = row.direction.replace(" → ", "_to_")
        null = direction_nulls[key]
        axes[1].hist(null, bins=40, alpha=0.45, label=row.direction)
        axes[1].axvline(row.actual_median_parent_response, color=[orange, blue][index], lw=2.2)
    axes[1].axvline(0, color=grey, ls=":")
    axes[1].set(title="Direction-specific parent response against shifted events", xlabel="median parent response", ylabel="shifted histories")
    axes[1].legend()
    parts = []
    for split, group in flank.groupby("split"):
        parts.append(group.plus_minus_minus.to_numpy())
    axes[2].boxplot(parts, tick_labels=["development", "holdout"], patch_artist=True, boxprops={"facecolor": "#d9e3f7"})
    axes[2].axhline(0, color=grey, ls=":")
    axes[2].set(title="Post-hoc +10 versus −10 minute flank asymmetry", ylabel="corr(+10 min) − corr(−10 min)")
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.suptitle("T449 post-frozen reading — directional splits are clues, not new passes", fontsize=18)
    fig.savefig(RESULTS / "T449_10_directional_exchange_split.png", dpi=180)
    plt.close(fig)

    posthoc = {
        "status": "post-frozen descriptive; cannot alter T449 gates",
        "holdout_final72_common_mode_median_spearman": float(fly_modes.rho_hours_common.median()),
        "holdout_final72_common_mode_positive_fraction": float((fly_modes.rho_hours_common > 0).mean()),
        "holdout_final72_differential_mode_median_spearman": float(fly_modes.rho_hours_differential.median()),
        "development_flank_asymmetry_median": float(flank[flank.split.eq("development")].plus_minus_minus.median()),
        "development_flank_asymmetry_positive_fraction": float((flank[flank.split.eq("development")].plus_minus_minus > 0).mean()),
        "holdout_flank_asymmetry_median": float(flank[flank.split.eq("holdout")].plus_minus_minus.median()),
        "holdout_flank_asymmetry_positive_fraction": float((flank[flank.split.eq("holdout")].plus_minus_minus > 0).mean()),
        "directional_exchanges": direction.to_dict(orient="records"),
        "primary_gates_unchanged": result["gates"],
    }
    (RESULTS / "T449_POSTHOC_RESULT.json").write_text(json.dumps(posthoc, indent=2), encoding="utf-8")
    print(json.dumps(posthoc, indent=2))


if __name__ == "__main__":
    main()
