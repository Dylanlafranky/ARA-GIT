# Q18 — Grouped Phase A/B Residual Geometry

**Date:** 26 July 2026  
**Claim:** `Q18-GROUP-RESIDUAL-v1`  
**Frozen protocol SHA-256:** `c3833446b6b78c31d48a533be7a3dc235d2e9e9100699f13aa0b7ca65be0035a`  
**Primary verdict:** **NOT SUPPORTED — 6/8 frozen gates passed**  
**Independent validation:** **75/75 checks passed**

## Outcome

The strict claim tested in Q18 was not supported. Removing the development-only Coupling-ARA diameter `J` did
not make that diameter stay sufficiently absent in the untouched holdout records, and the holdout residual did
not collapse cleanly to rank two.

However, the failure is informative rather than empty:

- the two remaining grouped Phase A/B diameters retained essentially all of their development magnitude;
- both remained directionally stable in holdout;
- their Phase A/B groups remained highly distinguishable;
- the four individual children remained `92.5%` distinguishable using only the two retained coordinates;
- none of `9,999` balanced-label full-pipeline controls or `1,000` same-archive pseudo-child controls passed the
  complete deterministic gate set.

The most careful current reading is:

> The four-child geometry contains three strongly coupled relational diameters. Two diameters can retain much of
> the child identity after a third development direction is projected out, but a diameter frozen in one archive
> is not stable enough in orientation to remain deleted in another archive.

This does not show causal regeneration because development and holdout are separate acquisition-index records,
not a physical remove-and-wait experiment.

## Post-result ARA hierarchy correction

The three measured contrasts must not be flattened into three peer rods. In the ARA interpretation supplied
after Q18:

\[
\underbrace{U}_{\text{child ARA 1}}
+
\underbrace{V}_{\text{child ARA 2}}
+
\underbrace{(U\leftrightarrow V)}_{\text{their coupling relation}}
\longrightarrow
\underbrace{J_{\mathrm{parent}}}_{\text{parent ARA/closure}}.
\]

Thus removing the measured parent-`J` direction does not mean physically deleting the two child waves that make
the parent. It sections the coupled whole and exposes `U` and `V` in relatively purer form. Their near-total
retention and strong Phase A/B classification are therefore the important positive observation:

- after the parent cut, `U` retained `99.995%` of its development magnitude;
- after the parent cut, `V` retained `99.966%`;
- their holdout Phase A/B accuracies were `98.125%` and `90.625%`.

The `57.5%` holdout `J` residual must consequently not be described as demonstrated physical regeneration.
Recombining the residual children algebraically can reconstruct a parent-like contrast, especially when the
child directions rotate between development and holdout.

The frozen Q18 verdict remains `NOT SUPPORTED` because Q18 explicitly registered the stricter
independent-removal gates. The hierarchy correction changes the interpretation and the design of the next test;
it does not rewrite the preregistered question after seeing its answer.

The canonical relative tier notation for the next tests is recorded in
`ARA_QUANTUM_FRACTAL_TIER_MAP_2026-07-26.md`: `J` is Tier 1, `U/V` are Tier 2, the four `Cij` identities are
Tier 3, and their internal children are Tier 4.

## Terminology correction

At this grouped parent rung the two sides of each diameter are called **Phase A** and **Phase B**.
`Anti-phase` is reserved for the purer reversal exposed after decompressing one child rung below. The sign names
are reversible; group membership is the tested content.

| Parent diameter | Phase A group | Phase B group |
|---|---|---|
| `U` | `C00, C01` | `C10, C11` |
| `V` | `C00, C10` | `C01, C11` |
| `J` Coupling ARA | `C00, C11` | `C01, C10` |

## The test in both languages

| ARA-first description | Mathematical description |
|---|---|
| Freeze one parent diameter from the development half. | Estimate a development contrast direction \(\hat D_g^{dev}\). |
| Remove that diameter from every child record. | Orthogonally project every centered vector away from \(\hat D_g^{dev}\). |
| Ask whether the removed Phase A/B division stays absent. | Measure the same contrast’s normalized holdout residual. |
| Ask whether the other two parent cuts retain their identities. | Measure retained magnitude, development-to-holdout cosine and binary balanced accuracy. |
| Ask whether the four children remain locked by the remaining pair. | Classify the four children in the two retained residual coordinates. |

The frozen removal was

\[
\underbrace{x^{(-g)}}_{\substack{\text{record after}\\\text{one parent cut is removed}}}
=
\underbrace{x-M^{dev}}_{\substack{\text{development-centred}\\\text{ARA record}}}
-
\underbrace{\left[(x-M^{dev})\cdot\hat D_g^{dev}\right]\hat D_g^{dev}}_
{\substack{\text{component along the}\\\text{removed grouped diameter}}}.
\]

This is a measurement-space subtraction, not a physical intervention on the quantum system.

## Frozen results

| Removed diameter | Holdout leakage ↓ | Minimum retained magnitude ↑ | Minimum holdout persistence ↑ | Minimum Phase A/B accuracy ↑ | Rank-two share ↑ | Four-child accuracy ↑ |
|---|---:|---:|---:|---:|---:|---:|
| `J` Coupling ARA — primary | `0.5747` | `0.9997` | `0.8309` | `0.9063` | `0.8931` | `0.9250` |
| `U` — secondary | `0.4790` | `0.9701` | `0.8176` | `0.9063` | `0.8582` | `0.8375` |
| `V` — secondary | `0.5588` | `0.9701` | `0.8286` | `0.9125` | `0.8969` | `0.8875` |

The leakage gate required `<= 0.25`; every removal failed it. The holdout rank-two gate required `>= 0.95`;
every removal also failed it. All remaining deterministic gates passed in all three branches.

For the primary `J` removal specifically:

- retained `U` Phase A/B balanced accuracy: `0.98125`;
- retained `V` Phase A/B balanced accuracy: `0.90625`;
- retained-axis absolute cosine: `0.24266`;
- four-child balanced accuracy: `0.925`;
- label-shuffle 99th percentile: `0.33125`;
- label-shuffle \(p=0.0001\).

## Why the removed diameter reappeared

The residual leakage has a direct geometric explanation. A direction estimated in development is not exactly
parallel to its holdout counterpart. Removing the development direction leaves the perpendicular component of
the rotated holdout direction.

| Diameter | Residual leakage | Equivalent orientation drift |
|---|---:|---:|
| `J` | `0.5747` | about `35.08°` |
| `U` | `0.4790` | about `28.62°` |
| `V` | `0.5588` | about `33.97°` |

These are the same persistence relations already visible in Q16:

\[
\underbrace{L_g}_{\text{residual leakage}}
\approx
\underbrace{\sqrt{1-P_g^2}}_{\substack{\text{part of the holdout diameter}\\\text{not aligned with the frozen development cut}}}.
\]

Therefore Q18 does **not** presently establish that a physically removed ARA diameter is recreated. It
establishes that one fixed linear cut does not remove the corresponding relation from independently measured
holdout geometry.

## ARA interpretation

The result fits a **coupled, orientation-drifting parent geometry** better than three rigid and independently
removable rods:

1. `U`, `V` and `J` are valid grouped Phase A/B cuts through the same four-child identity.
2. Removing one fixed cut does not destroy the children’s relational identity.
3. The remaining two cuts preserve most of that identity, but not all of the holdout shape.
4. The missing share appears as a third residual direction because the parent cuts rotate between record groups.

This is compatible with the ARA claim that the cuts are different diameter readings of one coupled sphere. It
does not by itself prove that ontology: a drifting low-dimensional statistical manifold is also an adequate
mathematical description.

## Established mathematical reading

The four prepared record centroids occupy a reproducible three-dimensional contrast subspace. The `U/V/J`
Walsh contrasts are a convenient basis for that subspace. Projecting away one development basis vector preserves
strong two-coordinate classification, but covariate shift rotates the corresponding holdout contrast and leaves
material third-dimensional residual energy.

The established reading and the ARA reading agree on the measured facts. They differ in interpretation:

- ARA treats the three cuts as coupled appearances of one parent sphere;
- conventional multivariate analysis treats them as a drifting three-dimensional contrast manifold.

Q18 does not decide between those interpretations.

## Controls and audit

- `9,999` balanced-label full-pipeline controls: `0` passed gates 1–7;
- `1,000` within-archive pseudo-child controls: `0` passed gates 1–7;
- independent validator: `75/75` checks passed;
- the validator did not import the primary implementation;
- source, Q17-result and frozen-protocol hashes matched exactly.

The controls show that the retained classification structure is not reproduced by the registered relabelling
controls. They cannot turn the failed leakage and rank-two gates into a successful primary verdict.

## What Q18 supports and does not support

**Supported as an observed property**

- the strongest Q17 division is properly treated as the two Phase A/B pole groups of Coupling ARA `J`;
- after `J` removal, the other two parent cuts remain stable and retain strong child information;
- the four-child identity is distributed across the grouped relational coordinates rather than stored in only
  one of them;
- the orientation of each grouped diameter changes materially between development and holdout records.

**Not supported**

- a frozen `J` direction can be removed and remain absent in holdout;
- the remaining geometry becomes a clean rank-two plane;
- all three diameters are independently removable under the frozen thresholds;
- the test demonstrates physical regeneration, a hidden quantum state or a new quantum law.

## Best next test

The next clean question is whether the changing orientation is itself lawful.

Freeze a transport rule using consecutive development record blocks, predict each grouped diameter’s later
orientation without using later child labels, and test whether that transported diameter removes holdout leakage
substantially better than the fixed Q18 direction. This would distinguish:

- a sphere/cycle whose diameter cuts rotate in a reproducible way;
- arbitrary archive drift;
- a fixed geometry measured with noise.

That should be a new frozen test. Q18 must remain unchanged.

## Reproduction

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q18_grouped_diameter_residual_test.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q18_grouped_diameter_residual_validate.py'
```

Primary outputs:

- `Q18_GROUPED_DIAMETER_RESIDUAL_RESULTS.json`
- `Q18_GROUPED_DIAMETER_RESIDUAL_METRICS.csv`
- `Q18_GROUPED_DIAMETER_RESIDUAL_PROJECTIONS.csv`
- `Q18_GROUPED_DIAMETER_RESIDUAL_CONTROLS.csv`
- `Q18_GROUPED_DIAMETER_RESIDUAL_VALIDATION.json`
