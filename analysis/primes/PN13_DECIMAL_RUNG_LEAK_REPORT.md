# PN13 decimal-rung leak law

**Date:** 21 July 2026  
**Orientation:** up = multiply the declared scale coordinate by ten; preserve sign/direction  
**Arm A verdict:** `NOT SUPPORTED [PRE-REGISTERED FRESH TARGETS]` — fixed-window prime-ladder vector  
**Arm B verdict:** `NOT SUPPORTED [PRE-REGISTERED FRESH TARGET]` — signed child coupling  
**Fixed-Pi sequence:** `NOT SUPPORTED`  
**Geometry verdict:** `AMPLITUDE RULE FAILED; AN ALMOST-DECIMAL JOINT-CLOSURE WAVELENGTH WAS EXPOSED POST-HOC`  
**Independent algorithmic validation:** `19/19` checks pass

## Answer first

We tested the literal reading that climbing one declared decimal rung gives the **same signed leftover** one additional
leading zero:

\[
\underbrace{L_{k+1}}_{\substack{\text{same residual}\\\text{one rung up}}}
=
\underbrace{\frac{L_k}{10}}_{\substack{\text{same direction}\\\text{one-tenth magnitude}}}.
\]

That rule did not survive either frozen reading.

- PN12's circular remainder did not shrink `0.014 -> 0.0014 -> 0.00014`; it measured
  `0.01419 -> 0.01513 -> 0.00338`, while its direction rotated by `85.65 degrees` and then `40.80 degrees`.
- PN10B's signed child coupling did not shrink with a stable sign; it measured
  `+0.00886 -> -0.01408 -> +0.16884`.
- The fixed sequence `-(pi-3)`, `-(pi-3)/10`, `-(pi-3)/100` failed at the lower and upper rungs. Only the already
  noticed middle value was close.

The test nevertheless exposed a cleaner neighboring relation. The **wavelength required for two adjacent gate
children to close together**, rather than the residual amplitude, grows almost one decimal digit per number-scale
rung. For the unchanged PN10B paid gates, the median exact joint-repeat lengths were

\[
5.4096\times10^7
\longrightarrow
4.3660\times10^8
\longrightarrow
3.4773\times10^9,
\]

or factors `8.07` and `7.96`. The definition itself explains this:

\[
\underbrace{q,r}_{\substack{\text{two adjacent child gates}\\\text{near }n^{0.45}}}
\quad\Longrightarrow\quad
\underbrace{T_{qr}=\operatorname{lcm}(q,r)=qr}_{\substack{\text{exact joint}\\\text{closure length}}}
\sim
\underbrace{n^{0.90}}_{\text{two }0.45\text{ exponents}},
\]

so one decimal number rung predicts a wavelength factor

\[
10^{0.90}=7.9433.
\]

Plainly: the extra digit was not found in **how strong the leftover is**. A close relative of it appears in **how
long the combined child cycle becomes**. This was identified after the registered amplitude result and is therefore
a new post-hoc hypothesis, not a successful PN13 prediction.

## 1. What was frozen

The user prior was:

> “Is it just an extra digit for each rung?”

After the proposed rung-versus-sample-size discriminator was explained:

> “Yes, can we test that. It might be the rule we have been hunting.”

Two appearances were frozen separately.

### Arm A — ladder height with aggregation held fixed

PN12's natural next-child phase remained unchanged:

\[
B_m=\prod_{j=1}^m p_j,
\qquad
u_m=\frac{B_m\bmod p_{m+1}}{p_{m+1}},
\qquad
\delta_m=(u_{m+1}-u_m)\bmod1.
\]

Every window contained exactly 4,000 steps. Therefore a smaller vector at a higher rung could not be explained by
averaging more observations.

\[
V_M=\frac1{4000}\sum_{m=M}^{M+3999}e^{2\pi i\delta_m}.
\]

The open anchor began at `M=1,000`; untouched targets began at `10,000` and `100,000`. The exploratory timing window
`50,000..53,999`, accidentally exposed before the formal freeze, was excluded.

### Arm B — raw-number scale with the child instrument held fixed

For prime node `n`, the nine largest prime gates below `n^0.45` supplied

\[
A_j(n)=2\frac{n\bmod q_j}{q_j},
\qquad
C(n)=\frac18\sum_{j=1}^{8}(A_j-1)(A_{j+1}-1).
\]

Every interval contained exactly one million raw integers. The scale starts were `4*10^8`, the already-open PN10B
anchor `4*10^9`, and untouched target `4*10^10`.

The protocol, code and target ranges were hashed before the PN13 development and targets were calculated.

## 2. Arm A result — the circular residual did not gain zeros

| Ladder-window start | Steps | `R=|V|` | Direction |
|---:|---:|---:|---:|
| `1,000` | 4,000 | `0.01418625` | `16.1347 degrees` |
| `10,000` | 4,000 | `0.01512678` | `101.7855 degrees` |
| `100,000` | 4,000 | `0.00338267` | `60.9901 degrees` |

The registered magnitude ratios were

\[
\frac{R_{10,000}}{R_{1,000}}=1.0663,
\qquad
\frac{R_{100,000}}{R_{10,000}}=0.2236,
\]

not `0.1` and `0.1`. Direction shifted by `85.65 degrees` and `40.80 degrees`, rather than staying within the frozen
`9-degree` tolerance. All four Arm A conditions failed.

The fixed-`N` uniform-circle control had mean `R=0.014071`, analytic expectation `0.014012`, 5th percentile
`0.003647` and 95th percentile `0.027620`. The first two windows look ordinary at that cancellation scale. The third
is a low-tail cancellation value, but it does not follow the registered decimal sequence or direction.

| Rival vector law | Sum of complex absolute errors on both targets |
|---|---:|
| `1/sqrt(10)` per rung | `0.0180274` |
| factor ten | `0.0183693` |
| zero | `0.0185094` |
| constant | `0.0319653` |

The rivals are close because the vectors are small and directionally unstable. Factor ten was not best.

**Arm A verdict: `NOT SUPPORTED`.**

## 3. Arm B result — the signed coupling flipped and then became strongly positive

| Scale | Raw interval start | Prime nodes | Prime mean coupling | Late-composite mean |
|---:|---:|---:|---:|---:|
| 8 | `400,000,000` | 50,426 | `+0.00885623` | `+0.00686993` |
| 9 | `4,000,000,000` | 45,166 | `-0.01407585` | `-0.01514929` |
| 10 | `40,000,000,000` | 41,056 | `+0.16883770` | `+0.16668711` |

The adjacent ratios were

\[
\frac{C_9}{C_8}=-1.5894,
\qquad
\frac{C_{10}}{C_9}=-11.9948.
\]

The fresh-target ratio's 95% 100-block bootstrap interval was `[-32.377,-7.204]`, nowhere near the registered
positive interval `[0.05,0.15]`. Every primary check failed: sign stability, both point ratios, target uncertainty and
rival comparison.

The target prediction from the factor-ten rule was `-0.00140758`; the observation was `+0.16883770`. Among the
frozen target rivals, zero was marginally closest, followed by factor ten, `1/sqrt(10)` and constant. None describes
the large positive local coupling particularly well.

The node distributions show that the means are not produced by one outlier:

| Scale | 5th percentile | Median | 95th percentile |
|---:|---:|---:|---:|
| 8 | `-0.13791` | `-0.00008` | `+0.18618` |
| 9 | `-0.18027` | `+0.01177` | `+0.16000` |
| 10 | `-0.03259` | `+0.16148` | `+0.45355` |

**Arm B verdict: `NOT SUPPORTED`.**

## 4. Fixed Pi sequence

| Scale | Fixed prediction | Observed prime mean | Relative error |
|---:|---:|---:|---:|
| 8 | `-0.14159265` | `+0.00885623` | `106.25%` |
| 9 | `-0.01415927` | `-0.01407585` | `0.589%` |
| 10 | `-0.00141593` | `+0.16883770` | `12,024%` |

The middle value is genuinely close, but the frozen neighboring rungs fail in sign and magnitude. That makes the
middle resemblance a local numerical correspondence in this observable, not a demonstrated Pi-leak ladder.

**Fixed-Pi verdict: `NOT SUPPORTED`.**

## 5. Post-hoc geometry — the slow adult modular wave

The surprisingly large scale-10 coupling was independently reproduced, then the unchanged instrument was run over
ten consecutive one-million-integer windows at every scale. This diagnostic does not alter PN13's verdict.

| Scale | Mean of 10 prime-window means | Window SD | Range | Positive / negative windows | Prime–composite correlation |
|---:|---:|---:|---:|---:|---:|
| 8 | `+0.00617` | `0.04011` | `-0.05136..+0.05711` | `6 / 4` | `0.99981` |
| 9 | `-0.02565` | `0.01442` | `-0.04765..-0.00762` | `0 / 10` | `0.99705` |
| 10 | `+0.20803` | `0.01339` | `+0.16884..+0.21507` | `10 / 0` | `0.99922` |

Primes and surviving composites share almost the same motion. The signal therefore belongs to the modular child-gate
geometry, not uniquely to prime identity.

For two adjacent prime gates `q` and `r`, their individual residue cycles have periods `q` and `r`. Because distinct
primes are coprime, their exact joint repeat is

\[
T_{qr}=\operatorname{lcm}(q,r)=qr.
\]

Their unwrapped relative phase changes by one turn on the approximate scale

\[
T_{\rm drift}=\frac{qr}{|q-r|},
\]

although exact discrete closure remains `qr`. At the three tested paid-gate scales:

| Scale | Median exact joint repeat `qr` | Median relative-phase one-turn scale | One-million window / drift scale |
|---:|---:|---:|---:|
| 8 | `54,096,009` | `4,367,582` | `22.90%` |
| 9 | `436,601,021` | `54,622,205` | `1.83%` |
| 10 | `3,477,342,957` | `290,024,340` | `0.345%` |

This explains the scale-10 persistence. A one-million window covers a substantial fraction of the lower-scale
relative drift but only a tiny slice of the upper-scale drift. It therefore sees a sustained local orientation rather
than averaging the two children over their complete relation.

### Where the almost-extra-digit law lives

PN10B chose gates near `n^0.45`. Consequently

\[
q\sim n^{0.45},\quad r\sim n^{0.45}
\quad\Longrightarrow\quad
qr\sim n^{0.90}.
\]

Increasing `n` by ten should therefore multiply the joint wavelength by `10^0.9=7.9433`. The observed exact-repeat
ratios, `8.07` and `7.96`, follow that algebra closely.

At the complete factor boundary, gates lie near `sqrt(n)=n^0.5`. There the analogous exact joint period obeys

\[
q r\sim n^{0.5}n^{0.5}=n,
\]

so one decimal rung in `n` produces approximately one full additional digit in joint closure length. This is a
mathematical consequence of two child periods near the square-root boundary, with local prime gaps affecting the
shorter drift envelope.

This is close to Dylan's geometric expectation: the two child waves create a larger, slower parent relation. It is
not yet evidence that the same wavelength law is universal outside this modular construction, and it is not a Pi
amplitude leak.

### Dylan correction — TE-ARA is always 2; the partition varies

Dylan identified the joint closure as the concrete structure intended by a full ARA/TE-ARA account:

> “This is where ARA 2.0 or a TEARA being 2 is from. The whole of two half waves at 1.0.”

Codex initially mistranslated this as requiring two equal `1.0` child allocations. Dylan corrected the canonical
rule: TE-ARA is the same ARA geometry viewed as total allocation. The pure identity is Phase A + Phase B = `2`.
In a real observed account, environmental couplings and unresolved Other can occupy part of that fixed total without
becoming extra pure poles. For example,

\[
\underbrace{t_A}_{0.25}
+
\underbrace{t_B}_{1.25}
+
\underbrace{t_{Other}}_{0.50}
=
\underbrace{\mathrm{TE\!-\!ARA}(I)}_{2.00}.
\]

The symmetric pure ridge `1+1=2` is allowed but is not the definition. The displayed `0.50 Other` is contextual
coupling, not part of the pure identity. The period equation uses
multiplication, `q*r~sqrt(n)*sqrt(n)~n`; TE-ARA uses a fixed normalised allocation ledger whose entries sum to `2`.
They are corresponding closure projections, not interchangeable units. The prime calculation does not measure
physical energy, but it gives an exact example of two half-scale child cycles closing one parent cycle while the
parent identity retains its invariant TE-ARA total.

If an `Other=0.50` parent allocation is opened as its own identity, its own internal TE-ARA ledger is renormalised to
`2`. The `0.50` is its edge weight inside the parent, not its internal identity total.

## 6. What changed and what did not

### Registered conclusions

- A residual-amplitude `/10` operator is not supported in either tested prime appearance.
- PN12's `0.01419` remains explained by fixed-`N` circular cancellation rather than a stable thruster.
- PN10B's `-0.01408` does not continue as a Pi-derived decimal sequence.

### New descriptive result

- Adjacent residue children contain a directly calculable slow joint wave.
- Its exact closure wavelength grows approximately as the square of the selected gate scale.
- With PN10B's `n^0.45` gates this is `n^0.9`; with full square-root gates it is approximately `n`.
- Fixed raw windows flatten different fractions of that wave at different rungs and are therefore not phase-comparable.

### Framework implication

The test does not support “one more zero in leak strength.” It does support a more precise route for the earlier
missing-adult-wave intuition: infer the parent wavelength from the two child periods and compare systems at equal
**relational phase coverage**, not equal raw window width.

## 7. Recommended next test

Freeze the wavelength reading before opening a new range:

\[
\underbrace{\theta_{q,r}(n)}_{\substack{\text{position on the}\\\text{child-pair adult wave}}}
=
\left(
\underbrace{n}_{\text{raw position}}
\underbrace{\frac{r-q}{qr}}_{\substack{\text{relative child}\\\text{phase advance}}}
\right)\bmod1.
\]

Then:

1. measure the signed child product against `theta` at several untouched scales;
2. predict that the curves collapse when expressed on the same `0–2` phase coordinate;
3. compare adjacent gates with distant-pair and shuffled-gate controls;
4. test paid `n^0.45` gates and full `sqrt(n)` boundary gates separately;
5. keep prime and late-composite populations visible.

That would test the newly located slow adult wave without claiming the failed amplitude rule succeeded.

## 8. Reproduction

- fidelity packet: `analysis/primes/PN13_DECIMAL_RUNG_LEAK_FIDELITY_PACKET_v1.md`
- frozen protocol: `analysis/primes/PN13_DECIMAL_RUNG_LEAK_PROTOCOL_v1_FROZEN.md`
- target freeze: `analysis/primes/PN13_TARGET_FREEZE_MANIFEST.json`
- primary script: `analysis/primes/pn13_decimal_rung_leak.py`
- development: `analysis/primes/PN13_DEVELOPMENT_RESULTS.json`
- target: `analysis/primes/PN13_TARGET_RESULTS.json`
- compact table: `analysis/primes/PN13_DECIMAL_RUNG_SUMMARY.csv`
- independent validator: `analysis/primes/validate_pn13_decimal_rung_leak.py`
- validation: `analysis/primes/PN13_DECIMAL_RUNG_VALIDATION.json`
- post-hoc diagnostic: `analysis/primes/pn13_posthoc_window_phase_diagnostic.py`
- post-hoc results: `analysis/primes/PN13_POSTHOC_WINDOW_PHASE_RESULTS.json`
- post-hoc windows: `analysis/primes/PN13_POSTHOC_WINDOW_PHASE_WINDOWS.csv`
