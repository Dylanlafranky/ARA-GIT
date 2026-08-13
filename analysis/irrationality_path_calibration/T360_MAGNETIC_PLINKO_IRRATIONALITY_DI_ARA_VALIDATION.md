# T360 independent validation

**Status:** PASS

The independent validator reads the saved CSV/JSON artifacts and does not import the analysis module. It recomputed:

- saved gate vector: `[PASS, FAIL, FAIL, FAIL, PASS]`;
- G1 median, positive-event rate, and exact paired p-value;
- G2 run wins, exact effect, and exact `4^5` within-run label p-value;
- G3 joint-positive rate, exact effect, and exact `4^5` within-run label p-value;
- G4 Spearman correlation and coordinate IQR conditions;
- active v5 protocol SHA-256;
- final figure existence and pixel dimensions.

All gate states and headline values matched the saved results. The Spearman comparison uses `1e-4` tolerance because CSV serialization changes tie handling in the fifth decimal place; the gate threshold is `|rho| < 0.90`, so this has no verdict effect.

Validated protocol v5 SHA-256:

`ADCB323D976D1EB0ABAB06A5D344373113B433C4C92DF1FCF2FF386C80368EA8`

Final figure dimensions: `3230 x 3040` pixels, RGB.
