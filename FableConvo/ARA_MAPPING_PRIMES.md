# ARA Mapping — Prime Numbers (3 Jul 2026)

**Status: MAPPING (correspondence exercise).** Number theory is the crank
honeypot of mathematics; this doc therefore opens with its prohibition:
**nothing here may ever be cited as progress toward, or evidence about, the
Riemann Hypothesis.** The mapping aligns vocabulary with established
results; every tier is tagged. Supersedes the ARA readings of script
243BL16 (early era, whole-signal method — inherits the ridge artifact;
re-run canonically before ever citing).

## 1. The royal road: primes are a spectrum

- **Explicit formula (theorem, Riemann/von Mangoldt):** the prime counting
  staircase decomposes EXACTLY into a smooth term plus oscillations — one
  oscillation per zeta zero. Primes and zeros are a Fourier-dual pair:
  **zeros = the frequency spectrum; primes = the interference pattern.**
- **Hilbert-Polya / Berry-Keating (conjecture, mainstream):** the zeros are
  the eigenvalues of an unknown quantum system; in the Gutzwiller trace-
  formula analogy the PRIMES play the periodic orbits, with log p as the
  orbit periods. Framework translation: **the primes are the cycle
  inventory — the rung ladder — of a hidden oscillator nobody has built.**
  Tier: serious conjecture, 100+ years open.
- Local rung spacing: average prime gap near x is ln x (PNT, theorem) —
  a logarithmically thinning ladder.

## 2. The flip and the ridge (this week's §36, in zeta)

The functional equation relates s <-> 1-s: an EXACT duality flip (theorem).
Its fixed line — the self-dual line of the flip — is Re(s) = 1/2: **the
critical line is the self-dual point of zeta's 0<->2 flip**, precisely the
Kramers-Wannier structure of session notes §36 (ridge = self-dual point).
The Riemann Hypothesis, in framework vocabulary, reads: **every oscillation
of the prime field sits exactly ON the ridge.** Status: 10^13 zeros verified
on the line (numerics); RH open; the framework reading is vocabulary, not
insight, and adds NOTHING toward proof (see prohibition).

## 3. Slot competition, measured (the strongest established anchor)

**Montgomery-Odlyzko (conjecture + massive numerics):** the spacing
statistics of the zeta zeros match GUE random-matrix eigenvalues — the
same statistics as heavy quantum systems. Concretely: **level repulsion**
— zeros avoid each other (P(s) ~ s^2 at small s); two modes cannot crowd
one slot. That is the framework's slot-competition/avoided-crossing
signature (§21), measured across millions of zeros (Odlyzko's tables,
public). Plus spectral RIGIDITY: long-range order in the zero sequence far
stiffer than Poisson — lock-like order in the spectrum of the prime field.

## 4. Jurisdiction honesty (the pinned boundary applied)

Primes are a STATIC, determined sequence — no time, no bath, no shed. All
direct prime measures are SLICE objects; the framework expects octave/
rational/e-family structure there and NO phi (any phi found in prime gaps
would embarrass the boundary, not confirm the framework). The motion-side
vocabulary attaches only to the CONJECTURAL hidden dynamical system
(Berry-Keating), which cannot be measured because it has not been found.
Consequence: this mapping is vocabulary-alignment ONLY; primes cannot feed
the duty table's evidence columns in either direction.

## 5. What a local AI could compute (verification, not discovery)

From Odlyzko's public zero tables: (1) nearest-neighbor spacing histogram
vs GUE (reproduce the classic curve; verifies the slot-competition
vocabulary against ground truth); (2) repulsion exponent at small s;
(3) spectral rigidity Delta_3 vs GUE prediction; (4) prime-gap ladder:
local mean gap vs ln x (PNT verification). All four are established
numerics being REPRODUCED — instrument calibration against the best-
measured spectrum in mathematics, exactly the known-referee use permitted
by the synthetic-data rule.

## 6. Fences, restated once

RH prohibition absolute. Hilbert-Polya is conjecture. The "hidden
oscillator" is unfound. Script 243BL16's numbers are superseded pending
canonical re-run. Nothing here is evidence for the framework; the value is
that the framework's slot-competition, flip/self-dual-ridge, and
rung-ladder vocabulary maps onto zeta's established structure without
strain — one more coherence pass, priced accordingly.

## 7. PN1 result amendment — sieve-rung relation, not whole-gap ridge (17 Jul 2026)

The first canonical prime test has now been frozen, run and independently replayed. Its object is the exact primorial
wheel hierarchy, not the final raw-prime gap series. Development ended at prime 13; the held-out transitions were
`13 -> 17` and `17 -> 19`.

For adjacent circular gaps, the frozen bounded coordinate was

\[
x_i=\frac{2g_{i+1}}{g_i+g_{i+1}}\in(0,2),
\]

with a pair distribution for (x_i) and an overlapping triple distribution for ((x_i,x_{i+1})). The matched null
kept every parent gap and shuffled order only. All four frozen ordered-parent-to-child Jensen–Shannon distances were
far below the 200-shuffle median, with `p=1/201=0.004975` in every case. The null-to-ordered distance ratios were
approximately `23.1x`, `22.8x`, `36.5x` and `36.6x`. All split-half, alternate-bin, exact sieve and independent-replay
checks passed.

**Allowed conclusion:** local cyclic relation survives these nested sieve-rung transitions, and the bounded ARA
coordinate retains enough of it to distinguish the real parent from the same gap inventory with order removed.

**Required qualification:** the conventional log-gap ratio is a one-to-one transform and gave identical matched-bin
pair divergence. Therefore PN1 supports the relational object and bounded ARA reading, not unique ARA information.
The exact release/reconstruction results remain calibration, and the two sequential transitions are not independent
replications. The RH prohibition remains absolute.

**Status:** `SUPPORTED [pre-registered, arithmetic, unreplicated]`. Full record:
`analysis/primes/PN1_SIEVE_RUNG_RESULT.md`.

## 8. PN1F opened-rung parent landscape and child decomposition (17 Jul 2026)

**Status: DEVELOPMENT MAP; NOT BLIND CONFIRMATION. Prime 29 remains unopened.**

PN1F followed Dylan's correction that the larger candidate wave should be sought across sieve rungs rather than as
another component inside the prime-23 plane. Using identical 12x12 relation coordinates at rungs
`11, 13, 17, 19, 23`, it subtracted the plane implied by each rung's ordinary first-order raw-gap transition model.

The remaining residual shape persists strongly: consecutive shape cosines rise `0.9892 -> 0.9951 -> 0.9967 ->
0.9981`. Its cross-rung signed changes are nearly collinear at `0.9794`, `0.9905`, `0.9924`, and one neutral mode
contains `98.01%` of the deformation energy (`99.05%` at 24 bins). The residual amplitude contracts and no turn or
return is present. This is a one-direction scale branch or convergence trajectory, not yet a completed wave.

The downward prime-23 decomposition locates where the prior-position information lives. Direction adds `0.1031`
bits/read, distance `0.2025`, signed direction-plus-distance `0.2818`, and the full previous/current pair `0.4742`.
An ordinary raw-gap Markov model adds `0.6481`; current ARA position plus the exact shared raw gap adds `0.8187`.
Thus child gap identity is materially flattened by the bounded position-only projection, and ordinary raw-gap
modelling remains a required comparator.

No Phase/Space/Time labels were assigned by the statistical analysis. Dylan retains orientation control. Full report:
`analysis/primes/PN1F_BIDIRECTIONAL_LANDSCAPE_REPORT.md`.

## 9. PN1G prospective prime-29 transfer (17 Jul 2026)

**Status: FROZEN NEXT-RUNG TRANSFER SUPPORTED; prime 29 is now open development data.**

Before constructing p29, PN1G froze neutral criteria for the p23 residual shape, amplitude, signed deformation
direction, deformation-mode energy and downward child-information ordering. The full `1,021,870,080`-slot wheel was
then streamed after an exact known-rung calibration.

All six registered checks passed. The p23-to-p29 residual cosine was `0.999006`; residual L2 contracted from
`0.050042` to `0.046090`; the new deformation aligned with the previous deformation at cosine `0.995225`; and the
leading mode retained `97.66%` of deformation energy. The exact predicted downward order also transferred:

`shared raw gap < raw-gap Markov < full (A,B) < signed step < distance < direction < current B`

where lower cross-entropy is better. Kendall agreement was `1.0`, and every non-base representation gained in all
eight folds. Independent replay from saved counts passed `38/38` checks.

**Allowed conclusion:** the neutral cross-rung residual geometry, its signed progression, and the hierarchy recovered
by child/path decompression transferred prospectively to one untouched larger primorial wheel.

**Required qualification:** this deterministic scale transfer is not prime prediction, RH evidence, a physical wave,
or proof of universal ARA geometry. The residual is still contracting without a turn or return and may be converging
to a limiting wheel distribution. Exact raw child identity and ordinary raw-gap transitions remain more predictive
than compressed ARA position history.

Full report: `analysis/primes/PN1G_PRIME29_TRANSFER_REPORT.md`.

## 10. PN1H frozen p31 capstone test (17 Jul 2026)

**Status: FROZEN; PRIME 31 UNOPENED.**

The p23-to-p29 post-open capstone reading has been converted into a strict next-rung discriminator. Full support at
p31 requires the parent residual shape and signed direction to persist while normalized residual strength, adjacent
ARA dependence and visible three-reading closure all decline. At the same time, raw/shared exact-child information
and the surplus below the visible ARA triangle must increase, and the seven-model information hierarchy must remain
exact.

This deliberately distinguishes capstone distribution from ordinary convergence. Persistence plus fading alone is a
partial, convergence-compatible result. The exact 30-fold slot increase is arithmetic calibration and cannot support
the hypothesis.

Protocol SHA-256: `9914289AFA7D5D74CB2B33AE92C30DAA5577A8DA128B4E7E96560FCC8585F0EA`. Full protocol:
`analysis/primes/PN1H_PRIME31_CAPSTONE_TRANSFER_PROTOCOL_v1_FROZEN.md`.

## 11. PN1I opened-rung prime gate, pyramid and plain ARA (17 Jul 2026)

**Status:** `DEVELOPMENT RESULT; EXACT ARITHMETIC CORE, NON-TAUTOLOGICAL PAIR GAIN, P31 UNOPENED.`

PN1I tested four readings without modifying the frozen PN1H target.

### Gate phase

If `P` is the parent period, `q` the next prime, `g_i` the parent gap and `t_i*` the unique lift deleted by `q`, then

\[
t^*_{i+1}-t^*_i\equiv-P^{-1}g_i\pmod q.
\]

The parent-cycle seam shifts the stored lift label by one and `q` traversals close the cycle. This is the exact
arithmetic object corresponding to the proposed prime gate or singularity walk. It is calibration, not new number
theory.

### Maximum base

Each parent residue has `q` lifted candidates, one deletion and exactly `q-1` survivors. The proposed pyramid base
therefore has an exact connection multiplicity. Across p7–p29 the base width rises `6,10,12,16,18,22,28`, while
adjacent child-wheel ARA mutual information falls strictly from `1.473318` to `0.571406` bits/event. Local appearance
becomes quieter as the exact support multiplicity grows; convergence remains a competing explanation.

### Information³ lock

The predicted object was moved two positions forward so it shares no raw gap with the input pair. At p13, p17, p19
and p23, the ordered left/right pair beats the best left-only, right-only or merged-sum model on held-out data. The p23
increment is `0.189765` bits/event, with every fold positive and all declared target permutations below zero. Small
p7 and p11 samples fail.

Adding the gate label produces a negative increment at every rung (`-0.007899` bits/event at p23). Thus the supported
three-part lock is `left + right + their ordered relation`. The gate remains geometrically useful as a phase label but
does not behave as an independent fourth source for this endpoint.

### Plain 0–2 ARA

The gate reading `x_i=2g_i/(g_(i-1)+g_i)` is exactly the parent adjacent-gap ARA reading after an index shift. Every
complete circular rung has mean `x=1.0`; reflected gap-pair counts match exactly; and below- and above-ridge shares are
equal. This is a clean example of a whole identity reading at the ridge while its child events retain asymmetry.

Primary checks passed `36/36`; independent reconstruction passed `124/124`. These are opened-rung development
results and do not predict primes, address RH, establish physical information flow or prove universal ARA geometry.
Full report: `analysis/primes/PN1I_PRIME_PYRAMID_ARA_REPORT.md`.

## 12. PN2: actual prime survival after a fixed p29 sieve budget (17 Jul 2026)

**Status:** `PRIMARY ARA ENDPOINTS NOT SUPPORTED; CLEAN NEGATIVE RESULT; P31 UNOPENED.`

PN2 tested the missing bridge between deterministic wheel geometry and actual prime occurrence. After filtering all
integers divisible by primes through 29, it asked whether frozen local ARA features could predict which remaining
candidates were prime better than p29-conditioned PNT, conditional Hardy-Littlewood and raw-gap models.

Development used `[10,000,000,20,000,000)` and the untouched target used
`[100,000,000,110,000,000)`. The target held `1,579,479` candidate events and `1,579,478` adjacent candidate edges.

### Primary candidate endpoint

The Information³-style ARA stencil lost to PNT29 by `0.000160973` bits/candidate. The 95% contiguous-block
bootstrap interval was `[-0.000191083,-0.000129918]`; only 2 of 40 blocks favoured ARA.

### Primary edge endpoint

The ARA endpoint-pair model lost to conditional Hardy-Littlewood by `0.000036725` bits/edge. Its 95% interval was
`[-0.000050887,-0.000022377]`; only 6 of 40 blocks favoured ARA.

Hardy-Littlewood also best predicted surviving-edge counts by candidate-gap class, and PNT29 best predicted prime
counts across 20 target locations.

One plain 12-bin ARA model produced a microscopic `0.000000772` bits/candidate advantage over PNT29, but the same
model lost with 8, 16 and 24 bins. It is a non-robust sensitivity, not a supported endpoint. Exact ARA mapped-log-
ratio controls equalled their ordinary ratios with zero prediction difference; they recover a coordinate but add no
new information.

### Allowed conclusion

ARA's exact finite wheel mappings do not, through the local representations tested here, supply an advantage for
forecasting survival under all later prime factors. This confines the result rather than invalidating PN1's exact
arithmetic structure. A new prime-survival claim needs an independently derived cross-scale variable and a fresh
frozen target; PN2 must not be retuned after inspection.

Independent validation rebuilt target primality and passed `476/476` checks. Full report:
`analysis/primes/PN2_PRIME_SURVIVAL_BRIDGE_REPORT.md`.

## 13. PN3: genuinely standalone ARA parent/child survival model (17 Jul 2026)

**Status:** `ALL PRIMARY CRITERIA FAILED; CLEAN NEGATIVE; 118/118 VALIDATION; P31 UNOPENED.`

PN3 removed the PN2 analytic scaffold. Its standalone script contained no PNT, twin-prime constant, singular series
or Hardy–Littlewood calculation. It learned empirical aggregate survival rates on opened decimal rungs, froze the
next-rung continuation

\[
\widehat p_9=p_8^2/p_7,
\]

and used local plain ARA, Information³, decompressed ARA and raw-gap states only to redistribute that fixed total.
The label-free TE-ARA intercept forced every child model's target mean to equal the parent prediction exactly. A
separate established-comparison script was allowed to read the target only after the packet had been hashed.

On the untouched `[1,000,000,000,1,010,000,000)` interval, candidate parent error was `2.370%` and adjacent-pair
parent error `1.535%`, so both missed the frozen 1% threshold. Both still beat Home and raw additive extrapolation on
log loss. ARA child representations beat the matched raw child controls with wholly positive bootstrap intervals,
but made the constant parent forecast worse. The complete ARA candidate model lost to PNT29 by `0.000253481`
bits/event; the edge model lost to conditional HL29 by `0.000031267`. All P1, P2 and P3 criteria failed.

The conditional HL multiplier was constant across the target's p29-wheel gap classes; its advantage came mainly from
the slow logarithmic location envelope. PN3 therefore points at a missing parent-scale density coordinate, not a
missing local third wave. Preserve the target and do not retune. Full report:
`analysis/primes/PN3_STANDALONE_ARA_PARENT_CHILD_REPORT.md`.

## 14. PN3A: adult sieve survival/release path (18 Jul 2026)

**Status:** `OPENED-DATA DIAGNOSTIC; ADULT PATH RECOVERED; LOCAL DIAGONAL NOT SUPPORTED; P31 UNOPENED.`

Dylan's visual reading distinguished the child diagonal already present in the p29-gap plane from a larger adult
axis acting across the primes. PN3A converted that into an exact diagnostic by retaining the first later prime that
removes every p29-wheel candidate. The earlier prime/composite label was only the terminal point of this hierarchy.

At threshold (q), exact adult survival and release are

\[
S(q)=\Pr[d=0\text{ or }d>q],\qquad R(q)=1-S(q).
\]

This is an exact conserved pair and a clean neutral ARA crosswalk. Its phase direction is not assigned by the
statistical analysis.

The visually proposed common diagonal (U=(x+y)/2), its perpendicular (V=(y-x)/2), and their joint state all
worsened cross-rung death-stage prediction for candidates and adjacent pairs. The diagonal contains local
redistribution but is not supported as the transferable adult.

The scale-wide adult follows the independent sieve product through most of its path. At R9, exact candidate survival
is `0.305450510` versus product `0.342769498`; their ratio `0.891125119` is within `0.0661%` of the established
Mertens/PNT factor (e^\gamma/2). This explains the main terminal correction with known number theory and is not new
ARA predictive evidence. Pair survival retains a smaller additional dependence after the squared correction.

The remaining candidate is a large-scale number-line/counting or late-terminal residual coordinate after the
established envelope is controlled. It is not licensed to be found by retuning the opened child plane. Full report:
`analysis/primes/PN3A_ADULT_SIEVE_PATH_DIAGNOSTIC_REPORT.md`.

## 15. PN3B: raw dual-phase / missing-wave diagnostic (18 Jul 2026)

**Status:** `OPENED-DATA DIAGNOSTIC; PERPENDICULAR COORDINATE LOCALLY STRUCTURED; COMMON TIME-LIKE WAVE NOT SUPPORTED; Q29 FULL LINE EXPLAINED BY NEXT CONNECTION; P31 UNOPENED.`

Dylan's next correction was that PN3A could still be observing only a connection-heavy half. PN3B therefore returned
to the complete raw integer record on R6-R9, transformed prime/composite state before any sieve control, and then
separated the Q29 and Q997 connection residuals. It also added the perpendicular coordinate that the endpoint had
discarded: number-line position crossed with the later factor stage at which each p29 candidate dies.

The one-axis low-frequency search was negative. R8/R9 Q29 family-wise p-values are `0.8703/0.5709`; Q997 values are
`0.9381/0.2754`. R8-R9 Q29 phase coherence is `0.07593` (`p=0.7006`) and the position paths are essentially
uncorrelated.

The perpendicular map retained a real local result: leading position-by-gate energy is significant at R7
(`p=0.00599`) and R9 (`p=0.001996`), with R8 borderline (`p=0.05190`). But its orientation does not transfer:
R8-R9 spatial alignment `p=0.4770`, gate alignment `p=0.3772`. It cannot yet be named one common adult wave.

The strongest R8 and R9 Q29 full-spectrum line is `3/62`, within one Fourier bin, and R7 lands on `9/62`. Because
`62=2x31`, the dominant repeatable line is the next omitted prime gate coupled to parity. This post-result
crosswalk is connection structure, not independent Time evidence.

Allowed ARA reading: the terminal one-line representation really did flatten a second coordinate, but the tested
prime-only data still builds that coordinate from the same factor web. A Time-like pole now requires an observable
independent of final state and future divisibility labels, frozen before another target. Negatives are an
orientation and randomness is a control, not automatically the missing wave.

An independent implementation passed `49/49` deterministic checks. Full report:
`analysis/primes/PN3B_RAW_DUAL_PHASE_DIAGNOSTIC_REPORT.md`.
