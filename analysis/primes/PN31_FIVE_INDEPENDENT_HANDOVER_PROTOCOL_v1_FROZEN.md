# PN31 five independent child-wave handovers - frozen protocol v1

**Frozen:** 22 July 2026, before primality labels were calculated  
**Status:** small native-ARA independent-child diagnostic  
**Population:** odd integers 2001 through 2999 inclusive  
**No wave 1, no fixed pairs, no child averaging, no sieve, and no fitted classifier**

## User correction being tested

Discard wave 1 because it crosses at every integer and would be a permanently winning, non-informative Phase A.

Retain the five child waves

\[
\mathcal W=\{3,5,9,11,13\}
\]

as five separate wave states. Do not force them into the fixed pairs `(3,11)` and `(5,9)`, and do not collapse them to one scalar before their individual positions are inspected.

At each chosen number, the child wave closest to approaching or sitting on its next handover is Phase A.

## Independent child coordinates

For chosen odd integer \(N\) and each wave \(w\in\mathcal W\), define

\[
r_w(N)=N\bmod w,
\]

\[
x_w(N)=2\frac{r_w(N)}{w}.
\]

This is the wave's current position on its own 0-2 ARA cycle.

Its directed forward distance to the next handover is

\[
h_w(N)=
\begin{cases}
0,&r_w(N)=0,\\[2mm]
2-x_w(N),&r_w(N)>0.
\end{cases}
\]

The phase description is:

- `on handover` when \(x_w=0\);
- `leaving handover` when \(0<x_w<1\);
- `local ridge` when \(x_w=1\);
- `approaching handover` when \(1<x_w<2\).

Because all five waves are odd, integer observations cannot land exactly at \(x_w=1\).

## Phase A and retained five-wave state

Define

\[
h_A(N)=\min_{w\in\mathcal W}h_w(N).
\]

Every wave attaining this minimum is a Phase A child. Exact ties are retained rather than broken arbitrarily. The remaining waves keep their own \((x_w,h_w,\text{direction})\) records; they are not automatically renamed Phase B and are not averaged.

Also retain:

1. the complete ordering of the five waves from smallest to largest forward handover distance;
2. the number of waves currently approaching handover;
3. the number sitting exactly on handover;
4. each wave's individual forward distance.

## Fresh label firewall

Generate these coordinates for every odd integer in

\[
2001\leq N\leq2999.
\]

This gives 500 chosen numbers. The coordinate generator must not contain a primality routine or read prime labels. The coordinate CSV is hashed and frozen before labels are attached.

Primality is then determined independently by direct trial division. No sieve is used.

## Primary hard comparison

All primes in this interval evade the five declared child divisors. Therefore the primary comparison is primes against **unresolved composites** that also evade all five divisors.

Frozen endpoints:

1. Compare Phase A distance \(h_A\) by mean, median and rank AUC. The proposed direction is that primes are closer to a child handover, so lower \(h_A\) is the positive direction.
2. Use 10,000 fixed-seed (`31001`) one-sided label permutations for the mean Phase A-distance difference.
3. Compare the categorical identity of Phase A between primes and unresolved composites using total-variation distance with 10,000 fixed-seed (`31002`) label permutations.
4. Compare the complete five-wave order signature using total-variation distance with 10,000 fixed-seed (`31003`) label permutations.
5. For each of the five waves, report its individual handover-distance AUC and one-sided permutation p-value using fixed seeds `31103`, `31105`, `31109`, `31111`, and `31113`. Apply Holm correction across the five p-values; these are component diagnostics, not five independent headline discoveries.
6. Compare the count of approaching waves descriptively and with a two-sided fixed-seed (`31004`) permutation test.
7. Repeat basic Phase A-distance summaries against all odd composites as an explicitly easier secondary comparison.

No fixed child pairing or pair-derived coordinate may enter PN31.

## Decision rule

- **Five-wave Phase A support:** unresolved-composite AUC is above 0.60, the one-sided Phase A-distance permutation is below 0.01, and either Phase A-identity or full-order permutation is below 0.01.
- **Ordered child structure only:** Phase A-identity or full-order permutation is below 0.01, but the Phase A-distance gate fails.
- **Suggestive:** at least one primary permutation result is below 0.05 without meeting either stronger rule.
- **Null:** no primary endpoint is below 0.05.
- **Opposite direction:** Phase A distance is reliably larger for primes.

This is an independent-wave structure test. It does not generate or certify primes and does not define a new parent-collapse law.
