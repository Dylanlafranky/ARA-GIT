# Q28 — ARA^9 Interlocking Rotational Transport

**Date:** 26 July 2026  
**Ledger:** T284  
**Strict frozen verdict:** **INCONCLUSIVE**  
**Independent validation:** **PASS — 38/38 checks**  
**Evidence tier:** registered on a fully opened Q27 source; not blind and not
A-tier provenance

## Answer first

Q28 does not confirm the proposed continuous angled interlocking point. It
does, however, recover a strong and reproducible **binary flip plus delayed
neighbour-web relation** that was hidden when Q27 compressed each relation to
\(h=|\det C|^{1/3}\).

On the hidden time half, allowing one proper rotation reduced weighted
reconstruction residual from `0.54617` to `0.10164`, an `81.39%` improvement.
The exact relation beat seed displacement by `33.58%`, time displacement by
`33.52%`, and zero lag by `23.53%`. Development selected lag `2`, and the
hidden half independently had its lowest residual at lag `2`. Singular-value
shape similarity was `0.99178`, above both displaced controls.

Two frozen requirements prevent promotion:

1. `76,393` hidden events survived, below the registered `100,000`-event
   eligibility floor.
2. Every connected \(3\times3\) relation in this simulator is exactly diagonal
   and symmetric. Reversing the named endpoint is therefore only a transpose
   that leaves the matrix unchanged. Correct- and wrong-endpoint residuals are
   exactly identical (`0.10164`), so Q28 cannot establish shared-endpoint
   interlocking.

The fitted rotations are correspondingly only `0°` or `180°`. This supports a
binary orientation/phase-flip description in this measurement cut, not the
proposed continuous angled pivot.

## Frozen hypothesis

Dylan's prior was:

> “I wonder if its the ARA^9 just interlocking then and traveling, the larger
> but small wave might be its angled rotational point.”

Q28 retained the complete connected relation

\[
C_{ij}
=
T_{ij}-a_i b_j
\]

rather than reducing it immediately to one closure amplitude. A source
release at time \(t\) was compared with the accumulation-weighted web of
active relations sharing one endpoint at \(t+\ell\). The only fitted
transformation was a positive scale and one proper \(SO(3)\) rotation.

Development times `0–241` selected \(\ell\in\{1,\ldots,8\}\). Hidden times
`250–491` evaluated the frozen lag. Controls were:

- no rotation;
- the opposite endpoint;
- seed displacement by `+37 mod 100`;
- time displacement by `+137` within the split;
- lag zero.

The deterministic event sampler was frozen before Q28 outcomes:

\[
(97s+53t+31p+17e+11b)\bmod16=0.
\]

## Source and reconstruction

The complete public Q27 simulator source was reused:

- DOI: `10.5281/zenodo.16753415`;
- two connectivity strata (`c2`, `c4`);
- `100` seeds per stratum;
- `500` time steps;
- all `66` unordered pair relations;
- `6.6 million` two-qubit density matrices.

Q28 reconstructed and cached all `6.6 million` connected \(3\times3\)
relations. The cache contains `59.4 million` signed matrix coefficients and is
`237,600,128` bytes.

The Q28 source-quality limits were disclosed as chosen after Q27:

| Check | Observed | Q28 limit | Result |
|---|---:|---:|---|
| maximum trace error | `2.53421e-05` | `5e-05` | pass |
| maximum Hermiticity error | `0` | `1e-06` | pass |
| minimum eigenvalue | `-3.11543e-07` | `-1e-06` | pass |

## Results

### Hidden pooled metrics

| Measure | Value |
|---|---:|
| eligible events | `76,393` |
| eligible trial strata | `200` |
| rotation residual | `0.101637` |
| no-rotation residual | `0.546173` |
| wrong-endpoint residual | `0.101637` |
| seed-displaced residual | `0.153025` |
| time-displaced residual | `0.152886` |
| zero-lag residual | `0.132915` |
| rotation gain vs no rotation | `81.391%` |
| shape similarity | `0.991784` |
| seed-displaced shape similarity | `0.982384` |
| time-displaced shape similarity | `0.982544` |

All `2,000/2,000` paired trial bootstrap draws favoured exact rotation over no
rotation, exact over seed displacement, exact over time displacement, and lag
2 over zero lag. Correct endpoint beat wrong endpoint in `0/2,000` draws
because their errors were identical.

### Lag curve

Development selected lag `2`:

| Lag | Development residual | Hidden residual |
|---:|---:|---:|
| 1 | `0.110411` | `0.108230` |
| **2** | **`0.104263`** | **`0.101637`** |
| 3 | `0.104345` | `0.102546` |
| 4 | `0.106472` | `0.104782` |
| 5 | `0.109882` | `0.109189` |
| 6 | `0.114540` | `0.114323` |
| 7 | `0.118674` | `0.119423` |
| 8 | `0.121908` | `0.121727` |

Lag 3 was close on development, but the exact preregistered selection was lag
2 and the hidden data preserved that ordering.

### Frozen gates

Passed:

- D1 source checksums;
- D2 complete source dimensions;
- D3 disclosed Q28 source precision;
- I1 rotation gain;
- I2 rotation bootstrap;
- I4 seed/time displacement controls;
- I5 singular-spectrum retention;
- T1 positive lag over zero lag;
- T2 development-to-hidden median angle;
- T3 hidden weight inside the broad development angle interval.

Failed:

- E1 event floor (`76,393 < 100,000`);
- I3 shared endpoint, because endpoint reversal is exactly degenerate;
- T4 same-direction composite, because it includes the failed endpoint
  direction test.

The strict verdict is therefore **INCONCLUSIVE**. Even if the event floor were
waived post hoc, the frozen interlocking claim would remain **not supported**
on this source because the endpoint-specific gate cannot pass.

## Why the endpoint control collapses

Independent raw reconstruction found

\[
C(t)
=
\begin{pmatrix}
c_x(t)&0&0\\
0&c_y(t)&0\\
0&0&c_z(t)
\end{pmatrix}
\]

for every checked relation, with zero sampled off-diagonal magnitude and zero
matrix asymmetry. Endpoint reversal maps \(C\mapsto C^\mathsf T\), but here

\[
C^\mathsf T=C.
\]

Thus “correct endpoint” and “wrong endpoint” are not two observable
conditions in this source. This is a source-identifiability limit, not evidence
that endpoints are physically interchangeable in general.

The same diagonal structure explains the angle histogram. A proper rotation
can preserve the diagonal axes or flip two signs through a `180°` turn; no
oblique angle is needed or identifiable.

## Two-language interpretation

| ARA geometry | Established quantum/data language |
|---|---|
| The larger web retains a phase/flip relation discarded by scalar closure. | The full connected-correlation block retains signed axis structure lost by \(|\det C|\). |
| Release is followed most cleanly by neighbour-web accumulation two slices later. | A frozen lag-2 association replicates on the hidden time half and beats zero lag. |
| The observed movement is compatible with a Phase B outside the visible endpoint cut. | The measured matrices show binary sign reorientation, while the intended endpoint channel is non-identifiable. |
| The angled rotational point is unresolved. | All observed relations are diagonal, restricting fitted angles to `0°/180°`. |

### Dylan's post-result ARA interpretation

Dylan identified the binary flip and delayed return as compatible with a
Phase B whose connection lies outside the present measurement/perception cut.
That interpretation is preserved as the leading ARA hypothesis, not promoted
to the Q28 empirical verdict. Q28 cannot distinguish it from the simulator's
diagonal sign symmetry.

## What would test the hidden-Phase-B interpretation

The next source must contain non-zero off-diagonal connected relations in one
stable, shared coordinate frame. It should preserve:

1. full \(3\times3\) signed relations;
2. named endpoint orientation;
3. time-resolved source release and neighbouring accumulation;
4. an untouched hidden time or trial partition.

Then the test can require:

- correct shared-endpoint alignment to beat endpoint reversal;
- a continuous angle distribution rather than only `0°/180°`;
- the frozen positive lag to survive;
- the flip/return relation to persist when visible diagonal symmetry no longer
  guarantees it.

If that happens while no visible endpoint explains the return, the
out-of-cut Phase-B hypothesis becomes materially stronger. If the relation
disappears when the diagonal symmetry is removed, Q28's effect was a property
of this simulator family rather than evidence for the proposed hidden
coupling.

## Reproduction

Primary runner:

`analysis/quantum/q28_ara9_interlocking_rotational_transport_test.py`

Independent validator:

`analysis/quantum/q28_ara9_interlocking_rotational_transport_validate.py`

Executed notebook:

`analysis/quantum/Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_NOTEBOOK.ipynb`

Frozen protocol SHA-256:

`400789b6ccfa22962d6860b23c379fada7ca00684346bab19daa8fbd88481d14`

Independent validation rebuilt `200` raw relations and passed `38/38`
checks. Maximum raw-to-cache coefficient error was `1.27081e-08`.

