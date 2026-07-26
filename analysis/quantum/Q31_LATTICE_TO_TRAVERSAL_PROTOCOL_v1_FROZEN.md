# Frozen protocol — Q31 lattice-to-traversal singularity flip

**Protocol ID:** `Q31-LATTICE-TO-TRAVERSAL-SINGULARITY-FLIP-v1`  
**Date frozen:** 26 July 2026  
**Ledger:** T285  
**Fidelity packet:** `Q31_LATTICE_TO_TRAVERSAL_FIDELITY_v1.md`  
**Source status:** no eligible new source or outcome has been opened at freeze.

## 1. Question and registered claim

Does a time-resolved persistent relation lattice cross an independently
specified local handover and continue as a locally predictable but non-closing
information path?

The proposed transition is:

\[
\text{persistent lattice}
\longrightarrow
\text{handover ridge}
\longrightarrow
\text{short-memory high, long-return low traversal}.
\]

The test does not assume Phi, a dipole, literal gas/plasma behaviour or a new
quantum object.

## 2. Eligible source

Select the first public source found after freeze that satisfies all hard
criteria without consulting its Q31 outcome:

1. measured experimental quantum data, not a generated simulation;
2. at least two independent relation coordinates in one fixed shared basis;
3. non-zero transverse/off-diagonal content above stated measurement precision;
4. at least 25 ordered samples around each candidate handover;
5. at least 30 independent trials, devices, trajectories or repeated sweeps;
6. an external control variable or pulse schedule locates the handover before
   any Q31 metric is calculated;
7. raw or minimally reconstructed complex amplitudes, Bloch vectors, density
   matrices or relation matrices are downloadable and redistributable or
   automatically fetchable;
8. enough metadata to separate development and untouched evaluation units.

Reject sources selected because their plotted outcomes resemble the hypothesis.
Record every inspected candidate and its eligibility decision.

## 3. Orientation and object

For the declared local diameter:

- `2`: persistent connection lattice;
- `1`: local handover ridge;
- `0`: unbound information traversal.

The complete state retains native magnitude, orientation, phase/path,
connection, trial identity, time and scale. The scalar below is never reported
alone.

For trial `r` and time `t`, let `M_r(t)` be the source-native relation object in
the fixed basis. Let `v_r(t)` be its vectorised transverse/off-diagonal
coordinates and let `a_r(t)=||v_r(t)||_2` be native activity.

Events with activity below a frozen source-precision floor are marked undefined,
not forced to a ridge.

## 4. Connection persistence

Use source-native edge magnitudes, without phase:

\[
C_r(t)=
\frac{
\langle |v_r(t)|,|v_r(t+1)|\rangle
}{
\max(||v_r(t)||_2||v_r(t+1)||_2,\epsilon)
}.
\]

`C` lies in `[0,1]`. It is high when the same relation support persists. A
source-specific signed adjacency may replace absolute magnitude only if that
choice is written in a source manifest before evaluation.

## 5. Coherent traversal

Define the complex or signed step

\[
\Delta v_r(t)=v_r(t+1)-v_r(t).
\]

Movement amount is

\[
D_r(t)=
\min\left(
1,
\frac{||\Delta v_r(t)||_2}
{\max(a_r(t)+a_r(t+1),\epsilon)}
\right).
\]

Local directional memory is

\[
P_r(t)=
\frac{1+\operatorname{Re}
\langle \widehat{\Delta v_r(t)},\widehat{\Delta v_r(t+1)}\rangle}{2}.
\]

The coherent-traversal score is:

\[
T_r(t)=D_r(t)P_r(t).
\]

This prevents large random jumps from being called pure traversal merely
because they move far.

The ARA position is:

\[
x_r(t)=\frac{2C_r(t)}{C_r(t)+T_r(t)}
\]

when `C+T` exceeds the frozen floor.

## 6. Short memory and long return

### Short memory

Report directional similarity at lags `1,2,3`. The primary short-memory score
is the weighted mean of lags `1–3`.

### Long return

For lags `4–12`, report:

1. complete-shape return error;
2. return to the same dominant relation/partner;
3. recurrence below a development-frozen distance threshold;
4. low-order closure at denominators `2–12`.

Finite data cannot prove irrationality. Q31 can only reject low-order closure
over the measured window. Phi or any other winding number is descriptive only
and cannot affect the primary verdict.

## 7. Independently located handover

The handover time `t*` comes from the experiment’s control variable, pulse
schedule or externally declared signed zero crossing. It may not be selected by
maximising `C`, `T`, `x`, prediction gain or visual resemblance.

Resample each trial to the source-native common progress coordinate, retaining:

- pre-window: four eligible steps ending before `t*`;
- crossing window: the nearest two steps around `t*`;
- post-window: four eligible steps beginning after `t*`;
- long-return window: lags `4–12` after the post-window begins.

If these windows cannot be formed without interpolation across missing data,
the trial is ineligible.

## 8. Controls

Use the same eligible events and native activity weights:

1. **No-crossing control:** the same protocol or sweep class without crossing
   the external handover.
2. **Trial displacement:** replace the future path with trial `(r+17) mod R`
   within the same source stratum.
3. **Time displacement:** circularly shift the future path by one quarter of
   the eligible trajectory, without crossing the development/evaluation split.
4. **Phase randomisation:** preserve every magnitude and time but independently
   rotate transverse phases using seed `31031`.
5. **Stable-lattice control:** retain the pre-handover path over the matched
   post window.
6. **Decay-only baseline:** preserve the observed native magnitude envelope
   while holding direction/partner identity fixed.

Controls must not receive fewer candidates or narrower windows than Q31.

## 9. TE-ARA allocation check

TE-ARA is secondary and cannot create the result.

Before evaluation, use development/calibration data to fix non-negative scaling
constants for connection, traversal and independently measured contextual
channels:

\[
t_C(t)+t_T(t)+t_O(t)\stackrel{?}{\approx}2.
\]

No per-slice renormalisation is permitted. Report the raw native magnitude
separately. If closure occurs only after outcome-dependent scaling, the TE-ARA
gate fails.

## 10. Split and statistics

- Development units: deterministic source-defined first half of independent
  trials/devices/sweeps.
- Evaluation units: untouched second half.
- No time path crosses the split.
- Freeze activity floors, recurrence threshold, any source-native edge
  definition and TE-ARA scaling on development only.
- Use paired trial-cluster bootstrap with `2,000` draws and seed `31031`.
- Report pooled and per-source-stratum results, medians, interquartile ranges,
  10/25/50/75/90% quantiles and event-centred examples.

## 11. Gates

### Data/eligibility

- `D1`: all source-selection criteria pass.
- `D2`: non-zero off-diagonal/transverse content exceeds source precision.
- `D3`: at least 30 untouched evaluation units and 500 eligible evaluation
  transitions.
- `D4`: all candidate handovers were located externally.

### Flip geometry

- `F1`: evaluation median `C` falls from pre to post by at least `10%`, with
  paired bootstrap probability at least `0.95`.
- `F2`: evaluation median `T` rises from pre to post by at least `10%`, with
  paired bootstrap probability at least `0.95`.
- `F3`: `x` moves from above `1` pre-handover to below `1` post-handover in at
  least `60%` of evaluation units.
- `F4`: the centres of the `C` fall and `T` rise differ by no more than one
  source-native sample.

### Information-thread discrimination

- `I1`: post-handover short-memory score beats trial-, time- and
  phase-randomised controls with bootstrap probability at least `0.95`.
- `I2`: post-handover long-return/partner persistence is at least `10%` below
  the stable-lattice control.
- `I3`: short memory remains at least `10%` above the phase-randomised control
  while long return remains no higher than the stable-lattice control.
- `I4`: the no-crossing control does not reproduce both `F1` and `F2`.

### Closure

- `T1`: independently calibrated evaluation TE-ARA absolute closure error is at
  most `10%` of total.
- `T2`: raw native activity does not fall by more than `50%` across the crossing.
  Larger loss classifies dissipation/projection loss rather than a demonstrated
  flip.

## 12. Verdict

- **LATTICE-TO-TRAVERSAL FLIP SUPPORTED:** `D1–D4` and `F1–F4` pass.
- **NON-CLOSING INFORMATION THREAD SUPPORTED:** `D1–D4` and `I1–I4` pass.
- **COMBINED SINGULARITY-FLIP INTERPRETATION SUPPORTED:** both branches and
  `T1–T2` pass.
- **PARTIAL:** exactly one geometry branch passes or both pass while closure is
  inconclusive.
- **NOT SUPPORTED:** eligibility passes but neither geometry branch passes.
- **INCONCLUSIVE:** a data/eligibility gate fails.

Specific falsifiers:

- connection falls without structured traversal rising;
- post-handover short memory is indistinguishable from randomised controls;
- the counter-side returns to stable partners like another lattice;
- connection and traversal changes do not share one crossing;
- the result disappears on untouched units;
- TE-ARA closure requires per-slice or outcome-dependent renormalisation.

## 13. Two-output reporting

Report separately:

1. **Claim verdict:** which frozen gates passed.
2. **Geometry verdict:** the full `C,T,x`, native magnitude, short-memory,
   long-return and TE-ARA distributions before, at and after the crossing,
   including all controls and individual events.

## 14. Evidence boundary

A positive result would establish this operational lattice-to-traversal package
on one fresh public source. It would not prove universal ARA geometry, literal
anti-connection, an irrational winding number, Phi, a new quantum object or a
fundamental Space/Time singularity.
