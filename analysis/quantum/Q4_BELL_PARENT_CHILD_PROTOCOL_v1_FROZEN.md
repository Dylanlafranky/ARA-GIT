# Q4 public Bell parent/child ARA protocol v1 — FROZEN

**Protocol ID:** `Q4-BELL-PARENT-CHILD-v1`  
**Ledger ID:** `T262`  
**Frozen:** 24 July 2026, before opening raw current values or analysis-script contents  
**Source audit:** `Q4_BELL_PARENT_CHILD_DATASET_AUDIT_2026-07-24.md`  
**Fidelity:** `Q4_BELL_PARENT_CHILD_FIDELITY_v1.md`  
**Status:** FROZEN

## Primary question

Does a public real \(\Phi^-\)-type Bell-state tomography record show the frozen ARA parent/child pattern:

> local child cuts near the `1.0` ridge, but a strongly structured parent relation on `XX`, `YY`, and `ZZ`?

## Eligible source

Use only Figshare file `26690663`, `UPUP-DOWNDOWN.zip`, MD5
`8cd8a5f2b3b9a2ccd090e47312bcc390`.

The author script may be used after freeze solely to document the raw binary format, acquisition-index mapping,
parity calibration and the standard fifteen-projection reconstruction. Any source-supplied final density matrix,
fidelity, plotted projection value or precomputed Bell-state verdict is forbidden as a predictor or substituted
outcome.

## Projection groups

The fifteen frozen projection labels are:

`ZZ, YZ, XZ, ZY, ZX, YY, YX, XY, XX, YI, XI, IY, IX, ZI, IZ`.

Define:

- **local children:** `YI, XI, IY, IX, ZI, IZ`;
- **same-axis parent relation:** `XX, YY, ZZ`;
- **mixed pair controls:** `YZ, XZ, ZY, ZX, YX, XY`.

For each recovered expectation \(\langle P\rangle\), map

\[
x_P=1-\langle P\rangle.
\]

## Primary estimation

Recover the fifteen Pauli expectations from raw current traces using the documented acquisition and parity
calibration. Retain every complete acquisition block independently where the source permits.

Report:

- every block-level and pooled Pauli expectation;
- every ARA coordinate;
- bootstrap intervals over complete acquisition blocks, or over the highest valid independent source grain if
  fewer than five complete blocks exist;
- raw and calibration exclusions;
- comparison with a direct standard Pauli reconstruction using exactly the same recovered expectations.

No sign, axis label, threshold, block, or projection may be chosen after viewing its agreement with the frozen
Bell pattern.

## Frozen empirical gates

All gates must pass for `SUPPORTED`.

| Gate | Requirement |
|---|---:|
| G1 local-child mean absolute expectation | `<= 0.20` |
| G2 same-axis signs | `XX < 0`, `YY > 0`, `ZZ > 0` |
| G3 weakest same-axis absolute expectation | `>= 0.50` |
| G4 same-axis mean magnitude minus local-child mean magnitude | `>= 0.40` |
| G5 mixed-pair mean absolute expectation | `<= 0.25` |
| G6 Bell correlation product `XX*YY*ZZ` | `<= -0.125` |
| G7 closest ideal Bell sign pattern | `Phi-minus`, with MAE margin `>= 0.20` over runner-up |
| G8 ARA/Pauli affine residual and pole-reversal residual | both `<= 1e-12` |

If the source permits at least five independent complete acquisition blocks, G1-G6 must also hold in at least
`80%` of blocks using the same thresholds. If fewer than five valid independent blocks exist, the pooled verdict
is retained but explicitly classified as single-record evidence.

Any clean gate failure gives `NOT SUPPORTED`. Source/schema/calibration ambiguity that prevents a defensible raw
reconstruction gives `INCONCLUSIVE`.

## Controls

1. **Local-only compression:** show that the six local child cuts cannot distinguish the four ideal Bell labels;
   this is an algebraic control, not a learned classifier.
2. **Relation-label shuffle:** permute the recovered parent-axis labels across `XX`, `YY`, `ZZ`; report how often
   the frozen \(\Phi^-\) sign pattern survives.
3. **Projection destruction:** pair each same-axis expectation with a mixed-axis label while preserving the
   marginal value distribution; the parent pattern should fail.
4. **Same-information standard account:** Pauli and ARA coordinates must be exactly affinely equivalent.

## Required interpretation

A pass may say:

> In this real prepared Bell-state record, locally ridge-like child marginals coexist with strong structured
> parent correlations, and the frozen three-cut relation identifies the expected Bell parent.

It may not say:

- ARA discovered Bell states or entanglement;
- local `1.0` proves resonance, cancellation or hidden consciousness;
- three cuts are universally sufficient for arbitrary two-qubit tomography;
- the result proves Information³, universal fractality, TE-ARA ontology, phi, quantum gravity or a new quantum
  law.

The standard-physics reading remains primary: this is an experimental Bell-state tomography record tested through
a frozen ARA parent/child crosswalk.

