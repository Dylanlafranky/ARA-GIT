# Audit — T305 carrier test ONLY (partial; not an audit of `analysis/muon`)

> **SCOPE WARNING.** This document audits the schedule-null script and **T305 alone**.
> The muon series runs **T305 → T409** (30 July – 18 August 2026), roughly thirty
> tests, and moved from idealised scheduling simulation onto real event-linked
> stopped-muon records (T379 holdout runs `6845.2020.0317.0` / `6845.2020.0318.0`).
> **Nothing from T306 onward has been audited here.** Do not cite this file as an
> assessment of the muon work.

**Date:** 30 July 2026
**Auditor:** Claude (Opus 5), independent of the run
**Scope:** `mucf_pulse_schedule_fx.py` and artifacts; `t305_phi_temporal_carrier_fusion.py`,
its frozen protocol, report, summary, validation.
**Method:** frozen protocol read against report; headline numbers recomputed from
`SUMMARY.csv` and `VALIDATION.json`; forced arithmetic separated from empirical content.

---

## Verdict

| Item | Status |
|---|---|
| Implementation and validation quality | **Strong** — 15/15, aggregates reconstructed to `1e-12`–`1e-14` |
| Frozen-gate discipline | **Strong** — gates predeclared, failures recorded, verdict MIXED not upgraded |
| **Space/Time landmark assignment** | **CONTRADICTS THE FROZEN PROTOCOL — must be resolved** |
| `3/8` collapse as evidence | **Forced arithmetic, not empirical** |
| φ vs other non-closing irrationals | **Margins 0.5–2%; not distinguished** |
| G3 reporting | **Understates the failure** |
| Most informative row (`π−3`) | **Undiscussed** |

Overall: the engineering is sound and the discipline is better than most published
work. Two reporting problems need correction, one of them serious.

---

## 1. CRITICAL — the Space/Time assignment reverses between protocol and report

**Frozen protocol**, §"Prior ARA claim":

> Dylan proposes that this larger **Time-side carrier** may advance by the Phi
> handover: `α_φ = φ⁻² = 0.381966...`

**Report**, §"The directional clue":

> Dylan had already assigned:
> - `0.381966` to the **Space-side** landmark;
> - `1.618034` to the **Time-side** mirror.

These are opposite. The protocol names `φ⁻² = 0.381966` as the Time-side carrier.
The report names it the Space-side landmark and promotes `1.618034` to Time-side.

The discrepancy runs in the direction of the observed winner. On the unit circle
`frac(k·1.618034) ≡ frac(k·0.618034)`, so "Time-side = 1.618034" is exactly the
`phi_reverse` candidate the protocol marked **ineligible**
(`eligible_forward = False` in `SUMMARY.csv`) and which G2 explicitly barred:

> Reverse Phi cannot rescue the forward prediction.

**Required action.** One of the two documents is wrong and it must be settled from
material predating 30 July 12:48 AEST. Either:

- the protocol mis-stated the assignment → correct the protocol, mark the
  amendment, and note that the primary carrier was misassigned at freeze; or
- the report is retro-assigning → strike the Space/Time paragraph from the report.

Until then the "directional clue" section cannot be cited. The report does refuse
to promote it to a pass, which is correct and to your credit — but the retro-labelling
sits underneath that refusal and undermines it.

---

## 2. φ and φ_reverse are one schedule reflected, and the difference is not about φ

From `SUMMARY.csv`, bit-identical:

```
phi          largest_gap_mean 0.0688791167828   discrepancy_mean 0.0504971882837
phi_reverse  largest_gap_mean 0.0688791167828   discrepancy_mean 0.0504971882837
```

Because `φ⁻¹ + φ⁻² = 1` exactly, `frac(k·φ⁻¹) = 1 − frac(k·φ⁻²)`. The two schedules
are **reflections about `t = ½`**. Gap and discrepancy are reflection-invariant, so
they must agree exactly — and they do.

Their fusion overlap differs only because the arrival densities are **not**
reflection-symmetric (the decay envelope least of all):

```
fusion_robust_overlap_mean   phi 0.0774851   phi_reverse 0.0777222   (+0.31%)
```

So the reverse-φ "win" measures whether a mirrored pulse train fits these particular
`g(t)` shapes slightly better. Any carrier `α` versus `1−α` would show the same effect.
It carries no information about φ specifically, and φ is the only candidate for which
both orientations were run — so there is no comparison class.

---

## 3. The `3/8` collapse is forced arithmetic

```
                distinct coverage at N=64      = sites × width
3/8   →  8 sites × 0.15/64 = 0.01875           reported 0.018366
1/3   →  3 sites × 0.15/64 = 0.00703           reported 0.007031
2/5   →  5 sites × 0.15/64 = 0.01172           reported 0.011680
```

A rational `p/q` visits `q` sites. Coverage is capped at `q × width` no matter how
many pulses are delivered. This is arithmetic, true of every rational, and true
before any data exist.

The report states this correctly ("the expected consequence of using a
denominator-eight closure"), but the surrounding framing still leans on the
φ-versus-`3/8` contrast as though it informed the local/carrier duality. It cannot.
It distinguishes **rational from irrational**, not `3/8` from φ. Any small-denominator
rational substitutes identically.

`strict_cell_win_share_vs_three_eighths` is subject to the same objection — and note
that φ (`0.9617`) is **beaten** on that metric by both `1/e` and `phi_reverse` (`0.9727`).

---

## 4. `8/21` is the clean control and it is the strongest result in the table

```
8/21 = 0.380952   vs   φ⁻² = 0.381966      difference 0.001014
fusion_robust_overlap_mean:  0.042533  vs  0.077485    difference −45%
```

The nearest tested Fibonacci convergent sits `0.001` from φ in value and performs at
**55%** of φ. That is decisive evidence that the effect is driven by **closure
denominator**, not by numerical proximity to φ. Anyone claiming "near-φ values inherit
φ's benefit" is refuted by this row.

It deserves promotion in the report. It is currently absent from the main numbers table.

---

## 5. `π−3` is the most informative row and it is not discussed anywhere

```
pi_minus_3 = 0.14159265   overlap_loss ≈ 2.3e-17 (none)   flat 0.0796875 (full)
             fusion_robust_overlap_mean = 0.033444   ← 43% of φ
```

`π−3` is irrational, never repeats, achieves **full** coverage on the flat null, and
still performs at under half of φ on the structured families.

The reason is visible in the setup: `0.14159 ≈ 1/7.06`, and the beam families are
**7-cycle**. A carrier near-commensurate with the source beats against it and
systematically misses the same phase region.

**This is the single result in the folder that demonstrates the original mechanism** —
that a schedule can fail by locking to the source's rhythm — and it does so without
relying on the trivial rational collapse. It also bounds the claim correctly:

> Irrationality is necessary but not sufficient. The carrier must also be far from
> resonance with the source structure. That is a property of the **source–carrier
> pair**, not an intrinsic property of φ.

Recommend a dedicated section.

---

## 6. G3 is reported as a single loss; it was a double failure

Protocol G3:

> Phi passes only if it is the **unique best forward fixed carrier and beats `3/8`**.

Actual tail values (`fusion_robust_overlap_tail_p05`):

```
one_over_e     0.0137877   ← winner
phi_reverse    0.0137655   (ineligible)
three_eighths  0.0125823
phi            0.0117264   ← −17.6% vs 1/e,  −7.3% vs 3/8
oracle_uniform 0.0116003
```

φ lost the tail to `1/e` **and to `3/8`**. The report says only "`1/e` won that
endpoint," which omits the second and more damaging half — losing to `3/8` on a gate
whose text explicitly required beating `3/8`.

Also worth noting: the **oracle has the worst tail of all**. Known-horizon uniform
scheduling is the mean-overlap ceiling and the tail floor. That is a real and
non-obvious finding about the oracle, currently unremarked.

---

## 7. Margins among non-closing irrationals

```
oracle_uniform  0.0788880   (ineligible ceiling)
phi_reverse     0.0777222   (ineligible)
phi             0.0774851
one_over_e      0.0770948   −0.51% vs φ
sqrt2_minus_1   0.0760510   −1.86% vs φ
```

φ's margin over `1/e` is **0.51%**. Against the tail deficit of 17.6% in the other
direction, the honest summary is that φ is **competitive but not distinguished**
among non-closing carriers.

This is consistent with theory rather than contrary to it. φ is provably optimal for
**max-gap discrepancy** (three-distance theorem) — and indeed wins G1's geometric
ranking. It has no proven optimality for **overlap against a structured arrival
density**, which is what G2/G3 measure. There was never a theoretical reason to
expect φ to win G3.

---

## 8. What is well done

- Gates predeclared with numeric thresholds and a stated verdict rule.
- G4 stationary null included, and it passes at `5.6e-16` spread — a real null,
  correctly refusing φ credit for matching it.
- The oracle is declared ineligible in advance rather than being quietly beaten.
- Fixed pulse width held across prefixes, explicitly to prevent stopping-time leakage.
  This is the flaw in the earlier `mucf_pulse_schedule_fx.py` run and T305 fixes it.
- Independent validation reconstructs every aggregate from the prefix table and adds
  dense-grid spot checks (`5.06e-5`).
- The interpretation boundary correctly excludes `P_X`, `η_X`, real arrival trains
  and net yield.

---

## Required corrections

1. **Resolve the Space/Time assignment against pre-freeze material.** Amend whichever
   document is wrong, visibly. Do not cite the directional clue until settled.
2. **Relabel the `3/8` collapse** as forced arithmetic in the main numbers table, not
   only in the discussion.
3. **State the G3 failure in full** — φ lost to `1/e` *and* to `3/8`.
4. **Promote `8/21`** into the main table as the near-φ closure control.
5. **Add a `π−3` section.** It is the folder's best evidence for the source–carrier
   resonance mechanism.
6. **Restate the deliverable** at the strength the data support:

> For an open-ended pulse count, a rational repetition rate collapses coverage by a
> factor equal to its denominator. Among non-closing carriers the differences are
> ≲2% on mean overlap, φ is best on max-gap geometry as theory predicts, and φ is not
> best on tail robustness. A carrier near-commensurate with the source (`π−3` against
> a 7-cycle beam) fails badly despite being irrational.

That is defensible, useful to Kou and Chen, and does not require φ to be privileged.
