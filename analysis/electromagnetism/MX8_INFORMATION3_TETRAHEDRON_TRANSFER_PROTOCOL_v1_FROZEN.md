# MX8 Information³ tetrahedron transfer — protocol v1 (frozen)

Frozen before calculation of any MX8 model coefficient or held-out outcome on 2026-07-15.

## Question

For two binary phase coordinates

\[
x\in\{-1,+1\},\qquad y\in\{-1,+1\},\qquad r=xy,
\]

does the relational coordinate `r` carry reusable information about route-conditioned field strength after the two
individual coordinates `x` and `y` have already been included?

This is a narrow held-out test of the ARA / Information³ claim. It is not a test of universal fractality and it does
not treat `r` as a third independent wave.

## Exact mathematical identity fixed before the test

The four possible lifted states are

\[
(x,y,xy)\in\{(+,+,+),(+,-,-),(-,+,-),(-,-,+)\}.
\]

They are the four vertices of a regular tetrahedron: all have norm `sqrt(3)`, every distinct pair has dot product
`-1`, and every edge has length `2 sqrt(2)`. The closure rule is `xyr=1`.

For route `r` with occupancy `p_r`, conditional magnitude `m_r`, and output sign `x_r y_r`, the exact resolved target is

\[
F=Q\sum_r p_r m_r x_r y_r.
\]

This identity is algebra, not a prediction. MX8 tests whether a compact relation term transfers to unseen times.

## Source and split

- Source: public `openPMD-example-datasets/example-2d/hdf5` Warp series already present locally.
- Snapshots: iterations 255 through 400 in steps of 5.
- Development fit: 255–320 inclusive (14 snapshots).
- Quarantined gap: 325–350 inclusive (6 snapshots; not used for fitting or selection).
- Final test: 355–400 inclusive (10 snapshots).
- Particle species: `Hydrogen1+` and `electrons`.
- Electric components: x, y, z, repeated as separate fits but scored together as a vector.
- Particle fields are bilinearly sampled using recorded openPMD offsets and deposited to the field grid with bilinear
  cloud-in-cell weights.
- Test route-conditioned amplitudes are used only to calculate the resolved target and exact identity ceiling. They
  are forbidden as model inputs.

## Frozen models

For each cell-component-route, define

\[
h=\log(m_r/\bar m),
\]

where `m_r` is the route-conditioned mean absolute electric-field component and `m̄` is the cell-component mean
absolute field magnitude. Fit by weighted least squares on development rows only, with weight `Q p_r`, separately
for x, y and z components.

Nested height models:

1. Route-blind: `h = a`.
2. Two-axis additive: `h = a + b_x x + b_y y`.
3. Information³ relation: `h = a + b_x x + b_y y + g xy`.

For held-out cells, reconstruct

\[
\widehat F=Q\bar m\sum_r p_r x_r y_r\exp(\widehat h_r).
\]

Additional fixed baselines:

- independent phase marginals: `Q m̄ E[x] E[y]`;
- joint sign only: `Q m̄ E[xy]`;
- route-blind height model;
- exact conditioned route identity (ceiling, explicitly non-predictive).

No coordinates, snapshot identifier, test-derived multiplier, nonlinear learner, or post-test coefficient adjustment
is allowed.

## Metrics and success gate

Primary metric: relative L2 error over all held-out force-vector cells.

Secondary metrics: NRMSE by target standard deviation, vector cosine/correlation, and median vector angular error.

Primary comparison: relation model versus additive model. The frozen success gate requires:

1. at least 5% lower relative L2 error;
2. a 95% snapshot-block-bootstrap interval for relative-L2 improvement entirely above zero;
3. vector correlation, NRMSE and median angular error all non-worse.

Use 10,000 deterministic bootstrap resamples of the ten held-out snapshots (`seed=20260715`).

## Interpretation boundary

A pass would show that the `xy` interaction coordinate has temporally reusable route-strength information in this
second simulator. It would support ARA's warning against flattening the relation between two phase axes. It would
not establish a novel Maxwell law, literal universal tetrahedra, scale recursion, or the full ARA framework.

A failure would leave the tetrahedron and exact decomposition mathematically true while showing that this compact
interaction coefficient does not transfer under the frozen model.

This remains a conditional-height closure: the held-out common magnitude `m̄` and route occupancies are supplied.
It does not predict the entire plasma state from a coarser parent state.
