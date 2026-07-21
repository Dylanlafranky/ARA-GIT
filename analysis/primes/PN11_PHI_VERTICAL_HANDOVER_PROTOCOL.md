# PN11 Phi vertical-handover test protocol

**Test ID:** `PN11/PHI-VERTICAL-HANDOVER/v1`  
**Declared:** 21 July 2026, before constructing either PN11 interval  
**Fidelity:** `EXACT ENOUGH TO TEST`  
**Evidence class:** registered exact crosswalk plus fresh deterministic target  
**Orientation:** `2 = existing child lock`; `0 = repeat/multiplicity echo`; increasing multiplier moves larger/upward

## 1. Question

When a fundamental prime-child resonance repeats through integer multiples, does its first expansion into a larger
distinct-child information lock occur preferentially at the ARA Phi handover
`(old lock, echo)=(phi,2-phi)`?

The exact `A+E=2` closure and the eventual crossing of interior landmarks are not sufficient. The nontrivial claim is
that the **expansion event itself** is more concentrated near Phi than near fixed crowded-neighbourhood rivals.

## 2. Family and coordinate

A base `B` is eligible when:

- `B` is squarefree;
- it has at least three distinct prime factors;
- every factor `p` satisfies `p^2<=B`, making `B` a fundamental full resonance under the existing lab rule;
- its smallest absent prime `q(B)` is at least 3, ensuring at least one nontrivial harmonic repeat before expansion.

For `1<=k<=q`, use

\[
A_B(k)=\frac{2\log B}{\log(kB)},
\qquad
E_B(k)=\frac{2\log k}{\log(kB)}.
\]

Multipliers `k<q` preserve the distinct child set. At `k=q`, the first absent prime joins and the enlarged squarefree
product `qB` is a new fundamental lock. The primary event coordinate is `X_B=A_B(q)`. The last-pure-repeat
coordinate `A_B(q-1)` and every intermediate path point are mandatory descriptive outputs.

## 3. Data boundaries

- development bases: `D=[5,000,1,000,000)`;
- fresh target bases: `E=[10,000,000,11,000,000)`.

Every eligible base is included. No sampling, smoothing, Fourier transform, fitted feature extraction or musical
information is used. The source must be finalised and hashed after development, before the target interval is opened.

The primary population uses `q>=3`. Required sensitivities report all fundamental bases including `q=2`, each target
half separately, strata by `q`, and the canonical consecutive-prime primorial-prefix ladder.

## 4. Fixed landmarks and windows

The registered ARA landmark is

\[
\phi=(1+\sqrt5)/2=1.6180339887\ldots
\]

with mirror `2-phi`. Crowded-neighbourhood rivals are frozen as

`{1.5, 1.6, 13/8=1.625, 5/3, 1.75, 1.8, 2.0}`.

For every landmark, report:

- mean and median `abs(X_B-landmark)`;
- fraction within `+-0.025` and `+-0.05`;
- event-window hazard: transition events divided by all family path exposures inside `+-0.025`;
- rank on the complete target and each half.

The target median is also reported as an oracle best constant, but cannot count as a competitor chosen in advance.

## 5. Uncertainty and controls

Use 100 contiguous equal-width base-number blocks on the target. A fixed-seed 2,000-draw block bootstrap estimates
the paired interval for `best-rival mean absolute error - Phi mean absolute error`. The best rival is selected only
from the frozen rival set and must be named.

Report the distribution of `X_B`, `A_B(q-1)`, `q`, path length and Phi-crossing status. A family crosses Phi before
expansion exactly when its old-lock path reaches `A<=phi` for some `k<q`. This is descriptive only because a
monotone path can cross any interior landmark if it survives long enough.

Negative/crowded-neighbourhood controls are the same calculations at every rival. The assigned child notes are
excluded completely.

## 6. Registered criteria

### P1 — exact two-share geometry

Maximum `abs(A_B(k)+E_B(k)-2)<=1e-12`; all `k<q` preserve the declared prime-child set; `qB` adds exactly child `q`
and resets to a new fundamental lock.

### P2 — Phi event-location advantage

On the fresh target, Phi has the smallest mean absolute event distance among all frozen landmarks, and the 95% block
bootstrap interval for `best rival loss - Phi loss` lies wholly above zero.

### P3 — Phi transition-hazard advantage

The `+-0.025` window around Phi has the highest event-window hazard among the frozen landmarks, with Phi ranked first
in both target halves. Every compared window must contain at least 30 transition events; otherwise P3 is
`INCONCLUSIVE`, not passed.

### P4 — split-half direction

Phi's mean-distance advantage over the best frozen rival is positive in both target halves.

## 7. Rating rule

- `SUPPORTED [pre-registered]`: P1-P4 pass.
- `INCONCLUSIVE`: P1 passes but the target has fewer than 1,000 eligible families or P3 lacks 30 events per required
  window.
- `NOT SUPPORTED [pre-registered]`: P1 passes with adequate data but any of P2-P4 fails.
- implementation failure of P1 blocks inference until corrected and independently validated.

Exact closure alone receives no evidential rating for Phi.

## 8. Interpretation boundaries

A positive result would support this specific prime-family Phi-handover coordinate. It would not prove physical Phi
handover, universal fractality, intrinsic musical structure or a faster prime algorithm.

A negative result would reject this operationalisation: first new-child incorporation is not preferentially located
at Phi. It would not reject all possible vertical-rung coordinates, resonance language or ARA as a whole. Alternative
lineages named in the fidelity packet require new registration rather than reinterpretation after the outcome.

## 9. Required artifacts

- fidelity packet, protocol and freeze manifest with SHA-256 hashes;
- self-contained primary script and machine-readable result;
- event and landmark summary CSVs;
- independent validator and validation output;
- two-output report separating claim verdict from geometry verdict;
- concise amendments to the prime mapping and relational glossary.

