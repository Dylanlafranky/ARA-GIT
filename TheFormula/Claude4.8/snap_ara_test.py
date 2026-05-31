#!/usr/bin/env python3
"""
P1 - SNAP-FAITHFUL ARA on RAW data.   (Dylan theory, 2026-05-30)
Snaps are the leakiest; the heart's QRS is a deep snap (slow build, fast dump, ARA<<1).
The smoothed-cycle ruler read ECG ~1.2 because the bandpass smears the spike. RAW keeps it.
Method (no filter on the timing): detect peaks on RAW; troughs = RAW minima between peaks;
build = trough_before->peak, release = peak->trough_after; ARA = median(release)/median(build).
Data: slp01a 250 Hz + ENSO/Solar monthly. All real/public.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
import rent_vs_ara_test as R
import phi_rung_entropy_decay_test as E

HERE = Path(__file__).resolve().parent


def snap_ara_raw(x, approx_period, prom_frac=0.3):
    x = np.asarray(x, float)
    dist = max(3, int(approx_period * 0.55))
    prom = prom_frac * np.std(x)
    pks, _ = find_peaks(x, distance=dist, prominence=prom)
    if len(pks) < 8:
        return None
    builds, releases = [], []
    for i in range(1, len(pks) - 1):
        a, p, b = pks[i - 1], pks[i], pks[i + 1]
        tb = a + int(np.argmin(x[a:p + 1]))
        ta = p + int(np.argmin(x[p:b + 1]))
        build = p - tb
        release = ta - p
        if build > 0 and release > 0:
            builds.append(build); releases.append(release)
    builds = np.array(builds, float); releases = np.array(releases, float)
    ab = releases / builds
    return {"n_beats": int(len(builds)), "ara_median": float(np.median(ab)),
            "ara_iqr": [float(np.percentile(ab, 25)), float(np.percentile(ab, 75))],
            "build_med": float(np.median(builds)), "release_med": float(np.median(releases))}


def measure(name, x, approx):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    raw = snap_ara_raw(x, approx)
    xd, per_d, fac = R.decimate_to(x, approx)
    sm, sm_n = R.ara_waveform(xd, per_d)
    if raw is None:
        print("  %-16s raw: too few cycles" % name); return None
    print("  %-16s smoothed=%.3f   RAW snap-ARA=%.3f   (n=%d, build/rel=%.0f/%.0f)" %
          (name, sm, raw["ara_median"], raw["n_beats"], raw["build_med"], raw["release_med"]))
    return {"system": name, "smoothed_ARA": float(sm), "raw_snap_ARA": raw["ara_median"],
            "raw_iqr": raw["ara_iqr"], "n_beats": raw["n_beats"],
            "build_med": raw["build_med"], "release_med": raw["release_med"]}


def main():
    print("=" * 70); print("P1  SNAP-FAITHFUL ARA (raw) vs SMOOTHED ARA  -- full axis"); print("=" * 70)
    rows = []
    xe, _, _ = E.load_enso(); xe = np.asarray(xe, float); xe = xe[np.isfinite(xe)]
    rows.append(measure("ENSO", xe, R.dominant_period(xe, 24, 96)))
    xs, _, _ = E.load_solar(); xs = np.asarray(xs, float); xs = xs[np.isfinite(xs)]
    rows.append(measure("Solar", xs, R.dominant_period(xs, 90, 160)))
    sig = np.load(HERE / "slp01a_sig.npy").astype(float)
    names = json.loads((HERE / "slp01a_names.json").read_text())
    chan = {n: i for i, n in enumerate(names)}; fs = 250.0
    def col(c):
        v = sig[:, chan[c]].astype(float); v = v[np.isfinite(v)]; return v[:120000]
    rows.append(measure("ECG (heart)", col("ECG"), R.dominant_period(col("ECG"), int(0.4*fs), int(1.5*fs))))
    rows.append(measure("BP (vascular)", col("BP"), R.dominant_period(col("BP"), int(0.4*fs), int(1.5*fs))))
    rows.append(measure("EEG (brain)", col("EEG (C4-A1)"), R.dominant_period(col("EEG (C4-A1)"), int(fs/12), int(fs/4))))
    rows.append(measure("Resp (lung)", col("Resp (sum)"), R.dominant_period(col("Resp (sum)"), int(2*fs), int(8*fs))))
    rows = [r for r in rows if r]
    print("\n" + "=" * 70); print("CORRECTED AXIS (raw snap-ARA), leakiest-first"); print("=" * 70)
    for r in sorted(rows, key=lambda d: d["raw_snap_ARA"]):
        print("    %-16s raw snap-ARA=%.3f   (smoothed said %.2f)" %
              (r["system"], r["raw_snap_ARA"], r["smoothed_ARA"]))
    (HERE / "snap_ara_result.json").write_text(json.dumps({"rows": rows, "fs_slp": fs}, indent=2))
    print("\nSaved snap_ara_result.json")


if __name__ == "__main__":
    main()
