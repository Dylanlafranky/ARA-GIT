# Data sources

All public, all observational. Nothing in this analysis was tuned on the
holdout; every fit is leakage-guarded (parameters from training/past data only).

## Warm Water Volume (the driver-below / fine sand)
- Source: NOAA/PMEL GTMBA Project Office — https://www.pmel.noaa.gov/tao/wwv/data/
- Files: `wwv.dat` (full basin), `wwv_west.dat` (warm pool, 120°E–155°W),
  `wwv_east.dat` (eastern, 155°W–80°W). Monthly, 1980–present.
- Definition: volume of water above the 20 °C isotherm, 5°N–5°S, 120°E–80°W;
  monthly anomalies relative to a 1980–2002 base (Meinen & McPhaden 2000).
- The scripts auto-download these. Anomaly column used, scaled by 1e14 m³.
- Cite PMEL/GTMBA if used in publication (contact: Michael.J.McPhaden@noaa.gov).

## NINO 3.4 (the apex grain)
- Monthly sea-surface-temperature anomaly for the NINO 3.4 region
  (5°N–5°S, 170°W–120°W). Long record (1870–present) used for the spectrum;
  the 1980+ overlap with WWV used for forecasting.
- Provide as a CSV with rows `YYYY-MM-DD, value` and missing = -99.99
  (e.g. from NOAA PSL: https://psl.noaa.gov/data/timeseries/month/).
- File expected: `nino34_long_anom.csv`.

## Method notes
- Train/holdout split: pre-2017 train, 2017+ holdout (fixed split), plus
  walk-forward refit-on-past from 2008 (the robustness test).
- Decisive metric: skill vs climatology (1 − MSE_model / MSE_climatology) on
  held-out forecasts. Skill vs persistence reported but treated as the weak
  baseline.
- Standardisation of the warm/cool grains uses train/past statistics only.
