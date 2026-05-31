"""
The R for the HEART: who informs the next heartbeat? (transfer entropy)
======================================================================
Same diagnostic we ran on ENSO (enso_info_exchange_R.py), now on the heart. The heart (RR
interval, beat-to-beat timing) is the target. Its neighbour systems are recorded on the same
clock in slp01a:
   * BP   (vascular)  -- the pressure wave the heart pushes into
   * EEG  (brain)     -- the autonomic command line
   * Resp (lung)      -- breathing, the slow modulator (RSA)

Transfer entropy TE(X->Y) at lag L (in BEATS) = how much knowing feeder X's past reduces our
surprise about the heart's NEXT RR, beyond the heart's own past. Net = TE(feeder->RR) -
TE(RR->feeder). Phase-scramble null (preserves spectrum, breaks coupling) gives a z-score.

We want to find, like with ENSO: which feeder is the MESSAGE (real info donor, leads) vs which
is the LOCK (tight phase grip but low info). Then stitch them by horizon.

Data: slp01a (250 Hz ECG/BP/EEG/Resp, PhysioNet slpdb). Real. Descriptive.
"""
import json
import numpy as np
from numpy.fft import rfft, irfft
from scipy.signal import find_peaks
import enso_info_exchange_R as R   # reuse te(), qbin(), phase_scramble(), best_te(), directed()

FS = 250.0

def per_beat_series():
    """Detect R-peaks on ECG; build per-beat RR + per-beat mean of each feeder."""
    sig = np.load("slp01a_sig.npy").astype(float)
    names = json.loads(open("slp01a_names.json").read())
    ch = {n: i for i, n in enumerate(names)}
    ecg = sig[:, ch["ECG"]]
    # R-peak detection on raw ECG
    dist = int(0.4 * FS)                       # >=0.4s apart (<=150 bpm)
    prom = 0.4 * np.std(ecg)
    pks, _ = find_peaks(ecg, distance=dist, prominence=prom)
    pks = pks[(pks > 1) & (pks < len(ecg) - 1)]
    rr = np.diff(pks) / FS * 1000.0            # RR interval in ms, one per beat-gap
    # feeder = mean of channel over each beat interval [pks[i], pks[i+1])
    feeders = {}
    for nm, col in [("BP", "BP"), ("EEG", "EEG (C4-A1)"), ("Resp", "Resp (sum)")]:
        x = sig[:, ch[col]]
        feeders[nm] = np.array([x[pks[i]:pks[i+1]].mean() for i in range(len(pks)-1)])
    # light outlier clean on RR (ectopics / detection misses)
    med = np.median(rr); good = (rr > 0.4*med) & (rr < 1.8*med)
    rr = rr[good]
    for nm in feeders: feeders[nm] = feeders[nm][good]
    return rr, feeders

def directed_heart(name, F, T, rng, lags=range(0, 13), q=5, nnull=200):
    """Like R.directed but prints heart-correct labels (beats, not mo)."""
    Lf, tf = R.best_te(F, T, lags, q)   # feeder -> heart
    Lr, tr = R.best_te(T, F, lags, q)   # heart -> feeder
    null = np.array([R.te(R.phase_scramble(F, rng), T, Lf, q) for _ in range(nnull)])
    z = (tf - null.mean()) / (null.std() + 1e-12)
    arrow = "feeder->HEART" if tf > tr else "HEART->feeder"
    print(f"   {name:6s}: TE(feeder->heart) {tf:.3f} bits @lag {Lf:+d} beats | "
          f"TE(heart->feeder) {tr:.3f} @lag {Lr:+d} | net {tf-tr:+.3f} -> {arrow}  (z {z:+.1f})")
    return name, tf, Lf, tr, Lr, z

def main():
    rr, feeders = per_beat_series()
    print("== R: INFORMATION EXCHANGE for the HEART (transfer entropy, bits) ==")
    print("   target = next RR interval; lag in BEATS; net>0 = donor, lag 0 + net<0 = downstream lock\n")
    print(f"   [RR] {len(rr)} beats, median {np.median(rr):.0f} ms\n")
    rng = np.random.default_rng(11)
    rows = []
    for nm, F in feeders.items():
        rows.append(directed_heart(nm, F, rr.copy(), rng, lags=range(0, 13), q=5, nnull=200))
    print()
    # the MESSAGE = real donor: net info flowing INTO the heart, z>2, leads (lag>0)
    donors = [r for r in rows if (r[1]-r[3]) > 0 and r[5] > 2]
    if donors:
        d = max(donors, key=lambda r: r[1]-r[3])
        print(f"MESSAGE (real info donor, leads): {d[0]}  net {d[1]-d[3]:+.3f} bits @ lag {d[2]:+d} beats (z {d[5]:+.1f}).")
    # the LOCK = tightest coupling but net flows the other way / simultaneous (lag 0)
    locks = [r for r in rows if (r[1]-r[3]) < 0 or r[2] == 0]
    if locks:
        k = max(locks, key=lambda r: r[1])   # strongest raw coupling among non-donors
        print(f"LOCK (tight grip, simultaneous/downstream): {k[0]}  net {k[1]-k[3]:+.3f} bits @ lag {k[2]:+d} beats (z {k[5]:+.1f}).")
    print("\nTransfer entropy = directed info flow. Real PhysioNet data. Descriptive diagnostic.")

if __name__ == "__main__": main()
