# T449 — Same-rung time-facing children in individual fruit-fly lifecycles

## Result first

T449 recovered a reproducible **same-rung local push/pull relation**, but it did **not** recover a directional child handover. The two frozen children couple most strongly at zero lag: when ten-minute temporal retention changes upward, traversal/renewal tends to change downward at the same time, and vice versa.

A slower, parent-facing lifecycle gradient is also visible. Across the final 72 hours of the untouched holdout flies, the common mode of both children declines toward author-indexed collapse in 15 of 16 flies; the differential child mode is much weaker. This is useful ARA geometry, but it remains retrospective evidence of a lifecycle-facing shadow rather than proof that either child is time itself.

## The exact test

### Who

The subjects are the same 47 published individual male *Drosophila* used in T448. Experiments 1–3 contain 31 development flies; the later and hotter experiment 4 contains 16 untouched holdout flies.

### What

Every individual recording was cut into consecutive ten-minute child windows. The test independently measured temporal retention, \(C_A\), and traversal/renewal, \(C_B\), from the ordered one-second behaviour history, then asked whether their relation carried a reproducible lead, exchange landmark, and parent response.

### When

The full recorded pre-collapse history of every fly was used. Collapse and death labels were withheld from coordinate construction and used only afterward to align and evaluate the recovered histories.

### Where

The relational address is:

\[
\text{individual fly}
\rightarrow
\text{ten-minute temporal child window}
\rightarrow
(C_A,C_B)
\rightarrow
\text{six-child hourly parent}
\rightarrow
\text{lifecycle/collapse evaluation}.
\]

The two children are on the same rung, in the same behavioural medium, and use the same ten-minute window. Their pair is treated as a simple ARA cut; it is **not** promoted to a Di-ARA without independent evidence that they are opposed poles of one strongly coupled identity.

### Why

The purpose was to test whether an explicitly time-ordered child relation turns before the coarser hourly lifecycle parent found in T448. A successful directional result would give a candidate bridge from local ordering to the larger lifecycle gradient and a clean selection rule for deeper biologic children.

### How

The behaviour label at each second is the exact modal state across all source frames in that second. Unstereotyped and on-edge labels remain unresolved separators rather than being converted into a biological state.

Temporal retention is the mean chance-corrected probability of retaining the same resolved state over 1, 10, and 60 seconds:

\[
C_A=\operatorname{mean}_{\ell\in\{1,10,60\}}
\frac{P(Y_t=Y_{t+\ell})-\sum_k p_k^2}{1-\sum_k p_k^2}.
\]

Traversal/renewal is the normalized conditional entropy of the next resolved state:

\[
C_B=\frac{H(Y_{t+1}\mid Y_t)}{\log K}.
\]

Development data alone fixed the robust centres, scales and selected lag. Experiment 4 then tested that frozen relation against timestamp shuffling, circular time shifts, temporal reversal, biological-composition controls and parent-response controls.

## Frozen results

| Quantity | Result | Meaning |
|---|---:|---|
| Published individuals | 47 | 31 development, 16 untouched holdout |
| Ten-minute windows | 30,902 | All extracted windows |
| Primary eligible windows | 14,855 (48.1%) | At least 80% resolved seconds and enough transitions/states |
| Development-selected lag | 0 minutes | The dominant relation is simultaneous at this resolution |
| Development median coupling | -0.0917 | Weak inverse coupling |
| Holdout median coupling | -0.1364 | Stronger inverse relation in the untouched cohort |
| Holdout timestamp-shuffle coupling | -0.0356 | Ordering contains additional structure |
| Circular-shift magnitude limit | 0.0654 | Frozen holdout relation exceeds the 95% null magnitude |
| Circular-shift p-value | 0.00050 | Q1 passes |
| Same-sign holdout flies | 16/16 | The inverse relation transfers across individuals |
| Reversed selected lag | 0 minutes | No direction flip; Q2 fails |
| Parent-response events | 1,330 | Pooled exchange landmarks with evaluable next-parent response |
| Pooled median parent response | -0.0403 | Exchanges do not precede the frozen terminal-parent direction |

Frozen gates:

- **Q1 PASS:** ordered coupling exceeds the circular-shift limit and is stronger than timestamp shuffling.
- **Q2 FAIL:** the sign transfers, but temporal reversal does not flip a non-zero lag because the selected lag is zero.
- **Q3 FAIL:** pooled exchange landmarks do not precede progress in the frozen terminal-parent direction.
- **Q4 PASS:** inverse coupling remains after controlling for biological composition, Zeitgeber phase and unresolved shares.

The frozen conclusion is therefore narrow: **chronological ordering matters, but the selected pair is not a recovered arrow of time or predictive handover.**

## Geometry visible below the gates

### Two scale-dependent views coexist

At the local ten-minute scale, consecutive changes in \(C_A\) and \(C_B\) form an immediate inverse push/pull. At the slower parent-facing lifecycle scale, the common mode

\[
M=\frac{z_A+z_B}{2}
\]

declines toward collapse, while the child-difference mode

\[
D=\frac{z_A-z_B}{2}
\]

has little consistent lifecycle trend. In the final 72 hours, 15 of 16 holdout flies have a positive Spearman relation between hours remaining and \(M\), with a median of 0.365; the median relation for \(D\) is only 0.049.

This is consistent with a parent/child reading: the coarse parent-facing view records a shared loss of temporal organisation, while the same-rung children exchange locally inside it. It does not establish that the common mode is a universal time coordinate, because alignment to known collapse is retrospective.

### Exchange direction matters

The post-frozen descriptive split cannot alter Q3, but it reveals an asymmetric branch:

- **retention → traversal:** 648 events; median next-parent response -0.0544, below the shifted 2.5% limit -0.0349 (lower-tail p=0.0020);
- **traversal → retention:** 682 events; median response +0.0076, not beyond its shifted null (upper-tail p=0.393).

The strong branch moves **against** the frozen terminal-parent direction. A cautious ARA interpretation is that retention-to-traversal crossings describe a movement/recovery excursion inside the lifecycle rather than the final connection-closing handover we were seeking.

## What this means for ARA

1. **Same-rung relational structure was recovered.** The relation transfers to all 16 untouched flies, survives time-shift and composition controls, and is not a deterministic complement.
2. **The parent and child cuts are not interchangeable.** The slow common mode carries lifecycle direction; the local differential relation carries immediate exchange.
3. **This pair does not yet supply the missing time-facing third coordinate.** Zero-lag inverse coupling is an exchange geometry, not enough to establish which side leads.
4. **Do not call this pair a Di-ARA yet.** We have two independently measured children in a simple ARA cut, but not independent evidence that they are a complete strongly coupled pole system.
5. **The null is informative.** It rules out the tempting claim that coarse behavioural retention versus transition entropy alone predicts the lifecycle handover.

## Data quality and limits

All 47 source files are present; source/window keys are unique; indices are contiguous within each recording; shares close to one within \(6.7\times10^{-16}\); time-to-collapse arithmetic reconciles within \(2.9\times10^{-14}\) hours; and every eligible row has finite primary coordinates.

The principal caveat is classifier visibility. Only 48.1% of all ten-minute windows meet the frozen eligibility requirement, with experiment-level coverage ranging from 32.1% to 58.7%. This is not silently filled: unresolved share remains a control, and all primary claims are restricted to eligible windows. The classifier is also a behavioural observation shadow rather than a molecular or physical clock.

## Recommended deeper biologic cut

The next child selection should be **time-reversal asymmetric by construction** while remaining on the same or a demonstrably coupled scale. The strongest available next cut is to change medium explicitly—from categorical behaviour states to continuous pose/kinematics—and measure, in the same ten-minute windows:

1. a whole-body persistence child: translation/orientation continuity of the fly;
2. an internal articulation child: limb/body-shape renewal relative to the fly's body frame;
3. a directed relation: forward-prediction error minus backward-prediction error, tested blind on experiment 4.

That cut asks whether an internal biologic child turns before the whole-body behavioural parent. It is more time-facing than state persistence versus entropy because its directed coordinate changes sign under temporal reversal; however, changing from categorical behaviour to continuous pose is a medium change and must be announced and frozen before execution.

## T449C addendum — what happens at the inversion?

The earlier wording “no handover” was too broad. T449 did not recover the **directional lifecycle/time handover** named by Q2 and Q3, but the sign inversion in \(D=z_A-z_B\) is a genuine, repeatedly observed **activity-state handover** in this cut.

Across the 4,259 adjacent eligible holdout pairs, 1,607 inversions occurred: 789 retention→traversal and 818 traversal→retention. They were not isolated coordinate crossings:

- **retention→traversal** coincided with falling idle share (matched median fly change -0.0602) and rising locomotion (+0.0385); exact fly-level sign-flip p-values were 0.00223 and 0.000183 respectively;
- **traversal→retention** coincided with rising idle (+0.0757) and falling locomotion (-0.0414); p-values were 0.00235 and 0.0000916;
- smaller grooming/proboscis changes occur in the expected direction, but they are secondary to the locomotion↔idle exchange;
- unresolved visibility did not materially rise during retention→traversal (p=0.856), which argues against the main pattern being a classifier-loss artefact.

The inversion rate also rises near collapse: 50.7 inversions per 100 adjacent eligible pairs in the final six hours, versus 36.3 beyond 72 hours. The within-fly final-six-hour increase is +10.6 percentage points at the median among the 13 flies with both bands, but its exact two-sided sign-flip p=0.0796 makes this a suggestive lifecycle modulation rather than a confirmed terminal-specific effect.

At the hourly parent scale, retention→traversal is followed by significant motion against the frozen terminal-parent direction, while traversal→retention has only a weak positive parent response. The best current ARA reading is therefore:

\[
\text{local retention-heavy state}
\rightleftarrows
\text{local traversal-heavy state},
\]

with the exchange becoming more frequent as the slower parent loses organisation. This is a handover inside the lifecycle parent, not yet the one-way child turn that identifies time direction or terminal collapse.

## Files

- `FROZEN_PROTOCOL.md` — pre-result test definition and gates
- `results/T449_RESULT.json` — frozen confirmatory result
- `results/T449_POSTHOC_RESULT.json` — explicitly post-frozen geometry
- `results/T449_DATA_QUALITY.json` — mechanical and visibility audit
- `results/T449_01_scope_and_visibility.png` through `T449_10_directional_exchange_split.png` — static visual evidence
- `results/T449_11_INVERSION_EVENT_DIAGNOSTIC.png` — biological and parent events at the inversion
- `results/T449C_INVERSION_EVENT_RESULT.json` — post-frozen inversion-event diagnostic
