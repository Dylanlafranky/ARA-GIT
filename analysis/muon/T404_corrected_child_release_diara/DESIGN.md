# T404 report design

## Decision and audience

The report must let the framework author and a technical reviewer answer four questions without reading source code:

1. Was T403's `0.532` release landmark real?
2. Does an exact `0.5 -> 1.0` octave replicate after correcting the coordinate?
3. What two-axis Di-ARA is actually visible in the population data?
4. Can the current public inputs test one individual spinning muon?

## Reading order

1. Answer-first summary and verdict.
2. Coordinate correction visual.
3. Three-stage landmark visual across all registered bandwidths.
4. Exact-octave residual and bootstrap uncertainty.
5. Storage-flow Di-ARA phase portrait.
6. Corrected detector/source profiles.
7. Gates, evidence classes, limitations, and individual-event boundary.

## Chart map

- `coordinate_map`: correct cumulative-ARA inverse versus T403's linear assumption.
- `landmark_sequence`: detector turn, source release maximum, and detector handover for every registered KDE bandwidth.
- `octave_residual_hist`: saved-split robustness distribution of `ridge - 2 x detector crest`.
- `storage_flow_diara`: remaining-parent storage versus delayed-child release flow, coloured by ordered stage.
- `corrected_profiles`: centred detector and fitted-source curves sampled at the corrected bin times.

## Semantic rules

- ARA coordinates always show an explicit `0-2` label.
- The parent/local ridge is marked at `1.0` where relevant.
- Exact octave is marked at residual `0`, not implied by visual proximity.
- Measured detector, fitted source, derived state, resampling, and independent holdout evidence remain separately labelled.
- The Di-ARA axes are visibly described as normalized derived axes; their shape is not presented as independent confirmation.
- The report must say that T397 is aggregate muSR, not an individual event link.
