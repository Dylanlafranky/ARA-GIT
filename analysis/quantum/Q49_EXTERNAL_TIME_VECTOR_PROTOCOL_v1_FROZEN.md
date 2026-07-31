# Q49 — external quantum time-vector protocol v1

**Frozen:** 30 July 2026 before any cycle-centre or centreline-heading value
was calculated  
**Ledger:** T309  
**Fidelity packet:** `Q49_EXTERNAL_TIME_VECTOR_FIDELITY_PACKET_v1.md`  
**Dylan verdict:** `EXACT ENOUGH TO TEST`  
**Status:** retrospective test on an opened deterministic simulator; the
external centreline observable itself is newly calculated

## Registered claim

The external centreline carrying each complete internally rotating quantum
ARA circle through time preferentially points along the oriented unit-turn
arc

\[
\boxed{
\frac1e
\longrightarrow
\operatorname{frac}(\phi)=\phi-1
}.
\]

The internal rotation of the circle is already known and is not the target.

## Source

Reuse the Q39 public `pure_strongmax` deterministic simulator:

- DOI: `10.5281/zenodo.16753415`;
- scalar closure:
  `public_data/q39_information3_strongmax/q39_derived_cache.npz`;
- `100` seeds, `500` slices, `66` observable pairs;
- Q39's frozen development calibration, circulation-coherence threshold
  `>=0.80`, minimum quadrant occupancy `>=0.05`, and complete four-quadrant
  cycle extraction.

No circle-centre, centreline tangent, or external heading from this source
has been inspected before this freeze.

## Whole-circle centre

For every complete parent cycle \(r\), use all of its ordered phase-plane
points \((u_t,v_t)\). The primary centre is the algebraic least-squares circle
centre:

\[
u_t^2+v_t^2
=
2c_{u,r}u_t+2c_{v,r}v_t+k_r.
\]

Thus

\[
\mathbf c_r=(c_{u,r},c_{v,r}).
\]

Record:

- fitted radius \(R_r\);
- radial residual
  \(\operatorname{median}|\,\|\mathbf p_t-\mathbf c_r\|-R_r\,|/R_r\);
- ordinary point centroid;
- midpoint of observed coordinate extrema.

The alternative centres are sensitivity checks, not fitted rescue options.

## External tangent and heading

For each interior cycle of a lineage:

\[
\underbrace{\mathbf d_r}_{\substack{\text{external/meta vector}\\
\text{through time}}}
=
\underbrace{\mathbf c_{r+1}}_{\text{next whole-circle centre}}
-
\underbrace{\mathbf c_{r-1}}_{\text{previous whole-circle centre}}.
\]

The dimensionless movement strength is

\[
m_r
=
\frac{\|\mathbf d_r\|}
{\operatorname{mean}(R_{r-1},R_r,R_{r+1})}.
\]

The primary eligible population requires \(m_r\ge0.01\). Fixed sensitivity
thresholds are `0`, `0.005`, `0.02`, and `0.05`.

Heading in unit turns is

\[
\underbrace{h_r}_{\text{external centreline heading}}
=
\operatorname{frac}
\left[
\frac{\operatorname{atan2}(d_{r,v},d_{r,u})}{2\pi}
\right].
\]

## Declared ARA carrier arc

\[
L=\frac1e=0.367879441\ldots,
\qquad
R=\phi-1=0.618033989\ldots.
\]

The oriented arc width is

\[
R-L=0.250154548\ldots
\]

or almost exactly one quarter-turn.

For headings inside that arc:

\[
x_r=2\frac{h_r-L}{R-L},
\]

so \(L\mapsto0\) and \(R\mapsto2\).

The fixed matched controls are equal-width arcs beginning one, two and three
quarter-turns after \(L\), wrapping modulo one.

## Instrument and construct gates

### G0 — correct object and numerical invariance

- every centre uses all points of one complete internal cycle;
- the heading uses centre differences only;
- translating all phase-plane points leaves headings unchanged;
- rotating all points by a fixed test angle rotates headings by the same
  amount;
- internal Q47 angular-turn and quadrant-flip fields are never loaded;
- all finite headings remain in `[0,1)`.

G0 earns no evidence.

### G1 — declared directional arc wins

At primary movement threshold `m>=0.01`:

- the \(1/e\rightarrow(\phi-1)\) arc has higher heading occupancy than each
  of the three matched quarter-turn rotated arcs;
- in a `5,000`-draw seed-cluster bootstrap, the declared arc exceeds the
  strongest control in at least `95%` of draws.

### G2 — survives time strata and centre estimators

The declared arc must be the highest-occupancy matched arc:

- independently in development and evaluation time strata;
- independently for the algebraic-circle, point-centroid, and
  extrema-midpoint centre estimates.

### G3 — ordered traversal

Within a lineage, a carrier run contains at least three consecutive eligible
headings inside the declared arc. A full half-traversal reaches local
`x<=0.25` and later `x>=1.75`, or the reverse.

G3 requires at least five full half-traversals across at least five lineages,
with both directions present.

### G4 — time order beats shuffled order

Independently permute eligible headings within each lineage `5,000` times,
preserving headings, movement strengths and lineage sizes. The observed
number of full half-traversals must exceed the `99th` percentile of this null
and be at least five.

## `3/8` diagnostic

`3/8` is not a frozen pass/fail gate. Report:

- its local coordinate near the \(1/e\) pole;
- heading density within `0.01` turns of `3/8`;
- the same density around equal-width comparison locations.

This tests Dylan's triangulation clue without allowing it to rescue a failed
carrier.

## Verdicts

Report two distinct verdicts:

1. **Directional-path verdict**
   - supported if G0, G1 and G2 pass;
   - mixed if G0 and one of G1/G2 passes;
   - not supported if G0 passes and neither G1 nor G2 passes;
   - invalid if G0 fails.
2. **Ordered-wobble verdict**
   - supported if G0, G3 and G4 pass;
   - not supported if G0 passes and either G3 or G4 fails;
   - invalid if G0 fails.

The path can be supported while an ordered wobble remains unsupported.

## Interpretation boundary

A pass would locate the external centreline heading in the proposed arc in
this deterministic two-coordinate simulator. It would not prove a universal
time vector, physical quantum-hardware transport, universal Phi, or movement
in literal physical space.

A failure would reject this source/coordinate realization. It would not
invalidate the exact near-quarter-turn separation of \(1/e\) and
\(\phi-1\).

