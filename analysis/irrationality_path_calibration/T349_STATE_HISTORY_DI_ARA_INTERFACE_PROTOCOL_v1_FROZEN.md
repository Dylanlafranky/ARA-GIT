# T349 frozen protocol v1 — state/history Di-ARA interface

**Frozen:** 11 August 2026, before implementation or scoring  
**Evidence class:** synthetic known-referee instrument/interface calibration  
**Claim packet:** `T349_STATE_HISTORY_DI_ARA_INTERFACE_CLAIM_PACKET_v1.md`  
**Originator sign-off:** user accepted the exact T349 design before execution

## WHO

Five T348 phase-history families—periodic rational, irrational rotation,
deterministic chaos, finite stochastic and continuous stochastic—are crossed
with three independently controlled radial families: contraction, neutral and
expansion. The resulting `5 × 3 = 15` core identities use multiple parameter
values, seeds and untouched holdout amplitudes. Reflected phase twins are
controls rather than additional identity labels.

## WHAT

Measure two related but non-flattened objects from each complex trajectory
`z_t = r_t exp(2 pi i u_t)`:

1. **older state Di-ARA:** radial contraction/expansion coordinate `x_L` and
   signed phase-orientation coordinate `x_C`;
2. **newer history Di-ARA:** address openness `x_P`, stochastic residual `x_R`
   and uncompressed closure history `C(H)`.

The older state geometry is the primary comparison—not a pre-assumed numerical
`e/Phi` placement. Fixed constants are a separate secondary specificity layer.

## WHEN

Coordinates are computed at path length `4096`. Generator parameter families,
radial log-spans and random seeds are divided into calibration and untouched
holdout sets before generation. All primary gates are scored on holdout paths.

## WHERE

Use the complex plane with independently declared radius and phase:

`z_t = r_t exp(2 pi i u_t)`.

The phase/history coordinate is the unit-circle projection `u_t`; the radial
coordinate is retained rather than normalized away. This deliberately gives
both candidate Di-ARA cuts native information.

## WHY

T348 calibrated path/history geometry on a fixed-radius circle and therefore
could not fairly test the older radial cut. T349 asks whether local state and
ordered history are distinct useful relations, redundant views, or a possible
child-to-parent interface.

## HOW

### Referee generators

The five phase generators and calibration/holdout parameter split remain the
T348 definitions, but use `24` replicates per parameter and T349-specific
seeds. Radial log-radius is linear over the observation:

`log r_t = sign × span × (t/(N-1) - 1/2)`.

`sign=-1,0,+1` declares contraction, neutral and expansion. Calibration spans
are `0.35, 0.75, 1.15`; untouched spans are `0.55, 0.95, 1.35`. Neutral paths
remain at radius one. No tested mathematical constant determines these spans.

### Frozen coordinates

Let `g = log(|z_N|/|z_0|)` and freeze `g_ref=0.75`. The radial state reading is

`x_L = 1 + tanh(g/g_ref)`.

It has exact reciprocal reflection `x_L(-g)=2-x_L(g)` and ridge `x_L=1`.

Let `delta_t = arg(z_{t+1} conjugate(z_t))`. The signed orientation reading is

`x_C = 1 + sum(sin delta_t)/sum(|sin delta_t|)`,

with a ridge fallback of one when the denominator vanishes.

`x_P`, `x_R` and `C(H)` retain the T348 calculations exactly and operate only
on the unit-circle phase projection. Generator labels, radial labels and
parameters do not enter those calculations.

### Frozen interventions

1. **Radial inversion:** `r_t -> 1/r_t`, phase unchanged.
2. **Phase reflection:** `u_t -> -u_t mod 1`, radius unchanged.
3. **Chronology destruction:** shuffle phase values only; retain the chronological
   radius sequence.
4. **Same-endpoint/different-history:** shuffle only the interior phase values,
   retaining the first and last complex states, radius sequence and visited
   phase multiset.

### Frozen gates

All thresholds apply to untouched holdouts.

1. **G1 radial recovery:** median `x_L<0.75` for contraction, `0.75<=x_L<=1.25`
   for neutral, and `x_L>1.25` for expansion; fixed-ridge radial-class accuracy
   at least `95%` overall and at least `90%` within every phase family.
2. **G2 history recovery across radius:** T348 broad-sector accuracy at least
   `85%` overall and at least `80%` within every radial family. Rotation
   coherence exceeds `0.90`; chaos and stochastic coherence remain below
   `0.25`; irrational best coherent miss improves from lag 64 to 512 in at
   least `80%` of holdouts.
3. **G3 radial inversion:** median absolute radial reflection error below
   `0.01`; median absolute changes in `x_C`, `x_P`, `x_R` and mean closure
   coherence below `0.02`.
4. **G4 phase reflection:** median absolute orientation reflection error below
   `0.01`; median absolute changes in `x_L`, `x_P`, `x_R` and mean closure
   coherence below `0.02`.
5. **G5 chronology specificity:** for periodic, irrational and chaotic paths,
   shuffling increases median `x_R` by at least `0.50`; median absolute changes
   in `x_L` and `x_P` remain below `0.10`. Rotation closure coherence falls by
   at least `0.50`.
6. **G6 endpoint/history distinction:** endpoint-preserving interior shuffling
   changes the endpoint by less than `1e-12`, increases median `x_R` by at least
   `0.50` for all three deterministic families, changes `x_L` and `x_P` by less
   than `0.10`, and lowers rotation closure coherence by at least `0.50`.
7. **G7 factorial independence:** holdout median `x_L` range across the five
   path families is below `0.02` within each radial family; holdout median
   `x_P` and `x_R` ranges across radial families are each below `0.02` within
   each phase family.
8. **G8 constant specificity (reported separately):** one universal fixed
   reciprocal amplitude passes only if mean absolute log error is below `0.10`
   and at least `80%` of non-neutral holdouts are within `0.10`. The geometry
   verdict does not depend on this constant gate.

Gates 1–7 must all pass for `SUPPORTED [synthetic state/history interface
calibration only]`. G8 retains its own supported/not-supported verdict.

## Controls and forbidden leakage

- Labels and generator parameters are referee truth only.
- Holdout radial spans, phase parameters and seeds are not used to change any
  coordinate, threshold or gate.
- No Phi, `1/e`, `e`, octave or fitted constant enters generation or primary
  coordinate normalization.
- The phase/history coordinates must be calculated from the same formulas as
  T348.
- Descriptive trajectory images never enter scoring.

## Chart contract

1. **State plane:** scatter of `x_L` versus `x_C`, colour by radial family,
   marker by phase-history family, fixed 0–2 axes and ridge lines.
2. **History plane:** scatter of `x_P` versus `x_R`, colour by phase family,
   marker fill/style by radial family, fixed 0–2 axes and ridge lines.
3. **Intervention arrows:** paired radial inversion and chronology-destruction
   effects, showing which coordinate moves.
4. **Factorial matrix:** 15-cell heatmap/table with radial and path-sector
   accuracies and sample counts.
5. **Constant specificity:** log-error comparison for fixed reciprocal
   candidates against calibration-fitted radial-strength controls.

Use blue/gold/orange/olive/pink roots plus neutral greys; no result relies on
colour alone. Export CSV, JSON, Markdown and static PNG; inspect the rendered
figure before reporting.

## Evidence boundary

The factors are independent by construction. Passing T349 proves that the
declared measurements can preserve and distinguish those factors under the
frozen synthetic conditions. It does not establish physical orthogonality,
causation, universal constants, or the ARA generative hypothesis.

