# PN34 — remaining-fill rank budget

**Run:** 22 July 2026  
**Formal status:** **PARTIAL SUPPORT**  
**Fresh test:** 6,000 prospectively frozen anchors across three previously unused scales  
**Implementation/reconstruction:** all non-endpoint checks passed

## Answer first

Yes—the useful relation is real, but it is a **population rank-budget rule**, not an individual prime cheat.

PN34 combined PN26's complete Phase A quiet-state locator with the PN33 inverse-density fill of the omitted Phase B parent. Without fitting to the fresh labels, it predicted how often the true next prime would appear in the first, first two and first three Phase A quiet states. All **9/9 calibration tolerances** and all **6/6 rank-budget thresholds** passed.

Full support was blocked by one deliberately strict endpoint: predicted first-reading success increased low → middle → high, while the observed middle and high cohorts swapped by only **0.20 percentage points**. The formal verdict is therefore partial support.

| Scale | Remaining fill x_B | Top 1 predicted | Top 1 observed | Top 2 predicted | Top 2 observed | Top 3 predicted | Top 3 observed |
|---|---:|---:|---:|---:|---:|---:|---:|
| low | 0.215884 | 92.791% | 92.850% | 99.480% | 99.450% | 99.963% | 99.950% |
| middle | 0.158364 | 94.659% | 95.450% | 99.715% | 99.700% | 99.985% | 100.000% |
| high | 0.134089 | 95.459% | 95.250% | 99.794% | 99.650% | 99.991% | 99.900% |

## What the bridge means in plain language

PN26 first removes every position struck by the complete lower Phase A parent. Its remaining quiet positions are strong prime candidates. Phase B is the omitted upper band of factor gates that can still turn some of those candidates into composites.

PN34 measured the unresolved Phase B thinning as

```text
R_B = product over Phase B of p/(p-1)
x_B = 2 log(R_B)/log(2)
first-reading prior = 1/R_B = 2^(-x_B/2)
top-k coverage = 1 - (1 - first-reading prior)^k
```

Plainly: if the omitted parent is small, most Phase A quiet states survive it and the first reading is usually enough. The residual failure probability tells us how quickly a second and third reading close the ranked list.

## Fresh rank counts

| Scale | Rank 1 | Rank 2 | Rank 3 | Beyond rank 3 |
|---|---:|---:|---:|---:|
| low | 1,857 | 132 | 10 | 1 |
| middle | 1,909 | 85 | 6 | 0 |
| high | 1,905 | 88 | 5 | 2 |

Across all three scales, two readings exceeded 99% coverage and three reached at least 99.9%. The fresh data contained three cases beyond rank three, so the construction remains an extremely short ranked approximation rather than a universal three-state identity.

## Benchmark reading

The fill prior's top-one log loss was `0.211445496`, versus `0.212766751` for the frozen pooled PN26 prior and `0.246562071` for the simple conditional PNT prior. That is only a `0.62%` improvement over the already-strong flat prior, but a `14.24%` improvement over the tested PNT conditional approximation.

The comparison matters: most predictive power still comes from PN26's complete Phase A parent. PN34 adds a small but coherent scale-aware calibration layer.

## Why the greater-than-1.5 shortcut is not the rule

The prospectively successful coordinate was not `max child > 1.5`. The relevant remaining-fill readings were only `0.134–0.216`. Earlier direct five-wave threshold checks rejected true primes and hard composites at almost the same rate. The successful object is the **complete omitted-parent density**, not one child's largest local coordinate.

## Scientific boundary

PN34 supports:

- a prospective bridge from PN33-style fill to PN26 rank depth;
- a no-fit population prior that calibrated all nine fresh scale/depth cells; and
- the interpretation that the omitted upper parent supplies the residual correction budget.

PN34 does not support:

- identifying which individual first candidate is composite;
- skipping construction of the lower/upper prime-gate parents;
- constant-cost prime generation or certification;
- improved asymptotic complexity; or
- new number theory beyond an ARA crosswalk to conditional sieve density.

## Validation and uncertainty

The prediction file was sealed before truth was opened. Independent reconstruction reproduced every candidate and prior at all three scales. Prime truth came from separately constructed segmented masks with deterministic Miller–Rabin spot checks. The validation receipt recorded `21/22` total checks; the sole false check is the registered scientific scale-order endpoint, not an implementation mismatch.

At the high scale, the predicted three-reading coverage (`99.9906%`) sat slightly above the observed Wilson interval because two of 2,000 anchors fell beyond rank three. This is another reason to retain the partial verdict and not overstate the population formula as exact.

## Recommended next step

Keep PN34 as the population-budget explanation for PN26. The next genuinely new target would require an anchor-varying, pre-label coordinate derived from the omitted parent that separates the rare rank-1 misses **within one scale**. Without that, the fill prior tells us how many readings to keep, not which reading wins.

## Artifacts

- Fidelity packet and frozen protocol: `PN34_FILL_RANK_BUDGET_FIDELITY_PACKET_v1_DRAFT.md`, `PN34_FILL_RANK_BUDGET_PROTOCOL_v1_FROZEN.md`
- Frozen predictions: `PN34_FILL_RANK_BUDGET_PREDICTIONS.csv`
- Results and validation: `PN34_FILL_RANK_BUDGET_RESULTS.json`, `PN34_FILL_RANK_BUDGET_VALIDATION.json`
- Validated rows: `PN34_FILL_RANK_BUDGET_VALIDATED_ROWS.csv`
- Figure and notebook: `PN34_FILL_RANK_BUDGET_FIGURE.png`, `PN34_FILL_RANK_BUDGET_REPRODUCIBILITY.ipynb`
