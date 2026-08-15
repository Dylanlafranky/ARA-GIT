# T380 — same-scale muon child cut

**Frozen:** 14 August 2026, before evaluating the same-scale child coordinates
against the later daughter delay.

## Question

T379 cut the four-counter detector into an upper half and a lower half. That
mostly recovered the parent-scale stopping-depth relation. T380 asks the
different question requested by the framework:

> When each adjacent counter pair is cut at its own scale, does the relation
> between those two child cuts carry prospective information about the later
> linked daughter time that is absent from the parent cut and ordinary detector
> geometry?

This is an event-level timing test. It does not directly observe either
neutrino.

## W5H

- **Who:** clean event-linked incoming-muon/later-electron candidates from the
  same public QuarkNet detector 6845 archive used in T379.
- **What:** the ARA relation inside the upper adjacent counter pair and inside
  the lower adjacent counter pair, followed by their same-scale coupling.
- **When:** February 11–12, 2020 remain calibration; March 17–18, 2020 remain
  untouched chronological holdout.
- **Where:** four closely stacked solid-plastic scintillator counters. No
  detector, medium, source or event-linking rule changes from T379.
- **Why:** a child can show evidence of its parent in a coarse cut, but seeing
  the child itself requires a cut at the child's scale.
- **How:** compute the two child coordinates from the incoming pulse only,
  freeze the models on calibration, then reveal and score the later daughter
  delay on holdout.

## Cohort

Only events with a positive gain-normalised prompt measurement in all four
counters are eligible. These events expose both adjacent two-counter children.
The already-reduced T379 event table contains 682 calibration and 572 holdout
events meeting this rule. No later-electron property participates in cohort
selection.

## Frozen coordinates

For gain-normalised incoming prompt strengths `q1...q4`, define the upper and
lower adjacent children:

\[
x_U=\frac{2q_2}{q_1+q_2},
\qquad
x_L=\frac{2q_4}{q_3+q_4}.
\]

Each coordinate lies on its own `0–2` ARA line. `0` and `2` are the two poles;
`1` is the same-scale ridge of that pair.

Decompress their joint relation as

\[
s_U=x_U-1,\qquad s_L=x_L-1,
\]

\[
C=\frac{s_U+s_L}{2}
\quad\text{(shared child direction)},
\]

\[
D=\frac{s_U-s_L}{2}
\quad\text{(child mismatch)},
\]

\[
K=1-|D|
\quad\text{(same-scale coupling/closure)},
\]

and retain the signed interaction `I=sU*sL` to distinguish aligned from
opposed child motion. `K` is a descriptive coordinate; the fitted term is
`|D|`, which contains exactly the same information without an arbitrary
offset.

The T379 parent cut remains

\[
x_P=\frac{2(q_3+q_4)}{q_1+q_2+q_3+q_4}.
\]

It is a control, not the T380 child coordinate.

## Frozen models

All models use the same truncated-exponential plus uniform-background outcome
model used in T379 over `0.3–10 microseconds`.

- `M0`: intercept only.
- `MG`: ordinary incoming geometry — log total prompt strength and ordinary
  depth centroid. Fourfold multiplicity is constant and is omitted.
- `MP`: `MG` plus the old parent coordinate `xP`, its absolute ridge distance,
  and the parent-by-depth interaction.
- `MC`: `MP` plus the same-scale child terms `C`, `D`, `|D|`, and `I`.
- `MW13_24`: the same child construction after the wrong pairing `(1,3)` and
  `(2,4)`.
- `MW14_23`: the same child construction after the wrong pairing `(1,4)` and
  `(2,3)`.

The primary increment is

\[
\Delta_{child}=\operatorname{NLL}(MP)-\operatorname{NLL}(MC).
\]

This asks whether the same-scale child cut adds information after the parent
cut is already known. The wrong-pair models use the same number and form of
additional terms as `MC`.

## Frozen gates

The same-scale child result is **supported** only if all are true:

1. `Delta_child > 0` separately in both untouched March holdout runs.
2. The chronological-block bootstrap 95% interval for `Delta_child` is wholly
   above zero.
3. `MC` beats both wrong-pair controls on pooled held-out NLL.
4. The observed `Delta_child` exceeds the 97.5th percentile of the within-run
   outcome-permutation distribution.

Failure of any gate gives **not supported**. A positive point estimate with an
interval crossing zero is a lead, not confirmation.

## Secondary diagnostics

- 2D held-out occupancy on `(xU,xL)` with both child ridges marked.
- Binned mean ordinary-model residual over that same plane.
- Held-out NLL for every frozen model, with exact values.
- Per-run increments and chronological-block uncertainty.
- Calibration versus holdout coordinate drift.
- Correlations of child coordinates with parent depth and total prompt
  strength, to identify detector-geometry redundancy.
- Descriptive daughter-delay summaries near the four same-scale quadrant
  centers. These are not independent gates.

## Boundaries

- The later electron is the visible daughter proxy. The two neutrinos are not
  directly measured.
- `xU`, `xL`, `C`, `D`, `K` and `I` are deterministic transforms of four prompt
  counter measurements. Support would mean useful same-scale decomposition,
  not proof of a universal ARA ontology.
- T379's fourfold-only parent result was already opened and had a positive but
  uncertain point estimate. T380 is not an independent dataset replication;
  it is a newly frozen deeper cut of that declared lead.
- No event is selected or tuned using its later daughter delay.

