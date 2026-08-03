# T307 — Complex irrationality quadrant in the muon-Fusion overlap model

**Date:** 3 August 2026  
**Frozen verdict:** **COORDINATE RECOVERED WITHOUT FULL PREDICTIVE SUPPORT**  
**Independent validation:** **PASS (`8/8`)**

## Result first

The new complex ARA coordinate is genuinely present and usable in the
idealised muon-Fusion overlap model:

- all three arrival families supplied valid complex states at every adjacent
  prefix;
- all four contraction/expansion × forward/reverse quadrants occurred in
  every family;
- the compressed quadrant state beat persistence, one global complex ratio,
  and all `1,000` frozen temporal-shuffle controls in all three families;
- nevertheless, a generic continuous affine AR(2) model predicted the next
  complex state better in all three families;
- the primary Phi-Time/`1/e` relation was not the most predictive tested pair;
- breaking the same-prefix lineage did not consistently damage the quadrant
  predictor.

The strict G2–G4 gates therefore fail. The result recovers the two-axis ARA
measurement plane and shows that its quadrant compression retains real order,
but it does not establish a unique or superior `1/e <-> Phi` muon law.

The post-gate radial audit produced a sharper exploratory clue: the observed
breathing was consistently closer to

\[
\boxed{1/\phi\longleftrightarrow\phi}
\]

than to the proposed asymmetric `1/e <-> Phi` radial pair. That clue is
promising enough for a fresh test, but it is post-hoc and cannot change the
frozen verdict.

## Plain-language translation

We stopped asking only, “Which schedule scores higher?” Instead, we kept the
entire response as the source phase moved around the observation cycle.

For every pulse count, the Phi-oriented schedule and the `1/e` schedule each
made a phase-response shape. Their difference supplied two perpendicular
cuts—cosine and sine—which formed one directed point. Moving to the next pulse
count moved that point.

That movement supplied exactly the proposed four possibilities:

1. grow while moving forward;
2. grow while moving backward;
3. shrink while moving forward;
4. shrink while moving backward.

Those labels were not random. Knowing the current quadrant helped predict the
next complex movement better than several simple controls. But reducing the
full continuous state to only four labels discarded enough information that a
standard continuous two-step model performed better.

In ARA language: the **quadrant is real and informative, but it is too coarse
to carry the whole muon-model identity by itself**.

## Frozen construction

Fresh prefixes `N=257..1024` were used. Earlier T305/T306 prefixes ended at
`256`.

The pulse width was fixed once at `0.15/1024` for every prefix and carrier.
This prevented late-prefix saturation without recomputing the width after
each stopping point.

For source phase \(\theta_j\), the paired contrast was

\[
D_N(\theta_j)=F_{\phi^{-1},N}(\theta_j)-F_{e^{-1},N}(\theta_j).
\]

Its two perpendicular cuts formed

\[
z_N
=
\frac{2}{128}\sum_{j=0}^{127}
D_N(\theta_j)e^{-i\theta_j}.
\]

Adjacent movement was then

\[
q_N=\frac{z_{N+1}}{z_N}=s_Ne^{i\delta_N}.
\]

`sign(log(s))` supplied contraction versus expansion and `sign(delta)`
supplied forward versus reverse traversal. No folding, clamping, Fourier
search, or outcome-fitted axis created these four states.

## Every family occupied all four quadrants

All `767` adjacent steps were amplitude-valid in each family.

| arrival family | contracting reverse | contracting forward | expanding reverse | expanding forward |
|---|---:|---:|---:|---:|
| `beam7` | 159 | 229 | 155 | 224 |
| `beam7_cycle23` | 144 | 223 | 108 | 292 |
| `beam7_decay` | 209 | 185 | 189 | 184 |

This passes G1. It establishes that the coordinate is usable; merely finding
four sign combinations is not evidence that the ARA compression is the best
law.

## The quadrant retained order, but AR(2) retained more

Holdout error is mean absolute complex error divided by the holdout median
amplitude. Lower is better.

| family | ARA quadrant | persistence | global ratio | affine AR(2) | shuffle 5th percentile |
|---|---:|---:|---:|---:|---:|
| `beam7` | **0.9016** | 1.6413 | 0.9811 | **0.00000000018** | 0.9415 |
| `beam7_cycle23` | **0.9094** | 1.4766 | 0.9769 | **0.7741** | 0.9555 |
| `beam7_decay` | **0.8740** | 0.9892 | 0.9109 | **0.8288** | 0.8984 |

For every family, the ARA compression:

- beat persistence;
- beat the global-ratio predictor;
- was better than every one of the `1,000` shuffled quadrant mappings;
- lost to affine AR(2).

The categorical next-quadrant accuracy was also above the holdout majority
baseline:

| family | quadrant-transition accuracy | majority baseline |
|---|---:|---:|
| `beam7` | 43.86% | 29.77% |
| `beam7_cycle23` | 45.17% | 38.64% |
| `beam7_decay` | 48.56% | 27.68% |

Thus “no predictive support” in the frozen verdict means **the complete G2
gate did not pass**. It does not mean the four states carried zero information.
They carried reproducible order after strong compression, but the unfrozen
continuous relation carried more.

The almost exact AR(2) result for `beam7` is expected from this analytic
instrument: a pure harmonic response generated by cumulative pulse additions
obeys a low-order linear complex recurrence. ARA did not outperform that
available structure.

## The primary pair was not predictively unique

G3 required the primary Phi-Time/`1/e` pair to have the largest ARA
improvement over the strongest fixed continuous baseline in at least two
families. It won none.

All primary improvements were negative because one of the continuous
baselines—especially AR(2)—remained better. Other control pairs lost less
information under the same four-state compression.

This says the recovered quadrant is a general complex-response coordinate in
this model, not a unique signature of the declared primary pair.

## Same-prefix lineage was not required by the compressed predictor

Primary ARA errors versus fixed broken-lineage shifts were:

| family | intact | shift 17 | shift 31 | shift 47 |
|---|---:|---:|---:|---:|
| `beam7` | 0.9016 | 0.9046 | 0.9173 | **0.8975** |
| `beam7_cycle23` | 0.9094 | **0.8804** | 0.9067 | 0.9301 |
| `beam7_decay` | 0.8740 | 0.8491 | 0.7238 | **0.6835** |

Because some broken relations predicted as well or better, G4 failed in all
three families. The four-state compression is responding substantially to
the schedules' marginal rhythmic structure rather than uniquely preserving
their exact same-prefix coupling.

## Post-gate radial result: reciprocal golden breathing

The frozen radial audit compared multi-lag magnitude ratios at lags
`1,2,4,8,16,32,64` against four fixed models:

1. asymmetric `1/e <-> Phi`;
2. reciprocal exponential `1/e <-> e`;
3. reciprocal golden `1/Phi <-> Phi`;
4. unity/persistence.

For the primary pair, reciprocal golden had the smallest median log-distance
in all `21/21` family–lag cells. Across all seven relation pairs, it won
`114/147` cells and unity won `33/147`. Neither model containing `1/e` won a
cell.

Pooling the primary pair across the three families and seven frozen lags gave:

| radial side | observed median | proposed reciprocal-golden landmark | relative difference |
|---|---:|---:|---:|
| contraction | 0.611600 | \(1/\phi=0.618034\) | -1.041% |
| expansion | 1.617293 | \(\phi=1.618034\) | -0.0458% |

The expansion result is particularly close. The two-endpoint log-distance
was `0.010922`. In a clearly post-hoc check, none of `1,000` within-family
temporal shuffles came as close; their fifth-percentile distance was
`0.087947` and median was `0.102765` (conservative empirical `p <= 0.001`).

This is a **lead, not a promoted finding**, for three reasons:

1. the pooled statistic and its shuffle comparison were inspected after the
   frozen gates;
2. the primary construction already contains the Phi-Time carrier
   \(\phi^{-1}\), so it is not an independent discovery of Phi;
3. the source is a deterministic scheduling model, not a muon trajectory.

It nevertheless gives a cleaner next hypothesis:

> In this model, `1/e` behaves better as a distinct decay landmark, while the
> observed radial breathing is approximately reciprocal
> `1/Phi <-> Phi`.

That favours the **separable-role alternative** already recorded in the
complex-quadrant hypothesis over the single asymmetric radial diameter.

## Frozen gates

| gate | result |
|---|---|
| G0 implementation and source integrity | **PASS** |
| G1 usable four-quadrant coordinate | **PASS — 3/3 families** |
| G2 ordered lineage beats every frozen baseline | **FAIL — AR(2) wins** |
| G3 primary-pair specificity | **FAIL — 0/3 families** |
| G4 intact versus broken lineage | **FAIL — 0/3 families** |

The strict frozen verdict remains:

\[
\boxed{\text{coordinate recovered without full predictive support}}
\]

## What this means for ARA

This test supports three narrower statements:

1. radial change and signed phase are a faithful two-axis decomposition of
   this model's ordered response;
2. the four ARA quadrants preserve measurable lineage information even after
   substantial compression;
3. the current asymmetric `1/e <-> Phi` radial placement is not supported by
   the radial audit; reciprocal `1/Phi <-> Phi` is the better fresh-test lead.

It does **not** support:

- a unique Phi/`1/e` muon mechanism;
- superiority over an appropriate continuous dynamical model;
- exact same-prefix coupling as the source of the compressed prediction;
- any claim about laboratory muon behaviour.

## Next decisive test

Freeze the reciprocal-golden radial prediction on a genuinely time-resolved
external record that was not generated from a Phi schedule:

\[
\operatorname{median}(s\mid s<1)\approx\phi^{-1},
\qquad
\operatorname{median}(s\mid s>1)\approx\phi.
\]

Require both ordered endpoints to beat temporal shuffle, non-Phi irrational
controls, fitted reciprocal endpoints, and a continuous complex model. That
would determine whether this is a transferable ARA breathing rule or a
property of the current circular scheduling instrument.

## Reproduction

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\t307_complex_irrationality_quadrant_muon.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\validate_t307_complex_irrationality_quadrant_muon.py'
```

Primary artifacts:

- frozen protocol: `T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_PROTOCOL_v1_FROZEN.md`;
- complex series: `T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_SERIES.csv`;
- local steps: `T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_STEPS.csv`;
- prediction table: `T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_PREDICTION.csv`;
- radial audit: `T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_RADIAL.csv`;
- machine-readable result: `T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_RESULTS.json`;
- independent validation: `T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON_VALIDATION.json`;
- figure: `T307_COMPLEX_IRRATIONALITY_QUADRANT_MUON.png`.

## Scientific boundary

The source families are idealised equations inherited from the Kou–Chen
muon-reactivation scheduling crosswalk. They are not measured particle tracks,
laboratory pulse-response traces, or net-Fusion-yield observations. T307 tests
the geometry and predictive compression of that scheduling instrument only.
