"""
ara_state_geometry.py

Build a readable ARA state map for the current/latest state of a system.

This is intentionally not another predictor. It is the inverse/map half:
  - read each subsystem through the same causal ARA bandpass machinery
  - place each active rung at coordinate + ARA/2
  - measure energy occupancy, phase, and accumulate/release state
  - compute within-subsystem and cross-subsystem distance candidates

The output is a JS data file for quick HTML inspection and a console summary.
"""

from __future__ import annotations

import json
import math
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_framework import _measure_rung, causal_bandpass
from ara_shape_kernel_test import (
    PHI,
    WORKSPACE_ROOT,
    estimate_system_ara,
    infer_phase_from_shape,
    kernel_from_bandpass,
    measure_rung_ara_from_bp,
    release_fraction,
    rung_range,
    safe_base,
    shape_value_at_phase,
)
from ara_shape_kernel_raw_mit_ecg_test import (
    FS,
    PHI as ECG_PHI,
    causal_bandpass_fixed_mean as ecg_bandpass,
    estimate_heart_period_samples,
    infer_phase_from_shape as ecg_infer_phase,
    kernel_from_bandpass as ecg_kernel_from_bandpass,
    load_raw_ecg,
    measure_rung_ara_from_bp as ecg_measure_ara,
    read_amp_theta as ecg_read_amp_theta,
    release_fraction as ecg_release_fraction,
    shape_value_at_phase as ecg_shape_value,
)


def finite(value, fallback=None):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def round_float(value, digits=6):
    value = finite(value)
    return None if value is None else round(value, digits)


def clean_for_json(value):
    if isinstance(value, dict):
        return {str(k): clean_for_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_for_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return [clean_for_json(v) for v in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        v = float(value)
        return v if math.isfinite(v) else None
    return value


def load_grid_monthly(path: Path, name: str, skip_lines: int) -> pd.Series:
    rows = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for _ in range(skip_lines):
            next(f, None)
        for line in f:
            parts = line.split()
            if len(parts) < 13:
                continue
            try:
                year = int(parts[0])
            except ValueError:
                continue
            for month, token in enumerate(parts[1:13], start=1):
                try:
                    value = float(token)
                except ValueError:
                    continue
                if -90.0 < value < 90.0:
                    rows.append((pd.Timestamp(year=year, month=month, day=1), value))
    return pd.Series(dict(rows), name=name).sort_index()


def load_nino() -> pd.Series:
    df = pd.read_csv(
        WORKSPACE_ROOT / "Nino34" / "nino34.long.anom.csv",
        skiprows=1,
        names=["date", "value"],
        header=None,
    )
    df["date"] = pd.to_datetime(df["date"].astype(str).str.strip(), errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()
    df = df[df["value"] > -50]
    return df.set_index("date")["value"].astype(float).rename("NINO")


def load_enso_frame() -> pd.DataFrame:
    nino = load_nino()
    soi = load_grid_monthly(WORKSPACE_ROOT / "SOI_NOAA" / "soi.data", "SOI", skip_lines=1)
    pdo = load_grid_monthly(WORKSPACE_ROOT / "PDO_NOAA" / "ersst.v5.pdo.dat", "PDO", skip_lines=2)
    common = nino.index.intersection(soi.index).intersection(pdo.index).sort_values()
    frame = pd.concat([nino.reindex(common), soi.reindex(common), pdo.reindex(common)], axis=1)
    return frame.dropna()


def load_solar_series() -> pd.Series:
    df = pd.read_csv(
        WORKSPACE_ROOT / "SILSO_Solar" / "SN_m_tot_V2.0.csv",
        sep=";",
        header=None,
        names=["year", "month", "decimal_year", "value", "sigma", "n_obs", "marker"],
    )
    dates = pd.to_datetime(
        {
            "year": pd.to_numeric(df["year"], errors="coerce"),
            "month": pd.to_numeric(df["month"], errors="coerce"),
            "day": 1,
        },
        errors="coerce",
    )
    vals = pd.to_numeric(df["value"], errors="coerce")
    out = pd.Series(vals.values, index=dates, name="SUNSPOT").dropna()
    return out[out >= 0.0].astype(float)


def phase_gap(a, b):
    d = abs((float(a) - float(b)) % 1.0)
    return min(d, 1.0 - d)


def phase_mean(rungs):
    if not rungs:
        return None
    sx = 0.0
    sy = 0.0
    for rung in rungs:
        w = float(rung.get("occupancy", 0.0))
        ang = 2.0 * math.pi * float(rung.get("phase", 0.0))
        sx += w * math.cos(ang)
        sy += w * math.sin(ang)
    if abs(sx) + abs(sy) < 1e-12:
        return None
    return (math.atan2(sy, sx) / (2.0 * math.pi)) % 1.0


def summarize_kernel(kernel):
    return {
        "cycles": int(kernel.get("n_cycles", 0)),
        "fallback": bool(kernel.get("fallback", True)),
        "release_preview": [
            round_float(x, 4)
            for x in np.asarray(kernel.get("release", []), dtype=float)[:: max(1, len(kernel.get("release", [])) // 8)]
        ][:9],
        "accumulate_preview": [
            round_float(x, 4)
            for x in np.asarray(kernel.get("accumulate", []), dtype=float)[:: max(1, len(kernel.get("accumulate", [])) // 8)]
        ][:9],
    }


def phase_label(phase, ara, release_fn):
    split = release_fn(ara)
    return "release" if float(phase) < split else "accumulate"


def finalize_subsystem(subsystem, home_position):
    rungs = subsystem["rungs"]
    total_energy = sum(float(r["energy"]) for r in rungs)
    for r in rungs:
        r["occupancy"] = float(r["energy"] / total_energy) if total_energy > 1e-12 else 0.0
        r["home_distance"] = abs(float(r["position"]) - float(home_position))
    subsystem["rungs"] = sorted(rungs, key=lambda r: r["coordinate"])

    energy_center = sum(float(r["position"]) * float(r["occupancy"]) for r in subsystem["rungs"])
    coord_center = sum(float(r["coordinate"]) * float(r["occupancy"]) for r in subsystem["rungs"])
    ara_center = sum(float(r["ara"]) * float(r["occupancy"]) for r in subsystem["rungs"])
    subsystem["center"] = {
        "position": round_float(energy_center),
        "coordinate": round_float(coord_center),
        "ara": round_float(ara_center),
        "phase": round_float(phase_mean(subsystem["rungs"])),
        "total_energy": round_float(total_energy),
    }
    subsystem["top_rungs"] = [
        {
            "label": r["label"],
            "period": r["period"],
            "position": r["position"],
            "ara": r["ara"],
            "phase": r["phase"],
            "state": r["state"],
            "occupancy": r["occupancy"],
        }
        for r in sorted(subsystem["rungs"], key=lambda x: x["occupancy"], reverse=True)[:6]
    ]
    return subsystem


def extract_power_subsystem(
    name,
    role,
    values,
    dates,
    anchor,
    home_period,
    base,
    unit,
    max_rungs=22,
    pin_factor=4,
):
    arr = np.asarray(values, dtype=float)
    home_coordinate = math.log(home_period) / math.log(base)
    home_k = int(round(home_coordinate))
    home_bp = causal_bandpass(arr[:anchor], home_period)
    home_kernel = kernel_from_bandpass(home_bp, home_period)
    home_ara = measure_rung_ara_from_bp(home_bp, home_period)
    if home_ara is None or not math.isfinite(home_ara):
        home_ara = 1.0
    home_position = home_coordinate + home_ara / 2.0

    rungs = []
    for k in rung_range(base, anchor, max_rungs=max_rungs):
        period = float(base ** int(k))
        if period < 3.0 or pin_factor * period > anchor:
            continue
        bp = causal_bandpass(arr[:anchor], period)
        rec = _measure_rung(bp, period, int(k))
        if rec is None:
            continue

        ara = measure_rung_ara_from_bp(bp, period)
        if ara is None or not math.isfinite(ara):
            ara = home_ara
        kernel = kernel_from_bandpass(bp, period)
        phase = infer_phase_from_shape(bp, rec["amp"], ara, kernel)
        shape_now = shape_value_at_phase(phase, ara, kernel)
        split = release_fraction(ara)
        coordinate = math.log(period) / math.log(base)
        position = coordinate + float(ara) / 2.0
        rungs.append(
            {
                "label": f"k{int(k)}",
                "k": int(k),
                "coordinate": round_float(coordinate),
                "period": round_float(period),
                "period_unit": unit,
                "amp": round_float(rec["amp"]),
                "energy": float(rec["amp"] ** 2),
                "theta": round_float(rec["theta"]),
                "phase": round_float(phase),
                "ara": round_float(ara),
                "release_fraction": round_float(split),
                "position": round_float(position),
                "band_value": round_float(bp[-1]),
                "shape_now": round_float(shape_now),
                "state": phase_label(phase, ara, release_fraction),
                "shape": summarize_kernel(kernel),
            }
        )

    subsystem = {
        "name": name,
        "role": role,
        "anchor": {
            "index": int(anchor),
            "date": str(dates[anchor - 1]) if dates is not None else None,
            "value": round_float(arr[anchor - 1]),
        },
        "base": round_float(base),
        "home_period": round_float(home_period),
        "home_period_unit": unit,
        "home_coordinate": round_float(home_coordinate),
        "home_k_nearest": home_k,
        "home_ara": round_float(home_ara),
        "home_position": round_float(home_position),
        "mean_to_anchor": round_float(np.mean(arr[:anchor])),
        "std_to_anchor": round_float(np.std(arr[:anchor])),
        "home_shape": summarize_kernel(home_kernel),
        "rungs": rungs,
    }
    return finalize_subsystem(subsystem, home_position)


def extract_ecg_subsystem():
    raw, dat_path, hea_path = load_raw_ecg(record="16265", channel=0, minutes=30)
    train0 = int(5 * 60 * FS)
    scale_mean = float(np.mean(raw[:train0]))
    scale_std = float(np.std(raw[:train0])) + 1e-9
    x = (raw - scale_mean) / scale_std
    heart_period, n_peaks = estimate_heart_period_samples(raw[:train0], fs=FS)
    anchor = int(25 * 60 * FS)
    base = float(ECG_PHI)

    home_bp = ecg_bandpass(x[:anchor], heart_period, center_mean=0.0)
    home_kernel = ecg_kernel_from_bandpass(home_bp, heart_period)
    home_ara = ecg_measure_ara(home_bp, heart_period)
    if home_ara is None or not math.isfinite(home_ara):
        home_ara = 1.0
    home_position = home_ara / 2.0

    rungs = []
    for offset in range(-3, 7):
        period = float(heart_period * (base ** offset))
        if period < 6.0 or 4.0 * period > anchor:
            continue
        bp = ecg_bandpass(x[:anchor], period, center_mean=0.0)
        amp_theta = ecg_read_amp_theta(bp, period)
        if amp_theta is None:
            continue
        amp, theta = amp_theta
        kernel = ecg_kernel_from_bandpass(bp, period)
        ara = ecg_measure_ara(bp, period)
        if ara is None or not math.isfinite(ara):
            ara = home_ara
        phase = ecg_infer_phase(bp, amp, ara, kernel)
        shape_now = ecg_shape_value(phase, ara, kernel)
        split = ecg_release_fraction(ara)
        position = offset + float(ara) / 2.0
        rungs.append(
            {
                "label": f"offset{offset:+d}",
                "offset": int(offset),
                "coordinate": round_float(offset),
                "period": round_float(period),
                "period_ms": round_float(1000.0 * period / FS),
                "period_unit": "samples",
                "amp": round_float(amp),
                "energy": float(amp**2),
                "theta": round_float(theta),
                "phase": round_float(phase),
                "ara": round_float(ara),
                "release_fraction": round_float(split),
                "position": round_float(position),
                "band_value": round_float(bp[-1]),
                "shape_now": round_float(shape_now),
                "state": phase_label(phase, ara, ecg_release_fraction),
                "shape": summarize_kernel(kernel),
            }
        )

    subsystem = {
        "name": "ECG_16265_CH0",
        "role": "raw voltage observable",
        "anchor": {
            "index": int(anchor),
            "seconds": round_float(anchor / FS),
            "value_raw_adc": round_float(raw[anchor - 1]),
            "value_z": round_float(x[anchor - 1]),
        },
        "base": round_float(base),
        "home_period": round_float(heart_period),
        "home_period_ms": round_float(1000.0 * heart_period / FS),
        "home_period_unit": "samples",
        "home_coordinate": 0.0,
        "home_k_nearest": 0,
        "home_ara": round_float(home_ara),
        "home_position": round_float(home_position),
        "mean_to_anchor": round_float(np.mean(x[:anchor])),
        "std_to_anchor": round_float(np.std(x[:anchor])),
        "home_shape": summarize_kernel(home_kernel),
        "rungs": rungs,
        "source": str(dat_path),
        "header": str(hea_path),
        "fs": FS,
        "first_train_r_peaks": int(n_peaks),
        "scale_mean_raw": round_float(scale_mean),
        "scale_std_raw": round_float(scale_std),
    }
    return finalize_subsystem(subsystem, home_position)


def top_for_pairing(subsystem, n=7):
    return sorted(subsystem.get("rungs", []), key=lambda r: r.get("occupancy", 0.0), reverse=True)[:n]


def coupling_record(left_name, left, right_name, right):
    p_gap = phase_gap(left["phase"], right["phase"])
    phase_alignment = math.cos(2.0 * math.pi * p_gap)
    energy_product = math.sqrt(max(left.get("occupancy", 0.0), 0.0) * max(right.get("occupancy", 0.0), 0.0))
    distance = abs(float(left["position"]) - float(right["position"]))
    proximity = 2.0 ** (-distance)
    support = energy_product * proximity * max(0.0, (1.0 + phase_alignment) / 2.0)
    opposition = energy_product * proximity * max(0.0, (1.0 - phase_alignment) / 2.0)
    path_score = energy_product * proximity * (0.35 + 0.65 * abs(phase_alignment))

    if phase_alignment < -0.55:
        kind = "mirror_or_destructive_candidate"
    elif 0.18 <= p_gap <= 0.32:
        kind = "handoff_candidate"
    elif phase_alignment > 0.55 and abs(left["coordinate"] - right["coordinate"]) >= 0.75:
        kind = "overflow_candidate"
    elif phase_alignment > 0.55:
        kind = "coherent_candidate"
    else:
        kind = "loose_candidate"

    return {
        "left_subsystem": left_name,
        "left_rung": left["label"],
        "right_subsystem": right_name,
        "right_rung": right["label"],
        "kind": kind,
        "distance": round_float(distance),
        "scale_gap": round_float(abs(float(left["coordinate"]) - float(right["coordinate"]))),
        "ara_gap": round_float(abs(float(left["ara"]) - float(right["ara"]))),
        "phase_gap": round_float(p_gap),
        "phase_alignment": round_float(phase_alignment),
        "energy_product": round_float(energy_product),
        "support_score": round_float(support),
        "opposition_score": round_float(opposition),
        "path_score": round_float(path_score),
    }


def within_couplings(subsystem):
    records = []
    for left, right in combinations(top_for_pairing(subsystem, n=8), 2):
        records.append(coupling_record(subsystem["name"], left, subsystem["name"], right))
    return sorted(records, key=lambda r: r["path_score"] or 0.0, reverse=True)[:10]


def cross_couplings(subsystems):
    records = []
    for left_sub, right_sub in combinations(subsystems, 2):
        for left in top_for_pairing(left_sub):
            for right in top_for_pairing(right_sub):
                records.append(coupling_record(left_sub["name"], left, right_sub["name"], right))
    records = sorted(records, key=lambda r: r["path_score"] or 0.0, reverse=True)
    return records[:18]


def vertical_ara_matches(subsystems):
    records = []
    for left_sub, right_sub in combinations(subsystems, 2):
        for left in top_for_pairing(left_sub, n=9):
            for right in top_for_pairing(right_sub, n=9):
                rec = coupling_record(left_sub["name"], left, right_sub["name"], right)
                rec["vertical_match_score"] = round_float(
                    math.sqrt(max(left.get("occupancy", 0.0), 0.0) * max(right.get("occupancy", 0.0), 0.0))
                    / (1.0 + float(rec["ara_gap"]))
                )
                records.append(rec)
    records = sorted(records, key=lambda r: r["vertical_match_score"] or 0.0, reverse=True)
    return records[:12]


def subsystem_distances(subsystems):
    records = []
    for left, right in combinations(subsystems, 2):
        lp = finite(left["center"].get("position"), 0.0)
        rp = finite(right["center"].get("position"), 0.0)
        la = finite(left["center"].get("ara"), 0.0)
        ra = finite(right["center"].get("ara"), 0.0)
        lg = finite(left["center"].get("coordinate"), 0.0)
        rg = finite(right["center"].get("coordinate"), 0.0)
        lp_phase = left["center"].get("phase")
        rp_phase = right["center"].get("phase")
        records.append(
            {
                "left": left["name"],
                "right": right["name"],
                "center_distance": round_float(abs(lp - rp)),
                "center_scale_gap": round_float(abs(lg - rg)),
                "center_ara_gap": round_float(abs(la - ra)),
                "center_phase_gap": round_float(phase_gap(lp_phase, rp_phase))
                if lp_phase is not None and rp_phase is not None
                else None,
            }
        )
    return records


def assemble_system(name, family, measurement, subsystems, notes):
    return {
        "name": name,
        "family": family,
        "measurement": measurement,
        "notes": notes,
        "subsystems": subsystems,
        "within_subsystem_couplings": {s["name"]: within_couplings(s) for s in subsystems},
        "subsystem_distances": subsystem_distances(subsystems),
        "cross_subsystem_couplings": cross_couplings(subsystems),
        "vertical_ara_matches": vertical_ara_matches(subsystems),
    }


def build_enso_system():
    frame = load_enso_frame()
    dates = [d.strftime("%Y-%m-%d") for d in frame.index]
    anchor = len(frame)
    home_period = 47.0
    base = 2.0
    subsystems = [
        extract_power_subsystem(
            "NINO",
            "target ocean temperature anomaly",
            frame["NINO"].values,
            dates,
            anchor,
            home_period,
            base,
            "months",
        ),
        extract_power_subsystem(
            "SOI",
            "atmospheric pressure mirror/feeder",
            frame["SOI"].values,
            dates,
            anchor,
            home_period,
            base,
            "months",
        ),
        extract_power_subsystem(
            "PDO",
            "basin-scale ocean feeder",
            frame["PDO"].values,
            dates,
            anchor,
            home_period,
            base,
            "months",
        ),
    ]
    return assemble_system(
        "ENSO",
        "climate coupled oscillator",
        {
            "unit": "monthly index values",
            "anchor_date": dates[-1],
            "start_date": dates[0],
            "samples": int(len(frame)),
            "home_period_months": home_period,
            "substrate_base": base,
            "scale_interpretation": "positions are log_base(period) + ARA/2",
        },
        subsystems,
        [
            "Uses common NINO/SOI/PDO monthly overlap only.",
            "Base 2.0 is selected because recent ENSO tests behaved like a near-resonant two-state substrate.",
        ],
    )


def build_solar_system():
    series = load_solar_series()
    data = series.values.astype(float)
    dates = [d.strftime("%Y-%m-%d") for d in series.index]
    anchor = len(data)
    home_period = 132.0
    anchors = np.linspace(max(int(4 * home_period), anchor - 900), anchor - 1, 45).astype(int)
    sys_ara, sys_ara_std = estimate_system_ara(data, home_period, anchors)
    base = safe_base(sys_ara)
    subsystem = extract_power_subsystem(
        "SUNSPOT",
        "solar activity observable",
        data,
        dates,
        anchor,
        home_period,
        base,
        "months",
        max_rungs=28,
    )
    return assemble_system(
        "Solar",
        "solar magnetic cycle",
        {
            "unit": "monthly mean sunspot number",
            "anchor_date": dates[-1],
            "start_date": dates[0],
            "samples": int(len(data)),
            "home_period_months": home_period,
            "substrate_base": round_float(base),
            "system_ara_mean_for_base": round_float(sys_ara),
            "system_ara_std": round_float(sys_ara_std),
            "scale_interpretation": "positions are log_base(period) + ARA/2",
        },
        [subsystem],
        [
            "Uses the current measured solar home ARA as the substrate base.",
            "Single-subsystem output still reports within-rung geometry, but cross-subsystem distances are empty.",
        ],
    )


def build_ecg_system():
    subsystem = extract_ecg_subsystem()
    return assemble_system(
        "Raw MIT ECG",
        "physiological oscillator",
        {
            "unit": "standardized raw ADC voltage",
            "record": "16265",
            "channel": 0,
            "samples": int(30 * 60 * FS),
            "anchor_seconds": subsystem["anchor"]["seconds"],
            "home_period_samples": subsystem["home_period"],
            "home_period_ms": subsystem["home_period_ms"],
            "substrate_base": round_float(ECG_PHI),
            "scale_interpretation": "positions are home-relative offset + ARA/2",
        },
        [subsystem],
        [
            "Raw ECG is mapped around the measured heartbeat period, not around absolute phi powers.",
            "This map shows why simple mean/envelope tracking is insufficient for the PQRST waveform: the high-frequency offsets carry real occupancy.",
        ],
    )


def build_all():
    started = time.time()
    systems = {
        "ENSO": build_enso_system(),
        "Solar": build_solar_system(),
        "Raw MIT ECG": build_ecg_system(),
    }
    return {
        "date": "2026-05-21",
        "method": "ARA state geometry extractor v0",
        "strict_causal_note": "Each anchor state is read from data up to the anchor only. This file does not score forecasts.",
        "elapsed_seconds": round_float(time.time() - started, 3),
        "systems": systems,
    }


def print_summary(data):
    print("ARA state geometry v0")
    print("=" * 92)
    for name, system in data["systems"].items():
        measurement = system["measurement"]
        print(f"\n{name}: {system['family']}")
        print(f"  anchor: {measurement.get('anchor_date') or measurement.get('anchor_seconds')}  base={measurement.get('substrate_base')}")
        for subsystem in system["subsystems"]:
            center = subsystem["center"]
            print(
                f"  {subsystem['name']:14s} center_pos={center['position']:.3f} "
                f"center_ara={center['ara']:.3f} total_energy={center['total_energy']:.3f}"
            )
            for rung in subsystem["top_rungs"][:3]:
                print(
                    f"    {rung['label']:>8s} P={rung['period']:.2f} "
                    f"ARA={rung['ara']:.3f} pos={rung['position']:.3f} "
                    f"occ={rung['occupancy']:.3f} {rung['state']}"
                )
        if system["subsystem_distances"]:
            print("  subsystem center distances:")
            for rec in system["subsystem_distances"]:
                print(
                    f"    {rec['left']} <-> {rec['right']}: "
                    f"distance={rec['center_distance']:.3f}, ara_gap={rec['center_ara_gap']:.3f}"
                )
        if system["cross_subsystem_couplings"]:
            best = system["cross_subsystem_couplings"][0]
            print(
                "  strongest cross candidate: "
                f"{best['left_subsystem']} {best['left_rung']} <-> "
                f"{best['right_subsystem']} {best['right_rung']} "
                f"{best['kind']} score={best['path_score']:.4f}"
            )


def main():
    data = build_all()
    out_path = HERE / "ara_state_geometry_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_STATE_GEOMETRY = ")
        json.dump(clean_for_json(data), f, indent=2, allow_nan=False)
        f.write(";\n")
    print_summary(data)
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    main()
