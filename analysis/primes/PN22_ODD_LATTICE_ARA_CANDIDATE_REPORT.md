# PN22 — odd-lattice ARA candidate test

**Date:** 21 July 2026  
**Status:** **EXACT MOD-14 WHEEL CROSSWALK — NOT PRIME-SPECIFIC**  
**Development inputs:** `A=1,...,1,000,000`  
**Independent validation:** 16/16 checks passed  
**Fresh 87-bit anchor:** remains sealed

## Result first

The proposed odd-compatible ARA construction is mathematically coherent and produces a real prime-candidate enrichment:

\[
\underbrace{T(A)}_{\text{upward odd-lattice projection}}
=
\operatorname{oddceil}
\left(
\underbrace{A}_{0\text{ singularity}}
+
\underbrace{2A}_{2\text{ singularity}}
+
\underbrace{\frac A2}_{1.0\text{ ridge offset}}
+1
\right).
\]

Among one million outputs, `166,740` were prime:

\[
\Pr(T(A)\text{ prime})=16.6740\%.
\]

All odd integers in the same output range were prime at `14.2942%`, so the ARA construction produced a **16.65% relative lift** over unfiltered odd numbers.

However, the transformation exactly enumerates four fixed admissible residue classes modulo 14. Against that exact matched control, its lift is precisely `1.000000`. The prime enrichment is therefore established wheel filtering rather than a new prime-location rule.

## Odd inputs work geometrically

For `A=27`:

\[
A=27,
\qquad B=54,
\qquad \frac{B-A}{2}=13.5.
\]

The continuous identity closes at

\[
27+54+13.5+1=95.5.
\]

Upward projection to the next odd lattice point gives

\[
T(27)=97,
\]

which is prime. The half-integer is therefore not a breakdown of the ARA construction; it records that the continuous ridge falls between discrete integer nodes.

## Exact piecewise form

Writing `A` by its remainder modulo 4 gives

\[
T(A)=
\begin{cases}
14k+1,&A=4k,\\
14k+5,&A=4k+1,\\
14k+9,&A=4k+2,\\
14k+13,&A=4k+3.
\end{cases}
\]

Therefore every output lies in

\[
T(A)\bmod14\in\{1,5,9,13\}.
\]

These lanes are always odd and never divisible by 7. That is why they contain primes more densely than the raw odd-number line.

The equality is exact over the tested range:

> `{T(1),...,T(1,000,000)}` equals every integer in `[5,3,500,001]` whose residue modulo 14 is `1`, `5`, `9`, or `13`.

## Prime-yield controls

| Population | Count | Prime rate | Candidate-relative lift |
|:---|---:|---:|---:|
| ARA candidates `T(A)` | 1,000,000 | **16.6740%** | 1.0000 |
| All odd integers in the same range | 1,749,999 | 14.2942% | **1.1665** |
| All integers coprime to 14 | 1,499,999 | 16.6765% | 0.9999 |
| Exact lanes `{1,5,9,13} mod 14` | 1,000,000 | **16.6740%** | **1.0000** |

There are 15 ways to select four of the six prime-admissible residues modulo 14. The ARA subset ranked 13th of 15 on this finite interval, but all rates lay in the extremely narrow range `16.6734%–16.6801%`. There is no meaningful special enrichment of its four lanes beyond admissibility.

## Worked examples

| `A` | `B=2A` | Ridge offset | Continuous result | `T(A)` | Prime? |
|---:|---:|---:|---:|---:|:---|
| 27 | 54 | 13.5 | 95.5 | **97** | yes |
| 32 | 64 | 16 | 113 | **113** | yes |
| 34 | 68 | 17 | 120 | **121** | no, `11²` |
| 36 | 72 | 18 | 127 | **127** | yes |
| 28 | 56 | 14 | 99 | **99** | no |
| 30 | 60 | 15 | 106 | **107** | yes |
| 40 | 80 | 20 | 141 | **141** | no |
| 48 | 96 | 24 | 169 | **169** | no, `13²` |
| 52 | 104 | 26 | 183 | **183** | no |
| 56 | 112 | 28 | 197 | **197** | yes |

The mixture is important: the construction excludes the parity and factor-7 troughs, but it does not exclude collisions with 3, 5, 11, 13, and higher prime children.

## Perfect-power subgroup

The two initiating examples, `27=3³` and `32=2⁵`, are perfect powers, so this subgroup was declared before calculation.

| Input subgroup | Inputs | Prime outputs | Candidate rate | Same-lane local control rate |
|:---|---:|---:|---:|---:|
| All unique perfect powers | 1,110 | 119 | **10.72%** | 18.09% |
| Odd perfect powers | 554 | 74 | 13.36% | 18.47% |
| Even perfect powers | 556 | 45 | 8.09% | 17.72% |
| Powers of two | 19 | 4 | 21.05% | 27.57% |

The full perfect-power subgroup performed substantially **worse** than its same-residue local controls. The powers-of-two sample is too small for a general conclusion and also did not outperform its control.

The successful `27` and `32` examples are therefore genuine hits, but they are not representative evidence for a perfect-power rule.

## ARA interpretation

The test establishes a clean structural translation:

1. `A` establishes the local 0 singularity.
2. `2A` establishes the local 2 singularity.
3. `A/2` restores the 1.0 ridge displacement.
4. `+1` and `oddceil` release the continuous closure onto the upward odd lattice.
5. The resulting four-lane geometry automatically avoids the 2- and 7-child collision schedules.

This gives additional mathematical content to the construction: it behaves as a compact two-gate wheel. But other prime-child schedules remain unresolved, so the output is a survivor candidate rather than a guaranteed prime.

## Verdict

PN22 is a positive **crosswalk** and a negative **prime-specific prediction** result:

- **Supported:** odd ARA processing is coherent; the rule gives an exact four-lane mod-14 structure and improves candidate purity over raw odds.
- **Not supported:** the rule identifies primes more accurately than the equivalent mod-14 wheel, guarantees primes, or gives special enrichment for perfect-power inputs.

No blind target run is justified without an additional ARA term that represents collisions from the remaining prime children.

## Files

- `PN22_ODD_LATTICE_ARA_CANDIDATE_PROTOCOL_v1_FROZEN.md`
- `pn22_odd_lattice_ara_candidate.py`
- `PN22_ODD_LATTICE_ARA_CANDIDATE_RESULTS.json`
- `validate_pn22_odd_lattice_ara_candidate.py`
- `PN22_ODD_LATTICE_ARA_CANDIDATE_VALIDATION.json`
- `PN22_ODD_LATTICE_ARA_CANDIDATE_REPRODUCIBILITY.ipynb`
- `PN22_NOTEBOOK_EXECUTION_VALIDATION.json`

