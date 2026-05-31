#!/usr/bin/env python3
"""
Does a system's per-phi-rung information RENT track its ARA?

Prediction under test (Dylan, 2026-05-30): rent-per-rung ~ 2 - ARA.
 - ARA = phi (golden engine)  -> rent = 2 - phi = 1/phi^2 = 0.382  ("most effective")
 - ARA -> 2  (pure harmonic / Sun flywheel) -> rent -> 0   (retains everything)
 - ARA -> 1  (balance point) -> rent -> 1   (sheds the most)

Two INDEPENDENT measurements per real system (no shared computation -> not circular):
  ARA   = single-cycle waveform asymmetry  (release/build of the dominant cycle;
          bycycle discipline: narrowband locates cycles, rise/decay timed on raw).
  RENT  = 1 - geomean(per-phi-rung retention of auto-mutual-information).
          (entropy leg from phi_rung_entropy_decay_test.py)

Systems (all real, public):
  ENSO Nino3.4 monthly (NOAA) ; SILSO sunspots monthly ;
  slpdb slp01a (250 Hz): ECG(heart), BP(vascular), EEG C4-A1(brain), Resp(lung).
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfiltfilt
import phi_rung_entropy_decay_test as E   # reuse MI machinery

PHI = E.PHI
HERE = Path(__file__).resolve().parent


def dominant_period(x, pmin, pmax):
    """Dominant cycle period (samples) from FFT peak within [pmin,pmax] samples."""
    x = np.asarray(x, float); x = x - x.mean()
    n = len(x)
    f = np.fft.rfftfreq(n, d=1.0)
    P = np.abs(np.fft.rfft(x * np.hanning(n)))**2
    per = np.full_like(f, np.inf)
    per[1:] = 1.0 / f[1:]
    band = (per >= pmin) & (per <= pmax)
    if not band.any():
        return None
    idx = np.argmax(np.where(band, P, 0))
    return float(per[idx])


def ara_waveform(x, period):
    """ARA = release/build of the dominant cycle.
    build = rising phase (trough->peak), release = falling phase (peak->trough).
    Cycles located on a narrowband-filtered copy; extrema refined on raw."""
    x = np.asarray(x, float)
    fs = 1.0
    lo = 1.0 / (period * 1.5); hi = 1.0 / (period / 1.5)
    hi = min(hi, 0.49)
    sos = butter(3, [lo, hi], btype="band", fs=fs, output="sos")
    xf = sosfiltfilt(sos, x)
    # cycle = trough -> trough.  Troughs = local minima of filtered signal.
    dxf = np.diff(xf)
    troughs = np.where((dxf[:-1] < 0) & (dxf[1:] >= 0))[0] + 1
    builds, releases = [], []
    for i in range(len(troughs) - 1):
        a, b = troughs[i], troughs[i+1]
        if b - a < 4:
            continue
        seg = x[a:b]
        pk = a + int(np.argmax(seg))   # peak refined on raw
        build = pk - a                 # trough -> peak  (accumulation)
        release = b - pk               # peak -> next trough (release)
        if build > 0 and release > 0:
            builds.append(build); releases.append(release)
    if len(builds) < 5:
        return None, len(builds)
    ara = float(np.median(releases) / np.median(builds))
    return ara, len(builds)


def decimate_to(x, period, target=24):
    """Decimate so dominant period ~ target samples; cap length for MI speed."""
    factor = max(1, int(round(period / target)))
    xd = x[::factor]
    if len(xd) > 8000:
        xd = xd[:8000]
    return xd, period / factor, factor


def rent_of(x, period_samples):
    """1 - geomean per-phi-rung retention of auto-MI. Anchor at ~1 cycle."""
    n = len(x)
    h0 = max(2, int(round(period_samples)))
    max_h = min(n // 3, int(h0 * PHI**6))
    if max_h <= h0 * 1.5:
        max_h = min(n // 3, h0 * 8)
    lags = np.unique(np.round(np.geomspace(1, max_h, 36)).astype(int))
    lags = lags[lags >= 1]
    ami, floor = E.ami_curve(x, lags, B=8, n_shuffle=15)
    ami_clean = np.maximum(ami - floor, 0.0)
    rr = E.rung_ratios(h0, None, ami_clean, lags)
    ret = rr["geomean_retention"]
    fit = E.fit_decay(lags[(lags >= h0) & (ami > floor)],
                      ami_clean[(lags >= h0) & (ami > floor)])
    return ret, rr, fit


def run_system(name, x, pmin, pmax, unit):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    per = dominant_period(x, pmin, pmax)
    if per is None:
        print(f"  {name}: no dominant period in band"); return None
    xd, per_d, fac = decimate_to(x, per)
    ara, ncyc = ara_waveform(xd, per_d)
    ret, rr, fit = rent_of(xd, per_d)
    rent = (1.0 - ret) if ret else None
    row = {"system": name, "unit": unit, "N_raw": int(len(x)),
           "dominant_period_raw": per, "decimate_factor": fac,
           "ARA_waveform": ara, "cycles_used": ncyc,
           "retention_per_rung": ret, "rent_per_rung": rent,
           "ami_power_law_R2": fit["power_law_R2"] if fit else None,
           "ami_better_model": fit["better_model"] if fit else None}
    pa = f"{ara:.3f}" if ara else "n/a"
    pr = f"{rent:.3f}" if rent else "n/a"
    r2 = f"{row['ami_power_law_R2']:.2f}" if row['ami_power_law_R2'] is not None else "n/a"
    print(f"  {name:16s} period~{per:8.1f}{unit}  ARA={pa:>6}  "
          f"rent={pr:>6}  2-ARA={2-ara:.3f}  amiR2={r2}" if ara else
          f"  {name:16s} ARA n/a")
    return row


def main():
    print("="*70); print("RENT-PER-RUNG vs ARA"); print("="*70)
    rows = []
    # ENSO monthly: dominant quasi-period 30-72 mo
    xe,_,_ = E.load_enso();  rows.append(run_system("ENSO", xe, 24, 96, "mo"))
    # Solar monthly: 11yr cycle ~ 90-160 mo
    xs,_,_ = E.load_solar(); rows.append(run_system("Solar", xs, 90, 160, "mo"))
    # slpdb 250 Hz signals
    sig = np.load(HERE/"slp01a_sig.npy").astype(float)
    names = json.loads((HERE/"slp01a_names.json").read_text())
    chan = {n:i for i,n in enumerate(names)}
    fs = 250.0
    rows.append(run_system("ECG (heart)", sig[:,chan['ECG']],
                           int(0.4*fs), int(1.5*fs), "smp"))      # ~0.4-1.5 s beat
    rows.append(run_system("BP (vascular)", sig[:,chan['BP']],
                           int(0.4*fs), int(1.5*fs), "smp"))
    rows.append(run_system("EEG (brain)", sig[:,chan['EEG (C4-A1)']],
                           int(fs/12), int(fs/4), "smp"))          # 4-12 Hz
    rows.append(run_system("Resp (lung)", sig[:,chan['Resp (sum)']],
                           int(2*fs), int(8*fs), "smp"))           # 2-8 s breath

    rows = [r for r in rows if r and r["ARA_waveform"] and r["rent_per_rung"]]
    ara = np.array([r["ARA_waveform"] for r in rows])
    rent = np.array([r["rent_per_rung"] for r in rows])
    pred = 2.0 - ara

    print("\n"+"="*70); print("RESULT"); print("="*70)
    if len(rows) >= 3:
        c = np.corrcoef(ara, rent)[0,1]
        cp = np.corrcoef(pred, rent)[0,1]   # equals -corr(ara,rent)
        mae_law = float(np.mean(np.abs(rent - pred)))
        print(f"  systems: {len(rows)}")
        print(f"  corr(ARA, rent)       = {c:+.3f}   (prediction: NEGATIVE)")
        print(f"  corr(2-ARA, rent)     = {cp:+.3f}   (prediction: POSITIVE)")
        print(f"  MAE of law rent=2-ARA = {mae_law:.3f}")
        # slope
        A = np.vstack([np.ones_like(ara), ara]).T
        sl,*_ = np.linalg.lstsq(A, rent, rcond=None)
        print(f"  fit rent = {sl[0]:.3f} + {sl[1]:.3f}*ARA")
        out = {"corr_ARA_rent": float(c), "corr_2minusARA_rent": float(cp),
               "MAE_law_2minusARA": mae_law, "fit_intercept": float(sl[0]),
               "fit_slope": float(sl[1]), "rows": rows,
               "phi": PHI, "rent_at_phi_law": 2-PHI}
        (HERE/"rent_vs_ara_result.json").write_text(json.dumps(out, indent=2))
        print("\n  per-system (ARA, rent, 2-ARA):")
        for r in rows:
            print(f"    {r['system']:16s} ARA={r['ARA_waveform']:.3f}  "
                  f"rent={r['rent_per_rung']:.3f}  2-ARA={2-r['ARA_waveform']:.3f}")
        print("\nSaved rent_vs_ara_result.json")
    else:
        print("  too few systems")

if __name__ == "__main__":
    main()
