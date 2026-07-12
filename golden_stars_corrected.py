#!/usr/bin/env python3
"""
golden_stars_corrected.py — independent re-run + correction of EnergyRatio/club_pop.py
=======================================================================================
Run 2026-07-02 (Claude, at Dylan's request) on freshly downloaded data:
  - OGLE-IV RRc catalog:  https://www.astrouw.edu.pl/ogle/ogle4/OCVS/blg/rrlyr/RRc.dat
  - Netzel & Smolec 2019 RR0.61 census: VizieR J/MNRAS/487/5584 table1.dat

CORRECTS the sign-interpretation error found by the 2026-06-20 peer-review audit
(club_pop.py line 40): a NEGATIVE corr(|Px/P1O - 1/phi|, R21) means FURTHER from
1/phi = lower R21 = leaner, i.e. the within-club gradient points AGAINST the
phi hypothesis, not for it.

ADDS the confound-controlled test the original lacked: each club star is matched
to control RRc stars with |dP| < 0.005 d and |dA_I| < 0.02 mag (R21 covaries with
both: corr(P,R21) = -0.40, corr(A,R21) = +0.44 in controls).

RESULTS (2026-07-02 run):
  club n=949, control n=17305
  mean R21: club 0.1138 vs control 0.1250  -> club 8.9% leaner
  Mann-Whitney (club < control): p = 5.7e-08

  MATCHED (P,A) test, n=946 club stars with >=5 lookalikes:
    mean(R21_club - R21_matched_ctrl) = -0.0077, Wilcoxon p = 8.8e-43
    => class-level leanness is REAL and NOT a period/amplitude artifact.  [FOR]

  within-club gradient:
    Pearson corr(dist_from_1/phi, R21) = -0.347 (p=3.4e-28), Spearman -0.418
    partial corr controlling (P, A)    = -0.203 (p=2.7e-10)
    => further from exact 1/phi = LEANER. Robust, survives controls,
       and INVERTS the claimed "leanness deepens toward exact phi".  [AGAINST]

HONEST SUMMARY: the data supports "RR0.61 stars are a leaner class than matched
ordinary RRc" (strong), and does NOT support "closeness to phi deepens leanness"
(the gradient runs the other way). Remaining confound: the extra non-radial mode
itself may bias the OGLE Fourier fit of R21.
"""
import numpy as np
from scipy import stats

PHI = (1 + 5**0.5) / 2

def load_club(path='/tmp/ns_table1.dat'):
    club = {}
    for ln in open(path, encoding='latin1'):
        t = ln.split()
        if t and t[0].startswith('OGLE'):
            try: club[t[0]] = float(t[5])   # Px/P1O
            except (ValueError, IndexError): pass
    return club

def load_rrc(path='/tmp/RRc.dat'):
    """OGLE RRc.dat columns: ID I V P e_P T0 A_I R21 phi21 R31 phi31"""
    recs = {}
    for ln in open(path, encoding='latin1'):
        t = ln.split()
        if not t or not t[0].startswith('OGLE'): continue
        try:
            P, A, R21 = float(t[3]), float(t[6]), float(t[7])
            if np.isfinite(R21) and R21 > 0: recs[t[0]] = (P, A, R21)
        except (ValueError, IndexError): pass
    return recs

def main():
    club, recs = load_club(), load_rrc()
    cids = [k for k in recs if k in club]
    kids = [k for k in recs if k not in club]
    cP, cA, cR = map(np.array, zip(*[recs[k] for k in cids]))
    kP, kA, kR = map(np.array, zip(*[recs[k] for k in kids]))

    print(f"club n={len(cids)}  control n={len(kids)}")
    print(f"mean R21: club {cR.mean():.4f}  control {kR.mean():.4f}"
          f"  -> club {100*(kR.mean()-cR.mean())/kR.mean():.1f}% leaner")
    print("Mann-Whitney (club<control) p = %.3e"
          % stats.mannwhitneyu(cR, kR, alternative='less')[1])

    # --- within-club gradient (sign-corrected interpretation) ---
    dist = np.abs(np.array([club[k] for k in cids]) - 1/PHI)
    pe, sp = stats.pearsonr(dist, cR), stats.spearmanr(dist, cR)
    print(f"\nwithin-club corr(dist, R21): Pearson {pe[0]:+.3f} (p={pe[1]:.1e})"
          f"  Spearman {sp[0]:+.3f}")
    print("  NEGATIVE => further from 1/phi = leaner  [AGAINST phi hypothesis]")

    # --- confounds ---
    print(f"\ncontrols: corr(P,R21)={stats.pearsonr(kP,kR)[0]:+.3f}"
          f"  corr(A,R21)={stats.pearsonr(kA,kR)[0]:+.3f}")

    # --- matched-control test ---
    diffs = []
    for i in range(len(cP)):
        m = (np.abs(kP-cP[i]) < 0.005) & (np.abs(kA-cA[i]) < 0.02)
        if m.sum() >= 5: diffs.append(cR[i] - kR[m].mean())
    diffs = np.array(diffs)
    print(f"\nMATCHED (P,A): n={len(diffs)};"
          f" mean diff {diffs.mean():+.4f}; Wilcoxon p=%.3e"
          % stats.wilcoxon(diffs)[1])

    # --- partial correlation controlling P, A ---
    X = np.column_stack([np.ones_like(cP), cP, cA])
    rd = dist - X @ np.linalg.lstsq(X, dist, rcond=None)[0]
    rr = cR   - X @ np.linalg.lstsq(X, cR,   rcond=None)[0]
    pp = stats.pearsonr(rd, rr)
    print(f"within-club PARTIAL corr(dist,R21 | P,A) = {pp[0]:+.3f} (p={pp[1]:.1e})")

if __name__ == '__main__':
    main()
