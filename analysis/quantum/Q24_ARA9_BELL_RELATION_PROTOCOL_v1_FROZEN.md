# Q24 ARA^9 Bell connected-relation protocol v1 — FROZEN

**Protocol ID:** `Q24-ARA9-BELL-RELATION-v1`  
**Ledger ID:** `T280`  
**Frozen:** 26 July 2026, before calculating the Q24 connected tensors or Q24 metrics  
**Test class:** prior-geometry identification and already-open public-data calibration  
**Source family:** Figshare DOI `10.6084/m9.figshare.14160476.v2`

## Evidential status before calculation

This is not a blind Bell prediction. The four public Bell records, their fifteen reconstructed Pauli expectations,
and the Q6/Q6B correlation-tensor singular values were already open.

The geometry being identified predates the quantum test:

- archived Script 201 described ARA^9 as “three systems × three axes = nine couplings” on 23 April 2026;
- the 16 July working formalism retained both a three-axis/two-step nine-reading packet and a separate
  nine-coefficient three-axis coupling operator;
- Q6/Q6B later assembled a \(3\times3\) two-parent relation tensor without identifying it as that older ARA^9
  coupling object.

Q24 therefore asks whether the older ARA^9 bookkeeping is an exact and useful crosswalk for the already-open
Bell relation. A pass is a calibrated identification, not independent confirmation of universal fractality.

## ARA-first question

Each of two parent identities has three declared diameter cuts, \(X,Y,Z\). Retaining every ordered cross-parent
pair supplies nine relation slots:

\[
\mathcal A^{(9)}_{AB}
=
\begin{pmatrix}
XX&XY&XZ\\
YX&YY&YZ\\
ZX&ZY&ZZ
\end{pmatrix}.
\]

Does the relation that remains after removing the two parents' separate contributions show the frozen
ARA closure ladder

```text
three retained relation directions -> one retained direction -> no retained direction
Bell parent                         -> classical mixture      -> uniform mixture
```

in both the raw-current reconstruction and the standard physical-state companion?

## Eligible source layers

### Primary ARA layer

Use the checksum-locked Q5 raw-current reconstruction without a density-matrix projection:

- `Q5_BELL_FOUR_STATE_RESULTS.json`;
- the four public ZIP archives and decoder frozen in `Q5_BELL_FOUR_STATE_PROTOCOL_v1_FROZEN.md`.

“Raw” here means the fifteen linear Pauli expectations reconstructed from the classified current records. It
does not mean unclassified ADC samples. No clipping, positivity projection, tensor diagonalization, Bell-label
fit, or outcome-dependent axis selection may occur before the Q24 ARA relation is formed.

### Established-physics companion

Apply the same Q24 equations to the positive-semidefinite, unit-trace Q6B states. This companion may test
robustness to the established physical-state constraint, but it does not replace or redefine the primary ARA
layer.

## Frozen ARA^9 construction

For every entity, define the three cuts of the first parent and second parent:

\[
\mathbf a=
\begin{pmatrix}
\langle XI\rangle\\
\langle YI\rangle\\
\langle ZI\rangle
\end{pmatrix},
\qquad
\mathbf b=
\begin{pmatrix}
\langle IX\rangle\\
\langle IY\rangle\\
\langle IZ\rangle
\end{pmatrix}.
\]

Define the measured nine-slot joint field

\[
T_{ij}=\langle \sigma_i\otimes\sigma_j\rangle,
\qquad i,j\in\{X,Y,Z\}.
\]

The frozen ARA “informative third” is the connected relation

\[
\boxed{
C=T-\mathbf a\mathbf b^\mathsf T
}.
\]

Plainly: \(\mathbf a\mathbf b^\mathsf T\) is what the nine slots would contain if the two local child readings
combined without an additional parent relation. \(C\) is the part that cannot be reconstructed from those two
separate readings alone.

Map every connected relation to the ARA diameter:

\[
\boxed{X^{(9)}_{ij}=1-C_{ij}}.
\]

Thus \(C_{ij}=+1,0,-1\) map to ARA \(0,1,2\). Raw finite-sample estimates are not clipped if they exceed the
physical interval slightly; the excursion must be reported.

## Frozen entities

Physically prepared public records:

1. `Phi-plus`
2. `Phi-minus`
3. `Psi-plus`
4. `Psi-minus`

Equal-state-weight reconstructed controls:

5. `Phi-classical = 0.5 Phi-plus + 0.5 Phi-minus`
6. `Psi-classical = 0.5 Psi-plus + 0.5 Psi-minus`
7. `Bell-uniform-mixed = 0.25` times all four Bell states

Controls must be mixed at the expectation/density level first. Their connected relation must then be calculated
from the mixed local cuts; connected tensors may not be averaged directly.

## Frozen metrics

For each connected tensor \(C\), calculate descending singular values

\[
s_1\ge s_2\ge s_3\ge0.
\]

They are read side by side as:

| Mathematics | ARA reading |
|---|---|
| singular direction of \(C\) | independent parent-relation direction |
| \(r_{0.5}=\#\{s_i\ge0.50\}\) | retained relation directions |
| \(h=|\det C|^{1/3}\) | three-direction closure strength |
| \(b=s_3/s_1\) | weakest/strongest directional balance |
| \(\det C<0\) | orientation-reversing or flipped three-axis relation |

Also calculate the relation-dominance share

\[
D_R=
\frac{\|C\|_F^2}
{\|C\|_F^2+\|\mathbf a\|_2^2+\|\mathbf b\|_2^2}.
\]

This is a bounded bookkeeping ratio, not TE-ARA and not a new physical energy.

Report:

- every raw and physical \(T,C,X^{(9)}\) cell;
- \(s_1,s_2,s_3,r_{0.5},\det C,h,b,D_R\);
- raw ARA range and maximum excursion beyond \(0\!-\!2\);
- raw-versus-physical differences.

## Frozen bootstrap

- seed: `2026072624`;
- replicates: `2,000`;
- resample complete classified records with replacement inside each prepared state and measurement orientation;
- rebuild all fifteen expectations, local vectors, joint tensors and connected tensors;
- form each control from the independently resampled prepared-state expectations;
- do not clip or physically project the primary bootstrap;
- report percentile 95% intervals and the frozen state-classification fractions.

## Frozen gates

All empirical gates must pass for `CALIBRATED`. A source/schema failure gives `INCONCLUSIVE`; any clean gate
failure gives `NOT CALIBRATED`.

### Raw ARA^9 geometry

1. `R1`: affine recovery residual \(\max|C-(1-X^{(9)})|\le10^{-12}\).
2. `R2`: every prepared Bell state has \(r_{0.5}=3\).
3. `R3`: every prepared Bell state has \(s_3\ge0.50\).
4. `R4`: both classical controls have \(r_{0.5}=1\).
5. `R5`: the uniform control has \(r_{0.5}=0\).
6. `R6`: the retained-direction sequence is exactly `3,3,3,3 / 1,1 / 0`.
7. `R7`: every Bell state has \(h\ge0.75\), while every reconstructed control has \(h\le0.30\).
8. `R8`: every Bell state has directional balance \(b\ge0.70\); both classical controls have \(b\le0.15\).
9. `R9`: every Bell state has relation-dominance share \(D_R\ge0.95\).
10. `R10`: every Bell state has \(\det C<0\).

### Resampling and companion checks

11. `B1`: every Bell state has `r=3` and negative determinant in at least `95%` of raw bootstrap draws.
12. `B2`: each classical control has `r=1` and the uniform control has `r=0` in at least `90%` of draws.
13. `P1`: the physical companion reproduces the exact `3,3,3,3 / 1,1 / 0` ladder.
14. `P2`: raw and physical classifications agree for all seven entities.

### Representation checks

15. `I1`: for the fixed proper rotations in the runner, singular values, \(h\), \(b\), \(D_R\), and determinant
    are invariant to at most `1e-12`.
16. `I2`: replacing each Bell \(C\) with its rank-one singular-value compression reduces retained directions
    from three to one; its determinant residual is at most `1e-12`, so \(h=0\) analytically.

## Interpretation boundary

A pass may say:

> The pre-existing ARA^9 three-axis coupling object maps exactly onto the full two-parent Bell relation tensor.
> In these public records, the connected nine-slot object distinguishes three-direction Bell closure, one-direction
> classical closure and zero-direction uniform mixing, and the classification survives raw resampling and a
> standard physical-state constraint.

A pass may not say:

- ARA predicted or discovered the Pauli tensor, Bell states, CHSH or entanglement;
- nine is statistically unique among all possible representations;
- every ARA^9 slot is independent;
- the result proves universal fractality, TE-ARA ontology, phi, consciousness, quantum gravity or a new quantum law.

The strongest legitimate result is a precise prior-geometry crosswalk plus a non-flattening relation
decomposition. A genuinely new test would need to freeze an ARA^9 transformation or outcome on untouched
quantum data.
