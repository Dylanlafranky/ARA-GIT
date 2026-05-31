"""
SpO2 as the slow RUNG BELOW BP (Dylan, 2026-05-30).
===================================================
Breath -> BP -> blood oxygen: oxygen is one rung lower again. Earlier (MIMIC combined-lock)
raw SpO2 added almost nothing on top of BP. New idea: don't use SpO2 as a fast signal --
use it the way the BRAIN worked in the NS bridge: as a SLOW TONIC STATE (slow band, tanked
with leak 1/phi). The fast detail is BP; the slow oxygen level is the rung beneath it.

Test per patient (and mean): base (RR) / +BP fast / +BP fast + SpO2 slow-tank.
Patient 476 is the only one with a real oxygen swing (45 pts) -- watch it especially.

STRICT-CAUSAL: trailing past-only slow band; train-only z + tank; future-beat target;
first half train / second half test; correlation leads. MIMIC mimicdb, real. Descriptive.
"""
import numpy as np

PHI = (1 + 5 ** 0.5) / 2; LEAK = 1 / PHI
RECS = ['041','230','417','476']; HS = [5,10,20,40]; NLAG = 4; W = 8

def ffill(d):
    d = d.astype(float).copy()
    for k in range(1, len(d)):
        if not np.isfinite(d[k]): d[k] = d[k-1]
    d[~np.isfinite(d)] = np.nanmean(d[np.isfinite(d)])
    return d

def trailing_slow(x, w):
    out = np.empty_like(x, float)
    for i in range(len(x)):
        out[i] = x[max(0,i-w+1):i+1].mean()
    return out

def leaky(drive):
    h = np.zeros_like(drive, float)
    for t in range(1, len(drive)):
        h[t] = LEAK*h[t-1] + (1-LEAK)*drive[t]
    return h

def design(rr, feats, t0, t1):
    rows = []
    for t in range(t0, t1):
        r = [rr[t-k] for k in range(NLAG)]
        for f in feats: r.append(f[t])
        r.append(1.0); rows.append(r)
    return np.array(rows)

def score(rr, feats, h, split_frac=0.5):
    n = len(rr); lo = NLAG; hi = n - h
    split = lo + int((hi-lo)*split_frac)
    Xtr = design(rr,feats,lo,split); Xte = design(rr,feats,split,hi)
    ytr = np.array([rr[t+h] for t in range(lo,split)])
    yte = np.array([rr[t+h] for t in range(split,hi)])
    m = Xtr[:,:-1].mean(0); s = Xtr[:,:-1].std(0); s[s==0]=1
    Xtr[:,:-1]=(Xtr[:,:-1]-m)/s; Xte[:,:-1]=(Xte[:,:-1]-m)/s
    beta,*_=np.linalg.lstsq(Xtr,ytr,rcond=None)
    pred=Xte@beta
    return np.nan if pred.std()==0 else float(np.corrcoef(pred,yte)[0,1])

def main():
    print("SpO2 as the slow rung below BP (MIMIC, strict-causal)\n")
    print("lift over base:   +BP fast   |   +BP fast + SpO2 slow-tank")
    agg = {h:[[],[]] for h in HS}
    for r in RECS:
        rr = ffill(np.load(f'/tmp/m_rr_{r}.npy'))
        bp = ffill(np.load(f'/tmp/m_bp_{r}.npy'))
        o  = ffill(np.load(f'/tmp/m_spo2_{r}.npy'))
        n = min(len(rr),len(bp),len(o)); rr,bp,o = rr[:n],bp[:n],o[:n]
        split = NLAG + int((n-NLAG)*0.5)
        zt = lambda x: (x - x[:split].mean())/(x[:split].std() or 1)
        bp_fast = bp - trailing_slow(bp, W)
        o_slow_tank = leaky(zt(trailing_slow(o, W)))
        print(f"  rec {r} (swing {np.ptp(o):.0f} pts):")
        for h in HS:
            b  = score(rr, [], h)
            a  = score(rr, [bp_fast], h)
            c  = score(rr, [bp_fast, o_slow_tank], h)
            agg[h][0].append(a-b); agg[h][1].append(c-b)
            print(f"     h={h:<3} {a-b:+0.3f}        {c-b:+0.3f}")
    print("\n  MEAN over 4 patients:")
    print("  h     +BP      +BP+SpO2slow")
    for h in HS:
        print(f"  {h:<4} {np.mean(agg[h][0]):+0.3f}     {np.mean(agg[h][1]):+0.3f}")
    print("\nIf SpO2 slow-tank beats +BP alone => the oxygen rung adds tonic context.")
    print("Watch 476 (45-pt swing): the rung should show most where oxygen actually moves.")

if __name__ == "__main__": main()
