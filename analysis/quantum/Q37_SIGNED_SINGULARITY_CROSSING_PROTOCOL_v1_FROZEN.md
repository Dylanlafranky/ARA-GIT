# Q37 Frozen Protocol — Signed Singularity Crossing

**Protocol ID:** `Q37-SIGNED-SINGULARITY-CROSSING-v1`  
**Ledger:** T292  
**Frozen:** 27 July 2026 before downloading or opening target values  
**Design:** prospective cross-archive test on an untouched public archive

## Source lock

Public source: Akhouri, Shandera and Henry, *Dataset for 6–14 qubits
evolving on network with varying connectivity*, Zenodo
`10.5281/zenodo.16753415`.

- target archive: `unnati_submit_12_pure_landmax.hdf5.zip`;
- deposited MD5: `ace64ede12cfbc9e5413326f23c306ad`;
- listed compressed size: approximately `224.2 MB`;
- target network identities: deposited `c2` and `c4` two-local branches;
- target seeds: all `0..99`;
- target times: all `0..499`;
- target pairs: all `66` two-qubit partitions.

The archive was selected using metadata only because it keeps the same
12-qubit pure initial-condition family as Q34–Q36 while changing the
network-ordering identity. No value from this archive has previously been
opened in the project.

## Frozen reconstruction

Reconstruct the raw connected tensor for every pair:

\[
C_{ij}
=
\operatorname{Tr}[\rho(\sigma_i\otimes\sigma_j)]
-
\operatorname{Tr}[\rho(\sigma_i\otimes I)]
\operatorname{Tr}[\rho(I\otimes\sigma_j)].
\]

Derive

\[
h=|\det C|^{1/3},\qquad A=\lVert C\rVert_F.
\]

Schema-only changes needed to locate the already-described branch, seed,
time and pair arrays are allowed. Metric, eligibility, control or gate
changes after value access require a new protocol version.

## Frozen lineage eligibility

Apply the exact Q35/Q36 complete-loop rule to target `c2`, using development
times `0..249` only:

1. normalize closure and first difference by the development `5%/95%`
   closure span and `95%` absolute-flow scale;
2. require at least `95%` valid development phase points;
3. require every phase-plane quadrant to contain at least `5%`;
4. require circulation coherence at least `0.80`.

No target evaluation value may affect lineage eligibility.

## Frozen crossing events

For every eligible target `c2` lineage:

1. calculate its development `20th` percentile of \(h\);
2. evaluate candidate times `258..491`;
3. retain \(t\) when
   \(h_{t-1}>h_t\le h_{t+1}\) and
   \(h_t\) is no greater than the development threshold;
4. retain events at least seven slices apart within a lineage.

## Primary signed metric

For every retained event:

\[
S_t=
\frac{
\sum_{k=1}^{7}\langle C_{t-k},C_{t+k}\rangle_F
}{
\sum_{k=1}^{7}
\lVert C_{t-k}\rVert_F\lVert C_{t+k}\rVert_F
}.
\]

All seven offsets remain paired. No lag search, rotation fit, sign
optimization or post-result axis swap is allowed.

### Signed-orientation support gates

All must pass:

1. median \(S\le-0.25\);
2. at least `60%` of events have \(S<0\);
3. seed-cluster bootstrap probability that mean \(-S>0\) is at least
   `0.99`;
4. exact \(S\) is at least `0.10` more negative than each frozen control in
   the event-weighted mean;
5. seed-cluster bootstrap probability that exact is more negative than each
   control is at least `0.95`.

Passing only gates 2–3 is reported as weak anti-orientation, not recovered
Phase B.

## Primary traversal metrics

\[
X_A=
\frac{2\sum_{k=1}^{7}A_{t+k}}
{\sum_{k=1}^{7}A_{t-k}+\sum_{k=1}^{7}A_{t+k}},
\qquad
X_h=
\frac{2\sum_{k=1}^{7}h_{t+k}}
{\sum_{k=1}^{7}h_{t-k}+\sum_{k=1}^{7}h_{t+k}}.
\]

The primary aggregate is the event-weighted mean, matching the Q36
equal-window quantity that generated the prediction. Event medians and
lineage-balanced means are mandatory robustness outputs.

### Traversal-replication support gates

All must pass for both \(X_A\) and \(X_h\):

1. event-weighted mean lies in the frozen broad band `[0.92, 0.98]`;
2. at least `55%` of events are below the ridge at `1`;
3. at least `55%` of represented lineages have a within-lineage mean below
   `1`;
4. seed-cluster bootstrap probability that the exact mean is below `1` is
   at least `0.99`;
5. exact event-weighted mean is at least `0.02` below each frozen control;
6. seed-cluster bootstrap probability that exact is lower than each control
   is at least `0.95`.

## Frozen controls

Every control uses the same formula, seven-slice windows and source-event
rows.

1. **Displaced time:** same `c2` seed and pair, shifted `+37` circularly
   within `258..491`.
2. **Pair:** next other development-eligible `c2` pair cyclically within the
   same seed, evaluated at the exact time.
3. **Network:** same seed, pair and time in deposited `c4`.

## Eligibility floor

The run is interpretable only with:

- at least `2,000` exact events;
- at least `80` represented seeds;
- at least `500` represented lineages.

Failure is reported as inconclusive, without changing the source or rule.

## Verdicts

- **SIGNED CROSSING + TRAVERSAL REPLICATED:** eligibility and every signed
  and traversal gate pass.
- **SIGNED CROSSING ONLY:** every signed gate passes; traversal does not.
- **TRAVERSAL ASYMMETRY ONLY:** every traversal gate passes; signed does not.
- **WEAK ANTI-ORIENTATION:** signed gates 2–3 pass but the full signed block
  does not.
- **NOT REPLICATED:** eligibility passes and neither registered block passes.
- **INCONCLUSIVE:** eligibility or source integrity fails.

## Diagnostics outside the primary gates

- determinant-sign agreement before versus after;
- offset-specific signed similarities for `k=1..7`;
- event and lineage distributions;
- Q36 `pure_greedy` and already-open Q27 `pure_random` descriptive
  comparison, calculated only after the target verdict is sealed.

## Statistical lock

- seed-cluster bootstrap;
- `20,000` draws;
- deterministic seed `371027`;
- no multiple alternative window, threshold or lag hunt.

## Honesty boundary

This can establish a reproducible signed and traversal consequence inside
this simulator family. It cannot by itself establish physical Phase B,
entanglement, a universal singularity, topological sphere continuity or
universal ARA.

