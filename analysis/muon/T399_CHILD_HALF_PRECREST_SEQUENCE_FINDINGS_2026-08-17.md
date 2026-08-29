# T399 — child-half before neutrino release crest findings

**Executed:** 2026-08-17  
**Frozen protocol:** `T399_CHILD_HALF_PRECREST_SEQUENCE_PROTOCOL_2026-08-17.md`  
**Frozen verdict:** **CHILD-HALF PRE-CREST SEQUENCE NOT SUPPORTED at the predeclared high-stringency gate; directionally supported in the fitted identity and independent coarse holdout**

## Question

T398 visually suggested the following ordered population sequence:

\[
\text{prompt crest}
\rightarrow
\text{branch equality}
\rightarrow
x=0.5\text{ child half}
\rightarrow
\text{delayed-neutrino release crest}.
\]

It also suggested that the prompt crest sat approximately one quarter of an ARA unit below child half. T399 froze and tested those two statements without changing the population-versus-individual evidence boundary.

## Primary native result

The fitted COHERENT identity shows the exact proposed order:

| Landmark | Time after SNS pulse | Cumulative ARA |
|---|---:|---:|
| Prompt \(\nu_\mu\) crest | \(0.500500\ \mu s\) | \(0.244269\) |
| Prompt/delayed branch equality | \(0.636074\ \mu s\) | \(0.437389\) |
| Child half | \(0.686649\ \mu s\) | \(0.500000\) |
| Delayed \(\nu_e+\bar\nu_\mu\) crest | \(0.785500\ \mu s\) | \(0.600426\) |

Therefore child half occurs

\[
0.785500-0.686649=0.098851\ \mu s
\]

before the delayed release-rate maximum. The prompt-crest-to-half displacement is

\[
0.5-0.244269=0.255731,
\]

which passes the frozen \(0.20\)–\(0.30\) calibration window and lies close to the proposed quarter.

## Robustness results

- **Registered leave-one-bin-out fits:** child half preceded the delayed crest in \(17/18=94.44\%\) of cuts, passing the frozen 90% gate. The complete four-landmark order held in 83.33%.
- **10,000 fixed-shape yield-sensitivity draws:** child half preceded the delayed crest in **93.13%**, below the frozen 95% gate. The quarter window held in 76.92%; the 95% displacement interval was `[0.167711,0.330878]`.
- **Independent T378 release:** piecewise-uniform child half occurred at \(0.81708\ \mu s\), before the delayed peak bin centre at \(1.25\ \mu s\). Its 0.5-\(\mu s\) bins cannot test the full native order or the quarter displacement.
- **Circular-shift control:** 87 of 1,199 wrong relative phases matched both the real four-landmark order and a quarter error no larger than the real curve. The add-one upper-tail value was **0.07333**, failing the frozen \(p\le0.05\) alignment gate.

Six of eight frozen gates passed. The two failures were the 95% yield-sensitivity threshold and the alignment-specific circular-shift threshold. Independent saved-artifact validation passed every implementation and presentation check.

## What the failure taught us

The failed robustness gate is not a random contradiction of the plotted geometry. A post-result diagnostic exposed the parent-asymmetry dependency.

For the released branch shapes, the prompt share must exceed

\[
s_P=0.126966
\]

for cumulative child half to occur before the delayed crest. The fitted identity has

\[
s_P=0.188586,
\]

a margin of \(0.061619\). The only leave-one-out failure removes energy bin 1 and drives the prompt share down to \(0.085961\), below the derived threshold.

The defensible ARA translation is therefore:

> The fitted muon-neutrino population places child half before the delayed crest, and this order is strongly but not 95%-robust to the registered amplitude uncertainty. Its location is displaced by parent branch asymmetry; it is not a universal yield-independent constant.

This agrees with the existing ARA rule that pure landmarks supply the geometry while an identity's asymmetric parent/child mixture controls where its observed flow occupies that geometry.

## Claim boundary

T399 does **not** show an individual neutrino being born at \(x=0.5\). It shows that the **joint fitted delayed-neutrino population** reaches a cumulative child-half landmark before its release-rate crest in the best-fit identity and the independent coarse release. The two daughter flavors remain statistically combined at detector-event level.

## Artifacts

- `T399_child_half_precrest_sequence/T399_CHILD_HALF_PRECREST_SEQUENCE_REPORT.html`
- `T399_child_half_precrest_sequence/T399_CHILD_HALF_PRECREST_SEQUENCE.svg`
- `T399_child_half_precrest_sequence/T399_RESULTS.json`
- `T399_child_half_precrest_sequence/T399_VALIDATION.json`
- `T399_child_half_precrest_sequence/T399_NATIVE_LANDMARKS.csv`
- `T399_child_half_precrest_sequence/T399_LEAVE_ONE_OUT_LANDMARKS.csv`
- `T399_child_half_precrest_sequence/T399_CIRCULAR_SHIFT_CONTROLS.csv`
- `T399_child_half_precrest_sequence/T399_YIELD_SENSITIVITY_HISTOGRAM.csv`

