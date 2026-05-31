"""
Reverse-inference: reconstruct the hidden autonomic-nervous-system tick, predict heart from IT.
==============================================================================================
Dylan, 2026-05-30. The heart is run by the autonomic nervous system (the hub), never measured
here (EEG was cortex, the wrong probe). Breath, BP and senses feed INTO the hub. Framework move:
reconstruct the hub from the feeders, then predict the heart from the hub.

Hub as a TANK (Dylan): inflow = BP FAST (forward donor) [+]; drain = breath SLOW (counterspin
clock) [-]; level = leaky integral, leak = 1/phi (autonomic tone has memory).

1D-tank lesson (it failed): integrating the FAST forward donor smears out the fast information
that was doing the work. You don't tank the forward spin -- only the counterspin is a tank. So
the hub is 2-compartment (the A-R-A shape): FAST forward node passes through + SLOW counterspin
node is tanked.

STRICT-CAUSAL: bands from past-only trailing smoother; z + integrator from TRAIN only; target a
FUTURE beat; last 40% held out; correlation leads. slp01a, real. Descriptive.
"""
import numpy as np
import heart_info_exchange_R as H
import heart_fast_forwardspin as F

PHI = (1 + 5 ** 0.5) / 2
LEAK = 1 / PHI
NLAG = 4
TRAIN_FRAC = 0.60
HS = (1, 2, 3, 5, 8, 13, 21)

def leaky_integrate(drive, leak=LEAK):
    h = np.zeros_like(drive, dtype=float)
    for t in range(1, len(drive)):
        h[t] = leak * h[t-1] + (1 - leak) * drive[t]
    return h

def design(rr, feats, t0, t1):
    rows = []
    for t in range(t0, t1):
        r = [rr[t-k] for k in range(NLAG)]
        for f in feats: r.append(f[t])
        r.append(1.0)
        rows.append(r)
    return np.array(rows)

def score(rr, feats, h):
    n = len(rr); lo = NLAG; hi = n - h
    split = lo + int((hi - lo) * TRAIN_FRAC)
    Xtr = design(rr, feats, lo, split); Xte = design(rr, feats, split, hi)
    ytr = np.array([rr[t+h] for t in range(lo, split)])
    yte = np.array([rr[t+h] for t in range(split, hi)])
    m = Xtr[:, :-1].mean(0); s = Xtr[:, :-1].std(0); s[s == 0] = 1.0
    Xtr[:, :-1] = (Xtr[:, :-1] - m) / s; Xte[:, :-1] = (Xte[:, :-1] - m) / s
    beta, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
    pred = Xte @ beta
    if np.std(pred) == 0: return np.nan
    return float(np.corrcoef(pred, yte)[0, 1])

def main():
    rr, fe = H.per_beat_series()
    bp_fast, _ = F.split_bands(fe["BP"])
    _, resp_slow = F.split_bands(fe["Resp"])
    n = len(rr); split = NLAG + int((n - NLAG) * TRAIN_FRAC)

    def ztrain(x):
        m = x[:split].mean(); s = x[:split].std() or 1.0
        return (x - m) / s

    hub1d = leaky_integrate(ztrain(bp_fast) - ztrain(resp_slow))
    hub_fast = bp_fast
    hub_slow_tank = leaky_integrate(ztrain(resp_slow))

    configs = {
        "base (RR only)":  [],
        "+raw feeders":    [bp_fast, resp_slow],
        "+hub 1D (tank)":  [hub1d],
        "+hub 2-compart":  [hub_fast, hub_slow_tank],
    }
    res = {nm: {h: score(rr, f, h) for h in HS} for nm, f in configs.items()}

    print("heart beats: %d   hub leak = 1/phi = %.3f   (train %d%%, held out rest)\n"
          % (n, LEAK, int(TRAIN_FRAC * 100)))
    names = list(configs)
    print("HELD-OUT CORRELATION (RR forecast)\n")
    print("h(beat)  " + "".join("%16s" % nm for nm in names))
    for h in HS:
        row = "%7d " % h
        for nm in names:
            v = res[nm][h]
            row += ("   %+7.3f      " % v) if v == v else ("   %10s   " % "--")
        print(row)

    b = res["base (RR only)"]
    print("\nLIFT over base:")
    print("   h    +raw feeders        +hub 1D    +hub 2-compart")
    for h in HS:
        print("%4d  %+14.3f %+14.3f %+16.3f" % (
            h, res["+raw feeders"][h]-b[h], res["+hub 1D (tank)"][h]-b[h],
            res["+hub 2-compart"][h]-b[h]))
    print("\n1D tank smears the fast donor (fails). 2-compartment keeps fast forward + tanks the")
    print("slow counterspin = the A-R-A hub shape. Strict-causal, held-out, correlation-led.")

if __name__ == "__main__": main()
