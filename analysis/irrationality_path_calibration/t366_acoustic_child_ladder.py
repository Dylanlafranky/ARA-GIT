"""T366: frozen acoustic child-ladder audit before Westerly-granite failure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
CATALOG_DIR = HERE / "T366_SOURCE_lab_seismicity"
SOURCE_DIR = HERE / "T366_SOURCE_Source_Data"
PROTOCOL = HERE / "T366_ACOUSTIC_CHILD_LADDER_PROTOCOL_v1_FROZEN.md"
STEM = "T366_ACOUSTIC_CHILD_LADDER"

RUNGS = [
    {"rung": -2, "role": "grandchild", "window_s": 1.0},
    {"rung": -1, "role": "child", "window_s": 2.0},
    {"rung": 0, "role": "current", "window_s": 4.0},
    {"rung": 1, "role": "parent", "window_s": 8.0},
    {"rung": 2, "role": "grandparent", "window_s": 16.0},
]
LANDMARKS = (0.5, 0.75, 1.0)
MERGE_SECONDS = 2.0
HORIZON_SECONDS = 10.0
RNG_SEED = 36620260812


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def trailing_sum(values: np.ndarray, width: int) -> np.ndarray:
    values = np.nan_to_num(np.asarray(values, dtype=float), nan=0.0)
    total = np.cumsum(np.insert(values, 0, 0.0))
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    return total[index + 1] - total[start]


def trailing_mean(values: np.ndarray, width: int) -> np.ndarray:
    total = np.cumsum(np.insert(np.asarray(values, dtype=float), 0, 0.0))
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    return (total[index + 1] - total[start]) / (index - start + 1)


def quadrant(x: float, y: float) -> str:
    if not np.isfinite(x) or not np.isfinite(y):
        return "undefined"
    if x >= 1 and y >= 1:
        return "Ab"
    if x >= 1 and y < 1:
        return "aB"
    if x < 1 and y < 1:
        return "bA"
    return "Ba"


def markdown_table(frame: pd.DataFrame, digits: int = 4) -> str:
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for values in frame.itertuples(index=False, name=None):
        row = []
        for value in values:
            if isinstance(value, (float, np.floating)):
                row.append("" if not np.isfinite(value) else f"{value:.{digits}f}")
            else:
                row.append(str(value))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def load_record(number: int) -> dict:
    stress_path = SOURCE_DIR / f"Fig5_stress_Wgn{number}.txt"
    catalog_path = CATALOG_DIR / f"AE_Wgn{number}_Pc_150_Axial.mat"
    stress_source = np.loadtxt(stress_path)
    time = stress_source[:, 0].astype(float)
    stress = stress_source[:, 1].astype(float)
    order = np.argsort(time)
    time, stress = time[order], stress[order]
    dt = float(np.median(np.diff(time)))
    split = int(0.8 * len(time))
    delta = np.diff(stress, prepend=stress[0])
    failure_index = int(split + np.argmin(delta[split:]))

    raw = loadmat(catalog_path, squeeze_me=True)
    event_time = np.asarray(raw["Time"], dtype=float)
    amplitude = np.asarray(raw["AdjAmp"], dtype=float)
    polarity = np.asarray(raw["pol"], dtype=float)
    finite = np.isfinite(event_time) & np.isfinite(amplitude) & np.isfinite(polarity) & (amplitude >= 0)
    event_time, amplitude, polarity = event_time[finite], amplitude[finite], polarity[finite]
    event_order = np.argsort(event_time)
    event_time, amplitude, polarity = event_time[event_order], amplitude[event_order], polarity[event_order]

    return {
        "record": f"Wgn{number}", "number": number,
        "stress_path": stress_path, "catalog_path": catalog_path,
        "time": time, "stress": stress, "dt": dt, "split": split,
        "failure_index": failure_index, "failure_time": float(time[failure_index]),
        "event_time": event_time, "amplitude": amplitude, "polarity": polarity,
    }


def bin_events(record: dict, raw_amplitude: bool = False, polarity_override: np.ndarray | None = None) -> dict[str, np.ndarray]:
    time = record["time"]
    event_time = record["event_time"]
    amplitude = record["amplitude"]
    polarity = record["polarity"] if polarity_override is None else np.asarray(polarity_override)
    keep = (event_time > time[0] - record["dt"]) & (event_time <= time[-1])
    event_time, amplitude, polarity = event_time[keep], amplitude[keep], polarity[keep]
    indices = np.searchsorted(time, event_time, side="left")
    valid = (indices >= 0) & (indices < len(time))
    indices, amplitude, polarity = indices[valid], amplitude[valid], polarity[valid]
    weight = amplitude if raw_amplitude else np.log1p(amplitude)
    connection = np.bincount(indices[polarity < -0.25], weights=weight[polarity < -0.25], minlength=len(time)).astype(float)
    movement = np.bincount(indices[polarity >= -0.25], weights=weight[polarity >= -0.25], minlength=len(time)).astype(float)
    count = np.bincount(indices, minlength=len(time)).astype(float)
    amplitude_sum = np.bincount(indices, weights=weight, minlength=len(time)).astype(float)
    return {"connection": connection, "movement": movement, "count": count, "amplitude": amplitude_sum}


def acoustic_coordinates(connection: np.ndarray, movement: np.ndarray, width: int, split: int) -> dict[str, np.ndarray | float]:
    c = trailing_sum(connection, width)
    m = trailing_sum(movement, width)
    total = c + m
    positive_calibration = total[:split][total[:split] > 0]
    if len(positive_calibration) < 20:
        q05, q95 = 0.0, max(float(np.nanmax(total[:split])), 1.0)
    else:
        q05, q95 = np.quantile(positive_calibration, [0.05, 0.95])
    x_t = np.clip(2 * (total - q05) / max(q95 - q05, 1e-12), 0, 2)
    x_m = np.divide(2 * m, total, out=np.full_like(total, np.nan), where=total > 0)
    active = (x_t >= 1) & (x_m >= 1) & np.isfinite(x_m)
    u, v = 2 * (x_t - 1), 2 * (x_m - 1)
    h = np.divide(2 * v, u + v, out=np.full_like(total, np.nan), where=active & ((u + v) > 1e-12))
    return {"C": c, "M": m, "total": total, "xT": x_t, "xM": x_m, "active": active, "u": u, "v": v, "h": h, "q05": float(q05), "q95": float(q95)}


def stress_coordinates(stress: np.ndarray, smooth_width: int, transfer_width: int, split: int) -> dict[str, np.ndarray | float]:
    smooth = trailing_mean(stress, smooth_width)
    delta = np.diff(smooth, prepend=smooth[0])
    accumulation = trailing_sum(np.maximum(delta, 0), transfer_width)
    release = trailing_sum(np.maximum(-delta, 0), transfer_width)
    activity = accumulation + release
    q05, q95 = np.quantile(smooth[:split], [0.05, 0.95])
    x_s = np.clip(2 * (smooth - q05) / max(q95 - q05, 1e-12), 0, 2)
    x_f = np.divide(2 * release, activity, out=np.ones_like(activity), where=activity > 1e-15)
    active = (x_s >= 1) & (x_f >= 1)
    u, v = 2 * (x_s - 1), 2 * (x_f - 1)
    h = np.divide(2 * v, u + v, out=np.full_like(v, np.nan), where=active & ((u + v) > 1e-12))
    return {"xT": x_s, "xM": x_f, "active": active, "u": u, "v": v, "h": h, "gap": np.abs(x_s - x_f), "q05": float(q05), "q95": float(q95)}


def build_acoustic_ladder(record: dict, bins: dict[str, np.ndarray]) -> dict[int, dict]:
    ladder = {}
    for item in RUNGS:
        width = max(1, int(round(item["window_s"] / record["dt"])))
        data = acoustic_coordinates(bins["connection"], bins["movement"], width, record["split"])
        data["gap"] = np.abs(data["xT"] - data["xM"])
        data["width"] = width
        ladder[item["rung"]] = data
    return ladder


def build_stress_ladder(record: dict) -> dict[int, dict]:
    ladder = {}
    for item in RUNGS:
        transfer = max(1, int(round(item["window_s"] / record["dt"])))
        smooth = max(1, int(round(item["window_s"] / (5 * record["dt"]))))
        data = stress_coordinates(record["stress"], smooth, transfer, record["split"])
        data["width"] = transfer
        ladder[item["rung"]] = data
    return ladder


def alarm_samples(ladder: dict[int, dict]) -> np.ndarray:
    gc, child, current = ladder[-2], ladder[-1], ladder[0]
    n = len(gc["h"])
    trigger = np.zeros(n, dtype=bool)
    trigger[1:] = child["active"][1:] & np.isfinite(child["h"][1:]) & (child["h"][1:] >= 0.5) & (
        (~child["active"][:-1]) | (~np.isfinite(child["h"][:-1])) | (child["h"][:-1] < 0.5)
    )
    gc_close = np.zeros(n, dtype=bool)
    child_close = np.zeros(n, dtype=bool)
    gw, cw = int(gc["width"]), int(child["width"])
    gc_close[gw:] = gc["gap"][gw:] < gc["gap"][:-gw]
    child_close[cw:] = child["gap"][cw:] < child["gap"][:-cw]
    current_open = (~current["active"]) | (~np.isfinite(current["h"])) | (current["h"] < 1)
    alarm = gc["active"] & child["active"] & np.isfinite(gc["h"]) & (gc["h"] >= 0.5) & trigger & current_open & gc_close & child_close
    return np.flatnonzero(alarm)


def merge_samples(samples: np.ndarray, gap: int) -> list[tuple[int, int, int]]:
    if len(samples) == 0:
        return []
    result = []
    start = last = int(samples[0])
    count = 1
    for value in samples[1:]:
        value = int(value)
        if value - last <= gap:
            last, count = value, count + 1
        else:
            result.append((start, last, count))
            start = last = value
            count = 1
    result.append((start, last, count))
    return result


def bout_frame(record: dict, samples: np.ndarray, channel: str) -> pd.DataFrame:
    merge_bins = max(1, int(round(MERGE_SECONDS / record["dt"])))
    horizon_bins = max(1, int(round(HORIZON_SECONDS / record["dt"])))
    rows = []
    holdout_samples = samples[samples >= record["split"]]
    for number, (start, end, count) in enumerate(merge_samples(holdout_samples, merge_bins), 1):
        contains = start <= record["failure_index"] <= start + horizon_bins
        rows.append({
            "record": record["record"], "channel": channel, "bout": number,
            "start_index": start, "end_alarm_index": end, "alarm_samples": count,
            "start_time_s": float(record["time"][start]), "lead_s": float(record["failure_time"] - record["time"][start]),
            "horizon_end_s": float(record["time"][min(start + horizon_bins, len(record["time"]) - 1)]),
            "contains_failure": bool(contains), "earlier_false": bool(start + horizon_bins < record["failure_index"]),
        })
    return pd.DataFrame(rows)


def first_associated(bouts: pd.DataFrame) -> pd.Series | None:
    if bouts.empty:
        return None
    associated = bouts[bouts["contains_failure"]]
    return None if associated.empty else associated.iloc[0]


def contiguous_onset(condition: np.ndarray, index: int) -> int | None:
    """Start of the true run that contains index, or the latest onset before it."""
    condition = np.asarray(condition, dtype=bool)
    if index < 0 or index >= len(condition):
        return None
    if not condition[index]:
        candidates = np.flatnonzero(condition[: index + 1])
        if len(candidates) == 0:
            return None
        index = int(candidates[-1])
    start = index
    while start > 0 and condition[start - 1]:
        start -= 1
    return int(start)


def event_order_metrics(record: dict, ladder: dict[int, dict], associated: pd.Series | None) -> dict:
    if associated is None:
        return {"grandchild_half_index": None, "child_half_index": None, "current_full_or_failure_index": None, "current_full_observed": False, "ordered": False}
    alarm = int(associated["start_index"])
    gc_condition = ladder[-2]["active"] & np.isfinite(ladder[-2]["h"]) & (ladder[-2]["h"] >= 0.5)
    child_condition = ladder[-1]["active"] & np.isfinite(ladder[-1]["h"]) & (ladder[-1]["h"] >= 0.5)
    gc_onset = contiguous_onset(gc_condition, alarm)
    child_onset = contiguous_onset(child_condition, alarm)
    current_full = ladder[0]["active"] & np.isfinite(ladder[0]["h"]) & (ladder[0]["h"] >= 1.0)
    after = np.flatnonzero(current_full[alarm : record["failure_index"] + 1]) + alarm
    current_observed = len(after) > 0
    current_index = int(after[0]) if current_observed else int(record["failure_index"])
    ordered = gc_onset is not None and child_onset is not None and gc_onset <= child_onset <= current_index
    return {
        "grandchild_half_index": gc_onset, "child_half_index": child_onset,
        "current_full_or_failure_index": current_index, "current_full_observed": bool(current_observed), "ordered": bool(ordered),
    }


def upward_crossings(data: dict, landmark: float) -> np.ndarray:
    h, active = data["h"], data["active"]
    valid = active[1:] & active[:-1] & np.isfinite(h[1:]) & np.isfinite(h[:-1])
    return np.flatnonzero(valid & (h[:-1] < landmark) & (h[1:] >= landmark)) + 1


def select_crossing(data: dict, landmark: float, failure: int, before_s: float, after_s: float, dt: float) -> int | None:
    cross = upward_crossings(data, landmark)
    lo, hi = failure - int(round(before_s / dt)), failure + int(round(after_s / dt))
    local = cross[(cross >= lo) & (cross <= hi)]
    if len(local) == 0:
        return None
    before = local[local <= failure]
    return int(before[-1] if len(before) else local[0])


def circular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs((a - b + 0.5) % 1 - 0.5)


def irrationality_address(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    valid = np.isfinite(x) & np.isfinite(y)
    x, y = x[valid], y[valid]
    if len(x) < 40:
        return {"x_P": np.nan, "x_R": np.nan, "history_coherence_mean": np.nan, "history_coherence_peak": np.nan}
    z = np.mod(np.arctan2(y - 1, x - 1) / (2 * np.pi), 1)
    resolutions = np.array([8, 16, 32, 64], dtype=float)
    occupied = [np.unique(np.floor(z * int(r)).astype(int) % int(r)).size for r in resolutions]
    x_p = float(np.clip(2 * np.polyfit(np.log(resolutions), np.log(np.maximum(occupied, 1)), 1)[0], 0, 2))
    half = len(z) // 2
    source, target = z[: half - 1], z[1:half]
    test_source, test_target = z[half:-1], z[half + 1 :]
    k = min(9, len(source))
    if k < 1 or len(test_source) < 1:
        return {"x_P": x_p, "x_R": np.nan, "history_coherence_mean": np.nan, "history_coherence_peak": np.nan}
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
    return {"x_P": x_p, "x_R": float(np.clip(2 * loss / max(null_loss, 1e-12), 0, 2)), "history_coherence_mean": float(np.mean(coherence)), "history_coherence_peak": float(np.max(coherence))}


def marker_error(marker: int, bouts: pd.DataFrame, horizon_bins: int) -> int:
    if bouts.empty:
        return 10**12
    errors = []
    for start in bouts["start_index"].astype(int):
        if start <= marker <= start + horizon_bins:
            errors.append(0)
        elif marker < start:
            errors.append(start - marker)
        else:
            errors.append(marker - (start + horizon_bins))
    return int(min(errors))


def threshold_baselines(record: dict, bins: dict[str, np.ndarray]) -> pd.DataFrame:
    width = max(1, int(round(1.0 / record["dt"])))
    count = trailing_sum(bins["count"], width)
    amp = trailing_sum(bins["amplitude"], width)
    rows = []
    for name, values in [("count_q95", count), ("amplitude_q95", amp)]:
        threshold = float(np.quantile(values[:record["split"]], 0.95))
        active = np.flatnonzero((values >= threshold) & (np.arange(len(values)) >= record["split"]))
        bouts = merge_samples(active, max(1, int(round(MERGE_SECONDS / record["dt"]))))
        horizon = int(round(HORIZON_SECONDS / record["dt"]))
        associated = [(s, e, c) for s, e, c in bouts if s <= record["failure_index"] <= s + horizon]
        lead = record["failure_time"] - record["time"][associated[0][0]] if associated else np.nan
        false = sum(s + horizon < record["failure_index"] for s, _, _ in bouts)
        rows.append({"record": record["record"], "baseline": name, "threshold": threshold, "associated": bool(associated), "lead_s": float(lead), "earlier_false_bouts": int(false), "total_bouts": len(bouts)})
    return pd.DataFrame(rows)


def analyze_record(record: dict, raw_amplitude: bool = False) -> dict:
    bins = bin_events(record, raw_amplitude=raw_amplitude)
    acoustic = build_acoustic_ladder(record, bins)
    bulk = build_stress_ladder(record)
    acoustic_bouts = bout_frame(record, alarm_samples(acoustic), "acoustic")
    bulk_bouts = bout_frame(record, alarm_samples(bulk), "bulk_stress")
    associated = first_associated(acoustic_bouts)

    landmark_rows = []
    for channel, ladder in [("acoustic", acoustic), ("bulk_stress", bulk)]:
        for item in RUNGS:
            for landmark in LANDMARKS:
                index = select_crossing(ladder[item["rung"]], landmark, record["failure_index"], 60, 10, record["dt"])
                landmark_rows.append({
                    "record": record["record"], "channel": channel, "rung": item["rung"], "role": item["role"], "landmark": landmark,
                    "cross_index": index if index is not None else np.nan,
                    "cross_time_s": float(record["time"][index]) if index is not None else np.nan,
                    "lead_s": float(record["failure_time"] - record["time"][index]) if index is not None else np.nan,
                })
    landmarks = pd.DataFrame(landmark_rows)

    addresses = []
    if associated is not None:
        alarm = int(associated["start_index"])
        for item in RUNGS:
            data = acoustic[item["rung"]]
            history = max(128, 8 * int(data["width"]))
            start = max(0, alarm - history + 1)
            addr = irrationality_address(data["xT"][start:alarm + 1], data["xM"][start:alarm + 1])
            addresses.append({
                "record": record["record"], "rung": item["rung"], "role": item["role"], "alarm_index": alarm,
                "xT_alarm": float(data["xT"][alarm]), "xM_alarm": float(data["xM"][alarm]), "h_alarm": float(data["h"][alarm]) if np.isfinite(data["h"][alarm]) else np.nan,
                "quadrant": quadrant(float(data["xT"][alarm]), float(data["xM"][alarm])), **addr,
            })
    addresses = pd.DataFrame(addresses)

    pseudo = {}
    horizon = max(1, int(round(HORIZON_SECONDS / record["dt"])))
    if not acoustic_bouts.empty:
        markers = np.linspace(record["split"], len(record["time"]) - 1, 1000).astype(int)
        errors = np.array([marker_error(marker, acoustic_bouts, horizon) for marker in markers]) * record["dt"]
        pseudo = {"real_error_s": float(marker_error(record["failure_index"], acoustic_bouts, horizon) * record["dt"]), "pseudo_median_error_s": float(np.median(errors)), "pseudo_zero_share": float(np.mean(errors == 0))}
    else:
        pseudo = {"real_error_s": np.inf, "pseudo_median_error_s": np.inf, "pseudo_zero_share": 0.0}

    return {
        "record": record, "bins": bins, "acoustic": acoustic, "bulk": bulk,
        "acoustic_bouts": acoustic_bouts, "bulk_bouts": bulk_bouts,
        "landmarks": landmarks, "addresses": addresses, "pseudo": pseudo,
        "baselines": threshold_baselines(record, bins),
    }


def control_analysis(record: dict, primary: dict) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED + record["number"])
    base_bins = primary["bins"]
    split = record["split"]
    rows = []

    def score(name: str, bins: dict[str, np.ndarray]) -> None:
        ladder = build_acoustic_ladder(record, bins)
        bouts = bout_frame(record, alarm_samples(ladder), name)
        associated = first_associated(bouts)
        rows.append({
            "record": record["record"], "control": name, "associated": associated is not None,
            "lead_s": float(associated["lead_s"]) if associated is not None else np.nan,
            "earlier_false_bouts": int(bouts["earlier_false"].sum()) if not bouts.empty else 0,
            "total_bouts": len(bouts),
        })

    reversed_bins = {key: values.copy() for key, values in base_bins.items()}
    for key in reversed_bins:
        reversed_bins[key][split:] = reversed_bins[key][split:][::-1]
    score("reversed_holdout", reversed_bins)

    order = rng.permutation(len(record["time"]) - split)
    permuted_bins = {key: values.copy() for key, values in base_bins.items()}
    for key in permuted_bins:
        permuted_bins[key][split:] = permuted_bins[key][split:][order]
    score("joint_bin_permutation", permuted_bins)

    polarity = record["polarity"].copy()
    event_holdout = record["event_time"] >= record["time"][split]
    polarity[event_holdout] = rng.permutation(polarity[event_holdout])
    polarity_bins = bin_events(record, polarity_override=polarity)
    score("polarity_permutation", polarity_bins)
    return pd.DataFrame(rows)


def summary_row(result: dict, evidence_role: str) -> dict:
    record = result["record"]
    acoustic = first_associated(result["acoustic_bouts"])
    bulk = first_associated(result["bulk_bouts"])
    return {
        "record": record["record"], "evidence_role": evidence_role,
        "stress_samples": len(record["time"]), "ae_events_total": len(record["event_time"]),
        "ae_events_synchronized": int(result["bins"]["count"].sum()),
        "failure_time_s": record["failure_time"],
        "acoustic_associated": acoustic is not None,
        "acoustic_lead_s": float(acoustic["lead_s"]) if acoustic is not None else np.nan,
        "acoustic_false_bouts": int(result["acoustic_bouts"]["earlier_false"].sum()) if not result["acoustic_bouts"].empty else 0,
        "acoustic_total_bouts": len(result["acoustic_bouts"]),
        "bulk_associated": bulk is not None,
        "bulk_lead_s": float(bulk["lead_s"]) if bulk is not None else np.nan,
        "bulk_false_bouts": int(result["bulk_bouts"]["earlier_false"].sum()) if not result["bulk_bouts"].empty else 0,
        "bulk_total_bouts": len(result["bulk_bouts"]),
        **result["pseudo"],
    }


def make_timeseries(result: dict) -> pd.DataFrame:
    record = result["record"]
    out = {
        "record": np.repeat(record["record"], len(record["time"])), "time_s": record["time"],
        "time_to_failure_s": record["time"] - record["failure_time"], "stress": record["stress"],
        "ae_count_bin": result["bins"]["count"], "ae_log_amplitude_bin": result["bins"]["amplitude"],
    }
    for prefix, ladder in [("ae", result["acoustic"]), ("bulk", result["bulk"])]:
        for item in RUNGS:
            data = ladder[item["rung"]]
            name = f"{prefix}_r{item['rung']}_{item['role']}"
            out[f"{name}_xT"] = data["xT"]
            out[f"{name}_xM"] = data["xM"]
            out[f"{name}_h"] = data["h"]
            out[f"{name}_active_Ab"] = data["active"]
    return pd.DataFrame(out)


def plot_results(results: dict[int, dict], summaries: pd.DataFrame, controls: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(17, 10), constrained_layout=True)
    colors = {-2: "#6a51a3", -1: "#3182bd", 0: "#31a354", 1: "#fd8d3c", 2: "#de2d26"}
    for column, number in enumerate([23, 20]):
        result = results[number]
        record = result["record"]
        ax = axes[0, column]
        lookback = 60 if number == 23 else 60
        mask = (record["time"] >= record["failure_time"] - lookback) & (record["time"] <= record["failure_time"] + 3)
        t = record["time"][mask] - record["failure_time"]
        stress = record["stress"][mask]
        ax.plot(t, (stress - np.nanmin(stress)) / max(np.ptp(stress), 1e-12), color="#222222", lw=1.5, label="bulk stress (local normalized)")
        activity = trailing_sum(result["bins"]["amplitude"], max(1, int(round(1 / record["dt"]))))[mask]
        activity = activity / max(np.nanquantile(activity, 0.99), 1e-12)
        ax.plot(t, np.clip(activity, 0, 2), color="#d95f0e", alpha=0.8, lw=1.1, label="1 s acoustic activity")
        ax.axvline(0, color="#c51b7d", ls="--", lw=1.5, label="failure")
        associated = first_associated(result["acoustic_bouts"])
        if associated is not None:
            alarm_t = float(associated["start_time_s"] - record["failure_time"])
            ax.axvspan(alarm_t, min(alarm_t + HORIZON_SECONDS, 3), color="#fdae6b", alpha=0.28, label="ARA acoustic forecast")
        ax.set_title(f"{record['record']}: acoustic child channel vs bulk parent")
        ax.set_xlabel("seconds relative to failure")
        ax.set_ylabel("local display scale")
        ax.grid(alpha=0.18)
        ax.legend(fontsize=8, loc="upper left")

        ax = axes[1, column]
        for item in RUNGS:
            h = result["acoustic"][item["rung"]]["h"][mask]
            ax.plot(t, h, color=colors[item["rung"]], lw=1.1, label=f"{item['role']} ({item['window_s']:g}s)")
        ax.axhline(0.5, color="#777777", ls=":", lw=1)
        ax.axhline(1.0, color="#2ca25f", ls="--", lw=1.2)
        ax.axvline(0, color="#c51b7d", ls="--", lw=1.2)
        ax.set_ylim(-0.05, 2.05)
        ax.set_title(f"{record['record']}: acoustic Ab child coordinate")
        ax.set_xlabel("seconds relative to failure")
        ax.set_ylabel("child ARA h (0-2)")
        ax.grid(alpha=0.18)
        ax.legend(fontsize=7, ncol=2, loc="upper left")

    holdout = results[23]
    record = holdout["record"]
    ax = axes[0, 2]
    mask = (record["time"] >= record["failure_time"] - 60) & (record["time"] <= record["failure_time"] + 3)
    for item in RUNGS:
        data = holdout["acoustic"][item["rung"]]
        ax.plot(data["xT"][mask], data["xM"][mask], color=colors[item["rung"]], lw=0.8, alpha=0.75, label=item["role"])
        ax.scatter(data["xT"][record["failure_index"]], data["xM"][record["failure_index"]], s=22, color=colors[item["rung"]])
    ax.axvline(1, color="#555555", lw=0.9)
    ax.axhline(1, color="#555555", lw=0.9)
    ax.set_xlim(0, 2.03); ax.set_ylim(0, 2.03)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Wgn23 acoustic relation paths (last 60 s)")
    ax.set_xlabel("xT: exposed acoustic parent")
    ax.set_ylabel("xM: movement vs connection")
    ax.grid(alpha=0.18)
    ax.legend(fontsize=7, ncol=2)

    ax = axes[1, 2]
    row = summaries[summaries["record"] == "Wgn23"].iloc[0]
    acoustic_lead = row["acoustic_lead_s"] if np.isfinite(row["acoustic_lead_s"]) else 0
    bulk_lead = row["bulk_lead_s"] if np.isfinite(row["bulk_lead_s"]) else 0
    control23 = controls[controls["record"] == "Wgn23"]
    labels = ["ARA acoustic", "bulk stress"] + list(control23["control"])
    leads = [acoustic_lead, bulk_lead] + [value if np.isfinite(value) else 0 for value in control23["lead_s"]]
    bars = ax.bar(np.arange(len(labels)), leads, color=["#d95f0e", "#555555", "#bdbdbd", "#bdbdbd", "#bdbdbd"])
    for bar, value in zip(bars, leads):
        ax.text(bar.get_x() + bar.get_width() / 2, max(value, 0) + 0.15, f"{value:.2f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(np.arange(len(labels)), labels, rotation=28, ha="right")
    ax.set_ylabel("associated warning lead (s; 0 = none)")
    ax.set_title("Wgn23 frozen warning and chronology controls")
    ax.grid(axis="y", alpha=0.18)

    fig.suptitle("T366 - acoustic children versus the connection-heavy bulk parent", fontsize=17, fontweight="bold")
    fig.savefig(path, dpi=190)
    plt.close(fig)


def main() -> None:
    records = {number: load_record(number) for number in (20, 23)}
    results = {number: analyze_record(record) for number, record in records.items()}
    raw_results = {number: analyze_record(record, raw_amplitude=True) for number, record in records.items()}
    controls = pd.concat([control_analysis(records[number], results[number]) for number in (20, 23)], ignore_index=True)
    summaries = pd.DataFrame([summary_row(results[23], "primary holdout"), summary_row(results[20], "disclosed development")])
    raw_summaries = pd.DataFrame([summary_row(raw_results[23], "raw-amplitude sensitivity"), summary_row(raw_results[20], "raw-amplitude sensitivity")])
    bouts = pd.concat([r["acoustic_bouts"] for r in results.values()] + [r["bulk_bouts"] for r in results.values()], ignore_index=True)
    landmarks = pd.concat([r["landmarks"] for r in results.values()], ignore_index=True)
    addresses = pd.concat([r["addresses"] for r in results.values()], ignore_index=True)
    baselines = pd.concat([r["baselines"] for r in results.values()], ignore_index=True)
    timeseries = pd.concat([make_timeseries(results[number]) for number in (20, 23)], ignore_index=True)

    holdout = summaries[summaries["record"] == "Wgn23"].iloc[0]
    holdout_result = results[23]
    primary_bout = first_associated(holdout_result["acoustic_bouts"])
    bulk_bout = first_associated(holdout_result["bulk_bouts"])
    event_landmarks = landmarks[(landmarks["record"] == "Wgn23") & (landmarks["channel"] == "acoustic")]
    order_metrics = event_order_metrics(records[23], holdout_result["acoustic"], primary_bout)
    event_order = pd.DataFrame([{
        "record": "Wgn23",
        **order_metrics,
        "grandchild_half_lead_s": records[23]["failure_time"] - records[23]["time"][order_metrics["grandchild_half_index"]] if order_metrics["grandchild_half_index"] is not None else np.nan,
        "child_half_lead_s": records[23]["failure_time"] - records[23]["time"][order_metrics["child_half_index"]] if order_metrics["child_half_index"] is not None else np.nan,
        "current_full_or_failure_lead_s": records[23]["failure_time"] - records[23]["time"][order_metrics["current_full_or_failure_index"]] if order_metrics["current_full_or_failure_index"] is not None else np.nan,
    }])
    child_order = bool(order_metrics["ordered"])

    control23 = controls[controls["record"] == "Wgn23"]
    real_lead = float(primary_bout["lead_s"]) if primary_bout is not None else np.nan
    real_false = int(holdout_result["acoustic_bouts"]["earlier_false"].sum()) if not holdout_result["acoustic_bouts"].empty else 0
    control_match = False
    if np.isfinite(real_lead):
        control_match = bool(((control23["associated"]) & (control23["lead_s"] >= real_lead - records[23]["dt"]) & (control23["earlier_false_bouts"] <= real_false)).any())

    source_rows = []
    for number, record in records.items():
        source_rows.extend([
            {"record": record["record"], "kind": "stress", "file": record["stress_path"].name, "sha256": digest(record["stress_path"]), "rows": len(record["time"])},
            {"record": record["record"], "kind": "AE catalog", "file": record["catalog_path"].name, "sha256": digest(record["catalog_path"]), "rows": len(record["event_time"])},
        ])
    source_qa = pd.DataFrame(source_rows)

    gates = pd.DataFrame([
        {"gate": 1, "name": "source and causality QA", "pass": bool(len(source_qa) == 4 and all(r["split"] < r["failure_index"] for r in records.values())), "detail": "Four source hashes recorded; all features trailing; calibration ends before failure."},
        {"gate": 2, "name": "holdout acoustic forecast", "pass": primary_bout is not None and float(primary_bout["lead_s"]) > 0, "detail": "Wgn23 10-second frozen acoustic horizon."},
        {"gate": 3, "name": "false-alarm boundary", "pass": real_false <= 1, "detail": f"Earlier Wgn23 acoustic bouts: {real_false}."},
        {"gate": 4, "name": "child order", "pass": child_order, "detail": "Grandchild half -> child half -> current full/failure."},
        {"gate": 5, "name": "bulk comparison", "pass": primary_bout is not None and (bulk_bout is None or float(primary_bout["lead_s"]) > float(bulk_bout["lead_s"])), "detail": "Acoustic warning must precede bulk stress warning or bulk must be silent."},
        {"gate": 6, "name": "marker specificity", "pass": holdout_result["pseudo"]["real_error_s"] < holdout_result["pseudo"]["pseudo_median_error_s"], "detail": f"real {holdout_result['pseudo']['real_error_s']:.3f}s vs pseudo median {holdout_result['pseudo']['pseudo_median_error_s']:.3f}s."},
        {"gate": 7, "name": "control specificity", "pass": not control_match, "detail": "No broken-chronology control may match both lead and false-alarm burden."},
        {"gate": 8, "name": "development repeat", "pass": first_associated(results[20]["acoustic_bouts"]) is not None, "detail": "Wgn20 scored unchanged and cannot rescue Wgn23."},
        {"gate": 9, "name": "irrationality address", "pass": bool(len(addresses[addresses["record"] == "Wgn23"]) > 0 and addresses[addresses["record"] == "Wgn23"][["x_P", "x_R"]].notna().all().all()), "detail": "All finite Wgn23 rung addresses reported at the acoustic alarm."},
    ])

    supported = bool(gates["pass"].all())
    status = "SUPPORTED ON THIS TWO-RECORD ARCHIVE" if supported else "NOT SUPPORTED UNDER THE FROZEN T366 GATES"
    result_json = {
        "test": "T366 acoustic child ladder", "status": status,
        "protocol_sha256": digest(PROTOCOL), "rng_seed": RNG_SEED,
        "records": json.loads(summaries.to_json(orient="records")),
        "gates": json.loads(gates.to_json(orient="records")),
        "source_qa": json.loads(source_qa.to_json(orient="records")),
        "evidence_boundary": "Event-level AE catalogue plus 10 Hz stress; not continuous raw-waveform recovery and not an independent earthquake predictor.",
    }

    outputs = {
        f"{STEM}_SUMMARY.csv": summaries, f"{STEM}_BOUTS.csv": bouts,
        f"{STEM}_LANDMARKS.csv": landmarks, f"{STEM}_IRRATIONALITY_ADDRESS.csv": addresses,
        f"{STEM}_CONTROLS.csv": controls, f"{STEM}_BASELINES.csv": baselines,
        f"{STEM}_RAW_AMPLITUDE_SENSITIVITY.csv": raw_summaries,
        f"{STEM}_SOURCE_QA.csv": source_qa, f"{STEM}_FROZEN_GATES.csv": gates,
        f"{STEM}_EVENT_ORDER.csv": event_order,
        f"{STEM}_TIMESERIES.csv": timeseries,
    }
    for name, frame in outputs.items():
        frame.to_csv(HERE / name, index=False)
    (HERE / f"{STEM}_RESULTS.json").write_text(json.dumps(result_json, indent=2, allow_nan=False), encoding="utf-8")
    plot_results(results, summaries, controls, HERE / f"{STEM}_FIGURE.png")

    report = f"""# T366 - acoustic children before connection-heavy granite failure

**Date:** 12 August 2026  
**Frozen verdict:** **{status}**

## Answer first

The frozen test asked whether acoustic/vibration children form an ordered ARA
handover before the bulk-stress parent visibly releases. The primary Wgn23
holdout result was {'an event-associated acoustic warning' if primary_bout is not None else 'no event-associated acoustic warning'}.
Its lead was {real_lead:.4f} s when finite, with {real_false} earlier false bouts.
The bulk comparator {'also warned' if bulk_bout is not None else 'did not produce an associated advance warning'}.

This result concerns the frozen ARA timing rule. The source paper independently
already reports accelerating AE rates and changing source mechanisms before
failure; those established observations are context, not an ARA discovery.

## Exact measurement

- **Connection child:** compression-type AE packets (`pol < -0.25`).
- **Movement child:** shear/tensile AE packets (`pol >= -0.25`).
- **Parent exposure:** recent summed `log(1 + adjusted amplitude)`.
- **Rungs:** 1, 2, 4, 8 and 16 s trailing windows.
- **Bulk comparator:** trailing normalized stress plus accumulation/release.
- **Event:** largest negative 10 Hz stress step in the final 20%.

No future sample enters any coordinate. A zero-event window remains undefined
on the mixing axis instead of being assigned a ridge.

## Record summary

{markdown_table(summaries)}

## Wgn23 frozen gates

{markdown_table(gates)}

## Event-local acoustic landmarks

The following are the last upward landmark crossings found inside a broad
60-second diagnostic window. Because the child coordinate can leave and re-enter
`Ab`, they are not all members of the final alarm bout and must not be read as
one ordered cascade.

{markdown_table(event_landmarks[["rung", "role", "landmark", "lead_s"]])}

The actual event-associated run, evaluated from the alarm backward through its
contiguous active state, was:

{markdown_table(event_order[["grandchild_half_lead_s", "child_half_lead_s", "current_full_observed", "current_full_or_failure_lead_s", "ordered"]])}

Thus the final bout did preserve grandchild -> child order, but the current rung
did not reach full closure before the macroscopic stress drop.

## Irrationality Di-ARA address at warning

{markdown_table(addresses[addresses["record"] == "Wgn23"])}

Only occupied quadrants are interpreted. The test does not require one fault
identity to use all four quadrants.

## Chronology controls

{markdown_table(control23)}

## Sensitivity and simple baselines

{markdown_table(raw_summaries)}

{markdown_table(baselines)}

The raw-amplitude calculation is diagnostic only. It cannot replace the frozen
log-amplitude result.

## ARA interpretation

If the acoustic gate passes while bulk stress does not warn, the specific
supported statement is that smaller internal connection failures expose a
movement channel before the coarse connection-heavy parent releases. If it
fails, that does not erase the observed AE acceleration; it rejects this
particular half-ridge alarm and/or scale ordering as a reliable description of
that acceleration.

## Established-science crosswalk

The experimenters describe long-term damage accumulation, crack alignment and
localization, followed by shorter rupture-nucleation processes. They identify
compression, shear and tensile AE sources from first-motion polarities. T366's
connection/movement split is an ARA crosswalk onto those measured source types;
it is not a replacement for their mechanics or an assertion that every
compression event is ontologically a Space wave.

## Evidence boundary

This archive supplies detected AE events rather than the continuous 10 MHz
waveforms. T366 can test event-scale child ordering but cannot recover quiet
sub-threshold vibration or waveform phase. There are only two synchronized
stress/catalogue records here, and Wgn20 was already viewed coarsely. A positive
result therefore warrants a waveform-rich independent archive, not a field
earthquake-prediction claim.
"""
    (HERE / f"{STEM}_REPORT_2026-08-12.md").write_text(report, encoding="utf-8")

    print(status)
    print(summaries.to_string(index=False))
    print(gates.to_string(index=False))


if __name__ == "__main__":
    main()
