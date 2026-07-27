# Q38 Post-Result Hypothesis — Perpendicular Quadrant Double Flip

**Date:** 27 July 2026  
**Status:** **POST-RESULT HYPOTHESIS / PRIOR ARA RULE, NEW QUANTUM
APPLICATION**  
**Evidence boundary:** This note does not alter or rescue Q38's frozen
verdict.

## Dylan's interpretation

After the fixed-anchor Q38 result was open, Dylan proposed that the observed
sequence might not mean “briefly enter Phase B, then return to the original
Phase A.” Instead, the whole local chart may flip across a quadrant:

\[
\underbrace{2\longrightarrow0}_{\substack{\text{old quadrant}\\\text{closes}}}
\;\Big|\;
\underbrace{0\longrightarrow2}_{\substack{\text{new quadrant}\\\text{opens}}}.
\]

The measured parent returns to the same apparent region, but its two children
have exchanged or reversed their phase roles:

\[
\boxed{AB\longrightarrow BA}.
\]

In this interpretation, Q38 approaches the seam approximately perpendicular
to the view used in earlier head-on singularity-flip discussions. The
negative first exit slice may be the interval after one child has flipped but
before the second child completes the quadrant handover.

## Tier placement correction

The four quadrants proposed here are **not the four Bell preparations**.
Those preparations were the upper-level calibration lens in Q24.

Q24 decomposed a complete two-parent preparation as:

\[
\underbrace{\mathbf a}_{\substack{\text{upper local}\\\text{parent A cuts}}},
\qquad
\underbrace{\mathbf b}_{\substack{\text{upper local}\\\text{parent B cuts}}},
\qquad
\underbrace{C=T-\mathbf a\mathbf b^{\mathsf T}}_{\substack{\text{connected relation}\\\text{ARA}^{9}\text{ lattice}}}.
\]

The Bell records made the \(3\times3\) connected lattice especially complete
and coherent, but Bell is not identical to that lattice. Q26 followed the
whole \(C(t)\) lattice from crest toward trough. Q36–Q38 then examined a
determinant pinch and orientation change **inside the trajectory of \(C\)**.

The corrected relative placement is:

\[
\underbrace{\text{whole prepared pair / Bell-level lens}}_{\text{upper account}}
\supset
\underbrace{C(t)=\text{ARA}^{9}\text{ connected lattice}}_{\text{relation identity}}
\xrightarrow[\text{across its own chart}]{\text{pinch / singularity}}
\underbrace{C'(t)}_{\text{post-flip lattice-side identity}}.
\]

Thus “down a tier and across” is the present ARA map. The same four-quadrant
geometry may recur at both levels because ARA is fractal, but the two
occurrences must not be given the same identity label.

## Minimal mathematical form

Let the measured parent relation be dominated locally by two labelled child
directions:

\[
\underbrace{C}_{\substack{\text{visible parent}\\\text{relation}}}
\approx
\underbrace{\sigma}_{\text{parent amplitude}}
\underbrace{u}_{\text{child A direction}}
\underbrace{v^{\mathsf T}}_{\text{child B direction}}.
\]

Then an ordered pair of child reversals gives:

\[
\begin{aligned}
\underbrace{u v^{\mathsf T}}_{\substack{\text{old quadrant}\\\text{positive parent orientation}}}
&\longrightarrow
\underbrace{(-u)v^{\mathsf T}}_{\substack{\text{one child crossed}\\\text{negative parent orientation}}}\\
&\longrightarrow
\underbrace{(-u)(-v)^{\mathsf T}}_{\substack{\text{both children crossed}\\\text{positive parent orientation}}}
=uv^{\mathsf T}.
\end{aligned}
\]

The parent-facing sign sequence is therefore:

\[
\boxed{+\longrightarrow-\longrightarrow+}.
\]

Here \(u\) and \(v\) are hypothetical **internal children of the ARA⁹
identity \(C\)**. They are not automatically Q24's upper local vectors
\(\mathbf a\) and \(\mathbf b\). Reusing \(\mathbf a,\mathbf b\) as the
flip-children would move back up the hierarchy and flatten the proposed
lower-rung event.

Plainly: one child flipping makes the visible parent point the other way.
When the second child also flips, the two negatives cancel in the parent
measurement. The parent looks restored even though both children are now in
their reversed orientations.

## Relation to the Q38 observation

The untouched `pure_mimic` target gave:

| Exit slice | Parent orientation to fixed anchor | Relative amplitude |
|---:|---:|---:|
| `+1` | `-0.9693` | `0.0922` |
| `+2` | `+0.9563` | `0.2541` |
| `+3` | `+0.9861` | `0.4670` |
| `+4` | `+0.9938` | `0.6507` |

This is compatible with:

1. the parent amplitude pinching almost to zero;
2. one child orientation crossing first, producing the negative parent;
3. the second child crossing, making the parent-facing relation positive
   again;
4. the new quadrant rebuilding its amplitude.

Compatibility is not identification. The same parent sequence can also be
produced by a weak transient reversal followed by ordinary recovery. Q38
measured only the parent relation and therefore cannot distinguish those
accounts.

## Why the parent tensor is insufficient

The factorisation has an unavoidable paired-sign ambiguity:

\[
uv^{\mathsf T}=(-u)(-v)^{\mathsf T}.
\]

Consequently, observing \(C_{\rm after}\approx C_{\rm before}\) cannot tell us
whether:

- neither child changed;
- both children flipped;
- the children rotated through another path that reconstructs the same
  parent relation.

This is not merely missing statistical power. It is an identifiability limit
of the parent-only measurement. Calling the positive return a completed
double flip requires separately observable child directions or another
independent orientation marker.

## Prior ARA lineage

The underlying two-reversal rule is not new.

### 1. Axiomatic chart involution

`ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md`, Definition 3.2 and Theorem 3,
already define:

\[
F_{\rm chart}(x,s,n)=(2-x,-s,n),
\qquad
F_{\rm chart}^{\,2}=I.
\]

The completed-seam parity conjecture then states:

\[
N_{\partial T}\text{ odd}\Rightarrow F_{\rm chart},
\qquad
N_{\partial T}\text{ even}\Rightarrow I.
\]

One completed crossing reverses the chart; a second restores the
parent-facing orientation.

### 2. Maxwell two-child sign result

`analysis/electromagnetism/MX6_MAXWELL_STRESS_PHASE_FLIP_REPORT.md` already
records the exact established algebra:

\[
\mathbf S=\frac1{\mu_0}\mathbf E\times\mathbf B.
\]

Flipping only \(\mathbf E\) or only \(\mathbf B\) reverses \(\mathbf S\).
Flipping both leaves \(\mathbf S\) unchanged. The report translates this as:
each child controls one signed direction, and both must swap for the larger
identity to retain its direction.

### 3. What is new in Q38

The new element is not the parity law. It is the proposed observation
geometry:

> Earlier examples were generally approached head-on as a completed
> orientation change. Q38 may be viewing the seam perpendicularly and
> resolving the short interval between the first and second child flips.

That application arose after Q38's outcomes were known. It is therefore a
new testable explanation, not a successful prior prediction.

## Required discriminating test

The next test must decompress the ARA⁹ identity \(C(t)\) into two
independently measured **internal** children or an equivalently identifying
three-part Information³ relation. It must not simply reuse the upper
two-qubit local vectors \(\mathbf a,\mathbf b\).

If the source supplies suitable internal child observables, freeze one
approach-side anchor for each:

\[
\underbrace{r_A(j)}_{\substack{\text{child A orientation}\\\text{to its own anchor}}},
\qquad
\underbrace{r_B(j)}_{\substack{\text{child B orientation}\\\text{to its own anchor}}},
\qquad
\underbrace{r_P(j)}_{\substack{\text{parent orientation}\\\text{to the parent anchor}}}.
\]

The quadrant-double-flip prediction is:

| Region | \(r_A\) | \(r_B\) | Parent \(r_P\) |
|---|---:|---:|---:|
| Approach | positive | positive | positive |
| Between child crossings, A first | negative | positive | negative |
| Completed new quadrant | negative | negative | positive |

The order may be A-first or B-first, but exactly one reliable child should
cross before the other. The event should occur specifically around the
registered pinch more often than at:

- displaced-time controls;
- different-pair controls;
- network controls.

Each child amplitude must be reported. A direction inferred while its
amplitude is near zero is not reliable.

### Measurement warning

Using only singular-value-decomposition signs of the parent tensor would not
solve the problem: singular vectors themselves have arbitrary paired signs.
The children need independent physical coordinates at the correct lower
tier, or another fixed external orientation reference. The upper local-state
vectors may be retained as controls, but they do not become the lower
children merely because they are available in the raw density matrix.

If the raw source does not contain reliable independent child directions,
the hypothesis is **not testable with this representation** and must await a
richer dataset.

## Information³ route to the fourth meta quadrant

The non-flattening candidate is to treat the ARA⁹ lattice as its own identity:

\[
\underbrace{C_A}_{\text{internal Phase A}}
+
\underbrace{C_B}_{\text{internal Phase B}}
+
\underbrace{J_C=\mathcal C(C_A,C_B)}_{\text{their retained relation}}
\longrightarrow
\underbrace{C}_{\text{whole ARA}^{9}\text{ identity}}.
\]

Across the singularity, the same typed relation should be rebuilt on the
adjacent chart. Three independently observed meta-quadrant relations may
then predict the fourth through a frozen closure rule. Merely setting the
fourth equal to “whatever makes the total close” would force the answer;
the test must derive the fourth from development data, freeze the
transformation and evaluate it on held-out trajectories.

This is the appropriate place to test full or high ARA coherence:

1. all three ARA⁹ relation directions remain identifiable or reconstruct;
2. the ordered quadrant path closes;
3. the Information³ relation predicts the held-out fourth meta quadrant;
4. the ARA score is compared with an independently calculated quantum
   coherence or purity quantity rather than defining success from itself.

## Falsification conditions

This particular quadrant-double-flip application is weakened or rejected if:

1. the two independently measured children do not cross in an ordered pair;
2. both appear unchanged while the parent follows `+ → - → +`;
3. the sequence is equally frequent away from the determinant pinch;
4. apparent child flips occur only when their amplitudes are too small to
   define direction;
5. the result disappears under an external-frame or gauge-invariant check.

## Plain explanation

The earlier flip rule says that two reversals can look like no reversal when
we view only the finished parent. Q38 may have photographed the transition
between them: first the old identity nearly disappears and points backwards,
then the second child crosses and the rebuilt parent points forwards again.

That interpretation is geometrically coherent and has a clear older ARA and
Maxwell lineage. The current parent data cannot prove it. We now need to
decompress the ARA⁹ lattice at the correct lower tier and watch its two
internal children separately.
