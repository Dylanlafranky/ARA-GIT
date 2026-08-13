# T366 - acoustic children before connection-heavy granite failure

**Date:** 12 August 2026  
**Frozen verdict:** **NOT SUPPORTED UNDER THE FROZEN T366 GATES**

## Answer first

The frozen test asked whether acoustic/vibration children form an ordered ARA
handover before the bulk-stress parent visibly releases. The primary Wgn23
holdout result was an event-associated acoustic warning.
Its lead was 0.5976 s when finite, with 31 earlier false bouts.
The bulk comparator did not produce an associated advance warning.

This result concerns the frozen ARA timing rule. The source paper independently
already reports accelerating AE rates and changing source mechanisms before
failure; those established observations are context, not an ARA discovery.

## Exact measurement

- **Connection child:** compression-type AE packets (`pol < -0.25`).
- **Movement child:** shear/tensile AE packets (`pol >= -0.25`).
- **Parent exposure:** recent summed `log(1 + adjusted amplitude)`.
- **Rungs:** 1, 2, 4, 8 and 16 s trailing windows.
- **Bulk comparator:** trailing normalized stress plus accumulation/release.
- **Event:** largest negative 10 Hz stress step in the final 20%.

No future sample enters any coordinate. A zero-event window remains undefined
on the mixing axis instead of being assigned a ridge.

## Record summary

| record | evidence_role | stress_samples | ae_events_total | ae_events_synchronized | failure_time_s | acoustic_associated | acoustic_lead_s | acoustic_false_bouts | acoustic_total_bouts | bulk_associated | bulk_lead_s | bulk_false_bouts | bulk_total_bouts | real_error_s | pseudo_median_error_s | pseudo_zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Wgn23 | primary holdout | 25399 | 16383 | 11621 | 5334.3994 | True | 0.5976 | 31 | 32 | False |  | 49 | 49 | 0.0000 | 0.0000 | 0.5430 |
| Wgn20 | disclosed development | 25140 | 13388 | 6070 | 4993.5400 | True | 0.0996 | 45 | 46 | True | 7.1718 | 63 | 65 | 0.0000 | 0.0000 | 0.6780 |

## Wgn23 frozen gates

| gate | name | pass | detail |
| --- | --- | --- | --- |
| 1 | source and causality QA | True | Four source hashes recorded; all features trailing; calibration ends before failure. |
| 2 | holdout acoustic forecast | True | Wgn23 10-second frozen acoustic horizon. |
| 3 | false-alarm boundary | False | Earlier Wgn23 acoustic bouts: 31. |
| 4 | child order | True | Grandchild half -> child half -> current full/failure. |
| 5 | bulk comparison | True | Acoustic warning must precede bulk stress warning or bulk must be silent. |
| 6 | marker specificity | False | real 0.000s vs pseudo median 0.000s. |
| 7 | control specificity | True | No broken-chronology control may match both lead and false-alarm burden. |
| 8 | development repeat | True | Wgn20 scored unchanged and cannot rescue Wgn23. |
| 9 | irrationality address | True | All finite Wgn23 rung addresses reported at the acoustic alarm. |

## Event-local acoustic landmarks

The following are the last upward landmark crossings found inside a broad
60-second diagnostic window. Because the child coordinate can leave and re-enter
`Ab`, they are not all members of the final alarm bout and must not be read as
one ordered cascade.

| rung | role | landmark | lead_s |
| --- | --- | --- | --- |
| -2 | grandchild | 0.5000 | 0.0000 |
| -2 | grandchild | 0.7500 | 11.3555 |
| -2 | grandchild | 1.0000 | 11.0566 |
| -1 | child | 0.5000 | 0.0000 |
| -1 | child | 0.7500 | 1.1953 |
| -1 | child | 1.0000 | 1.1953 |
| 0 | current | 0.5000 | 0.0000 |
| 0 | current | 0.7500 | 11.0566 |
| 0 | current | 1.0000 | 10.5586 |
| 1 | parent | 0.5000 | 10.6582 |
| 1 | parent | 0.7500 | 9.5625 |
| 1 | parent | 1.0000 | 4.4824 |
| 2 | grandparent | 0.5000 | 1.1953 |
| 2 | grandparent | 0.7500 | 5.3789 |
| 2 | grandparent | 1.0000 | 29.0859 |

The actual event-associated run, evaluated from the alarm backward through its
contiguous active state, was:

| grandchild_half_lead_s | child_half_lead_s | current_full_observed | current_full_or_failure_lead_s | ordered |
| --- | --- | --- | --- | --- |
| 0.7969 | 0.5976 | False | 0.0000 | True |

Thus the final bout did preserve grandchild -> child order, but the current rung
did not reach full closure before the macroscopic stress drop.

## Irrationality Di-ARA address at warning

| record | rung | role | alarm_index | xT_alarm | xM_alarm | h_alarm | quadrant | x_P | x_R | history_coherence_mean | history_coherence_peak |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Wgn23 | -2 | grandchild | 25092 | 1.4115 | 1.6713 | 1.2399 | Ab | 1.5969 | 0.8228 | 0.2256 | 0.8278 |
| Wgn23 | -1 | child | 25092 | 1.0146 | 1.4993 | 1.9431 | Ab | 1.5732 | 0.4689 | 0.2688 | 0.9421 |
| Wgn23 | 0 | current | 25092 | 1.4665 | 1.0644 | 0.2426 | Ab | 1.5405 | 0.4543 | 0.5890 | 0.9700 |
| Wgn23 | 1 | parent | 25092 | 1.3898 | 1.0776 | 0.3320 | Ab | 1.6506 | 0.4872 | 0.8886 | 0.9944 |
| Wgn23 | 2 | grandparent | 25092 | 1.3705 | 1.1415 | 0.5526 | Ab | 1.6711 | 0.2217 | 0.9823 | 0.9995 |

Only occupied quadrants are interpreted. The test does not require one fault
identity to use all four quadrants.

## Chronology controls

| record | control | associated | lead_s | earlier_false_bouts | total_bouts |
| --- | --- | --- | --- | --- | --- |
| Wgn23 | reversed_holdout | False |  | 32 | 35 |
| Wgn23 | joint_bin_permutation | False |  | 30 | 33 |
| Wgn23 | polarity_permutation | False |  | 37 | 38 |

## Sensitivity and simple baselines

| record | evidence_role | stress_samples | ae_events_total | ae_events_synchronized | failure_time_s | acoustic_associated | acoustic_lead_s | acoustic_false_bouts | acoustic_total_bouts | bulk_associated | bulk_lead_s | bulk_false_bouts | bulk_total_bouts | real_error_s | pseudo_median_error_s | pseudo_zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Wgn23 | raw-amplitude sensitivity | 25399 | 16383 | 11621 | 5334.3994 | False |  | 16 | 17 | False |  | 49 | 49 | 1.8924 | 4.1832 | 0.3120 |
| Wgn20 | raw-amplitude sensitivity | 25140 | 13388 | 6070 | 4993.5400 | True | 9.1640 | 39 | 41 | True | 7.1718 | 63 | 65 | 0.0000 | 0.0000 | 0.6270 |

| record | baseline | threshold | associated | lead_s | earlier_false_bouts | total_bouts |
| --- | --- | --- | --- | --- | --- | --- |
| Wgn20 | count_q95 | 5.0000 | False |  | 25 | 25 |
| Wgn20 | amplitude_q95 | 27.1451 | False |  | 30 | 30 |
| Wgn23 | count_q95 | 9.0000 | True | 4.9805 | 51 | 53 |
| Wgn23 | amplitude_q95 | 44.2230 | True | 2.7890 | 59 | 61 |

The raw-amplitude calculation is diagnostic only. It cannot replace the frozen
log-amplitude result.

## ARA interpretation

If the acoustic gate passes while bulk stress does not warn, the specific
supported statement is that smaller internal connection failures expose a
movement channel before the coarse connection-heavy parent releases. If it
fails, that does not erase the observed AE acceleration; it rejects this
particular half-ridge alarm and/or scale ordering as a reliable description of
that acceleration.

## Established-science crosswalk

The experimenters describe long-term damage accumulation, crack alignment and
localization, followed by shorter rupture-nucleation processes. They identify
compression, shear and tensile AE sources from first-motion polarities. T366's
connection/movement split is an ARA crosswalk onto those measured source types;
it is not a replacement for their mechanics or an assertion that every
compression event is ontologically a Space wave.

## Evidence boundary

This archive supplies detected AE events rather than the continuous 10 MHz
waveforms. T366 can test event-scale child ordering but cannot recover quiet
sub-threshold vibration or waveform phase. There are only two synchronized
stress/catalogue records here, and Wgn20 was already viewed coarsely. A positive
result therefore warrants a waveform-rich independent archive, not a field
earthquake-prediction claim.
