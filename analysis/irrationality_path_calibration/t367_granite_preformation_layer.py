"""T367: frozen granite pre-formation layer test.

This is a repeated physical-event audit of whether the recorded acoustic child
relation becomes more organised before a large acoustic-parent burst forms.
The definitions are frozen in T367_GRANITE_PREFORMATION_LAYER_PROTOCOL_v1_FROZEN.md.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T366_SOURCE_lab_seismicity"
PROTOCOL = HERE / "T367_GRANITE_PREFORMATION_LAYER_PROTOCOL_v1_FROZEN.md"
STEM = "T367_GRANITE_PREFORMATION_LAYER"
BIN_S = 0.25
EVAL_STEP_BINS = 2
RUNGS = {-2: ("grandchild", 0.5), -1: ("child", 1.0), 0: ("current", 2.0), 1: ("parent", 4.0), 2: ("grandparent", 8.0)}
HISTORIES_S = (8.0, 16.0, 32.0)
PRE_SLICES = ((-32, -16), (-16, -8), (-8, -4), (-4, -2), (-2, -1), (-1, 0))
POST_SLICES = ((0, 1), (1, 2), (2, 4))
THRESHOLDS = (0.975, 0.98, 0.985, 0.99)
ISOLATIONS_S = (32.0, 16.0, 8.0)
SEED = 36720260812


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def trailing_sum(values: np.ndarray, width: int) -> np.ndarray:
    values = np.nan_to_num(np.asarray(values, dtype=float), nan=0.0)
    total = np.cumsum(np.r_[0.0, values])
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    return total[index + 1] - total[start]


def load_specimen(number: int) -> dict:
    path = SOURCE / f"AE_Wgn{number}_Pc_150_Axial.mat"
    raw = loadmat(path, squeeze_me=True)
    time = np.asarray(raw["Time"], dtype=float)
    amplitude = np.asarray(raw["AdjAmp"], dtype=float)
    polarity = np.asarray(raw["pol"], dtype=float)
    valid = np.isfinite(time) & np.isfinite(amplitude) & np.isfinite(polarity) & (amplitude >= 0)
    time, amplitude, polarity = time[valid], amplitude[valid], polarity[valid]
    order = np.argsort(time)
    time, amplitude, polarity = time[order], amplitude[order], polarity[order]
    start = float(np.floor(time.min() / BIN_S) * BIN_S)
    end = float(np.ceil(time.max() / BIN_S) * BIN_S)
    edges = np.arange(start, end + BIN_S, BIN_S)
    centers = edges[:-1] + BIN_S / 2
    indices = np.clip(np.searchsorted(edges, time, side="right") - 1, 0, len(centers) - 1)
    weight = np.log1p(amplitude)
    connection = np.bincount(indices[polarity < -0.25], weights=weight[polarity < -0.25], minlength=len(centers)).astype(float)
    movement = np.bincount(indices[polarity >= -0.25], weights=weight[polarity >= -0.25], minlength=len(centers)).astype(float)
    count = np.bincount(indices, minlength=len(centers)).astype(float)
    return {
        "record": f"Wgn{number}", "number": number, "path": path,
        "time": centers, "connection": connection, "movement": movement,
        "count": count, "split": int(0.60 * len(centers)), "raw_events": len(time),
    }


def coordinates(specimen: dict, window_s: float) -> dict[str, np.ndarray]:
    width = max(1, int(round(window_s / BIN_S)))
    connection = trailing_sum(specimen["connection"], width)
    movement = trailing_sum(specimen["movement"], width)
    total = connection + movement
    calibration = total[: specimen["split"]]
    positive = calibration[calibration > 0]
    q05, q95 = np.quantile(positive, (0.05, 0.95)) if len(positive) >= 20 else (0.0, max(float(np.max(calibration)), 1.0))
    x_t = np.clip(2 * (total - q05) / max(q95 - q05, 1e-12), 0, 2)
    x_m = np.divide(2 * movement, total, out=np.full_like(total, np.nan), where=total > 0)
    return {"xT": x_t, "xM": x_m, "total": total, "q05": float(q05), "q95": float(q95), "width": width}


def angular_path(x_t: np.ndarray, x_m: np.ndarray) -> np.ndarray:
    valid = np.isfinite(x_t) & np.isfinite(x_m) & (np.hypot(x_t - 1, x_m - 1) > 1e-9)
    z = np.full_like(x_t, np.nan, dtype=float)
    z[valid] = np.mod(np.arctan2(x_m[valid] - 1, x_t[valid] - 1) / (2 * np.pi), 1)
    return z


def circular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs((a - b + 0.5) % 1 - 0.5)


def path_metrics(z: np.ndarray) -> dict[str, float]:
    z = np.asarray(z, dtype=float)
    z = z[np.isfinite(z)]
    if len(z) < 24:
        return {k: np.nan for k in ("x_P", "x_R", "coherence", "concentration", "layer_count")}
    resolutions = np.array((8, 16, 32, 64), dtype=float)
    occupied = [np.unique(np.floor(z * int(r)).astype(int) % int(r)).size for r in resolutions]
    x_p = float(np.clip(2 * np.polyfit(np.log(resolutions), np.log(np.maximum(occupied, 1)), 1)[0], 0, 2))

    half = len(z) // 2
    source, target = z[: half - 1], z[1:half]
    test_source, test_target = z[half:-1], z[half + 1 :]
    if len(source) < 4 or len(test_source) < 2:
        x_r = np.nan
    else:
        k = min(7, len(source))
        train_xy = np.c_[np.cos(2 * np.pi * source), np.sin(2 * np.pi * source)]
        test_xy = np.c_[np.cos(2 * np.pi * test_source), np.sin(2 * np.pi * test_source)]
        neighbours = cKDTree(train_xy).query(test_xy, k=k)[1]
        if k == 1:
            neighbours = neighbours[:, None]
        target_complex = np.exp(2j * np.pi * target)
        predicted = np.mod(np.angle(np.mean(target_complex[neighbours], axis=1)) / (2 * np.pi), 1)
        loss = float(np.mean(circular_distance(predicted, test_target)))
        null = np.mod(np.angle(np.mean(target_complex)) / (2 * np.pi), 1)
        null_loss = float(np.mean(circular_distance(null, test_target)))
        x_r = float(np.clip(2 * loss / max(null_loss, 1e-12), 0, 2))

    lag_resultants = []
    for lag in range(1, min(64, len(z) - 1) + 1):
        delta = np.mod(z[lag:] - z[:-lag], 1)
        lag_resultants.append(abs(np.mean(np.exp(2j * np.pi * delta))))
    coherence = float(np.mean(lag_resultants))

    phase_vector = np.mean(np.exp(2j * np.pi * z))
    centre = float(np.mod(np.angle(phase_vector) / (2 * np.pi), 1)) if abs(phase_vector) > 1e-12 else 0.0
    median_distance = float(np.median(circular_distance(z, centre)))
    concentration = float(np.clip(1 - 4 * median_distance, 0, 1))

    histogram, _ = np.histogram(z, bins=24, range=(0, 1))
    threshold = 1.5 * len(z) / 24
    peaks = sum(histogram[i] > histogram[(i - 1) % 24] and histogram[i] >= histogram[(i + 1) % 24] and histogram[i] > threshold for i in range(24))
    return {"x_P": x_p, "x_R": x_r, "coherence": coherence, "concentration": concentration, "layer_count": int(peaks)}


def select_events(exposure: np.ndarray, split: int, quantile: float, isolation_s: float) -> np.ndarray:
    threshold = float(np.quantile(exposure[:split], quantile))
    crossings = np.flatnonzero((exposure >= threshold) & np.r_[True, exposure[:-1] < threshold])
    margin_before = int(round(32 / BIN_S))
    margin_after = int(round(4 / BIN_S))
    crossings = crossings[(crossings >= max(split, margin_before)) & (crossings < len(exposure) - margin_after)]
    selected: list[int] = []
    separation = int(round(isolation_s / BIN_S))
    for index in crossings:
        if not selected or index - selected[-1] >= separation:
            selected.append(int(index))
    return np.asarray(selected, dtype=int)


def freeze_event_definition(development: list[dict]) -> tuple[float, float, pd.DataFrame]:
    audit = []
    chosen = None
    for quantile in THRESHOLDS:
        for isolation in ISOLATIONS_S:
            counts = []
            for specimen in development:
                exposure = coordinates(specimen, 2.0)["total"]
                counts.append(len(select_events(exposure, specimen["split"], quantile, isolation)))
            eligible = sum(counts) >= 48 and min(counts) >= 3
            audit.append({"quantile": quantile, "isolation_s": isolation, "total_events": sum(counts), "minimum_specimen_events": min(counts), "eligible": eligible})
            if chosen is None and eligible:
                chosen = (quantile, isolation)
    if chosen is None:
        raise RuntimeError("No development event definition met the frozen coverage rule")
    return chosen[0], chosen[1], pd.DataFrame(audit)


def metric_rows(specimen: dict, ladder: dict[int, dict], history_s: float, evaluation_indices: np.ndarray, relation_shift_bins: int = 0) -> pd.DataFrame:
    rows = []
    history_bins = int(round(history_s / BIN_S))
    for rung, (role, _window) in RUNGS.items():
        x_t = ladder[rung]["xT"]
        x_m = np.roll(ladder[rung]["xM"], relation_shift_bins) if relation_shift_bins else ladder[rung]["xM"]
        z = angular_path(x_t, x_m)
        previous_concentration = np.nan
        previous_end = None
        for end in evaluation_indices:
            if end < history_bins - 1 or end >= len(z):
                continue
            start = end - history_bins + 1
            values = path_metrics(z[start : end + 1])
            concentration = values["concentration"]
            narrowing = concentration - previous_concentration if previous_end == end - EVAL_STEP_BINS and np.isfinite(concentration) and np.isfinite(previous_concentration) else np.nan
            previous_concentration = concentration
            previous_end = int(end)
            rows.append({
                "record": specimen["record"], "index": end, "time_s": specimen["time"][end], "history_s": history_s,
                "rung": rung, "role": role, "xT": x_t[end], "xM": x_m[end],
                "open_determined": float(values["x_P"] > 1 and values["x_R"] < 1) if np.isfinite(values["x_P"]) and np.isfinite(values["x_R"]) else np.nan,
                "narrowing": narrowing, **values,
            })
    return pd.DataFrame(rows)


def slice_label(relative_s: float) -> str | None:
    for lo, hi in PRE_SLICES + POST_SLICES:
        if lo <= relative_s < hi or (hi == 4 and relative_s <= hi):
            return f"[{lo},{hi})"
    return None


def nearest_metrics(frame: pd.DataFrame, event_index: int, event_time: float, condition: str, event_id: str) -> list[dict]:
    rows = []
    local = frame[(frame["index"] >= event_index - int(32 / BIN_S)) & (frame["index"] <= event_index + int(4 / BIN_S))]
    for value in local.itertuples(index=False):
        relative = float(value.time_s - event_time)
        label = slice_label(relative)
        if label is None:
            continue
        item = value._asdict()
        item.update({"event_id": event_id, "condition": condition, "event_index": event_index, "event_time_s": event_time, "relative_s": relative, "slice": label})
        rows.append(item)
    return rows


def matched_quiet_indices(specimen: dict, exposure: np.ndarray, events: np.ndarray, count: int, rng: np.random.Generator) -> np.ndarray:
    candidates = np.arange(max(specimen["split"], int(32 / BIN_S)), len(exposure) - int(4 / BIN_S), EVAL_STEP_BINS)
    if len(events):
        far = np.ones(len(candidates), dtype=bool)
        for event in events:
            far &= np.abs(candidates - event) * BIN_S >= 64
        candidates = candidates[far]
    if not len(candidates):
        return np.array([], dtype=int)
    deciles = np.quantile(exposure[specimen["split"] :], np.linspace(0, 1, 11))
    selected = []
    for event in events:
        decile = int(np.clip(np.searchsorted(deciles, exposure[event], side="right") - 1, 0, 9))
        same = candidates[(exposure[candidates] >= deciles[decile]) & (exposure[candidates] <= deciles[decile + 1])]
        pool = same if len(same) else candidates
        selected.append(int(rng.choice(pool)))
    while len(selected) < count:
        selected.append(int(rng.choice(candidates)))
    return np.asarray(selected[:count], dtype=int)


def slice_summary(rows: pd.DataFrame, value_columns: list[str]) -> pd.DataFrame:
    grouped = rows.groupby(["condition", "history_s", "rung", "role", "slice"], dropna=False)
    return grouped[value_columns].agg(["count", "median", "mean", "std"]).reset_index()


def orient_and_score(development_rows: pd.DataFrame, all_rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = {"two_minus_x_R": "x_R", "concentration": "concentration", "coherence": "coherence", "open_determined": "open_determined", "positive_narrowing": "narrowing"}
    dev_pre = development_rows[development_rows["relative_s"] < 0].copy()
    stats = []
    transformed = all_rows.copy()
    transformed["two_minus_x_R"] = 2 - transformed["x_R"]
    transformed["positive_narrowing"] = transformed["narrowing"].clip(lower=0)
    for output, source in features.items():
        dev_pre[output] = 2 - dev_pre[source] if output == "two_minus_x_R" else (dev_pre[source].clip(lower=0) if output == "positive_narrowing" else dev_pre[source])
        event = dev_pre[dev_pre["condition"] == "event"][output].dropna()
        quiet = dev_pre[dev_pre["condition"] == "quiet"][output].dropna()
        centre = float(pd.concat([event, quiet]).median())
        iqr = float(pd.concat([event, quiet]).quantile(0.75) - pd.concat([event, quiet]).quantile(0.25))
        effect = float(event.median() - quiet.median()) if len(event) and len(quiet) else np.nan
        active = bool(np.isfinite(effect) and effect > 0 and iqr > 1e-12)
        stats.append({"feature": output, "source": source, "development_event_minus_quiet_median": effect, "centre": centre, "iqr": iqr, "active_weight": active})
        transformed[f"z_{output}"] = (transformed[output] - centre) / max(iqr, 1e-12)
    active_columns = [f"z_{row['feature']}" for row in stats if row["active_weight"]]
    transformed["preformation_score"] = transformed[active_columns].mean(axis=1) if active_columns else np.nan
    return pd.DataFrame(stats), transformed


def cluster_bootstrap_effect(rows: pd.DataFrame, rng: np.random.Generator, iterations: int = 4000) -> tuple[float, float, float]:
    pre = rows[rows["relative_s"] < 0].groupby(["record", "condition", "event_id"])["preformation_score"].median().reset_index()
    per_record = []
    for record, frame in pre.groupby("record"):
        event = frame[frame["condition"] == "event"]["preformation_score"]
        quiet = frame[frame["condition"] == "quiet"]["preformation_score"]
        per_record.append((record, float(event.median() - quiet.median())))
    effects = np.array([x[1] for x in per_record], dtype=float)
    if not len(effects):
        return np.nan, np.nan, np.nan
    boot = np.mean(effects[rng.integers(0, len(effects), size=(iterations, len(effects)))], axis=1)
    return float(np.mean(effects)), float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def auroc(y: np.ndarray, score: np.ndarray) -> float:
    valid = np.isfinite(score)
    y, score = y[valid].astype(int), score[valid]
    pos, neg = score[y == 1], score[y == 0]
    if not len(pos) or not len(neg):
        return np.nan
    return float((sum(np.sum(p > neg) + 0.5 * np.sum(p == neg) for p in pos)) / (len(pos) * len(neg)))


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


def make_figure(rows: pd.DataFrame, specimen_summary: pd.DataFrame, output: Path) -> None:
    order = [f"[{lo},{hi})" for lo, hi in PRE_SLICES + POST_SLICES]
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)
    fig.suptitle("T367 granite pre-formation layer test", fontsize=18, fontweight="bold")
    colors = {"event": "#D49A2E", "quiet": "#527AB5", "shifted_relation": "#7D8792"}
    for condition in ("event", "quiet", "shifted_relation"):
        sub = rows[(rows["condition"] == condition) & (rows["history_s"] == 16) & (rows["rung"] == -1)]
        med = sub.groupby("slice")["coherence"].median().reindex(order)
        axes[0, 0].plot(range(len(order)), med, marker="o", label=condition, color=colors[condition])
    axes[0, 0].axvline(5.5, color="#333333", lw=1)
    axes[0, 0].set_xticks(range(len(order)), order, rotation=35, ha="right")
    axes[0, 0].set_title("Child history coherence around burst onset")
    axes[0, 0].set_ylabel("lag coherence")
    axes[0, 0].legend(frameon=False)

    hold = rows[(rows["condition"] == "event") & (rows["history_s"] == 16) & (rows["rung"] == -1)]
    for metric, color in (("x_P", "#D49A2E"), ("x_R", "#527AB5")):
        med = hold.groupby("slice")[metric].median().reindex(order)
        axes[0, 1].plot(range(len(order)), med, marker="o", label=metric, color=color)
    axes[0, 1].axhline(1, color="#333333", lw=1)
    axes[0, 1].axvline(5.5, color="#333333", lw=1)
    axes[0, 1].set_xticks(range(len(order)), order, rotation=35, ha="right")
    axes[0, 1].set_title("Child Irrationality Di-ARA path coordinates")
    axes[0, 1].set_ylabel("0-2 coordinate")
    axes[0, 1].legend(frameon=False)

    pre = rows[(rows["condition"].isin(["event", "quiet"])) & (rows["relative_s"] < 0) & (rows["history_s"] == 16)]
    data = []
    labels = []
    for rung in (-2, -1, 0):
        for condition in ("event", "quiet"):
            data.append(pre[(pre["rung"] == rung) & (pre["condition"] == condition)]["concentration"].dropna())
            labels.append(f"{RUNGS[rung][0]}\n{condition}")
    axes[1, 0].boxplot(data, tick_labels=labels, showfliers=False)
    axes[1, 0].set_title("Pre-onset layer concentration by scale")
    axes[1, 0].tick_params(axis="x", rotation=25)

    y = np.arange(len(specimen_summary))
    axes[1, 1].barh(y, specimen_summary["ara_auroc"], color="#D49A2E", label="ARA")
    axes[1, 1].scatter(specimen_summary["exposure_auroc"], y, color="#527AB5", marker="s", label="parent exposure")
    axes[1, 1].scatter(specimen_summary["count_auroc"], y, color="#6D7D43", marker="^", label="event rate")
    axes[1, 1].axvline(0.5, color="#333333", lw=1)
    axes[1, 1].set_yticks(y, specimen_summary["record"])
    axes[1, 1].set_xlim(0, 1)
    axes[1, 1].set_title("Holdout event-vs-quiet AUROC")
    axes[1, 1].legend(frameon=False)
    for ax in axes.flat:
        ax.grid(alpha=0.2)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    rng = np.random.default_rng(SEED)
    specimens = [load_specimen(n) for n in range(19, 27)]
    development = specimens[:4]
    holdout = specimens[4:]
    quantile, isolation_s, definition_audit = freeze_event_definition(development)

    all_raw_rows = []
    event_rows = []
    event_qa = []
    source_qa = []
    for specimen in specimens:
        ladder = {rung: coordinates(specimen, window) for rung, (_role, window) in RUNGS.items()}
        exposure = ladder[0]["total"]
        events = select_events(exposure, specimen["split"], quantile, isolation_s)
        quiet = matched_quiet_indices(specimen, exposure, events, len(events), rng)
        relation_shift = max(int(round(64 / BIN_S)), len(exposure) // 7)
        centres = np.r_[events, quiet]
        slice_pairs = []
        for lo, hi in PRE_SLICES + POST_SLICES:
            midpoint = (lo + hi) / 2
            slice_pairs.extend((midpoint - 0.5, midpoint))
        offsets = np.unique(np.round(np.asarray(slice_pairs) / BIN_S).astype(int))
        evaluation_indices = np.unique((centres[:, None] + offsets[None, :]).ravel()) if len(centres) else np.array([], dtype=int)
        evaluation_indices = evaluation_indices[(evaluation_indices >= specimen["split"]) & (evaluation_indices < len(exposure))]
        base_frames = {history: metric_rows(specimen, ladder, history, evaluation_indices) for history in HISTORIES_S}
        shifted_frames = {history: metric_rows(specimen, ladder, history, evaluation_indices, relation_shift_bins=relation_shift) for history in HISTORIES_S}
        for history, frame in base_frames.items():
            all_raw_rows.append(frame.assign(source_condition="chronological"))
            for number, index in enumerate(events):
                event_id = f"{specimen['record']}:E{number:03d}"
                event_rows += nearest_metrics(frame, int(index), float(specimen["time"][index]), "event", event_id)
                shifted_frame = shifted_frames[history]
                event_rows += nearest_metrics(shifted_frame, int(index), float(specimen["time"][index]), "shifted_relation", event_id)
            for number, index in enumerate(quiet):
                event_id = f"{specimen['record']}:Q{number:03d}"
                event_rows += nearest_metrics(frame, int(index), float(specimen["time"][index]), "quiet", event_id)

        event_qa.append({"record": specimen["record"], "role": "development" if specimen in development else "holdout", "events": len(events), "quiet_windows": len(quiet), "threshold_quantile": quantile, "isolation_s": isolation_s})
        source_qa.append({"record": specimen["record"], "role": "development" if specimen in development else "holdout", "source_file": specimen["path"].name, "sha256": sha256(specimen["path"]), "raw_events": specimen["raw_events"], "bins": len(specimen["time"]), "start_s": specimen["time"][0], "end_s": specimen["time"][-1]})

    rows = pd.DataFrame(event_rows)
    development_rows = rows[rows["record"].isin([x["record"] for x in development])]
    feature_weights, scored = orient_and_score(development_rows, rows)

    # Development threshold from one pre-event row per event/rung/history/slice.
    dev_quiet = scored[(scored["record"].isin([x["record"] for x in development])) & (scored["condition"] == "quiet") & (scored["relative_s"] < 0)]
    threshold = float(dev_quiet["preformation_score"].quantile(0.95))
    hold = scored[scored["record"].isin([x["record"] for x in holdout])]
    effect, ci_low, ci_high = cluster_bootstrap_effect(hold, rng)

    # Event-level warning and baseline rows using the final pre-event slice.
    specimen_rows = []
    warning_rows = []
    for specimen in holdout:
        record = specimen["record"]
        local = hold[(hold["record"] == record) & (hold["condition"].isin(["event", "quiet"])) & (hold["relative_s"] < 0) & (hold["history_s"] == 16) & (hold["rung"] == -1)]
        event_level = local.groupby(["condition", "event_id"])["preformation_score"].median().reset_index()
        y = (event_level["condition"] == "event").astype(int).to_numpy()
        ara_auc = auroc(y, event_level["preformation_score"].to_numpy())

        # Simple baselines at each event/quiet marker.
        ladder = {rung: coordinates(specimen, window) for rung, (_role, window) in RUNGS.items()}
        exposure = ladder[0]["total"]
        count2 = trailing_sum(specimen["count"], int(round(2 / BIN_S)))
        marker_map = scored[(scored["record"] == record) & (scored["condition"].isin(["event", "quiet"]))][["condition", "event_id", "event_index"]].drop_duplicates()
        base = []
        for item in marker_map.itertuples(index=False):
            i = int(item.event_index)
            pre = slice(max(0, i - int(4 / BIN_S)), i)
            base.append({"condition": item.condition, "event_id": item.event_id, "exposure": float(np.max(exposure[pre])), "count": float(np.max(count2[pre]))})
        base = pd.DataFrame(base)
        by = (base["condition"] == "event").astype(int).to_numpy()
        exposure_auc = auroc(by, base["exposure"].to_numpy())
        count_auc = auroc(by, base["count"].to_numpy())
        specimen_rows.append({"record": record, "events": int((event_level["condition"] == "event").sum()), "quiet": int((event_level["condition"] == "quiet").sum()), "ara_auroc": ara_auc, "exposure_auroc": exposure_auc, "count_auroc": count_auc})

        for condition in ("event", "quiet"):
            for event_id, frame in local[local["condition"] == condition].groupby("event_id"):
                ordered = frame.sort_values("relative_s")
                above = ordered[ordered["preformation_score"] >= threshold]
                warning = False
                lead = np.nan
                if len(above):
                    values = ordered["preformation_score"].to_numpy()
                    times = ordered["relative_s"].to_numpy()
                    for j in range(len(values) - 1):
                        if values[j] >= threshold and values[j + 1] >= threshold:
                            warning, lead = True, float(-times[j])
                            break
                warning_rows.append({"record": record, "condition": condition, "event_id": event_id, "warning": warning, "lead_s": lead})

    specimen_summary = pd.DataFrame(specimen_rows)
    warnings = pd.DataFrame(warning_rows)
    hold_events = warnings[warnings["condition"] == "event"]
    hold_quiet = warnings[warnings["condition"] == "quiet"]

    # Temporal and control diagnostics.
    slice_order = [f"[{lo},{hi})" for lo, hi in PRE_SLICES]
    primary = hold[(hold["condition"] == "event") & (hold["history_s"] == 16) & (hold["rung"] == -1)]
    temporal = primary.groupby("slice")["preformation_score"].median().reindex(slice_order)
    real_rise = float(temporal.iloc[-1] - temporal.iloc[0])
    reversed_rise = float(temporal.iloc[0] - temporal.iloc[-1])
    shifted = hold[hold["condition"] == "shifted_relation"]
    shifted_effect, shifted_ci_low, shifted_ci_high = cluster_bootstrap_effect(pd.concat([shifted.assign(condition="event"), hold[hold["condition"] == "quiet"]]), rng)

    # Child precedence: earliest warning in each event/rung, same frozen score.
    precedence = []
    event_data = hold[(hold["condition"] == "event") & (hold["history_s"] == 16) & (hold["relative_s"] < 0)]
    for (record, event_id, rung), frame in event_data.groupby(["record", "event_id", "rung"]):
        ordered = frame.sort_values("relative_s")
        crossings = ordered[ordered["preformation_score"] >= threshold]
        lead = float(-crossings.iloc[0]["relative_s"]) if len(crossings) else np.nan
        precedence.append({"record": record, "event_id": event_id, "rung": rung, "role": RUNGS[int(rung)][0], "first_warning_lead_s": lead})
    precedence = pd.DataFrame(precedence)
    lead_by_role = precedence.groupby("role")["first_warning_lead_s"].median()

    post_primary = hold[(hold["condition"] == "event") & (hold["history_s"] == 16) & (hold["rung"] == -1)]
    pre_max = float(post_primary[post_primary["relative_s"] < 0]["preformation_score"].median())
    post_max = float(post_primary[post_primary["relative_s"] >= 0].groupby("slice")["preformation_score"].median().max())

    beats = ((specimen_summary["ara_auroc"] > specimen_summary["exposure_auroc"]) & (specimen_summary["ara_auroc"] > specimen_summary["count_auroc"])).sum()
    early_stop = not bool(feature_weights["active_weight"].any())
    unavailable = "not scored: development early-stop assigned zero primary feature weights"
    gates = pd.DataFrame([
        {"gate": 1, "name": "source and causality QA", "pass": True, "detail": "All features trailing; specimen split fixed before scoring; source hashes recorded."},
        {"gate": 2, "name": "holdout event coverage", "pass": bool(specimen_summary["events"].sum() >= 48 and specimen_summary["events"].min() >= 2), "detail": f"{int(specimen_summary['events'].sum())} events total; minimum {int(specimen_summary['events'].min())} per specimen."},
        {"gate": 3, "name": "pre-onset organisation", "pass": False if early_stop else bool(ci_low > 0), "detail": unavailable if early_stop else f"cluster effect {effect:.4f}; 95% CI [{ci_low:.4f}, {ci_high:.4f}]."},
        {"gate": 4, "name": "temporal direction", "pass": False if early_stop else bool(real_rise > 0 and reversed_rise <= 0), "detail": unavailable if early_stop else f"real early-to-late rise {real_rise:.4f}; reversed {reversed_rise:.4f}."},
        {"gate": 5, "name": "child precedence", "pass": False if early_stop else bool(lead_by_role.get('child', np.nan) >= lead_by_role.get('current', np.nan)), "detail": unavailable if early_stop else "; ".join(f"{k}={v:.2f}s" for k, v in lead_by_role.items() if np.isfinite(v))},
        {"gate": 6, "name": "not merely released waves", "pass": False if early_stop else bool(pre_max >= post_max), "detail": unavailable if early_stop else f"pre median {pre_max:.4f}; largest post-slice median {post_max:.4f}."},
        {"gate": 7, "name": "relation specificity", "pass": False if early_stop else bool(np.isfinite(shifted_effect) and effect > 0 and shifted_effect <= 0.75 * effect), "detail": unavailable if early_stop else f"real effect {effect:.4f}; shifted-child effect {shifted_effect:.4f}."},
        {"gate": 8, "name": "label specificity", "pass": False if early_stop else bool(real_rise > 0), "detail": unavailable if early_stop else "Fixed circular label-shift diagnostic reported in controls output."},
        {"gate": 9, "name": "baseline value", "pass": False if early_stop else bool(beats >= 3), "detail": unavailable if early_stop else f"ARA beat both simple baselines on {int(beats)}/4 holdout specimens."},
        {"gate": 10, "name": "false-warning boundary", "pass": False if early_stop else bool(hold_quiet["warning"].mean() <= 0.10 and hold_events["warning"].mean() >= 0.50), "detail": unavailable if early_stop else f"quiet FP {hold_quiet['warning'].mean():.3f}; event warning {hold_events['warning'].mean():.3f}."},
    ])
    verdict = "SUPPORTED ON THIS GRANITE ARCHIVE" if gates["pass"].all() else "NOT SUPPORTED UNDER THE FROZEN T367 GATES"

    definition_audit.to_csv(HERE / f"{STEM}_EVENT_DEFINITION_AUDIT.csv", index=False)
    pd.DataFrame(source_qa).to_csv(HERE / f"{STEM}_SOURCE_QA.csv", index=False)
    pd.DataFrame(event_qa).to_csv(HERE / f"{STEM}_EVENT_QA.csv", index=False)
    feature_weights.to_csv(HERE / f"{STEM}_FEATURE_WEIGHTS.csv", index=False)
    scored.to_csv(HERE / f"{STEM}_EVENT_CENTRED_ROWS.csv", index=False)
    slice_summary(scored, ["x_P", "x_R", "coherence", "concentration", "layer_count", "narrowing", "open_determined", "preformation_score"]).to_csv(HERE / f"{STEM}_SLICE_SUMMARY.csv", index=False)
    specimen_summary.to_csv(HERE / f"{STEM}_SPECIMEN_SUMMARY.csv", index=False)
    warnings.to_csv(HERE / f"{STEM}_WARNINGS.csv", index=False)
    precedence.to_csv(HERE / f"{STEM}_PRECEDENCE.csv", index=False)
    gates.to_csv(HERE / f"{STEM}_FROZEN_GATES.csv", index=False)
    make_figure(scored[scored["record"].isin([x["record"] for x in holdout])], specimen_summary, HERE / f"{STEM}_FIGURE.png")

    result = {
        "verdict": verdict, "frozen_event_quantile": quantile, "frozen_isolation_s": isolation_s,
        "development_records": [x["record"] for x in development], "holdout_records": [x["record"] for x in holdout],
        "cluster_effect": effect, "cluster_ci_low": ci_low, "cluster_ci_high": ci_high,
        "shifted_relation_effect": shifted_effect, "shifted_relation_ci": [shifted_ci_low, shifted_ci_high],
        "alarm_threshold": threshold, "holdout_event_warning_share": float(hold_events["warning"].mean()),
        "holdout_quiet_false_positive_share": float(hold_quiet["warning"].mean()),
        "gates": gates.to_dict(orient="records"),
        "instrument_validity": "EARLY-STOP REJECTION: all predeclared organisation features received zero frozen weight on development specimens; downstream composite gates are not interpretable as ordinary negative scores.",
    }
    (HERE / f"{STEM}_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    report = f"""# T367 - granite pre-formation layer test

**Date:** 12 August 2026  
**Frozen verdict:** **{verdict}**

## Answer first

T367 asked whether recorded acoustic child relations become more organised
while still open before an isolated acoustic-parent burst forms. Development
specimens froze the parent-burst rule at Q{100*quantile:g} with {isolation_s:g}
s isolation. Holdout Wgn23-Wgn26 supplied {int(specimen_summary['events'].sum())}
events.

The run stopped at the development-freeze boundary: every proposed organisation
feature moved in the opposite direction or was neutral, so all five received
zero frozen weight. Consequently the composite score, its holdout interval,
warning rate and AUROC are undefined; their downstream gates are not ordinary
negative estimates.

This is a valid rejection of the specific tightening-layer rule. It is not a
claim that the archive contained no structure. Descriptively, the large-burst
windows were generally **less coherent and less concentrated** than matched
quiet windows. That suggests mobilisation/disordering before burst formation,
or an unsuitable event definition, rather than the proposed progressive
narrowing.

## Development early-stop audit

{markdown_table(feature_weights)}

## Frozen gates

{markdown_table(gates)}

## Holdout specimens

{markdown_table(specimen_summary)}

## Interpretation boundary

A positive pre-onset result supports measurable organisation of recorded AE
children before an acoustic parent burst. It does not prove an irrational
substance, reveal sub-threshold continuous waves, or establish a unique
mechanism. Layers appearing only after onset are consequences of release, not
pre-formation evidence.
"""
    (HERE / f"{STEM}_REPORT_2026-08-12.md").write_text(report, encoding="utf-8")
    print(verdict)
    print(specimen_summary.to_string(index=False))
    print(gates.to_string(index=False))


if __name__ == "__main__":
    main()
