# Q4 Public Bell Parent/Child ARA Test

**Ledger:** `T262`  
**Public source:** [Madzik and Asaad, Figure 2 — Bell states tomography](https://doi.org/10.6084/m9.figshare.14160476.v2)  
**Frozen verdict:** `SUPPORTED — 8/8 GATES`  
**Independent validation:** `21/21` checks passed  
**Confidence:** share with caveats

## Answer first

The frozen parent/child prediction was supported on raw public Bell-state tomography currents.

Before opening a current value or the authors' analysis code, Q4 predicted that the prepared
\(\Phi^-\)-type Bell state would look almost quiet on either qubit alone but strongly structured in the relation
between them. That is what the raw reconstruction returned:

- the six local child expectations averaged only `0.05833` in absolute magnitude, placing their ARA coordinates
  close to the `1.0` ridge;
- `XX = -0.95`, `YY = +0.95`, and `ZZ = +0.95`;
- the weakest parent correlation magnitude was `0.95`;
- the parent-versus-child magnitude contrast was `0.89167`;
- the signed three-correlation product was `-0.857375`;
- the \(\Phi^-\) ideal was the nearest Bell pattern by MAE `0.05`, with a `1.26667` margin over every runner-up.

In plain language: each child looks nearly featureless when compressed to its own local diameter, but the
cross-child relation carries a very strong parent identity.

This is real, pre-outcome evidence for the ARA parent/child **crosswalk**. It is not a discovery of Bell
entanglement or a new quantum law: standard quantum mechanics predicts exactly this kind of local-marginal versus
pair-correlation structure.

## Frozen geometry and recovered values

The standard Pauli expectation and ARA coordinate are related by

\[
x_P=1-\langle P\rangle.
\]

| Projection | Role | Pauli expectation | 95% record-bootstrap interval | ARA coordinate |
|---|---|---:|---:|---:|
| `XX` | same-axis parent | -0.950 | [-1.000, -0.875] | 1.950 |
| `YY` | same-axis parent | +0.950 | [+0.875, +1.000] | 0.050 |
| `ZZ` | same-axis parent | +0.950 | [+0.875, +1.000] | 0.050 |
| `XI` | local child | 0.000 | [-0.225, +0.225] | 1.000 |
| `YI` | local child | +0.050 | [-0.175, +0.275] | 0.950 |
| `ZI` | local child | +0.050 | [-0.175, +0.275] | 0.950 |
| `IX` | local child | -0.125 | [-0.326, +0.075] | 1.125 |
| `IY` | local child | -0.075 | [-0.300, +0.125] | 1.075 |
| `IZ` | local child | +0.050 | [-0.175, +0.275] | 0.950 |

The mixed pair controls also stayed comparatively close to the ridge: their mean absolute expectation was
`0.1125`. The largest was `XY=-0.20`.

## The three-cut lock

For two-qubit Pauli operators,

\[
(XX)(YY)=-ZZ.
\]

The frozen Bell relation therefore required

\[
\operatorname{sgn}\langle XX\rangle
\times
\operatorname{sgn}\langle YY\rangle
\times
\operatorname{sgn}\langle ZZ\rangle=-1.
\]

The data returned `(-,+,+)` with all three magnitudes at `0.95`. Two signs select the Bell quadrant; the third is
a consistency relation. This is a precise established-physics counterpart to the proposed Information³ lock:
two measured poles plus their closing relation identify the parent more fully than either child marginal.

## All frozen gates passed

| Gate | Result | Verdict |
|---|---:|---|
| local-child mean absolute expectation `<=0.20` | 0.05833 | pass |
| `XX<0`, `YY>0`, `ZZ>0` | -0.95, +0.95, +0.95 | pass |
| weakest same-axis magnitude `>=0.50` | 0.95 | pass |
| parent-minus-child magnitude `>=0.40` | 0.89167 | pass |
| mixed-pair mean magnitude `<=0.25` | 0.11250 | pass |
| `XX*YY*ZZ <= -0.125` | -0.857375 | pass |
| nearest Bell pattern is \(\Phi^-\), margin `>=0.20` | margin 1.26667 | pass |
| affine and pole-reversal residuals `<=1e-12` | 0, 0 | pass |

## Raw-data reconstruction

The archive contains nine directly measured orientations:

`II, IX, IY, XI, XX, XY, YI, YX, YY`.

Each orientation contains `80` classified measurement records. Each record contains four state-selective
segments, each built from `40` electron-spin readouts. The public MATLAB script documents:

- unsigned 16-bit current conversion;
- current threshold `0.1`;
- more-than-one-sample tunnelling detection;
- state presence when more than half of the forty readouts tunnel;
- the linear combinations that recover all fifteen Pauli expectations.

The Python reproduction reads the binary members directly from the checksum-verified ZIP and applies those
documented operations. It does not ingest a source-supplied density matrix, Bell fidelity or projection result.

## Controls and limits

- Local-only ideal marginals give one identical zero pattern for all four Bell states, so they cannot identify the
  parent.
- Only `2/6` permutations of the three relation labels preserve the frozen `(-,+,+)` sign placement.
- Even the best reassignment of three mixed-pair controls to the \(\Phi^-\) pattern has MAE `0.91667`, compared
  with `0.05` for the actual same-axis parent cuts.
- ARA and Pauli values are exactly affinely equivalent. That equality is expected mathematics.
- The archive provides one complete tomography set. The `2,000`-replicate record bootstrap measures variability
  within that acquisition; it is not an independent device, state, laboratory or day replication.
- The filename declares which Bell state was prepared. Q4 predicted the unopened geometry and magnitude gates,
  not an unknown label.

## Scientific meaning

Q4 is the cleanest real-data example so far of the warning against flattening a fractal identity:

\[
\text{quiet child cuts}
\;\not\Rightarrow\;
\text{quiet parent relation}.
\]

It supports using scale, boundary and relational direction explicitly. It also gives the framework a rigorous
quantum example of `1.0` being a projection ridge rather than a dead or empty system.

The next useful quantum test should replicate this structure on the other three unopened Bell-state archives
using their sign patterns frozen now, then hold out one Bell label or acquisition as a true discrimination test.

## Reproduction artifacts

- source audit and fidelity packet;
- frozen protocol and SHA-256;
- `q4_bell_parent_child_test.py`;
- `q4_bell_parent_child_validate.py`;
- record, projection and bootstrap CSVs;
- result and independent-validation JSON.

