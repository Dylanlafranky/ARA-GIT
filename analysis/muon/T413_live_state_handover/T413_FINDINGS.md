# T413 — Live-state muonium handover

## Outcome

**Overall frozen verdict: NOT SUPPORTED for the proposed two-coordinate temporal Di-ARA predictor.**

The direct RF-on/RF-off ARA relation contains forecastable state, but the proposed second temporal cut—its strictly causal first difference—does not add reliable holdout information beyond the first coordinate alone.

This is a narrow negative calibration. It does not reject ARA generally, and it is not a test of individual-muon neutrino timing.

## Exact ARA cut tested

For matched RF-on and RF-off detector rates,

\[
x_d(t)=\frac{2R_{\mathrm{on},d}(t)}{R_{\mathrm{on},d}(t)+R_{\mathrm{off},d}(t)},
\qquad r_d(t)=x_d(t)-1.
\]

The equal-rate ridge is therefore `x = 1`, or `r = 0` after centering. The first causal detector-space mode is `A(t)`. Its backward difference is the proposed perpendicular child coordinate,

\[
B(t)=A(t)-A(t-\Delta t).
\]

A frozen affine 2×2 transition forecasts the future state `[A,B]` recursively. No future value is used to construct either coordinate.

## Frozen data split

- Development: 13 runs at 300 K, lower-field branch.
- Validation: 13 interleaved runs at 300 K, lower-field branch.
- Untouched holdout: 20 runs at 202 K, high-field branch.
- Development window: 0.25–2.5 microseconds.
- Future score window: 2.5–6.0 microseconds.
- Raw source: 46 public ISIS EMU Nexus runs, about 79.9 MB total.

## Holdout result

| Predictor | Median future RMSE | Full Di-ARA win share |
|---|---:|---:|
| Full temporal Di-ARA | 0.046842 | — |
| One-coordinate AR(1) | 0.046457 | 35% |
| No cross-coupling | 0.046647 | 45% |
| Persistence | 0.074772 | 100% |
| Damped harmonic | 0.057430 | 100% |
| Wrong orientation | 0.046866 | 60% |
| Broken time order | 0.048019 | 60% |

The median full-model advantage over the best simple comparator was negative. Its bootstrap 95% interval was approximately `[-0.000699, +0.000043]`, crossing zero. The predeclared primary relational gate therefore failed.

The full model did beat the damped-harmonic comparator by 18.6%, but AR(1) was the stronger comparator. That isolated pass cannot override the primary failure.

## ARA interpretation

What survived is the direct relation cut: RF-on versus RF-off contains a causal, forecastable live state. What did not survive is treating the first difference of that same state as an independently informative Di-ARA partner.

In ARA language, the attempted second axis was probably not an independently observed child. It was a mathematical derivative of the first cut, so it carried largely the same information. The next strict test should use a genuinely separate simultaneous observable—such as an independently recorded spin quadrature or electron-sensitive channel—then test whether the two observed coordinates close a stronger Di-ARA relation.

## Scope boundary

- This is an ensemble muonium-state test.
- It does not locate a neutrino-release instant for an individual muon.
- Zero crossings of the weak first relation mode are not, by themselves, physical handovers.
- The first mode retained only about 12.1% of development-window variance on the holdout branch, limiting physical interpretation.

## Integrity and reproduction

- Frozen protocol: `T413_FROZEN_PROTOCOL.md`
- Frozen protocol SHA-256: `5DF69B775E9F6608A776950665841B4EE48B2DD791EE90640B09F58778ACA693`
- Frozen implementation SHA-256: `3465B3FA918AF5ED15D8BC53E10A99B00A759F4A3000AD7DD56507A0EAEA06F7`
- Pre-holdout result SHA-256: `51A61EEDF14C636A100B74C333ED2D29DD9A589743FDA600FCBF752EB8422334`
- Independent validator status: passed.
- Maximum independently recomputed primary-RMSE error: exactly 0.
- The validator confirmed that no holdout split appeared in the pre-holdout result.

Run from this directory with the repository Python environment and local `pyhdf` dependency available:

```powershell
python t413_live_state_handover.py --splits development,validation,holdout --suffix FULL
python validate_t413_live_state_handover.py
python build_t413_report_artifact.py
```

The public experiment landing page is <https://data.isis.stfc.ac.uk/doi/STUDY/103197258>. Exact selected datafile IDs, fields, temperatures, expected filenames, and byte sizes are frozen in `source/T413_SOURCE_MANIFEST.csv`; the raw Nexus files are intentionally not repository artifacts.

## Durable outputs

- `results/T413_LIVE_STATE_HANDOVER_REPORT.html` — portable visual report.
- `results/T413_REPORT_ARTIFACT.json` — canonical report artifact.
- `results/T413_REPORT_DATA.sqlite` — exact report-widget tables and runnable provenance queries.
- `results/T413_FULL_RESULTS.json` — aggregate and per-run model details.
- `results/T413_FULL_RUN_METRICS.csv` — auditable per-run scores.
- `results/T413_FULL_PREDICTIONS.csv` — saved future predictions.
- `results/T413_VALIDATION.json` — independent validation record.

