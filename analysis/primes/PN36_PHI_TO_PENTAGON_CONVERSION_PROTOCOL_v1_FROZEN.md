# PN36 Phi-carrier to pentagonal-structure conversion protocol - v1 FROZEN

**Test ID:** `PN36/PHI-TO-PENTAGON-CONVERSION/v1`  
**Declared:** 22 July 2026, before target cells, candidate labels or outcomes are calculated  
**Fidelity:** `PN36_PHI_TO_PENTAGON_CONVERSION_FIDELITY_PACKET_v1_DRAFT.md`

## Question

Does a predeclared five-sector quantisation of the continuous Phi carrier locate prime incidence more strongly than
chance, raw Phi, direct pentagonal motion, 36-degree motion and matched non-fivefold quantisations?

## Frozen geometry

Use the eight modulo-30 structural lanes

\[
\mathcal R=\{1,7,11,13,17,19,23,29\},\qquad x(r)=r/30
\]

on a unit-turn circle (equivalently `2x` on the ARA `0-2` circumference). For a complete wheel cell beginning at a
multiple `c` of 30 in octave rung `[2^k,2^(k+1))`, define

\[
t=(c-2^k)/30,\qquad \sigma_k=(-1)^k,\qquad
\theta_\phi=(\sigma_k t/\phi^2)\bmod1.
\]

The frozen conversion operator is nearest-vertex fivefold quantisation

\[
C_5(\theta)=\frac{\lfloor5\theta+1/2\rfloor\bmod5}{5}.
\]

The converted crossings are `C5(theta_phi)` and `C5(theta_phi)+1/2 mod 1`. Candidate score is negative circular
distance from `x(r)` to the nearer crossing. Ties are ordered by residue. No primality operation is allowed in the
primary builder.

The distance from the carrier to its nearest fivefold sector boundary is stored as a descriptive conversion-state
diagnostic. It is not a registered support gate.

## Fresh target rungs

| Pair | Lower rung | Upper rung | Approximate scale | Seed |
|---:|---:|---:|---:|---:|
| 1 | `k=28` | `k=29` | `2.7e8 -> 1.1e9` | `36001` |
| 2 | `k=38` | `k=39` | `2.7e11 -> 1.1e12` | `36002` |
| 3 | `k=48` | `k=49` | `2.8e14 -> 1.1e15` | `36003` |

Sample `4,096` complete global modulo-30 cells without replacement in each rung using the fixed pair seed plus rung
index. Retain all eight candidates per cell: `196,608` sealed rows across `24,576` cells.

## Frozen rivals and controls

All models use the same candidates, orientation and scoring rule.

1. raw continuous Phi carrier;
2. direct pentagon rotation (`1/5` turn per cell);
3. direct 36-degree/half-pentagon rotation (`1/10` turn per cell);
4. the same Phi carrier quantised by `C_m` for `m={3,4,6,7,8}`;
5. converted `C_5` without octave orientation flips; and
6. `256` fixed within-rung circular shifts of the complete converted score profile.

The matched `C_m` controls distinguish fivefold structure from the generic act of quantising a continuous carrier.

## Metrics and uncertainty

1. Lane-stratified Mann-Whitney AUC for prime versus composite ordering.
2. Fraction of primes in the converted model's two nearest lanes per cell; structural null `2/8=25%`.
3. Six rung, three adjacent-pair and two fixed-half transfers.
4. `1,000` rung-stratified whole-cell bootstrap replicates.
5. `256` within-rung circular shifts and exact plus-one p-values.
6. Converted-distance octiles, all rival AUCs, and a descriptive sector-boundary/prime-count association.
7. Deterministic 64-bit Miller-Rabin labels, independent trial-division spots and planted/null instrument checks.

## Registered endpoints

All five gates are required for `SUPPORTED`:

- **G1 - converted preference:** `C5(Phi)` AUC is above `0.5`, its 95% whole-cell interval is wholly above `0.5`,
  and circular-shift `p <= 0.01`.
- **G2 - scale transfer:** all three adjacent-rung pairs exceed `0.5`, at least five of six rungs exceed `0.5`, and
  both fixed halves exceed `0.5`.
- **G3 - conversion specificity:** `C5(Phi)` exceeds raw Phi, direct pentagon, direct 36 degrees and every matched
  non-fivefold `C_m`; the 95% interval for `C5(Phi) - best frozen rival` is wholly above zero.
- **G4 - singularity flip:** converted `C5(Phi)` exceeds its no-flip version, the 95% difference interval is wholly
  above zero, and it wins in at least two of three adjacent-rung pairs.
- **G5 - crossing capture:** nearest-two capture exceeds `25%`, its 95% interval is wholly above `25%`, shift
  `p <= 0.01`, and all three rung pairs exceed `25%`.

`SUGGESTIVE` requires G1 plus G2 but failure of a later specificity/flip/capture gate. Adequate data with G1 failed
is `NOT SUPPORTED`. Freeze, reconstruction, arithmetic or instrument failure is `INCONCLUSIVE / IMPLEMENTATION
FAILURE`.

## Two-output rule

Report separately:

1. the registered predictive verdict for this exact conversion operator; and
2. the descriptive geometry, including whether the Phi carrier actually changes fivefold state as designed and
   whether any boundary pattern exists.

Known pentagon/Phi geometry and exact structural closure cannot rescue a failed predictive endpoint.

## Reproducibility order

1. Register this claim in the master ledger.
2. Freeze this fidelity/protocol pair plus the primary and validator code by SHA-256.
3. Run the label-free primary and hash its output.
4. Only then open primality in the validator.
5. Preserve scripts, manifest, candidates, scored rows, results, notebook, figure, report and validation receipts.

