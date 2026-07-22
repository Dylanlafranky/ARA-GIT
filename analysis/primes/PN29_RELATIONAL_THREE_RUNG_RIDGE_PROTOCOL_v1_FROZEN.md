# PN29 relational three-rung ridge — frozen protocol v1

**Frozen:** 22 July 2026, before primality labels were calculated  
**Status:** small native-ARA ridge diagnostic  
**Population:** odd integers 15 through 999 inclusive  
**No sieve and no large-number search**

## Question

After converting all six child waves onto local ARA coordinates and carrying their collapsed displacement upward through two relational rung halvings, do prime integers lie closer to the 1.0 ridge than nearby odd composites?

This is a ridge-location diagnostic. It does not attempt to generate the next prime.

## Child coordinates

Use the fixed child pairs

\[
(1,13),\qquad(3,11),\qquad(5,9).
\]

For chosen integer \(N\), the previously declared local completion is

\[
u_w(N)=
\begin{cases}
1,&w\mid N,\\[2mm]
\dfrac{2w}{N},&w\nmid N.
\end{cases}
\]

Each pair is converted onto its own total-2 ARA scale:

\[
x_{a,b}(N)=\frac{2u_b(N)}{u_a(N)+u_b(N)}
=1+\frac{u_b(N)-u_a(N)}{u_a(N)+u_b(N)}.
\]

Thus each pair has ridge \(x=1\), regardless of its raw numerical units.

## Three-child collapse

Collapse the three pair coordinates by their equal-weight mean:

\[
R_0(N)=\frac{x_{1,13}(N)+x_{3,11}(N)+x_{5,9}(N)}3.
\]

Its signed ridge displacement is

\[
\epsilon_0(N)=R_0(N)-1.
\]

## Relational rung transport

Moving upward from child to parent expresses the same displacement inside a twice-larger relational identity, so the normalised displacement halves at each rung:

\[
R_1(N)=1+\frac{\epsilon_0(N)}2,
\]

\[
\boxed{
R_2(N)=1+\frac{\epsilon_0(N)}4.
}
\]

The upper-rung ridge distance is

\[
D_2(N)=|R_2(N)-1|=\frac{|\epsilon_0(N)|}{4}.
\]

No ARA coordinate is added to an integer. No rounding or fixed number-line offset occurs.

## Frozen worked example

For 35:

\[
R_0(35)=1.0343776236,
\]

\[
R_1(35)=1.0171888118,
\]

\[
R_2(35)=1.0085944059,
\qquad
D_2(35)=0.0085944059.
\]

## Small test population

Calculate coordinates for every odd integer in

\[
15\le N\le999.
\]

This produces 493 numbers. The coordinate generator must not contain a primality routine or read prime labels. Its output must be hashed and frozen before labels are attached.

Primality is then determined independently by direct trial division for each number. No sieve is used.

## Frozen endpoints

1. Compare mean and median \(D_2\) for primes versus odd composites.
2. Calculate rank AUC:

\[
\mathrm{AUC}=P(D_{2,\rm prime}<D_{2,\rm composite})
+\tfrac12P(D_{2,\rm prime}=D_{2,\rm composite}).
\]

An AUC above 0.5 means a random prime is more ridge-close than a random odd composite.

3. Repeat the comparison against **unresolved composites**: composites not divisible by any nontrivial declared child label `{3,5,9,11,13}`. This controls whether any apparent separation is only a small-divisor screen.
4. Use 10,000 fixed-seed (`29200`) label permutations for one-sided tests of lower prime ridge distance, both overall and against unresolved composites.

## Decision rule

- **Strong ridge support:** overall and unresolved-composite AUC are both above 0.60, with both one-sided permutation p-values below 0.01.
- **Partial / child-filter support:** primes are closer overall with p below 0.01, but unresolved-composite separation fails.
- **Null:** no reliable overall separation.
- **Opposite direction:** primes are reliably farther from the ridge.

Because \(D_2=D_0/4\), the two-rung transform cannot change the ordering of numbers. This test asks whether the declared child coordinate already carries prime-ridge information and verifies that upward relational transport preserves it without mixing units.

