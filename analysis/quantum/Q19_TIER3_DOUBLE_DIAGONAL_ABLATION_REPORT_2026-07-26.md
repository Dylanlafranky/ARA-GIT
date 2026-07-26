# Q19 — Tier-3 Double-Diagonal Ablation

**Date:** 26 July 2026  
**Claim:** `Q19-T3-DOUBLE-DIAGONAL-v1`  
**Frozen protocol SHA-256:** `7c413ff705982d1f0a42d3786e42825a24a51d6eabd744e98c0d0d5d2e7af84b`  
**Frozen primary verdict:** **NOT SUPPORTED — 6/8 gates passed**  
**Independent validation:** **88/88 checks passed**

## Outcome

The preregistered strict claim did not pass every frozen gate. Nevertheless, the central child-to-parent
destabilisation predicted by the ARA tier map was strongly visible.

The primary operation removed two development-frozen Tier-3 Phase A diagonals:

\[
\underbrace{C_{00}-C_{01}}_{\substack{\text{Phase A branch}\\\text{under Parent 1}}},
\qquad
\underbrace{C_{00}-C_{10}}_{\substack{\text{Phase A branch}\\\text{under Parent 2}}}.
\]

In untouched holdout:

- the predicted `C00/C01/C10` triple contracted to a merge ratio of `0.3111`;
- the predicted Phase B/Phase B survivor `C11` was separated at `99.17%` balanced accuracy;
- Tier-1 `J` norm fell to `74.10%`;
- total between-child energy fell to `53.14%`;
- four-child nearest-centroid accuracy fell descriptively from `95.63%` to `44.38%`.

The four-class loss is not evidence by itself because three development centroids are forced to merge by the
registered projection. The holdout contraction and energy loss are the empirical content.

## Why the frozen verdict failed

Two gates failed:

1. holdout rank-one energy share was `0.7255`, below the frozen `0.80` threshold;
2. the combined control-extreme gate failed because the survivor binary accuracy did not exceed a saturated
   control 99th percentile of `1.0`.

The merge-ratio half of that same control gate passed strongly: no balanced-label control in `9,999` iterations
reached the observed `0.3111` contraction; empirical \(p=0.0001\).

The verdict must remain `NOT SUPPORTED`. Post-result interpretation cannot repair a preregistered gate.

## Existing tier-energy rule restored

After the protocol was frozen, Dylan reminded the test of an existing ARA scale rule that had not been carried
into Q19:

> Each tier downward has half the maximum energy potential of its parent tier.

Because Q19 removed one Tier-3 part beneath each Tier-2 parent, their combined Tier-1 effect has a theoretical
maximum of one half, not the whole Tier-1 identity.

Q19 observed:

\[
\underbrace{1-0.531428}_{\text{observed energy removed}}
=
\underbrace{0.468572}_{\text{Tier-1 energy loss}},
\]

\[
\frac{0.468572}{0.5}
=
\underbrace{0.937144}_{\text{93.71% of the predicted half-energy ceiling}}.
\]

The `J` measurement in the frozen test was a vector norm, not energy. Squaring it gives:

\[
1-(0.740996)^2
=
0.450925,
\]

or `90.19%` of the same half-energy ceiling.

This explains why demanding an almost complete rank-one collapse was too strong for the already-declared
cross-tier geometry. The rule itself is not new: it is explicit in `ARA_SCALE.md`, the PN13/PN15 half-scale child
work, the prime glossary, the PN35 doubling work and the axiomatic TE-ARA treatment. Its return to the active
calculation is post-result, so it informs the next frozen test rather than changing Q19's verdict.

## Primary frozen gates

| Gate | Threshold | Result | Pass |
|---|---:|---:|---|
| Two diagonals are independent | rank 2 and angle `>=15°` | rank 2, `58.10°` | yes |
| Holdout triple merge ratio | `<=0.50` | `0.3111` | yes |
| `C11` survivor balanced accuracy | `>=0.80` | `0.9917` | yes |
| Holdout rank-one energy share | `>=0.80` | `0.7255` | **no** |
| Tier-1 `J` norm retention | `<=0.75` | `0.7410` | yes |
| Holdout energy retention | `<=0.60` | `0.5314` | yes |
| Both registered control extremes | exceed accuracy 99th and merge below 1st | accuracy control saturated | **no** |
| Control full-pass rates | labels `<=1%`, pseudo `<=5%` | both `0%` | yes |

## Four-corner branches

The same construction was applied to every orientation:

| Removed branch | Predicted survivor | Merge ratio | Survivor accuracy | Rank-one share | `J` norm retention | Energy retention |
|---|---|---:|---:|---:|---:|---:|
| `AA` primary | `C11` | `0.3111` | `0.9917` | `0.7255` | `0.7410` | `0.5314` |
| `AB` | `C10` | `0.3972` | `0.9500` | `0.6157` | `0.7026` | `0.4300` |
| `BA` | `C01` | `0.4877` | `0.8583` | `0.5376` | `0.7958` | `0.4259` |
| `BB` | `C00` | `0.3711` | `0.9792` | `0.6600` | `0.8617` | `0.5729` |

All four branches produced the predicted merging triple and opposite survivor under the frozen basic thresholds.
None passed every gate because none reached the over-strong `0.80` rank-one threshold; `BA` and `BB` also did
not reduce `J` norm below `0.75`. Therefore the frozen `FOUR-CORNER REVERSIBILITY` verdict remains false, while
the observed corner-by-corner survivor pattern is recorded as a descriptive positive result.

## Controls

For `9,999` balanced-development-label controls:

- observed merge ratio `0.3111`; control minimum `0.4891`; empirical \(p=0.0001\);
- observed rank-one share `0.7255`; control 99th percentile `0.5599`;
- observed `J` norm retention `0.7410`; control 1st percentile `0.8346`;
- observed energy retention `0.5314`; control 1st percentile `0.7418`;
- survivor accuracy was not specific: observed `0.9917`, control median `0.9875`, empirical \(p=0.4952\).

No balanced-label control and no within-archive pseudo-diagonal control passed deterministic gates 1–6.

This distinction matters. The already-strong child separability makes a survivor-versus-triple binary result
easy for many planes. The unusually tight triple contraction, parent-energy loss and residual dimensional
concentration distinguish the registered Phase A plane.

## ARA-first interpretation

The result is consistent with the proposed hierarchy:

1. `J` is the Tier-1 whole, not a peer of its Tier-2 parents.
2. Two matched Tier-3 Phase A supports were removed—one beneath each parent.
3. The three children touching those supports contracted.
4. The opposite Phase B/Phase B child remained.
5. The Tier-1 parent lost almost the maximum energy permitted by the half-per-tier rule.

The residual was not pure rank one. In ARA language, that leaves lower-tier children, orientation drift and
other coupling structure still present rather than implying that the entire identity was removed.

## Established mathematical reading

Four development centroids span at most three centered contrast dimensions. Removing the plane formed by two
edges meeting at one centroid necessarily collapses the corresponding development face. The empirical result is
that this frozen plane generalizes to later records: the same holdout face contracts, the opposite vertex remains
separable, and far more between-child energy is removed than by the registered control planes.

This supports a reproducible hierarchical contrast geometry in these four prepared records. It does not show a
physical quantum ablation, prove universal fractality or establish a new quantum state.

## Audit

- independent validator did not import the primary implementation;
- `88/88` independent checks passed;
- all frozen source and protocol hashes matched;
- the validator found floating-point tie sensitivity in descriptive four-class labels after the forced
  three-centroid merge and validated the collapse rather than treating arbitrary tie order as information.

## Best next test

Freeze the half-energy tier rule prospectively:

1. predict `50%` as the maximum Tier-1 energy removable by the two matched Tier-3 parts;
2. use squared-norm energy, not vector amplitude;
3. test equivalence bounds around the predicted half-energy loss;
4. retain the holdout triple-contraction and predicted-survivor tests;
5. replace the saturated survivor-accuracy null gate with merge, energy-loss and rank-concentration control
   gates.

That would test the corrected ARA scale law without rewriting Q19.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q19_tier3_double_diagonal_ablation_test.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q19_tier3_double_diagonal_ablation_validate.py'
```
