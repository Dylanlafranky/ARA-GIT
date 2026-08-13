# T349 independent validation

**Verdict:** PASS — 36/36 checks

The validator does not import the run script. It independently recomputes headline accuracies, intervention summaries, every fixed-constant score, and all five coordinates from 15 complete raw example trajectories.

| Check | Result | Detail |
|---|---|---|
| protocol hash | PASS | 4F6DF8E7AA0F2726EF3952ED791D3246C6588D2EE0C70F7AEE763D10F6D8075E |
| claim hash | PASS | 3137E226C627F6C6657327D95CC00B4215389D3EC1D2EDDE5B68B0279ADF8CD8 |
| metric row count | PASS | rows=15120 |
| natural key unique | PASS | duplicates=0 |
| coordinate ranges | PASS | xL/xC/xP/xR all in [0,2] |
| core counts | PASS | (3024, 1656) |
| headline radial accuracy | PASS | 1.000000000000 |
| headline history accuracy | PASS | 0.956521739130 |
| radial_inverted x_l intervention | PASS | recomputed=1.25020082802 |
| radial_inverted x_c intervention | PASS | recomputed=0 |
| radial_inverted x_p intervention | PASS | recomputed=0 |
| radial_inverted x_r intervention | PASS | recomputed=0 |
| radial_inverted mean_rho intervention | PASS | recomputed=0 |
| phase_reflected x_l intervention | PASS | recomputed=0 |
| phase_reflected x_c intervention | PASS | recomputed=2 |
| phase_reflected x_p intervention | PASS | recomputed=0 |
| phase_reflected x_r intervention | PASS | recomputed=0 |
| phase_reflected mean_rho intervention | PASS | recomputed=0 |
| shuffled x_l intervention | PASS | recomputed=0 |
| shuffled x_c intervention | PASS | recomputed=0.965348111602 |
| shuffled x_p intervention | PASS | recomputed=0 |
| shuffled x_r intervention | PASS | recomputed=1.94528822312 |
| shuffled mean_rho intervention | PASS | recomputed=0.985870975738 |
| endpoint_shuffled x_l intervention | PASS | recomputed=0 |
| endpoint_shuffled x_c intervention | PASS | recomputed=0.968414878273 |
| endpoint_shuffled x_p intervention | PASS | recomputed=0 |
| endpoint_shuffled x_r intervention | PASS | recomputed=1.94390656141 |
| endpoint_shuffled mean_rho intervention | PASS | recomputed=0.985763737041 |
| constant plastic | PASS | mean_log_error=0.668800425677 |
| constant sqrt2 | PASS | mean_log_error=0.60342640972 |
| constant phi | PASS | mean_log_error=0.46878817494 |
| constant octave | PASS | mean_log_error=0.352284273147 |
| constant e | PASS | mean_log_error=0.283333333333 |
| raw-example formula reconstruction | PASS | groups=15 failures=0 |
| figure dimensions | PASS | size=(2400, 1500) |
| all primary gates passed | PASS | primary=7/7 constant=False |
