# 21 — Double-Helix Relation and Closure-Defect Predictor

This thread translates the July 2026 ARA mathematical mapping into a frozen causal forecast:

```text
two strands + their relation + full-cycle closure defect -> next temporal slice
```

The primary test is `nsr047`; `nsr053` is a simultaneous replication. The equations, horizons, preprocessing, baselines, and failure rules are frozen in `PREREGISTRATION.md` before either record is scored.

Files:

- `PREREGISTRATION.md` — frozen prediction and evaluation protocol.
- `ara_double_helix_predictor.py` — implementation.
- `ARA_DOUBLE_HELIX_PREDICTION_RESULT.md` — generated result and honest verdict.
- `ara_double_helix_prediction_result.json` — machine-readable scores.

## Frozen result

**Preregistered verdict: FAIL.**

- Primary `nsr047`: 0/6 horizons beat the matched rolling-circle channel on both correlation and MAE; mean correlation lift `-0.0006`.
- Replication `nsr053`: 5/6 horizons beat it on both; mean correlation lift `+0.0007`; h=48 MAE improved by `11.25 ms`.
- Transition-direction lift was `-0.0006` primary and `+0.0069` replication, below the partial-support threshold.
- Causal prefix audit passed exactly on both records (`max coefficient difference = 0`).
- Ordinary AR remained stronger than the raw circle and raw ARA geometry on both subjects.

The split means the fixed relation/closure translation is not universal as written. The relation-only ablation is more promising than the asymmetric-shape projection on `nsr053`, but no repair is made inside this frozen version.
