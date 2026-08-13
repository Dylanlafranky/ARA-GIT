# T355 independent validation

**Status:** **PASS** (30/30 checks)

The saved child readings independently reproduce the frozen unweighted parent midpoint. The non-mirror audit, endpoint recovery, localization, observer-width invariance, single-child comparison and wrong-pair specificity all recompute from the exported tables.

## Checks

| check | result | detail |
|---|---|---|
| protocol hash | PASS | `F6870F39C73D41D3EA13B314FF1C60BAFD7EB2395FEF5272FFAF4BCBFE1EA3BE` |
| audit rows | PASS | `144` |
| child rows | PASS | `1152` |
| pair rows | PASS | `576` |
| identity rows | PASS | `144` |
| 72 unique pair identities | PASS | `72` |
| two construction conditions | PASS | `['asymmetric', 'clean']` |
| two directional children | PASS | `{'irrational_to_rational': 576, 'rational_to_irrational': 576}` |
| four observation windows | PASS | `[128, 256, 384, 512]` |
| all child predictions finite | PASS | `finite=1.000000` |
| parent midpoint formula | PASS | `max delta=9.095e-13` |
| clean paths are mirror control | PASS | `mix RMS=0.000000000000` |
| asymmetric profiles are non-mirrored | PASS | `mix RMS=0.051063103890` |
| asymmetric advances fail exact complement | PASS | `advance RMS=0.062261252229` |
| endpoint recovery | PASS | `minimum=1.100430269850; prediction rate=1.000000` |
| headline recompute clean | PASS | `{"paired": 1.4258886724708193, "range": 2.5104554617771555, "single": 335.2735210367788, "wrong": 302.2476832838746}` |
| paired localization gate clean | PASS | `paired median=1.425889` |
| window invariance gate clean | PASS | `range median=2.510455` |
| single-child control clean | PASS | `paired=1.425889; single=335.273521` |
| wrong-pair control clean | PASS | `paired=1.425889; wrong=302.247683` |
| headline recompute asymmetric | PASS | `{"paired": 6.67426726261084, "range": 2.938798484799122, "single": 389.4613788471742, "wrong": 290.91775158827625}` |
| paired localization gate asymmetric | PASS | `paired median=6.674267` |
| window invariance gate asymmetric | PASS | `range median=2.938798` |
| single-child control asymmetric | PASS | `paired=6.674267; single=389.461379` |
| wrong-pair control asymmetric | PASS | `paired=6.674267; wrong=290.917752` |
| all window medians below frozen threshold clean | PASS | `{"128": 2.3669920287802597, "256": 1.2123918092640906, "384": 1.2216461203236122, "512": 1.3385808147743319}` |
| all window medians below frozen threshold asymmetric | PASS | `{"128": 7.961453339300988, "256": 6.8906477612133585, "384": 6.44576793362819, "512": 6.3608538527516885}` |
| official gate count | PASS | `6/6` |
| official verdict | PASS | `SUPPORTED [SYNTHETIC RELATIONAL PARENT-RIDGE INSTRUMENT ONLY]` |
| figure exists | PASS | `F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_path_calibration\T355_IRRATIONALITY_RELATIONAL_PARENT_RIDGE_FIGURE.png` |

## Required caveat

The paired reconstruction is not algebraically defined from the true centre, but both children were generated around a supplied common seam. This is a valid synthetic instrument calibration, not independent physical evidence for a universal relational ridge.
