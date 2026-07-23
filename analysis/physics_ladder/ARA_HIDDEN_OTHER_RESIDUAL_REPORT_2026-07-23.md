# ARA hidden `Other` residual test

**Orientation:** child-local stored quantities and declared internal transfers are read upward into one parent
continuity account. Negative residual means an unmodelled sink; positive residual means an unmodelled source.

**Date:** 23 July 2026  
**Status:** `SUPPORTED` controlled diagnostic-inference result  
**Protocol:** `HIDDEN_OTHER_RESIDUAL_PROTOCOL_2026-07-23.md`

## Answer first

The frozen ARA continuity residual

\[
\boxed{
\widehat s_i(t)
=
\frac{dq_i}{dt}-g_i(t)
}
\]

recovered the concealed `Other` term in all three controlled systems without receiving the damping, resistance or
quantum-decay coefficient. It identified the correct child or relation, recovered the sink sign at every active
sample, matched the hidden waveform to numerical precision, and recovered the integrated amount.

This is the first test in this sequence where the operator did more than reconstruct a parent that was already
closed: it located an omitted contribution. It is still a conservation residual in a controlled inverse problem,
not a forward prediction of a new law or an unknown real-world force.

## Frozen result

| System | Frozen role | Correct location | Sign accuracy | Source correlation | Peak-normalized RMSE | Integrated relative error |
|---|---|---|---:|---:|---:|---:|
| Damped coupled oscillators | development | oscillator 2 | 1.000000 | 1.000000 | \(1.0554\times10^{-9}\) | \(4.5071\times10^{-11}\) |
| Resistive capacitor coupling | verification | coupling relation | 1.000000 | 1.000000 | \(1.2855\times10^{-17}\) | 0 |
| Open two-level probability | untouched holdout | quantum state 2 | 1.000000 | 1.000000 | \(1.9916\times10^{-11}\) | \(7.3436\times10^{-12}\) |

All `18,991` derivative-supported samples were scored. All three models passed every frozen threshold. The largest
inactive-identity residual was \(1.8859\times10^{-9}\) of the active native peak.

## What was hidden

The estimator saw only each identity's stored quantity \(q_i(t)\) and its declared net internal transfer \(g_i(t)\).
The following native laws were withheld until scoring:

\[
\begin{array}{rcl}
\text{mechanics:}&s_{\rm hidden}&=-\gamma p_2^2,\\
\text{electromagnetism:}&s_{\rm hidden}&=-R I^2,\\
\text{quantum holdout:}&s_{\rm hidden}&=-\Gamma |b|^2.
\end{array}
\]

The electromagnetic case is the important localization check. The missing energy was not assigned to either
capacitor. It appeared on the zero-storage coupling relation because the power leaving capacitor 1 exceeded the
power arriving at capacitor 2 by \(RI^2\).

## Controls

The primary residual was compared with three deliberately incomplete readings:

1. no `Other` anywhere;
2. the correct parent loss spread equally across all identities;
3. the correct waveform assigned to the wrong identity.

The strongest control peak-normalized RMSE was `0.060912` in the electromagnetic system. The primary errors ranged
from \(1.29\times10^{-17}\) to \(1.06\times10^{-9}\), and only the primary method recovered location and magnitude
together.

## Plain-language explanation

For each child, the test asked: “How fast did the amount inside this child actually change, and how much of that
change was already explained by the named exchanges with its neighbours?” The difference is `Other`.

In the oscillator, that difference sat on the damped second oscillator. In the circuit, it sat in the resistor
between the capacitors. In the quantum holdout, it sat on the decaying second state. The same subtraction found all
three without being told the native loss coefficient.

That matches the intended ARA bookkeeping: a missing contribution is not forced into Phase A or Phase B, and it is
not smeared over the parent. It stays attached to the boundary, child or relation where the account fails to close.

## What the result establishes

- The exact child-to-parent boundary operator can be extended to non-closed systems by retaining a signed
  child/relation residual.
- `Other` is operationally measurable once the boundary, stored quantity and internal transfers are declared.
- The method distinguishes a child-local sink from a relation-local leak.
- One unchanged continuity calculation works for mechanical energy, electromagnetic energy and quantum
  probability in these controlled models.

## What it does not establish

- The residual is standard conservation accounting expressed in ARA language; exact recovery is expected when
  \(q_i\), \(g_i\) and the derivative are accurate.
- The test does not discover the functional law \(-\gamma p_2^2\), \(-RI^2\) or \(-\Gamma|b|^2\) in advance.
- The test uses simulated noiseless data with fully declared internal transfers.
- It does not prove universal fractality, Phi handover, a new force, or superiority over established state
  estimation and system-identification methods.

The next genuinely harder rung is forward law transfer: learn a compact rule for the recovered residual on
development systems, freeze it, and predict the held-out `Other` waveform before using the held-out stored-quantity
change.

## Reproduction

From the repository root:

```powershell
python analysis/physics_ladder/ara_hidden_other_residual_test.py
python analysis/physics_ladder/validate_ara_hidden_other_residual.py
```

Generated artifacts:

- `ARA_HIDDEN_OTHER_RESIDUAL_RESULTS.json`
- `ARA_HIDDEN_OTHER_RESIDUAL_SUMMARY.csv`
- `ARA_HIDDEN_OTHER_RESIDUAL_BOUNDED_SAMPLE.csv`
- `ARA_HIDDEN_OTHER_RESIDUAL_VALIDATION.json`

The independent validator does not call the simulation or recovery functions. It verifies the frozen protocol hash,
all pass thresholds, and independently recomputes location, sign, waveform error, inactive residual and parent
closure from the bounded output.
