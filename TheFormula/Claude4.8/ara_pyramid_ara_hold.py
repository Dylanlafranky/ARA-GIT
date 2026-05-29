"""
ARA pyramid ARA-HOLD predictor  (the hold itself is ARA-shaped in horizon)
==========================================================================

Dylan (2026-05-29): the flat hold helped at 12mo but BROKE the 24mo ring -- a
single grip applied at every lead is too blunt. "It should be ARA all the way
around." So the hold must GRIP near and RELEASE its grip out at the rings, along
an ARA decay curve -- not a hard cutoff, a breathing release.

This stays ARA-cubed (apex T + warm-west zW + cool-east zE) with the deterministic
lunar pressure coupler from above (low/high-moon regime). No new ocean basin.

Two changes vs the flat hold:

  1. ENVELOPE g(h) = phi^(-(h-1)/tau)      -- deterministic ARA decay in lead.
     Grip ~1 near, fades toward 0 by the ring. tau is a phi-power month-scale.

  2. ONE POOLED hold strength per regime, fit across ALL horizons at once (not a
     free coefficient per lead). This beats the few-events wall: every lead's
     hold rows pool into a single causal fit. The envelope -- not the data --
     carries the horizon SHAPE.

  base(h)  = handoff (per-regime eng+rech trust, fit on train)
  hold(h)  = a_reg * g(h) * (t0 - clim)        -- t0 = apex anomaly AT origin
  pred(h)  = base(h) + hold(h)

Strict causal: handoff betas fit on origins < CAL_SPLIT; pooled a fit on the SAME
train origins (residual truth-base regressed on g(h)*hold); envelope deterministic;
moon phase deterministic ephemeris; held-out = origins >= CAL_SPLIT. Correlation
leads. Reported FULL holdout, the 2017-2022 low-moon dead zone, and cross-event CV.

Usage: python3 ara_pyramid_ara_hold.py nino34_long_anom.csv
"""

import sys
import numpy as np
import ara_pyramid_release_spring as M
import ara_pyramid_hold_geometry as H

PHI = (1 + 5 ** 0.5) / 2
CAL = M.CAL_SPLIT_YEAR
HSET = list(range(1, M.HMAX + 1))


def envelope(h, tau):
    """Deterministic ARA grip-then-release: 1 near, fades by phi-power scale tau."""
    return PHI ** (-(h - 1) / tau)


def pooled_hold(rec, tau, train_mask_fn, eval_h):
    """Fit one hold strength per regime, pooled over ALL leads, on training origins.
    Returns prediction at eval_h (handoff base + a_reg*g(h)*hold) and the a's.
    train_mask_fn(oy) -> bool mask of training origins (causal split or CV block)."""
    # Stage 1: per-horizon handoff base for every lead; collect pooled residual rows.
    base = {}; hold = {}; low = {}; tr = {}; oy = {}; tyr = {}
    for h in HSET:
        if not rec[h]["truth"]:
            continue
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"])
        cl = np.array(rec[h]["clim"]); t = np.array(rec[h]["truth"])
        t0 = np.array(rec[h]["t0"]); o = np.array(rec[h]["oy"])
        lo = np.array(rec[h]["tpress"]) < 0
        trn = train_mask_fn(o)
        b = M.blend_handoff(eng, rech, cl, lo, t, trn)
        base[h] = b; hold[h] = (t0 - cl); low[h] = lo; tr[h] = t
        oy[h] = o; tyr[h] = np.array(rec[h]["tyr"])
    # Stage 2: pool residuals (truth - base) over all leads, fit a per regime on train.
    a = {}
    for nm, want_low in (("lo", True), ("hi", False)):
        fx = []; fy = []
        for h in HSET:
            if h not in base:
                continue
            trn = train_mask_fn(oy[h])
            reg = (low[h] == want_low) & trn
            if reg.sum() == 0:
                continue
            g = envelope(h, tau)
            fx.append(g * hold[h][reg])
            fy.append(tr[h][reg] - base[h][reg])
        if not fx or np.concatenate(fx).size < 24:
            a[nm] = 0.0; continue
        x = np.concatenate(fx); y = np.concatenate(fy)
        denom = float(x @ x)
        a[nm] = float(np.clip((x @ y) / denom, 0.0, 1.5)) if denom > 0 else 0.0
    # Apply at eval_h.
    h = eval_h
    g = envelope(h, tau)
    pred = base[h].copy()
    for nm, want_low in (("lo", True), ("hi", False)):
        reg = low[h] == want_low
        pred[reg] = base[h][reg] + a[nm] * g * hold[h][reg]
    return pred, base[h], tr[h], oy[h], tyr[h], a


def main():
    nino_csv = sys.argv[1] if len(sys.argv) > 1 else "nino34_long_anom.csv"
    M._dl("wwv_west.dat", "wwv_west.dat"); M._dl("wwv_east.dat", "wwv_east.dat")
    W = M.load_wwv("wwv_west.dat"); E = M.load_wwv("wwv_east.dat"); nino = M.load_nino(nino_csv)
    keys = sorted(set(W) & set(E) & set(nino))
    T = np.array([nino[k] for k in keys]); Wv = np.array([W[k] for k in keys]); Ev = np.array([E[k] for k in keys])
    yr = np.array([int(k[:4]) + (int(k[4:6]) - 1) / 12 for k in keys]); mon = np.array([int(k[4:6]) for k in keys])
    rec = H.walk(T, Wv, Ev, yr, mon)

    taus = [PHI ** 4, PHI ** 5, PHI ** 6]   # ~6.9, 11.1, 17.9 month grip-release scales
    cal_fn = lambda o: o < CAL

    print("ARA-HOLD PREDICTOR  (hold grips near, releases its grip along an ARA curve)\n")
    print("Correlation. FULL = holdout 2017+;  LOW = 2017-2022 dead zone.  CORRELATION LEADS.\n")
    for tau in taus:
        print(f"--- envelope tau = {tau:5.2f} months  (g(12)={envelope(12,tau):.2f}, g(24)={envelope(24,tau):.2f}) ---")
        print(f"{'lead':>4} | {'hand FULL':>10} {'arahold FULL':>13} | {'hand LOW':>9} {'arahold LOW':>12} | {'a lo/hi':>10}")
        for h in [6, 12, 18, 24, 30]:
            pred, base, tr, oy, tyr, a = pooled_hold(rec, tau, cal_fn, h)
            tst = oy >= CAL
            lw = tst & (tyr >= 2017) & (tyr < 2022)
            print(f"{h:>4} | {M.corr(base[tst],tr[tst]):>+10.3f} {M.corr(pred[tst],tr[tst]):>+13.3f}"
                  f" | {M.corr(base[lw],tr[lw]):>+9.3f} {M.corr(pred[lw],tr[lw]):>+12.3f}"
                  f" | {a['lo']:.2f}/{a['hi']:.2f}")
        print()

    print("Cross-event block-CV (leave-one-block-out), pooled correlation:")
    print(f"{'lead':>4} {'handoff':>8} " + " ".join(f"ah_t{int(t)}".rjust(8) for t in taus))
    # build block ids from any populated lead
    oy_ref = np.array(rec[12]["oy"]); edges = np.quantile(oy_ref, [1/3, 2/3])
    for h in [6, 12, 24, 30]:
        eng = np.array(rec[h]["eng"]); rech = np.array(rec[h]["rech"]); cl = np.array(rec[h]["clim"])
        tr = np.array(rec[h]["truth"]); oy = np.array(rec[h]["oy"]); lo = np.array(rec[h]["tpress"]) < 0
        blk = np.digitize(oy, edges)
        ph = np.full(len(oy), np.nan)
        pah = {ti: np.full(len(oy), np.nan) for ti in range(len(taus))}
        for b in range(3):
            te = blk == b
            if te.sum() < 12 or (~te).sum() < 24:
                continue
            ph[te] = M.blend_handoff(eng, rech, cl, lo, tr, ~te)[te]
            for ti, tau in enumerate(taus):
                pr, _, _, _, _, _ = pooled_hold(rec, tau, (lambda bb: (lambda o: np.digitize(o, edges) != bb))(b), h)
                pah[ti][te] = pr[te]
        row = f"{h:>4} {M.corr(ph,tr):>+8.3f} "
        row += " ".join(f"{M.corr(pah[ti],tr):>+8.3f}" for ti in range(len(taus)))
        print(row)
    print("\nRead: an ARA-hold that LIFTS 12mo LOW (the dead zone) while NOT breaking 24mo,")
    print("and survives cross-event CV, is the grip-then-release geometry Dylan asked for.")


if __name__ == "__main__":
    main()
