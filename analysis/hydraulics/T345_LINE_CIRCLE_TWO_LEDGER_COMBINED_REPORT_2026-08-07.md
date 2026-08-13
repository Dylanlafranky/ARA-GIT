# T345 — line/circle geometry and two information ledgers

**Date:** 7 August 2026  
**Status:** frozen post-T344 diagnostic; validated laboratory/numerical transfer  
**Frozen protocol SHA-256:** `65770ca22b4be2cdca94eecbb976f31d139b9df30847bec509b26920f52a7a23`

## Answer first

T345 gives a **mixed but fully replicated** result.

- The corrected line-versus-circle geometry passed strongly in both the
  laboratory and numerical representations.
- Coherent curved/non-closing paths concentrated ordered ARA-sector relations
  more strongly than crooked/random-like paths in both representations.
- The stronger frozen information story failed. Low-order closure did not have
  more relation concentration than coherent non-closure; coherent circular
  paths did not preserve more held-out future-movement information; and their
  successor windows lost rather than gained relation concentration.
- Laboratory and numerical Gates A/B/C/D were identically
  **PASS / FAIL / FAIL / FAIL**. All seven component signs agreed, so the
  predeclared transfer Gate E passed completely.

This is evidence for a narrow geometric distinction among straight closure,
coherent curvature and crooked curvature. It is not evidence for an exact
irrational constant, a universal Irrationality Di-ARA, or the proposed delayed
information handoff in its frozen T345 form.

## Why T345 was needed

T344's registered traversal statistic was

\[
T=\frac{\text{direct displacement}}{\text{total path length}},
\]

so it measured straightness. T345 separated that coordinate from historical
turn organisation:

\[
D=\frac{\|p_W-p_0\|}{\sum_j\|v_j\|},
\qquad
G=\frac{|\sum_j\gamma_j|}{\sum_j|\gamma_j|},
\qquad
C=(1-D)G.
\]

Here `D` is line directness, `G` asks whether turns keep the same signed
orientation, and `C` is conservative historical circularity. A curved zigzag
therefore does not automatically count as a circle.

T345 also kept two questions separate:

1. `I_move`: held-out information about the next ARA movement address;
2. `I_conn`: concentration in the 16 ordered ARA-sector relation channels.

`I_conn` is a relation-channel concentration, not total thermodynamic
information.

## Frozen results

| Frozen component (first minus second) | Laboratory estimate [95% whole-track CI] | Numerical estimate [95% whole-track CI] | Result |
|---|---:|---:|---|
| A1 structured − random circularity | `+0.175794 [0.157257, 0.183695]` | `+0.172279 [0.163277, 0.177037]` | PASS / PASS |
| A2 closure − structured directness | `+0.365938 [0.353160, 0.374329]` | `+0.241183 [0.236826, 0.245132]` | PASS / PASS |
| B1 closure − structured connection concentration | `−0.087339 [−0.100894, −0.073472]` | `−0.093919 [−0.103040, −0.086853]` | FAIL / FAIL |
| B2 structured − random connection concentration | `+0.126594 [0.100930, 0.152758]` | `+0.458914 [0.439943, 0.472858]` | PASS / PASS |
| C circle-like − crooked future-movement information | `−0.000757 [−0.003043, 0.001378]` | `−0.000233 [−0.000365, −0.000102]` | FAIL / FAIL |
| D1 future connection change after circle-like paths | `−0.185055 [−0.203439, −0.166811]` | `−0.082013 [−0.089674, −0.074048]` | FAIL / FAIL |
| D2 circle-like − crooked future connection change | `−0.225680 [−0.248201, −0.204450]` | `−0.237813 [−0.248631, −0.226640]` | FAIL / FAIL |

Every component used 2,000 whole-trajectory cluster-bootstrap replicates and
required agreement in at least two of the three hydraulic conditions. All
condition-specific signs underlying the passed components met that rule.

## Plain-language interpretation

The path really does have two separable aspects:

- how directly it gets from the start to the end;
- whether its bends keep turning coherently around one side.

That is the strongest T345 result. The coherent curved paths were not merely
messier straight paths; they occupied a reproducibly different region and
held a more concentrated set of ordered ARA relations than random crooked
motion.

The information handoff did **not** behave as predicted. Coherent circle-like
windows were already relation-concentrated, then their non-overlapping
successors became less concentrated. Crooked windows moved in the opposite
direction on average. A legitimate fresh lead is therefore:

> coherent curvature may be an accumulated relation state whose exit is a
> release/distribution event, rather than a state that subsequently
> accumulates connection concentration.

That sentence is post-result interpretation. It must receive a new frozen test
before it can count as evidence for an ARA accumulation-to-release handover.
It does not repair T345 Gates B-D.

## Transfer and validation

The laboratory representation contained 5,365 tracks and 2,476,448 primary
`W=15` windows. The numerical representation contained 5,400 tracks and
8,233,756 primary windows. Sensitivity outputs at `W=8` and `W=30` were also
retained.

An independent artifact validator:

- reconstructed all seven component verdicts from CSV outputs rather than
  trusting the result JSON;
- reconstructed Gates A-D;
- verified 2,000 valid bootstraps per component;
- verified all six public-source hashes and the frozen protocol hash;
- verified the `W=8,15,30` outputs and both registered path classes;
- confirmed identical gate verdicts and signs across representations.

The 8.23-million-window numerical optimizer initially exhausted memory while
allocating a full residual matrix. T345 replaced only that temporary with an
algebraically identical chunked calculation. A pre-run equivalence check gave
objective difference `0`, maximum coefficient difference `1.78×10⁻¹⁵`, and
maximum probability difference `6.66×10⁻¹⁶` against the original optimizer.

## Evidence boundary

The [BAW controlled-weir trajectory source](https://doi.org/10.48437/99f329-73aee6)
and its [associated study](https://doi.org/10.59490/jchs.2025.0050) had already
been opened for T344. T345's formulas and gates were frozen before T345
calculation, but the run remains a diagnostic successor rather than an
independent new-domain confirmation.

No `phi`, reciprocal-`phi`, `e` or `1/e` constant participates in a primary
T345 metric or gate.

## Post-result framework clarification (9 August 2026)

The failed delayed-handoff rule had placed Phase-B accumulation after the
circle. The corrected ARA interpretation is simultaneous and coupled:

\[
A_n \rightarrow B_{\rm stored}\rightarrow B_{\rm released}
\rightarrow A_{n+1}.
\]

The circle-like interval may already be the connection-stored state that
maintains bounded recurrent Phase-A movement. Its successor's negative
`delta I_conn` can therefore be a release or redistribution, rather than a
failure to begin accumulating. This interpretation was made after seeing
T345 and does not change its failed Gates B-D.

The next admissible test must be frozen independently. It should use movement
geometry alone to identify a Phase-A -> recurrent -> Phase-A handover, then
ask whether `I_conn` peaks in the recurrent interval and whether the magnitude
of its subsequent loss is coupled to the strength of the next directional
opening. It must also break the time-aligned connection/movement pairing as a
control.

## Artifacts

- `T345_LINE_CIRCLE_TWO_LEDGER_PROTOCOL_v1_FROZEN.md`
- `T345_LINE_CIRCLE_TWO_LEDGER_FIGURE.png`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_FIGURE.png`
- `T345_LINE_CIRCLE_TWO_LEDGER_CONTRASTS.csv`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_CONTRASTS.csv`
- `T345_LINE_CIRCLE_TWO_LEDGER_RESULTS.json`
- `T345_LINE_CIRCLE_TWO_LEDGER_NUMERICAL_REPLICATION_RESULTS.json`
- `T345_LINE_CIRCLE_TWO_LEDGER_VALIDATION_2026-08-07.md`
- `T345_LINE_CIRCLE_TWO_LEDGER_VALIDATION.json`
- `t345_line_circle_two_ledger.py`
- `validate_t345_line_circle_two_ledger.py`
