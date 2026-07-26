# Q33B — ARA-First Boundary-Child Flow Route

**Date:** 26 July 2026
**Ledger:** T288
**Frozen verdict:** **BOUNDARY-CHILD FLOW ROUTE SUPPORTED INSIDE THIS SIMULATOR**
**Independent validation:** PASS

## Result first

Q33B corrected Q33's category error by treating ARA as the generator and the
measured quantum relation as variable flow over that geometry.

The structural route was fixed before outcomes:

\[
\underbrace{2}_{\substack{\text{complete}\\\text{same-rung span}}}
+
\left(
\underbrace{1}_{\substack{\text{current-rung}\\\text{contribution}}}
+
\underbrace{\frac12}_{\substack{\text{single boundary child}\\
\text{projected one octave up}}}
\right)
=
\underbrace{\frac72}_{\text{ARA route}}.
\]

The `0.5` was not estimated from energy. It generated a directed prediction:
of the two endpoint recipients, the one closest to the child-side `0`
boundary should receive the flipped flow after its high-side source releases.

All frozen eligibility and routing gates passed.

Across `11,543` evaluation source events:

- boundary-child median normalized closure flow: `+0.04143`;
- boundary-child mean flow: `+0.04952`;
- positive next flow: `63.64%`;
- sibling positive flow: `55.83%`;
- topology control: `50.79%`;
- seed control: `56.38%`;
- time control: `56.02%`.

Every branch/seed-cluster bootstrap gave probability `1.000` that exact
boundary flow exceeded the sibling or named control.

## Geometry and measurement

### Fixed adjacent-rung geometry

The same fractal boundary is viewed as:

- the child's singularity;
- the parent's `1.0` ridge.

A complete child contribution at its own rung is `1`. One octave upward:

\[
\underbrace{\mathcal R_\uparrow}_{\text{fixed rung projection}}
\left(
\underbrace{1_c}_{\text{complete child identity}}
\right)
=
\underbrace{0.5}_{\text{child inside parent frame}}.
\]

This geometry is invariant. Raw energy does not redefine it.

### Boundary selection without future leakage

For each endpoint child:

\[
\underbrace{z_c(t)}_{\substack{\text{relative starting}\\\text{closure load}}}
=
\frac{
\underbrace{h_c(t)}_{|\det C_c(t)|^{1/3}}
}{
\underbrace{Q_{0.95}^{dev}(h_c)}_{\text{child's frozen reference}}
}.
\]

The smaller starting \(z\) selects the child nearer the low boundary. Ties use
pair index. This monotone ratio orders the candidates; it is not substituted
for the fixed `0.5` rung coefficient.

The observed flow is:

\[
\underbrace{g_c(t)}_{\substack{\text{next relation-closure}\\\text{movement}}}
=
\frac{h_c(t+1)-h_c(t)}{Q_{0.95}^{dev}(h_c)}.
\]

ARA supplied which route to inspect. The simulator supplied \(g_c\).

## Source and controls

Q33B retained the Q33 source definition:

- source on the high side with `2z>=1.5`;
- source closure falls on the next slice;
- source connected energy falls from its latest eight-slice crest;
- source is not itself an active matching edge;
- deterministic one-in-sixteen sampling;
- development scales from `t=0..249`;
- evaluation events from `t=258..492`.

Controls all used the same one-of-two lower-\(z\) rule:

1. the exact sibling;
2. two baseline-matched, non-endpoint topology relations;
3. endpoint relations from seed `+37`;
4. endpoint relations from time `+137`.

## Headline flow table

| Route | Events | Median \(g\) | Mean \(g\) | Positive fraction |
|---|---:|---:|---:|---:|
| Exact boundary child | 11,543 | **+0.04143** | **+0.04952** | **63.64%** |
| Exact sibling | 11,543 | +0.04081 | +0.02570 | 55.83% |
| Topology | 11,543 | +0.00033 | +0.01335 | 50.79% |
| Seed `+37` | 10,788 | +0.00237 | +0.02146 | 56.38% |
| Time `+137` | 10,790 | +0.00203 | +0.02126 | 56.02% |

The sibling's marginal median is close to the exact median, but its flow is
much wider and less reliably positive. The boundary-selected child has the
higher mean, higher positive fraction and positive paired median difference.

## Paired route tests

| Comparator | Median exact-minus-route flow | Cluster mean difference | Bootstrap probability exact is greater |
|---|---:|---:|---:|
| Sibling | +0.01781 | +0.02363 | 1.000 |
| Topology | +0.03385 | +0.03603 | 1.000 |
| Seed | +0.02997 | +0.02792 | 1.000 |
| Time | +0.02909 | +0.02832 | 1.000 |

Both connectivity branches reproduced:

| Branch | Events | Median exact flow | Positive fraction |
|---|---:|---:|---:|
| `c2` | 5,772 | +0.04281 | 63.34% |
| `c4` | 5,771 | +0.03964 | 63.94% |

Development and evaluation were also stable:

- development median `+0.04170`, positive `63.79%`;
- evaluation median `+0.04143`, positive `63.64%`.

## What the positive result means

Inside this simulator, the ARA-first boundary rule selects a recipient that:

- moves inward from the declared child-side boundary more reliably;
- gains more normalized relation closure on average;
- beats its sibling and relation-broken alternatives;
- reproduces across both connectivity branches and time partitions.

This is evidence for the **directed boundary-child flow consequence** of the
fixed route.

It is not a numerical recovery of `3.5`. The number `3.5` is the structural
coordinate that generated the child-selection and flip prediction.

## Important qualifications

### Lower-of-two selection

Choosing the lower of two candidates creates generic headroom or
mean-reversion pressure. Q33B addresses this by applying the same lower-of-two
rule to topology, seed and time controls. Those controls were already mildly
positive (`50.79–56.38%`), confirming that generic effect exists.

The evidential result is the excess exact route:

- `+7.81` percentage points over sibling;
- `+12.85` over topology;
- `+7.26` over seed;
- `+7.62` over time.

The control starting-\(z\) distributions are not perfectly identical. This is
a caveat for physical effect-size interpretation, although the controls often
began even closer to zero and still gained less.

### Closure flow is not raw energy flow

The primary supported quantity is normalized determinant-closure movement.
Raw connected-energy movement was secondary:

- exact median energy flow `+0.01785`;
- sibling median `+0.03482`;
- topology/seed/time near zero.

Thus Q33B supports more reliable **relation closure**, not a claim that the
chosen child always receives more literal energy than its sibling.

### Evidence boundary

The source is the already-open, exactly diagonal Q27/Q28 simulator used
throughout Q27–Q33. The evaluation partition was unchanged but not blind. This
is not hardware quantum evidence, physical conservation, universal ARA,
Phase-B identification or validation of the cosmological
\(\varphi^{3.5}\) ratio.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q33b_ara_first_boundary_child_test.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q33b_validate_ara_first_boundary_child.py'
```

Primary artifacts:

- `Q33B_ARA_FIRST_BOUNDARY_CHILD_FIDELITY_v1.md`
- `Q33B_ARA_FIRST_BOUNDARY_CHILD_PROTOCOL_v1_FROZEN.md`
- `Q33B_ARA_FIRST_BOUNDARY_CHILD_RESULTS.json`
- `Q33B_ARA_FIRST_BOUNDARY_CHILD_TRIALS.csv`
- `Q33B_ARA_FIRST_BOUNDARY_CHILD_GEOMETRY.png`
- `Q33B_ARA_FIRST_BOUNDARY_CHILD_NOTEBOOK.ipynb`
- `Q33B_ARA_FIRST_BOUNDARY_CHILD_VALIDATION.json`

The deterministic gzip event table is Git-ignored because of its size and is
recreated by the primary script from checksum-locked source caches.
