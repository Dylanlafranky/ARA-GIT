# T326 report — independent plant Phi circle-train replication

**Date:** 2 August 2026  
**Frozen protocol:** `T326_PHI_CIRCLE_TRAIN_INDEPENDENT_PLANTS_PROTOCOL_v1_FROZEN.md`  
**Protocol SHA-256:** `A049DEBBAB20DE75422A94D29ED932FCEAA9E984DFC58E9879937B6527296D18`  
**Verdict:** **NOT REPLICATED**

## Answer first

The independent Landrein Arabidopsis archive does **not** reproduce the exact
T325 scale split as a complete frozen result. Its lowest local-child fixed
loss is **one_over_e** (22.563°),
and its lowest ordered parent-carrier fixed loss is **fibonacci_8_21**
(84.357°).

For the declared close comparison, child `Phi - 3/8` is
`0.002735` ARA and
parent `Phi - 3/8` is
`0.005722` ARA.
Negative means Phi is better; positive means `3/8` is better.

Real downstream/developmental order versus within-plant shuffling gives
`p=0.198080` for the frozen Phi parent carrier.
The result is therefore retained even if its direction differs from T325: no
candidate or gate was changed after the protocol was frozen.

## Primary aggregate ranking

| Candidate | Child median | Child rank | Parent median | Parent rank |
|---|---:|---:|---:|---:|
| persistence | 127.250° | 9 | 91.000° | 9 |
| one_third | 28.500° | 6 | 88.000° | 5 |
| one_over_e | 22.563° | 1 | 85.669° | 3 |
| three_eighths | 25.000° | 4 | 85.000° | 2 |
| fibonacci_8_21 | 23.571° | 2 | 84.357° | 1 |
| phi | 23.742° | 3 | 86.746° | 4 |
| two_fifths | 26.000° | 5 | 91.000° | 8 |
| silver_conjugate | 28.617° | 7 | 88.435° | 7 |
| ridge | 52.750° | 8 | 88.000° | 6 |


## Cohort results

| Cohort | Plants | Child winner | Child loss | Parent winner | Parent loss |
|---|---:|---|---:|---|---:|
| Col0_JC-JL | 26 | three_eighths | 17.000° | three_eighths | 65.750° |
| Col0_JL | 34 | phi | 15.492° | fibonacci_8_21 | 80.036° |
| WS4_JC-JL | 25 | one_third | 50.000° | three_eighths | 82.000° |
| WS4_JL | 15 | two_fifths | 15.000° | silver_conjugate | 74.883° |
| bot1-7_JC-JL | 40 | one_third | 60.750° | ridge | 83.250° |
| bot1-7_JL | 20 | one_over_e | 16.500° | silver_conjugate | 82.409° |
| clasp1_JC-JL | 17 | two_fifths | 12.000° | phi | 55.876° |
| clasp1_JL | 19 | one_third | 25.000° | one_over_e | 88.605° |

## Ordered controls

- Phi true-order parent loss: `0.481923` ARA.
- Shuffled-order median: `0.490311` ARA.
- Shuffle lower-tail p: `0.198080`.
- Adjacent compensation ratio: `0.716925`.
- Within-order compensation p: `0.035096`.
- Broken-lineage compensation p: `0.447855`.
- Best five-lag return candidate: `one_over_e`.

## Cyanella resolution control

The Cyanella archive supplies ordered lineages, but angles are measured in
`22.5°` bins. The exact Phi-versus-`3/8` separation is only `2.507764°`.
Its numerical rankings are recorded in the machine outputs, but its formal
verdict is **INCONCLUSIVE — RESOLUTION**. It cannot decide the close constant
question.

## Source reconstruction and provenance

The Landrein primary uses the authors' published calculated divergence files.
Where raw angular positions exist, both subtraction directions were checked
against those published files. The median best reconstruction MAE is
`0.000000°` across `75` plant-file
checks. These checks verify extraction only and are not extra evidence.

The complete source hashes, event rows, plant scores, candidate summaries,
null results and independent validation are stored beside this report.

## Scientific boundary

This is an independent-source test of one frozen crosswalk. It neither proves
nor disproves the complete ARA framework. The result distinguishes the
specific T325 scale-split claim from the broader facts that phyllotactic
angles are ordered, approximately golden, noisy, genotype-dependent and
sometimes rearranged during stem development.
