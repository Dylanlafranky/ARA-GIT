# Audit — four recent muon tests against established muon physics

**Date:** 19 August 2026
**Auditor:** Claude (Opus 5), independent of the runs
**Selected:** T403, T406/T407, T408, T409 — the 18 August cluster, the most recent
and highest-claim tests in the series.
**Sources checked against:** ledger and `CLAIMS_STATUS.md` entries; COHERENT
stopped-pion source physics; muon decay kinematics.

---

## 0. Established physics baseline

The COHERENT CsI source is π⁺ decay at rest at the SNS:

```
π⁺ → μ⁺ + ν_μ           τ_π = 26 ns      PROMPT, monoenergetic 29.8 MeV
μ⁺ → e⁺ + ν_e + ν̄_μ     τ_μ = 2.197 μs   DELAYED
```

**The single most important consequence for this series:** `ν_e` and `ν̄_μ` are
emitted in the *same* muon decay. They share one parent and therefore one decay
constant. Their **emission-time distributions are identical exponentials**.

Established flavour separation at stopped-pion sources works by **prompt versus
delayed** — the 26 ns / 2.2 μs contrast — and *not* by separating `ν_e` from `ν̄_μ`,
which timing alone cannot do at any resolution.

---

## 1. T403 — reverse detector-to-muon component lineage

**Reported:** detector footprint matches delayed components with centred cosines
`anti_nu_mu 0.9569`, `delayed total 0.9549`, `nu_e 0.9503`; the two neutrino shapes
are themselves collinear at `0.99736`.

### Finding 1.1 — the collinearity is a theorem, not a resolution limit

The report treats the `0.99736` collinearity as an obstacle its method encountered.
It is not. Both delayed neutrinos are products of the same `μ⁺` decay with the same
`τ_μ`, so their time profiles **must** be near-identical. No timing-based method
— ARA, likelihood, machine learning, anything — can separate them. This is forced
by the decay chain.

**Consequence:** the three-way ranking `0.9569 / 0.9549 / 0.9503` spans `0.0066` on
quantities that are `99.7%` collinear. Those rankings carry **no information about
flavour**, and presenting them in rank order invites a reader to conclude a flavour
was identified. The report's own verdict ("does not distinguish the two neutrino
children") is correct but under-stated — it should say *cannot*, and say why.

**Required:** replace "does not distinguish" with the physics reason, and either drop
the per-flavour cosines or mark them explicitly as non-discriminating.

### Finding 1.2 — what the result actually establishes

Cosine `≈0.955` against the delayed branch as a whole, with unshifted alignment
ranking `1/8`, is a real match to the **delayed release envelope**. That is a match
to the muon lifetime, which is the dominant timing structure in the archive and is
known to five decimal places. The honest statement is that the coordinate recovers
`τ_μ`-shaped delayed structure — which is a validity check on the coordinate, not a
discovery about neutrinos.

The report's own adverse numbers support this reading and are correctly retained:
median resampled cosine `0.315`, 95% interval `[−0.660, 0.814]`, only `15.95%`
reaching `0.65`.

---

## 2. T406 / T407 — grandchild quarter and individual transfer

**Reported:** proposed `0.5 + 0.25 = 0.75`; corrected primary crest `0.706306`
(`82.52%` of the quarter interval); transfer to 2,109 event-linked records
**NOT SUPPORTED**.

### Finding 2.1 — the headline crest is not the centre of its own split distribution

```
headline "primary crest"          0.706306
median crest across 20 splits     0.948276
range across splits               0.640380 – 1.057814
within 0.75 ± 0.10                7/20 = 35%   (gate required 75%)
```

The report leads with `0.706306` while the median split lands at `0.948276` — a
displacement of `0.24`, larger than the entire `0.25` interval the claim is about.
`0.706306` is one split's value, not a stable estimate, and the split distribution
does not centre near it or near `0.75`.

**Required:** report the split median and range in the same sentence as the headline
crest, every time it appears. As written, `CLAIMS_STATUS.md` line 81 quotes
`0.706306` as "the corrected primary population crest" with the failed replication
several lines later.

### Finding 2.2 — check `0.706306` against `1/√2`

```
0.706306
0.707107 = 1/√2      difference 0.000801
```

That is close enough to warrant an explicit check, particularly because **T404
already found one implementation error in this exact coordinate chain** (linear
versus cumulative-ARA bin mapping, which produced the spurious `0.532` crest). If
any step of the construction contains an RMS, a quadrature sum, or a
half-power/equal-area boundary, `1/√2` appears mechanically and would not be a
measured feature.

**Required:** trace whether `1/√2` can enter the coordinate by construction. If it
can, the crest needs re-deriving. If it cannot, record that the proximity is
coincidence and move on.

### Finding 2.3 — the individual rejection is clean and should be foregrounded

Mean NLL improvements `−0.00000282` and `−0.00051254`, both intervals crossing zero,
neither improving both runs, permutation gates failed. That is a decisive negative
on a well-specified claim, and it is the strongest result in the four audited. It
rejects a static incoming detector ratio as an individual release clock.

---

## 3. T408 — nested parent and child windows

**Reported:** directionally positive, frozen rule **not supported**.

### Finding 3.1 — correctly called

```
MP−MN            +0.00237581       both runs positive
vs wrong-lineage +0.00103748       geometric control beaten
AUC              0.51594 → 0.54431
12-block CI      [−0.00099095, +0.00513850]   crosses zero
permutation p    0.175165
```

Three of five gates passed and you called it not supported. Correct.

### Finding 3.2 — the AUC should be stated in context

`MP` at `0.51594` is essentially chance. So the effect is a move from *chance* to
*barely above chance*, on `62/527` positives. With that base rate and that AUC, the
permutation result is what should be expected. Worth stating so the "+0.0024 log-loss,
both runs positive" line cannot be quoted as encouraging on its own.

---

## 4. T409 — chronological parent-ridge tracking

**Reported:** three bands recovered (`0.761`, `1.041`, `1.395`); the hypothesised
travelling upper ridge **not supported** (`p = 0.7455`); R2 displacement exceeds both
shuffle controls (`p = 0.0164`).

### Finding 4.1 — R2 needs a multiple-comparison statement

Three zones were frozen and tested. Bonferroni across three:

```
R2   p = 0.0164  →  0.049   marginal
R1   p = 0.0704  →  0.211
R3   p = 0.7455  →  1.0
```

R2 survives correction but only just. The report calls it "a fresh directional lead
requiring replication," which is right — but a reader who counts three zones and one
significant p will assume the correction was not considered. State it.

### Finding 4.2 — the bands are probably detector combinatorics, and this is testable now

`x_μ` is an incoming charged-detector coordinate built from counter multiplicities.
Small integer counts produce **discrete** ratio values, so banding is the expected
default, not a finding. R1 and R2 together hold `80%` of non-pole events, which is
what a two-dominant-multiplicity detector looks like.

The report lists "detector-topology relation" as a candidate identity but does not
test it. **It is testable immediately from data already held:** tabulate the integer
`(upper, lower)` counter pairs feeding each band. If R1 and R2 resolve to a small set
of integer pairs, the bands are combinatorics and the ARA reading adds nothing. If
the same band spans many distinct integer pairs, it is structure.

This check costs one groupby and would settle the physical identity of the two
strongest features in the test.

### Finding 4.3 — the retained estimator failure is good practice

R3's estimator selected `1.180`, its own lower boundary, and you kept the failure
rather than re-specifying, marking T409B descriptive-only. That is the correct
handling and should stay visible.

---

## 5. Cross-cutting

**5.1 — What the series has established, stated plainly.** The coordinate recovers
`τ_μ`-shaped delayed structure (T403) and produces stable population-scale bands
(T409). Every attempt to carry a population landmark down to an **individual** muon
has failed: T407 not supported, T408 not supported, T409's travelling-ridge
hypothesis not supported. That is a consistent, informative boundary and it should be
the headline of the series rather than a sequence of separate negatives.

**5.2 — The archive cannot see what the claims need.** As `CLAIMS_STATUS.md` already
notes, no current input event-links an individual spinning muon to its charged
daughter *and* both neutrinos. Neither neutrino is observed at all. Several tests are
therefore attempting an individual-clock claim on data that is structurally incapable
of confirming it — which is why they keep returning null in the same direction.

**5.3 — Positive.** Frozen protocols with SHA sidecars, wrong-lineage geometric
controls, block bootstraps, permutation nulls, retained estimator failures, and a
self-caught implementation error (T404 correcting T403). The negative results are
called against interest, repeatedly. The discipline is not the problem here.

---

## Required corrections

1. **T403:** state that `ν_e` / `ν̄_μ` collinearity is forced by their common parent
   and lifetime; mark the per-flavour cosines as non-discriminating or remove them.
2. **T406/T407:** quote `0.706306` together with split median `0.948276` and the
   `7/20` gate failure, in `CLAIMS_STATUS.md` as well as the findings file.
3. **T406:** trace whether `1/√2` can enter the coordinate by construction.
4. **T408:** state the `MP` baseline AUC of `0.51594` alongside the improvement.
5. **T409:** add the Bonferroni correction for three zones.
6. **T409:** run the integer counter-pair tabulation for R1 and R2.
7. **Series level:** promote 5.1 to a summary statement — population structure
   recovers, individual transfer does not, on an archive that cannot observe the
   quantity the individual claims require.
