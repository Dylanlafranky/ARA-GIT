# T394 — Native neutral pair and causal release findings

**Recorded:** 15 August 2026  
**Protocol:** `T394_NATIVE_NEUTRAL_PAIR_AND_CAUSAL_RELEASE_PROTOCOL_2026-08-15.md`  
**Protocol SHA-256:** `73285D4968422A57CFEC7F78C2A3ABA5FD903B8E460D939C62D1A770E49F10F6`  
**Source DOI:** `10.5281/zenodo.15081911`  
**Source SHA-256:** `B6BB10270E6C604935B47687293470CAEAFD01172288170D83349043566CD05A`  
**Status:** TEST 1 VALIDATED AS A TRUTH-MODEL CROSSWALK; TEST 2 VALIDATED AT POPULATION LEVEL; INDIVIDUAL ADVANCE GATE NOT TESTABLE IN THIS SOURCE

## Answer first

Both requested tests were completed.

1. The two neutrino children form a broad event-level ARA gradient over their
   own `0-2` identity. The pair always closes at `2`, but a fixed
   `(0.5,1.5)` split is not supported. The native mean is
   `(0.923816,1.076184)`, and the split changes systematically with the
   charged-daughter energy.
2. A calibration-only reconstruction of the population release anti-phase
   predicts the untouched tagged-decay time distribution substantially better
   than one fitted exponential. It does not yet predict which individual
   surviving muon releases next because the archive contains no varying
   pre-decay field for an individual muon.

The user's interpretation of Test 2 was therefore correct with one boundary:
we reconstructed the missing population anti-phase from calibration data,
froze it, and checked it against unseen daughter times. The available archive
cannot perform the final individual-muon version of that procedure.

## Test 1 — native two-neutrino identity

### Coordinate

For every frozen truth event,

\[
y_{\nu_e}
=
\frac{2E_{\nu_e}}{E_{\nu_e}+E_{\bar\nu_\mu}},
\qquad
y_{\bar\nu_\mu}=2-y_{\nu_e}.
\]

This is the neutrino pair measured at its own rung. It is not the neutrino
pair projected into the whole three-daughter parent account used in T393.

### Results

- Frozen truth events: `1,000,000`.
- Mean pair: `(0.92381574,1.07618426)`.
- Median electron-neutrino coordinate: `0.91514945`.
- Mean pair asymmetry: `0.49006995`.
- Anti-muon-neutrino is the heavier neutral child in `62.5081%` of events.
- Fraction within L1 distance `0.20` of either `(0.5,1.5)` orientation:
  `14.6393%`.

The `0.5/1.5` neighbourhood is not enriched. A uniform phase-space control
placed `17.2380%` of events there. The pair is therefore compatible with that
coarse geometry on some events, but it does not preferentially settle there.

The identity-dependent information is directional. Randomly swapping the two
neutrino labels preserved the amount of asymmetry but moved the probability of
the anti-muon-neutrino being heavier from `62.5081%` to `50.0415%`.

Pair asymmetry also rose monotonically across charged-daughter energy
quintiles:

| Charged-energy quintile | Mean neutral-pair asymmetry |
|---:|---:|
| 1 | 0.224517 |
| 2 | 0.390389 |
| 3 | 0.511177 |
| 4 | 0.613768 |
| 5 | 0.710498 |

### Test 1 claim ceiling

This is a frozen Standard-Model `V-A` truth crosswalk. It resolves the native
neutral-pair geometry more faithfully than a single conditional mean, but it
is not a direct simultaneous observation of the two neutrinos and is not an
individual decay-time predictor.

## Test 2 — unseen population handover reconstruction

### Source and split

The Super-Kamiokande archive contains `1,986,465` stopped-cosmic-muon rows.
The first two fields report a later decay-electron momentum and time, or zero;
remaining fields contain neutron times when present.

The frozen deterministic row-hash split produced:

- calibration tagged decays: `622,746`;
- validation tagged decays: `248,897`;
- untouched holdout tagged decays: `374,340`.

Decay-electron momentum, decay-electron time and all neutron fields were
forbidden as pre-outcome predictors. They were used only to define or reveal
the outcome.

### Models

- `M0`: one truncated exponential fitted on calibration rows.
- `MP`: calibration-only empirical release complement, 128 bins with Jeffreys
  `0.5` smoothing.
- `MR`: time-reversed empirical distribution as the wrong-direction control.

### Holdout scores

| Model | Mean NLL | KS | Integrated absolute CDF error |
|---|---:|---:|---:|
| M0 one exponential | 1.8493975 | 0.0720300 | 0.0284449 |
| MP reconstructed anti-phase | 1.8057631 | 0.0178327 | 0.0016773 |
| MR reversed control | 8.8689820 | 0.9935761 | 0.4993542 |

The NLL improvement was

\[
\Delta_{\mathrm{NLL}}
=
\mathrm{NLL}_{M0}-\mathrm{NLL}_{MP}
=0.04363439
\]

per held-out event, with block-bootstrap 95% interval
`[0.04286623,0.04443180]`.

### Independent robustness check

An independent validator reproduced the fitted exponential rate within
`4.13e-9`, reproduced the 128-bin scores, checked both ARA closure invariants
and verified the source hash. The population advantage remained positive at
every checked resolution:

| Bins | NLL gain | 95% low | 95% high | MP KS |
|---:|---:|---:|---:|---:|
| 32 | 0.0172952 | 0.0167487 | 0.0179239 | 0.0457066 |
| 64 | 0.0303975 | 0.0296497 | 0.0311858 | 0.0343174 |
| 128 | 0.0436344 | 0.0428175 | 0.0444309 | 0.0178327 |
| 256 | 0.0630466 | 0.0624643 | 0.0636272 | 0.0080884 |

### What Test 2 does and does not establish

The calibration reconstruction predicts the population distribution of
later tagged daughter times on untouched rows. That is a real leakage-safe
forecast of unseen outcomes at the population rung.

It is also flexible empirical density estimation. Its success is not unique
proof of ARA, and the increasingly close fit at finer resolution may encode
detector timing structure, capture mixture and response features as well as
muon decay physics.

The archive is outcome-conditioned and has no changing pre-decay field for a
still-living individual muon. The gate

> Which individual muon releases next, and how far in advance?

is therefore `STRUCTURALLY_UNTESTABLE_NO_PRE_OUTCOME_VARIATION` in this source.

## Frozen conclusion

T394 supports two bounded findings:

1. the native neutrino pair is a continuous, identity-dependent ARA gradient,
   not a universal fixed `(0.5,1.5)` pair;
2. the population release anti-phase can be reconstructed from calibration
   data and transferred to unseen tagged-decay rows.

The decisive next rung needs an event-linked source that measures the same
individual muon repeatedly before decay—preferably spin/polarisation phase,
trajectory, stopping-site field or another independently justified
traversal-child observable—and then records the daughter timestamp. Only that
grain can test advance individual handover prediction.

## Reproduction files

- `t394_native_pair_and_release.py`
- `validate_t394_native_pair_and_release.py`
- `T394_native_pair_and_release/T394_RESULTS.json`
- `T394_native_pair_and_release/T394_VALIDATION.json`
- `T394_native_pair_and_release/T394_TEST1_EVENT_SAMPLE.csv`
- `T394_native_pair_and_release/T394_TEST1_QUINTILES.csv`
- `T394_native_pair_and_release/T394_TEST2_HOLDOUT_CDF.csv`
- `T394_native_pair_and_release/T394_TEST2_SENSITIVITY.csv`
- `T394_native_pair_and_release/T394_REPORT_ARTIFACT.json`

