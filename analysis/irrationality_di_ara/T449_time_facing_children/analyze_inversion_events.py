"""Post-frozen T449C diagnostic: what happens near child-dominance inversions?"""

from __future__ import annotations

import json
import os
from itertools import product
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T449_time_facing_children\.mplconfig",
)
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T449_time_facing_children")
RESULTS = ROOT / "results"
RNG_SEED = 44903


def exact_sign_flip_p(effects: np.ndarray) -> float:
    effects = effects[np.isfinite(effects)]
    if not len(effects):
        return float("nan")
    observed = abs(float(np.mean(effects)))
    exceed = 0
    total = 0
    for signs in product((-1.0, 1.0), repeat=len(effects)):
        total += 1
        if abs(float(np.mean(effects * np.asarray(signs)))) >= observed - 1e-15:
            exceed += 1
    return exceed / total


def build_pairs(data: pd.DataFrame) -> pd.DataFrame:
    data = data.sort_values(["source_file", "child_window_index"]).copy()
    groups = data.groupby("source_file", sort=False)
    previous = groups.shift(1)
    adjacent = data.child_window_index.sub(previous.child_window_index).eq(1)
    pairs = data.loc[adjacent].copy()
    prior = previous.loc[adjacent]

    pairs["dominance_before"] = prior.dominance.to_numpy(dtype=float)
    pairs["ara_A_before"] = prior.ara_A.to_numpy(dtype=float)
    pairs["ara_B_before"] = prior.ara_B.to_numpy(dtype=float)
    pairs["is_exchange"] = (
        np.sign(pairs.dominance) != np.sign(pairs.dominance_before)
    ) & pairs.dominance.ne(0) & pairs.dominance_before.ne(0)
    pairs["direction"] = "no crossing"
    pairs.loc[pairs.is_exchange & pairs.dominance_before.gt(0), "direction"] = "retention → traversal"
    pairs.loc[pairs.is_exchange & pairs.dominance_before.lt(0), "direction"] = "traversal → retention"

    pairs["lifecycle_band"] = pd.cut(
        pairs.hours_to_collapse,
        bins=[0, 6, 24, 72, np.inf],
        labels=["final 6 h", "6–24 h", "24–72 h", ">72 h"],
        include_lowest=True,
    ).astype(str)

    current_groups = {
        "idle": pairs.share_idle,
        "proboscis": pairs.share_proboscis,
        "grooming": pairs.share_fore_groom + pairs.share_hind_groom + pairs.share_wing_groom,
        "locomotion": pairs.share_locomotion + pairs.share_altered_locomotion,
        "unresolved": pairs.share_unstereotyped + pairs.share_on_edge,
    }
    previous_groups = {
        "idle": prior.share_idle.to_numpy(dtype=float),
        "proboscis": prior.share_proboscis.to_numpy(dtype=float),
        "grooming": (prior.share_fore_groom + prior.share_hind_groom + prior.share_wing_groom).to_numpy(dtype=float),
        "locomotion": (prior.share_locomotion + prior.share_altered_locomotion).to_numpy(dtype=float),
        "unresolved": (prior.share_unstereotyped + prior.share_on_edge).to_numpy(dtype=float),
    }
    for name in current_groups:
        pairs[f"{name}_share"] = current_groups[name].to_numpy(dtype=float)
        pairs[f"delta_{name}"] = current_groups[name].to_numpy(dtype=float) - previous_groups[name]
    return pairs


def event_rates(pairs: pd.DataFrame) -> pd.DataFrame:
    order = ["final 6 h", "6–24 h", "24–72 h", ">72 h"]
    rows = []
    for band in order:
        cut = pairs[pairs.lifecycle_band.eq(band)]
        denominator = len(cut)
        for direction in ["retention → traversal", "traversal → retention", "either inversion"]:
            count = int(cut.is_exchange.sum()) if direction == "either inversion" else int(cut.direction.eq(direction).sum())
            rows.append(
                {
                    "lifecycle_band": band,
                    "direction": direction,
                    "adjacent_pairs": denominator,
                    "events": count,
                    "events_per_100_pairs": 100 * count / denominator if denominator else float("nan"),
                }
            )
    return pd.DataFrame(rows)


def per_fly_rate_contrast(pairs: pd.DataFrame) -> dict:
    rates = (
        pairs.groupby(["source_file", "lifecycle_band"], observed=True)
        .agg(pairs=("is_exchange", "size"), events=("is_exchange", "sum"))
        .reset_index()
    )
    rates["rate"] = rates.events / rates.pairs
    pivot = rates.pivot(index="source_file", columns="lifecycle_band", values="rate")
    if "final 6 h" not in pivot or ">72 h" not in pivot:
        return {}
    effect = (pivot["final 6 h"] - pivot[">72 h"]).dropna().to_numpy(dtype=float)
    return {
        "flies_with_both_bands": int(len(effect)),
        "median_final6_minus_gt72_rate": float(np.median(effect)) if len(effect) else float("nan"),
        "mean_final6_minus_gt72_rate": float(np.mean(effect)) if len(effect) else float("nan"),
        "positive_fraction": float(np.mean(effect > 0)) if len(effect) else float("nan"),
        "exact_two_sided_sign_flip_p": exact_sign_flip_p(effect),
    }


def behavior_residuals(pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = ["idle", "proboscis", "grooming", "locomotion", "unresolved"]
    controls = pairs[~pairs.is_exchange].copy()
    control_lookup = {
        feature: controls.groupby(["source_file", "lifecycle_band"], observed=True)[f"delta_{feature}"].mean()
        for feature in features
    }
    events = pairs[pairs.is_exchange].copy()
    event_rows = []
    for _, event in events.iterrows():
        for feature in features:
            baseline = control_lookup[feature].get((event.source_file, event.lifecycle_band), np.nan)
            event_rows.append(
                {
                    "source_file": event.source_file,
                    "direction": event.direction,
                    "lifecycle_band": event.lifecycle_band,
                    "feature": feature,
                    "raw_share_change": float(event[f"delta_{feature}"]),
                    "matched_nonexchange_mean_change": float(baseline) if np.isfinite(baseline) else np.nan,
                    "event_minus_matched_change": float(event[f"delta_{feature}"] - baseline) if np.isfinite(baseline) else np.nan,
                }
            )
    event_level = pd.DataFrame(event_rows)
    fly_level = (
        event_level.groupby(["direction", "feature", "source_file"], observed=True)
        .agg(
            events=("event_minus_matched_change", "count"),
            mean_raw_change=("raw_share_change", "mean"),
            mean_matched_residual=("event_minus_matched_change", "mean"),
        )
        .reset_index()
    )
    rows = []
    for (direction, feature), group in fly_level.groupby(["direction", "feature"], observed=True):
        effects = group.mean_matched_residual.to_numpy(dtype=float)
        rows.append(
            {
                "direction": direction,
                "feature": feature,
                "flies": int(len(group)),
                "events": int(group.events.sum()),
                "median_fly_raw_change": float(group.mean_raw_change.median()),
                "median_fly_matched_residual": float(group.mean_matched_residual.median()),
                "mean_fly_matched_residual": float(group.mean_matched_residual.mean()),
                "positive_fraction": float(np.mean(effects > 0)),
                "exact_two_sided_sign_flip_p": exact_sign_flip_p(effects),
            }
        )
    return event_level, pd.DataFrame(rows)


def event_centered_profiles(data: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    indexed = data.set_index(["source_file", "child_window_index"]).sort_index()
    rows = []
    features = {
        "C_A retention": "ara_A",
        "C_B traversal": "ara_B",
        "idle share": "share_idle",
        "proboscis share": "share_proboscis",
        "locomotion share": None,
        "grooming share": None,
    }
    for _, event in pairs[pairs.is_exchange].iterrows():
        for offset in [-1, 0, 1]:
            key = (event.source_file, int(event.child_window_index + offset))
            if key not in indexed.index:
                continue
            row = indexed.loc[key]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            for label, field in features.items():
                if label == "locomotion share":
                    value = row.share_locomotion + row.share_altered_locomotion
                elif label == "grooming share":
                    value = row.share_fore_groom + row.share_hind_groom + row.share_wing_groom
                else:
                    value = row[field]
                rows.append(
                    {
                        "source_file": event.source_file,
                        "direction": event.direction,
                        "offset_minutes": 10 * offset,
                        "series": label,
                        "value": float(value),
                    }
                )
    event_rows = pd.DataFrame(rows)
    profile = (
        event_rows.groupby(["direction", "offset_minutes", "series"], observed=True)
        .agg(events=("value", "size"), median=("value", "median"), q25=("value", lambda x: x.quantile(0.25)), q75=("value", lambda x: x.quantile(0.75)))
        .reset_index()
    )
    return profile


def make_figure(rates: pd.DataFrame, profile: pd.DataFrame, behavior: pd.DataFrame, parent: pd.DataFrame) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    blue, orange, purple, grey = "#388bfd", "#f59e0b", "#9b72cf", "#758195"
    directions = ["retention → traversal", "traversal → retention"]
    bands = ["final 6 h", "6–24 h", "24–72 h", ">72 h"]

    x = np.arange(len(bands))
    width = 0.36
    for index, direction in enumerate(directions):
        cut = rates[rates.direction.eq(direction)].set_index("lifecycle_band").reindex(bands)
        axes[0, 0].bar(x + (index - 0.5) * width, cut.events_per_100_pairs, width=width, label=direction, color=[orange, blue][index])
    axes[0, 0].set_xticks(x, bands)
    axes[0, 0].set(title="Inversion frequency by lifecycle distance", ylabel="events per 100 adjacent eligible pairs")
    axes[0, 0].legend()

    for direction, color in zip(directions, [orange, blue]):
        for series, style in [("C_A retention", "-"), ("C_B traversal", "--")]:
            cut = profile[(profile.direction.eq(direction)) & (profile.series.eq(series))].sort_values("offset_minutes")
            axes[0, 1].plot(cut.offset_minutes, cut["median"], marker="o", color=color, ls=style, label=f"{direction}: {series}")
    axes[0, 1].axvline(0, color=grey, ls=":")
    axes[0, 1].set(title="The measured children around each inversion", xlabel="minutes from sign change", ylabel="ARA coordinate (0–2)")
    axes[0, 1].legend(fontsize=8)

    features = ["idle", "proboscis", "grooming", "locomotion", "unresolved"]
    x = np.arange(len(features))
    for index, direction in enumerate(directions):
        cut = behavior[behavior.direction.eq(direction)].set_index("feature").reindex(features)
        axes[1, 0].bar(x + (index - 0.5) * width, cut.median_fly_matched_residual, width=width, label=direction, color=[orange, blue][index])
    axes[1, 0].axhline(0, color=grey, lw=1)
    axes[1, 0].set_xticks(x, features)
    axes[1, 0].set(title="Behaviour-share changes beyond same-fly non-crossing movement", ylabel="median fly residual share change")
    axes[1, 0].legend(fontsize=8)

    parent = parent.copy()
    x = np.arange(len(parent))
    axes[1, 1].bar(x, parent.actual_median_parent_response, color=[orange, blue])
    axes[1, 1].vlines(x, parent.null_2_5pct, parent.null_97_5pct, color=grey, lw=4, alpha=0.7, label="shifted 95% interval")
    axes[1, 1].axhline(0, color=grey, lw=1)
    axes[1, 1].set_xticks(x, parent.direction)
    axes[1, 1].set(title="Hourly parent response after each inversion direction", ylabel="following minus preceding parent progress")
    axes[1, 1].legend()

    fig.suptitle("T449C — what happens near the same-rung child inversion?", fontsize=19)
    fig.savefig(RESULTS / "T449_11_INVERSION_EVENT_DIAGNOSTIC.png", dpi=180)
    plt.close(fig)


def main() -> None:
    data = pd.read_csv(RESULTS / "T449_eligible_child_geometry.csv")
    holdout = data[data.split.eq("holdout")].copy()
    pairs = build_pairs(holdout)
    rates = event_rates(pairs)
    rate_contrast = per_fly_rate_contrast(pairs)
    event_level, behavior = behavior_residuals(pairs)
    profile = event_centered_profiles(holdout, pairs)
    parent = pd.read_csv(RESULTS / "T449_posthoc_directional_exchanges.csv")

    rates.to_csv(RESULTS / "T449_inversion_rates_by_lifecycle.csv", index=False)
    behavior.to_csv(RESULTS / "T449_inversion_behavior_deltas.csv", index=False)
    profile.to_csv(RESULTS / "T449_inversion_centered_profiles.csv", index=False)
    event_level.to_csv(RESULTS / "T449_inversion_event_level_behavior.csv", index=False)
    make_figure(rates, profile, behavior, parent)

    summary = {
        "status": "post-frozen T449C diagnostic; cannot alter T449 gates",
        "holdout_adjacent_eligible_pairs": int(len(pairs)),
        "holdout_inversions": int(pairs.is_exchange.sum()),
        "inversion_fraction": float(pairs.is_exchange.mean()),
        "directions": {key: int(value) for key, value in pairs.loc[pairs.is_exchange, "direction"].value_counts().items()},
        "rates_by_lifecycle": rates.to_dict(orient="records"),
        "final6_vs_gt72_inversion_rate": rate_contrast,
        "behavior_matched_diagnostics": behavior.to_dict(orient="records"),
        "parent_response": parent.to_dict(orient="records"),
        "definition": "inversion = sign change in dominance z_A-z_B across adjacent eligible ten-minute windows",
    }
    (RESULTS / "T449C_INVERSION_EVENT_RESULT.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
