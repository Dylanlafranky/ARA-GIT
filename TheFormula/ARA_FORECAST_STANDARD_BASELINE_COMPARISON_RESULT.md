# Forecast standard-baseline comparison (strict causal)

Date: 3 June 2026

This is the correction to the earlier comparison note. It is an actual local benchmark run against stronger proxy baselines, not only a source audit.

Important fence: this still does **not** use archived operational forecast submissions from SWPC, IRI/NMME, Sea Ice Outlook, FluSight, or clinical task leaderboards. It compares ARA to strong local baselines on the same observed series.

## Baselines

- `persistence`: predict the current value.
- `seasonal_naive`: predict the previous same phase/period value.
- `harmonic_clock`: train-only sine/cosine cycle clock plus trend.
- `lag_harmonic_ridge`: causal lags plus cycle clock.
- `home_ar`: repo's causal lag readout from `ara_framework.run_forecast`.
- `home_plus_ara`: headline ARA features plus causal lags.

## Summary by horizon

| system | h | ARA corr | best non-ARA corr | corr lift | ARA MAE | best non-ARA MAE | MAE delta | verdict |
|---|---:|---:|---|---:|---:|---|---:|---|
| solar_sunspots_self | 12 | +0.873 | lag_harmonic_ridge +0.875 | -0.002 | 26.9 | lag_harmonic_ridge 26.5 | 0.473 | baseline corr win |
| solar_sunspots_self | 24 | +0.788 | lag_harmonic_ridge +0.804 | -0.016 | 34 | lag_harmonic_ridge 33.4 | 0.621 | baseline corr win |
| solar_sunspots_self | 60 | +0.756 | lag_harmonic_ridge +0.784 | -0.028 | 36.6 | home_ar 37 | -0.408 | baseline corr win; ARA MAE win |
| solar_sunspots_self | 132 | +0.689 | lag_harmonic_ridge +0.700 | -0.011 | 42.4 | lag_harmonic_ridge 42.3 | 0.17 | baseline corr win |
| qbo_30mb_self | 3 | +0.767 | home_ar +0.777 | -0.010 | 1.88 | persistence 1.84 | 0.0398 | baseline corr win |
| qbo_30mb_self | 6 | +0.531 | home_ar +0.524 | +0.008 | 3.11 | persistence 3.26 | -0.144 | ARA corr win; ARA MAE win |
| qbo_30mb_self | 12 | +0.545 | home_ar +0.563 | -0.019 | 3.8 | seasonal_naive 3.28 | 0.518 | baseline corr win |
| qbo_30mb_self | 18 | +0.267 | lag_harmonic_ridge +0.318 | -0.051 | 2.96 | home_ar 2.77 | 0.19 | baseline corr win |
| qbo_30mb_self | 24 | +0.369 | persistence +0.497 | -0.128 | 2.65 | persistence 2.16 | 0.485 | baseline corr win |
| enso_nino34_self | 3 | +0.826 | home_ar +0.824 | +0.002 | 0.398 | home_ar 0.399 | -0.000518 | ARA corr win; ARA MAE win |
| enso_nino34_self | 6 | +0.526 | home_ar +0.513 | +0.013 | 0.58 | home_ar 0.594 | -0.0142 | ARA corr win; ARA MAE win |
| enso_nino34_self | 12 | +0.271 | home_ar +0.200 | +0.071 | 0.696 | home_ar 0.698 | -0.00185 | ARA corr win; ARA MAE win |
| enso_nino34_self | 18 | +0.134 | home_ar +0.201 | -0.067 | 0.738 | home_ar 0.704 | 0.0339 | baseline corr win |
| enso_nino34_self | 24 | +0.262 | home_ar +0.352 | -0.090 | 0.661 | home_ar 0.615 | 0.0458 | baseline corr win |
| enso_nino34_with_soi_wwv | 3 | +0.829 | home_ar +0.824 | +0.005 | 0.392 | home_ar 0.399 | -0.0071 | ARA corr win; ARA MAE win |
| enso_nino34_with_soi_wwv | 6 | +0.500 | home_ar +0.513 | -0.013 | 0.608 | home_ar 0.594 | 0.0142 | baseline corr win |
| enso_nino34_with_soi_wwv | 12 | +0.248 | home_ar +0.200 | +0.048 | 0.697 | home_ar 0.698 | -0.000803 | ARA corr win; ARA MAE win |
| enso_nino34_with_soi_wwv | 18 | +0.149 | home_ar +0.201 | -0.052 | 0.728 | home_ar 0.704 | 0.024 | baseline corr win |
| enso_nino34_with_soi_wwv | 24 | +0.216 | home_ar +0.352 | -0.136 | 0.705 | home_ar 0.615 | 0.0894 | baseline corr win |
| retail_holiday_cycle | 1 | +0.500 | seasonal_naive +0.824 | -0.325 | 0.0457 | seasonal_naive 0.0234 | 0.0223 | baseline corr win |
| retail_holiday_cycle | 2 | +0.449 | seasonal_naive +0.824 | -0.376 | 0.0456 | seasonal_naive 0.0236 | 0.022 | baseline corr win |
| retail_holiday_cycle | 3 | +0.233 | seasonal_naive +0.823 | -0.590 | 0.0545 | seasonal_naive 0.0237 | 0.0308 | baseline corr win |
| retail_holiday_cycle | 6 | +0.816 | home_ar +0.821 | -0.005 | 0.0269 | seasonal_naive 0.024 | 0.00285 | baseline corr win |
| retail_holiday_cycle | 12 | +0.867 | lag_harmonic_ridge +0.868 | -0.001 | 0.0258 | persistence 0.0245 | 0.00129 | baseline corr win |
| arctic_sea_ice_monthly | 1 | +0.993 | lag_harmonic_ridge +0.995 | -0.002 | 0.316 | seasonal_naive 0.331 | -0.0149 | baseline corr win; ARA MAE win |
| arctic_sea_ice_monthly | 2 | +0.987 | lag_harmonic_ridge +0.993 | -0.006 | 0.498 | seasonal_naive 0.332 | 0.166 | baseline corr win |
| arctic_sea_ice_monthly | 3 | +0.989 | seasonal_naive +0.992 | -0.003 | 0.509 | seasonal_naive 0.333 | 0.175 | baseline corr win |
| arctic_sea_ice_monthly | 6 | +0.992 | lag_harmonic_ridge +0.993 | -0.000 | 0.365 | seasonal_naive 0.33 | 0.0352 | baseline corr win |
| arctic_sea_ice_monthly | 12 | +0.992 | home_ar +0.993 | -0.001 | 0.551 | persistence 0.327 | 0.224 | baseline corr win |
| flu_ilinet_weekly | 2 | +0.911 | home_ar +0.930 | -0.018 | 0.38 | home_ar 0.342 | 0.0377 | baseline corr win |
| flu_ilinet_weekly | 4 | +0.805 | home_ar +0.807 | -0.002 | 0.64 | home_ar 0.615 | 0.025 | baseline corr win |
| flu_ilinet_weekly | 8 | +0.587 | harmonic_clock +0.609 | -0.021 | 0.968 | harmonic_clock 0.839 | 0.128 | baseline corr win |
| flu_ilinet_weekly | 13 | +0.431 | harmonic_clock +0.603 | -0.172 | 1.27 | harmonic_clock 0.853 | 0.412 | baseline corr win |
| flu_ilinet_weekly | 26 | +0.405 | harmonic_clock +0.580 | -0.175 | 1.23 | lag_harmonic_ridge 0.87 | 0.356 | baseline corr win |

ARA `home_plus_ara` beat the best local non-ARA baseline on correlation at **6/34** horizons.
ARA `home_plus_ara` beat the best local non-ARA baseline on MAE at **8/34** horizons.

## Fetch/load status

- `retail_holiday_cycle`: loaded, n=401
- `arctic_sea_ice_monthly`: loaded, n=573
- `flu_ilinet_weekly`: loaded, n=711

## Read

- If `home_plus_ara` beats persistence but loses to `home_ar` or `lag_harmonic_ridge`, the result is a persistence/lag-memory win, not an ARA-over-standard win.
- If it beats `seasonal_naive`, that matters for annual systems where persistence inversion can otherwise exaggerate the apparent difficulty.
- If it beats `lag_harmonic_ridge`, that is the cleanest local evidence that ARA features add signal beyond ordinary memory plus a cycle clock.
- Dengue is intentionally excluded from this core pass because it was an incomplete side run and needs external drivers before it is a fair forecast claim.

## Operational archive status

Still pending, not passed here:

- Solar: archived SWPC/panel hindcasts for smoothed sunspot number and F10.7.
- ENSO: IRI/NMME/CFSv2 hindcast/real-time forecast archives with same lead/season/class metrics.
- Sea ice: Sea Ice Outlook September extent submissions/baselines.
- Flu: FluSight WIS/relative-WIS targets and forecast hub submissions.
- Retail: X-13/ARIMA/ETS comparison on raw and seasonally adjusted sales.
- CGM/ECG: OhioT1DM/PhysioNet task metrics with subject-level splits and clinical/event scores.

## Input requirements and cost comparison

| system | ARA inputs | standard method | standard input count | standard compute | cost / burden | status |
|---|---|---|---|---|---|---|
| Solar / sunspots | Monthly sunspot number only in this local stack. (1 observed monthly index.) | NOAA/SWPC solar-cycle progression: statistical/cycle-curve product plus expert/panel forecasting, not a deep ML model. | 2 core public indices plus historical cycle archive, cycle-fit machinery, uncertainty bands, and panel/expert maintenance. | Low direct compute; moderate operational burden because the product is maintained, validated, and expert-reviewed. | Public data/products are free to consume; producing the official product is an institutional/moderate staff burden rather than a large HPC burden. | Local proxy only. SWPC/panel archive benchmark still pending. |
| ENSO / NINO3.4 | NINO3.4 alone, or NINO3.4 + SOI + east/west WWV feeder series. (1 index for self-run, 4 observed indices for feeder-run.) | IRI/CPC plume and NMME/CFSv2-style seasonal forecasting: coupled dynamical ensembles plus statistical models; some ML exists but is not the core operational baseline. | Hundreds to millions of gridded state variables depending on model: ocean/atmosphere/land fields, multiple ensemble members, and many variables at daily/6-hourly/monthly cadence. | High. Coupled climate ensembles and data assimilation require institutional HPC; statistical plume members are cheaper. | Public forecast products are free to view; producing NMME/CFSv2-class forecasts is high-cost institutional modelling/HPC. | Local proxy only. IRI/NMME/CFSv2 hindcast archive comparison still pending. |
| QBO 30mb | Monthly QBO 30mb wind index only in the self-forecast stack. (1 observed monthly index.) | Seasonal/dynamical atmospheric models plus oscillator/statistical baselines; not usually a single public ML leaderboard. | Many pressure levels and global atmospheric state fields if using seasonal models; 1 index if using a simple oscillator baseline. | Low for oscillator/statistical baselines; moderate-high for seasonal Earth-system models. | Public index data are free; operational dynamical model production is institutional/moderate-high. | Local proxy only. Published/operational QBO hindcast comparison still pending. |
| Arctic sea ice | Monthly Arctic sea-ice extent only. (1 observed monthly index.) | Sea Ice Outlook style ensemble of dynamical, statistical, heuristic, and some ML methods. | 1 index for simple statistical methods; gridded satellite concentration/extent plus ocean-atmosphere-ice fields for dynamical/ML systems. | Low for extent trend/statistical models; moderate-high for coupled sea-ice/ocean/atmosphere models; ML training can be moderate-high but inference cheap. | Public data are free; operational/dynamical modelling cost is moderate-high and multi-team. | Local proxy only. Sea Ice Outlook September-submission comparison still pending. |
| Influenza / ILINet | National weekly ILINet/WILI series only. (1 observed weekly national surveillance series.) | CDC FluSight forecast-hub ensemble of many submitted statistical, mechanistic, ensemble, and ML models. | At minimum weekly target by jurisdiction; many teams add ED, hospitalization, lab, mobility, weather, demographics, or mechanistic state variables. | Low for ARIMA/trend models; moderate for mechanistic and ensemble systems; some submitted ML/deep models have higher training cost. | Public surveillance data are free; production model cost is moderate, with forecast-hub maintenance and WIS/relative-WIS scoring. | Local proxy only. FluSight forecast-hub WIS/relative-WIS benchmark still pending. |
| Retail holiday cycle | FRED RSXFSN not-seasonally-adjusted retail sales transformed into a causal trailing-12-month cycle index. (1 monthly retail series after local cycle transform.) | X-13ARIMA-SEATS / ARIMA / ETS style statistical seasonal adjustment and demand forecasting; business systems often add ML/covariates. | 1 official series for X-13-style adjustment; tens to thousands of product/location/promo/covariate fields in business demand forecasting. | Low for official X-13/ARIMA on one series; moderate-high for SKU/store-scale ML demand systems. | Public macro data are free; business-grade demand forecasts can be moderate-high depending on covariate systems. | Local proxy only. Full X-13/ARIMA/ETS raw-sales comparison still pending. |
| CGM glucose | CGM series only in the current self-forecast. (1 glucose time series in the self-run.) | Subject-specific physiological/statistical/ML glucose prediction; clinical products use validated medical workflows. | Often 4-8 core streams: CGM, insulin, carbs/meals, activity, sleep/stress/illness context, demographics, and device state. | Low-moderate for per-subject statistical models; moderate for ML; high cost comes from clinical validation, safety, and regulatory process. | Benchmark data may require agreements; clinical/pump-grade validation is high cost and regulatory/medical, not just compute. | Not a clinical benchmark. OhioT1DM/D1namo/Tidepool-style driver benchmark pending. |
| Heart / ECG | ECG/RR and optional morphology features in prior local tests. (1 ECG/RR stream in the simplest run; optional morphology features if enabled.) | Signal-processing plus ML/deep-learning classification/forecasting on PhysioNet-style patient splits; clinical standard is validation-heavy. | 1-12 ECG leads sampled at high frequency, beat annotations, patient splits, labels, and often morphology/RR features. | Low for classic signal processing and AR baselines; moderate for CNN/RNN/transformer training; inference is usually cheap. | Public data are often free; clinical-grade validation is high cost because it needs patient-level task design and safety metrics. | Research signal only. PhysioNet task benchmark pending. |

