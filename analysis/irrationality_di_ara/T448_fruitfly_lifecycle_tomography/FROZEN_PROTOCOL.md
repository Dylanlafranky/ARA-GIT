# T448 — Individual fruit-fly lifecycle tomography and terminal handover

Status: frozen before viewing lifecycle geometry.

## Who

The measured identities are individual male *Drosophila melanogaster*. Each fly remains the unit of development/holdout separation; hours from the same fly may never appear on both sides of that split.

The source contains 47 individuals recorded continuously from 2–3 days after adult emergence until death under the experiment's nutrient-limited and warm conditions. This is an accelerated dying/stress setting, not a conventional 2–3 month lifespan assay.

## What

Every complete observed hour is reduced to four mutually exclusive, scientifically supplied behaviour parts after excluding `unstereotyped` and `on_edge` classifications:

1. **Traversal T:** locomotion + altered locomotion.
2. **Maintenance G:** fore + hind + wing grooming.
3. **Intake P:** proboscis extension.
4. **Quiescence I:** idle.

Because the four parts close to one, they contain three independent degrees of freedom. We preserve those three degrees with an orthonormal isometric log-ratio basis:

\[
z_1=\sqrt{1/2}\log(T/G),
\]

\[
z_2=\sqrt{2/3}\log(\sqrt{TG}/P),
\]

\[
z_3=\sqrt{3/4}\log((TGP)^{1/3}/I).
\]

These are respectively:

- **Cut 1 — traversal ↔ maintenance**;
- **Cut 2 — external action ↔ intake**;
- **Cut 3 — participation ↔ quiescence**.

No pair is called a Di-ARA merely because it is plotted together. The three pairwise disks are tomographic projections of the same three-coordinate lifecycle state. A coupled Di-ARA interpretation is permitted only after the data show stable relational coupling.

Death and collapse times are outcomes from the authors' experiment index. Neither hours lived, fraction of lifespan, hours remaining, file length nor proximity to death may be used to construct the three input coordinates.

## When

The primary window is one hour, matching the source study's natural analysis scale and leaving circadian changes visible. A retrospective view may align hours by time before collapse/death, but prospective scoring uses only information available at the end of the observed hour.

The authors' separate `Collapse (hours into video)` landmark is the primary handover event because it can precede recorded death. Recorded death is a secondary endpoint. Their distinction is retained rather than averaged away.

## Where

The relational address is:

individual fly → hourly four-part behavioural composition → three independent balance cuts → three pairwise disks → combined three-coordinate lifecycle shadow → collapse/death outcome.

This is a behavioural shadow of the living identity. It does not directly measure biological time, molecular damage, or an internal life/death singularity.

## Why

The test asks whether individual flies approach a repeatable terminal region across several independent cuts, whether the cuts reveal distortion that one disk hides, and whether that region transfers to completely unseen flies.

For ARA, a positive result is not simply “activity falls before death.” The stronger result would be a reproducible relational approach in the three-cut geometry, with multiple cuts locating terminal proximity more reliably than any single cut and surviving circadian/environmental controls.

## How

1. Aggregate real public HDF5 behaviour labels into fly-hours.
2. Preserve excluded/edge share as a data-quality measure, not a fourth lifecycle coordinate.
3. Freeze development and holdout by experiment: experiments 1–3 develop the geometry; experiment 4 is the hard holdout because it is hotter and recorded later.
4. Fit zero replacement, robust centres and robust scales using development flies only.
5. Display each independent coordinate on a common 0–2 ARA map without per-fly or per-axis refitting. Raw proportions and unscaled log-ratios remain available.
6. Estimate the empirical terminal region from development flies' final pre-collapse hours. Do not force a circle or sphere; compare spherical, elliptical and nearest-manifold descriptions.
7. On holdout flies, measure whether distance to that frozen terminal region falls as collapse approaches and whether three cuts outperform one.
8. Controls: shuffled collapse times, time-of-day matching, leave-camera-out checks, light/dark phase, experiment temperature/humidity, and edge-classification share.
9. Report gates and geometry separately. A failed frozen gate cannot erase a visible shape; a visible shape cannot retroactively change the frozen gate.

## Frozen primary claims and gates

Primary claim A: terminal-region distance should decline over the final 24 hours more strongly than during matched non-terminal hours.

Primary claim B: the three-coordinate distance should outperform every single-coordinate and pairwise distance on the untouched experiment-4 flies.

Primary claim C: the observed ordering should exceed at least 95% of within-fly circularly shifted collapse controls.

The verified cohort contains 31 development flies and 16 experiment-4 holdout flies, each with at least 32 complete pre-collapse hours. Before viewing geometry, the numerical gates are frozen as:

- **Gate A:** in exact 24-hour, same-fly, same-Zeitgeber-time pairs, at least 65% of final-six-hour observations are closer to the development terminal region than their one-day-earlier controls.
- **Gate B:** the three-coordinate terminal-distance AUROC exceeds the best single-coordinate or pairwise AUROC by at least 0.02 on those untouched holdout pairs.
- **Gate C:** the observed three-coordinate paired-win rate exceeds the 95th percentile of 2,000 within-fly circular endpoint shifts.
- **Supporting trend:** the median within-fly Spearman correlation between hours remaining and terminal distance during the final 24 hours is at least +0.25.

Passing A and C supports temporal alignment. Passing B supports the added value of multi-cut tomography. The supporting trend describes approach shape and is not allowed to overturn the primary gates.

## Mandatory pivot notice

If file endings, classifier construction or missingness make collapse mechanically derivable from the input channels, the test must be relabelled a reconstruction/calibration test rather than a prospective handover test. That change must be stated before interpretation.
