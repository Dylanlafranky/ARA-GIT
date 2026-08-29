from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import pathlib
from dataclasses import dataclass

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from scipy import signal


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MANIFEST = ROOT / "T427_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
SOURCE_AUDIT = RESULTS / "T427_SOURCE_AUDIT.json"
EPS = 1e-12
FS_EXPECTED = 4096.0
EVENT_INTERVAL = (-1.50, 0.25)
OFF_INTERVALS = ((-12.0, -4.0), (4.0, 12.0))
STFT_SECONDS = 0.064
HOP_SECONDS = 0.004
FREQ_BAND = (30.0, 512.0)
PERSIST = 3
SEED = 42720260824
N_TIME_SLIDE = 10_000
N_PHASE_SCRAMBLE = 1_000
N_LOCK_CONTROL = 1_000


@dataclass
class DetectorData:
    event: str
    detector: str
    role: str
    gps_event: float
    source_path: pathlib.Path
    fs: float
    gps_start: float
    strain: np.ndarray
    whitened: np.ndarray
    band: np.ndarray
    sample_rel: np.ndarray
    frame_rel: np.ndarray
    freqs: np.ndarray
    power: np.ndarray
    c1: np.ndarray
    c2: np.ndarray
    z_native: np.ndarray
    native_raw: np.ndarray
    movement_raw: np.ndarray
    connection_raw: np.ndarray
    stats: dict[str, tuple[float, float]]
    qa: dict[str, object]


def file_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def robust_location_scale(values: np.ndarray) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return 0.0, 1.0
    loc = float(np.median(values))
    scale = float(1.4826 * np.median(np.abs(values - loc)))
    if not np.isfinite(scale) or scale < 1e-10:
        q25, q75 = np.percentile(values, [25, 75])
        scale = float((q75 - q25) / 1.349)
    if not np.isfinite(scale) or scale < 1e-10:
        scale = float(np.std(values))
    if not np.isfinite(scale) or scale < 1e-10:
        scale = 1.0
    return loc, scale


def ara_map(z: np.ndarray) -> np.ndarray:
    a = np.clip((np.asarray(z) - 3.0) / 1.5, -50.0, 50.0)
    return 2.0 / (1.0 + np.exp(-a))


def decode_strings(values: np.ndarray) -> list[str]:
    out: list[str] = []
    for value in values:
        if isinstance(value, bytes):
            out.append(value.decode("utf-8", errors="replace"))
        else:
            out.append(str(value))
    return out


def hdf_scalar(handle: h5py.File, key: str) -> object:
    value = handle[key][()]
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.generic):
        return value.item()
    return value


def read_hdf(path: pathlib.Path, event: dict[str, object], detector: str) -> tuple[np.ndarray, float, float, dict[str, object]]:
    with h5py.File(path, "r") as handle:
        strain = np.asarray(handle["strain/Strain"], dtype=float)
        spacing = float(handle["strain/Strain"].attrs["Xspacing"])
        gps_start = float(handle["strain/Strain"].attrs["Xstart"])
        fs = 1.0 / spacing
        duration = float(hdf_scalar(handle, "meta/Duration"))
        detector_meta = str(hdf_scalar(handle, "meta/Detector"))

        dq_names = decode_strings(np.asarray(handle["quality/simple/DQShortnames"]))
        dq_mask = np.asarray(handle["quality/simple/DQmask"], dtype=np.int64)
        inj_names = decode_strings(np.asarray(handle["quality/injections/InjShortnames"]))
        inj_mask = np.asarray(handle["quality/injections/Injmask"], dtype=np.int64)

    gps_event = float(event["gps"])
    sec_start = max(0, int(math.floor(gps_event + EVENT_INTERVAL[0] - gps_start)))
    sec_stop = min(len(dq_mask), int(math.ceil(gps_event + EVENT_INTERVAL[1] - gps_start)) + 1)
    dq_slice = dq_mask[sec_start:sec_stop]
    inj_slice = inj_mask[sec_start:sec_stop]

    required_bits: dict[str, bool] = {}
    for idx, name in enumerate(dq_names):
        upper = name.upper()
        if upper in {"DATA", "CBC_CAT1", "BURST_CAT1"}:
            required_bits[name] = bool(len(dq_slice) and np.all((dq_slice & (1 << idx)) != 0))
    public_dq_pass = bool(len(dq_slice)) and all(required_bits.values()) if required_bits else bool(len(dq_slice)) and np.all(dq_slice > 0)

    qa = {
        "event": event["event"],
        "role": event["role"],
        "detector": detector,
        "path": path.as_posix(),
        "sha256": file_sha256(path),
        "bytes": path.stat().st_size,
        "fs_hz": fs,
        "duration_s": duration,
        "n_samples": len(strain),
        "finite_fraction": float(np.mean(np.isfinite(strain))),
        "zero_fraction": float(np.mean(strain == 0)),
        "detector_metadata": detector_meta,
        "dq_shortnames": "|".join(dq_names),
        "dq_event_values": "|".join(map(str, np.unique(dq_slice).tolist())),
        "required_dq_bits": json.dumps(required_bits, sort_keys=True),
        "public_dq_pass": public_dq_pass,
        "injection_shortnames": "|".join(inj_names),
        "injection_event_values": "|".join(map(str, np.unique(inj_slice).tolist())),
    }
    return strain, fs, gps_start, qa


def interval_mask(times: np.ndarray, intervals: tuple[tuple[float, float], ...]) -> np.ndarray:
    mask = np.zeros(len(times), dtype=bool)
    for lo, hi in intervals:
        mask |= (times >= lo) & (times <= hi)
    return mask


def whiten_and_bandpass(strain: np.ndarray, fs: float, sample_rel: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    off_mask = interval_mask(sample_rel, OFF_INTERVALS)
    off = strain[off_mask]
    nperseg = min(len(off), int(round(4 * fs)))
    noverlap = nperseg // 2
    f_psd, psd = signal.welch(
        off,
        fs=fs,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        detrend="constant",
        average="median",
    )
    fft_freqs = np.fft.rfftfreq(len(strain), 1.0 / fs)
    psd_interp = np.interp(fft_freqs, f_psd, psd, left=psd[0], right=psd[-1])
    floor = max(float(np.nanmedian(psd_interp)) * 1e-12, np.finfo(float).tiny)
    white = np.fft.irfft(np.fft.rfft(strain) / np.sqrt(np.maximum(psd_interp, floor)), n=len(strain))
    white_scale = float(np.std(white[off_mask]))
    if white_scale > 0:
        white = white / white_scale
    sos = signal.butter(4, FREQ_BAND, btype="bandpass", fs=fs, output="sos")
    band = signal.sosfiltfilt(sos, white)
    return white, band


def spectral_features(data: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nperseg = int(round(STFT_SECONDS * fs))
    hop = int(round(HOP_SECONDS * fs))
    noverlap = nperseg - hop
    f, t, z = signal.stft(
        data,
        fs=fs,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=max(512, nperseg),
        detrend=False,
        boundary=None,
        padded=False,
    )
    keep = (f >= FREQ_BAND[0]) & (f <= FREQ_BAND[1])
    f = f[keep]
    power = np.abs(z[keep]) ** 2
    native = np.log(np.sum(power, axis=0) + EPS)
    p = power / (np.sum(power, axis=0, keepdims=True) + EPS)
    entropy = -np.sum(p * np.log(p + EPS), axis=0) / np.log(len(f))
    concentration = 1.0 - entropy
    sqrt_p = np.sqrt(p)
    hellinger = np.zeros(power.shape[1])
    hellinger[1:] = np.sqrt(np.sum((sqrt_p[:, 1:] - sqrt_p[:, :-1]) ** 2, axis=0)) / np.sqrt(2.0)
    ridge = f[np.argmax(power, axis=0)]
    ridge_move = np.zeros_like(ridge)
    ridge_move[1:] = np.abs(np.log2((ridge[1:] + EPS) / (ridge[:-1] + EPS)))
    movement = hellinger + ridge_move
    movement_raw = native + np.log(movement + 1e-6)
    return t, f, power, native, movement_raw, concentration


def build_detector(event: dict[str, object], detector: str, source_path: pathlib.Path) -> DetectorData:
    strain, fs, gps_start, qa = read_hdf(source_path, event, detector)
    sample_rel = gps_start + np.arange(len(strain)) / fs - float(event["gps"])
    white, band = whiten_and_bandpass(strain, fs, sample_rel)
    frame_t, freqs, power, native, movement_raw, connection_raw = spectral_features(band, fs)
    frame_rel = gps_start + frame_t - float(event["gps"])
    off = interval_mask(frame_rel, OFF_INTERVALS)
    n_loc, n_scale = robust_location_scale(native[off])
    m_loc, m_scale = robust_location_scale(movement_raw[off])
    k_loc, k_scale = robust_location_scale(connection_raw[off])
    z_native = (native - n_loc) / n_scale
    z_m = (movement_raw - m_loc) / m_scale
    z_k = (connection_raw - k_loc) / k_scale
    c1 = ara_map(z_m)
    c2 = ara_map(z_k)
    event_mask = (frame_rel >= EVENT_INTERVAL[0]) & (frame_rel <= EVENT_INTERVAL[1])
    qa.update(
        {
            "event_frames": int(np.sum(event_mask)),
            "offsource_frames": int(np.sum(off)),
            "c1_low_saturation": int(np.sum(event_mask & (c1 < 0.02))),
            "c1_high_saturation": int(np.sum(event_mask & (c1 > 1.98))),
            "c2_low_saturation": int(np.sum(event_mask & (c2 < 0.02))),
            "c2_high_saturation": int(np.sum(event_mask & (c2 > 1.98))),
            "max_native_z": float(np.nanmax(z_native[event_mask])),
        }
    )
    return DetectorData(
        event=str(event["event"]), detector=detector, role=str(event["role"]),
        gps_event=float(event["gps"]), source_path=source_path, fs=fs,
        gps_start=gps_start, strain=strain, whitened=white, band=band,
        sample_rel=sample_rel, frame_rel=frame_rel, freqs=freqs, power=power,
        c1=c1, c2=c2, z_native=z_native, native_raw=native,
        movement_raw=movement_raw, connection_raw=connection_raw,
        stats={"native": (n_loc, n_scale), "movement": (m_loc, m_scale), "connection": (k_loc, k_scale)},
        qa=qa,
    )


def align_to_reference(values: np.ndarray, lag_frames: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=float)
    if lag_frames >= 0:
        if lag_frames == 0:
            out[:] = values
        else:
            out[:-lag_frames] = values[lag_frames:]
    else:
        out[-lag_frames:] = values[:lag_frames]
    return out


def best_lag(reference: np.ndarray, other: np.ndarray, max_frames: int, mask: np.ndarray) -> tuple[int, float]:
    best = (0, -np.inf)
    for lag in range(-max_frames, max_frames + 1):
        shifted = align_to_reference(other, lag)
        valid = mask & np.isfinite(reference) & np.isfinite(shifted)
        if np.sum(valid) < 8:
            continue
        a = reference[valid]
        b = shifted[valid]
        if np.std(a) < EPS or np.std(b) < EPS:
            corr = -np.inf
        else:
            corr = abs(float(np.corrcoef(a, b)[0, 1]))
        if corr > best[1]:
            best = (lag, corr)
    return best


def persistent_starts(mask: np.ndarray, n: int = PERSIST) -> list[int]:
    starts: list[int] = []
    run = 0
    for idx, value in enumerate(mask):
        run = run + 1 if bool(value) else 0
        if run == n:
            starts.append(idx - n + 1)
    return starts


def first_persistent(mask: np.ndarray, start: int = 0, stop: int | None = None) -> int | None:
    if stop is None:
        stop = len(mask)
    sub = np.zeros_like(mask, dtype=bool)
    sub[max(0, start):min(len(mask), stop)] = mask[max(0, start):min(len(mask), stop)]
    starts = persistent_starts(sub)
    return starts[0] if starts else None


def find_onset(z_native: np.ndarray) -> int | None:
    return first_persistent(np.isfinite(z_native) & (z_native >= 3.0))


def score_sequence(times: np.ndarray, c1: np.ndarray, c2: np.ndarray, z_native: np.ndarray) -> dict[str, object]:
    valid = np.isfinite(c1) & np.isfinite(c2) & np.isfinite(z_native)
    ch = valid & (c1 < 1.0) & (c2 > 1.0)
    mh = valid & (c1 > 1.0) & (c2 < 1.0)
    opening = valid & (np.abs(c1 - 0.5) <= 0.25) & (np.abs(c2 - 1.5) <= 0.25)
    onset = find_onset(z_native)
    pre_ch = None
    move = None
    reclose = None
    if onset is not None:
        pre_starts = [s for s in persistent_starts(ch) if s + PERSIST - 1 < onset]
        pre_ch = pre_starts[-1] if pre_starts else None
        move = first_persistent(mh, start=onset + 1)
        if move is not None:
            reclose = first_persistent(ch, start=move + PERSIST)
    opening_pass = bool(onset is not None and opening[onset])
    complete = bool(pre_ch is not None and opening_pass and move is not None and reclose is not None)
    def value(idx: int | None, arr: np.ndarray) -> float:
        return float(arr[idx]) if idx is not None else float("nan")
    return {
        "complete": complete,
        "pre_connection_idx": pre_ch,
        "onset_idx": onset,
        "movement_idx": move,
        "reclosure_idx": reclose,
        "opening_pass": opening_pass,
        "onset_time": value(onset, times),
        "onset_c1": value(onset, c1),
        "onset_c2": value(onset, c2),
        "onset_parent_mean": value(onset, (c1 + c2) / 2.0),
        "movement_time": value(move, times),
        "reclosure_time": value(reclose, times),
        "pre_connection_time": value(pre_ch, times),
    }


def event_view(detectors: dict[str, DetectorData]) -> dict[str, object]:
    h = detectors["H1"]
    event_mask = (h.frame_rel >= EVENT_INTERVAL[0]) & (h.frame_rel <= EVENT_INTERVAL[1])
    idx = np.where(event_mask)[0]
    times = h.frame_rel[idx]
    ref_z = h.z_native[idx]
    lag_mask = (times >= -0.50) & (times <= 0.10)
    aligned: dict[str, dict[str, np.ndarray | int | float]] = {}
    for name, det in detectors.items():
        raw = {"c1": det.c1[idx], "c2": det.c2[idx], "z": det.z_native[idx]}
        if name == "H1":
            lag, corr = 0, 1.0
        else:
            max_seconds = 0.010 if name == "L1" else 0.030
            max_frames = int(round(max_seconds / HOP_SECONDS))
            lag, corr = best_lag(ref_z, raw["z"], max_frames, lag_mask)
        aligned[name] = {
            "lag": lag,
            "lag_seconds": lag * HOP_SECONDS,
            "activity_corr": corr,
            "c1": align_to_reference(raw["c1"], lag),
            "c2": align_to_reference(raw["c2"], lag),
            "z": align_to_reference(raw["z"], lag),
        }
    c1 = np.nanmean(np.vstack([aligned["H1"]["c1"], aligned["L1"]["c1"]]), axis=0)
    c2 = np.nanmean(np.vstack([aligned["H1"]["c2"], aligned["L1"]["c2"]]), axis=0)
    z = np.nanmean(np.vstack([aligned["H1"]["z"], aligned["L1"]["z"]]), axis=0)
    distance = np.sqrt(
        (aligned["H1"]["c1"] - aligned["L1"]["c1"]) ** 2
        + (aligned["H1"]["c2"] - aligned["L1"]["c2"]) ** 2
    )
    agreement = 1.0 - distance / (2.0 * np.sqrt(2.0))
    score = score_sequence(times, c1, c2, z)
    stage_indices = [score[k] for k in ("pre_connection_idx", "onset_idx", "movement_idx", "reclosure_idx")]
    stage_indices = [int(k) for k in stage_indices if k is not None]
    score["median_stage_agreement"] = float(np.nanmedian(agreement[stage_indices])) if stage_indices else float("nan")
    score["lag_l1_ms"] = float(aligned["L1"]["lag_seconds"]) * 1000.0
    score["lag_l1_activity_corr"] = float(aligned["L1"]["activity_corr"])
    return {"times": times, "c1": c1, "c2": c2, "z": z, "agreement": agreement, "score": score, "aligned": aligned, "idx": idx}


def ar2_prediction_error(samples: np.ndarray, fs: float) -> float:
    n_train = int(round(0.064 * fs))
    n_test = int(round(0.032 * fs))
    x = np.asarray(samples[:n_train + n_test], dtype=float)
    if len(x) < n_train + n_test or np.std(x[n_train:]) < EPS:
        return float("nan")
    train = x[:n_train]
    y = train[2:]
    design = np.column_stack([np.ones(len(y)), train[1:-1], train[:-2]])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    preds = []
    for i in range(n_train, n_train + n_test):
        preds.append(beta[0] + beta[1] * x[i - 1] + beta[2] * x[i - 2])
    target = x[n_train:n_train + n_test]
    return float(np.mean((target - np.asarray(preds)) ** 2) / (np.var(target) + EPS))


def sample_window(det: DetectorData, start_rel: float, duration: float = 0.096) -> np.ndarray:
    mask = (det.sample_rel >= start_rel) & (det.sample_rel < start_rel + duration)
    return det.band[mask]


def phase_scramble(samples: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    spectrum = np.fft.rfft(samples)
    phase = rng.uniform(0, 2 * np.pi, len(spectrum))
    phase[0] = 0.0
    if len(samples) % 2 == 0:
        phase[-1] = 0.0
    return np.fft.irfft(np.abs(spectrum) * np.exp(1j * phase), n=len(samples))


def information_lock(detectors: dict[str, DetectorData], view: dict[str, object], rng: np.random.Generator) -> dict[str, object]:
    score = view["score"]
    onset = score["onset_idx"]
    reclose = score["reclosure_idx"]
    if onset is None or reclose is None:
        return {"eligible": False, "pass": False, "reason": "missing onset or reclosure"}
    times = view["times"]
    post_start = float(times[reclose])
    opening_time = float(times[onset])
    post_errors = []
    pre_errors = []
    selected_pre: dict[str, float] = {}
    phase_controls = np.full((N_LOCK_CONTROL, 2), np.nan)
    for d_idx, name in enumerate(("H1", "L1")):
        det = detectors[name]
        lag_s = float(view["aligned"][name]["lag_seconds"])
        d_post = post_start + lag_s
        post = sample_window(det, d_post)
        post_error = ar2_prediction_error(post, det.fs)
        post_errors.append(post_error)

        candidate_starts = np.arange(EVENT_INTERVAL[0], opening_time - 0.096, HOP_SECONDS)
        if len(candidate_starts) == 0:
            return {"eligible": False, "pass": False, "reason": "no pre-opening comparison window"}
        frame_z = view["aligned"][name]["z"]
        post_frame = int(np.argmin(np.abs(times - post_start)))
        post_native = float(frame_z[post_frame])
        candidate_scores = []
        for start in candidate_starts:
            mask = (times >= start) & (times < start + 0.096)
            candidate_scores.append(abs(float(np.nanmedian(frame_z[mask])) - post_native) if np.any(mask) else np.inf)
        pre_start = float(candidate_starts[int(np.argmin(candidate_scores))]) + lag_s
        selected_pre[name] = pre_start
        pre = sample_window(det, pre_start)
        pre_errors.append(ar2_prediction_error(pre, det.fs))
        for rep in range(N_LOCK_CONTROL):
            phase_controls[rep, d_idx] = ar2_prediction_error(phase_scramble(post, rng), det.fs)
    post_median = float(np.nanmedian(post_errors))
    pre_median = float(np.nanmedian(pre_errors))
    control_median = np.nanmedian(phase_controls, axis=1)
    q05 = float(np.nanpercentile(control_median, 5))
    passed = bool(np.isfinite(post_median) and post_median < pre_median and post_median < q05)
    return {
        "eligible": True,
        "pass": passed,
        "post_start": post_start,
        "pre_start_h1": selected_pre.get("H1", float("nan")),
        "pre_start_l1": selected_pre.get("L1", float("nan")),
        "post_error_h1": post_errors[0],
        "post_error_l1": post_errors[1],
        "post_error_median": post_median,
        "pre_error_h1": pre_errors[0],
        "pre_error_l1": pre_errors[1],
        "pre_error_median": pre_median,
        "phase_control_q05": q05,
        "phase_control_median": float(np.nanmedian(control_median)),
    }


def detector_source_paths(event: dict[str, object]) -> dict[str, pathlib.Path]:
    audit = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    return {
        row["detector"]: pathlib.Path(row["local_path"])
        for row in audit if row["event"] == event["event"]
    }


def analyse_event(event: dict[str, object], rng: np.random.Generator) -> tuple[dict[str, DetectorData], dict[str, object], dict[str, object]]:
    paths = detector_source_paths(event)
    detectors = {name: build_detector(event, name, path) for name, path in paths.items()}
    view = event_view(detectors)
    lock = information_lock(detectors, view, rng)
    return detectors, view, lock


def circular_shift_with_local_lag(values: np.ndarray, frames: int, ref: np.ndarray, max_lag: int, mask: np.ndarray) -> np.ndarray:
    rolled = np.roll(values, frames)
    lag, _ = best_lag(ref, rolled, max_lag, mask)
    return align_to_reference(rolled, lag)


def time_slide_null(views: dict[str, dict[str, object]], rng: np.random.Generator) -> np.ndarray:
    counts = np.zeros(N_TIME_SLIDE, dtype=int)
    for rep in range(N_TIME_SLIDE):
        count = 0
        for view in views.values():
            times = view["times"]
            a = view["aligned"]
            ref_z = np.asarray(a["H1"]["z"])
            frames = int(round(rng.uniform(0.20, 0.80) / HOP_SECONDS))
            if rng.random() < 0.5:
                frames *= -1
            mask = (times >= -0.50) & (times <= 0.10)
            rolled_z = np.roll(np.asarray(a["L1"]["z"]), frames)
            local_lag, _ = best_lag(ref_z, rolled_z, int(round(0.010 / HOP_SECONDS)), mask)
            l1_c1 = align_to_reference(np.roll(np.asarray(a["L1"]["c1"]), frames), local_lag)
            l1_c2 = align_to_reference(np.roll(np.asarray(a["L1"]["c2"]), frames), local_lag)
            l1_z = align_to_reference(rolled_z, local_lag)
            c1 = np.nanmean(np.vstack([a["H1"]["c1"], l1_c1]), axis=0)
            c2 = np.nanmean(np.vstack([a["H1"]["c2"], l1_c2]), axis=0)
            z = np.nanmean(np.vstack([a["H1"]["z"], l1_z]), axis=0)
            count += int(score_sequence(times, c1, c2, z)["complete"])
        counts[rep] = count
    return counts


def phase_scrambled_track(det: DetectorData, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sample_mask = (det.sample_rel >= EVENT_INTERVAL[0] - STFT_SECONDS) & (det.sample_rel <= EVENT_INTERVAL[1] + STFT_SECONDS)
    segment = phase_scramble(det.band[sample_mask], rng)
    t, _, _, native, movement, connection = spectral_features(segment, det.fs)
    segment_start = float(det.sample_rel[np.where(sample_mask)[0][0]])
    rel = segment_start + t
    keep = (rel >= EVENT_INTERVAL[0]) & (rel <= EVENT_INTERVAL[1])
    n_loc, n_scale = det.stats["native"]
    m_loc, m_scale = det.stats["movement"]
    k_loc, k_scale = det.stats["connection"]
    return ara_map((movement[keep] - m_loc) / m_scale), ara_map((connection[keep] - k_loc) / k_scale), (native[keep] - n_loc) / n_scale


def phase_scramble_null(events: dict[str, tuple[dict[str, DetectorData], dict[str, object]]], rng: np.random.Generator) -> np.ndarray:
    counts = np.zeros(N_PHASE_SCRAMBLE, dtype=int)
    for rep in range(N_PHASE_SCRAMBLE):
        count = 0
        for detectors, view in events.values():
            tracks = {name: phase_scrambled_track(detectors[name], rng) for name in ("H1", "L1")}
            min_len = min(len(tracks["H1"][0]), len(tracks["L1"][0]), len(view["times"]))
            times = np.asarray(view["times"])[:min_len]
            h1 = tuple(x[:min_len] for x in tracks["H1"])
            l1 = tuple(x[:min_len] for x in tracks["L1"])
            mask = (times >= -0.50) & (times <= 0.10)
            lag, _ = best_lag(h1[2], l1[2], int(round(0.010 / HOP_SECONDS)), mask)
            l1a = tuple(align_to_reference(x, lag) for x in l1)
            c1 = np.nanmean(np.vstack([h1[0], l1a[0]]), axis=0)
            c2 = np.nanmean(np.vstack([h1[1], l1a[1]]), axis=0)
            z = np.nanmean(np.vstack([h1[2], l1a[2]]), axis=0)
            count += int(score_sequence(times, c1, c2, z)["complete"])
        counts[rep] = count
    return counts


def reverse_and_wrong_controls(holdouts: dict[str, tuple[dict[str, DetectorData], dict[str, object]]]) -> tuple[int, list[dict[str, object]]]:
    reverse_count = 0
    wrong_rows: list[dict[str, object]] = []
    names = list(holdouts)
    for name in names:
        view = holdouts[name][1]
        reverse_count += int(score_sequence(np.asarray(view["times"]), np.asarray(view["c1"])[::-1], np.asarray(view["c2"])[::-1], np.asarray(view["z"])[::-1])["complete"])
    for idx, name in enumerate(names):
        other = names[(idx + 1) % len(names)]
        v1 = holdouts[name][1]
        v2 = holdouts[other][1]
        n = min(len(v1["times"]), len(v2["times"]))
        times = np.asarray(v1["times"])[:n]
        h = v1["aligned"]["H1"]
        l = v2["aligned"]["L1"]
        c1 = np.nanmean(np.vstack([np.asarray(h["c1"])[:n], np.asarray(l["c1"])[:n]]), axis=0)
        c2 = np.nanmean(np.vstack([np.asarray(h["c2"])[:n], np.asarray(l["c2"])[:n]]), axis=0)
        z = np.nanmean(np.vstack([np.asarray(h["z"])[:n], np.asarray(l["z"])[:n]]), axis=0)
        distance = np.sqrt((np.asarray(h["c1"])[:n] - np.asarray(l["c1"])[:n]) ** 2 + (np.asarray(h["c2"])[:n] - np.asarray(l["c2"])[:n]) ** 2)
        score = score_sequence(times, c1, c2, z)
        wrong_rows.append({"h1_event": name, "l1_event": other, "complete": score["complete"], "median_agreement": float(np.nanmedian(1 - distance / (2 * np.sqrt(2))))})
    return reverse_count, wrong_rows


def third_detector_test(detectors: dict[str, DetectorData], view: dict[str, object]) -> dict[str, object]:
    if "V1" not in detectors:
        return {"eligible": False, "reason": "no V1 file"}
    v = view["aligned"]["V1"]
    eligible = bool(np.any(np.convolve(np.asarray(v["z"]) >= 3.0, np.ones(PERSIST, dtype=int), mode="valid") >= PERSIST))
    if not eligible:
        return {"eligible": False, "reason": "V1 native activity never persisted above z=3", "max_v1_z": float(np.nanmax(v["z"]))}
    v_score = score_sequence(np.asarray(view["times"]), np.asarray(v["c1"]), np.asarray(v["c2"]), np.asarray(v["z"]))
    h_score = view["score"]
    matches = []
    for key in ("onset_idx", "movement_idx", "reclosure_idx"):
        a, b = h_score[key], v_score[key]
        matches.append(bool(a is not None and b is not None and abs(int(a) - int(b)) <= 2))
    return {
        "eligible": True,
        "v1_complete": v_score["complete"],
        "timing_matches": int(sum(matches)),
        "all_three_stage_times_match": bool(all(matches)),
        "max_v1_z": float(np.nanmax(v["z"])),
        "lag_v1_ms": float(v["lag_seconds"]) * 1000,
    }


def style() -> None:
    plt.rcParams.update({
        "figure.facecolor": "#0d1117", "axes.facecolor": "#111827",
        "axes.edgecolor": "#94a3b8", "axes.labelcolor": "#e5e7eb",
        "xtick.color": "#cbd5e1", "ytick.color": "#cbd5e1",
        "text.color": "#e5e7eb", "grid.color": "#334155", "grid.alpha": 0.45,
        "font.size": 10, "savefig.facecolor": "#0d1117",
    })


def add_stage_lines(ax: plt.Axes, score: dict[str, object]) -> None:
    colors = {"onset_time": "#f59e0b", "movement_time": "#ef4444", "reclosure_time": "#22c55e"}
    labels = {"onset_time": "native onset", "movement_time": "movement", "reclosure_time": "reclosure"}
    for key, color in colors.items():
        value = float(score.get(key, np.nan))
        if np.isfinite(value):
            ax.axvline(value, color=color, lw=1.4, ls="--", label=labels[key])


def event_figure(event: str, detectors: dict[str, DetectorData], view: dict[str, object], out: pathlib.Path) -> None:
    style()
    score = view["score"]
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    ax = axes[0, 0]
    offsets = {"H1": 0.0, "L1": 5.0, "V1": 10.0}
    for name, det in detectors.items():
        mask = (det.sample_rel >= EVENT_INTERVAL[0]) & (det.sample_rel <= EVENT_INTERVAL[1])
        y = det.band[mask]
        y = y / (np.std(y) + EPS) + offsets[name]
        ax.plot(det.sample_rel[mask], y, lw=0.65, label=f"{name} whitened 30–512 Hz (+{offsets[name]:.0f})")
    add_stage_lines(ax, score)
    ax.set(title="Independent detector strain histories", xlabel="Seconds relative to published event GPS (used only for crop)", ylabel="Whitened strain (standardized + display offset)")
    ax.grid(True); ax.legend(fontsize=8, ncol=2)

    ax = axes[0, 1]
    h = detectors["H1"]
    idx = view["idx"]
    p = 10 * np.log10(h.power[:, idx] / (np.nanmedian(h.power[:, idx]) + EPS) + EPS)
    mesh = ax.pcolormesh(view["times"], h.freqs, p, shading="auto", cmap="magma", vmin=np.percentile(p, 10), vmax=np.percentile(p, 99))
    add_stage_lines(ax, score)
    ax.set(title="H1 model-free time–frequency cut", xlabel="Seconds relative to event GPS", ylabel="Frequency (Hz)")
    fig.colorbar(mesh, ax=ax, label="Power relative to event median (dB)")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.plot(view["times"], view["c1"], color="#60a5fa", lw=2, label="C1 movement/traversal ARA")
    ax.plot(view["times"], view["c2"], color="#f59e0b", lw=2, label="C2 connection/concentration ARA")
    ax.plot(view["times"], np.clip(ara_map(view["z"]), 0, 2), color="#94a3b8", alpha=.55, lw=1, label="native activity shown on 0–2 display map")
    ax.axhline(1, color="white", lw=1, ls=":", label="ARA ridge 1.0")
    add_stage_lines(ax, score)
    ax.set_ylim(0, 2.03); ax.set(title="Consensus H1/L1 ARA histories", xlabel="Seconds relative to event GPS", ylabel="Independent ARA coordinate (0–2)")
    ax.grid(True); ax.legend(fontsize=8, ncol=2)

    ax = axes[1, 1]
    time_norm = Normalize(float(view["times"][0]), float(view["times"][-1]))
    ax.scatter(view["c1"], view["c2"], c=view["times"], cmap="viridis", norm=time_norm, s=10, alpha=.65)
    ax.plot(view["c1"], view["c2"], color="#cbd5e1", alpha=.28, lw=.7)
    ax.axvline(1, color="white", ls="--", lw=1); ax.axhline(1, color="white", ls="--", lw=1)
    ax.add_patch(plt.Rectangle((0.25, 1.25), .5, .5, fill=False, ec="#f59e0b", lw=2, ls="--"))
    stage_meta = [("onset_idx", "opening", "#f59e0b"), ("movement_idx", "movement", "#ef4444"), ("reclosure_idx", "reclosure", "#22c55e")]
    for key, label, color in stage_meta:
        idx_stage = score.get(key)
        if idx_stage is not None:
            ax.scatter([view["c1"][idx_stage]], [view["c2"][idx_stage]], s=90, color=color, edgecolor="white", zorder=5, label=label)
    ax.set(xlim=(0, 2), ylim=(0, 2), title="Time-facing Irrationality Di-ARA path", xlabel="C1 movement/traversal ARA (0–2)", ylabel="C2 connection/concentration ARA (0–2)")
    ax.grid(True); ax.legend(fontsize=8)
    fig.colorbar(plt.cm.ScalarMappable(norm=time_norm, cmap="viridis"), ax=ax, label="Seconds relative to event GPS")
    status = "PASS" if score["complete"] else "FAIL"
    fig.suptitle(f"T427 {event} — frozen spacetime handover: {status}", fontsize=17, fontweight="bold")
    fig.savefig(out, dpi=170)
    plt.close(fig)


def summary_figures(holdouts: dict[str, tuple[dict[str, DetectorData], dict[str, object]]], summary: pd.DataFrame, locks: pd.DataFrame, nulls: dict[str, np.ndarray]) -> list[pathlib.Path]:
    style(); paths: list[pathlib.Path] = []
    fig, axes = plt.subplots(2, 3, figsize=(17, 10), constrained_layout=True)
    for ax, (name, (_, view)) in zip(axes.flat, holdouts.items()):
        ax.plot(view["c1"], view["c2"], lw=1, color="#93c5fd", alpha=.7)
        ax.scatter(view["c1"], view["c2"], c=view["times"], cmap="viridis", s=6)
        ax.axvline(1, color="white", ls="--", lw=.7); ax.axhline(1, color="white", ls="--", lw=.7)
        ax.add_patch(plt.Rectangle((.25, 1.25), .5, .5, fill=False, ec="#f59e0b", lw=1.3, ls="--"))
        ax.set(xlim=(0,2), ylim=(0,2), title=f"{name} — {'PASS' if view['score']['complete'] else 'FAIL'}", xlabel="C1 movement", ylabel="C2 connection")
        ax.grid(True)
    axes.flat[-1].axis("off")
    fig.suptitle("T427 untouched holdouts — separate spacetime Di-ARA trajectories", fontsize=17, fontweight="bold")
    p = RESULTS / "T427_HOLDOUT_TRAJECTORY_GALLERY.png"; fig.savefig(p, dpi=170); plt.close(fig); paths.append(p)

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    y = np.arange(len(summary))
    for key, label, color in [("pre_connection_time","pre connection","#8b5cf6"),("onset_time","native onset","#f59e0b"),("movement_time","movement","#ef4444"),("reclosure_time","reclosure","#22c55e")]:
        ax.scatter(summary[key], y, s=70, label=label, color=color)
    for i, row in summary.iterrows():
        vals = [row[k] for k in ("pre_connection_time","onset_time","movement_time","reclosure_time") if np.isfinite(row[k])]
        if vals: ax.plot(vals, [i]*len(vals), color="#94a3b8", lw=1)
    ax.axvline(0, color="white", ls=":", label="published peak crosswalk (opened after scoring)")
    ax.set(yticks=y, yticklabels=summary["event"], xlabel="Seconds relative to published event GPS", title="Frozen stage-time waterfall", ylabel="Untouched holdout")
    ax.grid(True); ax.legend(ncol=3, fontsize=8)
    p = RESULTS / "T427_STAGE_TIME_WATERFALL.png"; fig.savefig(p, dpi=170); plt.close(fig); paths.append(p)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), constrained_layout=True)
    observed = int(summary["complete"].sum())
    for ax, (name, values) in zip(axes, nulls.items()):
        bins = np.arange(-0.5, 6.5, 1)
        ax.hist(values, bins=bins, color="#64748b", edgecolor="#cbd5e1", alpha=.85)
        ax.axvline(observed, color="#ef4444", lw=3, label=f"observed {observed}/5")
        ax.set(title=f"{name.replace('_',' ').title()} null", xlabel="Complete loops among five holdouts", ylabel="Replicates", xticks=range(6))
        ax.grid(True); ax.legend()
    fig.suptitle("Observed loop count against frozen chronology controls", fontsize=16, fontweight="bold")
    p = RESULTS / "T427_NULL_DISTRIBUTIONS.png"; fig.savefig(p, dpi=170); plt.close(fig); paths.append(p)

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    x = np.arange(len(locks)); width=.25
    ax.bar(x-width, locks["pre_error_median"], width, label="matched pre-opening", color="#60a5fa")
    ax.bar(x, locks["post_error_median"], width, label="post-reclosure", color="#22c55e")
    ax.bar(x+width, locks["phase_control_q05"], width, label="5th percentile phase-scramble", color="#f59e0b")
    ax.set(xticks=x, xticklabels=locks["event"], ylabel="AR(2) normalized one-step error (lower = more locked)", title="Independent information-lock check")
    ax.grid(True, axis="y"); ax.legend()
    p = RESULTS / "T427_INFORMATION_LOCK.png"; fig.savefig(p, dpi=170); plt.close(fig); paths.append(p)
    return paths


def image_data(path: pathlib.Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def html_table(frame: pd.DataFrame, columns: list[str] | None = None) -> str:
    if columns is not None:
        frame = frame[columns]
    return frame.to_html(index=False, border=0, classes="data", float_format=lambda x: f"{x:.4g}")


def build_report(summary: pd.DataFrame, qa: pd.DataFrame, locks: pd.DataFrame, third: pd.DataFrame, wrong: pd.DataFrame, results: dict[str, object], figures: list[pathlib.Path]) -> None:
    cards = "".join(f'<section class="figure"><img src="data:image/png;base64,{image_data(p)}" alt="{p.stem}"><p>{p.stem}</p></section>' for p in figures)
    protocol_hash = (ROOT / "T427_FROZEN_PROTOCOL.sha256").read_text(encoding="utf-8").strip().split()[0]
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>T427 spacetime strain handover</title>
<style>body{{background:#0d1117;color:#e5e7eb;font:16px/1.55 system-ui;margin:0}}main{{max-width:1500px;margin:auto;padding:36px}}h1{{font-size:2.2rem}}h2{{margin-top:2.4rem;color:#93c5fd}}.lead{{font-size:1.15rem;color:#cbd5e1;max-width:1100px}}.badge{{display:inline-block;padding:7px 12px;border-radius:999px;background:{'#14532d' if results['primary_supported'] else '#7f1d1d'};font-weight:700}}.figure{{background:#111827;border:1px solid #334155;border-radius:12px;padding:14px;margin:22px 0}}.figure img{{width:100%;height:auto}}table.data{{width:100%;border-collapse:collapse;background:#111827;font-size:.88rem}}table.data th,table.data td{{padding:8px;border:1px solid #334155;text-align:right}}table.data th{{background:#1e293b}}code{{color:#fbbf24}}a{{color:#60a5fa}}.note{{border-left:4px solid #f59e0b;padding:12px 16px;background:#1f2937}}</style></head><body><main>
<h1>T427 — Spacetime-strain Irrationality Di-ARA handover</h1>
<p class="lead">A waveform-template-free, time-facing test of opening, movement excursion, reclosure and Information³-style relational locking in public multi-detector gravitational-wave strain.</p>
<p><span class="badge">{'PRIMARY SUPPORT' if results['primary_supported'] else 'PRIMARY NOT SUPPORTED'}</span></p>
<p class="note"><strong>ARA-first boundary:</strong> event GPS time was used only to retrieve and crop a fixed interval. Inspiral/merger/ringdown labels and the published peak were not used to construct coordinates or choose stages. Protocol SHA-256: <code>{protocol_hash}</code>.</p>
<h2>Answer first</h2><p>{results['answer_first']}</p>
<h2>Frozen gates</h2><pre>{json.dumps(results['gates'], indent=2)}</pre>
<h2>Holdout results</h2>{html_table(summary)}
<h2>Independent information-lock channel</h2>{html_table(locks)}
<h2>Three-detector Information³ check</h2>{html_table(third)}
<h2>Wrong-relation control</h2>{html_table(wrong)}
<h2>Visual evidence</h2>{cards}
<h2>Source and data-quality audit</h2>{html_table(qa, ['event','role','detector','fs_hz','duration_s','finite_fraction','zero_fraction','public_dq_pass','max_native_z','c1_low_saturation','c1_high_saturation','c2_low_saturation','c2_high_saturation','sha256'])}
<h2>What this is in established physics</h2><p>The independent detector time series are calibrated gravitational-wave strain. After scoring, the ARA stage times are compared with the published event peak. That comparison is a crosswalk only: it does not enter the frozen coordinate construction.</p>
<h2>Claim boundary</h2><p>A pass would support this operational transfer of the T426 temporal route to these public strain records. It would not prove universal ARA geometry or replace general relativity. A failure rejects the frozen transfer and is retained without relabelling coordinates or events.</p>
<h2>Reproduction</h2><p>Run <code>t427_spacetime_strain_handover.py --mode all</code> after the source downloader. CSV, JSON, PNG and source hashes are stored beside this report.</p>
</main></body></html>"""
    (RESULTS / "T427_SPACETIME_STRAIN_HANDOVER_REPORT.html").write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dev", "all"), default="all")
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    events = manifest["events"]
    if args.mode == "dev":
        events = [e for e in events if e["role"] == "development_only"]
    rng = np.random.default_rng(SEED)
    analysed: dict[str, tuple[dict[str, DetectorData], dict[str, object], dict[str, object]]] = {}
    qa_rows: list[dict[str, object]] = []
    for event in events:
        print(f"Analysing {event['event']} ({event['role']})", flush=True)
        detectors, view, lock = analyse_event(event, rng)
        analysed[event["event"]] = (detectors, view, lock)
        qa_rows.extend(det.qa for det in detectors.values())
        event_figure(event["event"], detectors, view, RESULTS / f"T427_{event['event']}_DIAGNOSTIC.png")
    pd.DataFrame(qa_rows).to_csv(RESULTS / f"T427_{args.mode.upper()}_SOURCE_QA.csv", index=False)
    if args.mode == "dev":
        dev = analysed["GW150914"]
        payload = {"event": "GW150914", "score": dev[1]["score"], "information_lock": dev[2]}
        (RESULTS / "T427_DEV_RESULT.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        print(json.dumps(payload, indent=2, default=str))
        return

    holdouts = {name: (det, view) for name, (det, view, _) in analysed.items() if det["H1"].role == "primary_holdout"}
    summary_rows=[]; lock_rows=[]; third_rows=[]; detector_rows=[]; coordinate_rows=[]
    for name, (detectors, view) in holdouts.items():
        score = dict(view["score"]); score["event"] = name; summary_rows.append(score)
        lock = dict(analysed[name][2]); lock["event"] = name; lock_rows.append(lock)
        third = third_detector_test(detectors, view); third["event"] = name; third_rows.append(third)
        for detector, aligned in view["aligned"].items():
            for i, t in enumerate(view["times"]):
                detector_rows.append({"event":name,"detector":detector,"time_s":t,"c1":aligned["c1"][i],"c2":aligned["c2"][i],"z_native":aligned["z"][i]})
        for i,t in enumerate(view["times"]):
            coordinate_rows.append({"event":name,"time_s":t,"c1":view["c1"][i],"c2":view["c2"][i],"z_native":view["z"][i],"agreement":view["agreement"][i]})
    summary = pd.DataFrame(summary_rows)
    locks = pd.DataFrame(lock_rows)
    for column in (
        "pre_error_median", "post_error_median", "phase_control_q05",
        "phase_control_median",
    ):
        if column not in locks:
            locks[column] = np.nan
    third = pd.DataFrame(third_rows)
    print("Running 10,000 detector time-slide replicates", flush=True)
    time_slide = time_slide_null({k: v[1] for k, v in holdouts.items()}, rng)
    print("Running 1,000 phase-scramble replicates", flush=True)
    phase_null = phase_scramble_null({name:(analysed[name][0], analysed[name][1]) for name in holdouts}, rng)
    reverse_count, wrong_rows = reverse_and_wrong_controls(holdouts)
    wrong = pd.DataFrame(wrong_rows)
    observed = int(summary["complete"].sum())
    p_time = float((1 + np.sum(time_slide >= observed)) / (1 + len(time_slide)))
    p_phase = float((1 + np.sum(phase_null >= observed)) / (1 + len(phase_null)))
    median_agreement = float(summary["median_stage_agreement"].median())
    wrong_agreement = float(wrong["median_agreement"].median())
    lock_passes = int(locks["pass"].fillna(False).sum())
    gates = {
        "loops_at_least_3_of_5": bool(observed >= 3),
        "time_slide_p_lt_0_05": bool(p_time < .05),
        "phase_scramble_p_lt_0_05": bool(p_phase < .05),
        "information_lock_at_least_3_of_5": bool(lock_passes >= 3),
        "stage_agreement_at_least_0_70": bool(median_agreement >= .70),
        "agreement_beats_wrong_relation": bool(median_agreement > wrong_agreement),
    }
    primary_supported = all(gates.values())
    answer_first = (
        f"The frozen four-stage route completed in {observed}/5 untouched events; "
        f"time-slide p={p_time:.4g}, phase-scramble p={p_phase:.4g}. "
        f"Independent post-reclosure information locking passed in {lock_passes}/5. "
        f"Median H1/L1 stage agreement was {median_agreement:.3f} versus "
        f"{wrong_agreement:.3f} for wrong-event pairing. The conjunction of frozen "
        f"primary gates {'passed' if primary_supported else 'did not pass'}."
    )
    result_payload = {
        "observed_complete_loops": observed,
        "information_lock_passes": lock_passes,
        "time_slide_p": p_time,
        "phase_scramble_p": p_phase,
        "time_reverse_complete_loops": reverse_count,
        "median_stage_agreement": median_agreement,
        "wrong_relation_median_agreement": wrong_agreement,
        "gates": gates,
        "primary_supported": primary_supported,
        "answer_first": answer_first,
    }
    summary.to_csv(RESULTS / "T427_HOLDOUT_SUMMARY.csv", index=False)
    locks.to_csv(RESULTS / "T427_INFORMATION_LOCK.csv", index=False)
    third.to_csv(RESULTS / "T427_THREE_DETECTOR_INFORMATION3.csv", index=False)
    wrong.to_csv(RESULTS / "T427_WRONG_RELATION.csv", index=False)
    pd.DataFrame(detector_rows).to_csv(RESULTS / "T427_DETECTOR_COORDINATES.csv", index=False)
    pd.DataFrame(coordinate_rows).to_csv(RESULTS / "T427_CONSENSUS_COORDINATES.csv", index=False)
    pd.DataFrame({"time_slide": time_slide}).to_csv(RESULTS / "T427_TIME_SLIDE_NULL.csv", index=False)
    pd.DataFrame({"phase_scramble": phase_null}).to_csv(RESULTS / "T427_PHASE_SCRAMBLE_NULL.csv", index=False)
    (RESULTS / "T427_RESULTS.json").write_text(json.dumps(result_payload, indent=2), encoding="utf-8")
    figures = [RESULTS / f"T427_{name}_DIAGNOSTIC.png" for name in analysed]
    figures.extend(summary_figures(holdouts, summary, locks, {"time_slide":time_slide,"phase_scramble":phase_null}))
    qa = pd.DataFrame(qa_rows)
    build_report(summary, qa, locks, third, wrong, result_payload, figures)
    print(json.dumps(result_payload, indent=2))


if __name__ == "__main__":
    main()
