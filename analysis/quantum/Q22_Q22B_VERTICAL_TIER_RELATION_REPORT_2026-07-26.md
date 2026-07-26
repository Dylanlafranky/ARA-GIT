# Q22/Q22B vertical Tier-4 to Tier-1 relation report

**Date:** 26 July 2026  
**Source:** Google Willow surface-code records, Zenodo DOI `10.5281/zenodo.13273331`  
**Status:** Q22A method-corrected control; Q22B **NOT SUPPORTED** (`1/13` frozen gates)

## Question

Q21 showed that asymmetric lower-tier children can recompress to a Tier-1 parent near the ARA `1.0` ridge.
Q22 asked whether the direct vertical relation between Tier-4 grandchildren and that Tier-1 whole also transports
logical-outcome information across detector patches and cycle durations.

In ARA language, the first construction compared:

\[
J^{[1]}\longleftrightarrow x^{[4]}.
\]

Dylan caught before validation or ledger promotion that this omitted the declared singularity flip at every
completed rung crossing. Tier 4 to Tier 1 crosses three boundaries, so the faithful Tier-1-facing coordinate is:

\[
x^{[4\rightarrow1]}
=F^3(x^{[4]})
=2-x^{[4]},
\qquad F(x)=2-x.
\]

Q22A is therefore retained only as the unflipped control. Q22B froze and tested the corrected odd-parity
orientation on a new untouched detector patch.

## Important distinction: local identity versus transported orientation

The Tier-4 child remains \(x^{[4]}\) in its own local frame. Only its orientation relative to Tier 1 is flipped.
The normalized `0-2` phase coordinate was not divided by eight: the separate rule that energy/amplitude capacity
halves per downward rung is not the same observable as phase position.

## Data separation

| Run | Patch | Development | Holdout | Target status at freeze |
|---|---|---:|---:|---|
| Q22A | `d5_at_q6_9` | 13 cycles | 30 cycles | absent |
| Q22B | `d5_at_q8_7` | 13 cycles | 30 cycles | absent |

X and Z logical outcomes were scored separately. Geometry, feature definitions, controls, thresholds and model
fitting rules were frozen before the corresponding holdout outcome files were extracted.

## Q22A: unflipped control

The unflipped representation gave the expected descriptive ordering: its forward child-to-parent distance was
smaller than past and broken-path controls in both bases. It did not predict logical outcomes:

- vertical state AUROC: `0.504319 / 0.503626` for X/Z;
- vertical travel AUROC: `0.501243 / 0.502874`;
- combined vertical AUROC: `0.502156 / 0.503120`;
- count AUROC: `0.505958 / 0.506933`;
- permutation p-values: `0.120 / 0.054`;
- frozen gates: `4/12`.

This cannot be promoted as the intended ARA test because it omitted the pre-existing odd-boundary flip.

## Q22B: corrected flip

Q22B used:

\[
J^{[1]}\longleftrightarrow\left(2-x^{[4]}\right)
\]

on the untouched `d5_at_q8_7` patch. Before outcomes were opened, the descriptive directional gate already failed:
the flipped future path was farther from the Tier-1 ridge than the past path in both bases.

| Model | X AUROC | Z AUROC | Mean |
|---|---:|---:|---:|
| Flipped vertical state | 0.498573 | 0.502180 | 0.500377 |
| Flipped vertical travel | 0.498591 | 0.497307 | 0.497949 |
| Flipped state + travel | 0.498755 | 0.498090 | 0.498422 |
| Unflipped control | 0.498531 | 0.499889 | 0.499210 |
| Q21 child topology | 0.502834 | 0.501870 | 0.502352 |
| Event fraction | 0.500544 | 0.503807 | 0.502176 |

Flipped-model permutation p-values were `0.694 / 0.728`. Only the count non-inferiority gate passed, giving
`1/13` frozen gates. Independent validation passed `57/57` checks.

## What the result says in ARA

Using all four direct children and both complementary pathways can legitimately recompress toward a Tier-1
`1.0` parent ridge. That averaging is not itself a failure: it is the expected whole-from-children result.

However, Q22B did more than average a single directional number. The frozen predictive model retained every
child and delay as separate inputs. Those branch-preserving details still carried no transported logical signal.
Therefore “the whole evens out” explains the parent-ridge summary, but does not rescue this particular predictive
formulation.

## Honest verdict

Q22B rejects the specific claim that the net three-boundary transform \(2-x^{[4]}\), applied to all retained
children and both direct pathways in this representation, supplies useful cross-patch logical-outcome prediction.
It does **not** falsify:

- the algebraic flip rule \(F^2=I\);
- parent-ridge coarse-graining;
- a single branch-preserving lineage rule;
- absolute amplitude transfer between tiers;
- the wider ARA framework.

The observed switch from “future closer” in Q22A to “future farther” in Q22B is partly a mathematical consequence
of mirroring a near-ridge coordinate. It is not evidence by itself that information physically travels backward.

## Clean next discrimination

Freeze one declared lineage through the rung handovers rather than pooling both complementary routes:

1. choose one Tier-4 child and its orientation without outcomes;
2. transport it boundary by boundary with the declared flips;
3. keep the complementary lineage as a separate control;
4. compare branch-preserving, branch-swapped and broken paths;
5. keep normalized phase position separate from measured amplitude capacity;
6. validate on a fresh patch or independent public dataset.

That test directly distinguishes “both pathways recombine at the parent ridge” from “one directional lineage
transports identifiable information upward.”

## Reproduction

The frozen protocols, manifests, results and independent validations are:

- `Q22_WILLOW_VERTICAL_TIER4_TIER1_PROTOCOL_v1_FROZEN.md`
- `Q22_WILLOW_VERTICAL_TIER4_TIER1_FREEZE_MANIFEST.json`
- `Q22_WILLOW_VERTICAL_TIER4_TIER1_RESULTS.json`
- `Q22_WILLOW_VERTICAL_TIER4_TIER1_VALIDATION.json`
- `Q22B_WILLOW_FLIP_VERTICAL_PROTOCOL_v1_FROZEN.md`
- `Q22B_WILLOW_FLIP_VERTICAL_FREEZE_MANIFEST.json`
- `Q22B_WILLOW_FLIP_VERTICAL_RESULTS.json`
- `Q22B_WILLOW_FLIP_VERTICAL_VALIDATION.json`

Q22B protocol SHA-256:
`625689063971a2c56a568f1a58610915e1792e3d0721305408ffff3452334725`.
