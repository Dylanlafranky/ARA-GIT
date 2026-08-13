# T352 independent validation

**Status:** **PASS — 30/30 checks passed**

This validator does not import the T352 run script. It independently rebuilds every event summary from the saved local-window coordinates, repeats the matched bootstrap calculations, checks the frozen protocol hash and verifies the rendered figure.

| check | result | detail |
|---|---|---|
| protocol hash | PASS | E6E3D4A6EA76996E99D02E378CB837E259DE5AB0E3A27946167CD4C513F99838 |
| window row count | PASS | 41328 |
| event row count | PASS | 1008 |
| three modes per identity | PASS | abrupt/ordered/shuffled |
| fixed window width | PASS | 512 states |
| fixed centre stride | PASS | 64 states |
| coordinate range x_P | PASS | [0.0, 2.0] |
| coordinate range x_R | PASS | [0.0, 2.0] |
| all regions present | PASS | ['handover', 'post', 'pre'] |
| event summary numerical reconstruction | PASS | max error 4.441e-16 |
| band width reconstruction | PASS | exact |
| irrational_to_rational excursion estimate | PASS | 1.15140462914 |
| irrational_to_rational excursion interval | PASS | [0.638498617591, 1.47462023414] |
| irrational_to_rational reclosure estimate | PASS | 0 |
| irrational_to_rational reclosure interval | PASS | [0, 0] |
| irrational_to_rational area estimate | PASS | 0.109191989742 |
| irrational_to_rational area interval | PASS | [-0.000958500133466, 0.22603880916] |
| irrational_to_rational rough estimate | PASS | 0.0179207369317 |
| irrational_to_rational rough interval | PASS | [0.00721678311759, 0.0299358293907] |
| rational_to_irrational excursion estimate | PASS | 1.15563402585 |
| rational_to_irrational excursion interval | PASS | [0.737367680839, 1.7882396438] |
| rational_to_irrational reclosure estimate | PASS | 1.74149973955e-18 |
| rational_to_irrational reclosure interval | PASS | [8.94466792301e-19, 9.71865274889e-16] |
| rational_to_irrational area estimate | PASS | -0.000434391285664 |
| rational_to_irrational area interval | PASS | [-0.00255962918355, 0.0377636199765] |
| rational_to_irrational rough estimate | PASS | 0.0174871462489 |
| rational_to_irrational rough interval | PASS | [0.00638475830961, 0.0269772213098] |
| gate count | PASS | 4/6 |
| verdict logic | PASS | MEASUREMENT DUSK ONLY |
| figure readable | PASS | 2380x1700 |

## Boundary

This is artifact-level numerical validation. It does not independently regenerate every raw synthetic path, and it does not change the synthetic-only evidence class.
