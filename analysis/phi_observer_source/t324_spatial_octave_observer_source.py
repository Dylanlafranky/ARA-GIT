from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_deps"))

import h5py
import numpy as np
from PIL import Image, ImageDraw, ImageFont


DATA_FILE = HERE / "data" / "qu_kemar_anechoic_radius_0.5_1_2_3_m.sofa"
SOURCE_URL = (
    "https://sofacoustics.org/data/sofatoolbox_test/"
    "qu_kemar_anechoic_radius_0.5_1_2_3_m.sofa"
)
SOURCE_SHA256 = "4d11740336d936ad129473029fadce5320f7455f0475634fed4d5519b2878a42"
PROTOCOL = HERE / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_PROTOCOL_v1_FROZEN.md"
RESULTS_DIR = HERE / "results"
RESULTS_JSON = RESULTS_DIR / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_RESULTS.json"
PATHS_CSV = RESULTS_DIR / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_PATHS.csv"
RATIOS_CSV = RESULTS_DIR / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_RATIOS.csv"
FREQUENCIES_CSV = RESULTS_DIR / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_FREQUENCIES.csv"
FIGURE = HERE / "T324_SPATIAL_OCTAVE_OBSERVER_SOURCE.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
RADII = (0.5, 1.0, 2.0, 3.0)
ANGLE_TARGETS = {
    "direct": 0.0,
    "thirty": 30.0,
    "phi": 36.0,
    "ordinary_octave": 45.0,
    "phi_reversed": 54.0,
    "ridge_half": 60.0,
    "perpendicular": 90.0,
}
NON_OCTAVE_TARGETS = {
    "ordinary_non_octave": math.degrees(math.atan(0.5)),
    "phi": 36.0,
    "ordinary_octave": 45.0,
    "phi_reversed": 54.0,
}
FREQ_MIN = 500.0
FREQ_MAX = 8000.0
MAG_FLOOR = 0.01
PHASE_FLOOR = 0.05
MIN_BINS = 8
N_BOOT = 5000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_seed(*parts: object) -> int:
    payload = "|".join(map(str, parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def decode(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.bytes_):
        return bytes(value).decode("utf-8", errors="replace")
    return str(value)


def fetch_source() -> None:
    DATA_FILE.parent.mkdir(exist_ok=True)
    if DATA_FILE.exists() and sha256(DATA_FILE) == SOURCE_SHA256:
        return
    urllib.request.urlretrieve(SOURCE_URL, DATA_FILE)
    actual = sha256(DATA_FILE)
    if actual != SOURCE_SHA256:
        DATA_FILE.unlink(missing_ok=True)
        raise RuntimeError(f"Source checksum mismatch: {actual} != {SOURCE_SHA256}")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(exist_ok=True)
    if not rows:
        raise RuntimeError(f"Refusing to write empty CSV: {path}")
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def angle_loss(theta: np.ndarray, target: float) -> float:
    return float(np.sqrt(np.mean((theta - target) ** 2)))


def nearest(value: float, targets: dict[str, float]) -> str:
    return min(targets, key=lambda name: abs(value - targets[name]))


def cluster_bootstrap_difference(
    rows: list[dict],
    left: str,
    right: str,
    label: str,
    ear: int | None = None,
) -> dict:
    grouped: dict[int, list[float]] = {}
    for row in rows:
        if ear is not None and int(row["ear"]) != ear:
            continue
        a = float(row[left])
        b = float(row[right])
        if not (math.isfinite(a) and math.isfinite(b)):
            continue
        grouped.setdefault(int(row["direction_index"]), []).append(a - b)
    source_values = np.asarray(
        [np.mean(grouped[key]) for key in sorted(grouped)], dtype=float
    )
    if not len(source_values):
        return {
            "source_directions": 0,
            "median_difference": math.nan,
            "ci95_low": math.nan,
            "ci95_high": math.nan,
        }
    rng = np.random.default_rng(stable_seed("T324", label, ear))
    draws = rng.integers(0, len(source_values), size=(N_BOOT, len(source_values)))
    boots = np.median(source_values[draws], axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "source_directions": int(len(source_values)),
        "median_difference": float(np.median(source_values)),
        "ci95_low": float(lo),
        "ci95_high": float(hi),
    }


def load_matched_data() -> dict:
    if sha256(DATA_FILE) != SOURCE_SHA256:
        raise RuntimeError("Frozen KEMAR source hash does not match")
    with h5py.File(DATA_FILE, "r") as f:
        ir_flat = np.asarray(f["Data.IR"], dtype=float)
        source = np.asarray(f["SourcePosition"], dtype=float)
        fs = float(np.asarray(f["Data.SamplingRate"], dtype=float).reshape(-1)[0])
        data_delay = np.asarray(f["Data.Delay"], dtype=float)
        delay_units = decode(f["Data.Delay"].attrs.get("Units", "unspecified"))
        latency_present = "MeasurementAudioLatency" in f
        latency = (
            np.asarray(f["MeasurementAudioLatency"], dtype=float)
            if latency_present
            else None
        )
        attrs = {key: decode(value) for key, value in f.attrs.items()}

    if source.shape != (ir_flat.shape[0], 3):
        raise RuntimeError(f"Unexpected SourcePosition shape: {source.shape}")
    if sorted(np.unique(source[:, 2]).tolist()) != list(RADII):
        raise RuntimeError(f"Frozen radii absent: {np.unique(source[:, 2])}")
    if np.any(data_delay != 0.0):
        if delay_units.lower() not in {"second", "seconds", "s"}:
            raise RuntimeError(
                "Non-zero Data.Delay is present without a parseable seconds unit"
            )
    # Zero is invariant under the unspecified unit. Its timing contribution is
    # exactly zero and therefore does not require a conversion assumption.

    keys = sorted({(round(float(a), 6), round(float(e), 6)) for a, e in source[:, :2]})
    lookup: dict[tuple[float, float, float], int] = {}
    for idx, (az, el, radius) in enumerate(source):
        key = (round(float(az), 6), round(float(el), 6), round(float(radius), 6))
        if key in lookup:
            raise RuntimeError(f"Duplicate direction-radius record: {key}")
        lookup[key] = idx
    missing = [
        (az, el, radius)
        for az, el in keys
        for radius in RADII
        if (az, el, radius) not in lookup
    ]
    if missing:
        raise RuntimeError(f"Unmatched direction-radius records: {missing[:5]}")

    d_count = len(keys)
    ears = ir_flat.shape[1]
    samples = ir_flat.shape[2]
    ir = np.empty((d_count, len(RADII), ears, samples), dtype=float)
    flat_indices = np.empty((d_count, len(RADII)), dtype=int)
    for d, (az, el) in enumerate(keys):
        for j, radius in enumerate(RADII):
            idx = lookup[(az, el, radius)]
            ir[d, j] = ir_flat[idx]
            flat_indices[d, j] = idx

    h = np.fft.rfft(ir, axis=-1)
    mag = np.abs(h)
    raw_phase = np.unwrap(np.angle(h), axis=-1)
    freqs = np.fft.rfftfreq(samples, d=1.0 / fs)

    # Data.Delay is [I,R] here and is identically zero. MeasurementAudioLatency
    # is absent. Preserve a general per-direction/radius/ear timing array so the
    # exact metadata path remains explicit.
    delay_seconds = np.zeros((d_count, len(RADII), ears), dtype=float)
    if np.any(data_delay):
        delay_seconds += np.broadcast_to(
            data_delay.reshape(1, 1, ears), delay_seconds.shape
        )
    if latency_present:
        lat = np.asarray(latency, dtype=float)
        if lat.size == 1:
            delay_seconds += float(lat.reshape(-1)[0])
        elif lat.shape == (ir_flat.shape[0], ears):
            for d in range(d_count):
                for j in range(len(RADII)):
                    delay_seconds[d, j] += lat[flat_indices[d, j]]
        else:
            raise RuntimeError(
                f"Unparseable MeasurementAudioLatency shape: {lat.shape}"
            )
    total_phase = raw_phase - (
        2.0 * np.pi * freqs[None, None, None, :] * delay_seconds[..., None]
    )

    return {
        "ir": ir,
        "mag": mag,
        "raw_phase": raw_phase,
        "total_phase": total_phase,
        "freqs": freqs,
        "fs": fs,
        "directions": np.asarray(keys, dtype=float),
        "metadata": {
            "file": str(DATA_FILE),
            "sha256": sha256(DATA_FILE),
            "shape_flat": list(ir_flat.shape),
            "shape_matched": list(ir.shape),
            "sampling_rate_hz": fs,
            "directions": d_count,
            "ears": ears,
            "samples": samples,
            "radii_m": list(RADII),
            "data_delay_shape": list(data_delay.shape),
            "data_delay_units": delay_units,
            "data_delay_min": float(np.min(data_delay)),
            "data_delay_max": float(np.max(data_delay)),
            "measurement_audio_latency_present": latency_present,
            "database": attrs.get("DatabaseName"),
            "listener": attrs.get("ListenerShortName"),
            "room_type": attrs.get("RoomType"),
            "license": attrs.get("License"),
            "reference": attrs.get("References"),
        },
    }


def analyze_angle_step(
    phase: np.ndarray,
    mag: np.ndarray,
    freqs: np.ndarray,
    directions: np.ndarray,
    lower_idx: int,
    upper_idx: int,
    step_label: str,
    targets: dict[str, float],
) -> dict:
    band = np.flatnonzero((freqs >= FREQ_MIN) & (freqs <= FREQ_MAX))
    max_mag = np.max(mag[..., 1:], axis=-1)
    d_count, _, ears, _ = phase.shape
    next_direction = np.roll(np.arange(d_count), -1)
    path_rows: list[dict] = []
    event_angles: list[np.ndarray] = []
    frequency_angles: dict[int, list[float]] = {int(k): [] for k in band}
    quadrants = {"++": 0, "+-": 0, "-+": 0, "--": 0}
    excluded_paths = 0

    for d in range(d_count):
        for ear in range(ears):
            p0 = phase[d, lower_idx, ear]
            p1 = phase[d, upper_idx, ear]
            valid = (
                (mag[d, lower_idx, ear, band] >= MAG_FLOOR * max_mag[d, lower_idx, ear])
                & (mag[d, upper_idx, ear, band] >= MAG_FLOOR * max_mag[d, upper_idx, ear])
            )
            ks = band[valid]
            parallel = p0[ks]
            rung = p1[ks] - p0[ks]
            stable = (np.abs(parallel) >= PHASE_FLOOR) & (np.abs(rung) >= PHASE_FLOOR)
            ks = ks[stable]
            parallel = parallel[stable]
            rung = rung[stable]
            if len(ks) < MIN_BINS:
                excluded_paths += 1
                continue
            theta = np.degrees(np.arctan2(np.abs(rung), np.abs(parallel)))
            ara_x = 2.0 * np.cos(np.radians(theta))

            q = int(next_direction[d])
            broken_upper = phase[q, upper_idx, ear]
            broken_valid = (
                (mag[d, lower_idx, ear, band] >= MAG_FLOOR * max_mag[d, lower_idx, ear])
                & (mag[q, upper_idx, ear, band] >= MAG_FLOOR * max_mag[q, upper_idx, ear])
            )
            bks = band[broken_valid]
            bparallel = p0[bks]
            brung = broken_upper[bks] - p0[bks]
            bstable = (np.abs(bparallel) >= PHASE_FLOOR) & (np.abs(brung) >= PHASE_FLOOR)
            btheta = np.degrees(
                np.arctan2(np.abs(brung[bstable]), np.abs(bparallel[bstable]))
            )
            broken_phi = angle_loss(btheta, 36.0) if len(btheta) >= MIN_BINS else math.nan

            row = {
                "step": step_label,
                "direction_index": d,
                "azimuth_deg": float(directions[d, 0]),
                "elevation_deg": float(directions[d, 1]),
                "ear": ear,
                "lower_radius_m": RADII[lower_idx],
                "upper_radius_m": RADII[upper_idx],
                "eligible_bins": int(len(ks)),
                "free_angle_deg": float(np.mean(theta)),
                "median_angle_deg": float(np.median(theta)),
                "median_ara_x": float(np.median(ara_x)),
                "broken_phi_loss": broken_phi,
            }
            for name, target in targets.items():
                row[f"loss_{name}"] = angle_loss(theta, target)
            path_rows.append(row)
            event_angles.append(theta)

            sx = np.where(parallel >= 0, "+", "-")
            sy = np.where(rung >= 0, "+", "-")
            for a, b in zip(sx, sy):
                quadrants[str(a) + str(b)] += 1
            for k, value in zip(ks, theta):
                frequency_angles[int(k)].append(float(value))

    frequency_rows = []
    for k in band:
        values = np.asarray(frequency_angles[int(k)], dtype=float)
        if not len(values):
            continue
        median = float(np.median(values))
        frequency_rows.append(
            {
                "metric": "angle",
                "step": step_label,
                "frequency_hz": float(freqs[k]),
                "events": int(len(values)),
                "median": median,
                "mean": float(np.mean(values)),
                "closest_target": nearest(median, targets),
            }
        )

    all_angles = np.concatenate(event_angles) if event_angles else np.asarray([])
    losses = {
        name: float(np.median([row[f"loss_{name}"] for row in path_rows]))
        for name in targets
    }
    comparisons = {
        name: cluster_bootstrap_difference(
            path_rows, "loss_phi", f"loss_{name}", f"{step_label}-phi-{name}"
        )
        for name in targets
        if name != "phi"
    }
    broken_comparison = cluster_bootstrap_difference(
        path_rows, "loss_phi", "broken_phi_loss", f"{step_label}-broken"
    )
    per_ear = {}
    for ear in range(ears):
        subset = [row for row in path_rows if int(row["ear"]) == ear]
        median_free = float(np.median([row["free_angle_deg"] for row in subset]))
        per_ear[str(ear)] = {
            "paths": len(subset),
            "median_free_angle_deg": median_free,
            "closest_free_target_36_45_54": nearest(
                median_free,
                {"phi": 36.0, "ordinary_octave": 45.0, "phi_reversed": 54.0},
            ),
        }

    median_free = float(np.median([row["free_angle_deg"] for row in path_rows]))
    summary = {
        "paths": len(path_rows),
        "excluded_paths": excluded_paths,
        "events": int(len(all_angles)),
        "median_event_angle_deg": float(np.median(all_angles)),
        "median_free_path_angle_deg": median_free,
        "median_event_ara_x": float(
            np.median(2.0 * np.cos(np.radians(all_angles)))
        ),
        "median_target_losses": losses,
        "closest_loss_target": min(losses, key=losses.get),
        "closest_free_target": nearest(median_free, targets),
        "phi_target_comparisons": comparisons,
        "observed_phi_minus_broken": broken_comparison,
        "quadrant_counts": quadrants,
        "per_ear": per_ear,
    }
    return {
        "path_rows": path_rows,
        "frequency_rows": frequency_rows,
        "event_angles": all_angles,
        "summary": summary,
    }


def analyze_ratios(
    phase: np.ndarray,
    mag: np.ndarray,
    freqs: np.ndarray,
    directions: np.ndarray,
    label: str,
) -> dict:
    band = np.flatnonzero((freqs >= FREQ_MIN) & (freqs <= FREQ_MAX))
    max_mag = np.max(mag[..., 1:], axis=-1)
    d_count, _, ears, _ = phase.shape
    ratio_rows: list[dict] = []
    rho_values: list[np.ndarray] = []
    eta_values: list[np.ndarray] = []
    rho_by_frequency: dict[int, list[float]] = {int(k): [] for k in band}
    eta_by_frequency: dict[int, list[float]] = {int(k): [] for k in band}
    excluded_rho = 0
    excluded_eta = 0

    for d in range(d_count):
        for ear in range(ears):
            phases = phase[d, :, ear]
            magnitude_ok = np.ones(len(band), dtype=bool)
            for radius_idx in range(len(RADII)):
                magnitude_ok &= (
                    mag[d, radius_idx, ear, band]
                    >= MAG_FLOOR * max_mag[d, radius_idx, ear]
                )

            d05_1 = phases[1, band] - phases[0, band]
            d1_2 = phases[2, band] - phases[1, band]
            rho_ok = (
                magnitude_ok
                & (np.abs(d05_1) >= PHASE_FLOOR)
                & (np.abs(d1_2) >= PHASE_FLOOR)
            )
            rho_ks = band[rho_ok]
            rho = np.abs(d1_2[rho_ok]) / np.abs(d05_1[rho_ok])

            d2_3 = phases[3, band] - phases[2, band]
            eta_ok = (
                magnitude_ok
                & (np.abs(d1_2) >= PHASE_FLOOR)
                & (np.abs(d2_3) >= PHASE_FLOOR)
            )
            eta_ks = band[eta_ok]
            eta = np.abs(d2_3[eta_ok]) / np.abs(d1_2[eta_ok])

            if len(rho) < MIN_BINS:
                excluded_rho += 1
            if len(eta) < MIN_BINS:
                excluded_eta += 1
            if len(rho) < MIN_BINS or len(eta) < MIN_BINS:
                continue

            row = {
                "analysis": label,
                "direction_index": d,
                "azimuth_deg": float(directions[d, 0]),
                "elevation_deg": float(directions[d, 1]),
                "ear": ear,
                "rho_bins": int(len(rho)),
                "median_rho": float(np.median(rho)),
                "rho_log_loss_phi": float(np.median(np.abs(np.log(rho) - math.log(PHI)))),
                "rho_log_loss_two": float(np.median(np.abs(np.log(rho) - math.log(2.0)))),
                "eta_bins": int(len(eta)),
                "median_eta": float(np.median(eta)),
                "eta_log_loss_one": float(np.median(np.abs(np.log(eta)))),
                "eta_log_loss_phi": float(np.median(np.abs(np.log(eta) - math.log(PHI)))),
                "eta_log_loss_two": float(np.median(np.abs(np.log(eta) - math.log(2.0)))),
            }
            ratio_rows.append(row)
            rho_values.append(rho)
            eta_values.append(eta)
            for k, value in zip(rho_ks, rho):
                rho_by_frequency[int(k)].append(float(value))
            for k, value in zip(eta_ks, eta):
                eta_by_frequency[int(k)].append(float(value))

    frequency_rows: list[dict] = []
    for metric, values_by_frequency, targets in (
        ("rho", rho_by_frequency, {"phi": PHI, "ordinary_two": 2.0}),
        ("eta", eta_by_frequency, {"ordinary_one": 1.0, "phi": PHI, "two": 2.0}),
    ):
        for k in band:
            values = np.asarray(values_by_frequency[int(k)], dtype=float)
            if not len(values):
                continue
            median = float(np.median(values))
            frequency_rows.append(
                {
                    "metric": metric,
                    "step": label,
                    "frequency_hz": float(freqs[k]),
                    "events": int(len(values)),
                    "median": median,
                    "mean": float(np.mean(values)),
                    "closest_target": nearest(median, targets),
                }
            )

    all_rho = np.concatenate(rho_values) if rho_values else np.asarray([])
    all_eta = np.concatenate(eta_values) if eta_values else np.asarray([])
    per_ear = {}
    for ear in range(ears):
        subset = [row for row in ratio_rows if int(row["ear"]) == ear]
        median_rho = float(np.median([row["median_rho"] for row in subset]))
        median_eta = float(np.median([row["median_eta"] for row in subset]))
        comparison = cluster_bootstrap_difference(
            ratio_rows,
            "rho_log_loss_phi",
            "rho_log_loss_two",
            f"{label}-rho-phi-two",
            ear=ear,
        )
        per_ear[str(ear)] = {
            "paths": len(subset),
            "median_rho": median_rho,
            "rho_closest_target": nearest(median_rho, {"phi": PHI, "ordinary_two": 2.0}),
            "phi_minus_two_log_loss": comparison,
            "median_eta": median_eta,
            "eta_closest_target": nearest(
                median_eta, {"ordinary_one": 1.0, "phi": PHI, "two": 2.0}
            ),
        }

    summary = {
        "paths": len(ratio_rows),
        "excluded_rho_paths": excluded_rho,
        "excluded_eta_paths": excluded_eta,
        "rho_events": int(len(all_rho)),
        "eta_events": int(len(all_eta)),
        "median_event_rho": float(np.median(all_rho)),
        "median_path_rho": float(np.median([row["median_rho"] for row in ratio_rows])),
        "rho_closest_target": nearest(
            float(np.median([row["median_rho"] for row in ratio_rows])),
            {"phi": PHI, "ordinary_two": 2.0},
        ),
        "rho_phi_minus_two_log_loss": cluster_bootstrap_difference(
            ratio_rows,
            "rho_log_loss_phi",
            "rho_log_loss_two",
            f"{label}-rho-phi-two",
        ),
        "median_event_eta": float(np.median(all_eta)),
        "median_path_eta": float(np.median([row["median_eta"] for row in ratio_rows])),
        "eta_closest_target": nearest(
            float(np.median([row["median_eta"] for row in ratio_rows])),
            {"ordinary_one": 1.0, "phi": PHI, "two": 2.0},
        ),
        "per_ear": per_ear,
    }
    return {
        "ratio_rows": ratio_rows,
        "frequency_rows": frequency_rows,
        "rho_values": all_rho,
        "eta_values": all_eta,
        "summary": summary,
    }


def analytic_null(freqs: np.ndarray) -> dict:
    band = freqs[(freqs >= FREQ_MIN) & (freqs <= FREQ_MAX)]
    phase = {radius: -2.0 * np.pi * band * radius / 343.0 for radius in RADII}
    angles = {}
    for lower, upper in ((0.5, 1.0), (1.0, 2.0), (2.0, 3.0)):
        theta = np.degrees(
            np.arctan2(np.abs(phase[upper] - phase[lower]), np.abs(phase[lower]))
        )
        angles[f"{lower:g}_to_{upper:g}"] = float(np.median(theta))
    rho = np.abs(phase[2.0] - phase[1.0]) / np.abs(phase[1.0] - phase[0.5])
    eta = np.abs(phase[3.0] - phase[2.0]) / np.abs(phase[2.0] - phase[1.0])
    return {
        "angles_deg": angles,
        "median_rho": float(np.median(rho)),
        "median_eta": float(np.median(eta)),
    }


def arrival_time_audit(ir: np.ndarray, fs: float) -> dict:
    peak = np.argmax(np.abs(ir), axis=-1).astype(float)
    threshold_onset = np.empty_like(peak)
    for d in range(ir.shape[0]):
        for radius in range(ir.shape[1]):
            for ear in range(ir.shape[2]):
                trace = np.abs(ir[d, radius, ear])
                threshold = 0.1 * np.max(trace)
                eligible = np.flatnonzero(trace >= threshold)
                threshold_onset[d, radius, ear] = float(eligible[0])
    expected = {
        "0.5_to_1": (1.0 - 0.5) / 343.0 * fs,
        "1_to_2": (2.0 - 1.0) / 343.0 * fs,
        "2_to_3": (3.0 - 2.0) / 343.0 * fs,
    }
    observed_peak = {
        "0.5_to_1": float(np.median(peak[:, 1] - peak[:, 0])),
        "1_to_2": float(np.median(peak[:, 2] - peak[:, 1])),
        "2_to_3": float(np.median(peak[:, 3] - peak[:, 2])),
    }
    observed_onset = {
        "0.5_to_1": float(np.median(threshold_onset[:, 1] - threshold_onset[:, 0])),
        "1_to_2": float(np.median(threshold_onset[:, 2] - threshold_onset[:, 1])),
        "2_to_3": float(np.median(threshold_onset[:, 3] - threshold_onset[:, 2])),
    }
    return {
        "peak_sample_by_radius_m": {
            str(radius): float(np.median(peak[:, j]))
            for j, radius in enumerate(RADII)
        },
        "ten_percent_onset_sample_by_radius_m": {
            str(radius): float(np.median(threshold_onset[:, j]))
            for j, radius in enumerate(RADII)
        },
        "median_matched_peak_increment_samples": observed_peak,
        "median_matched_onset_increment_samples": observed_onset,
        "expected_free_field_increment_samples_at_343mps": expected,
        "interpretation": (
            "The stored responses keep arrivals in nearly the same sample region across "
            "radii; they do not retain the literal free-field time-of-flight increments."
        ),
    }


def determine_verdict(angle_summaries: dict, ratio_summary: dict, raw_ratio: dict) -> dict:
    octave_labels = ("0.5_to_1", "1_to_2")
    g1 = all(
        angle_summaries[label]["closest_loss_target"] == "phi"
        and angle_summaries[label]["phi_target_comparisons"]["ordinary_octave"]["ci95_high"] < 0
        for label in octave_labels
    )
    g2 = all(
        all(
            ear_summary["closest_free_target_36_45_54"] == "phi"
            for ear_summary in angle_summaries[label]["per_ear"].values()
        )
        for label in octave_labels
    )
    g3 = all(
        angle_summaries[label]["observed_phi_minus_broken"]["ci95_high"] < 0
        for label in octave_labels
    )
    g4 = all(
        ear_summary["rho_closest_target"] == "phi"
        and ear_summary["phi_minus_two_log_loss"]["ci95_high"] < 0
        for ear_summary in ratio_summary["per_ear"].values()
    )
    timing_same = (
        ratio_summary["rho_closest_target"] == raw_ratio["rho_closest_target"]
    )
    non_oct = angle_summaries["2_to_3"]
    g5 = (
        non_oct["closest_loss_target"] == "ordinary_non_octave"
        and ratio_summary["eta_closest_target"] == "ordinary_one"
        and timing_same
        and g1
        and g2
        and g4
    )
    gates = {
        "G1_phi_angle_specificity": g1,
        "G2_repeated_free_angle_location": g2,
        "G3_relation_control": g3,
        "G4_offset_invariant_phi_scaling": g4,
        "G5_non_octave_and_timing_robustness": g5,
    }
    passed = sum(gates.values())
    verdict = "SUPPORTED" if passed == 5 else "MIXED" if passed >= 3 else "NOT SUPPORTED"
    return {"gates": gates, "passed": passed, "total": 5, "verdict": verdict}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    choices = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in choices:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def histogram(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], values: np.ndarray,
              bounds: tuple[float, float], color: str, bins: int = 60, width: int = 3) -> None:
    x0, y0, x1, y1 = box
    clipped = values[(values >= bounds[0]) & (values <= bounds[1])]
    counts, edges = np.histogram(clipped, bins=bins, range=bounds, density=True)
    if not np.any(counts):
        return
    counts = counts / np.max(counts)
    points = []
    for i, count in enumerate(counts):
        center = (edges[i] + edges[i + 1]) / 2.0
        px = x0 + (center - bounds[0]) / (bounds[1] - bounds[0]) * (x1 - x0)
        py = y1 - count * (y1 - y0)
        points.append((px, py))
    if len(points) > 1:
        draw.line(points, fill=color, width=width)


def draw_figure(analyses: dict, ratios: dict, verdict: dict, output: Path) -> None:
    canvas = Image.new("RGB", (1900, 1320), "#fbfcfe")
    d = ImageDraw.Draw(canvas)
    ink = "#202733"
    muted = "#667085"
    grid = "#d9dee7"
    blue = "#3b6fb6"
    gold = "#d79a2b"
    slate = "#7d8795"
    purple = "#8d63b8"
    d.text((70, 45), "T324 - literal spatial-octave observer-source test", fill=ink, font=font(40, True))
    d.text(
        (70, 98),
        f"360 matched directions x 2 ears | frozen verdict: {verdict['verdict']} ({verdict['passed']}/5 gates)",
        fill=muted,
        font=font(23),
    )

    panels = {
        "angles": (70, 175, 920, 680),
        "losses": (980, 175, 1830, 680),
        "ratios": (70, 760, 920, 1240),
        "frequency": (980, 760, 1830, 1240),
    }
    for box in panels.values():
        d.rounded_rectangle(box, radius=18, fill="#ffffff", outline=grid, width=2)

    # Panel 1: angle distributions.
    x0, y0, x1, y1 = panels["angles"]
    d.text((x0 + 28, y0 + 22), "Spatial projection angles", fill=ink, font=font(27, True))
    d.text((x0 + 28, y0 + 58), "Same direction, ear and frequency; complete published timing", fill=muted, font=font(18))
    plot = (x0 + 70, y0 + 110, x1 - 35, y1 - 65)
    for value, label, color in (
        (36.0, "Phi 36", purple),
        (45.0, "ordinary 45", ink),
        (NON_OCTAVE_TARGETS["ordinary_non_octave"], "2->3 null", slate),
    ):
        px = plot[0] + value / 90.0 * (plot[2] - plot[0])
        d.line((px, plot[1], px, plot[3]), fill=color, width=2)
        d.text((px + 4, plot[1] + 3), label, fill=color, font=font(15, True))
    histogram(d, plot, analyses["0.5_to_1"]["event_angles"], (0, 90), blue)
    histogram(d, plot, analyses["1_to_2"]["event_angles"], (0, 90), gold)
    histogram(d, plot, analyses["2_to_3"]["event_angles"], (0, 90), slate)
    d.line((plot[0], plot[3], plot[2], plot[3]), fill=ink, width=2)
    for tick in (0, 18, 36, 45, 54, 72, 90):
        px = plot[0] + tick / 90.0 * (plot[2] - plot[0])
        d.text((px - 12, plot[3] + 8), str(tick), fill=muted, font=font(16))
    d.text((plot[0], plot[3] + 35), "folded angle (degrees)", fill=muted, font=font(17))
    d.text((plot[2] - 240, plot[1] + 55), "0.5->1 m", fill=blue, font=font(17, True))
    d.text((plot[2] - 240, plot[1] + 80), "1->2 m", fill=gold, font=font(17, True))
    d.text((plot[2] - 240, plot[1] + 105), "2->3 m control", fill=slate, font=font(17, True))

    # Panel 2: median path RMS losses.
    x0, y0, x1, y1 = panels["losses"]
    d.text((x0 + 28, y0 + 22), "Frozen target losses", fill=ink, font=font(27, True))
    d.text((x0 + 28, y0 + 58), "Median path RMS angle loss; lower is better", fill=muted, font=font(18))
    rows = [
        ("0.5->1", analyses["0.5_to_1"]["summary"]),
        ("1->2", analyses["1_to_2"]["summary"]),
    ]
    max_loss = max(
        summary["median_target_losses"][target]
        for _, summary in rows
        for target in ("phi", "ordinary_octave", "phi_reversed")
    ) * 1.12
    chart = (x0 + 105, y0 + 115, x1 - 45, y1 - 70)
    colors = {"phi": purple, "ordinary_octave": ink, "phi_reversed": gold}
    targets = [("phi", "36"), ("ordinary_octave", "45"), ("phi_reversed", "54")]
    bar_w = 42
    group_gap = 180
    start_x = chart[0] + 130
    for g, (step, summary) in enumerate(rows):
        gx = start_x + g * group_gap * 2
        for j, (target, label) in enumerate(targets):
            value = summary["median_target_losses"][target]
            bx = gx + j * (bar_w + 18)
            by = chart[3] - value / max_loss * (chart[3] - chart[1])
            d.rectangle((bx, by, bx + bar_w, chart[3]), fill=colors[target])
            d.text((bx - 2, by - 24), f"{value:.2f}", fill=ink, font=font(14))
            d.text((bx + 8, chart[3] + 8), label, fill=muted, font=font(15))
        d.text((gx + 40, chart[3] + 35), step + " m", fill=ink, font=font(18, True))
    d.line((chart[0], chart[3], chart[2], chart[3]), fill=ink, width=2)
    d.text((chart[0], chart[1] - 2), "degrees", fill=muted, font=font(16))

    # Panel 3: offset-invariant ratio distributions.
    x0, y0, x1, y1 = panels["ratios"]
    d.text((x0 + 28, y0 + 22), "Offset-invariant distance increments", fill=ink, font=font(27, True))
    d.text((x0 + 28, y0 + 58), "rho: octave increments | eta: equal 1 m increments", fill=muted, font=font(18))
    plot = (x0 + 75, y0 + 110, x1 - 35, y1 - 65)
    bounds = (0.0, 3.0)
    for value, label, color in ((1.0, "1", slate), (PHI, "phi", purple), (2.0, "2", ink)):
        px = plot[0] + value / 3.0 * (plot[2] - plot[0])
        d.line((px, plot[1], px, plot[3]), fill=color, width=2)
        d.text((px + 3, plot[1] + 3), label, fill=color, font=font(16, True))
    histogram(d, plot, ratios["rho_values"], bounds, blue)
    histogram(d, plot, ratios["eta_values"], bounds, gold)
    d.line((plot[0], plot[3], plot[2], plot[3]), fill=ink, width=2)
    for tick in (0, 0.5, 1, 1.5, 2, 2.5, 3):
        px = plot[0] + tick / 3.0 * (plot[2] - plot[0])
        d.text((px - 12, plot[3] + 8), str(tick), fill=muted, font=font(15))
    d.text((plot[2] - 205, plot[1] + 55), "rho (octaves)", fill=blue, font=font(17, True))
    d.text((plot[2] - 205, plot[1] + 80), "eta (control)", fill=gold, font=font(17, True))
    d.text((plot[0], plot[3] + 35), "absolute phase-increment ratio", fill=muted, font=font(17))

    # Panel 4: rho by frequency.
    x0, y0, x1, y1 = panels["frequency"]
    d.text((x0 + 28, y0 + 22), "Octave ratio across frequency", fill=ink, font=font(27, True))
    d.text((x0 + 28, y0 + 58), "Median rho across matched directions and ears", fill=muted, font=font(18))
    plot = (x0 + 80, y0 + 110, x1 - 40, y1 - 65)
    rho_freq = [row for row in ratios["frequency_rows"] if row["metric"] == "rho"]
    for value, label, color in ((PHI, "phi", purple), (2.0, "ordinary 2", ink)):
        py = plot[3] - value / 3.0 * (plot[3] - plot[1])
        d.line((plot[0], py, plot[2], py), fill=color, width=2)
        d.text((plot[0] + 4, py - 20), label, fill=color, font=font(15, True))
    points = []
    for row in rho_freq:
        px = plot[0] + (row["frequency_hz"] - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * (plot[2] - plot[0])
        value = min(3.0, max(0.0, row["median"]))
        py = plot[3] - value / 3.0 * (plot[3] - plot[1])
        points.append((px, py))
    if len(points) > 1:
        d.line(points, fill=blue, width=3)
    d.line((plot[0], plot[3], plot[2], plot[3]), fill=ink, width=2)
    d.line((plot[0], plot[1], plot[0], plot[3]), fill=ink, width=2)
    for hz in (500, 2000, 4000, 6000, 8000):
        px = plot[0] + (hz - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * (plot[2] - plot[0])
        d.text((px - 22, plot[3] + 8), str(hz), fill=muted, font=font(15))
    for value in (0, 1, 2, 3):
        py = plot[3] - value / 3.0 * (plot[3] - plot[1])
        d.text((plot[0] - 28, py - 9), str(value), fill=muted, font=font(15))
    d.text((plot[0], plot[3] + 35), "frequency (Hz)", fill=muted, font=font(17))
    d.text((plot[0] - 54, plot[1] - 2), "rho", fill=muted, font=font(16))

    d.text(
        (70, 1275),
        "Source: official SOFA Toolbox test archive | Frozen before file inspection | Bars and curves are descriptive; gates use direction-cluster inference",
        fill=muted,
        font=font(16),
    )
    canvas.save(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        fetch_source()
    if not DATA_FILE.exists():
        raise SystemExit("Frozen source missing. Run with --fetch.")

    data = load_matched_data()
    total = data["total_phase"]
    raw = data["raw_phase"]
    mag = data["mag"]
    freqs = data["freqs"]
    directions = data["directions"]

    angle_05_1 = analyze_angle_step(
        total, mag, freqs, directions, 0, 1, "0.5_to_1", ANGLE_TARGETS
    )
    angle_1_2 = analyze_angle_step(
        total, mag, freqs, directions, 1, 2, "1_to_2", ANGLE_TARGETS
    )
    angle_2_3 = analyze_angle_step(
        total, mag, freqs, directions, 2, 3, "2_to_3", NON_OCTAVE_TARGETS
    )
    raw_angle_05_1 = analyze_angle_step(
        raw, mag, freqs, directions, 0, 1, "raw_0.5_to_1", ANGLE_TARGETS
    )
    raw_angle_1_2 = analyze_angle_step(
        raw, mag, freqs, directions, 1, 2, "raw_1_to_2", ANGLE_TARGETS
    )
    ratios = analyze_ratios(total, mag, freqs, directions, "complete_timing")
    raw_ratios = analyze_ratios(raw, mag, freqs, directions, "stored_ir_only")

    angle_analyses = {
        "0.5_to_1": angle_05_1,
        "1_to_2": angle_1_2,
        "2_to_3": angle_2_3,
    }
    angle_summaries = {key: value["summary"] for key, value in angle_analyses.items()}
    timing_sensitivity = {
        "0.5_to_1": raw_angle_05_1["summary"],
        "1_to_2": raw_angle_1_2["summary"],
        "ratios": raw_ratios["summary"],
    }
    verdict = determine_verdict(
        angle_summaries, ratios["summary"], raw_ratios["summary"]
    )
    null = analytic_null(freqs)
    timing_audit = arrival_time_audit(data["ir"], data["fs"])

    results = {
        "test": "T324 spatial-octave observer-source",
        "date": "2026-08-01",
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "source": data["metadata"],
        "frozen_parameters": {
            "radii_m": list(RADII),
            "frequency_band_hz": [FREQ_MIN, FREQ_MAX],
            "magnitude_floor_fraction": MAG_FLOOR,
            "phase_floor_rad": PHASE_FLOOR,
            "minimum_bins_per_path": MIN_BINS,
            "cluster_bootstrap_samples": N_BOOT,
            "phi": PHI,
            "angle_targets_deg": ANGLE_TARGETS,
            "non_octave_targets_deg": NON_OCTAVE_TARGETS,
        },
        "analytic_free_field_null": null,
        "arrival_time_audit": timing_audit,
        "angle_summaries": angle_summaries,
        "ratio_summary": ratios["summary"],
        "timing_sensitivity": timing_sensitivity,
        "verdict": verdict,
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    all_path_rows = (
        angle_05_1["path_rows"]
        + angle_1_2["path_rows"]
        + angle_2_3["path_rows"]
    )
    write_csv(PATHS_CSV, all_path_rows)
    write_csv(RATIOS_CSV, ratios["ratio_rows"] + raw_ratios["ratio_rows"])
    frequency_rows = (
        angle_05_1["frequency_rows"]
        + angle_1_2["frequency_rows"]
        + angle_2_3["frequency_rows"]
        + ratios["frequency_rows"]
    )
    write_csv(FREQUENCIES_CSV, frequency_rows)
    draw_figure(angle_analyses, ratios, verdict, FIGURE)

    print(json.dumps({
        "verdict": verdict,
        "analytic_null": null,
        "angle_summaries": {
            key: {
                "median_free_path_angle_deg": value["median_free_path_angle_deg"],
                "median_event_angle_deg": value["median_event_angle_deg"],
                "closest_loss_target": value["closest_loss_target"],
                "median_target_losses": value["median_target_losses"],
            }
            for key, value in angle_summaries.items()
        },
        "ratio_summary": ratios["summary"],
    }, indent=2))


if __name__ == "__main__":
    main()
