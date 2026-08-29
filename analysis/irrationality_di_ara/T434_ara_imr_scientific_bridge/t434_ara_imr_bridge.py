"""T434: frozen ARA / published IMR-cutoff bridge comparison."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import pathlib
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)
T427_DIR = HERE.parent / "T427_spacetime_strain_handover"
T427_RESULTS = T427_DIR / "results"
sys.path.insert(0, str(T427_DIR))
import t427_spacetime_strain_handover as t427  # noqa: E402

COORDS = T427_RESULTS / "T427_CONSENSUS_COORDINATES.csv"
SOURCE_AUDIT = T427_RESULTS / "T427_SOURCE_AUDIT.json"
EVENTS = ["GW170104", "GW170809", "GW170814", "GW170818"]
IMR = {
    "GW170104": {"fc_hz": 143.0, "rho_insp": 10.9, "rho_post": 8.5, "gr_quantile_pct": 24.4},
    "GW170809": {"fc_hz": 136.0, "rho_insp": 10.6, "rho_post": 7.1, "gr_quantile_pct": 14.7},
    "GW170814": {"fc_hz": 161.0, "rho_insp": 15.3, "rho_post": 7.2, "gr_quantile_pct": 7.8},
    "GW170818": {"fc_hz": 128.0, "rho_insp": 9.3, "rho_post": 7.2, "gr_quantile_pct": 25.5},
}
WINDOW = (-0.25, 0.05)
SMOOTH_FRAMES = 7
FREQ_INTEGRATE_FRAMES = 4
MIN_SHIFT_FRAMES = 16
N_NULL = 10_000
SEED = 43420260826


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rolling_median(values: np.ndarray, width: int = SMOOTH_FRAMES) -> np.ndarray:
    return pd.Series(values).rolling(width, center=True, min_periods=1).median().to_numpy()


def crossing_landmark(frame: pd.DataFrame) -> dict[str, float | str]:
    times = frame.time_s.to_numpy(float)
    c1 = rolling_median(frame.c1.to_numpy(float))
    c2 = rolling_median(frame.c2.to_numpy(float))
    z = rolling_median(frame.z_native.to_numpy(float))
    delta = c1 - c2
    peak_idx = int(np.nanargmax(z))
    peak_time = float(times[peak_idx])
    candidates: list[tuple[float, float, int, float]] = []
    for i in range(len(delta) - 1):
        if not np.isfinite(delta[i:i+2]).all():
            continue
        if delta[i] == 0 or delta[i] * delta[i + 1] < 0:
            denom = abs(delta[i]) + abs(delta[i + 1])
            frac = 0.0 if denom == 0 else abs(delta[i]) / denom
            t_cross = float(times[i] + frac * (times[i + 1] - times[i]))
            parent = float((c1[i] + c2[i] + c1[i + 1] + c2[i + 1]) / 4.0)
            candidates.append((abs(t_cross - peak_time), abs(parent - 1.0), i, t_cross))
    if candidates:
        _, _, idx, landmark_time = min(candidates)
        mode = "zero_crossing_nearest_activity_peak"
    else:
        local = np.where(np.abs(times - peak_time) <= 0.064)[0]
        if len(local) == 0:
            local = np.arange(len(times))
        idx = int(local[np.nanargmin(np.abs(delta[local]))])
        landmark_time = float(times[idx])
        mode = "minimum_child_gap_near_activity_peak"
    c1_at = float(np.interp(landmark_time, times, c1))
    c2_at = float(np.interp(landmark_time, times, c2))
    return {
        "landmark_time_s": landmark_time,
        "activity_peak_time_s": peak_time,
        "c1_at_landmark": c1_at,
        "c2_at_landmark": c2_at,
        "parent_mean_at_landmark": (c1_at + c2_at) / 2.0,
        "landmark_mode": mode,
    }


def align_2d(values: np.ndarray, lag: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=float)
    if lag == 0:
        out[:] = values
    elif lag > 0:
        out[:, :-lag] = values[:, lag:]
    else:
        out[:, -lag:] = values[:, :lag]
    return out


def event_frequency_track(event: str, audit_rows: list[dict[str, object]]) -> pd.DataFrame:
    rows = [x for x in audit_rows if x["event"] == event and x["detector"] in {"H1", "L1"}]
    by_det = {str(x["detector"]): x for x in rows}
    if set(by_det) != {"H1", "L1"}:
        raise RuntimeError(f"Missing H1/L1 source for {event}")
    event_meta = {"event": event, "gps": float(by_det["H1"]["gps"]), "role": "T434_scientific_bridge"}
    h = t427.build_detector(event_meta, "H1", pathlib.Path(str(by_det["H1"]["local_path"])))
    l = t427.build_detector(event_meta, "L1", pathlib.Path(str(by_det["L1"]["local_path"])))
    lag_mask = (h.frame_rel >= -0.50) & (h.frame_rel <= 0.10)
    lag, lag_corr = t427.best_lag(h.z_native, l.z_native, 2, lag_mask)

    def normalized_power(det: t427.DetectorData) -> np.ndarray:
        off = t427.interval_mask(det.frame_rel, t427.OFF_INTERVALS)
        baseline = np.nanmedian(det.power[:, off], axis=1)
        baseline = np.where(np.isfinite(baseline) & (baseline > 1e-12), baseline, 1.0)
        return det.power / baseline[:, None]

    hp = normalized_power(h)
    lp = align_2d(normalized_power(l), lag)
    coherent = np.sqrt(np.clip(hp, 0, None) * np.clip(lp, 0, None))
    excess = np.clip(coherent - 1.0, 0.0, None)
    event_idx = np.where((h.frame_rel >= WINDOW[0]) & (h.frame_rel <= WINDOW[1]))[0]
    track_rows = []
    kernel = np.array([0.25, 0.5, 0.25])
    for idx in event_idx:
        lo = max(0, idx - FREQ_INTEGRATE_FRAMES)
        hi = min(excess.shape[1], idx + FREQ_INTEGRATE_FRAMES + 1)
        spectrum = np.nanmean(excess[:, lo:hi], axis=1)
        spectrum = np.convolve(np.nan_to_num(spectrum), kernel, mode="same")
        if not np.any(spectrum > 0):
            spectrum = np.nanmean(coherent[:, lo:hi], axis=1)
        ridge_idx = int(np.nanargmax(spectrum))
        total = float(np.nansum(spectrum))
        if total > 0:
            cumulative = np.cumsum(np.nan_to_num(spectrum))
            median_idx = int(np.searchsorted(cumulative, cumulative[-1] / 2.0))
            centroid = float(np.nansum(h.freqs * spectrum) / total)
        else:
            median_idx = ridge_idx
            centroid = float(h.freqs[ridge_idx])
        track_rows.append({
            "event": event,
            "time_s": float(h.frame_rel[idx]),
            "ridge_frequency_hz": float(h.freqs[ridge_idx]),
            "median_excess_frequency_hz": float(h.freqs[min(median_idx, len(h.freqs)-1)]),
            "centroid_excess_frequency_hz": centroid,
            "h1_l1_lag_ms": float(lag * t427.HOP_SECONDS * 1000.0),
            "h1_l1_activity_corr": float(lag_corr),
        })
    return pd.DataFrame(track_rows)


def auc_score(values: np.ndarray, labels: np.ndarray) -> float:
    values = np.asarray(values, float)
    labels = np.asarray(labels, bool)
    valid = np.isfinite(values)
    values, labels = values[valid], labels[valid]
    n1, n0 = int(labels.sum()), int((~labels).sum())
    if n1 < 5 or n0 < 5:
        return float("nan")
    ranks = pd.Series(values).rank(method="average").to_numpy()
    auc = (float(ranks[labels].sum()) - n1 * (n1 + 1) / 2.0) / (n1 * n0)
    return max(auc, 1.0 - auc)


def build_rows() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    coords = pd.read_csv(COORDS)
    audit = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    rows = []
    tracks: dict[str, pd.DataFrame] = {}
    for event in EVENTS:
        frame = coords[(coords.event == event) & coords.time_s.between(*WINDOW)].copy().sort_values("time_s")
        landmark = crossing_landmark(frame)
        track = event_frequency_track(event, audit)
        tracks[event] = track
        t = float(landmark["landmark_time_s"])
        f_ara = float(np.interp(t, track.time_s, track.ridge_frequency_hz))
        f_median = float(np.interp(t, track.time_s, track.median_excess_frequency_hz))
        f_centroid = float(np.interp(t, track.time_s, track.centroid_excess_frequency_hz))
        fc = IMR[event]["fc_hz"]
        merged = pd.merge_asof(
            frame.sort_values("time_s"), track.sort_values("time_s"), on="time_s", direction="nearest", tolerance=0.0025
        ).dropna(subset=["ridge_frequency_hz"])
        delta = rolling_median((merged.c1 - merged.c2).to_numpy(float))
        labels = merged.ridge_frequency_hz.to_numpy(float) >= fc
        rows.append({
            "event": event,
            **landmark,
            "ara_handover_ridge_frequency_hz": f_ara,
            "ara_handover_median_excess_frequency_hz": f_median,
            "ara_handover_centroid_excess_frequency_hz": f_centroid,
            "published_imr_fc_hz": fc,
            "absolute_percent_difference": abs(f_ara - fc) / fc * 100.0,
            "absolute_log_frequency_error": abs(math.log(f_ara / fc)),
            "orientation_invariant_auc": auc_score(delta, labels),
            "frames_below_fc": int((~labels).sum()),
            "frames_above_fc": int(labels.sum()),
            "rho_insp": IMR[event]["rho_insp"],
            "rho_post": IMR[event]["rho_post"],
            "gr_quantile_pct": IMR[event]["gr_quantile_pct"],
            "h1_l1_lag_ms": float(track.h1_l1_lag_ms.iloc[0]),
            "h1_l1_activity_corr": float(track.h1_l1_activity_corr.iloc[0]),
        })
    return pd.DataFrame(rows), tracks


def score_controls(rows: pd.DataFrame, tracks: dict[str, pd.DataFrame]) -> dict[str, object]:
    rng = np.random.default_rng(SEED)
    coords = pd.read_csv(COORDS)
    observed_error = float(np.median(rows.absolute_log_frequency_error))
    observed_auc = float(np.nanmedian(rows.orientation_invariant_auc))
    fc_values = np.array([IMR[e]["fc_hz"] for e in EVENTS], float)
    f_values = rows.set_index("event").loc[EVENTS, "ara_handover_ridge_frequency_hz"].to_numpy(float)
    wrong = []
    for perm in itertools.permutations(fc_values):
        wrong.append(float(np.median(np.abs(np.log(f_values / np.asarray(perm))))))
    p_wrong = float(np.mean(np.asarray(wrong) <= observed_error))

    # Cache the unchanged child histories and scientific frequency-regime labels.
    # This is mechanically identical to rebuilding them inside every null draw,
    # but avoids 40,000 redundant reads of the same frozen coordinate file.
    auc_inputs: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for event in EVENTS:
        track = tracks[event]
        frame = coords[(coords.event == event) & coords.time_s.between(*WINDOW)].copy().sort_values("time_s")
        merged = pd.merge_asof(
            frame,
            track.sort_values("time_s"),
            on="time_s",
            direction="nearest",
            tolerance=0.0025,
        ).dropna(subset=["ridge_frequency_hz"])
        delta = rolling_median((merged.c1 - merged.c2).to_numpy(float))
        labels = merged.ridge_frequency_hz.to_numpy(float) >= IMR[event]["fc_hz"]
        auc_inputs[event] = (delta, labels)

    shift_errors = np.empty(N_NULL)
    shift_aucs = np.empty(N_NULL)
    for k in range(N_NULL):
        errs, aucs = [], []
        for event in EVENTS:
            track = tracks[event]
            n = len(track)
            allowed = np.concatenate([np.arange(MIN_SHIFT_FRAMES, n // 2 + 1), np.arange(n // 2 + 1, n - MIN_SHIFT_FRAMES + 1)])
            shift = int(rng.choice(allowed))
            landmark_time = float(rows.loc[rows.event == event, "landmark_time_s"].iloc[0])
            idx = int(np.argmin(np.abs(track.time_s.to_numpy(float) - landmark_time)))
            f_shift = float(np.roll(track.ridge_frequency_hz.to_numpy(float), shift)[idx])
            errs.append(abs(math.log(f_shift / IMR[event]["fc_hz"])))

            delta, labels = auc_inputs[event]
            aucs.append(auc_score(np.roll(delta, shift), labels))
        shift_errors[k] = np.median(errs)
        shift_aucs[k] = np.nanmedian(aucs)
    p_shift_error = float((1 + np.sum(shift_errors <= observed_error)) / (N_NULL + 1))
    p_shift_auc = float((1 + np.sum(shift_aucs >= observed_auc)) / (N_NULL + 1))
    return {
        "observed_median_log_error": observed_error,
        "observed_median_absolute_percent_difference": float(np.median(rows.absolute_percent_difference)),
        "events_within_25_percent": int((rows.absolute_percent_difference <= 25.0).sum()),
        "wrong_event_assignment_p": p_wrong,
        "temporal_shift_error_p": p_shift_error,
        "observed_median_orientation_invariant_auc": observed_auc,
        "temporal_shift_auc_p": p_shift_auc,
        "wrong_event_error_values": wrong,
        "shift_error_quantiles": {str(q): float(np.quantile(shift_errors, q)) for q in (0.05, 0.5, 0.95)},
        "shift_auc_quantiles": {str(q): float(np.quantile(shift_aucs, q)) for q in (0.05, 0.5, 0.95)},
        "shift_errors": shift_errors,
        "shift_aucs": shift_aucs,
    }


def plot_comparison(rows: pd.DataFrame, controls: dict[str, object]) -> pathlib.Path:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), constrained_layout=True)
    x = np.arange(len(rows))
    ax = axes[0]
    ax.scatter(x, rows.published_imr_fc_hz, s=95, color="#d99a22", marker="s", label="Published IMR cutoff $f_c$")
    ax.scatter(x, rows.ara_handover_ridge_frequency_hz, s=95, facecolor="white", edgecolor="#2468b4", linewidth=2, label="Frozen ARA exchange frequency")
    for i, row in rows.reset_index(drop=True).iterrows():
        ax.plot([i, i], [row.published_imr_fc_hz, row.ara_handover_ridge_frequency_hz], color="#64748b", lw=1.3)
        ax.text(i, max(row.published_imr_fc_hz, row.ara_handover_ridge_frequency_hz)+8, f"{row.absolute_percent_difference:.1f}%", ha="center", fontsize=9)
    ax.set_xticks(x, rows.event, rotation=20)
    ax.set_ylim(20, 530)
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title("Frozen ARA exchange and published IMR boundary")
    ax.legend(fontsize=9)

    ax = axes[1]
    vals = np.asarray(controls["shift_errors"], float)
    ax.hist(vals, bins=36, color="#d9e6f5", edgecolor="#2468b4", alpha=.95)
    obs = float(controls["observed_median_log_error"])
    ax.axvline(obs, color="#d99a22", lw=2.5, label=f"Observed median = {obs:.3f}")
    ax.set_xlabel("Median |log($f_{ARA}/f_c$)|")
    ax.set_ylabel("Temporal-shift replicates")
    ax.set_title("Temporal bridge-destruction control (10,000 shifts)")
    ax.legend(fontsize=9)
    fig.suptitle("T434 — ARA / IMR scientific comparison", fontsize=17, fontweight="bold")
    out = RESULTS / "T434_ARA_IMR_COMPARISON.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def plot_gallery(rows: pd.DataFrame, tracks: dict[str, pd.DataFrame]) -> pathlib.Path:
    coords = pd.read_csv(COORDS)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True, sharey=True, constrained_layout=True)
    for ax, event in zip(axes.flat, EVENTS):
        row = rows.loc[rows.event == event].iloc[0]
        track = tracks[event]
        frame = coords[(coords.event == event) & coords.time_s.between(*WINDOW)].copy().sort_values("time_s")
        delta = rolling_median((frame.c1-frame.c2).to_numpy(float))
        ax.plot(track.time_s, track.ridge_frequency_hz, color="#2468b4", lw=1.5, marker="o", ms=2.5, label="model-free H1/L1 spectral ridge")
        ax.axhline(row.published_imr_fc_hz, color="#d99a22", lw=2, ls="--", label="published IMR $f_c$")
        ax.axvline(row.landmark_time_s, color="#111827", lw=1.6, ls=":", label="frozen ARA exchange")
        positive = delta >= 0
        ax.fill_between(frame.time_s, 30, 512, where=positive, color="#d9e6f5", alpha=.18, step="mid", label="C1-leading interval")
        ax.set_title(f"{event}: ARA {row.ara_handover_ridge_frequency_hz:.0f} Hz; IMR {row.published_imr_fc_hz:.0f} Hz")
        ax.set_xlim(*WINDOW); ax.set_ylim(30, 512)
        ax.set_xlabel("Seconds relative to event GPS"); ax.set_ylabel("Frequency (Hz)")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=9)
    fig.suptitle("T434 event paths — ARA child exchange against the traditional IMR split", fontsize=16, fontweight="bold")
    out = RESULTS / "T434_EVENT_GALLERY.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return out


def write_summary(rows: pd.DataFrame, controls: dict[str, object], gates: dict[str, bool]) -> None:
    supported = all(gates.values())
    lines = [
        "# T434 results — ARA / IMR scientific bridge",
        "",
        f"**Primary verdict: {'SUPPORTED' if supported else 'NOT SUPPORTED'} at this frozen cut.**",
        "",
        f"Median absolute frequency difference: {controls['observed_median_absolute_percent_difference']:.2f}%.",
        f"Events within 25%: {controls['events_within_25_percent']}/4.",
        f"Temporal-shift p-value: {controls['temporal_shift_error_p']:.4g}.",
        f"Wrong-event assignment p-value: {controls['wrong_event_assignment_p']:.4g}.",
        f"Median orientation-invariant AUC: {controls['observed_median_orientation_invariant_auc']:.3f}; shift p={controls['temporal_shift_auc_p']:.4g}.",
        "",
        "## Gates",
        "",
    ]
    lines += [f"- {'PASS' if value else 'FAIL'} — {name}" for name, value in gates.items()]
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "This compares a frozen ARA child exchange with a standard published IMR boundary. The ARA frequency translation and IMR analysis both ultimately use the same detector strain, but the event-specific published cutoff was not used to construct or select the ARA landmark. A failure rejects this operational bridge, not either parent framework.",
        "",
        "## Files",
        "",
        "- `results/T434_EVENT_RESULTS.csv`",
        "- `results/T434_FREQUENCY_TRACKS.csv`",
        "- `results/T434_RESULTS.json`",
        "- `results/T434_ARA_IMR_COMPARISON.png`",
        "- `results/T434_EVENT_GALLERY.png`",
    ]
    (HERE / "T434_RESULTS_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows, tracks = build_rows()
    controls = score_controls(rows, tracks)
    gates = {
        "median absolute percentage difference <= 20%": controls["observed_median_absolute_percent_difference"] <= 20.0,
        "at least 3/4 events within 25%": controls["events_within_25_percent"] >= 3,
        "temporal-shift frequency p <= 0.05": controls["temporal_shift_error_p"] <= 0.05,
        "wrong-event assignment p <= 0.05": controls["wrong_event_assignment_p"] <= 0.05,
        "median AUC >= 0.70 and shift p <= 0.05": controls["observed_median_orientation_invariant_auc"] >= 0.70 and controls["temporal_shift_auc_p"] <= 0.05,
    }
    supported = all(gates.values())
    rows.to_csv(RESULTS / "T434_EVENT_RESULTS.csv", index=False)
    pd.concat(tracks.values(), ignore_index=True).to_csv(RESULTS / "T434_FREQUENCY_TRACKS.csv", index=False)
    plot_comparison(rows, controls)
    plot_gallery(rows, tracks)
    payload = {
        "events": EVENTS,
        "official_imr_source": "https://dcc.ligo.org/public/0156/P1800316/008/O2_testingGR_v2.pdf",
        "controls": {k: v for k, v in controls.items() if k not in {"shift_errors", "shift_aucs", "wrong_event_error_values"}},
        "gates": gates,
        "primary_supported": supported,
        "source_hashes": {"T427_consensus": sha256(COORDS), "T427_source_audit": sha256(SOURCE_AUDIT)},
    }
    (RESULTS / "T434_RESULTS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    pd.DataFrame({"shift_error": controls["shift_errors"], "shift_auc": controls["shift_aucs"]}).to_csv(RESULTS / "T434_SHIFT_NULLS.csv", index=False)
    write_summary(rows, controls, gates)
    print(rows[["event", "landmark_time_s", "ara_handover_ridge_frequency_hz", "published_imr_fc_hz", "absolute_percent_difference", "orientation_invariant_auc"]].to_string(index=False))
    print(json.dumps({"gates": gates, "primary_supported": supported, "controls": payload["controls"]}, indent=2))


if __name__ == "__main__":
    main()
