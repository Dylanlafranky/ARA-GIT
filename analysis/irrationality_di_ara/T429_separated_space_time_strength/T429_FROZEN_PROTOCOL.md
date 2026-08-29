# T429 — Separated space/time strain and gravitational-strength crosswalk

Frozen before development scoring. T427 and T428 remain unchanged.

## Question

Did T427/T428 obscure the relevant relation by mixing movement, frequency,
amplitude and spectral shape? If the received gravitational-wave record is cut
into a time-facing history and a space/connection-facing history first, do the
two histories jointly order merger maturity, and do they agree with an
independently calculated established-physics coupling proxy?

This is not a blind merger-discovery test: published event GPS times are used to
retrieve and crop every record. It is an event-locked relational test.

## Who, where and when

- Identity: one binary-black-hole event at a time. Events are never pooled into
  one ARA identity.
- Replicates: public calibrated strain from H1 and L1; V1 is a secondary view
  where available.
- Development event: GW150914 only.
- Untouched holdouts: GW170104, GW170608, GW170809, GW170814 and GW170818.
- Event interval: -1.50 to +0.25 seconds relative to the published event GPS.
- Primary maturity interval: -1.25 to -0.03 seconds. The final 30 ms and all
  post-event samples are excluded from inspiral-formula scoring.
- Off-source calibration: [-12,-4] and [4,12] seconds, unchanged from T427.

## Model-free ARA construction

All signal-derived coordinates are constructed before source masses or distance
are read.

### Time/movement wave

The time-facing wave uses phase/frequency evolution only:

1. `T_frequency`: power-weighted spectral centroid in 30–512 Hz.
2. `T_chirp`: positive smoothed derivative of log centroid frequency.

Each feature is mapped independently to 0–2 using its detector-specific
off-source empirical CDF. Their mean is `T_A`, the exposed time/movement
coordinate. No amplitude term enters it.

### Space/connection wave

The space-facing wave uses received amount and cross-detector structure:

1. `S_amount`: log total 30–512 Hz spectral power in each detector.
2. `S_agreement`: H1/L1 agreement of independently normalized power histories
   after a fixed +/-10 ms lag search performed on power, not phase.

`S_amount` is mapped to 0–2 from detector-specific off-source ECDFs and combined
across H1/L1. `S_agreement` remains independently measured and is not defined as
`2-T_A`. Their mean is `S_B`, the exposed space/connection coordinate.

The labels A/B state the chosen orientation for this cut. Reversing the labels
would not change the relational result. Neither coordinate is forced to close
with the other or to sum to 2.

## Established-physics crosswalk (kept separate)

Official GWOSC GWTC-1 median source parameters are read only after the
model-free histories have been written:

- source-frame component masses and total mass;
- detector-frame chirp mass;
- luminosity distance and redshift;
- network matched-filter SNR.

Using the independently measured consensus frequency `f(t)`:

    r(f) = [G M_z / (pi f)^2]^(1/3)
    u(f) = G M_z / (r c^2)
    b(f) = eta * u(f),  eta = m1*m2/(m1+m2)^2
    tau(f) = 5/256 * (G Mc_z/c^3)^(-5/3) * (pi f)^(-8/3)

`b(f)` is a dimensionless binding/coupling proxy, not a new ARA coordinate.
`tau(f)` is the leading-order quasi-circular inspiral time proxy. Both are
crosswalks to established physics and are not used to construct `T_A` or `S_B`.

Received strain amplitude is not intrinsic source gravity: detector antenna
response, inclination, calibration and distance affect it. The report must keep
received strength and inferred source coupling visibly separate.

## Frozen controls

1. Equal-duration off-source windows processed identically.
2. Circular time shifts between the H1 and L1 amount histories.
3. Reversed chronology, reported descriptively rather than treated as an
   independent data set.
4. Wrong-event source parameters applied to each event's already frozen
   frequency history. They may affect only the crosswalk, never the ARA path.

## Primary holdout gates

The separated cut is supported only if all are true:

1. At least 4/5 holdouts show positive chronological Spearman association for
   `T_A` during the primary maturity interval, with a block-shift p <= 0.05.
2. At least 4/5 show positive chronological Spearman association for `S_B`,
   with a block-shift p <= 0.05.
3. At least 4/5 have both late pre-event medians (-0.25,-0.03 s) above the 90th
   percentile of identically sized off-source windows.
4. At least 4/5 show positive association between the independently constructed
   `S_B` and the established-physics binding proxy `b(f)`, p <= 0.05 under
   circular block shifts of `S_B`.
5. Matched H1/L1 power-history agreement beats circularly shifted agreement in
   at least 4/5 holdouts.

The source-parameter crosswalk is not allowed to rescue a failed model-free
gate. A fail rejects this separated operational cut, not the general ARA
framework.

## Visual contract

The report must show, with numbers and units:

- raw/whitened strain and time-frequency power;
- separate frequency/chirp and amount/agreement histories;
- `T_A` and `S_B` on independent 0–2 axes through chronological time;
- the time-facing versus space-facing Di-ARA path for each event;
- off-source and circular-shift controls;
- inferred separation, binding proxy and inspiral-time proxy in a visibly
  separate established-physics panel;
- identical-scale small multiples for all untouched holdouts;
- an explicit ARA reading, established-physics reading, and unresolved boundary.

## Interpretation boundary

A pass would support a reproducible separated relational instrument for these
event-locked strain histories and show that its connection-facing history tracks
an independently calculated physical coupling proxy. It would not prove that
ARA generates gravity, identify literal internal black-hole children, or show a
blind prediction of merger time. A failure would show that this particular
separation and projection are not sufficient.
