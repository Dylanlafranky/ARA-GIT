# T305 — ARA Phi Temporal Carrier: Known Calibration and Muon-Fusion Schedule

**Date:** 30 July 2026  
**Frozen verdict:** **MIXED — 2/3 substantive gates passed**  
**Validation:** **15/15 independent checks passed**

## Result first

The test found a real distinction between **local closure** and a
**continuously unfolding carrier**.

- Exact Phi was the best predeclared **forward fixed carrier** for geometric
  coverage across unknown prefix lengths.
- Exact Phi was also the best forward fixed carrier for **mean robust
  Fusion-overlap**, beating `3/8` in `96.17%` of the `183` family-prefix
  comparisons.
- Phi did **not** win the harshest across-prefix lower-tail test. `1/e` won
  that endpoint.
- The reverse Phi orientation had the best mean of every fixed carrier,
  although it was frozen as an orientation control and cannot rescue the
  primary forward prediction.
- The known-horizon uniform schedule remained the overall ceiling, as it
  should when the final pulse count is supplied in advance.

This is encouraging evidence for Phi as a robust non-repeating scheduling
carrier in the tested model. It is not evidence that natural Fusion contains
a Phi clock.

## Plain-language explanation

Imagine repeatedly placing pulses around a circular time window.

`3/8` visits eight positions and then starts landing on the same positions
again. It is therefore a useful **closed local pattern**, but a poor rule for
an indefinitely continuing schedule. By pulse 64, its 64 delivered pulses
cover only the same eight temporal slots. Most later pulse energy is
overlapping earlier pulse energy.

Phi does not close into a short repeating pattern. As more pulses arrive, it
keeps filling unused parts of the time circle. This is very close to Dylan's
proposed temporal-tension distinction:

- local rational closure can define a connected state;
- a larger Time-side carrier needs to avoid repeatedly occupying its old
  path.

Phi did that best on the average endpoints frozen here. It was not uniquely
best under every possible definition of robustness, because `1/e` protected
the single worst tail slightly better.

## ARA and established-physics views side by side

| ARA view | Scheduling / Fusion view |
|---|---|
| One parent cycle is the `0 -> 1` directed half of an ARA sphere. | One normalized observation window is the pulse-scheduling circle. |
| The carrier advances by a fixed relation \(\alpha\). | Pulse \(k\) is placed at \(\operatorname{frac}(k\alpha)\). |
| Reoccupying the same temporal path creates temporal tension / locking. | A rational step repeats after its denominator and later pulses overlap earlier pulses. |
| A non-closing Time-side carrier should preserve usable handovers across unknown prefixes. | A low-discrepancy irrational sequence keeps filling new gaps without knowing the final pulse count. |
| The local `3/8` connection form and the Phi carrier need not be the same coordinate. | `3/8` can be a compact eight-site pattern while Phi is a non-repeating streaming schedule. |
| Fusion usefulness depends on coupling to the stuck-muon population. | The tested quantity is \(f_X=\int g(t)C(t)\,dt\), the field–population overlap factor. |

## Known comparisons

### Exact implementation controls

Noiseless sequences generated at Phi, reverse Phi, `3/8`,
`\sqrt2-1` and `1/3` were all recovered to the frozen numerical tolerance.
This confirms that the directed-carrier coordinate measures the rule supplied
to it. It does not favour Phi.

### Public physical calibration

The already-open T302 Arabidopsis calibration remains unchanged:

- confirmation wild-type center: `0.387492`;
- distance from `phi^-2`: `0.005526`;
- local one-step winner: `3/8`;
- cumulative-position winner: exact Phi.

That known system supplied the calibration pattern we wanted: rational local
placement and Phi cumulative transport can separate. Because golden-angle
phyllotaxis was already known, it is calibration rather than discovery.

## Fusion experiment

For every prefix from `N=4` through `64`, every candidate received:

- the same number of delivered pulses;
- the same fixed pulse width `0.15/64`;
- the same pulse peak and energy per pulse;
- the same `128` unknown source phases.

The fixed width is important. A schedule that does not know when it will stop
cannot redesign all its earlier pulses after learning the final `N`.

The idealized arrival families were stationary, seven-cycle beam, coupled
seven/twenty-three-cycle beam, and seven-cycle beam under a muon-decay
envelope. The non-flat families supplied the primary Fusion endpoints.

## Main numbers

| Carrier | Mean geometric rank ↓ | Mean robust \(f_X\) ↑ | Lower-tail \(f_X\) ↑ | Total overlap loss |
|---|---:|---:|---:|---:|
| known-horizon uniform oracle | — | **0.078888** | 0.011600 | 0 |
| reverse Phi | control | **0.077722** | 0.013765 | 0 |
| **Phi forward** | **1.9713** | **0.077485** | 0.011726 | 0 |
| `1/e` | 3.0246 | 0.077095 | **0.013788** | 0 |
| `sqrt(2)-1` | 2.3074 | 0.076051 | 0.011358 | 0 |
| `3/8` | 5.8525 | 0.015477 | 0.012582 | 3.740625 |

The exact Phi forward schedule retained `98.22%` of the oracle's mean robust
overlap. Reverse Phi retained `98.52%`.

At the full 64-pulse prefix:

| Carrier | distinct union coverage | available coverage if no overlap |
|---|---:|---:|
| Phi | 0.15000 | 0.15000 |
| reverse Phi | 0.15000 | 0.15000 |
| `1/e` | 0.15000 | 0.15000 |
| `sqrt(2)-1` | 0.15000 | 0.15000 |
| `3/8` | **0.01875** | 0.15000 |

The `3/8` result is not a generic condemnation of that landmark. It is the
expected consequence of using a denominator-eight closure as an indefinitely
repeated scheduling carrier.

## Frozen gates

| Gate | Result |
|---|---|
| G0 exact controls and numerical integration | **PASS** |
| G1 unknown-prefix geometric coverage | **PASS — Phi** |
| G2 mean robust Fusion overlap | **PASS — Phi** |
| G3 harsh across-prefix lower tail | **FAIL — `1/e`** |
| G4 stationary null | **PASS** |

The strict frozen verdict is therefore **MIXED**, not supported in full.

## The directional clue

Dylan had already assigned:

- `0.381966` to the Space-side landmark;
- `1.618034` to the Time-side mirror on the ARA `0–2` diameter.

On the unit scheduling circle, that Time-side orientation is the frozen
`phi_reverse = 0.618034` control. It produced the best mean robust overlap of
all fixed carriers. The source families explain why direction can matter:

- the pure seven-cycle source was exactly mirror-neutral;
- the coupled seven/twenty-three-cycle source usually favoured forward Phi;
- the decay envelope more often favoured reverse Phi.

This is a useful directional clue, but it is not promoted to a primary pass
after seeing the result. A future experimental or independently simulated
test should freeze the `1.618034` Time-side direction as primary beforehand.

## What this adds to the framework

The strongest framework result is not merely “Phi scored well.” It is that
the test numerically separated two roles that had been getting flattened:

\[
\underbrace{3/8}_{\text{short rational closure}}
\quad\neq\quad
\underbrace{\phi^{-2}\text{ or }\phi^{-1}}_{\text{unfolding carrier}}.
\]

That matches the recent ARA distinction between:

1. a locally connected/closed child arrangement;
2. the larger carrier moving that completed identity through later slices.

The result also resists the claim that Phi is automatically optimal. It lost
the lower-tail gate to another irrational carrier, `1/e`, and the oracle still
won when future horizon knowledge was allowed.

## Scientific boundary

The public Kou-Chen work defines the external contribution as

\[
R_X=f_XP_X\eta_X.
\]

T305 tests only scheduling effects on \(f_X\). It does not measure:

- the microscopic stripping probability \(P_X\);
- post-stripping recycling \(\eta_X\);
- a real stuck-muon arrival train;
- net Fusion yield or energy gain.

The source paper itself treats its benchmark regimes as model scenarios and
states that a fully time-dependent treatment would require coupled rate
equations. The decisive next step is therefore a time-resolved experimental
or validated transport record, with the carrier direction and stopping rule
frozen before exposure.

## Reproduction

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\t305_phi_temporal_carrier_fusion.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\validate_t305_phi_temporal_carrier_fusion.py'
```

Artifacts:

- frozen protocol:
  `T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_PROTOCOL_v1_FROZEN.md`;
- full prefix table:
  `T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_PREFIX_RESULTS.csv`;
- candidate summary:
  `T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_SUMMARY.csv`;
- machine-readable result:
  `T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_RESULTS.json`;
- independent validation:
  `T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_VALIDATION.json`;
- figure:
  `T305_ARA_PHI_TEMPORAL_CARRIER_FUSION.png`.

