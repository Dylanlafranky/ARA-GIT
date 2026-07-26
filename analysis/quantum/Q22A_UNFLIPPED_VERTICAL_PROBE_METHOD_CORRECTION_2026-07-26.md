# Q22A method correction — omitted vertical singularity flips

**Recorded:** 26 July 2026  
**Trigger:** Dylan noticed the missing singularity flip before Q22A validation
or ledger promotion.

Q22A compared the local Tier-4 coordinate \(x_4\) directly with Tier 1. That
does not implement the declared ARA rung rule. Tier 4 to Tier 1 crosses three
completed parent/child boundaries:

\[
x_4
\rightarrow 2-x_4
\rightarrow x_4
\rightarrow 2-x_4.
\]

The net Tier-1-facing orientation is therefore:

\[
\boxed{x_{4\rightarrow1}=2-x_4}.
\]

Q22A remains a reproducible **unflipped/even-parity control**. Its result must
not be reported as the intended ARA vertical-travel test:

- directional geometry passed in the unflipped representation;
- logical-outcome prediction remained near chance;
- strict verdict was `NOT SUPPORTED`, 4/12 gates.

Q22B applies the pre-existing odd-boundary flip rule and uses the previously
untouched `d5_at_q8_7` patch. The local Tier-4 identity stays expressed in its
own frame; only its relation to Tier 1 uses the lifted coordinate \(2-x_4\).

The `0–2` position is dimensionless and normalized within each tier. The
separate rule that amplitude capacity halves one tier downward is not silently
multiplied into this phase-position coordinate. A later amplitude-transfer
test must measure that quantity explicitly.
