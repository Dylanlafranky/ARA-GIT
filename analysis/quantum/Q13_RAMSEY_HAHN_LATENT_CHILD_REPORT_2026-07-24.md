# Q13 Ramsey/Hahn latent-child report

**Date:** 24 July 2026  
**Ledger:** T272  
**Status:** **PARTIAL / NOT CALIBRATED — 6/10 frozen gates passed**  
**Protocol:** `Q13_RAMSEY_HAHN_LATENT_CHILD_PROTOCOL_v1_FROZEN.md`  
**Protocol SHA-256:** `17b6a9bb93e845842e12289d98eda6390b9881be15ce6f996bd8a5b8e6588021`

> **Sphere-first/quadrant re-evaluation, corrected 24 July 2026:** Ramsey and Hahn are two valid
> protocol-conditioned ARA parent paths, each decompressed into an A/B pair. Therefore
> \(R_A,R_B,H_A,H_B\) are four legitimate ARA coordinate children of the larger comparison, although they are not
> four independent laboratory subsystems. Their amplitudes correlate strongly with ordinal stage
> (`|median r|=0.909–0.968`). In the same held-out identities, a
> two-parameter linear ordinal-stage model removed median amplitude covariance `0.980694`, exceeding selected
> \(H_B\)'s `0.916136` without using a revealed candidate child in the held-out rows. The common amplitude
> progression remains real; this rejects only the unique one-child-generates-three interpretation, not the
> two-parent/four-child quadrant. Ideal common-interval Ramsey/Hahn sensitivity functions are an exact orthogonal
> sum/difference pair, which Q13's unequal-time one-latent test did not test. Frozen gates are unchanged. See
> `Q13_Q14_RAMSEY_HAHN_QUADRANT_REAUDIT_2026-07-24.md`.

## Plain-language result

Dylan proposed that Ramsey and Hahn can be treated as two parent views, each decompressed into a visible child
and an unresolved/purity child:

\[
\underbrace{R_A}_{\substack{\text{Ramsey}\\\text{visible child}}},
\quad
\underbrace{R_B}_{\substack{\text{Ramsey}\\\text{unresolved child}}},
\quad
\underbrace{H_A}_{\substack{\text{Hahn}\\\text{visible child}}},
\quad
\underbrace{H_B}_{\substack{\text{Hahn}\\\text{unresolved child}}}.
\]

Q13 asked a precise version of “one hidden child becomes three relations”: if one child is supplied as a latent
coordinate, can it remove the shared relation among the other three on a Bell identity excluded from fitting?

The answer splits cleanly:

- **Yes for amplitude/magnitude.** The selected child removed a median `91.61%` of the relation among the other
  three amplitude paths. The best of `999` selection-corrected within-state shuffles did not reproduce it:
  `p=0.001`.
- **No clear confirmation for direction.** It removed only `12.64%` of directional relation, below the frozen
  `25%` threshold and compatible with the shuffled control: `p=0.336`.
- **No unique hidden-child identity was established.** The unresolved Hahn child \(H_B\) had the highest combined
  score, but by only `0.00187` over the visible Ramsey child \(R_A\). \(H_B\) won only `2/4` held-out Bell
  identities.

So the earlier visual impression was real in one important sense: all four children share a strong aligned
amplitude path, and revealing one can account for most of the amplitude relation among the other three. The data
do **not** yet show that one particular hidden Phase B is the unique source of those three relations, or that its
directional handoff has been recovered.

## Frozen question

For every Bell identity and matched wait index, Q13 constructed:

\[
\begin{aligned}
R_A&=C_{V,\mathrm{Ramsey}},&
R_B&=C_{P,\mathrm{Ramsey}},\\
H_A&=C_{V,\mathrm{Hahn}},&
H_B&=C_{P,\mathrm{Hahn}}.
\end{aligned}
\]

Here \(V=K+R\) is the compact visible relation from Q11, \(P=2(1-\operatorname{Tr}\rho^2)\) is independently
defined purity loss, and each local relation plane is:

\[
\underbrace{C_Z}_{\substack{\text{two-cut}\\\text{child identity}}}
=
\underbrace{(x_Z-1)}_{\substack{\text{local amplitude}\\\text{ARA cut}}}
+
i\underbrace{(y_Z-1)}_{\substack{\text{opening/closing}\\\text{direction cut}}}.
\]

Amplitude and direction were tested separately. Equal **ordinal indices** were paired. Ramsey covers
`0.02–40.02 us`, while Hahn covers `1–1000 us`; Q13 therefore did not claim equal clock times.

## Held-out test

Each child was tested in turn as the proposed latent coordinate \(h\). One entire Bell identity was withheld.
The other three identities (`33` rows) fitted:

\[
\underbrace{v_j}_{\text{one visible child}}
=
\underbrace{\alpha_j}_{\text{offset}}
+
\underbrace{\beta_j h}_{\substack{\text{relation carried}\\\text{by candidate }h}}.
\]

The coefficients were then applied to the withheld identity (`11` rows). With \(S\) the covariance of its three
remaining children and \(S_r\) their covariance after conditioning on \(h\), the frozen score was:

\[
\underbrace{\Delta}_{\substack{\text{visible relation}\\\text{removed by }h}}
=
1-
\frac{
\underbrace{\sum_{i<j}(S_r)_{ij}^{\,2}}_{\text{remaining off-diagonal relation}}
}{
\underbrace{\sum_{i<j}S_{ij}^{\,2}}_{\text{original off-diagonal relation}}
}.
\]

This is a latent-factor/partial-covariance test. It is not ordinary reconstruction of one child from the other
three, because the candidate child is deliberately revealed in the held-out rows.

## Candidate results

| Candidate | ARA label | Amplitude reduction | Direction reduction | Composite |
|---|---|---:|---:|---:|
| \(R_A\) | Ramsey visible A | **0.927677** | 0.111097 | 0.519387 |
| \(R_B\) | Ramsey unresolved B | 0.864695 | 0.067473 | 0.466084 |
| \(H_A\) | Hahn visible A | 0.916898 | 0.115331 | 0.516115 |
| \(H_B\) | Hahn unresolved B | 0.916136 | **0.126382** | **0.521259** |

The candidate scores are too close to interpret the winning label strongly. \(R_A\) actually gives the greatest
amplitude reduction, while \(H_B\) wins the predeclared average because its direction score is slightly higher.

The per-identity composite winners were:

| Held-out Bell identity | Winning child |
|---|---|
| \(\Phi^+\) | \(H_B\) |
| \(\Phi^-\) | \(R_B\) |
| \(\Psi^+\) | \(H_B\) |
| \(\Psi^-\) | \(R_A\) |

Phase-B-labelled candidates therefore win `3/4` identities as a class, but no single child wins the required
`3/4`. This is suggestive, not a frozen success.

## Rank-one geometry

If one latent scalar drives three children linearly, the covariance it induces has the outer-product form:

\[
\underbrace{I}_{\substack{\text{relation induced}\\\text{among three children}}}
=
\underbrace{\boldsymbol\beta\boldsymbol\beta^{\mathsf T}}_{\substack{\text{one latent path}\\\text{projected three ways}}}
\underbrace{\operatorname{Var}(h)}_{\text{latent variation}}.
\]

For selected \(H_B\), the removed covariance had median leading-mode energy shares:

- amplitude: `0.999986`;
- direction: `0.982804`.

This shape is close to rank one. However, the fitted matrix \(I\) is rank one by construction. The empirical
content is whether the held-out removed covariance has the same shape and signs. Amplitude sign agreement was
`1.0`; direction sign agreement was only `0.333333`, failing the frozen `2/3` gate.

## Selection-corrected null

Within each Bell identity, the candidate trajectory was permuted over its eleven wait indices. This preserves
its values but breaks its alignment with the other three children. The complete four-candidate selection was
repeated for each of `999` deterministic permutations.

| Score | Observed | Null reference | Add-one p |
|---|---:|---:|---:|
| Amplitude reduction | 0.916136 | 99th percentile 0.443442 | **0.001** |
| Direction reduction | 0.126382 | 95th percentile 0.304421 | 0.336 |
| Composite | 0.521259 | 95th percentile 0.191801 | **0.001** |

The significant composite is driven mainly by amplitude. It must not be reported as independent confirmation
of both axes.

## Frozen gates

| Gate | Result |
|---|---|
| L1 — 44 complete four-child cells | PASS |
| L2 — 33 train / 11 held-out rows | PASS |
| L3 — selected candidate is Phase B | PASS: \(H_B\) |
| L4 — amplitude reduction at least 0.60 | PASS: 0.916136 |
| L5 — direction reduction at least 0.25 | **FAIL: 0.126382** |
| L6 — selection-corrected amplitude \(p\leq0.01\) | PASS: 0.001 |
| L7 — selection-corrected direction \(p\leq0.05\) | **FAIL: 0.336** |
| L8 — rank-one share at least 0.70 on both axes | PASS |
| L9 — sign agreement at least \(2/3\) on both axes | **FAIL: direction 1/3** |
| L10 — one candidate wins at least 3/4 identities | **FAIL: 2/4** |

## What this means for the ARA statement

The supported statement is:

> Across matched Ramsey/Hahn stages in this public Bell dataset, the four decompressed child coordinates share a
> strong, approximately one-dimensional amplitude relation. A supplied child can remove most of the other
> three's held-out amplitude covariance.

The unsupported stronger statement is:

> The test has identified one physical hidden Phase-B child that causally hands off between Ramsey and Hahn and
> generates three independently observed descendants.

The latter would require at least one of:

1. a pulse-resolved experiment where Ramsey and Hahn channels are observed on a common clock;
2. an external physical channel measurement not calculated from the same density matrices;
3. a forward test that hides the candidate itself and predicts its amplitude **and** direction;
4. a new dataset on which \(H_B\), frozen in advance, clearly defeats the other three candidates.

## Q14 follow-up: equal-depth parity

Q14 subsequently tested whether the Ramsey and Hahn child sets corresponded only after an additional A/B swap.
That crossed pairing was strongly worse than same-label pairing. The parity audit then clarified that both Q13
pairs are proposed **child sets at the same depth**. Dylan subsequently clarified that the swap occurs only
after a full scale-level TE-ARA completes and crosses a rung boundary—not at every child relation. Equal-depth
or nearby-rung sets therefore predict retained phase labels; any equal boundary parity cancels as
\(S^{\mathsf T}S=I\). Q14 rejected an unmatched extra swap between the two Q13 sets; it did not test an
odd completed-rung transition. See
`Q14_CHILD_PHASE_SWAP_REPORT_2026-07-24.md`.

## Data-quality and evidence boundaries

- The source contains all expected `88` Q11 records and all `44` matched four-child cells; values are finite.
- Bell identities are held out intact, so rows from the test identity do not enter coefficient fitting.
- All four children remain transforms of the same underlying reconstructed density matrices. They are not four
  independent sensors or four independently perturbed physical subsystems.
- The local normalization compares waveform shape rather than absolute physical magnitude.
- Eleven points per held-out identity make covariance and directional estimates noisy.
- Q11/Q12 outcomes were already open. Q13 is a frozen post-outcome structural test, not a blind discovery or
  forward prediction.
- Independent source-to-result code reproduced candidate selection, every candidate summary, fold winner and all
  `999`-permutation statistics exactly.

## Reproduction files

- `q13_ramsey_hahn_latent_child_test.py` — frozen primary runner
- `q13_ramsey_hahn_latent_child_validate.py` — independent source-to-result validator
- `Q13_RAMSEY_HAHN_FOUR_CHILDREN.csv` — 44 constructed cells
- `Q13_RAMSEY_HAHN_LATENT_FOLDS.csv` — held-out diagnostics
- `Q13_RAMSEY_HAHN_LATENT_CANDIDATES.csv` — candidate comparison
- `Q13_RAMSEY_HAHN_LATENT_GATES.csv` — frozen gates
- `Q13_RAMSEY_HAHN_LATENT_RESULTS.json` — machine-readable result
- `Q13_RAMSEY_HAHN_LATENT_VALIDATION.json` — independent validation
- `Q13_RAMSEY_HAHN_NULL_SUMMARY.json` — selection-corrected null
- `Q13_RAMSEY_HAHN_LATENT_GEOMETRY.svg` / `.png` — result figure
