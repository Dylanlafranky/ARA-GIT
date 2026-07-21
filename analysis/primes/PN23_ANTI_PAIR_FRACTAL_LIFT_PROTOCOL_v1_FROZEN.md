# PN23 anti-pair fractal lift protocol — frozen v1

**Frozen:** 21 July 2026, before PN23 computation  
**Status:** exact recursive arithmetic test  
**Fresh 87-bit prime anchor:** sealed and not used

## Question

Can the wheel-sieve state be carried recursively using only one adult representative from each reversible pair, instead of separately carrying both phase directions?

For an even wheel modulus `M`, every surviving residue `r` has an opposite residue `M-r`. PN23 treats

\[
(r,M-r)
\]

as one ARA anti-pair. The smaller member `r<M/2` is the stored adult representative; the other member must be reconstructed rather than independently supplied.

## Frozen ladder

Start with the exact coprime residues modulo `M=14` and the three anti-pair representatives

\[
1,\;3,\;5
\quad\leftrightarrow\quad
(1,13),\;(3,11),\;(5,9).
\]

Lift recursively through new prime gates:

- development: `p = 3, 5, 11, 13`;
- untouched validation rung: `p = 17`.

This gives the wheel sequence

\[
14\to42\to210\to2310\to30030\to510510.
\]

The held-out rung and all decision rules are fixed before computation.

## One-pair reconstruction rule

For a stored adult representative `r`, current modulus `M`, and new prime `p` with `gcd(M,p)=1`, compute the unique killed copy

\[
k_A\equiv-rM^{-1}\pmod p,
\qquad 0\le k_A<p.
\]

The opposite branch is not independently searched. Its killed copy is predicted by reversibility:

\[
k_B=p-1-k_A.
\]

The two branches before the gate are

\[
r+jM
\quad\text{and}\quad
(M-r)+jM,
\qquad j=0,1,\ldots,p-1.
\]

Delete `j=k_A` from the first branch and `j=k_B` from the opposite branch. Pair every survivor `s` with `Mp-s`, and retain only

\[
\min(s,Mp-s)
\]

as the representative carried to the next rung.

## ARA ridge coordinate

Normalize the two killed-copy locations onto the ARA diameter:

\[
x_A=\frac{2k_A}{p-1},
\qquad
x_B=\frac{2k_B}{p-1}.
\]

The frozen ridge prediction is

\[
\frac{x_A+x_B}{2}=1.
\]

This may be a direct ridge, `x_A=x_B=1`, or a coarse-grained ridge made from asymmetric children.

## Primary pass conditions

Every rung must satisfy all of the following:

1. `k_A` is the unique copy of `r` divisible by `p`.
2. `k_B=p-1-k_A` is the unique killed copy of `M-r`.
3. The reconstructed survivor set exactly equals a direct `gcd(n,Mp)=1` enumeration.
4. The reconstructed anti-pair representatives exactly equal the lower-half members of that direct set.
5. Pair count is exactly multiplied by `p-1`.
6. The maximum numerical error in `(x_A+x_B)/2=1` is zero to floating precision, while the exact integer identity `k_A+k_B=p-1` holds without tolerance.

The held-out `p=17` rung passes only if all six conditions hold without changing the rule.

## Controls and interpretation

- **Direct control:** brute-force coprimality in the new modulus.
- **Compression control:** separately store every residue lane; the anti-pair method must use exactly half as many stored representatives.
- **No prime-locator promotion:** passing PN23 establishes a lossless recursive crosswalk to wheel-sieve/CRT symmetry. It does not, by itself, locate the next prime without applying new prime gates.
- **Falsifier:** any mismatch between reconstructed and direct residues, any failed opposite collision, or any non-ridge pair average.

## Predeclared reporting

Report every rung's modulus, gate, residue count, anti-pair count, expected growth, direct-ridge count, reconstruction mismatches, collision failures, maximum ridge error, and compression ratio. Include all three `M=14, p=3` pair paths as worked examples.
