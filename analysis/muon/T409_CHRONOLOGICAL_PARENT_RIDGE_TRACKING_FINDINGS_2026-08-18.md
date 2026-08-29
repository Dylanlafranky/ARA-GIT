# T409 chronological parent-ridge tracking

Date: 18 August 2026

## Question

T408's individual-event scatter appeared to contain three vertical parent-coordinate bands near `x_mu = 0.75`, `1.0`, and `1.35`. T409 asked whether those bands persist through chronological event blocks and, specifically, whether the upper band behaves like a travelling or movement-loaded relation.

The observed quantity remains the incoming charged-detector ARA coordinate `x_mu`. The later charged-daughter delay is available in the event record, but neither emitted neutrino is observed. This test therefore describes structure in the incoming parent coordinate; it is not a direct neutrino-birth measurement.

## Frozen primary construction

- Source: the 2,109 untouched T379 holdout records from runs `6845.2020.0317.0` and `6845.2020.0318.0`.
- Chronology: six equal-count event-index blocks per run, twelve blocks total.
- Exact topology poles `x_mu = 0` and `x_mu = 2` were retained in population accounting but excluded from density-centre estimation.
- Frozen zones: R1 `[0.60,0.90)`, R2 `[0.90,1.18)`, and broad R3 `[1.18,1.55]`.
- Ridge centre: maximum of a Gaussian-smoothed density with bandwidth `0.035 ARA`.
- Motion: count-weighted RMS displacement of block centres from the pooled centre.
- Controls: 5,000 global-order shuffles and 5,000 within-run shuffles.

## Operational failure and repair boundary

The broad R3 estimator selected `1.180`, exactly its lower boundary. It therefore did not measure the line drawn near `1.35`. That frozen failure is retained.

T409B was then registered as a post-result sensitivity, restricted to a strictly interior local density crest in `[1.25,1.50]`. Because this repair followed inspection of the failed estimator, it is descriptive and cannot upgrade the original visual observation to a confirmatory finding.

## Results

| Relation | Pooled centre | Events | Share of 1,425 non-pole events | Resolved blocks | Motion M | Global shuffle p | Reading |
|---|---:|---:|---:|---:|---:|---:|---|
| R1 | 0.761 | 584 | 40.98% | 12/12 | 0.04469 | 0.0704 | Strong persistent band; weak chronological excess |
| R2 | 1.041 | 560 | 39.30% | 12/12 | 0.04068 | 0.0164 | Strong persistent band; chronological displacement exceeds shuffle |
| Marked R3 | 1.395 | 90 | 6.32% | 10/12 | 0.04060 | 0.7455 | Weak interior crest present; chronological travel not resolved |

The marked upper crest ranges from `1.302` to `1.438` across the ten blocks where it resolves. That movement is smaller than ordinary shuffled-order variation: the global-null median is `0.04646` and its 95th percentile is `0.06317`. The within-run result agrees (`p = 0.6719`).

R2 is the only frozen band whose chronological displacement exceeds both shuffle controls at this block scale. This is a fresh directional lead, not the hypothesised moving upper line, and requires unchanged replication in a new source.

## ARA reading

The user's marked vertical lines correspond to recurring values of the parent coordinate, not merely drawing artefacts:

- two densely occupied parent relations are centred near `0.76` and `1.04`;
- a third, much sparser relation is recoverable near `1.40`;
- the present one-dimensional chronological cut does not show that the upper relation carries more movement than the lower relations.

This leaves open several ARA-compatible identities for the third crest: a sparse child/nearby branch, a detector-topology relation, or a mixture. Chronology alone does not provide the missing same-scale anti-phase required to turn the three vertical positions into a resolved Di-ARA path.

## Verdict

**UPPER STRUCTURE RESOLVED, BUT NOT AS A CHRONOLOGICALLY TRAVELLING RIDGE.**

The visual hypothesis was partly right: there are three recoverable parent-coordinate structures. The stronger proposed interpretation—that the upper structure is uniquely movement-loaded or travels through time—is not supported by this dataset and cut.

No claim is made here about an individual neutrino-release instant.

## Validation and next strict test

Independent validation passed all 18 source, direct-density, count, and saved-block motion checks. The full permutation arrays were not retained, so the validator confirmed the registered draw counts and p-values rather than replaying every null draw.

The next strict test should freeze the three centres on these two runs and transfer them unchanged to a genuinely independent event source. To test movement rather than occupancy, it should add an independently observed incoming axis—preferably spin/polarization-sensitive maturity or another same-scale anti-phase cut—rather than infer that axis from chronology alone.

## Reproduction records

- Protocol: `analysis/muon/T409_CHRONOLOGICAL_PARENT_RIDGE_TRACKING_PROTOCOL_2026-08-18.md`
- Primary script: `analysis/muon/t409_chronological_parent_ridge_tracking.py`
- Repair protocol: `analysis/muon/T409B_MARKED_UPPER_INTERIOR_SENSITIVITY_PROTOCOL_2026-08-18.md`
- Repair script: `analysis/muon/t409b_marked_upper_interior_sensitivity.py`
- Results and charts: `analysis/muon/T409_chronological_parent_ridge_tracking/`
- Validated report artifact: `analysis/muon/T409_chronological_parent_ridge_tracking/artifact.json`

