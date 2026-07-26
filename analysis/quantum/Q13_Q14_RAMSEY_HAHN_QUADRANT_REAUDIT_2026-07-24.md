# Q13-Q14 Ramsey/Hahn quadrant re-audit

**Date:** 24 July 2026  
**Status:** `POST-RESULT CONSTRUCT CORRECTION / FROZEN Q13-Q14 GATES UNCHANGED`  
**Prompted correction:** ARA children are relational roles at a declared boundary and rung. They are not limited
to independently measured laboratory subsystems.

## Answer first

The previous sphere-first audit made a categorical mistake. It correctly noted that
\(R_A,R_B,H_A,H_B\) are not four independent physical subsystems, but incorrectly allowed that fact to demote
their ARA child status.

The faithful hierarchy is:

\[
\boxed{
\begin{aligned}
\mathcal R&=\mathcal C(R_A,R_B,J_R),\\
\mathcal H&=\mathcal C(H_A,H_B,J_H),\\
\mathcal Q_{RH}&=\mathcal C_\times(\mathcal R,\mathcal H,J_{RH}).
\end{aligned}
}
\]

Ramsey and Hahn are two complete protocol-conditioned ARA parent paths. Each is decompressed into an A/B pair:

\[
\boxed{
\{R_A,R_B,H_A,H_B\}
=
\text{four legitimate ARA coordinate children of the larger Ramsey/Hahn comparison}.
}
\]

They are not four simultaneously observed physical subsystems. That changes the evidential type, not their ARA
classification.

The quadrant proposal also has a precise established-physics home. For ideal pure dephasing over one common
interval with a midpoint Hahn refocusing pulse, Ramsey and Hahn are an exact sum/difference—or normalized
Hadamard—basis. Their **control/sensitivity paths are perpendicular**. The current Q13 data do not directly test
that perpendicularity because the original test matched unequal physical times by ordinal stage and fitted one
latent coordinate rather than two parent axes.

The corrected result is therefore:

- **supported:** two ARA parents, four ARA coordinate children, and strong A/B opposition inside both parents;
- **exact established crosswalk:** ideal Ramsey/Hahn sensitivity functions form an orthogonal sum/difference
  basis on a common interval;
- **not yet supported by these outputs:** a stable \(90^\circ\) angle between the measured Ramsey and Hahn state
  trajectories, or a literal causal transfer from one experimental run into the other;
- **still not supported:** one unique hidden child generating the other three.

## 1. Why the four children are valid ARA children

ARA's child label is indexed by the parent boundary, projection and rung. A parent-level branch may itself be a
complete lower-rung ARA with its own A/B pair. It does not need to be an elementary particle or an independently
instrumented subsystem.

Q11 supplies an A/B decomposition inside each protocol:

\[
\begin{aligned}
R_A&=C_{V,\mathrm{Ramsey}},
&
R_B&=C_{P,\mathrm{Ramsey}},\\
H_A&=C_{V,\mathrm{Hahn}},
&
H_B&=C_{P,\mathrm{Hahn}}.
\end{aligned}
\]

Here \(V\) is the compact visible Bell relation and \(P\) is the purity-loss/unresolved relation. Both are
calculated from reconstructed density matrices, but each is a time-ordered two-cut ARA coordinate carrying
amplitude and opening/closing direction.

The internal opposition is strong:

| Proposed parent | Median \(\cos(A,-B)\) | Median normalized closure error |
|---|---:|---:|
| Ramsey | `0.938439` | `0.197057` |
| Hahn | `0.999216` | `0.052362` |

This supports two A/B parent paths. It does not identify the B coordinate as one unique external physical
environment channel.

## 2. The exact Ramsey/Hahn quadrant in control space

For one dephasing-frequency history \(\delta\omega(t)\) over total duration \(T\), split the interval:

\[
\phi_1=\int_0^{T/2}\delta\omega(t)\,dt,
\qquad
\phi_2=\int_{T/2}^{T}\delta\omega(t)\,dt.
\]

Ideal Ramsey gives both halves the same sign:

\[
\Phi_R=\phi_1+\phi_2.
\]

An ideal Hahn echo applies a \(\pi\) refocusing pulse at the midpoint, reversing the sign of the second-half
phase accumulation:

\[
\Phi_H=\phi_1-\phi_2.
\]

Therefore:

\[
\boxed{
\begin{pmatrix}
\Phi_R\\
\Phi_H
\end{pmatrix}
=
\underbrace{
\begin{pmatrix}
1&1\\
1&-1
\end{pmatrix}
}_{\text{sum/difference transform}}
\begin{pmatrix}
\phi_1\\
\phi_2
\end{pmatrix}.
}
\]

After normalization by \(1/\sqrt2\), the matrix is orthogonal:

\[
\frac1{\sqrt2}
\begin{pmatrix}
1&1\\
1&-1
\end{pmatrix}
\left[
\frac1{\sqrt2}
\begin{pmatrix}
1&1\\
1&-1
\end{pmatrix}
\right]^{\mathsf T}
=I.
\]

The two sensitivity functions are:

\[
y_R(t)=1,
\qquad
y_H(t)=
\begin{cases}
+1,&0\le t<T/2,\\
-1,&T/2\le t\le T,
\end{cases}
\]

and their common-interval inner product is exactly:

\[
\boxed{
\langle y_R,y_H\rangle
=
\int_0^T y_R(t)y_H(t)\,dt
=\frac T2-\frac T2=0.
}
\]

This is the clean mathematical meaning of Ramsey and Hahn being perpendicular. Their four oriented branches

\[
\boxed{+\Phi_R,\ -\Phi_R,\ +\Phi_H,\ -\Phi_H}
\]

form the four cardinal directions of a control-coordinate quadrant. The transform is reversible:

\[
\phi_1=\frac{\Phi_R+\Phi_H}{2},
\qquad
\phi_2=\frac{\Phi_R-\Phi_H}{2}.
\]

In ARA language, the first and second half-interval phase children are recombined through two perpendicular
parent readings. The Hahn midpoint pulse is a physical sign handover. This is not a literal energy flow from a
Ramsey run into a Hahn run; the two protocols are alternative controlled histories of the same prepared system.

The source experiment explicitly uses free Ramsey waiting and Hahn echo with midpoint refocusing pulses:
`https://www.nature.com/articles/s41467-025-57987-0`.

### 2.1 Two four-child constructions must not be silently identified

The re-audit exposes two related but not yet identical four-coordinate accounts:

\[
+\Phi_R,\ -\Phi_R,\ +\Phi_H,\ -\Phi_H
\]

are the exact oriented branches of the ideal Ramsey/Hahn **control quadrant**. By contrast,

\[
R_A=C_{V,R},\quad R_B=C_{P,R},\quad
H_A=C_{V,H},\quad H_B=C_{P,H}
\]

are Q13's **derived visible/unresolved coordinate children**. The strong within-protocol opposition supports
grouping each Q13 pair as an A/B decomposition, but it does not prove the identifications

\[
(R_A,R_B,H_A,H_B)
\equiv
(+\Phi_R,-\Phi_R,+\Phi_H,-\Phi_H).
\]

That equality requires a common-clock experiment that measures signed phase-sensitive outputs and the
visible/unresolved allocation together.

The proposed cross-parent handover also needs an orientation convention. A four-quadrant cycle could be written,
for example,

\[
+\Phi_R\rightarrow+\Phi_H\rightarrow-\Phi_R\rightarrow-\Phi_H\rightarrow+\Phi_R,
\]

or in the reverse direction. This is the precise version of “Phase A of one hands to Phase B of the other,” but
the present Ramsey and Hahn runs do not themselves demonstrate that temporal cycle. They establish the
perpendicular control axes; a controlled path between those axes remains the next test.

### 2.2 The component that unravels and returns

The earlier “unravels and then comes back together” description refers most cleanly to **echo-refocusable phase
coherence**, not to Q13's uniquely identified hidden child.

For an ensemble of phase histories, the visible coherence is schematically

\[
C_R(T)
=
\left|
\left\langle e^{i(\phi_1+\phi_2)}\right\rangle
\right|
\]

under Ramsey. Slightly different frequency offsets make the individual phases fan out. Their coarse-grained sum
can shrink through cancellation even though the individual relative phases have not been erased.

Under Hahn,

\[
C_H(T)
=
\left|
\left\langle e^{i(\phi_1-\phi_2)}\right\rangle
\right|.
\]

For slowly varying or quasi-static offsets, \(\phi_2\approx\phi_1\), so the midpoint sign reversal causes those
phases to refocus. The temporarily missing signal was therefore still encoded in dispersed phase relations and
was recoverable by the echo operation.

The preferred ARA term is **refocusable dispersed phase relation** or **echo-recoverable coherence**. “Hidden”
is acceptable only if it means hidden from the chosen coarse-grained projection during the fan-out. It does not
mean a separately identified invisible particle, channel or unique child.

Because Ramsey and Hahn are applied to the same measured system and no completed rung boundary has been
established between them, the current ARA parity rule retains the labels across the protocol comparison:

\[
\boxed{
R_A\leftrightarrow H_A,
\qquad
R_B\leftrightarrow H_B.
}
\]

The echo-recoverable dispersed relation therefore belongs in the **\(H_B\) slot** while it is fanned out. The
return to visible coherence occurs inside Hahn's own cycle:

\[
\boxed{
H_A
\xrightarrow{\text{dephase}}
H_B
\xrightarrow{\pi\text{ pulse and rephase}}
H_A.
}
\]

This corrects the tempting but unsupported shortcut \(R_B\rightarrow H_A\). A B-to-A label exchange between
Ramsey and Hahn would require an independently established odd completed-rung separation. Q14 instead found that
same-label correspondence was much better than an extra crossed-label swap.

One evidence boundary remains: Q13's \(H_B=C_{P,H}\) is a derived unresolved/purity coordinate. It is the correct
ARA location for the candidate relation, but it has not yet isolated the echo-recoverable microscopic phase
distribution from irreversible decoherence, environmental coupling and measurement loss.

The current public dataset supports the existence of a refocusable component because Hahn delayed the
three-axis-to-one-axis contraction by `11.45x` relative to Ramsey. It does not continuously observe a complete
departure-and-return trajectory. Q10 explicitly found derivative reversals but no full closed loop inside the
available observation window. Thus:

\[
\boxed{
\text{echo-refocusable relation supported}
\quad\neq\quad
\text{complete hidden-child cycle directly measured}.
}
\]

### 2.3 Q8's `unresolved H` is the original Phase-B candidate

The repeated letter `H` obscured the lineage. Q8's grey **unresolved \(H\)** does not mean Hahn. It is the
TE-ARA remainder

\[
\boxed{
H_{\rm unres}=2-K-R,
}
\]

where \(K\) is persistent parity and \(R\) is the resolved transverse phase relation. As \(R\) contracted,
\(H_{\rm unres}\) accumulated. That made it the original candidate Phase-B/handover account.

Because this remainder closes TE-ARA by definition, Q8 alone could not show that it was a physical wave. Q9 then
compared it with independently calculated loss of two-qubit purity and found correlation `0.981999`. Q11 removed
the algebraic circularity by defining

\[
\underbrace{V}_{\text{candidate Phase A}}=K+R,
\qquad
\underbrace{P}_{\text{candidate Phase B}}
=2\left(1-\operatorname{Tr}\rho^2\right),
\]

and obtained the measured anti-phase relation

\[
\boxed{
C_P=-C_V+E.
}
\]

Median A/B opposition was `0.938439` in Ramsey and `0.999390` in Hahn. Thus the faithful lineage is

\[
\boxed{
H_{\rm unres}^{\rm Q8}
\longrightarrow
\text{purity cross-check in Q9}
\longrightarrow
P\text{ as the independent B coordinate in Q11}
\longrightarrow
R_B,H_B\text{ in Q13}.
}
\]

Here \(H_B\) means **Hahn's B child**; it is not the same notation as Q8's unresolved \(H\). The echo-refocusable
relation is plausibly part of this B account. The complete grey remainder need not be recoverable: it can also
contain irreversible decoherence, system-environment correlation, off-core tensor structure and measurement
limitations.

### 2.4 Methodology correction: the self-identity TE-ARA gate was skipped

The intended promotion sequence was:

1. identify unresolved \(H\) as a candidate object;
2. ARA-map its amplitude and opening/closing direction;
3. construct **its own** TE-ARA account,
   \[
   \boxed{
   \underbrace{T_U}_{2}
   =
   \underbrace{U_{\rm self}}_{\substack{\text{repeatable structure}\\\text{belonging to the candidate}}}
   +
   \underbrace{O_U}_{\substack{\text{state, protocol, environment}\\\text{and measurement Other}}};
   }
   \]
4. establish that \(U_{\rm self}/2\) is large and survives held-out controls;
5. only then test whether the resulting identity couples to Ramsey/Hahn in the predicted handover direction;
6. promote it from **candidate Phase B** to **calibrated Phase B** only if both gates pass.

The program completed steps 1 and 2. Q10 created the two-axis unresolved-\(H\) instrument
\((x_H,y_H)\). Its reported TE-ARA equation,

\[
T_{\rm low/open}
+T_{\rm high/open}
+T_{\rm high/close}
+T_{\rm low/close}=2,
\]

was a normalized **path-occupancy account**. It described where the candidate travelled. It did not decompose
how much of unresolved \(H\) belonged to a coherent self-identity versus `Other`.

Q11 then moved directly to step 5 by testing the visible/purity anti-phase relation, and Q13 used provisional
A/B labels. Therefore the four coordinate children remain valid, but the physical name **Phase B** has not yet
passed the intended self-identity TE-ARA gate.

A post-result probe shows that the skipped test is worth performing. At the `16` approximately common Ramsey/Hahn
wait pairs:

- purity-defined unresolved \(P_R>P_H\) in `15/16` cells;
- among positive cells, median apparent echo-recoverable share
  \((P_R-P_H)/P_R\) was `0.664349`;
- the unresolved reduction
  \(\Delta P=P_R-P_H\) tracked visible-relation retention
  \(\Delta V=V_H-V_R\) with correlation `0.953478`;
- the through-origin slope was `0.840035`.

These are **unfrozen descriptive coupling results**, not a Phase-B promotion. \(V\) and \(P\) come from the same
density matrices, the grids provide only four near-common waits per state, and their algebraic relation can
inflate correspondence. The correct next test must first estimate \(U_{\rm self}\) from native unresolved data
with held-out state/time controls, then test the Ramsey/Hahn handover on data not used to define that identity.

## 3. Why Q13 did not test this quadrant

Q13 paired equal ordinal indices:

- Ramsey: `0.02–40.02 us`;
- Hahn: `1–1000 us`.

It then asked whether one revealed scalar child could remove covariance among the other three. That is a
one-latent-axis question:

\[
v_j=\alpha_j+\beta_jh.
\]

The quadrant claim is a two-parent/two-axis model. Consequently:

- Q13's strong common amplitude result can represent shared radial/decoherence progression;
- Q13's failed directional one-latent result does not reject four-child quadrant structure;
- the stage comparator challenges only the claim that one unique child generates the other three.

The four-child covariance spectrum supports that distinction:

| Axis family | PC1 | PC2 | PC1 + PC2 |
|---|---:|---:|---:|
| amplitude | `87.2554%` | `12.2936%` | `99.5490%` |
| direction | `51.1675%` | `42.4026%` | `93.5701%` |

Amplitude is dominated by one common radial path. Direction requires two large modes. PCA axes are orthogonal by
construction, so this is evidence that one direction coordinate is inadequate—not proof that the physical
Ramsey/Hahn axes are exactly perpendicular.

## 4. Post-result common-time output diagnostic

The source grids contain four approximately common durations:

\[
(4.02,3.98),\ (8.02,7.94),\ (16.02,15.85),\ (32.02,31.62)\ \mu\mathrm{s}.
\]

Across four Bell identities this gives `16` comparisons with duration differences below `2%`.

For the derived parent axes

\[
r=\frac{R_A-R_B}{2},
\qquad
h=\frac{H_A-H_B}{2},
\]

the output-plane angle statistics were:

- mean: `91.636°`;
- median: `76.962°`;
- within `15°` of perpendicular: `3/16 = 18.75%`.

For the raw physical Bell relation plane \(u+iv\):

- mean: `90.366°`;
- median: `80.945°`;
- within `15°` of perpendicular: `3/16 = 18.75%`.

The means look strikingly close to \(90^\circ\), but the individual angles are widely dispersed. The output
trajectories therefore do not demonstrate a stable right angle.

The derived median angles at successive common waits were:

\[
49.849^\circ,\quad53.436^\circ,\quad98.930^\circ,\quad162.653^\circ.
\]

That apparent rotation was not distinctive under a within-state Hahn-wait rematching control. Ramsey wait order
was retained while the four Hahn waits were reassigned. Mean per-state Spearman was `0.95`, but the exact
four-state rematching tail was `p=0.916667`. A deterministic `200,000`-draw control gave `p=0.978035` for
monotone median angles and `p=0.975070` for monotonicity plus at least the observed rotation. The sweep therefore
does not depend specifically on correct Ramsey/Hahn time pairing; it is descriptive, not evidence of a
cross-parent handover.

This distinction is important:

\[
\boxed{
\text{orthogonal control kernels}
\not\Rightarrow
\text{every measured output point lies }90^\circ\text{ apart}.
}
\]

## 5. Q14's corrected scope

Q14 compared:

\[
\mathbf H\approx\mathbf R
\quad\text{against}\quad
\mathbf H\approx S\mathbf R,
\]

where \(S\) literally swaps the A/B labels. The quadrant relation is instead a Hadamard rotation between two
control paths. A label swap is not a \(90^\circ\) control-space rotation.

Q14 therefore retains a narrow valid result:

> an extra unmatched A/B label swap does not improve Ramsey-to-Hahn output correspondence.

It did not test:

- the ideal Ramsey/Hahn control-kernel orthogonality;
- the two-parent/four-child quadrant;
- the midpoint sum/difference reconstruction;
- a physical common-clock handover.

## 6. Correct next test

The strongest next test should freeze the ideal two-axis relation before opening results:

1. choose common total durations \(T\);
2. retain native, unnormalized phase-sensitive observables;
3. measure or simulate the two half-interval phase contributions \(\phi_1,\phi_2\);
4. predict both protocol outputs:
   \[
   \widehat\Phi_R=\phi_1+\phi_2,
   \qquad
   \widehat\Phi_H=\phi_1-\phi_2;
   \]
5. compare with time-only, one-latent and standard filter-function controls;
6. test inverse recovery of \(\phi_1,\phi_2\) from Ramsey plus Hahn;
7. only then test whether their four oriented output branches form a stable quadrant after measurement distortion.

## Bottom line

The user correction is valid:

\[
\boxed{
\text{Ramsey A/B}+\text{Hahn A/B}
=
\text{four ARA children inside a larger two-parent account}.
}
\]

The ideal physics is even cleaner than the previous audit recognized: Ramsey and Hahn are a reversible
orthogonal sum/difference basis in control space. The current data strongly support the two internal A/B pairs
and show that direction needs two large modes. They do not yet show that the measured output trajectories remain
perpendicular or that one child physically hands energy into another protocol.

## Q15 completion of the skipped self-identity gate

Q15 subsequently performed the missing native

\[
T_U=U_{\rm self}+O_U=2
\]

decomposition using purity-defined unresolved data, four-state held-out prediction and `9,999` independent
time-order shuffles.

Ramsey passed the dominant self-identity gate:

- common change share `0.997439`;
- common rate share `0.915259`;
- conservative TE-ARA account `1.830519` self plus `0.169481` Other.

Hahn was coherent but mixed:

- common change share `0.986048`;
- common rate share `0.676414`;
- conservative account `1.352827` self plus `0.647173` Other.

The apparent common-time handover remained numerically close
(\(r=0.953478\), slope `0.840035`, MAE `0.091438`), but failed the decisive rematching control:
within-state Hahn-wait reassignments produced median null correlation `0.976921` and one-sided `p=0.9973`.

Therefore Q15 closes the procedural gap but does **not** promote unresolved \(H\) to a pure Phase B. The correct
label remains **coherent unresolved ARA mode / candidate Phase-B account**. Full report:
`Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_REPORT_2026-07-24.md`.

## Reproduction

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q13_ramsey_hahn_quadrant_reaudit.py'
```

Inputs:

- `Q13_RAMSEY_HAHN_FOUR_CHILDREN.csv`;
- `Q8_BELL_RELATION_PLANE_RECORDS.csv`.
