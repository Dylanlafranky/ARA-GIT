# T373 — Independent liquid-argon child-half handover transfer

**Frozen:** 2026-08-13 (Australia/Brisbane), before calculating the argon branch handover or fitting the argon event cube.

## Question

Does the T372 prompt/delayed child-handover construction transfer from COHERENT CsI to the independent COHERENT CENNS-10 liquid-argon release, after allowing the detector-specific parent asymmetry to move the handover away from the pure child-half landmark `x = 0.5`?

This is a prospective transfer of an already formulated coordinate to previously inspected public data. It is not a fully blind data-source test: the argon release was inspected during T371 and rejected there for unsafe timing-only inference. The present 3D energy × pulse-shape × time fit and its handover score were not previously run.

## Who / what / when / where / why / how

- **Who:** prompt pion-lineage CEvNS and delayed muon-lineage CEvNS in the CENNS-10 argon detector.
- **What:** their rate-equality handover and the cumulative ARA position of that handover.
- **When:** the native released 0.5 microsecond timing bins.
- **Where:** the full released 3D event cube, retaining recoil-energy and pulse-shape information to separate signal from neutron and steady-state backgrounds.
- **Why:** an external detector/target must reproduce the relational handover if T372 describes the source lineage rather than a CsI display artefact.
- **How:** derive a frozen prompt/delayed branch split from the released CEvNS model only; then estimate the two branch amplitudes from event counts with the published background families and compare the measured handover with the frozen prediction.

## Source files

Official COHERENT liquid-argon release cached at:

`F:/SystemFormulaFolder/external_data/coherent_argon_3903810/`

Files used:

- `datanobkgsub.txt` — observed 3D counts;
- `cevnspdf.txt` — released CEvNS signal template;
- `brnpdf.txt` — prompt beam-related neutron template;
- `delbrnpdf.txt` — delayed beam-related neutron template;
- `bkgpdf.txt` — steady-state background template;
- `LArParametersAnlA.yaml` — source timing and pre-fit background constraints.

## Frozen construction

### 1. Model-side branch decomposition

At each energy × pulse-shape cell, decompose the released CEvNS timing vector as a non-negative sum of two frozen source-timing bases:

- prompt basis: SNS proton-pulse Gaussian convolved with the charged-pion lifetime;
- delayed basis: that prompt lineage convolved with the positive-muon lifetime.

Use the released proton-pulse mean `0.440 microseconds` and width `0.150 microseconds`; use established lifetimes `tau_pi = 0.026033 microseconds` and `tau_mu = 2.1969811 microseconds`. Integrate both bases over the native time-bin edges and truncate/renormalize only to the released observation window. Non-negative least squares is applied independently to every energy × pulse-shape cell. No event counts enter this decomposition.

The summed decomposed branches define the frozen model prediction:

1. Find the first post-prompt equality `r_P(t) = r_D(t)` by linear interpolation of their native-bin rates.
2. Compute

   `x_H = 2 * cumulative_signal(t_H) / total_signal`.

3. Record `Delta_H = x_H - 0.5` and the predicted prompt share.

### 2. Event-side measurement

Fit the complete 3D observed counts with five non-negative components:

1. prompt CEvNS branch;
2. delayed CEvNS branch;
3. prompt beam-related neutrons;
4. delayed beam-related neutrons;
5. steady-state background.

Use Poisson likelihood for the count cube. Background amplitudes receive the pre-fit Gaussian constraints frozen in `LArParametersAnlA.yaml`: prompt BRN `497 +/- 160`, delayed BRN `33 +/- 33`, steady state `3154 +/- 25`. Prompt and delayed CEvNS amplitudes are free and receive no signal-normalization prior.

The event-side handover is calculated from the fitted prompt and delayed branch rates with the same equality and cumulative formula used for the prediction.

### 3. Uncertainty

Run a deterministic-seed parametric bootstrap from the fitted five-component count model. Refit every replicate and calculate prompt share, `t_H`, `x_H` and `Delta_H`. Report percentile 95% intervals and failure rates for non-identifiable/no-crossing replicates.

## Frozen gates

Primary gates:

1. **Transfer gate:** the frozen model-predicted `x_H` lies inside the event-fit 95% bootstrap interval.
2. **Identifiability gate:** at least 80% of bootstrap replicates produce finite prompt and delayed amplitudes and a post-prompt equality crossing.
3. **Mixture-information gate:** freeing the prompt/delayed signal ratio must improve or match the fixed published-ratio model; report the likelihood-ratio statistic without treating a boundary-sensitive asymptotic p-value as exact.

Secondary, separately reported:

4. **Pure child-half gate:** whether `x = 0.5` lies inside the event-fit 95% interval.
5. **Direction gate:** measured and predicted `Delta_H` have the same sign.

## Interpretation boundary

- Passing the transfer gate supports the T372 statement that the handover is a detector/identity-specific displacement around the child-half landmark.
- It does not establish a universal correction law, because the prediction uses the released argon signal model.
- If the event cube cannot identify the two CEvNS branches, the result is `INCONCLUSIVE`, not a failure of ARA geometry.
- If the mixture is identifiable but excludes the predicted handover, the T372 transfer claim fails on this detector.
- The pure `x = 0.5` claim is not substituted for the asymmetry-adjusted prediction.

