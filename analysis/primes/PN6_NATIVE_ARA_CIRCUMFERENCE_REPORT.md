# PN6 native ARA circumference report

**Test ID:** `PN6/NATIVE-ARA-CIRCUMFERENCE/FRESH-R11-v1`  
**Target:** `[100,000,000,000, 101,000,000,000)`  
**Status:** `FRESH PRE-HASHED TARGET / 5 OF 7 CRITERIA PASS / MIXED RESULT / NATIVE ARA ONLY`  
**Independent validation:** `109/109` checks passed

## TL;DR

The native ARA circumference model produced a real prospective result, but not a complete registered success.

Before the target existed, the model froze one canonical ARA circle, one shared log-rung withdrawal factor and two
identity paths. It then predicted the terminal candidate survival within **0.102%** and adjacent-pair survival within
**0.320%**. The observed candidate and pair phase-withdrawal factors remained close to the frozen shared value, the
circle improved on the direct native logarithmic extrapolation, and two independently expressed ARA routes to the
pair identity both landed within 1%.

However, the registered core required the primary model to beat Home on full-path log loss for both identities and
to keep phase RMSE below `0.015` radians. Home retained slightly lower log loss, and the pair phase RMSE was
`0.01846`. Therefore P1 and P2 fail, the strict core verdict is **not supported**, and the result remains mixed.

This was intentionally tested without Buchstab, PNT, Mertens, Hardy-Littlewood, Fourier, SVD or NMF. No established
prime-law audit has been run in this report, so the native verdict cannot be blurred or rescued by another method.

## What was frozen

The direct p29-conditioned survivor share at each log-gate cell was converted to the ARA diameter reading

\[
\underbrace{x_r(g)}_{\substack{\text{ARA release reading}\\0\text{ retained},\ 2\text{ released}}}
=2\left(1-\underbrace{S_r(g)}_{\text{direct surviving share}}\right).
\]

The diameter was decompressed onto the fixed upper branch of a unit circle centred at 1:

\[
\underbrace{\theta_r(g)}_{\substack{\text{circumference phase}\\\text{ARA position on the arc}}}
=\arccos\!\left(2S_r(g)-1\right),
\qquad 0\leq\theta\leq\pi.
\]

Across R8-R10, candidate and adjacent-pair phase increments supplied one shared withdrawal factor:

\[
\underbrace{\rho}_{\substack{\text{shared change in phase step}\\\text{from one log rung to the next}}}
=0.8342632892110983.
\]

The untouched R11 prediction was then

\[
\underbrace{\widehat\theta_{11,e}}_{\text{predicted next-rung phase}}
=
\underbrace{\theta_{10,e}}_{\text{current phase}}
+
\underbrace{\rho}_{\text{shared withdrawal}}
\left(
\underbrace{\theta_{10,e}-\theta_{9,e}}_{\text{previous phase step}}
\right),
\]

\[
\underbrace{\widehat S_{11,e}}_{\text{predicted surviving share}}
=\frac{1+\cos\widehat\theta_{11,e}}{2}.
\]

Plainly: R9 to R10 showed how far the path moved around the ARA circle. Earlier opened rungs showed that this movement
was shrinking. The frozen model continued that shrinking movement once more and projected it back onto the 0-2
diameter.

## Freeze and target integrity

- Frozen prediction packet SHA-256: `1077EF7BA101E8C8F4EAF47DC2E056ABFB5608DB98D30B16915A497563409A0C`.
- The builder verified that hash before it constructed any R11 target state.
- Exact target candidates after filtering by primes through 29: `157,947,219`.
- Exact terminal candidate survivors: `39,475,591`.
- Exact adjacent candidate edges: `157,947,218`.
- Exact terminal adjacent-pair survivors: `9,792,119`.
- Candidate, edge and gate-death accounting all close exactly.
- No frozen path was clipped, repaired, smoothed or monotonized.

## Primary numerical result

| Identity | Model | Path log loss (bits/risk event) | Survival RMSE | Phase RMSE | Terminal relative error |
|---|---:|---:|---:|---:|---:|
| Candidate | Home R10 | **0.328872028** | 0.0289198 | 0.0603036 | 9.9902% |
| Candidate | Direct native log | 0.329384200 | 0.0055269 | 0.0154225 | 1.0117% |
| Candidate | **Circle + shared rho** | 0.329361017 | **0.0045637** | **0.0134827** | **0.1017%** |
| Adjacent pair | Home R10 | **0.551304813** | 0.0272845 | 0.0667420 | 21.0906% |
| Adjacent pair | Direct native log | 0.552903814 | 0.0086474 | 0.0205102 | 1.7560% |
| Adjacent pair | **Circle + shared rho** | 0.552876093 | **0.0077485** | **0.0184641** | **0.3198%** |

The circle model beats the direct native log path on the registered full-path loss for both identities. It also
improves survival RMSE, phase RMSE and terminal error. The improvement in log loss is small but correctly directed:
`0.000023183` bits/event for candidates and `0.000027721` bits/event for pairs.

Home nevertheless wins the particular registered log-loss score. This is not because Home predicts the complete
path well: its terminal errors are roughly 10% and 21%. The score weights every at-risk event at every gate, so the
very large early populations dominate it; Home happens to approximate those early conditional removals slightly
better. The protocol required a log-loss win in addition to the terminal and phase conditions, so this remains a
real failure rather than being reinterpreted after seeing the target.

## Shared phase-withdrawal result

| Reading | Value | Distance from frozen rho |
|---|---:|---:|
| Frozen shared `rho` | 0.834263289 | - |
| Observed candidate R10-R11 withdrawal | 0.807460249 | 0.0268030 |
| Observed pair R10-R11 withdrawal | 0.771911782 | 0.0623515 |

The two observed readings differ by `0.0355485`. Both are within the frozen tolerance of `0.15`, and they are within
the cross-identity tolerance of `0.10`. P5 therefore passes.

In plain language: both identities continued around the circumference in the predicted direction, and both next
steps shrank by broadly the same fraction. The pair step shrank somewhat more strongly than the candidate step,
which is also where the stricter pair phase tolerance was missed.

## Pair identity through two native routes

The direct pair-circle route and the candidate-parent-plus-retained-relation route disagreed by only
`0.000590834` survival RMSE before the target. After opening R11:

- direct pair circle terminal error: `0.3198%`;
- candidate plus `J` terminal error: `0.4383%`.

Both satisfy the registered 1% terminal requirement, so P7 passes. This is useful route closure: the pair identity
can be reached from its own circumference or from the candidate identity plus their retained relation without the
two constructions drifting far apart.

## Registered criteria

| Criterion | Result | Reason |
|---|---:|---|
| P1 candidate primary core | **FAIL** | Terminal and phase conditions pass; primary does not beat Home log loss. |
| P2 pair primary core | **FAIL** | Primary does not beat Home log loss; phase RMSE `0.01846 > 0.015`. |
| P3 candidate circle beats direct native log | **PASS** | Lower registered path log loss. |
| P4 pair circle beats direct native log | **PASS** | Lower registered path log loss. |
| P5 shared withdrawal recurs | **PASS** | Both observed factors remain close to frozen rho and to each other. |
| P6 valid unrepaired paths | **PASS** | Both primary paths are finite, monotone and inside `[0,1]`. |
| P7 native pair-route closure | **PASS** | Pretarget routes agree and both posttarget terminal errors are below 1%. |

**Total: 5/7 pass.** The protocol defines P1+P2+P5+P6 as the strict recurrence core, so that core does not pass.
The canonical circle's added value over the direct native logarithmic extrapolation does pass, as does pair-route
closure.

## Honest interpretation

The strongest supported statement is:

> On a genuinely untouched one-billion-integer rung, a canonical ARA circle with one shared phase-withdrawal factor
> transferred the terminal candidate and pair states to substantially below 1% error, improved on direct native
> logarithmic extrapolation, reproduced similar cross-rung withdrawal in both identities, and closed two native pair
> routes.

The result does **not** establish that this ARA model is the correct full prime-survival law. Under its own frozen
rules it did not beat Home on the full-path log-loss criterion, and its pair phase path missed the declared transfer
tolerance. The visual circle is therefore more than a decorative redescription here—it added prospective value over
the matched native log control—but it is not yet a complete native account of the entire path.

This is exactly the sort of partial result the protocol was designed to reveal: the slow rung/circumference relation
appears real and useful, while some within-rung pair-path structure remains unresolved.

## Recommended next native test

Do not retune R11. Preserve PN6 as a mixed result.

The cleanest next step is an unchanged replication of the same frozen equation on R12. That asks whether the strong
terminal transfer, shared withdrawal and pair-route closure repeat, and whether the P1/P2 failures persist. A later
alternative model may use R11 as opened development data, but it must state any extra within-rung coordinate before
opening another target. This prevents the missing path structure from becoming a retrospective rescue.

## Reproducibility artifacts

- Protocol: `PN6_NATIVE_ARA_CIRCUMFERENCE_PROTOCOL.md`
- Frozen packet: `PN6_NATIVE_ARA_FROZEN_PREDICTIONS.json`
- Freeze manifest: `PN6_NATIVE_ARA_FREEZE_MANIFEST.json`
- Exact target aggregates: `PN6_R11_TARGET_AGGREGATES.json`
- Machine-readable results: `PN6_NATIVE_ARA_RESULTS.json`
- Path table: `PN6_NATIVE_ARA_PATHS.csv`
- Primary artifact: `PN6_NATIVE_ARA_PRIMARY_ARTIFACT.json`
- Independent validation: `PN6_NATIVE_ARA_VALIDATION.json`
- Figure: `PN6_NATIVE_ARA_CIRCUMFERENCE.png`
- Executed notebook: `PN6_NATIVE_ARA_CIRCUMFERENCE.ipynb`

