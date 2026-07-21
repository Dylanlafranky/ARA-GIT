# ARA Prime Resonance Families and Information Locks

**Date:** 21 July 2026  
**Tier:** `POST-HOC EXACT ARITHMETIC / ARA GEOMETRY CROSSWALK / ASSIGNED SONIFICATION`  
**Prediction status:** `NOT A PRIME-PREDICTION RESULT`  
**Validation:** `18/18 EXACT CHECKS PASS`

## Purpose

This note preserves the numerical structures exposed after the prime square-ridge lab was turned into a music-box
instrument. It keeps four layers separate:

1. **exact arithmetic** — factorisations, products, divisor counts and logarithmic closure;
2. **instrument definition** — which children are visible and how events are classified;
3. **assigned sonification** — fixed musical labels used to hear the child inventory;
4. **ARA interpretation** — ridge, recurrence, reflected pair and hierarchical-lock language.

The exact arithmetic does not depend on ARA. The ARA reading is a proposed relational organisation of that arithmetic.
The musical pitches are labels chosen by the instrument and are not evidence that primes possess an intrinsic C-major
scale.

## 1. Instrument definitions

For an integer node `n`, the instrument exposes the active distinct prime children

\[
H(n)=\{p\text{ prime}:p^2\le n\text{ and }p\mid n\}.
\]

The square condition matters. It says that child `p` has crossed its independent-responsibility boundary in the
incremental sieve. Multiples of `p` exist below `p^2`; they have already been removed by smaller children.

Define the distinct-child base

\[
b(n)=\prod_{p\in H(n)}p.
\]

The lab then uses these operational classes:

- **quiet node:** `H(n)` is empty;
- **ordinary collision:** one or more active children strike without satisfying a later resonance class;
- **fundamental full resonance:** at least three children are active and `b(n)=n`;
- **harmonic resonance repeat:** at least three children are active, `b(n)<n`, and `b(n)` divides `n`;
- **primorial rung:** a fundamental full resonance whose child set contains consecutive primes beginning with 2.

On the PN10 factor diameter, a divisor `d` has coordinate

\[
x_n(d)=\frac{2\log d}{\log n}.
\]

Therefore `1` is at `0`, `sqrt(n)` is at the `1.0` ridge, and `n` is at `2`. Reflected factors close exactly:

\[
x_n(d)+x_n(n/d)=2.
\]

### Assigned child notes

The active prime lanes are assigned consecutive notes of an ascending C-major scale:

| Prime child | Note | Prime child | Note | Prime child | Note |
|---:|:---:|---:|:---:|---:|:---:|
| 2 | C4 | 11 | G4 | 23 | D5 |
| 3 | D4 | 13 | A4 | 29 | E5 |
| 5 | E4 | 17 | B4 | 31 | F5 |
| 7 | F4 | 19 | C5 | 37 | G5 |

The assignment continues in the same scale order through child `67 -> G6`. A composite event sounds its active
children from low to high; a quiet prime is a rest. The audible timing and chord membership are arithmetic. The pitch
choice and perceived musical pleasantness are not.

## 2. Collision-order ladder and population

The first node at which each visible collision count occurs is:

| Active voices | First node | Exact reason |
|---:|---:|---|
| 0 | 2 | first quiet prime node |
| 1 | 4 | `2^2` activates child 2 |
| 2 | 12 | children 2 and 3 are active |
| 3 | 30 | `2*3*5` |
| 4 | 210 | `2*3*5*7` |
| 5 | 2,310 | `2*3*5*7*11` |

Through node 5,000, the voice-count population is:

| Voices | Number of nodes |
|---:|---:|
| 0 | 669 |
| 1 | 1,964 |
| 2 | 1,270 |
| 3 | 808 |
| 4 | 281 |
| 5 | 7 |

**Plain-language ARA reading:** each additional simultaneous child requires a rarer shared multiple. The audible
texture therefore thins as the instrument moves from single collisions to larger collective closures. This is the
ordinary multiplication of distinct prime periods, presented as a rung ladder.

## 3. The 510 resonance family

The first four-child fundamental closure used in the lab is

\[
510=2\times3\times5\times17.
\]

Its active notes are `C4-D4-E4-B4`. Because the four children are distinct and their product is the whole node,

\[
\sum_{p\in\{2,3,5,17\}}x_{510}(p)
=\frac{2\log(2\cdot3\cdot5\cdot17)}{\log510}=2.
\]

The same child inventory returns at `1,020`, `1,530`, `2,040`, `2,550`, `3,060`, `4,080`, and `4,590`. These are
harmonic repeats in the instrument. At `3,570`, child 7 joins the set:

\[
3570=2\times3\times5\times7\times17,
\]

so the event becomes a new five-child fundamental closure with notes `C4-D4-E4-F4-B4`.

**Plain-language ARA reading:** 510 is not a square ridge. No single child sits at `1.0`. It is a collective ridge:
four child periods return together, and their decompressed factor positions exhaust the full `0-2` parent diameter.
Later multiples repeat the same lock until another independently visible child changes the identity.

## 4. Screen-resolution crosswalk

The observation that several familiar display dimensions resemble resonance numbers has two exact arithmetic parts.

### 4.1 Exact 30 and 210 repeat families

Many common dimensions are exact multiples of the three-child closure `30=2*3*5`:

\[
\begin{aligned}
720&=30\times24, &1080&=30\times36, &1440&=30\times48,\\
1920&=30\times64, &2160&=30\times72, &2880&=30\times96,\\
3840&=30\times128, &4320&=30\times144, &7680&=30\times256.
\end{aligned}
\]

There is also a familiar four-child example:

\[
1680=210\times8,
\qquad 210=2\times3\times5\times7.
\]

This is consistent with the engineering usefulness of dimensions that divide cleanly into many smaller integer
blocks. It is not an independent ARA prediction.

### 4.2 The 510 family beside the binary ladder

Because `510=512-2`, its multiples sit beside corresponding multiples of 512:

| Resonance multiple | Binary-ladder neighbour | Difference |
|---:|---:|---:|
| 1,020 | 1,024 | 4 |
| 1,530 | 1,536 | 6 |
| 2,040 | 2,048 | 8 |
| 2,550 | 2,560 | 10 |
| 3,060 | 3,072 | 12 |
| 3,570 | 3,584 | 14 |
| 4,080 | 4,096 | 16 |

In general,

\[
510k=512k-2k.
\]

**Plain-language ARA reading:** the picture resembles two nearby ladders, one highly composite and one binary. But
the nearness is completely explained by `510=512-2`; it should be recorded as an arithmetic crosswalk, not evidence
that screen engineers unknowingly selected an ARA constant.

Standards context: [CTA-861 timing calculator](https://www.cta.tech/cta-861-ovt-calculator/) and
[VESA DisplayPort resolution overview](https://vesa.org/displayport-developer/why-displayport/).

## 5. The complementary pair 714-715

Two consecutive nodes are both fundamental closures:

\[
714=2\times3\times7\times17,
\qquad
715=5\times11\times13.
\]

Their child sets are disjoint and together contain the first seven primes:

\[
\{2,3,7,17\}\cup\{5,11,13\}
=\{2,3,5,7,11,13,17\}.
\]

Under the assigned sonification, the two nodes partition the first C-major octave exactly once:

- `714 -> C4-D4-F4-B4`;
- `715 -> E4-G4-A4`.

They are also a known Ruth-Aaron pair because the sums of their distinct prime factors agree:

\[
2+3+7+17=5+11+13=29.
\]

Their product closes the first-seven-prime parent:

\[
714\times715
=510510
=2\times3\times5\times7\times11\times13\times17
=17\#.
\]

Since `714` and `715` are the two adjacent integers around `sqrt(510510)=714.499825...`, their parent positions are

\[
x_{510510}(714)=0.9998935126888657,
\qquad
x_{510510}(715)=1.0001064873111343,
\]

and their sum is exactly `2`.

**Plain-language ARA reading:** this is an unusually clean binary closure. Two different fundamental child
identities sit on opposite sides of the parent ridge, divide its first-seven-prime inventory between them without
overlap, and multiply back into the complete parent. The exact arithmetic is established; identifying it as an ARA
complementary resonance pair is the framework crosswalk.

Research context: [The Ruth-Aaron Pair Problem](https://math.colgate.edu/~integers/s72/s72.pdf).

## 6. The harmonic-repeat triple 1274-1276

Three consecutive nodes have the same exponent shape:

\[
\begin{aligned}
1274&=2\times7^2\times13,\\
1275&=3\times5^2\times17,\\
1276&=2^2\times11\times29.
\end{aligned}
\]

Each has three distinct prime children but four prime factors when multiplicity is retained. Each therefore has the
form `p^2*q*r` and exactly

\[
(2+1)(1+1)(1+1)=12
\]

positive divisors. Exhaustive checking shows that 1,274 is the first starting point of three consecutive integers
that all have exactly 12 divisors.

The current lab uses distinct active children, so it labels all three as harmonic repeats. The part flattened by
that view is the repeated child:

| Node | Distinct notes | Repeated child | Multiplicity echo `n/rad(n)` |
|---:|---|---:|---:|
| 1,274 | C4-F4-A4 | 7 / F4 | 7 |
| 1,275 | D4-E4-B4 | 5 / E4 | 5 |
| 1,276 | C4-G4-E5 | 2 / C4 | 2 |

Here `rad(n)` is the product of the distinct prime factors. The exact reconstruction is

\[
n=\operatorname{rad}(n)\frac{n}{\operatorname{rad}(n)}.
\]

The same missing content is visible on the factor diameter:

| Node | Sum of distinct-child positions | Repeated-child echo | Total |
|---:|---:|---:|---:|
| 1,274 | 1.455683138 | 0.544316862 | 2.000000000 |
| 1,275 | 1.549851739 | 0.450148261 | 2.000000000 |
| 1,276 | 1.806152950 | 0.193847050 | 2.000000000 |

**Plain-language ARA reading:** these nodes do not introduce three new child identities at every strike. Each repeats
one child inside a three-child base. The current music box tells us *which distinct lanes are present* but suppresses
how many times a lane participates. A future instrument can preserve that information by striking the repeated note
twice or giving it greater weight. That would be an instrument improvement, not a new theorem.

Number-theory context: [OEIS A182683, numbers of form p^2*q*r and hence 12 divisors](https://oeis.org/A182683).

## 7. The 1885-1887 three-by-three lock

The next observed triple has a different structure:

\[
\begin{aligned}
1885&=5\times13\times29,\\
1886&=2\times23\times41,\\
1887&=3\times17\times37.
\end{aligned}
\]

Each node is squarefree, contains three independently active children, and is a fundamental full resonance under the
lab definition. Across the three parents, all nine children are different:

\[
\{2,3,5,13,17,23,29,37,41\}.
\]

Their assigned notes are:

- `1885 -> E4-A4-E5`;
- `1886 -> C4-D5-A5`;
- `1887 -> D4-B4-G5`.

The three parents form a larger parent whose factorisation retains all nine child lanes:

\[
N=1885\times1886\times1887=6,708,492,570
=\prod_{p\in\{2,3,5,13,17,23,29,37,41\}}p.
\]

Because the middle integer is `m=1886`, the same closure is

\[
N=(m-1)m(m+1)=m^3-m.
\]

Their positions on the new parent diameter are

\[
\begin{aligned}
x_N(1885)&=0.6666197954037039,\\
x_N(1886)&=0.6666666749500042,\\
x_N(1887)&=0.6667135296462919,
\end{aligned}
\]

and the three positions sum exactly to `2`. Each parent therefore contributes almost `2/3` of the parent diameter.
Any one parent can also be compared with the product of the other two, producing a reflected factor pair near
`2/3 <-> 4/3`.

Within the lab range through 5,000, 1,885 is the only starting point at which three consecutive nodes are all
fundamental three-child resonances under the exact `p^2<=n` activation rule.

**Plain-language ARA reading:** this is the clearest current arithmetic example of the proposed Information^3 idea.
Three child factors close each local identity; three neighbouring identities then multiply into a parent containing
nine separate children. It is a literal `3 x 3` hierarchy in the factor web. The product formula is automatic after
factorisation; the interesting post-hoc observation is that the three consecutive, pairwise-coprime, squarefree
nodes supply the complete grouping without repeating a child.

## 8. Comparison of the three structures

| Structure | Local identities | Parent closure | ARA location | What is distinctive |
|---|---|---|---|---|
| 510 family | one four-child base | repeated by integer multiples | child positions sum to 2 | separates fundamental closure from harmonic recurrence |
| 714-715 | two complementary parents | `714*715=17#` | approximately `1 <-> 1` | disjoint partition of first seven primes; Ruth-Aaron balance |
| 1274-1276 | three repeated-child parents | each closes only after restoring multiplicity | distinct sum plus echo = 2 | three consecutive `p^2*q*r` nodes; exposes flattened multiplicity |
| 1885-1887 | three three-child parents | one nine-child product | approximately `2/3+2/3+2/3=2` | consecutive squarefree `3 x 3` hierarchy |

The structures must not be collapsed into one claim. The 714 pair is a binary reflected closure, the 1274 triple is
a multiplicity pattern, and the 1885 triple is a squarefree three-parent lock.

## 9. Geometry verdict and scientific verdict

### Geometry verdict

The music-box decompression exposed several exact nested relations that a simple prime/composite label hides:

- independent child activation at `p^2`;
- simultaneous child membership at composite nodes;
- full distinct-child closure versus later recurrence;
- multiplicity echoes flattened by a distinct-child-only representation;
- complementary two-parent and three-parent product closures;
- exact `0-2` logarithmic factor closure at both child and parent levels.

This supports the usefulness of ARA as a relational accounting language for the sieve and factor web.

### Claim and benchmark verdict

These are post-hoc arithmetic decompositions. They do **not** yet:

- predict a previously unknown prime;
- beat trial division, an incremental sieve, or established prime-counting methods;
- establish that the notes carry intrinsic physical significance;
- demonstrate a universal physical resonance constant;
- independently prove that the universe is fractal.

A stronger next step would freeze a feature derived from one of these structures—especially multiplicity or
parent-lock geometry—then test it on an unopened range against baselines using the same factor information.

## 10. Reproduction files

- Interactive instrument: `analysis/primes/ARA_PRIME_SQUARE_RIDGE_LAB.html`
- Instrument guide: `analysis/primes/ARA_PRIME_SQUARE_RIDGE_LAB_README.md`
- Instrument validator: `analysis/primes/validate_ara_prime_square_ridge_lab.py`
- Instrument validation: `analysis/primes/ARA_PRIME_SQUARE_RIDGE_LAB_VALIDATION.json`
- This note's exact validator: `analysis/primes/validate_prime_resonance_locks.py`
- This note's validation output: `analysis/primes/ARA_PRIME_RESONANCE_LOCKS_VALIDATION.json`
- Earlier 510 note: `FableConvo/NOTE_PRIME_510_RESONANCE_RIDGE_2026-07-21.md`

The dedicated validator passes all `18/18` checks, including the first collision-order ladder, voice counts through
5,000, display-number identities, the 714-715 complement, the 1274-1276 multiplicity run, and the 1885-1887
three-by-three closure.
