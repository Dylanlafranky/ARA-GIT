from __future__ import annotations

import argparse
import hashlib
import json
import math
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
sys.path.insert(0, str(T427_ROOT))
import t427_spacetime_strain_handover as t427  # noqa: E402

PROTOCOL = ROOT / "T429_FROZEN_PROTOCOL.md"
MANIFEST = T427_ROOT / "T427_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
PARAMETERS = ROOT / "T429_SOURCE_PARAMETERS_MANIFEST.json"
EVENT_INTERVAL = (-1.50, 0.25)
MATURITY_INTERVAL = (-1.25, -0.03)
LATE_INTERVAL = (-0.25, -0.03)
OFF_INTERVALS = ((-12.0, -4.0), (4.0, 12.0))
SEED = 42920260824
N_NULL = 2_000
MIN_SHIFT = 16

G = 6.67430e-11
C = 299_792_458.0
M_SUN = 1.98847e30


@dataclass
class DetectorFeatures:
    detector: str
    times: np.ndarray
    centroid_hz: np.ndarray
    chirp_rate: np.ndarray
    amount_raw: np.ndarray
    frequency_ara: np.ndarray
    chirp_ara: np.ndarray
    amount_ara: np.ndarray
    z_native: np.ndarray
    whitened_sample_t: np.ndarray
    whitened: np.ndarray
    freqs: np.ndarray
    power: np.ndarray


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def interval_mask(times: np.ndarray, intervals: tuple[tuple[float, float], ...]) -> np.ndarray:
    mask = np.zeros(len(times), dtype=bool)
    for lo, hi in intervals:
        mask |= (times >= lo) & (times <= hi)
    return mask


def ecdf_ara(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    ref = np.sort(np.asarray(reference, dtype=float)[np.isfinite(reference)])
    if len(ref) < 30:
        raise ValueError("Insufficient off-source values for an ARA projection")
    ranks = np.searchsorted(ref, np.asarray(values, dtype=float), side="right")
    q = (ranks + 0.5) / (len(ref) + 1.0)
    return np.clip(2.0 * q, 0.0, 2.0)


def smooth(values: np.ndarray, size: int = 9) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return ndimage.median_filter(values, size=size, mode="nearest")


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    valid = np.isfinite(a) & np.isfinite(b)
    if np.sum(valid) < 20:
        return float("nan")
    return float(stats.spearmanr(a[valid], b[valid]).statistic)


def build_features(event: dict[str, object], detector: str, path: pathlib.Path) -> tuple[t427.DetectorData, DetectorFeatures]:
    det = t427.build_detector(event, detector, path)
    total = np.sum(det.power, axis=0) + t427.EPS
    p = det.power / total[None, :]
    centroid = np.sum(p * det.freqs[:, None], axis=0)
    log_centroid = smooth(np.log(np.maximum(centroid, 1e-9)), 9)
    chirp = np.maximum(np.gradient(log_centroid, t427.HOP_SECONDS), 0.0)
    chirp = smooth(chirp, 9)
    amount = np.log(total)
    off = interval_mask(det.frame_rel, OFF_INTERVALS)
    feature = DetectorFeatures(
        detector=detector,
        times=det.frame_rel,
        centroid_hz=centroid,
        chirp_rate=chirp,
        amount_raw=amount,
        frequency_ara=ecdf_ara(centroid, centroid[off]),
        chirp_ara=ecdf_ara(chirp, chirp[off]),
        amount_ara=ecdf_ara(amount, amount[off]),
        z_native=det.z_native,
        whitened_sample_t=det.sample_rel,
        whitened=det.band,
        freqs=det.freqs,
        power=det.power,
    )
    return det, feature


def align(values: np.ndarray, lag: int) -> np.ndarray:
    return t427.align_to_reference(np.asarray(values, dtype=float), lag)


def best_amount_lag(h: DetectorFeatures, l: DetectorFeatures) -> tuple[int, float]:
    mask = (h.times >= EVENT_INTERVAL[0]) & (h.times <= EVENT_INTERVAL[1])
    return t427.best_lag(h.amount_ara, l.amount_ara, 2, mask)


def network_model_free(features: dict[str, DetectorFeatures]) -> dict[str, np.ndarray | float | int]:
    h = features["H1"]
    l = features["L1"]
    lag, lag_corr = best_amount_lag(h, l)
    lf = align(l.frequency_ara, lag)
    lc = align(l.chirp_ara, lag)
    la = align(l.amount_ara, lag)
    lcent = align(l.centroid_hz, lag)

    frequency_ara = np.nanmean(np.vstack([h.frequency_ara, lf]), axis=0)
    chirp_ara = np.nanmean(np.vstack([h.chirp_ara, lc]), axis=0)
    amount_ara = np.nanmean(np.vstack([h.amount_ara, la]), axis=0)
    centroid_hz = np.nanmean(np.vstack([h.centroid_hz, lcent]), axis=0)

    agreement_raw = np.clip(1.0 - np.abs(h.amount_ara - la) / 2.0, 0.0, 1.0)
    off = interval_mask(h.times, OFF_INTERVALS) & np.isfinite(agreement_raw)
    agreement_ara = ecdf_ara(agreement_raw, agreement_raw[off])

    time_ara = np.nanmean(np.vstack([frequency_ara, chirp_ara]), axis=0)
    space_ara = np.nanmean(np.vstack([amount_ara, agreement_ara]), axis=0)
    return {
        "times": h.times,
        "frequency_ara": frequency_ara,
        "chirp_ara": chirp_ara,
        "amount_ara": amount_ara,
        "agreement_ara": agreement_ara,
        "time_ara": time_ara,
        "space_ara": space_ara,
        "centroid_hz": centroid_hz,
        "h_amount": h.amount_ara,
        "l_amount_aligned": la,
        "lag_frames": lag,
        "lag_seconds": lag * t427.HOP_SECONDS,
        "lag_corr": lag_corr,
    }


def block_shift_p(values: np.ndarray, times: np.ndarray, mask: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    v = np.asarray(values[mask], dtype=float)
    t = np.asarray(times[mask], dtype=float)
    valid = np.isfinite(v) & np.isfinite(t)
    v, t = v[valid], t[valid]
    observed = spearman(v, t)
    if len(v) < 2 * MIN_SHIFT + 1 or not np.isfinite(observed):
        return observed, float("nan")
    shifts = np.arange(MIN_SHIFT, len(v) - MIN_SHIFT)
    null = np.empty(N_NULL)
    for i in range(N_NULL):
        null[i] = spearman(np.roll(v, int(rng.choice(shifts))), t)
    p = float((1 + np.sum(null >= observed)) / (N_NULL + 1))
    return observed, p


def late_offsource_percentile(values: np.ndarray, times: np.ndarray) -> tuple[float, float, int]:
    late = (times >= LATE_INTERVAL[0]) & (times <= LATE_INTERVAL[1])
    observed = float(np.nanmedian(values[late]))
    duration = LATE_INTERVAL[1] - LATE_INTERVAL[0]
    medians: list[float] = []
    for lo, hi in OFF_INTERVALS:
        for start in np.arange(lo, hi - duration, duration / 2.0):
            mask = (times >= start) & (times <= start + duration)
            if np.sum(mask) >= 20:
                medians.append(float(np.nanmedian(values[mask])))
    off = np.asarray(medians, dtype=float)
    pct = float(np.mean(off < observed)) if len(off) else float("nan")
    return observed, pct, len(off)


def agreement_shift_p(view: dict[str, np.ndarray | float | int], times: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    mask = (times >= MATURITY_INTERVAL[0]) & (times <= MATURITY_INTERVAL[1])
    h = np.asarray(view["h_amount"], dtype=float)
    l = np.asarray(view["l_amount_aligned"], dtype=float)
    observed = float(np.nanmedian(1.0 - np.abs(h[mask] - l[mask]) / 2.0))
    event_h = h[mask]
    event_l = l[mask]
    shifts = np.arange(MIN_SHIFT, len(event_l) - MIN_SHIFT)
    null = np.empty(N_NULL)
    for i in range(N_NULL):
        shifted = np.roll(event_l, int(rng.choice(shifts)))
        null[i] = float(np.nanmedian(1.0 - np.abs(event_h - shifted) / 2.0))
    p = float((1 + np.sum(null >= observed)) / (N_NULL + 1))
    return observed, p


def source_crosswalk(view: dict[str, np.ndarray | float | int], row: dict[str, object]) -> dict[str, np.ndarray | float]:
    f = np.clip(np.asarray(view["centroid_hz"], dtype=float), 20.0, 1024.0)
    m1_source = float(row["mass_1_source"])
    m2_source = float(row["mass_2_source"])
    z = float(row["redshift"])
    total_source = m1_source + m2_source
    total_detector_kg = total_source * (1.0 + z) * M_SUN
    chirp_detector_kg = float(row["chirp_mass_source"]) * (1.0 + z) * M_SUN
    eta = m1_source * m2_source / total_source**2
    separation_m = (G * total_detector_kg / (np.pi * f) ** 2) ** (1.0 / 3.0)
    compactness = G * total_detector_kg / (separation_m * C**2)
    binding = eta * compactness
    tau = (5.0 / 256.0) * (G * chirp_detector_kg / C**3) ** (-5.0 / 3.0) * (np.pi * f) ** (-8.0 / 3.0)
    return {
        "separation_km": separation_m / 1000.0,
        "compactness": compactness,
        "binding": binding,
        "tau_s": tau,
        "eta": eta,
        "total_mass_source": total_source,
        "chirp_mass_detector": float(row["chirp_mass_source"]) * (1.0 + z),
    }


def coupling_shift_p(space: np.ndarray, binding: np.ndarray, times: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    mask = (times >= MATURITY_INTERVAL[0]) & (times <= MATURITY_INTERVAL[1])
    s = np.asarray(space[mask], dtype=float)
    b = np.asarray(binding[mask], dtype=float)
    valid = np.isfinite(s) & np.isfinite(b)
    s, b = s[valid], b[valid]
    observed = spearman(s, b)
    shifts = np.arange(MIN_SHIFT, len(s) - MIN_SHIFT)
    null = np.empty(N_NULL)
    for i in range(N_NULL):
        null[i] = spearman(np.roll(s, int(rng.choice(shifts))), b)
    p = float((1 + np.sum(null >= observed)) / (N_NULL + 1))
    return observed, p


def process_model_free(events: list[dict[str, object]]) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    bundles: dict[str, dict[str, object]] = {}
    rows: list[dict[str, object]] = []
    for event in events:
        paths = t427.detector_source_paths(event)
        detector_data: dict[str, t427.DetectorData] = {}
        features: dict[str, DetectorFeatures] = {}
        for detector in ("H1", "L1"):
            det, feature = build_features(event, detector, paths[detector])
            detector_data[detector] = det
            features[detector] = feature
        view = network_model_free(features)
        bundles[str(event["event"])] = {
            "event": event,
            "detectors": detector_data,
            "features": features,
            "view": view,
        }
        times = np.asarray(view["times"])
        event_mask = (times >= EVENT_INTERVAL[0]) & (times <= EVENT_INTERVAL[1])
        for i in np.where(event_mask)[0]:
            rows.append({
                "event": event["event"], "role": event["role"], "time_s": times[i],
                "T_frequency": view["frequency_ara"][i], "T_chirp": view["chirp_ara"][i],
                "S_amount": view["amount_ara"][i], "S_agreement": view["agreement_ara"][i],
                "T_A": view["time_ara"][i], "S_B": view["space_ara"][i],
                "frequency_hz": view["centroid_hz"][i],
            })
    return bundles, rows


def score_events(bundles: dict[str, dict[str, object]], parameter_rows: dict[str, dict[str, object]], rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict[str, object]] = []
    cross_rows: list[dict[str, object]] = []
    for event, bundle in bundles.items():
        view = bundle["view"]
        times = np.asarray(view["times"], dtype=float)
        maturity = (times >= MATURITY_INTERVAL[0]) & (times <= MATURITY_INTERVAL[1])
        t_rho, t_p = block_shift_p(np.asarray(view["time_ara"]), times, maturity, rng)
        s_rho, s_p = block_shift_p(np.asarray(view["space_ara"]), times, maturity, rng)
        t_late, t_pct, n_off = late_offsource_percentile(np.asarray(view["time_ara"]), times)
        s_late, s_pct, _ = late_offsource_percentile(np.asarray(view["space_ara"]), times)
        agree, agree_p = agreement_shift_p(view, times, rng)

        cross = source_crosswalk(view, parameter_rows[event])
        c_rho, c_p = coupling_shift_p(np.asarray(view["space_ara"]), np.asarray(cross["binding"]), times, rng)
        row = {
            "event": event,
            "role": bundle["event"]["role"],
            "time_rho": t_rho, "time_shift_p": t_p,
            "space_rho": s_rho, "space_shift_p": s_p,
            "late_time_ara": t_late, "late_time_off_pct": t_pct,
            "late_space_ara": s_late, "late_space_off_pct": s_pct,
            "n_off_windows": n_off,
            "amount_agreement": agree, "agreement_shift_p": agree_p,
            "space_binding_rho": c_rho, "space_binding_shift_p": c_p,
            "lag_ms": 1000.0 * float(view["lag_seconds"]),
            "lag_corr": float(view["lag_corr"]),
            "m1_source_msun": parameter_rows[event]["mass_1_source"],
            "m2_source_msun": parameter_rows[event]["mass_2_source"],
            "chirp_source_msun": parameter_rows[event]["chirp_mass_source"],
            "distance_mpc": parameter_rows[event]["luminosity_distance"],
            "network_snr": parameter_rows[event]["network_matched_filter_snr"],
            "eta": cross["eta"],
        }
        summary_rows.append(row)
        event_mask = (times >= EVENT_INTERVAL[0]) & (times <= EVENT_INTERVAL[1])
        for i in np.where(event_mask)[0]:
            cross_rows.append({
                "event": event, "time_s": times[i],
                "frequency_hz": view["centroid_hz"][i],
                "T_A": view["time_ara"][i], "S_B": view["space_ara"][i],
                "separation_km": cross["separation_km"][i],
                "compactness": cross["compactness"][i],
                "binding_proxy": cross["binding"][i],
                "inspiral_tau_s": cross["tau_s"][i],
            })
        bundle["crosswalk"] = cross
    return pd.DataFrame(summary_rows), pd.DataFrame(cross_rows)


def style() -> None:
    plt.style.use("dark_background")
    plt.rcParams.update({
        "figure.facecolor": "#0b1220", "axes.facecolor": "#111827",
        "axes.edgecolor": "#94a3b8", "axes.labelcolor": "#e5e7eb",
        "xtick.color": "#cbd5e1", "ytick.color": "#cbd5e1",
        "grid.color": "#334155", "font.size": 10,
    })


def plot_event(event: str, bundle: dict[str, object], summary: pd.DataFrame, out: pathlib.Path) -> None:
    style()
    view = bundle["view"]
    times = np.asarray(view["times"])
    mask = (times >= EVENT_INTERVAL[0]) & (times <= EVENT_INTERVAL[1])
    t = times[mask]
    cross = bundle["crosswalk"]
    row = summary.loc[summary.event == event].iloc[0]
    fig, axes = plt.subplots(3, 2, figsize=(15, 15), constrained_layout=True)

    ax = axes[0, 0]
    for detector, offset in (("H1", 0.0), ("L1", 5.0)):
        feat = bundle["features"][detector]
        sm = (feat.whitened_sample_t >= EVENT_INTERVAL[0]) & (feat.whitened_sample_t <= EVENT_INTERVAL[1])
        ax.plot(feat.whitened_sample_t[sm], feat.whitened[sm] + offset, lw=.55, label=f"{detector} whitened strain (+{offset:g})")
    ax.axvline(0, color="white", ls="--", lw=1, label="published event GPS")
    ax.set(title="Received detector strain (measurement)", xlabel="Seconds relative to event GPS", ylabel="Whitened strain + display offset"); ax.grid(True); ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(t, np.asarray(view["frequency_ara"])[mask], color="#60a5fa", label="T frequency (0–2)")
    ax.plot(t, np.asarray(view["chirp_ara"])[mask], color="#a78bfa", label="T chirp rate (0–2)")
    ax.plot(t, np.asarray(view["time_ara"])[mask], color="white", lw=1.8, label="T_A mean")
    ax.axhline(1, color="#94a3b8", ls=":", label="off-source ridge")
    ax.set(title=f"Time/movement wave | rho={row.time_rho:.3f}, p={row.time_shift_p:.3f}", xlabel="Seconds relative to event GPS", ylabel="Independent ARA coordinate (0–2)", ylim=(0,2)); ax.grid(True); ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.plot(t, np.asarray(view["amount_ara"])[mask], color="#f59e0b", label="S received amount (0–2)")
    ax.plot(t, np.asarray(view["agreement_ara"])[mask], color="#22c55e", label="S H1/L1 agreement (0–2)")
    ax.plot(t, np.asarray(view["space_ara"])[mask], color="white", lw=1.8, label="S_B mean")
    ax.axhline(1, color="#94a3b8", ls=":", label="off-source ridge")
    ax.set(title=f"Space/connection wave | rho={row.space_rho:.3f}, p={row.space_shift_p:.3f}", xlabel="Seconds relative to event GPS", ylabel="Independent ARA coordinate (0–2)", ylim=(0,2)); ax.grid(True); ax.legend(fontsize=8)

    ax = axes[1, 1]
    ax.plot(np.asarray(view["time_ara"])[mask], np.asarray(view["space_ara"])[mask], color="#94a3b8", lw=.7, alpha=.55)
    sc = ax.scatter(np.asarray(view["time_ara"])[mask], np.asarray(view["space_ara"])[mask], c=t, cmap="viridis", s=13)
    ax.axvline(1, color="white", ls=":"); ax.axhline(1, color="white", ls=":")
    ax.set(title="Separated time-facing / space-facing Di-ARA path", xlabel="T_A phase/frequency movement (0–2)", ylabel="S_B amount/agreement connection (0–2)", xlim=(0,2), ylim=(0,2)); ax.grid(True)
    fig.colorbar(sc, ax=ax, label="Seconds relative to event GPS")

    ax = axes[2, 0]
    ax.plot(t, np.asarray(cross["separation_km"])[mask], color="#60a5fa", label="orbital separation proxy (km)")
    ax2 = ax.twinx()
    ax2.plot(t, np.asarray(cross["binding"])[mask], color="#f59e0b", label="dimensionless binding proxy")
    ax.axvline(0, color="white", ls="--", lw=1)
    ax.set(title="Established-physics crosswalk (not used by ARA)", xlabel="Seconds relative to event GPS", ylabel="Separation proxy (km)"); ax2.set_ylabel("eta × GM/(rc²)", color="#f59e0b"); ax.grid(True)
    lines = ax.get_lines()[:1] + ax2.get_lines(); ax.legend(lines, [x.get_label() for x in lines], fontsize=8)

    ax = axes[2, 1]
    ax.scatter(np.asarray(cross["binding"])[mask], np.asarray(view["space_ara"])[mask], c=t, cmap="viridis", s=14)
    ax.set(title=f"Independent S_B vs binding proxy | rho={row.space_binding_rho:.3f}, p={row.space_binding_shift_p:.3f}", xlabel="Established-physics binding proxy eta × GM/(rc²)", ylabel="Model-free S_B (0–2)"); ax.grid(True)

    fig.suptitle(f"T429 {event} — separated time/space strain and source-strength crosswalk", fontsize=18, fontweight="bold")
    fig.savefig(out, dpi=170)
    plt.close(fig)


def plot_holdouts(bundles: dict[str, dict[str, object]], summary: pd.DataFrame, out: pathlib.Path) -> None:
    style()
    holdouts = [name for name, b in bundles.items() if b["event"]["role"] == "primary_holdout"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), constrained_layout=True)
    for ax, event in zip(axes.flat, holdouts):
        view = bundles[event]["view"]
        times = np.asarray(view["times"])
        mask = (times >= EVENT_INTERVAL[0]) & (times <= EVENT_INTERVAL[1])
        row = summary.loc[summary.event == event].iloc[0]
        ax.plot(np.asarray(view["time_ara"])[mask], np.asarray(view["space_ara"])[mask], color="#94a3b8", alpha=.45, lw=.7)
        ax.scatter(np.asarray(view["time_ara"])[mask], np.asarray(view["space_ara"])[mask], c=times[mask], cmap="viridis", s=8)
        ax.axvline(1, color="white", ls=":", lw=.8); ax.axhline(1, color="white", ls=":", lw=.8)
        ax.set(title=f"{event} | time rho {row.time_rho:.2f} | space rho {row.space_rho:.2f}", xlabel="T_A time/movement (0–2)", ylabel="S_B space/connection (0–2)", xlim=(0,2), ylim=(0,2)); ax.grid(True)
    axes.flat[-1].axis("off")
    fig.suptitle("T429 untouched holdouts — separated Space/Time Di-ARA paths", fontsize=18, fontweight="bold")
    fig.savefig(out, dpi=170)
    plt.close(fig)


def gate_summary(summary: pd.DataFrame) -> dict[str, object]:
    hold = summary.loc[summary.role == "primary_holdout"].copy()
    g1 = int(np.sum((hold.time_rho > 0) & (hold.time_shift_p <= .05)))
    g2 = int(np.sum((hold.space_rho > 0) & (hold.space_shift_p <= .05)))
    g3 = int(np.sum((hold.late_time_off_pct >= .90) & (hold.late_space_off_pct >= .90)))
    g4 = int(np.sum((hold.space_binding_rho > 0) & (hold.space_binding_shift_p <= .05)))
    g5 = int(np.sum(hold.agreement_shift_p <= .05))
    passed = all(x >= 4 for x in (g1, g2, g3, g4, g5))
    return {
        "gate_1_time_trend": g1, "gate_2_space_trend": g2,
        "gate_3_late_both": g3, "gate_4_space_binding": g4,
        "gate_5_matched_agreement": g5, "denominator": 5,
        "primary_supported": passed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("development", "holdout", "all"), required=True)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if args.phase == "development":
        events = [e for e in manifest["events"] if e["role"] == "development_only"]
    elif args.phase == "holdout":
        events = [e for e in manifest["events"] if e["role"] == "primary_holdout"]
    else:
        events = manifest["events"]

    bundles, model_rows = process_model_free(events)
    model_frame = pd.DataFrame(model_rows)
    model_path = RESULTS / f"T429_{args.phase.upper()}_MODEL_FREE_HISTORIES.csv"
    model_frame.to_csv(model_path, index=False)

    # This file is deliberately opened only after the model-free histories exist.
    parameter_payload = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    parameter_rows = {row["event"]: row for row in parameter_payload["events"]}
    rng = np.random.default_rng(SEED + {"development": 0, "holdout": 1, "all": 2}[args.phase])
    summary, crosswalk = score_events(bundles, parameter_rows, rng)
    summary.to_csv(RESULTS / f"T429_{args.phase.upper()}_SUMMARY.csv", index=False)
    crosswalk.to_csv(RESULTS / f"T429_{args.phase.upper()}_PHYSICS_CROSSWALK.csv", index=False)

    for event, bundle in bundles.items():
        plot_event(event, bundle, summary, RESULTS / f"T429_{event}_SEPARATED_DIAGNOSTIC.png")
    if args.phase in {"holdout", "all"}:
        plot_holdouts(bundles, summary, RESULTS / f"T429_{args.phase.upper()}_HOLDOUT_DI_ARA.png")
        gates = gate_summary(summary)
        (RESULTS / f"T429_{args.phase.upper()}_GATES.json").write_text(json.dumps(gates, indent=2), encoding="utf-8")
        print(json.dumps(gates, indent=2))
    else:
        print(summary.to_string(index=False))

    run = {
        "phase": args.phase,
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(pathlib.Path(__file__)),
        "source_parameters_sha256": sha256(PARAMETERS),
        "events": list(bundles),
        "model_free_written_before_parameters_loaded": True,
    }
    (RESULTS / f"T429_{args.phase.upper()}_RUN.json").write_text(json.dumps(run, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
