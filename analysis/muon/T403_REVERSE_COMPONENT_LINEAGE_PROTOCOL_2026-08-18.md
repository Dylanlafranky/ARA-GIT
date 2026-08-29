# T403 — Reverse component lineage: detector child back through the muon parent

Date frozen: 2026-08-18

## Question

Can the signed delayed-neutrino detector footprint recovered in T402 be identified as a component of an upstream waveform already present in the muon programme, when the comparison is made from child to parent rather than parent to child?

## Who, what, when, where, why and how

- **Who:** the COHERENT CsI delayed-neutrino detector footprint from T402; the fitted stopped-muon delayed branch and its `nu_e` and `anti_nu_mu` children from T398/T400; and the independent RAL Silver muon phase trace from T397 as a separate exploratory comparison.
- **What:** compare component shapes rather than raw amplitudes: parent release, parent remaining, release gradient, remaining-parent curvature, flavor contrast, and the independent spin-phase residue.
- **When:** every same-archive source candidate is sampled at the eight fixed T402 local-child bin centres between T400's frozen left and right boundaries. The T397 phase trace remains on its own 0–2 cycle.
- **Where:** detector child -> delayed-neutrino source branch -> stopped-muon parent. T397 is displayed beside this path but is not inserted into it as an event-linked step.
- **Why:** a downstream detector need not preserve the whole parent waveform. It may preserve a signed component such as accumulation versus release, a child contrast, or a change in flow.
- **How:** centre and L2-normalise every candidate, score fixed direct and fixed reversed orientation against T402's frozen eight-bin `C-AC` vector, and compare the registered alignment with all non-zero circular shifts. No fitted continuous time shift, amplitude, offset or smoothing parameter may be used to declare a match.

## Frozen inputs

1. `T402_whole_shape_child_relation/T402_BIN_SUMMARY.csv`
2. `T402_whole_shape_child_relation/T402_RESULTS.json`
3. `T400_nested_child_window_population_to_event/T400_RESULTS.json`
4. `T398_population_neutrino_wave_overlap/T398_NATIVE_WAVE_OVERLAP.csv`
5. `T398_population_neutrino_wave_overlap/T398_RESULTS.json`
6. `T397_spin_phase_maturity_vs_orientation/T397_PHASE_PROFILES.csv`
7. `T397_spin_phase_maturity_vs_orientation/T397_RESULTS.json`

## Fixed detector vector

Use the eight T402 `C` rows ordered by `bin_center` and their `mean_C_minus_AC` values. T402 already established that this vector is a robust signed source-difference axis but not an exact reflected whole waveform.

## Fixed same-archive candidates

At each T402 bin centre, convert local ARA coordinate to time using T400's frozen linear map

\[
t(x)=L+\frac{x}{2}(R-L).
\]

Interpolate the T398 native curves and form:

1. delayed total release rate, centred;
2. `nu_e` release rate, centred;
3. `anti_nu_mu` release rate, centred;
4. flavor contrast `anti_nu_mu - nu_e`, centred;
5. remaining-muon fraction, centred;
6. released-muon fraction `1 - remaining`, centred;
7. first gradient of delayed total release with respect to local ARA;
8. second gradient of remaining-muon fraction with respect to local ARA.

The last two are component tests. Because the T398 remaining-muon curve is derived from the delayed template, they are algebraically related and do not constitute independent confirmations.

## Fixed T397 exploratory comparison

For each available field, average the observed and predicted W-channel phase profiles into eight equal phase bins. Centre and L2-normalise them. Because the T397 phase origin is not linked to COHERENT event time, report:

- direct and reversed cosine only as descriptive values;
- best rigid circular orientation and its rank;
- whether the candidate has the same broad one-positive/one-negative topology.

No T397 resemblance may be classified as an event-level lineage match.

## Scores and gates

For candidate vector `c` and detector vector `d`:

\[
s_{direct}=\hat d\cdot\hat c,
\qquad
s_{reverse}=\hat d\cdot\widehat{c[::-1]}.
\]

For each orientation, rank the registered zero-shift absolute cosine among all eight circular shifts; rank 1 is best.

- **G1 — detector integrity:** the reproduced T402 vector and landmarks equal the saved T402 result.
- **G2 — component selection:** at least one same-archive candidate has absolute registered cosine >= 0.65.
- **G3 — alignment control:** the selected candidate's registered orientation ranks 1/8 against circular shifts.
- **G4 — derivative specificity:** the selected component candidate beats both whole positive rates (`nu_e`, `anti_nu_mu`, delayed total) by at least 0.10 absolute cosine.
- **G5 — evidence boundary:** any T397 comparison remains explicitly separate, and no result is described as an individual-neutrino birth waveform.

## Interpretation classes

- **Component located:** G1–G5 pass. The detector footprint is consistent with one registered upstream component on this archive and coordinate.
- **Partial component relation:** G1, G2 and G5 pass, but alignment or specificity fails. A component resemblance exists without unique lineage identification.
- **Not located:** G1 and G5 pass but G2 fails.
- **Invalid:** G1 or G5 fails.

## Claim boundary

This is a reverse lineage audit across saved population and detector-response products. Even a positive result identifies a component relation, not the complete neutrino wave, not a direct measurement of neutrino flavor per event, and not the birth time of neutrinos from one named muon. T397 is a different medium, detector and experiment.
