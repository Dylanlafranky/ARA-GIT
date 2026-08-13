# T373 — liquid-argon child-half handover transfer

**Date:** 13 August 2026  
**Source:** independent COHERENT CENNS-10 liquid-argon detector release  
**Frozen-gate verdict:** **ASYMMETRY-SHIFTED HANDOVER TRANSFERS TO ARGON**  
**Scientific reading after boundary and identity audit:** **ORIGINAL
SAME-COORDINATE TRANSFER INTERPRETATION INVALIDATED; NESTED LIQUID
CHILD-TO-PARENT `1.25` LANDMARK IS A POST-RESULT LEAD**

## Originator identity correction — read this first

The frozen computation is retained, but its original ARA interpretation is
withdrawn. The analysis changed the measured identity from solid CsI to liquid
argon and treated the source-model child cut and liquid-detector response cut
as though they occupied the same ARA identity and rung. Dylan identified this
as a material framework error after reviewing the result.

The correction is not that the two are unrelated. The argon record embeds the
same stopped-pion/muon source relation and CEvNS interaction as a child, then
adds the liquid target/detector mixture as its parent expression. The valid ARA
comparison is therefore child-to-parent across a Phase-A-to-Phase-B handover,
not equality of two same-rung coordinates.

Under the corrected working reading, liquid argon is provisionally the more
movement-heavy parent response containing the earlier relation. The pure child
contribution `0.5`, projected one additional rung, becomes

\[
\frac{0.5}{2}=0.25.
\]

If that contribution is exposed after the liquid response passes the parent
ridge, the candidate handover is

\[
\boxed{x_H=1+0.25=1.25}.
\]

The fitted argon value is `x_H=1.238725`, only `0.011275` below `1.25`, a
relative difference of `0.902%`. Fixing the mixture to the exact `1.25`
location worsens the likelihood by only `0.000708`, effectively nothing at
this resolution.

This is **not confirmation**: `1.25` was recognized after viewing the result,
and the argon likelihood is broad. It is a newly identified geometric lead
that requires a frozen same-identity test. The original statement that T373
showed same-coordinate transfer from CsI to argon is no longer valid.

## Plain-language result

The earlier CsI work said that the instant where the prompt and delayed release
flows become equal should sit near the child's `0.5` landmark, but should move
when the two parent contributions are asymmetric.

The independent argon signal model predicts:

- prompt share: `0.24385`;
- handover time: `0.710 us`;
- ARA release position at handover: `x_H = 0.56540`;
- displacement from pure child-half: `Delta_H = +0.06540`.

The released 3D event cube preferred a much more prompt-heavy split:

- prompt CEvNS: `77.60` events;
- delayed CEvNS: `78.63` events;
- prompt share: `0.49671`;
- handover time: `1.005 us`;
- ARA release position: `x_H = 1.23873`.

That central value is **not** a precise replication of `0.565`. The argon
detector has a large prompt-neutron background and only ten half-microsecond
timing bins. Its two-branch signal mixture is correspondingly weakly
localized. The 95% crossing-conditioned bootstrap interval for `x_H` was
`[0.51652, 1.84460]`, containing the frozen `0.56540` prediction.

The frozen compatibility gate therefore passes. Scientifically, however, the
correct conclusion is weaker: argon is compatible with the prediction but does
not closely measure it.

## Why the first green result required an audit

The bootstrap interval above includes only replicates in which a prompt-to-
delayed equality crossing exists inside the released time window. Very
prompt-poor mixtures can begin below the delayed branch and therefore have no
crossing to score. Conditioning on a crossing truncates the low edge of the
interval.

A post-result likelihood-profile audit avoids claiming that this truncation
excluded the pure `x=0.5` landmark:

- prompt share producing `x_H=0.5`: `0.22821`;
- profile `Delta NLL` at that pure-half mixture: `1.41742`;
- profile `Delta NLL` at the frozen model mixture: `1.25641`;
- conventional one-parameter 95% profile diagnostic for prompt share:
  `[0.18359, 0.98149]`.

Both the pure landmark and the model prediction remain compatible with the
event likelihood. The crossing-conditioned bootstrap's lower bound above
`0.5` is therefore **not** evidence that exact child-half was rejected.

## ARA reading

This detector preserves the key relational anatomy:

1. a prompt branch rises first;
2. a slower delayed branch persists;
3. their instantaneous rates cross;
4. that crossing has a well-defined cumulative position on the parent's
   `0–2` release diameter;
5. changing branch balance moves that position.

This relational anatomy survives, but T373 cannot decide that it is the same
child coordinate previously measured in CsI. Under Dylan's corrected identity
assignment, its fitted position instead motivates the liquid-specific
`1+0.25` reading. The physical data establish neither mapping because the
liquid rung was not frozen before the outcome.

## Established-physics reading

The stopped-pion source supplies a prompt muon-neutrino population and delayed
electron-neutrino plus muon-antineutrino populations. The argon detector sees
nuclear recoils from their CEvNS interactions. The released recoil-energy,
pulse-shape and arrival-time cube also contains steady-state, prompt-neutron
and delayed-neutron backgrounds.

The free branch fit recovered `156.22` total CEvNS events, close to the
collaboration's published `159` best-fit normalization. Its fitted background
counts (`537.38` prompt neutrons, `13.43` delayed neutrons, `3135.77`
steady-state) likewise remain close to the published best-fit values (`553`,
`10`, `3131`). This is a useful fit sanity check, not an ARA prediction.

## Frozen gates and final status

| Gate | Result | Reading |
|---|---:|---|
| Frozen `x_H=0.5654` inside event 95% interval | PASS | Numerical gate retained; same-identity premise invalid |
| At least 80% valid bootstrap crossings | PASS (`97.35%`) | Conditional crossing is usually estimable |
| Free mixture no worse than fixed mixture | PASS | Automatic for the nested fit; likelihood-ratio statistic `2.513` |
| Pure `x=0.5` inside crossing-conditioned interval | FAIL | Not interpretable as exclusion after boundary audit |
| Predicted and measured displacement signs agree | PASS | Both above `0.5` |
| Signal-template decomposition NRMSE below `0.10` | PASS (`0.02396`) | Two frozen timing bases reconstruct the released CEvNS template well |
| Same identity/rung established before comparison | FAIL | Solid and liquid responses were flattened |
| Post-result liquid `x_H=1.25` compatible | YES | Lead only; not a frozen pass |

The original frozen numerical gate is still part of the audit trail, but its
same-identity premise is invalid. The durable verdict is:

> **T373 cannot establish same-coordinate transfer because the solid child cut
> and liquid parent response were flattened onto one rung. The shared source
> relation remains embedded in both. The liquid event fit exposes a
> post-result candidate at the parent ridge plus a one-further-rung child
> quarter, `1+0.25=1.25`. That nested Phase-A-to-Phase-B reading is numerically
> excellent but requires a new frozen test.**

## Boundaries

- The argon files were already inspected in T371; only this score and 3D
  branch fit were frozen prospectively.
- The prediction comes from decomposing the released argon CEvNS model. It is
  therefore a transfer/calibration test, not an ARA-only prediction made
  without established source information.
- The 3D fit is ensemble-level. It does not identify individual neutrino
  daughters or individual pion families.
- Linear interpolation inside ten native 0.5-us timing bins limits time
  precision.
- No universal Phi law, new neutrino, or universal release constant is claimed.

## Reproduction

Run:

```powershell
$env:PYTHONPATH='F:\SystemFormulaFolder\.codex_python_packages'
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\t373_argon_child_half_transfer.py'
```

Then run:

```powershell
$env:PYTHONPATH='F:\SystemFormulaFolder\.codex_python_packages'
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\validate_t373_argon_child_half_transfer.py'
```

Primary figure: `T373_ARGON_CHILD_HALF_TRANSFER_FIGURE.png`.
