# MX10 — Cross-Rung State-Contraction Test

**Protocol version:** 1.0, frozen before outcome calculation  
**Freeze date:** 2026-07-23  
**Status:** invalidated after the first run; retained as an audit trail

## Post-run invalidation note

The first run revealed that the electric components occupy different
half-cell-offset locations on the openPMD mesh. Equal array indices therefore
did not represent a collocated A/B observation. No v1 scientific verdict is
accepted. The original protocol and result are preserved, while corrected
collocation is frozen separately in protocol v2 before its outcomes are
calculated.

## Question

Does the same two-channel ARA state geometry obey one transferable
coarse-graining law when the observation scale is doubled?

MX9 proves that a positive two-channel coherency matrix has an exact ARA
diameter on every declared axis. MX10 tests a stronger, non-algebraic claim:
whether one scale multiplier learned at the first spatial rung predicts the
state contraction at later rungs, later times, different component pairings,
and a different plasma simulator.

This protocol does **not** call the imposed block sizes discovered physical
octaves. They are controlled observation rungs. A pass supports transferable
coarse-graining; it does not by itself establish universal physical fractality.

## Sources and split

### Development and held-out time transfer

- Public `openPMD-example-datasets/example-2d/hdf5` Warp 4 series.
- Electric-field components `E/x`, `E/y`, and `E/z`.
- Development iterations: 255–320 inclusive in steps of 5.
- Quarantine iterations: 325–350 inclusive in steps of 5; not scored.
- Held-out iterations: 355–400 inclusive in steps of 5.
- Each 51×201 field is centre-cropped deterministically to 48×192 so that all
  declared block rungs divide the same raw region.

### External simulator transfer

- Public PIConGPU 0.5.0 openPMD snapshot `simData_200.h5`, iteration 200.
- Electric-field components `E/x`, `E/y`, and `E/z`.
- All 32 planes normal to each of the three grid axes are used, producing 96
  raw 32×32 planes.
- This source was used by earlier ARA tests, but the MX10 statistic and outcome
  were not calculated before this protocol was frozen.

## Declared Phase-A/Phase-B observations

The three unordered electric-component pairs are evaluated without selecting a
favourite pair after seeing outcomes:

1. `(E_x, E_y)`
2. `(E_y, E_z)`
3. `(E_z, E_x)`

The labels A and B specify the declared measurement orientation only. Swapping
them reverses the population axis but cannot change the axis-independent state
radius used here.

## State at one block

For real samples \(A_j,B_j\) within one non-overlapping spatial block:

\[
G=
\begin{pmatrix}
\langle A^2\rangle & \langle AB\rangle\\
\langle AB\rangle & \langle B^2\rangle
\end{pmatrix},
\qquad
T=\operatorname{tr}G.
\]

The MX9 state radius is

\[
r=
\frac{
\sqrt{(2G_{AB})^2+(G_{BB}-G_{AA})^2}
}{T},
\qquad 0\le r\le1.
\]

At a one-cell block, a nonzero real two-channel sample is a pure boundary state
and \(r=1\). Larger blocks combine differently oriented children, so movement
toward the interior records unresolved child mixing. This is a contraction
measure, not energy loss.

For one field plane and component pair at block width \(b\), define the
activity-weighted state radius

\[
D_b=
\frac{\sum_{\mathrm{blocks}}T\,r}
{\sum_{\mathrm{blocks}}T}.
\]

## Frozen rungs and law

Use non-overlapping square block widths

\[
b\in\{1,2,4,8,16\}.
\]

The one-parameter log-rung law is

\[
\widehat D_b=b^{-\beta}.
\]

It is anchored at the exact one-cell boundary \(D_1=1\). Learn only from the
development-set transition \(1\rightarrow2\):

\[
\widehat\beta
=
-\frac{\operatorname{mean}_{\rm development,pairs}\log D_2}{\log2}.
\]

No later rung, held-out iteration, or external plane may alter
\(\widehat\beta\).

## Comparators

1. **Flat/no contraction:** \(\widehat D_b=1\).
2. **Independent 2-D mixing:** \(\widehat D_b=b^{-1}\).
3. **Pair-specific development law:** one \(\beta\) per component pair, fitted
   only from development \(D_2\). This tests whether the common law loses
   important pair identity.
4. **Local one-step law:** for each scored plane and pair, infer its own
   \(\beta_{\rm local}=-\log D_2/\log2\), then predict \(b=4,8,16\). This uses
   one local child transition and is therefore an adaptive reference, not a
   blind transfer model.

## Metrics

- Primary: mean absolute log error,
  \(\operatorname{MALE}=\operatorname{mean}|\log\widehat D-\log D|\).
- Secondary: median absolute percentage error, rung-wise bias, fitted exponent
  by pair, and bootstrap confidence intervals resampled by Warp iteration or
  PIConGPU plane.
- All finite nonzero-activity blocks are retained. No outcome trimming.

## Frozen decision rule

The common law receives:

- **internal support** if, on held-out Warp data, it beats both fixed
  comparators, its MALE is no more than 20% above the local one-step law on
  rungs 4–16, and its MALE is no more than 10% above the pair-specific law;
- **external support** if, on PIConGPU planes, it beats both fixed comparators
  and its MALE is no more than 25% above the local one-step law on rungs 4–16;
- **strong cross-rung support** only if both internal and external conditions
  pass;
- **partial support** if the internal condition passes but external transfer
  fails;
- **not supported as one transferable law** if the internal condition fails.

Regardless of verdict, exact MX9 state bounds and exact incoherent aggregation
remain mathematical results; MX10 tests only the stronger scale-law claim.

## Required outputs

- machine-readable JSON containing source hashes, all \(D_b\) observations,
  fitted coefficients, metrics, confidence intervals, and verdict;
- a readable Markdown report;
- an independent validation script that recomputes a disjoint deterministic
  subset directly from the HDF5 sources;
- no promotion beyond the frozen evidence boundary.
