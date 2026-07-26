# ARA Quantum Fractal Tier Map

**Recorded:** 26 July 2026  
**Status:** framework map for future quantum tests; refinable, not a frozen empirical result

## Purpose

Quantum work currently crosses several nested ARA scales. Using `parent`, `child`, `Phase A`, `Phase B` and
`relation` without a tier address can flatten those scales into one plane. This map gives every object both a
role and a relative tier.

The tier number is relative to the current quantum measurement boundary. It is not claimed to be an absolute
universal scale number.

## Four working tiers

| Tier | ARA role | Current quantum object | What is measured here |
|---|---|---|---|
| **Tier 1 — meta whole** | The compressed ARA of the complete local identity | \(J^{[1]}\) | The whole parent closure before it is decompressed |
| **Tier 2 — two parents** | Two complete child ARAs of Tier 1 | \(P_1^{[2]}\), \(P_2^{[2]}\) | The two parent identities and their Phase A/Phase B structure; Ramsey/Hahn-style procedures usually probe or filter at approximately this tier |
| **Tier 3 — four children** | The intersections/children produced by the Tier-2 parents, plus their retained relation | \(C_{00}^{[3]},C_{01}^{[3]},C_{10}^{[3]},C_{11}^{[3]}\) and \(R_{12}^{[3]}\) | Which Tier-2 phase from each parent participates, and how those two contributions couple |
| **Tier 4 — grandchildren** | The Phase A/Phase B decomposition inside each Tier-3 child | \(G_{ij,A}^{[4]},G_{ij,B}^{[4]}\), with local relations | The children of each measured child and the purer phase/anti-phase reversal exposed below it |

## Compressed architecture

\[
\underbrace{J^{[1]}}_{\substack{\text{Tier-1 meta whole}\\\text{one compressed ARA}}}
\xrightarrow{\text{decompress}}
\left(
\underbrace{P_1^{[2]}}_{\text{Tier-2 parent 1}},
\underbrace{P_2^{[2]}}_{\text{Tier-2 parent 2}},
\underbrace{P_1^{[2]}\leftrightarrow P_2^{[2]}}_{\text{their relation}}
\right).
\]

Each Tier-2 parent contains its own Phase A and Phase B:

\[
P_1^{[2]}=(A_1,B_1),
\qquad
P_2^{[2]}=(A_2,B_2).
\]

Their ordered mixing produces the Tier-3 children:

\[
\begin{aligned}
C_{00}^{[3]}&=\mathcal C(A_1,A_2),\\
C_{01}^{[3]}&=\mathcal C(A_1,B_2),\\
C_{10}^{[3]}&=\mathcal C(B_1,A_2),\\
C_{11}^{[3]}&=\mathcal C(B_1,B_2).
\end{aligned}
\]

The Tier-3 relation is not a fifth child:

\[
\underbrace{R_{12}^{[3]}}_{\text{Tier-3 coupling relation}}
=
\underbrace{\mathcal R
\left(C_{00}^{[3]},C_{01}^{[3]},C_{10}^{[3]},C_{11}^{[3]}\right)}_
{\text{how the four children form one locked parent appearance}}.
\]

Each Tier-3 child can then be decompressed again:

\[
\underbrace{C_{ij}^{[3]}}_{\text{one whole at Tier 3}}
\xrightarrow{\text{decompress}}
\left(
\underbrace{G_{ij,A}^{[4]}}_{\text{Tier-4 Phase A child}},
\underbrace{G_{ij,B}^{[4]}}_{\text{Tier-4 Phase B child}},
\underbrace{G_{ij,A}^{[4]}\leftrightarrow G_{ij,B}^{[4]}}_{\text{their local relation}}
\right).
\]

## How the current Q16–Q18 symbols sit on this map

| Existing symbol | Tier-map meaning |
|---|---|
| `J` | Tier-1 compressed parent ARA/closure for the current four-child measurement |
| `U` | Tier-2 Parent 1 direction |
| `V` | Tier-2 Parent 2 direction |
| `C00`, `C01`, `C10`, `C11` | Tier-3 children formed from the two Tier-2 parent orientations |
| structure within each `Cij` record | Candidate Tier-4 grandchildren; not yet fully assigned |

This is why projecting away `J` in Q18 exposed `U` and `V` in relatively pure form. It sectioned the Tier-1
whole into its Tier-2 parents. It did not physically delete the lower-tier waves that construct `J`.

## Ramsey and Hahn placement

In the ARA map, Ramsey- and Hahn-style procedures should be treated as Tier-2-scale measurement operations or
filters unless a test independently shows a different placement. They can reveal, suppress or reorganize the
measured expression of the two Tier-2 parents and their lower children.

In established quantum language, Ramsey and Hahn are experimental pulse protocols rather than ontological
parent states. Keeping that statement in a separate column prevents the conventional tool from dictating the
ARA hierarchy while preserving an accurate crosswalk.

## Naming rules for future tests

1. Every object receives a tier superscript or an explicit tier in prose.
2. `Parent` and `child` are always relative: a Tier-3 child becomes the parent of its Tier-4 children.
3. `J` without a tier is prohibited in new protocols; use \(J^{[1]}\), \(J^{[2]}\), and so on.
4. `Phase A` and `Phase B` name the two sides of an ARA at the tier being measured.
5. `Anti-phase` is reserved for the purer reversal revealed after descending below the current grouped tier.
6. A relation coordinate is not automatically an additional child identity.
7. Measurements from different tiers must not be added or compared until the scale transformation is stated.
8. Removing a parent closure is a section/decompression operation unless a physical intervention was actually
   performed.

## Consequence for the next quantum test

The next test should operate separately but symmetrically inside both Tier-2 parents:

1. freeze \(P_1^{[2]}\) and \(P_2^{[2]}\) from development data;
2. identify the Tier-3 Phase A-side child direction inside each parent;
3. apply the same sectional operation to both parent branches;
4. measure the corresponding Tier-3 Phase B-side directions;
5. test whether the two child relations reconstruct the Tier-1 \(J^{[1]}\) closure;
6. only then descend into candidate Tier-4 grandchildren.

This tests recursive ARA hierarchy rather than treating Tier 1, Tier 2 and Tier 3 as simultaneous peer axes.

## Cross-tier orientation and the Q22 correction

The same child can have two valid coordinates:

- \(x^{[k]}\): its local position inside Tier \(k\);
- \(x^{[k\rightarrow j]}\): its orientation after transport into Tier \(j\)'s frame.

With one singularity flip at each completed rung boundary,

\[
F(x)=2-x,
\qquad
F^m(x)=
\begin{cases}
x,&m\ \text{even},\\
2-x,&m\ \text{odd}.
\end{cases}
\]

Tier 4 to Tier 1 crosses three boundaries, so its Tier-1-facing coordinate is \(2-x^{[4]}\). Q22A omitted this
transform and is retained only as an unflipped control. Q22B froze the corrected transform on a new Willow patch
and failed `12/13` gates; its mean state-plus-travel AUROC was `0.498422`.

This negative result rejects the tested all-children/both-pathways vertical predictor, not the flip algebra.
Both complementary paths can correctly recombine toward the Tier-1 parent ridge, while still carrying no useful
logical-outcome signal in their separately retained child/delay features. The clean next test is therefore one
declared branch-preserving lineage, with its complementary and branch-swapped lineages held as controls.

Normalized `0-2` phase position must remain separate from tier-dependent amplitude capacity. The latter cannot be
inserted as a factor of \(2^{-m}\) unless an amplitude observable has been independently declared and measured.

## Q23 connection-wave/bit parent result

Q23 separately normalized a slow connection-web identity and logical retention, then formed their one-rung-up
parent \(P=2B/(C+B)\). Every genuine parent median was near `1`, but shuffled and misassigned relations also
centred there. The exact identity

\[
P(C,B)+P(B,C)=2
\]

shows why: exchangeable pairings are symmetric around the parent ridge. A specific coupling therefore requires
excess correct-pair ridge concentration relative to relation-broken controls. Q23 did not show that excess and
was **NOT SUPPORTED** (`3/10` gates).

The predeclared anti-child handover decomposition was weakly positive in all four datasets, but its pooled
`p=0.0226` was calculated post-result and cannot rescue the primary. It remains a candidate single-lineage cut,
not an established larger Phase B.
