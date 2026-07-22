# PN32 child-parent double Information³ lock - frozen protocol v1

**Frozen:** 22 July 2026, before primality labels were calculated  
**Status:** native-ARA cross-rung closure test  
**Population:** odd integers 3001 through 3999 inclusive  
**No wave 1, no fixed pairs, no averaging, no sieve, and no fitted classifier**

## Claim being tested

PN31 found that the complete ordering of the five retained child waves carried a sample-level prime/composite
difference even though the nearest child, its identity, every individual wave, and every post-hoc pair relation were
null. The proposed ARA interpretation is that the joint pattern may be a **double Information³ lock**:

\[
\underbrace{(A_c,B_c,J_c)}_{\text{child triangle}}
+
\underbrace{(A_p,B_p,J_p)}_{\text{doubled parent triangle}}.
\]

Here `A` and `B` are the two extrema of one declared handover ordering and `J` is the complete relation retained
between them. The two triangles supply six named components. This is the operational meaning of "hexagon" in PN32;
it is not inferred merely by counting five waves plus one extra item.

The parent rung is frozen as the exact structural doubling

\[
N\longmapsto 2N.
\]

This is an ARA rung convention being tested, not an established theorem about primes.

## Five independent wave coordinates

Retain exactly

\[
\mathcal W=\{3,5,9,11,13\}.
\]

For rung value \(M\in\{N,2N\}\) and wave \(w\), define

\[
r_w(M)=M\bmod w,
\qquad
x_w(M)=2\frac{r_w(M)}w,
\]

\[
h_w(M)=
\begin{cases}
0,&r_w(M)=0,\\[1mm]
2-x_w(M),&r_w(M)>0.
\end{cases}
\]

Order the five wave identities from smallest to largest \(h_w\). Exact ties are retained as grouped identities.
For the hard prime-versus-unresolved-composite comparison no retained child divides \(N\), and the generator will
verify that these rows have no order ties at either rung.

At each rung:

- `Phase A` is the wave group with minimum \(h_w\), nearest to its next handover;
- `Phase B` is the wave group with maximum \(h_w\), the opposite endpoint of this declared ordering;
- `J` is the complete closest-to-farthest five-wave order, not an average or selected pair.

The child lock is \(T_c=(A_c,B_c,J_c)\); the parent lock is \(T_p=(A_p,B_p,J_p)\).

## Cross-rung closure relation

For unique-order rows, list the child waves in child-order and replace each wave by its rank in the parent-order.
The resulting five-place permutation is

\[
K_{c\to p}=J_p\circ J_c^{-1}.
\]

This is a relation-preserving projection of the full six-component lock: it records how the entire child ordering
rearranges on the doubled rung. It is not a seventh independent wave.

## Relation-broken control

Before labels are known, generate 1,000 fixed-seed (`32004`) controls. The hard-comparison eligibility condition—no
declared child divides \(N\)—is available without prime labels. Within each consecutive 50-row block, retain every
eligible child triangle and every eligible parent triangle unchanged but randomly reassign which eligible parent
triangle belongs to which eligible child row. Ineligible rows remain fixed. Recompute \(K_{c\to p}\) after the
reassignment.

This control preserves:

1. all five child-wave coordinates;
2. all five parent-wave coordinates;
3. each complete child triangle;
4. each complete parent triangle;
5. local number-scale composition within 50-row blocks.

It destroys only the genuine `N -> 2N` child-parent pairing. If the intact result does not exceed this control, the
data do not support a closure-specific reading.

## Label firewall

1. Generate all child and parent coordinates for the 500 odd integers from 3001 through 3999.
2. Generate and freeze the 1,000 relation-broken parent-index maps.
3. Hash and freeze both artifacts.
4. Only then attach primality labels using direct trial division.
5. Do not use a sieve in coordinate generation or label reveal.

The hard control is again odd composites that evade direct division by all five declared child waves.

## Frozen endpoints

Use total-variation distance between primes and unresolved composites with 10,000 fixed-seed label permutations:

1. **PN31 replication:** child-order \(J_c\), seed `32001`.
2. **Parent-order control:** parent-order \(J_p\), seed `32002`.
3. **Double-lock closure:** relative permutation \(K_{c\to p}\), seed `32003`.
4. **Relation-broken comparison:** calculate the same closure TV for each of the 1,000 pre-frozen parent
   reassignments. The one-sided control p-value is `(1 + controls >= intact)/(1001)`.
5. Report the exact child-parent order-pair TV descriptively, with its category count, but do not use it for the
   verdict because sparse exact pairs can approach perfect separation without stable structure.
6. Report Phase-A/Phase-B endpoint-transition counts descriptively. They are not separately tested endpoints.

## Decision rule

- **Double-lock closure support:** child-order replication `p<0.01`, intact closure `p<0.01`, and relation-broken
  control `p<0.01`.
- **Closure-specific signal without PN31 replication:** both closure gates pass but child-order replication does not.
- **Child-order replication only:** child-order replication passes but either closure gate fails.
- **Suggestive:** at least one of the three inferential gates is below `0.05` without meeting a stronger rule.
- **Null:** none is below `0.05`.

PN32 does not generate or certify primes. Even a positive result would establish a stable association for this
declared modular doubling representation, not prove a literal physical hexagon or universal fractal closure.
