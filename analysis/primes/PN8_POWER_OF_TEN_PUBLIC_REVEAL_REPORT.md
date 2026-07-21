# PN8 Power-of-Ten Public-Reveal Pilot

**Test ID:** `PN8/POWER-OF-TEN-PUBLIC-REVEAL/PILOT-v1`  
**Date:** 19 July 2026  
**Status:** `PROSPECTIVE PUBLIC REVEAL / PROBABILITY TRANSFER POSITIVE / SHARPNESS GATE FAILED / 3 OF 4 PRIMARY CONDITIONS PASS`

## Technical summary

PN8 asked whether the frozen PN7C ARA models could transfer far beyond their development range without seeing the target primes. Five boundaries were fixed in advance: `10^50`, `10^100`, `10^150`, `10^200`, and `10^250`. For each boundary, only the four greatest primes below it were calculated. The prediction packet was then hashed before the public values above the boundaries were retrieved from OEIS A033873/A003617.

The strongest frozen ARA model, ARA-M2, achieved a mean target-bin log loss of **4.076804 bits**, better than ARA-M1 (**4.643778**), ARA-IID (**4.487415**), and a uniform 24-bin forecast (**4.584963**). It assigned more probability to the revealed target than ARA-M1 in **4 of 5** cases. However, it put only **1 of 5** revealed targets in its top-three bins and none in its top bin. The registered top-three sharpness requirement was at least 2 of 5, so the overall pilot gate failed.

The honest result is therefore mixed but useful: the two-step ARA context transferred probabilistic information to 50–250 digit boundaries, yet it did not concentrate that information sharply enough to be called an effective prime-location method. This is evidence for scale transfer of a weak relational signal, not a demonstration of exact prime prediction.

## Key findings

| Model | Mean log loss (bits; lower is better) | Top-1 hits | Top-3 hits | Interpretation |
|---|---:|---:|---:|---|
| ARA-M2 | **4.076804** | 0/5 | 1/5 | Best probability score; broad rather than sharp |
| ARA-IID | 4.487415 | 1/5 | 1/5 | Unconditional ARA-state distribution |
| Uniform, 24 bins | 4.584963 | — | — | Reference probability forecast |
| ARA-M1 | 4.643778 | 1/5 | 1/5 | Current ARA state only |
| RawGap-M1 | Infinite | 0/5 | 0/5 | Diagnostic support failure at `10^250`; not a fair claimed victory |

ARA-M2 improved mean log loss over ARA-M1 by **0.566974 bits per target** and over ARA-IID by **0.410611 bits per target**. The improvement is meaningful as a probability comparison, but five cases are far too few to estimate a stable effect size.

| Boundary | Public offset above `10^n` | Crossing gap | Revealed ARA bin | ARA-M2 rank | ARA-M2 log loss | Top-3 hit |
|---:|---:|---:|---:|---:|---:|:---:|
| `10^50` | 151 | 208 | 16 | 8 | 4.247109 | No |
| `10^100` | 267 | 1,064 | 21 | 2 | 3.104690 | **Yes** |
| `10^150` | 67 | 340 | 12 | 8 | 4.260765 | No |
| `10^200` | 357 | 546 | 21 | 5 | 3.925999 | No |
| `10^250` | 1,227 | 1,260 | 15 | 16 | 4.845457 | No |

No separate chart is used in this repository report because five exact cases are clearer in a table and a large visual could overstate the sample. The companion interactive report contains one compact model-comparison chart for accessibility.

## Scope, data, and definitions

The target for each boundary was the first prime strictly greater than `10^n`. Let `g_-` be the final fully known prime gap below the boundary and `g_+` be the crossing gap from the greatest prime below the boundary to the first prime above it. The revealed state was

\[
x=\frac{2g_+}{g_-+g_+},\qquad 0<x<2,
\]

then assigned to one of 24 equal ARA bins. ARA-M1 conditions on the latest known ARA state. ARA-M2 conditions on the previous and latest ARA states, retaining one additional arrival relation. ARA-IID retains only the overall frozen ARA-state distribution. RawGap-M1 predicts an exact next gap from the current exact gap and is projected onto the same 24-bin coordinate.

This pilot predicted **ranges of relational ARA state**, not exact decimal prime values. An exact prime generator would additionally need a justified within-bin location rule.

Public reveal data came from OEIS A033873, the offset between `10^n` and the first prime above it, cross-referenced to OEIS A003617. The exact rows used were `50 151`, `100 267`, `150 67`, `200 357`, and `250 1227`.

## Methodology and reveal barrier

1. The protocol, exponents, models, bins, and pass criteria were frozen before reveal.
2. Four consecutive primes immediately below each boundary were generated with a below-only script. No search crossed a boundary.
3. ARA-IID, ARA-M1, ARA-M2, and RawGap-M1 distributions were generated from the already-frozen PN7C model.
4. The full prediction packet was serialized and SHA-256 hashed: `AA26297D54D1BB52203A9A77B1F981977D893C6630D739C521E906459391A7BA`.
5. Only then were the five OEIS rows retrieved and stored in a separate reveal packet.
6. A scorer evaluated the frozen distributions without refitting. An independent implementation recomputed the distributions, targets, losses, ranks, aggregates, and registered conditions.

Registered primary conditions:

| Condition | Requirement | Result |
|---|---|---|
| Q1 | ARA-M2 top-three contains at least 2/5 targets | **Fail: 1/5** |
| Q2 | ARA-M2 mean log loss below ARA-M1 | **Pass** |
| Q3 | ARA-M2 mean log loss below ARA-IID | **Pass** |
| Q4 | ARA-M2 gives the target more probability than ARA-M1 in at least 3/5 cases | **Pass: 4/5** |

Because Q1–Q4 were jointly required, PN8 is **not** registered as promising enough to scale under its own pilot gate.

## Validation and robustness

- The independent numerical validator passed **164/164** checks.
- The boundary validator passed **50/50** checks: all four pre-boundary primes and the revealed post-boundary prime passed 96-round probable-prime checks, the reported primes were consecutive over the scanned intervals, and the post-boundary value was the first passing integer found above the boundary.
- The executed notebook completed **4/4** code cells without error.
- The protocol, input, prediction, reveal, scorer, result, and validation files are separately preserved and hashable.

These checks protect arithmetic integrity and reveal order. They do not turn probable-prime tests into formal primality certificates, and they do not overcome the small sample.

## Limitations

1. **Five targets do not measure effectiveness.** Extremely large integers test whether a representation transfers across scale; statistical effectiveness requires many untouched targets.
2. **The top-three result is weak.** Better average log loss means the probability distribution improved, but 1/5 top-three and 0/5 top-one show that it remained diffuse.
3. **RawGap-M1 has a support defect at this scale.** Its frozen exact-gap alphabet assigned zero probability to the `10^250` outcome. This makes its mean loss infinite and prevents a fair extrapolation comparison. Q5 remains diagnostic only.
4. **Targets share one construction.** All are powers of ten. This makes the test reproducible but does not establish transfer to arbitrary numerical landmarks.
5. **No exact-prime claim was tested.** The target was a 24-bin relation between consecutive gaps, not the exact offset or exact prime.
6. **The slow adult-wave hypothesis was not isolated.** PN8 tested local child-state transfer at distant scales. Five isolated boundary snapshots cannot establish a larger wave across many primes.

## Recommended next steps

The next test should become **wider, not merely larger**:

1. Pre-register at least 100 untouched boundaries using a deterministic rule fixed before reveal.
2. Preserve ARA-M2 unchanged for the primary replication so PN8 is not retrofitted.
3. Replace the RawGap diagnostic with a scale-capable baseline fixed before targets are opened—for example a gap model normalized by `log N`, plus an established prime-gap probability baseline.
4. Score full probability distributions with log loss and calibration, while retaining top-three as a sharpness check.
5. If exact prime location is the goal, add and separately validate a within-bin offset model. Do not infer an exact value from the ARA bin alone.
6. Test the proposed slow adult coordinate in a separate registered sequence-level experiment rather than adding it post hoc to PN8.

## Further questions

- Does ARA-M2 retain its log-loss advantage over 100+ untouched targets?
- Is the gain calibrated, or does it come from a small number of fortunate high-probability cases?
- Does a scale-normalized raw-gap or Hardy–Littlewood-informed baseline remove the apparent advantage?
- Can a separately frozen adult-scale coordinate improve top-three concentration without harming calibration?
- What additional coordinate is required to move from relational-bin prediction to exact offset prediction?

## Allowed concise claim

> Across five pre-hashed powers of ten, frozen ARA-M2 reduced mean target-bin log loss relative to ARA-M1, ARA-IID, and a uniform 24-bin forecast, and assigned higher target probability than ARA-M1 in four cases. It achieved only one top-three hit, failed the registered sharpness gate, and therefore demonstrates transferable probabilistic context rather than effective or exact prime prediction.

