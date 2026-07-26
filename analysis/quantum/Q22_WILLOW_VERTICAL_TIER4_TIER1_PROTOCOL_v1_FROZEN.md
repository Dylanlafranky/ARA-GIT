# Q22 frozen protocol v1 — Tier-4 to Tier-1 vertical ARA state and travel

**Frozen before outcome extraction:** 26 July 2026  
**Source:** Google Quantum AI Willow QEC deposit, DOI `10.5281/zenodo.13273331`  
**Status:** labels remain unopened when this protocol is written

## Question

Q21 retained Tier-4 grandchildren and lateral Tier-3 handovers but did not
explicitly measure the vertical relation from a completed Tier-4 child wave to
the Tier-1 whole relation.

Q22 tests two related ARA claims:

1. **vertical state:** Tier 4 and Tier 1 possess a measurable same-window ARA
   relation;
2. **vertical travel:** a completed Tier-4 information wave is more faithfully
   related to a later Tier-1 state than to an equally distant earlier state.

The second claim freezes the directional prediction:

\[
\boxed{\text{Tier 4 leads Tier 1}}
\]

Similarity is allowed to be delayed by one, two or three complete detector
cycles. No delay is selected after results.

## Public data and staging

Use the previously untouched patch `d5_at_q6_9`.

| Role | Basis | Cycles | Shots |
|---|---:|---:|---:|
| development | X and Z separately | 13 | 50,000 each |
| untouched holdout | X and Z separately | 30 | 50,000 each |

Stage 1 extracts only:

- `metadata.json`;
- `circuit_ideal.stim`;
- `detection_events.b8`.

Stage 2 may extract `obs_flips_actual.b8` only after this protocol, the feature
implementation and the outcome-blind calibration are checksum-frozen.

## ARA hierarchy used

| Tier | ARA meaning in Q22 |
|---|---|
| Tier 1 | the whole/meta crossed-versus-aligned relation \(J_t\) |
| Tier 2 | the spatial X and Y parent diameters |
| Tier 3 | soft spatial children \(AA,AB,BB,BA\) |
| Tier 4 | each Tier-3 child decompressed across adjacent earlier/later slices |

The Tier-3 children use normalized detector coordinates and the fixed circular
order:

\[
(AA,\ AB,\ BB,\ BA).
\]

For shot \(s\), slice \(t\), child \(c\), let \(S_{s,t,c}\) be the
coordinate-weighted detector activity and let
\[
P_{s,t,c}=\frac{S_{s,t,c}}{\sum_d S_{s,t,d}}
\]
when that slice contains activity.

## Tier-1 whole coordinate

The whole/meta relation is

\[
\boxed{
J_{s,t}=2(P_{s,t,AB}+P_{s,t,BA})
}
\]

on the ARA `0–2` diameter. `1` is its equal crossed/aligned ridge.

## Tier-4 child coordinate

For a completed adjacent-time window \((t,t+1)\):

\[
\boxed{
x^{(4)}_{s,t,c}
=
\frac{2S_{s,t+1,c}}
{S_{s,t,c}+S_{s,t+1,c}}
}
\]

when at least one endpoint has activity. This is the local earlier-to-later
ARA of one Tier-3 child.

## Cut A — same-window vertical state

The Tier-1 coordinate for the same window is:

\[
\bar J_{s,t}=\frac{J_{s,t}+J_{s,t+1}}2.
\]

The vertical ARA relation is:

\[
\boxed{
V^{(0)}_{s,t,c}
=
\frac{2x^{(4)}_{s,t,c}}
{x^{(4)}_{s,t,c}+\bar J_{s,t}}
}
\]

and its mirrored reading is \(2-V^{(0)}\). Equality is the `1.0` ridge.

The Information³ lock is not flattened to \(V\) alone. It retains:

\[
\left(
\bar J,\ x^{(4)},\ V^{(0)}
\right).
\]

Per shot, the registered `vertical_state` vector contains:

- mean and standard deviation of Tier-1 \(J\): 2 coordinates;
- mean and standard deviation of each Tier-4 child: 8 coordinates;
- mean \(V^{(0)}\) and mean \(|V^{(0)}-1|\) for each child: 8 coordinates.

Total: `18` coordinates.

## Cut B — strictly directional vertical travel

The completed Tier-4 window \((t,t+1)\) is never compared with a Tier-1 slice
inside that same window.

For delay \(d\in\{1,2,3\}\):

\[
V^{(+d)}_{s,t,c}
=
\frac{2x^{(4)}_{s,t,c}}
{x^{(4)}_{s,t,c}+J_{s,t+1+d}}
\]

is the future reading, while

\[
V^{(-d)}_{s,t,c}
=
\frac{2x^{(4)}_{s,t,c}}
{x^{(4)}_{s,t,c}+J_{s,t-d}}
\]

is its matched past control. The future and past slices are equally distant
from the centre of the Tier-4 window and neither shares its data.

For every child and delay, retain:

- mean vertical ARA reading;
- mean ridge distance \(|V-1|\).

The future relation contributes `24` coordinates. With the 10 Tier-1/Tier-4
identity coordinates, `vertical_travel` has `34` coordinates.

The combined registered primary model `vertical_both` contains the 10 identity
coordinates, 8 static coordinates and 24 future-travel coordinates: `42`
coordinates. No coordinate selection is allowed.

## Frozen comparators and controls

| Model | Coordinates |
|---|---|
| `vertical_state` | registered 18-coordinate same-window lock |
| `vertical_travel` | registered 34-coordinate future lock |
| `vertical_both` | registered 42-coordinate combined primary |
| `past_travel_control` | same identities plus the 24 matched past relations |
| `broken_vertical_both` | Tier 4 from shot \(s\), Tier 1 from shot \(s+1\), circularly shifted |
| `q21_child_topology` | Q21's 24 Tier-4/lateral coordinates on the same records |
| `event_fraction` | total detector-event fraction |
| `vertical_both_plus_count` | primary coordinates plus event fraction |

The broken-relation control preserves marginal Tier-1 and Tier-4 distributions
but destroys their within-shot Information³ lock.

## Frozen predictive model

Fit X and Z independently.

For every feature set:

1. standardize using development means and population standard deviations;
2. calculate the development centroid for logical outcome `0`;
3. calculate the development centroid for logical outcome `1`;
4. use their difference as a fixed linear direction;
5. score the untouched 30-cycle records without refitting.

Report AUROC, average precision, accuracy at the development midpoint, class
prevalence, feature count and all fitted coefficients.

Run `999` development-label permutations per basis with seed `20260726`.
Refit only the `vertical_both` direction and score the unchanged holdout.
The one-sided empirical p-value is:

\[
p=\frac{1+\#\{\mathrm{AUC}_{null}\geq\mathrm{AUC}_{observed}\}}{1000}.
\]

## Construction checks

- all ARA coordinates and vertical relations remain in `[0,2]` within
  numerical tolerance;
- all registered feature matrices contain finite values;
- development and holdout feature counts match;
- each delay has non-zero valid coverage;
- future and past comparisons do not reuse a Tier-4 window endpoint;
- source members match ZIP CRC-32 and the Zenodo archive checksum;
- no outcome file exists in the geometry staging directory.

## Registered gates

### Directional geometry gates

1. the mean future ridge distance is smaller than the matched past ridge
   distance in both holdout bases;
2. the mean future ridge distance is smaller than the broken-shot future
   distance in both holdout bases.

These gates test the directional ARA claim without using logical labels.

### Predictive gates

3. `vertical_state` holdout AUROC is at least `0.52` in both bases;
4. `vertical_travel` holdout AUROC is at least `0.52` in both bases;
5. `vertical_both` holdout AUROC is at least `0.55` in both bases;
6. mean `vertical_both - q21_child_topology` AUROC is at least `0.01`;
7. mean `vertical_both - event_fraction` AUROC is at least `0.01`;
8. mean `vertical_both - past_travel_control` AUROC is at least `0.01`;
9. mean `vertical_both - broken_vertical_both` AUROC is at least `0.01`;
10. permutation p-value is at most `0.01` in both bases;
11. adding event fraction changes mean AUROC by less than `0.01`;
12. the fitted `vertical_both` score direction is concordant between
    development and holdout in both bases.

Report every gate separately. The strict overall result is `SUPPORTED` only if
all twelve gates pass. A failed predictive gate does not erase a separately
passed directional-geometry gate, and vice versa.

## Claim boundary

Q22 can test whether this particular raw-detector ARA representation captures:

- a vertical Tier-4↔Tier-1 state relation;
- a forward-delayed rather than backward relation;
- additional information about the logical outcome.

It cannot by itself prove universal fractality, physical causation, a new
quantum state, or superiority to production surface-code decoders. The patch
and processor are shared across development and holdout.
