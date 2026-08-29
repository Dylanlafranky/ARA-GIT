# T419 — Direct dynamic Irrationality Di-ARA handover

**Frozen before development fitting or any validation/holdout scoring:** 22 August 2026  
**Status:** ARA-first temporal test on the same public muoniated-acetone ensemble used by T413–T418

## Question

Do two independently measured ARA histories exchange useful future information?
Specifically, does present openness/traversal help predict later connection closure,
and does present closure help predict later reopening, after accounting for each
target's own recent history and the parent controls?

This is the direct test of how a connection closes and reforms through time in
the current instrument. It is not an individual-muon or neutrino-birth test.

## Who / what / when / where / why / how

### Who

The frozen T413 source manifest: 13 development runs, 13 interleaved-field
validation runs, and 20 high-field/temperature holdout runs. RF-on and RF-off
remain distinct histories. The observed identity is the detector-population
spin relation of the muoniated-acetone radical.

### What

Two coordinates are calculated independently from the same past-only phase
history:

1. **Openness/traversal**

   \[
   U(t)=\frac{2L_{\rm local}(t)}
              {L_{\rm local}(t)+L_{\rm null}(t)}\in[0,2].
   \]

   `L_local` is the loss of a local phase-address predictor and `L_null` is
   the loss of a constant circular-mean predictor. `U=1` means equal losses;
   larger values lean toward unresolved/open traversal in this instrument.

2. **Connection closure**

   \[
   R(t)=2\,\operatorname{median}_{\ell=1}^{32}
   \left|\left\langle
   e^{i2\pi z_{j+\ell}}e^{-i2\pi z_j}
   \right\rangle_j\right|\in[0,2].
   \]

   Larger `R` means the phase history repeats more coherently across its
   measured lags.

Neither coordinate is defined as `2 -` the other. Their sum is not forced to
two. Any exchange relation is therefore empirical rather than bookkeeping.

### When

Each coordinate uses a 128-native-bin history and is read every four native
bins. The **primary future horizon is 32 reads = 128 native bins**, about
2.048 microseconds. Therefore the source and future target histories are
adjacent but have no shared native bins.

Shorter horizons of 1, 2, 4, 8, 16 and 24 reads are retained as diagnostics
only. They overlap internally and cannot by themselves establish a temporal
handover.

### Where

The particle ensemble, detector geometry, source files, 0.25–6.00 microsecond
interval, spin-path reconstruction, material and temperature splits remain
unchanged from T416–T418. Magnetic-field turn budget and RF condition are
parent controls; they are not re-labelled as the handover.

### Why

T416–T418 recovered static and boundary shapes but did not directly test the
dynamic claim. T419 asks the harder question: whether one independently
measured side contains out-of-window information about the later other side.

### How

For each direction, a target-own-history baseline is compared with a transfer
model.

For `U -> later R`:

\[
Z_{R,0}(t)=[R(t),\Delta R(t),P(t),K_B,\mathrm{RF}],
\]

\[
Z_{R,1}(t)=[Z_{R,0}(t),U(t),\Delta U(t)].
\]

For `R -> later U`:

\[
Z_{U,0}(t)=[U(t),\Delta U(t),P(t),K_B,\mathrm{RF}],
\]

\[
Z_{U,1}(t)=[Z_{U,0}(t),R(t),\Delta R(t)].
\]

Here `P(t)=2(1-exp(-t/tau_mu))` is the declared population-lifespan parent
coordinate, and

\[
K_B=\log_2(\gamma_\mu B\tau_\mu)
\]

records the field-dependent number of spin turns available in one mean muon
lifetime. `K_B` is a nuisance/parent control, not an ARA landmark.

Development-only means, scales and ordinary-least-squares coefficients are
frozen before validation and holdout scoring. Metrics are averaged within
run/period and then paired at magnetic-field level.

## Frozen controls

Each directional arm is tested against:

1. **Own-history baseline:** omit the opposite coordinate and its slope.
2. **Circular timing shift:** rotate the added coordinate/slope together
   within each run/period while leaving target and parent histories fixed.
3. **Reverse chronology:** reverse the added coordinate/slope within each
   run/period.
4. **Wrong-frequency reconstruction:** replace only the added coordinate with
   the median of the four predeclared T416 sideband reconstructions.
5. **RF separation:** require positive added information in RF-on and RF-off.
6. **Field-level bootstrap:** resample fields, keeping RF pairs together.

All pseudorandom controls use seed 419. Bootstrap intervals use 10,000 draws;
circular timing uses 1,000 draws.

## Frozen gates

Validation and holdout are judged separately. A stage supports the direct
bidirectional handover only if all gates pass:

1. At least 75% of run/period histories provide at least eight primary
   non-overlapping source/target pairs.
2. For both directions, the field-bootstrap 95% interval for
   `MSE_baseline - MSE_transfer` lies wholly above zero.
3. For both directions, correct timing beats at least 95% of circular shifts.
4. For both directions, the field-bootstrap 95% interval for
   `MSE_wrong - MSE_transfer` lies wholly above zero.
5. For both directions, the field-bootstrap 95% interval for
   `MSE_reverse - MSE_transfer` lies wholly above zero.
6. Baseline-minus-transfer improvement is positive for both directions in
   RF-on and RF-off separately.

Support across this archive requires both validation and holdout to pass all
gates. Short-lag diagnostics cannot rescue a failed non-overlap gate.

## Chart contract

The final report must show, with numeric axes and units:

1. independent `U` and `R` histories through time for labelled examples;
2. their path in the `U x R` plane with chronology marked;
3. actual versus baseline/transfer future values at the non-overlap horizon;
4. per-field improvement for both directions and RF conditions;
5. correct, shifted, reversed and wrong-frequency controls;
6. lag dependence, with overlapping diagnostics visually separated from the
   primary non-overlap horizon;
7. all gates, sample counts, equations and claim boundaries.

## Claim boundary

A pass would show bidirectional, timing-specific and frequency-specific future
information exchange between two independently constructed histories in this
population spin identity. That would support the proposed dynamic
Irrationality Di-ARA handover instrument here. It would not prove literal
energy transfer, a universal irrationality law, microscopic muon constituents,
or an individual decay/neutrino release time.

