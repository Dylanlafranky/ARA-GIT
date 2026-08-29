# T426 — Main Irrationality Di-ARA macro-handover follow-up

## Question

Does the main hourglass Irrationality Di-ARA follow the ARA-ordered path

\[
\text{connection-heavy}
\rightarrow
\text{opening near }(0.5,1.5)
\rightarrow
\text{movement excursion}
\rightarrow
\text{connection-heavy reclosure}?
\]

The test uses the same 16 held-out Toyoura-sand hourglass discharges as T424. The opening anchor is the independently observed first downstream-flow onset (`direct_active = 1`), not a coordinate selected from the Di-ARA path during T426.

## Frozen ARA address

- C1: movement/traversal coordinate on its own 0–2 ARA.
- C2: connection/packing coordinate on its own 0–2 ARA.
- Connection-heavy: C1 < 1 and C2 > 1.
- Opening landmark: |C1 - 0.5| <= 0.25 and |C2 - 1.5| <= 0.25.
- Movement-heavy: C1 > 1 and C2 < 1.
- Reclosure: a return to connection-heavy after the movement excursion.
- Frozen persistence: three consecutive frames.

The complete frozen procedure and hash are in `T426_FROZEN_PROTOCOL.md`.

## Result

The frozen four-stage path completed in **16 of 16 runs**.

Median coordinates and timing:

| Stage | C1 movement | C2 connection | Median timing |
|---|---:|---:|---:|
| Observed opening | 0.5012 | 1.5000 | 61.8% of pre-closure history |
| Persistent movement excursion | 1.1595 | 0.7749 | 0.0833 s after opening |
| Persistent connection reclosure | 0.8579 | 1.1866 | 0.8500 s after movement |
| Terminal T424 closure | — | — | 0.7333 s after reclosure |

The median opening relation is almost exactly the proposed child pair:

\[
(C1,C2)=(0.5012,1.5000),\qquad \frac{C1+C2}{2}=1.0011.
\]

This means the parent-compressed relation is at the 1.0 ridge while the two child coordinates remain strongly asymmetric.

## Controls

The observed 16/16 result was compared with 10,000 frozen replicates per stochastic control:

| Control | Mean completed runs | 95th percentile | Empirical p for 16/16 |
|---|---:|---:|---:|
| Random pseudo-onset anywhere in the eligible history | 0.243 | 1 | < 0.0001 |
| Jointly circular-shifted C1/C2 path relative to the real onset | 0.143 | 1 | < 0.0001 |
| Time-reversed histories | 0 | — | — |

A post-freeze diagnostic sampled only frames already inside the frozen opening box. Those anchors completed an average of 7.18 runs, with a 95th percentile of 9/16; none of the 10,000 replicates reached 16/16 (empirical p < 0.0001). This shows that box membership alone does not explain the ordered result. The independently observed flow onset selects a particular part of the broader opening corridor.

## Robustness

The frozen persistence width is three frames. A post-freeze sensitivity check produced:

- one frame: 16/16;
- three frames: 16/16;
- five frames: 16/16;
- eight frames: 11/16.

The sequence therefore survives modest persistence demands, but five runs do not remain continuously inside every required state for eight frames.

## ARA reading

For this physical source and this cut, the main Irrationality Di-ARA behaves as the proposed larger handover, not merely as the quieter local quotient cut:

1. a connection-heavy identity exists before visible flow;
2. visible opening begins at the asymmetric child pair near (0.5,1.5), whose compressed parent relation is at the ridge;
3. the trajectory crosses into a movement-heavy child relation;
4. it returns to a connection-heavy relation before terminal closure.

The reclosure is not terminal closure. It is an earlier return of the relational balance, followed by a median 0.733 s before the T424 endpoint.

## Claim boundary

T426 supports the frozen macro-handover order in this hourglass source. It does **not** yet establish that every system must traverse the same observable quadrants, that the order is causal, or that the (0.5,1.5) landmark is distortion-free in every identity.

The opening address was first observed in T424. T426 is a frozen follow-up on the same held-out run set, not a new independent dataset replication. A genuinely stronger next step is to freeze this entire instrument and apply it unchanged to a new hourglass dataset or a second time-facing granular-flow source.

