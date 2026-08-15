# T378 — independent 2017 CsI muon-handover holdout

**Frozen:** 14 August 2026, after source/schema and aggregate-count inspection,
but before signal-template construction, component fitting or control scoring  
**Evidence class:** public physical holdout; known-decay recovery/crosswalk  
**Relationship to T371/T372:** same solid CsI[Na] detector family and same
stopped-pion source identity, but the earlier 2017 exposure/release rather than
the 2021 event record used for T371/T372

## Who, what, when, where, why and how

- **Who:** the prompt `nu_mu` branch from stopped positive-pion decay and the
  delayed `nu_e + anti-nu_mu` branch from the subsequent positive-muon decay.
- **What:** the ensemble two-branch handover recovered from independently
  released coincidence and anti-coincidence count cells. This is not a linked
  prediction of one private muon decay.
- **When:** `0 <= arrival time < 6 microseconds`, in the released 0.5-us bins.
- **Where:** `6 <= PE < 30` in COHERENT's CsI[Na] detector, using the 2017
  Science exposure (`7.47594 GW hr`).
- **Why:** this is the closest public holdout to the clean T371 instrument: a
  separate exposure with the same connection-heavy solid medium, native timing
  separation and released prompt/delayed source PDFs.
- **How:** fit beam-on coincidence and anti-coincidence cells jointly with four
  separately retained components: steady background, prompt SNS neutrons,
  prompt pion-neutrino release and delayed muon-neutrino release. Only after the
  physical fit is frozen are the two fitted branch yields compressed to ARA.

## Source and independence

- COHERENT Collaboration data release for `arXiv:1708.01294`, Zenodo record
  `10.5281/zenodo.1228631`.
- Required files: all four beam-on/off coincidence/anti-coincidence grids,
  prompt and delayed neutrino timing PDFs, prompt-neutron timing and PE PDFs,
  detector parameters and companion documentation.
- SHA-256 hashes of all consumed files will be exported.

## Instrument

### Data boundary

The primary observation is the beam-on 12-time-bin by 12-energy-bin
coincidence grid. The beam-on anti-coincidence grid constrains the steady
background. The beam-off coincidence/anti-coincidence pair is processed
identically as a negative control.

### Component construction

1. **Steady background:** factorised PE and time marginals from the released
   anti-coincidence record, with its normalization constrained by the joint
   anti-coincidence likelihood.
2. **Prompt neutrons:** released PE and timing PDFs with the released
   acceptance and `25%` normalization uncertainty.
3. **Prompt neutrinos:** released prompt timing PDF multiplied by a
   detector-response CEvNS PE template.
4. **Delayed neutrinos:** released delayed timing PDF multiplied by its
   detector-response CEvNS PE template.

The CEvNS PE calculation uses only published source spectra, Standard Model
CEvNS kinematics, the released 2017 constant quenching factor, light yield and
acceptance. A time-only fit and reasonable response alternatives are retained
as robustness checks because the energy response is reconstructed rather than
released as a ready-made template.

## ARA measurement

For fitted non-negative prompt and delayed yields `P` and `D`,

```text
x_prompt  = 2 P / (P + D)
x_delayed = 2 D / (P + D)
```

Their sum is forced to two and is bookkeeping only. The instantaneous handover
is the first finite time satisfying

```text
P * prompt_rate(t_H) = D * delayed_rate(t_H).
```

The cumulative release coordinate at that point is

```text
x_H = 2 * integral(start..t_H)(prompt + delayed)
          / integral(start..end)(prompt + delayed).
```

The T372 interval `[0.1787, 0.6916]` and exact child landmark `0.5` are frozen
out-of-sample comparisons, not fitting targets.

## Frozen controls and gates

1. file hashes, data boundaries and counts reproduce;
2. both branch yields have bootstrap 95% lower bounds above zero;
3. full ordered pair improves AIC by at least 10 over each single-branch fit;
4. no more than 10 of 1,000 fixed-seed common time permutations fit as well;
5. delayed crest follows prompt crest;
6. both branches remain positive under time- and PE-bin leave-one-out checks;
7. beam-off data do not reproduce the on-beam pair support;
8. reasonable detector-response and time-only alternatives do not reverse the
   branch order or erase one branch.

## TE-ARA/confound boundary

`x_prompt + x_delayed = 2` cannot establish coupling. Evidence must come from
the observed need for both ordered components, the beam-on/off contrast and
robustness. Prompt-neutron uncertainty, empirical steady-background shape,
finite counts, acceptance, quenching factor, light yield and reconstructed
CEvNS energy response remain explicit `Other` terms.

## Interpretation limit

A pass independently recovers the ensemble handover in a historical solid-CsI
holdout. It does not prove universal ARA, event-link individual particles,
predict one decay time, or independently discover the Standard Model chain.
