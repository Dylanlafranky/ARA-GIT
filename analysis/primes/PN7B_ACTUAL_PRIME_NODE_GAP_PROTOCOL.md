# PN7B actual-prime node / traversal-gap protocol

**Test ID:** `PN7B/ACTUAL-PRIME-NODE-GAP/OPENED-R10-R11-v1`  
**Declared:** 19 July 2026, before generating any PN7B actual-prime gap aggregate or result  
**Evidence class:** registered structural test on already-open decimal windows  
**Protected material:** do not construct the p31 primorial wheel and do not open R12

## 1. Question

Test Dylan's corrected direct pair:

> Treat each actual prime as a connection node, the traversal into and out of that node as its gap pair, and the
> ordered frequency of those node-gap states as the larger wave. Does the same ARA relation recur across decimal
> rungs, and does it retain ordered structure beyond gap inventory alone?

This differs from PN1-PN1I, which primarily studied **primorial-wheel candidate gaps**, and from PN2-PN7A, which
studied p29-candidate survival or removal. PN7B uses actual consecutive primes and actual consecutive-prime gaps.

It is not a prime predictor: actual-prime labels are required to construct the object being measured.

## 2. Frozen windows and roles

Use only the already-open intervals:

- R7: `[10,000,000, 10,100,000)`
- R8: `[100,000,000, 101,000,000)`
- R9: `[1,000,000,000, 1,010,000,000)`
- R10: `[10,000,000,000, 10,100,000,000)`
- R11: `[100,000,000,000, 101,000,000,000)`

R7-R9 contextualize development-scale convergence. R10 and R11 are the registered evaluation pair. They are
historically opened, so this is not a blind prediction; however, the PN7B operator and criteria are fixed before
their actual-prime gap aggregates are generated.

Within each interval, discard only the first and last prime as incomplete boundary nodes. Do not import a prime from
outside the interval to close either boundary.

## 3. Native node-gap ARA

For three consecutive actual primes,

\[
\underbrace{p_{i-1}}_{\text{previous connection}}
<
\underbrace{p_i}_{\text{measured prime node}}
<
\underbrace{p_{i+1}}_{\text{next connection}},
\]

define the incoming and outgoing traversal gaps

\[
\underbrace{g_i^-}_{\substack{\text{incoming traversal}\\\text{into the node}}}
=p_i-p_{i-1},
\qquad
\underbrace{g_i^+}_{\substack{\text{outgoing traversal}\\\text{from the node}}}
=p_{i+1}-p_i.
\]

The primary ARA diameter reading is

\[
\underbrace{x_i}_{\substack{\text{node-gap ARA state}\\0<x_i<2}}
=
\frac{2g_i^+}{g_i^-+g_i^+},
\qquad
\underbrace{a_i}_{\substack{\text{centred asymmetry}\\-1<a_i<1}}
=x_i-1
=
\frac{g_i^+-g_i^-}{g_i^-+g_i^+}.
\]

Interpretation is frozen as:

- `x<1`: the incoming gap is larger;
- `x=1`: incoming and outgoing gaps are equal at the node ridge;
- `x>1`: the outgoing gap is larger;
- `g^-+g^+`: retained raw local traversal span, not discarded by the audit.

This orientation may not be reversed after results. The mapped log-ratio `log(g+/g-)` is a one-to-one coordinate
control and may not be claimed as independent corroboration.

## 4. The larger frequency and order appearances

Use 24 fixed equal ARA bins on `[0,2]` for the primary test. Sensitivities are 12 and 48 bins.

For each rung retain:

1. `F_r`: normalized frequency of node states across ARA bins — **how often each mix occurs**;
2. `T_r`: normalized ordered plane of consecutive states `(x_i,x_(i+1))` — **how one mix hands to the next**;
3. first-half and second-half versions of both, assigned by the prime-node number-line position;
4. mean centred asymmetry and mirror relation `F_r(x)` versus `F_r(2-x)`;
5. raw incoming/outgoing gap totals and local-span inventory for audit.

The frequency curve alone is not treated as the full wave because it discards order. The transition plane alone is
not treated as independent evidence because consecutive ARA readings share one raw gap. Both must be reported.

## 5. Frozen controls

The primary objects remain direct ARA counts. Controls are diagnostic and may not replace them.

### 5.1 Distant gap-pair control

Freeze offset `delta=257` in prime-gap index. Construct

\[
x_i^{(257)}=\frac{2g_{i+257}}{g_i+g_{i+257}}.
\]

This preserves the rung's raw gap inventory while breaking the immediate prime-node pairing.

### 5.2 Distant state-transition control

Compare the observed handover `(x_i,x_(i+1))` with `(x_i,x_(i+257))`. This preserves the observed ARA-state
inventory while breaking immediate ordered adjacency.

### 5.3 Split-half stability

Use the distance between first-half and second-half direct shapes as the measurement-noise/stationarity reference.
The controls must differ from the direct object by more than this internal instability before the pair is called
non-trivial.

## 6. Frozen metrics

- Pearson correlation and Jensen-Shannon divergence in bits for `F`.
- Cosine similarity and Jensen-Shannon divergence in bits for flattened `T`.
- Total-variation distance for direct-versus-control and split-half comparisons.
- Smoothed cross-entropy in bits per node using additive `1/2` count in every ARA bin.
- Mean `a`, mirror correlation, and exact counts for integrity.

Zero-count transition cells remain zero for geometric distances. Smoothing is used only for cross-entropy.

## 7. Registered conditions

### P1 — frequency-wave recurrence

R10 versus R11 must have `corr(F10,F11) >= 0.995` and `JSD(F10,F11) <= 0.002` bits.

### P2 — ordered-handover recurrence

R10 versus R11 must have `cosine(T10,T11) >= 0.990` and `JSD(T10,T11) <= 0.010` bits.

### P3 — the local node pairing is not gap-inventory alone

At both R10 and R11,

`TV(F_direct,F_gap-offset257) > 5 * TV(F_first-half,F_second-half)`.

### P4 — the immediate handover is not state-frequency alone

At both R10 and R11,

`TV(T_direct,T_state-offset257) > 5 * TV(T_first-half,T_second-half)`.

### P5 — rung transfer

On R11 node states, the R10 frequency model must have lower cross-entropy than both the R9 frequency model and the
R10 distant-gap-pair control.

### P6 — scale convergence

`JSD(F10,F11) < JSD(F9,F10)` and `JSD(T10,T11) < JSD(T9,T10)`.

### P7 — reversible ridge symmetry

At both R10 and R11, mirror correlation must be at least `0.995` and `abs(mean(a)) <= 0.002`.

The **direct pair core** is P1+P2+P3+P4. Overall pass count is reported separately. Failure is preserved without
changing bins, offset, orientation or thresholds.

## 8. Interpretation fences

A passing result may support only:

> Actual prime nodes possess a scale-recurring incoming/outgoing gap ARA shape, and its immediate ordered relation
> contains structure not reproduced by the same rung's gap inventory or ARA-state frequency alone.

It does not establish that:

- ARA generates primes or predicts unknown prime locations;
- the 0-2 coordinate contains information absent from the raw gap pair;
- the cause is physical wave propagation;
- all higher-order structure is unique to ARA;
- a universal Time wave has been isolated.

A failed core means this direct prime-node/gap representation did not meet its declared recurrence and non-triviality
conditions on these windows. Earlier wheel and sieve results remain separate.

## 9. Reproducibility requirements

1. Hash this protocol before constructing PN7B aggregates.
2. Stream exact prime positions from deterministic sieving; do not retain an arbitrary sampled subset.
3. Reconcile prime totals with the terminal counts already recorded by PN3A/PN5/PN6.
4. Save direct/control counts, metrics, a bounded curve table and a static figure.
5. Run an independently coded validator that does not import the scorer.
6. Execute a reader-facing notebook top to bottom.
7. Record the result in `FableConvo/ARA_MAPPING_PRIMES.md` without overwriting PN7A.

