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

The three-point ARA stencil (historically labelled “Information³-style”) lost to PNT29 by `0.000160973`
bits/candidate. The 95% contiguous-block
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

and used local plain ARA, three-point ARA stencils, decompressed ARA and raw-gap states only to redistribute that
fixed total. The label-free parent-budget intercept forced every child model's target mean to equal the parent
prediction exactly. This was probability-mass conservation, not the canonical TE-ARA energy-participation quantity. A
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

## 16. Centered terminology and PN4 direct sieve-state transfer (19 Jul 2026)

The centering audit corrected three historical labels without altering any frozen protocol or numerical outcome:

- three consecutive readings are a **three-point ARA stencil**, not Information³ unless two identities and their
  retained relation are explicit;
- PN3 conserved a parent probability budget, not canonical TE-ARA;
- PN3B used a raw integer source but processed Fourier/SVD methods, and future factor-removal stage is diagnostic,
  not a prospective feature.

Authority: `analysis/primes/PN_CENTERING_TERMINOLOGY_CORRECTION_2026-07-19.md`.

PN4 then returned directly to the exact PN3A sieve-death arrays. It measured survivor/release on
`x=2(1-S)` in 24 fixed normalized log-gate cells and retained the candidate/pair relation
`J=log(S_edge/S_candidate^2)`. R6-R8 supplied prior paths; R9 was excluded from construction by code but was already
historically opened, so the result is retrospective.

The large deformation transfers strongly. From R8 to R9, candidate terminal error falls from `12.2177%` under the
independent sieve to `1.5723%` under ARA same-form transfer. Pair error falls from `26.9769%` under independence to
`2.8232%` when the explicit relation is retained. Both improvement directions repeat from R7->R8 to R8->R9.

The frozen ARA models are not the winners. Raw multiplicative-ratio transfer reaches `0.0495%` candidate terminal
error and `0.2070%` pair error, with slightly lower path log loss. The local three-point ARA stencil also loses to
the best local control. Only 2 of 8 separately scored criteria pass.

This is a useful geometry result but not a new prime-calculation result. The winning candidate ratio is almost the
established Mertens/PNT factor: R8 `0.8906841`, R9 `0.8911251`, and `e^gamma/2 = 0.8905362`. A future multiplicative
rung-coupling law may be written in ARA language, but it must be frozen on a new transfer and compared directly with
Mertens/Buchstab/PNT controls; PN4 cannot confirm a rule discovered from PN4.

The independent validator passed `88/88` checks. Full report:
`analysis/primes/PN4_DIRECT_SIEVE_STATE_ARA_REPORT.md`.

## 17. PN5 fresh R10 multiplicative rung transfer (19 Jul 2026)

**Status:** `FRESH PRE-HASHED TARGET / MULTIPLICATIVE RULE HIGHLY ACCURATE / STRONG PARTIAL SUPPORT / BUCHSTAB PATH CONTROL WINS / PAIR J NEAREST-RUNG CRITERION FAILS / P31 UNOPENED.`

PN5 froze the newly proposed vertical coordinate `k=log(S/S_independent)` and candidate/pair relation
`J=log(S_edge/S_candidate^2)` before constructing the next 1% decimal window,
`[10,000,000,000,10,100,000,000)`. The complete prediction packet was hashed first. The target then exactly
enumerated 100 million integers, 15,794,726 p29-conditioned candidates and 15,794,725 adjacent pairs.

The primary multiplicative rule achieved `0.019187%` candidate terminal error and `0.130979%` pair terminal error.
It decisively beat independence and the prior additive ARA rules, required no repair, and passed P1, P2 and P6.

The registered result remains partial. Candidate `k` is closer from R9 than R8, but pair `J` is slightly closer from
R8, so the combined nearest-rung P3 criterion fails. The Buchstab asymptotic path has lower candidate log loss, and
Buchstab plus frozen R9 `J` has lower pair log loss, so P4 and P5 fail. Three of six registered criteria pass.

The observed R10 survivor path repeats the same arc-like visual form. That is compatible with the ARA sectional-slice
reading, but the Buchstab curve shares the same visible arc and scores better. A literal circle claim therefore needs
its own frozen equal-complexity comparison.

Allowed conclusion: multiplicative/log-ratio scale transfer is a highly accurate prospective recurrence for the
candidate envelope, and explicit pair coupling is useful. It is algebraically raw-equivalent and does not yet exceed
the established sieve envelope. The best tested full-path construction is the established Buchstab parent plus the
retained pair relation.

An independent implementation repeated the full 100-million-integer target with a different chunk size and passed
`56/56` checks. Full report: `analysis/primes/PN5_MULTIPLICATIVE_RUNG_TRANSFER_REPORT.md`.

## 18. PN6 fresh native circumference/log-rung transfer (19 Jul 2026)

**Status:** `FRESH PRE-HASHED TARGET / 5 OF 7 PASS / MIXED NATIVE RESULT / NO ESTABLISHED-LAW AUDIT / P31 UNOPENED.`

PN6 tested Dylan's native-circle reading directly. At every log-gate cell it mapped direct survivor share to the ARA
diameter, `x=2(1-S)`, and then to the fixed upper branch of the canonical unit circle,
`theta=acos(2S-1)`. Candidate and adjacent-pair phase increments across R8-R10 supplied one shared next-rung
withdrawal factor, `rho=0.8342632892`. This prediction was written and hashed before constructing the fresh
one-billion-integer target `[100,000,000,000,101,000,000,000)`.

The frozen primary predicted candidate terminal survival within `0.1017%` and pair survival within `0.3198%`.
Observed next-rung withdrawal was `0.8074602` for candidates and `0.7719118` for pairs, both close to the frozen
shared value and only `0.03555` apart. The canonical circle beat the direct native logarithmic extrapolation on path
log loss for both identities. A second native route to the pair identity, candidate plus retained relation `J`, also
landed below 1% terminal error. P3-P7 pass.

The strict core does not pass. Home retains slightly lower at-risk-weighted path log loss for both identities, even
though its terminal errors are approximately 10% and 21%, and the pair phase RMSE is `0.01846` against the frozen
`0.015` tolerance. Therefore P1 and P2 fail. Preserve this as a mixed result: it supports a useful prospective
circumference/rung recurrence and native pair-route closure, but not a complete native law for the full sieve path.

No Buchstab, PNT, Mertens, Hardy-Littlewood, Fourier, SVD or NMF model was used or run as a post-result comparator in
PN6. A separately coded full target reconstruction with a different chunk size passed `109/109` checks. Full report:
`analysis/primes/PN6_NATIVE_ARA_CIRCUMFERENCE_REPORT.md`.

## 19. Phase-referenced counterwave correction (19 Jul 2026)

**Status:** `DESIGN NOTE / NOT FROZEN / NO NEW TARGET OPENED.`

Dylan corrected the search order implied by PN3B. Rather than asking whether an unreferenced second coordinate already
looks like one common Time wave, first treat the adult connection survival/release path as Phase A, ARA its full
appearance, use how it recurs or moves across rungs as the orientation landmark, and only then search its predicted
counterphase for an independently measured opposite-wave candidate.

PN6 has already supplied the first half: `S -> x=2(1-S) -> theta=acos(2S-1)` maps the adult connection wave, and
cross-rung `Delta theta` records how that appearance moves. Neither `theta+pi` nor an algebraically constructed
complement can count as evidence for Phase B. The counterphase location must be fixed from Phase A, then tested using
an observable not manufactured from the same survival coordinate.

“Occurrence in relation” currently has two non-equivalent readings: vertical reappearance across R rungs, and lateral
event occurrence along the number line after alignment to adult ARA phase. A strong triangulation may use their
intersection, but the intended reading must be confirmed before freezing. Complete design and non-tautology fences:
`analysis/primes/PN7_PHASE_REFERENCED_COUNTERWAVE_DESIGN_NOTE_2026-07-19.md`.

## 20. PN7A phase-referenced occurrence test (19 Jul 2026)

**Status:** `OPENED-DATA REGISTERED DEVELOPMENT TEST / 0 OF 5 CONDITIONS PASS / TESTED COUNTERWAVE REPRESENTATION NOT SUPPORTED / P31-R12 UNOPENED.`

PN7A implemented the corrected search order. It first treated the direct p29-conditioned survivor/release path as
the adult connection-side Phase A, mapped it through `x=2(1-S)` onto the fixed circle coordinate
`theta=acos(2S-1)`, and measured cross-rung movement by `V_r=theta_r-theta_(r-1)`. It then tested an independent
occurrence reading: exposure-corrected removal asymmetry between the right and left halves of 64 raw ordered
number-line bins. R9-R11 occurrence was aligned by the adult ARA phase without a fitted sign, shift, smoother or
spectral component.

The tested opposite-wave representation failed all five registered conditions. Candidate occurrence mean
recurrence changed from `+0.3713` in raw gate order to `-0.1304` after adult-phase alignment. Edge recurrence changed
from `+0.2674` to `+0.1615`. Candidate and edge phase-aligned occurrence disagree at R10 and R11 (`-0.1901` and
`-0.1996`), vertical-lateral signs are inconsistent, and the adult/root occurrence split does not consistently
dominate the quarter/eighth children.

Allowed conclusion: the adult connection wave remains clean, but its proposed Time-side counterpart is not visible
as a recurring fixed-window left/right imbalance of raw removal occurrence. This result rejects that occurrence lens;
it does not reject every possible opposite coordinate. The fixed decimal-window split is not translation-invariant
and appears to measure finite-window fluctuation. A later native development test may examine ordered traversal or
waiting distance between events, but must freeze that new observable before inspection and must not retune PN7A.

The direct R7-R11 reconstruction reconciled with earlier totals, the independent scalar implementation passed
`136/136` checks, the executed notebook completed `4/4` code cells, and no fresh target was opened. Full report:
`analysis/primes/PN7A_PHASE_REFERENCED_OCCURRENCE_REPORT.md`.

## 21. PN7B actual-prime node / traversal-gap pair (19 Jul 2026)

**Status:** `DIRECT PAIR CORE SUPPORTED / 6 OF 7 REGISTERED CONDITIONS PASS / OPENED-DATA STRUCTURAL TEST / P31-R12 UNOPENED.`

Dylan identified that PN7A had not tested the direct pair. PN7B therefore used actual consecutive primes rather than
p29 candidate-removal position. At every internal actual prime `p_i`, incoming and outgoing gaps
`g_minus=p_i-p_(i-1)` and `g_plus=p_(i+1)-p_i` define the node-centred ARA state
`x_i=2g_plus/(g_minus+g_plus)`. The frequency vector retains how often each ARA mix occurs, while the ordered plane
retains the handover `(x_i,x_(i+1))`.

The R10-R11 frequency correlation is `0.9994386` with Jensen-Shannon divergence `0.0001781` bits. The ordered-plane
cosine is `0.9990303` with divergence `0.0006077` bits. Immediate node pairing differs from a distant same-gap-
inventory control by 25.3 and 67.0 times split-half instability at R10/R11. Immediate handover differs from a
distant same-state-frequency control by 26.9 and 74.3 times instability. R10 frequency transfers to R11 better than
R9 or the R10 distant-pair control, and both frequency/ordered distances converge across the final rungs. P1-P6 pass.

P7 fails because the frozen mirror reversed 24 equal bins. Exact ridge and other discrete rational states sit on bin
boundaries, so bin reversal is not exact incoming/outgoing gap reversal. The failure remains registered. A clearly
post-endpoint raw gap-pair audit finds near-zero mean direction and transpose cosines `0.999928/0.999991` at R10/R11;
it diagnoses the grain distortion but cannot change the 6/7 result.

Allowed conclusion: actual-prime connection nodes possess a scale-recurring incoming/outgoing gap ARA shape, and
immediate node pairing is not reproduced by distant pairing of the same gap inventory. This is structural evidence,
not prime generation: actual primes are required inputs, the ARA coordinate is information-equivalent to a log gap
ratio, known arithmetic constraints correlate gaps, and consecutive ARA readings mechanically share one gap. A
future PN7C must preserve that shared overlap in its null/control before attributing residual sequential memory to a
larger interaction wave.

The independent validator re-sieved every window with different chunk boundaries and passed `80/80` checks. The
executed notebook completed `4/4` code cells. Full report:
`analysis/primes/PN7B_ACTUAL_PRIME_NODE_GAP_REPORT.md`.

## 22. PN7C actual-gap sequential memory (19 Jul 2026)

**Status:** `CODE-ISOLATED R11 / 5 OF 7 PASS / ARRIVAL MEMORY TRANSFERS / BEYOND OVERLAP / NOT BEYOND FIRST-ORDER RAW-GAP CONTROL / RESIDUAL CORE FAILS.`

PN7C tested the matched control required by PN7B. R9-R10 actual-prime gaps trained four frozen models before the
PN7C R11 sequence was constructed: ARA-IID, current-state ARA-M1, arrival-plus-current ARA-M2, and an exact one-step
RawGap-M1 projected through the same ARA bins. R11 was historically opened, so code isolation prevents target tuning
but does not restore blindness.

At 24 bins, adding arrival direction improves transferred ARA cross-entropy from `4.230639` to `4.112585` bits per
reading, a `0.118054`-bit gain. It is positive in all 100 R11 blocks and at 12, 24 and 48 bins. Brier and top-3 also
improve. P1-P3 and P7 pass.

R11 empirical conditional memory is `0.121900` bits. The largest of five exact-inventory overlap-preserving
shuffles is `0.101432`, leaving `0.020467` bits; P4 passes. A 10-million-path first-order raw-gap Markov world reaches
`0.118849`, however, leaving only `0.003051` bits—below the frozen `0.010` requirement. P5 fails. RawGap-M1 also
predicts better than ARA-M2 (`3.621871` versus `4.112585` bits), so P6 fails and the P1-P5 residual core does not pass.

Allowed conclusion: arrival direction is a real, distributed and transferable part of the local actual-gap ARA
relation, and observed order exceeds shared overlap alone. The tested local memory is nevertheless almost reproduced
by ordinary one-step exact-gap dynamics, while ARA's binned relational compression discards useful absolute scale.
PN7C tests consecutive-gap child handover; it does not test Dylan's proposed slow adult wave across many primes or
number-line scale.

The validator independently rebuilt the full R11 gap sequence, repeated the shuffles and Markov control, and passed
`43/43` checks. Full report: `analysis/primes/PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_REPORT.md`.

## 23. PN8 power-of-ten public-reveal pilot (19 Jul 2026)

**Status:** `PROSPECTIVE PUBLIC REVEAL / PROBABILITY TRANSFER POSITIVE / SHARPNESS GATE FAILED / 3 OF 4 PRIMARY CONDITIONS PASS.`

PN8 tested whether the frozen PN7C local ARA models transfer to five distant decimal boundaries. The targets
`10^50`, `10^100`, `10^150`, `10^200`, and `10^250`, the 24-bin state, models and conditions were registered before
reveal. Only four consecutive primes below each boundary were generated. ARA-IID, ARA-M1, ARA-M2 and RawGap-M1
forecasts were serialized, then the prediction packet was frozen with SHA-256
`AA26297D54D1BB52203A9A77B1F981977D893C6630D739C521E906459391A7BA`. The first-prime-above offsets were retrieved
afterward from public OEIS sequences A033873/A003617.

ARA-M2 achieved mean target-bin log loss `4.076804` bits, better than ARA-M1 (`4.643778`), ARA-IID (`4.487415`)
and the uniform 24-bin value (`4.584963`). It assigned more target probability than ARA-M1 in four of five cases.
Q2-Q4 therefore pass. Its target ranks were 8, 2, 8, 5 and 16, producing zero top-one hits and only one top-three
hit. Q1 required at least two top-three hits, so Q1 and the joint pilot gate fail.

RawGap-M1 produced zero probability for the `10^250` target because the actual crossing gap fell outside its frozen
exact-gap support. Its infinite mean loss is a support/extrapolation defect and remains diagnostic; it is not an
honest basis for claiming an ARA victory.

Allowed conclusion: the frozen two-step ARA context transferred useful probability mass to five 50-250 digit
boundaries, but it remained too broad to locate the outcome sharply. PN8 supports weak scale transfer, not
effectiveness, exact prime prediction or the proposed adult slow wave. Very large numbers test transfer across scale;
many untouched targets are required to test effectiveness. A follow-up should preserve ARA-M2 unchanged across at
least 100 pre-registered boundaries and add a scale-capable raw-gap or established prime baseline.

Independent numerical validation passed `164/164` checks, prime-boundary validation passed `50/50`, and the executed
notebook completed `4/4` code cells. Full report:
`analysis/primes/PN8_POWER_OF_TEN_PUBLIC_REVEAL_REPORT.md`.

## 24. PN9 tangent-sphere ridge and adult scale (19 Jul 2026)

**Status:** `REGISTERED OPENED-DATA TRANSFER / TANGENT REPRESENTATION EXACT / SCALE INFORMATION PRESENT / 24-BIN TRANSFER CORE FAILS / 12-BIN SENSITIVITY POSITIVE / R12-P31 PROTECTED.`

Dylan proposed reading each actual-prime gap as the diameter of a sphere section, with each internal prime forming
the contact ridge between the incoming and outgoing gap-spheres. This is an exact geometric representation: the
distance between adjacent gap midpoints equals the sum of their half-gap radii. It is not prime-specific, because the
same tangent-interval identity holds for any strictly increasing sequence.

PN9 decomposed the local pair into two native 0–2 readings. The established PN7B coordinate
`x=2*g_out/(g_in+g_out)` records contact balance. The added coordinate first retains local sphere scale
`L=(g_in+g_out)/2`, then compares it with the established prime-number-theorem home scale through
`y=2*L/(L+ln(p))`. At a known node the unbinned pair is reversible:
`L=ln(p)*y/(2-y)`, `g_out=x*L`, `g_in=(2-x)*L`. Numerical reconstruction error is below `3.5e-13` gap units.

The ordered R11 record contains `0.440599` bits of conditional scale information. Five exact-gap-inventory shuffles
reach at most `0.337216`, leaving `0.103383` bits of ordered residual, so P6 passes. The scale axis is therefore
informative beyond mechanical shared-gap overlap plus the same gap inventory.

The primary 24-bin coordinate does not transfer, however. Adding `y` worsens cross-entropy by `0.159506` bits on
R9→R10 and `0.059191` on R9+R10→R11; all 100 R11 blocks are negative. The 24-bin marginal-`y` divergences are
`0.025694` and `0.012103` bits, above the registered `0.005` recurrence limit. RawGap-M1 remains much better than the
scale-aware model on R11 (`3.621871` versus `4.171776` bits). P1–P5 and P7 fail.

The predeclared 12-bin sensitivity moves in the opposite direction: scale improves transfer by `0.197766` bits on
R9→R10 and `0.191356` on R11. A post-result merge of the fixed scale bins gives marginal divergences `0.003959` and
`0.001204`. This cannot replace the failed primary verdict, but it generates a precise follow-up: an adult coordinate
may require a coarser grain than the child contact coordinate.

Allowed conclusion: PN9 recovered the absolute local scale discarded by PN7C and found strong ordered scale
information, but `y=2L/(L+ln(p))` at 24 equal bins is not a demonstrated rung-invariant adult wave. The result does
not identify a physical Time pole or predict unknown primes. A future PN9B should freeze child `x` at 24 bins, adult
`y` at 12, use hierarchical backoff, predict both next `x` and next `y`, retain raw-gap/modular controls, and preserve
R12 until every choice is frozen.

The independent validator reproduced all headline values within `1.78e-15`. Full report:
`analysis/primes/PN9_TANGENT_SPHERE_RIDGE_SCALE_REPORT.md`.

## 25. PN10 factor sphere: exact ridge recovery and early-ridge scale transfer (20 Jul 2026)

**Status:** `FROZEN FRESH-RANGE TEST / P1-P6 PASS / EXACT AT RIDGE / PROBABILISTIC BEFORE RIDGE / P31-R12 PROTECTED.`

Dylan corrected the ontology: the multiplicative and sieve-survivor descriptions are not independent waves but the
two reversible directions of one ARA factor sphere. PN10 therefore defined the native factor position
`x_n(d)=2*log(d)/log(n)`. Factor `1` is `0`, `sqrt(n)` is the `1.0` ridge, and the whole number `n` is `2`. Whenever
`d` divides `n`, its partner closes the diameter exactly: `x_n(d)+x_n(n/d)=2`.

This produces an exact ARA prime procedure. Walk prime divisor gates upward while `x_n(q)<=1`. A divisor collision
means composite; a quiet ridge with no divisor means prime. The rule is algebraically ordinary trial division through
`sqrt(n)`, so the result is an exact crosswalk rather than a new faster algorithm.

The protocol was frozen at SHA-256
`A46FC79D82034CB827F907C531C4DF208B9E33E3AFCE8E9E00D60E637D8F4BEE` before constructing development
`[10^6,2*10^6)` or fresh evaluation `[2*10^9,2.001*10^9)`. On the fresh one-million-integer interval, the ridge
rule recovered all `46,903` primes with zero classification errors. Factor-pair closure held to `4.44e-16`, and all
`1,229` checked prime squares put their prime root exactly at the ridge. P1-P4 pass.

Stopping before the ridge gave a transferable probability rather than an identity label. At `c=0.90`, development
prime purity was `83.7346%`; fresh purity was `83.5286%`, only `0.206` percentage points away. The unscaled fixed-Q
control missed by `29.735` points. Mean fresh Brier across the four frozen cutoffs was `0.021150` for scaled ARA and
`0.034329` for fixed-Q; mean cross-scale purity error was `0.009205` versus `0.190307`. P5-P6 pass.

The limit is loadbearing: `9,249` composites still survived at `c=0.90`. One factor-depth coordinate cannot identify
which pre-ridge survivors are prime. The next nontrivial test is therefore a separately frozen parent-plus-child
relation that attempts to rank those hidden composites without merely continuing trial division, against controls
using exactly the same raw divisor information.

Allowed conclusion: the factor sphere gives a mathematically exact reversible ARA crosswalk and a strongly
scale-normalised partial-sieve coordinate. It does not yet prove a new prime theorem, reduce computational cost,
beat established rough-number theory, or establish universal physical fractality. The independent validator passed
`64/64` checks. Full report: `analysis/primes/PN10_FACTOR_SPHERE_PRIME_RECOVERY_REPORT.md`.

## 26. PN10B pre-ridge child-phase ranking (20 Jul 2026)

**Status:** `REGISTERED FRESH TARGET / CHILD CLOSURE EXACT / PRIME-RANKING NULL / P1 PASS, P2-P6 FAIL / P31-R12 PROTECTED.`

PN10B decompressed the already-paid parent sieve state without testing a later divisor. For the nine largest tested
prime gates `q_j<=n^0.45`, it used `A_j=2*(n mod q_j)/q_j`, `B_j=2-A_j`, signed child orientation
`s_j=A_j-1`, and ordered adjacent coupling `h_j=s_j*s_(j+1)`. These are child coordinates inside the PN10 factor
sphere; A/B are two directions of one child, not independent evidence.

The protocol and source were hash-frozen before opening fresh interval
`[4,000,000,000,4,001,000,000)`. The target retained `54,275` pre-ridge survivors: `45,166` primes and `9,109`
composites. Child closure was exact, all gates were already paid, and no survivor had a zero paid remainder. P1
passes.

The primary outcome was null. ARA full log loss was `0.652923909` bits per survivor versus `0.652816910` for the
parent-only forecast; paired gain `-0.000106999`, 95% contiguous-block interval
`[-0.000241111,+0.000034314]`, AUC `0.500307`. It did not beat Raw full or order-scrambled ARA, and the tiny
positive D-to-E development-transfer difference reversed on the fresh target. P2-P5 fail. ARA compact beat Raw
compact by `0.000055850` bits/event but was worse than parent, so P6 fails. The established constant Buchstab
rough-number probability gave the lowest fresh log loss while providing no individual ranking.

Allowed conclusion: the factor sphere can be decomposed into exact local A/B residue children, but this nine-gate
child web does not expose which survivors contain a later unseen factor. This is a clean null for one child identity,
not a disproof of ARA decompression or universal fractality. Exact primality still requires the remaining divisor
gates. Independent validation passed `79/79` checks with zero metric disagreement. Full report:
`analysis/primes/PN10B_CHILD_PHASE_PRIME_RANKING_REPORT.md`.

### PN10B geometry disclosure: the event crest and child waves are different coordinates

A post-hoc disclosure retained the frozen NULL and exposed the shape that the benchmark summary had compressed.
Aligned on 45,162 interior primes, parent factor progress reaches exactly `1.0` at offset zero. Every odd offset is
an even composite and falls to the least-factor-2 trough near `0.062701`; even offsets form ordinary sieve-period
shoulders. This is an exact retrospective event ridge, not a new advance prime predictor.

The nine paid-gate children do not crest at offset zero. Their population mean stays near 1.0 through the event,
while each prime can be highly asymmetric inside: pooled prime child A spans `0.0000955-1.9999044`, individual
prime centroids span `0.4997889-1.4266385`, and nodes exhibit one through six adjacent side flips. Across all prime
children, the mean A coordinate is `0.9998605`; surviving composites read `0.9986144` and match the prime landmark,
spread, coupling and flip distributions to standardized differences below `0.015`.

Thus two simultaneous results must remain visible: **parent event geometry recovered; paid-gate child geometry rich
but not prime-specific.** Full lead/at/lag trace and examples:
`analysis/primes/PN10B_EVENT_CENTERED_GEOMETRY_REPORT.md`.

## 27. PN10C three-lane decomposition of the prime event shoulders (20 Jul 2026)

**Status:** `POST-HOC STRUCTURAL RECOVERY / RED-BLUE CONDITIONAL PAIR SUPPORTED / BLACK COMMON LANE SUPPORTED / INDEPENDENT STRONGER BLACK WAVE NOT SUPPORTED.`

Dylan marked three repeating even-offset families in the PN10B parent event trace: two smaller alternating coloured
families as a Phase A/Phase B pair, plus a larger black family as a directly coupled third wave. PN10C froze that
reading as a diagnostic before calculating the conditional summaries.

The red/blue interpretation landed exactly after separating central primes by orientation. At `p=1 mod 6`, offset
lane 2 is entirely divisible by 3 and reads `0.099378`, while lane 4 remains admissible at `0.423268`. At
`p=5 mod 6`, the roles reverse: lane 2 reads `0.422946`, lane 4 reads `0.099378`. The frozen role-swap contrast is
`+0.323729`, 95% CI `[+0.323298,+0.324171]`. Reflecting one centre orientation through the event cuts mean absolute
trace error from `0.107882` to `0.000515`, so the coloured families are a genuine reversible conditional pair.

Black is real but is not an independently stronger third lane at this grain. Its orientation difference is
`-0.000358`, with a 95% interval containing zero. It appears `+0.157804` above pooled red/blue before conditioning,
because black offsets preserve both admissible mod-6 orientations while each coloured branch is factor-3 suppressed
in one orientation. Against the *currently admissible* coloured branch, black is instead `-0.004060` lower
(`d=-0.153`). Its best name is therefore **common/invariant route**, not third independent source.

The common route then decompressed recursively. With black offset `k=6m`, one `m mod 5` child in each centre-`mod 5`
row rotates into the exact factor-5 trough `0.145586686`; eligible children average `0.487412541`. This is the
established mod-30 wheel expressed as parent/common-route/child geometry. Matched coprime composite centres reproduce
the red/blue swap (`+0.323995`), proving the shoulders are a general modular lattice; the exact `1.0` centre ridge is
the part specific to completed prime factor survival.

Allowed conclusion: ARA correctly directed attention to orientation, reflection, a shared route and recursive child
decompression. The result is an unusually clean structural crosswalk, not a new prime theorem, prospective predictor
or proof of universal fractality. PN10B remains NULL. Next: freeze `6 -> 30 -> 210` plus one eligible-lane statistic
not mechanically fixed by divisibility, then open a new interval. Full report:
`analysis/primes/PN10C_MOD6_THREE_LANE_COUPLING_REPORT.md`.

## 28. ARA prime square-ridge lab (20 Jul 2026)

**Status:** `EXACT INTERACTIVE CROSSWALK / 24 OF 24 VALIDATION CHECKS PASS / ESTABLISHED INCREMENTAL SIEVE / NOT A NEW SPEED CLAIM.`

The proposed missing vertical relation was made precise as **prime gate size squared**. When a prime `p` is found,
its multiples below `p²` have already been struck by smaller prime children. Its first independently necessary strike
is therefore `p²`, followed by `p²+p`, `p²+2p`, and so on. An integer struck by one or more active children is
composite; a quiet integer becomes the next prime and registers another child.

This is exactly the postponed/incremental Sieve of Eratosthenes. The ARA contribution is a coordinated geometric
reading rather than a new algorithm: horizontal prime periods, the vertical `p²` activation ladder, multi-child
collision multiplicity, and the PN10 reversible factor diameter are displayed together.

The bridge to the factor ridge is exact. At the first new `p` strike,
`x_(p²)(p)=2*log(p)/log(p²)=1`. Thus the square boundary is simultaneously:

- the standard point where gate `p` first adds information not already supplied by smaller gates;
- a self-reflected factor pair `p*p`;
- the exact `1.0` ridge of the PN10 factor sphere.

The phrase “child begins at `p²`” is restricted to **independent sieve responsibility**. It does not deny earlier
multiples of `p`. The squared rung is also `p²`, not the square of a primorial wheel.

The standalone instrument generates all primes through `5,000`. Independent validation recovered `669` primes with
zero mismatches, matched every collision voice to the true active prime divisors, placed every prime square on the
ridge, closed reflected factors to maximum error `4.44e-16`, and verified the later resonance classifications and
music-box mapping. All `24/24` checks passed.

Allowed conclusion: the user's horizontal-child plus vertical-rung-squared geometry maps cleanly and exactly onto
the established incremental sieve. It gives a useful multiview ARA instrument and clarifies how child, current and
adult directions relate in this arithmetic system. Exactness here demonstrates a successful crosswalk; because the
underlying sieve is known, it does not by itself prove universal fractality or improve prime-computation complexity.

Files:

- `analysis/primes/ARA_PRIME_SQUARE_RIDGE_LAB.html`
- `analysis/primes/ARA_PRIME_SQUARE_RIDGE_LAB_README.md`
- `analysis/primes/validate_ara_prime_square_ridge_lab.py`
- `analysis/primes/ARA_PRIME_SQUARE_RIDGE_LAB_VALIDATION.json`

## 29. Prime 510 collective resonance ridge (21 Jul 2026)

**Status:** `EXACT POST-HOC ARITHMETIC IDENTIFICATION / FOUR CHILD PHASES LOCK / COLLECTIVE DIAMETER CLOSES / NOT A SQUARE RIDGE.`

Dylan noticed that node `510` carries four simultaneous child collisions and identified it as the resonance ridge
discussed elsewhere in ARA. The distinction from the square ridge is exact:

\[
510=2\times3\times5\times17
=\operatorname{lcm}(2,3,5,17).
\]

Consequently, all four modular child phases equal zero at 510 and their phase-coherence magnitude is exactly `1`.
This is their fundamental shared period and the first joint collision after child `17` becomes independently active
at `17²=289`.

On the PN10 factor diameter, the four child positions are approximately `0.222362`, `0.352435`, `0.516308`, and
`0.908895`. None equals `1`, because 510 is not a square. Their sum is nevertheless exactly `2`, since their product
is the complete parent `510`. The closest reflected pair is `17×30`, located at
`0.908895 <-> 1.091105`.

ARA reading: **the parent is phase-locked at a collective resonance ridge while the decompressed children remain
asymmetric and together exhaust the declared diameter.** This is the prime-number example of the earlier
resonance-ridge/TE-ARA distinction. A factor square and a collective resonance are two different measurements:

- `49=7²`: one child is self-reflected at factor position `1.0`;
- `510=lcm(2,3,5,17)`: four children complete one shared phase cycle, while no individual child occupies `1.0`.

The modular resonance and logarithmic closure are exact arithmetic. Their identification as another appearance of
the general ARA resonance ridge is a framework crosswalk, not a claim of physical energy resonance or independent
evidence for universal fractality. Full note:
`FableConvo/NOTE_PRIME_510_RESONANCE_RIDGE_2026-07-21.md`.

### Instrument implementation (21 Jul 2026)

The interactive square-ridge instrument was extended into a resonance discriminator without changing its exact
sieve engine. It now separates five geometrically different events: prime-child square activation, ordinary
multi-child collision, fundamental collective closure, harmonic recurrence of an earlier child set, and the
consecutive-prime primorial rung.

The distinction is operational. For an event with active distinct child primes `P`, let `b=product(P)`. A
fundamental closure requires at least three voices and `b=n`; a harmonic repeat has at least three voices, `b<n`,
and `b` divides `n`. Primorial rungs are the special fundamental closures whose children are all consecutive primes
from 2. The instrument therefore labels 510 as a four-child fundamental closure, 1,020 as its repeat, 3,570 as a
new five-child closure, and 4,620 as a five-child repeat of 2,310.

The same child lanes now carry a fixed ascending C-major note assignment. A node sounds only the active children
that strike it, as a short low-to-high arpeggio; a quiet prime is a rest. Thus 510 audibly preserves its four-child
decomposition as `C4-D4-E4-B4`. This is sonification of the exact modular event inventory, not an additional
mathematical test or a claim that musical harmony predicts primes.

Independent validation now passes `24/24` checks. This is an exact visualization of established arithmetic
structure and an improved ARA discriminator; it does not change PN10B's predictive null or create a new prime
theorem.

## 30. Music-box decompression and resonance families (21 Jul 2026)

**Status:** `POST-HOC EXACT ARITHMETIC / ASSIGNED SONIFICATION / STRUCTURAL CROSSWALK / NOT PREDICTIVE EVIDENCE.`

The music-box layer assigns ascending C-major notes to the active prime-child lanes: `2=C4`, `3=D4`, `5=E4`,
`7=F4`, and onward through `67=G6`. A composite node sounds the exact children that strike it; a quiet prime is a
rest. The arithmetic event inventory is exact, but the pitch assignment is conventional. Pleasant or complete
musical intervals therefore cannot be counted as evidence.

The first visible collision orders occur at nodes `2, 4, 12, 30, 210, 2310` for zero through five voices. Through
5,000 the corresponding node counts are `669, 1964, 1270, 808, 281, 7`. The 510 family demonstrates the difference
between identity and recurrence: `510=2*3*5*17` is a four-child fundamental closure; its later multiples repeat that
child set until a new child joins. At `3570=2*3*5*7*17`, the added child creates a new five-child fundamental closure.

Several familiar display dimensions lie exactly on the `30=2*3*5` repeat family, including 720, 1080, 1440, 1920,
2160, 2880, 3840, 4320 and 7680; `1680=210*8`. The nearby 510/binary pattern is also exact but elementary:
`510k=512k-2k`. These are useful engineering/arithmetic crosswalks, not independent ARA predictions.

## 31. The 714-715 complementary resonance pair (21 Jul 2026)

**Status:** `EXACT POST-HOC BINARY CLOSURE / KNOWN RUTH-AARON PAIR / ARA CROSSWALK.`

The consecutive fundamental closures

\[
714=2\times3\times7\times17,
\qquad
715=5\times11\times13
\]

contain disjoint child sets whose union is the first seven primes. Under the assigned notes, they partition the first
C-major octave: `714 -> C4-D4-F4-B4` and `715 -> E4-G4-A4`. Their distinct-prime sums also balance at 29, making
them a known Ruth-Aaron pair.

Their product is the first-seven-prime primorial:

\[
714\times715=510510=17\#.
\]

On that parent factor diameter their coordinates are `0.9998935126888657` and `1.0001064873111343`, summing exactly
to 2. Thus two different child identities occupy opposite sides of the parent ridge and close the whole parent. The
arithmetic is exact; the name **complementary ARA resonance pair** is the framework interpretation.

## 32. The 1274-1276 multiplicity-echo triple (21 Jul 2026)

**Status:** `EXACT POST-HOC MULTIPLICITY PATTERN / FIRST THREE-NODE 12-DIVISOR RUN / INSTRUMENT LIMIT IDENTIFIED.`

The three consecutive nodes factor as

\[
1274=2\times7^2\times13,
\quad
1275=3\times5^2\times17,
\quad
1276=2^2\times11\times29.
\]

Each has the exponent form `p^2*q*r`, three distinct children, four factors with multiplicity and exactly 12 positive
divisors. Node 1274 begins the first run of three consecutive integers all having 12 divisors.

The current lab keeps distinct active children, so it hears the three nodes as harmonic repeats but suppresses the
repeated child: respectively 7/F4, 5/E4 and 2/C4. The missing content is recovered by
`n=rad(n)*(n/rad(n))`. On the factor diameter, the distinct-child sum plus the repeated-child echo closes exactly at
2 for every node. This recommends a later sonification option that repeats or weights the doubled note; it does not
alter the exact sieve or make a prediction claim.

## 33. The 1885-1887 three-by-three lock (21 Jul 2026)

**Status:** `EXACT POST-HOC THREE-PARENT CLOSURE / UNIQUE THROUGH 5000 UNDER THE LAB RULE / INFORMATION³ CANDIDATE.`

The consecutive squarefree nodes

\[
1885=5\times13\times29,
\quad
1886=2\times23\times41,
\quad
1887=3\times17\times37
\]

are each fundamental three-child resonances under the exact `p^2<=n` activation rule. Their nine children are all
different. Multiplying the three identities produces one nine-child parent:

\[
N=1885\times1886\times1887=6,708,492,570=1886^3-1886.
\]

Their parent coordinates are `0.6666197954037039`, `0.6666666749500042`, and `0.6667135296462919`, which sum
exactly to 2. Through node 5,000, 1885 is the only start of three consecutive fundamental three-child events under
the instrument's rule.

ARA reading: three child factors close each local identity, then three adjacent identities close a parent retaining
nine independent child lanes—a literal `3 x 3` hierarchical lock. This is a strong Information³ illustration, but
it was recognised after opening the data. The algebraic closure follows once the factors are known and is not yet a
prospective prime result.

The complete definitions, arithmetic, plain-language interpretations, caveats and `18/18` independent checks are in
`analysis/primes/ARA_PRIME_RESONANCE_LOCKS_2026-07-21.md`. Reproduction is provided by
`analysis/primes/validate_prime_resonance_locks.py` and
`analysis/primes/ARA_PRIME_RESONANCE_LOCKS_VALIDATION.json`.

## 34. PN11 Phi vertical handover through resonance families (21 Jul 2026)

**Status:** `NOT SUPPORTED [PRE-REGISTERED FRESH TARGET] / EXACT TWO-SHARE AND LOCK-EXPANSION CROSSWALK RETAINED.`

Dylan proposed that fundamental resonance and harmonic repetition travel vertically through the rungs as Phase A
and Phase B, pass through Phi, and support that progress by forming new information locks. The accepted PN11
translation followed one fundamental squarefree child product `B` through its pure repeat multiples until the first
absent prime `q` joined.

The resulting ARA decomposition is exact:

\[
A_B(k)=\frac{2\log B}{\log(kB)},
\qquad
E_B(k)=\frac{2\log k}{\log(kB)},
\qquad
A_B(k)+E_B(k)=2.
\]

Every multiplier below `q` preserves the child set, while `qB` adds exactly one child and becomes a larger fundamental
lock. Thus the **lock -> harmonic path -> expanded lock** geometry is recovered without approximation.

The registered Phi-location claim failed on all `45,768` eligible families in the fresh interval
`[10,000,000,11,000,000)`. The expansion coordinate

\[
X_B=\frac{2\log B}{\log(qB)}
=\frac{2}{1+\log q/\log B}
\]

had mean `1.853770` and median `1.872585`. Phi ranked sixth among eight frozen landmarks by mean distance
(`0.235736`); `9/5=1.8` ranked first (`0.056714`). The paired best-rival-minus-Phi difference was `-0.179022`, with
100-block bootstrap interval `[-0.179105,-0.178939]`. Both fixed target halves repeated the negative direction.
No target family reached Phi before its first child expansion, and the frozen `phi+-0.025` window contained zero
path exposures and zero events.

The reason is analytic. Exact Phi placement requires `q=B^(1/phi^3)`. At `B` near ten million that would require
`q` near 45, while the observed first missing children were 3 through 17, with median 3. For small `q` at increasing
scale, `X_B` tends toward 2 rather than remaining at Phi. Including immediate `q=2` families moved the median still
closer to 2, so the primary exclusion was favourable to Phi.

The 510 example remains a valid local crossing but not a handover location: its old-lock path crosses Phi between
multipliers 4 and 5, while child 7 joins at multiplier 7 when the old-lock coordinate is `1.524246`. Likewise, the
canonical primorial ladder crosses from below Phi to above it once between bases 30,030 and 510,510; monotone passage
through an interior landmark is not evidence that the landmark causes the transitions.

Allowed conclusion: prime resonance families possess an exact reversible lock/echo coordinate and exact nested
information-lock expansion. Their first expansion is governed by the scale-dependent ratio `log(q)/log(B)`, not by
a universal Phi location in this representation. This rejects PN11's specified observable, not every possible Phi
handover meaning or ARA as a whole. Independent validation passed `26/26` checks. Full report:
`analysis/primes/PN11_PHI_VERTICAL_HANDOVER_REPORT.md`.

## 35. PN12 larger angular carrier on the prime ladder (21 Jul 2026)

**Status:** `NOT SUPPORTED [PRE-REGISTERED FRESH TARGET] FOR BOTH 137.5° AND 36° / EXACT ADJACENT PHASE RETAINED.`

Dylan's next refinement placed the local prime spheres and logarithmic rung ladder on a much larger possible Phi
wave. Rather than assign Phi to that wave, PN12 used the current primorial lock's raw position on its next absent prime
child:

\[
B_m=\prod_{j=1}^m p_j,
\qquad q_m=p_{m+1},
\qquad u_m=(B_m\bmod q_m)/q_m,
\qquad \delta_m=(u_{m+1}-u_m)\bmod1.
\]

The signed primary was the golden-angle step `137.507764°`. Dylan added 36° before the run; it received a separate
frozen verdict and could not rescue the primary. Controls included the reverse golden angle, `1/e`, nearby rational
angles, polygon angles, anti-phase and zero turn.

Across 4,000 untouched upward steps on rungs 1,000–5,000, the measured increment coherence was only `R=0.014186`,
almost identical to order-scrambled controls (mean `0.013812`). The circular mean direction was `16.134746°` and was
unstable across halves. Golden ranked 9/12. Thirty-six degrees ranked first, but by only `0.000631` turns over zero;
its bootstrap interval crossed zero and the distribution had no carrier coherence. Both registered claims are
`NOT SUPPORTED`.

The raw phases and steps broadly covered the circle, with means and medians near one-half and quartiles near one-quarter
and three-quarters. Thus the correct geometry statement is not “36° won”; it is that the exact adjacent-child phase
projection behaves like a broadly dispersed circular sequence rather than a one-angle carrier. A curved/nonconstant
meta-wave or a full residue-torus observable would be a new claim. Validation reproduced every target value and passed
`22/22` checks. Full report: `analysis/primes/PN12_PHI_CARRIER_REPORT.md`.

### Post-result Pi-leak / one-thruster probe

Dylan noticed that PN12's `R=0.01419` resembled an earlier leak-scale number and proposed that a small uncancelled
remainder might propel the larger circle like a rocket with one working thruster. The analogy translates cleanly: a
real thrust requires a nonzero **signed** mean vector whose magnitude plateaus and whose direction remains stable as
more rungs are included.

The open-target post-hoc check instead matched the circular sampling floor. For 4,000 unaligned directions,
`E[R]~sqrt(pi)/(2sqrt(4000))=0.0140125`; observed `R=0.0141862`, or `R*sqrt(N)=0.8972` against the null coefficient
`0.8862`. Prefix magnitudes fell toward the `1/sqrt(N)` curve, and directions wandered across disjoint blocks. The
defined Pi-leak values are `pi-3=0.141592654` and `(pi-3)/pi=0.045070341`; reaching `0.014159265` requires the
unregistered post-hoc operation `(pi-3)/10`. A PN10B child-coupling mean near `-0.01408` is a different signed metric
and also appeared in composites.

Therefore the one-thruster reading is `NOT SUPPORTED` on the current open data. The useful future falsifier is now
explicit: on fresh higher rungs, a thrust residual must retain a predeclared direction and plateau above the
`1/sqrt(N)` cancellation floor.

## 36. PN13 decimal-rung leak test and the located adult wavelength (21 Jul 2026)

Dylan noticed that `pi-3=0.14159`, PN12's `R=0.01419` and PN10B's signed coupling near `-0.01408` might differ by
one decimal digit per ARA rung. PN13 froze the literal relation `L_(k+1)=L_k/10` on two unchanged prime appearances,
with aggregation size fixed so ordinary `1/sqrt(N)` cancellation could not impersonate a rung.

The amplitude claim failed both fresh readings. PN12 fixed-window vector magnitudes across ladder starts `10^3`,
`10^4`, `10^5` were `0.014186`, `0.015127`, `0.003383`; ratios `1.066` and `0.224`, with direction shifts `85.65°`
and `40.80°`. PN10B signed child coupling across fixed one-million-integer intervals at `4*10^8`, `4*10^9`,
`4*10^10` was `+0.008856`, `-0.014076`, `+0.168838`. The fixed Pi sequence failed outside its already-seen middle
point. Registered verdicts: `NOT SUPPORTED`; independent arithmetic validation `19/19`.

The failure exposed a different native relation. Adjacent child gates `q,r` have exact joint closure
`lcm(q,r)=qr`. Because PN10B selected gates near `n^0.45`, their median exact-repeat wavelength progressed
`54.10m -> 436.60m -> 3.477b`, factors `8.07` and `7.96`, matching `qr~n^0.9` and the decimal-rung factor
`10^0.9=7.943`. At the full factor boundary `q,r~sqrt(n)`, exact joint closure scales as `qr~n`: one decimal number
rung gives approximately one additional wavelength digit, with local prime gaps controlling the shorter relative-
phase drift envelope.

Thus the “extra digit” is not supported in residual strength. Its clean mathematical home in this construction is
the **adult joint-cycle length generated by two child periods**. This is a post-hoc analytic crosswalk, not a rescue
of PN13. The next clean test should express child coupling against
`theta_(q,r)(n)=n(r-q)/(qr) mod 1` and ask whether untouched scales collapse onto the same 0–2 phase curve, with
distant and shuffled gate-pair controls. Full report: `analysis/primes/PN13_DECIMAL_RUNG_LEAK_REPORT.md`.

### TE-ARA closure back-translation

Dylan identified `qr~sqrt(n)*sqrt(n)~n` as the prime example of the original ARA `2.0` / TE-ARA `2` idea: two
half-scale child waves close the parent. Codex initially flattened that into a required `1+1` partition; Dylan's
canonical correction is that **TE-ARA is the same ARA geometry viewed as a fixed total 2**. The pure identity is
Phase A + Phase B. In `0.25+1.25+0.50=2`, the `0.50` is contextual coupling in the real observation, not an extra
pure pole; `1+1=2` is the symmetric pure ridge. Keep the typed
coordinates separate: `sqrt(n)` is half the parent log-scale exponent, component allocations are parent-ledger edge
weights, and period multiplication is not energy addition. When a component is opened as its own identity, its
internal TE-ARA ledger renormalises to 2.
