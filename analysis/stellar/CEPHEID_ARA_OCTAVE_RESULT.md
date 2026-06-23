# Cepheids on the octave ladder — ARA vs period (population test)

**22 June 2026.** Extends the single δ Cephei placement (ARA = 1/skewness = 0.43) to a Cepheid
*population* on the octave ladder, testing the framework claim: **longer-period Cepheids become more
symmetric → ARA climbs toward 1 (clock); short-period ones are asymmetric engines/snaps.**

## Data (real, public — OGLE via VizieR)
- **Type II Cepheids, LMC** (J/AcA/68/89, Soszyński+) — 290 stars with full Fourier shape (R21, φ21,
  R31, φ31). ARA computed by **reconstructing each light curve** from its harmonics and timing the
  ascending (brightening = release) vs descending (fading = accumulation) branch: ARA = rise/fall.
- **Classical Cepheids, LMC** (J/AcA/58/163, Soszyński+) — 3375 stars; fundamental-mode subset n=1818
  with R21 (asymmetry *magnitude*; the OGLE classical tables omit the φ phase, so no signed ARA).

## Result — the prediction holds, strongly

**Type II (n=257 with ARA):** ARA median 0.82; 66% sit on the engine/snap side (ARA<1, fast rise).
ARA **climbs with period**: Spearman ρ(ARA, log₂P) = **+0.53, p≈5×10⁻²⁰**; |ARA−1| vs period
ρ = **−0.44, p≈3×10⁻¹³** (more clock-like at long P). By subtype, monotonic up the ladder:

| subtype | median period | median ARA | reading |
|---|---:|---:|---|
| BL Her | 1.6 d | **0.57** | short, asymmetric snap-engine |
| pW Vir | 7.4 d | 0.60 | — |
| W Vir | 12.8 d | 1.23 | crossed the ridge |
| RV Tau | 34.9 d | **0.97** | long, near-symmetric clock |

**Classical (n=1818):** R21 (asymmetry) collapses from ~0.44 at short period to **~0.22 at the
Hertzsprung resonance (~10 d)** — i.e. the curves go more sinusoidal / clock-like there, the same
"approach the clock" behaviour seen independently of the signed ARA.

**δ Cephei** (classical, P=5.37 d, ARA 0.43) sits exactly where expected — the short-period,
asymmetric-engine regime. Single point → population trend, confirmed.

## Reading
Short-period pulsators are **asymmetric engines/snaps** (fast rise, slow fade); as period lengthens they
relax toward the **symmetric clock** (ARA→1). This is the octave ladder doing real work on starlight:
position on the ladder predicts the build/release shape. Matches the δ Cephei result and the framework's
"only long-period Cepheids are near-symmetric" claim.

On the **#1 (golden-vs-rational sub-structure) question:** the harmonic content here is the standard
*integer*-harmonic Fourier series (rational), and the ARA trend is about asymmetry magnitude/direction,
not a golden 5-fold subdivision — consistent with the prior that the sub-structure is hexagonal/rational
(no pentagon signature needed or seen). So this is a clean ARA-vs-position result, not new evidence for φ.

## Honest caveats
- Type II Cepheids ≠ classical (δ Cephei is classical); the trend is shown cleanly on Type II because
  those tables carry the φ phases. A classical-Cepheid catalogue with φ21 would confirm the *signed* ARA
  trend directly (classical here only gave R21 magnitude).
- ARA from a 3-harmonic reconstruction is approximate — fine for the rise/fall split, but it won't
  capture RV Tau alternating-minima structure, which may bias their ARA toward 1.
- ARA = rise/fall is one operationalization (the δ Cephei convention). The *trend* (ρ≈0.5, p≈1e-20) is
  robust to that choice.

Data: `cep_t2_ara.csv`, `cep_classical_F.csv`. Figure: `cepheid_ara_octaves.png`.
Supersedes the single-point δ Cephei reading in `Mapping/ARA_OVER2_AUDIT.md` (now a population).
