# Q53 — recorded qutrit external-return protocol v1 (frozen)

**Frozen before reconstructing or inspecting the directional trajectory:**  
30 July 2026

**Source class:** recorded measurements from one physical trapped-ion qutrit  
**Measured object:** the external centreline carrying complete projected
qutrit-state circuits through recorded time

## 1. Exact question

Q53 asks only:

> Does the recorded whole-direction vector repeatedly travel between the
> \(1/e\) and \(\phi\) directional landmarks and back, completing an active
> \(0\rightarrow2\rightarrow0\) ARA traversal?

Q53 does **not** test a parent ridge, child cancellation, TE-ARA closure,
energy, the local 7.5/15 cadence, or the internal turn of a circuit.

## 2. Immutable source

- Experiment: *Sustained state-independent quantum contextual correlations
  from a single ion*.
- Public file: `ExpDataYuOh.csv`.
- Local SHA-256:
  `5410775C307EDEA9F68E95133CF0A733B6CD34E7D9D774B6509472FACE74D55D`.
- Profiled valid measurements: `53,459,987`.
- Valid recorded subsequences: `53,301`.
- Source-flagged purged subsequences: `1,062`.

Only rows beginning with `o` are omitted, exactly as instructed by the source.
No simulated continuation, interpolation, imputation, or generated future is
allowed.

Each retained pair contains:

1. the measured Yu–Oh ray, numbered `1` through `13`;
2. the recorded photon count.

The physical source threshold is retained without fitting:

- photon count `>= 6`: bright;
- photon count `<= 5`: dark.

## 3. Fixed ray geometry

The ray numbers are mapped to Table I of the source paper in its published
order, then normalized:

```text
 1  ( 0,  1, -1)      8  ( 1, -1,  1)
 2  (-1,  0,  1)      9  ( 1,  1, -1)
 3  ( 1, -1,  0)     10  ( 1,  1,  1)
 4  ( 0,  1,  1)     11  ( 1,  0,  0)
 5  ( 1,  0,  1)     12  ( 0,  1,  0)
 6  ( 1,  1,  0)     13  ( 0,  0,  1)
 7  (-1,  1,  1)
```

No rotation is fitted to the observed trajectory.

## 4. Recorded-state reconstruction

The reconstruction translates the recorded ray and response into the
post-measurement direction. It does not predict or generate an observation.

Let \(\psi_{t-1}\) be the preceding real qutrit direction and \(r_t\) the
recorded normalized ray.

For a bright result:

\[
\psi_t=r_t .
\]

For a dark result:

\[
\psi_t=
\frac{(I-r_tr_t^\mathsf T)\psi_{t-1}}
{\left\|(I-r_tr_t^\mathsf T)\psi_{t-1}\right\|}.
\]

Because a quantum ray is unchanged by \(\psi\mapsto-\psi\), choose the sign
at each step that maximizes continuity with \(\psi_{t-1}\). At an exact tie,
use the sign whose first non-zero component is positive.

Every valid source row ends bright. The first retained row is used only to
establish its known final ray; directional extraction starts with the next
row. A dark update with norm below `1e-10` is a recorded/reconstruction
inconsistency: end the current circuit lineage and wait for the next bright
result to re-establish direction. It is reported, not silently repaired.

## 5. Three fixed sphere cuts

Use all three coordinate planes without selecting a winner:

1. \((\psi_0,\psi_1)\);
2. \((\psi_1,\psi_2)\);
3. \((\psi_2,\psi_0)\).

Within each cut, label the four sign quadrants. A complete internal circuit
must visit four adjacent quadrants in strict cyclic order, clockwise or
counter-clockwise, and return to its starting quadrant. A two-quadrant jump
breaks the candidate circuit. Repeated samples inside one quadrant are
retained.

A projected point lying exactly on either cut axis is retained in the circle
fit but does not declare a new quadrant. It inherits the last non-boundary
quadrant for transition tracking; before any non-boundary quadrant has been
seen, it cannot start a circuit.

A circuit must contain at least six projected points. Fit its algebraic
circle using all its points and retain its centre, radius, ordinary centroid,
extrema midpoint and median relative radial residual. No residual threshold
is used to select a preferred result; residual bands `<=0.25`, `<=0.50` and
all finite fits are reported separately.

## 6. Whole-direction vector

For each interior circuit \(r\) in the same continuous lineage:

\[
\mathbf d_r=\mathbf c_{r+1}-\mathbf c_{r-1},
\qquad
m_r=
\frac{\|\mathbf d_r\|}
{\operatorname{mean}(R_{r-1},R_r,R_{r+1})}.
\]

The primary movement gate remains the previously frozen Q49 value
\(m_r\ge0.01\). Sensitivities `0`, `0.005`, `0.02`, and `0.05` are reported.

The heading is:

\[
h_r=
\operatorname{frac}
\left[
\frac{\operatorname{atan2}(d_{r,2},d_{r,1})}{2\pi}
\right].
\]

This is the direction of the **whole fitted circuit moving through recorded
time**, not the internal direction around the circuit.

## 7. \(1/e\leftrightarrow\phi\) ARA

\[
L=\frac1e,
\qquad
R=\operatorname{frac}(\phi)=\phi-1,
\qquad
W=R-L.
\]

For a heading inside the oriented arc \([L,R]\):

\[
x=2\frac{h-L}{W}.
\]

Thus:

- \(1/e\mapsto0\);
- \(\phi-1\mapsto2\).

The three matched controls are equal-width arcs beginning one, two and three
quarter-turns after \(L\). They are fixed before inspection.

## 8. Complete active return

Within one uninterrupted carrier run inside the tested arc, a strict complete
return is:

\[
x\le0.25
\quad\longrightarrow\quad
x\ge1.75
\quad\longrightarrow\quad
x\le0.25.
\]

The reverse `2 → 0 → 2` is reported separately and cannot replace the primary
direction.

Every participating event must pass the movement gate. Returns are counted
without reusing an endpoint as the start of more than one return.

## 9. Frozen controls and gates

### G0 — source and reconstruction integrity

- source hash matches;
- all retained ray labels are `1…13`;
- all source-flagged rows are omitted;
- no generated values enter the record;
- all finite reconstructed directions have unit norm within `1e-9`;
- reconstruction inconsistencies and lineage breaks are reported.

G0 earns no evidence.

### G1 — declared directional location

At `m >= 0.01`, the declared \(1/e\rightarrow\phi\) arc must have higher
eligible heading occupancy than every matched rotated arc in at least two of
the three fixed sphere cuts.

### G2 — complete ordered return

The declared arc must contain strict active `0 → 2 → 0` returns in at least
two of the three fixed sphere cuts and independently in each chronological
third of the record.

### G3 — time order

Within each cut and chronological third, permute eligible headings inside
fixed consecutive blocks of `10,000` events. Use `1,000` deterministic
permutations with seed `530053`.

The declared-arc return rate must exceed the `99th` percentile of the shuffled
return rate in at least two cuts. This preserves the observed heading
distribution while removing its precise order.

### G4 — landmark specificity

The declared arc's non-overlapping `0 → 2 → 0` return rate must exceed the
return rate in each of its three matched rotated arcs in at least two cuts.

## 10. Verdict

- **SUPPORTED:** G0–G4 pass.
- **MIXED:** G0 passes and exactly two or three of G1–G4 pass.
- **NOT SUPPORTED:** G0 passes and fewer than two substantive gates pass.
- **INVALID / NOT TESTABLE:** G0 fails or too few complete circuits survive to
  define an external direction.

The result must also state which cuts, chronological thirds and centre
estimators carry or fail the pattern.

## 11. Interpretation boundary

A pass would show repeated ordered \(1/e\rightarrow\phi\rightarrow1/e\)
whole-direction traversal in this recorded single-qutrit experiment under the
declared reconstruction. It would not by itself prove universal Phi, a
fundamental time vector, or universal ARA geometry.

A failure would reject this directional realization on this experimental
record. It would not be relabelled as a ridge result, because ridge behaviour
is not the Q53 question.
