# Q33 — Two-Axis Parent/Child 3.5 Projection

**Date:** 26 July 2026  
**Ledger:** T287  
**Frozen implementation verdict:** **CROSS-RUNG 3.5 PROJECTION NOT SUPPORTED BY THIS IMPLEMENTATION**  
**Post-result ARA audit:** **IMPLEMENTATION INVALID AS A PURE ARA 3.5 TEST**  
**Independent validation:** PASS

> **Correction:** the frozen computation is reproducible, but it substituted
> an unbounded physical capacity ratio for ARA's fixed octave coordinate and
> averaged two recipients instead of retaining the single boundary-nearest
> child. Its raw measurements remain valid. Its negative `3.5` interpretation
> does not. See
> `Q33_POST_RESULT_ARA_COORDINATE_CORRECTION_2026-07-26.md`.

## Result first

This is the corrected quantum test of the ARA construction

\[
\underbrace{2}_{\substack{\text{complete}\\\text{same-rung span}}}
+
\underbrace{\left(1+\frac12\right)}_{\substack{\text{current-rung whole}\\
+\text{child at half capacity}}}
=
\underbrace{3.5}_{\text{two-axis path}}.
\]

The arithmetic was not the uncertain part. Q33 attempted to test whether the endpoint
relations called “children” in Q32 actually have half the source relation's
capacity when both are kept in one common parent-facing energy coordinate.
The calculation did not return one-half, but the post-result audit found that
this was the wrong quantity to use as an ARA rung coordinate.

Across 11,543 evaluation source events, the median two-child mean capacity
ratio was

\[
\rho_{\rm child\mid source}=1.27349,
\]

not \(0.5\). The corresponding median path was therefore

\[
L=3+\rho=4.27349,
\]

not \(3.5\) under the frozen implementation. Because \(\rho\) is an unbounded
flow/capacity ratio rather than a bounded ARA coordinate, this substitution is
not a faithful ARA path calculation.

This does **not** erase the Q32 ordered-handover result. Backward tracing
strengthened that part: the children began near their own local ARA pole, and
their summed realised energy gain closely matched the source loss at the
median. The correction is about tier identity: these endpoint relations behave
like neighbouring/same-network relations, not demonstrated one-rung-lower
children in the selected capacity coordinate.

## What was tested

The public Q27/Q28 simulator lineage supplies a connected \(3\times3\)
relation matrix \(C_p(t)\) for every pair \(p\).

### Local ARA cut

\[
\underbrace{x_p(t)}_{\substack{\text{local ARA}\\\text{position}}}
=
\frac{
2\underbrace{|\det C_p(t)|^{1/3}}_{\text{local relation closure}}
}{
\underbrace{Q_{0.95}^{\rm dev}(|\det C_p|^{1/3})}_{\text{its own frozen scale}}
}.
\]

Every relation remains a complete local `0–2` identity on this cut.

### Common parent-facing capacity

\[
\underbrace{E_p(t)}_{\text{connected-relation energy}}
=
\underbrace{\lVert C_p(t)\rVert_F^2}_{\text{squared matrix amplitude}},
\]

\[
\underbrace{\rho_{c\mid p}}_{\substack{\text{child capacity}\\
\text{inside source frame}}}
=
\frac{
\underbrace{Q_{0.95}^{\rm dev}(E_c)}_{\text{child frozen capacity}}
}{
\underbrace{Q_{0.95}^{\rm dev}(E_p)}_{\text{source frozen capacity}}
}.
\]

Unlike Q32's local normalization, this ratio does not independently stretch
every relation back to `0–2`. It therefore preserves a possible `1/2`
parent/child scale difference.

## Frozen source and route rules

- Development scales used only `t=0..249`.
- Evaluation source events used `t=258..492`.
- A source had to start at local `x>=1.5`, release on the next slice, and
  lose connected energy from its backward-traced crest.
- The two active relations touching the source's two endpoints were retained.
- Each source and child was traced backward eight slices:
  - source to its latest local maximum;
  - child to its latest local minimum.
- Topology-, seed- and time-displaced routes used the same two-child rule.
- No future child value selected an event or route.

The protocol and fidelity packet were SHA-256 frozen before outcome
calculation.

## Headline measurements

| Measurement | Evaluation result | Frozen target |
|---|---:|---:|
| Source events | 11,543 | at least 5,000 |
| Branch/seed strata | 200 | at least 100 |
| Exact child routes | 23,086 | at least 5,000 |
| Median child energy-capacity ratio | **1.27349** | 0.40–0.60 |
| `c2` median capacity ratio | **1.24587** | 0.35–0.65 |
| `c4` median capacity ratio | **1.30661** | 0.35–0.65 |
| Median complete path \(3+\rho\) | **4.27349** | 3.5 |
| Median backward child-origin `x` | **0.04137** | at most 0.5 |
| Events with both origins `x<=0.5` | **81.50%** | at least 50% |
| Median summed realised transfer ratio | **1.03265** | diagnostic only |
| Median combined axial movement angle | **26.46°** | diagnostic only |

Both frozen backward-pole gates passed. The half-capacity gates failed.

## Did the chosen energy definition hide the half-rung?

Two alternative scale readings were calculated as non-verdict diagnostics:

| Parent-facing reading | Exact median |
|---|---:|
| Squared-amplitude energy ratio | 1.27349 |
| Amplitude ratio | 1.10793 |
| Determinant-closure scale ratio | 1.14516 |

None recovered `0.5`. The negative half-capacity result is therefore not
specific to squaring the matrix amplitude.

## Controls

The exact relations were closer to `0.5` than topology and seed controls, but
not robustly better than the within-split time control:

| Control | Median-error advantage of exact | Cluster-bootstrap probability exact is better |
|---|---:|---:|
| Topology | 10.39% | 1.0000 |
| Seed `+37` | 7.18% | 1.0000 |
| Time `+137` | 1.01% | 0.9395 |

The frozen requirements were at least 5% and at least 0.95 against every
control. The time-control gates failed.

This means the endpoint route carries some topology-specific structure, but
its position near a half-capacity target is not temporally distinctive enough
to support the octave claim.

## ARA interpretation after correction

The raw quantum result separates three statements that had previously been
compressed together:

1. **Ordered release and accumulation:** supported inside this simulator by
   Q32.
2. **A child begins near its own pole before the observed handover:** supported
   more strongly by Q33.
3. **ARA projects a complete boundary child upward as `1 -> 0.5`:** this is a
   declared geometric rule, not a raw-amplitude hypothesis tested by Q33.

Plainly: the relations behave like genuine outgoing/incoming handover paths.
Q33 validly measured their variable load. It did not validly test the fixed
octave geometry. A corrected test must choose the single boundary-nearest child
and apply the declared `1 -> 0.5` projection before predicting an external
consequence.

The near-unity realised transfer diagnostic is notable:

\[
\operatorname{median}
\left(
\frac{\Delta E_{c_1}^{+}+\Delta E_{c_2}^{+}}
{\Delta E_p^{+}}
\right)
=1.03265.
\]

It is consistent with the two recipients collectively taking up roughly the
amount released by the source at the median. Because the simulator does not
guarantee local conservation and the ratio has a heavy tail, this is
descriptive evidence only.

## What Q33 does and does not say

Q33 does not directly test the corrected `2 + (1 + 0.5)` geometry. It tests
whether raw endpoint/source capacity happens to equal the geometric rung
coefficient. The post-result audit identifies that as a category error.

It therefore does not falsify:

- the ARA `3.5` rule for a genuinely independently identified parent/child
  rung pair;
- the local TE-ARA completeness of each endpoint relation;
- ordered source-to-recipient handover;
- singularity or phase-flip hypotheses outside the measured cut.

The clean next version must identify the boundary child geometrically, apply
the fixed half-rung projection, preserve the singularity flip, and use that
route to predict an independently observable outcome. Raw energy can then test
the flow over the route, but cannot redefine the route.

## Reproduction

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q33_two_axis_parent_child_35_test.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q33_validate_two_axis_parent_child_35.py'
```

Primary artifacts:

- `Q33_TWO_AXIS_PARENT_CHILD_35_RESULTS.json`
- `Q33_TWO_AXIS_PARENT_CHILD_35_EVENTS.csv.gz`
- `Q33_TWO_AXIS_PARENT_CHILD_35_TRIALS.csv`
- `Q33_TWO_AXIS_PARENT_CHILD_35_GEOMETRY.png`
- `Q33_TWO_AXIS_PARENT_CHILD_35_NOTEBOOK.ipynb`
- `Q33_TWO_AXIS_PARENT_CHILD_35_VALIDATION.json`

The deterministic full event table is gzip-compressed and ignored by Git
because it remains about 26 MB. Running the primary script recreates it from
the checksum-locked caches; the compact result, trial table, figure and
independent validator are the repository-facing audit path.

## Evidence boundary

This is retrospective evidence from one already-open, exactly diagonal
simulator lineage. The evaluation partition was unchanged but has already been
used in Q27–Q32. It is not fresh blind replication, hardware quantum data, or
a universal physical calibration of the ARA rung scale.

## Corrected successor

Q33B subsequently held the ARA `1 -> 0.5` projection fixed and tested its
directed boundary-child flow consequence. All frozen Q33B gates passed.
See `Q33B_ARA_FIRST_BOUNDARY_CHILD_REPORT_2026-07-26.md`.
