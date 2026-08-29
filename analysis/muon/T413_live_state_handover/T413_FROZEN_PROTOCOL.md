# T413 — Frozen live-state muonium handover protocol

**Status:** frozen before inspecting any selected scan response.

## Question

Can a strictly pre-holdout ARA relation measured in a live, coupled muon–electron
spin system predict the later relation of that same ensemble better than simpler
one-state alternatives?

This is an **ensemble live-state handover test**. It is not a test of the exact
decay time of one muon and it is not an individual-neutrino prediction.

## Source and identity boundary

- Public ISIS experiment: **RB1620447**, *Development of Radio Frequency µSR as
  a Method for Determining Hyperfine Coupling Constants*.
- Part DOI: `10.5286/ISIS.E.84939772`.
- Instrument: EMU.
- Parent identity: the hyperfine-coupled muon–electron spin system in the
  muoniated acetone radical.
- Directly observed branches: the matched 96-detector records acquired under
  the independently switched **RF-on** and **RF-off** conditions.
- The detector record is population/ensemble data. No event-level lineage is
  inferred.

The public files are HDF4 Nexus files. Each selected file must contain exactly
192 detector records, two switching states, the period label `RF on;RF off`,
and two exposure-frame counts. The first 96 detectors are paired with the last
96 in the recorded period order.

## Frozen run selection

Selection is based only on run metadata, temperature and applied field. No
response amplitude is used to select a file.

1. **Development:** acetone at 300 K, field `F = 50 + 36k` G within
   `[50, 500]` G.
2. **Internal validation:** acetone at 300 K, field `F = 68 + 36k` G within
   `[50, 500]` G.
3. **Untouched holdout:** acetone at 202 K, high-field branch,
   `F = 1800 + 36k` G within `[1800, 2496]` G.

Repeated coarse-check files whose field duplicates a fine-scan field are
excluded by retaining the chronologically later fine-scan sequence. Files that
fail the structural checks above are excluded with the reason recorded.

## Direct ARA cut

For detector `d` and rebinned time `t`, exposure-corrected rates are

\[
R_{\rm on,d}(t)=\frac{C_{\rm on,d}(t)}{N_{\rm frames,on}},\qquad
R_{\rm off,d}(t)=\frac{C_{\rm off,d}(t)}{N_{\rm frames,off}}.
\]

The paired ARA coordinate is

\[
x_d(t)=\frac{2R_{\rm on,d}(t)}
{R_{\rm on,d}(t)+R_{\rm off,d}(t)}\in[0,2],
\qquad r_d(t)=x_d(t)-1.
\]

`x = 1` is the equal recorded-rate ridge. This is a measurement ridge, not an
assumption that all physical children are individually symmetric there.

Counts are rebinned by 8 native bins. Only corrected times
`0.25 <= t < 6.0 microseconds` are used. The causal development window is
`0.25 <= t < 2.5 microseconds`; the untouched within-run future is
`2.5 <= t < 6.0 microseconds`.

## Temporal Di-ARA cut

The first spatial relation mode `u` is estimated by a weighted SVD of the
96-dimensional `r(t)` pattern in the causal development window only. Its sign
is fixed so its first non-zero development score is positive. The state cut is

\[
A(t)=u^\top r(t).
\]

The independently meaningful temporal/path cut is the causal first difference

\[
B(t)=A(t)-A(t-\Delta t).
\]

`A` is the live RF-on/RF-off relation seen across the detector ensemble. `B`
is its measured traversal direction. `B` is **not** defined as `2-A`, a fitted
missing child, or a TE-ARA remainder.

The full two-coordinate ARA predictor fits an affine `2 x 2` transition on
`[A(t), B(t)]` using only the development window, then recursively predicts
the within-run future. The fitted linear part is allowed to contract or expand
as measured; no Phi, `1/e`, 0.5, 1.0 or 2.0 transition landmark is imposed.

## Frozen comparators

All comparators receive exactly the same causal samples.

1. **Persistence:** hold the final development value of `A`.
2. **One-coordinate AR(1):** predict `A` from only its immediately preceding
   value; this is the no-perpendicular-child comparator.
3. **Diagonal state model:** use `[A,B]` but prohibit cross-coupling between
   them.
4. **Standard damped harmonic:** fit
   `c + exp(-lambda*t)*(a*cos(omega*t)+b*sin(omega*t))` on development only;
   frequency and damping are selected only from the frozen grids below.
5. **Wrong orientation:** reverse both off-diagonal signs of the fitted ARA
   transition.
6. **Broken-order control:** deterministically permute development time order
   with seed `413` before fitting the ARA transition, then forecast in true
   order.

Frozen harmonic grids:

- frequency: `0.01` to `12.00 MHz` in `0.01 MHz` steps;
- damping: `0.00` to `2.00 per microsecond` in `0.05` steps.

No holdout result may change these grids, the time split, rebinning or mode
count.

## Outcomes

Primary outcome:

- count-weighted RMSE of `A(t)` over the within-run future, aggregated by the
  median across untouched 202 K holdout runs.

Secondary outcomes:

- full 96-detector-pattern weighted RMSE after reconstructing the predicted
  first-mode contribution and retaining the development ridge component;
- correlation of predicted and observed future `A(t)`;
- first future `A=0` (equivalently direct-coordinate `x=1`) crossing-time
  error for runs that actually contain such a crossing;
- pairwise run wins and field-bootstrap intervals;
- performance by applied field, to reveal whether any result is confined to
  the resonance neighbourhood.

## Frozen interpretation gates

1. **Relational predictive support:** on the untouched holdout, the full ARA
   transition has lower median primary RMSE than persistence, AR(1), and the
   diagonal state model; the field-bootstrap 95% interval for its improvement
   over the best of those three excludes zero; and the broken-order control is
   worse.
2. **Orientation support:** the frozen orientation beats the wrong-orientation
   control on a majority of holdout runs and in median RMSE.
3. **Added predictive value beyond the established waveform model:** the ARA
   model beats the damped-harmonic comparator by at least 2% in median holdout
   RMSE with a bootstrap interval excluding zero.
4. If gates 1–2 pass but gate 3 does not, the result is a successful ARA
   recovery/crosswalk of the live coupled-state dynamics, **not** a new
   predictor beyond established waveform modelling.
5. If gate 1 fails, the proposed live-state temporal Di-ARA predictor is not
   supported in this operationalisation. A visually recognizable circle,
   ridge or quadrant cannot rescue that result.

## Leakage and quality rules

- No future time bin enters the SVD, scaling, coefficient fitting or model
  selection for its run.
- Holdout temperature and field responses are not inspected until this file is
  hashed.
- Exposure frames, zero denominators, non-finite values and detector pairing
  are audited explicitly.
- Excluded files and runs remain in the manifest with reasons.
- Primary metrics are recomputed from saved per-run predictions by a separate
  validation script.

## What this test cannot establish

Even a pass does not show that ARA is the microscopic cause of the hyperfine
dynamics, that a universal landmark controls the transition, or that one can
predict an individual muon decay/neutrino release. It tests whether the declared
two-pole relation plus its causal perpendicular traversal retains transferable
future information in a clean coupled quantum system.
