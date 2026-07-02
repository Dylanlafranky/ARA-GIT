"""
Element 3 - coupling rules: is arm-2 the shared CARRIER of the 1-3 coupling?

Phase-locking value (PLV) for each pair, mean phase difference, instantaneous-
frequency steadiness per arm, and the key test: partial correlation of arm-1 and
arm-3 with arm-2 held fixed. If the raw positive corr(1,3) flips negative under
the partial, arm-2 ACCOUNTS FOR (carries) the apparent 1-3 co-movement, and the
two ends are intrinsically anti-phase once the shared carrier is removed.

FRAMEWORK NOTE (do not call partial correlation mediation): a partial-corr
sign-flip identifies a COMMON CARRIER, not a proven causal mediator. Here the
carrier is the shared common mode (one ~1.333 s clock all three arms ride), so
"the clock" is the COMMON MODE; arm-2 is its carrier/projection, not itself the
timekeeper (see the null below: arm-2 is NOT the steadiest oscillator). Arm-2's
physical betweenness is a separate mechanistic prior, not shown by this statistic.

NOTE: this is a DESCRIPTIVE coupling analysis (not a forecast), so a zero-phase
filtfilt + Hilbert on the full series is acceptable here. Do NOT reuse this
pattern in the forecasting scripts (06, 07) - those must stay strictly causal.

Expected: PLV 0.94-0.99 all pairs; partial corr(1,3|2) flips negative in 2/3
runs; arm-2 NOT the steadiest oscillator (run-1 artifact, does not replicate).

Run:  python 04_coupling_partial_corr.py
"""
import numpy as np
from scipy.signal import hilbert, butter, filtfilt
from pendulum_common import load_triple, rest_centered, wrap, RUNS


def analyze(run):
    t, th_raw, vel, fs = load_triple(run, decimate=10)
    th = rest_centered(th_raw)
    b, a = butter(2, [0.4, 1.3], btype="band", fs=fs)
    ph = {i: np.angle(hilbert(filtfilt(b, a, th[i] - th[i].mean()))) for i in (1, 2, 3)}
    print(f"== {run} ==")
    print("  PLV and mean phase-diff:")
    for x, y in [(1, 3), (1, 2), (2, 3)]:
        d = wrap(ph[x] - ph[y])
        plv = np.abs(np.mean(np.exp(1j * d)))
        md = np.angle(np.mean(np.exp(1j * d))) * 180 / np.pi
        print(f"    arm{x}-arm{y}:  PLV={plv:.3f}   mean phase diff={md:+6.0f} deg")
    print("  clock quality (inst-freq std; lower = cleaner clock):")
    for i in (1, 2, 3):
        insf = np.diff(np.unwrap(ph[i])) * fs / (2 * np.pi)
        print(f"    arm{i}: mean f={np.mean(insf):.3f} Hz  std={np.std(insf):.3f}")
    A = np.vstack([th[1], th[2], th[3]])
    C = np.corrcoef(A)
    partial13 = (C[0, 2] - C[0, 1] * C[2, 1]) / np.sqrt((1 - C[0, 1] ** 2) * (1 - C[2, 1] ** 2))
    print(f"  corr(arm1,arm3)       = {C[0, 2]:+.3f}")
    print(f"  partial corr(1,3 | 2) = {partial13:+.3f}   (flip toward/below 0 = arm2 is the shared CARRIER, not a proven mediator)\n")


def main():
    for run in RUNS:
        analyze(run)


if __name__ == "__main__":
    main()
