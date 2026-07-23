# Frozen protocol — prospective recovery of a hidden ARA `Other` term

**Frozen:** 23 July 2026, before running the recovery  
**Status:** prospective diagnostic-inference test  
**Primary question:** can one unchanged continuity residual recover the sign, location and magnitude of a concealed
source, sink or relation leak from raw stored quantities and declared internal transfers?

## 1. Frozen residual

For identities \(i=1,\dots,n\), let

\[
\underbrace{q_i(t)}_{\substack{\text{stored quantity}\\\text{inside identity }i}}
\]

be measured directly. Let

\[
\underbrace{g_i(t)}_{\substack{\text{known net internal transfer}\\\text{into identity }i}}
\]

be calculated from the declared coupling flows, with

\[
\sum_i g_i=0
\]

only when every internal relation is lossless and fully represented.

The hidden `Other` estimator is

\[
\boxed{
\widehat s_i(t)
=
\frac{dq_i}{dt}
-
g_i(t)
}.
\]

No damping, resistance or quantum-decay coefficient is supplied to this estimator.

The derivative \(dq_i/dt\) is calculated from the raw stored-quantity time series by one unchanged fourth-order
central difference:

\[
\frac{dq_i}{dt}(t_k)
\approx
\frac{
-q_i(t_{k+2})+8q_i(t_{k+1})-8q_i(t_{k-1})+q_i(t_{k-2})
}{12\Delta t}.
\]

Only the two edge samples at each end are omitted because this stencil is undefined there.

## 2. Frozen systems

### System A — damped coupled mechanical identities

Two onsite oscillators are coupled by a spring. The measured identity vector is:

1. oscillator 1 energy;
2. coupling-spring energy;
3. oscillator 2 energy.

A hidden viscous sink acts only on oscillator 2. Its coefficient and native sink formula are withheld from the
estimator.

### System B — resistive electromagnetic relation

Two capacitive identities exchange energy through a resistor. The measured identity vector is:

1. capacitor 1 energy;
2. zero-storage coupling relation;
3. capacitor 2 energy.

The estimator receives power leaving capacitor 1 and power reaching capacitor 2, but is not told that their
difference is Joule heating. The hidden `Other` should therefore be localized to the relation rather than either
capacitor.

### System C — open two-level quantum holdout

Two coupled probability identities exchange probability current. A hidden decay channel acts only on state 2.
The non-Hermitian decay coefficient and native sink formula are withheld. This system is the untouched holdout;
the residual definition and pass thresholds cannot change after Systems A and B.

## 3. Required predictions

For each system the estimator must freeze:

1. **sign:** source or sink;
2. **location:** the child or relation with the largest integrated absolute residual;
3. **time-resolved magnitude:** \(\widehat s_i(t)\);
4. **integrated amount:** \(\int\widehat s_i\,dt\).

The native source/sink formula is revealed only for scoring.

## 4. Controls

1. **No-Other control:** \(s_i=0\) everywhere.
2. **Parent-only control:** place the recovered total equally across all identities, erasing location.
3. **Wrong-location control:** assign the recovered source waveform to the identity with the smallest integrated
   residual.

The primary ARA residual must recover more information than merely noticing that the parent total changed.

## 5. Frozen simulation and data rules

- Use deterministic fourth-order Runge–Kutta integration.
- Use raw simulated state variables; no smoothing, Fourier decomposition, fitted regression or learned component
  is permitted.
- Use at least 4,001 time samples per system.
- Score only interior points supported by the frozen derivative stencil.
- Define an active source point as
  \[
  |s_i(t)|\ge 10^{-6}\max_t|s_i(t)|.
  \]
- Save bounded deterministic samples; regenerate the complete arrays from the reproduction script.

## 6. Pass criteria

Each system passes only if:

1. the predicted hidden location is exactly correct;
2. active-point sign accuracy is at least `99.9%`;
3. time-resolved source correlation is at least `0.999`;
4. normalized source RMSE is at most `0.001` of the native peak magnitude;
5. integrated hidden-amount relative error is at most `0.001`;
6. inactive identities have residual RMS at most `0.001` of the active native peak;
7. the located residual beats all three controls on their declared sign/location/magnitude task.

The overall result passes only if all three systems pass without changing the estimator.

## 7. Interpretation fence

A pass would show that ARA's boundary-aware continuity account can diagnose an omitted term and distinguish a
child-local sink from a relation-local leak. That is more informative than the preceding exact closure identity.

It would still be a controlled inverse problem: the relevant stored quantities and internal flows are supplied,
and the residual is a standard conservation diagnostic. A pass would not by itself establish a new force,
universal fractality, Phi, quantum gravity or superiority over all established system-identification methods.

The next level after a pass would be a true forward holdout: infer a compact law for the recovered `Other` from
development systems, freeze it, and predict the loss waveform in a new system before observing its stored-quantity
change.
