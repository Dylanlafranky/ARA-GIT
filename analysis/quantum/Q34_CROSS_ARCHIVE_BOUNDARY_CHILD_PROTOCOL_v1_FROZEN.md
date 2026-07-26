# Q34 — Cross-Archive Boundary-Child Protocol v1 (FROZEN)

**Frozen:** 26 July 2026 before target-archive download or numerical inspection
**Ledger:** T289
**Design:** exact Q33B replication on `12_pure_greedy`

## 1. Fixed geometry

\[
\mathcal R_\uparrow(1_c)=\frac12,
\qquad
L=2+\left(1+\frac12\right)=3.5.
\]

The child `0` boundary and parent `1.0` ridge are the same adjacent-rung
boundary viewed from different frames. The structural coordinate is fixed and
is not refitted on Q34.

## 2. Locked target

- Zenodo DOI `10.5281/zenodo.16753415`
- archive `unnati_submit_12_pure_greedy.hdf5.zip`
- archive MD5 `c1cf77ccff486e3786d73ba47f8674f1`
- all `100` deposited seeds
- both deposited `c2` and `c4` branches
- all `500` time slices
- all `66` unordered two-qubit relations

The extracted HDF5 SHA-256 and derived-cache hashes will be recorded after
checksum-verified extraction. Schema discovery may locate deposited paths but
must not modify this protocol.

## 3. Frozen partitions and scales

- development scale window: `t=0..249`;
- development event window: `t=8..242`;
- evaluation event window: `t=258..492`;
- each relation's closure reference:
  \(s_h=Q_{0.95}^{dev}(|\det C|^{1/3})\);
- each relation's connected-energy reference:
  \(s_E=Q_{0.95}^{dev}(\lVert C\rVert_F^2)\).

No evaluation value enters a scale, threshold or route selection.

## 4. Frozen source eligibility

For branch \(b\), seed \(s\), time \(t\), and source relation \(p\):

1. `2*z_source(t) >= 1.5`;
2. source closure falls from `t` to `t+1`;
3. connected energy falls from the latest local maximum in `t-8..t` to
   `t+1`;
4. the source relation is not active at `t`;
5. exactly one active edge touches each source endpoint and they are distinct;
6. retain deterministic samples satisfying
   `(97*s + 53*t + 31*p + 11*b) mod 16 = 0`.

## 5. Frozen boundary-child rule

For the two exact endpoint children \(c_1,c_2\):

\[
z_c(t)=\frac{h_c(t)}{s_{h,c}},
\qquad
h_c(t)=|\det C_c(t)|^{1/3}.
\]

Choose the child with smaller starting \(z_c(t)\). Break an exact tie by lower
pair index. The other exact endpoint is the sibling.

The primary outcome is

\[
g_c(t)=\frac{h_c(t+1)-h_c(t)}{s_{h,c}}.
\]

## 6. Frozen controls

Use the Q33B controls unchanged:

1. exact sibling;
2. two non-endpoint active relations matched to the exact pair's starting
   \(z\), then selected by the same lower-\(z\) rule;
3. endpoint pair at seed `(s+37) mod 100`, selected lower-\(z\);
4. endpoint pair at time displaced by `+137` within the same partition,
   selected lower-\(z\).

Unavailable controls remain missing; no replacement search is allowed.

## 7. Frozen primary gates

Eligibility:

- at least `5,000` evaluation source events;
- at least `100` branch/seed strata;
- at least `2,000` paired events for each control.

Routing:

1. pooled exact median \(g>0\);
2. exact median \(g>0\) in both `c2` and `c4`;
3. pooled exact positive fraction at least `0.55`;
4. exact positive fraction exceeds sibling, topology, seed and time by at
   least `0.02` each;
5. median paired exact-minus-comparator \(g>0\) for all four comparisons;
6. branch/seed-cluster bootstrap probability that exact mean flow exceeds each
   comparator is at least `0.95`.

All gates must pass.

## 8. Frozen verdicts

If every eligibility and routing gate passes:

`CROSS-ARCHIVE BOUNDARY-CHILD FLOW REPLICATED INSIDE THIS SIMULATOR FAMILY`.

If eligibility passes but any routing gate fails:

`CROSS-ARCHIVE BOUNDARY-CHILD FLOW NOT REPLICATED`.

If eligibility fails:

`INCONCLUSIVE — CROSS-ARCHIVE ELIGIBILITY GATE`.

## 9. Secondary diagnostics

Report, but do not use to change the verdict:

- raw connected-energy flow;
- source-release/positive-child overlap;
- starting-\(z\) distributions;
- development/evaluation stability;
- direct effect-size comparison with Q33B;
- data-quality and exact-diagonality checks.

## 10. Independent validation

The validator must not import the primary runner. It must:

- verify protocol, fidelity, archive, extracted-source and cache hashes;
- verify dimensions and event-key uniqueness;
- reconstruct at least `64` deterministic event routes directly from the raw
  HDF5 and saved scales;
- recompute headline metrics and every frozen gate;
- confirm the structural child weight remains exactly `0.5`;
- confirm the declared verdict.
