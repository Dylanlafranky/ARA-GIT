# T403 — Reverse component lineage findings

## Coordinate audit notice (T404/T405)

T404 found that T403 converted the eight local-child bins back to source time
linearly, although T400's registered child coordinate is cumulative parent
ARA and therefore nonlinear in time. The apparent fitted-source crest near
`0.532` is not valid; the corrected T400 source crest is `0.706306`.

The detector topology itself remains unchanged: its aggregate turn is near
`0.50-0.57` and its ridge-nearest handover is near `0.936-1.051`. The
corrected order is therefore detector/parent turn, displaced child release
maximum, then parent handover. T405 further shows that the child coordinate's
displacement from the pure parent `0.5` reference is perfectly monotonic in
saved branch participation inside T400, but that relation is structurally
carried by the equality boundary used to construct the cut. It validates the
distortion-aware coordinate response; it is not independent physical proof.

Use the integrated corrected report for current interpretation:
`analysis/muon/T404_corrected_child_release_diara/T404_CORRECTED_CHILD_RELEASE_DIARA_REPORT.html`.

## Result

**Verdict: `PARTIAL COMPONENT RELATION`.** Starting at the detector and tracing backward, the stable T402 signed footprint is present in the fitted delayed-neutrino release branch on the same T400 local ARA rung. It is not uniquely identifiable as one flavor child or as the independently measured silver spin wave.

The detector footprint has the already-replicated sequence:

1. positive lower-side crest at local ARA `0.50–0.57`;
2. sign crossing near the ridge at `0.936–1.051`;
3. negative upper-side trough at `1.88–1.91`.

When the T398 source components are sampled at the same eight T402 bin centres, the centred delayed-release shapes match the detector footprint strongly and without a circular shift:

- `anti_nu_mu` release: cosine `+0.9569`, registered alignment rank `1/8`;
- delayed total release: cosine `+0.9549`, rank `1/8`;
- `nu_e` release: cosine `+0.9503`, rank `1/8`.

The apparent `anti_nu_mu` win is only `0.0066` above `nu_e`. The two fitted flavor curves themselves have centred cosine `0.99736` in this window. After removing their unequal fitted weights and comparing only their flavor-specific shape difference, the detector cosine falls to `0.1341` and the alignment ranks `8/8`.

**Therefore the recovered child is the common delayed-release component, not a resolved `nu_e` or `anti_nu_mu` identity.** In ARA language, the detector contains a clear projection of the joint neutral-child branch through its positive/ridge/negative relation, but this cut has not decompressed the two neutral children from each other.

## Comparison with the muon parent

The derived remaining-muon and released-muon complements reach absolute cosine about `0.70–0.73`, but their registered alignment ranks `2/8`, not first. The reversed release-gradient and remaining-parent-curvature components reach about `0.769` and rank `1/8`, but neither beats the whole delayed-release branch. This is consistent with a downstream release footprint while failing the stronger claim that the detector isolates a derivative-only or curvature-only child.

Across the 326 saved T402 resampling probes, the selected relation has median cosine `0.315`, 95% resampling interval `[-0.660, 0.814]`, and only `15.95%` of splits reach absolute cosine `0.65`. Its orientation agrees with the aggregate result in `72.09%` of splits. The match is consequently stable as an aggregate population shape, not as a split-level or individual-event reconstruction.

## Search in earlier muon tests

- **T398/T400:** contains the strongest same-archive match. This is the delayed joint-neutrino release branch and its fitted children.
- **T397:** the fitted 160 G W phase has absolute cosine `0.723`, but the registered alignment ranks only `3/8`; the observed trace is weaker. T397 is a different medium, detector and experiment, so this is shape comparison only and does not establish ancestry.
- **T395/T396:** excluded from waveform scoring. They contain successful truth-model parent/child statistical locks, not observed temporal waveforms.

## What the detector waveform is—and is not

The visible T402 curve is a detector response contrast, `C-AC`, not a pristine neutrino field waveform. Its useful components are:

- early detector enrichment while the delayed branch is above its within-window average;
- a handover near the local ARA ridge;
- late detector depletion as the branch returns.

This result does not identify the birth time of an individual neutrino, resolve both neutrino flavors event by event, or show that the T397 silver spin phase directly caused the COHERENT delayed branch.

## Best next cut

Use an independent detector/source archive to freeze the three T402 landmarks and test whether its measured detector residual again follows the independently supplied delayed-release source template. To separate the two neutrino children, the next dataset must contain flavor-sensitive information or an independently observed charged-daughter relation; timing alone leaves the two fitted flavor shapes almost collinear in this window.
