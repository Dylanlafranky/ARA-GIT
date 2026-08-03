# T337 — Di-ARA traversal direction predictor

**Date:** 3 August 2026  
**Framework verdict:** **ARCHITECTURE-INVALID AS AN ARA HANDOVER TEST**  
**Implementation verdict:** **THE IMPOSED `T+iR` DIRECTION MODEL WAS NOT SUPPORTED**  
**Primary horizon:** 6 months  
**Validation:** PASS, `10/10` independent checks

> **Post-result correction:** T337 inherited T336's unestablished assumption
> that NINO3.4 and warm-water volume were the relevant same-scale perpendicular
> ARA axes. Its scores remain reproducible, but they test only Codex's imposed
> `T+iR` representation. They do not test Dylan's ENSO geometry. See
> `../T336_T337_ENSO_ARCHITECTURE_INVALIDATION_2026-08-03.md`.

## Plain-language result

T336 showed a small direction hint after the full handover failed as a direct
value predictor. T337 froze that narrower question and trained the same causal
features to predict whether NINO3.4 would rise or fall.

The hint did **not** become a forecasting win. At the primary six-month
holdout:

- signed traversal: balanced accuracy `0.7353`, accuracy `0.7157`;
- raw levels: `0.7322`, `0.7157`;
- ordinary raw movement: `0.7438`, `0.7255`.

Traversal gained only `0.0032` over raw levels and lost `0.0085` to ordinary
movement. Its paired interval against raw movement was
`[-0.0268, 0.0000]`. It failed the predeclared `+0.02` material-improvement
gate, the ordinary-accuracy guard, and the bootstrap gate.

The corrected combined conclusion from T336 and T337 is:

> The imposed `T+iR` radius/turn features did not beat the named controls. A
> geometry-led ENSO handover model remains untested because the tested axes
> were never established as the correct identity, scale or perpendicular pair.

## Frozen target and models

The directional target was

\[
y_{t,h}=\operatorname{sign}(T_{t+h}-T_t).
\]

Exact-zero changes were excluded. The primary model used only the three
continuous signed traversal cuts at octave lags `1,2,4`, added to the same
strong state baseline as T336. Raw movement, full Di-ARA, radius-only,
quadrant labels, past-trend persistence and broken lineage were frozen
controls. Every decoder used the same fixed ridge penalty and causal expanding
fit.

## Primary six-month replay

There were `102` non-zero-change origins in 2017–2025.

| Model | Balanced accuracy | Accuracy | Positive recall | Negative recall | AUC |
|---|---:|---:|---:|---:|---:|
| Raw levels | 0.7322 | 0.7157 | 0.8372 | 0.6271 | 0.8270 |
| Raw movement | **0.7438** | **0.7255** | 0.8605 | 0.6271 | 0.8285 |
| Signed traversal | 0.7353 | 0.7157 | 0.8605 | 0.6102 | **0.8301** |
| Full Di-ARA | 0.7004 | 0.6863 | 0.7907 | 0.6102 | 0.8242 |
| Radius only | 0.7259 | 0.7157 | 0.7907 | **0.6610** | 0.8266 |
| Quadrant labels | 0.6910 | 0.6863 | 0.7209 | **0.6610** | 0.8013 |
| Broken full relation | 0.7142 | 0.7059 | 0.7674 | **0.6610** | 0.8199 |

Traversal's AUC was fractionally highest, but the thresholded forecast—the
declared task—was worse than raw movement. That is not a pass.

## Bootstrap and gates

| Comparison | Balanced-accuracy lift | 95% interval | P(lift > 0) |
|---|---:|---:|---:|
| Traversal vs raw levels | +0.00315 | [-0.02459, +0.03821] | 0.5328 |
| Traversal vs raw movement | -0.00847 | [-0.02679, 0.00000] | 0.0000 |

Only the lineage-specificity gate passed. The primary material lift,
ordinary-accuracy and bootstrap gates failed.

## Horizon pattern

| Horizon | Raw levels | Raw movement | Traversal | Traversal minus raw movement |
|---:|---:|---:|---:|---:|
| 3 months | 0.7596 | 0.7596 | **0.7788** | +0.0192 |
| 6 months | 0.7322 | **0.7438** | 0.7353 | -0.0085 |
| 9 months | **0.7611** | 0.7519 | 0.7500 | -0.0019 |
| 12 months | 0.7679 | 0.7679 | 0.7714 | +0.0036 |

The three-month lift is the strongest descriptive lead and lands just below
the frozen `+0.02` material threshold. It was not the primary horizon and has
no predeclared primary bootstrap, so it cannot be promoted. The 12-month
broken relation also beat intact traversal (`0.7839` versus `0.7714`), further
showing that the small horizon-specific variations are not a stable operator.

## Interpretation

T337 says only that appending the imposed `T+iR` cuts to this classifier did
not reliably outperform the controls. It cannot say whether the intended
movement geometry is present, absent or transportable because that geometry
was never established.

The next step is architectural, not predictive: Dylan identifies the proposed
ENSO parent and its child/rung relations; Codex translates those relations into
measurable coordinates and controls; Dylan confirms the translation; only then
is a new transport test frozen.

## Reproduction files

- `T337_DI_ARA_ENSO_DIRECTION_PROTOCOL_v1_FROZEN.md`
- `T337_DI_ARA_ENSO_DIRECTION_PROTOCOL_v1_FROZEN.sha256`
- `t337_diara_enso_direction.py`
- `T337_DI_ARA_ENSO_DIRECTION_RESULTS.json`
- `T337_DI_ARA_ENSO_DIRECTION_SCORES.csv`
- `validate_t337_diara_enso_direction.py`
- `T337_DI_ARA_ENSO_DIRECTION_VALIDATION.json`

Frozen SHA-256 values:

- protocol: `831A55751213E07622F0D286A3CB956FFECE02D2E2689E51EB49218FEFA42EC4`
- scoring script: `5F12A29DBDF8A9AF68B76455A3A26DA92D5DB5C3BA55030C1F07519A7FBF1605`
