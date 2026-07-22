# PN25 pair-ridge compression protocol — frozen v1

**Frozen:** 22 July 2026, before target computation  
**Status:** prospective arithmetic scale-transfer test  
**Protected 87-bit anchor:** remains sealed and is not an input

## Correction being tested

The mod-14 survivor lanes are

\[
1,3,5,9,11,13
\]

with reversible pairs

\[
(1,13),\quad(3,11),\quad(5,9).
\]

The earlier proposal accidentally mixed **identity completeness** with **ridge position**. Every pair is one complete
identity, but the pair's directional odds are

\[
q(a)=\frac{a}{14-a},\qquad a\in\{1,3,5\},
\]

giving `1/13`, `3/11`, and `5/9`. These are successive readings of one pair-gradient, not three TE-ARA allocations
to be added.

Converting odds to an ARA total-2 composition gives

\[
x_A=\frac{2q}{1+q}=\frac a7,
\qquad
x_B=2-x_A=\frac{14-a}{7}.
\]

Thus every pair satisfies `x_A+x_B=2`, while the left-side ridge-closeness values are

\[
c(a)=\frac a7\in\left\{\frac17,\frac37,\frac57\right\}.
\]

The missing `(7,7)` pair would give `(x_A,x_B)=(1,1)`. It is absent from the survivor wheel because residue 7 is
divisible by the gate 7.

For any oriented survivor residue `r`, define

\[
x(r)=\frac r7,\qquad
c(r)=1-|x(r)-1|=\frac{\min(r,14-r)}7,
\qquad
s(r)=\operatorname{sign}(r-7).
\]

The six raw lanes are therefore represented exactly by three closeness classes plus one orientation bit.

## Questions

1. Does greater pair-ridge closeness predict fewer visible handovers before the next prime?
2. Does greater closeness predict a higher probability that the base candidate is already prime?
3. Does greater closeness predict closure within three candidate states?
4. Does the three-class pair compression retain nearly all predictive information available in the six raw residue
   lanes?
5. Along a candidate's handover path, does ridge-closeness tend to increase toward the terminal prime?

## Development source

Use the already-open PN24 sample of 2,000 anchors from `[4,000,000,000,4,001,000,000)`. It supplies frozen
development probabilities for:

- one global rate;
- two orientation rates;
- three pair-class rates;
- six raw-lane rates.

No target outcomes may be used to fit those probabilities.

## Fresh target ranges

These strings were searched in the prime-analysis repository before freezing and were absent. Draw 2,000 distinct
anchors from each interval:

| Scale | Interval | Seed |
|---|---|---:|
| low | `[61,000,000, 61,500,000)` | 25001 |
| middle | `[61,000,000,000, 61,000,500,000)` | 25002 |
| high | `[610,000,000,000, 610,000,500,000)` | 25003 |

Sampling rule: `sorted(random.Random(seed).sample(range(low,high),2000))`.

The three cohorts are scale-transfer targets. The protected 87-bit anchor remains sealed.

## Outcomes

For each anchor, reproduce the exact PN24 nearest-handover cascade from base gates `{2,7}` through the independently
verified next prime.

- `H`: visible handover count;
- `Y0 = 1[H=0]`: base upper child is already the next prime;
- `Y3 = 1[H<=2]`: exact prime reached within three candidate states;
- `c_initial`: closeness class of the initial upper child;
- `c_final`: closeness class of the terminal prime;
- `delta_c = c_final-c_initial`.

## Frozen primary predictions

### P1 — ordered handover prediction

For each target scale and in the pooled scale-stratified target:

\[
E[H\mid c=1/7] > E[H\mid c=3/7] > E[H\mid c=5/7].
\]

The pooled Pearson correlation between `c` and `H` must be negative. Its one-sided scale-stratified permutation
`p` value uses 10,000 fixed-seed (`25100`) permutations and must be below `0.01` for a strong pass.

### P2 — immediate ridge prediction

At every scale:

\[
P(Y0=1\mid1/7)<P(Y0=1\mid3/7)<P(Y0=1\mid5/7).
\]

### P3 — three-state closure prediction

At every scale:

\[
P(Y3=1\mid1/7)<P(Y3=1\mid3/7)<P(Y3=1\mid5/7).
\]

### P4 — upward path prediction

Pooled target paths must have `mean(delta_c)>0`, and the fraction with `delta_c>0` must exceed the fraction with
`delta_c<0`.

## Frozen compression comparison

Fit Bernoulli probabilities only on PN24 development data and score them without refitting on all 6,000 targets.
Score `Y0` and `Y3` using Brier loss for:

1. global constant;
2. orientation only;
3. three pair-closeness classes;
4. six raw residue lanes.

The pair compression passes its narrow fidelity test when its Brier loss is no more than 2% worse than the full
six-lane model for both outcomes:

\[
\frac{Brier_{pair}-Brier_{lane}}{Brier_{lane}}\le0.02.
\]

This tests information retention, not predictive usefulness. Separately report whether either model beats the global
baseline.

## Exact arithmetic checks

For every survivor lane:

- `q=a/(14-a)`;
- `2q/(1+q)=a/7` exactly as a rational number;
- pair TE-ARA shares sum exactly to 2;
- mirror residues have equal closeness and opposite orientation;
- `(7,7)` maps to `(1,1)` and is excluded by gate 7.

## Decision rule

- **Strong dynamic support:** P1–P4 all pass, including every-scale ordering, and pair compression fidelity passes.
- **Partial support:** exact coordinate and compression fidelity pass, with at least two dynamic predictions in the
  declared direction, but the strong P1 threshold or every-scale ordering fails.
- **Geometric-only support / dynamic null:** exact coordinate passes but fewer than two dynamic predictions pass.
- **Failure:** exact pair/TE-ARA identities fail or pair compression loses more than 2% versus raw lanes on either
  outcome.

If compression fidelity passes while both pair and lane models fail to beat the global baseline, report the pair
coordinate as a faithful compression of **non-predictive lane information**, not as a predictor.

## Controls and claim boundary

- Six raw lanes control whether discarding orientation loses information.
- Orientation-only and global models control whether pair closeness adds information.
- Scale-stratified permutation prevents a scale mixture from creating the primary correlation.
- All probability estimates are frozen from development; target data are scoring-only.
- The exact coordinate is a reparameterisation of mod-14 residue geometry. Predictive novelty requires target
  performance beyond matched residue controls.
- No result here establishes a faster prime algorithm, universal ARA geometry, or a physical energy law.
