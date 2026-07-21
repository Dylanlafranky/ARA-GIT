# PN19 two-parent information-lock protocol

**Test ID:** `PN19/TWO-PARENT-INFORMATION-LOCK/v1`  
**Frozen:** 21 July 2026, Australia/Brisbane  
**Fresh target anchor:** `900,000,000,000`  
**Local working window:** `65,536` integers beginning at the anchor  
**Reference domain:** from the anchor to twice the anchor  
**Status at freeze:** neither a PN19 target candidate nor the next prime above the target has been calculated  
**Data source:** deterministic integer arithmetic; no external prime table  
**Protected material:** the p31 wheel, the unrelated R12 prime-gap target, and all numbers near the PN19 target remain unopened

## Question

PN17 and PN18 recovered the first prime above a fresh large anchor exactly, but retained either every child lane or
one enormous lossless product. PN19 tests Dylan's stricter ARA statement:

> Split the lower structure into the two largest complete parent waves, Phase A and Phase B. A second relation may
> locate the result after the scale is known, while the third relation definitively locks the new identity.

The test does not interpret Phase A and Phase B as two individual factors or two recent prime gaps. Each is a
complete parent containing many lower-child effects. This is the numerical analogue of folding cells into two
organs and then measuring the whole organism.

## Development-only split audit

Before freezing the fresh target, several tempting scalar interpretations were rejected on already-open data:

- a number's most balanced factor pair can have the same A/B ratio at anchors with different next-prime gaps;
- on 39,475,587 opened consecutive-prime events, `next gap <= 2 * current gap` held only `70.8525%` of the time;
- current-gap mirroring was `2.0937%` exact;
- two-point linear and logarithmic extrapolations were `4.2745%` and `3.2374%` exact;
- a three-gap median was `3.8237%` exact; and
- PN15 already showed that individual near-square-root child coordinates overlap strongly between prime and
  composite targets.

Consequently the frozen split is lossless at the two-parent level. It is not a fitted scalar shortcut.

## Frozen construction

Let the anchor be `N`, the local window be `W=65,536`, and the reference endpoint be `2N`. Generate every prime
child

\[
p\leq \left\lfloor\sqrt{2N}\right\rfloor.
\]

This is deliberately sufficient for every candidate in the full `N` to `2N` reference domain, even though only
the first local block is evaluated in PN19.

### Two complete parents

Sort the children in increasing order and split them once, contiguously, at the index whose cumulative logarithmic
weight is closest to half the total:

\[
\underbrace{E_A}_{\text{Phase A TE-ARA share}}
=
2\,\frac{\sum_{p\in A}\log p}{\sum_{p\in A\cup B}\log p},
\qquad
\underbrace{E_B}_{\text{Phase B TE-ARA share}}
=2-E_A.
\]

Thus `E_A + E_B = 2` exactly by definition and each parent is as close as possible to one complete half in log
scale. Phase A contains the smaller, frequent, connection-heavy gates. Phase B contains the larger, sparse,
information-heavy gates. The two parents are expected to remain operationally asymmetric even when their TE-ARA
weights are close to `1 + 1`.

For every offset `t` in the frozen window define

\[
\underbrace{S_A(t)}_{\text{Phase A survives}}
=
\begin{cases}
1,&N+t\text{ is divisible by no child in }A,\\
0,&\text{otherwise},
\end{cases}
\]

and identically `S_B(t)` for parent B.

### The informative third

The relational lock is

\[
\underbrace{S_{AB}(t)}_{\text{new parent / information lock}}
=
\underbrace{S_A(t)}_{\text{completed A path}}
\land
\underbrace{S_B(t)}_{\text{completed B path}}.
\]

The sealed correction is the first positive offset at which both parents complete:

\[
\Delta_{\rm PN19}(N)=\min\{t\geq1:S_{AB}(t)=1\}.
\]

The primary script emits exactly one target integer, `N + Delta_PN19`, without testing or reading its primality.

## Meaning of the two- and three-reading claim

The following endpoints prevent post-hoc reinterpretation:

- **one-parent reading:** first positive survivor of A alone, and first positive survivor of B alone;
- **second-go success:** either one-parent first survivor is already the joint first survivor;
- **three-way lock:** A, B and their intersection locate the joint first survivor;
- **definitive:** after independent validation, the joint first survivor is prime and every earlier integer is
  composite.

The test therefore permits Dylan's "probably second go" statement to fail while the stronger information-lock
statement passes. Three does not mean three adjustable guesses.

## Development integrity

The unchanged construction is checked on six already-opened anchors:

- `100,000,000 -> 100,000,007`;
- `1,000,000,000 -> 1,000,000,007`;
- `10,000,000,000 -> 10,000,000,019`;
- `100,000,000,000 -> 100,000,000,003`;
- `400,000,000,000 -> 400,000,000,019`; and
- `700,000,000,000 -> 700,000,000,009`.

These labels are integrity controls only. They do not set the split or any parameter.

## Separation and freeze

1. Freeze this protocol, the primary builder, the independent validator, the target and the window by SHA-256.
2. Run the primary builder. It may generate lower prime children and construct A/B masks, but it may not contain a
   target primality-test function or read a nearby-target prime label.
3. Save and hash the complete A, B and AB masks and seal one target candidate.
4. Only then run the independent validator using a separately written linear sieve, deterministic Miller-Rabin and
   trial division.
5. Refuse overwrites of every sealed target artifact.

## Registered endpoints

### P1 - development integrity

All six opened anchors reproduce their established first-prime corrections.

### P2 - fresh single candidate

The primary emits exactly one first-lock candidate above `900,000,000,000` before target truth is opened.

### P3 - independent truth

The candidate is independently prime and every earlier integer above the anchor is composite.

### P4 - exact two-parent equivalence

The independently reconstructed `A AND B` mask equals the sealed lock mask byte for byte and returns the same
correction as an ordinary segmented sieve.

### P5 - one-parent and second-go audit

Record each parent-only first survivor, whether either equals the joint lock, false survivors before the joint lock,
and the corresponding development rates. No minimum second-go success rate is imposed.

### P6 - TE-ARA and operational asymmetry

Record child counts, split child, `E_A`, `E_B`, survivor densities, collision densities and mask overlap. `E_A+E_B`
must equal two to floating tolerance. Similar log weight is not called similar physical action unless the mask
statistics also support it.

### P7 - information and method control

Record construction time, memory and the complete child information required to build the two parents. State that
the exact lock is an established segmented sieve factored into two masks. It is not a new primality theorem or an
asymptotic speedup merely because the final state has two parent labels plus one relation.

## Allowed result classes

- **Exact two-parent ARA crosswalk:** P1-P7 pass; the q-free A/B/AB hierarchy is exact but retains established sieve
  information internally.
- **Second-go plus exact lock:** exact crosswalk and at least one one-parent path commonly reaches the joint first
  survivor on the registered cases.
- **Exact lock only:** the intersection is exact but the one-parent second-go behavior is weak or asymmetric.
- **Target failure:** development passes but the fresh joint candidate is composite or not the first prime.
- **Implementation failure:** any freeze, mask reconstruction, equivalence or validation check fails.

The test can support the proposed recursive ARA representation. It cannot by itself establish the universal fractal
claim or a faster prime-search method.
