# Session Record — Q33 Corrected Two-Axis 3.5 Quantum Test

**Date:** 26 July 2026  
**Participants:** Dylan La Franchi and Sol/Codex  
**Ledger:** T287

> **Post-result correction:** Q33's calculations reproduce, but the method
> conflated raw physical capacity with ARA's invariant octave coordinate and
> averaged both endpoint recipients. The record below preserves the frozen
> attempt. It is not a valid negative test of the pure `3.5` construction.

## Why this test was restarted

Q30 had operationalized the quantum `1.5` as an Information³
triangle-closing edge. Dylan corrected that translation by returning to the
older dark-sector and prime-rung construction:

- a complete same-rung ARA span contributes `2`;
- a crossed-rung leg retains one complete current-rung contribution, `1`;
- a child viewed inside the parent frame contributes half, `0.5`;
- therefore the legal two-axis route is `2 + 1.5 = 3.5`.

The `0.5` is a parent-facing projection. The child is still a complete local
TE-ARA of `2` when opened inside its own identity.

The methodological error to avoid was naming Q32's later endpoint recipient a
lower-rung child without measuring the scale difference.

## Frozen translation

For connected relation matrix \(C_p(t)\):

\[
h_p(t)=|\det C_p(t)|^{1/3},
\qquad
x_p(t)=\frac{2h_p(t)}{Q_{.95}^{dev}(h_p)}.
\]

This is the relation's local ARA cut.

The common capacity coordinate is

\[
E_p(t)=\lVert C_p(t)\rVert_F^2,
\qquad
\rho_{c\mid p}
=
\frac{Q_{.95}^{dev}(E_c)}{Q_{.95}^{dev}(E_p)}.
\]

The corrected ARA prediction is

\[
\rho_{c\mid p}\approx0.5,
\qquad
V=1+\rho\approx1.5,
\qquad
L=3+\rho\approx3.5.
\]

The protocol used development `t=0..249` to freeze local and common scales.
Source events occupied `t=258..492` in the unchanged evaluation half. Each
source was traced backward eight slices to its latest crest; each of its two
active endpoint recipients was traced backward to its latest local pole.
Equal-count topology, seed `+37` and time `+137` routes were controls.

Frozen protocol SHA-256:
`C91AFEDC4A01B763B81940A0057929644DDDE1806825AFCDF21A7FCED48F0A23`.

## Results

- Evaluation source events: `11,543`.
- Branch/seed strata: `200`.
- Exact endpoint routes: `23,086`.
- Median energy-capacity ratio: `1.27349`.
- Median complete route: `4.27349`.
- `c2` median ratio: `1.24587`.
- `c4` median ratio: `1.30661`.
- Median amplitude ratio: `1.10793`.
- Median determinant-closure scale ratio: `1.14516`.

The raw-capacity equality-to-half test failed in both branches and under all
three scale readings. A post-result audit determined that raw capacity was not
the ARA rung coordinate and therefore could not test the structural `0.5`.

Exact half-distance was better than topology and seed controls, but the time
control remained almost identical:

- topology advantage `10.39%`, bootstrap `1.0000`;
- seed advantage `7.18%`, bootstrap `1.0000`;
- time advantage `1.01%`, bootstrap `0.9395`.

The frozen time-control gates required at least `5%` and `0.95`.

## Strong surviving result

Backward tracing resolved the uncertainty raised by Q32:

- median exact child-origin local `x = 0.04137`;
- both endpoint recipients began at `x<=0.5` in `81.50%` of events;
- both frozen pole-origin gates passed.

The median summed realised child gain divided by source loss was `1.03265`.
The median combined axial movement angle was `26.46°`. Both are diagnostics,
not verdict gates.

## Scientific interpretation

The session separated three claims:

1. a releasing source is followed by ordered endpoint-recipient accumulation;
2. those recipients can be traced back toward their own local poles;
3. ARA projects the complete boundary child upward with structural weight
   `0.5`, independently of its variable physical load.

The first was supported by Q32. The second is supported by Q33. The third was
not validly tested by the frozen Q33 implementation.

Plainly: “recipient that responds next” and “one-rung-lower child” are not
synonyms. The endpoint relations live in the same simulated pair-relation
network and behave more like comparable-capacity neighbours than half-sized
children.

This does not reject the conditional two-axis `3.5` theorem. The frozen
implementation's negative interpretation is retired; only its raw-capacity
and backward-origin diagnostics remain.

## Next safe thread

To test `3.5` again, identify two tiers independently before looking at their
capacity ratio. Then:

1. keep every identity locally complete on its own `0–2`;
2. project the lower identity into the upper frame without renormalizing it;
3. freeze the expected half-capacity and controls;
4. test whether the lower tier actually contributes `0.5`;
5. only then assemble `2 + (1 + 0.5)`.

Do not infer the rung solely from temporal ordering or endpoint adjacency.

## Artifacts

- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_FIDELITY_v1.md`
- `analysis/quantum/Q33_POST_RESULT_ARA_COORDINATE_CORRECTION_2026-07-26.md`
- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_PROTOCOL_v1_FROZEN.md`
- `analysis/quantum/q33_two_axis_parent_child_35_test.py`
- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_RESULTS.json`
- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_EVENTS.csv.gz`
- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_TRIALS.csv`
- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_GEOMETRY.png`
- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_REPORT_2026-07-26.md`
- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_NOTEBOOK.ipynb`
- `analysis/quantum/q33_validate_two_axis_parent_child_35.py`
- `analysis/quantum/Q33_TWO_AXIS_PARENT_CHILD_35_VALIDATION.json`

The full gzip event table is deterministic and Git-ignored because of its
size. The primary script reproduces it from checksum-locked Q27/Q28 caches.

## Evidence boundary

The source is the same already-open, exactly diagonal public simulator used in
Q27–Q32. The later split was unchanged but has been inspected in previous
tests. This is not fresh blind replication, hardware data, a universal
quantum result or validation of the cosmological \(\varphi^{3.5}\) ratio.

## Corrected successor

Q33B then implemented the ARA-first version: keep `1 -> 0.5` structural,
select the single boundary-nearest endpoint, and score its next
relation-closure flow. All frozen gates passed. The full successor record is
`SESSION_RECORD_2026-07-26_Q33B_ARA_FIRST_BOUNDARY_CHILD.md`.
