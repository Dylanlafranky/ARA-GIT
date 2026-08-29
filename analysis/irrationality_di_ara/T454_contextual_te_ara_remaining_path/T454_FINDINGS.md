# T454 findings — contextual TE-ARA remaining path

The direct contextual allocation

\[
\widehat B=2-(A+R_{AB}+C)
\]

is more accurate than the pure complement `2−A` on both untouched groups.

## Main result

- Experiment 9, relation + fixed 0.25 versus pure: **8.31%** lower remaining-generation MAE.
- Experiments 1–6, relation + fixed 0.25 versus pure: **26.77%** lower MAE.
- Relation alone versus pure: **4.53%** improvement in Experiment 9 and **24.76%** externally.
- Fixed 0.25 beyond the relation alone: **3.96%** improvement in Experiment 9 and about **2.67%** externally.
- The correctly signed relation is better than the reverse-sign control on both holdouts.
- Frozen gates: **4/6 passed**.

The large external relational gain has an entirely positive whole-cell bootstrap interval. The 12-cell same-platform relational and child increments have intervals crossing zero.

## Child interpretation

The parent-facing size child has holdout median `0.321`; Rpl13A has median `0.233`. Fixed `0.25` is therefore close to the Rpl child ridge but below the typical size-child contribution.

A post-result constant-offset scan has a broad external minimum at `0.20` and a small-holdout minimum at `0.57`. Therefore `0.25` is a useful frozen correction and compatible with the larger external geometry, but it is not uniquely locked as a universal child allocation.

## ARA interpretation

The pure partition is too simple for this observed identity. Generation progress and clock progress are asymmetric, and retaining their signed relation materially improves the remaining path. The child/context term improves it further, but its amount remains identity- and boundary-dependent.
