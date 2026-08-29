# T434 — ARA / inspiral–merger–ringdown scientific bridge

**Status:** frozen before scoring  
**Date:** 26 August 2026 (Australia/Brisbane)

## Question

Does the child-role exchange in the already-written time-facing Irrationality
Di-ARA correspond to the independently published inspiral/post-inspiral
boundary used in the LIGO–Virgo GWTC-1 inspiral–merger–ringdown (IMR)
consistency test?

This is a crosswalk test. It does not allow general relativity, waveform
templates or the published cutoff to construct or move the ARA landmark.

## Who, what, when, where, why and how

- **Who:** GW170104, GW170809, GW170814 and GW170818. GW170608 remains a
  labelled low-information comparison because the published GWTC-1 IMR test
  excluded it for insufficient post-inspiral information.
- **What:** the frozen T427 movement/traversal child `C1` and
  connection/concentration child `C2`. Their local exchange is compared with
  the published event-specific IMR cutoff frequency `f_c`.
- **When:** `[-0.25,+0.05] s` relative to the published event GPS. This is an
  event-locked retrospective comparison, not a blind merger discovery test.
- **Where:** the existing public 4096 Hz GWOSC H1/L1 strain files and the
  already-written T427 consensus ARA coordinates.
- **Why:** establish whether the ARA handover has a quantitative bridge to the
  standard scientific division between inspiral and post-inspiral data.
- **How:** freeze the ARA exchange time first; translate that time to a
  model-free H1/L1 cross-detector spectral-ridge frequency; only then compare
  it with the published `f_c`.

## Frozen ARA landmark

For each event:

1. Apply a centred seven-frame median to `C1`, `C2` and native activity.
2. Find all zero crossings of `C1-C2` in the event interval.
3. Select the crossing closest to the maximum smoothed native activity.
4. If no crossing exists, select the minimum `|C1-C2|` within 64 ms of that
   activity maximum.

The rule is invariant to swapping the names of the two children. The ARA ridge
at 1.0 is recorded descriptively but is not imposed as an exact landmark,
because measured children may be displaced by unmeasured participation.

## Frozen model-free frequency translation

The published IMR cutoff is not used here.

1. Rebuild the unchanged T427 64 ms Hann STFT, 4 ms hop, 30–512 Hz.
2. Divide each detector's power spectrum by its own off-source median spectrum.
3. Align L1 to H1 using the already-defined native-activity lag search, limited
   to ±8 ms.
4. Form the geometric mean of H1 and aligned-L1 normalized power.
5. Around every event frame, integrate ±16 ms and smooth over three frequency
   bins.
6. The maximum coherent-excess bin is the model-free spectral-ridge frequency.

The ARA handover frequency is the spectral-ridge frequency at the frozen ARA
exchange time.

## Independently published comparison

The official GWTC-1 IMR consistency paper supplies:

| Event | `f_c` (Hz) | inspiral SNR | post-inspiral SNR |
|---|---:|---:|---:|
| GW170104 | 143 | 10.9 | 8.5 |
| GW170809 | 136 | 10.6 | 7.1 |
| GW170814 | 161 | 15.3 | 7.2 |
| GW170818 | 128 | 9.3 | 7.2 |

Source: LIGO–Virgo, *Tests of general relativity with binary black hole signals
from the LIGO–Virgo Catalog GWTC-1*, Table III,
https://dcc.ligo.org/public/0156/P1800316/008/O2_testingGR_v2.pdf

## Primary comparison and controls

For each event, calculate the absolute log-frequency error

`E = |log(f_ARA / f_c)|`.

Primary aggregate: median `E` across the four events.

Controls:

1. **Wrong-event cutoff:** enumerate all 24 assignments of the four published
   cutoff frequencies to the four frozen ARA landmarks.
2. **Temporal bridge destruction:** 10,000 replicates independently circularly
   shift each event's model-free frequency track by at least 64 ms before
   reading it at the frozen ARA landmark.
3. **Child-role ordering:** below and above `f_c`, calculate the
   orientation-invariant AUC with which `C1-C2` separates the two scientific
   frequency regimes. Compare the median AUC with 10,000 circular shifts of the
   child-difference history.

## Frozen gates

The bridge is **supported** only if all are true:

1. median absolute percentage difference is at most 20%;
2. at least three of four events are within 25%;
3. temporal-shift `p <= 0.05` for the handover-frequency error;
4. exact wrong-event assignment `p <= 0.05`;
5. median orientation-invariant AUC is at least 0.70 and its shift `p <= 0.05`.

A failure rejects this operational ARA/IMR bridge at this cut and sampling
scale. It does not reject the general ARA framework or the established IMR
method.

## Independence boundary

- `C1`, `C2` and the exchange time were written before this test.
- The frequency translation and ARA coordinates share the same raw strain, so
  agreement is not independent signal discovery.
- The event-specific `f_c` values arise from standard waveform-based parameter
  estimation and numerical-relativity remnant fits; they are not used in the
  ARA construction.
- The event GPS supplies the crop location. Timing agreement is therefore
  retrospective.

