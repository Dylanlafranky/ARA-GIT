# Q10-Q14 sphere-first re-evaluation

**Date:** 24 July 2026  
**Status:** `POST-RESULT CONSTRUCT AUDIT / FROZEN NUMBERS AND GATES UNCHANGED`  
**Scope:** Q10 unresolved geometry through Q14 child-swap diagnostic  
**Controlling ARA object:** one complete sphere/wave identity; each scalar is one declared diameter cut or
allocation view; children, cuts, protocols and rungs must not be treated as interchangeable.

## Answer first

The Q10-Q14 numbers reproduce and the saved validators remain internally consistent. The main correction is not
numerical. It is the identity hierarchy.

The four quantities called children in Q13,

\[
R_A,\ R_B,\ H_A,\ H_B,
\]

are most faithfully classified as **four ARA coordinate children within a two-parent protocol comparison**:

- Ramsey versus Hahn is a change of pulse protocol and physical time grid;
- A versus B is visible compact relation versus purity-loss summary;
- all four values are calculated from reconstructed density matrices rather than four independent sensors;
- every amplitude trace is independently normalized to its own observed minimum and maximum.

ARA child status is relational and does not require an independently measured elementary subsystem. Ramsey and
Hahn are therefore two valid protocol-conditioned ARA parent paths, each with a visible A child and unresolved B
child. They are not an observed parent-to-child rung transition or four simultaneous laboratory subsystems. The
strong Q13 amplitude relation is real, but an ordinary common progression through decoherence explains it at least
as well as the proposed unique latent-child interpretation.

The corrected ARA reading is:

\[
\boxed{
\mathcal R=\mathcal C(R_A,R_B,J_R),
\qquad
\mathcal H=\mathcal C(H_A,H_B,J_H)
}
\]

inside the larger comparison:

\[
\boxed{
\mathcal Q_{RH}
=
\mathcal C_\times(\mathcal R,\mathcal H,J_{RH}).
}
\]

The unsupported stronger reading is that one unique hidden child generates the other three or that these four
coordinate children are four independently measured physical subsystems. Full quadrant correction:
`Q13_Q14_RAMSEY_HAHN_QUADRANT_REAUDIT_2026-07-24.md`.

## 1. The centered quantum hierarchy

At each state, protocol and wait, the complete measured parent is the reconstructed two-qubit density matrix:

\[
\underbrace{\rho}_{\text{measured two-qubit parent}}
=
\frac14\left[
I\otimes I
+\underbrace{\mathbf a\cdot\boldsymbol\sigma\otimes I}_{\text{qubit-A child state}}
+\underbrace{I\otimes\mathbf b\cdot\boldsymbol\sigma}_{\text{qubit-B child state}}
+\underbrace{\sum_{ij}T_{ij}\sigma_i\otimes\sigma_j}_{\text{retained A-B relation}}
\right].
\]

This is the clean Information³ placement already recovered in Q9:

\[
\text{Child A}+\text{Child B}+\text{their relation}\longrightarrow\text{parent}.
\]

Inside the relation tensor, Q8's \(u\), \(v\) and \(K\) are typed directional cuts:

\[
C=u+iv=Re^{i\theta},
\qquad
K=|ZZ|.
\]

They reconstruct about \(98\%\) of the measured tensor structure in these Bell trajectories. This is the clean
sphere-first interpretation: several declared directional cuts recover most of one parent relation.

The later quantities must be placed below that hierarchy:

| Quantity | Sphere-first classification |
|---|---|
| \(V=K+R\) | compact scalar summary of expressed parent relation |
| \(P=2(1-\operatorname{Tr}\rho^2)\) | purity-loss allocation computed from the same parent |
| \(H=2-K-R\) | contextual residual in one normalized ledger |
| \(C_H=(x_H-1)+i(y_H-1)\) | phase portrait of that residual's amplitude and rate |
| \(E=C_P+C_V\) | discrepancy between two locally normalized parent summaries |
| \(m_0,m_F,m_S,m_{FS}\) | Walsh/Hadamard symmetry coordinates across Bell labels |
| Ramsey/Hahn | two protocol-conditioned ARA parent paths; not nested rungs |

Items in the right column may be valid ARA coordinate children once their parent boundary, observable and direction
are declared. Independent measurement and dynamical closure are additionally required before calling one an
autonomous physical channel or completed child sphere.

## 2. Data and calculation checks

The audit used the saved Q8-Q14 CSV and JSON artifacts. It did not alter any frozen runner, protocol, gate or
result.

### 2.1 Local normalization fixes every amplitude trace to the same endpoints

For every one of the eight Q11 trajectories:

\[
\min x_V=\min x_P=0,
\qquad
\max x_V=\max x_P=2.
\]

This is correct for a local shape comparison, but it removes absolute magnitude and guarantees common endpoint
coverage. High amplitude-shape correlation therefore means that the **within-window progression shape** repeats;
it does not establish equal physical energy, one universal child amplitude or a completed TE-ARA boundary.

### 2.2 Standard Bell-core geometry explains the purity-loss complement

For an ideal compact Bell correlation block with persistent cut \(K\) and two transverse cuts of radius \(R\),
the standard two-qubit purity contribution is:

\[
\operatorname{Tr}\rho_{\rm core}^2
=
\frac{1+K^2+2R^2}{4}.
\]

The corresponding half-scale unresolved allocation is:

\[
P_{\rm core}=2\left(1-\operatorname{Tr}\rho_{\rm core}^2\right).
\]

Against the measured purity-loss coordinate, this known same-parent proxy gave:

| Condition | Correlation | Mean absolute error |
|---|---:|---:|
| Ramsey | `0.999149` | `0.035239` |
| Hahn | `0.995538` | `0.052120` |

For comparison, Q11's reported linear \(H=2-K-R\) correlations were `0.974867` and `0.988051`.

Thus Q11's strong visible/unresolved anti-relation is expected primarily from the established relation between
the same parent's correlation strength and purity. It remains a valid ARA crosswalk between two coordinate
children, but it is not evidence that they are independently measured physical subsystems.

### 2.3 A simple progression control challenges Q13's hidden-child reading

Within each Bell identity, median correlations with ordinal wait stage were:

| Q13 amplitude view | Median \(r\) with stage |
|---|---:|
| \(R_A\) | `-0.967855` |
| \(R_B\) | `+0.908709` |
| \(H_A\) | `-0.916875` |
| \(H_B\) | `+0.910872` |

The four amplitudes therefore share a strong common decay/progression coordinate before any latent-child model
is introduced.

Using the same held-out Bell identities as Q13, a two-parameter linear ordinal-stage model removed median
off-diagonal amplitude covariance:

\[
\boxed{0.980694}
\]

compared with:

\[
\boxed{0.916136}
\]

for Q13's selected supplied child \(H_B\).

The linear stage model uses no revealed candidate-child value from the held-out rows. A more flexible
leave-one-identity-out stage template reached `0.999797`, but that value is descriptive because its per-stage
lookup is more flexible.

For direction, the two-parameter linear stage model was weak (`0.028427` median reduction); quadratic and cubic
stage models reached `0.619299` and `0.909966`, showing that direction contains nonlinear progression but also
warning that only eleven stages make flexible comparisons unstable.

The key methodological consequence is:

> Q13's within-trajectory permutation null proves that aligned progression matters. It does not distinguish one
> hidden child from the ordinal stage shared by all four locally normalized trajectories.

### 2.4 Q11 anti-phase versus an ordinary stage template splits by protocol

A leave-one-Bell-identity-out target-stage template gave these mean two-axis errors:

| Condition | Q11 ARA anti-phase | Ordinary stage template |
|---|---:|---:|
| Ramsey | `0.311976` | `0.187658` |
| Hahn | `0.114834` | `0.171814` |

The ordinary template is better in Ramsey; the parameter-free anti-phase relation is better in Hahn. This is
consistent with Q10-Q13's repeated finding that Hahn follows a cleaner shared path while Ramsey contains more
state-specific directional structure. It does not support one universal hidden-child relation across both
protocols.

## 3. Revised interpretation by test

### Q10 — valid open coordinate child; autonomous physical closure remains open

Q10 successfully gives \(H\) two non-redundant coordinates: amplitude and opening/closing rate. This is a valid
decompression of a scalar residual. No trajectory closes a loop, and \(H\) is still defined from the parent
ledger. Therefore Q10 shows a reproducible **partial phase portrait of an open ARA coordinate child**, not a
completed independent physical child sphere.

Frozen result: `9/9` gates remains unchanged.

### Q11 — complementary same-parent coordinate children

The anti-phase geometry is real and especially clean in Hahn. The standard Bell-core purity identity explains
why it occurs. The best interpretation is two valid ARA coordinate children describing complementary portions
of one parent's deformation, with a retained residual. They are not independently measured physical subsystems.

Frozen result: `10/10` gates remains unchanged; its evidence ceiling is a same-sphere relation calibration.

### Q12 — radial/common and angular/label modes

The Hadamard modes are exact coordinate axes. Under the sphere-first reading:

- \(m_0\) is principally a common radial/decoherence deformation;
- \(m_F\) and \(m_S\) describe Bell-family and sign/orientation structure;
- \(m_{FS}\) is the coupled interaction required to close the label plane.

Calling them coordinate children remains acceptable if the word is kept explicitly representational. They are
not four physical child systems. The held-out failure correctly shows that the interaction axis is load-bearing.

Frozen result: `6/10` gates remains unchanged.

### Q13 — two parents/four coordinate children retained; unique latent generator not supported

The strong amplitude result is better described as a common radial/progression mode shared by four ARA children.
The selected \(H_B\) is not unique, direction fails, and an ordinary linear stage coordinate removes more
amplitude covariance than \(H_B\). The frozen statement that “a supplied child removes shared covariance” remains
numerically true, but it is not ARA-specific evidence for one hidden Phase B generating three relations. The
direction matrix instead has two large modes (`51.17%` and `42.40%`), so Q13's one-latent direction model was
under-dimensioned for the proposed quadrant.

Frozen result: `6/10` gates remains unchanged. Construct status:
`COMMON PROGRESSION SUPPORTED / FOUR-INDEPENDENT-PHYSICAL-SUBSYSTEM AND UNIQUE-LATENT-CHILD READING NOT
SUPPORTED`.

### Q14 — correct numerical rejection of the wrong rung proxy

Q14 shows that the same observable types correspond across Ramsey and Hahn more closely than crossed observable
types. Under the restored geometry, no completed rung boundary was established between the two protocols, so an
extra swap was not predicted. A label swap is also not the Hadamard rotation that makes ideal Ramsey/Hahn control
functions perpendicular. Q14 therefore does not test the two-parent/four-child quadrant.

Frozen result: `2/12` gates remains unchanged. It rejects the unmatched swap proxy and supplies no direct evidence
for or against the completed-rung flip law.

## 4. What remains strong in the quantum arc

The strongest ARA-compatible quantum results remain:

1. **Q1:** several diameter cuts retain information that one cut discards; same-information ARA and Bloch accounts
   are exactly equivalent.
2. **Q4-Q5:** actual local qubit subsystems can sit near their reduced-state ridge while their measured relation
   strongly identifies the Bell parent.
3. **Q6B-Q7:** the parent relation has several independent axes, and physical dephasing contracts them
   directionally from three strong axes to one; Hahn changes the traversal rate.
4. **Q8:** perpendicular relation cuts plus persistent parity reconstruct about \(98\%\) of the measured parent
   tensor.
5. **Q9:** Child A + Child B + their full relation reconstructs the parent density matrix exactly; parent radius
   fixes hidden-cut magnitude but not mirror direction.

These are faithful examples of one sphere being read through several cuts, of a parent carrying relation
information absent from its local children, and of direction being indispensable. They are established quantum
geometry translated into ARA language, not a new derivation of quantum mechanics.

## 5. Required next test

A genuine next-rung/hidden-child test needs:

1. an independently measured physical child or environment channel rather than another function of \(\rho\);
2. a common physical clock or a predeclared map between protocol times;
3. a native magnitude account in addition to local `0–2` normalization;
4. a standard master-equation/Kraus-channel and time-only comparator;
5. a predeclared parent boundary and child boundary;
6. for a flip test, an independently identified completed TE-ARA seam separating the two measurements.

Controlled trajectories with known dephasing, depolarizing, bit-flip, phase-flip and amplitude-damping channels
would be the cleanest next calibration. A later blind channel or new device would then test whether the same
sphere-cut rule transfers.

## Bottom line

The quantum data continue to fit the ARA sphere language well, but the fit is strongest at the level of:

\[
\boxed{
\text{whole state}
\leftrightarrow
\text{multiple directional cuts}
\leftrightarrow
\text{retained child relation}
}
\]

The Q10-Q14 attempt to recursively open the unresolved region was useful because it exposed both a common radial
mode and missing directional dimension. The data contain two Ramsey children and two Hahn children at the larger
comparison boundary. They do not yet establish that the residual is an autonomous closed physical sphere, that
Ramsey and Hahn are nested rungs, that the measured output paths remain exactly perpendicular, or that one hidden
Phase B generates the other three children.
