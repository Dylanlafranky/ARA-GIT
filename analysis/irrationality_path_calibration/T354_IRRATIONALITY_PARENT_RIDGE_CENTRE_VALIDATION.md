# T354 independent validation

**Status:** **PASS** (18/18 checks)

The frozen result is reproducible: the one-direction `x_P=1` midpoint does not localize the known centre and moves with observer width. The official verdict remains `RIDGE NOT RESOLVED`.

## Checks

| check | result | detail |
|---|---|---|
| protocol hash | PASS | `B4AA7EA73FD3C3916827269EA41393E59E31D0416A4B1CFCF9367834D5C7EDD5` |
| series row count | PASS | `864` |
| profile row count | PASS | `102816` |
| identity row count | PASS | `216` |
| four windows | PASS | `[128, 256, 384, 512]` |
| both directions | PASS | `{'irrational_to_rational': 432, 'rational_to_irrational': 432}` |
| matched modes | PASS | `{'ordered': 432, 'abrupt': 432}` |
| distributed referee centres | PASS | `n=54` |
| all predictions finite | PASS | `finite=1.000000` |
| identity summaries recompute | PASS | `rows=216` |
| headline irrational_to_rational ordered | PASS | `error=325.223103092816; range=166.328443176563` |
| headline irrational_to_rational abrupt | PASS | `error=107.032491628313; range=172.075403007448` |
| headline rational_to_irrational ordered | PASS | `error=320.327084788684; range=165.861179523501` |
| headline rational_to_irrational abrupt | PASS | `error=104.893665309804; range=173.070591597119` |
| R1 recompute | PASS | `minimum=1.409588698847` |
| official verdict | PASS | `RIDGE NOT RESOLVED; 1/6` |
| figure exists | PASS | `F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_path_calibration\T354_IRRATIONALITY_PARENT_RIDGE_CENTRE_FIGURE.png` |
| posthoc direction-pair calculation reproducible | PASS | `{"ordered": {"median_paired_abs_error": 1.4370634128745223, "p95_paired_abs_error": 5.787136810853269}, "abrupt": {"median_paired_abs_error": 1.133153572042147,` |

## Post-hoc observation - not a frozen T354 gate

The forward and reverse one-direction biases are almost exactly opposite. Averaging the two independently predicted directional centres gives a median absolute error below three states in both modes. This is hypothesis-generating only and requires a newly frozen direction-pair test.

- ordered paired median absolute error: `1.437063` states
- abrupt paired median absolute error: `1.133154` states
