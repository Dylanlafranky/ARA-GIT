# Q45 — 15-cycle parent-complement shaping protocol

Date frozen: 28 July 2026 (Australia/Brisbane)

Status: **pre-analysis frozen descriptive protocol**.

This test uses the already-open Q44 public simulator archive. It may shape and
falsify the proposed parent-complement mapping, but it is not an independent
replication and cannot alter the prospective Q44/Q44A verdict.

## Question

The approximately `7.5` connected child is a complete ARA identity at its own
rung and projects to `0.5` in the approximately `15` parent frame. What
observable relation, if any, supplies the other parent-level contribution?

The first candidate is the local product relation

\[
L(t)=a(t)b(t)^{\mathsf T},
\]

where \(a\) and \(b\) are the two local Bloch vectors. The already measured
connected relation is

\[
C(t)=T(t)-a(t)b(t)^{\mathsf T},
\]

and the full two-body Pauli relation is

\[
T(t)=C(t)+L(t).
\]

The exact last equality is bookkeeping and is **not** a test result. Q45 asks
whether \(L\) has the cadence, participation, phase and lagged information
expected of the missing parent complement.

## Source and fixed scope

- Public archive: `unnati_submit_12_inhomo_v1_mimic.hdf5.zip`
- Deposited MD5: `08b2eaa89268952f7e197eecb2ea9610`
- Branch: `c2_2local connectivity`
- Seeds: `0..99`
- Time samples: `0..499`
- Two-qubit pairs: all `66`
- Development interval: samples `0..249`
- Evaluation interval: samples `250..499`

The density matrices, \(C\), and the Q44 results have already been observed.
The local-product candidate \(L\) has not been computed for this test before
this protocol is frozen.

## ARA-first unit definitions

At the child rung, \(C\) remains one complete identity with internal Phase A,
Phase B and their relation. Its internal poles are not counted as two separate
parent contributions.

At the parent rung the proposed pure projection is

\[
\frac12_C+\frac12_Y=1_P,
\]

where \(Y\) is unknown. Q45 tests \(Y=L\).

For a 15-sample parent path, movement participation is measured without
assuming additivity of squared amplitudes:

\[
P_X(t)=\sum_{j=0}^{14}\left\|X(t+j+1)-X(t+j)\right\|_F,
\]

\[
s_L(t)=\frac{P_L(t)}{P_C(t)+P_L(t)},
\qquad
s_C(t)=1-s_L(t).
\]

The corresponding 0–2 display coordinates are

\[
x_L=2s_L,\qquad x_C=2s_C.
\]

Thus equal parent-path participation is \(s_L=s_C=0.5\), or
\(x_L=x_C=1.0\). This is a movement-share diagnostic, not a claim that tensor
norm is physical energy.

The signed relation between child and candidate movement is retained as

\[
j_{CL}(t)=
\frac{\langle\Delta C(t),\Delta L(t)\rangle_F}
{\|\Delta C(t)\|_F\|\Delta L(t)\|_F}.
\]

This is the visible third term: the two movements plus how they align.

## Eligibility and parent phase

Eligibility is determined from the connected closure \(C\) only.

1. Construct the established Q40 ARA cut from
   \(h_C=|\det C|^{1/3}\).
2. Use development samples only to fit the unwrapped ARA orbit.
3. Retain a lineage when development yields either:
   - `two_turn_7_5`: period `7.35..7.65` and lag-15 coordinate
     correlation at least `0.95`; or
   - `one_turn_15`: period `14.8..15.2` and lag-15 coordinate
     correlation at least `0.95`.
4. Extrapolate the development phase into evaluation. Evaluation \(C\), \(L\)
   or \(T\) may not be used to refit phase or cadence.

For `two_turn_7_5`, the parent phase is one half of the fitted child phase. For
`one_turn_15`, the fitted phase is already the parent phase. The wrong-rung
control uses the unhalved child phase in the first family and the doubled
phase in the second family.

Minimum adequacy:

- at least `80` represented seeds;
- at least `1,000` eligible lineages; and
- at least `10,000` evaluation phase observations.

## Frozen analyses

### A. Parent-phase reconstruction

For each eligible lineage, build a `16`-bin template of the nine entries of
\(L\) using development samples and the extrapolated 15-cycle parent phase.
Apply the frozen template to evaluation samples.

Comparators:

1. development mean of \(L\);
2. wrong-rung phase template;
3. fixed four-sample lagged phase template, used as a quarter-cycle timing
   control.

Primary score:

\[
\mathrm{skill}=1-
\frac{\sum\|\widehat L-L\|_F^2}
{\sum\|\bar L_{\mathrm{dev}}-L\|_F^2}.
\]

Positive skill means the 15-cycle phase predicts held-out candidate shape
better than a static candidate.

### B. Parent-path participation

Use non-overlapping 15-sample windows in evaluation and calculate \(s_L\),
\(s_C\), \(x_L\), \(x_C\), and \(j_{CL}\). Summaries are first balanced by
lineage and then by seed.

The proposed half-complement location is treated as descriptively consistent
when the seed-balanced median \(s_L\) lies in `[0.40, 0.60]` and its 95%
seed-bootstrap interval contains `0.50`.

### C. Child-to-parent lagged flow

Let \(\Delta X_t=X_t-X_{t-1}\). Fit scalar coefficients on development only:

\[
\widehat{\Delta T}_{t+1}
=\alpha\Delta C_t
\]

versus

\[
\widehat{\Delta T}_{t+1}
=\alpha\Delta C_t+\beta\Delta L_t.
\]

The candidate adds forward information only when the augmented evaluation
error is lower and the 95% seed-bootstrap interval for the error advantage is
strictly positive.

### D. Parent-to-child lagged flow

Fit on development only:

\[
\widehat{\Delta C}_{t+1}
=\gamma\Delta C_t
\]

versus

\[
\widehat{\Delta C}_{t+1}
=\gamma\Delta C_t+\kappa\Delta L_t.
\]

The candidate adds downward/constraint information only when the augmented
evaluation error is lower and the 95% seed-bootstrap interval for the error
advantage is strictly positive.

For both directions, a four-sample-lagged \(L\) model is retained as a timing
control. Coefficients are pooled scalar gains, not unrestricted nine-entry
matrix regressions.

## Frozen interpretation gates

The candidate \(L\) is **supported in this shaping archive** only if:

1. adequacy passes;
2. the parent-phase template has positive held-out skill with a strictly
   positive 95% seed-bootstrap interval;
3. the parent-phase template beats the wrong-rung template with a strictly
   positive 95% interval;
4. the path-share estimate satisfies the declared half-complement band;
5. child-to-parent augmented flow has a strictly positive error advantage;
6. parent-to-child augmented flow has a strictly positive error advantage.

`PARTIAL` means adequacy passes and at least three of gates 2–6 pass.
`NOT SUPPORTED` means adequacy fails or fewer than three of gates 2–6 pass.

No outcome may be described as a universal quantum law or an independent ARA
replication.

## Falsifiers and scientific boundaries

The \(L\) parent-complement proposal takes a direct hit if:

- \(L\) has no reproducible 15-cycle phase structure;
- the wrong-rung template performs as well or better;
- \(L\)'s movement participation is far from the proposed missing half;
- real \(L\) adds no lagged information beyond \(C\); or
- an equally sized mistimed control performs as well.

Even a fully supported result would not establish:

- that \(L\) is a hidden particle, field or unmeasured physical sector;
- that ARA units are joules;
- a universal exact `0.5` across quantum systems;
- causal influence from a statistical forecast alone; or
- transfer to a new archive, gate angle, simulator or device.

The next rung after a supported shaping result is to freeze the same mappings
and apply them unchanged to an untouched archive with a changed intervention.

