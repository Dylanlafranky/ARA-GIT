# Q38 Frozen Protocol — Fixed-Anchor Phase Cycle

**Protocol ID:** `Q38-FIXED-ANCHOR-PHASE-CYCLE-v1`  
**Ledger:** T293  
**Frozen:** 27 July 2026 before downloading or opening target values  
**Design:** prospective cross-archive test on an untouched public archive

## Source lock

Public source: Akhouri, Shandera and Henry, *Dataset for 6–14 qubits
evolving on network with varying connectivity*, Zenodo
`10.5281/zenodo.16753415`.

- target archive: `unnati_submit_12_pure_mimic.hdf5.zip`;
- deposited MD5: `04477abdac1849dd034576c0dbb685cb`;
- listed compressed size: approximately `224.5 MB`;
- target network identities: deposited `c2` and `c4` two-local branches;
- target seeds: all `0..99`;
- target times: all `0..499`;
- target pairs: all `66` two-qubit partitions.

The archive was selected using metadata only. No value from this archive has
previously been opened in the project.

## Frozen reconstruction

For every pair, reconstruct the raw connected tensor

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
h=|\det C|^{1/3},
\qquad
A=\lVert C\rVert_F.
\]

Schema-only changes needed to locate the already-declared branch, seed, time
and pair arrays are allowed. Metric, eligibility, window, control or gate
changes after target-value access require a new protocol version.

## Frozen lineage eligibility

Apply the exact Q35–Q37 complete-loop rule to target `c2`, using development
times `0..249` only:

1. normalize closure and first difference by the development `5%/95%`
   closure span and `95%` absolute-flow scale;
2. require at least `95%` valid development phase points;
3. require every phase-plane quadrant to contain at least `5%`;
4. require circulation coherence at least `0.80`.

No target evaluation value may affect lineage eligibility.

## Frozen pinch events

For every eligible target `c2` lineage:

1. calculate its development `20th` percentile of \(h\);
2. evaluate candidate times `258..485`, leaving fourteen exit slices;
3. retain \(t\) when
   \(h_{t-1}>h_t\le h_{t+1}\) and
   \(h_t\) is no greater than the development threshold;
4. retain events at least fourteen slices apart within a lineage.

## Fixed Phase-A anchor

For each event, inspect approach offsets `-7..-3` only. Let

\[
k_*=
\operatorname*{arg\,max}_{k\in\{3,4,5,6,7\}}
A_{t-k},
\qquad
C_A=C_{t-k_*}.
\]

Ties use the earliest time, which is the largest \(k\). The anchor is fixed
after selection and is not refitted, rotated, reflected or sign-optimized.

## Exit path

For exit offsets \(j=1,\ldots,14\), calculate

\[
r_j=
\frac{\langle C_A,C_{t+j}\rangle_F}
{\lVert C_A\rVert_F\lVert C_{t+j}\rVert_F},
\qquad
a_j=\frac{A_{t+j}}{A_A}.
\]

An orientation reading is reliable only where \(a_j\ge0.10\).

### Ordered event construction

1. Search reliable offsets `1..7` for the minimum \(r_j\). Call its offset
   \(j_B\) and value \(r_B\).
2. **Phase-B entry:** \(r_B\le-0.25\).
3. **Strong Phase-B appearance:** \(r_B\le-0.50\), reported separately.
4. After \(j_B\), search offsets through `14` for the maximum reliable
   \(r_j\) whose amplitude recovery satisfies \(a_j\ge0.50\). Call the
   maximum \(r_A^+\) and its earliest offset \(j_A^+\).
5. **Phase-A return:** \(r_A^+\ge+0.25\).
6. **Completed local cycle:** both Phase-B entry and later Phase-A return.

The continuous cycle score is

\[
Q=\min(-r_B,r_A^+).
\]

If either ordered component is unavailable, \(Q=-1\) and the binary cycle
indicator is zero. This prevents an incomplete path from receiving partial
continuous-cycle credit.

## Frozen controls

Every control receives its own pre-only anchor and the same exit
construction.

1. **Displaced time:** same `c2` seed and pair, shifted `+37` circularly
   within `258..485`.
2. **Pair:** next other development-eligible `c2` pair cyclically within the
   same seed, evaluated at the exact time.
3. **Network:** same seed, pair and time in deposited `c4`.

## Primary cycle-support gates

Eligibility must pass and all gates below must pass:

1. at least `55%` of exact events complete the ordered cycle;
2. at least `55%` of represented lineages have a within-lineage cycle
   fraction of at least `0.50`;
3. seed-cluster bootstrap probability that the exact cycle fraction exceeds
   `0.50` is at least `0.99`;
4. median exact continuous score \(Q\ge0.25\);
5. exact event cycle fraction exceeds every control by at least `0.10`;
6. exact mean \(Q\) exceeds every control by at least `0.10`;
7. seed-cluster bootstrap probability that exact cycle incidence exceeds
   each control is at least `0.95`;
8. seed-cluster bootstrap probability that exact \(Q\) exceeds each control
   is at least `0.95`.

## Registered timing diagnostic

If the cycle block passes, the proposed slice-seven return receives timing
support when the median \(j_A^+\) among completed exact cycles lies in
`[6,10]`. This is reported separately and cannot rescue a failed cycle block.

## Eligibility floor

The run is interpretable only with:

- at least `2,000` exact events;
- at least `80` represented seeds;
- at least `500` represented lineages.

Failure is `INCONCLUSIVE — ELIGIBILITY`, without changing source or rules.

## Verdicts

- **FIXED-ANCHOR A→B→A CYCLE REPLICATED:** eligibility and all eight primary
  gates pass.
- **ORDERED CYCLE SIGNAL, INCOMPLETE:** eligibility passes, exact beats every
  control under both bootstrap blocks, but one or more remaining gates fail.
- **NOT REPLICATED:** eligibility passes and the controlled ordered-cycle
  block fails.
- **INCONCLUSIVE:** eligibility or source integrity fails.

## Mandatory robustness outputs

- offset-wise median, `25%/75%` and `5%/95%` bands of \(r_j\);
- event, lineage and seed cycle fractions;
- strong-Phase-B fraction;
- \(j_B\) and \(j_A^+\) distributions;
- amplitude ratio at the selected Phase-B and Phase-A return points;
- same statistics for every control;
- fixed-anchor exit-path heatmap sorted by \(j_B\) then \(j_A^+\);
- descriptive Q37 `pure_landmax` replay only after the prospective target
  verdict is sealed.

## Statistical lock

- seed-cluster bootstrap;
- `20,000` draws;
- deterministic seed `381027`;
- no alternative anchor, threshold, window, lag or sign hunt.

## Honesty boundary

Q38 can establish an ordered fixed-anchor tensor path within this simulator
family. It cannot by itself establish physical Phase B, a literal
singularity, topological sphere traversal, entanglement mechanism or
universal ARA.
