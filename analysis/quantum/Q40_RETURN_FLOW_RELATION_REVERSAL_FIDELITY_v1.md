# Q40 Translation Fidelity — Conditional Return-Flow Relation Reversal

**Test ID:** `Q40-RETURN-FLOW-RELATION-REVERSAL-v1`  
**Date:** 27 July 2026  
**Freeze stage:** target-independent, before target archive selection  
**ARA status:** prospective replication of a post-Q39 hypothesis

## 1. ARA claim being tested

Q40 tests one specific statement inside the lower connected-relation lattice:

> A complete four-quadrant cycle normally carries the ordered relation from
> the first two visits forward into the fourth. On a visible return-flow
> branch, that relation reverses orientation while the third-visit identity
> remains the local anchor.

For three visible quadrant identities,

\[
\underbrace{D}_{\substack{\text{ordered relation}\\\text{carried forward}}}
=
\underbrace{C_1}_{\text{first visit}}
-
\underbrace{C_2}_{\text{second visit}},
\qquad
\underbrace{P}_{\substack{\text{ordinary forward}\\\text{continuation}}}
=
\underbrace{C_3}_{\text{current identity}}
+
\underbrace{D}_{\text{relation contribution}}.
\]

The visible return-flow flag is

\[
\underbrace{F}_{\substack{\text{return-flow flag}\\\text{uses no }C_4}}
=
\mathbf 1
\left[
\underbrace{\cos(P,C_3)}_{\substack{\text{orientation of the proposed}\\
\text{next whole relative to the current whole}}}
<0
\right].
\]

The frozen Q40 prediction is

\[
\boxed{
\widehat C_4=
\begin{cases}
C_3-D, & F=1,\\
C_3+D, & F=0.
\end{cases}}
\]

Only the ordered relation contribution \(D\) changes sign. The complete
predicted identity is not multiplied by \(-1\).

## 2. Tier lock

| Relative tier | Q40 object |
|---|---|
| Upper calibration lens | complete two-qubit preparation and the available physical labels |
| Tested identity | connected \(3\times3\) relation lattice \(C(t)\) |
| Internal ARA cut | closure side \(u(t)\) and closure flow \(v(t)\) |
| Four internal visits | contiguous quadrant means \(C_1,C_2,C_3,C_4\) |
| Hidden target | the raw fourth-visit lattice \(C_4\) |
| Tested return-flow relation | conditional orientation of \(D=C_1-C_2\) |

Q40 does not move Bell labels down and rename them as the four internal
quadrants. It also does not call the local Bloch vectors the two hidden
children. Those are different decompression questions.

## 3. Four-quadrant ARA map

Use

\[
\underbrace{u}_{\text{closure side}}
=
\frac{h-m}{r},
\qquad
\underbrace{v}_{\text{closure flow}}
=
\frac{\Delta h}{s},
\qquad
h=|\det C|^{1/3}.
\]

With \(u\) horizontal and \(v\) vertical, Dylan's fixed ARA reading is:

| Plane position | Mathematical sign | ARA name | Plain meaning |
|---|---:|---|---|
| top right | \(u\ge0,\ v\ge0\) | \(Ab\) | Phase A leads while the relation accumulates |
| bottom right | \(u\ge0,\ v<0\) | \(aB\) | Phase B becomes locally dominant on the release side |
| bottom left | \(u<0,\ v<0\) | \(bA\) | reversed-side release / return continuation |
| top left | \(u<0,\ v\ge0\) | \(Ba\) | reversed-side accumulation returning toward the first side |

The clockwise ARA cycle is

\[
Ab\rightarrow aB\rightarrow bA\rightarrow Ba\rightarrow Ab.
\]

In the numerical labels already used by Q39 this is

\[
Q_{++}\rightarrow Q_{+-}\rightarrow Q_{--}\rightarrow Q_{-+}
\rightarrow Q_{++}.
\]

The geometry is reversible. A lineage whose development half establishes
the opposite circulation is retained in its measured direction; it is not
silently flipped to imitate the clockwise picture.

## 4. ARA-to-math translation

| ARA term | Q40 operational quantity |
|---|---|
| complete lower-tier identity | \(C(t)=T(t)-\mathbf a(t)\mathbf b(t)^{\mathsf T}\) |
| parent closure cut | \(h(t)=|\det C(t)|^{1/3}\) |
| ridge-side coordinate | development-normalised \(u(t)\) |
| accumulation/release coordinate | development-normalised \(v(t)=\Delta h(t)/s\) |
| one quadrant identity | mean raw \(C(t)\) during one contiguous visit |
| ordinary ordered continuation | \(C_3+(C_1-C_2)\) |
| visible return-flow condition | \(\cos(C_1-C_2+C_3,C_3)<0\) |
| relation reversal | \(C_3-(C_1-C_2)\) |
| hidden fourth state | observed \(C_4\), unavailable to the predictor |

## 5. What is inherited and what is new

Inherited unchanged from frozen Q39:

- the connected matrix \(C\);
- determinant-magnitude closure \(h\);
- development-only coordinate normalisation;
- four sign quadrants;
- development-learned circulation;
- contiguous-visit cycle extraction;
- masking of every \(C_4\) value from the prediction.

New, and therefore the sole Q40 mechanism under test:

- the visible condition \(\cos(C_1-C_2+C_3,C_3)<0\);
- conditional reversal of \(C_1-C_2\), not the whole predicted matrix.

## 6. What would count as support

On a genuinely untouched archive, the visible flag must:

1. identify the minority cases in which the ordinary forward prediction
   points opposite the observed \(C_4\);
2. improve held-out fourth-visit reconstruction on the flagged branch;
3. improve the full eligible population without degrading the unflagged
   branch;
4. beat the frozen Q39 baselines, whole-sign correction, persistence guard,
   inverted-flag control and a development-fitted affine comparator.

Support concerns the conditional ordered relation-flow operator at this
tested tier. It does not automatically establish the same rule at every
quantum or physical tier.

## 7. What would not count

- inspecting \(C_4\) before choosing whether to reverse \(D\);
- selecting the target after seeing numerical performance;
- choosing a different relation term after the target is open;
- using \(2-x\), \(x+(2-x)=2\), or any other forced complement as evidence;
- calling every negative cosine a singularity by definition;
- treating a whole-matrix sign flip as the same as relation reversal;
- fitting the ARA coefficients on evaluation cycles;
- relabelling the return branch as a discovered physical Phase B;
- using a closed-looking plot without out-of-sample reconstruction gain.

## 8. Honest interpretation boundary

Q40 is a prospective test of a rule discovered post hoc in Q39A. A pass
would show that a target-blind relation-orientation condition replicates on
an untouched archive and improves masked fourth-quadrant reconstruction.
That would be evidence for a reusable conditional ARA relation-flow rule
inside this simulator family.

It would not yet prove a literal singularity crossing, a unique hidden
quantum state, entanglement transport, universal fractality, or physical
Phase B. Cross-tier fractality and entanglement remain separate later tests.
