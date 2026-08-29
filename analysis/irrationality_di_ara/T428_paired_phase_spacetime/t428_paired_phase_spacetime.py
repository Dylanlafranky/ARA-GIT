from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal, stats


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
T427_ROOT = ROOT.parent / "T427_spacetime_strain_handover"
sys.path.insert(0, str(T427_ROOT))
import t427_spacetime_strain_handover as t427  # noqa: E402

PROTOCOL = ROOT / "T428_FROZEN_PROTOCOL.md"
MANIFEST = T427_ROOT / "T427_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
SEED = 42820260824
N_NULL = 1_000
EVENT_INTERVAL = (-1.50, 0.25)
OFF_INTERVALS = ((-12.0, -4.0), (4.0, 12.0))
MIN_NULL_SHIFT = 16


@dataclass
class FourFeatures:
    detector: str
    event: str
    role: str
    times: np.ndarray
    raw: dict[str, np.ndarray]
    ara: dict[str, np.ndarray]
    z_native: np.ndarray


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def interval_mask(times: np.ndarray, intervals=OFF_INTERVALS) -> np.ndarray:
    mask = np.zeros(len(times), dtype=bool)
    for lo, hi in intervals:
        mask |= (times >= lo) & (times <= hi)
    return mask


def ecdf_ara(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    ref = np.sort(np.asarray(reference, dtype=float)[np.isfinite(reference)])
    if len(ref) < 10:
        raise ValueError("Insufficient off-source reference values")
    ranks = np.searchsorted(ref, np.asarray(values, dtype=float), side="right")
    q = (ranks + 0.5) / (len(ref) + 1.0)
    return np.clip(2.0 * q, 0.0, 2.0)


def four_raw_features(det: t427.DetectorData) -> dict[str, np.ndarray]:
    nperseg = int(round(t427.STFT_SECONDS * det.fs))
    hop = int(round(t427.HOP_SECONDS * det.fs))
    f, stft_t, z = signal.stft(
        det.band,
        fs=det.fs,
        window="hann",
        nperseg=nperseg,
        noverlap=nperseg - hop,
        nfft=max(512, nperseg),
        detrend=False,
        boundary=None,
        padded=False,
    )
    keep = (f >= t427.FREQ_BAND[0]) & (f <= t427.FREQ_BAND[1])
    f = f[keep]
    z = z[keep]
    power = np.abs(z) ** 2
    total = np.sum(power, axis=0) + t427.EPS
    p = power / total[None, :]

    # Candidate T_B: coherent carriage into the next time slice.  The phase
    # factor removes the deterministic phase advance caused by the STFT hop.
    persistence = np.zeros(z.shape[1], dtype=float)
    phase_step = np.exp(2j * np.pi * f * t427.HOP_SECONDS)
    predicted = z[:, :-1] * phase_step[:, None]
    current = z[:, 1:]
    numerator = np.abs(np.sum(np.conj(predicted) * current, axis=0))
    denominator = np.sqrt(np.sum(np.abs(predicted) ** 2, axis=0) * np.sum(np.abs(current) ** 2, axis=0))
    persistence[1:] = numerator / (denominator + t427.EPS)
    persistence[0] = persistence[1] if len(persistence) > 1 else 0.0

    # Candidate K_B: effective spectral width.  This is not 1-K_A and is not
    # algebraically fixed by entropy.
    centroid = np.sum(p * f[:, None], axis=0)
    width = np.sqrt(np.sum(p * (f[:, None] - centroid[None, :]) ** 2, axis=0))

    if not np.allclose(det.frame_rel, det.gps_start + stft_t - det.gps_event, atol=1e-8):
        raise AssertionError("T428 STFT frame grid drifted from T427")
    return {
        "T_A": np.asarray(det.movement_raw, dtype=float),
        "T_B": persistence,
        "K_A": np.asarray(det.connection_raw, dtype=float),
        "K_B": width,
    }


def build_four(event: dict[str, object], detector: str, path: pathlib.Path) -> tuple[t427.DetectorData, FourFeatures]:
    det = t427.build_detector(event, detector, path)
    raw = four_raw_features(det)
    off = interval_mask(det.frame_rel)
    ara = {name: ecdf_ara(values, values[off]) for name, values in raw.items()}
    return det, FourFeatures(
        detector=detector,
        event=str(event["event"]),
        role=str(event["role"]),
        times=det.frame_rel,
        raw=raw,
        ara=ara,
        z_native=det.z_native,
    )


def align(values: np.ndarray, lag: int) -> np.ndarray:
    return t427.align_to_reference(values, lag)


def best_positive_lag(reference: np.ndarray, other: np.ndarray, max_frames: int = 2) -> tuple[int, float]:
    best = (0, -np.inf)
    for lag in range(-max_frames, max_frames + 1):
        shifted = align(other, lag)
        valid = np.isfinite(reference) & np.isfinite(shifted)
        if np.sum(valid) < 20:
            continue
        corr = float(np.corrcoef(reference[valid], shifted[valid])[0, 1])
        if corr > best[1]:
            best = (lag, corr)
    return best


def event_slice(bundle: FourFeatures) -> dict[str, np.ndarray]:
    mask = (bundle.times >= EVENT_INTERVAL[0]) & (bundle.times <= EVENT_INTERVAL[1])
    out = {name: values[mask] for name, values in bundle.ara.items()}
    out["times"] = bundle.times[mask]
    out["z_native"] = bundle.z_native[mask]
    return out


def network_view(bundles: dict[str, FourFeatures]) -> dict[str, object]:
    h = event_slice(bundles["H1"])
    l = event_slice(bundles["L1"])
    lag, lag_corr = best_positive_lag(h["T_A"], l["T_A"], max_frames=2)
    names = ("T_A", "T_B", "K_A", "K_B", "z_native")
    l_aligned = {name: align(l[name], lag) for name in names}
    consensus = {}
    for name in names:
        consensus[name] = np.nanmean(np.vstack([h[name], l_aligned[name]]), axis=0)
    consensus["times"] = h["times"]
    distance = np.sqrt(sum((h[name] - l_aligned[name]) ** 2 for name in ("T_A", "T_B", "K_A", "K_B")))
    agreement = np.clip(1.0 - distance / 4.0, 0.0, 1.0)
    return {
        "H1": h,
        "L1": l,
        "L1_aligned": l_aligned,
        "lag_frames": lag,
        "lag_seconds": lag * t427.HOP_SECONDS,
        "lag_corr": lag_corr,
        "consensus": consensus,
        "agreement": agreement,
    }


def pair_metrics(data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    t_sum = data["T_A"] + data["T_B"]
    k_sum = data["K_A"] + data["K_B"]
    t_closure = np.abs(t_sum - 2.0)
    k_closure = np.abs(k_sum - 2.0)
    simultaneous_closure = np.sqrt((t_closure**2 + k_closure**2) / 2.0)
    t_gap = np.abs(data["T_A"] - data["T_B"])
    k_gap = np.abs(data["K_A"] - data["K_B"])
    coupled_gap = np.sqrt((t_gap**2 + k_gap**2) / 2.0)
    t_balance = 2.0 * data["T_A"] / (t_sum + t427.EPS)
    k_balance = 2.0 * data["K_A"] / (k_sum + t427.EPS)
    return {
        "t_closure": t_closure,
        "k_closure": k_closure,
        "simultaneous_closure": simultaneous_closure,
        "t_gap": t_gap,
        "k_gap": k_gap,
        "coupled_gap": coupled_gap,
        "t_balance": np.clip(t_balance, 0, 2),
        "k_balance": np.clip(k_balance, 0, 2),
    }


def persistent_any(mask: np.ndarray, n: int = 3) -> bool:
    run = 0
    for value in mask:
        run = run + 1 if bool(value) else 0
        if run >= n:
            return True
    return False


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    valid = np.isfinite(a) & np.isfinite(b)
    if np.sum(valid) < 10:
        return float("nan")
    return float(stats.spearmanr(a[valid], b[valid]).statistic)


def offsource_closure(bundles: dict[str, FourFeatures]) -> np.ndarray:
    duration = EVENT_INTERVAL[1] - EVENT_INTERVAL[0]
    values: list[float] = []
    for detector in ("H1", "L1"):
        b = bundles[detector]
        for lo, hi in OFF_INTERVALS:
            starts = np.arange(lo, hi - duration + 1e-9, duration / 2.0)
            for start in starts:
                mask = (b.times >= start) & (b.times < start + duration)
                if np.sum(mask) < 100:
                    continue
                data = {name: arr[mask] for name, arr in b.ara.items()}
                values.append(float(np.nanmedian(pair_metrics(data)["simultaneous_closure"])))
    return np.asarray(values, dtype=float)


def event_closure(bundles: dict[str, FourFeatures]) -> float:
    values = []
    for detector in ("H1", "L1"):
        data = event_slice(bundles[detector])
        values.append(float(np.nanmedian(pair_metrics(data)["simultaneous_closure"])))
    return float(np.mean(values))


def circular_null(consensus: dict[str, np.ndarray], observed_closure: float, gap_threshold: float, rng: np.random.Generator) -> float:
    n = len(consensus["T_A"])
    possible = np.arange(MIN_NULL_SHIFT, n - MIN_NULL_SHIFT)
    hits = 0
    for _ in range(N_NULL):
        shift = int(rng.choice(possible))
        null = {
            "T_A": consensus["T_A"],
            "K_A": consensus["K_A"],
            "T_B": np.roll(consensus["T_B"], shift),
            "K_B": np.roll(consensus["K_B"], shift),
        }
        metrics = pair_metrics(null)
        closure_good = float(np.nanmedian(metrics["simultaneous_closure"])) <= observed_closure
        handover_good = persistent_any(metrics["coupled_gap"] <= gap_threshold, 3)
        hits += int(closure_good and handover_good)
    return (hits + 1.0) / (N_NULL + 1.0)


def wrong_event_share(views: dict[str, dict[str, object]]) -> tuple[float, pd.DataFrame]:
    rows = []
    events = list(views)
    for event in events:
        matched = float(np.nanmedian(views[event]["agreement"]))
        h = views[event]["H1"]
        for other in events:
            if other == event:
                continue
            l = views[other]["L1"]
            lag, _ = best_positive_lag(h["T_A"], l["T_A"], max_frames=2)
            la = {name: align(l[name], lag) for name in ("T_A", "T_B", "K_A", "K_B")}
            distance = np.sqrt(sum((h[name] - la[name]) ** 2 for name in la))
            agreement = np.clip(1.0 - distance / 4.0, 0.0, 1.0)
            wrong = float(np.nanmedian(agreement))
            rows.append({"event": event, "wrong_event": other, "matched_agreement": matched, "wrong_agreement": wrong, "matched_wins": matched > wrong})
    frame = pd.DataFrame(rows)
    return float(frame["matched_wins"].mean()), frame


def style() -> None:
    plt.style.use("dark_background")
    plt.rcParams.update({
        "figure.facecolor": "#0d1117", "axes.facecolor": "#111827",
        "axes.edgecolor": "#94a3b8", "axes.labelcolor": "#e5e7eb",
        "xtick.color": "#cbd5e1", "ytick.color": "#cbd5e1",
        "grid.color": "#334155", "font.size": 10,
    })


COLORS = {"T_A": "#60a5fa", "T_B": "#f59e0b", "K_A": "#a78bfa", "K_B": "#22c55e"}


def event_figure(event: str, view: dict[str, object], gap_threshold: float, out: pathlib.Path) -> None:
    style()
    c = view["consensus"]
    m = pair_metrics(c)
    times = c["times"]
    handover = m["coupled_gap"] <= gap_threshold
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), constrained_layout=True)

    ax = axes[0, 0]
    for name in ("T_A", "T_B", "K_A", "K_B"):
        ax.plot(times, c[name], lw=1.5, color=COLORS[name], label=name)
    ax.axhline(1, color="white", ls=":", lw=1, label="local child ridge")
    ax.scatter(times[handover], c["T_A"][handover], s=18, facecolors="none", edgecolors="white", label="coupled-gap run")
    ax.set(title="Four independently measured candidate histories", xlabel="Seconds relative to event GPS", ylabel="Local child ARA coordinate (0–2)", ylim=(0, 2))
    ax.grid(True); ax.legend(ncol=3, fontsize=8)

    ax = axes[0, 1]
    ax.plot(c["T_A"], c["T_B"], color="#94a3b8", alpha=.45, lw=.8)
    sc = ax.scatter(c["T_A"], c["T_B"], c=times, cmap="viridis", s=11)
    ax.axvline(1, color="white", ls=":"); ax.axhline(1, color="white", ls=":")
    ax.set(title="Traversal candidate ARA", xlabel="T_A spectral movement", ylabel="T_B coherent persistence", xlim=(0,2), ylim=(0,2)); ax.grid(True)
    fig.colorbar(sc, ax=ax, label="Seconds relative to event GPS")

    ax = axes[0, 2]
    ax.plot(c["K_A"], c["K_B"], color="#94a3b8", alpha=.45, lw=.8)
    sc = ax.scatter(c["K_A"], c["K_B"], c=times, cmap="viridis", s=11)
    ax.axvline(1, color="white", ls=":"); ax.axhline(1, color="white", ls=":")
    ax.set(title="Connection candidate ARA", xlabel="K_A spectral concentration", ylabel="K_B spectral dispersion", xlim=(0,2), ylim=(0,2)); ax.grid(True)
    fig.colorbar(sc, ax=ax, label="Seconds relative to event GPS")

    ax = axes[1, 0]
    ax.plot(times, m["t_closure"], color=COLORS["T_A"], label="|T_A+T_B-2|")
    ax.plot(times, m["k_closure"], color=COLORS["K_A"], label="|K_A+K_B-2|")
    ax.plot(times, m["coupled_gap"], color="#f8fafc", lw=1.4, label="coupled A/B gap")
    ax.axhline(gap_threshold, color="#f59e0b", ls="--", label=f"dev gap threshold {gap_threshold:.3f}")
    ax.set(title="Closure and handover diagnostics", xlabel="Seconds relative to event GPS", ylabel="ARA distance", ylim=(0,2)); ax.grid(True); ax.legend(fontsize=8)

    ax = axes[1, 1]
    ax.plot(m["t_balance"], m["k_balance"], color="#cbd5e1", alpha=.4, lw=.8)
    sc = ax.scatter(m["t_balance"], m["k_balance"], c=times, cmap="viridis", s=12)
    ax.scatter(m["t_balance"][handover], m["k_balance"][handover], facecolors="none", edgecolors="#f59e0b", s=45, label="coupled-gap threshold")
    ax.axvline(1, color="white", ls=":"); ax.axhline(1, color="white", ls=":")
    ax.set(title="Coupled balance Di-ARA", xlabel="Traversal balance: 2T_A/(T_A+T_B)", ylabel="Connection balance: 2K_A/(K_A+K_B)", xlim=(0,2), ylim=(0,2)); ax.grid(True); ax.legend(fontsize=8)
    fig.colorbar(sc, ax=ax, label="Seconds relative to event GPS")

    ax = axes[1, 2]
    ax.plot(times, view["agreement"], color="#60a5fa", label="H1/L1 four-coordinate agreement")
    ax.plot(times, np.clip((c["z_native"] + 3) / 6, 0, 1), color="#f59e0b", alpha=.8, label="native activity (display only)")
    ax.set(title="Independent-detector agreement", xlabel="Seconds relative to event GPS", ylabel="0–1 display scale", ylim=(0,1)); ax.grid(True); ax.legend(fontsize=8)

    fig.suptitle(f"T428 {event} — paired-phase spacetime test", fontsize=18, fontweight="bold")
    fig.savefig(out, dpi=170)
    plt.close(fig)


def summary_figure(summary: pd.DataFrame, views: dict[str, dict[str, object]], gap_threshold: float, out: pathlib.Path) -> None:
    style()
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), constrained_layout=True)
    for ax, (event, view) in zip(axes.flat, views.items()):
        c = view["consensus"]
        m = pair_metrics(c)
        handover = m["coupled_gap"] <= gap_threshold
        ax.plot(m["t_balance"], m["k_balance"], color="#94a3b8", alpha=.35, lw=.7)
        ax.scatter(m["t_balance"], m["k_balance"], c=c["times"], cmap="viridis", s=7)
        ax.scatter(m["t_balance"][handover], m["k_balance"][handover], facecolors="none", edgecolors="#f59e0b", s=28)
        ax.axvline(1, color="white", ls=":", lw=.8); ax.axhline(1, color="white", ls=":", lw=.8)
        row = summary.loc[summary.event == event].iloc[0]
        ax.set(title=f"{event} | closure pct {row.closure_percentile:.2f} | null p {row.null_p:.3f}", xlabel="Traversal balance", ylabel="Connection balance", xlim=(0,2), ylim=(0,2)); ax.grid(True)
    axes.flat[-1].axis("off")
    fig.suptitle("T428 untouched holdouts — coupled paired-phase Di-ARA", fontsize=18, fontweight="bold")
    fig.savefig(out, dpi=170)
    plt.close(fig)


def control_figure(summary: pd.DataFrame, wrong: pd.DataFrame, out: pathlib.Path) -> None:
    style()
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5), constrained_layout=True)
    x = np.arange(len(summary))
    axes[0].bar(x, summary["closure_percentile"], color="#60a5fa")
    axes[0].axhline(.75, color="#f59e0b", ls="--", label="frozen 0.75 gate")
    axes[0].set(xticks=x, xticklabels=summary.event, ylim=(0,1), title="Event closure versus off-source windows", ylabel="Share of off-source windows with worse closure"); axes[0].tick_params(axis="x", rotation=30); axes[0].grid(True); axes[0].legend()
    axes[1].bar(x, summary["median_agreement"], color="#a78bfa")
    axes[1].axhline(float(summary.attrs.get("agreement_threshold", np.nan)), color="#f59e0b", ls="--", label="development threshold")
    axes[1].set(xticks=x, xticklabels=summary.event, ylim=(0,1), title="H1/L1 four-coordinate agreement", ylabel="Median agreement"); axes[1].tick_params(axis="x", rotation=30); axes[1].grid(True); axes[1].legend()
    axes[2].scatter(wrong["wrong_agreement"], wrong["matched_agreement"], color="#22c55e", alpha=.8)
    axes[2].plot([0,1],[0,1], color="white", ls=":")
    axes[2].set(xlim=(0,1), ylim=(0,1), title="Matched event versus wrong-event pairing", xlabel="Wrong-event agreement", ylabel="Matched-event agreement"); axes[2].grid(True)
    fig.suptitle("T428 controls and frozen gates", fontsize=17, fontweight="bold")
    fig.savefig(out, dpi=170)
    plt.close(fig)


def load_all() -> tuple[dict[str, dict[str, FourFeatures]], dict[str, dict[str, t427.DetectorData]], dict[str, object]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cache = pathlib.Path(manifest["raw_cache"])
    bundles: dict[str, dict[str, FourFeatures]] = {}
    detector_data: dict[str, dict[str, t427.DetectorData]] = {}
    for event in manifest["events"]:
        name = str(event["event"])
        bundles[name] = {}
        detector_data[name] = {}
        for detector, url in event["files"].items():
            path = cache / name / pathlib.PurePosixPath(url).name
            det, four = build_four(event, detector, path)
            detector_data[name][detector] = det
            bundles[name][detector] = four
    return bundles, detector_data, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", action="store_true")
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    if not args.score:
        raise SystemExit("Use --score after the frozen protocol is reviewed")

    rng = np.random.default_rng(SEED)
    bundles, detector_data, manifest = load_all()
    views = {event: network_view(detectors) for event, detectors in bundles.items()}

    dev_name = "GW150914"
    dev_view = views[dev_name]
    dev_metrics = pair_metrics(dev_view["consensus"])
    gap_threshold = float(np.nanpercentile(dev_metrics["coupled_gap"], 20))
    agreement_threshold = float(np.nanpercentile(dev_view["agreement"], 25))
    dev_event_closure = event_closure(bundles[dev_name])
    dev_off = offsource_closure(bundles[dev_name])
    dev_closure_percentile = float(np.mean(dev_off > dev_event_closure))
    dev_freeze = {
        "protocol_sha256": sha256(PROTOCOL),
        "development_event": dev_name,
        "coupled_gap_threshold_q20": gap_threshold,
        "agreement_threshold_q25": agreement_threshold,
        "development_event_closure": dev_event_closure,
        "development_closure_percentile": dev_closure_percentile,
        "n_offsource_windows": int(len(dev_off)),
    }
    (ROOT / "T428_DEV_FREEZE.json").write_text(json.dumps(dev_freeze, indent=2), encoding="utf-8")

    holdout_names = [name for name in views if name != dev_name]
    holdout_views = {name: views[name] for name in holdout_names}
    rows = []
    coord_rows = []
    for event in holdout_names:
        view = views[event]
        c = view["consensus"]
        metrics = pair_metrics(c)
        observed_closure = event_closure(bundles[event])
        off = offsource_closure(bundles[event])
        closure_percentile = float(np.mean(off > observed_closure))
        handover_pass = persistent_any(metrics["coupled_gap"] <= gap_threshold, 3)
        median_agreement = float(np.nanmedian(view["agreement"]))
        null_p = circular_null(c, float(np.nanmedian(metrics["simultaneous_closure"])), gap_threshold, rng)
        rows.append({
            "event": event,
            "event_closure": observed_closure,
            "offsource_closure_median": float(np.nanmedian(off)),
            "closure_percentile": closure_percentile,
            "closure_pass": closure_percentile >= .75,
            "coupled_handover_pass": handover_pass,
            "coupled_gap_min": float(np.nanmin(metrics["coupled_gap"])),
            "coupled_gap_median": float(np.nanmedian(metrics["coupled_gap"])),
            "median_agreement": median_agreement,
            "agreement_pass": median_agreement >= agreement_threshold,
            "lag_frames": int(view["lag_frames"]),
            "lag_seconds": float(view["lag_seconds"]),
            "lag_corr": float(view["lag_corr"]),
            "traversal_spearman": spearman(c["T_A"], c["T_B"]),
            "connection_spearman": spearman(c["K_A"], c["K_B"]),
            "null_p": null_p,
            "null_pass": null_p <= .05,
        })
        for i, time in enumerate(c["times"]):
            coord_rows.append({
                "event": event, "time_s": float(time),
                **{name: float(c[name][i]) for name in ("T_A", "T_B", "K_A", "K_B")},
                **{name: float(metrics[name][i]) for name in ("simultaneous_closure", "coupled_gap", "t_balance", "k_balance")},
                "agreement": float(view["agreement"][i]),
            })

    summary = pd.DataFrame(rows)
    wrong_share, wrong = wrong_event_share(holdout_views)
    summary.attrs["agreement_threshold"] = agreement_threshold
    gates = {
        "closure_pass_count": int(summary.closure_pass.sum()),
        "handover_pass_count": int(summary.coupled_handover_pass.sum()),
        "agreement_pass_count": int(summary.agreement_pass.sum()),
        "wrong_event_win_share": wrong_share,
        "null_pass_count": int(summary.null_pass.sum()),
    }
    gates["primary_supported"] = bool(
        gates["closure_pass_count"] >= 4
        and gates["handover_pass_count"] >= 4
        and gates["agreement_pass_count"] >= 4
        and gates["wrong_event_win_share"] >= .75
        and gates["null_pass_count"] == len(summary)
    )

    summary.to_csv(RESULTS / "T428_HOLDOUT_SUMMARY.csv", index=False)
    wrong.to_csv(RESULTS / "T428_WRONG_EVENT_CONTROL.csv", index=False)
    pd.DataFrame(coord_rows).to_csv(RESULTS / "T428_CONSENSUS_COORDINATES.csv", index=False)
    results = {"dev_freeze": dev_freeze, "gates": gates, "holdouts": rows}
    (RESULTS / "T428_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    for event, view in holdout_views.items():
        event_figure(event, view, gap_threshold, RESULTS / f"T428_{event}_PAIRED_PHASE.png")
    summary_figure(summary, holdout_views, gap_threshold, RESULTS / "T428_HOLDOUT_DI_ARA_GALLERY.png")
    control_figure(summary, wrong, RESULTS / "T428_CONTROLS.png")

    code_hash = sha256(pathlib.Path(__file__))
    (ROOT / "T428_ANALYSIS_CODE.sha256").write_text(f"{code_hash}  {pathlib.Path(__file__).name}\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
