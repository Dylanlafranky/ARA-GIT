from __future__ import annotations

import argparse
import base64
import hashlib
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
T427_ROOT = ROOT.parent / "T427_spacetime_strain_handover"
T429_ROOT = ROOT.parent / "T429_separated_space_time_strength"
sys.path.insert(0, str(T427_ROOT))
sys.path.insert(0, str(T429_ROOT))
import t427_spacetime_strain_handover as t427  # noqa: E402
import t429_separated_space_time_strength as t429  # noqa: E402


PROTOCOL = ROOT / "T430_FROZEN_PROTOCOL.md"
OLD_MANIFEST = T427_ROOT / "T427_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
OLD_AUDIT = T427_ROOT / "results" / "T427_SOURCE_AUDIT.json"
NEW_AUDIT = RESULTS / "T430_SOURCE_AUDIT.json"
OLD_PARAMETERS = T429_ROOT / "T429_SOURCE_PARAMETERS_MANIFEST.json"

EVENT_INTERVAL = (-1.50, 0.25)
PRIMARY_INTERVAL = (-0.50, -0.03)
WIDE_INTERVAL = (-1.25, -0.03)
OFF_INTERVALS = ((-12.0, -4.0), (4.0, 12.0))
N_NULL = 2_000
MIN_SHIFT = 16
SEED = 43020260824
EPS = 1e-12


@dataclass
class DetectorFeatures:
    detector: str
    times: np.ndarray
    centroid_hz: np.ndarray
    amount_ara: np.ndarray
    density_ara: np.ndarray
    connection_ara: np.ndarray
    period_ara: np.ndarray
    qa: dict[str, object]


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mask_interval(times: np.ndarray, interval: tuple[float, float]) -> np.ndarray:
    return (times >= interval[0]) & (times <= interval[1])


def mask_intervals(times: np.ndarray, intervals: tuple[tuple[float, float], ...]) -> np.ndarray:
    out = np.zeros(len(times), dtype=bool)
    for interval in intervals:
        out |= mask_interval(times, interval)
    return out


def smooth(values: np.ndarray, size: int = 9) -> np.ndarray:
    return ndimage.median_filter(np.asarray(values, dtype=float), size=size, mode="nearest")


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    valid = np.isfinite(a) & np.isfinite(b)
    if np.sum(valid) < 20:
        return float("nan")
    return float(stats.spearmanr(a[valid], b[valid]).statistic)


def first_persistent_time(times: np.ndarray, values: np.ndarray, threshold: float = 1.0, count: int = 3) -> float:
    above = np.asarray(values) >= threshold
    for i in range(0, max(0, len(above) - count + 1)):
        if np.all(above[i:i + count]):
            return float(times[i])
    return float("nan")


def build_detector(event: dict[str, object], detector: str, path: pathlib.Path) -> tuple[t427.DetectorData, DetectorFeatures]:
    det = t427.build_detector(event, detector, path)
    total = np.sum(det.power, axis=0) + EPS
    probability = det.power / total[None, :]
    centroid = np.sum(probability * det.freqs[:, None], axis=0)
    amount = np.log(total)
    density = det.connection_raw
    period = 1.0 / np.maximum(centroid, 1e-9)
    off = mask_intervals(det.frame_rel, OFF_INTERVALS)
    amount_ara = t429.ecdf_ara(amount, amount[off])
    density_ara = t429.ecdf_ara(density, density[off])
    period_ara = t429.ecdf_ara(period, period[off])
    connection = np.nanmean(np.vstack([amount_ara, density_ara]), axis=0)
    return det, DetectorFeatures(
        detector=detector,
        times=det.frame_rel,
        centroid_hz=centroid,
        amount_ara=amount_ara,
        density_ara=density_ara,
        connection_ara=connection,
        period_ara=period_ara,
        qa=det.qa,
    )


def network_view(features: dict[str, DetectorFeatures]) -> dict[str, np.ndarray | float | int]:
    h = features["H1"]
    l = features["L1"]
    event_mask = mask_interval(h.times, EVENT_INTERVAL)
    lag, lag_corr = t427.best_lag(h.amount_ara, l.amount_ara, 2, event_mask)

    def aligned(values: np.ndarray) -> np.ndarray:
        return t427.align_to_reference(np.asarray(values, dtype=float), lag)

    l_centroid = aligned(l.centroid_hz)
    l_amount = aligned(l.amount_ara)
    l_density = aligned(l.density_ara)
    l_connection = aligned(l.connection_ara)
    l_period = aligned(l.period_ara)

    centroid = smooth(np.nanmean(np.vstack([h.centroid_hz, l_centroid]), axis=0), 9)
    amount = np.nanmean(np.vstack([h.amount_ara, l_amount]), axis=0)
    density = np.nanmean(np.vstack([h.density_ara, l_density]), axis=0)
    connection = np.nanmean(np.vstack([amount, density]), axis=0)
    period = np.nanmean(np.vstack([h.period_ara, l_period]), axis=0)
    return {
        "times": h.times,
        "centroid_hz": centroid,
        "amount_ara": amount,
        "density_ara": density,
        "connection_ara": connection,
        "period_ara": period,
        "h_connection": h.connection_ara,
        "l_connection": l_connection,
        "h_amount": h.amount_ara,
        "l_amount": l_amount,
        "lag_frames": lag,
        "lag_ms": lag * t427.HOP_SECONDS * 1000.0,
        "lag_corr": lag_corr,
    }


def remaining_traversal(frequency_hz: np.ndarray) -> np.ndarray:
    frequency_hz = np.asarray(frequency_hz, dtype=float)
    cycles = np.cumsum((frequency_hz * t427.HOP_SECONDS)[::-1])[::-1]
    cycles = cycles - cycles[-1]
    if len(cycles) < 2 or not np.isfinite(cycles[0]) or cycles[0] <= EPS:
        return np.full(len(cycles), np.nan)
    return np.clip(2.0 * cycles / cycles[0], 0.0, 2.0)


def circular_relation_p(
    movement: np.ndarray,
    connection: np.ndarray,
    observed: float,
    rng: np.random.Generator,
    tail: str,
) -> tuple[float, np.ndarray]:
    valid = np.isfinite(movement) & np.isfinite(connection)
    movement = movement[valid]
    connection = connection[valid]
    if len(movement) < 2 * MIN_SHIFT + 1:
        return float("nan"), np.asarray([], dtype=float)
    shifts = np.arange(MIN_SHIFT, len(connection) - MIN_SHIFT)
    null = np.empty(N_NULL)
    for i in range(N_NULL):
        null[i] = spearman(movement, np.roll(connection, int(rng.choice(shifts))))
    if tail == "lower":
        p = (1 + np.sum(null <= observed)) / (N_NULL + 1)
    else:
        p = (1 + np.sum(null >= observed)) / (N_NULL + 1)
    return float(p), null


def window_score(
    view: dict[str, np.ndarray | float | int],
    interval: tuple[float, float],
    rng: np.random.Generator | None = None,
) -> tuple[dict[str, float | int], pd.DataFrame, dict[str, np.ndarray]]:
    times = np.asarray(view["times"], dtype=float)
    mask = mask_interval(times, interval)
    t = times[mask]
    frequency = np.asarray(view["centroid_hz"], dtype=float)[mask]
    connection = np.asarray(view["connection_ara"], dtype=float)[mask]
    amount = np.asarray(view["amount_ara"], dtype=float)[mask]
    density = np.asarray(view["density_ara"], dtype=float)[mask]
    period = np.asarray(view["period_ara"], dtype=float)[mask]
    movement = remaining_traversal(frequency)
    total = movement + connection
    residual = np.abs(total - 2.0)
    rho_inverse = spearman(movement, connection)
    rho_growth = spearman(t, connection)
    rho_period = spearman(period, connection)
    inverse_p = growth_p = float("nan")
    inverse_null = growth_null = np.asarray([], dtype=float)
    if rng is not None:
        inverse_p, inverse_null = circular_relation_p(movement, connection, rho_inverse, rng, "lower")
        growth_p, growth_null = circular_relation_p(t, connection, rho_growth, rng, "upper")
    score = {
        "window_start_s": interval[0],
        "window_end_s": interval[1],
        "n_frames": int(len(t)),
        "inverse_rho": rho_inverse,
        "inverse_shift_p": inverse_p,
        "connection_time_rho": rho_growth,
        "connection_time_shift_p": growth_p,
        "period_connection_rho": rho_period,
        "median_te_ara_residual": float(np.nanmedian(residual)),
        "closure_occupancy": float(np.nanmean(residual <= 0.50)),
        "median_te_ara_sum": float(np.nanmedian(total)),
        "first_persistent_connection_ridge_s": first_persistent_time(t, connection),
        "start_connection": float(connection[0]),
        "end_connection": float(connection[-1]),
    }
    history = pd.DataFrame({
        "time_s": t,
        "M_rem": movement,
        "C_acc": connection,
        "TE_ARA_sum": total,
        "TE_ARA_residual": residual,
        "C_amount": amount,
        "C_density": density,
        "local_period_ARA": period,
        "frequency_hz": frequency,
    })
    return score, history, {"inverse": inverse_null, "growth": growth_null}


def detector_agreement(view: dict[str, np.ndarray | float | int], rng: np.random.Generator) -> tuple[float, float, np.ndarray]:
    times = np.asarray(view["times"], dtype=float)
    mask = mask_interval(times, PRIMARY_INTERVAL)
    h = np.asarray(view["h_connection"], dtype=float)[mask]
    l = np.asarray(view["l_connection"], dtype=float)[mask]
    valid = np.isfinite(h) & np.isfinite(l)
    h, l = h[valid], l[valid]
    observed = spearman(h, l)
    shifts = np.arange(MIN_SHIFT, len(l) - MIN_SHIFT)
    null = np.empty(N_NULL)
    for i in range(N_NULL):
        null[i] = spearman(h, np.roll(l, int(rng.choice(shifts))))
    p = float((1 + np.sum(null >= observed)) / (N_NULL + 1))
    return observed, p, null


def offsource_windows(
    view: dict[str, np.ndarray | float | int],
    duration: float,
) -> tuple[pd.DataFrame, list[pd.DataFrame]]:
    rows: list[dict[str, float | int]] = []
    histories: list[pd.DataFrame] = []
    step = duration / 2.0
    for interval_index, (lo, hi) in enumerate(OFF_INTERVALS):
        starts = np.arange(lo, hi - duration + 1e-9, step)
        for window_index, start in enumerate(starts):
            interval = (float(start), float(start + duration))
            score, history, _ = window_score(view, interval)
            score.update({"off_interval": interval_index, "off_window": window_index})
            rows.append(score)
            history["off_interval"] = interval_index
            history["off_window"] = window_index
            history["relative_window_time_s"] = history["time_s"] - interval[0]
            histories.append(history)
    return pd.DataFrame(rows), histories


def load_sources(phase: str) -> tuple[list[dict[str, object]], dict[str, dict[str, pathlib.Path]]]:
    if phase == "development":
        manifest = json.loads(OLD_MANIFEST.read_text(encoding="utf-8"))
        audit = json.loads(OLD_AUDIT.read_text(encoding="utf-8"))
        events = [dict(row, role="development_seen") for row in manifest["events"]]
    else:
        audit = json.loads(NEW_AUDIT.read_text(encoding="utf-8"))
        event_rows: dict[str, dict[str, object]] = {}
        for row in audit:
            event_rows.setdefault(row["event"], {
                "event": row["event"], "gps": row["gps"], "role": "untouched_confirmation"
            })
        events = list(event_rows.values())
    paths: dict[str, dict[str, pathlib.Path]] = {}
    for row in audit:
        if row["detector"] not in {"H1", "L1"}:
            continue
        paths.setdefault(row["event"], {})[row["detector"]] = pathlib.Path(row["local_path"])
    return events, paths


def load_parameters(phase: str, events: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    if phase == "development":
        payload = json.loads(OLD_PARAMETERS.read_text(encoding="utf-8"))
        return {row["event"]: row for row in payload["events"]}
    out: dict[str, dict[str, object]] = {}
    audit = json.loads(NEW_AUDIT.read_text(encoding="utf-8"))
    for event in events:
        row = next(x for x in audit if x["event"] == event["event"])
        out[event["event"]] = json.loads(pathlib.Path(row["parameters_path"]).read_text(encoding="utf-8"))
    return out


def analyse(phase: str) -> tuple[
    dict[str, dict[str, object]], pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    events, paths = load_sources(phase)
    bundles: dict[str, dict[str, object]] = {}
    summaries: list[dict[str, object]] = []
    all_histories: list[pd.DataFrame] = []
    all_off: list[pd.DataFrame] = []
    qa_rows: list[dict[str, object]] = []

    for event_index, event in enumerate(events):
        name = str(event["event"])
        rng = np.random.default_rng(SEED + event_index + (0 if phase == "development" else 100))
        detectors: dict[str, t427.DetectorData] = {}
        features: dict[str, DetectorFeatures] = {}
        for detector in ("H1", "L1"):
            det, feat = build_detector(event, detector, paths[name][detector])
            detectors[detector] = det
            features[detector] = feat
            qa_rows.append(feat.qa)
        view = network_view(features)
        primary, history, nulls = window_score(view, PRIMARY_INTERVAL, rng)
        wide, _, _ = window_score(view, WIDE_INTERVAL, rng)
        agree, agree_p, agree_null = detector_agreement(view, rng)
        off, off_histories = offsource_windows(view, PRIMARY_INTERVAL[1] - PRIMARY_INTERVAL[0])

        residual_pct = float(np.mean(off["median_te_ara_residual"] <= primary["median_te_ara_residual"]))
        occupancy_pct = float(np.mean(off["closure_occupancy"] < primary["closure_occupancy"]))
        primary.update({
            "event": name,
            "role": event["role"],
            "residual_offsource_percentile": residual_pct,
            "occupancy_offsource_percentile": occupancy_pct,
            "detector_connection_rho": agree,
            "detector_connection_shift_p": agree_p,
            "lag_ms": view["lag_ms"],
            "lag_corr": view["lag_corr"],
            "wide_inverse_rho": wide["inverse_rho"],
            "wide_connection_time_rho": wide["connection_time_rho"],
            "wide_median_residual": wide["median_te_ara_residual"],
            "wide_closure_occupancy": wide["closure_occupancy"],
            "n_offsource_windows": len(off),
        })
        summaries.append(primary)
        history.insert(0, "event", name)
        history.insert(1, "role", event["role"])
        all_histories.append(history)
        off.insert(0, "event", name)
        all_off.append(off)
        bundles[name] = {
            "event": event,
            "detectors": detectors,
            "features": features,
            "view": view,
            "primary": primary,
            "history": history,
            "offsource": off,
            "offsource_histories": off_histories,
            "nulls": {**nulls, "agreement": agree_null},
        }

    return (
        bundles,
        pd.DataFrame(summaries),
        pd.concat(all_histories, ignore_index=True),
        pd.concat(all_off, ignore_index=True),
        pd.DataFrame(qa_rows),
    )


def confirmation_gates(summary: pd.DataFrame) -> dict[str, object]:
    n = len(summary)
    g1_rows = (summary.inverse_rho <= -0.30) & (summary.inverse_shift_p <= 0.05)
    g2_rows = summary.residual_offsource_percentile <= 0.10
    g3_rows = (summary.connection_time_rho >= 0.30) & (summary.connection_time_shift_p <= 0.05)
    g4_rows = (summary.closure_occupancy >= 0.60) & (summary.occupancy_offsource_percentile >= 0.95)
    g5_rows = (summary.detector_connection_rho > 0) & (summary.detector_connection_shift_p <= 0.05)
    counts = [int(x.sum()) for x in (g1_rows, g2_rows, g3_rows, g4_rows, g5_rows)]
    return {
        "denominator": n,
        "required_each": 3,
        "gate_1_inverse_gradient_count": counts[0],
        "gate_2_residual_control_count": counts[1],
        "gate_3_connection_growth_count": counts[2],
        "gate_4_closure_occupancy_count": counts[3],
        "gate_5_detector_agreement_count": counts[4],
        "event_gate_rows": {
            "gate_1_inverse": dict(zip(summary.event, g1_rows.astype(bool))),
            "gate_2_residual": dict(zip(summary.event, g2_rows.astype(bool))),
            "gate_3_growth": dict(zip(summary.event, g3_rows.astype(bool))),
            "gate_4_occupancy": dict(zip(summary.event, g4_rows.astype(bool))),
            "gate_5_agreement": dict(zip(summary.event, g5_rows.astype(bool))),
        },
        "primary_supported": bool(all(count >= 3 for count in counts)),
    }


def style() -> None:
    plt.style.use("dark_background")
    plt.rcParams.update({
        "figure.facecolor": "#0b1220", "axes.facecolor": "#111827",
        "axes.edgecolor": "#94a3b8", "axes.labelcolor": "#e5e7eb",
        "xtick.color": "#cbd5e1", "ytick.color": "#cbd5e1",
        "grid.color": "#334155", "font.size": 10,
    })


def plot_event(event: str, bundle: dict[str, object], crosswalk: pd.DataFrame, out: pathlib.Path) -> None:
    style()
    history = bundle["history"]
    score = bundle["primary"]
    view = bundle["view"]
    times = np.asarray(view["times"], dtype=float)
    mask = mask_interval(times, PRIMARY_INTERVAL)
    t = history.time_s.to_numpy()
    fig, axes = plt.subplots(3, 2, figsize=(16, 15), constrained_layout=True)

    ax = axes[0, 0]
    ax.plot(t, history.M_rem, lw=2, color="#60a5fa", label="M_rem: traversal still available (2→0)")
    ax.plot(t, history.C_acc, lw=2, color="#f59e0b", label="C_acc: independent connection-facing state (0→2)")
    ax.plot(t, history.TE_ARA_sum, lw=1.4, color="#22c55e", label="M_rem + C_acc")
    ax.axhline(1, color="#cbd5e1", ls=":", label="ARA ridge 1")
    ax.axhline(2, color="white", ls="--", label="pure TE-ARA total 2")
    ax.set(title="The corrected inverse-gradient cut through time", xlabel="Seconds relative to official event GPS", ylabel="Independent ARA coordinate / sum", ylim=(0, 3.6)); ax.grid(True); ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(history.M_rem, history.C_acc, color="#94a3b8", alpha=.6, lw=.9)
    sc = ax.scatter(history.M_rem, history.C_acc, c=t, cmap="viridis", s=24)
    x = np.linspace(0, 2, 201)
    ax.plot(x, 2 - x, color="white", ls="--", lw=1.5, label="pure inverse shore: M+C=2")
    ax.axvline(1, color="#cbd5e1", ls=":"); ax.axhline(1, color="#cbd5e1", ls=":")
    ax.set(title=f"Chronological ARA plane | rho={score['inverse_rho']:.3f}, p={score['inverse_shift_p']:.3f}", xlabel="M_rem — remaining traversal (0–2)", ylabel="C_acc — connection-facing state (0–2)", xlim=(0, 2), ylim=(0, 2)); ax.grid(True); ax.legend(fontsize=8)
    fig.colorbar(sc, ax=ax, label="Seconds relative to event GPS")

    ax = axes[1, 0]
    ax.fill_between(t, 0, history.TE_ARA_residual, color="#a78bfa", alpha=.28)
    ax.plot(t, history.TE_ARA_residual, color="#c084fc", lw=1.8, label="|M_rem+C_acc−2|")
    ax.axhline(.5, color="white", ls="--", label="frozen closure tolerance 0.50")
    ridge = score["first_persistent_connection_ridge_s"]
    if np.isfinite(ridge):
        ax.axvline(ridge, color="#f59e0b", ls=":", label=f"first persistent C ridge {ridge:.3f}s")
    ax.set(title=f"TE-ARA closure | median residual={score['median_te_ara_residual']:.3f}; occupancy={score['closure_occupancy']:.1%}", xlabel="Seconds relative to event GPS", ylabel="Absolute TE-ARA residual", ylim=(0, max(1.25, float(history.TE_ARA_residual.max()) * 1.1))); ax.grid(True); ax.legend(fontsize=8)

    ax = axes[1, 1]
    ax.plot(t, history.C_amount, color="#fb923c", label="C_amount: received spectral amount")
    ax.plot(t, history.C_density, color="#22c55e", label="C_density: spectral concentration")
    ax.plot(t, history.C_acc, color="white", lw=2, label="C_acc: independent component mean")
    ax.axhline(1, color="#cbd5e1", ls=":", label="off-source ridge")
    ax.set(title=f"What creates connection | time rho={score['connection_time_rho']:.3f}, p={score['connection_time_shift_p']:.3f}", xlabel="Seconds relative to event GPS", ylabel="Connection-facing ARA coordinate (0–2)", ylim=(0, 2)); ax.grid(True); ax.legend(fontsize=8)

    ax = axes[2, 0]
    h = np.asarray(view["h_connection"])[mask]
    l = np.asarray(view["l_connection"])[mask]
    ax.plot(t, h, color="#60a5fa", label="H1 connection view")
    ax.plot(t, l, color="#f59e0b", label="L1 connection view after frozen lag")
    ax.set(title=f"Independent detector check | rho={score['detector_connection_rho']:.3f}, p={score['detector_connection_shift_p']:.3f}; lag={score['lag_ms']:.1f} ms", xlabel="Seconds relative to event GPS", ylabel="Detector connection coordinate (0–2)", ylim=(0, 2)); ax.grid(True); ax.legend(fontsize=8)

    ax = axes[2, 1]
    cross = crosswalk.loc[crosswalk.event == event]
    ax.plot(cross.time_s, cross.separation_km, color="#60a5fa", lw=1.8, label="orbital separation proxy (km)")
    ax2 = ax.twinx()
    ax2.plot(cross.time_s, cross.binding_proxy, color="#f59e0b", lw=1.8, label="binding proxy")
    ax.set(title="Established-physics crosswalk (unlocked only after ARA scoring)", xlabel="Seconds relative to official event GPS", ylabel="Separation proxy (km)"); ax2.set_ylabel("eta × GM/(r c²)", color="#f59e0b"); ax.grid(True)
    lines = ax.get_lines() + ax2.get_lines(); ax.legend(lines, [line.get_label() for line in lines], fontsize=8)

    fig.suptitle(f"T430 {event} — remaining traversal versus accumulated connection", fontsize=18, fontweight="bold")
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_gallery(bundles: dict[str, dict[str, object]], summary: pd.DataFrame, out: pathlib.Path) -> None:
    style()
    fig, axes = plt.subplots(2, 2, figsize=(15, 13), constrained_layout=True)
    for ax, (event, bundle) in zip(axes.flat, bundles.items()):
        h = bundle["history"]
        row = summary.loc[summary.event == event].iloc[0]
        ax.plot(h.M_rem, h.C_acc, color="#94a3b8", lw=.9, alpha=.6)
        ax.scatter(h.M_rem, h.C_acc, c=h.time_s, cmap="viridis", s=17)
        x = np.linspace(0, 2, 201)
        ax.plot(x, 2 - x, color="white", ls="--", label="M+C=2")
        ax.axvline(1, color="#cbd5e1", ls=":"); ax.axhline(1, color="#cbd5e1", ls=":")
        ax.set(title=f"{event} | rho {row.inverse_rho:.2f}, p {row.inverse_shift_p:.3f} | closure {row.closure_occupancy:.0%}", xlabel="M_rem remaining traversal (0–2)", ylabel="C_acc connection-facing state (0–2)", xlim=(0, 2), ylim=(0, 2)); ax.grid(True); ax.legend(fontsize=8)
    fig.suptitle("T430 untouched confirmation — identical-scale inverse-gradient ARA paths", fontsize=18, fontweight="bold")
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_controls(summary: pd.DataFrame, offsource: pd.DataFrame, out: pathlib.Path) -> None:
    style()
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), constrained_layout=True)
    metrics = [
        ("inverse_rho", "Inverse gradient: event versus off-source", "Spearman rho (more negative supports opposition)"),
        ("median_te_ara_residual", "TE-ARA residual: event versus off-source", "Median |M+C−2| (lower is better)"),
        ("closure_occupancy", "Closure occupancy: event versus off-source", "Fraction within residual ≤0.50 (higher is better)"),
        ("connection_time_rho", "Connection growth: event versus off-source", "Spearman rho(time,C_acc)"),
    ]
    for ax, (metric, title, ylabel) in zip(axes.flat, metrics):
        events = summary.event.tolist()
        data = [offsource.loc[offsource.event == event, metric].to_numpy() for event in events]
        positions = np.arange(len(events))
        box = ax.boxplot(data, positions=positions, widths=.55, patch_artist=True, showfliers=False)
        for patch in box["boxes"]:
            patch.set_facecolor("#334155")
        ax.scatter(positions, summary[metric], color="#f59e0b", s=70, zorder=4, label="event window")
        ax.set_xticks(positions, events, rotation=20)
        ax.set(title=title, ylabel=ylabel); ax.grid(True, axis="y"); ax.legend(fontsize=8)
    fig.suptitle("T430 matched-duration controls — the 2→0 movement bookkeeping is applied everywhere", fontsize=17, fontweight="bold")
    fig.savefig(out, dpi=180)
    plt.close(fig)


def build_crosswalk(
    bundles: dict[str, dict[str, object]],
    parameters: dict[str, dict[str, object]],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for event, bundle in bundles.items():
        view = bundle["view"]
        cross = t429.source_crosswalk(view, parameters[event])
        times = np.asarray(view["times"], dtype=float)
        mask = mask_interval(times, PRIMARY_INTERVAL)
        for i in np.where(mask)[0]:
            rows.append({
                "event": event,
                "time_s": times[i],
                "frequency_hz": np.asarray(view["centroid_hz"])[i],
                "separation_km": np.asarray(cross["separation_km"])[i],
                "binding_proxy": np.asarray(cross["binding"])[i],
                "compactness": np.asarray(cross["compactness"])[i],
            })
    return pd.DataFrame(rows)


def image_uri(path: pathlib.Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def html_table(frame: pd.DataFrame, columns: list[str], digits: int = 3) -> str:
    display = frame[columns].copy()
    for column in display.select_dtypes(include=["float"]).columns:
        display[column] = display[column].map(lambda value: f"{value:.{digits}f}" if np.isfinite(value) else "—")
    return display.to_html(index=False, border=0, classes="data")


def build_html_report(
    summary: pd.DataFrame,
    gates: dict[str, object],
    figures: list[pathlib.Path],
    phase: str,
) -> pathlib.Path:
    supported = gates.get("primary_supported") if gates else None
    outcome = "SUPPORTED" if supported else "NOT SUPPORTED" if supported is not None else "EXPLORATORY"
    cards = "".join(
        f"<div class='card'><strong>{key.replace('_', ' ')}</strong><span>{value}</span></div>"
        for key, value in gates.items() if key.startswith("gate_") and key.endswith("_count")
    )
    columns = [
        "event", "inverse_rho", "inverse_shift_p", "connection_time_rho", "connection_time_shift_p",
        "median_te_ara_residual", "residual_offsource_percentile", "closure_occupancy",
        "occupancy_offsource_percentile", "detector_connection_rho", "detector_connection_shift_p",
    ]
    images = "".join(f"<img src='{image_uri(path)}' alt='{path.stem}'>" for path in figures)
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>T430 report</title><style>
    body{{margin:0;background:#07101d;color:#e5e7eb;font:16px/1.55 system-ui,Segoe UI,sans-serif}}
    main{{max-width:1500px;margin:auto;padding:32px}} h1{{font-size:2.2rem;margin-bottom:.2rem}} h2{{margin-top:2.2rem;color:#93c5fd}}
    .sub{{color:#94a3b8}} .outcome{{font-size:1.35rem;color:#fbbf24;font-weight:800}} .cards{{display:flex;gap:12px;flex-wrap:wrap}}
    .card{{background:#111827;border:1px solid #334155;border-radius:12px;padding:14px;min-width:190px;display:flex;flex-direction:column}}
    .card span{{font-size:1.7rem;color:#fbbf24}} img{{width:100%;margin:18px 0;border:1px solid #334155;border-radius:12px}}
    table.data{{border-collapse:collapse;width:100%;font-size:.82rem;background:#111827}} .data th,.data td{{padding:8px;border:1px solid #334155;text-align:right}}
    .data th:first-child,.data td:first-child{{text-align:left}} code{{color:#fbbf24}} .note{{border-left:4px solid #60a5fa;padding:10px 16px;background:#0f1b2d}}
    </style></head><body><main>
    <h1>T430 — Remaining traversal versus accumulated connection</h1>
    <p class='sub'>Frozen same-rung inverse-gradient test | phase: {phase} | public GWOSC strain | generated 2026-08-24</p>
    <p class='outcome'>Frozen confirmation outcome: {outcome}</p>
    <h2>Answer first</h2>
    <p>This test corrects T429's movement-identity error. <code>M_rem</code> is now the traversal budget still left in the scored window, while <code>C_acc</code> is independently assembled from spectral amount and concentration. Their complement is tested, never imposed. Equal-duration off-source windows receive the same 2→0 movement construction.</p>
    <div class='cards'>{cards}</div>
    <h2>Exact event metrics</h2>{html_table(summary, columns)}
    <h2>Visual findings</h2>{images}
    <h2>ARA reading</h2>
    <p>One binary-black-hole event is one identity. H1 and L1 are independent observations. The blue child is remaining traversal (2→0); the orange child is the observed connection-facing state. The dashed diagonal is pure TE-ARA closure at 2. Individual paths may miss it because the observed system, detector response, noise and unmeasured children distort the pure landmark.</p>
    <h2>Established-physics crosswalk</h2>
    <p>The final panel converts the same observed frequency history into an orbital-separation and binding proxy. It was unlocked only after all model-free ARA histories and scores were written. It translates the relation; it does not define or rescue it.</p>
    <h2>Method and controls</h2>
    <p>64 ms Hann STFT, 4 ms hop, 30–512 Hz; primary interval −0.50 to −0.03 s. Detector features are off-source empirical-CDF projections onto 0–2. Circular shifts test temporal ordering; sliding off-source windows test whether closure is special to the event; shifted detector histories test shared-source agreement. Four events absent from T427–T429 were held untouched until the protocol hash was frozen.</p>
    <h2>Limitations and unresolved boundary</h2>
    <p class='note'><strong>Instrument boundary:</strong> despite the frozen name <code>C_acc</code>, the implemented feature is an instantaneous connection-facing state (amount plus concentration), not a cumulative integral. Also, because <code>M_rem</code> is strictly decreasing, inverse-gradient rho and connection-growth rho are the same ranked test with opposite signs; they are not independent evidence. A pass would support this operational instrument in event-locked strain, not universal ARA or a replacement for general relativity. A failure rejects this coordinate construction and sampling scale, not the framework. The official event time supplies the crop endpoint, so this is retrospective rather than a blind forecast.</p>
    <h2>Next falsifier</h2>
    <p>If supported, freeze the event endpoint independently of the catalog time and ask whether the two-child state predicts it prospectively. If unsupported, inspect which independent child—amount or concentration—breaks the same-rung relation before changing any identity.</p>
    </main></body></html>"""
    path = RESULTS / f"T430_{phase.upper()}_REMAINING_TRAVERSAL_CONNECTION_REPORT.html"
    path.write_text(html, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("development", "confirmation"), required=True)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    bundles, summary, histories, offsource, qa = analyse(args.phase)

    prefix = f"T430_{args.phase.upper()}"
    # Model-free outputs are written before the established-physics parameter file is opened.
    summary.to_csv(RESULTS / f"{prefix}_SUMMARY.csv", index=False)
    histories.to_csv(RESULTS / f"{prefix}_HISTORIES.csv", index=False)
    offsource.to_csv(RESULTS / f"{prefix}_OFFSOURCE_CONTROLS.csv", index=False)
    qa.to_csv(RESULTS / f"{prefix}_SOURCE_QA.csv", index=False)

    parameters = load_parameters(args.phase, [bundle["event"] for bundle in bundles.values()])
    crosswalk = build_crosswalk(bundles, parameters)
    crosswalk.to_csv(RESULTS / f"{prefix}_PHYSICS_CROSSWALK.csv", index=False)

    figures: list[pathlib.Path] = []
    for event, bundle in bundles.items():
        path = RESULTS / f"T430_{event}_INVERSE_GRADIENT_DIAGNOSTIC.png"
        plot_event(event, bundle, crosswalk, path)
        figures.append(path)
    if args.phase == "confirmation":
        gallery = RESULTS / "T430_CONFIRMATION_ARA_GALLERY.png"
        controls = RESULTS / "T430_CONFIRMATION_CONTROLS.png"
        plot_gallery(bundles, summary, gallery)
        plot_controls(summary, offsource, controls)
        figures = [gallery, controls] + figures
        gates = confirmation_gates(summary)
        (RESULTS / "T430_CONFIRMATION_GATES.json").write_text(json.dumps(gates, indent=2), encoding="utf-8")
    else:
        gates = {}
    report = build_html_report(summary, gates, figures, args.phase)
    run = {
        "phase": args.phase,
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(pathlib.Path(__file__)),
        "events": list(bundles),
        "model_free_outputs_written_before_physics_parameters_loaded": True,
        "report": report.as_posix(),
    }
    (RESULTS / f"{prefix}_RUN.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
    print(json.dumps({"gates": gates, "summary": summary.to_dict(orient="records"), "report": str(report)}, indent=2, default=str))


if __name__ == "__main__":
    main()
