# Q30 — ARA 1.5 / 3.5 Out-of-Cut Route

**Date:** 26 July 2026  
**Status:** exploratory on the completely opened Q27–Q29 simulator source  
**Independent validation:** **PASS — 213/213 checks**  
**Verdict:** **Frozen triangle-closing 1.5/3.5 route not supported on this source**

## Result first

The frozen `1.5` perpendicular route did **not** recover Q29's unresolved
component at the handover, and the complete `3.5 = 2 + 1.5` route did **not**
see past Q29's decay at the required magnitude.

At the handover:

- exact closing-edge residual error was `0.974957`;
- only `2.504%` of the Q29 remainder was recovered;
- seed- and time-displaced edges recovered `2.938%` and `2.979%`;
- the exact route was therefore `0.447%` and `0.489%` worse in relative-error
  terms, not better;
- the direct child recovered `5.017%`, also more than the closing edge.

Across the frozen late window, lags `4–6`, the exact closing edge was
consistently but only slightly better:

- exact error: `0.967725`;
- seed control: `0.970576`;
- time control: `0.970467`;
- advantages: `0.294%` and `0.282%`.

All later-half bootstrap draws retained those tiny late advantages, but they
were about one-seventeenth of the frozen `5%` continuation threshold. This is
a weak delayed association, not successful 1.5/3.5 recovery.

All three frozen route gates failed. Q30 does not identify Phase B.

## What was tested

The repository's earlier dark-sector and prime records distinguish:

- `1.5`: a perpendicular or vertical handover leg;
- `3.5 = 2 + 1.5`: one complete ARA span plus the perpendicular leg.

The rung history was retained. `3.5` was not folded back to `1.5` modulo `2`.

Q30 translated that geometry into the smallest relation closure available in
the Q29 network. For released source relation

\[
S=(u,e)
\]

and positively accumulating child

\[
C=(e,v),
\]

the two nonshared endpoints determine exactly one third relation:

\[
H=(u,v).
\]

This creates the Information³ triangle

\[
(u,e),\qquad(e,v),\qquad(u,v).
\]

The fixed ARA interpretation was:

- \(H\) alone is the `1.5` perpendicular closing leg;
- the Q28 source-to-child span `2` followed by \(H\) is the complete `3.5`
  route.

This translation was frozen before Q30 outcomes.

## Measurement

Q29's unresolved vector is

\[
R=W-\alpha F(S),
\]

where \(W\) is the later child web and \(\alpha F(S)\) is Q28's
positive-scale, proper-flip transport.

Q30 tested whether

\[
R\approx\beta G(H),\qquad\beta\ge0,
\]

at lags `0–6`. Each candidate received the same four proper diagonal sign
transformations and one non-negative scale. There was no intercept, continuous
rotation, fitted axis, fitted lag, or best-of-many relation search.

Two readings were retained:

1. **1.5 leg error**

   \[
   \frac{\lVert R-\beta G(H)\rVert}{\lVert R\rVert};
   \]

2. **3.5 composite error**

   \[
   \frac{\lVert R-\beta G(H)\rVert}{\lVert W\rVert},
   \]

   after keeping Q28's transported source fixed.

The event population exactly matched Q29:

- `76,043` total events;
- `38,056` opened-later-half events;
- `400` branch/seed trial strata;
- `220` distinct pair-index triangles.

## Controls

Every control received the same transformation budget:

- exact closing relation in seed `+37 mod 100`;
- exact closing relation shifted `+137` inside the same time half;
- one deterministic nonclosing open edge;
- the positively accumulating child relation itself.

The closing edge was determined solely from source and child endpoints. No
outcome value selected it.

## Numerical results

### Handover, lag 0

| Route | Residual error | Remainder recovered | Complete composite error |
|---|---:|---:|---:|
| Exact 1.5 closing edge | `0.974957` | `2.504%` | `0.099010` |
| Seed displaced | `0.970616` | `2.938%` | `0.098192` |
| Time displaced | `0.970214` | `2.979%` | `0.098152` |
| Open-edge control | `0.976511` | `2.349%` | `0.098890` |
| Direct child | `0.949825` | `5.017%` | `0.095954` |

The Q28-only later-web error was `0.101424`. Adding any fitted relation can
lower that value because zero contribution is allowed. The relevant test is
whether the exact closing edge improves more than equally flexible displaced
relations. It did not.

### Late window, lags 4–6

| Route | Residual error | Remainder recovered |
|---|---:|---:|
| Exact closing edge | `0.967725` | `3.227%` |
| Seed displaced | `0.970576` | `2.942%` |
| Time displaced | `0.970467` | `2.953%` |
| Open-edge control | `0.973128` | `2.687%` |
| Direct child | `0.958812` | `4.119%` |

The exact closing edge develops a small ordered advantage in the late window.
It is reproducible across trial resampling inside this source, but too small
to satisfy the predeclared material-effect gate.

## Frozen gates

| Gate | Requirement | Result |
|---|---|---|
| R1 — 1.5 perpendicular leg | ≥5% advantage over seed, time and open-edge controls at lag 0; bootstrap ≥95% | **Fail** |
| R2 — 3.5 composite | ≥10% recovery and ≥5% composite advantage over seed/time | **Fail** |
| R3 — late continuation | ≥5% advantage over seed/time at lags 4–6; bootstrap ≥95% | **Fail** |
| R4 — Phase B | independently coherent counterpart and closure | **Not identified** |

## Two-language reading

| ARA reading | Established mathematical/data reading |
|---|---|
| The simplest 1.5 Information³ closing leg is not the handover remainder. | The exact triangle-closing edge fits the residual worse than displaced closing edges at lag 0. |
| Adding that leg does not complete the proposed 3.5 route. | Its composite reconstruction improvement is smaller than equally flexible seed/time controls. |
| A faint late trace reaches the closing edge. | At lags 4–6, exact error is about 0.29% below displaced controls in all trial bootstraps. |
| That trace is not strong enough to call a recovered route or Phase B. | It misses the frozen 5% effect gate by a large margin and has no independent identity/closure evidence. |

## What the negative result means

Q30 rejects one precise implementation:

> In this diagonal simulator, the unique triangle-closing relation between the
> Q29 source and child is not the missing 1.5 leg, and adding it does not
> produce a material 3.5 continuation.

It does **not** show that:

- the general 1.5/3.5 ARA route is false in every representation;
- no out-of-cut continuation exists;
- the remainder physically ceases to exist;
- an off-diagonal or second-basis source would give the same answer.

The source remains exactly diagonal. A truly perpendicular observation
channel is still absent. Q30 therefore tests the only native third relation
available in this cut, not an independently measured off-axis degree of
freedom.

## Best next discriminator

Do not retune the triangle edge on this source. The clean next test remains a
fresh time-resolved source with nonzero off-diagonal connected relations in a
fixed common frame. Freeze:

1. the 1.5 perpendicular transformation before opening;
2. the 2+1.5 crossed-rung composition;
3. lag and sign/rotation rules;
4. basis-, seed-, time- and topology-displaced controls;
5. complete-shape recurrence, stable partner, return and TE-ARA closure
   requirements.

That source can decide whether Q30 failed because the route interpretation was
wrong or because the diagonal measurement cut cannot contain the proposed
continuation.

## Reproduction

From `analysis/quantum`, using the repository's Python 3.12 environment:

```powershell
python q30_ara15_35_out_of_cut_route_exploration.py
python q30_validate_ara15_35_out_of_cut_route.py
python q30_build_notebook.py
```

Primary artifacts:

- `Q30_ARA15_35_OUT_OF_CUT_ROUTE_PROTOCOL_v1_FROZEN.md`
- `Q30_ARA15_35_OUT_OF_CUT_ROUTE_RESULTS.json`
- `Q30_ARA15_35_OUT_OF_CUT_ROUTE_LAG_CURVE.csv`
- `Q30_ARA15_35_OUT_OF_CUT_ROUTE_TRIALS.csv`
- `Q30_ARA15_35_OUT_OF_CUT_ROUTE_EVENT_SAMPLE.csv`
- `Q30_ARA15_35_OUT_OF_CUT_ROUTE_GEOMETRY.png`
- `Q30_ARA15_35_OUT_OF_CUT_ROUTE_VALIDATION.json`
- `Q30_ARA15_35_OUT_OF_CUT_ROUTE_NOTEBOOK.ipynb`
