# Golden Stars — Independent Re-run and Correction

**2 July 2026. Independent verification by Claude (Fable 5) at Dylan's request, on freshly
downloaded data.** Supplements `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md`; confirms and extends
finding #1 of `PEER_REVIEW_AUDIT_2026-06-20.md`. Reproduction script: `golden_stars_corrected.py`
(run `EnergyRatio/fetch_data.py` first, or download RRc.dat + ns_table1.dat as in the script header).

## What was re-run

Data re-fetched 2026-07-02 from the primary sources (OGLE-IV OCVS `blg/rrlyr/RRc.dat`;
Netzel & Smolec 2019 RR0.61 census, VizieR J/MNRAS/487/5584). All numbers below are from
that fresh download, independent of any cached files.

## Result 1 — the class-level leanness claim SURVIVES, strengthened (FOR)

- Club n=949, control n=17,305. Mean R21: club **0.1138** vs control **0.1250** →
  club **8.9% leaner** (Mann-Whitney, club<control: p = 5.7×10⁻⁸).
- **New confound-controlled test** (not in the original): each club star matched to
  control RRc stars with |ΔP| < 0.005 d and |ΔA_I| < 0.02 mag. R21 covaries strongly with
  both (corr(P,R21) = −0.40, corr(A,R21) = +0.44 in controls), so this matching is required.
  Result: club stars are still leaner than their lookalikes —
  **mean ΔR21 = −0.0077, Wilcoxon p = 8.8×10⁻⁴³, n = 946**.
- Conclusion: RR0.61 stars are a genuinely leaner class; the effect is not a
  period/amplitude artifact.

## Result 2 — the within-club φ-gradient "backbone" is INVERTED (AGAINST)

The audit's sign finding is confirmed and is robust:

- Pearson corr(|Px/P1O − 1/φ|, R21) = **−0.347** (p = 3.4×10⁻²⁸); Spearman **−0.418**.
- Survives partial correlation controlling for period and amplitude: **−0.203** (p = 2.7×10⁻¹⁰).
- A negative correlation means **further from exact 1/φ = lower R21 = leaner**.
  The claimed reading ("leanness deepens toward exact φ") is the opposite of what the
  data shows. A φ-attractor hypothesis predicts a positive slope; the measured slope is
  negative, strong, and control-resistant.

## Corrected careful claim

> RR0.61 stars (period ratio ≈ 0.61) are systematically leaner (lower R21) than ordinary
> single-mode RRc stars, and this survives matching on period and amplitude
> (p ≈ 10⁻⁴²). However, within the class, leanness does **not** deepen toward exact 1/φ —
> the gradient runs the other way (partial r = −0.20). The data supports "the RR0.61
> class is special," not "closeness to φ causes leanness."

## Required edits

1. `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md` — replace the within-club backbone sentence
   with the corrected claim above; the population claim can be strengthened using the
   matched-control numbers.
2. `CLAIMS_STATUS.md` (31 May update) — same correction; move "leanness deepens toward
   exact 1/φ" to the retracted/corrected record.
3. `EnergyRatio/club_pop.py` line 40 — fix the comment
   `[negative => closer to 1/phi = leaner]` (mathematically inverted).

## Remaining open confound

The additional non-radial mode in RR0.61 stars may itself bias the OGLE Fourier fit of
the primary mode's R21 (extra power in the light curve → mis-estimated harmonic
amplitudes). Distinguishing "leaner pulsation" from "R21 measurement bias in the
presence of the extra mode" needs prewhitening the secondary mode before measuring R21
on a subsample — a decisive follow-up, doable with the existing `golden_prewhiten.py`
approach on OGLE photometry.
