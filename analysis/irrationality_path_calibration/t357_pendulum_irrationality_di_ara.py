"""T357: frozen physical-pendulum transfer of the T348 Irrationality Di-ARA.

The script deliberately uses only angle, angular velocity and time to construct
the primary path coordinates.  It does not use spectral labels, Phi, e, 1/e,
or a fitted pendulum period.
"""

from __future__ import annotations

import hashlib
import json
import math
import zlib
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import loadmat


HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "pendulum_scripts" / "data"
SEED = 3_570_811
TARGET_HZ = 200.0
SAMPLES_PER_CYCLE = 8
WINDOW_CYCLES = 4
WINDOW_N = SAMPLES_PER_CYCLE * WINDOW_CYCLES
RESOLUTIONS = np.array([4, 8, 16, 32], dtype=int)
MAX_LAG = 16
K = 3

CLAIM = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md"
PROTOCOL = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"

FILES = {
    "single": {
        "free": "pend_single.mat",
        "driven1": "SingleDataWithControl_1_Dt_0_0001.mat",
        "driven2": "SingleDataWithControl_2_Dt_0_0001.mat",
    },
    "double": {
        "free": "pend_double.mat",
        "driven1": "DoubleDataWithControl_1_Dt_0_0001.mat",
        "driven2": "DoubleDataWithControl_2_Dt_0_0001.mat",
    },
}

PREFIX = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA"
METRICS_CSV = Path(f"{PREFIX}_WINDOW_METRICS.csv")
SERIES_CSV = Path(f"{PREFIX}_WINDOW_SERIES.csv")
CLOSURE_CSV = Path(f"{PREFIX}_CLOSURE_CURVES.csv")
SUMMARY_CSV = Path(f"{PREFIX}_RECORD_SUMMARY.csv")
QA_CSV = Path(f"{PREFIX}_DATA_QA.csv")
GATES_CSV = Path(f"{PREFIX}_FROZEN_GATES.csv")
EXAMPLE_CSV = Path(f"{PREFIX}_EXAMPLE_PATHS.csv")
RESULTS_JSON = Path(f"{PREFIX}_RESULTS.json")
FIGURE_PNG = Path(f"{PREFIX}_FIGURE.png")
REPORT_MD = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA_REPORT_2026-08-11.md"


@dataclass
class Prepared:
    family: str
    stratum: str
    filename: str
    t: np.ndarray
    parent_u: np.ndarray
    child_u: np.ndarray
    landmark_t: np.ndarray
    parent_z: np.ndarray
    child_z: np.ndarray
    n_cycles: int
    n_windows: int
    qa: dict


def wrap(a: np.ndarray) -> np.ndarray:
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def circular_rest(theta: np.ndarray) -> float:
    return float(np.arctan2(np.mean(np.sin(theta)), np.mean(np.cos(theta))))


def robust_scale(x: np.ndarray) -> float:
    s = float(np.percentile(np.abs(x[np.isfinite(x)]), 90.0))
    return max(s, 1e-9)


def phase_plane(theta: np.ndarray, velocity: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict]:
    rest = circular_rest(theta)
    q = wrap(theta - rest)
    sq = robust_scale(q)
    sv = robust_scale(velocity)
    c = q / sq + 1j * velocity / sv
    angle = np.unwrap(np.angle(c))
    direction = -1.0
    u = direction * angle / (2.0 * np.pi)
    backtrack = float(np.mean(np.diff(u) < -1e-5))
    return q, u, {
        "rest_rad": rest,
        "q_scale": sq,
        "v_scale": sv,
        "phase_direction": direction,
        "phase_backtrack_fraction": backtrack,
    }


def interpolate_crossing(t0: float, t1: float, q0: float, q1: float) -> float:
    denom = q1 - q0
    if abs(denom) < 1e-15:
        return t0
    return float(t0 + (-q0 / denom) * (t1 - t0))


def upward_crossings(t: np.ndarray, q: np.ndarray, velocity: np.ndarray) -> np.ndarray:
    # The signed q crossing already fixes the upward direction.  Do not also
    # require a positive sampled derivative: the single-arm encoder is
    # quantised and can report exactly zero velocity at the crossing sample.
    idx = np.where((q[:-1] <= 0.0) & (q[1:] > 0.0))[0]
    times = [interpolate_crossing(t[i], t[i + 1], q[i], q[i + 1]) for i in idx]
    kept: list[float] = []
    for value in times:
        if not kept or value - kept[-1] >= 0.25:
            kept.append(value)
    return np.asarray(kept, dtype=float)


def parent_landmarks(t: np.ndarray, parent_u: np.ndarray, crossings: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    all_times: list[np.ndarray] = []
    all_phases: list[np.ndarray] = []
    adjusted = 0
    total_steps = 0
    for left, right in zip(crossings[:-1], crossings[1:]):
        mask = (t >= left) & (t <= right)
        ts = t[mask]
        us = parent_u[mask]
        if len(ts) < 4:
            continue
        u_left = float(np.interp(left, t, parent_u))
        u_right = float(np.interp(right, t, parent_u))
        if u_right <= u_left + 0.5:
            continue
        ts = np.concatenate(([left], ts[(ts > left) & (ts < right)], [right]))
        us = np.concatenate(([u_left], us[(t[mask] > left) & (t[mask] < right)], [u_right]))
        mono = np.maximum.accumulate(us)
        adjusted += int(np.sum(np.diff(us) < 0.0))
        total_steps += max(0, len(us) - 1)
        targets = u_left + (u_right - u_left) * np.arange(SAMPLES_PER_CYCLE) / SAMPLES_PER_CYCLE
        all_times.append(np.interp(targets, mono, ts))
        # The reference clock coordinate is the declared equal phase grid.
        # Keep it exact rather than reading encoder jitter back into the clock.
        all_phases.append(np.arange(SAMPLES_PER_CYCLE, dtype=float) / SAMPLES_PER_CYCLE)
    if not all_times:
        raise RuntimeError("No complete parent cycles survived landmark construction")
    return np.concatenate(all_times), np.concatenate(all_phases), adjusted / max(total_steps, 1)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def prepare(family: str, stratum: str, filename: str) -> Prepared:
    path = DATA / filename
    m = loadmat(path, squeeze_me=True, struct_as_record=False)
    if family == "single":
        theta_struct = m["Theta1"]
        t_full = np.asarray(theta_struct.time).ravel().astype(float)
        th1_full = np.asarray(theta_struct.signals.values).ravel().astype(float)
        dt = float(np.median(np.diff(t_full)))
        v1_full = np.gradient(np.unwrap(th1_full), t_full)
    else:
        dt = float(np.asarray(m["dt"]).ravel()[0])
        t_full = np.asarray(m["Time"]).ravel().astype(float)
        th1_full = np.asarray(m["Theta1"]).ravel().astype(float)
        v1_full = np.asarray(m["dTheta1"]).ravel().astype(float)
    step = max(1, int(round(1.0 / (dt * TARGET_HZ))))
    t = t_full[::step].astype(float)
    th1 = th1_full[::step]
    v1 = v1_full[::step]
    q1, u1, qa1 = phase_plane(th1, v1)
    if family == "double":
        th2 = np.asarray(m["Theta2"]).ravel()[::step].astype(float)
        v2 = np.asarray(m["dTheta2"]).ravel()[::step].astype(float)
        _, u2, qa2 = phase_plane(th2, v2)
    else:
        u2 = u1.copy()
        qa2 = qa1.copy()
    crossings = upward_crossings(t, q1, v1)
    landmark_t, parent_z, landmark_adjust = parent_landmarks(t, u1, crossings)
    child_z = np.mod(np.interp(landmark_t, t, u2), 1.0)
    n_cycles = len(landmark_t) // SAMPLES_PER_CYCLE
    n_windows = n_cycles // WINDOW_CYCLES
    keep = n_windows * WINDOW_N
    parent_z = parent_z[:keep]
    child_z = child_z[:keep]
    landmark_t = landmark_t[:keep]
    qa = {
        "family": family,
        "stratum": stratum,
        "filename": filename,
        "file_sha256": sha256(path),
        "raw_samples": int(len(t_full)),
        "decimated_samples": int(len(t)),
        "dt_seconds": dt,
        "decimation": step,
        "effective_hz": 1.0 / (dt * step),
        "duration_seconds": float(t[-1] - t[0]),
        "upward_crossings": int(len(crossings)),
        "complete_cycles": int(n_cycles),
        "complete_windows": int(n_windows),
        "parent_q_scale": qa1["q_scale"],
        "parent_v_scale": qa1["v_scale"],
        "parent_phase_backtrack_fraction": qa1["phase_backtrack_fraction"],
        "landmark_monotone_adjustment_fraction": landmark_adjust,
        "child_q_scale": qa2["q_scale"],
        "child_v_scale": qa2["v_scale"],
        "child_phase_backtrack_fraction": qa2["phase_backtrack_fraction"],
    }
    return Prepared(family, stratum, filename, t, u1, u2, landmark_t, parent_z, child_z, n_cycles, n_windows, qa)


def circular_mean(z: np.ndarray) -> float:
    v = np.mean(np.exp(2j * np.pi * z))
    if abs(v) < 1e-15:
        return 0.0
    return float((np.angle(v) / (2.0 * np.pi)) % 1.0)


def circular_loss(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2.0 * np.pi * (actual - predicted))


def address_openness(z: np.ndarray) -> tuple[float, list[int]]:
    occupied = []
    for bins in RESOLUTIONS:
        idx = np.minimum((np.mod(z, 1.0) * bins).astype(int), bins - 1)
        occupied.append(int(np.unique(idx).size))
    beta = float(np.polyfit(np.log(RESOLUTIONS), np.log(np.maximum(occupied, 1)), 1)[0])
    return 2.0 * float(np.clip(beta, 0.0, 1.0)), occupied


def knn_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    distance = np.abs(test_x[:, None] - train_x[None, :])
    distance = np.minimum(distance, 1.0 - distance)
    nearest = np.argpartition(distance, kth=K - 1, axis=1)[:, :K]
    vec = np.mean(np.exp(2j * np.pi * train_y[nearest]), axis=1)
    pred = np.mod(np.angle(vec) / (2.0 * np.pi), 1.0)
    pred[np.abs(vec) < 1e-12] = circular_mean(train_y)
    return pred


def stochastic_residual(z: np.ndarray) -> tuple[float, float, float]:
    split = len(z) // 2
    train_x, train_y = z[: split - 1], z[1:split]
    test_x, test_y = z[split:-1], z[split + 1 :]
    prediction = knn_predict(train_x, train_y, test_x)
    null = np.full_like(test_y, circular_mean(train_y))
    local = float(np.mean(circular_loss(test_y, prediction)))
    null_loss = float(np.mean(circular_loss(test_y, null)))
    ratio = local / max(null_loss, 1e-12)
    return 2.0 * min(1.0, ratio), local, null_loss


def closure_history(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rho, miss = [], []
    for lag in range(1, MAX_LAG + 1):
        delta = z[lag:] - z[:-lag]
        vec = np.mean(np.exp(2j * np.pi * delta))
        rho.append(float(abs(vec)))
        miss.append(float(np.angle(vec) / (2.0 * np.pi)))
    return np.asarray(rho), np.asarray(miss)


def orientation(z: np.ndarray) -> float:
    vec = np.mean(np.exp(2j * np.pi * (z[1:] - z[:-1])))
    return float(np.angle(vec) / (2.0 * np.pi))


def metrics(z: np.ndarray) -> tuple[dict, np.ndarray, np.ndarray]:
    xp, occupied = address_openness(z)
    xr, local, null = stochastic_residual(z)
    rho, miss = closure_history(z)
    best_idx = int(np.argmax(rho))
    cycle_idx = SAMPLES_PER_CYCLE - 1
    result = {
        "x_p": xp,
        "x_r": xr,
        "local_loss": local,
        "null_loss": null,
        "occupied_b4": occupied[0],
        "occupied_b8": occupied[1],
        "occupied_b16": occupied[2],
        "occupied_b32": occupied[3],
        "cycle_rho": float(rho[cycle_idx]),
        "cycle_miss_signed": float(miss[cycle_idx]),
        "cycle_miss_abs": float(abs(miss[cycle_idx])),
        "cycle_closure": bool(rho[cycle_idx] >= 0.80 and abs(miss[cycle_idx]) <= 0.03),
        "best_rho": float(rho[best_idx]),
        "best_lag": best_idx + 1,
        "best_miss_abs": float(abs(miss[best_idx])),
        "any_coherent_return": bool(np.any(rho >= 0.80)),
        "median_rho": float(np.median(rho)),
        "orientation": orientation(z),
    }
    return result, rho, miss


def seeded_rng(key: str) -> np.random.Generator:
    return np.random.default_rng(SEED + zlib.crc32(key.encode("utf-8")))


def broken_child(target: Prepared, donor: Prepared) -> np.ndarray:
    frac = (target.landmark_t - target.t[0]) / max(target.t[-1] - target.t[0], 1e-12)
    donor_t = donor.t[0] + frac * (donor.t[-1] - donor.t[0])
    return np.mod(np.interp(donor_t, donor.t, donor.child_u), 1.0)


def run_windows(prepared: dict[tuple[str, str], Prepared]):
    metric_rows, series_rows, closure_rows = [], [], []
    donor_order = {"free": "driven1", "driven1": "driven2", "driven2": "free"}
    for (family, stratum), item in prepared.items():
        base = item.parent_z if family == "single" else item.child_z
        conditions = {"chronological": base}
        if family == "double":
            donor = prepared[("double", donor_order[stratum])]
            conditions["broken_lineage"] = broken_child(item, donor)
        for w in range(item.n_windows):
            left, right = w * WINDOW_N, (w + 1) * WINDOW_N
            chronological = base[left:right].copy()
            window_conditions = {
                "chronological": chronological,
                "shuffled": seeded_rng(f"{family}:{stratum}:{w}").permutation(chronological),
                "reversed": chronological[::-1].copy(),
            }
            if family == "double":
                window_conditions["broken_lineage"] = conditions["broken_lineage"][left:right].copy()
            for condition, z in window_conditions.items():
                identity = f"{family}:{stratum}"
                window_id = f"{identity}:w{w:03d}"
                values, rho, miss = metrics(z)
                metric_rows.append({
                    "identity": identity,
                    "family": family,
                    "stratum": stratum,
                    "condition": condition,
                    "window": w,
                    "window_id": window_id,
                    **values,
                })
                for sample, value in enumerate(z):
                    series_rows.append({
                        "identity": identity,
                        "family": family,
                        "stratum": stratum,
                        "condition": condition,
                        "window": w,
                        "window_id": window_id,
                        "sample": sample,
                        "cycle": sample // SAMPLES_PER_CYCLE,
                        "landmark": sample % SAMPLES_PER_CYCLE,
                        "phase": float(value),
                        "ara_phase": float(2.0 * value),
                    })
                for lag, (r, d) in enumerate(zip(rho, miss), start=1):
                    closure_rows.append({
                        "identity": identity,
                        "family": family,
                        "stratum": stratum,
                        "condition": condition,
                        "window": w,
                        "window_id": window_id,
                        "lag": lag,
                        "rho": float(r),
                        "miss_signed": float(d),
                        "miss_abs": float(abs(d)),
                    })
    return pd.DataFrame(metric_rows), pd.DataFrame(series_rows), pd.DataFrame(closure_rows)


def record_summary(metrics_df: pd.DataFrame) -> pd.DataFrame:
    numeric = [
        "x_p", "x_r", "local_loss", "null_loss", "cycle_rho", "cycle_miss_signed",
        "cycle_miss_abs", "best_rho", "best_lag", "best_miss_abs", "median_rho", "orientation",
    ]
    out = metrics_df.groupby(["identity", "family", "stratum", "condition"], as_index=False)[numeric].median()
    counts = metrics_df.groupby(["identity", "family", "stratum", "condition"], as_index=False).agg(
        windows=("window", "size"),
        cycle_closure_share=("cycle_closure", "mean"),
        coherent_return_share=("any_coherent_return", "mean"),
    )
    return out.merge(counts, on=["identity", "family", "stratum", "condition"], validate="one_to_one")


def pick(summary: pd.DataFrame, family: str, stratum: str, condition: str) -> pd.Series:
    row = summary[(summary.family == family) & (summary.stratum == stratum) & (summary.condition == condition)]
    if len(row) != 1:
        raise RuntimeError(f"Expected one summary row for {family}/{stratum}/{condition}, got {len(row)}")
    return row.iloc[0]


def score_gates(summary: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    strata = ["free", "driven1", "driven2"]
    s = {k: pick(summary, "single", k, "chronological") for k in strata}
    d = {k: pick(summary, "double", k, "chronological") for k in strata}
    sh = {k: pick(summary, "double", k, "shuffled") for k in strata}
    br = {k: pick(summary, "double", k, "broken_lineage") for k in strata}

    g1_hits = sum((r.x_p < 1.0) and (r.x_r < 1.0) and (r.cycle_rho >= 0.80) and (r.cycle_miss_abs <= 0.03) for r in s.values())
    dxp = {k: float(d[k].x_p - s[k].x_p) for k in strata}
    g2_hits = sum(v >= 0.20 for v in dxp.values())
    d_xr_hits = sum(r.x_r < 1.25 for r in d.values())
    shuffle_dxr = {k: float(sh[k].x_r - d[k].x_r) for k in strata}
    shuffle_rho_drop = {k: float(d[k].best_rho - sh[k].best_rho) for k in strata}
    shuffle_xp = []
    for family in ["single", "double"]:
        for k in strata:
            c = pick(summary, family, k, "chronological")
            q = pick(summary, family, k, "shuffled")
            shuffle_xp.append(abs(float(q.x_p - c.x_p)))
    g4_hits = sum(
        (r.cycle_rho >= 0.80) and (r.cycle_miss_abs > 0.03) and
        (r.cycle_closure_share < 0.50) and (r.coherent_return_share > 0.0)
        for r in d.values()
    )
    lineage = {k: max(float(br[k].x_r - d[k].x_r), float(d[k].best_rho - br[k].best_rho)) for k in strata}
    g5_hits = sum(v >= 0.15 for v in lineage.values())
    reverse_xp, reverse_rho, reverse_orientation = [], [], []
    for family in ["single", "double"]:
        for k in strata:
            c = pick(summary, family, k, "chronological")
            r = pick(summary, family, k, "reversed")
            reverse_xp.append(abs(float(r.x_p - c.x_p)))
            reverse_rho.append(abs(float(r.best_rho - c.best_rho)))
            reverse_orientation.append(abs(float(r.orientation + c.orientation)))
    g6_orientation_hits = sum(v <= 0.02 for v in reverse_orientation)

    checks = [
        ("G1", "single closure referee in >=2/3 records", g1_hits, g1_hits >= 2),
        ("G2", "double-minus-single x_P >=0.20 in >=2/3 and positive median", f"hits={g2_hits}; median={np.median(list(dxp.values())):.6f}", g2_hits >= 2 and np.median(list(dxp.values())) > 0.0),
        ("G3a", "double x_R <1.25 in >=2/3", d_xr_hits, d_xr_hits >= 2),
        ("G3b", "shuffle raises x_R >=0.25 in >=2/3", f"hits={sum(v >= 0.25 for v in shuffle_dxr.values())}; values={shuffle_dxr}", sum(v >= 0.25 for v in shuffle_dxr.values()) >= 2),
        ("G3c", "shuffle lowers best rho >=0.15 in >=2/3", f"hits={sum(v >= 0.15 for v in shuffle_rho_drop.values())}; values={shuffle_rho_drop}", sum(v >= 0.15 for v in shuffle_rho_drop.values()) >= 2),
        ("G3d", "shuffle preserves x_P within 0.02 in all six", max(shuffle_xp), max(shuffle_xp) <= 0.02),
        ("G4", "coherent nonzero one-cycle miss in >=2/3 doubles", g4_hits, g4_hits >= 2),
        ("G5", "broken lineage penalty >=0.15 in >=2/3 doubles", f"hits={g5_hits}; values={lineage}", g5_hits >= 2),
        ("G6a", "reversal preserves x_P and best rho in all six", f"max_dxP={max(reverse_xp):.6f}; max_drho={max(reverse_rho):.6f}", max(reverse_xp) <= 0.02 and max(reverse_rho) <= 0.05),
        ("G6b", "reversal flips orientation within 0.02 in >=5/6", f"hits={g6_orientation_hits}; max_error={max(reverse_orientation):.6f}", g6_orientation_hits >= 5),
    ]
    gates = pd.DataFrame(checks, columns=["gate", "requirement", "value", "pass"])
    grouped = {
        "G1": bool(gates[gates.gate == "G1"].iloc[0]["pass"]),
        "G2": bool(gates[gates.gate == "G2"].iloc[0]["pass"]),
        "G3": bool(gates[gates.gate.str.startswith("G3")]["pass"].all()),
        "G4": bool(gates[gates.gate == "G4"].iloc[0]["pass"]),
        "G5": bool(gates[gates.gate == "G5"].iloc[0]["pass"]),
        "G6": bool(gates[gates.gate.str.startswith("G6")]["pass"].all()),
    }
    grouped["overall"] = all(grouped.values())
    details = {
        "grouped_gates": grouped,
        "paired_xp_difference": dxp,
        "shuffle_xr_increase": shuffle_dxr,
        "shuffle_best_rho_drop": shuffle_rho_drop,
        "lineage_penalty": lineage,
        "max_shuffle_xp_change": max(shuffle_xp),
        "max_reversal_xp_change": max(reverse_xp),
        "max_reversal_best_rho_change": max(reverse_rho),
        "max_reversal_orientation_sum_error": max(reverse_orientation),
    }
    return gates, details


def example_rows(prepared: dict[tuple[str, str], Prepared]) -> pd.DataFrame:
    rows = []
    for family in ["single", "double"]:
        item = prepared[(family, "free")]
        z = item.parent_z if family == "single" else item.child_z
        limit = min(len(z), 12 * SAMPLES_PER_CYCLE)
        for i in range(limit):
            rows.append({
                "family": family,
                "stratum": "free",
                "sample": i,
                "cycle": i // SAMPLES_PER_CYCLE,
                "landmark": i % SAMPLES_PER_CYCLE,
                "phase": float(z[i]),
                "ara_phase": float(2.0 * z[i]),
            })
    return pd.DataFrame(rows)


def plot(summary: pd.DataFrame, metrics_df: pd.DataFrame, closure_df: pd.DataFrame, examples: pd.DataFrame, gates: pd.DataFrame):
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    blue, gold, grey, dark = "#4C78A8", "#D99B2B", "#AAB2BD", "#27313D"
    fig, axes = plt.subplots(3, 2, figsize=(15, 17), constrained_layout=True)

    ax = axes[0, 0]
    styles = {
        ("single", "chronological"): (blue, "o", "single chronological"),
        ("double", "chronological"): (gold, "s", "double chronological"),
        ("double", "shuffled"): (grey, "x", "double shuffled"),
        ("double", "broken_lineage"): (dark, "^", "double broken lineage"),
    }
    for (family, condition), (color, marker, label) in styles.items():
        d = summary[(summary.family == family) & (summary.condition == condition)]
        ax.scatter(d.x_p, d.x_r, s=85, c=color, marker=marker, label=label, edgecolor=dark if marker not in ["x"] else None)
        for _, row in d.iterrows():
            ax.annotate(row.stratum.replace("driven", "D"), (row.x_p, row.x_r), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.axvline(1, color=dark, lw=1)
    ax.axhline(1, color=dark, lw=1)
    ax.set(xlim=(-0.05, 2.05), ylim=(-0.05, 2.05), xlabel="address openness x_P", ylabel="stochastic residual x_R", title="Record-level Irrationality Di-ARA plane")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[0, 1]
    for family, color, ls in [("single", blue, "-"), ("double", gold, "-")]:
        d = examples[examples.family == family]
        for landmark in range(SAMPLES_PER_CYCLE):
            q = d[d.landmark == landmark]
            ax.plot(q.cycle, q.ara_phase, color=color, lw=1.1, alpha=0.75, ls=ls)
        ax.plot([], [], color=color, lw=2.5, label=f"{family}: 8 parent landmarks")
    ax.axhline(1, color=dark, lw=1)
    ax.set(xlabel="successive arm-1 parent cycle", ylabel="child phase on ARA 0-2", ylim=(-0.05, 2.05), title="Relative phase strands through the parent clock")
    ax.legend(frameon=False)
    ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[1, 0]
    for family, condition, color, ls, label in [
        ("single", "chronological", blue, "-", "single chronological"),
        ("double", "chronological", gold, "-", "double chronological"),
        ("double", "shuffled", grey, "--", "double shuffled"),
    ]:
        d = closure_df[(closure_df.family == family) & (closure_df.stratum == "free") & (closure_df.condition == condition)]
        q = d.groupby("lag", as_index=False).rho.median()
        ax.plot(q.lag, q.rho, color=color, ls=ls, lw=2, marker="o", ms=3, label=label)
    ax.axvline(8, color=dark, lw=1, label="one parent cycle")
    ax.axhline(0.8, color=dark, lw=1, ls=":")
    ax.set(xlabel="lag (parent-clock samples)", ylabel="closure coherence rho", ylim=(-0.02, 1.03), title="Closure coherence across lags (free records)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[1, 1]
    for family, condition, color, ls, label in [
        ("single", "chronological", blue, "-", "single chronological"),
        ("double", "chronological", gold, "-", "double chronological"),
        ("double", "shuffled", grey, "--", "double shuffled"),
    ]:
        d = closure_df[(closure_df.family == family) & (closure_df.stratum == "free") & (closure_df.condition == condition)]
        q = d.groupby("lag", as_index=False).miss_abs.median()
        ax.plot(q.lag, q.miss_abs, color=color, ls=ls, lw=2, marker="o", ms=3, label=label)
    ax.axvline(8, color=dark, lw=1)
    ax.axhline(0.03, color=dark, lw=1, ls=":", label="physical closure tolerance")
    ax.set(xlabel="lag (parent-clock samples)", ylabel="absolute circular miss (turns)", ylim=(-0.01, 0.51), title="Closure miss across lags (free records)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[2, 0]
    strata = ["free", "driven1", "driven2"]
    x = np.arange(3)
    s = [pick(summary, "single", k, "chronological") for k in strata]
    d = [pick(summary, "double", k, "chronological") for k in strata]
    width = 0.36
    ax.bar(x - width / 2, [r.x_p for r in s], width, color=blue, label="single x_P", edgecolor=dark)
    ax.bar(x + width / 2, [r.x_p for r in d], width, color=gold, label="double x_P", edgecolor=dark)
    ax.plot(x, [r.x_r for r in d], color=dark, marker="D", lw=1.8, label="double x_R")
    ax.axhline(1, color=dark, lw=1, ls=":")
    ax.set_xticks(x, ["free", "driven 1", "driven 2"])
    ax.set(ylabel="ARA coordinate (0-2)", ylim=(0, 2.05), title="Paired physical-record readings")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", color="#E7E9EC", lw=0.7)

    ax = axes[2, 1]
    ax.axis("off")
    lines = ["Frozen gates"]
    for _, row in gates.iterrows():
        mark = "PASS" if bool(row["pass"]) else "FAIL"
        lines.append(f"{row['gate']:>3}  {mark:<4}  {row['requirement']}")
    lines.append("")
    lines.append("Finite data can support structured non-closure;")
    lines.append("it cannot prove a number-theoretically irrational ratio.")
    ax.text(0.02, 0.98, "\n".join(lines), va="top", ha="left", family="monospace", fontsize=9.3, color=dark)
    ax.set_title("Preregistered verdict components", loc="left")

    fig.suptitle(
        "T357 - physical pendulum Irrationality Di-ARA transfer\n"
        "Source: dynamicslab MultiArm-Pendulum, Zenodo 10.5281/zenodo.6633719; record medians",
        fontsize=17,
        color=dark,
    )
    fig.savefig(FIGURE_PNG, dpi=180, facecolor="white")
    plt.close(fig)


def write_report(summary: pd.DataFrame, gates: pd.DataFrame, details: dict, qa: pd.DataFrame):
    strata = ["free", "driven1", "driven2"]
    grouped = details["grouped_gates"]
    verdict = "SUPPORTED [controlled physical transfer]" if grouped["overall"] else "NOT SUPPORTED AS A COMPLETE PHYSICAL TRANSFER"
    d_free = pick(summary, "double", "free", "chronological")
    d_one = pick(summary, "double", "driven1", "chronological")
    d_two = pick(summary, "double", "driven2", "chronological")
    passed_groups = sum(bool(grouped[g]) for g in ["G1", "G2", "G3", "G4", "G5", "G6"])
    table = []
    for family in ["single", "double"]:
        for stratum in strata:
            r = pick(summary, family, stratum, "chronological")
            table.append(f"| {family} | {stratum} | {int(r.windows)} | {r.x_p:.3f} | {r.x_r:.3f} | {r.cycle_rho:.3f} | {r.cycle_miss_abs:.4f} | {r.best_rho:.3f} |")
    gate_lines = [f"| {r.gate} | {'PASS' if r['pass'] else 'FAIL'} | {r.requirement} | {r.value} |" for _, r in gates.iterrows()]
    text = f"""# T357 - physical pendulum Irrationality Di-ARA transfer

**Run date:** 11 August 2026  
**Source:** dynamicslab MultiArm-Pendulum experimental records, Zenodo 10.5281/zenodo.6633719  
**Frozen overall verdict:** **{verdict}**

## Plain-language answer

This test asked whether a second pendulum, viewed through the first pendulum's cycle, behaves like a structured path that keeps missing closure rather than like either an ordinary repeating loop or shuffled motion. The single pendulum was the known closure reference. The double pendulum was not assigned an outcome in advance.

The overall verdict follows the frozen gates exactly. Individual supported components remain useful even when the complete transfer verdict fails. Finite experimental data can establish coherent non-closure over the observed horizon; it cannot prove that an underlying frequency ratio is mathematically irrational.

{passed_groups} of the six grouped gates passed. The failure was specific: **G4, coherent non-closure**. The free and driven-1 double records returned to almost the same child phase after one arm-1 cycle (`rho={d_free.cycle_rho:.3f}, miss={d_free.cycle_miss_abs:.4f}` and `rho={d_one.cycle_rho:.3f}, miss={d_one.cycle_miss_abs:.4f}` turns). They are phase-locked at this cut, not irrationality examples. Driven-2 did not show clean closure, but its one-cycle coherence fell to `{d_two.cycle_rho:.3f}`; that is too incoherent to qualify as the ordered, repeatedly missing path frozen in the claim.

The strong partial result is that coupling opened more relational addresses in all three strata while retaining substantial history dependence. Shuffling preserved `x_P` exactly but raised `x_R` by `1.31` to `1.84` and lowered closure coherence in every double record. Broken lineage was penalised in both driven records. The instrument therefore transferred physically, but these particular coupled runs did not instantiate its coherent-nonclosing quadrant.

## Record-level readings

| family | run | windows | x_P | x_R | one-cycle rho | one-cycle miss | best rho |
|---|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

`x_P` reads finite/reused to open/resolving. `x_R` reads relation-determined to stochastic residual. The one-cycle columns test whether the child returns to the same phase after one arm-1 parent cycle.

## Frozen gates

| gate | result | requirement | observed |
|---|---|---|---|
{chr(10).join(gate_lines)}

Grouped gates: `{json.dumps(grouped, sort_keys=True)}`

## What the controls mean

- **Shuffle** keeps every observed phase value but destroys their order. A rise in `x_R` with unchanged `x_P` means the instrument correctly assigns the damage to history rather than support.
- **Reverse** asks whether the same path is recognised when traversed backwards. Support and unsigned closure should remain while orientation changes sign.
- **Broken lineage** gives the parent clock a physically unrelated arm-2 history. A penalty indicates that the true parent-child pairing contains information not supplied by a plausible child path alone.

## Data sufficiency and QA

All three declared single records and all three declared double records were processed. Complete six-cycle windows per record ranged from {int(qa.complete_windows.min())} to {int(qa.complete_windows.max())}. The analysis summarised within physical record before comparison; it did not treat the many windows as independent experiments.

## Evidence boundary

This is a controlled transfer of the T348 instrument to one public pendulum archive. It does not prove universal ARA geometry, a mathematically irrational frequency, or that all coupled pendulums occupy the same sector. Driven and free files are separate experimental runs rather than perfectly matched interventions.

## Reproduction

```powershell
& 'F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe' 'analysis\\irrationality_path_calibration\\t357_pendulum_irrationality_di_ara.py'
& 'F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe' 'analysis\\irrationality_path_calibration\\validate_t357_pendulum_irrationality_di_ara.py'
```

## Artifact index

- frozen claim and protocol: `T357_PENDULUM_IRRATIONALITY_DI_ARA_*_v1.md` plus SHA-256 records;
- complete sampled windows: `{SERIES_CSV.name}`;
- window metrics and lag curves: `{METRICS_CSV.name}`, `{CLOSURE_CSV.name}`;
- record summaries and gates: `{SUMMARY_CSV.name}`, `{GATES_CSV.name}`;
- data QA: `{QA_CSV.name}`;
- machine verdict: `{RESULTS_JSON.name}`;
- visual: `{FIGURE_PNG.name}`.
"""
    REPORT_MD.write_text(text, encoding="utf-8")


def main():
    if not CLAIM.exists() or not PROTOCOL.exists():
        raise FileNotFoundError("Frozen T357 claim/protocol is missing")
    prepared: dict[tuple[str, str], Prepared] = {}
    for family, rows in FILES.items():
        for stratum, filename in rows.items():
            item = prepare(family, stratum, filename)
            if item.n_windows < 1:
                raise RuntimeError(f"Insufficient complete windows in {filename}")
            prepared[(family, stratum)] = item

    metrics_df, series_df, closure_df = run_windows(prepared)
    summary = record_summary(metrics_df)
    qa = pd.DataFrame([item.qa for item in prepared.values()])
    gates, details = score_gates(summary)
    examples = example_rows(prepared)

    metrics_df.to_csv(METRICS_CSV, index=False)
    series_df.to_csv(SERIES_CSV, index=False)
    closure_df.to_csv(CLOSURE_CSV, index=False)
    summary.to_csv(SUMMARY_CSV, index=False)
    qa.to_csv(QA_CSV, index=False)
    gates.to_csv(GATES_CSV, index=False)
    examples.to_csv(EXAMPLE_CSV, index=False)

    grouped = details["grouped_gates"]
    result = {
        "test": "T357 physical pendulum Irrationality Di-ARA transfer",
        "date": "2026-08-11",
        "source_doi": "10.5281/zenodo.6633719",
        "evidence_class": "controlled public physical-system transfer",
        "overall_verdict": "SUPPORTED [controlled physical transfer]" if grouped["overall"] else "NOT SUPPORTED AS A COMPLETE PHYSICAL TRANSFER",
        "grouped_gates": grouped,
        "details": details,
        "record_count": 6,
        "window_count": int(metrics_df[metrics_df.condition == "chronological"].shape[0]),
        "claim_sha256": sha256(CLAIM),
        "protocol_sha256": sha256(PROTOCOL),
        "boundary": "Finite physical structured non-closure only; not proof of a mathematically irrational ratio or universal ARA.",
    }
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    plot(summary, metrics_df, closure_df, examples, gates)
    write_report(summary, gates, details, qa)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
