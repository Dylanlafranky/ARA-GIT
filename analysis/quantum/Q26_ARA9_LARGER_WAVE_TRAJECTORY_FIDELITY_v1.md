# Q26 ARA^9 larger-wave trajectory fidelity note

**Date:** 26 July 2026  
**Purpose:** prevent either a successful amplitude result or the failed orientation result from overwriting the
other.

## Frozen result

Q26 returned `SUPPORTED — 13/14 SCORED GATES`.

The complete connected ARA^9 closure:

- fell with wait time at median Spearman `-0.9364`;
- ended in the frozen trough on `25/28` primary trajectories;
- completed crest-to-trough movement on `25/28`;
- crossed the ridge within one sample on `21/22` eligible trajectories;
- crossed the trough within one sample on `25/28` eligible trajectories;
- beat persistence and elementwise linear in every primary trajectory;
- required the true time order to obtain the observed accuracy.

## Failed component

The frozen angular predictor did not beat its no-rotation ablation:

- ARA phase MAE: `1.3819 rad`;
- no-rotation phase MAE: `1.2388 rad`;
- stable determinant-orientation flips: `1/28`.

The supported result is therefore a larger-wave **amplitude contraction**, not a demonstrated full orientation
reversal.

## Calibration boundary

ARA cut MAE was `0.08502`, while the no-rotation contraction gave `0.08632`. The difference is small and the
cluster-bootstrap probability of ARA winning was only `0.6344`.

The strongest new information is:

1. a complete ARA^9 relation can be followed as one trajectory object;
2. its closure magnitude moves predictably from crest through handover toward trough;
3. the Q25 static missing-cut failure should not be treated as evidence against that larger envelope;
4. the extra directional walk has not yet been recovered.

## Provenance boundary

Dylan stated the crest-to-trough larger-wave interpretation before the Q26 target matrices were downloaded or
opened. However:

- the dataset is from the same published experiment family used earlier in the quantum arc;
- general faster decoherence at higher temperature was known from the publication;
- Q26 is a staged partially blind trajectory test, not a clean outside-domain prediction;
- it must not be promoted as an A-tier provenance hit.

## Controlling interpretation

Q26 supports:

\[
\text{local ARA}^{9}\text{ crest}
\rightarrow
\text{larger-wave handover}
\rightarrow
\text{later ARA}^{9}\text{ trough}.
\]

Q26 does not support:

\[
\text{local ARA}^{9}\text{ orientation}
\rightarrow
\text{opposite later orientation}.
\]

Report:
`analysis/quantum/Q26_ARA9_LARGER_WAVE_TRAJECTORY_REPORT_2026-07-26.md`.

