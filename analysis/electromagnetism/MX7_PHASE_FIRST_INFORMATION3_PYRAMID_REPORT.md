# MX7 phase-first Information³ / pyramid closure

## Result first

The frozen MX7 test found a real but narrower result than the initial geometric expectation.

Keeping the four signed routes separately -- `AA`, `AB`, `BA`, and `BB` -- is necessary to avoid flattening two
different pairings into one positive or negative output. However, their **joint sign occupancy alone did not improve
the electric-force closure** on the fixed public PIConGPU snapshot. Relative to the independently compressed two-sign
marginal model, the joint four-route model:

- reduced vector correlation from `0.4455` to `0.3727`;
- increased NRMSE from `0.8993` to `1.2151`;
- improved median angular error from `56.74°` to `53.10°`.

It therefore failed the frozen material phase-first gate. The earlier MX5 first positional-moment model remains the
best compact model in this comparison: correlation `0.5964`, NRMSE `0.8077`, and median angle `48.59°`.

The second result is exact but must be typed correctly. Once each of the four routes retained its **own conditional
field magnitude**, the particle-first electric target was reconstructed at `3.58e-15` relative L2 error. This is an
exact decomposition of the same resolved data, not an out-of-sample prediction and not independent evidence for a
universal ARA law.

## The frozen ladder

For a particle-to-grid contribution and one electric-field component, define

\[
\underbrace{s_q}_{\substack{\text{charge sign}\\\text{ARA phase of source}}}
\in\{-1,+1\},
\qquad
\underbrace{s_E}_{\substack{\text{field sign}\\\text{ARA phase of field}}}
\in\{-1,+1\},
\qquad
\underbrace{r=s_qs_E}_{\substack{\text{joint relation}\\\text{informative third}}},
\qquad
\underbrace{m=|E|}_{\substack{\text{field magnitude}\\\text{route strength}}}.
\]

Plainly: the charge has a signed orientation, the electric field has a signed orientation, and their product says
whether that particular interaction contributes positively or negatively. The product is not a third independent
wave. It is the relation created by the two signed inputs.

Let (Q) be the deposited absolute-charge activity and angle brackets be its weighted average. The exact child-first
electric force-density component is

\[
\underbrace{F^{\rm child}}_{\substack{\text{resolved target}\\\text{child-first output}}}
=
\underbrace{Q}_{\substack{\text{activity envelope}\\\text{how much participates}}}
\underbrace{\langle mr\rangle}_{\substack{\text{magnitude joined to relation}\\\text{unflattened coupling}}}.
\]

The first compact model keeps the two phases separately:

\[
\underbrace{F^{\rm marg}}_{\substack{\text{two-marginal model}\\\text{separate compression}}}
=Q\langle m\rangle\langle s_q\rangle\langle s_E\rangle.
\]

The triangle model restores their joint sign relation:

\[
\underbrace{F^{\rm joint}}_{\substack{\text{four-route sign model}\\\text{triangle closure}}}
=Q\langle m\rangle\langle s_qs_E\rangle.
\]

This correctly distinguishes `AA` and `BB` from `AB` and `BA`, but it still assigns one common mean magnitude to all
routes. On this dataset that assumption is too strong. The model modestly improves direction but overshoots the
resolved vector magnitude and worsens the overall fit.

The fully decompressed route-conditioned expression is

\[
\underbrace{F^{\rm pyramid}}_{\substack{\text{route-conditioned closure}\\\text{exact ceiling}}}
=
\underbrace{Q}_{\text{activity}}
\sum_{a,b}
\underbrace{p_{ab}}_{\substack{\text{route occupancy}\\AA,AB,BA,BB}}
\underbrace{\bar m_{ab}}_{\substack{\text{mean strength}\\\text{inside that route}}}
\underbrace{s_as_b}_{\substack{\text{route orientation}\\+,-,-,+}}
=Q\langle mr\rangle.
\]

Plainly: a perfect answer requires knowing not only which of the four routes is occupied, but how strong that route is.
That extra magnitude coordinate is the added geometric height that motivates the **pyramid** description. In three
vector components the construction repeats along each axis, so a single flat triangle is insufficient to lock the
whole vector identity.

## What “Information³” means here

The ARA reading is two identities plus the relation created by their coupling:

\[
\underbrace{s_q}_{\text{first information}}
+
\underbrace{s_E}_{\text{second information}}
+
\underbrace{(s_q,s_E)}_{\substack{\text{joint relation}\\\text{closing information}}}.
\]

This is a defensible structural meaning for the project term `Information³`. It is **not** a claim that Shannon
information has literally been cubed. As an established information-theory diagnostic, the measured Shannon mutual
information between the two signs was small: median `0.000277 bits`, 95th percentile `0.004532 bits`, maximum
`0.05784 bits`. Nevertheless, it strongly localized the absolute phase correction across cells and components
(Spearman `0.8664`).

Plainly: the two signs are only weakly dependent in raw information quantity, but the places where that dependence
appears are strongly associated with where the phase-only model needs correction. That makes mutual information a
useful map of the relation, not a sufficient reconstruction of force.

## Correction anatomy

The exact decomposition is

\[
F^{\rm child}
=F^{\rm marg}
+\underbrace{Q\langle m\rangle
\left(\langle s_qs_E\rangle-\langle s_q\rangle\langle s_E\rangle\right)}_{\text{phase-relation correction}}
+\underbrace{Q\left(\langle mr\rangle-\langle m\rangle\langle r\rangle\right)}_{\text{magnitude--relation correction}}.
\]

The phase-relation correction had relative L2 magnitude `1.0813` of the target. The remaining magnitude--relation
correction had relative L2 magnitude `1.2150`. These are vector correction norms, not exclusive percentages; they can
exceed one because the terms oppose and cancel.

The weighted route occupancies were close to balanced by charge sign but not by field sign: averaged over x, y and z,
`AA=0.2335`, `AB=0.2665`, `BA=0.2334`, and `BB=0.2666`. Occupancy differences alone therefore cannot explain the
target. Route-dependent magnitude carries the decisive local structure.

## Data and validation

The input was iteration 200 of the CC0 [openPMD example datasets](https://github.com/openPMD/openPMD-example-datasets)
PIConGPU file used by MX4--MX6. Its SHA-256 was locked to
`6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5`. The analysis used trilinear sampling with
recorded Yee offsets and cloud-in-cell deposition. The primary mask contained 9,266 interior vector cells and 27,798
component rows.

An independent validator reconstructed every saved model and identity directly from the cell CSV. It reproduced all
reported metrics with maximum absolute difference `0.0`; maximum algebraic identity error was `3.58e-15`. The
notebook executed all six code cells without error. The figure was visually inspected after generation.

## Scientific interpretation and next test

MX7 supports a precise methodological point: **prematurely reducing a coupled pair to one resultant sign discards
route identity, and retaining route identity still does not permit magnitude to be detached from the route**. That is
directly relevant to ARA's concern about flattening phase/anti-phase children at a parent grain.

MX7 does not show that a triangle or pyramid is a new physical law. The conditioned pyramid is exact because it keeps
the same local conditional information used by the target. The strongest current compact recovery remains the
ordinary first-order moment closure from MX5.

The next discriminating test should therefore be frozen as a held-out prediction: learn a compact mapping from
independently available local geometry to the four route-conditioned magnitudes on one spatial region or time slice,
then predict a withheld region or later slice. Compare it against MX5 first moments, standard regression closures,
shuffled-route controls and a no-interaction baseline. Only held-out improvement would turn the pyramid from a
decompression identity into evidence for a reusable closure rule.

## Reproduction packet

- `MX7_PHASE_FIRST_INFORMATION3_PYRAMID_PROTOCOL_v1_FROZEN.md`
- `mx7_phase_first_information3_pyramid.py`
- `MX7_PHASE_FIRST_INFORMATION3_PYRAMID_RESULTS.json`
- `MX7_PHASE_FIRST_INFORMATION3_PYRAMID_CELLS.csv`
- `MX7_PHASE_FIRST_INFORMATION3_PYRAMID.png`
- `mx7_validate_outputs.py`
- `MX7_PHASE_FIRST_INFORMATION3_PYRAMID_VALIDATION.json`
- `MX7_PHASE_FIRST_INFORMATION3_PYRAMID_NOTEBOOK.ipynb`
- `MX7_NOTEBOOK_EXECUTION_VALIDATION.json`
