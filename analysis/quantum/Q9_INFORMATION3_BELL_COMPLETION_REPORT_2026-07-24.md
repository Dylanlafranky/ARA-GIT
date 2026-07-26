# Q9 Information³ Bell closure and masked-child completion

**Test ID:** `Q9-INFORMATION3-BELL-COMPLETION-v1`  
**Ledger ID:** `T268`  
**Date:** 24 July 2026  
**Verdict:** `NOT CALIBRATED — 5/9 frozen gates passed`  
**Result class:** exact state closure supported; signed masked-child completion not supported

## Answer first

The Information³ instruction produced one exact result, one strong structural result and one important failure.

1. **Exact whole-state closure:** Child A + Child B + their relation reconstructed every one of the `88`
   two-qubit density matrices to numerical precision.
2. **Strong unresolved-information bridge:** Q8's linear unresolved coordinate \(H\) tracked independently
   calculated loss of observable two-qubit purity with correlation `0.981999`.
3. **Failed signed-child filling:** the hidden perpendicular child's magnitude remained recoverable, but the
   attempted temporal lock chose its positive/negative mirror side correctly only `62.5%` of the time.

The result sharpens the framework. The missing item is not mainly the child's size; it is **directional relation
information**. A parent radius and one diameter cut do not distinguish two mirror locations.

## Data and freeze status

The test reused Q7/Q8's `88` checksum-pinned public Bell-state records. The data were already open, so this is a
post-outcome mathematical test rather than a blind prediction.

The fidelity statement, formulas, controls and nine gates were frozen before calculating the Q9 allocation and
completion scores.

Protocol SHA-256:

`621760a7fed6cbf0a9f5832b9cca198f7cb4b45469bde38ef636c0db57d82fad`

## Lock 1 — two children plus their relation exactly form the state

Every two-qubit state has the standard Pauli decomposition:

\[
\boxed{
\underbrace{\rho}_{\substack{\text{complete measured}\\\text{parent identity}}}
=\frac14\left[
I\otimes I
+\underbrace{\mathbf a\cdot\boldsymbol\sigma\otimes I}_{\text{Child A}}
+\underbrace{I\otimes\mathbf b\cdot\boldsymbol\sigma}_{\text{Child B}}
+\underbrace{\sum_{ij}T_{ij}\sigma_i\otimes\sigma_j}_{\text{their relation}}
\right].
}
\]

This is an exact established-quantum realization of:

\[
\boxed{\text{Information A}+\text{Information B}+\text{their relation}
\longrightarrow\text{one parent identity}.}
\]

Across all `88` physical records:

- maximum density-matrix reconstruction error: `6.338e-16`;
- maximum purity-closure error: `2.220e-15`.

Plainly: neither child's information is enough, and merely placing both children beside each other is still
insufficient. Their measured relation is the third information needed to reconstruct the parent.

This exactness is not a new derivation; it is the standard Pauli-basis representation translated faithfully into
Information³/ARA language.

## Lock 2 — filling the complete information budget

Define:

\[
I_A=\lVert\mathbf a\rVert^2,\qquad
I_B=\lVert\mathbf b\rVert^2,\qquad
I_{AB}=\lVert T\rVert_F^2.
\]

The exact purity identity is:

\[
\boxed{
I_A+I_B+I_{AB}=4\operatorname{Tr}(\rho^2)-1.
}
\]

Relative to a pure two-qubit parent, the unresolved information is:

\[
\boxed{
I_{\rm unresolved}
=3-I_A-I_B-I_{AB}
=4\left(1-\operatorname{Tr}\rho^2\right).
}
\]

The filled allocation is therefore:

\[
\boxed{
\underbrace{I_A}_{\text{Child A}}
+
\underbrace{I_B}_{\text{Child B}}
+
\underbrace{I_{\rm core}}_{\text{Bell relation core}}
+
\underbrace{I_{\rm off}}_{\text{measured off-core relation}}
+
\underbrace{I_{\rm unresolved}}_{\text{missing from pure system boundary}}
=3.
}
\]

The compact Q8 Bell block dominated the measured relation. Median measured off-core shares were only:

- Ramsey: `0.015920`;
- Hahn: `0.019306`.

Plainly: only about `1.6–1.9%` of the measured relation information lay perpendicular to the compact Bell block
*inside the observed two-qubit tensor*. Most of Q8's growing unresolved allocation was therefore not a large
measured off-plane relation hiding elsewhere within the same tensor.

## What Q8's unresolved \(H\) was tracking

To place the exact squared-information budget beside Q8's linear TE-ARA account, compare:

\[
H=2-K-R
\]

with

\[
\frac{I_{\rm unresolved}}2
=2\left(1-\operatorname{Tr}\rho^2\right).
\]

Across all records:

\[
\boxed{
\operatorname{corr}\left(H,\frac{I_{\rm unresolved}}2\right)
=0.981999
}
\]

with mean absolute difference `0.076279`.

By condition:

| Condition | Correlation | MAE |
|---|---:|---:|
| Ramsey | `0.974867` | `0.094680` |
| Hahn | `0.988051` | `0.057879` |

Representative median allocations:

| Slice | \(H\) | \(I_{\rm unresolved}\) | \(I_{\rm unresolved}/2\) | purity |
|---|---:|---:|---:|---:|
| Ramsey initial | `0.070193` | `0.140057` | `0.070028` | `0.964986` |
| Ramsey final | `1.040902` | `2.052814` | `1.026407` | `0.486797` |
| Hahn initial | `0.113309` | `0.290842` | `0.145421` | `0.927289` |
| Hahn final | `1.150456` | `2.281143` | `1.140571` | `0.429714` |

Plainly: the grey unresolved region in Q8 behaves much more like information leaving the observable pure
two-qubit identity than like a large additional correlation rotating into another measured tensor direction.

This is compatible with a component becoming perpendicular to the selected system boundary. It does **not**
establish a coherent environmental wave. Reduced purity can also result from environmental entanglement,
classical averaging, preparation/readout limitations or the physical reconstruction procedure.

## Lock 3 — deliberately hiding the perpendicular child

For each of `72` interior trajectory points, the measured \(v_t\) was hidden.

The permitted lock supplied:

- visible child \(u_t\);
- parent transverse radius \(R_{s,t}\);
- the neighbouring \(v_{t-1}\) and \(v_{t+1}\) values to choose direction.

Magnitude:

\[
|v_t|
=\sqrt{\max(0,R_{s,t}^2-u_t^2)}.
\]

The two possible completions were \(+|v_t|\) and \(-|v_t|\). The frozen rule chose the one closest to the average
of the neighbouring values.

Results:

| Completion | MAE |
|---|---:|
| ARA/Information³ parent-radius + temporal branch | `0.180487` |
| zero fill | `0.250318` |
| time-only linear interpolation | `0.193574` |
| always-positive magnitude branch | `0.259325` |

The ARA completion improved zero fill by `27.90%` and the always-positive branch by `30.40%`, but missed the
frozen `50%` improvement gates. Sign accuracy was only:

\[
\boxed{62.5\%}
\]

versus the frozen `80%` requirement.

The result was better under the more slowly changing Hahn trajectory:

| Condition | ARA completion MAE | Time-only MAE | sign accuracy |
|---|---:|---:|---:|
| Ramsey | `0.239202` | `0.233725` | `58.33%` |
| Hahn | `0.121773` | `0.153422` | `66.67%` |

Plainly: Q8 showed that the parent radius closes the missing child's **size** accurately. Q9 shows that size does
not tell us which side of the diameter the child occupies. The samples can rotate across a mirror branch between
recorded waits, especially in Ramsey, so neighbouring scalar values do not reliably supply orientation.

This is a useful failure for Information³:

\[
\boxed{
\text{two magnitudes plus an undirected relation do not lock direction.}
}
\]

The informative third must retain orientation, ordering or another independent cut. It cannot merely restate the
parent's total size.

## Frozen-gate outcome

| Gate | Result |
|---|---:|
| `I1` — exact Information³ density reconstruction | PASS |
| `I2` — exact purity closure | PASS |
| `I3` — nonnegative allocation | PASS |
| `I4` — compact Bell block dominates measured relation | PASS |
| `I5` — signed completion MAE at most 0.08 | **FAIL** |
| `I6` — at least 50% improvement over zero fill | **FAIL** |
| `I7` — at least 50% improvement over positive-only branch | **FAIL** |
| `I8` — at least 80% sign accuracy | **FAIL** |
| `I9` — filled magnitude remains inside parent radius | PASS |

Independent validation rebuilt all `88` source records and all `72` masked completions, matched every audited
field with maximum difference `0.0`, and reproduced the `5/9` gate outcome.

## Scientific conclusion

Supported:

1. Child A + Child B + their relation exactly reconstruct the measured two-qubit parent.
2. Q8's compact Bell relation accounts for about `98%` of measured relation information.
3. Q8's unresolved linear \(H\) is an excellent empirical coordinate for loss of observable two-qubit purity in
   this dataset.
4. Parent radius supplies useful hidden-child magnitude information.

Not supported:

1. The frozen Information³ interpolation did not identify the hidden child's signed direction accurately enough.
2. The currently measured off-plane tensor components do not fill most of \(H\).
3. The test does not identify purity loss as a coherent perpendicular environmental wave.
4. This is not causal forecasting or a reduction in measurements: the parent radius is supplied from the current
   whole-state tensor.

The next valid test requires a genuinely directional third datum: denser time sampling, a known phase-evolution
operator, an additional independent measurement cut, or direct environment/system correlation measurements.

## Reproduction artifacts

- `Q9_INFORMATION3_BELL_COMPLETION_FIDELITY_v1.md`
- `Q9_INFORMATION3_BELL_COMPLETION_PROTOCOL_v1_FROZEN.md`
- `Q9_INFORMATION3_BELL_COMPLETION_PROTOCOL_v1_FROZEN.sha256`
- `Q9_INFORMATION3_BELL_ALLOCATIONS.csv`
- `Q9_INFORMATION3_BELL_COMPLETIONS.csv`
- `Q9_INFORMATION3_BELL_GATES.csv`
- `Q9_INFORMATION3_BELL_COMPLETION_RESULTS.json`
- `Q9_INFORMATION3_BELL_COMPLETION_VALIDATION.json`
- `q9_information3_bell_completion_test.py`
- `q9_information3_bell_completion_validate.py`

