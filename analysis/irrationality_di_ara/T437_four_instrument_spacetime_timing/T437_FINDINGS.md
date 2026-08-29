# T437 findings — four ARA timing instruments on SXS:BBH:0305

## Outcome

T437 compared three previously defined Irrationality Di-ARA instruments with an
experimental reverse-facing Rationality reconstruction.  The prediction
artifact was written and SHA-256 sealed before the common-horizon answer was
opened by the scorer.

Only the **state** clock landed within one local parent waveform cycle:

| Clock | Signed error | Absolute error in parent cycles | Result |
|---|---:|---:|---|
| State Irr-Di-ARA | `+7.2517 M` | `0.6377` | close, but exact power-crest crosswalk |
| Path/history Irr-Di-ARA | `-173.3933 M` | `15.2487` | not supported as event clock |
| Dynamic Irr-Di-ARA, unchanged T436 | `-99.2437 M` | `8.7278` | not supported |
| Reverse Rationality reconstruction | `-200.5316 M` | `17.6353` | not supported |
| T435 frozen median baseline | `+37.5422 M` | `3.3016` | outside one cycle |

The state read is exactly the waveform-power maximum.  It therefore recovers a
real timing landmark in ARA language but does not constitute an independent
new clock.  The state selection also used its preregistered fallback because
the full expansion-to-contraction crossing occurs after the eligible pre-crest
basin.

## What the other instruments did recover

The path/history and reverse Rationality coordinates were not arbitrary noise.
Their selected geometric distances were `0.5486` and `0.4250`; deterministic
chronology shuffling increased these to `1.8791` and `1.7972`.  The instruments
therefore retain ordered path structure.

What failed was **event specificity**.  The black-hole chirp remains highly
coherent over many windows (`rho` is near one), while the address-openness
coordinate repeatedly crosses its ridge.  The same path relation can describe
many ordered sections of the waveform, so its internally strongest boundary is
not the first common horizon.

The reverse-facing result directly tests the suggestion that a settled event
may be easier to reconstruct from its Rationality side.  Under the frozen
future-window implementation, it is not: the reconstructed boundary is about
`200.5 M` early.  This rules out this specific mirror instrument, not every
possible Rationality definition.

## ARA interpretation

- **State Di-ARA** describes the local expansion/contraction state and reaches
  its useful ridge at the ordinary amplitude crest.
- **Path/history Di-ARA** records whether the route is reused/open and
  determined/unresolved.  Here it sees a coherent evolving route but lacks the
  second relation needed to identify the merger handover uniquely.
- **Dynamic Di-ARA** remains a failed transfer from the muon instrument; it was
  deliberately not repaired after T436.
- **Reverse Rationality** gives a cleaner internal distance than the forward
  path read, but cleaner closure geometry is not the same as the correct event
  time.

## Boundary and next test

Only one SXS collision is archived locally, so T437 is a one-event calibration.
Do not tune another boundary on BBH:0305.  The next meaningful test is to obtain
several additional SXS simulations, freeze the state/crest and path instruments
on a development subset, and test untouched systems.  The specific unresolved
question is whether ARA can predict the system-dependent offset between first
common-horizon formation and the waveform amplitude crest.

## Files

- frozen method: `T437_FROZEN_PROTOCOL.md`
- sealed prediction: `results/T437_WAVEFORM_ONLY_FOUR_INSTRUMENT_CLOCKS.json`
- scored result: `results/T437_SCORED_RESULT.json`
- visual audit: `results/T437_FOUR_INSTRUMENT_TIMING_AUDIT.png`
- portable report: `results/T437_FOUR_INSTRUMENT_TIMING_REPORT.html`
