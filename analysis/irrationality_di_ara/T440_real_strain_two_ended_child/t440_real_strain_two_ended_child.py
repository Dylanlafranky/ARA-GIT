from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import ndimage, stats


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
WORKSPACE = ROOT.parents[4]
CACHE = WORKSPACE / "_data_cache" / "GWOSC"
T427_PATH = ROOT.parent / "T427_spacetime_strain_handover" / "t427_spacetime_strain_handover.py"
T427_MANIFEST = ROOT.parent / "T427_spacetime_strain_handover" / "T427_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
PROTOCOL = ROOT / "T440_FROZEN_PROTOCOL.md"

EVENT_WINDOW = (-0.32, 0.08)
OFF_INTERVALS = ((-12.0, -4.0), (4.0, 12.0))
CONTROL_SECONDS = 0.40
HOP_SECONDS = 0.004
MAX_LAG_FRAMES = 8
MAX_SIDE_GAP = 0.032
MAX_DETECTOR_GAP = 0.016
SEED = 44020260827
N_WRONG_EVENT = 5000


def load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


t427 = load_module(T427_PATH, "t427_for_t440")


@dataclass
class ParentHistory:
    event: str
    role: str
    detector: str
    times: np.ndarray
    p_space: np.ndarray
    p_time: np.ndarray
    e_space: np.ndarray
    e_time: np.ndarray
    d_space: np.ndarray
    d_time: np.ndarray
    components: dict[str, np.ndarray]
    source_path: pathlib.Path
    qa: dict[str, object]


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def interval_mask(times: np.ndarray, intervals: tuple[tuple[float, float], ...]) -> np.ndarray:
    out = np.zeros(len(times), dtype=bool)
    for lo, hi in intervals:
        out |= (times >= lo) & (times <= hi)
    return out


def ecdf_ara(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    ref = np.sort(np.asarray(reference, dtype=float))
    ref = ref[np.isfinite(ref)]
    if len(ref) < 4:
        return np.full_like(values, np.nan, dtype=float)
    rank = np.searchsorted(ref, values, side="right")
    return np.clip(2.0 * (rank + 0.5) / (len(ref) + 1.0), 0.0, 2.0)


def smooth(values: np.ndarray, size: int = 5) -> np.ndarray:
    return ndimage.median_filter(np.asarray(values, dtype=float), size=size, mode="nearest")


def aligned(values: np.ndarray, lag: int) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    out = np.full_like(values, np.nan)
    if lag == 0:
        return values.copy()
    if lag > 0:
        out[lag:] = values[:-lag]
    else:
        out[:lag] = values[-lag:]
    return out


def safe_spearman(a: np.ndarray, b: np.ndarray) -> float:
    valid = np.isfinite(a) & np.isfinite(b)
    if np.sum(valid) < 12:
        return float("nan")
    if np.nanstd(a[valid]) < 1e-12 or np.nanstd(b[valid]) < 1e-12:
        return 0.0
    return float(stats.spearmanr(a[valid], b[valid]).statistic)


def build_event_manifest() -> list[dict[str, object]]:
    manifest = json.loads(T427_MANIFEST.read_text(encoding="utf-8"))
    by_name = {row["event"]: row for row in manifest["events"]}
    events: list[dict[str, object]] = []
    for name in ("GW150914", "GW170814"):
        src = by_name[name]
        paths = {
            detector: CACHE / "T427" / name / pathlib.Path(url).name
            for detector, url in src["files"].items()
            if detector in {"H1", "L1"}
        }
        events.append({"event": name, "gps": src["gps"], "role": "development_only", "paths": paths})

    for cache_name, role in (("T431", "locked_evaluation_a"), ("T432", "locked_evaluation_b")):
        for folder in sorted((CACHE / cache_name).iterdir()):
            if not folder.is_dir():
                continue
            api_files = list(folder.glob("*_eventapi.json"))
            if not api_files:
                continue
            meta = json.loads(api_files[0].read_text(encoding="utf-8"))
            paths: dict[str, pathlib.Path] = {}
            for detector, prefix in (("H1", "H-"), ("L1", "L-")):
                candidates = sorted(folder.glob(f"{prefix}*.hdf5"))
                if candidates:
                    paths[detector] = candidates[0]
            if set(paths) == {"H1", "L1"}:
                events.append({"event": folder.name, "gps": float(meta["gps"]), "role": role, "paths": paths})
    return events


def build_parent(event: dict[str, object], detector: str, path: pathlib.Path) -> ParentHistory:
    det = t427.build_detector(event, detector, path)
    power = np.asarray(det.power, dtype=float)
    total = np.sum(power, axis=0) + t427.EPS
    p = power / total[None, :]

    amount = np.log(total)
    entropy = -np.sum(p * np.log(p + t427.EPS), axis=0) / np.log(power.shape[0])
    concentration = 1.0 - entropy
    centroid = np.sum(p * det.freqs[:, None], axis=0)

    hellinger = np.zeros(power.shape[1], dtype=float)
    affinity = np.sum(np.sqrt(p[:, 1:] * p[:, :-1]), axis=0)
    hellinger[1:] = np.sqrt(np.clip(1.0 - affinity, 0.0, 1.0))
    ridge = det.freqs[np.argmax(power, axis=0)]
    ridge_move = np.zeros_like(ridge)
    ridge_move[1:] = np.abs(np.log2((ridge[1:] + t427.EPS) / (ridge[:-1] + t427.EPS)))
    redistribution = hellinger + ridge_move

    off = interval_mask(det.frame_rel, OFF_INTERVALS)
    amount_ara = ecdf_ara(amount, amount[off])
    concentration_ara = ecdf_ara(concentration, concentration[off])
    frequency_ara = ecdf_ara(centroid, centroid[off])
    redistribution_ara = ecdf_ara(redistribution, redistribution[off])

    p_space = smooth(np.nanmean(np.vstack([amount_ara, concentration_ara]), axis=0), 5)
    p_time = smooth(np.nanmean(np.vstack([frequency_ara, redistribution_ara]), axis=0), 5)
    d_space = np.gradient(p_space, HOP_SECONDS)
    d_time = np.gradient(p_time, HOP_SECONDS)
    raw_space = smooth(np.abs(d_space), 3)
    raw_time = smooth(np.abs(d_time), 3)
    e_space = ecdf_ara(raw_space, raw_space[off])
    e_time = ecdf_ara(raw_time, raw_time[off])

    return ParentHistory(
        event=str(event["event"]), role=str(event["role"]), detector=detector,
        times=np.asarray(det.frame_rel), p_space=p_space, p_time=p_time,
        e_space=e_space, e_time=e_time, d_space=d_space, d_time=d_time,
        components={
            "space_amount": amount_ara,
            "space_concentration": concentration_ara,
            "time_frequency": frequency_ara,
            "time_redistribution": redistribution_ara,
        },
        source_path=path,
        qa=det.qa,
    )


def normalized_mass(values: np.ndarray) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    v = np.where(np.isfinite(v), np.maximum(v, 0.0), 0.0)
    total = float(np.sum(v))
    if total <= 0:
        return np.full(len(v), 1.0 / max(len(v), 1))
    return v / total


def history_overlap(e_space: np.ndarray, e_time: np.ndarray) -> float:
    ps = normalized_mass(e_space)
    pt = normalized_mass(e_time)
    return float(np.sum(np.sqrt(ps * pt)))


def score_arrays(times: np.ndarray, e_space: np.ndarray, e_time: np.ndarray,
                 d_space: np.ndarray | None = None, d_time: np.ndarray | None = None) -> dict[str, float | int | str]:
    t = np.asarray(times, dtype=float)
    es = np.asarray(e_space, dtype=float)
    et = np.asarray(e_time, dtype=float)
    valid = np.isfinite(t) & np.isfinite(es) & np.isfinite(et)
    t, es, et = t[valid], es[valid], et[valid]
    if len(t) < 20:
        return {"overlap": float("nan"), "rho_zero": float("nan"), "rho_best": float("nan"),
                "best_lag_frames": 0, "best_lag_s": 0.0, "dice": float("nan"),
                "space_peak_time": float("nan"), "time_peak_time": float("nan"),
                "side_peak_gap_s": float("nan"), "space_centroid_time": float("nan"),
                "time_centroid_time": float("nan"), "centroid_gap_s": float("nan"),
                "joint_child_time": float("nan"), "quadrant": "unknown"}

    ps, pt = normalized_mass(es), normalized_mass(et)
    overlap = history_overlap(es, et)
    rho_zero = safe_spearman(es, et)
    candidates: list[tuple[float, int]] = []
    for lag in range(-MAX_LAG_FRAMES, MAX_LAG_FRAMES + 1):
        candidates.append((safe_spearman(es, aligned(et, lag)), lag))
    finite_candidates = [(rho, lag) for rho, lag in candidates if np.isfinite(rho)]
    rho_best, best_lag = max(finite_candidates, default=(float("nan"), 0), key=lambda item: item[0])
    et_aligned = aligned(et, best_lag)
    both = np.isfinite(et_aligned)
    q_space = np.nanquantile(es[both], 0.8)
    q_time = np.nanquantile(et_aligned[both], 0.8)
    hs = (es >= q_space) & both
    ht = (et_aligned >= q_time) & both
    denom = int(np.sum(hs) + np.sum(ht))
    dice = float(2 * np.sum(hs & ht) / denom) if denom else float("nan")

    space_peak = int(np.nanargmax(es))
    time_peak = int(np.nanargmax(et))
    space_centroid = float(np.sum(t * ps))
    time_centroid = float(np.sum(t * pt))
    joint = np.sqrt(np.maximum(es, 0.0) * np.maximum(et, 0.0))
    joint_idx = int(np.nanargmax(joint))
    quadrant = "unknown"
    if d_space is not None and d_time is not None:
        ds = np.asarray(d_space, dtype=float)[valid]
        dt = np.asarray(d_time, dtype=float)[valid]
        quadrant = ("S+" if ds[joint_idx] >= 0 else "S-") + "/" + ("T+" if dt[joint_idx] >= 0 else "T-")

    return {
        "overlap": overlap,
        "rho_zero": rho_zero,
        "rho_best": float(rho_best),
        "best_lag_frames": int(best_lag),
        "best_lag_s": float(best_lag * HOP_SECONDS),
        "dice": dice,
        "space_peak_time": float(t[space_peak]),
        "time_peak_time": float(t[time_peak]),
        "side_peak_gap_s": float(abs(t[space_peak] - t[time_peak])),
        "space_centroid_time": space_centroid,
        "time_centroid_time": time_centroid,
        "centroid_gap_s": float(abs(space_centroid - time_centroid)),
        "joint_child_time": float(t[joint_idx]),
        "quadrant": quadrant,
    }


def score_history(history: ParentHistory, lo: float, hi: float) -> dict[str, float | int | str]:
    mask = (history.times >= lo) & (history.times <= hi)
    return score_arrays(history.times[mask], history.e_space[mask], history.e_time[mask],
                        history.d_space[mask], history.d_time[mask])


def control_scores(history: ParentHistory) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for interval_id, (lo, hi) in enumerate(OFF_INTERVALS):
        start = lo
        while start + CONTROL_SECONDS <= hi + 1e-9:
            score = score_history(history, start, start + CONTROL_SECONDS)
            rows.append({"event": history.event, "role": history.role, "detector": history.detector,
                         "interval_id": interval_id, "start_s": start, **score})
            start += CONTROL_SECONDS
    return pd.DataFrame(rows)


def percentile(observed: float, controls: np.ndarray, higher: bool = True) -> float:
    c = np.asarray(controls, dtype=float)
    c = c[np.isfinite(c)]
    if not np.isfinite(observed) or len(c) == 0:
        return float("nan")
    if higher:
        return float((1 + np.sum(c <= observed)) / (len(c) + 1))
    return float((1 + np.sum(c >= observed)) / (len(c) + 1))


def common_grid(history: ParentHistory) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    grid = np.arange(EVENT_WINDOW[0], EVENT_WINDOW[1] + HOP_SECONDS / 2, HOP_SECONDS)
    es = np.interp(grid, history.times, history.e_space)
    et = np.interp(grid, history.times, history.e_time)
    return grid, es, et


def wrong_event_null(histories: dict[tuple[str, str], ParentHistory], evaluation_events: list[str], rng: np.random.Generator) -> tuple[float, np.ndarray]:
    correct: list[float] = []
    grids: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for event in evaluation_events:
        for detector in ("H1", "L1"):
            grids[(event, detector)] = common_grid(histories[(event, detector)])
            grid, es, et = grids[(event, detector)]
            correct.append(history_overlap(es, et))
    observed = float(np.nanmedian(correct))
    null = np.empty(N_WRONG_EVENT, dtype=float)
    base = np.arange(len(evaluation_events))
    for i in range(N_WRONG_EVENT):
        perm = rng.permutation(base)
        if np.any(perm == base):
            perm = np.roll(base, int(rng.integers(1, len(base))))
        scores: list[float] = []
        for detector in ("H1", "L1"):
            for left_idx, right_idx in enumerate(perm):
                left = evaluation_events[left_idx]
                right = evaluation_events[int(right_idx)]
                grid, es, _ = grids[(left, detector)]
                _, _, et = grids[(right, detector)]
                scores.append(history_overlap(es, et))
        null[i] = np.nanmedian(scores)
    return observed, null


def style() -> None:
    plt.style.use("dark_background")
    plt.rcParams.update({"figure.facecolor": "#0b1220", "axes.facecolor": "#111827",
                         "axes.edgecolor": "#94a3b8", "grid.color": "#334155",
                         "font.size": 10, "axes.titleweight": "bold"})


def plot_event(history_h: ParentHistory, history_l: ParentHistory, detector_rows: pd.DataFrame, out: pathlib.Path) -> None:
    style()
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    for history, color_s, color_t, label in ((history_h, "#22c55e", "#60a5fa", "H1"),
                                              (history_l, "#f59e0b", "#c084fc", "L1")):
        mask = (history.times >= EVENT_WINDOW[0]) & (history.times <= EVENT_WINDOW[1])
        axes[0, 0].plot(history.times[mask], history.p_space[mask], color=color_s, lw=1.7, label=f"{label} Space/Connection parent")
        axes[0, 0].plot(history.times[mask], history.p_time[mask], color=color_t, lw=1.4, alpha=.9, label=f"{label} Time/Movement parent")
        axes[0, 1].plot(history.times[mask], history.e_space[mask], color=color_s, lw=1.7, label=f"{label} child from Space")
        axes[0, 1].plot(history.times[mask], history.e_time[mask], color=color_t, lw=1.4, alpha=.9, label=f"{label} child from Time")
        axes[1, 0].plot(history.p_time[mask], history.p_space[mask], color=color_t, alpha=.7, lw=1.1, label=label)
        axes[1, 1].plot(history.e_time[mask], history.e_space[mask], color=color_s, alpha=.7, lw=1.1, label=label)
        row = detector_rows[detector_rows.detector == label].iloc[0]
        axes[0, 1].axvline(row.joint_child_time, color=color_s, ls="--", alpha=.8)
    axes[0, 0].axhline(1, color="white", ls=":", lw=1, label="ARA ridge 1.0")
    axes[0, 0].set(title="Independent parent histories", xlabel="Seconds relative to published event GPS", ylabel="Parent ARA coordinate (0–2)", ylim=(0, 2))
    axes[0, 1].axhline(1, color="white", ls=":", lw=1, label="child ridge 1.0")
    axes[0, 1].set(title="Two independently constructed child histories", xlabel="Seconds relative to published event GPS", ylabel="Child ARA coordinate (0–2)", ylim=(0, 2))
    axes[1, 0].axvline(1, color="white", ls=":", lw=1); axes[1, 0].axhline(1, color="white", ls=":", lw=1)
    axes[1, 0].set(title="Parent Di-ARA trajectory", xlabel="Time/Movement parent (0–2)", ylabel="Space/Connection parent (0–2)", xlim=(0,2), ylim=(0,2))
    axes[1, 1].axvline(1, color="white", ls=":", lw=1); axes[1, 1].axhline(1, color="white", ls=":", lw=1)
    axes[1, 1].set(title="Two-ended child plane", xlabel="Child from Time end (0–2)", ylabel="Child from Space end (0–2)", xlim=(0,2), ylim=(0,2))
    for ax in axes.ravel():
        ax.grid(True, alpha=.45); ax.legend(fontsize=8, loc="best")
    fig.suptitle(f"T440 {history_h.event} — real-strain two-ended child reconstruction", fontsize=18, fontweight="bold")
    fig.savefig(out, dpi=170, bbox_inches="tight")
    plt.close(fig)


def plot_summary(detector_results: pd.DataFrame, event_results: pd.DataFrame, null: np.ndarray, observed: float, out: pathlib.Path) -> None:
    style()
    eval_det = detector_results[detector_results.role.str.startswith("locked")].copy()
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    x = np.arange(len(eval_det))
    colors = np.where(eval_det.detector.eq("H1"), "#60a5fa", "#f59e0b")
    axes[0,0].bar(x-.18, eval_det.overlap_percentile, width=.36, color=colors, alpha=.9, label="overlap percentile")
    axes[0,0].bar(x+.18, eval_det.rho_percentile, width=.36, color="#c084fc", alpha=.65, label="best-lag rho percentile")
    axes[0,0].axhline(.90, color="white", ls="--", label="frozen 90% detector gate")
    axes[0,0].set(title="Event-window specificity by detector", xlabel="Event-detector stream", ylabel="Within-file control percentile", ylim=(0,1.05), xticks=x, xticklabels=[f"{e}\n{d}" for e,d in zip(eval_det.event,eval_det.detector)],)
    axes[0,0].tick_params(axis="x", rotation=75, labelsize=7)

    axes[0,1].scatter(eval_det.side_peak_gap_s*1000, eval_det.detector_gap_s*1000, c=colors, s=55, alpha=.85)
    axes[0,1].axvline(MAX_SIDE_GAP*1000, color="white", ls="--", label="Space/Time side gate")
    axes[0,1].axhline(MAX_DETECTOR_GAP*1000, color="#f472b6", ls="--", label="H1/L1 gate")
    axes[0,1].set(title="Independent timing agreement", xlabel="Space-end vs Time-end peak gap (ms)", ylabel="H1 vs L1 joint-child gap (ms)")

    bins = np.linspace(float(np.nanmin(null)), float(np.nanmax(null)), 35)
    axes[1,0].hist(null, bins=bins, color="#475569", alpha=.9, label="wrong-event median overlaps")
    axes[1,0].axvline(observed, color="#22c55e", lw=3, label=f"correct-event median {observed:.3f}")
    axes[1,0].set(title="Correct-event identity versus wrong-event pairing", xlabel="Median two-ended history overlap", ylabel="Null replicates")

    ordered = event_results.sort_values("event").copy()
    gate_columns = ["both_overlap_gate", "both_rho_gate", "both_side_gap_gate", "detector_time_gate"]
    ordered["gate_count"] = ordered[gate_columns].astype(int).sum(axis=1)
    y = np.arange(len(ordered))
    axes[1,1].barh(y, ordered.gate_count, color=np.where(ordered.accepted, "#22c55e", "#f59e0b"), alpha=.85)
    axes[1,1].axvline(4, color="white", ls="--", label="all four gates required")
    axes[1,1].set(title="Frozen event-level gate completion", xlabel="Number of event gates passed (of 4)", ylabel="Locked evaluation event", yticks=y, yticklabels=ordered.event, xlim=(0,4.25), xticks=[0,1,2,3,4])
    for ax in axes.ravel():
        ax.grid(True, alpha=.4)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(fontsize=8, loc="best")
    fig.suptitle("T440 — real GWOSC strain: two-ended child test", fontsize=19, fontweight="bold")
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    events = build_event_manifest()
    histories: dict[tuple[str, str], ParentHistory] = {}
    source_rows: list[dict[str, object]] = []
    history_rows: list[dict[str, object]] = []
    control_frames: list[pd.DataFrame] = []

    for event in events:
        for detector in ("H1", "L1"):
            path = event["paths"][detector]
            history = build_parent(event, detector, path)
            histories[(history.event, detector)] = history
            print(f"built {history.event} {detector}", flush=True)
            source_rows.append({"event": history.event, "role": history.role, "detector": detector,
                                "path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size,
                                "public_dq_pass": history.qa.get("public_dq_pass")})
            mask = (history.times >= EVENT_WINDOW[0]) & (history.times <= EVENT_WINDOW[1])
            for i in np.where(mask)[0]:
                history_rows.append({"event": history.event, "role": history.role, "detector": detector,
                                     "time_s": history.times[i], "p_space": history.p_space[i],
                                     "p_time": history.p_time[i], "e_space": history.e_space[i],
                                     "e_time": history.e_time[i], "joint_child": np.sqrt(history.e_space[i]*history.e_time[i]),
                                     "d_space": history.d_space[i], "d_time": history.d_time[i]})
            control_frames.append(control_scores(history))

    controls = pd.concat(control_frames, ignore_index=True)
    detector_rows: list[dict[str, object]] = []
    for (event_name, detector), history in histories.items():
        score = score_history(history, *EVENT_WINDOW)
        subset = controls[(controls.event == event_name) & (controls.detector == detector)]
        detector_rows.append({
            "event": event_name, "role": history.role, "detector": detector, **score,
            "overlap_percentile": percentile(float(score["overlap"]), subset.overlap.to_numpy()),
            "rho_percentile": percentile(float(score["rho_best"]), subset.rho_best.to_numpy()),
            "dice_percentile": percentile(float(score["dice"]), subset.dice.to_numpy()),
            "gap_percentile": percentile(float(score["side_peak_gap_s"]), subset.side_peak_gap_s.to_numpy(), higher=False),
        })
    detector_results = pd.DataFrame(detector_rows)

    event_rows: list[dict[str, object]] = []
    evaluation_events = [str(event["event"]) for event in events if str(event["role"]).startswith("locked")]
    for event_name in evaluation_events:
        rows = detector_results[detector_results.event == event_name].set_index("detector")
        detector_gap = abs(float(rows.loc["H1", "joint_child_time"]) - float(rows.loc["L1", "joint_child_time"]))
        both_overlap = bool(np.all(rows.overlap_percentile >= .90))
        both_rho = bool(np.all(rows.rho_percentile >= .90))
        both_side = bool(np.all(rows.side_peak_gap_s <= MAX_SIDE_GAP + 1e-12))
        detector_time = bool(detector_gap <= MAX_DETECTOR_GAP + 1e-12)
        accepted = both_overlap and both_rho and both_side and detector_time
        event_rows.append({"event": event_name, "role": rows.role.iloc[0], "detector_gap_s": detector_gap,
                           "both_overlap_gate": both_overlap, "both_rho_gate": both_rho,
                           "both_side_gap_gate": both_side, "detector_time_gate": detector_time,
                           "accepted": accepted, "median_overlap": float(rows.overlap.median()),
                           "median_joint_child_time": float(rows.joint_child_time.median())})
        detector_results.loc[detector_results.event == event_name, "detector_gap_s"] = detector_gap
    event_results = pd.DataFrame(event_rows)

    observed_wrong, wrong_null = wrong_event_null(histories, evaluation_events, rng)
    wrong_p = float((1 + np.sum(wrong_null >= observed_wrong)) / (len(wrong_null) + 1))
    accepted_count = int(event_results.accepted.sum())
    population_gate = accepted_count >= 7 and wrong_p <= .05

    source_frame = pd.DataFrame(source_rows)
    history_frame = pd.DataFrame(history_rows)
    source_frame.to_csv(RESULTS / "T440_SOURCE_AUDIT.csv", index=False)
    history_frame.to_csv(RESULTS / "T440_EVENT_HISTORIES.csv", index=False)
    controls.to_csv(RESULTS / "T440_OFFSOURCE_CONTROLS.csv", index=False)
    detector_results.to_csv(RESULTS / "T440_DETECTOR_RESULTS.csv", index=False)
    event_results.to_csv(RESULTS / "T440_EVENT_RESULTS.csv", index=False)
    pd.DataFrame({"wrong_event_median_overlap": wrong_null}).to_csv(RESULTS / "T440_WRONG_EVENT_NULL.csv", index=False)

    for event_name in ["GW150914", "GW170814", *evaluation_events]:
        rows = detector_results[detector_results.event == event_name]
        plot_event(histories[(event_name, "H1")], histories[(event_name, "L1")], rows,
                   RESULTS / f"T440_{event_name}_TWO_ENDED_CHILD.png")
    plot_summary(detector_results, event_results, wrong_null, observed_wrong, RESULTS / "T440_SUMMARY.png")

    result = {
        "verdict": "SUPPORTED" if population_gate else "NOT SUPPORTED",
        "accepted_events": accepted_count,
        "required_events": 7,
        "n_evaluation_events": len(evaluation_events),
        "correct_event_median_overlap": observed_wrong,
        "wrong_event_empirical_p": wrong_p,
        "event_count_gate": accepted_count >= 7,
        "wrong_event_gate": wrong_p <= .05,
        "population_gate": population_gate,
        "quadrant_counts": detector_results[detector_results.role.str.startswith("locked")].quadrant.value_counts().to_dict(),
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(pathlib.Path(__file__)),
        "seed": SEED,
    }
    (RESULTS / "T440_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
