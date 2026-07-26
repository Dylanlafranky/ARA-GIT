# Session record — Q22 vertical tier relation and singularity-flip correction

**Date:** 26 July 2026  
**Participants:** Dylan La Franchi and Codex/Sol

## Thread

After Q21 recovered a near-`1.0` Tier-1 parent from asymmetric children, the next proposed test was the vertical
ARA relation from Tier-4 grandchildren to the Tier-1 whole. Q22A was frozen and run on a fresh Google Willow
patch.

Before Q22A was validated or promoted, Dylan asked whether the singularity flip had been applied. It had not.
The ARA rule already recorded elsewhere is one orientation flip per completed parent/child boundary. Tier 4 to
Tier 1 crosses three boundaries:

\[
x_4\rightarrow2-x_4\rightarrow x_4\rightarrow2-x_4.
\]

Q22A was therefore reclassified as an unflipped control. A new Q22B protocol applied the corrected net transform
\(2-x_4\) and was frozen on the untouched `d5_at_q8_7` patch before its target bits were extracted.

## Result

Q22B was **NOT SUPPORTED**:

- `1/13` frozen gates passed;
- mean flipped state-plus-travel AUROC was `0.498422`;
- mean count AUROC was `0.502176`;
- X/Z permutation p-values were `0.694/0.728`;
- independent validation passed `57/57`.

The flipped future path was also farther from the parent ridge than the past path in both bases, contradicting
the registered descriptive direction before outcomes were opened.

## Interpretive correction

Dylan noted that using the direct children and both complementary pathways may naturally even out at the parent.
That is consistent with the ARA parent-ridge rule: asymmetric children can recombine into a whole near `1.0`.

The distinction is:

- **coarse-grained parent:** both pathways may average toward the ridge, as expected;
- **branch-preserving prediction:** Q22B retained all children and delays separately, and those details still did
  not predict the logical outcome.

Thus the parent-ridge interpretation remains coherent, while this all-paths vertical prediction is rejected.

## Methodological lesson

The flip must be declared before every cross-tier test, including its parity:

\[
F^m(x)=
\begin{cases}
x,&m\ \text{even},\\
2-x,&m\ \text{odd}.
\end{cases}
\]

Local identity coordinates and transported parent-facing orientations must not be conflated. Likewise,
dimensionless phase position and tier-dependent amplitude capacity are separate quantities.

## Next loose thread

Test one frozen directional lineage from Tier 4 to Tier 1, with the complementary lineage and a branch-swapped
path as controls. This keeps the two pathways distinct rather than letting their valid parent-level
recombination hide lineage-specific movement.

Full report:
`analysis/quantum/Q22_Q22B_VERTICAL_TIER_RELATION_REPORT_2026-07-26.md`.
