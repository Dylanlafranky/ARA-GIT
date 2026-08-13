"""T346: frozen temporal Di-ARA storage-handover-release test."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPRESENTATION = os.environ.get("T346_REPRESENTATION", "lab").strip().lower()
if REPRESENTATION not in {"lab", "num"}:
    raise ValueError("T346_REPRESENTATION must be 'lab' or 'num'")
os.environ["T344_REPRESENTATION"] = REPRESENTATION

import t344_baw_weir_irrationality_di_ara as base  # noqa: E402
from t345_line_circle_two_ledger import normalise_example  # noqa: E402


HERE = Path(__file__).resolve().parent
PREFIX = "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER" + (
    "" if REPRESENTATION == "lab" else "_NUMERICAL_REPLICATION"
)
PROTOCOL = HERE / "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = "205f48d722b80e59f3d0c766790c1ecfeabbf7eac50f3f644590301e1fdda512"
PRIMARY_W = 15
WINDOWS = (8, 15, 30)
BOOTSTRAPS = 2000
PERMUTATIONS = 1000
RNG_SEED = 34620260809


def connection_information_one(sectors: np.ndarray) -> float:
    if len(sectors) < 2:
        return math.nan
    left, right = sectors[:-1], sectors[1:]
    valid = (left >= 0) & (right >= 0)
    if not np.any(valid):
        return math.nan
    edge = left[valid].astype(np.int16) * 4 + right[valid].astype(np.int16)
    counts = np.bincount(edge, minlength=16).astype(np.float64)
    n = float(counts.sum())
    p = counts[counts > 0] / n
    entropy = float(-np.sum(p * np.log(p)))
    occupied = int(np.count_nonzero(counts))
    corrected = min(math.log(16.0), entropy + (occupied - 1) / (2.0 * n))
    return math.log(16.0) - corrected


def block_arrays(event: dict, run: np.ndarray, window: int) -> tuple[dict, np.ndarray]:
    pos = np.column_stack([event["x_pos"][run], event["z_pos"][run]])
    n_blocks = (len(pos) - 1) // window
    if n_blocks < 3:
        return {}, pos
    used_steps = n_blocks * window
    pos = pos[: used_steps + 1]
    steps = np.diff(pos, axis=0).reshape(n_blocks, window, 2)
    lengths = np.linalg.norm(steps, axis=2)
    path_length = lengths.sum(axis=1)
    starts = pos[np.arange(n_blocks) * window]
    ends = pos[(np.arange(n_blocks) + 1) * window]
    chord = np.linalg.norm(ends - starts, axis=1)
    directness = np.divide(
        chord, path_length, out=np.full(n_blocks, np.nan), where=path_length > 0
    )

    cross = steps[:, :-1, 0] * steps[:, 1:, 1] - steps[:, :-1, 1] * steps[:, 1:, 0]
    dot = np.sum(steps[:, :-1] * steps[:, 1:], axis=2)
    turns = np.arctan2(cross, dot)
    net_turn = turns.sum(axis=1)
    total_turn = np.abs(turns).sum(axis=1)
    turn_consistency = np.divide(
        np.abs(net_turn),
        total_turn,
        out=np.zeros(n_blocks, dtype=np.float64),
        where=total_turn > 1e-15,
    )
    circularity = (1.0 - directness) * turn_consistency

    local_sector = event["sector"][run][: used_steps + 1]
    local_speed = event["speed"][run][: used_steps + 1]
    local_time = event["time"][run][: used_steps + 1]
    tmin, tmax = float(event["time"].min()), float(event["time"].max())
    span = max(tmax - tmin, 1e-12)
    connection = np.full(n_blocks, np.nan)
    speed = np.full(n_blocks, np.nan)
    progress = np.full(n_blocks, np.nan)
    frame = np.full(n_blocks, -1, dtype=np.int64)
    for block in range(n_blocks):
        start = block * window
        stop = start + window
        connection[block] = connection_information_one(local_sector[start:stop])
        speed[block] = float(np.nanmean(local_speed[start:stop]))
        midpoint = start + window // 2
        progress[block] = (float(local_time[midpoint]) - tmin) / span
        frame[block] = int(event["frame"][run[start]])

    return {
        "directness": directness,
        "turn_consistency": turn_consistency,
        "circularity": circularity,
        "connection": connection,
        "path_length": path_length,
        "speed": speed,
        "progress": progress,
        "frame": frame,
    }, pos


def build_anchors(events: list[dict], window: int) -> tuple[pd.DataFrame, dict | None, dict]:
    rows: list[dict] = []
    best_score = -math.inf
    best_example = None
    triple_count = 0
    for event in events:
        for run_number, run in enumerate(base.contiguous_runs(event["frame"])):
            arrays, pos = block_arrays(event, run, window)
            if not arrays:
                continue
            n_blocks = len(arrays["directness"])
            for pre in range(0, n_blocks - 2, 3):
                centre, post = pre + 1, pre + 2
                triple_count += 1
                dpre, dc, dpost = (
                    arrays["directness"][pre],
                    arrays["directness"][centre],
                    arrays["directness"][post],
                )
                gc = arrays["turn_consistency"][centre]
                iconn = arrays["connection"][[pre, centre, post]]
                if not np.all(np.isfinite([dpre, dc, dpost, gc, *iconn])):
                    continue
                anchor_type = None
                if dpre >= 0.75 and dc <= 0.75 and gc >= 0.75 and dpost >= 0.75:
                    anchor_type = "circle"
                elif dpre >= 0.75 and dc <= 0.75 and gc <= 0.25 and dpost >= 0.75:
                    anchor_type = "crooked"
                if anchor_type is None:
                    continue
                progress = float(arrays["progress"][centre])
                row = {
                    "representation": REPRESENTATION,
                    "window": window,
                    "condition": event["condition"],
                    "track_id": event["track_id"],
                    "run_id": f"{event['track_id']}:{run_number}",
                    "centre_frame": int(arrays["frame"][centre]),
                    "progress": progress,
                    "progress_decile": min(int(progress * 10), 9),
                    "centre_speed": float(arrays["speed"][centre]),
                    "anchor_type": anchor_type,
                    "d_pre": float(dpre),
                    "d_centre": float(dc),
                    "d_post": float(dpost),
                    "g_pre": float(arrays["turn_consistency"][pre]),
                    "g_centre": float(gc),
                    "g_post": float(arrays["turn_consistency"][post]),
                    "c_pre": float(arrays["circularity"][pre]),
                    "c_centre": float(arrays["circularity"][centre]),
                    "c_post": float(arrays["circularity"][post]),
                    "i_pre": float(iconn[0]),
                    "i_centre": float(iconn[1]),
                    "i_post": float(iconn[2]),
                    "path_pre": float(arrays["path_length"][pre]),
                    "path_centre": float(arrays["path_length"][centre]),
                    "path_post": float(arrays["path_length"][post]),
                    "speed_pre": float(arrays["speed"][pre]),
                    "speed_centre": float(arrays["speed"][centre]),
                    "speed_post": float(arrays["speed"][post]),
                }
                row["s_build"] = row["i_centre"] - row["i_pre"]
                row["s_release"] = row["i_centre"] - row["i_post"]
                row["s_peak"] = row["i_centre"] - 0.5 * (row["i_pre"] + row["i_post"])
                row["o_in"] = row["d_pre"] - row["d_centre"]
                row["o_out"] = row["d_post"] - row["d_centre"]
                rows.append(row)

                if anchor_type == "circle" and row["c_centre"] > best_score:
                    block_start = pre * window
                    points = normalise_example(pos[block_start : block_start + 3 * window + 1])
                    best_score = row["c_centre"]
                    best_example = {
                        "condition": event["condition"],
                        "track_id": event["track_id"],
                        "run_id": row["run_id"],
                        "centre_frame": row["centre_frame"],
                        "window": window,
                        "score": best_score,
                        "points": points,
                        "ledger": {key: row[key] for key in (
                            "d_pre", "d_centre", "d_post", "i_pre", "i_centre", "i_post"
                        )},
                    }
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, best_example, {"triples": triple_count, "anchors": 0}
    frame["centre_speed_quintile"] = -1
    for condition, group in frame.groupby("condition", sort=False):
        edges = np.quantile(group["centre_speed"], [0.2, 0.4, 0.6, 0.8])
        frame.loc[group.index, "centre_speed_quintile"] = np.searchsorted(
            edges, group["centre_speed"].to_numpy(), side="right"
        )
    frame["centre_speed_quintile"] = frame["centre_speed_quintile"].astype(np.int8)
    return frame, best_example, {
        "triples": triple_count,
        "anchors": int(len(frame)),
        "circle_anchors": int((frame["anchor_type"] == "circle").sum()),
        "crooked_anchors": int((frame["anchor_type"] == "crooked").sum()),
        "tracks": int(frame["track_id"].nunique()),
    }


def bootstrap_mean(frame: pd.DataFrame, metric: str, seed: int) -> dict:
    track = frame.groupby("track_id", sort=False)[metric].mean().dropna()
    conditions = (
        frame.groupby(["condition", "track_id"], sort=False)[metric]
        .mean()
        .groupby(level=0)
        .mean()
    )
    rng = np.random.default_rng(seed)
    values = track.to_numpy(dtype=np.float64)
    boot = np.empty(BOOTSTRAPS)
    for index in range(BOOTSTRAPS):
        boot[index] = rng.choice(values, size=len(values), replace=True).mean()
    return {
        "estimate": float(values.mean()),
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
        "anchors": int(len(frame)),
        "tracks": int(len(track)),
        "condition_estimates": {str(k): float(v) for k, v in conditions.items()},
        "condition_positive": int((conditions > 0).sum()),
        "bootstraps": BOOTSTRAPS,
    }


def bootstrap_contrast(
    circle: pd.DataFrame, crooked: pd.DataFrame, metric: str, seed: int
) -> dict:
    a = circle.groupby("track_id", sort=False)[metric].mean().dropna()
    b = crooked.groupby("track_id", sort=False)[metric].mean().dropna()
    ids = np.array(sorted(set(a.index) | set(b.index)), dtype=object)
    a_map, b_map = a.to_dict(), b.to_dict()
    point = float(a.mean() - b.mean())
    rng = np.random.default_rng(seed)
    boot = np.empty(BOOTSTRAPS)
    for index in range(BOOTSTRAPS):
        sample = rng.choice(ids, size=len(ids), replace=True)
        av = [a_map[item] for item in sample if item in a_map]
        bv = [b_map[item] for item in sample if item in b_map]
        boot[index] = np.mean(av) - np.mean(bv)
    cond = {}
    for condition in base.CONDITIONS:
        ac = circle.loc[circle["condition"] == condition].groupby("track_id")[metric].mean()
        bc = crooked.loc[crooked["condition"] == condition].groupby("track_id")[metric].mean()
        cond[condition] = float(ac.mean() - bc.mean()) if len(ac) and len(bc) else math.nan
    return {
        "estimate": point,
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
        "circle_anchors": int(len(circle)),
        "crooked_anchors": int(len(crooked)),
        "tracks": int(len(ids)),
        "condition_estimates": cond,
        "condition_positive": int(sum(np.isfinite(v) and v > 0 for v in cond.values())),
        "bootstraps": BOOTSTRAPS,
    }


def corr_from_rows(frame: pd.DataFrame, x: str, y: str) -> float:
    if len(frame) < 3:
        return math.nan
    xv = frame[x].to_numpy(dtype=np.float64)
    yv = frame[y].to_numpy(dtype=np.float64)
    if np.std(xv) == 0 or np.std(yv) == 0:
        return math.nan
    return float(np.corrcoef(xv, yv)[0, 1])


def corr_from_sums(values: np.ndarray) -> float:
    n, sx, sy, sxx, syy, sxy = values
    if n < 3:
        return math.nan
    vx = sxx - sx * sx / n
    vy = syy - sy * sy / n
    if vx <= 0 or vy <= 0:
        return math.nan
    return float((sxy - sx * sy / n) / math.sqrt(vx * vy))


def bootstrap_rank_correlation(frame: pd.DataFrame, x: str, y: str, seed: int) -> dict:
    work = frame.copy()
    work["stratum"] = (
        work["condition"].astype(str)
        + ":"
        + work["progress_decile"].astype(str)
        + ":"
        + work["centre_speed_quintile"].astype(str)
    )
    eligible = work.groupby("stratum")["track_id"].transform("nunique") >= 2
    work = work.loc[eligible].copy()
    work["xr"] = work.groupby("condition")[x].rank(method="average", pct=True)
    work["yr"] = work.groupby("condition")[y].rank(method="average", pct=True)
    work["xr"] -= work.groupby("condition")["xr"].transform("mean")
    work["yr"] -= work.groupby("condition")["yr"].transform("mean")
    rho = corr_from_rows(work, "xr", "yr")

    condition_rho = {
        condition: corr_from_rows(group, "xr", "yr")
        for condition, group in work.groupby("condition", sort=False)
    }
    work = work.reset_index(drop=True)
    work["x2"] = work["xr"] * work["xr"]
    work["y2"] = work["yr"] * work["yr"]
    work["xy"] = work["xr"] * work["yr"]
    track_stats = (
        work.groupby("track_id", sort=False)
        .agg(
            n=("xr", "size"),
            sx=("xr", "sum"),
            sy=("yr", "sum"),
            sxx=("x2", "sum"),
            syy=("y2", "sum"),
            sxy=("xy", "sum"),
        )
        .to_numpy(dtype=np.float64)
    )
    rng = np.random.default_rng(seed)
    boot = np.empty(BOOTSTRAPS)
    for index in range(BOOTSTRAPS):
        sampled = rng.integers(0, len(track_stats), size=len(track_stats))
        boot[index] = corr_from_sums(track_stats[sampled].sum(axis=0))

    group_cache = []
    track_codes, _ = pd.factorize(work["track_id"], sort=False)
    for _, group in work.groupby("stratum", sort=False):
        indices = group.index.to_numpy(dtype=np.int64)
        if np.unique(track_codes[indices]).size >= 2:
            group_cache.append((indices, track_codes[indices]))
    xr = work["xr"].to_numpy(dtype=np.float64)
    yr = work["yr"].to_numpy(dtype=np.float64)
    null = np.empty(PERMUTATIONS)
    for permutation in range(PERMUTATIONS):
        donor_y = np.empty(len(work), dtype=np.float64)
        donor_y.fill(np.nan)
        for indices, local_tracks in group_cache:
            candidates = rng.integers(0, len(indices), size=len(indices))
            bad = local_tracks[candidates] == local_tracks
            while np.any(bad):
                candidates[bad] = rng.integers(0, len(indices), size=int(bad.sum()))
                bad = local_tracks[candidates] == local_tracks
            donor_y[indices] = yr[indices[candidates]]
        valid = np.isfinite(donor_y)
        null[permutation] = float(np.corrcoef(xr[valid], donor_y[valid])[0, 1])
    p = float((1 + np.sum(null >= rho)) / (PERMUTATIONS + 1))
    return {
        "estimate": rho,
        "ci_low": float(np.nanquantile(boot, 0.025)),
        "ci_high": float(np.nanquantile(boot, 0.975)),
        "anchors": int(len(work)),
        "tracks": int(work["track_id"].nunique()),
        "condition_estimates": {str(k): float(v) for k, v in condition_rho.items()},
        "condition_positive": int(sum(np.isfinite(v) and v > 0 for v in condition_rho.values())),
        "broken_null_median": float(np.nanmedian(null)),
        "broken_null_q99": float(np.nanquantile(null, 0.99)),
        "broken_p_one_sided": p,
        "bootstraps": BOOTSTRAPS,
        "permutations": PERMUTATIONS,
        "null": null,
    }


def eligible(frame: pd.DataFrame) -> tuple[bool, dict]:
    counts = {
        condition: {
            "anchors": int(len(group)),
            "tracks": int(group["track_id"].nunique()),
        }
        for condition, group in frame.groupby("condition", sort=False)
    }
    eligible_conditions = sum(
        item["anchors"] >= 30 and item["tracks"] >= 10 for item in counts.values()
    )
    status = (
        len(frame) >= 200
        and frame["track_id"].nunique() >= 30
        and eligible_conditions >= 2
    )
    return bool(status), {
        "anchors": int(len(frame)),
        "tracks": int(frame["track_id"].nunique()),
        "eligible_conditions": int(eligible_conditions),
        "by_condition": counts,
    }


def analyse(frame: pd.DataFrame, window: int) -> tuple[dict, pd.DataFrame]:
    circle = frame.loc[frame["anchor_type"] == "circle"].copy()
    crooked = frame.loc[frame["anchor_type"] == "crooked"].copy()
    circle_eligible, circle_counts = eligible(circle)
    crooked_eligible, crooked_counts = eligible(crooked)
    seed = RNG_SEED + window * 100
    build = bootstrap_mean(circle, "s_build", seed + 1) if circle_eligible else None
    release = bootstrap_mean(circle, "s_release", seed + 2) if circle_eligible else None
    peak = bootstrap_mean(circle, "s_peak", seed + 3) if circle_eligible else None
    approach = (
        bootstrap_rank_correlation(circle, "s_build", "o_in", seed + 4)
        if circle_eligible
        else None
    )
    exit_flow = (
        bootstrap_rank_correlation(circle, "s_release", "o_out", seed + 5)
        if circle_eligible
        else None
    )
    contrast = (
        bootstrap_contrast(circle, crooked, "s_peak", seed + 6)
        if circle_eligible and crooked_eligible
        else None
    )

    def positive(component: dict | None) -> bool:
        return bool(
            component
            and component["ci_low"] > 0
            and component["condition_positive"] >= 2
        )

    gate_a = bool(positive(build) and positive(release) and positive(peak))
    gate_b = bool(
        positive(approach)
        and positive(exit_flow)
        and approach["broken_p_one_sided"] <= 0.01
        and exit_flow["broken_p_one_sided"] <= 0.01
    )
    gate_c = bool(positive(contrast))

    null_rows = []
    for name, component in (("rho_in", approach), ("rho_out", exit_flow)):
        if component is not None:
            null_rows.extend(
                {"window": window, "component": name, "permutation": i, "rho": float(value)}
                for i, value in enumerate(component.pop("null"))
            )
    result = {
        "window": window,
        "eligibility": {"circle": circle_counts, "crooked": crooked_counts},
        "components": {
            "s_build": build,
            "s_release": release,
            "s_peak": peak,
            "rho_in": approach,
            "rho_out": exit_flow,
            "circle_minus_crooked_s_peak": contrast,
        },
        "gates": {"A": gate_a, "B": gate_b, "C": gate_c},
    }
    return result, pd.DataFrame(null_rows)


def bootstrap_profile(circle: pd.DataFrame, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    profile = {}
    ids = circle["track_id"].drop_duplicates().to_numpy()
    grouped = {key: group for key, group in circle.groupby("track_id", sort=False)}
    for metric, columns in {
        "D": ["d_pre", "d_centre", "d_post"],
        "I_conn": ["i_pre", "i_centre", "i_post"],
    }.items():
        track_values = np.array(
            [[group[column].mean() for column in columns] for group in grouped.values()]
        )
        boot = np.empty((1000, 3))
        for index in range(1000):
            sample = rng.integers(0, len(ids), size=len(ids))
            boot[index] = track_values[sample].mean(axis=0)
        profile[metric] = {
            "mean": track_values.mean(axis=0),
            "low": np.quantile(boot, 0.025, axis=0),
            "high": np.quantile(boot, 0.975, axis=0),
        }
    return profile


def make_figure(frame: pd.DataFrame, result: dict, example: dict | None, output: Path):
    circle = frame.loc[frame["anchor_type"] == "circle"].copy()
    profile = bootstrap_profile(circle, RNG_SEED + 999)
    fig, axes = plt.subplots(2, 3, figsize=(18, 10.5))
    phase = np.arange(3)
    labels = ["Phase A in", "B-stored", "Phase A out"]
    blue, gold, grey, red = "#4779bd", "#d89a2b", "#8793a1", "#c94f45"

    ax = axes[0, 0]
    for metric, color, marker in (("D", blue, "o"), ("I_conn", gold, "s")):
        item = profile[metric]
        ax.plot(phase, item["mean"], color=color, marker=marker, linewidth=2.5, label=metric)
        ax.fill_between(phase, item["low"], item["high"], color=color, alpha=0.18)
    ax.set_xticks(phase, labels)
    ax.set_title("Movement-defined handover profile")
    ax.set_ylabel("native coordinate")
    ax.legend(frameon=False)

    ax = axes[0, 1]
    dmean = profile["D"]["mean"]
    imean = profile["I_conn"]["mean"]
    ax.plot(dmean, imean, color=grey, linewidth=2)
    ax.scatter(dmean, imean, c=[blue, gold, blue], s=90, zorder=3)
    for i in range(2):
        ax.annotate("", xy=(dmean[i + 1], imean[i + 1]), xytext=(dmean[i], imean[i]),
                    arrowprops=dict(arrowstyle="->", color="#222", lw=1.7))
    for x, y, label in zip(dmean, imean, labels):
        ax.annotate(label, (x, y), xytext=(5, 6), textcoords="offset points", fontsize=9)
    ax.set_xlabel("Phase-A directness D")
    ax.set_ylabel("Phase-B-child proxy I_conn")
    ax.set_title("Temporal Di-ARA phase portrait")

    ax = axes[0, 2]
    sample = circle.sample(min(len(circle), 100_000), random_state=RNG_SEED % (2**32 - 1))
    hb = ax.hexbin(sample["s_release"], sample["o_out"], gridsize=45, mincnt=1, cmap="viridis")
    fig.colorbar(hb, ax=ax, label="anchor count")
    ax.axvline(0, color="#333", lw=1)
    ax.set_xlabel("connection release  I_c - I_post")
    ax.set_ylabel("next Phase-A opening  D_post - D_c")
    ax.set_title("Release/opening magnitude coupling")

    components = result["components"]
    ax = axes[1, 0]
    keys = ["s_build", "s_release", "s_peak", "circle_minus_crooked_s_peak"]
    names = ["build", "release", "peak", "peak vs crooked"]
    estimates = [components[key]["estimate"] if components[key] else np.nan for key in keys]
    lows = [components[key]["ci_low"] if components[key] else np.nan for key in keys]
    highs = [components[key]["ci_high"] if components[key] else np.nan for key in keys]
    errors = np.array([np.array(estimates) - np.array(lows), np.array(highs) - np.array(estimates)])
    ax.bar(names, estimates, color=[gold, gold, gold, grey])
    ax.errorbar(np.arange(len(keys)), estimates, yerr=errors, fmt="none", ecolor="#222", capsize=4)
    ax.axhline(0, color="#222", lw=1)
    ax.tick_params(axis="x", rotation=18)
    ax.set_ylabel("trajectory-weighted estimate (nats)")
    ax.set_title("Frozen storage components")

    ax = axes[1, 1]
    ckeys = ["rho_in", "rho_out"]
    cnames = ["approach/build", "release/open"]
    intact = [components[key]["estimate"] if components[key] else np.nan for key in ckeys]
    nulls = [components[key]["broken_null_median"] if components[key] else np.nan for key in ckeys]
    x = np.arange(2)
    ax.bar(x - 0.18, intact, width=0.36, color=blue, label="intact")
    ax.bar(x + 0.18, nulls, width=0.36, color=grey, label="broken-lineage null median")
    ax.axhline(0, color="#222", lw=1)
    ax.set_xticks(x, cnames)
    ax.set_ylabel("condition-centred rank correlation")
    ax.set_title("Magnitude coupling versus broken pairing")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 2]
    if example is not None:
        points = np.asarray(example["points"])
        for block, color in enumerate((blue, gold, blue)):
            start = block * example["window"]
            stop = (block + 1) * example["window"] + 1
            ax.plot(points[start:stop, 0], points[start:stop, 1], color=color, lw=2.3)
        ax.scatter(points[0, 0], points[0, 1], color="#222", s=35, zorder=3)
        ledger = example["ledger"]
        text = (
            f"D: {ledger['d_pre']:.3f} -> {ledger['d_centre']:.3f} -> {ledger['d_post']:.3f}\n"
            f"I: {ledger['i_pre']:.3f} -> {ledger['i_centre']:.3f} -> {ledger['i_post']:.3f}"
        )
        ax.text(0.02, 0.98, text, transform=ax.transAxes, va="top", fontsize=9,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="#bbb"))
        ax.set_aspect("equal", adjustable="datalim")
    ax.set_title("Highest-circularity eligible raw handover")
    ax.set_xlabel("normalized x")
    ax.set_ylabel("normalized z")

    fig.suptitle(
        f"T346 temporal Di-ARA storage-handover-release ({REPRESENTATION})\n"
        "anchor selected from movement only; I_conn is a connection-child proxy, not complete Phase B",
        fontsize=15,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output, dpi=190)
    plt.close(fig)


def serialise_example(example: dict | None) -> tuple[dict | None, pd.DataFrame]:
    if example is None:
        return None, pd.DataFrame()
    serial = {key: value for key, value in example.items() if key != "points"}
    serial["points"] = np.asarray(example["points"]).tolist()
    rows = []
    for index, point in enumerate(example["points"]):
        rows.append({
            "order": index,
            "block": min(index // example["window"], 2),
            "x": float(point[0]),
            "z": float(point[1]),
            **{key: value for key, value in example.items() if key not in {"points", "ledger"}},
        })
    return serial, pd.DataFrame(rows)


def flatten_summary(results: dict) -> pd.DataFrame:
    rows = []
    for window, item in results["windows"].items():
        for name, component in item["components"].items():
            if component is None:
                rows.append({"window": int(window), "component": name, "eligible": False})
                continue
            rows.append({
                "window": int(window),
                "component": name,
                "eligible": True,
                **{key: value for key, value in component.items() if key not in {"condition_estimates"}},
            })
    return pd.DataFrame(rows)


def write_report(results: dict, output: Path):
    primary = results["windows"][str(PRIMARY_W)]
    components = primary["components"]
    lines = [
        "# T346 temporal Di-ARA storage-handover-release report",
        "",
        "**Date:** 9 August 2026  ",
        f"**Representation:** {REPRESENTATION}  ",
        f"**Frozen protocol SHA-256:** `{PROTOCOL_SHA}`",
        "",
        "## Answer first",
        "",
        f"Frozen Gates A/B/C: **{'PASS' if primary['gates']['A'] else 'FAIL'} / "
        f"{'PASS' if primary['gates']['B'] else 'FAIL'} / "
        f"{'PASS' if primary['gates']['C'] else 'FAIL'}**.",
        "",
        "The anchor was selected from movement geometry alone. Connection values did not",
        "participate in identifying the recurrent centre.",
        "",
        "## Primary W=15 components",
        "",
        "| component | estimate | 95% whole-track CI | condition-positive | broken p |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, component in components.items():
        if component is None:
            lines.append(f"| {name} | ineligible | — | — | — |")
        else:
            p = component.get("broken_p_one_sided")
            p_text = "—" if p is None else f"{p:.6f}"
            lines.append(
                f"| {name} | {component['estimate']:+.6f} | "
                f"[{component['ci_low']:+.6f}, {component['ci_high']:+.6f}] | "
                f"{component['condition_positive']}/3 | {p_text} |"
            )
    lines.extend([
        "",
        "## Evidence boundary",
        "",
        "This is a frozen post-T345 mechanism test on two representations of the same",
        "controlled-weir system. It cannot establish a universal carrier/source wave,",
        "light, gravity, a universal constant or independent cross-domain replication.",
        "Failed components remain failed.",
        "",
        "## Artifacts",
        "",
        f"- `{PREFIX}_FIGURE.png`",
        f"- `{PREFIX}_SUMMARY.csv`",
        f"- `{PREFIX}_BROKEN_NULLS.csv`",
        f"- `{PREFIX}_EXAMPLE.csv`",
        f"- `{PREFIX}_RESULTS.json`",
        "- `t346_temporal_di_ara_storage_handover.py`",
    ])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    actual_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if actual_hash != PROTOCOL_SHA:
        raise RuntimeError(f"Frozen protocol hash mismatch: {actual_hash}")

    tracks, audits = [], []
    for condition in base.CONDITIONS:
        print(f"[T346:{REPRESENTATION}] loading {condition}", flush=True)
        loaded, audit = base.load_condition(condition)
        tracks.extend(loaded)
        audits.append(audit)
    print(f"[T346:{REPRESENTATION}] deriving {len(tracks):,} tracks", flush=True)
    events = [base.derive_track_events(track) for track in tracks]

    window_results, null_frames, frames = {}, [], {}
    primary_example = None
    construction = {}
    for window in WINDOWS:
        print(f"[T346:{REPRESENTATION}] building non-overlapping W={window}", flush=True)
        frame, example, counts = build_anchors(events, window)
        frames[window] = frame
        construction[str(window)] = counts
        if window == PRIMARY_W:
            primary_example = example
        print(
            f"[T346:{REPRESENTATION}] W={window}: {len(frame):,} anchors / "
            f"{frame['track_id'].nunique() if len(frame) else 0:,} tracks",
            flush=True,
        )
        result, null = analyse(frame, window)
        window_results[str(window)] = result
        null_frames.append(null)

    primary = window_results[str(PRIMARY_W)]
    primary_signs = {
        name: int(np.sign(component["estimate"])) if component else 0
        for name, component in primary["components"].items()
    }
    numerical_sign_agreement = None
    other_path = HERE / (
        "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_NUMERICAL_REPLICATION_RESULTS.json"
        if REPRESENTATION == "lab"
        else "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_RESULTS.json"
    )
    if other_path.exists():
        other = json.loads(other_path.read_text(encoding="utf-8"))
        other_primary = other["windows"][str(PRIMARY_W)]
        other_signs = {
            name: int(np.sign(component["estimate"])) if component else 0
            for name, component in other_primary["components"].items()
        }
        numerical_sign_agreement = {
            "same_all_six_signs": bool(primary_signs == other_signs),
            "same_gate_ABC": bool(primary["gates"] == other_primary["gates"]),
            "this_signs": primary_signs,
            "other_signs": other_signs,
        }

    serial_example, example_frame = serialise_example(primary_example)
    results = {
        "test": "T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER",
        "representation": REPRESENTATION,
        "status": "frozen_post_T345_mechanism_test",
        "protocol_sha256": PROTOCOL_SHA,
        "tracks": len(tracks),
        "construction": construction,
        "windows": window_results,
        "primary_gate_ABC": primary["gates"],
        "representation_transfer_if_available": numerical_sign_agreement,
        "example": serial_example,
        "source_audits": audits,
    }

    flatten_summary(results).to_csv(HERE / f"{PREFIX}_SUMMARY.csv", index=False)
    pd.concat(null_frames, ignore_index=True).to_csv(HERE / f"{PREFIX}_BROKEN_NULLS.csv", index=False)
    example_frame.to_csv(HERE / f"{PREFIX}_EXAMPLE.csv", index=False)
    (HERE / f"{PREFIX}_RESULTS.json").write_text(
        json.dumps(results, indent=2, allow_nan=False), encoding="utf-8"
    )
    make_figure(frames[PRIMARY_W], primary, primary_example, HERE / f"{PREFIX}_FIGURE.png")
    write_report(results, HERE / f"{PREFIX}_REPORT_2026-08-09.md")
    print(json.dumps({"gates": primary["gates"], "construction": construction[str(PRIMARY_W)]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
