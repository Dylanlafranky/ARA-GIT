"""
ARA TWO-BAND DRIFT predictor  (gated metawave floor with a DRIFTING period)
===========================================================================

Dylan (2026-05-29): a fixed-frequency band fit de-phases as it walks forward and
turns ANTI-correlated (locks one beat, the real beat wanders, prediction inverts).
Fix: re-estimate each band's period every step from a trailing window, and fit the
sinusoid on that same recent window -- so the spine keeps phase with the breathing
instead of damping itself flat. Everything else (engine, recharge, regime gate) is
identical to ara_twoband_center.py, so the ONLY change is fixed -> drifting period.

Strict causal: period + amp + phase all from T[i-WIN .. i]; handoff betas fit on
origins < CAL_SPLIT; held-out >= CAL_SPLIT. Correlation leads. Reported full holdout,
the 2017-2022 dead zone, and cross-event block-CV. Compared to fixed-period & handoff.

Usage: python3 ara_twoband_drift.py nino34_long_anom.csv
"""

import sys
import numpy as np
import ara_pyramid_release_spring as M
import ara_twoband_center as C

CAL = M.CAL_SPLIT_YEAR
WIN = 300                 # trailing window for the drifting band fit (months)
GBAND = (20.0, 38.0)      # green search range
BBAND = (40.0, 84.0)      # brown search range


def best_period(seg, lo, hi):
    """Causal dominant period in [lo,hi] mo from a trailing window (zero-padded FFT)."""
    s = seg - seg.mean(); n = len(s)
    nfft = max(2048, 1 << int(np.ceil(np.log2(n * 4))))
    P = np.abs(np.fft.rfft(s * np.hanning(n), nfft)) ** 2
    f = np.fft.rfftfreq(nfft, 1.0)
    per = np.where(f > 0, 1.0 / np.maximum(f, 1e-12), 0.0)
    m = (per >= lo) & (per <= hi)
    pp = per[m]; PP = P[m]
    return float(pp[np.argmax(PP)])


def walk_drift(T, W, E, yr, mon):
    """Same scaffolding as C.walk but the center uses per-origin drifting periods."""
    tmo = np.arange(len(T), dtype=float)
    rec = {h: {"eng": [], "rech": [], "truth": [], "clim": [], "center": [],
               "oy": [], "tyr": [], "tpress": []} for h in range(1, M.HMAX + 1)}
    for i in range(len(T)):
        if yr[i] < M.WALK_START:
            continue
        idx = np.arange(0, i)
        if len(idx) < M.MIN_TRAIN:
            continue
        zW = (W - W[idx].mean()) / W[idx].std()
        zE = (E - E[idx].mean()) / E[idx].std()
        X = np.column_stack([T, zW, zE]); clim = T[idx].mean()
        # --- DRIFT: estimate band periods + fit sinusoids on the trailing window ---
        w0 = max(0, i - WIN)
        wt = tmo[w0:i + 1]; wT = T[w0:i + 1]
        gp = best_period(wT, *GBAND); bp = best_period(wT, *BBAND)
        cob = np.linalg.lstsq(C.design(wt, [gp, bp]), wT, rcond=None)[0]
        # --- engine / recharge unchanged (full-history, as in C.walk) ---
        B = np.linalg.lstsq(M.seasonal_features(X[idx][:-1], mon[idx][:-1]), X[idx][1:], rcond=None)[0]
        for h in range(1, M.HMAX + 1):
            if i + h >= len(T):
                break
            x = X[i].copy()
            for kk in range(h):
                mm = ((mon[i] - 1 + kk) % 12) + 1
                x = M.seasonal_features(x[None, :], np.array([mm]))[0] @ B
            eng = x[0]
            past = idx[idx + h < i]
            if len(past) >= 60:
                A = np.column_stack([np.ones(len(past)), zW[past], zE[past]])
                co = np.linalg.lstsq(A, T[past + h], rcond=None)[0]
                rech = co[0] + co[1] * zW[i] + co[2] * zE[i]
            else:
                rech = clim
            center = float(C.design(np.array([tmo[i + h]]), [gp, bp]) @ cob)
            r = rec[h]
            r["eng"].append(eng); r["rech"].append(rech); r["truth"].append(T[i + h])
            r["clim"].append(clim); r["center"].append(center)
            r["oy"].append(yr[i]); r["tyr"].append(yr[i + h]); r["tpress"].append(M.pressure_proxy(yr[i + h]))
    return rec


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    M._dl("wwv_west.dat", "wwv_west.dat"); M._dl("wwv_east.dat", "wwv_east.dat")
    W = M.load_wwv("wwv_west.dat"); E = M.load_wwv("wwv_east.dat"); nino = M.load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys]); Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys]); mon = np.array([int(k[4:6]) for k in keys])

    rec_fix = C.walk(T, Wv, Ev, yr, mon, C.GREEN_MO + C.BROWN_MO)   # fixed-period spine
    rec_drf = walk_drift(T, Wv, Ev, yr, mon)                        # drifting-period spine

    print("ARA TWO-BAND DRIFT  (gated metawave floor, period re-estimated each step)\n")
    print("Correlation. FULL = holdout 2017+;  LOW = 2017-2022 dead zone.  CORRELATION LEADS.\n")
    print(f"{'lead':>4} | {'hand FULL':>10} {'fix FULL':>9} {'drift FULL':>11}"
          f" | {'hand LOW':>9} {'fix LOW':>8} {'drift LOW':>10} | {'fixProj':>8} {'drftProj':>8}")
    for h in [6, 12, 18, 24, 30]:
        eng, rech, cl, tr, ctrF, oy, tyr, low = C.scores(rec_fix, h)
        _, _, _, _, ctrD, _, _, _ = C.scores(rec_drf, h)
        trn = oy < CAL; tst = oy >= CAL
        hand = M.blend_handoff(eng, rech, cl, low, tr, trn)
        gF = C.blend_gated(eng, rech, cl, ctrF, low, tr, trn)
        gD = C.blend_gated(eng, rech, cl, ctrD, low, tr, trn)
        lw = tst & (tyr >= 2017) & (tyr < 2022)
        print(f"{h:>4} | {M.corr(hand[tst],tr[tst]):>+10.3f} {M.corr(gF[tst],tr[tst]):>+9.3f}"
              f" {M.corr(gD[tst],tr[tst]):>+11.3f} | {M.corr(hand[lw],tr[lw]):>+9.3f}"
              f" {M.corr(gF[lw],tr[lw]):>+8.3f} {M.corr(gD[lw],tr[lw]):>+10.3f}"
              f" | {M.corr(ctrF[tst],tr[tst]):>+8.3f} {M.corr(ctrD[tst],tr[tst]):>+8.3f}")

    print("\nCross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'handoff':>8} {'fix':>8} {'drift':>8}")
    for h in [6, 12, 24, 30]:
        eng, rech, cl, tr, ctrF, oy, tyr, low = C.scores(rec_fix, h)
        _, _, _, _, ctrD, _, _, _ = C.scores(rec_drf, h)
        edges = np.quantile(oy, [1/3, 2/3]); blk = np.digitize(oy, edges)
        ph = np.full(len(oy), np.nan); pF = np.full(len(oy), np.nan); pD = np.full(len(oy), np.nan)
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            ph[te] = M.blend_handoff(eng, rech, cl, low, tr, ~te)[te]
            pF[te] = C.blend_gated(eng, rech, cl, ctrF, low, tr, ~te)[te]
            pD[te] = C.blend_gated(eng, rech, cl, ctrD, low, tr, ~te)[te]
        print(f"{h:>4} {M.corr(ph,tr):>+8.3f} {M.corr(pF,tr):>+8.3f} {M.corr(pD,tr):>+8.3f}")
    print("\nRead: drift vs fix shows whether keeping phase (period re-estimated each step)")
    print("lets the gated spine hold its grip further into the holdout.")


if __name__ == "__main__":
    main()
