# T345 line–circle / two-ledger diagnostic protocol v1 (frozen)

**Frozen:** 7 August 2026, before calculating any T345 metric or result  
**Source:** BAW controlled-weir trajectories, DOI `10.48437/99f329-73aee6`  
**Relation to T344:** post-result successor; T344 remains unchanged

## Status and purpose

T344 showed that its registered traversal statistic was path directness, not
coherent circulation or persistence through return flow. T345 freezes the
originator's correction that the proposed Irrationality Di-ARA contains two
perpendicular geometric questions and two distinguishable information
ledgers:

1. line/radial travel versus historically coherent circular travel;
2. future movement information versus information concentrated in stable ARA
   relations.

The laboratory and numerical BAW sources have already been inspected in
T344. T345 is therefore a **frozen post-result diagnostic**, not an untouched
confirmation. It may refine or reject the corrected operationalisation, but
cannot rescue or overwrite T344 Gate D.

## Unchanged ARA event construction

For physical displacement vectors

\[
w_t=(x_t-x_{t-1})+i(z_t-z_{t-1}),
\qquad
\frac{w_t}{w_{t-1}}=s_t e^{i\delta_t},
\]

the two event-level ARA children remain

\[
X_t=\frac{2s_t}{1+s_t},
\qquad
Y_t=1+\frac{\delta_t}{\pi}.
\]

The four ordered sectors remain `Ba`, `Ab`, `bA`, `aB`. Laboratory image-y is
inverted to physical height; numerical y is already physical height. Exact
zero-length and non-finite steps are excluded exactly as in T344.

## Primary window and sensitivity

- Primary history length: `W=15` consecutive native events.
- Sensitivity only: `W=8` and `W=30`.
- A window cannot cross a missing-frame boundary.
- All inference clusters by complete particle trajectory.
- Comparisons are matched by hydraulic condition, progress decile and speed
  quintile where both groups exist.

## Geometry ledger

For positions `p_0,...,p_W` and step vectors `v_j=p_{j+1}-p_j`:

### Line directness

\[
D=
\frac{\lVert p_W-p_0\rVert}
     {\sum_{j=0}^{W-1}\lVert v_j\rVert}
\in[0,1].
\]

`D=1` is a perfectly straight path. Lower `D` means bending, returning or
circulating, but does not by itself identify a circle.

### Historical turning consistency

Let

\[
\gamma_j=\operatorname{Arg}\!\left(\frac{v_{j+1}}{v_j}\right).
\]

Then

\[
G=\frac{\left|\sum_j\gamma_j\right|}
        {\sum_j|\gamma_j|}\in[0,1].
\]

`G=1` means the observed turns consistently wind in one direction; `G≈0`
means turns cancel, as in a zigzag or irregular reversal.

### Historical circularity

\[
C=(1-D)G.
\]

This is deliberately conservative. A high score requires both curvature or
return and a consistent historical turn direction. It is a circulation score,
not proof of a perfect Euclidean circle or mathematical irrationality.

### Frozen path types

- **circle-like:** `D≤0.75` and `G≥0.75`;
- **crooked/random-like:** `D≤0.75` and `G≤0.25`;
- all other windows: mixed, retained for continuous surfaces but not the
  circle-versus-crooked contrast.

These thresholds are fixed before T345 calculation and are not selected from
outcomes.

## Two information ledgers

### Future traversal information `I_move`

T345 retains T344's out-of-condition realised information score. A
calibration-only multinomial model uses the starting parent coordinates
`X,Y,(X−1)(Y−1),|X−1|−|Y−1|` to predict the ARA sector `W` events later.
For the unseen condition,

\[
I_{\rm move}=
\log p_{\rm parent}(S_{t+W})
-\log p_{\rm marginal}(S_{t+W}).
\]

This is information retained for the named future movement address. It is not
total physical information.

### Relation/connection storage `I_conn`

Within each window, count the 16 possible ordered ARA-sector edges
`S_j→S_{j+1}`. With edge probabilities `p_e`, `n=W−1` valid edges and `k`
occupied edge types, use the Miller–Madow-corrected entropy

\[
H_{MM}=
-\sum_e p_e\log p_e+\frac{k-1}{2n},
\]

capped at `log(16)`. Define

\[
I_{\rm conn}=\log(16)-H_{MM}.
\]

This is the information concentration of the realised connection channels
relative to a uniform 16-edge relation field. High values mean that the window
has settled into a small set of repeated ordered relations. It is not claimed
to be thermodynamic information or the full TE-ARA budget.

## Non-overlapping handover

For a starting window at offset `o`, its successor begins at `o+W` in the same
contiguous track run. The windows share only the boundary location, not any
ARA event. Define

\[
\Delta I_{\rm conn}
=I_{\rm conn}(o+W)-I_{\rm conn}(o).
\]

This measures whether a path type precedes accumulation into more concentrated
ARA relations.

## Frozen comparisons and gates

All primary confidence intervals are 2,000 whole-trajectory cluster bootstrap
intervals. A directional gate also requires the named sign in at least two of
three hydraulic conditions. Each group must contain at least 100 windows and
20 trajectories per condition; otherwise the comparison is not testable.

### Gate A — line/circle geometry

Both must pass:

1. `C(structured non-closing) > C(random-like)`;
2. `D(low-order closure) > D(structured non-closing)`.

The T344 closure labels are retained only for this diagnostic crosswalk.

### Gate B — connection-storage ladder

Both must pass:

1. `I_conn(closure) > I_conn(structured non-closing)`;
2. `I_conn(structured non-closing) > I_conn(random-like)`.

This is the frozen expression of closure transferring the visible motion into
concentrated relations, with structured non-closure occupying an intermediate
accumulation state.

### Gate C — coherent curve versus random crookedness

Circle-like windows must have greater `I_move` than crooked/random-like
windows after the frozen matching and clustering.

### Gate D — delayed connection accumulation

Both must pass:

1. mean `ΔI_conn` after circle-like windows is positive;
2. `ΔI_conn(circle-like) > ΔI_conn(crooked/random-like)`.

### Gate E — numerical transfer

The numerical representation is scored separately using the frozen physical
axis map. Full transfer requires Gates A–D to have the same pass/fail status
and every component contrast to have the same sign. Partial transfer must list
the exact components that agree and disagree.

## Exact irrational landmarks

No `Phi`, reciprocal-Phi, `e`, `1/e`, rational angle or fitted constant enters
any primary metric, threshold or gate. They remain outside T345.

## Visual contract

The shipped static figure will use a white research surface and a restrained
blue/gold palette. It must show:

1. example native paths for straight closure, circle-like movement and
   crooked/random-like movement;
2. a `D×G` count surface;
3. a `D×G` mean `I_conn` surface;
4. a `D×G` mean `I_move` surface;
5. class-level geometry and ledger contrasts with exact denominators;
6. non-overlapping `ΔI_conn` by path type.

No 3D perspective, truncated bar baseline or decorative interpolation may
create the apparent geometry. A separate CSV must back each aggregated panel.

## Claim boundary

Passing T345 would support the corrected two-axis/two-ledger interpretation in
this already-opened controlled-flow source. It would not prove universal
Irrationality Di-ARA, conservation of information, exact irrational constants
or the universal fractal-sphere hypothesis. Failure of a gate remains a
failure of the frozen operationalisation and must be recorded without
reclassifying windows after inspection.
