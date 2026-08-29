# T398 — population neutrino wave-overlap findings

**Executed:** 2026-08-17  
**Protocol SHA-256:** `8aee1b49cb564e7f2af3726cb52d4732c463352dea67f98e6624509333a57d83`  
**Verdict:** **POPULATION NEUTRINO RELEASE WAVEFORM OBSERVED; INDIVIDUAL BIRTH UNOBSERVED**

## Plain-language answer

We had already detected the delayed neutrino population in T371/T372, but we
had not placed the full sequence into one evidence-graded view. T398 now does
that.

The official COHERENT source template shows a prompt muon-neutrino branch,
followed by the delayed electron-neutrino plus anti-muon-neutrino branch from
the stopped-muon population. The two fitted rates are equal at
`0.6360822416 microseconds`; this is the dotted handover line in the report.
The delayed curve then remains dominant as it decays through the rest of the
six-microsecond window.

This is a population waveform. The data still do not attach one named muon to
the exact two neutrinos it produced, so the result does not show an individual
neutrino's instant of birth.

## Main numbers

### Primary COHERENT 2022 CsI source

- fitted prompt `nu_mu`: `60.18235`, 95% interval
  `[32.41801, 89.19976]`;
- fitted delayed `nu_e + anti_nu_mu`: `258.94245`, 95% interval
  `[187.91715, 333.29511]`;
- removing the delayed branch costs `57.68352` AIC units;
- prompt 0.5-microsecond-bin peak: `0.25 microseconds`;
- delayed 0.5-microsecond-bin peak: `0.75 microseconds`;
- native rate-equality handover: `0.6360822416 microseconds`;
- T372 bootstrap interval for the handover: `[0.51970717, 0.70263430]`
  microseconds;
- cumulative 0–2 ARA coordinate at rate equality: `0.43740278`.

The last point is important. Instantaneous equality of the prompt and delayed
flows occurs before the cumulative parent ridge. These are two different ARA
cuts and must not be collapsed into one landmark.

### Delayed neutral children

Reopening the official flavor-resolved source file and applying the frozen
T371 response yields:

- `nu_e`: `38.721997%` of the detector-weighted delayed template;
- `anti_nu_mu`: `61.278003%`;
- pointwise flavor-child closure error: exactly `0.0` in the saved artifact.

These are source-template components. The CsI events are not flavor-tagged
individually.

### Independent COHERENT 2017 CsI holdout

- fitted prompt `nu_mu`: `33.69769`, 95% interval
  `[16.41925, 55.12611]`;
- fitted delayed `nu_e + anti_nu_mu`: `79.56754`, 95% interval
  `[30.19199, 128.54840]`;
- prompt peak: `0.75 microseconds`;
- delayed peak: `1.25 microseconds`;
- fitted equality: `1.03941893 microseconds`.

The holdout therefore repeats positive prompt and delayed populations in the
correct order. Its original T378 boundary remains unchanged: not every frozen
high-stringency exact-handover gate passed.

## Evidence layers

1. **Measured:** beam-coincident and anti-coincident CsI event counts.
2. **Fitted:** prompt and delayed population components required by those
   counts.
3. **Template-resolved:** separate expected `nu_e` and `anti_nu_mu` children.
4. **Derived:** remaining-muon fraction from the unreleased delayed-template
   tail and its cumulative-release complement.
5. **Separate comparison:** T397 RAL Silver spin phase. It is not part of the
   COHERENT event record and was not used in the reconstruction.

## Validation

All eight frozen T398 gates passed. An independent saved-artifact validator
also passed all eleven checks, including:

- exact protocol hash;
- 1,200-row native ledger and strictly increasing time;
- 5 ns display reconstruction of the 1 ns handover to within
  `5.70e-7 microseconds`;
- exact neutral-child closure;
- exact remaining-plus-released complement;
- correct prompt/delayed order in T371 and T378;
- explicit separation of the T397 source;
- preservation of the individual-event claim boundary.

## What the visual means in ARA language

The plot shows a source-side prompt branch losing dominance to a delayed
release branch. The dotted line marks equal instantaneous contribution from
those two fitted populations. The smooth remaining-muon curve is a useful ARA
bookkeeping view of unreleased delayed capacity, but it is derived from the
same delayed template and is not a second observation.

The separate `nu_e` and `anti_nu_mu` curves are the two delayed children. They
overlap in time because they are produced by the same stopped-muon population,
while differing in detector-weighted share. Their sum restores the delayed
parent branch.

## Boundary and next decisive test

T398 does not yet show one muon spinning, reaching a handover, and producing
its own two neutrinos. That requires an event-linked archive with all of the
following in the same record:

1. parent-muon spin or direction before decay;
2. charged-daughter energy and direction;
3. neutral-sensitive timing or missing momentum;
4. an event key joining those measurements.

That is the next experiment capable of turning a population release waveform
into an individual Information-cubed handover test.

## Primary artifacts

- `analysis/muon/T398_population_neutrino_wave_overlap/T398_POPULATION_NEUTRINO_WAVE_OVERLAP_REPORT.html`
- `analysis/muon/T398_population_neutrino_wave_overlap/T398_POPULATION_NEUTRINO_WAVE_OVERLAP_PREVIEW.png`
- `analysis/muon/T398_population_neutrino_wave_overlap/T398_RESULTS.json`
- `analysis/muon/T398_population_neutrino_wave_overlap/T398_VALIDATION.json`
- `analysis/muon/T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv`

