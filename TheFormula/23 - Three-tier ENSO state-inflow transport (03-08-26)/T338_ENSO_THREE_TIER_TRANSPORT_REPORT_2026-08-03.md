# T338 — three-tier ENSO state–inflow transport

**Date:** 3 August 2026  
**Frozen framework verdict:** **MIXED**  
**Ocean child route:** **SUPPORTED**  
**Atmospheric child route:** **NOT SUPPORTED BY THE THREE FROZEN WIND CUTS**  
**Independent validation:** **PASS**

## Plain-language result

This test kept Dylan's confirmed identity tree intact:

1. ENSO is the parent identity.
2. La Niña and El Niño are its two directional children.
3. Each child is decompressed into an oceanic grandchild and an atmospheric
   grandchild.
4. The inflow field is measured separately and followed upward to see whether
   it predicts movement in the corresponding state.

The ocean side worked. East–west warm-water-volume redistribution predicted
the direction of Niño3.4 one month later on the untouched 2005–2025 period.
A separate 0–300 m heat-content change measure reproduced the same ocean
direction even more strongly.

The atmospheric side did not work in the frozen form. None of the west,
central or east 850-hPa trade-wind cuts passed all gates against SOI, and none
passed the OLR replication gates. The failures were not featureless: west and
central winds mainly recovered the La Niña-directed half, while the east cut
was more El Niño-directed. That is evidence of unresolved regional/phase
structure, not evidence that the three cuts form one clean atmospheric inflow
identity.

The nested ocean-plus-atmosphere inflow relation did predict movement of the
compressed ENSO parent at two months. This is useful structural evidence, but
it does not repair the failed atmospheric-child gate. Under the frozen rule,
the overall verdict therefore remains **MIXED**.

## Frozen ARA architecture

The four retained grandchild strengths are

\[
L_O=\max(-O,0),\qquad L_A=\max(-A,0),
\]

\[
E_O=\max(O,0),\qquad E_A=\max(A,0),
\]

where `O` is the development-scaled Niño3.4 ocean state and `A=-SOI` is the
development-scaled atmospheric state, both oriented toward El Niño when
positive.

The two child cuts are

\[
x_L=2\frac{L_A}{L_O+L_A},\qquad
x_E=2\frac{E_A}{E_O+E_A}.
\]

On either diameter, `0` is ocean-led, `2` is atmosphere-led and `1` is their
equal ridge. The parent compression is

\[
S_L=L_O+L_A,\qquad S_E=E_O+E_A,
\]

\[
x_P=2\frac{S_E}{S_L+S_E}.
\]

These equations preserve the declared tree; their algebraic reconstruction is
not itself an empirical discovery. The empirical question is whether the
separate inflow cuts lead later state movement on untouched data.

## Untouched holdout scores

Development was fixed to January 1980–December 2004. Leads were selected once
there and applied to January 2005–December 2025.

| Path | Lead | n | Balanced accuracy | 95% block interval | Spearman ρ | El recall | La recall | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Ocean WWV redistribution → Niño3.4 | 1 | 245 | **0.6364** | **[0.6099, 0.6850]** | **0.3724** | 0.6271 | 0.6457 | **PASS** |
| West trade wind → SOI | 4 | 243 | 0.5116 | [0.4742, 0.5725] | -0.1145 | 0.2672 | **0.7559** | FAIL |
| Central trade wind → SOI | 2 | 225 | 0.4575 | [0.3971, 0.5156] | -0.1245 | 0.2710 | **0.6441** | FAIL |
| East trade wind → SOI | 2 | 230 | 0.4948 | [0.4311, 0.5454] | 0.0197 | **0.6075** | 0.3821 | FAIL |
| Nested inflow relation → ENSO parent | 2 | 99 | **0.6241** | **[0.5270, 0.6685]** | **0.1029** | 0.6000 | 0.6481 | **PASS** |
| West trade wind → OLR | 2 | 223 | 0.5053 | [0.4601, 0.5505] | -0.0676 | 0.2525 | **0.7581** | FAIL |
| Central trade wind → OLR | 2 | 214 | 0.5437 | [0.4748, 0.5832] | 0.0181 | 0.3608 | **0.7265** | FAIL |
| East trade wind → OLR | 1 | 212 | 0.5553 | [0.4774, 0.6256] | 0.2005 | **0.6633** | 0.4474 | FAIL |
| Heat-content change → Niño3.4 | 1 | 240 | **0.7093** | **[0.6666, 0.7590]** | **0.5502** | 0.7257 | 0.6929 | **PASS** |

The atmospheric architecture gate required at least two of the three primary
wind paths to pass. The count was `0/3`, so a passing ocean path cannot promote
the whole test to supported.

## Controls and what they mean

For the primary WWV path, balanced accuracy was:

- declared direction: `0.6364`;
- wrong orientation: `0.3636`;
- time-reversed record: `0.5377`;
- month-preserving shuffled years: `0.5145`;
- last-movement persistence: `0.6521`.

The first four comparisons support an ordered ocean relation rather than a
mere sign convention or monthly climatology. However, simple persistence was
slightly stronger. The result is therefore evidence for an ocean feeder path,
not a claim of improved forecasting.

For the nested parent relation, the declared cut scored `0.6241`, compared
with `0.3759` for wrong orientation, `0.5278` for time reversal, `0.5019` for
shuffled years and `0.3173` for parent persistence. That relation is stronger
than its named controls, although it uses only `99` non-zero holdout movements
and remains supplementary to the failed atmospheric architecture gate.

The heat-content replication scored `0.7093`, above the same Niño3.4
persistence control of `0.6521`. This is the strongest surviving result in
T338.

## ARA interpretation

The test supports one complete upward path:

\[
\text{ocean grandchild inflow}
\longrightarrow
\text{ocean child state}
\longrightarrow
\text{ENSO parent movement}.
\]

It does **not** yet support the symmetric atmospheric path using a single
regional trade-wind anomaly as the corresponding cut. The directional recalls
suggest that the atmospheric identity is being sliced across regions and
phases: different cuts see different sides of the movement. Compressing those
cuts would hide that asymmetry, so they remain separate.

The disciplined conclusion is:

> The three-tier ARA decomposition produced a reproducible ocean-to-parent
> transport relation and a passing nested parent relation. The atmospheric
> grandchild remains unresolved by the frozen wind cuts, so the full
> ocean–atmosphere transport architecture is not yet recovered.

## Scientific translation

In conventional ENSO language, the passing ocean paths say that changes in
equatorial Pacific subsurface warm-water distribution and heat content carry
information about near-future Niño3.4 movement. The non-passing atmospheric
paths say that fixed regional trade-wind anomalies do not, by themselves,
provide a stable two-sided predictor of later SOI or OLR movement under this
sign-and-lead rule.

This is compatible with ocean and atmosphere being strongly coupled without
implying that one monthly atmospheric cut must lead both El Niño and La Niña in
the same way.

## Boundaries

- The four-grandchild tree was declared before scoring, but the exact public
  observables are translations of those identities, not the identities
  themselves.
- Standardisation used development data only.
- No smoothing, Fourier transform, spectral decomposition or retrospective
  alignment was used.
- This is a transport crosswalk, not a bedrock proof and not a production ENSO
  forecast.
- The WWV and heat-content replications are distinct measurements of related
  ocean physics, not independent physical systems.
- A better atmospheric cut must be frozen before it is scored. It cannot be
  chosen retrospectively from the directional pattern found here.

## Recommended next geometry question

Do not add more same-rung variables yet. First ask Dylan to identify whether
the atmospheric grandchild should itself be decompressed into a wind child and
a convection child, with their ordered handover forming the atmospheric
identity. If confirmed, freeze that Di-ARA and test whether its accumulated
movement, rather than any one wind region, climbs into SOI and then the ENSO
parent.

## Reproduction files

- `T338_ENSO_THREE_TIER_TRANSPORT_PROTOCOL_v1_FROZEN.md`
- `T338_ENSO_THREE_TIER_TRANSPORT_PROTOCOL_v1_FROZEN.sha256`
- `t338_enso_three_tier_transport.py`
- `T338_ENSO_THREE_TIER_TRANSPORT_RESULTS.json`
- `T338_ENSO_THREE_TIER_TRANSPORT_COORDINATES.csv`
- `T338_ENSO_THREE_TIER_TRANSPORT_VISUAL.svg`
- `validate_t338_enso_three_tier_transport.py`
- `T338_ENSO_THREE_TIER_TRANSPORT_VALIDATION.json`
- `SOURCES.md`

Frozen protocol SHA-256:

`940E98BA047469090684B40F32E6525574C270A283A9B6768210A6C974812374`
