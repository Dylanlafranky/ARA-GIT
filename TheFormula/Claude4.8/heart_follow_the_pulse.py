"""
Follow the pulse: a consistent lead frame from the input, not a decaying forecast.
==================================================================================
Dylan, 2026-05-30: the heart is the body's CLOCK (a terminal energy pulse), so forecasting
it by its own past decays fast. But the INPUT arrives early and the pulse takes a ~fixed time
to travel the rungs down to the heart. So anchoring on an upstream feeder should give a lead
that stays FLAT out to its propagation distance, while the heart's own autoregression decays.

Test, strict-causal, each predictor ALONE (no RR lags mixed in, so we isolate each rung's own
lead information) vs the heart's own AR baseline:
   AR(heart)     = RR's own recent beats           -> should DECAY with horizon
   breath FAST   = fast respiratory drive           -> leads ~4 beats (R-map)
   BP FAST       = fast pressure/oxygen detail
   brain SLOW    = EEG slow tonic state (tanked)     -> slow, indirect, hardest path
Also: the CHAIN (brain-slow + breath-fast + BP-fast together) = watch the whole path.

For each, report corr to RR[t+h] across horizons, and the cross-correlation LEAD (beats) of
each channel to the heart. Flat curve out to the lead = consistent lead frame. slp01a, real.
"""
import numpy as np
import heart_info_exchange_R as H
import heart_fast_forwardspin as F

PHI = (1 + 5 ** 0.5) / 2; LEAK = 1 / PHI
TRAIN_FRAC = 0.60; HS = (1, 2, 3, 5, 8, 13, 21)

def leaky(x):
    h = np.zeros_like(x, float)
    for t in range(1, len(x)): h[t] = LEAK*h[t-1] + (1-LEAK)*x[t]
    return h

def design(rr, feats, lags, t0, t1):
    rows = []
    for t in range(t0, t1):
        r = [rr[t-k] for k in range(lags)]
        for f in feats: r.append(f[t])
        r.append(1.0); rows.append(r)
    return np.array(rows)

def score(rr, feats, lags, h):
    n = len(rr); lo = max(lags, 1); hi = n - h
    split = lo + int((hi-lo)*TRAIN_FRAC)
    Xtr = design(rr,feats,lags,lo,split); Xte = design(rr,feats,lags,split,hi)
    ytr = np.array([rr[t+h] for t in range(lo,split)])
    yte = np.array([rr[t+h] for t in range(split,hi)])
    if Xtr.shape[1] > 1:
        m = Xtr[:,:-1].mean(0); s = Xtr[:,:-1].std(0); s[s==0]=1
        Xtr[:,:-1]=(Xtr[:,:-1]-m)/s; Xte[:,:-1]=(Xte[:,:-1]-m)/s
    beta,*_=np.linalg.lstsq(Xtr,ytr,rcond=None); pred=Xte@beta
    return np.nan if pred.std()==0 else float(np.corrcoef(pred,yte)[0,1])

def lead_beats(feed, rr, maxlag=20):
    """+L means feed leads heart by L beats (feed[t] best matches rr[t+L])."""
    a = (feed-feed.mean())/(feed.std() or 1); b = (rr-rr.mean())/(rr.std() or 1)
    best, bl = 0.0, 0
    for L in range(0, maxlag+1):
        if L == 0: c = abs(np.corrcoef(a, b)[0,1])
        else:      c = abs(np.corrcoef(a[:-L], b[L:])[0,1])
        if c > best: best, bl = c, L
    return bl, best

def main():
    rr, fe = H.per_beat_series()
    rr = np.asarray(rr, float)
    bp_fast,   _        = F.split_bands(fe["BP"])
    resp_fast, _        = F.split_bands(fe["Resp"])
    _,         eeg_slow = F.split_bands(fe["EEG"])
    n = len(rr); split = int(n*TRAIN_FRAC)
    zt = lambda x: (x - x[:split].mean())/(x[:split].std() or 1)
    brain_slow_tank = leaky(zt(eeg_slow))

    feeders = {
        "breath FAST": resp_fast,
        "BP FAST":     bp_fast,
        "brain SLOW":  brain_slow_tank,
    }
    print("CROSS-CORRELATION LEAD to the heart (beats):")
    for nm, f in feeders.items():
        L, c = lead_beats(np.asarray(f,float), rr)
        print("   %-12s leads heart by %2d beats   (|corr| %.3f)" % (nm, L, c))

    print("\nSTANDALONE corr to RR[t+h] -- each rung ALONE vs the heart's own AR\n")
    cols = ["AR(heart)","breath FAST","BP FAST","brain SLOW","CHAIN(all3)"]
    print("h(beat) " + "".join("%14s" % c for c in cols))
    for h in HS:
        ar  = score(rr, [], 2, h)                                  # heart's own past, decays
        br  = score(rr, [resp_fast], 0, h)                         # breath alone, no RR
        bpf = score(rr, [bp_fast], 0, h)                           # BP alone
        brn = score(rr, [brain_slow_tank], 0, h)                   # brain alone
        ch  = score(rr, [resp_fast, bp_fast, brain_slow_tank], 0, h)  # whole path, no RR
        row = "%6d " % h
        for v in (ar, br, bpf, brn, ch):
            row += ("%+13.3f " % v) if v == v else ("%13s " % "--")
        print(row)
    print("\nDECAY check: AR(heart) should fall fastest with horizon; an input rung that")
    print("holds flatter out to its lead = the consistent lead frame (watch the fuse).")

if __name__ == "__main__": main()
