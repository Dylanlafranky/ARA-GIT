# T449 — same-rung time-facing children beneath the fruit-fly lifecycle gradient

Status: frozen before extracting or viewing the T449 child coordinates.

T448 remains a valid broad time-facing discovery cut. T448's fixed terminal-point hypothesis failed, while T448B recovered a transferable one-cycle direction. T449 does not replace either result; it asks what ordered, same-rung temporal relation sits underneath the T448B parent direction.

## Who

The measured identities are the same 47 individual male *Drosophila melanogaster*. Experiments 1–3 (31 flies) remain development; experiment 4 (16 later, hotter flies) remains untouched holdout.

Hours and child windows from the same fly may never occur on both sides of that split. The experiment is an accelerated nutrient-limited, warm dying/stress condition rather than a normal-lifespan assay.

## What

The input is the authors' ordered frame-level behaviour sequence. Biological labels are not preselected as ARA children; they remain annotations explaining which observed behaviours occupy a temporal state.

Every recording is reduced to a one-second categorical sequence by taking the modal behaviour label within each second. Labels `unstereotyped` and `on_edge` are treated as unresolved separators: they are retained as quality controls and may not create a transition by stitching the resolved sequence across a gap.

Two candidate children are measured over the same non-overlapping ten-minute window:

### Candidate child \(C_A\): temporal retention / connection

For resolved behaviour state \(Y_t\), at lags \(\tau\in\{1,10,60\}\) seconds,

\[
A_\tau=
\frac{P(Y_t=Y_{t+\tau})-\sum_k p_k^2}
{1-\sum_k p_k^2}.
\]

The chance term \(\sum_kp_k^2\) removes persistence caused only by occupancy imbalance, especially a large idle share. The child coordinate \(C_A\) is the equal-weight mean of the three valid lag estimates; raw lag values remain available.

### Candidate child \(C_B\): temporal traversal / renewal

Using all valid one-second ordered transitions inside the same ten-minute window,

\[
C_B=
\frac{H(Y_{t+1}\mid Y_t)}{\log K},
\]

where \(K\) is the number of resolved behaviour states actually available to the window. This is conditional transition entropy: low values mean the current relation strongly restricts the next state; high values mean the next state traverses a less restricted set of possibilities.

These quantities are related but are not algebraic complements. T449 may call them a coupled ARA pair only if an ordered relation transfers to holdout; it may not call them a Di-ARA without additional independent pole evidence.

### Relation \(R_{AB}\)

\(R_{AB}\) is the directional lead–lag relation between changes in \(C_A\) and changes in \(C_B\) across consecutive ten-minute windows. Development flies select one lag from \(-12\) to \(+12\) child windows (\(-120\) to \(+120\) minutes) by the largest absolute median within-fly cross-correlation; its sign and lag are frozen before holdout evaluation.

Positive lag is defined as \(C_A\) leading \(C_B\). A time reversal must reverse the lag address; a timestamp shuffle must remove the coherent lag structure.

## When

The child scale is ten minutes. Six consecutive child windows are summarized by their median to locate the existing one-hour T448 parent without redefining the parent coordinate.

The full pre-collapse history is used for child geometry. Collapse and death times are withheld from child construction and revealed only for evaluation of where the learned landmarks sit relative to the recorded outcomes.

## Where

The relational address is:

individual fly → ordered one-second behaviour state → ten-minute \((C_A,C_B,R_{AB})\) child relation → one-hour parent summary → frozen T448B lifecycle direction → author-recorded collapse/death landmarks.

Both proposed children occupy the same temporal rung and use the same observation medium, window, resolved-state population and sampling frequency. Behaviour categories annotate the points but do not define the axes.

## Why

The test asks whether the broad lifecycle gradient is underlaid by a genuinely time-facing same-rung exchange: retained temporal relation, ordered renewal, and a directional coupling between them. A positive result must depend on chronology rather than merely on which behaviours are common near collapse.

The test does not ask for a universal death coordinate. It asks whether a reproducible child relationship precedes or accompanies movement of the parent lifecycle gradient and whether its landmarks survive an unseen experimental regime.

## How

1. Extract ordered ten-minute child windows from all public HDF5 behaviour files up to the authors' collapse landmark.
2. Require at least 80% resolved seconds, at least 300 valid adjacent transitions and at least two resolved states per child window. Retain unresolved and edge shares as controls.
3. Fit robust development centres and scales for \(C_A\) and \(C_B\) only. Apply the same common 0–2 display mapping to holdout without per-fly or per-experiment refitting; raw measurements remain primary.
4. Estimate the development lead–lag relation across complete histories, freezing its lag and sign before viewing holdout.
5. Detect descriptive child exchange landmarks where standardized child dominance changes sign. A crossing alone is not a handover: report whether directed coupling is locally strong and whether the parent changes afterward.
6. Evaluate the frozen lag, sign, exchange geometry and child-to-parent ordering on experiment 4.
7. Controls: within-window timestamp shuffle, full-history time reversal, occupancy-matched Markov surrogates, same-Zeitgeber-time comparisons, unresolved/edge share, camera, temperature and humidity.
8. Report frozen qualification separately from visible geometry. A failed gate cannot erase shape; a visible shape cannot redefine a gate.

## Frozen qualifications

### Q1 — genuine time ordering

The observed holdout \(|R_{AB}|\) at the frozen development lag must exceed the 95th percentile of 2,000 within-fly circular child-window shifts. The relation must weaken under within-window timestamp shuffle.

### Q2 — directional transfer

At least 65% of eligible holdout flies must reproduce the frozen development sign of \(R_{AB}\). Reversing each history must reverse the lag address rather than reproduce the same directional address.

### Q3 — parent ordering

Using exchange landmarks detected from \(C_A,C_B\) alone, the median frozen T448B parent-direction progress in the following one hour must exceed progress in the preceding one hour and exceed the 95th percentile of within-fly shifted exchange landmarks.

### Q4 — biological non-reduction

The frozen child relation must retain at least half of its absolute holdout coupling after stratifying or residualizing by idle share, resolved behaviour composition, Zeitgeber phase and unresolved share. This qualification prevents simple occupancy change from being renamed a temporal child relation.

Passing Q1 and Q2 supports a same-rung time-facing relation. Passing Q3 connects that relation to the previously observed lifecycle parent. Q4 is required before interpreting the child pair as more than a biological-composition shadow.

## Mandatory pivot notice

If the public frame-level sequence cannot be extracted at the required grain, if classifier smoothing mechanically creates the measured persistence, or if the two coordinates collapse to a near-deterministic complement, T449 must be reported as inconclusive at this measurement depth. The next cut may then use more time-facing biological/pose variables, but that medium change must be announced before testing.
