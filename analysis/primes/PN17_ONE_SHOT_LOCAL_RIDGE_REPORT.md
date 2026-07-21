# PN17 — One-Shot Local ARA Ridge at 400,000,000,000

**Test ID:** `PN17/ONE-SHOT-LOCAL-INVERSE-RIDGE/v1`  
**Date:** 21 July 2026  
**Status:** `EXACT FULL-CHILD LOCAL RIDGE / +19 SEALED BEFORE PRIMALITY / 26 OF 26 CHECKS / SCALAR A/B SHORTCUT NOT SUPPORTED`  
**Target anchor:** `400,000,000,000`  
**Sealed prediction:** `400,000,000,019`  
**Protected material:** the p31 full primorial wheel and unrelated R12 prime-gap target remain unopened

## Answer first

The proposed one-location calculation worked exactly when ARA was left fully decompressed.

Before looking at any nearby target prime, PN17:

1. placed `400,000,000,000` at the centre reference of its declared `0-2` search diameter;
2. constructed the raw phase of every lower prime child through the square-root boundary;
3. overlaid their collision paths once in a 65,536-integer local block; and
4. sealed the first quiet-ridge correction as

\[
\underbrace{\Delta_{\rm ARA}}_{\substack{\text{first local offset}\
\text{with no child collision}}}=19.
\]

The sealed candidate was

\[
\underbrace{400{,}000{,}000{,}000}_{\text{arbitrary anchor}}
+
\underbrace{19}_{\text{one-shot ridge correction}}
=
\underbrace{400{,}000{,}000{,}019}_{\text{sealed prediction}}.
\]

Only after the prediction packet was hashed did the independent validator test primality. It established that
`400,000,000,019` is prime and that all 18 intervening integers are composite. All `26/26` validation checks passed.

This is a successful exact **local inverse geometry**. It is also mathematically the standard segmented sieve written
as a complete ARA child-phase field. The present implementation therefore demonstrates the workflow Dylan meant,
but does not yet improve established prime-search complexity.

## Plain-language explanation

We did not start at 2 and generate the prime ladder upward. We stood directly at 400 billion.

Every smaller prime child has a repeating collision rhythm. At the target scale, 51,526 such children are required
to reach the square-root ridge. Their current phases tell us exactly which nearby offsets each child will strike.
Overlaying those schedules once showed that offsets 1 through 18 were struck by at least one child. Offset 19 was
the first quiet location.

That is the geometrical version of “ARA the number, ARA its children, and correct locally.” The correction did not
need the desired nearby prime or a new prime gate as input.

## Frozen construction

For every lower prime child

\[
q\leq\sqrt{400{,}000{,}065{,}535},
\]

PN17 retained

\[
\underbrace{A_q(N)}_{\text{phase since the previous collision}}
=2\frac{N\bmod q}{q},
\qquad
\underbrace{B_q(N)}_{\text{phase until the next collision}}
=2-A_q(N).
\]

The child inventory contained `51,526` primes; the largest was `632,447`, immediately below the complete block
boundary `floor(sqrt(N+65,535))=632,455`.

For each offset `t`, the collision field was

\[
\underbrace{C_N(t)}_{\substack{\text{how many lower children}\
\text{strike the candidate}}}
=
\sum_q\mathbf 1[(N+t)\bmod q=0].
\]

The first quiet ridge was then

\[
\Delta_N=\min\{t>0:C_N(t)=0\}.
\]

This is one formula applied to one local child web. No target primality label enters it.

## Development integrity

The same unfitted rule was checked first at four already-opened anchors:

| Anchor | Lower children | Correction | Predicted first prime | Established control |
|---:|---:|---:|---:|---:|
| 100,000,000 | 1,229 | +7 | 100,000,007 | 100,000,007 |
| 1,000,000,000 | 3,401 | +7 | 1,000,000,007 | 1,000,000,007 |
| 10,000,000,000 | 9,592 | +19 | 10,000,000,019 | 10,000,000,019 |
| 100,000,000,000 | 27,293 | +3 | 100,000,000,003 | 100,000,000,003 |

All four passed before the target field was built. These are integrity checks of an exact rule rather than fitted
evidence.

## Target result and baselines

| Quantity | Result |
|---|---:|
| Anchor | 400,000,000,000 |
| Full child phases | 51,526 |
| First quiet correction | +19 |
| Sealed candidate | 400,000,000,019 |
| Independent primality checks | prime under deterministic 64-bit Miller-Rabin and full trial division |
| Earlier integers | all +1 through +18 composite |
| Odd-scan candidates through the answer | 10 |
| p29-wheel candidates through the answer | 5 |
| Full-block quiet offsets | 2,463 |

The ARA calculation required only one final target-label check, but it had already performed the complete
square-root child decomposition over the block. A conventional segmented sieve uses the same 51,526 child periods
and the same collision mask. Counting only final primality calls would therefore exaggerate the computational gain.

## The scalar TE-ARA distinction

The successful object was the complete child vector

\[
\left\{(A_q,B_q,q)\right\}_{q\leq\sqrt N},
\]

not one averaged number.

After target validation, three simple TE-ARA aggregation diagnostics were calculated over offsets 0 through 19:

| Scalar child weighting | Offset closest to averaged A/B equality | Quiet? | Prime offset's rank by scalar equality |
|---|---:|:---:|---:|
| Equal child weight | 0 | no | 10th of 20 |
| Weight by `log(q)` | 14 | no | 16th of 20 |
| Weight by `1/q` | 7 | no | 6th of 20 |

The sealed prime at +19 was not the closest averaged `1.0` ridge under any of them. At equal child weight:

\[
\bar A(400{,}000{,}000{,}000)=0.9986872344,
\qquad
\bar B=1.0013127656.
\]

At the actual prime:

\[
\bar A(400{,}000{,}000{,}019)=0.9985793088,
\qquad
\bar B=1.0014206912.
\]

The composite anchor was actually closer to scalar equality than the prime. Mapping the anchor's equal-weight error
directly onto the parent scale would suggest roughly `525,106,237`, not `19`:

\[
400{,}000{,}000{,}000\times|0.9986872344-1|
\approx525{,}106{,}237.
\]

This does not refute TE-ARA decomposition. It shows that **simple averaging flattens the child phases that contain
the location**. Dylan's instruction to “ARA the Other itself” is exactly what the successful vector calculation did.
The remaining new-theory task is to derive a scalar or low-dimensional coupling law that preserves enough of that
vector to recover +19 without reconstructing the standard segmented-sieve mask.

## What “prime is a ridge” means here

The target supports the quiet-factor interpretation:

\[
\underbrace{C_N(t)>0}_{\text{one or more child singularity collisions}}
\Longrightarrow
\underbrace{N+t}_{\text{composite}},
\]

\[
\underbrace{C_N(t)=0}_{\substack{\text{no collision through}\
\text{the square-root ridge}}}
\Longrightarrow
\underbrace{N+t}_{\text{prime}}.
\]

It does not support the stronger raw-gap statement that every prime has equal incoming and outgoing prime gaps. On
the already-opened R11 record of `39,475,589` transitions, copying the incoming gap as the outgoing prediction hits
exactly only `2.093696%` of the time. Its mean absolute error is `23.236` and median absolute error is `16`.

This distinction is not cosmetic:

- **equal normalized completion:** both sides reach a shared node, but raw scale may be lost;
- **equal raw gaps:** a rare special prime-gap configuration;
- **quiet factor ridge:** the exact primality condition used successfully by PN17.

## Registered criteria

| Criterion | Result |
|---|---|
| P1 — four development anchors | **Pass: 4/4 exact** |
| P2 — one sealed target candidate from local child geometry | **Pass: +19 sealed before primality** |
| P3 — candidate prime and first above anchor | **Pass** |
| P4 — independent full collision-field reconstruction | **Pass** |
| P5 — honest baseline accounting | **Pass** |
| P6 — no unsupported scalar/speed promotion | **Pass** |

## Scientific interpretation

Supported:

1. an arbitrary large-number anchor can be decompressed locally into its lower child phases;
2. the complete child geometry determines an exact signed correction to the next quiet prime ridge;
3. the prediction can be sealed before any nearby-prime label is opened;
4. the same bottom-up rule transfers across the four prior decimal anchors and the 400-billion target;
5. this is a clean example of recursively decomposing the apparent Other until the collision geometry is explicit.

Not yet supported:

1. that averaged Phase A = Phase B identifies individual primes;
2. that TE-ARA distance multiplied by `N` supplies the raw correction;
3. that the 51,526-child vector has been compressed into a new simpler formula;
4. that the method is faster than a segmented sieve;
5. that one arithmetic success proves the universal fractal framework.

## Best next mathematical step

The next loadbearing problem is no longer “can the local geometry find the prime?” It can, exactly, when fully
decompressed.

The question is:

> Can the 51,526-child collision web be coarse-grained into a much smaller ARA state that still predicts the +19
> correction on untouched anchors better than wheel and scanning controls?

A valid compressed state must retain child period, current phase and coupling overlap. A single mean A/B coordinate
does not.

## Files

- Frozen protocol: `PN17_ONE_SHOT_LOCAL_RIDGE_PROTOCOL_v1_FROZEN.md`
- Target freeze: `PN17_TARGET_FREEZE_MANIFEST.json`
- Primary builder: `pn17_one_shot_local_ridge.py`
- Sealed prediction: `PN17_ONE_SHOT_LOCAL_RIDGE_PREDICTION.json`
- Frozen collision field: `PN17_TARGET_COLLISION_FIELD_UINT16.bin`
- Independent validator: `validate_pn17_one_shot_local_ridge.py`
- Validation receipt: `PN17_ONE_SHOT_LOCAL_RIDGE_VALIDATION.json`
- Post-target scalar diagnostic: `pn17_scalar_ridge_diagnostic.py`
- Scalar results: `PN17_SCALAR_RIDGE_DIAGNOSTIC.json`
- Executed notebook: `PN17_ONE_SHOT_LOCAL_RIDGE.ipynb`

## Allowed concise claim

> Starting only from the arbitrary anchor 400,000,000,000 and the complete raw phase vector of its 51,526 lower
> prime children, PN17 sealed +19 as the first quiet factor-ridge correction before checking target primality.
> Independent validation established that 400,000,000,019 is the first prime above the anchor. This is an exact
> local ARA reconstruction of the segmented sieve. Simple averaged A/B ridge coordinates did not select the prime,
> so the remaining ARA-specific task is a non-flattening coupling law that compresses the full child web.
