# MX2 draft — is the TE-ARA particle gap a handover or identity-formation state?

**Prepared:** 12 July 2026  
**Status:** `DRAFT / DEVELOPMENT FEASIBILITY INSPECTED / NO CONFIRMATORY RESULT`  
**Parent:** MX1 Gauss ↔ ARA/TE-ARA crosswalk  
**Data rule:** Alves/OSIRIS remains development-only. MX1 frozen artifacts and sealed confirmation rules must not be
changed by MX2.

## Outcome first

Test whether the independent source-participation gap

\[
\underbrace{\Delta_{\mathrm P}(t)}_{\substack{\text{field-predicted source participation}\\
\text{minus particle-measured participation}}}
=
\underbrace{\mathrm{TE\!-\!ARA}_{\rho,G}(t)}_{\text{Gauss-predicted source}}
-
\underbrace{\mathrm{TE\!-\!ARA}_{\rho,F}(t)}_{\text{particle source}}
\]

is associated with actual field–particle energy exchange, rather than being only particle noise, field amplitude or
the deterministic \(ik\) field-to-source projection.

The first unregistered feasibility inspection gives a narrowing result: \(\Delta_{\mathrm P}\) behaves more like an
identity-formation/coherence **state** than an instantaneous power-transfer meter.

## Source and data conventions

The public record describes a 1D1V electrostatic two-stream instability with two equal electron beams at
\(\pm0.2c\), immobile neutralising ions, periodic boundaries, a relativistic Boris pusher and charge-conserving
Esirkepov deposition.

Local array inspection establishes:

\[
v(u)=\frac{u}{\sqrt{1+u^2}}
\]

to maximum numerical error \(1.5\times10^{-8}\). The `u` grid is uniformly spaced by
\(du=0.00390625\), and the distribution array is integrated along this momentum grid. Therefore use \(u=p/(m_ec)\),
\(v/c=u/\gamma\), and \(\gamma=\sqrt{1+u^2}\).

This convention must be re-verified from metadata or conservation before any transfer to another archive.

## Physical reconstruction

In the simulation's normalised units:

\[
\underbrace{n_e(x,t)}_{\text{electron density}}
=
\Delta u\sum_u F(t,u,x),
\]

\[
\underbrace{J(x,t)}_{\text{electron current}}
=
-\Delta u\sum_u
\underbrace{v(u)}_{\text{particle velocity}}
F(t,u,x),
\]

\[
\underbrace{U_E(t)}_{\text{total electric-field energy}}
=
\frac{\Delta x}{2}\sum_x E(x,t)^2,
\]

\[
\underbrace{K_e(t)}_{\text{total relativistic electron kinetic energy}}
=
\Delta x\,\Delta u
\sum_{x,u}
\underbrace{(\gamma(u)-1)}_{\text{kinetic energy per }m_ec^2}
F(t,u,x),
\]

\[
\underbrace{P_{E\to p}(t)}_{\text{field-to-particle power}}
=
\Delta x\sum_xJ(x,t)E(x,t).
\]

For the periodic electrostatic domain, require

\[
\frac{dU_E}{dt}\approx-P_{E\to p},
\qquad
\frac{dK_e}{dt}\approx P_{E\to p},
\qquad
\frac{d(U_E+K_e)}{dt}\approx0.
\]

This conservation gate must pass before interpreting any TE-ARA gap physically.

## Development feasibility already inspected

This inspection occurred before a formal MX2 freeze, so it is calibration only:

| Check | Development result |
|---|---:|
| \(dU_E/dt\) vs \(-P_{E\to p}\) | \(r=0.9839\), NRMSE 0.236, slope 0.913 |
| \(dK_e/dt\) vs \(P_{E\to p}\) | \(r=0.9831\), NRMSE 0.237, slope 0.923 |
| Relative range of \(U_E+K_e\) | 0.00101 (about 0.10%) |
| \(U_E\) change, first to last saved slice | +0.01303 |
| \(K_e\) change, first to last saved slice | -0.01303 |

The archive therefore supports a meaningful energy-transfer calculation.

Exploratory gap associations on eligible slices:

| Association | Correlation |
|---|---:|
| \(\Delta_{\mathrm P}\) vs field energy \(U_E\) | -0.725 |
| \(-d\Delta_{\mathrm P}/dt\) vs particle-to-field power \(-P_{E\to p}\) | -0.091 |
| \(-d\Delta_{\mathrm P}/dt\) vs \(dU_E/dt\) | -0.028 |

The instantaneous handover-rate interpretation is not supported by this raw development check. The gap closes as the
field/particle identity becomes established, but its moment-to-moment closing rate does not follow the energy-transfer
rate.

## Revised candidate interpretations

### H1 — instantaneous handover meter

\[
-\frac{d\Delta_{\mathrm P}}{dt}
\propto
-P_{E\to p}.
\]

**Development status:** raw null. Retain as a falsified/simple control; do not rescue by choosing a favourable smoother
or lag after seeing the data.

### H2 — cumulative identity-formation state

\[
\Delta_{\mathrm P}(t)
\downarrow
\quad\text{as}\quad
\underbrace{\int_{t_0}^{t}-P_{E\to p}(s)\,ds}_{\text{particle-to-field transferred energy}}
\uparrow.
\]

**Development status:** compatible but confounded by field amplitude and signal-to-noise. Requires matched-amplitude
and independent-noise controls.

### H3 — local coupling organisation

At phase-aligned cells, regions with sustained cumulative work exchange should show reduced field/particle identity
disagreement after a predeclared delay. This is stronger than a global time correlation because it predicts where the
identity closes.

**Development status:** not run.

## Required controls

1. **Amplitude/SNR baseline:** predict \(\Delta_{\mathrm P}\) from \(E_{\mathrm{rms}}\), source activity and a
   predeclared particle-noise proxy.
2. **Spectral-Other baseline:** include particle high-\(k\), non-identity power without using the target gap itself.
3. **Matched-amplitude hysteresis:** compare rising and saturated/declining slices at similar \(E_{\mathrm{rms}}\).
   A genuine formation-state memory may differ when amplitude is matched; a simple SNR effect should not.
4. **Deterministic projection control:** \(\Delta_{\mathcal G}=\mathrm{TE\!-\!ARA}_E-
   \mathrm{TE\!-\!ARA}_{\rho,G}\) must not be relabelled as independent physical exchange.
5. **Time-shuffled work:** preserve gap and amplitude distributions but destroy transfer order.
6. **Phase/cell shuffle:** preserve marginal cell activity but destroy local coupling alignment.
7. **Alternative identity families:** fixed matched-size non-harmonic mode sets must not reproduce the same association.

## Prospective scoring design

Because the full Alves development series has now been inspected, it cannot supply confirmatory MX2 evidence.

Before opening a new archive:

1. freeze momentum/velocity reconstruction and signs;
2. freeze derivative, smoothing and any allowed lag from physical sampling—not performance;
3. freeze amplitude/noise controls and matched-amplitude bins;
4. freeze global state and local cell targets;
5. require the energy-conservation gate;
6. register thresholds and hashes;
7. test once on an untouched kinetic archive containing \(E\) and \(F(x,u,t)\).

Primary comparison:

\[
\underbrace{\Delta_{\mathrm P}}_{\text{particle identity gap}}
\sim
\underbrace{\text{amplitude + SNR + spectral Other}}_{\text{null/control model}}
+
\underbrace{\text{cumulative work + transfer direction/history}}_{\text{handover-added model}}.
\]

Handover support requires the added work/history terms to improve held-out prediction beyond the control model, retain
their predeclared sign, and reproduce in local cells. A global correlation with amplitude or time is insufficient.

Secondary candidate identity-closure index:

\[
\underbrace{C_{\mathrm{id}}}_{\text{0--1 participation agreement}}
=
1-\frac{|\Delta_{\mathrm P}|}{2}.
\]

Compare it prospectively with established coherent-mode/trapping diagnostics. It is useful only if it is robust to
particle noise and adds held-out onset/state information beyond field amplitude and ordinary spectral coherence.

## Interpretation rules

- Energy conservation passes, instantaneous association fails: not a live power-flow meter.
- Control model explains the gap: signal quality or ordinary spectral maturation is sufficient.
- Cumulative/local work adds held-out value: supports a physical identity-formation/handover marker.
- Only the deterministic \(ik\) gap behaves: supports transformation geometry, not a new physical node.
- New archive lacks adequate momentum range or normalisation: mark MX2 untestable there; do not improvise.

## Plain-language summary

Measure how much energy the particles give the field at every saved moment. Ask whether the orange–green TE-ARA gap
closes at the same moment, after the exchange, or only because the signal becomes larger and cleaner. The existing
data say it does **not** close moment by moment with power flow. It may instead describe how completely the particle
web has settled into the field's identity. A new untouched dataset and stronger noise controls are required to decide.
