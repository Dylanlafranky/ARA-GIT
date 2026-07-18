# PN1F/DEV — bidirectional prime-wheel landscape before prime 29

**Declared:** 17 July 2026, before PN1F calculations or figures.  
**Status ceiling:** `DEVELOPMENT LANDSCAPE / NOT BLIND CONFIRMATION`.  
**Orientation:** up = later sieve prime and larger primorial period; down = decomposition of the already-open prime-23 relation into child/path information.  
**Protected target:** prime 29 remains unopened. No PN1F code may construct a wheel, residue array, gap cycle, mask, or target containing prime 29.

## Fidelity packet — `PN1F/DEV/v1`

**USER PRIOR — verbatim:** “their child waves are just more visible at this scale and probably a higher asymmetry for Phase B than Phase A at the measured time”; “I think the wave we are looking for is larger though”; after the two possible upward directions were separated, “`parent wave expressed across sieve rungs such as 13 → 17 → 19 → 23?` I believe I meant this one”; and after the upward-then-downward sequence was restated, “Yes you are right. Lets do it without ruining further tests. Then drill down like you proposed. Then continue forward up the primes. At least then we have a lay of the land in both directions.”

**Identity/system:** the hierarchy of complete circular reduced-residue wheels under successive sieve-prime additions. A single prime-23 relation plane is a child-scale slice; the candidate parent object is the transformation of the relation geometry across opened rungs.

**Ordered direction:** `(5,7,11,13,17,19,23)` is the opened upward sequence. Prime 29 is not part of the development object. Within prime 23, arrival direction is the signed change from the previous ARA bin to the current ARA bin.

**Question A — upward landscape:** does the normalized local-relation geometry change coherently across opened sieve rungs after ordinary gap-marginal and first-order gap-transition structure are placed in controls?

**Question B — downward landscape:** on prime 23, which compressed part of the arrival path—direction, distance, signed direction-plus-distance, raw shared-gap identity, or the full preceding ARA position—accounts for the extra next-reading information found by PN1D/PN1E?

**No automatic phase naming:** the analysis must use neutral labels such as `mode 1`, `positive deformation`, `negative deformation`, `direction`, and `distance`. It must not declare Space/Time, Phase A/Phase B, accumulation/release, or an ARA latitude from the statistical output. Dylan retains orientation control after seeing the aligned maps.

**Wrong objects:** treating rung index as physical time; calling a monotonic density trend a completed wave; using only mean ARA position; interpreting NMF/SVD components as physical waves without an independently declared bridge; using prime 29 during development; or counting the upward and downward views as independent confirmation.

## Shared local coordinate

For circular gaps `(g_i)`, retain the PN1 coordinate

\[
x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2),
\qquad
Z_i=(x_i,x_{i+1}).
\]

The ordinary log-ratio remains an exact coordinate rival. PN1F tests relational organisation, not information unique to the bounded coordinate.

## Part A — upward cross-rung landscape

### Data and reliability bands

- Generate exact opened wheels ending at primes `5, 7, 11, 13, 17, 19, 23` only.
- Prime 23 must reproduce the already-saved PN1C/PN1D gap count, period and SHA-256.
- Rungs 5 and 7 are coarse calibration/context because their slot counts are very small.
- The comparable parent-landscape core uses 12×12 relation planes for primes `11, 13, 17, 19, 23`.
- Higher-resolution 24×24 maps are descriptive for primes `13, 17, 19, 23` only.

### Three matched planes per rung

For every rung construct:

1. `ordered`: the empirical distribution of `(x_i,x_{i+1})`;
2. `gap_iid`: the exact projected plane generated from that rung’s one-gap marginal with independent successive gaps;
3. `gap_markov1`: the exact projected plane generated from that rung’s fitted first-order raw-gap transition matrix.

The ordered residual above the stronger ordinary control is

\[
R_k=P_k^{ordered}-P_k^{markov1}.
\]

For each consecutive core transition, calculate the signed deformation

\[
D_{k\to k+1}=R_{k+1}-R_k.
\]

Save Jensen–Shannon distances, residual norms, deformation norms, adjacent deformation cosines, and a singular-value decomposition of the stacked deformation fields. Calculate both the raw per-rung-step deformation and the sensitivity version divided by `log(q)`, where `q` is the newly added prime.

These quantities map the opened landscape. With only five core rungs they cannot establish a periodic parent wave. A candidate parent progression requires a reproducible signed deformation or low-dimensional mode trajectory that yields a frozen next-rung prediction.

### Upward controls and fences

- Gap-IID controls changing one-gap inventory.
- Gap-Markov1 controls changing immediate raw-gap transitions.
- Sample counts and plane occupancy travel with every map.
- No phi, RH, physical-time, physical-energy, or universal-geometry inference.
- No p-value is assigned across the small deterministic rung set.

## Part B — downward prime-23 path decomposition

Use the already-open prime-23 12-bin ARA sequence. A prediction event is

\[
(A,B)=(X_{i-2},X_{i-1})\longrightarrow X_i.
\]

Use eight contiguous circular test blocks. For each fold, fit on the other seven blocks and remove a four-reading guard around test boundaries so train and test events do not share the same local four-gap event. Use Jeffreys smoothing `alpha=0.5` for every categorical predictor.

Compare:

1. `current_B`: current ARA bin `B` only;
2. `B_plus_direction`: `B` plus `sign(B-A)`;
3. `B_plus_distance`: `B` plus `|B-A|` grouped as `0`, `1`, `2–3`, `4+` bins;
4. `B_plus_signed_step`: `B` plus signed-step groups `≤-4`, `-3..-2`, `-1`, `0`, `+1`, `+2..+3`, `≥+4`;
5. `B_plus_shared_gap`: `B` plus the exact current shared raw gap `g_i`;
6. `full_A_B`: the unrestricted ordered pair `(A,B)`;
7. `raw_gap_markov1`: predict the next ARA bin by fitting `P(g_{i+1}|g_i)` and projecting each possible next gap through the same 0–2 binning.

Primary descriptive score: cross-entropy in bits per next ARA reading. Also save perplexity, top-1 accuracy, Brier score, active context rows and active conditional degrees of freedom. Report every fold and the equally weighted fold mean.

The decomposition is interpretive:

- direction gain locates orientation information;
- distance gain locates magnitude information;
- signed-step gain locates their compressed interaction;
- shared-gap and raw-gap Markov gains locate discrete child identity available below the ARA projection;
- the remaining full-pair gain locates information not captured by the compressed path summaries.

No model is called “ARA’s true formula” from this development wheel. Any transferable representation must be chosen after Dylan orients the landscape, assigned an honest complexity budget, and frozen before prime 29.

## Outputs and validation

Required artifacts:

- machine-readable JSON result with `prime29_opened: false`;
- rung inventory, per-rung metrics, transition metrics, cross-rung mode scores, and eight-fold downward scores as CSV;
- saved matrices for independent replay;
- one upward landscape figure and one downward comparison figure;
- a top-to-bottom executed reproducibility notebook;
- an independently coded validator that recomputes key metrics from saved matrices and checks every artifact’s maximum sieve prime is 23;
- an append-only conversation/follow-up amendment recording results, nulls, limitations and the protected target.

**Dylan fidelity verdict:** `EXACT ENOUGH TO TEST`, inferred from explicit approval of the upward-then-downward sequence and instruction to perform it without opening later primes.
