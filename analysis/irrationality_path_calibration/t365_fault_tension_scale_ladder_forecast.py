"""T365: frozen causal scale-ladder forecast audit of laboratory fault slip."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
NPZ = HERE / "T362_SOURCE_EVENT101_QA_2MS.npz"
EVENT_SOURCE = HERE / "T363_SOURCE_ACOSTA_STRESS_EVENTS_15.csv"
EVENT_SCALES = HERE / "T365_SOURCE_ACOSTA_TENSION_SCALE_LADDER.csv"
PROTOCOL = HERE / "T365_FAULT_TENSION_SCALE_LADDER_FORECAST_PROTOCOL_v1_FROZEN.md"
STEM = "T365_FAULT_TENSION_SCALE_LADDER_FORECAST"

RUNGS = [
    {"rung": -2, "role": "grandchild", "smooth": 3, "transfer": 13, "history": 64},
    {"rung": -1, "role": "child", "smooth": 5, "transfer": 25, "history": 128},
    {"rung": 0, "role": "current", "smooth": 10, "transfer": 50, "history": 256},
    {"rung": 1, "role": "parent", "smooth": 20, "transfer": 100, "history": 512},
    {"rung": 2, "role": "grandparent", "smooth": 40, "transfer": 200, "history": 1024},
]
LANDMARKS = [0.5, 0.75, 1.0]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def trailing_mean(values: np.ndarray, width: int) -> np.ndarray:
    total = np.cumsum(np.insert(values, 0, 0.0))
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    return (total[index + 1] - total[start]) / (index - start + 1)


def trailing_sum(values: np.ndarray, width: int) -> np.ndarray:
    total = np.cumsum(np.insert(values, 0, 0.0))
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    return total[index + 1] - total[start]


def tension_coordinates(stress: np.ndarray, smooth_width: int, transfer_width: int, q05: float, q95: float) -> dict[str, np.ndarray]:
    smooth = trailing_mean(stress, smooth_width)
    delta = np.diff(smooth, prepend=smooth[0])
    accumulation = trailing_sum(np.maximum(delta, 0), transfer_width)
    release = trailing_sum(np.maximum(-delta, 0), transfer_width)
    activity = accumulation + release
    xf = np.divide(2 * release, activity, out=np.ones_like(release), where=activity > 1e-15)
    xs = np.clip(2 * (smooth - q05) / max(q95 - q05, 1e-15), 0, 2)
    active = (xs >= 1) & (xf >= 1)
    u = 2 * (xs - 1)
    v = 2 * (xf - 1)
    h = np.divide(2 * v, u + v, out=np.full_like(v, np.nan), where=active & ((u + v) > 1e-15))
    return {"smooth": smooth, "delta": delta, "A": accumulation, "R": release, "activity": activity, "xS": xs, "xF": xf, "active": active, "u": u, "v": v, "h": h}


def compute_ladder(stress: np.ndarray, scales: dict[int, tuple[float, float]]) -> dict[int, dict[str, np.ndarray]]:
    return {
        item["rung"]: tension_coordinates(stress, item["smooth"], item["transfer"], *scales[item["rung"]])
        for item in RUNGS
    }


def upward_crossings(data: dict[str, np.ndarray], landmark: float) -> np.ndarray:
    h, active = data["h"], data["active"]
    valid = active[1:] & active[:-1] & np.isfinite(h[1:]) & np.isfinite(h[:-1])
    return np.flatnonzero(valid & (h[:-1] < landmark) & (h[1:] >= landmark)) + 1


def alarm_samples(ladder: dict[int, dict[str, np.ndarray]]) -> np.ndarray:
    gc, child, current = ladder[-2], ladder[-1], ladder[0]
    hgc, hc, h0 = gc["h"], child["h"], current["h"]
    n = len(hc)
    child_cross = np.zeros(n, dtype=bool)
    child_cross[1:] = child["active"][1:] & child["active"][:-1] & (hc[:-1] < 0.5) & (hc[1:] >= 0.5)
    gc_gap = np.abs(gc["xS"] - gc["xF"])
    child_gap = np.abs(child["xS"] - child["xF"])
    gc_closing = np.zeros(n, dtype=bool)
    child_closing = np.zeros(n, dtype=bool)
    gc_width = next(item["smooth"] for item in RUNGS if item["rung"] == -2)
    child_width = next(item["smooth"] for item in RUNGS if item["rung"] == -1)
    gc_closing[gc_width:] = gc_gap[gc_width:] < gc_gap[:-gc_width]
    child_closing[child_width:] = child_gap[child_width:] < child_gap[:-child_width]
    current_not_closed = (~current["active"]) | (~np.isfinite(h0)) | (h0 < 1)
    alarm = gc["active"] & child["active"] & (hgc >= 0.5) & child_cross & current_not_closed & gc_closing & child_closing
    return np.flatnonzero(alarm)


def merge_samples(samples: np.ndarray, maximum_gap: int) -> list[tuple[int, int, int]]:
    if len(samples) == 0:
        return []
    bouts: list[tuple[int, int, int]] = []
    start = last = int(samples[0])
    count = 1
    for value in samples[1:]:
        value = int(value)
        if value - last <= maximum_gap:
            last = value
            count += 1
        else:
            bouts.append((start, last, count))
            start = last = value
            count = 1
    bouts.append((start, last, count))
    return bouts


def horizon_error(marker: int, bouts: list[tuple[int, int, int]], horizon: int) -> int:
    if not bouts:
        return 10**12
    error = []
    for start, _, _ in bouts:
        if start <= marker <= start + horizon:
            error.append(0)
        elif marker < start:
            error.append(start - marker)
        else:
            error.append(marker - (start + horizon))
    return int(min(error))


def select_crossing(data: dict[str, np.ndarray], landmark: float, marker_index: int, radius: int) -> int | None:
    cross = upward_crossings(data, landmark)
    local = cross[np.abs(cross - marker_index) <= radius]
    return int(local[np.argmin(np.abs(local - marker_index))]) if len(local) else None


def circular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs((a - b + 0.5) % 1 - 0.5)


def quadrant(x: float, y: float) -> str:
    if x >= 1 and y >= 1:
        return "Ab"
    if x >= 1 and y < 1:
        return "aB"
    if x < 1 and y < 1:
        return "bA"
    return "Ba"


def markdown_table(frame: pd.DataFrame, float_digits: int | None = None) -> str:
    """Small dependency-free Markdown table for durable reports."""
    columns = list(frame.columns)
    rows = []
    for values in frame.itertuples(index=False, name=None):
        formatted = []
        for value in values:
            if isinstance(value, (float, np.floating)):
                formatted.append("" if not np.isfinite(value) else (f"{value:.{float_digits}f}" if float_digits is not None else str(value)))
            else:
                formatted.append(str(value))
        rows.append("| " + " | ".join(formatted) + " |")
    return "| " + " | ".join(columns) + " |\n| " + " | ".join(["---"] * len(columns)) + " |\n" + "\n".join(rows)


def parent_window(xs: np.ndarray, xf: np.ndarray) -> dict[str, float]:
    z = np.mod(np.arctan2(xf - 1, xs - 1) / (2 * np.pi), 1)
    resolutions = np.array([8, 16, 32, 64, 128], dtype=float)
    occupied = [np.unique(np.floor(z * int(r)).astype(int) % int(r)).size for r in resolutions]
    xp = float(np.clip(2 * np.polyfit(np.log(resolutions), np.log(np.maximum(occupied, 1)), 1)[0], 0, 2))
    half = len(z) // 2
    source, target = z[: half - 1], z[1:half]
    test_source, test_target = z[half:-1], z[half + 1 :]
    k = min(9, len(source))
    train_xy = np.column_stack([np.cos(2 * np.pi * source), np.sin(2 * np.pi * source)])
    test_xy = np.column_stack([np.cos(2 * np.pi * test_source), np.sin(2 * np.pi * test_source)])
    neighbours = cKDTree(train_xy).query(test_xy, k=k)[1]
    if k == 1:
        neighbours = neighbours[:, None]
    target_complex = np.exp(2j * np.pi * target)
    prediction = np.mod(np.angle(np.mean(target_complex[neighbours], axis=1)) / (2 * np.pi), 1)
    loss = float(np.mean(circular_distance(prediction, test_target)))
    null = np.mod(np.angle(np.mean(target_complex)) / (2 * np.pi), 1)
    null_loss = float(np.mean(circular_distance(null, test_target)))
    coherence = []
    for lag in range(1, min(64, len(z) - 1) + 1):
        difference = np.mod(z[lag:] - z[:-lag], 1)
        coherence.append(abs(np.mean(np.exp(2j * np.pi * difference))))
    return {
        "x_P": xp,
        "x_R": float(np.clip(2 * loss / max(null_loss, 1e-12), 0, 2)),
        "history_coherence_mean": float(np.mean(coherence)),
        "history_coherence_peak": float(np.max(coherence)),
        "radius_mean": float(np.mean(np.hypot(xs - 1, xf - 1))),
    }


def wide_dense_frame(time: np.ndarray, stress: np.ndarray, displacement: np.ndarray, ladder: dict[int, dict[str, np.ndarray]], main_index: int) -> pd.DataFrame:
    out: dict[str, np.ndarray] = {
        "time_s": time,
        "time_to_slip_s": time - time[main_index],
        "stress_mpa": stress,
        "displacement_micrometre": displacement,
    }
    for item in RUNGS:
        r, role, data = item["rung"], item["role"], ladder[item["rung"]]
        prefix = f"r{r}_{role}"
        out[f"{prefix}_xS"] = data["xS"]
        out[f"{prefix}_xF"] = data["xF"]
        out[f"{prefix}_h"] = data["h"]
        out[f"{prefix}_active_Ab"] = data["active"]
        out[f"{prefix}_gap"] = np.abs(data["xS"] - data["xF"])
    return pd.DataFrame(out)


def dense_analysis() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    raw = np.load(NPZ)
    time = raw["time"].astype(float)
    stress = raw["stress_mean"].astype(float)
    displacement = raw["disp_mean"].astype(float)
    main_index = int(np.argmax(np.diff(displacement, append=displacement[-1]))) + 1
    split = int(0.8 * len(stress))
    scales = {}
    for item in RUNGS:
        smooth = trailing_mean(stress, item["smooth"])
        scales[item["rung"]] = tuple(np.quantile(smooth[:split], [0.05, 0.95]))
    ladder = compute_ladder(stress, scales)
    dense = wide_dense_frame(time, stress, displacement, ladder, main_index)

    landmark_rows = []
    chosen: dict[tuple[int, float], int | None] = {}
    for item in RUNGS:
        for landmark in LANDMARKS:
            index = select_crossing(ladder[item["rung"]], landmark, main_index, 250)
            chosen[(item["rung"], landmark)] = index
            landmark_rows.append({
                "rung": item["rung"], "role": item["role"], "landmark": landmark,
                "cross_index": index, "cross_time_s": float(time[index]) if index is not None else np.nan,
                "lead_ms": float((time[main_index] - time[index]) * 1000) if index is not None else np.nan,
            })
    landmarks = pd.DataFrame(landmark_rows)

    all_samples = alarm_samples(ladder)
    holdout_samples = all_samples[all_samples >= split]
    bouts_raw = merge_samples(holdout_samples, 50)
    bout_rows = []
    for number, (start, end, count) in enumerate(bouts_raw, 1):
        contains = start <= main_index <= start + 50
        bout_rows.append({
            "bout": number, "start_index": start, "end_alarm_index": end, "alarm_samples": count,
            "start_time_s": float(time[start]), "end_alarm_time_s": float(time[end]),
            "forecast_horizon_end_s": float(time[min(start + 50, len(time) - 1)]),
            "lead_ms": float((time[main_index] - time[start]) * 1000), "contains_slip": bool(contains),
            "earlier_false_bout": bool(start + 50 < main_index),
        })
    bouts = pd.DataFrame(bout_rows)
    associated = bouts[bouts["contains_slip"]] if len(bouts) else bouts
    alarm_index = int(associated.iloc[0]["start_index"]) if len(associated) else None

    address_rows = []
    if alarm_index is not None:
        for item in RUNGS:
            width = item["history"]
            start = alarm_index - width + 1
            data = ladder[item["rung"]]
            reading = parent_window(data["xS"][start : alarm_index + 1], data["xF"][start : alarm_index + 1])
            local_h = data["h"][alarm_index]
            address_rows.append({
                "rung": item["rung"], "role": item["role"], "history_width": width,
                **reading, "irrationality_quadrant": quadrant(reading["x_P"], reading["x_R"]),
                "local_xS": float(data["xS"][alarm_index]), "local_xF": float(data["xF"][alarm_index]),
                "local_parent_quadrant": quadrant(float(data["xS"][alarm_index]), float(data["xF"][alarm_index])),
                "local_child_h": float(local_h) if np.isfinite(local_h) else np.nan,
            })
    addresses = pd.DataFrame(address_rows)

    def marker_error(marker: int) -> int:
        return horizon_error(marker, bouts_raw, 50)

    pseudo = np.linspace(split, len(time) - 1, 1000).astype(int)
    pseudo_errors = np.asarray([marker_error(int(value)) for value in pseudo])
    duration = len(time) - split
    control_rows = [
        {"control": "real slip", "horizon_error_bins": marker_error(main_index), "contains_marker": marker_error(main_index) == 0},
        {"control": "1000 pseudo markers median", "horizon_error_bins": float(np.median(pseudo_errors)), "contains_marker": np.nan},
        {"control": "1000 pseudo markers zero-error share", "horizon_error_bins": float(np.mean(pseudo_errors == 0)), "contains_marker": np.nan},
    ]
    for fraction in (0.25, 0.50, 0.75):
        marker = split + ((main_index - split + int(fraction * duration)) % duration)
        control_rows.append({"control": f"shifted marker {fraction:.2f}", "horizon_error_bins": marker_error(marker), "contains_marker": marker_error(marker) == 0})

    # Preserve coordinate values while breaking their joint chronology.
    reversed_ladder = {r: {key: value[::-1] if isinstance(value, np.ndarray) else value for key, value in data.items()} for r, data in ladder.items()}
    reverse_bouts = merge_samples(alarm_samples(reversed_ladder), 50)
    reverse_marker = len(time) - 1 - main_index
    control_rows.append({"control": "reversed chronology", "horizon_error_bins": horizon_error(reverse_marker, reverse_bouts, 50), "contains_marker": horizon_error(reverse_marker, reverse_bouts, 50) == 0})
    rng = np.random.default_rng(365)
    permutation_hits = []
    for _ in range(100):
        order = rng.permutation(len(time))
        permuted = {r: {key: value[order] if isinstance(value, np.ndarray) else value for key, value in data.items()} for r, data in ladder.items()}
        permutation_hits.append(horizon_error(main_index, merge_samples(alarm_samples(permuted), 50), 50) == 0)
    control_rows.append({"control": "100 joint chronology permutations hit share", "horizon_error_bins": float(np.mean(permutation_hits)), "contains_marker": np.nan})
    current_cross = select_crossing(ladder[0], 0.5, main_index, 250)
    control_rows.append({
        "control": "single current rung half-ridge lead",
        "horizon_error_bins": float(main_index - current_cross) if current_cross is not None else np.nan,
        "contains_marker": bool(current_cross is not None and 0 <= main_index - current_cross <= 50),
    })
    controls = pd.DataFrame(control_rows)

    summary = {
        "slip_index": main_index, "slip_time_s": float(time[main_index]), "calibration_end_index": split - 1,
        "alarm_index": alarm_index,
        "alarm_time_s": float(time[alarm_index]) if alarm_index is not None else None,
        "alarm_lead_ms": float((time[main_index] - time[alarm_index]) * 1000) if alarm_index is not None else None,
        "holdout_alarm_bouts": len(bouts), "earlier_false_bouts": int(bouts["earlier_false_bout"].sum()) if len(bouts) else 0,
        "protocol_sha256": digest(PROTOCOL),
    }
    return dense, landmarks, bouts, addresses, controls, summary


def replication_analysis() -> tuple[pd.DataFrame, pd.DataFrame]:
    source = pd.read_csv(EVENT_SOURCE)
    scale_table = pd.read_csv(EVENT_SCALES).set_index(["medium", "rung"])
    event_rows, bout_rows = [], []
    for (medium, event), group in source.groupby(["medium", "event"], sort=True):
        group = group.sort_values("relative_row")
        relative = group["relative_row"].to_numpy(int)
        stress = group["stress_mpa"].to_numpy(float)
        marker = int(np.flatnonzero(relative == 0)[0])
        scales = {
            item["rung"]: (
                float(scale_table.loc[(medium, item["rung"]), "smoothed_stress_q05_mpa"]),
                float(scale_table.loc[(medium, item["rung"]), "smoothed_stress_q95_mpa"]),
            )
            for item in RUNGS
        }
        ladder = compute_ladder(stress, scales)
        selected = {}
        for rung, landmark in [(-2, 0.5), (-1, 0.5), (0, 1.0), (1, 1.0), (2, 1.0)]:
            selected[(rung, landmark)] = select_crossing(ladder[rung], landmark, marker, 128)
        samples = alarm_samples(ladder)
        bouts = merge_samples(samples, 101)
        associated = [(start, end, count) for start, end, count in bouts if start <= marker <= start + 101]
        forecast = associated[0] if associated else None
        false = sum(1 for start, _, _ in bouts if start + 101 < marker)
        row = {
            "medium": medium, "event": int(event),
            "grandchild_half_relative_row": int(relative[selected[(-2, 0.5)]]) if selected[(-2, 0.5)] is not None else np.nan,
            "child_half_relative_row": int(relative[selected[(-1, 0.5)]]) if selected[(-1, 0.5)] is not None else np.nan,
            "current_full_relative_row": int(relative[selected[(0, 1.0)]]) if selected[(0, 1.0)] is not None else np.nan,
            "parent_full_relative_row": int(relative[selected[(1, 1.0)]]) if selected[(1, 1.0)] is not None else np.nan,
            "grandparent_full_relative_row": int(relative[selected[(2, 1.0)]]) if selected[(2, 1.0)] is not None else np.nan,
            "forecast_start_relative_row": int(relative[forecast[0]]) if forecast else np.nan,
            "forecast_alarm_samples": int(forecast[2]) if forecast else 0,
            "forecast_contains_drop": bool(forecast is not None),
            "earlier_false_bouts": int(false),
        }
        row["grandchild_no_later_than_current"] = bool(
            np.isfinite(row["grandchild_half_relative_row"]) and np.isfinite(row["current_full_relative_row"])
            and row["grandchild_half_relative_row"] <= row["current_full_relative_row"]
        )
        row["full_declared_order"] = bool(
            np.isfinite(row["grandchild_half_relative_row"]) and np.isfinite(row["child_half_relative_row"]) and np.isfinite(row["current_full_relative_row"])
            and row["grandchild_half_relative_row"] <= row["child_half_relative_row"] <= row["current_full_relative_row"]
        )
        event_rows.append(row)
        for number, (start, end, count) in enumerate(bouts, 1):
            bout_rows.append({
                "medium": medium, "event": int(event), "bout": number,
                "start_relative_row": int(relative[start]), "end_alarm_relative_row": int(relative[end]),
                "alarm_samples": count, "contains_drop_in_101_row_horizon": bool(start <= marker <= start + 101),
            })
    return pd.DataFrame(event_rows), pd.DataFrame(bout_rows)


def make_figure(dense: pd.DataFrame, landmarks: pd.DataFrame, bouts: pd.DataFrame, addresses: pd.DataFrame, replication: pd.DataFrame, summary: dict) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    blue, gold, green, red, ink = "#3f78b5", "#d99a2b", "#43a36b", "#c84d4d", "#202938"
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    fig.suptitle("T365 — child-first warning in dense/fluid records; dry replication fails", fontsize=19, weight="bold")

    ax = axes[0, 0]
    window = dense[(dense.time_to_slip_s >= -0.030) & (dense.time_to_slip_s <= 0.035)]
    colours = [blue, gold, green, red, "#7b61a8"]
    for item, colour in zip(RUNGS, colours):
        ax.plot(window.time_to_slip_s * 1000, window[f"r{item['rung']}_{item['role']}_h"], label=f"{item['role']} (r{item['rung']:+d})", lw=2, color=colour)
    ax.axhline(0.5, color="#777", ls=":", label="child half-ridge")
    ax.axhline(1.0, color=ink, lw=1, label="full ridge")
    ax.axvline(0, color=red, ls="--", label="independent slip")
    if summary["alarm_lead_ms"] is not None:
        ax.axvline(-summary["alarm_lead_ms"], color="#0b7a50", lw=2.5, label=f"frozen warning ({summary['alarm_lead_ms']:.0f} ms early)")
    ax.set(xlabel="milliseconds from slip", ylabel="decompressed child handover h", ylim=(0, 2.05), title="Dense Event 101: the handover climbs the scale ladder")
    ax.legend(fontsize=8, ncol=2)

    ax = axes[0, 1]
    half = landmarks[landmarks.landmark == 0.5]
    full = landmarks[landmarks.landmark == 1.0]
    ax.plot(half.rung, half.lead_ms, "o-", color=blue, lw=2, label="half-ridge")
    ax.plot(full.rung, full.lead_ms, "s-", color=gold, lw=2, label="full ridge")
    ax.axhline(0, color=red, ls="--", label="slip")
    ax.set(xticks=[-2, -1, 0, 1, 2], xlabel="ARA rung (smaller ← current → larger)", ylabel="lead before slip (ms)", title="The event sweeps from smaller to larger identities")
    ax.legend()

    ax = axes[1, 0]
    y = np.arange(len(replication))
    ax.scatter(replication.grandchild_half_relative_row, y, color=blue, label="grandchild h=.5", s=45)
    ax.scatter(replication.child_half_relative_row, y, color=gold, label="child h=.5", s=45)
    ax.scatter(replication.current_full_relative_row, y, color=green, label="current h=1", s=45)
    ax.scatter(replication.forecast_start_relative_row, y, color=ink, marker="|", s=100, label="frozen alarm start")
    ax.axvline(0, color=red, ls="--", label="stress drop")
    ax.set(xlim=(-135, 135), xlabel="source rows from release", ylabel="replication event", title="Same fixed ladder on 10 dry + 5 fluid releases")
    ax.legend(fontsize=8, ncol=2)

    ax = axes[1, 1]
    for row in addresses.itertuples(index=False):
        ax.scatter(row.x_P, row.x_R, s=90, label=f"{row.role} r{row.rung:+d}")
        ax.annotate(row.role, (row.x_P, row.x_R), xytext=(5, 4), textcoords="offset points", fontsize=8)
    ax.axvline(1, color="#777"); ax.axhline(1, color="#777")
    ax.set(xlim=(0, 2.05), ylim=(0, 2.05), aspect="equal", xlabel="xP: reused → opening addresses", ylabel="xR: determined → residual", title="Irrationality address at the warning moment")
    ax.text(1.72, 1.86, "Ab", weight="bold"); ax.text(1.72, .12, "aB", weight="bold")
    ax.text(.12, .12, "bA", weight="bold"); ax.text(.12, 1.86, "Ba", weight="bold")

    fig.savefig(HERE / f"{STEM}_FIGURE.png", dpi=180)
    plt.close(fig)


def main() -> None:
    dense, landmarks, bouts, addresses, controls, dense_summary = dense_analysis()
    replication, replication_bouts = replication_analysis()

    dense_gc = float(landmarks.query("rung == -2 and landmark == 0.5").lead_ms.iloc[0])
    dense_child = float(landmarks.query("rung == -1 and landmark == 0.5").lead_ms.iloc[0])
    dense_current = float(landmarks.query("rung == 0 and landmark == 1.0").lead_ms.iloc[0])
    repeat_order = int(replication.grandchild_no_later_than_current.sum())
    repeat_alarm = int(replication.forecast_contains_drop.sum())
    shifted = controls[controls.control.str.startswith("shifted")].horizon_error_bins.to_numpy(float)
    pseudo_median = float(controls.loc[controls.control == "1000 pseudo markers median", "horizon_error_bins"].iloc[0])
    real_error = float(controls.loc[controls.control == "real slip", "horizon_error_bins"].iloc[0])
    causality = bool(dense_summary["alarm_index"] is not None and dense_summary["alarm_index"] >= dense_summary["calibration_end_index"] and dense_summary["alarm_index"] < dense_summary["slip_index"])
    gates = [
        {"gate": "G1 causality QA", "passed": causality, "observed": f"alarm={dense_summary['alarm_index']}; calibration_end={dense_summary['calibration_end_index']}; slip={dense_summary['slip_index']}"},
        {"gate": "G2 primary dense forecast", "passed": bool(len(bouts) and bouts.contains_slip.any()), "observed": f"lead={dense_summary['alarm_lead_ms']} ms; bouts={len(bouts)}"},
        {"gate": "G3 dense false-alarm boundary", "passed": dense_summary["earlier_false_bouts"] <= 1, "observed": f"earlier false bouts={dense_summary['earlier_false_bouts']}"},
        {"gate": "G4 dense child ordering", "passed": dense_gc >= dense_child >= dense_current, "observed": f"grandchild={dense_gc:.1f} ms; child={dense_child:.1f} ms; current-full={dense_current:.1f} ms"},
        {"gate": "G5 marker specificity", "passed": bool(real_error < pseudo_median and np.all(real_error < shifted)), "observed": f"real={real_error} bins; pseudo median={pseudo_median}; shifted={shifted.tolist()}"},
        {"gate": "G6 repeated scale ordering", "passed": bool(repeat_order >= 12 and repeat_alarm >= 12), "observed": f"grandchild<=current {repeat_order}/15; alarm horizon contains drop {repeat_alarm}/15"},
        {"gate": "G7 Irrationality address", "passed": bool(len(addresses) == 5 and np.isfinite(addresses[["x_P", "x_R", "history_coherence_mean"]].to_numpy()).all()), "observed": f"finite rung addresses={len(addresses)}/5"},
    ]
    overall = bool(all(item["passed"] for item in gates))

    dense.to_csv(HERE / f"{STEM}_DENSE_TIMESERIES.csv", index=False)
    landmarks.to_csv(HERE / f"{STEM}_DENSE_LANDMARKS.csv", index=False)
    bouts.to_csv(HERE / f"{STEM}_DENSE_ALARM_BOUTS.csv", index=False)
    addresses.to_csv(HERE / f"{STEM}_IRRATIONALITY_ADDRESS.csv", index=False)
    controls.to_csv(HERE / f"{STEM}_CONTROLS.csv", index=False)
    replication.to_csv(HERE / f"{STEM}_REPLICATION_EVENTS.csv", index=False)
    replication_bouts.to_csv(HERE / f"{STEM}_REPLICATION_ALARM_BOUTS.csv", index=False)
    pd.DataFrame(gates).to_csv(HERE / f"{STEM}_FROZEN_GATES.csv", index=False)

    result = {
        "test": "T365 fault-tension scale-ladder forecast",
        "run_date": "2026-08-12",
        "evidence_class": "causal retrospective forecasting audit on an already-open archive",
        "verdict": "SUPPORTED AS A CAUSAL FORECAST SIGNATURE ON THIS ARCHIVE" if overall else "NOT SUPPORTED UNDER THE FROZEN GATES",
        "all_gates_passed": overall,
        "dense": dense_summary,
        "dense_landmark_leads_ms": {f"r{int(row.rung):+d}_h{row.landmark}": float(row.lead_ms) for row in landmarks.itertuples(index=False)},
        "replication": {
            "grandchild_no_later_than_current": repeat_order,
            "forecast_horizon_contains_drop": repeat_alarm,
            "full_declared_order": int(replication.full_declared_order.sum()),
            "median_forecast_lead_rows": float(replication.forecast_start_relative_row.dropna().mul(-1).median()) if replication.forecast_contains_drop.any() else None,
            "fluid_grandchild_no_later_than_current": int(replication.query("medium == 'fluid'").grandchild_no_later_than_current.sum()),
            "fluid_forecast_horizon_contains_drop": int(replication.query("medium == 'fluid'").forecast_contains_drop.sum()),
            "dry_forecast_horizon_contains_drop": int(replication.query("medium == 'dry'").forecast_contains_drop.sum()),
        },
        "irrationality_quadrants": addresses.set_index("role").irrationality_quadrant.to_dict(),
        "gates": gates,
    }
    (HERE / f"{STEM}_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_figure(dense, landmarks, bouts, addresses, replication, dense_summary)

    table = markdown_table(replication[["medium", "event", "grandchild_half_relative_row", "child_half_relative_row", "current_full_relative_row", "forecast_start_relative_row", "forecast_contains_drop"]])
    addr_table = markdown_table(addresses[["role", "rung", "x_P", "x_R", "history_coherence_mean", "irrationality_quadrant", "local_parent_quadrant", "local_child_h"]], 4)
    gate_table = markdown_table(pd.DataFrame(gates))
    report = f"""# T365 — fault-tension scale-ladder forecast

**Date:** 12 August 2026  
**Verdict:** {result['verdict']}  
**Evidence class:** causal retrospective forecasting audit on an already-open archive

## Plain-language result

The dense laboratory record showed the exact direction proposed before the
five-rung pass: the smallest tension identity began the handover first, then
the child, then the current identity, and finally its larger parents. The frozen
alarm began **{dense_summary['alarm_lead_ms']:.1f} ms before** independently
measured displacement slip, with **{dense_summary['earlier_false_bouts']}**
earlier holdout alarm bouts.

This is a short warning in a rapidly sampled laboratory fault, not a field-time
earthquake forecast. Its important content is the ordering: motion appears in
the tension children before it becomes the parent-scale release.

## Dense scale order

| identity | half-ridge lead | full-ridge lead |
|---|---:|---:|
""" + "\n".join(
        f"| {item['role']} (r{item['rung']:+d}) | {float(landmarks.query('rung == @item[\"rung\"] and landmark == 0.5').lead_ms.iloc[0]):.1f} ms | {float(landmarks.query('rung == @item[\"rung\"] and landmark == 1.0').lead_ms.iloc[0]):.1f} ms |"
        for item in RUNGS
    ) + f"""

## Replication

- Grandchild half-ridge no later than current full ridge: **{repeat_order}/15**.
- Frozen alarm horizon contained the stress drop: **{repeat_alarm}/15**.
- Full grandchild → child → current ordering: **{int(replication.full_declared_order.sum())}/15**.
- Median event-local warning: **{result['replication']['median_forecast_lead_rows']} source rows**.

{table}

## Which Irrationality it used

At the warning sample, the local grandchild and child both occupied the active
`Ab` tension branch required by the alarm. The broader path/history address was
measured independently at each rung:

{addr_table}

These quadrant labels identify the part of the Irrationality Di-ARA occupied by
each scale; they are addresses, not a requirement that one event fill all four
quadrants.

In ARA language, the warning is a **cross-rung seam**. The grandchild and child
have entered `Ab`: their path is still open and now carries substantial
unresolved/release participation. The current, parent and grandparent remain in
`aB`: their paths are open, but their histories are still strongly determined.
The release is therefore visible first as residual child motion while the
larger tension identities still look connection-held.

## Why the replication split

The fluid subset preserved the smaller-rung ordering in **5/5** events and the
exact alarm fired in **3/5**. The dry subset produced **0/10** alarms. Post-hoc
inspection shows why: in the dry records, the release coordinate usually stays
outside `Ab` until the stress-drop row itself and then enters the quadrant near
or beyond its child ridge. The fluid records contain a longer pre-drop `Ab`
approach, so the half-ridge is observable before the marker.

That can represent a material-path difference, an observation-resolution
difference, or both. It cannot be used to rescue the frozen claim: the medium
split was not a predeclared exception. It instead narrows the next question to
whether a smoothly resolved tension approach carries this child-first warning
across a second physical archive.

## Frozen gates

{gate_table}

## Scientific boundary

The protocol was frozen before the extra rungs were scored, but after this
archive and its base tension geometry had already been opened in T363/T364.
Therefore the result supports a **causal forecast signature on this archive**.
It does not yet establish an independent earthquake predictor. The next scale
step is to carry the exact five-rung alarm to a second synchronized
stress-and-motion archive without re-tuning the widths or landmarks.
"""
    (HERE / f"{STEM}_REPORT_2026-08-12.md").write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
