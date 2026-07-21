# PN23 — anti-pair fractal lift report

**Date:** 21 July 2026  
**Outcome:** **PASS — lossless recursive anti-pair compression**  
**Independent validation:** **40/40 checks passed**

## Plain-language result

Yes: we can use the repeating, reversible structure instead of separately carrying both sides of every pair.

At each wheel-sieve rung, one stored adult lane `A=r` was enough to reconstruct:

1. its opposite adult lane `B=M-r`;
2. the exact child copy removed by the new prime gate on the A side;
3. the removed copy on the B side;
4. every surviving child pair at the next rung; and
5. the complete direct wheel residue set.

This worked without a rule change through

\[
14\to42\to210\to2310\to30030\to510510,
\]

including the untouched `p=17` rung. At that held-out rung, 2,880 stored parent pairs reconstructed 46,080 child pairs and all 92,160 individual residues, with no missing or extra values.

## Frozen test

The starting wheel modulo 14 contains three reversible pairs:

\[
(1,13),\quad(3,11),\quad(5,9).
\]

Only the lower-side representatives

\[
1,\quad3,\quad5
\]

were carried. Development used new prime gates `3, 5, 11, 13`; gate `17` was held back until the rule was frozen.

For stored representative `r`, modulus `M`, and new prime gate `p`, the killed A-side copy is

\[
\underbrace{k_A}_{\substack{\text{A-side child copy}\\\text{removed by gate }p}}
\equiv
\underbrace{-rM^{-1}}_{\substack{\text{solve the collision}\\r+k_AM\equiv0}}
\pmod p.
\]

ARA reversibility fixes the opposite collision without another search:

\[
\underbrace{k_B}_{\substack{\text{B-side removed copy}\\\text{anti-phase location}}}
=
\underbrace{p-1-k_A}_{\substack{\text{reflection across}\\\text{the child-copy ridge}}}.
\]

Normalize the child positions to the 0–2 ARA diameter:

\[
\underbrace{x_A}_{\text{A-side ARA position}}
=\frac{2k_A}{p-1},
\qquad
\underbrace{x_B}_{\text{B-side ARA position}}
=\frac{2k_B}{p-1}.
\]

Then

\[
\underbrace{\frac{x_A+x_B}{2}}_{\substack{\text{adult reading of}\\\text{both child directions}}}
=1.
\]

Plainly: the two child positions are exact reflections. They can be individually asymmetric, but the complete pair reads as the adult 1.0 ridge.

## Results by rung

| Phase | Lift | Parent pairs | Child pairs | Full residues recovered | Direct 1/1 ridges | Pair-ridge error | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| Development | `14 × 3 → 42` | 3 | 6 | 12 | 1 | 0 | Pass |
| Development | `42 × 5 → 210` | 6 | 24 | 48 | 2 | 0 | Pass |
| Development | `210 × 11 → 2310` | 24 | 240 | 480 | 3 | 0 | Pass |
| Development | `2310 × 13 → 30030` | 240 | 2,880 | 5,760 | 18 | 0 | Pass |
| **Held out** | **`30030 × 17 → 510510`** | **2,880** | **46,080** | **92,160** | **170** | **0** | **Pass** |

Every rung also matched an independently enumerated `gcd(n,Mp)=1` control exactly. Storage was always one representative for every two individual residue lanes: an exact `2:1` compression.

## Smallest worked rung

For `M=14` and gate `p=3`:

| Stored A | Reconstructed B | Killed copies `(k_A,k_B)` | ARA child positions `(x_A,x_B)` | Adult mean | Child-pair representatives carried upward |
|---:|---:|---:|---:|---:|---|
| 1 | 13 | `(1,1)` | `(1,1)` | 1 | `1, 13` |
| 3 | 11 | `(0,2)` | `(0,2)` | 1 | `11, 17` |
| 5 | 9 | `(2,0)` | `(2,0)` | 1 | `5, 19` |

This displays the distinction we had been discussing:

- `(1,1)` is a **direct ridge** visible in the children;
- `(0,2)` and `(2,0)` are **asymmetric child states** whose complete adult identity is nevertheless the 1.0 ridge.

The next wheel residues are reconstructed as the six pairs

\[
(1,41),(5,37),(11,31),(13,29),(17,25),(19,23).
\]

## What “abusing the fractal nature” achieved

The same local rule was applied at every rung. No separate B-side state was needed: reflection reconstructed it. No special rule was introduced for the larger modulus. This is a precise example of a child rule remaining valid after coarse-graining into a new parent identity.

The recursive pair counts were

\[
3\to6\to24\to240\to2880\to46080,
\]

and each lift obeyed

\[
\underbrace{N_{k+1}}_{\text{next-rung adult pairs}}
=
\underbrace{(p-1)}_{\substack{\text{surviving children}\\\text{per adult pair}}}
\underbrace{N_k}_{\text{current adult pairs}}.
\]

So the useful reduction is real but specific: it removes the redundant anti-phase half, giving a factor-of-two state compression. It does **not** reduce the whole next rung to only two global numbers. Each surviving adult pair remains a distinct child identity.

## Scientific status

This is a strong, exact ARA crosswalk:

- reversible A/B pairing is lossless;
- asymmetric children close to an exact adult ridge;
- the same transformation repeats at every scale tested;
- a held-out rung was reconstructed without adjustment.

It is also established modular arithmetic. The result follows from Chinese-remainder/wheel symmetry once residues are paired by `r ↔ M-r`. The held-out rung therefore validates the implementation and the ARA interpretation, not a previously unknown prime theorem.

Most importantly, it does not yet produce a constant-cost next-prime locator. The next prime gate `p` is still an input, and the number of surviving pair identities grows by `p-1`. The result tells us exactly what can be compressed safely and what cannot.

## Reproducible artifacts

- Frozen protocol: `PN23_ANTI_PAIR_FRACTAL_LIFT_PROTOCOL_v1_FROZEN.md`
- Primary implementation: `pn23_anti_pair_fractal_lift.py`
- Results: `PN23_ANTI_PAIR_FRACTAL_LIFT_RESULTS.json`
- Rung table: `PN23_ANTI_PAIR_FRACTAL_LIFT_RUNGS.csv`
- Worked paths: `PN23_ANTI_PAIR_FRACTAL_LIFT_WORKED_PATHS.csv`
- Independent validator: `validate_pn23_anti_pair_fractal_lift.py`
- Validation: `PN23_ANTI_PAIR_FRACTAL_LIFT_VALIDATION.json`
- Executed notebook: `PN23_ANTI_PAIR_FRACTAL_LIFT_REPRODUCIBILITY.ipynb`

## Next clean test

Use the pair-compressed representation as an actual wheel generator and benchmark it against a conventional full-lane generator on:

1. exact outputs;
2. peak stored state;
3. runtime; and
4. whether any higher-order grouping compresses more than the proven `2:1` anti-pair symmetry without losing residue identity.

That separates a genuine computational benefit from a correct geometric relabelling.
