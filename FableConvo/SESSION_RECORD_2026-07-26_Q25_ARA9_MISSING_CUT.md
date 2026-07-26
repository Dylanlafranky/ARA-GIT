# Session record — Q25 ARA^9 missing-cut reconstruction

**Date:** 26 July 2026  
**Participants:** Dylan La Franchi and Codex/Sol

## Trigger

After Q24 identified the older ARA^9 object as the complete connected Bell relation, Codex proposed hiding one of
the nine relation cuts and predicting it from the other eight.

Dylan agreed, then added:

> “But I think this is also just the crest of a larger wave in connection space. We might find the whole shape
> flips and becomes a trough in the next ARA^9.”

This statement preceded opening the external numerical matrices. It was retained as a separate secondary
larger-wave probe so it could not alter the primary missing-cut verdict.

## Frozen test

Q25 calibrated one static sphere-closure rule on the already-open Q24 Bell matrices, then froze it before
downloading values from Zenodo `10.5281/zenodo.4604775`.

The external source contained:

- one fully mixed input density matrix;
- four outcome-conditioned Bell-state density matrices;
- four Bell-measurement operators.

Each of nine connected cuts was hidden once. All `81` predictions were hashed before the targets were read.

## Result

The primary test failed `5/12` gates:

```text
ARA MAE                 0.12394
physical midpoint MAE   0.08687
ridge MAE               0.18616
eight-cell mean MAE     0.21630
```

ARA beat the two simple controls but not physical positivity. The clean verdict is `NOT SUPPORTED`.
Independent validation passed `490/490`.

## Larger-wave observation

The mixed input had closure `0.0089` and zero retained directions. The four outputs had closure
`0.5162–0.5765`, a mean gain of `0.5284`, but retained `1,2,2,1` directions at the frozen `0.50` threshold.

Thus the transition was a strong trough-to-partial-crest movement, but not the frozen complete-crest result.
The source did not contain the specifically proposed crest-to-trough direction.

## Secondary result

On the four normalized Bell-measurement operators, ARA missing-cut MAE was `0.07105`, better than the physical
midpoint's `0.08716` and the ridge's `0.19516`. This is recorded as a distinct secondary cross-object result and
does not rescue the primary state-matrix failure.

## Methodological lesson

Q24 identified the right complete relation object. Q25 showed that this does not imply that a static, locally
balanced sphere assumption is sufficient for missing-cut reconstruction.

Dylan's larger-wave qualification is now the strongest next lineage: acquire a full ARA^9 trajectory and test
whether the local relation moves crest → handover → trough, including any singularity/orientation flip, on
untouched later tomography.

Full report:
`analysis/quantum/Q25_ARA9_BLIND_MISSING_CUT_REPORT_2026-07-26.md`.

