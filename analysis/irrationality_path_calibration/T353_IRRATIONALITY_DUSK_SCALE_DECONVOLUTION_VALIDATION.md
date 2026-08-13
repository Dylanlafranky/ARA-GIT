# T353 independent validation

**Status:** **PASS — 20/20 checks passed**

The validator does not import the T353 run script. It rebuilds all band widths from saved profiles, independently reconstructs the matched deconvolution and smear fits, checks headline statistics, the protocol hash and the rendered figure.

| check | result | detail |
|---|---|---|
| protocol hash | PASS | 47E458700C35A0A994A6371C8E4387A5BF47E10859ED600203EE74908E9D6F68 |
| band count | PASS | 2304 |
| profile count | PASS | 76032 |
| identity count | PASS | 288 |
| two modes per window | PASS | ordered/abrupt |
| four windows per mode | PASS | 128/256/384/512 |
| x_R range | PASS | [0.0, 2.0] |
| band width stride | PASS | 32-state grain |
| band-width reconstruction | PASS | exact |
| identity numerical reconstruction | PASS | max error 3.553e-15 |
| positive-window reconstruction | PASS | exact |
| irrational_to_rational duration median | PASS | 56.000000 |
| irrational_to_rational duration Spearman | PASS | -0.034018229053 |
| irrational_to_rational absolute error median | PASS | 352.000000 |
| rational_to_irrational duration median | PASS | 24.000000 |
| rational_to_irrational duration Spearman | PASS | -0.016945439537 |
| rational_to_irrational absolute error median | PASS | 376.000000 |
| gate count | PASS | 2/6 |
| verdict | PASS | WINDOW SMEAR ONLY |
| figure readable | PASS | 2380x1700 |

## Boundary

This is artifact-level numerical validation. It does not independently regenerate the raw synthetic paths and does not change the synthetic-only evidence class.
