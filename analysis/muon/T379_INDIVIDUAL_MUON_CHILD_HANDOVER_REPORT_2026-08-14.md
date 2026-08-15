# T379 — individual-muon child handover

**Date:** 14 August 2026  
**Primary verdict:** **INDIVIDUAL ADVANCE INFORMATION NOT SUPPORTED**  
**Frozen `x_mu = 0.50` landmark verdict:** **NOT SUPPORTED**

## Answer first

Public data do exist for individual stopped-muon candidates. T379 used an
independent QuarkNet four-counter detector and linked each incoming muon pulse
pattern to its own later charged-electron candidate. The electron is directly
detected; the two neutrinos are produced in the same muon decay but are not
directly observed by this instrument.

The event-level ARA coordinate was real and reproducible, but it did **not**
provide held-out information about which individual muon would decay earlier
after ordinary pulse strength, multiplicity and stack depth were known.

This preserves the earlier distinction:

- the population release curve locates a parent-scale handover;
- that parent crossing is not automatically an internal countdown carried by
  every individual child.

## Frozen question and coordinate

Calibration used `6845.2020.0211.0` and `6845.2020.0212.0`. Later files
`6845.2020.0317.0` and `6845.2020.0318.0` remained untouched holdout data.
All runs used the same four closely stacked solid-plastic scintillators.

Calibration-only channel medians normalised the prompt time-over-threshold
measurements. The incoming child cut was

\[
A=q_1+q_2,
\qquad
B=q_3+q_4,
\qquad
x_\mu=\frac{2B}{A+B}.
\]

No delayed-electron time, channel or amplitude entered this coordinate.

The prospective models were:

1. `M0`: population lifetime plus uniform accidental component;
2. `MG`: total prompt strength, multiplicity and ordinary stack depth;
3. `MA`: `MG` plus signed ARA position, asymmetry and its frozen depth
   interaction;
4. `MW`: an intentionally wrong diagonal counter pairing;
5. `ML50`: `MG` plus the separately frozen `x_mu=0.50±0.05` landmark.

## Data reduction and quality

The four raw files contained `15,884,080` lines and `4,720,318` reconstructed
hardware triggers. They reduced to `4,505` clean, event-linked muon/electron
pairs:

| split | linked pairs |
|---|---:|
| calibration | 2,396 |
| untouched holdout | 2,109 |

The parser initially returned zero pairs because QuarkNet records the stopped
muon and later electron in two linked hardware triggers. Correcting that raw
event-linking layer produced about 1,000–1,200 candidates per file, consistent
with the order of magnitude of the earlier detector-6234 record.

The frozen protocol prose described the TMC subcount as `0.75 ns`. For this
25 MHz hardware, the five-bit subcount spans a 40 ns counter tick and is
`1.25 ns`; the executable reduction used the exact run clock divided by 32.
This was a pre-outcome format correction, not a fitted physical parameter.

Only `56` unmatched falling edges occurred across the complete raw archive,
and there were no recorded parse failures. Calibration-only fourfold ToT
medians were `18.75`, `20.00`, `18.75` and `23.75 ns` for channels 1–4.

## Prospective result

Lower held-out negative log likelihood is better.

| model | held-out mean NLL |
|---|---:|
| memoryless `M0` | 1.8528471 |
| ordinary geometry `MG` | **1.8040590** |
| ARA child relation `MA` | 1.8046886 |
| wrong diagonal pair `MW` | 1.8028830 |
| frozen landmark `ML50` | 1.8040626 |

The registered ARA increment was

\[
\operatorname{NLL}(MG)-\operatorname{NLL}(MA)
=-0.0006297,
\]

with chronological-block 95% interval

\[
[-0.0014962,\;0.0002848].
\]

It was negative in both untouched runs (`-0.0004713` and `-0.0007956`). Thus
the ARA terms very slightly worsened prediction rather than improving it, and
the interval includes zero.

All frozen cut variants agreed:

| cut | MG−MA NLL | 95% interval | verdict |
|---|---:|---:|---|
| main, 100 ns / 0.30 µs | -0.000630 | [-0.001496, 0.000285] | not supported |
| 50 ns prompt | -0.000566 | [-0.001432, 0.000322] | not supported |
| 150 ns prompt | -0.000691 | [-0.001556, 0.000187] | not supported |
| 0.20 µs lower delay | -0.000326 | [-0.000854, 0.000187] | not supported |
| 0.50 µs lower delay | -0.000525 | [-0.001350, 0.000305] | not supported |

## Frozen `0.50` landmark

The calibration data placed the `0.50±0.05` window in the predeclared
higher-hazard direction. That direction did not transfer consistently:

- March 17: ordinary-minus-landmark NLL `+0.0002826`;
- March 18: ordinary-minus-landmark NLL `-0.0003036`;
- pooled difference `-0.0000037`;
- chronological-block 95% interval `[-0.0012136, 0.0010606]`.

The landmark therefore failed its independent gate.

## Why the raw plot still looks structured

On holdout events,

\[
\rho(x_\mu,\text{delay})=0.1213,
\qquad
\rho(\text{depth},\text{delay})=0.1205,
\]

but

\[
\rho(x_\mu,\text{depth})=0.9793.
\]

The ARA coordinate is therefore almost the same ordering as ordinary stopping
depth in this detector. The visible timing gradient is genuine detector/event
structure, but it is already carried by the ordinary geometry control. The
ARA decompression did not add a separate child clock.

The wrong diagonal pair had the lowest pooled NLL, but it did not beat `MG` in
both holdout runs and was not a registered physical cut. It is a diagnostic of
residual detector geometry, not a positive ARA result.

Post-hoc quality checks did not reverse the conclusion. Removing the `x=0`
and `x=2` endpoints remained unsupported. Fourfold-only events had a positive
point estimate (`+0.00369`) but a 95% interval crossing zero
(`[-0.00106, 0.00848]`), so it is only a possible deeper-cut lead.

## ARA interpretation boundary

T379 does not say that the muon population lacks an ARA handover. It says that
this particular incoming upper/lower child cut does not tell us the later
handover time of one otherwise similar muon.

A handful of named events can illustrate the geometry, but it cannot establish
individual predictability. Even with 2,109 held-out individual events, no
reproducible advance information appeared beyond ordinary detector geometry.

The next genuinely different child test would require event-linked internal
state information not present here—such as muon spin/polarisation, local field,
stopping material, and charged-daughter energy or direction—while still hiding
the later decay time during coordinate construction.

## Reproduction records

- frozen protocol: `T379_INDIVIDUAL_MUON_CHILD_HANDOVER_PROTOCOL_2026-08-14.md`
- executable: `t379_individual_muon_child_handover.py`
- saveable report: `T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER.html`
- event table: `T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv`
- numerical result: `T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER_RESULTS.json`
- validation record: `T379_individual_muon_child/T379_INDIVIDUAL_MUON_CHILD_HANDOVER_VALIDATION.json`
