# PN30 dynamic relational flip ridge - frozen protocol v1

**Frozen:** 22 July 2026, before primality labels were calculated  
**Status:** small native-ARA reversible-ridge diagnostic  
**Population:** odd integers 1001 through 1999 inclusive  
**No sieve and no large-number search**

## Question

Does restoring the declared ARA singularity flip to the three child pairs improve prime-ridge separation, especially against composites that evade the declared child divisors?

PN29 kept the child pairs permanently oriented as `(1,13)`, `(3,11)`, `(5,9)`. PN30 tests the newly clarified rule that the child which has most recently crossed its singularity becomes Phase A until its partner crosses.

## Child-wave phase

For a chosen odd integer \(N\) and child wave \(w\), define its normalized progress since its most recent singularity crossing as

\[
\theta_w(N)=\frac{N\bmod w}{w},
\qquad 0\leq\theta_w<1.
\]

Its equivalent position on the ARA diameter is

\[
s_w(N)=2\theta_w(N).
\]

Thus \(s_w=0\) immediately after a singularity crossing, \(s_w=1\) at the local ridge, and \(s_w\to2\) immediately before the next flip.

For each unordered pair

\[
\{1,13\},\qquad\{3,11\},\qquad\{5,9\},
\]

the child with smaller \(\theta\) is assigned Phase A and the other is assigned Phase B. This compares differently sized waves on the same normalized cycle rather than comparing their raw labels.

If the two phases are equal, the pair is at a synchronized crossing. Because the members of all three declared pairs are coprime, equality in this population occurs only at their shared exact crossing. The pair coordinate is then fixed at the ridge \(1\).

## Local completion and oriented pair coordinate

Retain the PN29 local-completion rule:

\[
u_w(N)=
\begin{cases}
1,&w\mid N,\\[2mm]
\dfrac{2w}{N},&w\nmid N.
\end{cases}
\]

After dynamically assigning Phase A and Phase B, calculate

\[
x_{A\to B}(N)=\frac{2u_B(N)}{u_A(N)+u_B(N)}.
\]

Swapping orientation maps \(x\) to \(2-x\). Therefore the flip changes the sign of a pair's ridge displacement while preserving its magnitude:

\[
x_{B\to A}=2-x_{A\to B}.
\]

This is important because PN30 collapses the three **signed** pair displacements before taking an absolute distance.

## Three-pair collapse and upward transport

Collapse the dynamically oriented pair coordinates by their equal-weight mean:

\[
R_0^{\rm flip}(N)=\frac{x_{\{1,13\}}+x_{\{3,11\}}+x_{\{5,9\}}}{3},
\qquad
\epsilon_0^{\rm flip}=R_0^{\rm flip}-1.
\]

Carry the displacement upward through the same two relational rung halvings used in PN29:

\[
R_1^{\rm flip}=1+\frac{\epsilon_0^{\rm flip}}2,
\qquad
R_2^{\rm flip}=1+\frac{\epsilon_0^{\rm flip}}4,
\]

\[
D_2^{\rm flip}=\left|R_2^{\rm flip}-1\right|.
\]

No ARA coordinate is added to an integer. No fixed number-line offset is introduced.

## Frozen internal comparator

On the same unlabeled integers, also calculate the PN29 static-orientation coordinate

\[
R_0^{\rm static}=\frac{x_{1\to13}+x_{3\to11}+x_{5\to9}}3,
\qquad
D_2^{\rm static}=\frac{|R_0^{\rm static}-1|}{4}.
\]

This is not a substitute method. It isolates the effect of restoring the ARA flip while holding the child waves, completion rule, collapse and rung transport constant.

## Fresh small population and label firewall

Calculate both coordinate systems for every odd integer in

\[
1001\leq N\leq1999.
\]

The coordinate generator must not contain a primality routine or read prime labels. Its output is hashed and frozen before primality is determined independently by direct trial division. No sieve is used.

## Frozen endpoints

1. Compare mean and median \(D_2^{\rm flip}\) for primes and odd composites.
2. Calculate rank AUC, where values above \(0.5\) mean primes are more ridge-close.
3. Repeat against unresolved composites not divisible by any declared nontrivial child label `{3,5,9,11,13}`.
4. Repeat endpoints for the static-orientation comparator on the same population.
5. Report the dynamic-minus-static AUC change and the orientation/tie frequencies for each child pair.
6. Use 10,000 fixed-seed (`30001` and `30002`) one-sided label permutations for the dynamic coordinate.

## Decision rule

- **Flip-supported prime ridge:** dynamic AUC exceeds 0.60 overall and against unresolved composites, both dynamic one-sided permutation p-values are below 0.01, and dynamic unresolved AUC exceeds static unresolved AUC.
- **Flip adds residual information:** dynamic unresolved AUC exceeds 0.55 with one-sided p below 0.05 and exceeds static unresolved AUC, without meeting the strong rule.
- **Child-filter support only:** dynamic separates primes from all composites but not unresolved composites.
- **Null / no improvement:** dynamic does not reliably separate primes or does not improve the unresolved comparison.
- **Opposite direction:** primes are reliably farther from the dynamic ridge.

This remains an exploratory coordinate diagnostic. It does not generate or certify primes.
