# PN14 child-to-adult wave and adult-rung ridge - frozen protocol

**Test ID:** `PN14/CHILD-ADULT-RIDGE/v1`  
**Declared:** 21 July 2026  
**Fidelity packet:** `PN14_ADULT_WAVE_RIDGE_FIDELITY_PACKET_v1.md`  
**Dylan verdict:** `EXACT ENOUGH TO TEST`  
**Status:** frozen before calculating the scale-11 target

## Question

Do the two paid-gate child cycles generate a scale-stable adult wave whose consecutive growth steps meet near the
ARA `1.0` ridge, and does equal relative-phase coverage align the adult wave's internal signed-coupling shape across
scales?

The scale ridge and phase-shape collapse are rated separately. The exact identity `lcm(q,r)=qr` is an arithmetic
crosswalk, not a prediction.

## Fixed construction

At each decimal scale `d in {8,9,10,11}`, set `N_d=4*10^d` and select the nine largest prime gates
`q_(d,j) <= N_d^0.45`, descending. The eight adjacent ordered pairs use the same order at every scale.

For pair `j`,

\[
T_{d,j}=q_{d,j}q_{d,j+1},\qquad
D_{d,j}=\frac{T_{d,j}}{|q_{d,j}-q_{d,j+1}|}.
\]

Define `J_d` as the median of the eight exact joint periods. Define adult scale growth `G_d=J_(d+1)/J_d`.

Scales 8-10 are open development data from PN13. Scale 11 is the untouched target.

## Arm A - adult scale-ridge prediction

The fixed exponent rival/expectation is

\[
G_*=10^{2(0.45)}=10^{0.9}=7.943282347\ldots.
\]

The target growth is `G_10=J_11/J_10`. Compare it with the preceding open growth `G_9=J_10/J_9` through

\[
R_{9\to10}=\frac{2G_9}{G_9+G_{10}},\qquad B_{9\to10}=2-R_{9\to10}.
\]

**Frozen prediction:**

1. `G_10` is within 5% of `G_*`;
2. the target two-entry adult-growth reading lies within `0.98 <= R <= 1.02` (and therefore the complement does too).

Both must pass for Arm A to be `SUPPORTED`. A clean miss is `NOT SUPPORTED`.

**Rivals/disclosure:** report a constant joint period, linear child-only scaling `10^0.45`, full square-root scaling
`10^1`, all eight pair periods/gaps, and the asymptotic algebra that makes `10^0.9` expected. Arm A is a stringent
consistency check of the ARA reading, not a parameter-free discovery.

## Arm B - equal-relative-phase shape collapse

At each scale choose the adjacent pair whose `T_(d,j)` is closest to `J_d`; break ties by the lower pair index. Hold
that pair fixed throughout the scale's measurement.

Define

\[
\theta(n)=\left(n\frac{r-q}{qr}\right)\bmod1,
\qquad A_q(n)=2\frac{n\bmod q}{q},
\qquad A_r(n)=2\frac{n\bmod r}{r},
\qquad Z(n)=(A_q-1)(A_r-1).
\]

Use 16 target phase sectors with centers `(k+0.5)/16`. For each sector, choose the first forward raw position from
`N_d` whose `theta` is nearest the center, then take a centered contiguous block of width `8*max(q,r)` (rounded to
an odd integer). Overlaps, if any, are merged for primality calculation but each sector retains its declared rows.

Report three populations separately:

1. all raw integers in the blocks;
2. primes;
3. late composites that survive every prime gate `p<=max(q,r)` but are composite under the full square-root sieve.

Bin by the same 16 fixed theta sectors and record count, mean, SD and quantiles of `Z`. The development template is
the unweighted mean of the scale-8, scale-9 and scale-10 prime bin means. It is saved and hashed before scale 11 is
opened.

**Frozen target prediction:** the scale-11 prime curve has:

- Pearson correlation at least `0.90` with the frozen development template;
- RMSE at most `0.075` in signed-product units;
- at least 40% lower RMSE than a constant-zero curve;
- lower RMSE than the frozen wrong-coordinate control described below.

All four pass for Arm B to be `SUPPORTED`. Adequate counts with a clean miss give `NOT SUPPORTED`; any sector with
fewer than 100 target primes makes Arm B `INCONCLUSIVE`.

## Fixed controls and established arithmetic curve

- **Wrong-coordinate control:** retain `Z_qr` but assign theta from the representative gate `q` and the ninth paid
  gate. This tests whether arbitrary modular phase gives the same collapse.
- **Permutation control:** fixed seed `14072126` permutes theta sectors within each population while retaining `Z`.
- **Flat controls:** zero and the development grand mean.
- **Established curve:** for uniformly sampled raw sawtooth phases, report
  `C(theta)=1/3-2*theta+2*theta^2`. This is an analytic arithmetic rival/crosswalk, not independent ARA evidence.
- **Pair-distance disclosure:** report all adjacent pairs and the representative-pair rule; no result-selected pair.

## Instrument checks

- every selected gate is prime and below the fixed `N_d^0.45` boundary;
- exact `A_q+(2-A_q)=2` and `A_r+(2-A_r)=2` closure to floating tolerance;
- direct least-common-multiple spot checks equal `q*r`;
- independently recomputed scale-11 gates and periods;
- exact prime counts in sampled blocks agree between the primary and validator implementations;
- synthetic/full-period small-prime fixtures recover the analytic sawtooth curve;
- all 16 target sectors meet the minimum-count gate.

## Two-output reporting

1. **Claim verdict:** Arm A and Arm B separately, with every frozen criterion.
2. **Geometry verdict:** child periods, adult periods, growth readings, phase-sector distributions, raw/prime/late-
   composite curves, controls, crossings, crests, troughs and pair-level variation even if either arm fails.

## Scope fence

PN14 tests an exact modular construction and its scale transfer. It does not show that every physical ARA identity
uses exponent `0.45`, that decimal scale is universal, that primes are predictable without sieving, or that the same
adult waveform exists outside the tested arithmetic system.
