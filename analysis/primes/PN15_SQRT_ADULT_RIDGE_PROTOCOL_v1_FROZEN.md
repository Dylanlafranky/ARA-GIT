# PN15 full-square-root child closure and adult-rung ridge - frozen protocol

**Test ID:** `PN15/SQRT-CHILD-ADULT-RIDGE/v1`  
**Declared:** 21 July 2026  
**Fidelity packet:** `PN15_SQRT_ADULT_RIDGE_FIDELITY_PACKET_v1.md`  
**Dylan verdict:** `EXACT ENOUGH TO TEST`  
**Status:** frozen before calculating scale-12 square-root gates or results

## Question

At the complete factor boundary, do two child periods near the ARA `1.0` coordinate close an adult near `2.0`, does
that adult grow by factor `10` per decimal rung, and do consecutive adult-growth steps meet at a fresh `1.0/1.0`
ridge? Separately, does the fixed pair's internal signed phase curve transfer to scale 12?

The algebraic closure and the prospective scale/shape checks are reported separately.

## Fixed construction

For `d in {8,9,10,11,12}`, set `N_d=4*10^d`. Select the nine largest prime gates not exceeding `sqrt(N_d)`, in
descending order, and form the eight adjacent ordered pairs `(q_(d,j),r_(d,j))`.

For each pair define

\[
x_{d,j}^{(A)}=\frac{2\log q_{d,j}}{\log N_d},\qquad
x_{d,j}^{(B)}=\frac{2\log r_{d,j}}{\log N_d},
\]

\[
T_{d,j}=q_{d,j}r_{d,j},\qquad
D_{d,j}=\frac{T_{d,j}}{|q_{d,j}-r_{d,j}|}.
\]

Let `J_d` be the median of the eight `T_(d,j)` values and `G_d=J_(d+1)/J_d`. Scales 8-11 are development; scale
12 is the untouched target.

## Arm A - full-boundary child/adult and scale ridge

The fixed adult-growth expectation is

\[
G_*=10^{2(0.5)}=10.
\]

The target growth is `G_11=J_12/J_11`. Its comparison with the preceding development growth `G_10=J_11/J_10` is

\[
R_{10\to11}=\frac{2G_{10}}{G_{10}+G_{11}},\qquad B_{10\to11}=2-R_{10\to11}.
\]

**Frozen primary predictions:**

1. `G_11` lies within 1% of `10`;
2. both target growth-ridge entries lie in `[0.995,1.005]`;
3. the scale-12 median pair has both child coordinates in `[0.995,1.000]` and their sum in `[1.990,2.000]`;
4. the target adult fill `J_12/N_12` is at least `0.999` and below `1`.

All four must pass for Arm A to be `SUPPORTED`. A clean miss is `NOT SUPPORTED`.

**Rivals/disclosure:** report constant adult size, single-child factor `sqrt(10)`, PN14's `10^0.9`, exact factor
`10`, all eight child coordinates/products/gaps, and the asymptotic algebra that makes the target expected. This is a
crosswalk/consistency test, not a parameter-free discovery.

## Arm B - fixed-pair equal-relative-phase transfer

At each scale choose the adjacent pair whose product is closest to `J_d`; break ties by lower pair index. Hold the
pair fixed throughout that scale's phase measurement. This does not claim the pair remains the moving square-root
boundary away from the anchor.

Define

\[
\theta(n)=\left(n\frac{r-q}{qr}\right)\bmod1,
\qquad Z(n)=\left(2\frac{n\bmod q}{q}-1\right)
              \left(2\frac{n\bmod r}{r}-1\right).
\]

Use 16 phase sectors centered at `(k+0.5)/16`. For each sector choose the first forward raw position from `N_d` whose
`theta` is nearest the center, then take a centered block of odd width `2*max(q,r)+1`. Report raw integers, exact
primes and exact composites separately. The development prime template is the unweighted mean of scale 8-11 bin
means and is hash-sealed before scale 12 is opened.

**Frozen target predictions:** scale-12 prime curve:

- correlation at least `0.95` with the development template;
- RMSE at most `0.025` signed-product units;
- at least 60% lower RMSE than zero;
- lower RMSE than the wrong-coordinate control;
- at least 1,000 target primes in every sector.

All five pass for Arm B `SUPPORTED`. Adequate counts with any clean miss give `NOT SUPPORTED`; inadequate counts make
the arm `INCONCLUSIVE`.

## Fixed controls and checks

- **Wrong coordinate:** retain `Z_qr` but assign phase using representative `q` and the ninth square-root gate.
- **Permutation:** fixed seed `15072126` permutes the 16 sector labels.
- **Flat controls:** zero and the development grand mean.
- **Established curve:** raw sawtooth autocorrelation `C(theta)=1/3-2theta+2theta^2`.
- **Population disclosure:** raw, prime and composite curves and counts; no claim that fixed-pair blocks are all at
  their own complete moving factor boundary.
- Every gate must be prime and `<=sqrt(N_d)`; each first omitted gate must be `>sqrt(N_d)`.
- `A+(2-A)=2` closure, `lcm(q,r)=qr`, exact segmented prime counts and fixed sector locations.
- An independent bytearray-sieve validator reconstructs scale 12.
- A full `1009*1013` small-cycle fixture must achieve analytic correlation `>=0.999` and RMSE `<=0.005`.

## Two-output reporting

1. **Claim verdict:** Arm A and Arm B separately against every frozen gate.
2. **Geometry verdict:** child coordinates, adult fill, growth ridge, sector distributions, crests/troughs/crossings,
   raw/prime/composite overlap and every control even if a claim fails.

## Scope fence

PN15 tests the full square-root prime-gate construction. It does not produce primes without division, demonstrate
new number theory, establish that every ARA rung is decimal, or prove that the same relation is universal in physics.

