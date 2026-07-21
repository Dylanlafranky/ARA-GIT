# Note — 510 as an exact discrete resonance-ridge example

**Date:** 21 July 2026  
**Tier:** `EXACT ARITHMETIC STRUCTURE / ARA CROSSWALK / NOT A PHYSICAL-ENERGY RESONANCE CLAIM`  
**Origin:** Dylan noticed that `510` has four simultaneous child collisions and identified it as the resonance ridge
previously discussed in ARA.

## Result in one sentence

`510` is not a prime-square ridge, but it is the **fundamental four-child resonance ridge** of prime periods
`2, 3, 5, 17`: all four modular phases align exactly for the first time, and the four corresponding PN10 factor
positions collectively close the full ARA diameter.

## Exact arithmetic

Let the four prime-child periods be

\[
P=\{2,3,5,17\}.
\]

Their joint recurrence is

\[
\underbrace{L(P)}_{\substack{\text{least shared period}\\
\text{ARA: fundamental resonance node}}}
=
\underbrace{\operatorname{lcm}(2,3,5,17)}_{\text{first exact phase alignment}}
=510.
\]

Because the four periods are distinct primes, the least common multiple is their product:

\[
510=2\times3\times5\times17.
\]

Using the discrete phase of child `p`,

\[
\underbrace{\theta_p(n)}_{\substack{\text{phase of child }p\\
\text{at number-line node }n}}
=
2\pi\frac{n\bmod p}{p},
\]

all four phases are zero at 510:

\[
\theta_2(510)=\theta_3(510)=\theta_5(510)=\theta_{17}(510)=0.
\]

Equivalently, the standard phase-coherence magnitude is maximal:

\[
\underbrace{R(510;P)}_{\substack{\text{collective phase coherence}\\
\text{resonance discriminator}}}
=
\left|\frac14\sum_{p\in P}e^{i\theta_p(510)}\right|
=1.
\]

This is exact modular synchronization. It repeats at `1020`, `1530`, and every `510k`; `510` is the fundamental
joint period and the first shared strike after the `p=17` child becomes independently active at `17²=289`.

## Collective ARA closure

Under the PN10 factor-diameter coordinate

\[
x_n(d)=\frac{2\log d}{\log n},
\]

the four child positions at 510 are

| Child | ARA factor position at 510 | Reflected partner |
|---:|---:|---:|
| `2` | `0.222362` | `1.777638` (`255`) |
| `3` | `0.352435` | `1.647565` (`170`) |
| `5` | `0.516308` | `1.483692` (`102`) |
| `17` | `0.908895` | `1.091105` (`30`) |

No individual child lies at `1.0`, because `510` is not a square. Nevertheless,

\[
\underbrace{x_{510}(2)+x_{510}(3)+x_{510}(5)+x_{510}(17)}_{\substack{\text{four child contributions}\\
\text{collective closure}}}
=
\frac{2\log(2\cdot3\cdot5\cdot17)}{\log510}
=2.
\]

Thus two exact statements coexist:

1. **phase space:** all four child periods align, so coherence is `1`;
2. **factor space:** their combined positions exhaust the full declared diameter, so participation closes at `2`.

This is the discrete arithmetic example of the earlier ARA distinction between a **resonance ridge reading** and
full **TE-ARA closure**: the parent can read as one coherent locked event while the decompressed children remain at
different asymmetric positions.

## Do not merge the two ridge types

| Ridge | Exact condition | Example | Meaning |
|---|---|---|---|
| **Prime-square/factor ridge** | one prime factor is its own reflection: `n=p²` and `x_n(p)=1` | `49=7²` | one child meets itself at the factor midpoint |
| **Collective resonance ridge** | several child phases synchronize: `R(n;P)=1` | `510=lcm(2,3,5,17)` | multiple children complete one shared cycle and act as a coherent parent event |

The number of collisions does not create a square ridge. Conversely, a collective resonance need not place any
individual factor at `x=1`. “Ridge” is therefore incomplete unless its coordinate is named: **factor-position ridge**
or **phase-coherence/resonance ridge**.

## Scientific boundary

The modular synchronization, least-common-multiple recurrence, phase coherence, and logarithmic closure above are
exact arithmetic. Calling the parent appearance an ARA resonance ridge is a framework interpretation of those facts.
It is not evidence that 510 carries physical energy, oscillates in time, or establishes universal fractality.

What the example does add is a clean discriminator that was missing from the prime instrument:

- a square-ridge event is detected by a self-reflected factor;
- a resonance-ridge event is detected by simultaneous child phase closure;
- a multi-child collision can be tested for both rather than inferred from collision count alone.

## Instrument implementation

The interactive lab now implements this distinction directly. It marks square activation, ordinary collision,
fundamental full resonance, harmonic repeat, and the primorial rung as separate states. Its default view is 510, and
the child-wave and factor-diameter panels retain all four voices instead of flattening them into the parent label.

The same rule identifies `1,020` as a repeat of the 510 child set, `3,570` as a new five-child full closure after
child 7 joins, and `4,620` as a five-child repeat whose distinct child product is `2,310`.

The four children at 510 also receive the permanent ascending lane notes `C4`, `D4`, `E4`, and `B4`. The lab sounds
them as a short upward arpeggio, so the audible event preserves rather than replaces the exact child inventory.
Quiet prime nodes remain rests. This is a sonification aid, not a new resonance test.

The independent validator passes `24/24` checks. This operationalizes the crosswalk; it does not promote it beyond
the scientific boundary stated above.
