# Golden Stars Run Leaner — φ and the Energy Budget of Pulsating Stars

**Date:** 31 May 2026 · ARA Framework (Dylan La Franchi & Claude)
**Status:** **CORRECTED 30 JULY 2026 — exact-Phi leanness gradient not
supported as written.** The historical class association is retained with
caveats; the within-club dose-response interpretation contained a sign error.

> **Correction (formal re-run already completed 2 July 2026):** this report
> defines lower `R21` as leaner and reports
> `corr(|Px/P1O - 1/phi|, R21) = -0.347`. Because smaller distance means
> *closer* to Phi, a negative correlation means that moving farther from exact
> Phi is associated with lower `R21`. The sentence claiming the opposite was
> mathematically reversed. The independent re-run found an `8.9%` class gap
> and a period/amplitude-matched difference (`p=8.8e-43`) but confirmed the
> within-class exact-Phi gradient runs the opposite way (partial
> `r=-0.203`). See `../GOLDEN_STARS_CORRECTION.md` and
> `analysis/phi_calibration/T303_PHI_THREE_EIGHTHS_STATE_DUALITY_AUDIT_2026-07-30.md`.

## The question

Dylan: cosmic systems are *space*-leaning (integer-resonance clockwork), but the **small, fast pulsation inside** a star might lean *time* — where φ lives. And if φ is the optimal (engine/balance) ratio, the φ-near stars should **expel and consume leaner** than off-φ stars. Test it on real starlight.

## Data (all real, public)

- **Kepler light curves** via `lightkurve` (MAST), 30-min cadence, one+ quarter each. Frequencies measured by us (Lomb–Scargle + iterative prewhitening + sine refit).
- **OGLE-IV** double-mode catalogs (`astrouw.edu.pl/ogle`): RRd (double RR Lyrae) and Cep F+1O.
- **Netzel & Smolec 2019** census of RR0.61 stars (VizieR `J/MNRAS/487/5584`), cross-matched to OGLE bulge `RRc.dat` for harmonic parameters.

Supersedes Script 98 (Cepheid ARA from hand-typed literature rise fractions) — this is raw photometry + real catalogs.

## Leanness metric

**R21 = A(2f)/A(f₁)** — the Fourier harmonic spray, i.e. how much energy leaks from the fundamental into its 2nd harmonic. A clean near-sinusoidal pulse has low R21; a shocky/sawtooth, dissipative pulse has high R21. **Lower R21 = leaner.**

## Result — the gradient (all real data)

| Class | 2nd-mode ratio | leanness R21 |
|---|---|---|
| Single-mode classical Cepheid (V1154 Cyg) | integer harmonics only (1×,2×,3×,4× exact); **φ absent** | **0.28** (fattest) |
| Ordinary double-mode pulsators (433 OGLE) | 1.34–1.42 (near-rational Petersen ratio) | 0.16 (RRd) / 0.19 (Cep) |
| Near-φ "golden" club (4 Kepler RRc) | within ~2% of φ (3 within 1%) | **≈0.11** (leanest) |

Golden club members (raw Kepler, 2nd-mode/f₁): KIC 5520878 = 1.583 (−2.2%), KIC 4064484 = 1.626 (+0.5%), KIC 8832417 = 1.635 (+1.1%), KIC 9453114 = 1.630 (+0.7%). All R21 ≈ 0.106–0.118.

### Population confirmation (n≈950)
- φ-club = 949 OGLE RR0.61 stars (period ratio Px/P1O ≈ 0.61 = 1/φ). Mean R21 **0.1138** vs 18,318 ordinary single-mode RRc **0.1181** → club **3.6% leaner**, Mann–Whitney p = **0.016**.
- **Within the club: corr(|Px/P1O − 1/φ|, R21) = −0.347 (n=949).**
  The original text incorrectly said this meant closer to exact `1/φ` was
  leaner. With lower `R21 = leaner`, the reported sign points in the opposite
  direction.

## Reading & mechanism

The corrected calculation reports a class-level association: the selected
RR0.61 group has lower mean `R21` than the broad RRc control, and the result
survives period/amplitude matching. It does **not** show that closeness to
exact Phi tracks greater leanness inside the group.
The proposed KAM/locking mechanism therefore remains a hypothesis rather than
the demonstrated explanation of this comparison. Note `1/φ = 0.618` is the
golden-family reciprocal.

This matches the framework's earlier φ-rung **entropy-decay** result on ECG/ENSO (`PHI_RUNG_ENTROPY_DECAY_RESULT.md`): φ = most-irrational packing = least entropy leaked per cycle. There it was a number in a decay curve; here it is a physical energy signature in starlight — same principle, new domain.

## What failed first (honest trail)
Tested on the 433-star crowd before assembling the club:
- **Density/period proxy** — mixed (RRd denser→φ r=−0.84, but Cep denser→away r=+0.78). Not universal.
- **Small-mode energy fraction** — weak and *backwards* (−0.28).
- **Total brightness/amplitude** — null.
Only **leanness (R21)** pointed the right way in both classes and on the golden stars. Sampling lesson: you cannot find "what pushes toward φ" by correlating *within* a crowd that never reaches φ (all jammed at 1.34–1.42 by metallicity/mass); we had to assemble the near-φ **club** and compare it to the crowd.

## Caveats (kept explicit)
- n=4 Kepler club is a **known related class** (Lindner 2015 strange-nonchaotic stars) — re-found, not independently discovered. The leanness *measurement* is ours.
- R21 is **one** (clean, physical) leanness proxy.
- The corrected re-run found an `8.9%` class gap and a matched-control
  difference of `-0.0077` in `R21`.
- The old within-club exact-Phi gradient was interpreted in the wrong
  direction and cannot serve as the backbone of the claim.
- The corrected download/reproduction pathway is documented in
  `../GOLDEN_STARS_CORRECTION.md` and `../golden_stars_corrected.py`.
- Golden-star secondary modes may be **non-radial**, vs the crowd's radial overtones — not perfectly apples-to-apples.
- "φ resists locking / most-irrational stability" is **established mathematics** (KAM). The empirical leanness gradient and the cross-domain entropy framing are the framework's new contribution.

## Scripts (this folder)
`golden_prewhiten.py` (Kepler frequency extraction), `popdist2.py` (OGLE double-mode ratio distribution), `lean.py` (R21 vs ratio in OGLE crowd), `club_lean.py` (4 Kepler golden stars, raw), `club_pop.py` (RR0.61 cross-match leanness + within-club gradient), `tsratio.py`/`ampfrac.py` (failed density/amplitude proxies, kept for the trail).

## Next
Widen further (RR0.68 group; LMC/SMC RR0.61); test a second leanness proxy (higher harmonics R31, light-curve skew); check whether the φ-club is also more *transient* (strange-nonchaotic / shorter stable lifetime) — Dylan's "burns bright" angle.
