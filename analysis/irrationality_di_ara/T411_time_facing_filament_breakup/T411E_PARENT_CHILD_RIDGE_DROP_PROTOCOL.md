# T411E — parent–child coarse-ridge drop

## Status

Frozen post-hoc mechanism test.  The rule below was written after T411D exposed
S2/S4, so S2/S4 are diagnostic data rather than a sealed confirmation.

## Hypothesis

The identity-scaled handover clock is carried by the coarse relation between
the causal connection-heavy child and its causal parent.  If

\[
R_{PC}(t)=\frac{x_C(t)+x_P(t)}{2},
\]

then `R_PC = 1` is the compressed child–parent ridge while preserving
`x_C != x_P`.  The proposed handover landmark is the first downward passage
through this ridge after the T411D child has issued.

## Causal rule

1. Reuse the frozen T411D causal `x_C`, `x_P` and child issue; do not refit the
   rate windows.
2. Start observing `R_PC` at the child issue time.
3. Arm once `R_PC > 1` has been observed.
4. Issue on the fifth already-observed consecutive frame at or below 1.
5. Record both the interpolated ridge passage and the later causal issue time.
6. Use the causal issue time as the zero-offset parent timestamp prediction.

No fixed seconds, lifetime fraction or fluid-specific parameter is fitted.

## Comparators

- T411D child-only prediction using its frozen 0.058 s development offset.
- causal parent-only issue;
- the next upward `R_PC = 1` passage after the child issue;
- 1,000 circular shifts of the pair relation within each event.

## Readout

Report coverage, fraction issued before the offline T411C parent target,
median lead, normalized absolute timing error, error against each comparator,
and the circular-shift timing p-value.  Results are split by S1–S4.

## Interpretation boundary

Success would show that the proposed coarse ridge is a useful identity-scaled
temporal landmark in this dataset.  Because the hypothesis was proposed after
S2/S4 were viewed and the target is reconstructed from the same diameter
traces, it would still require unchanged external replication.

