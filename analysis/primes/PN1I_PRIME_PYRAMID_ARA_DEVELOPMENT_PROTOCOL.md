# PN1I/DEVELOPMENT/v1 — prime-gate, pyramid and plain-ARA tests

**Declared:** 17 July 2026, before computing the PN1I endpoints below.

**Status:** METHOD-LOCKED DEVELOPMENT ON OPENED RUNGS ONLY.

**Maximum generated prime:** 23.

**Prime 29 use:** saved aggregate PN1F/PN1G outputs only.

**Prime 31:** sealed and prohibited. PN1I must not generate, inspect or derive any prime-31 residue, gap, gate,
partial count or score. PN1H remains unchanged.

## Purpose

Test four readings supplied by Dylan after the PN1H freeze:

1. the new prime as a gate/singularity around a lift circle;
2. the parent as an apex over the largest admissible base of surviving children;
3. the recursive double-pyramid as a connected wave plus an Information^3 lock;
4. the ordinary ARA 0–2 coordinate, without requiring the pyramid interpretation.

These are development tests on already opened arithmetic data. Method-locking prevents endpoint drift but does not
turn them into prospective confirmations.

## Exact construction

For a parent wheel with period `P`, ordered reduced residues `r_i`, circular gaps `g_i`, and next prime `q`, define
the unique excluded lift

\[
t_i^*\in\{0,\ldots,q-1\},
\qquad
r_i+t_i^*P\equiv0\pmod q.
\]

Every parent has `q` lifted candidates, one excluded branch and `q-1` surviving children. The base width is therefore

\[
b_q=q-1,
\qquad
N_q=(q-1)N_{\mathrm{parent}}.
\]

The local deletion joins the incoming and outgoing parent gaps

\[
(g_{L,i},g_{R,i})=(g_{i-1},g_i)
\longrightarrow
G_i=g_{L,i}+g_{R,i}.
\]

Exact fan-out, one deletion per parent and the sum `G_i=g_L+g_R` are arithmetic calibration. They cannot count as
independent ARA evidence.

## Opened transitions

Primary generated transitions:

`5->7`, `7->11`, `11->13`, `13->17`, `17->19`, `19->23`.

Saved aggregate plain-ARA comparison extends through the already opened `23->29` result.

## Test A — prime-gate circle

In parent-residue order, `t_i^*` is the location of the removed branch on the `q`-position lift circle. Record:

- branch occupancy and total-variation distance from uniform;
- circular ordered transition mutual information `I(t_i^*;t_{i+1}^*)`;
- the same mutual information after 32 seeded order-destroying permutations preserving branch counts;
- the observed-minus-independent transition residual matrix.

The gate sequence is called ordered beyond marginals only when its observed transition mutual information exceeds the
largest of the 32 shuffled-order controls. Because this is a complete deterministic wheel, the control is an
order-destruction comparison, not population-sampling inference.

## Test B — maximum-base pyramid

Verify for every generated transition:

- exactly one excluded lift per parent;
- exactly `q-1` surviving branches per parent;
- no adjacent excluded candidates, so each local operation is a two-gap-to-one-gap merge;
- exact parent, child and deletion counts.

Crosswalk base width against the standard adjacent-gap ARA measurements already computed through prime 29:

- adjacent ARA mutual information;
- ordered-minus-Gap-Markov residual L2 where available;
- full visible A/B gain and exact shared-child gain at primes 23 and 29.

Report monotonicity and Spearman rank association descriptively. The `q-1` multiplier and cumulative event growth are
known arithmetic and cannot confirm a capstone-information claim by themselves.

## Test C — double-pyramid Information^3 lock

Use the ordinary gate ARA coordinate

\[
x_i=\frac{2g_{R,i}}{g_{L,i}+g_{R,i}}\in(0,2),
\]

with 12 fixed equal-width bins. Fit categorical models in eight contiguous circular folds with Jeffreys smoothing
`alpha=0.5`.

Predictors:

1. marginal baseline;
2. left gap only;
3. right gap only;
4. merged sum only;
5. ordered left/right pair;
6. prime-gate branch `t_i^*` only;
7. ordered pair plus gate branch.

Targets:

- lag 1: `x_(i+1)`, a connectivity calibration that shares the edge `g_i`;
- lag 2: `x_(i+2)`, the primary continuation endpoint, which shares no raw gap with `(g_(i-1),g_i)`.

The non-tautological pair contribution is

\[
\Delta_{pair}=G_{pair}-\max(G_L,G_R,G_{sum}),
\]

and the extra gate-relation contribution is

\[
\Delta_{gate}=G_{pair+gate}-\max(G_{pair},G_{gate}),
\]

where `G` is held-out log-loss gain over the marginal model in bits/event. Report overall and minimum-fold deltas.
Compare the lag-2 deltas with 16 seeded target permutations preserving all predictor and target marginals.

Do not use `G_i=g_L+g_R` as a prediction target. That equality is guaranteed by construction.

## Test D — plain ARA

Analyze `x_i=2g_R/(g_L+g_R)` directly, independently of pyramid language. For every transition report:

- mean coordinate;
- shares below, exactly at and above the `1.0` ridge;
- mean absolute distance from `1.0`;
- 12-bin entropy;
- reflection error between `p(x)` and `p(2-x)`;
- adjacent coordinate mutual information and shuffled-order controls.

Also retain the previously established child-wheel coordinate

\[
x_j^{wheel}=\frac{2g_{j+1}}{g_j+g_{j+1}}
\]

through prime 29 as the direct cross-rung ARA comparison.

## Outputs and fences

Required outputs:

- deterministic Python implementation;
- machine-readable JSON, CSV and NPZ inventories;
- two figures;
- executed reproducibility notebook;
- independently coded validation;
- technical report with a plain-language explanation after each test.

Interpretation must separate:

1. exact/known wheel arithmetic;
2. newly measured ordered structure;
3. compatibility with ARA;
4. any result that fails or remains ambiguous.

No result may be described as prime prediction, a proof of literal Euclidean pyramids, physical information flow,
the Riemann hypothesis, universal fractal geometry or a completed ARA cycle.
