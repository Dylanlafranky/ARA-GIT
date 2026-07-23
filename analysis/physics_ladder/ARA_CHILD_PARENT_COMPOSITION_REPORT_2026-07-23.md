# ARA child-to-parent composition across three continuity laws

**Date:** 23 July 2026  
**Status:** frozen prospective reconstruction test passed  
**Validation:** `15/15` independent checks passed  
**Confidence:** ready to share as an exact formalization/reconstruction result; not as evidence of new dynamics

## Technical summary

One unchanged child-to-parent ARA operator reconstructed the directly measured parent account in:

1. a classical Newton/Hamilton string-energy wave;
2. a lossless Maxwell/Poynting transmission line;
3. a free Schrödinger Gaussian probability-current holdout.

All `12,291` planned model samples were retained. The largest absolute frozen-operator error was
\(2.1538\times10^{-14}\), consistent with floating-point arithmetic. The largest quantum-holdout error was
\(2.4425\times10^{-15}\).

The best incorrect control still had a mean absolute error of `0.302350` ARA units. This shows that retaining the
child interface in the parent activity account or simply averaging child positions is not equivalent to the
boundary-aware composition.

The result establishes a precise ARA aggregation rule for this class of continuity systems:

> A flow through a shared interface is external to each child but internal to their enclosing parent. It must
> therefore be removed once from accumulated activity and once from released activity when the parent is formed.

This is also ordinary finite-volume conservation accounting expressed in ARA coordinates. The result strengthens
ARA's mathematical coherence and supplies a missing aggregation law, but it does not yet distinguish ARA from
established conservation mathematics.

## Frozen operator

For each child \(i\):

\[
\underbrace{T_i}_{\substack{\text{child activity}\\\text{ARA: active TE account}}}
=
\underbrace{A_i}_{\substack{\text{inward flow}\\\text{ARA: accumulation}}}
+
\underbrace{R_i}_{\substack{\text{outward flow}\\\text{ARA: release}}},
\]

\[
\underbrace{x_i}_{\substack{\text{child diameter position}\\0\le x_i\le2}}
=
\frac{
2\underbrace{R_i}_{\text{release}}
}{
\underbrace{A_i+R_i}_{T_i}
}.
\]

The inverse decompression is

\[
\underbrace{R_i}_{\text{release}}
=\frac{T_i x_i}{2},
\qquad
\underbrace{A_i}_{\text{accumulation}}
=\frac{T_i(2-x_i)}{2}.
\]

Let \(I\) be the magnitude of the flow through the children’s shared interface. At child grain it is counted twice:
once as a release and once as an accumulation. At parent grain it crosses no external boundary. Therefore

\[
\underbrace{A_P}_{\text{parent accumulation}}
=
\sum_i A_i-I,
\qquad
\underbrace{R_P}_{\text{parent release}}
=
\sum_i R_i-I,
\]

\[
\boxed{
\underbrace{x_P}_{\substack{\text{predicted parent}\\\text{ARA position}}}
=
\frac{
2\left(
\underbrace{\sum_iR_i}_{\text{all child releases}}
-
\underbrace{I}_{\text{internal handover}}
\right)
}{
\underbrace{\sum_i(A_i+R_i)}_{\text{all child activity}}
-
\underbrace{2I}_{\substack{\text{same internal handover}\\\text{counted in both directions}}}
}
}.
\]

This is the first explicit reviewed ARA aggregation law in the repository that states exactly what changes when a
child boundary is absorbed into a parent.

## One-dimensional boundary declaration

For a signed flux \(F\), positive means rightward. For interval \([a,b]\):

\[
A=\max(F(a),0)+\max(-F(b),0),
\]

\[
R=\max(-F(a),0)+\max(F(b),0).
\]

For adjacent children \([a,c]\) and \([c,b]\):

\[
I=|F(c)|.
\]

Nothing about this declaration changes between the classical, electromagnetic and quantum models.

## Results

| Model | Test role | Valid samples | Frozen maximum error | Naive-child MAE | Interface-retained MAE | Continuity residual |
|---|---|---:|---:|---:|---:|---:|
| Classical string energy | operator establishment | 4,097 / 4,097 | \(5.3291\times10^{-15}\) | 0.422412 | 0.312725 | 0 |
| Lossless transmission line | verification | 4,097 / 4,097 | \(2.1538\times10^{-14}\) | 0.444557 | 0.302350 | 0 |
| Free Gaussian probability | untouched holdout | 4,097 / 4,097 | \(2.4425\times10^{-15}\) | 0.415981 | 0.534342 | \(6.1062\times10^{-11}\) |

The quantum residual is an independent finite-difference check against the preregistered \(10^{-6}\) tolerance.
The classical and electromagnetic residuals use their analytic derivatives.

Orientation reversal also passed:

\[
x'_P=2-x_P
\]

with a worst saved-model discrepancy of \(2.1538\times10^{-14}\).

An independent randomized validator generated `100,000` signed triples
\((F_{\rm left},F_{\rm interface},F_{\rm right})\). The maximum composition discrepancy was
\(3.5083\times10^{-14}\); the maximum reversal discrepancy was \(3.5971\times10^{-14}\).

## Why the controls fail

### Naive mean

\[
x_{\rm naive}=\frac{x_1+x_2}{2}.
\]

This assumes both children have equal activity and ignores the fact that their shared boundary is counted in
opposite directions.

### Activity-weighted but unclosed

\[
x_{\rm unclosed}
=
\frac{T_1x_1+T_2x_2}{T_1+T_2}
=
\frac{2(R_1+R_2)}{T_1+T_2}.
\]

This respects unequal child activity but leaves the internal interface inside the parent account. It therefore
measures the collection of two children, not their externally bounded parent.

### Frozen boundary-aware operator

\[
x_P
=
\frac{2(R_1+R_2-I)}{T_1+T_2-2I}.
\]

This changes grain correctly. It removes the relation that crossed child boundaries but no longer crosses the
parent boundary.

## Physical models

### Classical Newton/Hamilton wave

For an ideal string with unit density and tension:

\[
u_{\rm string}
=\frac12 y_t^2+\frac12 y_x^2,
\qquad
S_{\rm string}=-y_ty_x,
\]

\[
\partial_tu_{\rm string}+\partial_xS_{\rm string}=0.
\]

The raw field is an analytic superposition of left- and right-travelling waves. No spectral decomposition or
smoothing is applied.

### Maxwell/Poynting transmission line

For a lossless unit-inductance and unit-capacitance line:

\[
u_{\rm EM}
=\frac12V^2+\frac12I_{\rm line}^2,
\qquad
P_{\rm EM}=VI_{\rm line},
\]

\[
\partial_tu_{\rm EM}+\partial_xP_{\rm EM}=0.
\]

The voltage and current are constructed directly from analytic forward and backward waves. The same boundary rule
is applied unchanged.

### Schrödinger probability holdout

For a free Gaussian packet in units \(\hbar=m=1\):

\[
\rho=|\psi|^2,
\qquad
j=\operatorname{Im}(\psi^*\partial_x\psi),
\]

\[
\partial_t\rho+\partial_xj=0.
\]

Here the accumulated/released quantity is probability rather than physical energy. This is important: the common
mathematics does not make probability and energy the same quantity. It shows that both possess the same local
boundary-accounting form.

## What this adds to ARA

The previous physics atlas established that the continuity grammar

\[
\partial_tq+\nabla\!\cdot\mathbf J=s
\]

appears in multiple theories. This test adds the scale transformation:

\[
\boxed{
\text{child accounts}
\;-\;
\text{internal paired handovers}
\;\longrightarrow\;
\text{parent external account}
}.
\]

That makes the ARA “zoom” rule more precise:

1. choose the parent boundary;
2. preserve each child’s accumulation, release and total activity;
3. identify transfers that cross child boundaries but remain inside the parent;
4. cancel those transfers from both directional accounts;
5. recompress the remaining external account onto `0–2`.

The relation is not destroyed. Its classification changes: it was boundary flow at child grain and becomes
internal structure at parent grain.

## Limitations

1. **This is an identity-level test.** The result follows from consistent boundary accounting and is expected to
   be exact.
2. **The three models share source-free continuity.** They test cross-domain transfer of the operator, not all
   physical laws.
3. **No unknown physics was predicted.** Parent values were predicted from complete child boundary information.
4. **An interface that stores quantity needs an additional relation account.** A spring, reactive element or
   quantum coupling region can temporarily accumulate energy or probability. Treating it as instantaneous
   handover would leave a meaningful residual.
5. **The result does not prove literal fractal spheres, Phi, universal TE-ARA energy or quantum gravity.**

## Validation assessment

**Overall assessment:** ready to share with the formalization fence attached.

The independent validator passed `15/15` checks:

- frozen-protocol hash;
- three-model coverage;
- complete sample retention;
- primary and orientation tolerances;
- control comparisons;
- native continuity residuals;
- saved-row recalculation;
- `100,000` randomized signed-flux accounts;
- artifact bounds and source structure;
- explicit universality limitations.

## Recommended next test

The next experiment should introduce a relation that stores or removes quantity:

- a damped two-mass/spring system;
- a resistive transmission-line section;
- or a quantum region with a declared source/sink or open-system term.

Freeze the visible child accounts, hide the native source label and ask whether

\[
\underbrace{\Delta_{\rm Other}}_{\text{unexplained parent residual}}
=
\underbrace{\text{direct parent change}}_{\text{revealed later}}
-
\underbrace{\text{closed ARA prediction}}_{\text{frozen beforehand}}
\]

recovers the sign, location and magnitude of the hidden term.

That would move from an exact reconstruction identity toward a genuinely discriminating ARA inference.

## Reproduction

```powershell
cd F:\SystemFormulaFolder\GIT\ARA-GIT

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  .\analysis\physics_ladder\ara_child_parent_composition_test.py

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  .\analysis\physics_ladder\validate_ara_child_parent_composition.py
```

Generated artifacts:

- `CHILD_PARENT_COMPOSITION_PROTOCOL_2026-07-23.md`
- `ARA_CHILD_PARENT_COMPOSITION_SUMMARY.csv`
- `ARA_CHILD_PARENT_COMPOSITION_BOUNDED_SAMPLE.csv`
- `ARA_CHILD_PARENT_COMPOSITION_RESULTS.json`
- `ARA_CHILD_PARENT_COMPOSITION_VALIDATION.json`
- `ARA_CHILD_PARENT_COMPOSITION_REPORT_ARTIFACT.json`
