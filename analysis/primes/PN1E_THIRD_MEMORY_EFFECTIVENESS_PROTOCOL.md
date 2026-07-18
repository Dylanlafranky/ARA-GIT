# PN1E third-memory predictive effectiveness and attribution protocol

**Protocol ID:** `PN1E/DEV/v1`  
**Status:** frozen development protocol  
**Date frozen:** 17 July 2026  
**Data status:** prime 23 is already-open development data; prime 29 must remain unopened  

## Dylan instruction being operationalised

> "Can you plain language it for me and then continue to the next test. I understand the third thing is helping, but I am not sure how effective we are at the moment. You're mentioning a comparison with Markov control, but I do not know the relational scale it is being compared on."

## Purpose

PN1D showed two facts on the complete prime-23 wheel:

1. a stable third spatial component improves a rank-2 description;
2. three successive 12-bin ARA readings retain conditional dependence beyond IID and first-order raw-gap Markov projections.

PN1E asks the practical next question: **how much does the extra ARA memory improve held-out next-reading prediction, on what scale, and which local ARA contexts and raw gap constellations supply the improvement?**

This remains exploratory development analysis. It is not a new blind prediction and cannot confirm transfer beyond prime 23.

## Frozen object and orientation

Use the same exact prime-23 circular gap cycle as PN1C and PN1D:

- gap count: `36,495,360`;
- period: `223,092,870`;
- gap-array SHA-256: `F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C`.

For each adjacent pair of positive gaps,

\[
x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2).
\]

Bin (x_i) into `B=12` equal bins on 0-2. A three-reading prediction event is

\[
X_{i-2},X_{i-1}\longrightarrow X_i,
\]

which is generated from four raw gaps

\[
(g_{i-2},g_{i-1},g_i,g_{i+1}).
\]

Thus all predictive scores are measured per **next 12-bin ARA reading**, not per prime, raw gap, or physical time unit.

## Test A - held-out predictive effectiveness

Split the complete circular relation sequence into two consecutive equal halves. Fit on half 1 and score half 2, then reverse.

Use fixed additive Jeffreys smoothing `alpha=0.5` for every categorical distribution.

### Models

1. `ARA-IID`: predicts the next ARA bin from its training-half marginal only.
2. `ARA-Markov-1`: predicts (X_i) from (X_{i-1}).
3. `ARA-Markov-2`: predicts (X_i) from ((X_{i-2},X_{i-1})).

### Primary score

Held-out cross-entropy in bits per next ARA reading:

\[
\mathrm{CE}=-\frac1N\sum_i\log_2\widehat P(X_i\mid\text{declared context}).
\]

Lower is better. Define:

\[
\Delta_{2|1}=\mathrm{CE}(\text{ARA-Markov-1})-\mathrm{CE}(\text{ARA-Markov-2}).
\]

Report also:

- relative log-loss reduction (\Delta_{2|1}/\mathrm{CE}(\text{ARA-Markov-1}));
- perplexity reduction (1-2^{\mathrm{CE}_2}/2^{\mathrm{CE}_1});
- top-1 and top-3 next-bin accuracy;
- multiclass Brier score.

### Development classification

- `STRONG PRACTICAL EFFECT`: Markov-2 beats Markov-1 in both directions, mean gain at least `0.05` bits/reading, and relative log-loss reduction at least `2%`.
- `SUGGESTIVE PRACTICAL EFFECT`: it wins both directions with mean gain at least `0.01` bits/reading or relative reduction at least `0.5%`.
- `WEAK OR ABSENT`: otherwise.

These thresholds classify development effect size only. They are not a p-value and do not promote the result to blind confirmation.

## Test B - locate the Markov-control scale

Using the full saved PN1D empirical, exact-IID-gap, and first-order-gap-Markov three-reading probability tensors, calculate for each model:

- (H(X_i\mid X_{i-1})): uncertainty with one visible ARA neighbour;
- (H(X_i\mid X_{i-2},X_{i-1})): uncertainty with two ARA neighbours;
- their difference, the conditional mutual information;
- the difference as a percentage of one-neighbour uncertainty.

The first-order raw-gap Markov control knows (P(g_{i+1}\mid g_i)) and is projected through the same 0-2 coordinate into the same 12 ARA bins. It is therefore a control at the **immediate raw-gap neighbour scale**, evaluated on the **same three-reading ARA scale**.

The empirical excess above that control is descriptive:

\[
I_{empirical}-I_{gap\ Markov}.
\]

Do not call this excess a percentage forecast improvement. It is extra conditional information after the control's one-neighbour gap structure is supplied.

## Test C - ARA-context attribution

For every observed context ((X_{i-2},X_{i-1})=(a,b)), calculate its contribution

\[
C_{ab}=P(a,b)D_{KL}\!\left[P(X_i\mid a,b)\,\|\,P(X_i\mid b)\right].
\]

The contributions sum to (I(X_{i-2};X_i\mid X_{i-1})). Save all active contexts and report:

- top 5, 10 and 20 context shares of total conditional information;
- each context's two ARA bin centres;
- its frequency, contribution in bits/reading, and dominant next bin;
- whether the dominant next bin changes relative to the one-step model.

## Test D - raw gap-constellation attribution

Count all observed circular raw-gap quadruples ((g_{i-2},g_{i-1},g_i,g_{i+1})). Map each quadruple to its three ARA bins and assign the local log-information term

\[
L=\log_2\frac{P(X_i\mid X_{i-2},X_{i-1})}{P(X_i\mid X_{i-1})}.
\]

For each distinct quadruple save:

- raw gap values;
- mapped ARA bin centres;
- occurrence probability;
- signed contribution (P(quadruple)L);
- whether it changes the Markov-1 top prediction.

Report the top 30 positive contributors and the total positive and negative contribution masses separately. This is attribution, not a causal genealogy.

## Robustness and exact checks

1. Protocol hash must match before analysis.
2. Gap count, period, parity, positivity, and frozen gap hash must match PN1C/PN1D.
3. Both train/test directions must be reported separately.
4. Repeat Test A at `B=8`, `B=12`, and `B=16`; `B=12` remains primary.
5. Verify that context contributions sum to empirical conditional mutual information within `1e-12` bits.
6. Verify that raw quadruple signed contributions sum to the same value within `1e-12` bits.
7. Independently reconstruct the p23 gaps and all primary model scores without importing the primary PN1E analysis.
8. Prime 29 must not be generated, opened, inferred from, or read.

## Evidence ceiling

PN1E may support statements about:

- the practical predictive value of two-step versus one-step ARA memory on p23;
- the immediate relational scale of the raw-gap Markov control;
- concentration of the effect in particular ARA contexts and raw gap constellations.

It cannot establish:

- exactly three waves;
- a physical third wave;
- transfer to prime 29 or another domain;
- unique superiority of ARA over every alternative representation;
- Riemann-Hypothesis, phi, universal-leak, or physical-universality claims.
