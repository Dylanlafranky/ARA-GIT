# T344 runtime addendum v1 (frozen)

**Frozen:** 6 August 2026, before calculating any T344 ARA result  
**Reason:** the available verified scientific runtime contains NumPy and SciPy but not
scikit-learn.

The computational addendum names scikit-learn multinomial logistic regression. The
runtime will instead solve the same fixed model directly with SciPy `L-BFGS-B`:

\[
\mathcal L(W,b)=
-\frac1n\sum_i \log \operatorname{softmax}(X_iW+b)_{y_i}
+\frac{1}{2Cn}\lVert W\rVert_2^2,
\qquad C=1.
\]

- Inputs are standardised using training means and standard deviations only.
- The fourth class is the zero-reference class to identify the multinomial parameters.
- The intercept is not penalised.
- Optimiser tolerance is `1e-9` and maximum iterations are `1000`.
- All additive, intact and broken models use the identical solver and objective.
- No coefficient, feature, regularisation value or gate is altered after outcomes.

This is an implementation substitution, not a new statistical model or a response to
the data. The resulting optimisation status and gradient norm must be recorded for every
fold.

