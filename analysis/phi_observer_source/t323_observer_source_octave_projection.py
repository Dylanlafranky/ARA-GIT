from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_deps"))

import h5py
import numpy as np
from PIL import Image, ImageDraw, ImageFont


DATASETS = {
    "NH2": HERE / "data" / "ARI_NH2_hrtf_M_dtf_256.sofa",
    "NH4": HERE / "data" / "ARI_NH4_hrtf_M_dtf_256.sofa",
}
SOURCES = {
    "NH2": {
        "url": "https://sofacoustics.org/data/sofatoolbox_test/ARI_NH2_hrtf_M_dtf%20256.sofa",
        "sha256": "ba90827a8477a574a6267f38d48ea564587223d110aec28a2768698e1821efb0",
    },
    "NH4": {
        "url": "https://sofacoustics.org/data/sofatoolbox_test/ARI_NH4_hrtf_M_dtf%20256.sofa",
        "sha256": "855da8e2317dff83866a9a2e74e952d9d404013d186d3a510286c7dfd7525d2a",
    },
}
RESULTS = HERE / "results"
TARGETS = {
    "direct": 0.0,
    "thirty": 30.0,
    "phi": 36.0,
    "pure_delay": 45.0,
    "phi_complement": 54.0,
    "ridge_half": 60.0,
    "perpendicular": 90.0,
}
N_SCRAMBLES = 64
N_BOOT = 5000
MAG_FLOOR = 0.01
PHASE_FLOOR = 0.05


def stable_seed(*parts: object) -> int:
    raw = "|".join(map(str, parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "little")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fetch_sources() -> None:
    (HERE / "data").mkdir(exist_ok=True)
    for label, path in DATASETS.items():
        expected = SOURCES[label]["sha256"]
        if path.exists() and sha256(path) == expected:
            continue
        urllib.request.urlretrieve(SOURCES[label]["url"], path)
        actual = sha256(path)
        if actual != expected:
            path.unlink(missing_ok=True)
            raise RuntimeError(f"{label} checksum mismatch: {actual} != {expected}")


def to_float(value: float | np.floating | None) -> float | None:
    if value is None:
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def angle_from_components(parallel: np.ndarray, octave: np.ndarray) -> np.ndarray:
    return np.degrees(np.arctan2(np.abs(octave), np.abs(parallel)))


def losses(theta: np.ndarray) -> dict[str, float]:
    return {
        name: float(np.sqrt(np.mean((theta - target) ** 2)))
        for name, target in TARGETS.items()
    }


def analyze_phase(
    phase: np.ndarray,
    mag: np.ndarray,
    source_pos: np.ndarray,
    fs: float,
    label: str,
    do_controls: bool = True,
) -> dict:
    m_count, ears, bins = phase.shape
    n_time = (bins - 1) * 2
    lower_bins = np.arange(2, bins // 2 + 1, dtype=int)
    freqs = lower_bins * fs / n_time
    max_mag = np.max(mag[:, :, 1:], axis=2)

    sort_idx = np.lexsort((source_pos[:, 2], source_pos[:, 1], source_pos[:, 0]))
    next_map = np.empty(m_count, dtype=int)
    next_map[sort_idx] = np.roll(sort_idx, -1)

    path_rows: list[dict] = []
    event_rows: list[dict] = []
    bin_events: dict[int, list[float]] = {int(k): [] for k in lower_bins}
    bin_ara: dict[int, list[float]] = {int(k): [] for k in lower_bins}
    quadrant_counts = {"++": 0, "+-": 0, "-+": 0, "--": 0}

    for m in range(m_count):
        for ear in range(ears):
            p = phase[m, ear]
            q = next_map[m]
            p_next = phase[q, ear]
            valid = (
                (mag[m, ear, lower_bins] >= MAG_FLOOR * max_mag[m, ear])
                & (mag[m, ear, 2 * lower_bins] >= MAG_FLOOR * max_mag[m, ear])
                & (np.abs(p[lower_bins]) >= PHASE_FLOOR)
            )
            ks = lower_bins[valid]
            if len(ks) == 0:
                continue
            parallel = p[ks]
            octave = p[2 * ks] - p[ks]
            theta = angle_from_components(parallel, octave)
            ara_x = 2.0 * np.cos(np.radians(theta))
            row = {
                "dataset": label,
                "source_index": m,
                "ear": ear,
                "azimuth_deg": float(source_pos[m, 0]),
                "elevation_deg": float(source_pos[m, 1]),
                "radius_m": float(source_pos[m, 2]),
                "eligible_pairs": int(len(ks)),
                "free_angle_deg": float(np.mean(theta)),
                "median_angle_deg": float(np.median(theta)),
                "median_ara_x": float(np.median(ara_x)),
            }
            for name, value in losses(theta).items():
                row[f"loss_{name}"] = value

            if do_controls:
                broken_valid = (
                    (mag[m, ear, lower_bins] >= MAG_FLOOR * max_mag[m, ear])
                    & (mag[q, ear, 2 * lower_bins] >= MAG_FLOOR * max_mag[q, ear])
                    & (np.abs(p[lower_bins]) >= PHASE_FLOOR)
                )
                bks = lower_bins[broken_valid]
                btheta = angle_from_components(p[bks], p_next[2 * bks] - p[bks])
                row["broken_phi_loss"] = losses(btheta)["phi"] if len(bks) else math.nan

                increments = np.diff(p)
                scramble_losses = []
                for rep in range(N_SCRAMBLES):
                    rng = np.random.default_rng(stable_seed("T323", label, m, ear, rep))
                    permuted = rng.permutation(increments)
                    scrambled = np.concatenate(([0.0], np.cumsum(permuted)))
                    stheta = angle_from_components(
                        scrambled[ks], scrambled[2 * ks] - scrambled[ks]
                    )
                    scramble_losses.append(losses(stheta)["phi"])
                row["scrambled_phi_loss"] = float(np.mean(scramble_losses))

            path_rows.append(row)

            for j, k in enumerate(ks):
                par = float(parallel[j])
                octv = float(octave[j])
                sx = "+" if par >= 0 else "-"
                sy = "+" if octv >= 0 else "-"
                quadrant_counts[sx + sy] += 1
                bin_events[int(k)].append(float(theta[j]))
                bin_ara[int(k)].append(float(ara_x[j]))
                event_rows.append(
                    {
                        "dataset": label,
                        "source_index": m,
                        "ear": ear,
                        "lower_bin": int(k),
                        "lower_frequency_hz": float(k * fs / n_time),
                        "parallel_phase_rad": par,
                        "octave_increment_rad": octv,
                        "theta_deg": float(theta[j]),
                        "ara_x": float(ara_x[j]),
                        "quadrant": sx + sy,
                    }
                )

    bin_rows = []
    for k, f in zip(lower_bins, freqs):
        values = np.asarray(bin_events[int(k)], dtype=float)
        if len(values) == 0:
            continue
        median = float(np.median(values))
        closest = min(TARGETS, key=lambda name: abs(median - TARGETS[name]))
        bin_rows.append(
            {
                "dataset": label,
                "lower_bin": int(k),
                "lower_frequency_hz": float(f),
                "upper_frequency_hz": float(2 * f),
                "events": int(len(values)),
                "mean_theta_deg": float(np.mean(values)),
                "median_theta_deg": median,
                "median_ara_x": float(np.median(bin_ara[int(k)])),
                "closest_target": closest,
            }
        )

    return {
        "path_rows": path_rows,
        "event_rows": event_rows,
        "bin_rows": bin_rows,
        "quadrant_counts": quadrant_counts,
        "lower_bins": lower_bins,
    }


def cluster_bootstrap_diff(
    rows: list[dict], left: str, right: str, seed: int
) -> dict[str, float | int]:
    source_ids = sorted({int(row["source_index"]) for row in rows})
    grouped: dict[int, list[float]] = {source: [] for source in source_ids}
    for row in rows:
        a = float(row[left])
        b = float(row[right])
        if math.isfinite(a) and math.isfinite(b):
            grouped[int(row["source_index"])].append(a - b)
    eligible = [source for source in source_ids if grouped[source]]
    source_values = np.asarray(
        [np.mean(grouped[source]) for source in eligible], dtype=float
    )
    point = float(np.median(source_values))
    rng = np.random.default_rng(seed)
    boots = np.empty(N_BOOT, dtype=float)
    for i in range(N_BOOT):
        draw = rng.integers(0, len(source_values), size=len(source_values))
        boots[i] = np.median(source_values[draw])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "source_directions": int(len(source_values)),
        "median_difference": point,
        "ci95_low": float(lo),
        "ci95_high": float(hi),
    }


def summarize_dataset(label: str, analysis: dict) -> dict:
    rows = analysis["path_rows"]
    summary = {
        "source_directions": len({row["source_index"] for row in rows}),
        "paths": len(rows),
        "events": len(analysis["event_rows"]),
        "median_free_angle_deg": float(np.median([r["free_angle_deg"] for r in rows])),
        "median_path_angle_deg": float(np.median([r["median_angle_deg"] for r in rows])),
        "median_ara_x": float(np.median([r["median_ara_x"] for r in rows])),
        "median_target_losses": {
            name: float(np.median([r[f"loss_{name}"] for r in rows]))
            for name in TARGETS
        },
        "quadrant_counts": analysis["quadrant_counts"],
        "bin_target_wins": {
            name: sum(row["closest_target"] == name for row in analysis["bin_rows"])
            for name in TARGETS
        },
        "eligible_bins": len(analysis["bin_rows"]),
    }
    summary["closest_loss_target"] = min(
        TARGETS, key=lambda name: summary["median_target_losses"][name]
    )
    summary["closest_free_angle_target"] = min(
        TARGETS,
        key=lambda name: abs(summary["median_free_angle_deg"] - TARGETS[name]),
    )
    summary["paired_target_comparisons"] = {}
    for name in TARGETS:
        if name == "phi":
            continue
        summary["paired_target_comparisons"][f"phi_minus_{name}"] = cluster_bootstrap_diff(
            rows,
            "loss_phi",
            f"loss_{name}",
            stable_seed("T323", label, "phi", name),
        )
    summary["control_comparisons"] = {
        "observed_phi_minus_broken": cluster_bootstrap_diff(
            rows,
            "loss_phi",
            "broken_phi_loss",
            stable_seed("T323", label, "broken"),
        ),
        "observed_phi_minus_scrambled": cluster_bootstrap_diff(
            rows,
            "loss_phi",
            "scrambled_phi_loss",
            stable_seed("T323", label, "scrambled"),
        ),
    }
    summary["median_control_losses"] = {
        "observed_phi": float(np.median([r["loss_phi"] for r in rows])),
        "broken_phi": float(np.nanmedian([r["broken_phi_loss"] for r in rows])),
        "scrambled_phi": float(np.nanmedian([r["scrambled_phi_loss"] for r in rows])),
    }
    return summary


def load_and_analyze(label: str, path: Path) -> tuple[dict, dict, dict]:
    with h5py.File(path, "r") as f:
        ir = np.asarray(f["Data.IR"], dtype=float)
        fs = float(np.asarray(f["Data.SamplingRate"])[0])
        source_pos = np.asarray(f["SourcePosition"], dtype=float)
        latency = np.asarray(f["MeasurementAudioLatency"], dtype=float)
        attrs = {
            key: (
                value.decode("utf-8", errors="replace")
                if isinstance(value, bytes)
                else str(value)
            )
            for key, value in f.attrs.items()
        }
    h = np.fft.rfft(ir, axis=2)
    mag = np.abs(h)
    phase = np.unwrap(np.angle(h), axis=2)
    primary = analyze_phase(phase, mag, source_pos, fs, label, do_controls=True)

    # Post-hoc archive-timing sensitivity only. This is not allowed to replace
    # the frozen primary result.
    bins = phase.shape[2]
    omega = 2.0 * np.pi * np.arange(bins) / ir.shape[2]
    total_phase = phase - latency[:, :, None] * omega[None, None, :]
    latency_analysis = analyze_phase(
        total_phase, mag, source_pos, fs, label + "_latency", do_controls=False
    )
    metadata = {
        "file": str(path),
        "sha256": sha256(path),
        "shape": list(ir.shape),
        "sampling_rate_hz": fs,
        "source_position_type": "spherical",
        "source_directions": int(ir.shape[0]),
        "receivers": int(ir.shape[1]),
        "samples": int(ir.shape[2]),
        "latency_min_samples": float(np.min(latency)),
        "latency_max_samples": float(np.max(latency)),
        "database": attrs.get("DatabaseName"),
        "listener": attrs.get("ListenerShortName"),
        "room_type": attrs.get("RoomType"),
        "license_field": attrs.get("License"),
    }
    return primary, latency_analysis, metadata


def verdict(summaries: dict[str, dict]) -> tuple[dict[str, bool], str]:
    nh2, nh4 = summaries["NH2"], summaries["NH4"]
    g1 = (
        nh2["closest_loss_target"] == "phi"
        and nh4["closest_loss_target"] == "phi"
        and all(
            comp["ci95_high"] < 0
            for comp in nh2["paired_target_comparisons"].values()
        )
    )
    p45_2 = nh2["paired_target_comparisons"]["phi_minus_pure_delay"]
    p45_4 = nh4["paired_target_comparisons"]["phi_minus_pure_delay"]
    g2 = (
        p45_2["median_difference"] < 0
        and p45_2["ci95_high"] < 0
        and p45_4["median_difference"] < 0
    )
    g3 = (
        nh2["closest_free_angle_target"] == "phi"
        and nh4["closest_free_angle_target"] == "phi"
    )
    g4 = all(
        nh2["control_comparisons"][key]["median_difference"] < 0
        and nh2["control_comparisons"][key]["ci95_high"] < 0
        and nh4["control_comparisons"][key]["median_difference"] < 0
        for key in ["observed_phi_minus_broken", "observed_phi_minus_scrambled"]
    )
    g5 = all(
        summary["bin_target_wins"]["phi"] > summary["eligible_bins"] / 2
        for summary in [nh2, nh4]
    )
    gates = {"G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5}
    count = sum(gates.values())
    status = "SUPPORTED" if count == 5 else "MIXED" if count >= 3 else "NOT SUPPORTED"
    return gates, status


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def draw_visual(summaries: dict, analyses: dict, out: Path) -> None:
    width, height = 1800, 1200
    img = Image.new("RGB", (width, height), "#f7f8fa")
    d = ImageDraw.Draw(img)
    ink, muted, grid = "#172033", "#657086", "#d9dee8"
    blue, gold, orange = "#3f6fb5", "#d89a2b", "#d5662f"
    d.text((60, 35), "T323 — observer–source octave projection", fill=ink, font=font(44, True))
    d.text(
        (60, 90),
        "Measured ARI HRIR transfer paths · angle from accumulated phase and octave increment",
        fill=muted,
        font=font(24),
    )

    panels = [(60, 160, 850, 640), (930, 160, 1740, 640), (60, 700, 850, 1140), (930, 700, 1740, 1140)]
    for x0, y0, x1, y1 in panels:
        d.rectangle((x0, y0, x1, y1), fill="#ffffff", outline=grid, width=2)

    # Panel 1: angle distribution.
    x0, y0, x1, y1 = panels[0]
    d.text((x0 + 25, y0 + 20), "Event-angle distribution", fill=ink, font=font(28, True))
    plot = (x0 + 75, y0 + 85, x1 - 30, y1 - 55)
    bins = np.linspace(0, 90, 46)
    max_density = 0.0
    histograms = {}
    for label in ["NH2", "NH4"]:
        vals = np.asarray([r["theta_deg"] for r in analyses[label]["event_rows"]])
        hist, edges = np.histogram(vals, bins=bins, density=True)
        histograms[label] = (hist, edges)
        max_density = max(max_density, float(np.max(hist)))
    for target, color, name in [(36, orange, "Phi 36°"), (45, ink, "delay 45°")]:
        px = plot[0] + (target / 90) * (plot[2] - plot[0])
        d.line((px, plot[1], px, plot[3]), fill=color, width=3)
        d.text((px + 5, plot[1] + 5), name, fill=color, font=font(18, True))
    for label, color in [("NH2", blue), ("NH4", gold)]:
        hist, edges = histograms[label]
        pts = []
        for i, value in enumerate(hist):
            center = (edges[i] + edges[i + 1]) / 2
            px = plot[0] + center / 90 * (plot[2] - plot[0])
            py = plot[3] - value / max_density * (plot[3] - plot[1])
            pts.append((px, py))
        d.line(pts, fill=color, width=4)
    d.line((plot[0], plot[3], plot[2], plot[3]), fill=ink, width=2)
    for tick in [0, 18, 36, 45, 54, 72, 90]:
        px = plot[0] + tick / 90 * (plot[2] - plot[0])
        d.text((px - 15, plot[3] + 8), str(tick), fill=muted, font=font(17))
    d.text((plot[0], plot[3] + 32), "folded projection angle (degrees)", fill=muted, font=font(18))
    d.text((plot[2] - 150, plot[1] + 45), "NH2 — blue", fill=blue, font=font(18, True))
    d.text((plot[2] - 150, plot[1] + 70), "NH4 — gold", fill=gold, font=font(18, True))

    # Panel 2: fixed target loss.
    x0, y0, x1, y1 = panels[1]
    d.text((x0 + 25, y0 + 20), "Median path loss by frozen target", fill=ink, font=font(28, True))
    names = list(TARGETS)
    max_loss = max(summaries[l]["median_target_losses"][n] for l in summaries for n in names)
    chart_left, chart_top, chart_right, chart_bottom = x0 + 75, y0 + 85, x1 - 25, y1 - 85
    group_w = (chart_right - chart_left) / len(names)
    for i, name in enumerate(names):
        center = chart_left + (i + 0.5) * group_w
        for j, (label, color) in enumerate([("NH2", blue), ("NH4", gold)]):
            value = summaries[label]["median_target_losses"][name]
            bw = group_w * 0.28
            left = center + (j - 1) * bw
            top = chart_bottom - value / max_loss * (chart_bottom - chart_top)
            d.rectangle((left, top, left + bw, chart_bottom), fill=color)
        short = {"phi_complement": "54°", "pure_delay": "45°", "ridge_half": "60°", "perpendicular": "90°", "direct": "0°", "thirty": "30°", "phi": "36°"}[name]
        d.text((center - 16, chart_bottom + 8), short, fill=muted, font=font(17))
    d.line((chart_left, chart_bottom, chart_right, chart_bottom), fill=ink, width=2)
    d.text((chart_left, chart_bottom + 38), "target angle · lower RMS loss is better", fill=muted, font=font(18))

    # Panel 3: octave-bin progression.
    x0, y0, x1, y1 = panels[2]
    d.text((x0 + 25, y0 + 20), "Median angle across octave pairs", fill=ink, font=font(28, True))
    plot = (x0 + 80, y0 + 80, x1 - 30, y1 - 70)
    freq_all = [r["lower_frequency_hz"] for l in analyses for r in analyses[l]["bin_rows"]]
    fmin, fmax = min(freq_all), max(freq_all)
    for target, color in [(36, orange), (45, ink)]:
        py = plot[3] - target / 90 * (plot[3] - plot[1])
        d.line((plot[0], py, plot[2], py), fill=color, width=2)
    for label, color in [("NH2", blue), ("NH4", gold)]:
        pts = []
        for row in analyses[label]["bin_rows"]:
            px = plot[0] + (math.log2(row["lower_frequency_hz"]) - math.log2(fmin)) / (math.log2(fmax) - math.log2(fmin)) * (plot[2] - plot[0])
            py = plot[3] - row["median_theta_deg"] / 90 * (plot[3] - plot[1])
            pts.append((px, py))
        d.line(pts, fill=color, width=4)
    d.line((plot[0], plot[3], plot[2], plot[3]), fill=ink, width=2)
    d.line((plot[0], plot[1], plot[0], plot[3]), fill=ink, width=2)
    for hz in [375, 750, 1500, 3000, 6000, 12000]:
        if fmin <= hz <= fmax:
            px = plot[0] + (math.log2(hz) - math.log2(fmin)) / (math.log2(fmax) - math.log2(fmin)) * (plot[2] - plot[0])
            d.text((px - 22, plot[3] + 8), str(hz), fill=muted, font=font(16))
    for angle in [0, 18, 36, 45, 54, 72, 90]:
        py = plot[3] - angle / 90 * (plot[3] - plot[1])
        d.text((plot[0] - 45, py - 10), str(angle), fill=muted, font=font(16))
    d.text((plot[0], plot[3] + 38), "lower frequency (Hz, log2 axis)", fill=muted, font=font(18))

    # Panel 4: result summary with quadrant composition.
    x0, y0, x1, y1 = panels[3]
    d.text((x0 + 25, y0 + 20), "ARA readout and signed quadrants", fill=ink, font=font(28, True))
    y = y0 + 85
    for label, color in [("NH2", blue), ("NH4", gold)]:
        s = summaries[label]
        d.text((x0 + 35, y), label, fill=color, font=font(24, True))
        d.text((x0 + 115, y), f"median θ {s['median_free_angle_deg']:.2f}° · x {s['median_ara_x']:.4f} · closest {s['closest_loss_target']}", fill=ink, font=font(20))
        y += 50
        total = sum(s["quadrant_counts"].values())
        bar_left, bar_right = x0 + 115, x1 - 40
        cursor = bar_left
        shades = [blue, "#7898c8", gold, "#ead09a"]
        for (q, count), shade in zip(s["quadrant_counts"].items(), shades):
            w = (bar_right - bar_left) * count / total
            d.rectangle((cursor, y, cursor + w, y + 26), fill=shade)
            if w > 45:
                d.text((cursor + 4, y + 3), q, fill="#172033", font=font(15, True))
            cursor += w
        y += 70
    d.text((x0 + 35, y), "Reference", fill=muted, font=font(20, True))
    d.text((x0 + 145, y), "36° → x=φ   ·   45° → x=√2", fill=ink, font=font(20))
    y += 48
    d.text((x0 + 35, y), "Source", fill=muted, font=font(20, True))
    d.text((x0 + 145, y), "ARI NH2/NH4 · 1,550 directions × 2 ears", fill=ink, font=font(20))
    img.save(out)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="download checksum-locked SOFA inputs")
    args = parser.parse_args()
    if args.fetch:
        fetch_sources()
    missing = [str(path) for path in DATASETS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing inputs; rerun with --fetch: " + ", ".join(missing))
    RESULTS.mkdir(exist_ok=True)
    analyses = {}
    latency_analyses = {}
    metadata = {}
    summaries = {}
    latency_summaries = {}
    for label, path in DATASETS.items():
        primary, latency, meta = load_and_analyze(label, path)
        analyses[label] = primary
        latency_analyses[label] = latency
        metadata[label] = meta
        summaries[label] = summarize_dataset(label, primary)
        latency_summaries[label] = {
            "median_free_angle_deg": float(np.median([r["free_angle_deg"] for r in latency["path_rows"]])),
            "median_ara_x": float(np.median([r["median_ara_x"] for r in latency["path_rows"]])),
            "median_target_losses": {
                name: float(np.median([r[f"loss_{name}"] for r in latency["path_rows"]]))
                for name in TARGETS
            },
        }
        latency_summaries[label]["closest_loss_target"] = min(
            TARGETS, key=lambda name: latency_summaries[label]["median_target_losses"][name]
        )

    gates, status = verdict(summaries)
    output = {
        "test": "T323 observer-source octave projection",
        "protocol": "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_PROTOCOL_v1_FROZEN.md",
        "targets_degrees": TARGETS,
        "parameters": {
            "magnitude_floor_fraction": MAG_FLOOR,
            "phase_floor_rad": PHASE_FLOOR,
            "phase_scrambles_per_path": N_SCRAMBLES,
            "cluster_bootstrap_samples": N_BOOT,
        },
        "metadata": metadata,
        "primary_summaries": summaries,
        "posthoc_latency_sensitivity": latency_summaries,
        "gates": gates,
        "gates_passed": sum(gates.values()),
        "verdict": status,
    }
    (RESULTS / "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_RESULTS.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    write_csv(
        RESULTS / "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_PATHS.csv",
        analyses["NH2"]["path_rows"] + analyses["NH4"]["path_rows"],
    )
    write_csv(
        RESULTS / "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_BINS.csv",
        analyses["NH2"]["bin_rows"] + analyses["NH4"]["bin_rows"],
    )
    # Retain a deterministic, compact event sample for visual/audit inspection.
    sample = []
    for label in ["NH2", "NH4"]:
        rows = analyses[label]["event_rows"]
        stride = max(1, len(rows) // 5000)
        sample.extend(rows[::stride])
    write_csv(RESULTS / "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION_EVENT_SAMPLE.csv", sample)
    draw_visual(
        summaries,
        analyses,
        HERE / "T323_OBSERVER_SOURCE_OCTAVE_PROJECTION.png",
    )
    print(json.dumps({"verdict": status, "gates": gates, "summaries": summaries}, indent=2))


if __name__ == "__main__":
    main()
