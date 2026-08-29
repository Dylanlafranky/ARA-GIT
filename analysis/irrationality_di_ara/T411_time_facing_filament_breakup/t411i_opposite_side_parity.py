"""T411I: outcome-free parent/grandchild opposite-side parity diagnostic.

This diagnostic asks whether the S1/S2 grandchild coordinate occupies the
opposite ARA side of its parent, rather than treating the T411H landmarks as
fixed numerical targets.  Orientation is measured only before the final child
handover window so that the outcome cannot select the sign.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
INPUT = HERE / "results" / "T411H_three_rung_grandchild_lock" / "T411H_PREDICTIONS.csv"
OUT = HERE / "results" / "T411I_opposite_side_parity"
RNG = np.random.default_rng(41109)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator <= 1e-12:
        return np.nan
    return float(np.dot(a, b) / denominator)


def event_metrics(group: pd.DataFrame) -> dict[str, float | str | int]:
    v = group["v"].to_numpy(float)
    u = group["u"].to_numpy(float)
    w = group["w"].to_numpy(float)
    dv = group["dv"].to_numpy(float)
    du = group["du"].to_numpy(float)
    dw = group["dw"].to_numpy(float)
    nonzero_vw = np.abs(v * w) > 1e-12
    nonzero_vu = np.abs(v * u) > 1e-12
    return {
        "Name": str(group["Name"].iloc[0]),
        "fluid": str(group["fluid"].iloc[0]),
        "partition": str(group["partition"].iloc[0]),
        "n_snapshots": int(len(group)),
        "position_alignment_parent_grandchild": cosine(v, w),
        "position_alignment_parent_child": cosine(v, u),
        "position_alignment_child_grandchild": cosine(u, w),
        "flow_alignment_parent_grandchild": cosine(dv, dw),
        "flow_alignment_parent_child": cosine(dv, du),
        "flow_alignment_child_grandchild": cosine(du, dw),
        "median_parent_grandchild_product": float(np.median(v * w)),
        "opposite_side_fraction_parent_grandchild": (
            float(np.mean((v * w)[nonzero_vw] < 0)) if nonzero_vw.any() else np.nan
        ),
        "opposite_side_fraction_parent_child": (
            float(np.mean((v * u)[nonzero_vu] < 0)) if nonzero_vu.any() else np.nan
        ),
    }


def bootstrap_median_ci(values: np.ndarray, draws: int = 10_000) -> tuple[float, float]:
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return np.nan, np.nan
    samples = RNG.choice(values, size=(draws, len(values)), replace=True)
    medians = np.median(samples, axis=1)
    return tuple(float(x) for x in np.quantile(medians, [0.025, 0.975]))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(INPUT)
    all_events: list[dict[str, float | str | int]] = []

    for guard_factor in (1.0, 2.0):
        quiet = frame.loc[frame["lead_s"] > guard_factor * frame["child_horizon_s"]].copy()
        for _, group in quiet.groupby(["partition", "fluid", "Name"], sort=True):
            if len(group) < 4:
                continue
            row = event_metrics(group)
            row["quiet_guard_child_horizons"] = guard_factor
            all_events.append(row)

    event_frame = pd.DataFrame(all_events)
    event_frame.to_csv(OUT / "T411I_EVENT_ORIENTATION.csv", index=False)

    summary_rows: list[dict[str, float | str | int]] = []
    for keys, group in event_frame.groupby(
        ["partition", "quiet_guard_child_horizons", "fluid"], sort=True
    ):
        partition, guard_factor, fluid = keys
        for metric in (
            "position_alignment_parent_grandchild",
            "position_alignment_parent_child",
            "position_alignment_child_grandchild",
            "flow_alignment_parent_grandchild",
            "opposite_side_fraction_parent_grandchild",
            "opposite_side_fraction_parent_child",
        ):
            values = group[metric].to_numpy(float)
            finite = values[np.isfinite(values)]
            lo, hi = bootstrap_median_ci(finite)
            summary_rows.append(
                {
                    "partition": partition,
                    "quiet_guard_child_horizons": guard_factor,
                    "fluid": fluid,
                    "metric": metric,
                    "n_events": int(len(finite)),
                    "median": float(np.median(finite)) if len(finite) else np.nan,
                    "bootstrap_95_low": lo,
                    "bootstrap_95_high": hi,
                    "fraction_positive": float(np.mean(finite > 0)) if len(finite) else np.nan,
                }
            )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "T411I_FLUID_SUMMARY.csv", index=False)

    contrast_rows: list[dict[str, float | str]] = []
    metric = "position_alignment_parent_grandchild"
    for (partition, guard_factor), group in event_frame.groupby(
        ["partition", "quiet_guard_child_horizons"], sort=True
    ):
        s12 = group.loc[group["fluid"].isin(["S1", "S2"]), metric].dropna().to_numpy(float)
        s34 = group.loc[group["fluid"].isin(["S3", "S4"]), metric].dropna().to_numpy(float)
        if not len(s12) or not len(s34):
            continue
        observed = float(np.median(s12) - np.median(s34))
        boot = np.empty(10_000)
        for index in range(len(boot)):
            boot[index] = np.median(RNG.choice(s12, len(s12), replace=True)) - np.median(
                RNG.choice(s34, len(s34), replace=True)
            )
        lo, hi = (float(x) for x in np.quantile(boot, [0.025, 0.975]))
        contrast_rows.append(
            {
                "partition": partition,
                "quiet_guard_child_horizons": guard_factor,
                "metric": metric,
                "median_S1_S2_minus_S3_S4": observed,
                "bootstrap_95_low": lo,
                "bootstrap_95_high": hi,
            }
        )

    contrast = pd.DataFrame(contrast_rows)
    contrast.to_csv(OUT / "T411I_GROUP_CONTRAST.csv", index=False)

    result = {
        "question": "Are S1/S2 grandchildren coupled to the opposite ARA side of the parent?",
        "orientation_rule": "opposite side means centered parent v and grandchild w align negatively",
        "outcome_protection": "only snapshots earlier than one or two child horizons were used",
        "source": str(INPUT.relative_to(HERE)),
        "events": int(event_frame["Name"].nunique()),
        "rows": int(len(event_frame)),
    }
    (OUT / "T411I_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
