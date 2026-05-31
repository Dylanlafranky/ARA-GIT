#!/usr/bin/env python3
"""
Does the next rung = the MIX of the two rungs below it?  (Dylan, 2026-05-30)

Mechanism: two consecutive phi-rungs, periods r and r*phi, multiplied, generate a
difference-frequency component whose period is r*phi^2 EXACTLY -- the next-but-one rung.
  1/r - 1/(r*phi) = (1 - 1/phi)/r = (1/phi^2)/r  ->  period r*phi^2.
So if a system literally builds its slow wave by mixing its two faster waves, the PRODUCT
of the two fast bandpassed rungs, re-filtered at the slow rung, should reconstruct the real
slow rung.

Two readouts per system:
  RECON  = peak cross-correlation of (generated slow) vs (actual slow).   higher = cleaner mix.
  LAG    = the delay (fraction of the slow period) at that peak.            larger = more friction.

Dylan's sharper prediction: clean + on-time near phi (golden hand-off);
lagged + smeared at ARA~1.0 (balance point has temporal friction).

Descriptive co-structure test (zero-phase filtering, NOT a forecast). Phase-randomized
surrogate null tells us if the mix-coupling beats a spectrum-matched control.
All data real/public (same sources as rent_vs_ara_test.py).
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfiltfilt, correlate, correlation_lags
import phi_rung_entropy_decay_test as E
import rent_vs_ara_test as R

PHI = E.PHI
HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(7)

# ARA measured earlier (rent_vs_ara_test.py), for the lag-vs-ARA comparison
ARA = {"ENSO": 0.905, "Solar": 1.091, "EEG (brain)": 1.000,
       "ECG (heart)": 1.200, "BP (vascular)": 1.556, "Resp (lung)": 1.667}


def norm(a):
    a = np.asarray(a, float); a = a - a.mean()
    s = a.std()
    return a / s if s > 0 else a


def bp(x, period, ratio=1.3):
    lo = 1.0 / (period * ratio)
    hi = min(1.0 / (period / ratio), 0.49)
    sos = butter(3, [lo, hi], btype="band", fs=1.0, output="sos")
    return sosfiltfilt(sos, x)


def phase_rand(x):
    X = np.fft.rfft(x); mag = np.abs(X); ph = np.angle(X)
    rp = rng.uniform(-np.pi, np.pi, len(ph)); rp[0] = ph[0]
    if len(x) % 2 == 0:
        rp[-1] = ph[-1]
    return np.fft.irfft(mag * np.exp(1j * rp), n=len(x))


def generated_slow(sig, r1, r2, r3):
    """slow component built by MIXING the two faster rungs."""
    mix = bp(sig, r1) * bp(sig, r2)
    return bp(mix, r3)


def peak_corr_lag(a, b, maxlag):
    """max positive corr of (b vs a) within +-maxlag.  lag>0 => b lags a."""
    a = norm(a); b = norm(b)
    c = correlate(b, a, mode="full") / len(a)
    lags = correlation_lags(len(b), len(a), mode="full")
    m = np.abs(lags) <= maxlag
    cc = c[m]; ll = lags[m]
    i = int(np.argmax(cc))
    return float(cc[i]), int(ll[i])


def run(name, x, P0):
    x = norm(x)
    r1, r2, r3 = P0, P0 * PHI, P0 * PHI**2
    if len(x) < 6 * r3:
        print(f"  {name:16s} too short for slow rung r3={r3:.0f} (need {6*r3:.0f}, have {len(x)})")
        return None
    gen = generated_slow(x, r1, r2, r3)
    act = bp(x, r3)
    maxlag = int(round(r3))
    corr, lag = peak_corr_lag(gen, act, maxlag)
    null = []
    for _ in range(40):
        xs = phase_rand(x)
        g = generated_slow(xs, r1, r2, r3)
        a = bp(xs, r3)
        c, _ = peak_corr_lag(g, a, maxlag)
        null.append(c)
    null = np.array(null)
    z = float((corr - null.mean()) / (null.std() + 1e-9))
    lag_frac = lag / r3
    row = {"system": name, "ARA": ARA.get(name), "P0": float(P0),
           "r3_slow_period": float(r3), "recon_corr": corr,
           "lag_samples": lag, "lag_frac_of_slow": float(lag_frac),
           "null_mean": float(null.mean()), "z_vs_null": z}
    print(f"  {name:16s} ARA={ARA.get(name):.2f}  recon={corr:+.3f}  "
          f"lag={lag_frac:+.3f}slow  z={z:+.1f}")
    return row


def main():
    print("=" * 70); print("NEXT RUNG = MIX OF TWO BELOW  (recon + lag vs ARA)"); print("=" * 70)
    rows = []
    xe, _, _ = E.load_enso()
    xe = np.asarray(xe, float); xe = xe[np.isfinite(xe)]
    rows.append(run("ENSO", xe, R.dominant_period(xe, 24, 96)))

    xs, _, _ = E.load_solar()
    xs = np.asarray(xs, float); xs = xs[np.isfinite(xs)]
    rows.append(run("Solar", xs, R.dominant_period(xs, 90, 160)))

    sig = np.load(HERE / "slp01a_sig.npy").astype(float)
    names = json.loads((HERE / "slp01a_names.json").read_text())
    chan = {n: i for i, n in enumerate(names)}
    fs = 250.0
    N = 40000  # ~160 s, plenty of slow cycles, keeps it fast
    def col(c):
        v = sig[:, chan[c]].astype(float); v = v[np.isfinite(v)]
        return v[:N]
    rows.append(run("ECG (heart)", col("ECG"), R.dominant_period(col("ECG"), int(0.4*fs), int(1.5*fs))))
    rows.append(run("BP (vascular)", col("BP"), R.dominant_period(col("BP"), int(0.4*fs), int(1.5*fs))))
    rows.append(run("EEG (brain)", col("EEG (C4-A1)"), R.dominant_period(col("EEG (C4-A1)"), int(fs/12), int(fs/4))))
    rows.append(run("Resp (lung)", col("Resp (sum)"), R.dominant_period(col("Resp (sum)"), int(2*fs), int(8*fs))))

    rows = [r for r in rows if r]
    print("\n" + "=" * 70); print("RESULT"); print("=" * 70)
    # keep only mixes that beat the null (real coupling)
    real = [r for r in rows if r["z_vs_null"] >= 2.0]
    print(f"  systems with mix-coupling above null (z>=2): {len(real)}/{len(rows)}")
    if len(real) >= 3:
        ara = np.array([r["ARA"] for r in real])
        recon = np.array([r["recon_corr"] for r in real])
        lagf = np.array([np.abs(r["lag_frac_of_slow"]) for r in real])
        c_recon = float(np.corrcoef(ara, recon)[0, 1])
        c_lag = float(np.corrcoef(ara, lagf)[0, 1])
        print(f"  corr(ARA, recon_quality) = {c_recon:+.3f}   (predict POSITIVE: cleaner near phi)")
        print(f"  corr(ARA, |lag|)         = {c_lag:+.3f}   (predict NEGATIVE: less lag near phi)")
        out = {"rows": rows, "corr_ARA_recon": c_recon, "corr_ARA_lag": c_lag, "phi": PHI}
    else:
        out = {"rows": rows, "note": "too few above-null systems"}
    (HERE / "blend_next_rung_result.json").write_text(json.dumps(out, indent=2))
    print("\n  per-system:")
    for r in rows:
        print(f"    {r['system']:16s} ARA={r['ARA']:.2f}  recon={r['recon_corr']:+.3f}  "
              f"|lag|={abs(r['lag_frac_of_slow']):.3f}  z={r['z_vs_null']:+.1f}")
    print("\nSaved blend_next_rung_result.json")


if __name__ == "__main__":
    main()
