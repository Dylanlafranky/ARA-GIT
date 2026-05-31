"""
Is BP genuinely extra, or just the heart's own echo?  (Dylan, 2026-05-30)
========================================================================
BP is the heart talking to itself (heart->BP lock). IF its forecast lift is only that
echo, then giving the model MORE of the heart's own recent beats (more RR lags) should
make BP redundant -- its lift should shrink toward 0 (like RSA made breath redundant).
IF BP's lift SURVIVES deeper RR memory, it carries something the beat-timing alone does
not (e.g. pressure amplitude, oxygen loading) = genuinely extra.

Sweep NLAG (depth of the heart's own memory) and watch the BP-fast lift.

STRICT-CAUSAL: BP fast band = causal trailing split; train-only z; future-beat target;
last 40% held out; correlation leads. slp01a, real. Descriptive.
"""
import numpy as np
import heart_info_exchange_R as H
import heart_fast_forwardspin as F

TRAIN_FRAC = 0.60

def design(rr, feats, t0, t1, nlag):
    rows = []
    for t in range(t0, t1):
        r = [rr[t-k] for k in range(nlag)]
        for f in feats: r.append(f[t])
        r.append(1.0)
        rows.append(r)
    return np.array(rows)

def score(rr, feats, h, nlag):
    n = len(rr); lo = nlag; hi = n - h
    split = lo + int((hi - lo) * TRAIN_FRAC)
    Xtr = design(rr, feats, lo, split, nlag); Xte = design(rr, feats, split, hi, nlag)
    ytr = np.array([rr[t+h] for t in range(lo, split)])
    yte = np.array([rr[t+h] for t in range(split, hi)])
    m = Xtr[:, :-1].mean(0); s = Xtr[:, :-1].std(0); s[s == 0] = 1.0
    Xtr[:, :-1] = (Xtr[:, :-1] - m) / s; Xte[:, :-1] = (Xte[:, :-1] - m) / s
    beta, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
    pred = Xte @ beta
    return np.nan if np.std(pred) == 0 else float(np.corrcoef(pred, yte)[0, 1])

def main():
    rr, fe = H.per_beat_series()
    bp_fast, _ = F.split_bands(fe["BP"])
    HS = (5, 8)
    NLAGS = (4, 8, 16, 24)
    print("BP-fast lift over base as the heart gets MORE of its own memory (NLAG)\n")
    print("           " + "".join("   h=%-2d        " % h for h in HS))
    print("  NLAG     base   +BP   lift |  base   +BP   lift")
    for nl in NLAGS:
        cells = []
        for h in HS:
            b  = score(rr, [], h, nl)
            bp = score(rr, [bp_fast], h, nl)
            cells.append((b, bp, bp - b))
        print("  %3d   %+5.3f %+5.3f %+6.3f | %+5.3f %+5.3f %+6.3f" % (
            nl, cells[0][0], cells[0][1], cells[0][2],
                cells[1][0], cells[1][1], cells[1][2]))
    print("\nIf 'lift' shrinks toward 0 as NLAG grows => BP was the heart's echo.")
    print("If 'lift' holds => BP carries extra (pressure/oxygen), not just beat timing.")

if __name__ == "__main__": main()
