# Q48 — Quantum \(1/e \leftrightarrow (2-\phi)\) Carrier Wobble

> **PROXY TEST — CONSTRUCT INVALID FOR THE INTENDED CLAIM.**
> This run measured the circle's internal parent-to-parent turning amount.
> Dylan's intended object was the external/meta vector that carries the whole
> rotating circle forward through time. The numerical result below remains a
> reproducible description of that proxy and must not be counted as evidence
> against the intended \(1/e\leftrightarrow\phi\) directional-path claim.

**Date:** 30 July 2026  
**Ledger:** T308  
**Source status:** retrospective ARA-native test on an opened deterministic
quantum simulator  
**Proxy verdict:** **NOT SUPPORTED for the proxy only — 0/4 substantive gates**  
**ARA claim verdict:** **WRONG OBJECT / UNTESTED**  
**Validation:** **PASS — 20/20 checks; 282 raw events independently
recalculated**

## Answer first

The requested test was:

> Treat \(1/e\) as the local `0` pole and anti-Phi
> \(2-\phi=\phi^{-2}\) as the local `2` pole. Does the complete quantum
> parent movement repeatedly wobble between them, with `3/8` acting as the
> near-ridge triangulation point?

In this archive, **no**.

Across `33,604` parent-to-parent movement events reconstructed from the full
available timeline:

- only `7` events (`0.0208%`) entered the proposed interval;
- those seven came from seven different lineages and six seeds;
- every event was isolated;
- there were zero three-event carrier runs;
- there were zero increasing or decreasing half-traversals;
- there were zero ordered crossings of the local ridge;
- all seven occurred during the early development portion of the simulator.

The seven events did not cluster at the carrier ridge. After remapping the
interval to its own ARA diameter, their median was

\[
\boxed{x_{\rm median}=0.121}
\]

on the local `0..2` coordinate. Their complete range was `0.074..0.479`.
The ridge is `1.0`.

Plainly: the rare events sat close to the \(1/e\) pole and then disappeared.
They did not travel back and forth through the interval.

## The exact ARA being tested

The selected poles were

\[
\underbrace{L=\frac1e}_{\substack{\text{local 0}\\
\text{Space-side pole}}}
=0.367879441\ldots
\]

and

\[
\underbrace{R=2-\phi=\phi^{-2}}_{\substack{\text{local 2}\\
\text{Time-side pole}}}
=0.381966011\ldots.
\]

The local ARA coordinate was

\[
\underbrace{x(\delta)}_{\substack{\text{movement heading}\\
\text{inside the proposed carrier}}}
=
2\,
\frac{
\underbrace{\delta}_{\text{measured parent movement}}
-
\underbrace{1/e}_{\text{local 0}}
}{
\underbrace{(2-\phi)-1/e}_{\text{carrier diameter}}
}.
\]

This retains the original measured movement. It only asks where that movement
sits between the declared poles.

The exact interval ridge is

\[
\frac{1/e+(2-\phi)}2
=0.374922726\ldots.
\]

The proposed `3/8` landmark is

\[
\frac38=0.375,
\qquad
x(3/8)=1.010971271\ldots.
\]

So `3/8` really is extremely close to the **geometric midpoint** of the
selected interval. That is an exact mathematical crosswalk. The empirical
question was whether the quantum movement actually used that ridge.

It did not in this source.

## What was measured

Q48 preserved Q47's complete-lattice movement coordinate. At each of the four
ordered internal quadrant anchors, the complete connected \(3\times3\)
identity was compared with the same anchor in the next parent cycle:

\[
\underbrace{\delta_{r,q}}_{\substack{\text{one quadrant strand's}\\
\text{parent-to-parent movement}}}
=
\frac1{2\pi}
\cos^{-1}
\left(
\left\langle U_{r,q},U_{r+1,q}\right\rangle_F
\right).
\]

The parent reading was the equal four-strand mean:

\[
\underbrace{\bar\delta_r}_{\text{complete parent movement}}
=
\frac{
\delta_{r,1}+\delta_{r,2}+\delta_{r,3}+\delta_{r,4}
}{4}.
\]

Q48 then restored temporal order. A real wobble required consecutive
\(\bar\delta_r\) values to move through the local interval and cross its
ridge. Merely landing once near a landmark was insufficient.

## Frozen gates

| Gate | Frozen requirement | Result |
|---|---|---|
| G0 | Reproduce Q47 and the exact geometry | **PASS** |
| G1 | At least 20 carrier events across 10 lineages and 10 seeds | **FAIL:** 7 events, 7 lineages, 6 seeds |
| G2 | At least five full ordered half-traversals in both directions | **FAIL:** 0 |
| G3 | Ordered traversal beats 5,000 lineage-permutation nulls | **FAIL:** no eligible traversal |
| G4 | Measured carrier events use the `3/8`/ridge neighborhood | **FAIL:** 0% near it; median \(x=0.121\) |

Frozen verdict: **NOT SUPPORTED — 0/4 substantive gates**.

## Why the earlier `3/8` visual was suggestive

The earlier Q47 event contained three quadrant strands that moved almost a
half-turn and one that barely moved:

\[
\frac{0.5+0.5+0+0.5}{4}
=
\frac38.
\]

Q48 found six additional events with the same broad anatomy. Typical examples
looked like:

\[
(0.489,\ 0.489,\ 0.002,\ 0.495)
\longrightarrow
\bar\delta=0.369.
\]

That is unmistakably a **three-moving / one-preserved** parent state.
However, its measured mean is below exact `3/8`. On the broad half-turn
scale, `0.369` looks visually close to `0.375`. On the much narrower
\(1/e\leftrightarrow(2-\phi)\) carrier scale, the difference is substantial:
the event lands near the local `0` pole, not the ridge.

This is exactly why the local ARA remapping mattered. It separated two claims
that initially looked identical:

1. **Supported descriptively:** rare parent transitions can contain three
   near-opposed strands and one preserved strand.
2. **Not supported here:** those events form a continuous wave wobbling
   between \(1/e\) and anti-Phi.

## The stronger pattern exposed

The development-half transition tail formed visible bands near the ideal
four-strand levels

\[
0,\quad\frac18,\quad\frac14,\quad\frac38,\quad\frac12.
\]

Among the `480` events with movement at least `0.05`, nearest-level counts
were:

| Nearest level | Events |
|---|---:|
| \(1/8\) | 278 |
| \(1/4\) | 64 |
| \(3/8\) | 89 |
| \(1/2\) | 49 |

The `1/8` and `1/4` bands were especially tight: `99.64%` and `90.63%`,
respectively, lay within `0.02` turns of their ideal levels. The `3/8` and
`1/2` assignments were broader, so this is a **descriptive closure-band
observation**, not yet a frozen quantization law.

In ARA language, the better current reading is:

> The parent normally recurs. During sparse early transitions, one, two,
> three or four quadrant strands can reorient strongly. Averaging the four
> strands produces approximate \(k/8\) parent movement bands. The apparent
> `3/8` event is the three-strand member of that family, not evidence of a
> separate continuous Phi carrier.

## Important segmentation result

Q47 began cycle extraction at the evaluation boundary `t=250` and found one
large opening event in the carrier interval. Q48 instead began at the start
of the complete timeline and maintained one continuous parent-cycle
segmentation.

Under that continuous extraction:

- the Q47 evaluation-opening carrier event was not retained as the same
  parent-to-parent comparison;
- all seven carrier occupants appeared earlier, during development;
- no carrier occupant appeared in later evaluation behavior.

This makes the old single event more sensitive to where the measurement
window was opened than a universal carrier should be. Q48 still reproduced
the exact Q47 result separately, so this is not a calculation discrepancy;
it is a measurement-boundary distinction.

## Plain-language translation

Your proposed tiny ARA is mathematically clean:

- \(1/e\) is one pole;
- anti-Phi is the other;
- `3/8` is almost exactly their midpoint.

But this quantum dataset does not show the parent direction breathing between
those poles. It mostly sits at recurrence. Rarely, several of the four
internal strands flip together. When three flip, the parent average naturally
lands somewhere near `3/8`.

So the evidence points to **a discrete four-strand closure state**, not the
continuous meta-vector wobble we were testing.

That does not erase the exact \(1/e\), anti-Phi, and `3/8` relation. It tells
us that this particular quantum movement observable does not activate it as
a recurring carrier.

## Scientific boundary

- The source is a deterministic public simulator, not quantum hardware.
- The source and Q47 evaluation result were already open.
- The development-half parent movement was newly exposed in Q48.
- The movement coordinate is a fraction-of-turn displacement, not an
  absolute spatial heading.
- The connected matrices are exactly diagonal; true off-axis movement is not
  represented.
- Failure here rejects this coordinate/source combination, not every possible
  ARA realization of a time vector.

## Reproduction

- Frozen protocol:
  `Q48_E_PHI_CARRIER_WOBBLE_PROTOCOL_v1_FROZEN.md`
- Runner:
  `q48_e_phi_carrier_wobble.py`
- Machine-readable result:
  `Q48_E_PHI_CARRIER_WOBBLE_RESULTS.json`
- Compressed event table:
  `Q48_E_PHI_CARRIER_WOBBLE_EVENTS.csv.gz`
- Figure:
  `Q48_E_PHI_CARRIER_WOBBLE.png`
- Validator:
  `q48_validate_e_phi_carrier_wobble.py`
- Validation:
  `Q48_E_PHI_CARRIER_WOBBLE_VALIDATION.json`
