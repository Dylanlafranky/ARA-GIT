# PN14 child-to-adult wave and rung ridge - translation-fidelity packet v1

**Claim ID:** `PN14/CHILD-ADULT-RIDGE/v1`  
**Declared:** 21 July 2026  
**Status:** frozen before the scale-11 target was calculated  
**Dylan fidelity verdict:** `EXACT ENOUGH TO TEST` under the low-energy explicit-approval rule.

## F0 - frozen source

**USER PRIOR:**

> "The ratios were 8.07 and 7.96. Because those children were selected near n^0.45, so we found a phase a and
> phase B, and they're direct increases of the child wave below. And yes, we should run that test."

**DYLAN CORRECTION before the run:**

> "8.07/7.96 is just a 1.0 ridge or very close to it."

**Identity/system being measured:** adjacent prime-gate child cycles in the already-open PN10B/PN13 construction,
their joint adult repeat, and the relation between consecutive adult scale-growth steps.

**Ordered poles and direction:** for a fixed adjacent gate pair `(q,r)`, Phase A is the signed residue cycle
`s_q=2(n mod q)/q-1` and Phase B is `s_r=2(n mod r)/r-1`. Up means multiplying the raw-number scale by ten. Pole
names can be reversed if the reversal is declared; all calculations retain one orientation.

**Scale/rung origin:** decimal scales with anchors `N_d=4*10^d`. The child gates are the nine largest primes below
`N_d^0.45`, preserving PN10B's paid-gate definition. This is a declared prime-test rung, not a claim that every ARA
octave is base ten.

**Invariant relational claim:**

1. two coprime child periods `q` and `r` directly generate an adult closure period `T_qr=q*r`;
2. because both child scales are selected near `N^0.45`, adult periods grow near `N^0.90`;
3. consecutive adult growth multipliers should therefore meet at a near-`1.0` ARA ridge;
4. after raw position is changed into relative child-pair phase, the signed child-product shape should align across
   scales instead of being flattened by unequal raw-window coverage.

**Permitted decompression:** exact joint period, relative phase, signed child product, the two-entry TE-ARA
normalisation of consecutive growth multipliers, and separate raw/prime/paid-surviving-composite curves.

**Forbidden substitutions/proxies:** treating `8.07` or `7.96` themselves as ARA phase readings; using equal raw
window widths as equal adult phase coverage; moving the `0.45` gate boundary after seeing scale 11; selecting the
target pair by its result; hiding prime/composite curves inside a single mean; or treating an arithmetic recovery as
independent evidence for a universal physical law.

**Observable needed:** scale-11 median adjacent-pair joint period for the untouched rung-ridge check, plus equal
relative-phase samples for one deterministically selected median-product adjacent pair at scales 8-11.

**Known ambiguity / competing reading:** the adult closure is an exact consequence of coprimality. The evidential
question is not whether `lcm(q,r)=qr`; it is whether the same child-to-adult scaling remains ridge-stable at the
untouched rung and whether phase normalisation recovers a common internal shape in prime and survivor populations.

**Wrong-object condition:** if the target uses a different exponent, moving pair-selection rule, unequal phase
coverage, or an amplitude comparison in place of wavelength/phase, it is not this test.

## F1 - three-view translation

### Plain restatement

The two nearby child cycles do not merely sit next to one another. Together they make a much slower adult cycle. The
adult grows by almost the same factor on each tenfold scale step, so comparing one growth step with the next gives a
near-balanced `1.0` ridge. We then walk around equal portions of that adult cycle at each scale and ask whether the
children draw the same shape there.

### Mathematical representation

For the eight adjacent paid-gate pairs at scale `d`,

\[
T_{d,j}=q_{d,j}r_{d,j},\qquad J_d=\operatorname{median}_j T_{d,j},\qquad
G_d=\frac{J_{d+1}}{J_d}.
\]

The two-entry ridge reading between consecutive growth steps is

\[
\underbrace{R_d}_{\substack{\text{adult-growth}\\\text{ARA reading}}}
=\frac{2G_d}{G_d+G_{d+1}},\qquad
\underbrace{2-R_d}_{\text{opposite entry}},
\]

so exact equality gives `R_d=1`. For one fixed adjacent pair,

\[
\theta_{q,r}(n)=\left(n\frac{r-q}{qr}\right)\bmod 1,\qquad
Z_{q,r}(n)=\left(2\frac{n\bmod q}{q}-1\right)
            \left(2\frac{n\bmod r}{r}-1\right).
\]

### Back-translation without the source wording

Measure two child clocks, multiply their coprime periods to obtain the parent clock, and compare how much that parent
clock lengthens on neighboring scale steps. Equal lengthening is the balanced ridge. Next, replace absolute integer
position with position around the parent relation and check whether the same signed interaction curve reappears.

## Added assumptions and discarded information

**AI additions:** median across the eight adjacent pairs is the fixed adult-scale summary; the pair nearest that
median is the fixed phase-shape representative; a 16-sector relative-phase grid is sufficient to test curve
collapse; the target tolerance and controls are fixed in the companion protocol.

**Information discarded:** the other seven pair-specific adult shapes, Phi handover, physical energy, and any claim
about primes beyond this modular construction are outside the primary test, though pair-level summaries remain in
the geometry output.

**Alternative objects:** a common-phase rather than relative-phase adult coordinate; a full square-root gate pair;
an aggregation rung not tied to raw-number scale; a curved carrier external to the modular pair.

**First flattening risk:** an equal-width raw window sees 22.9%, 1.83%, and 0.345% of the observed adult drift at
scales 8-10. Comparing those means as though they were the same phase slice destroys the intended relation.

## F3 - critical-field gate

| Field | Match | Note |
|---|---:|---|
| identity | 1 | adjacent child cycles and their joint adult |
| poles | 1 | two signed residue children |
| direction | 1 | up is fixed as a tenfold scale step |
| rung | 1 | `N_d=4*10^d`, `q,r near N_d^0.45` |
| observable | 1 | adult growth ridge and phase-aligned child product |
| coupling | 1 | direct coprime joint closure |
| closure | 1 | `T_qr=q*r` |
| falsifier | 1 | fixed in the companion protocol |

**Fidelity:** `1.00` as documentation fidelity, not truth probability.
