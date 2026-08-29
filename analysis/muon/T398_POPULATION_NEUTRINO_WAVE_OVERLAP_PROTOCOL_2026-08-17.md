# T398 — population neutrino wave-overlap protocol

**Frozen:** 2026-08-17  
**Status before execution:** predeclared visual-recovery and source-separation test  
**Question:** can the already recovered stopped-pion/muon branches be placed on one common time axis so that the precursor, handover, and delayed neutrino waveforms are visible without pretending that separate experiments are event-linked?

## Who, what, when, where, why and how

- **Who / identities:** the stopped-pion source, the intermediate stopped-muon population, and the two delayed neutrino children \(\nu_e\) and \(\bar\nu_\mu\) recorded statistically by the COHERENT CsI detector. The prompt \(\nu_\mu\) branch is retained as the source-side sibling. RAL Silver T397 is a different positive-muon population and is only a separate comparison cut.
- **What / ARA cut:** overlay the prompt source branch, an explicitly inferred remaining-muon envelope, each delayed neutrino child, their combined delayed branch, and the cumulative 0–2 ARA traversal. Mark the native instantaneous branch-equality time with a dotted line.
- **When:** \(0\)–\(6\ \mu\mathrm{s}\) after the SNS proton pulse. The primary view uses the 5 ns display sample saved by T372 from the released native timing templates; the measured event-count view remains in the released 0.5 \(\mu\mathrm{s}\) bins.
- **Where / medium:** primary test in the COHERENT CsI[Na] detector at the SNS. The independent holdout uses the earlier COHERENT CsI release. T397 RAL Silver is not merged onto this time axis because it is a different medium, detector and event grain.
- **Why:** the user asked to see whether the neutrino “spawn” and the waves leading to it have actually been observed. The report must distinguish a population-level release waveform from an unobserved individual particle birth.
- **How:** reconstruct the released flavor templates from the official `snsFlux2D.root`, apply the same detector response and fitted normalisations as T371, preserve the T372 native handover, and compare the result with measured binned timing and the independent T378 release.

## Predeclared evidence classes

1. **Measured:** beam-coincident and anti-coincident CsI event counts.
2. **Fitted from measured counts:** prompt \(\nu_\mu\) and delayed \(\nu_e+\bar\nu_\mu\) component yields and time profiles.
3. **Template-resolved:** the separate \(\nu_e\) and \(\bar\nu_\mu\) delayed child profiles. COHERENT CsI does not identify their flavor event by event.
4. **Derived bookkeeping:** remaining-muon fraction, defined as the unreleased tail integral of the fitted delayed template; cumulative release is its complement.
5. **Separate comparison only:** the T397 160 G detector-normalized common-mode spin phase. It cannot be claimed as the precursor of a T371 event.

## Frozen calculations

Let \(r_p(t)\) be the fitted prompt-\(\nu_\mu\) rate and let

\[
r_d(t)=r_{\nu_e}(t)+r_{\bar\nu_\mu}(t)
\]

be the fitted delayed rate. The visual handover time is the already saved T372 native solution

\[
r_p(t_H)=r_d(t_H).
\]

The derived remaining-muon and released shares are

\[
S_\mu(t)=\frac{\int_t^{6\,\mu s}r_d(u)\,du}
                 {\int_0^{6\,\mu s}r_d(u)\,du},
\qquad
R_\nu(t)=1-S_\mu(t).
\]

These two curves are complementary by construction and are not an independent physical confirmation. They expose the bookkeeping implied by the observed delayed template.

## Frozen gates

The population release view passes only if all of the following hold:

1. the reconstructed prompt and combined delayed native profiles reproduce the saved T372 profiles to numerical tolerance;
2. the delayed fitted yield and its 95% interval are strictly positive in T371;
3. removing the delayed branch costs at least 10 AIC units in T371;
4. the delayed crest follows the prompt crest;
5. the native equality time falls inside the saved T372 bootstrap interval;
6. the two flavor-resolved delayed profiles add exactly to the combined delayed branch;
7. the earlier T378 source again resolves positive prompt and delayed populations in the correct time order, even if its stricter frozen handover verdict remains partial;
8. the final language says **population release observed**, not **individual neutrino birth observed**.

## Falsifiers and boundaries

- A delayed profile that is unnecessary, non-positive, or earlier than the prompt source branch falsifies the claimed population sequence on that source.
- Failure to reproduce the saved T372 native profiles indicates an implementation error.
- The test cannot identify one muon and then name the exact neutrinos produced by it.
- The inferred remaining-muon envelope is mathematically coupled to the delayed template and must not be counted as a second independent measurement.
- The separate \(\nu_e\) and \(\bar\nu_\mu\) curves are source-template components, not flavor tags on individual CsI events.
- T397 may illustrate a candidate charged-sector phase cut, but it cannot be overlaid as though it were recorded in the same collision or detector.

## Decision labels

- **POPULATION NEUTRINO RELEASE WAVEFORM OBSERVED:** all eight gates pass.
- **DELAYED POPULATION PRESENT; OVERLAP INCOMPLETE:** delayed events are supported but one or more reconstruction or replication gates fail.
- **NOT SUPPORTED:** the delayed branch is not required or appears in the wrong order.

