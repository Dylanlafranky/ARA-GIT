# Q27 implementation manifest — frozen before numerical matrix read

**Protocol:** `Q27-ARA9-NETWORK-RECONSTRUCTION-v1`  
**Frozen:** 26 July 2026 after schema inspection and before reading any density-matrix value  
**Purpose:** bind schema details that the Zenodo record did not expose without changing the scientific test.

## Schema discovered without reading values

The frozen archive contains two strata:

- `c2_2local connectivity`: 100 unitary seeds;
- `c4_2local connectivity`: 100 unitary seeds.

Each stratum contains:

- 500 integer-labelled time groups (`0–499`);
- all 66 unordered pairs of 12 qubits;
- one `4 x 4 complex64` density matrix per pair and time;
- a `499 x 6 x 2` ordered connectivity array per seed.

Both strata will be analysed completely, separately and pooled. Neither can be dropped after seeing results.

## Deterministic eligibility clarification

Within exposed times `0–249`:

1. find all runs of at least five crest samples and all later runs of at least five trough samples;
2. pair each trough with the latest crest ending before it;
3. retain candidates whose mirrored return centre lies in `250–499`;
4. if several qualify, use the chronologically first qualifying trough.

The registered mirror reverses the exposed path around the trough and clamps earlier than the qualifying crest
to that crest's first value. No target value enters the mirror.

## Transfer statistic

For a source pair, define release and direct-neighbour accumulation:

\[
r_t=\max(0,-\Delta h_{\rm source,t}),\qquad
g_t=\max(0,\Delta G_{\rm neighbour,t}).
\]

Their directional overlap is

\[
K(r,g)=\frac{\sum_t r_tg_t}
{\sqrt{\sum_t r_t^2}\sqrt{\sum_t g_t^2}}.
\]

`K` is zero when either path has no measurable movement. It is reported in established language as normalized
release-to-accumulation overlap and in ARA language as the degree to which one child's release coincides with the
parent-neighbour accumulation path.

Pair-shuffled controls preserve every source release path and every neighbour-accumulation path but permute which
pair owns the latter within the same trial. Circular-time controls preserve both paths and shift only their
alignment.

## Orientation

For a local reconstruction, orientation before and after the trough is reliable only when the determinant sign is
nonzero and constant across five consecutive above-trough samples. Opposite reliable signs count as a flip.

## Data-quality sample

Every trial contributes the same frozen 25 matrices to the physical reconstruction audit:

- time indices `0, 124, 249, 374, 499`;
- pair indices `0, 16, 32, 48, 65` in numeric pair order.

No invalid matrix is repaired. Violations and tolerances are reported.

## Randomness and bootstrap

- control seed: `27027`;
- pair-shuffle draws: `999`;
- circular-time draws: `999`;
- trial-cluster bootstrap draws: `2,000`;
- split halves: unitary seeds `0–49` and `50–99`, evaluated in both connectivity strata.

## Evidence boundary retained

The two connectivity strata are an internal replication contrast from the same simulator and deposit. Pooled
results cannot hide opposite signs or a failed stratum. The simulator guarantees quantum evolution, not the
registered ARA eligibility, return timing, direct-neighbour advantage, or amplitude-vs-orientation separation.

