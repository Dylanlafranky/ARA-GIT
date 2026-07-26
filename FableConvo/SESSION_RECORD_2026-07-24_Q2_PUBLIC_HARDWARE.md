# Session Record — Q2 Public-Hardware ARA Test

**Date:** 24 July 2026  
**Ledger entry:** T259  
**Status:** Completed; strong two-cut claim **NOT SUPPORTED** (`4/7` frozen gates)

## Why this test was run

Q1 showed, in a controlled synthetic open-qubit instrument, that several measured cuts can preserve distinctions
lost by one compressed diameter. Q2 asked the harder next question: does the same two-cut advantage survive on
untouched public experimental hardware data?

The selected source was Arnold and Werner et al., *All-optical superconducting qubit readout*:

- paper DOI: `10.1038/s41567-024-02741-4`;
- public data DOI: `10.5281/zenodo.14033026`;
- archive: `AllopticalSCQreadout_data.zip`;
- local archive SHA-256:
  `73F3E2CA7B3658452B4C171532C751E96D7392DCB8741B87A18E28C7073D67FD`.

The archive provides raw I/Q shots for six optical-pulse repetition conditions, plus second-readout and
prepared-file replications. I and Q are receiver quadratures. They are not Bloch X/Y/Z axes, so this test concerns
readout-output geometry rather than full state tomography.

## Freeze and leakage control

Before numerical shot values were opened, only public metadata, file names, array shapes and types were inspected.
The fidelity statement, protocol, hashes, seven gates and T259 ledger entry were then frozen.

Each of the six hardware conditions was held out in full. The other five conditions alone selected the one-cut
axis and fitted centring, scale, orientation and covariance. Source-provided thresholds, angles and fidelity fields
were prohibited.

Primary comparison:

1. training-selected native I-or-Q one-cut LDA;
2. two-cut ARA-coordinate LDA;
3. independently implemented raw I/Q LDA as an equal-information control.

The frozen protocol also required pole reversal, complement, label-shuffle and shot-pair-destruction controls.

## Primary result

Across `600,000` untouched target classifications:

| Quantity | Result |
|---|---:|
| Two-cut ARA balanced accuracy | `0.882808` |
| Training-selected one-cut balanced accuracy | `0.882838` |
| ARA gain | `-0.000030` |
| Gain in percentage points | `-0.0030` |
| Paired 95% interval | `[-0.000147,+0.000050]` |
| Worst held-out-condition ARA accuracy | `0.758340` |
| Q-only balanced accuracy | `0.578943` |
| Frozen gates passed | `4/7` |

Every outer fold selected I. The useful class separation was already almost entirely aligned with that one native
axis. Adding Q therefore supplied no held-out advantage.

The same boundary repeated:

| Registered arm | Two-cut ARA | Selected one cut | Gain |
|---|---:|---:|---:|
| Primary first readout | `0.882808` | `0.882838` | `-0.000030` |
| Second readout | `0.844917` | `0.845145` | `-0.000228` |
| Prepared first readout | `0.860245` | `0.860713` | `-0.000468` |
| Prepared second readout | `0.819055` | `0.819525` | `-0.000470` |

QDA produced only small improvements, consistent with mild cloud non-linearity rather than missing linear
two-cut information.

## Two distinct conclusions

### Strong information-gain claim

**Not supported.** The two decisive gain gates failed:

- gain was below the frozen `+0.005` threshold;
- the paired confidence interval did not lie above zero.

The result must not be rewritten as a successful two-cut advantage.

### Coordinate translation claim

**Supported as an exact crosswalk.** Independently fitted raw-I/Q LDA and ARA-coordinate LDA produced:

- identical balanced accuracy;
- zero prediction disagreements;
- zero pole-reversal disagreements;
- complement residual `4.44e-16`.

That exact agreement verifies that the chosen ARA 0–2 coordinates preserve the information in the raw two-axis
linear account. It is expected from an invertible affine transformation and is not evidence of new quantum
physics by itself.

## Control correction retained without changing the verdict

The frozen one-shot label-shuffle gate returned balanced accuracy `0.733465` and failed. A post-run audit showed
why this control was under-specified: one random binary relabelling in two dimensions creates an arbitrary small
hyperplane that can align or anti-align with the true I direction. Complementing that shuffle gives approximately
`0.266535`; their paired mean is chance.

The frozen G7 failure remains recorded. No gate was changed after seeing the target. The overall result remains
`4/7` and **NOT SUPPORTED**, because G2 and G3 independently reject the strong claim.

## Secondary dynamics crosswalk

The source's published T1 and Ramsey/T2* observations and fits were also mapped descriptively onto 0–2:

- every T1 fit crossed the `1.0` ridge once;
- the three Ramsey/T2* fits crossed it `11`, `11` and `15` times.

This faithfully distinguishes monotonic relaxation from oscillatory phase evolution. It is not an independent
prediction because source-supplied fit extrema define the coordinate span.

## Scientific meaning

This is a useful boundary result, not a collapse of the broader multi-cut idea:

- Q1 deliberately created identities that shared one cut while differing on transverse cuts;
- Q2's real receiver geometry placed almost all state separation on I;
- decompression cannot recover information that the measured second cut does not contain.

The correct next test is public real tomography with independently measured X/Y/Z axes or randomized measurement
directions. A second valid option is a preregistered receiver-phase experiment that deliberately rotates class
separation away from I and tests when a coupled second cut becomes necessary.

## Reproduction files

- `analysis/quantum/Q2_PUBLIC_HARDWARE_DATASET_AUDIT_2026-07-24.md`
- `analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_FIDELITY_v1.md`
- `analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_PROTOCOL_v1_FROZEN.md`
- `analysis/quantum/q2_public_hardware_iq_test.py`
- `analysis/quantum/q2_public_hardware_iq_validate.py`
- `analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_REPORT_2026-07-24.md`
- `analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_RESULTS.json`
- `analysis/quantum/Q2_PUBLIC_HARDWARE_IQ_VALIDATION.json`
- `analysis/quantum/q2_public_hardware_dynamics_crosswalk.py`
- `analysis/quantum/Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.png`
- `analysis/quantum/public_data/README.md`

Independent output validation passed `19/19` checks.

## Q3 amendment — corrected ridge-normal cut calibration

After the broader ARA geometry was re-centred, Dylan supplied a more precise cut-selection rule:

- for Connection, cut perpendicular to a ridge and seek the appropriate Phase-B direction;
- for Information, make the same perpendicular cut but seek Phase A;
- retain the dominant mixing order (`Ab`, `aB`, `Ba`, `bA`) rather than flattening the section.

The first numerical implementation was deliberately limited to the already-open Q2 I/Q source. It was classified
before running as a **post-hoc known-source calibration**, not a new blind quantum test.

Training on five hardware conditions defined a covariance-whitened I/Q plane. The equal-class ridge and its
normal were then exact standard Fisher/LDA objects. The normal oriented from ground toward excited was called the
Information-facing Phase-A cut for this local question; its ninety-degree tangent was retained as the Phase-B
control. The sixth condition remained completely held out.

Results:

- Phase-A balanced accuracy: `0.882808`;
- Phase-B/control balanced accuracy: `0.496607`;
- raw-I/Q LDA balanced accuracy: `0.882808`;
- Phase-A/raw-LDA prediction disagreements: `0`;
- mean held-out separation share on Phase A: `0.991162`;
- worst held-out separation share on Phase A: `0.963241`;
- pole-reversal disagreements: `0`;
- calibration gates: `7/7`;
- independent validation: `18/18`.

This adds a clean local operating rule: once the question and ridge are declared, the useful one-dimensional cut
is the ridge normal, while the tangent is a genuine negative control. The result also explains why Q2 gained
nothing from native Q: the useful class direction was already almost entirely one-dimensional.

The strict boundary remains important. The normal/LDA equality is guaranteed by the standard mathematics, and
the source was already open. The empirical part is that the training-defined normal remained stable across the
six held-out hardware conditions. The next evidential rung must apply the frozen rule to a fresh public quantum
source with independent measurement directions or deliberately changing readout orientation.
