# PN1G/TRANSFER/v1 — streamed transfer from prime 23 to prime 29

**Declared:** 17 July 2026, before constructing any prime-29 residue, gap, relation, count, figure, or score.  
**Status:** `FROZEN NEXT-RUNG TRANSFER TEST`.  
**Source rung:** prime 23, already opened in PN1F.  
**Target rung:** prime 29, unopened at declaration.  
**Geometry authority:** statistical outputs remain neutrally oriented. Dylan retains authority for Space/Time, Phase A/Phase B, accumulation/release, and ARA direction labels.

## Why this target is being opened

PN1F found a stable residual relation shape across the exact sieve wheels ending at `11, 13, 17, 19, 23`. Its signed deformation became more aligned while its amplitude contracted. PN1F also found a strict ordering of downward representations inside prime 23. Prime 29 is the first untouched rung available for a real transfer check of both observations.

Opening prime 29 changes it from confirmation data into development data for every hypothesis invented after this protocol. The frozen scores below remain auditable even if the target subsequently receives unrestricted ARA geometry-walking.

## Identity and coordinate

The tested identity is the complete circular reduced-residue wheel modulo the primorial ending at prime 29.

For circular gaps `(g_i)`, retain exactly the PN1F coordinate

\[
x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2),
\qquad
Z_i=(x_i,x_{i+1}).
\]

Use the same 12×12 primary relation plane and 24×24 sensitivity plane. The ordinary controls remain:

1. the exact plane projected from the one-gap marginal under Gap-IID;
2. the exact plane projected from the fitted first-order raw-gap transition matrix, Gap-Markov-1.

The residual is

\[
R_{29}=P_{29}^{ordered}-P_{29}^{Gap\text{-}Markov1},
\]

and the unopened deformation is

\[
D_{23\to29}=R_{29}-R_{23}.
\]

No alternative binning, normalization, residual definition, phase orientation, or control may replace these primary definitions after prime 29 is opened.

## Frozen expectations

The expectations are deliberately neutral and few. They were chosen from PN1F before prime 29 was generated.

### U1 — residual-shape inheritance

Primary pass if

\[
\cos(R_{23},R_{29})\ge 0.98.
\]

Report the continuous cosine as the main result. The threshold is a conservative transfer boundary below the opened-rung sequence `0.9892, 0.9951, 0.9967, 0.9981`.

### U2 — continued contraction

Primary pass if

\[
0<\lVert R_{29}\rVert_2<\lVert R_{23}\rVert_2=0.0500418728\ldots
\]

Also report the deformation norm `||D_23→29||_2`. No lower bound on that deformation is imposed beyond nonzero, because PN1F did not justify a quantitative decay law.

### U3 — deformation-direction continuation

Primary pass if

\[
\cos(D_{19\to23},D_{23\to29})\ge0.98.
\]

This tests the direction rather than pretending the unequal prime steps have equal amplitude.

### U4 — low-dimensional parent progression

Append `D_23→29` to the four already-open 12-bin deformation fields and recompute the same uncentred SVD. Primary pass if the leading mode retains at least `95%` of total deformation energy.

The 24-bin version is sensitivity only. It must be reported but cannot rescue a failed 12-bin primary.

### D1 — downward representation ordering

Repeat PN1F's eight guarded contiguous-fold prediction on prime 29 with the identical 12-bin target, Jeffreys smoothing `alpha=0.5`, and representations:

`current_B`, `B_plus_direction`, `B_plus_distance`, `B_plus_signed_step`, `full_A_B`, `raw_gap_markov1`, and `B_plus_shared_gap`.

The frozen predicted ordering from lowest to highest cross-entropy is:

\[
B+shared\ gap
<raw\ gap\ Markov1
<full(A,B)
<B+signed\ step
<B+distance
<B+direction
<current\ B.
\]

Grade both the exact ordering and Kendall rank agreement. Every non-base representation must also preserve a positive gain over `current_B` in every fold. Complexity statistics travel with each score; this ordering is not a claim that ARA compression beats the ordinary raw-gap controls.

## Additional recorded measurements — not extra primary predictions

- exact period, slot count, gap sum, gap alphabet, gap SHA-256, and all-gaps-positive/even checks;
- 12-bin and 24-bin ordered, Gap-IID, Gap-Markov-1, residual, and deformation matrices;
- ordered-plane JSD, residual cosine, deformation cosine, turn angle, and mode scores;
- child rising/equal/falling shares and exact circular mean signed step;
- all eight downward fold scores, active contexts, conditional degrees of freedom, perplexity, top-1 accuracy, and Brier score;
- any post-open observation, clearly labelled `POST-OPEN DEVELOPMENT`.

## Streaming implementation and calibration

The prime-29 wheel contains `1,021,870,080` surviving slots. It must be generated as an ordered stream of lifted prime-23 residues, excluding multiples of 29, without materializing the target residue or gap cycle.

Before the target stream is allowed to count prime 29, the same streaming code must replay the already-open `19→23` construction and reproduce, exactly:

- prime-23 period `223,092,870`;
- slot count `36,495,360`;
- total gap sum equal to the period;
- gap SHA-256 `F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C` using the saved int32 gap representation;
- PN1F 12-bin and 24-bin ordered planes and raw-gap transition inventory.

Failure of this calibration blocks target interpretation until the implementation is corrected. It does not count as a prime-29 result.

## Independent validation

An independently coded validator must check:

- the frozen protocol hash;
- source prime-23 arrays against PN1F;
- expected prime-29 totient and primorial arithmetic;
- normalization, zero-sum residuals, nonnegative counts, circular closure and fold totals;
- recomputation of U1–U4 and D1 from saved counts/matrices rather than trusting the headline JSON;
- notebook execution and final figure dimensions.

## Interpretation fence

A successful transfer would show that the neutral cross-rung relation geometry and the downward child-information ordering survive one untouched sieve rung. It would not prove a physical wave, a completed cycle, the Riemann hypothesis, prime predictability, or universal ARA geometry. A failure is retained and investigated; it is not erased by a post-open redefinition.

**Dylan instruction authorizing opening:** “OKay good. Lets continue with the testing then.” This followed the explicit choice to freeze a small neutral prime-29 registration and then geometry-walk the opened target.
