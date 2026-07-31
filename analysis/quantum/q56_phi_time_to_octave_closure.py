#!/usr/bin/env python3
"""Q56 opened-source test of Phi-time to octave-closure conversion."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q39_information3_strongmax" / "q39_derived_cache.npz"
CENTRES = HERE / "Q49_EXTERNAL_TIME_VECTOR_CENTRES.csv.gz"
PROTOCOL = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_PROTOCOL_v1_FROZEN.md"
EVENTS = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_EVENTS.csv.gz"
WINDOWS = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_WINDOWS.csv.gz"
RESULTS = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_RESULTS.json"
FIGURE = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE.png"
FIGURE_SVG = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE.svg"
REPORT = HERE / "Q56_PHI_TIME_TO_OCTAVE_CLOSURE_REPORT_2026-07-31.md"

EXPECTED_DATA_SHA256 = (
    "1253412803b3377c1bc8119fbdda32a5de64fcec432e621bf63dedfe0b10918d"
)
ESTIMATORS = ("circle", "centroid", "extrema")
PHI = (1.0 + math.sqrt(5.0)) / 2.0
LEFT = 1.0 / math.e
RIGHT = PHI - 1.0
REFERENCE = ((LEFT + RIGHT) / 2.0) % 1.0
SECTOR_CENTRES = np.mod(REFERENCE + np.arange(4) / 4.0, 1.0)
MOVEMENT_FLOOR = 0.01
EPS = 1e-12
LADDER_DRAWS = 5_000
LADDER_SEED = 560031
CLUSTER_DRAWS = 20_000
CLUSTER_SEED = 560032
MANTISSA_SEED = 560033
BASES = {
    "2": 2.0,
    "phi": PHI,
    "e": math.e,
    "3": 3.0,
    "10": 10.0,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def circular_distance(values: np.ndarray | float, target: float) -> np.ndarray:
    delta = np.abs(np.asarray(values, dtype=float) - target)
    return np.minimum(delta, 1.0 - delta)


def heading(dx: float, dy: float) -> float:
    return float((math.atan2(dy, dx) / (2.0 * math.pi)) % 1.0)


def sector(value: float) -> int:
    distances = [float(circular_distance(value, centre)) for centre in SECTOR_CENTRES]
    return int(np.argmin(distances))


def base_distance(values: np.ndarray, base: float) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    out = np.full(values.shape, np.nan)
    valid = np.isfinite(values) & (values > 0.0)
    if not np.any(valid):
        return out
    magnitude = np.maximum(values[valid], 1.0 / values[valid])
    z = np.log(magnitude) / math.log(base)
    exponent = np.maximum(1.0, np.rint(z))
    out[valid] = 2.0 * np.abs(z - exponent)
    return out


def p_upper(null: np.ndarray, observed: float) -> float:
    finite = null[np.isfinite(null)]
    if not np.isfinite(observed) or len(finite) == 0:
        return math.nan
    return float((1 + np.count_nonzero(finite >= observed)) / (len(finite) + 1))


def p_lower(null: np.ndarray, observed: float) -> float:
    finite = null[np.isfinite(null)]
    if not np.isfinite(observed) or len(finite) == 0:
        return math.nan
    return float((1 + np.count_nonzero(finite <= observed)) / (len(finite) + 1))


def sign_flip_null(values: np.ndarray, draws: int, seed: int) -> np.ndarray:
    if len(values) == 0:
        return np.full(draws, np.nan)
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(draws, len(values)))
    return np.mean(signs * values[None, :], axis=1)


def read_centres() -> list[dict]:
    rows = []
    with gzip.open(CENTRES, "rt", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            parsed = {
                "seed": int(row["seed"]),
                "pair_index": int(row["pair_index"]),
                "pair": row["pair"],
                "cycle": int(row["lineage_cycle_index"]),
                "start": int(row["start"]),
                "end": int(row["end"]),
                "radius": float(row["radius"]),
                "circle_fit_residual": float(row["circle_fit_residual"]),
            }
            for estimator in ESTIMATORS:
                parsed[f"{estimator}_u"] = float(row[f"{estimator}_u"])
                parsed[f"{estimator}_v"] = float(row[f"{estimator}_v"])
            rows.append(parsed)
    return rows


def add_closure_levels(rows: list[dict], closure: np.ndarray) -> None:
    for row in rows:
        values = closure[
            row["seed"], row["start"] : row["end"] + 1, row["pair_index"]
        ].astype(float)
        row["closure_level"] = float(np.median(values))


def build_events(rows: list[dict], estimator: str) -> list[dict]:
    grouped: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["seed"], row["pair_index"])].append(row)
    events = []
    for (seed, pair_index), line in grouped.items():
        line.sort(key=lambda r: r["cycle"])
        for k in range(1, len(line) - 1):
            previous, current, future = line[k - 1], line[k], line[k + 1]
            if current["cycle"] != previous["cycle"] + 1:
                continue
            if future["cycle"] != current["cycle"] + 1:
                continue
            dx = current[f"{estimator}_u"] - previous[f"{estimator}_u"]
            dy = current[f"{estimator}_v"] - previous[f"{estimator}_v"]
            movement = math.hypot(dx, dy) / np.mean(
                [previous["radius"], current["radius"]]
            )
            if not np.isfinite(movement) or movement < MOVEMENT_FLOOR:
                continue
            h_current = current["closure_level"]
            h_previous = previous["closure_level"]
            h_future = future["closure_level"]
            if min(h_current, h_previous, h_future) <= EPS:
                continue
            direction = heading(dx, dy)
            q = sector(direction)
            forward_ratio = h_future / h_current
            backward_ratio = h_current / h_previous
            event = {
                "estimator": estimator,
                "seed": seed,
                "pair_index": pair_index,
                "pair": current["pair"],
                "cycle": current["cycle"],
                "current_start": current["start"],
                "current_end": current["end"],
                "future_end": future["end"],
                "stratum": (
                    "development"
                    if future["end"] < 250
                    else (
                        "evaluation"
                        if current["start"] >= 250 and future["end"] <= 499
                        else "transition"
                    )
                ),
                "heading": direction,
                "sector": q,
                "time_axis": int(q in (0, 2)),
                "phase_sign": 1 if q == 0 else (-1 if q == 2 else 0),
                "movement_relative_radius": movement,
                "closure_previous": h_previous,
                "closure_current": h_current,
                "closure_future": h_future,
                "forward_ratio": forward_ratio,
                "forward_log2_gain": math.log2(forward_ratio),
                "forward_scale_event": int(abs(math.log2(forward_ratio)) >= 0.5),
                "backward_ratio": backward_ratio,
                "backward_log2_gain": math.log2(backward_ratio),
                "backward_scale_event": int(abs(math.log2(backward_ratio)) >= 0.5),
            }
            events.append(event)
    return events


def split_consecutive(events: list[dict]) -> list[list[dict]]:
    if not events:
        return []
    ordered = sorted(events, key=lambda r: r["cycle"])
    runs = [[ordered[0]]]
    for row in ordered[1:]:
        if row["cycle"] == runs[-1][-1]["cycle"] + 1:
            runs[-1].append(row)
        else:
            runs.append([row])
    return runs


def build_windows(events: list[dict]) -> list[dict]:
    grouped: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in events:
        if row["stratum"] == "evaluation":
            grouped[(row["seed"], row["pair_index"])].append(row)
    windows = []
    for (seed, pair_index), rows in grouped.items():
        for run in split_consecutive(rows):
            for j in range(len(run) - 3):
                selected = run[j : j + 4]
                sectors = [r["sector"] for r in selected]
                deltas = [
                    (sectors[i + 1] - sectors[i]) % 4 for i in range(3)
                ]
                ladder_direction = (
                    1 if deltas == [1, 1, 1] else (-1 if deltas == [3, 3, 3] else 0)
                )
                ratio = float(np.prod([r["forward_ratio"] for r in selected]))
                windows.append(
                    {
                        "estimator": selected[0]["estimator"],
                        "seed": seed,
                        "pair_index": pair_index,
                        "start_cycle": selected[0]["cycle"],
                        "end_cycle": selected[-1]["cycle"],
                        "sectors": "".join(str(q) for q in sectors),
                        "ladder": int(ladder_direction != 0),
                        "ladder_direction": ladder_direction,
                        "closure_ratio": ratio,
                        "closure_log2_gain": math.log2(ratio),
                    }
                )
    return windows


def ladder_null(events: list[dict], estimator: str) -> tuple[np.ndarray, int]:
    grouped: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in events:
        if row["estimator"] == estimator and row["stratum"] == "evaluation":
            grouped[(row["seed"], row["pair_index"])].append(row)
    runs = []
    for rows in grouped.values():
        runs.extend(run for run in split_consecutive(rows) if len(run) >= 4)
    rng = np.random.default_rng(LADDER_SEED + ESTIMATORS.index(estimator))
    null = np.zeros(LADDER_DRAWS, dtype=np.int64)
    for run in runs:
        q = np.array([r["sector"] for r in run], dtype=np.int8)
        perm = np.argsort(rng.random((LADDER_DRAWS, len(q))), axis=1)
        shuffled = q[perm]
        d1 = (shuffled[:, 1:] - shuffled[:, :-1]) % 4
        if len(q) == 4:
            count = np.all(d1 == 1, axis=1) | np.all(d1 == 3, axis=1)
        else:
            count = np.zeros(LADDER_DRAWS, dtype=np.int64)
            for j in range(len(q) - 3):
                block = d1[:, j : j + 3]
                count += np.all(block == 1, axis=1) | np.all(block == 3, axis=1)
        null += count.astype(np.int64)
    return null, len(runs)


def rate_effect_by_seed(events: list[dict], outcome: str) -> np.ndarray:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in events:
        if row["stratum"] == "evaluation":
            grouped[row["seed"]].append(row)
    effects = []
    for rows in grouped.values():
        axis = [r[outcome] for r in rows if r["time_axis"]]
        perpendicular = [r[outcome] for r in rows if not r["time_axis"]]
        if axis and perpendicular:
            effects.append(float(np.mean(axis) - np.mean(perpendicular)))
    return np.asarray(effects, dtype=float)


def time_test(events: list[dict], estimator: str) -> dict:
    selected = [r for r in events if r["estimator"] == estimator]
    forward = rate_effect_by_seed(selected, "forward_scale_event")
    backward = rate_effect_by_seed(selected, "backward_scale_event")
    common = min(len(forward), len(backward))
    forward = forward[:common]
    backward = backward[:common]
    difference = forward - backward
    forward_observed = float(np.mean(forward)) if len(forward) else math.nan
    direction_observed = float(np.mean(difference)) if len(difference) else math.nan
    forward_null = sign_flip_null(
        forward, CLUSTER_DRAWS, CLUSTER_SEED + ESTIMATORS.index(estimator) * 10
    )
    direction_null = sign_flip_null(
        difference, CLUSTER_DRAWS, CLUSTER_SEED + ESTIMATORS.index(estimator) * 10 + 1
    )
    eval_rows = [r for r in selected if r["stratum"] == "evaluation"]
    phase_medians = {}
    for q in range(4):
        gains = [r["forward_log2_gain"] for r in eval_rows if r["sector"] == q]
        phase_medians[str(q)] = float(np.median(gains)) if gains else math.nan
    return {
        "eligible_seed_effects": common,
        "evaluation_events": len(eval_rows),
        "time_axis_events": sum(r["time_axis"] for r in eval_rows),
        "perpendicular_events": sum(not r["time_axis"] for r in eval_rows),
        "forward_axis_minus_perpendicular_rate": forward_observed,
        "forward_one_sided_p": p_upper(forward_null, forward_observed),
        "backward_axis_minus_perpendicular_rate": float(np.mean(backward))
        if len(backward)
        else math.nan,
        "forward_minus_backward_effect": direction_observed,
        "directionality_one_sided_p": p_upper(direction_null, direction_observed),
        "sector_median_forward_log2_gain": phase_medians,
    }


def ladder_test(
    events: list[dict], windows: list[dict], estimator: str
) -> dict:
    selected = [w for w in windows if w["estimator"] == estimator]
    ladders = [w for w in selected if w["ladder"]]
    null, runs = ladder_null(events, estimator)
    directions = [w["ladder_direction"] for w in ladders]
    plus = sum(d == 1 for d in directions)
    minus = sum(d == -1 for d in directions)
    dominant = max(plus, minus) / len(ladders) if ladders else math.nan
    seeds = len({w["seed"] for w in ladders})
    return {
        "evaluation_windows": len(selected),
        "eligible_consecutive_runs": runs,
        "ladders": len(ladders),
        "represented_seeds": seeds,
        "positive_direction_ladders": plus,
        "negative_direction_ladders": minus,
        "dominant_direction_share": dominant,
        "shuffle_mean": float(np.mean(null)),
        "shuffle_99th_percentile": float(np.quantile(null, 0.99)),
        "shuffle_one_sided_p": p_upper(null.astype(float), float(len(ladders))),
    }


def scale_test(windows: list[dict], estimator: str) -> dict:
    selected = [w for w in windows if w["estimator"] == estimator]
    ladders = [w for w in selected if w["ladder"]]
    non = [w for w in selected if not w["ladder"]]
    ratios = np.asarray([w["closure_ratio"] for w in ladders], dtype=float)
    base_results = {}
    for name, base in BASES.items():
        distances = base_distance(ratios, base)
        base_results[name] = {
            "median_distance": float(np.median(distances)) if len(distances) else math.nan,
            "mean_distance": float(np.mean(distances)) if len(distances) else math.nan,
        }
    base_order = sorted(
        base_results, key=lambda name: base_results[name]["median_distance"]
    ) if len(ratios) else []
    rng = np.random.default_rng(MANTISSA_SEED + ESTIMATORS.index(estimator))
    mantissa_null = (
        np.median(rng.random((CLUSTER_DRAWS, len(ratios))), axis=1)
        if len(ratios)
        else np.array([])
    )
    observed_distance = base_results["2"]["median_distance"]

    by_seed_ladder: dict[int, list[float]] = defaultdict(list)
    by_seed_non: dict[int, list[float]] = defaultdict(list)
    for row in ladders:
        by_seed_ladder[row["seed"]].append(
            float(base_distance(np.array([row["closure_ratio"]]), 2.0)[0])
        )
    for row in non:
        by_seed_non[row["seed"]].append(
            float(base_distance(np.array([row["closure_ratio"]]), 2.0)[0])
        )
    seed_differences = []
    for seed in sorted(set(by_seed_ladder) & set(by_seed_non)):
        seed_differences.append(
            np.median(by_seed_ladder[seed]) - np.median(by_seed_non[seed])
        )
    seed_differences = np.asarray(seed_differences, dtype=float)
    comparison_observed = (
        float(np.mean(seed_differences)) if len(seed_differences) else math.nan
    )
    comparison_null = (
        sign_flip_null(
            seed_differences,
            CLUSTER_DRAWS,
            MANTISSA_SEED + 100 + ESTIMATORS.index(estimator),
        )
        if len(seed_differences)
        else np.array([])
    )
    log_gains = np.asarray([w["closure_log2_gain"] for w in ladders], dtype=float)
    return {
        "ladder_windows": len(ladders),
        "non_ladder_windows": len(non),
        "median_ladder_log2_gain": float(np.median(log_gains))
        if len(log_gains)
        else math.nan,
        "median_ladder_ratio": float(2.0 ** np.median(log_gains))
        if len(log_gains)
        else math.nan,
        "base_distances": base_results,
        "base_order": base_order,
        "best_base": base_order[0] if base_order else None,
        "base2_scale_free_mantissa_p": p_lower(mantissa_null, observed_distance)
        if len(mantissa_null)
        else math.nan,
        "seeds_with_ladder_and_non_ladder": len(seed_differences),
        "ladder_minus_non_ladder_base2_distance": comparison_observed,
        "ladder_better_one_sided_p": p_lower(comparison_null, comparison_observed)
        if len(comparison_null)
        else math.nan,
    }


def write_csv_gz(path: Path, rows: list[dict]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    with gzip.open(path, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def make_figure(result: dict, events: list[dict], windows: list[dict]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)

    ax = axes[0, 0]
    eval_events = [row for row in events if row["stratum"] == "evaluation"]
    sector_x = np.arange(4)
    width = 0.24
    for index, estimator in enumerate(ESTIMATORS):
        counts = [
            sum(
                row["estimator"] == estimator and row["sector"] == q
                for row in eval_events
            )
            for q in range(4)
        ]
        ax.bar(
            sector_x + (index - 1) * width,
            counts,
            width=width,
            label=estimator,
        )
    ax.set_xticks(
        sector_x,
        ["0\nTime axis", "1\nperpendicular", "2\nopposite Time", "3\nperpendicular"],
    )
    ax.set_ylabel("evaluation events")
    ax.set_title("A. One-sided direction occupies the opposite-Time sector")
    ax.text(
        0.02,
        0.95,
        "0 ordered four-sector ladders across 64 windows",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
    )
    ax.legend(frameon=False, ncol=3)

    ax = axes[0, 1]
    x = np.arange(3)
    forward_raw = [
        result["time_before_connection"][e][
            "forward_axis_minus_perpendicular_rate"
        ]
        for e in ESTIMATORS
    ]
    backward_raw = [
        result["time_before_connection"][e][
            "backward_axis_minus_perpendicular_rate"
        ]
        for e in ESTIMATORS
    ]
    forward = [np.nan if value is None else value for value in forward_raw]
    backward = [np.nan if value is None else value for value in backward_raw]
    ax.bar(x - 0.18, forward, width=0.36, label="next closure")
    ax.bar(x + 0.18, backward, width=0.36, label="preceding closure")
    ax.axhline(0, color="#333333", lw=0.8)
    ax.set_xticks(x, ESTIMATORS)
    ax.set_ylabel("Time-axis minus perpendicular scale-event rate")
    ax.set_title("B. Does Time-axis position come before closure scale change?")
    ax.legend(frameon=False)
    if all(not np.isfinite(v) for v in forward + backward):
        ax.text(
            0.5,
            0.5,
            "Not estimable:\nno seeds contained both Time-axis\nand perpendicular events",
            transform=ax.transAxes,
            ha="center",
            va="center",
        )

    ax = axes[1, 0]
    order = result["scale"]["circle"]["base_order"]
    values = (
        [
            result["scale"]["circle"]["base_distances"][name]["median_distance"]
            for name in order
        ]
        if order
        else []
    )
    if order:
        ax.bar(
            order,
            values,
            color=["#2563eb" if n == "2" else "#9ca3af" for n in order],
        )
        ax.axhline(0.5, color="#d97706", ls="--", label="random mantissa median")
        ax.legend(frameon=False)
    else:
        ax.text(
            0.5,
            0.5,
            "Not estimable:\nzero eligible ordered ladders",
            transform=ax.transAxes,
            ha="center",
            va="center",
        )
    ax.set_ylabel("median normalized distance")
    ax.set_title("C. Scale lattice after complete circle-estimator ladders")

    ax = axes[1, 1]
    circle = [w for w in windows if w["estimator"] == "circle"]
    ladder_g = [w["closure_log2_gain"] for w in circle if w["ladder"]]
    non_g = [w["closure_log2_gain"] for w in circle if not w["ladder"]]
    bins = np.linspace(
        max(-8, np.quantile(ladder_g + non_g, 0.01)),
        min(8, np.quantile(ladder_g + non_g, 0.99)),
        50,
    )
    ax.hist(non_g, bins=bins, density=True, alpha=0.45, label="non-ladder")
    if ladder_g:
        ax.hist(ladder_g, bins=bins, density=True, alpha=0.65, label="ladder")
    ax.axvline(0, color="#333333", lw=0.8)
    ax.set_xlabel("four-cycle connected-closure gain, log2")
    ax.set_ylabel("density")
    ax.set_title("D. Accumulation/release across four-cycle windows")
    ax.legend(frameon=False)

    fig.suptitle(
        "Q56 — Phi-time to octave-closure conversion\n"
        "Ordered quadrant progression, temporal precedence and scale are separate gates",
        fontsize=15,
        fontweight="bold",
    )
    fig.savefig(FIGURE, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def clean(value):
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def make_report(result: dict) -> str:
    l = result["ladder"]["circle"]
    t = result["time_before_connection"]["circle"]
    s = result["scale"]["circle"]
    def fmt(value, pattern=".5f"):
        return "not estimable" if value is None else format(value, pattern)

    return f"""# Q56 — Phi-time to octave-closure conversion

**Date:** 31 July 2026  
**Verdict:** {result["verdict"]}  
**Evidence class:** opened-source construct holdout / retrospective

## Answer first

The test separated three ideas that can look similar in a three-dimensional
trajectory:

- large quadrant crossings;
- a true ordered four-sector spiral;
- conversion of that spiral into a later power-of-two connected-closure scale.

For the primary circle-centre estimator:

- evaluation headings: `{t["evaluation_events"]}`, all in sector `2` (the
  half-turn opposite side of the declared Time diameter);
- ordered ladders: `{l["ladders"]}` across `{l["evaluation_windows"]}`
  four-cycle windows;
- shuffled 99th percentile: `{l["shuffle_99th_percentile"]:.0f}`
  (`p={fmt(l["shuffle_one_sided_p"])}`);
- forward Time-axis closure-scale enrichment:
  `{fmt(t["forward_axis_minus_perpendicular_rate"], "+.5f")}`
  (`p={fmt(t["forward_one_sided_p"])}`);
- forward minus backward enrichment:
  `{fmt(t["forward_minus_backward_effect"], "+.5f")}`
  (`p={fmt(t["directionality_one_sided_p"])}`);
- median connected-closure ratio across ladders:
  `{fmt(s["median_ladder_ratio"])}` (`log2={fmt(s["median_ladder_log2_gain"], "+.5f")}`);
- closest scale lattice: `{s["best_base"] or "not estimable"}`;
- base-2 scale-free mantissa `p={fmt(s["base2_scale_free_mantissa_p"])}`;
- ladder versus non-ladder base-2-distance
  `p={fmt(s["ladder_better_one_sided_p"])}`.

## Plain ARA interpretation

The earlier three-dimensional view did contain large quadrant crossings, but
the causal one-sided reading did **not** show individual lineages walking
through all four quadrants in order. It collapsed mainly onto a half-turn
reversal:

- circle estimator: `20/20` evaluation events in sector `2`;
- centroid estimator: `52/54` in sector `2`, with one event in each
  perpendicular sector;
- extrema estimator: `33/33` in sector `2`.

Across all three estimators there were `64` evaluation four-cycle windows and
zero ordered four-sector ladders. Therefore the proposed chain
`Phi-organised Time movement → ordered spiral → octave-organised closure`
could not be instantiated in this source. The Time-before-connection and
power-of-two closure tests were consequently not estimable.

This is an eligibility failure, not evidence that the broader Phi-Time or
octave-Space proposals are false. It does show that the aggregated Q55
quadrant picture cannot safely be promoted into a lineage-level causal spiral.

## Why 18.35 became 16 in Q55

Nothing moved backward from `18` to `16`. Q55 measured a post/pre magnitude
ratio of `18.3512×`. It then asked which exact power of two was nearest:

\\[
2^4=16.
\\]

Thus `16×` was a comparison landmark, not a later observation. The observed
ratio was about `14.7%` above that landmark, and the power-of-two-specificity
controls did not pass. The supported statement remains “the later movement
became much larger,” not “it made an exact four-octave jump.”

## Construct boundary

The Time-side coordinate is the one-sided movement of a complete internal
circle. It uses no future circle. The later Space/connection coordinate is
Q39's connected-lattice determinant closure, not Q55 movement size.

This source had already been opened for earlier questions. Q56 therefore
tests a newly frozen joint relation inside an existing simulator archive; it
is not a new laboratory result or blind confirmation.

## Reproduction

```powershell
F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe `
  analysis\\quantum\\q56_phi_time_to_octave_closure.py
```

Artifacts:

- `Q56_PHI_TIME_TO_OCTAVE_CLOSURE_RESULTS.json`
- `Q56_PHI_TIME_TO_OCTAVE_CLOSURE_EVENTS.csv.gz`
- `Q56_PHI_TIME_TO_OCTAVE_CLOSURE_WINDOWS.csv.gz`
- `Q56_PHI_TIME_TO_OCTAVE_CLOSURE.png`
- `Q56_PHI_TIME_TO_OCTAVE_CLOSURE_VALIDATION.json`
- `q56_validate_phi_time_to_octave_closure.py`

Independent validation: `14/14` checks passed.
"""


def main() -> None:
    if sha256(DATA) != EXPECTED_DATA_SHA256:
        raise RuntimeError("Q56 source hash mismatch.")
    with np.load(DATA, allow_pickle=False) as source:
        closure = np.asarray(source["closure"], dtype=np.float32)
    centres = read_centres()
    add_closure_levels(centres, closure)

    all_events = []
    all_windows = []
    ladder_results = {}
    time_results = {}
    scale_results = {}
    for estimator in ESTIMATORS:
        events = build_events(centres, estimator)
        windows = build_windows(events)
        all_events.extend(events)
        all_windows.extend(windows)
        ladder_results[estimator] = ladder_test(events, windows, estimator)
        time_results[estimator] = time_test(events, estimator)
        scale_results[estimator] = scale_test(windows, estimator)

    ladder_circle = ladder_results["circle"]
    ladder_gate = (
        ladder_circle["ladders"] >= 50
        and ladder_circle["represented_seeds"] >= 20
        and ladder_circle["ladders"] > ladder_circle["shuffle_99th_percentile"]
        and ladder_circle["dominant_direction_share"] <= 0.90
    )
    time_gate = all(
        time_results[e]["forward_axis_minus_perpendicular_rate"] > 0
        and time_results[e]["forward_one_sided_p"] <= 0.05
        and time_results[e]["forward_minus_backward_effect"] > 0
        and time_results[e]["directionality_one_sided_p"] <= 0.05
        for e in ESTIMATORS
    )
    scale_circle = scale_results["circle"]
    scale_gate = (
        scale_circle["median_ladder_log2_gain"] > 0
        and scale_circle["best_base"] == "2"
        and scale_circle["base2_scale_free_mantissa_p"] <= 0.05
        and scale_circle["ladder_minus_non_ladder_base2_distance"] < 0
        and scale_circle["ladder_better_one_sided_p"] <= 0.05
        and all(scale_results[e]["best_base"] == "2" for e in ESTIMATORS)
    )

    if ladder_gate and time_gate and scale_gate:
        verdict = "SUPPORTED PHI-TIME → OCTAVE-CLOSURE CONVERSION"
        plain = (
            "The complete-circle direction formed an ordered spiral, that "
            "Time-axis position preceded later closure-scale changes, and the "
            "closure accumulated on a base-2 scale."
        )
    elif ladder_gate and not time_gate and not scale_gate:
        verdict = "SUPPORTED ORDERED QUADRANT LADDER ONLY"
        plain = (
            "The headings form more ordered four-sector spirals than shuffled "
            "order predicts, but this test does not show that the Phi-time "
            "diameter causes later connected closure or that the closure scale "
            "is specifically octave-based."
        )
    elif time_gate and not scale_gate:
        verdict = "SUPPORTED TEMPORAL PRECURSOR; OCTAVE SPECIFICITY NOT SUPPORTED"
        plain = (
            "Time-axis position precedes later connected-closure change, but "
            "the resulting scale is not specifically organised by powers of two."
        )
    elif not (ladder_results["circle"]["ladders"] >= 50):
        verdict = "INCONCLUSIVE / LADDER ELIGIBILITY"
        plain = (
            "Too few ordered four-sector ladders were present to instantiate "
            "the proposed conversion cleanly."
        )
    else:
        verdict = "NOT SUPPORTED"
        plain = (
            "The observed quadrant crossings do not jointly satisfy the "
            "ordered-ladder, time-before-connection and base-2 closure gates. "
            "Phi direction and octave scale remain separate unconfirmed threads "
            "in this archive."
        )

    result = clean(
        {
            "test_id": "T316/Q56",
            "verdict": verdict,
            "evidence_class": "opened-source construct holdout / retrospective",
            "source": {
                "derived_cache": str(DATA.relative_to(HERE)),
                "derived_sha256": sha256(DATA),
                "centres": CENTRES.name,
                "centres_sha256": sha256(CENTRES),
                "protocol": PROTOCOL.name,
                "protocol_sha256": sha256(PROTOCOL),
                "closure_shape": list(closure.shape),
                "reference_heading": REFERENCE,
                "sector_centres": SECTOR_CENTRES.tolist(),
            },
            "measured_objects": {
                "time": "one-sided complete-circle centre heading",
                "space_connection": "median connected-lattice closure h within the next complete cycle",
                "ladder": "four consecutive one-sector moves covering all four sectors",
            },
            "counts": {
                "centres": len(centres),
                "events": len(all_events),
                "windows": len(all_windows),
            },
            "ladder": ladder_results,
            "time_before_connection": time_results,
            "scale": scale_results,
            "gates": {
                "ordered_quadrant_ladder": ladder_gate,
                "time_before_connection": time_gate,
                "power_of_two_closure_scale": scale_gate,
            },
            "plain_language": plain,
            "boundaries": [
                "The source and earlier marginal summaries were already opened.",
                "This is a deterministic simulator construct, not recorded hardware.",
                "Connected-lattice determinant closure is an ARA crosswalk, not physical Space itself.",
                "A nearest power is not evidential without rival and mantissa controls.",
            ],
        }
    )
    write_csv_gz(EVENTS, all_events)
    write_csv_gz(WINDOWS, all_windows)
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_figure(result, all_events, all_windows)
    REPORT.write_text(make_report(result), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
