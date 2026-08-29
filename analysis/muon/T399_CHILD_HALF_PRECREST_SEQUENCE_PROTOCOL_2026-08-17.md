# T399 — child-half before neutrino release crest protocol

**Frozen:** 2026-08-17  
**Status before execution:** predeclared post-T398 landmark-order and robustness test  
**Primary question:** does the delayed muon-neutrino population pass the ARA child-half landmark before its release-rate crest, with the preceding prompt crest approximately one quarter of an ARA unit below child half?

## Who, what, when, where, why and how

- **Who / identities:** the fitted prompt \(\nu_\mu\) population and the fitted delayed \(\nu_e+\bar\nu_\mu\) population in the COHERENT CsI release used by T371/T372/T398. The earlier COHERENT CsI release used by T378 is the independent, coarser holdout.
- **What / ARA cut:** on one cumulative \(0\!\rightarrow\!2\) parent traversal, locate (i) prompt-rate crest, (ii) prompt/delayed instantaneous equality, (iii) cumulative child half \(x=0.5\), and (iv) delayed-rate crest.
- **When:** \(0\)–\(6\ \mu\mathrm{s}\) after the SNS proton pulse. The primary source is sampled every 5 ns from the released native templates. The holdout is available only in released 0.5 \(\mu\mathrm{s}\) bins.
- **Where / medium:** COHERENT CsI[Na] at the SNS. No RAL Silver spin data are merged into this test.
- **Why:** T398 visually suggested that the delayed neutrino branch was already at child-half before its outward release became maximal, and that the earlier prompt crest sat near \(x=0.25\). T399 tests that exact reading rather than relabelling the release crest as the birth time.
- **How:** recompute the four landmarks from the saved native curves; repeat the calculation over every registered T371 leave-one-bin-out fit; run a yield-uncertainty sensitivity ensemble from the registered 95% intervals; compare the real alignment with phase-shifted delayed-branch controls; and check the child-half-before-delayed-crest order on the independent T378 release.

## Definitions

For fitted prompt and delayed rates \(r_p(t)\) and \(r_d(t)\), define

\[
x(t)=2\,\frac{\int_0^t[r_p(u)+r_d(u)]\,du}
                 {\int_0^{6\,\mu s}[r_p(u)+r_d(u)]\,du}.
\]

The landmarks are

\[
t_P=\arg\max r_p(t),\qquad
t_H:\ r_p(t_H)=r_d(t_H),\qquad
t_{1/2}:x(t_{1/2})=0.5,\qquad
t_D=\arg\max r_d(t).
\]

The proposed quarter displacement is

\[
\Delta x_{P\rightarrow1/2}=0.5-x(t_P).
\]

## Frozen gates

1. **Native order:** \(t_P<t_H<t_{1/2}<t_D\).
2. **Native child-half precedes crest:** \(t_D-t_{1/2}>0\).
3. **Native quarter compatibility:** \(0.20\leq\Delta x_{P\rightarrow1/2}\leq0.30\). This is a calibration gate, not an independent prediction, because it was proposed after viewing T398.
4. **Leave-one-bin-out robustness:** child half precedes the delayed crest in at least 90% of the registered T371 leave-one-energy-bin-out and leave-one-time-bin-out fits.
5. **Yield-uncertainty robustness:** child half precedes the delayed crest in at least 95% of 10,000 positive-yield sensitivity draws from split-normal approximations to the registered T371 95% intervals.
6. **Independent coarse holdout:** the T378 cumulative child-half crossing precedes the delayed branch’s peak bin. Its 0.5 \(\mu\mathrm{s}\) bins are not precise enough to gate the full native four-landmark order or the quarter displacement.
7. **Alignment control:** among all non-zero circular shifts of the native delayed branch, no more than 5% reproduce both the real four-landmark order and a quarter-displacement error no larger than the real curve’s \(|\Delta x-0.25|\). Failure is informative and prevents an alignment-specific claim.
8. **Claim boundary:** the result must be stated as a population handover/landmark result. It cannot be stated as direct observation of an individual neutrino birth.

## Robustness interpretation

The yield ensemble varies branch amplitudes while retaining the released branch shapes. It is therefore a parameter-sensitivity test, not a fresh detector bootstrap. The leave-one-bin-out fits and the independent T378 release carry the genuinely distinct robustness burden.

Circular shifts preserve the delayed curve’s shape while destroying its measured alignment with the prompt curve. They test whether the observed quarter-and-order combination is special to the real relative placement; they are not alternative physical decay models.

## Decision labels

- **SUPPORTED AT POPULATION LEVEL:** gates 1–6 and 8 pass. Gate 7 determines whether the stronger alignment-specific statement is also supported.
- **ORDER SUPPORTED; QUARTER OR ALIGNMENT UNRESOLVED:** the child-half-before-crest sequence is robust but gate 3 or 7 fails.
- **NOT SUPPORTED:** the native ordering fails or child half does not reliably precede the delayed crest.

## Evidence boundary

The delayed branch combines two neutrino flavors statistically. T399 tests the timing geometry of the joint delayed population. It does not establish that each daughter neutrino individually carries \(0.5\), and it does not identify the exact creation time of a named neutrino from a named muon.
