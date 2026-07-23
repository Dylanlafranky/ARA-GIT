# MX10 — Cross-Rung State-Contraction Test

**Protocol version:** 2.0, frozen before corrected outcome calculation  
**Freeze date:** 2026-07-23  
**Status:** prospective corrected analysis of reused public data

## Why v2 exists

The v1 dry run exposed a source-geometry error: the recorded electric
components are staggered by half a grid cell. Pairing equal array indices would
combine different physical locations. V1 is invalidated and preserved. V2
changes only source alignment and the external rungs forced by the resulting
common domain; its hypothesis, fit rule, comparators, metrics, and decision
thresholds remain unchanged.

## Question

Does the same two-channel ARA state geometry obey one transferable
coarse-graining law when the observation scale is doubled?

MX9 proves that a positive two-channel coherency matrix has an exact ARA
diameter on every declared axis. MX10 tests the stronger, non-algebraic claim
that one scale multiplier learned at the first spatial rung predicts state
contraction at later rungs, later times, different component pairings, and a
different plasma simulator.

The block sizes are controlled observation rungs, not discovered physical
octaves. A pass supports transferable coarse-graining; it does not alone prove
universal physical fractality.

## Sources and split

### Warp development and held-out time transfer

- Public `openPMD-example-datasets/example-2d/hdf5` Warp 4 series.
- Electric-field components `E/x`, `E/y`, and `E/z`.
- Development: iterations 255–320 inclusive in steps of 5.
- Quarantine: iterations 325–350 inclusive in steps of 5; not scored.
- Held out: iterations 355–400 inclusive in steps of 5.

### PIConGPU external simulator transfer

- Public PIConGPU 0.5.0 openPMD snapshot `simData_200.h5`, iteration 200.
- Electric-field components `E/x`, `E/y`, and `E/z`.
- All planes normal to all three grid axes are used after collocation.

## Frozen collocation

For each mesh axis, the common target offset is one half cell. A component
recorded at offset 0 is linearly averaged with its next neighbour along that
axis. A component already recorded at offset 0.5 is unchanged. Only the common
interior physical domain shared by all three collocated components is retained.
No wraparound, padding, or outcome-dependent shift is allowed.

- Warp becomes 50×200 after collocation, then is centre-cropped to 48×192.
- PIConGPU becomes 31×31×31 after collocation. Each 31×31 plane is
  centre-cropped to 24×24.

## Declared Phase-A/Phase-B observations

Evaluate all three unordered pairs:

1. `(E_x, E_y)`
2. `(E_y, E_z)`
3. `(E_z, E_x)`

A/B labels declare orientation. Swapping them cannot change the
axis-independent state radius used here.

## Block state and field statistic

For collocated real samples \(A_j,B_j\) in one non-overlapping block:

\[
G=
\begin{pmatrix}
\langle A^2\rangle&\langle AB\rangle\\
\langle AB\rangle&\langle B^2\rangle
\end{pmatrix},
\qquad
T=\operatorname{tr}G,
\]

\[
r=
\frac{\sqrt{(2G_{AB})^2+(G_{BB}-G_{AA})^2}}{T},
\qquad 0\le r\le1.
\]

For one plane and pair at block width \(b\):

\[
D_b=\frac{\sum_{\rm blocks}T\,r}{\sum_{\rm blocks}T}.
\]

Larger blocks mix differently oriented children. Contraction toward the state
ball interior represents unresolved child mixing, not energy loss.

## Frozen rungs and transferable law

- Warp rungs: \(b\in\{1,2,4,8,16\}\).
- PIConGPU rungs: \(b\in\{1,2,4,8\}\), limited by the unbiased collocated
  common domain.

The common one-parameter law is

\[
\widehat D_b=b^{-\beta}.
\]

It is anchored at \(D_1=1\). Learn only from Warp development \(1\to2\):

\[
\widehat\beta
=-\frac{\operatorname{mean}_{\rm development,pairs}\log D_2}{\log2}.
\]

No later rung, held-out iteration, or external plane may alter it.

## Comparators

1. Flat/no contraction: \(\widehat D_b=1\).
2. Independent 2-D mixing: \(\widehat D_b=b^{-1}\).
3. Pair-specific development law: one development-\(D_2\) exponent per pair.
4. Local one-step law: each scored plane/pair uses its own \(D_2\) to predict
   its larger rungs.

## Metrics and frozen decision

Primary error is mean absolute log error (MALE). Also report median absolute
percentage error, signed log error, rung and pair breakdowns, and 95% bootstrap
intervals resampled by iteration or plane.

The common law receives:

- **internal support** if held-out Warp MALE beats both fixed comparators, is
  no more than 20% above the local law on rungs 4–16, and no more than 10%
  above the pair-specific law;
- **external support** if PIConGPU MALE beats both fixed comparators and is no
  more than 25% above the local law on rungs 4–8;
- **strong cross-rung support** only if both pass;
- **partial support** if internal passes and external fails;
- **not supported as one transferable law** if internal fails.

Exact MX9 bounds and aggregation remain mathematical results whatever MX10
finds. MX10 tests only the stronger common scale-law claim.

## Required outputs

- versioned JSON with hashes, observations, coefficients, metrics, confidence
  intervals, and verdict;
- readable report;
- independent direct-source validation on a deterministic subset;
- preserved v1 invalidation trail.
