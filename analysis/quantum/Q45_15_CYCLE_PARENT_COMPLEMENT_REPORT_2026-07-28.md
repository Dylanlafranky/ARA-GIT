# Q45 — what supplies the other half of the 15-cycle parent?

Date: 28 July 2026 (Australia/Brisbane)

## Answer first

The first candidate, the local-product relation

\[
L=ab^{\mathsf T},
\]

behaves strongly like an **upward contributor to the approximately 15-sample
parent**, but Q45 does not establish it as the complete bidirectional missing
half.

The frozen verdict is:

> **NOT SUPPORTED**

That verdict has two specific causes:

1. only `17` seeds and `79` lineages passed the strict development-only
   cadence definition, far below the frozen `80`-seed and `1,000`-lineage
   adequacy requirements; and
2. \(L\) added no one-step information for predicting the child \(C\) from
   above.

The upward results were nevertheless strong:

- held-out 15-cycle phase skill for \(L\): `0.609`, 95% seed interval
  `[0.454, 0.748]`;
- movement-path share assigned to \(L\): `0.589`, interval
  `[0.417, 0.666]`;
- child-to-parent error fell from `0.814` with \(C\) alone to `0.411` with
  \(C+L\); and
- real-time \(L\) beat the same candidate delayed by four samples.

The honest interpretation is therefore:

> **\(L\) is a strong parent-complement candidate for the upward 7.5→15
> relation in this shaping archive. It is not yet the confirmed second half
> of a bidirectional parent-child ARA.**

## The two languages side by side

| ARA reading | Established quantum quantity |
|---|---|
| already measured connected child | \(C=T-ab^{\mathsf T}\), the connected two-body Pauli relation |
| candidate parent complement | \(L=ab^{\mathsf T}\), the product of the two local Bloch vectors |
| proposed parent relation | \(T=C+L\), the full two-body Pauli correlation tensor |
| child path share | 15-sample Frobenius path length of \(C\) |
| candidate path share | 15-sample Frobenius path length of \(L\) |
| relation / informative third | signed Frobenius alignment of \(\Delta C\) and \(\Delta L\) |
| parent phase | approximately 15-sample phase extrapolated from development \(C\) only |

The exact identity

\[
T=C+L
\]

is standard tensor bookkeeping. It was not counted as evidence. The scored
questions were whether \(L\)'s phase repeats, whether its movement occupies
the proposed missing share, whether correct timing matters, and whether it
predicts future flow.

## \(L\) follows the 15-cycle parent phase

A 16-bin \(L\) template was built on development samples `0..248`. Its phase
was supplied only by the connected \(C\) orbit and extrapolated into held-out
samples `250..498`.

Against a static development mean:

\[
\mathrm{skill}_{15}
=
0.609,
\qquad
95\%\ \mathrm{CI}
=
[0.454,0.748].
\]

The correct parent phase also beat:

- the wrong-rung phase by `+0.925`, interval `[0.663, 1.204]`; and
- a fixed four-sample-lag timing control by `+1.887`, interval
  `[1.673, 2.087]`.

Plainly: the candidate is not merely a large static background. Its detailed
nine-entry relation shape changes reproducibly with the 15-cycle phase, and
the actual timing matters.

The evidence is dominated by the parent-resolved class:

| Development classifier | Lineages | Seeds | Parent-phase skill | \(L\) movement share |
|---|---:|---:|---:|---:|
| two-turn `7.5` | 14 | 7 | 0.440 | 0.514 |
| one-turn `15` | 65 | 17 | 0.621 | 0.625 |

The two-turn share is close to the proposed half but highly uncertain because
only seven seeds contribute. The one-turn class is more consistently above
half.

## Near-half movement does not mean near-half state size

Across non-overlapping 15-sample evaluation paths:

\[
s_L
=
\frac{P_L}{P_C+P_L}
=
0.589,
\qquad
95\%\ \mathrm{CI}
=
[0.417,0.666].
\]

On the 0–2 display this is:

\[
x_L=2s_L\approx1.178,
\qquad
x_C\approx0.822.
\]

This passes Q45's predeclared broad half-complement gate because the point
estimate lies in `[0.40,0.60]` and the interval contains `0.50`.

But the state-amplitude result is very different:

\[
\frac{\|L\|}{\|C\|+\|L\|}
\approx0.955,
\qquad
95\%\ \mathrm{CI}
=[0.943,0.971].
\]

Plainly: \(L\) is most of the static tensor magnitude, while \(C\) is much
smaller but far more active relative to its size. The near-half result applies
to **movement across a parent cycle**, not to stored amplitude or physical
energy. This resembles a large/slow background paired with a smaller/more
dynamic connected relation, but that ARA interpretation remains a hypothesis.

The mean instantaneous movement alignment was only:

\[
\langle j_{CL}\rangle
=
0.024,
\qquad
95\%\ \mathrm{CI}
=[-0.011,0.061].
\]

Thus \(C\) and \(L\) do not generally move in the same matrix direction at
each individual step. Their useful relation appears in the larger cadence and
timing, not as simple stepwise parallel motion.

## \(L\) carries strong child-to-parent information

Q45 fitted only pooled scalar gains on development. It then predicted the next
full-parent matrix difference in evaluation.

| Predictor | Seed-balanced scaled error |
|---|---:|
| child \(C\) only | 0.81391 |
| child \(C\) + real-time \(L\) | **0.41141** |
| child \(C\) + \(L\) delayed four samples | 0.71596 |

The real candidate's advantage over \(C\) alone was:

\[
0.81391-0.41141
=
0.40250,
\qquad
95\%\ \mathrm{CI}
=[0.33589,0.46127].
\]

Its advantage over the mistimed candidate was:

\[
0.71596-0.41141
=
0.30455,
\qquad
95\%\ \mathrm{CI}
=[0.25352,0.35044].
\]

Plainly: knowing the candidate relation at the correct time supplies a large
amount of information about how the full parent will move next. This is the
strongest positive Q45 result.

## The one-step downward test failed

For the reverse question—predicting the next child movement—the result was:

| Predictor | Seed-balanced scaled error |
|---|---:|
| child persistence | **0.41964** |
| child + real-time \(L\) | 0.41980 |
| child + \(L\) delayed four samples | 0.41923 |

The real candidate's advantage was slightly negative:

\[
-0.000155,
\qquad
95\%\ \mathrm{CI}
=[-0.000454,0.000127].
\]

This does not establish parent→child constraint at a one-sample delay. It does
not prove that no downward influence exists at any delay; it says the exact
frozen one-step model did not see one.

## Why the strict verdict remains negative

Q45 required all of the following:

| Frozen gate | Result |
|---|---|
| at least 80 seeds and 1,000 lineages | **fail** — 17 seeds, 79 lineages |
| parent phase beats static \(L\) | pass |
| parent phase beats wrong rung | pass |
| movement share is consistent with broad half band | pass |
| \(L\) improves child→parent flow | pass |
| \(L\) improves parent→child flow | **fail** |

The numerical pattern is promising, but the method was deliberately not
allowed to call four positive signals a confirmation when breadth and
bidirectionality failed.

## Data quality and independent validation

Independent validation passed every check:

- source archive and protocol hashes matched;
- all saved summaries recomputed with zero numerical difference;
- raw density matrices reproduced cached \(L\), \(C\), and \(T=C+L\);
- maximum raw reconstruction discrepancy was
  `1.69e-08`;
- maximum local Bloch-vector norm was `0.95295`, within the physical bound;
- no non-finite local-product values occurred; and
- both visual outputs and phase-profile arrays had the expected shape.

## What this result changes

Q45 gives a concrete first answer to “what else is coupled to the 15 parent?”

The local-product relation \(L=ab^{\mathsf T}\):

- has an independently predictable parent-phase shape;
- contributes near half of the observed 15-cycle movement under the frozen
  path-length account;
- is a much larger and slower state component than \(C\); and
- strongly completes the upward prediction of the full parent.

It does **not** yet justify saying:

- \(L\) is the universal missing ARA half;
- the parent drives the child at a one-sample delay;
- the state itself is split 50:50;
- a new quantum entity has been discovered; or
- the result transfers beyond this already-open simulator archive.

## Best next test

The most informative next test is a frozen transfer with two separate
questions:

1. apply the same \(C/L/T\) decomposition and 15-cycle parent-phase mapping to
   a different intervention or untouched archive; and
2. predeclare a complete parent→child lag profile, such as lags `1..30`, with
   multiplicity control rather than choosing a successful delay after seeing
   the result.

That would distinguish:

- a genuinely stable parent complement;
- an upward-only descriptive decomposition;
- a delayed downward constraint missed by the one-step gate; and
- a result specific to the present mimic archive.

## Primary artifacts

- `Q45_15_CYCLE_PARENT_COMPLEMENT_PROTOCOL_v1_FROZEN.md`
- `Q45_15_CYCLE_PARENT_COMPLEMENT_RESULTS.json`
- `Q45_15_CYCLE_PARENT_COMPLEMENT_LINEAGES.csv.gz`
- `Q45_15_CYCLE_PARENT_COMPLEMENT_FLOW_SEEDS.csv`
- `Q45_15_CYCLE_PARENT_COMPLEMENT_PROFILES.npz`
- `Q45_15_CYCLE_PARENT_COMPLEMENT_DIAGNOSTICS.png`
- `Q45_15_CYCLE_PARENT_COMPLEMENT_DIAGNOSTICS.svg`
- `Q45_15_CYCLE_PARENT_COMPLEMENT_VALIDATION.json`
- `q45_15_cycle_parent_complement_test.py`
- `q45_validate_15_cycle_parent_complement.py`

