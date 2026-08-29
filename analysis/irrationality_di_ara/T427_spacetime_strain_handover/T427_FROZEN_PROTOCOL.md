# T427 — Spacetime-strain Irrationality Di-ARA handover and Information³ lock

**Status:** frozen before downloading or inspecting any event strain waveform  
**Frozen:** 24 August 2026 (Australia/Brisbane)  
**ARA hypothesis and geometry:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## Relational address — who, what, when, where, why and how

- **Who:** one transient gravitational-wave strain identity, observed
  independently by the Hanford (`H1`) and Livingston (`L1`) detectors. Virgo
  (`V1`) is a third independent relation where its native activity is strong
  enough to be evaluated. Detectors are observations of the same proposed
  identity, not parent and child identities.
- **What:** the time-facing main Irrationality Di-ARA route

  \[
  \text{connection-heavy}
  \rightarrow
  \text{opening near }(0.5,1.5)
  \rightarrow
  \text{movement-heavy excursion}
  \rightarrow
  \text{connection-heavy reclosure},
  \]

  followed by an independent test of whether reclosure carries a more
  predictable, lower-dimensional information lock.
- **When:** a fixed event-centred interval from `-1.50 s` to `+0.25 s`
  relative to the published event GPS time. Noise calibration uses only the
  fixed off-source intervals `[-12,-4] s` and `[+4,+12] s`. Published peak
  time is not used to construct the ARA axes or select stages; it is opened
  only after sequence scoring as a scientific crosswalk.
- **Where:** the strain time series inside each detector, on a two-coordinate
  ARA plane. `C1` is movement/traversal and `C2` is connection/concentration.
  The coordinates are independent `0–2` readings and are not forced to sum
  to `2`.
- **Why:** test opening, handover and information locking directly in a
  time-facing spacetime measurement rather than through a material proxy such
  as sand, droplets or a detector response.
- **How:** construct each detector's coordinates without waveform templates,
  locate a native strain-activity onset independently of those coordinates,
  freeze the T426 four-stage sequence, and compare untouched events with
  time-slide, phase-scramble, time-reversal and off-source controls.

## Prior-result and crosswalk boundary

The exact route was registered in T426 before this test and recovered in
`16/16` hourglass discharges. T427 transfers that already named geometry to a
new physical domain. T427 does **not** use inspiral, merger or ringdown labels
to build the coordinates. Those established-physics labels are applied only
after scoring to describe where an ARA stage landed.

The raw data and public event metadata are from the Gravitational Wave Open
Science Center (GWOSC), CC BY 4.0. Event GPS time is used only to retrieve and
crop a fixed interval.

## Event split frozen before waveform inspection

### Development / implementation-only event

- `GW150914-v2`: `H1`, `L1`, 32 s, 4096 Hz HDF5.

This event may be used to verify HDF reading, filtering, numerical stability,
plot layout and sign conventions. It is excluded from all primary gates.
No threshold may be changed to make its ARA route pass.

### Untouched primary holdouts

1. `GW170104`
2. `GW170608`
3. `GW170809`
4. `GW170814`
5. `GW170818`

Use the public 32 s, 4096 Hz HDF5 strain for every listed detector. `H1/L1`
form the primary relation. A listed `V1` stream is used only for the secondary
Information³ check and only if it passes the frozen native-activity
eligibility rule below.

If a frozen file is unavailable or fails public data-quality flags, mark that
event/detector unavailable. Do not substitute another event after waveform
inspection. The current O4 event `GW250207_115645` is reserved as a future
external replication because its early public release is a different, much
longer file product.

## Fixed preprocessing

1. Read calibrated strain and sampling metadata from HDF5.
2. Reject NaNs, non-finite sampling metadata or a failed public data-quality
   flag in the event interval.
3. Estimate the noise power spectral density separately for each detector
   from the two off-source intervals only, using Welch medians.
4. Whiten without a waveform template.
5. Apply a zero-phase `30–512 Hz` band-pass. No source-mass, chirp or ringdown
   parameter enters the filter.
6. Compute a Hann short-time Fourier transform using `64 ms` windows and
   `4 ms` hops. Analyses use only `30–512 Hz` bins.
7. For detector comparison, estimate one fixed time offset per detector from
   the native activity histories by maximum absolute correlation over
   `±10 ms` for `H1/L1` and `±30 ms` for a pair containing `V1`. The same
   lag search is repeated inside every null control.

## Native magnitude and independently anchored onset

For each time-frequency frame let

\[
N(t)=\log\!\left(\sum_f |X(f,t)|^2+\epsilon\right)
\]

be native activity. Robust off-source location and scale are the median and
`1.4826 × MAD`. The activity reading is

\[
z_N(t)=\frac{N(t)-\operatorname{median}(N_{\rm off})}
{1.4826\,\operatorname{MAD}(N_{\rm off})+\epsilon}.
\]

Network onset is the first frame in the event interval for which the median
`H1/L1` activity is at least `z_N=3` for three consecutive frames. Native
activity is reported separately and is not itself either ARA axis.

## Two independently defined ARA coordinates

Let the normalized within-frame spectral distribution be

\[
p_f(t)=\frac{|X(f,t)|^2}{\sum_f |X(f,t)|^2}.
\]

### C1 — movement/traversal ARA

Movement is the sum of spectral-distribution change and ridge displacement:

\[
M(t)=H\bigl(p(t),p(t-1)\bigr)
+\left|\log_2\frac{f_{\rm ridge}(t)+\epsilon}
{f_{\rm ridge}(t-1)+\epsilon}\right|,
\]

where `H` is Hellinger distance and `f_ridge` is the maximum-power frequency.
The raw movement channel is

\[
Y_M(t)=N(t)+\log(M(t)+\epsilon).
\]

### C2 — connection/concentration ARA

Connection is spectral concentration:

\[
K(t)=1-\frac{-\sum_f p_f(t)\log(p_f(t)+\epsilon)}{\log n_f}.
\]

`K=0` is maximally spread over the selected frequency bins and `K=1` is
maximally concentrated. It is independent of `C1`; it is not calculated as
`2-C1` or as a residual. Its raw channel is `Y_K(t)=K(t)`.

### Robust 0–2 chart

Each raw channel is standardized only against its own detector's off-source
history. With robust score `z`, map to the declared ARA diameter by

\[
\boxed{x(z)=\frac{2}{1+\exp[-(z-3)/1.5]}}.
\]

Thus the ridge `x=1` means that a feature is three robust off-source scales
above its local detector background. The map is frozen and is not refitted
per event. Report saturation counts at `x<0.02` or `x>1.98`.

Per-detector coordinates are `C1_d=x(z_{Y_M,d})` and
`C2_d=x(z_{Y_K,d})`. After lag alignment, the primary event path is the
unweighted mean of the independently formed `H1/L1` coordinates. Detector
agreement is retained as a separate coupling observable:

\[
A_{HL}(t)=1-\frac{\|D_{H1}(t)-D_{L1}(t)\|_2}{2\sqrt2}.
\]

## Frozen ARA regions and sequence

- **Connection-heavy:** `C1 < 1` and `C2 > 1`.
- **Opening box:** `|C1-0.5| <= 0.25` and `|C2-1.5| <= 0.25`.
- **Movement-heavy:** `C1 > 1` and `C2 < 1`.
- **Persistent stage:** its inequalities hold for three consecutive frames.
- **Bridge samples:** both-high and both-low frames may connect stages but are
  not relabelled.

A holdout completes the loop only if:

1. a persistent connection-heavy interval occurs before native onset;
2. the independently anchored native-onset coordinate lies in the opening
   box;
3. a persistent movement-heavy interval follows onset;
4. a new persistent connection-heavy interval follows that excursion before
   the end of the fixed event interval.

Stage time, ARA coordinate, native activity, detector agreement and distance
from the ideal landmarks must be reported. A landmark is a pure address, not
an assertion that every event must land there without distortion.

## Information-lock test

The lock test uses a channel not used to construct either ARA coordinate.
For each detector, fit an autoregression of order two using only samples in a
`64 ms` window and score one-step normalized prediction error on the following
`32 ms`. Compare:

1. the first eligible post-reclosure window;
2. an equal-native-activity pre-opening window;
3. matched time-slide and phase-scramble controls.

An event supports local information locking when the median `H1/L1`
post-reclosure error is lower than its matched pre-opening error and lower
than at least `95%` of its control errors. This is a predictability claim, not
an energy or entropy identity.

## Secondary three-detector Information³ test

Where `V1` has three consecutive frames at `z_N>=3`, construct its ARA path
independently and hide it during `H1/L1` stage location. The `H1/L1` relation
predicts the stage order and times in `V1` after only the frozen light-travel
lag search. A stage matches when its start lies within two STFT hops (`8 ms`)
of the predicted time and has the same quadrant label.

This is a stricter relational reconstruction:

\[
(D_{H1},D_{L1},R_{HL})\longrightarrow D_{V1}^{\rm predicted}.
\]

Failure or ineligibility does not alter the primary two-detector gate.

## Frozen controls

Use seed `42720260824` and `10,000` sequence replicates where computationally
practical.

1. **Detector time slide:** shift `L1` by a uniformly selected non-zero offset
   in `[0.20,0.80] s`, circularly within the event interval; redo lag search.
2. **Phase scramble:** retain each detector's Fourier amplitudes over the
   event interval, independently randomize conjugate-symmetric phases, and
   rebuild the full instrument.
3. **Time reversal:** reverse both detector histories around the fixed event
   interval while retaining the forward stage rule.
4. **Off-source pseudo-event:** apply the complete instrument to fixed-length
   windows sampled from available off-source data.
5. **Wrong relation:** pair `H1` from one holdout with `L1` from a different
   holdout after normalizing both to their own GPS-relative event clocks.

Controls repeat normalization, lag search, onset detection and sequence
scoring. Null inference is based on the number of complete holdout loops and
the information-lock advantage.

## Primary gates

Structural support requires all of:

1. at least `3/5` primary holdouts complete the frozen four-stage loop;
2. the observed completion count exceeds the detector-time-slide and
   phase-scramble null distributions with empirical `p<0.05`;
3. at least `3/5` holdouts satisfy the independent information-lock rule;
4. median aligned `H1/L1` ARA agreement during the four scored stages is at
   least `0.70` and exceeds wrong-relation pairing.

The opening-box count, crosswalk to published peak time and three-detector
Information³ result are reported separately even when a primary gate fails.

## Required visuals

1. fully labelled raw and whitened strain for every detector and event;
2. spectrogram with native onset and all ARA stage times;
3. `C1/C2` histories, native magnitude and detector agreement;
4. Di-ARA trajectory with arrows, ridges, opening box and stage markers;
5. independent detector trajectories side by side;
6. information-lock prediction-error comparison;
7. five-event holdout gallery and stage-time waterfall;
8. observed gates against each null distribution;
9. three-detector Information³ view where eligible;
10. a source/data-quality panel with files, hashes, sample rates, missingness,
    saturation and exclusions.

## Interpretation boundary

A pass supports this specific model-free spacetime-strain realization of the
previously frozen time-facing Irrationality Di-ARA route and its associated
predictability lock. It does not prove that gravitational waves cause the
geometry, that the route is compulsory in every identity, or that ARA replaces
general relativity. A failure rejects this operational transfer while leaving
T426 and the exact ARA coordinate definitions intact.

Because all selected events are already known gravitational-wave detections,
T427 tests internal handover geometry and relational reconstruction—not event
existence or detection significance.
