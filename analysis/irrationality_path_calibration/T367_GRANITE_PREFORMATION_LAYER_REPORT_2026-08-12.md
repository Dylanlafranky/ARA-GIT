# T367 - granite pre-formation layer test

**Date:** 12 August 2026  
**Frozen verdict:** **NOT SUPPORTED UNDER THE FROZEN T367 GATES**

## Answer first

T367 asked whether recorded acoustic child relations become more organised
while still open before an isolated acoustic-parent burst forms. Development
specimens froze the parent-burst rule at Q97.5 with 8
s isolation. Holdout Wgn23-Wgn26 supplied 59
events.

The run stopped at the development-freeze boundary: every proposed organisation
feature moved in the opposite direction or was neutral, so all five received
zero frozen weight. Consequently the composite score, its holdout interval,
warning rate and AUROC are undefined; their downstream gates are not ordinary
negative estimates.

This is a valid rejection of the specific tightening-layer rule. It is not a
claim that the archive contained no structure. Descriptively, the large-burst
windows were generally **less coherent and less concentrated** than matched
quiet windows. That suggests mobilisation/disordering before burst formation,
or an unsuitable event definition, rather than the proposed progressive
narrowing.

## Development early-stop audit

| feature | source | development_event_minus_quiet_median | centre | iqr | active_weight |
| --- | --- | --- | --- | --- | --- |
| two_minus_x_R | x_R | -0.0241 | 0.5566 | 0.6715 | False |
| concentration | concentration | -0.0343 | 0.8387 | 0.1933 | False |
| coherence | coherence | -0.0494 | 0.8824 | 0.2742 | False |
| open_determined | open_determined | 0.0000 | 0.0000 | 0.0000 | False |
| positive_narrowing | narrowing | 0.0000 | 0.0000 | 0.0050 | False |

## Frozen gates

| gate | name | pass | detail |
| --- | --- | --- | --- |
| 1 | source and causality QA | True | All features trailing; specimen split fixed before scoring; source hashes recorded. |
| 2 | holdout event coverage | True | 59 events total; minimum 2 per specimen. |
| 3 | pre-onset organisation | False | not scored: development early-stop assigned zero primary feature weights |
| 4 | temporal direction | False | not scored: development early-stop assigned zero primary feature weights |
| 5 | child precedence | False | not scored: development early-stop assigned zero primary feature weights |
| 6 | not merely released waves | False | not scored: development early-stop assigned zero primary feature weights |
| 7 | relation specificity | False | not scored: development early-stop assigned zero primary feature weights |
| 8 | label specificity | False | not scored: development early-stop assigned zero primary feature weights |
| 9 | baseline value | False | not scored: development early-stop assigned zero primary feature weights |
| 10 | false-warning boundary | False | not scored: development early-stop assigned zero primary feature weights |

## Holdout specimens

| record | events | quiet | ara_auroc | exposure_auroc | count_auroc |
| --- | --- | --- | --- | --- | --- |
| Wgn23 | 2 | 2 |  | 0.5000 | 0.2500 |
| Wgn24 | 16 | 16 |  | 0.7734 | 0.7852 |
| Wgn25 | 3 | 3 |  | 0.6667 | 0.6667 |
| Wgn26 | 38 | 38 |  | 0.8934 | 0.8850 |

## Interpretation boundary

A positive pre-onset result supports measurable organisation of recorded AE
children before an acoustic parent burst. It does not prove an irrational
substance, reveal sub-threshold continuous waves, or establish a unique
mechanism. Layers appearing only after onset are consequences of release, not
pre-formation evidence.
