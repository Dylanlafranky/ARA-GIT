# PN22 odd-lattice ARA candidate protocol — frozen v1

**Frozen:** 21 July 2026, before PN22 computation  
**Status:** development-only arithmetic test  
**Fresh 87-bit anchor:** not used

## Proposed construction

For integer starting identity `A`, construct the opposite singularity `B=2A`. The local ridge offset is half the diameter:

\[
\Delta_{BA}=\frac{B-A}{2}=\frac A2.
\]

The continuous candidate is

\[
C(A)=A+B+\Delta_{BA}+1=\frac{7A}{2}+1.
\]

Project it upward onto the odd-integer lattice:

\[
T(A)=\operatorname{oddceil}(C(A)),
\]

where `oddceil(x)` is the smallest odd integer greater than or equal to `x`.

The upward direction is frozen from the proposed release direction. It is not selected after observing primality.

## Development range

- Inputs: every integer `A` from `1` through `1,000,000`.
- Outputs: approximately `5` through `3,500,001`.
- Exact primality is determined with a conventional Eratosthenes sieve.

## Algebraic audit

Derive `T(A)` separately for `A mod 4`. Report the output residue classes modulo 14 and determine whether the transformation is equivalent to an established wheel filter.

## Primary prime-yield comparison

Report:

1. prime rate among all `T(A)` candidates;
2. prime rate among all odd integers in the same output range;
3. prime rate among all integers coprime to 14 in that range;
4. prime rate among the exact output residue classes selected by `T`;
5. prime rates for every four-of-six subset of the prime-admissible residues modulo 14.

### Primary decision

- **New candidate enrichment:** `T` exceeds a residue- and range-matched control.
- **Wheel crosswalk:** `T` equals its exact residue-class control and any lift over raw odds is explained by excluding multiples of 7.
- **No enrichment:** `T` does not improve even on raw odd candidates.

## Predeclared examples

Report at minimum:

- `A=27`;
- `A=32`;
- `A=34`;
- `A=36`;
- at least four additional nearby inputs showing both prime and composite outputs.

## Perfect-power subgroup

Because `27=3^3` and `32=2^5`, evaluate all unique perfect powers `A=b^e <= 1,000,000`, with `b>=2` and `e>=2`. Also show powers of two separately as a small descriptive subgroup.

For every subgroup candidate `T(A)`, compare primality with the same residue class at offsets `T(A) ± 14j`, `j=1,...,10`, restricted to the sieved range. This preserves the modulo-14 lane and approximately matches scale.

The perfect-power result is secondary. Report a cluster-by-input standard error for the candidate-minus-local-control difference; do not promote the small powers-of-two subgroup into a general claim.

## Fresh-test rule

Do not apply the sealed 87-bit anchor unless PN22 shows enrichment beyond exact residue-matched controls and a separate input-selection rule is frozen. A prime hit for a hand-selected example is not sufficient.

