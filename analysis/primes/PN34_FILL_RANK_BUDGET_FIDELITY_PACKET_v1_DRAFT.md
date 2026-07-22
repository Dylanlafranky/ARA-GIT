# PN34 remaining-fill rank-budget fidelity packet — v1

**Status:** exact test translation approved by Dylan's 22 July 2026 instruction, “Can we try that please.”  
**Development source:** PN26, already opened.  
**Fresh target status at drafting:** no target anchors, candidates, prime labels or outcomes calculated.

## Dylan's geometry being tested

PN26 retained one complete lower, connection-heavy Phase A parent and ranked its first quiet states. PN33 supplied a
way to express accumulated gate density as a local `0–2` fill coordinate. The proposed bridge is:

1. Phase A identifies the possible ridge locations.
2. The omitted Phase B gates describe how much unresolved collision capacity remains.
3. That remaining fill should tell us how many Phase A quiet readings must be retained at the population level.
4. It need not identify which individual quiet reading is the false survivor.

This preserves the same ARA object while changing direction: PN26 supplies the visible quiet-state sequence; PN33's
inverse-density operator measures the unfinished complementary parent.

## Exact mathematical translation

For the PN26 logarithmic split, let `B` be the omitted upper parent. Define

\[
R_B=\prod_{p\in B}\frac{p}{p-1},
\qquad
x_B=2\frac{\log R_B}{\log 2}.
\]

The no-fit first-reading prior is

\[
\pi_1=\frac1{R_B}=2^{-x_B/2}.
\]

If successive Phase A quiet readings are treated as repeated population opportunities, the registered rank budget is

\[
\pi_k=1-(1-\pi_1)^k,
\qquad k\in\{1,2,3\}.
\]

This is a probability/coverage statement. It is not a deterministic label for an individual candidate.

## Development check that motivated freezing

On the already-open 6,000 PN26 anchors, the largest absolute no-fit error was:

- first reading: `0.5632` percentage points;
- first two: `0.1819` percentage points;
- first three: `0.0379` percentage points.

These figures authorize a fresh test but are not themselves prospective evidence.

## Fidelity boundaries

PN34 must not:

- replace `B` with a fitted scalar or hand-selected child;
- use target labels to tune `R_B`, `x_B`, thresholds or rank depth;
- claim that the prior selects the particular rank-1 miss;
- claim constant-time prime generation;
- describe the inverse-density product as new number theory; or
- hide a standard sieve under a three-operation description.

The strongest permissible positive result is a prospective ARA crosswalk: the same remaining-fill coordinate that
describes accumulated gate density also calibrates the visible PN26 rank budget across fresh scales.

