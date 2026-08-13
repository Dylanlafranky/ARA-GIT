"""T347 frozen cross-rung return and Phase-B reconstruction test.

Primary source: numerical BAW controlled-weir trajectories already opened by
T344--T346.  This script does not physically remove a component.  Its
attenuation arm is a fixed computational reconstruction.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplcache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


os.environ["T346_REPRESENTATION"] = "num"
os.environ["T344_REPRESENTATION"] = "num"

import t344_baw_weir_irrationality_di_ara as base  # noqa: E402
import t346_temporal_di_ara_storage_handover as t346  # noqa: E402


HERE = Path(__file__).resolve().parent
PREFIX = "T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION"
PROTOCOL = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = "fecd7973e838dd0b71bdc3d099d56e46154a8212735a4c70c213420cde0c0e16"
WINDOW = 15
LAMBDAS = np.array([0.0, 0.25, 0.5, 0.75, 1.0], dtype=np.float64)
BOOTSTRAPS = 2000
PERMUTATIONS = 1000
RNG_SEED = 34720260809


def wrap(angle):
    return np.angle(np.exp(1j * np.asarray(angle)))


def direction(vector: np.ndarray) -> float:
    return float(math.atan2(vector[1], vector[0]))


def circular_mean(values: list[float] | np.ndarray) -> float:
    z = np.exp(1j * np.asarray(values, dtype=np.float64)).mean()
    return float(math.atan2(z.imag, z.real))


def interpolate_vertex(points: np.ndarray, coordinate: float) -> np.ndarray:
    left = int(math.floor(coordinate))
    fraction = coordinate - left
    return (1.0 - fraction) * points[left] + fraction * points[left + 1]


def segment_metrics(points: np.ndarray, sectors: np.ndarray) -> dict:
    steps = np.diff(points, axis=0)
    lengths = np.linalg.norm(steps, axis=1)
    path = float(lengths.sum())
    chord = float(np.linalg.norm(points[-1] - points[0]))
    directness = chord / path if path > 0 else math.nan
    if len(steps) >= 2:
        cross = steps[:-1, 0] * steps[1:, 1] - steps[:-1, 1] * steps[1:, 0]
        dot = np.sum(steps[:-1] * steps[1:], axis=1)
        net_turn = float(np.arctan2(cross, dot).sum())
    else:
        net_turn = 0.0
    return {
        "directness": directness,
        "net_turn": net_turn,
        "connection": float(t346.connection_information_one(sectors)),
        "path": path,
    }


def child_reading(points: np.ndarray, sectors: np.ndarray) -> dict:
    readings = []
    for split in (7, 8):
        first = segment_metrics(points[: split + 1], sectors[:split])
        second = segment_metrics(points[split:], sectors[split:])
        readings.append((first, second))
    first_d = float(np.mean([item[0]["directness"] for item in readings]))
    second_d = float(np.mean([item[1]["directness"] for item in readings]))
    first_i = float(np.mean([item[0]["connection"] for item in readings]))
    second_i = float(np.mean([item[1]["connection"] for item in readings]))
    first_turn = circular_mean([item[0]["net_turn"] for item in readings])
    second_turn = circular_mean([item[1]["net_turn"] for item in readings])
    return {
        "child_b_directness": first_d,
        "child_a_directness": second_d,
        "child_b_connection": first_i,
        "child_a_connection": second_i,
        "delta_i_ba": first_i - second_i,
        "delta_d_ba": second_d - first_d,
        "delta_b": first_turn,
        "wrong_child_delta": second_turn,
    }


def build_events(events: list[dict]) -> tuple[pd.DataFrame, dict, dict]:
    rows = []
    construction = {"triples": 0, "coherent": 0}
    examples = []
    for event in events:
        for run_number, run in enumerate(base.contiguous_runs(event["frame"])):
            arrays, points = t346.block_arrays(event, run, WINDOW)
            if not arrays:
                continue
            n_blocks = len(arrays["directness"])
            used_steps = n_blocks * WINDOW
            local_sector = event["sector"][run][: used_steps + 1]
            for pre in range(0, n_blocks - 2, 3):
                construction["triples"] += 1
                centre, post = pre + 1, pre + 2
                dpre, dc, dpost = (
                    arrays["directness"][pre],
                    arrays["directness"][centre],
                    arrays["directness"][post],
                )
                gc = arrays["turn_consistency"][centre]
                if not np.all(np.isfinite([dpre, dc, dpost, gc])):
                    continue
                if not (dpre >= 0.75 and dc <= 0.75 and gc >= 0.75 and dpost >= 0.75):
                    continue
                construction["coherent"] += 1

                pre_start = pre * WINDOW
                centre_start = centre * WINDOW
                centre_end = centre_start + WINDOW
                post_start = post * WINDOW
                pre_mid = interpolate_vertex(points, pre_start + 7.5)
                post_mid = interpolate_vertex(points, post_start + 7.5)
                u_in = points[centre_start] - pre_mid
                u_out = post_mid - points[centre_end]
                if np.linalg.norm(u_in) <= 1e-15 or np.linalg.norm(u_out) <= 1e-15:
                    continue
                theta_in, theta_out = direction(u_in), direction(u_out)
                theta_parent = circular_mean([theta_in, theta_out])
                centre_points = points[centre_start : centre_end + 1]
                centre_steps = np.diff(centre_points, axis=0)
                step_lengths = np.linalg.norm(centre_steps, axis=1)
                valid = step_lengths > 1e-15
                if valid.sum() < 2:
                    continue
                step_angles = np.arctan2(centre_steps[valid, 1], centre_steps[valid, 0])
                roughness = float(np.mean(np.abs(wrap(step_angles - theta_parent))))
                parent_turn = float(abs(wrap(theta_out - theta_in)))
                smoothing = roughness - parent_turn
                centre_path = float(step_lengths.sum())
                normal = np.array([-math.sin(theta_parent), math.cos(theta_parent)])
                perpendicular = np.abs((centre_points - centre_points[0]) @ normal)
                maximum_departure = float(perpendicular.max() / centre_path) if centre_path else math.nan
                centre_chord_angle = direction(centre_points[-1] - centre_points[0])
                chord_alignment = float(math.cos(centre_chord_angle - theta_parent))

                child = child_reading(
                    centre_points,
                    local_sector[centre_start:centre_end],
                )
                progress = float(arrays["progress"][centre])
                row = {
                    "condition": event["condition"],
                    "track_id": event["track_id"],
                    "run_id": f"{event['track_id']}:{run_number}",
                    "centre_frame": int(arrays["frame"][centre]),
                    "progress": progress,
                    "progress_decile": min(int(progress * 10), 9),
                    "centre_speed": float(arrays["speed"][centre]),
                    "d_pre": float(dpre),
                    "d_centre": float(dc),
                    "d_post": float(dpost),
                    "g_centre": float(gc),
                    "theta_in": theta_in,
                    "theta_out": theta_out,
                    "theta_parent": theta_parent,
                    "parent_persistence": float(math.cos(theta_out - theta_in)),
                    "centre_roughness": roughness,
                    "parent_turn": parent_turn,
                    "smoothing_score": smoothing,
                    "max_perpendicular_departure": maximum_departure,
                    "centre_chord_alignment": chord_alignment,
                    **child,
                }
                rows.append(row)
                examples.append((smoothing, row.copy(), points[pre_start : post_start + WINDOW + 1].copy()))

    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("No T347 coherent anchors were recovered")
    frame["centre_speed_quintile"] = -1
    for condition, group in frame.groupby("condition", sort=False):
        edges = np.quantile(group["centre_speed"], [0.2, 0.4, 0.6, 0.8])
        frame.loc[group.index, "centre_speed_quintile"] = np.searchsorted(
            edges, group["centre_speed"].to_numpy(), side="right"
        )
    frame["centre_speed_quintile"] = frame["centre_speed_quintile"].astype(np.int8)
    frame["stratum"] = (
        frame["condition"].astype(str)
        + ":" + frame["progress_decile"].astype(str)
        + ":" + frame["centre_speed_quintile"].astype(str)
    )
    eligible = frame.groupby("stratum")["track_id"].transform("nunique") >= 2
    frame = frame.loc[eligible].reset_index(drop=True)
    examples.sort(key=lambda item: item[0], reverse=True)
    best = examples[0]
    example = {"row": best[1], "points": best[2]}
    construction.update({
        "eligible_anchors": int(len(frame)),
        "tracks": int(frame["track_id"].nunique()),
        "conditions": {str(k): int(v) for k, v in frame.groupby("condition").size().items()},
    })
    return frame, example, construction


def track_bootstrap(frame: pd.DataFrame, metric: str, seed: int) -> tuple[dict, np.ndarray]:
    track = frame.groupby("track_id", sort=False)[metric].mean().dropna()
    values = track.to_numpy(dtype=np.float64)
    rng = np.random.default_rng(seed)
    boot = np.empty(BOOTSTRAPS)
    for index in range(BOOTSTRAPS):
        boot[index] = rng.choice(values, len(values), replace=True).mean()
    condition = frame.groupby(["condition", "track_id"])[metric].mean().groupby(level=0).mean()
    return {
        "estimate": float(values.mean()),
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
        "condition_estimates": {str(k): float(v) for k, v in condition.items()},
        "condition_positive": int((condition > 0).sum()),
        "tracks": int(len(values)),
        "anchors": int(len(frame)),
    }, boot


def donor_indices(frame: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    donors = np.full(len(frame), -1, dtype=np.int64)
    tracks = frame["track_id"].to_numpy()
    for _, group in frame.groupby("stratum", sort=False):
        idx = group.index.to_numpy(dtype=np.int64)
        local_tracks = tracks[idx]
        choices = rng.integers(0, len(idx), len(idx))
        bad = local_tracks[choices] == local_tracks
        while np.any(bad):
            choices[bad] = rng.integers(0, len(idx), int(bad.sum()))
            bad = local_tracks[choices] == local_tracks
        donors[idx] = idx[choices]
    if np.any(donors < 0):
        raise RuntimeError("Unassigned matched donor")
    return donors


def track_mean_array(frame: pd.DataFrame, values: np.ndarray) -> float:
    work = pd.DataFrame({"track_id": frame["track_id"].to_numpy(), "value": values})
    return float(work.groupby("track_id", sort=False)["value"].mean().mean())


def matched_nulls(frame: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED + 5000)
    theta_in = frame["theta_in"].to_numpy()
    theta_out = frame["theta_out"].to_numpy()
    delta_b = frame["delta_b"].to_numpy()
    rows = []
    for permutation in range(PERMUTATIONS):
        donor = donor_indices(frame, rng)
        persistence = track_mean_array(frame, np.cos(theta_out[donor] - theta_in))
        donor_delta = delta_b[donor]
        loss = np.array([
            track_mean_array(frame, 1.0 - np.cos(theta_out - (theta_in + lam * donor_delta)))
            for lam in LAMBDAS
        ])
        rev_loss = np.array([
            track_mean_array(frame, 1.0 - np.cos(theta_out - (theta_in - lam * donor_delta)))
            for lam in LAMBDAS
        ])
        improvement = loss[0] - loss
        rev_improvement = rev_loss[0] - rev_loss
        row = {
            "permutation": permutation,
            "wrong_lineage_persistence": persistence,
            "max_steering_improvement": float(improvement[1:].max()),
            "max_reverse_improvement": float(rev_improvement[1:].max()),
        }
        for index, lam in enumerate(LAMBDAS):
            row[f"loss_lambda_{lam:g}"] = float(loss[index])
            row[f"reverse_loss_lambda_{lam:g}"] = float(rev_loss[index])
        rows.append(row)
    return pd.DataFrame(rows)


def loss_curve(frame: pd.DataFrame, delta_column: str, sign: float, seed: int) -> tuple[pd.DataFrame, dict]:
    theta_in = frame["theta_in"].to_numpy()
    theta_out = frame["theta_out"].to_numpy()
    delta = sign * frame[delta_column].to_numpy()
    work = pd.DataFrame({"track_id": frame["track_id"]})
    for lam in LAMBDAS:
        work[f"loss_{lam:g}"] = 1.0 - np.cos(theta_out - (theta_in + lam * delta))
    by_track = work.groupby("track_id", sort=False).mean()
    rng = np.random.default_rng(seed)
    sample = rng.integers(0, len(by_track), size=(BOOTSTRAPS, len(by_track)))
    boot_loss = np.empty((BOOTSTRAPS, len(LAMBDAS)))
    values = by_track.to_numpy()
    for index in range(BOOTSTRAPS):
        boot_loss[index] = values[sample[index]].mean(axis=0)
    mean_loss = values.mean(axis=0)
    improvement = boot_loss[:, [0]] - boot_loss
    rows = []
    for index, lam in enumerate(LAMBDAS):
        rows.append({
            "lambda": float(lam),
            "loss": float(mean_loss[index]),
            "loss_ci_low": float(np.quantile(boot_loss[:, index], 0.025)),
            "loss_ci_high": float(np.quantile(boot_loss[:, index], 0.975)),
            "improvement_vs_zero": float(mean_loss[0] - mean_loss[index]),
            "improvement_ci_low": float(np.quantile(improvement[:, index], 0.025)),
            "improvement_ci_high": float(np.quantile(improvement[:, index], 0.975)),
        })
    best_positive = int(1 + np.argmax((mean_loss[0] - mean_loss)[1:]))
    return pd.DataFrame(rows), {
        "best_lambda": float(LAMBDAS[best_positive]),
        "best_loss": float(mean_loss[best_positive]),
        "zero_loss": float(mean_loss[0]),
        "best_improvement": float(mean_loss[0] - mean_loss[best_positive]),
        "best_improvement_ci_low": float(np.quantile(improvement[:, best_positive], 0.025)),
        "best_improvement_ci_high": float(np.quantile(improvement[:, best_positive], 0.975)),
        "zero_is_minimum": bool(int(np.argmin(mean_loss)) == 0),
    }


def analyse(frame: pd.DataFrame) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    components = {}
    bootstrap_rows = []
    for offset, metric in enumerate((
        "parent_persistence", "smoothing_score", "delta_i_ba", "delta_d_ba",
        "max_perpendicular_departure", "centre_chord_alignment",
    )):
        component, boot = track_bootstrap(frame, metric, RNG_SEED + offset)
        components[metric] = component
        bootstrap_rows.extend(
            {"metric": metric, "replicate": index, "estimate": float(value)}
            for index, value in enumerate(boot)
        )

    nulls = matched_nulls(frame)
    persistence = components["parent_persistence"]
    persistence["wrong_lineage_null_median"] = float(nulls["wrong_lineage_persistence"].median())
    persistence["wrong_lineage_null_q99"] = float(nulls["wrong_lineage_persistence"].quantile(0.99))
    persistence["wrong_lineage_p"] = float(
        (1 + (nulls["wrong_lineage_persistence"] >= persistence["estimate"]).sum())
        / (PERMUTATIONS + 1)
    )

    intact_curve, intact = loss_curve(frame, "delta_b", +1.0, RNG_SEED + 100)
    intact_curve["model"] = "intact B"
    reverse_curve, reverse = loss_curve(frame, "delta_b", -1.0, RNG_SEED + 101)
    reverse_curve["model"] = "reversed B"
    wrong_curve, wrong = loss_curve(frame, "wrong_child_delta", +1.0, RNG_SEED + 102)
    wrong_curve["model"] = "wrong child"
    curves = pd.concat([intact_curve, reverse_curve, wrong_curve], ignore_index=True)

    intact["matched_null_p"] = float(
        (1 + (nulls["max_steering_improvement"] >= intact["best_improvement"]).sum())
        / (PERMUTATIONS + 1)
    )
    reverse["matched_null_p"] = float(
        (1 + (nulls["max_reverse_improvement"] >= reverse["best_improvement"]).sum())
        / (PERMUTATIONS + 1)
    )
    gate_a = bool(
        persistence["ci_low"] > 0
        and persistence["condition_positive"] >= 2
        and persistence["wrong_lineage_p"] <= 0.01
    )
    smooth = components["smoothing_score"]
    gate_b = bool(smooth["ci_low"] > 0 and smooth["condition_positive"] >= 2)
    di, dd = components["delta_i_ba"], components["delta_d_ba"]
    gate_c = bool(
        di["ci_low"] > 0 and di["condition_positive"] >= 2
        and dd["ci_low"] > 0 and dd["condition_positive"] >= 2
    )
    steering = bool(
        intact["best_improvement_ci_low"] > 0 and intact["matched_null_p"] <= 0.01
    )
    counter = bool(
        reverse["best_improvement_ci_low"] > 0 and reverse["matched_null_p"] <= 0.01
    )
    if intact["zero_is_minimum"] and gate_a:
        classification = "Phase A maintains direction"
    elif steering and not counter:
        classification = "Phase B steers"
    elif counter and not steering:
        classification = "Phase B counter-steers/stabilizes"
    else:
        classification = "unresolved"
    result = {
        "components": components,
        "gates": {"A_parent_direction": gate_a, "B_scale_up_smoothing": gate_b, "C_child_handover": gate_c},
        "all_three_gates": bool(gate_a and gate_b and gate_c),
        "ablation": {"classification": classification, "intact": intact, "reversed": reverse, "wrong_child": wrong},
    }
    return result, curves, nulls, pd.DataFrame(bootstrap_rows)


def make_figure(frame: pd.DataFrame, example: dict, result: dict, curves: pd.DataFrame, nulls: pd.DataFrame, output: Path):
    blue, gold, green, grey, red = "#4779bd", "#d89a2b", "#4c9b72", "#9aa5b1", "#c9534b"
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 11))

    ax = axes[0, 0]
    pts = example["points"]
    for start, stop, color, label in ((0, 16, blue, "adult A in"), (15, 31, gold, "W15 handover"), (30, 46, green, "adult A out")):
        ax.plot(pts[start:stop, 0], pts[start:stop, 1], color=color, lw=2.3, label=label)
    pre_mid = interpolate_vertex(pts, 7.5)
    post_mid = interpolate_vertex(pts, 37.5)
    ax.plot([pre_mid[0], pts[15, 0]], [pre_mid[1], pts[15, 1]], color="#222", lw=3, alpha=.7)
    ax.plot([pts[30, 0], post_mid[0]], [pts[30, 1], post_mid[1]], color="#222", lw=3, alpha=.7, label="W30 outer direction")
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_title("Example: parent view around the W15 handover")
    ax.set_xlabel("numerical x (m)")
    ax.set_ylabel("numerical z (m)")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0, 1]
    metrics = ["parent_persistence", "smoothing_score", "delta_i_ba", "delta_d_ba"]
    labels = ["parent\npersistence", "scale-up\nsmoothing", "child ΔI\n(B−A)", "child ΔD\n(A−B)"]
    comps = result["components"]
    estimates = np.array([comps[item]["estimate"] for item in metrics])
    low = np.array([comps[item]["ci_low"] for item in metrics])
    high = np.array([comps[item]["ci_high"] for item in metrics])
    ax.bar(np.arange(4), estimates, color=[blue, green, gold, gold])
    ax.errorbar(np.arange(4), estimates, yerr=np.vstack([estimates-low, high-estimates]), fmt="none", ecolor="#222", capsize=4)
    ax.axhline(0, color="#222", lw=1)
    ax.set_xticks(np.arange(4), labels)
    ax.set_title("Frozen effects with 95% whole-track intervals")

    ax = axes[1, 0]
    styles = {"intact B": (blue, "o"), "reversed B": (red, "s"), "wrong child": (grey, "^")}
    for name, group in curves.groupby("model", sort=False):
        color, marker = styles[name]
        ax.plot(group["lambda"], group["loss"], color=color, marker=marker, lw=2.2, label=name)
        ax.fill_between(group["lambda"], group["loss_ci_low"], group["loss_ci_high"], color=color, alpha=.13)
    null_mean = np.array([nulls[f"loss_lambda_{lam:g}"].mean() for lam in LAMBDAS])
    null_low = np.array([nulls[f"loss_lambda_{lam:g}"].quantile(.025) for lam in LAMBDAS])
    null_high = np.array([nulls[f"loss_lambda_{lam:g}"].quantile(.975) for lam in LAMBDAS])
    ax.plot(LAMBDAS, null_mean, color="#333", ls="--", lw=1.8, label="matched wrong-lineage B")
    ax.fill_between(LAMBDAS, null_low, null_high, color="#333", alpha=.08)
    ax.set_xlabel("retained Phase-B contribution λ")
    ax.set_ylabel("directional loss 1 − cos(error)")
    ax.set_title("Frozen graded Phase-B reconstruction")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    sample = frame.sample(min(len(frame), 40_000), random_state=347)
    hb = ax.hexbin(sample["smoothing_score"], sample["delta_i_ba"], gridsize=42, mincnt=1, cmap="viridis")
    fig.colorbar(hb, ax=ax, label="handover anchors")
    ax.axvline(0, color="#ddd", lw=1)
    ax.axhline(0, color="#ddd", lw=1)
    ax.set_xlabel("scale-up smoothing score")
    ax.set_ylabel("child ordered-information contrast ΔI")
    ax.set_title("Where parent smoothing and child return coexist")

    gate_text = " · ".join(f"{key[0]}={'PASS' if value else 'FAIL'}" for key, value in result["gates"].items())
    fig.suptitle(
        "T347 cross-rung return and Phase-B reconstruction\n"
        f"{len(frame):,} numerical handovers · {frame['track_id'].nunique():,} tracks · {gate_text}",
        fontsize=15,
    )
    fig.tight_layout(rect=[0, 0, 1, .94])
    fig.savefig(output, dpi=190)
    plt.close(fig)


def write_report(results: dict, output: Path):
    r = results["analysis"]
    c = r["components"]
    lines = [
        "# T347 cross-rung return and Phase-B ablation report",
        "",
        "**Date:** 9 August 2026  ",
        f"**Frozen protocol SHA-256:** `{PROTOCOL_SHA}`  ",
        "**Evidence boundary:** numerical BAW representation already used in T344–T346; not independent confirmation.",
        "",
        "## Answer first",
        "",
        f"Frozen Gates A/B/C: **{'PASS' if r['gates']['A_parent_direction'] else 'FAIL'} / {'PASS' if r['gates']['B_scale_up_smoothing'] else 'FAIL'} / {'PASS' if r['gates']['C_child_handover'] else 'FAIL'}**.",
        f"The frozen Phase-B reconstruction classification is **{r['ablation']['classification']}**.",
        "",
        "## Frozen components",
        "",
        "| component | estimate | 95% whole-track CI | positive conditions |",
        "|---|---:|---:|---:|",
    ]
    for name in ("parent_persistence", "smoothing_score", "delta_i_ba", "delta_d_ba", "max_perpendicular_departure", "centre_chord_alignment"):
        item = c[name]
        lines.append(f"| {name} | {item['estimate']:+.6f} | [{item['ci_low']:+.6f}, {item['ci_high']:+.6f}] | {item['condition_positive']}/3 |")
    p = c["parent_persistence"]
    lines.extend([
        "",
        f"The parent-persistence matched wrong-lineage test gave `p={p['wrong_lineage_p']:.6f}` (null median `{p['wrong_lineage_null_median']:+.6f}`).",
        "",
        "## Graded reconstruction",
        "",
        "| model | best lambda | improvement vs lambda=0 | 95% CI | matched-null p |",
        "|---|---:|---:|---:|---:|",
    ])
    for key in ("intact", "reversed", "wrong_child"):
        item = r["ablation"][key]
        p_text = "—" if "matched_null_p" not in item else f"{item['matched_null_p']:.6f}"
        lines.append(f"| {key} | {item['best_lambda']:.2f} | {item['best_improvement']:+.6f} | [{item['best_improvement_ci_low']:+.6f}, {item['best_improvement_ci_high']:+.6f}] | {p_text} |")
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "The attenuation arm changes a reconstructed angular contribution while holding the observed event fixed. It does not physically remove Phase B. The result tests this operational decomposition only; it cannot establish a universal carrier, energy flow or universal ARA geometry.",
        "",
        "## Reproduction artifacts",
        "",
        f"- `{PREFIX}_FIGURE.png`",
        f"- `{PREFIX}_EVENTS.csv`",
        f"- `{PREFIX}_ABLATION_CURVES.csv`",
        f"- `{PREFIX}_MATCHED_NULLS.csv`",
        f"- `{PREFIX}_BOOTSTRAPS.csv`",
        f"- `{PREFIX}_RESULTS.json`",
        "- `t347_cross_rung_return_phase_b_ablation.py`",
    ])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def serialise(value):
    if isinstance(value, dict):
        return {str(k): serialise(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialise(v) for v in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def main():
    actual_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if actual_hash != PROTOCOL_SHA:
        raise RuntimeError(f"Frozen protocol hash mismatch: {actual_hash}")

    tracks, audits = [], []
    for condition in base.CONDITIONS:
        print(f"[T347] loading numerical {condition}", flush=True)
        loaded, audit = base.load_condition(condition)
        tracks.extend(loaded)
        audits.append(audit)
    print(f"[T347] deriving {len(tracks):,} tracks", flush=True)
    derived = [base.derive_track_events(track) for track in tracks]
    print("[T347] constructing frozen W15 handovers", flush=True)
    frame, example, construction = build_events(derived)
    print(f"[T347] scoring {len(frame):,} anchors across {frame['track_id'].nunique():,} tracks", flush=True)
    analysis, curves, nulls, bootstraps = analyse(frame)

    results = {
        "test": PREFIX,
        "status": "frozen_post_T346_mechanism_test",
        "protocol_sha256": PROTOCOL_SHA,
        "representation": "numerical",
        "construction": construction,
        "analysis": analysis,
        "source_audits": audits,
    }
    results = serialise(results)
    frame.to_csv(HERE / f"{PREFIX}_EVENTS.csv", index=False)
    curves.to_csv(HERE / f"{PREFIX}_ABLATION_CURVES.csv", index=False)
    nulls.to_csv(HERE / f"{PREFIX}_MATCHED_NULLS.csv", index=False)
    bootstraps.to_csv(HERE / f"{PREFIX}_BOOTSTRAPS.csv", index=False)
    (HERE / f"{PREFIX}_RESULTS.json").write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    make_figure(frame, example, analysis, curves, nulls, HERE / f"{PREFIX}_FIGURE.png")
    write_report(results, HERE / f"{PREFIX}_REPORT_2026-08-09.md")
    print(json.dumps({"construction": construction, "gates": analysis["gates"], "ablation": analysis["ablation"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
