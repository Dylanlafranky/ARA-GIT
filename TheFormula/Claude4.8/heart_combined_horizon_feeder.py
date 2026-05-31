"""
Stitch the heart forecaster: breath (donor, short) + BP (lock, long).  Same logic as ENSO.
============================================================================================
The heart R-map (heart_info_exchange_R.py) found the SAME shape as ENSO:
   * Resp (breath) = the MESSAGE / info donor -- leads ~4 beats, net info INTO the heart
   * BP   (vascular) = the LOCK -- huge coupling but simultaneous / downstream (heart->BP)
   * EEG  (cortex) = wrong probe (the heart is run by the AUTONOMIC nervous system, not cortex)

Dylan's structural note: breath and BP don't touch the heart directly -- they feed the
NERVOUS SYSTEM, which then feeds the heart. An extra hop. So each measured channel may carry
only ~HALF its information through to the beat (the nervous system is the hidden middle node /
shadow third). We watch for that halving in the lift.

   combined(h) = +Resp  for short horizons (the message leads)
               = +BP    for long  horizons (the lock holds)

STRICTLY CAUSAL: feeders contemporaneous (known at beat t); standardize on TRAIN only; target
is a FUTURE beat; last 40% held out; correlation leads. Target = RR interval, h beats ahead.
Data: slp01a (PhysioNet slpdb, 250 Hz). Real. Descriptive.

Usage: python3 heart_combined_horizon_feeder.py
"""
import numpy as np
import heart_info_exchange_R as H   # reuse per_beat_series()

NLAG = 4            # autoregressive RR memory (beats)
TRAIN_FRAC = 0.60
HS = (1, 2, 3, 5, 8, 13)   # horizons in beats

def zfit(tr):
    m = tr.mean(0); s = tr.std(0); s[s == 0] = 1.0
    return m, s

def design(rr, feed, t0, t1):
    """rows from beat index t0..t1; cols = [RR lags, feeders..., ones]."""
    rows = []
    for t in range(t0, t1):
        r = [rr[t-k] for k in range(NLAG)]      # rr[t], rr[t-1], ...
        for f in feed: r.append(f[t])           # contemporaneous feeder(s)
        r.append(1.0)
        rows.append(r)
    return np.array(rows)

def run_config(rr, feeders, h):
    """Strict-causal: fit on train beats, predict held-out, return corr(pred, actual)."""
    n = len(rr)
    lo = NLAG; hi = n - h                        # need rr[t-NLAG+1..t] and rr[t+h]
    idx = np.arange(lo, hi)
    split = lo + int((hi - lo) * TRAIN_FRAC)
    Xtr = design(rr, feeders, lo, split)
    Xte = design(rr, feeders, split, hi)
    ytr = np.array([rr[t+h] for t in range(lo, split)])
    yte = np.array([rr[t+h] for t in range(split, hi)])
    # standardize feature cols (not the ones col) on TRAIN only
    m, s = zfit(Xtr[:, :-1])
    Xtr2 = Xtr.copy(); Xte2 = Xte.copy()
    Xtr2[:, :-1] = (Xtr[:, :-1] - m) / s
    Xte2[:, :-1] = (Xte[:, :-1] - m) / s
    beta, *_ = np.linalg.lstsq(Xtr2, ytr, rcond=None)
    pred = Xte2 @ beta
    if np.std(pred) == 0 or np.std(yte) == 0: return np.nan
    return float(np.corrcoef(pred, yte)[0, 1])

def main():
    rr, fe = H.per_beat_series()
    resp = fe["Resp"]; bp = fe["BP"]
    print(f"heart beats: {len(rr)}  median RR {np.median(rr):.0f} ms   (train {TRAIN_FRAC:.0%}, rest held out)\n")

    configs = {
        "base (RR only)": [],
        "+Resp (breath)": [resp],
        "+BP (lock)":     [bp],
        "+Resp+BP":       [resp, bp],
    }
    res = {nm: {h: run_config(rr, f, h) for h in HS} for nm, f in configs.items()}

    # stitch: breath donates short, BP locks long. crossover where BP overtakes Resp.
    def pick(h): return "+Resp (breath)" if h <= 3 else "+BP (lock)"
    names = list(configs) + ["combined"]
    print("HELD-OUT CORRELATION (RR forecast)   combined = Resp(h<=3) / BP(h>3)\n")
    print(f"{'h(beat)':>7}  " + "".join(f"{nm:>16}" for nm in names))
    for h in HS:
        row = f"{h:>7} "
        for nm in names:
            src = pick(h) if nm == "combined" else nm
            v = res[src][h]
            row += f"   {v:>+7.3f}      " if v == v else f"   {'--':>10}   "
        print(row)

    b = res["base (RR only)"]; rsp = res["+Resp (breath)"]; bpv = res["+BP (lock)"]
    print(f"\nSHORT (breath donates): h=1 base {b[1]:+.3f} -> +Resp {rsp[1]:+.3f} | h=3 base {b[3]:+.3f} -> +Resp {rsp[3]:+.3f}")
    print(f"LONG  (BP locks):       h=8 base {b[8]:+.3f} -> +BP   {bpv[8]:+.3f} | h=13 base {b[13]:+.3f} -> +BP {bpv[13]:+.3f}")
    print("\nIf each channel feeds the heart THROUGH the nervous system, expect ~half the lift")
    print("a direct feed would give. Strict-causal, contemporaneous feeders, held-out test.")

if __name__ == "__main__": main()
