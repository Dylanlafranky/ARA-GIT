# Q51 — Cross-archive external reversal replication

**Date:** 30 July 2026  
**Status:** FROZEN BEFORE EXTERNAL-CENTRE CALCULATION ON THE LISTED ARCHIVES  
**Evidence class:** Construct holdout across previously downloaded archives;
not a fully blind new-data test.

**Operational amendment before any branch result was saved:** The first
`random:c2` execution revealed that a frozen same-lineage population may be
empty. The protocol now explicitly records such a branch as `NOT TESTABLE`
without loosening eligibility. No directional result had been calculated or
saved when this handling rule was added.

## Question

Q50 found, in the `strongmax` archive, that the same seed/pair lineages moved
from the declared external direction toward its exact half-turn opposite.
The reversal coincided with a large collapse in centre movement and did not
complete a `0 → 2 → 0` return.

Q51 asks:

1. Does the same external directional reversal repeat under other network
   selection strategies?
2. Does it occur in both the `c2` and `c4` connectivity branches?
3. Is it an active traversal with recovered movement, or residual drift
   during deterministic relaxation?

## Frozen archives

| Strategy label | Derived archive |
|---|---|
| random | `public_data/q27_network_reconstruction/q27_derived_cache.npz` |
| greedy | `public_data/q34_cross_archive_greedy/q34_derived_cache.npz` |
| landmax | `public_data/q37_signed_crossing_landmax/q37_derived_cache.npz` |
| mimic | `public_data/q38_fixed_anchor_mimic/q38_derived_cache.npz` |

Both stored branches are tested separately:

- `c2_2local connectivity`;
- `c4_2local connectivity`.

These data have appeared in earlier ARA analyses, but their complete-cycle
external centres and the Q50 directional coordinate have not been calculated
before this freeze. Q51 is therefore a construct holdout, not an untouched
archive replication.

## Frozen geometry and extraction

For each archive/branch:

1. apply Q49's unchanged development-calibrated state/change plane;
2. accept the same circulation and quadrant-occupancy criteria;
3. extract the same complete four-quadrant cycles;
4. fit the same circle, centroid and extrema centres;
5. construct the same central-difference external movement;
6. apply Q50's same-lineage population and directional ARA coordinate.

No archive-specific axis rotation, sign correction, threshold or fit is
allowed.

If a branch has no lineage meeting the frozen same-lineage population, it is
reported as `NOT TESTABLE` and fails to contribute to any replication count.
The population rule will not be loosened after inspection.

The directional coordinate remains:

\[
x_{\rm ext}
=
1-
\frac{\sum_i\mathbf d_i\cdot\hat{\mathbf e}}
{\sum_i\|\mathbf d_i\|},
\]

where `0` is the declared external direction, `1` is its directional ridge
and `2` is the exact half-turn opposite.

## Frozen per-branch gates

### R1 — Opposing strata

- development aggregate: `x < 1`;
- evaluation aggregate: `x > 1`.

### R2 — Half-turn geometry

The movement-weighted development/evaluation heading separation must be
within `0.10` turns of an exact half-turn:

\[
|\Delta h-0.5|\le0.10.
\]

### R3 — Same-lineage direction

- declared-to-opposite paired lineages outnumber opposite-to-declared;
- seed-cluster bootstrap 95% interval for paired `Δx` lies above zero.

### R4 — Active movement rather than residual-only drift

At least one must hold:

- evaluation mean relative movement is at least `10%` of development mean
  relative movement; or
- after the first `0 → 2` ridge crossing, mean movement recovers to at least
  `25%` of the two-bin pre-crossing mean.

Failure of R4 means the orientation reversal may be a deterministic
relaxation tail. It cannot be called a traversing external wave.

### R5 — Complete return

The twenty fixed 25-slice bins must contain, in order:

- `x ≤ 0.5`;
- later `x ≥ 1.5`;
- later `x ≤ 0.5`.

R5 is required to call the observed window a complete `0 → 2 → 0` cycle.

## Cross-archive summaries

- **Orientation-reversal replication:** R1–R3 pass in at least three of the
  four `c2` strategies.
- **Active-traversal replication:** R1–R4 pass in at least three of four
  `c2` strategies.
- **Complete-cycle replication:** R1–R5 pass in at least three of four `c2`
  strategies.
- `c4` is reported as a rung/branch sensitivity and cannot replace the
  primary `c2` gate.

## Interpretation boundaries

Even a cross-archive pass is evidence about a deterministic
changing-connectivity simulator. It is not automatically evidence of:

- laboratory quantum hardware;
- a physical singularity;
- a universal time vector;
- the full ARA framework.

A common reversal combined with common movement collapse would more strongly
support a reusable description of the simulator's relaxation geometry than
an active `0 → 2 → 0` wave.
