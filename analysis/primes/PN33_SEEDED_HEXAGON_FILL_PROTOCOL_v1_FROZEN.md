# PN33 seeded-hexagon fill and rung doubling - protocol v1 FROZEN

**Frozen:** 22 July 2026, before target fill coordinates or gap summaries were calculated  
**Status:** REGISTERED  
**Orientation:** independent connection constraint accumulates upward from local `0` to local `2`; absolute spacing is retained when the local coordinate resets.  
**Fidelity:** `PN33_SEEDED_HEXAGON_FILL_FIDELITY_PACKET_v1_DRAFT.md`; Dylan verdict `EXACT ENOUGH TO TEST`.

## Registered claim

A completed prime-connection generation does not instantly produce another completed generation. The next prime gate
is the first connection in a newly expanded identity. Later independent prime gates progressively fill that identity.
Completion occurs when the inverse density of wheel survivors has doubled relative to the generation's starting
baseline. The doubled raw scale is retained and only the normalized local fill resets.

This protocol does **not** test instant `N -> 2N` closure, a literal six-prime hexagon, a constant Phi transition or a
constant-cost prime generator.

## Frozen arithmetic object

For every prime gate `p`,

\[
W(p)=\prod_{r\le p}r,
\qquad
D(p)=\frac{W(p)}{\varphi_E(W(p))}
=\prod_{r\le p}\frac{r}{r-1}.
\]

`D(p)` is inverse survivor density, equivalently the mean spacing of residues surviving the completed wheel. Euler's
totient `varphi_E` is distinct from the golden ratio.

For baseline gate `b`,

\[
R_b(p)=\frac{D(p)}{D(b)},
\qquad
x_b(p)=2\frac{\log R_b(p)}{\log2}.
\]

The seed is the first prime gate after `b`. The completion gate is

\[
c_b=\min\{p>b:R_b(p)\ge2\}.
\]

The completion overshoot is

\[
\epsilon_b=R_b(c_b)-2.
\]

At the next generation, set `b_new=c_b`, retain `D(c_b)` as the absolute baseline, and restart local progress at
`x_(b_new)=0`. The first prime after `c_b` is a small positive seed reading, not another completed `2`.

## Target firewall

No target coordinates or gap summaries are to be calculated before this protocol and its manifest are hashed.

The target baselines are selected deterministically, without inspecting their completion locations:

1. **primary:** the smallest prime gate greater than or equal to `10,000`;
2. **scale check A:** the smallest prime gate greater than or equal to `1,000`;
3. **scale check B:** the smallest prime gate greater than or equal to `3,000`.

For each baseline, walk consecutive prime gates until the first `R_b(p)>=2`. The hard computational ceiling is
`p=200,000,000`. Failure to complete the primary generation below that ceiling is `INCONCLUSIVE`, not a null.

The two scale checks overlap the primary gate record and therefore test scale consistency, not independent
replication. Independent replication requires a later disjoint generation or separate implementation.

Coordinate generation may identify prime gates by deterministic exact arithmetic, but it must not compute, display or
score target prime-gap summaries. Freeze and hash the coordinate table first. A separate scorer then attaches the raw
consecutive gaps already implied by the gate sequence.

## Frozen geometry disclosure

Split each completed generation into eight bands on the local coordinate:

\[
[0,.25),[.25,.5),[.5,.75),[.75,1),
[1,1.25),[1.25,1.5),[1.5,1.75),[1.75,2].
\]

For each band record sample count, mean, median, interquartile range, 10th/90th percentiles, every raw gap, and the
first and last worked event. Plot raw `D(p)` and locally reset `x_b(p)` separately. Mark the seed, `x=1`, nearest gate
to golden Phi, first `x>=2`, overshoot `epsilon`, and seed-child square `q^2`. Phi and `q^2` are descriptive landmarks,
not inferential endpoints in PN33.

## Frozen ARA transfer prediction

Normalize the observed prime-gap scale by the first band's median. The no-fit ARA curve is

\[
\widehat G_{ARA}(x)=2^{x/2}.
\]

It predicts scale multipliers `1`, `sqrt(2)` and `2` at local coordinates `0`, `1` and `2`. This applies to a robust
population gap scale, not every individual prime gap.

## Primary endpoints

Use the primary baseline for the status verdict.

1. **Direction:** Spearman correlation between the eight ordered band centres and their median raw gaps is positive.
2. **Doubling:** final-band / first-band median-gap ratio has a 95% moving-block-bootstrap interval containing `2` and
   excluding `1`.
3. **Curve:** report log-MAE of all eight normalized band medians against `2^(x/2)`.
4. **Reset:** after completion, the next seed's local coordinate is below `0.25`, while its absolute spacing baseline
   remains at least twice the preceding baseline, apart from recorded discrete overshoot.

Use 10,000 moving-block bootstrap resamples, block length 64 consecutive gaps, seed `33001`. If either endpoint band
contains fewer than 500 gaps, doubling is `INCONCLUSIVE`.

## Controls and rivals

Run the same band summaries and error metrics for:

1. **PNT:** `G_PNT(p)=log(p)/log(b)`;
2. **raw gate count:** equal progress per gate, ignoring `q/(q-1)`;
3. **raw integer doubling:** completion at `p=2b`;
4. **fixed polygon count:** generation sizes of `6`, `12` and `24` new gates;
5. **order-broken fill:** 1,000 permutations of the frozen `q/(q-1)` increments, seed `33002`.

The PNT comparison is load-bearing. Matching it establishes a clean ARA crosswalk to known prime-density scaling;
it does not establish new prime mathematics. An ARA-specific residual claim requires lower held-out log-MAE than PNT
by at least `5%` on the primary baseline and the same direction on both scale checks. This residual threshold is
secondary and must not replace the geometry verdict.

## Decision rule

- **SUPPORTED spacing expression:** direction and doubling pass, the curve is no worse than PNT by more than `5%`,
  and both scale checks have the same direction.
- **SUGGESTIVE:** direction passes and the endpoint estimate is nearer `2` than `1`, but uncertainty or one scale
  check blocks support.
- **NULL:** measurement is adequate but the coordinate does not organize gap scale beyond the flat/order-broken
  controls.
- **NOT SUPPORTED:** adequate target data show the opposite direction or a final/first interval excluding `2` in
  favour of a materially different value.
- **INCONCLUSIVE:** the primary generation or endpoint sample requirements do not complete under the frozen ceiling.

Separately report:

1. **benchmark verdict:** ARA versus PNT and rivals;
2. **geometry verdict:** seed, fill, ridge, completion, overshoot, reset and retained absolute scale.

Even a supported result proves neither literal spatial hexagons nor Phi causation. It tests the signed
spacing-capacity decompression of the broader ARA claim.

## Reproducibility contract

The implementation must be deterministic, self-contained, runnable from a fresh clone, and produce:

- frozen coordinate CSV and hash manifest;
- scored band/gap table;
- result JSON;
- executed notebook;
- geometry figure;
- report with both verdicts;
- independent validator and validation JSON.

