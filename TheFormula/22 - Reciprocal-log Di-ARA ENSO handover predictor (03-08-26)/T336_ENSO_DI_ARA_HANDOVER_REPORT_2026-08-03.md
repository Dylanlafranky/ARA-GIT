# T336 — reciprocal/log Di-ARA ENSO handover predictor

**Date:** 3 August 2026  
**Framework verdict:** **ARCHITECTURE-INVALID AS AN ARA HANDOVER TEST**  
**Implementation verdict:** **THE IMPOSED `T+iR` ENCODING WAS NOT SUPPORTED**  
**Primary horizon:** 6 months  
**Validation:** PASS, `12/12` independent checks

> **Post-result correction:** Codex imposed NINO3.4 and warm-water volume as
> same-scale perpendicular axes without establishing that geometry with Dylan.
> Complex notation guarantees mathematical perpendicularity; it does not prove
> an ARA-perpendicular ENSO identity. This report therefore preserves a valid
> computational negative for that imposed encoding, but it does not test or
> reject Dylan's ENSO handover geometry. See
> `../T336_T337_ENSO_ARCHITECTURE_INVALIDATION_2026-08-03.md`.

## Plain-language result

The imposed `T+iR` coordinate did **not** improve direct six-month ENSO value
prediction over either a strong raw-state model or the same model supplied
with ordinary raw movements. The full Di-ARA handover scored climatology skill
`0.4110`, compared with `0.4315` for the raw-state model and `0.4312` for raw
movement. Its MAE was also worse: `0.4865` instead of approximately `0.473`.

This is a clean negative for the imposed encoding and tested decoder. Because
the identity, rung equality and perpendicularity were not established first,
it is not evidence for or against the intended ARA coordinate. Within the
imposed encoding, the decomposition exposed:

- the **radial contraction/expansion cut** caused most of the point-value loss;
- the **signed traversal/turn cut** nearly tied the strong baseline at six
  months and slightly exceeded its skill (`0.4328` versus `0.4315`), although
  it did not improve MAE;
- the full handover and radius-only forms sometimes improved direction while
  worsening the predicted magnitude;
- the apparent 9–12 month improvement in the 2008–2016 evaluation period
  reversed in the fixed 2017–2025 replay holdout.

The corrected conclusion is therefore:

> The artificial `T+iR` construction is not an adequate direct point-value
> decoder. Whether a correctly mapped ENSO ARA/Di-ARA handover is adequate was
> not tested.

## The tested identity: ARA and conventional math side by side

The coupled ENSO state was

\[
z_t=T_t+iR_t,
\]

where `T` is the causally standardised NINO3.4 surface state and `R` is the
causally standardised full-basin warm-water-volume reservoir.

For octave lags `m = 1, 2, 4`, the same handover was written in two languages:

| ARA reading | Mathematical coordinate | Meaning in this test |
|---|---|---|
| position on the centred `0–2` diameter | \(a_{t,m}=\tanh(\tfrac12\log(|z_t|/|z_{t-m}|))\) | contraction below the ridge or expansion above it |
| perpendicular traversal cut | \(\delta_{t,m}=\arg(z_t\overline z_{t-m})/\pi\) | reverse or forward turn through the coupled plane |
| Di-ARA state | \((a_{t,m},\delta_{t,m})\) | one of `Ba`, `Ab`, `bA`, `aB` |

The bounded ARA coordinate is `x = 1 + a`. Reciprocal contraction and
expansion reflect exactly as `x ↔ 2-x`. No Phi value, Fourier transform,
fitted waveform, or post-result endpoint was inserted.

## Data and causal design

- Public monthly NINO3.4 and NOAA/PMEL western/eastern WWV data.
- Common record: January 1980 through December 2025 (`552` months).
- Expanding causal fit: a training example was admitted only after its target
  month was already observable at the current forecast origin.
- Evaluation origins: 2008–2016.
- Fixed replay holdout origins: 2017–2025.
- Horizons: 3, 6, 9 and 12 months; 6 months was primary.
- Ridge penalty: fixed at `1`; no lag, model, endpoint or penalty was tuned
  after scoring.

Because ENSO and much of this calendar period had already been studied in
TheFormula, this is a **fixed retrospective replay**, not a pristine
untouched-domain confirmation.

## Primary six-month holdout result

There were `102` forecast origins.

| Model | Skill vs climatology | MAE | Correlation | Direction |
|---|---:|---:|---:|---:|
| Raw levels | 0.4315 | 0.4733 | 0.6475 | 0.7353 |
| Raw levels + ordinary movement | 0.4312 | 0.4732 | 0.6476 | 0.7353 |
| Raw levels + full Di-ARA | 0.4110 | 0.4865 | 0.6336 | 0.7451 |
| Raw levels + radius only | 0.4141 | 0.4865 | 0.6353 | **0.7549** |
| Raw levels + turn only | **0.4328** | 0.4738 | **0.6489** | 0.7353 |
| Raw levels + quadrant labels | 0.3362 | 0.5141 | 0.5800 | 0.7451 |
| Broken surface/reservoir lineage | 0.3332 | 0.5240 | 0.5770 | 0.7157 |

The point estimate for turn-only skill is only `+0.0013` above raw levels and
its MAE is slightly worse. It is a lead for the next test, not a forecasting
win.

## Frozen gates and uncertainty

The paired 12-month moving-block bootstrap used `5,000` repetitions.

| Comparison | Observed MSE improvement | 95% interval | P(improvement > 0) |
|---|---:|---:|---:|
| Full Di-ARA vs raw levels | -0.01210 | [-0.03637, +0.01013] | 0.1584 |
| Full Di-ARA vs raw movement | -0.01192 | [-0.03705, +0.01087] | 0.1692 |

The frozen point-estimate and bootstrap gates failed. The intact relation did
beat the deliberately broken 12-month-offset lineage, so the negative cannot
be explained merely by the broken control being equally good.

## Horizon and split behaviour

In evaluation, the full handover slightly improved skill at 3, 9 and 12
months; at 12 months it scored `0.0738` versus `0.0443` for raw movement, and
turn-only reached `0.0845`. None of that transported to the later replay:

| Horizon | Raw-movement skill | Full Di-ARA skill | Di-ARA lift |
|---:|---:|---:|---:|
| 3 months | 0.7253 | 0.7095 | -0.0158 |
| 6 months | 0.4312 | 0.4110 | -0.0202 |
| 9 months | 0.2392 | 0.1813 | -0.0579 |
| 12 months | 0.1950 | 0.1277 | -0.0673 |

That reversal is evidence of regime dependence or evaluation-period fitting,
and is exactly why the later fixed replay was retained.

## What the test does and does not say

Everything in this section is scoped to the imposed `T+iR` representation. It
does not establish that these are the correct ENSO identities, rungs or cuts.

### Supported observations

1. The reciprocal/log ARA and signed-turn cuts can be calculated causally on
   a complex physical record.
2. The two cuts are not interchangeable: the radius term and turn term carry
   materially different forecasting effects.
3. Correct surface/reservoir lineage is more coherent than the declared
   12-month-offset broken relation at the primary horizon.
4. Direction can improve while point value worsens, reproducing a longstanding
   TheFormula distinction between geometry and amplitude decoding.

### Rejected or still open

1. The full handover is **not** a superior six-month point-value predictor in
   this implementation.
2. Four quadrant labels are too coarse to recover the useful continuous
   movement.
3. Evaluation-period improvements do not count as transportable evidence when
   they reverse in holdout.
4. This test does not decide whether another parent identity, child boundary,
   target variable, or transition decoder can use the same geometry better.

## Correct next rung

Do not reuse these coordinates yet. First map the ENSO parent, children, rungs
and coupling directions with Dylan guiding the geometry. Codex should then
translate the agreed map into mathematics and controls, and Dylan should
confirm the translation before a new protocol is frozen.

**Subsequent result:** T337 froze a direction branch before this architectural
error was recognized and therefore inherited it. T337 is also retained only
as a negative for the imposed representation. Its report is in `../23 -
Di-ARA traversal direction predictor
(03-08-26)/T337_DI_ARA_ENSO_DIRECTION_REPORT_2026-08-03.md`.

## Reproduction and audit files

- `T336_ENSO_DI_ARA_HANDOVER_PROTOCOL_v1_FROZEN.md`
- `T336_ENSO_DI_ARA_HANDOVER_PROTOCOL_v1_FROZEN.sha256`
- `t336_enso_di_ara_handover.py`
- `T336_ENSO_DI_ARA_HANDOVER_RESULTS.json`
- `T336_ENSO_DI_ARA_HANDOVER_FORECASTS.csv`
- `validate_t336_enso_di_ara_handover.py`
- `T336_ENSO_DI_ARA_HANDOVER_VALIDATION.json`

Frozen SHA-256 values:

- protocol: `FCD42628005836B0793426C3B10F0EA27E36AE36400B0AC260F4CC7EC7F187A7`
- scoring script: `C2306B46927A059B4F4B1F5730A9B8D3F69CD6A16ADF4D1DB043ADD8F238974C`
