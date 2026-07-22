# PN33 seeded-hexagon fill and doubling - translation fidelity packet v1 DRAFT

**Claim ID:** PN33/SEEDED-HEXAGON-FILL/v1  
**Created:** 22 July 2026  
**Status:** SIGNED - `EXACT ENOUGH TO TEST`  
**Orientation:** upward means a larger/slower prime-connection rung; within a rung, `0 -> 2` means newly opened capacity -> completely filled capacity.

## F0 - USER PRIOR

> "the NEW hexagon is not FILLED straight away, the prime is just the first connection inside of it. It then has to fill by going up the gradient, and when it fully fills, that is when it doubles again."

Immediately preceding clarification:

> "the size of the hexagon and its total would double each time. Which is why the primes space out more."

## Frozen intended object

- **Identity/system being measured:** one prime-connection generation, treated as an ARA/hexagonal identity envelope. The identity is not one integer and is not one prime.
- **Ordered poles:** newly expanded and mostly empty connection capacity at `0`; completely accumulated connection capacity at `2`.
- **Direction:** later independent prime gates add connection pressure and move the current generation upward along the fill gradient.
- **Scale/rung origin:** completion of the preceding generation. The next prime after that boundary is the first connection/seed of the new generation.
- **Invariant relational claim:** seed, fill, completion and expansion are different events. A prime begins a new connection layer; it does not instantaneously complete that layer. Only accumulated completion causes the next capacity doubling.
- **TE-ARA rule:** each generation is normalized to a local total of `2`. When a generation completes, the *raw* spacing/capacity baseline has doubled, while the new local fill coordinate resets. Normalization does not erase the retained raw scale.

## Permitted decompression

- Independent prime gates may be represented by their exact multiplicative effect on the surviving integer lattice.
- The connection web may be read through primorial/wheel arithmetic, Euler-totient survivor density, local prime gaps and square-root activation boundaries.
- Child, current-generation and adult readings may all be retained, provided they are not averaged into one unnamed scalar.
- A logarithm may be used only to express a multiplicative doubling as equal rung distance; it may not manufacture a periodic wave that is absent from the raw relations.

## Forbidden substitutions and proxies

1. Do not treat `N -> 2N` as an instant completed parent. PN32 already tested that proxy and found it null.
2. Do not treat the seed prime as the filled hexagon.
3. Do not call `q^2` the complete adult structure merely because it is the first independent strike of gate `q`; it is a child-scale landmark unless Dylan explicitly identifies it as the intended completion.
4. Do not define a hexagon as six selected prime labels merely because six items are convenient.
5. Do not define fill using the next-prime outcome that the test later claims to explain.
6. Do not insert Phi, 36 degrees, a Fourier phase, a fitted classifier or a sieve probability as the fill coordinate.
7. Do not claim a new prime generator. This test concerns seed-fill-completion geometry and spacing, not constant-cost primality certification.

## Observable needed

An acceptable instrument must expose all four separately:

1. **seed:** the first independent prime connection after a completed boundary;
2. **fill:** a label-free, monotone accumulation of new connection pressure;
3. **completion:** the first crossing of the predeclared total-capacity boundary;
4. **expansion:** retention of the completed raw scale while a new local `0-2` coordinate begins.

The proposed primary observable is the inverse survivor-density multiplier created by successive independent prime gates. Let

\[
\underbrace{D(p)}_{\substack{\text{raw connection spacing}\\\text{after gates through }p}}
=
\underbrace{\frac{W(p)}{\varphi_E(W(p))}}_{\substack{\text{wheel circumference}\\\text{divided by survivors}}}
=
\prod_{\substack{r\le p\\r\ \mathrm{prime}}}
\frac{r}{r-1},
\qquad
W(p)=\prod_{r\le p}r.
\]

Here `varphi_E` is Euler's totient; it is not the golden ratio.

For a completed baseline gate `b_j`, define the unrounded capacity ratio and local ARA fill by

\[
\underbrace{R_j(p)}_{\text{raw rung growth}}
=\frac{D(p)}{D(b_j)},
\qquad
\underbrace{x_j(p)}_{\text{local ARA fill on 0-2}}
=2\frac{\log R_j(p)}{\log 2}.
\]

The generation completes at the first prime gate

\[
\underbrace{c_j}_{\text{completion gate}}
=
\min\{p>b_j:R_j(p)\ge2\}.
\]

The next prime after `c_j` is the seed of generation `j+1`. Set `b_(j+1)=c_j`; retain the raw baseline `D(c_j)` and restart only the normalized fill coordinate.

## Plain restatement - AI RESTATEMENT

Begin immediately after an old connection structure has filled. The next prime does not arrive as another complete structure; it makes the first connection inside a newly enlarged one. Every later independent prime gate removes another share of the remaining open number lattice, so the typical distance between survivors grows. When that raw survivor spacing has doubled relative to the start of the generation, call the structure filled. Keep that doubled spacing as the new baseline, reset only the local ARA fill reading, and let the next prime seed the next generation.

## Mathematical representation - AI TRANSLATION

\[
\underbrace{b_j}_{\text{old completed boundary}}
\xrightarrow{\text{next prime}}
\underbrace{s_j}_{\text{first new connection}}
\xrightarrow{\prod r/(r-1)}
\underbrace{x_j:0\rightarrow2}_{\text{gradual fill}}
\xrightarrow{R_j\ge2}
\underbrace{c_j}_{\text{completion}}
\longrightarrow
\underbrace{b_{j+1}=c_j}_{\substack{\text{doubled raw baseline}\\\text{new local coordinate}}}.
\]

The local state resets; the raw scale does not:

\[
x_{j+1}(b_{j+1})=0,
\qquad
D(b_{j+1})\ge2D(b_j).
\]

## Back-translation without the source wording

Successive independent divisor relations thin the available number lattice multiplicatively. Treat the inverse surviving fraction as the raw scale of one generation. The first new divisor identity makes a small nonzero contribution. Contributions accumulate until the inverse density is twice its value at the previous boundary. That point becomes the reference scale for the following generation, whose dimensionless progress starts again near zero.

## AI additions and discarded information

### Assumptions added by the AI

- `D=W/varphi_E(W)` is the proposed meaning of connection capacity because it directly measures how far apart wheel survivors become as gates accumulate.
- "Doubles" is interpreted as doubling this raw mean survivor spacing, not doubling an integer label, wheel circumference, prime index or number of edges.
- A generation may contain many prime gates. "Hexagon" does not force exactly six gates in this instrument.

### Information this compression discards

- the full ordered residue pattern inside each wheel;
- which individual survivor is removed by which gate;
- local prime-gap fluctuations around the mean spacing;
- child-scale landmarks such as the first independent `q` strike at `q^2`;
- any literal spatial embedding of the proposed hexagon/pentagon geometry.

### Competing readings still possible

1. **Gate-layer reading:** one prime `q` seeds a layer that fills only after all `q`-to-old-wheel relations across `qW` are expressed.
2. **Square-boundary reading:** `q` seeds a child identity and `q^2` is its completion/doubling boundary.
3. **Fixed geometric-slot reading:** a generation contains `6, 12, 24, ...` discrete connection slots.
4. **Spacing-capacity reading (proposed primary):** however many gates are required to double `W/varphi_E(W)` constitute one completed generation.

These are not interchangeable. PN33 must remain DRAFT until Dylan confirms that reading 4 is the intended first test, or replaces it with one of the others.

## First possible reversal or flattening

The largest risk is equating "more connections" with "more surviving candidates." Adding a prime gate creates more relational structure while removing survivor positions. The proposed observable therefore uses **inverse survivor density**: stronger accumulated connection constraint means survivors are farther apart.

## Wrong-object conditions

The test is construct-invalid if it:

- reports only prime/composite accuracy;
- starts the new generation already at `x=2`;
- resets the raw spacing scale when the local coordinate resets;
- chooses the completion point after looking at prime gaps;
- calls a smooth PNT/log trend a literal observed hexagon without an independent geometric bridge.

## Required Dylan verdict

Choose one protocol label after reading the short check below:

> I think you mean that a prime seeds a larger but mostly empty connection generation. Later prime connections progressively constrain the number lattice until its raw spacing capacity has doubled; only then is that generation complete and the following prime begins the next locally reset `0-2` fill. I would first test "fill" as the accumulated inverse-survivor-density multiplier `product p/(p-1)`, while retaining `q^2` and full-wheel completion as separate child/adult landmarks. The main thing this translation discards is the full residue-web shape inside each rung.

Allowed verdicts: `EXACT ENOUGH TO TEST`, `USABLE WITH CORRECTION`, `WRONG OBJECT`, or `UNSURE / KEEP AS MUSING`.

## Dylan fidelity verdict - 22 July 2026

**Dylan's response:** "Yes, that should be functionally correct I think."

**Recorded protocol verdict:** `EXACT ENOUGH TO TEST`.

The phrase "functionally correct" authorizes the spacing-capacity observable as the first operational test. It does
not promote inverse survivor density into the only possible decompression of the ARA geometry. The competing
gate-layer, square-boundary and fixed-slot readings remain recorded as different future tests rather than being
silently treated as refuted if PN33 is null.

