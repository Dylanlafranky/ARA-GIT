"""
Two-band ("green & brown") analysis + the amplitude meta-wave
=============================================================

This reproduces, from the NINO 3.4 record alone, the three findings about the two
interannual bands Dylan flagged as a wave-above-ENSO:

  GREEN band  = quasi-biennial (QB), ~28 months
  BROWN band  = low-frequency (LF), ~48-67 months

1. SPECTRUM: the interannual power splits into these two bands of comparable power.
2. COUPLING: a segmented bispectrum shows the two bands are PHASE-coupled (not two
   independent neighbours) -- bicoherence ~0.34 vs a ~0.06 noise floor, with a
   combination tone near 15-20 months.
3. AMPLITUDE META-WAVE: the Hilbert envelope of the band-passed signal is itself a
   coherent wave, ~2x slower than the signal (de-correlation ~14 mo vs ~7), with
   spectral peaks at ~5.2 yr (the beat of the two bands), ~7.8 yr, and ~12 yr.
   (Dylan called this; an earlier rolling-std proxy missed it, the Hilbert envelope found it.)

Why it matters: the two bands are a genuine coupled pair, and their beat is a real
deterministic amplitude modulation. BUT the skill-recurrence it produces is
NON-STATIONARY (the QB period wanders 2-2.5 yr), so it is describable, not bankable
for forecasting past the ~6-month horizon. See README.md / SESSION_LOG.md.

Run:  python3 two_band_metawave_analysis.py /path/to/nino34_long_anom.csv
Outputs: prints a summary and writes results/two_band_metawave.json
"""

import os
import sys
import json
import numpy as np

try:
    from scipy.signal import hilbert
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


def load_nino(p, miss=-99.99):
    d = {}
    for ln in open(p):
        s = [x.strip() for x in ln.split(",")]
        if len(s) == 2 and s[0][:4].isdigit():
            v = float(s[1])
            if v > miss + 0.001:
                d[s[0][:7].replace("-", "")] = v
    keys = sorted(d)
    return np.array([d[k] for k in keys]), keys


def detrend(x):
    x = x - x.mean()
    return x - np.polyval(np.polyfit(np.arange(len(x)), x, 1), np.arange(len(x)))


def interannual_spectrum(x):
    N = len(x)
    P = np.abs(np.fft.rfft(x * np.hanning(N))) ** 2
    f = np.fft.rfftfreq(N, 1.0)
    per = np.where(f > 0, 1.0 / np.maximum(f, 1e-12), 0.0)
    band = (per >= 20) & (per <= 90)
    pb, Pb = per[band], P[band] / P[band].max()
    peaks = []
    for i in range(1, len(Pb) - 1):
        if Pb[i] > Pb[i - 1] and Pb[i] >= Pb[i + 1] and Pb[i] > 0.25:
            peaks.append((round(float(pb[i]), 1), round(float(Pb[i]), 3)))
    return sorted(peaks, key=lambda t: -t[1])


def bispectrum_qb_lf(x, L=256, step=96):
    win = np.hanning(L)
    segs = []
    i = 0
    while i + L <= len(x):
        segs.append(np.fft.rfft(x[i:i + L] * win))
        i += step
    segs = np.array(segs)
    nseg = len(segs)
    floor = 1.0 / nseg

    def b2(k1, k2):
        k3 = k1 + k2
        if k3 >= segs.shape[1]:
            return float("nan")
        X1, X2, X3 = segs[:, k1], segs[:, k2], segs[:, k3]
        num = np.abs(np.sum(X1 * X2 * np.conj(X3))) ** 2
        den = np.sum(np.abs(X1 * X2) ** 2) * np.sum(np.abs(X3) ** 2)
        return float(num / den) if den > 0 else float("nan")

    def k(period):
        return int(round((1.0 / period) / (1.0 / L)))

    triads = {}
    for qb in (28,):
        for lf in (42, 48, 67):
            ks = k(qb) + k(lf)
            triads[f"QB{qb}xLF{lf}"] = {
                "b2": round(b2(k(qb), k(lf)), 3),
                "sum_tone_mo": round(1.0 / (ks / L), 1),
            }
    return {"n_segments": nseg, "noise_floor": round(floor, 3),
            "sig_threshold_3xfloor": round(3 * floor, 3), "triads": triads}


def amplitude_metawave(x):
    N = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(N, 1.0)
    per = np.where(f > 0, 1.0 / np.maximum(f, 1e-12), 1e9)
    X[(per < 18) | (per > 120)] = 0
    xb = np.fft.irfft(X, N)
    if HAVE_SCIPY:
        env = np.abs(hilbert(xb))
    else:
        Xf = np.fft.fft(xb)
        Xa = np.zeros(N, complex)
        Xa[0] = Xf[0]; Xa[1:N // 2] = 2 * Xf[1:N // 2]; Xa[N // 2] = Xf[N // 2]
        env = np.abs(np.fft.ifft(Xa))
    env = env - env.mean()

    def efold(s):
        s = s - s.mean()
        ac = np.correlate(s, s, "full")[len(s) - 1:]
        ac /= ac[0]
        return int(next((i for i, v in enumerate(ac) if v < 1 / np.e), len(ac)))

    E = np.abs(np.fft.rfft(env * np.hanning(N))) ** 2
    pe = per[1:]; Ep = E[1:]
    b = (pe >= 20) & (pe <= 160)
    pb, eb = pe[b], Ep[b] / Ep[b].max()
    peaks = []
    for i in range(1, len(eb) - 1):
        if eb[i] > eb[i - 1] and eb[i] >= eb[i + 1] and eb[i] > 0.3:
            peaks.append({"period_mo": round(float(pb[i]), 1),
                          "period_yr": round(float(pb[i]) / 12, 2),
                          "rel_power": round(float(eb[i]), 2)})
    return {"envelope_decorrelation_mo": efold(env),
            "signal_decorrelation_mo": efold(x),
            "band_beat_mo": round(1 / (1 / 28 - 1 / 48)),
            "envelope_peaks": sorted(peaks, key=lambda d: -d["rel_power"])}


def main():
    csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    x, keys = load_nino(csv)
    x = detrend(x)
    out = {
        "record": {"months": len(x), "start": keys[0], "end": keys[-1]},
        "spectrum_interannual_peaks_period_mo_relpower": interannual_spectrum(x),
        "bispectrum_band_coupling": bispectrum_qb_lf(x),
        "amplitude_metawave": amplitude_metawave(x),
    }
    os.makedirs("results", exist_ok=True)
    with open("results/two_band_metawave.json", "w") as f:
        json.dump(out, f, indent=2)

    print("TWO-BAND ('green & brown') + AMPLITUDE META-WAVE\n")
    print(f"record: {out['record']['months']} months, {out['record']['start']}-{out['record']['end']}\n")
    print("1. interannual spectrum peaks (period_mo, rel_power):")
    for p, pw in out["spectrum_interannual_peaks_period_mo_relpower"]:
        tag = "GREEN/QB" if p < 38 else "BROWN/LF"
        print(f"     {p:6.1f} mo  power {pw:.2f}   [{tag}]")
    bc = out["bispectrum_band_coupling"]
    print(f"\n2. band coupling (bispectrum): {bc['n_segments']} segs, floor {bc['noise_floor']}, "
          f"sig>{bc['sig_threshold_3xfloor']}")
    for name, t in bc["triads"].items():
        sig = "coupled" if t["b2"] > bc["sig_threshold_3xfloor"] else "weak"
        print(f"     {name}: b^2={t['b2']} -> sum tone {t['sum_tone_mo']}mo  [{sig}]")
    mw = out["amplitude_metawave"]
    print(f"\n3. amplitude meta-wave (Hilbert envelope):")
    print(f"     envelope de-correlation {mw['envelope_decorrelation_mo']}mo vs signal "
          f"{mw['signal_decorrelation_mo']}mo (slower = real meta-wave)")
    print(f"     two-band beat = {mw['band_beat_mo']}mo")
    for pk in mw["envelope_peaks"]:
        print(f"     peak {pk['period_mo']}mo ({pk['period_yr']}yr) rel power {pk['rel_power']}")
    print("\nwrote results/two_band_metawave.json")


if __name__ == "__main__":
    main()
