# ENSO Five-Axis Neighbourhood Test

This tests the 31-sphere local environment idea on ENSO/NINO3.4:

- home sphere: NINO3.4
- measured contacts: SOI, WWV west, WWV east, combined WWV reservoir
- unmeasured contacts: recursive ARA terrain defaults
- contact lattice: 5 axes x 2 directions x 3 depths = 30 surrounding contacts
- readout: strict-causal ridge delta readout fit on the 1/phi training span

Important fence: this is a first ablation of the full surroundings, not a final operational ENSO forecast.

## Results

| h | best five-axis corr | best non-ARA corr | existing home+ARA corr | best five-axis MAE | best non-ARA MAE | existing home+ARA MAE | read |
|---:|---:|---:|---:|---:|---:|---:|---|
| 3 | home_plus_five_axis_depth2_summary +0.839 | home_ar +0.824 | +0.829 | five_axis_depth1_summary_no_home 0.375 | home_ar 0.399 | 0.392 | five corr win; five MAE win |
| 6 | home_plus_five_axis_depth2_summary +0.506 | home_ar +0.513 | +0.500 | home_plus_five_axis_depth2_summary 0.606 | home_ar 0.594 | 0.608 | baseline corr win |
| 12 | five_axis_depth1_full_no_home +0.152 | home_ar +0.200 | +0.248 | home_plus_five_axis_depth3_summary 0.695 | home_ar 0.698 | 0.697 | baseline corr win; five MAE win |
| 18 | five_axis_depth2_full_no_home +0.170 | home_ar +0.201 | +0.149 | three_axis_depth3_summary_no_home 0.700 | home_ar 0.704 | 0.728 | baseline corr win; five MAE win |
| 24 | home_plus_five_axis_depth2_summary +0.145 | home_ar +0.352 | +0.216 | five_axis_depth2_summary_no_home 0.706 | home_ar 0.615 | 0.705 | baseline corr win |

Best five-axis variant beat the best non-ARA correlation baseline at **1/5** horizons.
Best five-axis variant beat the best non-ARA MAE baseline at **3/5** horizons.
Existing `home_plus_ara` beat the best non-ARA correlation baseline at **2/5** horizons.

## Interpretation

- If five-axis no-home wins, the surroundings are carrying standalone geometry signal.
- If home-plus-five-axis wins, the surroundings are useful as calibration around home wave memory.
- If ordinary `home_ar` still wins, the current five-axis wiring is not yet adding enough over causal memory.
- If depth 2/3 helps over depth 1, the three-deep environment is earning its keep.

