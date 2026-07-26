# Q15 — Is unresolved \(H\) its own Phase-B identity?

**Date:** 24 July 2026  
**Status:** independently validated post-outcome calibration  
**Verdict:** **coherent but mixed; Phase B not promoted**

## Answer first

The unresolved quantum component is not merely featureless leftover error. It has a strong, repeatable trajectory
across the four Bell states, predicts a held-out Bell state, survives a destroyed-time-order control and appears
under both the Q8 residual definition and the independently purity-defined Q11 definition.

It did **not**, however, pass the stricter test for one dominant Phase-B identity in both protocols:

- Ramsey was strongly self-coherent;
- Hahn retained a common accumulation/release trajectory, but its rate of movement contained too much
  state-specific `Other`;
- the attractive Ramsey/Hahn handover correlation was not special to correct wait-time matching.

The safe conclusion is therefore:

\[
\boxed{
\text{unresolved }H
=
\text{recurring ARA candidate mode}
+
\text{material Other},
\quad
\text{not yet one pure Phase B}.
}
\]

## 1. The test that had been skipped

Q8 introduced

\[
H_{\rm Q8}=2-K-R.
\]

Q9 linked it closely to independently calculated purity loss. Q10 then gave this waveform an amplitude axis and
an opening/closing axis. But Q10's TE-ARA total described how the path occupied four quadrants; it did not measure:

\[
\underbrace{T_H}_{2}
=
\underbrace{H_{\rm self}}_{\text{repeatable identity}}
+
\underbrace{O_H}_{\text{state-specific or unresolved Other}}.
\]

Q15 performs that omitted decomposition before allowing the Phase-B name.

The primary unresolved waveform is

\[
U=2(1-\operatorname{Tr}\rho^2),
\]

which is purity loss calculated from each public two-qubit density matrix. The algebraic Q8 remainder is retained
only as a robustness definition.

## 2. How self and Other were separated

For each protocol and wait, Q15 averaged the unresolved trajectories of the four Bell states:

\[
U_{st}=\mu_t+\epsilon_{st}.
\]

- \(\mu_t\) is the part that repeats across all four identities;
- \(\epsilon_{st}\) is the state-specific remainder.

The test removed each state's starting level, so a large common grey baseline could not automatically pass. It
measured both:

1. the accumulated change \(D_s(t)=U_s(t)-U_s(t_0)\);
2. the movement rate \(G_s(t)=dU_s/dt\).

The conservative self-share is the weaker of those two:

\[
\eta_H=\min(\eta_D,\eta_G),
\qquad
H_{\rm self}=2\eta_H,
\qquad
O_H=2(1-\eta_H).
\]

This is an ARA participation account. It is not a claim that the plotted shares are separately conserved physical
energies.

## 3. Results

| Protocol | common change \(\eta_D\) | common rate \(\eta_G\) | conservative self \(\eta_H\) | TE-ARA self | TE-ARA Other | held-out \(R_D^2\) | held-out \(R_G^2\) | shuffled-time \(p\) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Ramsey | `0.997439` | `0.915259` | `0.915259` | `1.830519` | `0.169481` | `0.978916` | `0.677142` | `0.0001` |
| Hahn | `0.986048` | `0.676414` | `0.676414` | `1.352827` | `0.647173` | `0.955962` | `0.367521` | `0.0073` |

Both protocols passed the frozen **coherent-but-mixed** gate. Only Ramsey passed the frozen **dominant coherent
identity** gate.

The result is not caused by choosing one convenient unresolved definition:

| Protocol | correlation: Q8 algebraic \(H\) vs purity-defined \(U\) |
|---|---:|
| Ramsey | `0.974867` |
| Hahn | `0.988051` |

An unfrozen numerical robustness check used ordinary adjacent first differences instead of the frozen gradient.
It gave common rate shares of `0.878556` in Ramsey and `0.556833` in Hahn. The exact number changes, but the
important conclusion becomes stronger: Hahn movement is materially mixed.

### Plain-language reading

For Ramsey, almost the entire unresolved rise and most of its movement happen as one shared waveform across the
four Bell states. On the conservative TE-ARA account, about `1.831` of the total `2` belongs to that repeatable
mode and `0.169` belongs to Other.

For Hahn, the overall rise is still highly repeatable, but the detailed speed and bends differ much more by Bell
state. Its conservative account is about `1.353` self and `0.647` Other. That is a real common structure, but it
is not pure enough to safely call the whole grey region one Phase B.

## 4. Conditional Ramsey/Hahn handover

At the `16` state/wait pairs whose Ramsey and Hahn durations differ by no more than `2%`:

| Diagnostic | Result | Frozen requirement |
|---|---:|---:|
| sign agreement | `15/16 = 0.9375` | at least `0.75` |
| correlation, unresolved reduction vs visible recovery | `0.953478` | at least `0.80` |
| through-origin slope | `0.840035` | `0.5–1.5` |
| MAE from one-for-one handover | `0.091438` | at most `0.20` |
| median positive apparent refocusable share | `0.664349` | descriptive |
| correct-time correlation rematching \(p\) | `0.9973` | at most `0.05` |

The first four numbers look like a clean handover. The control changes the interpretation.

When Hahn waits were reassigned within each Bell state, while keeping every Hahn record physically intact, the
null correlation had median `0.976921`—higher than the correctly matched value `0.953478`. The correct
Ramsey/Hahn time correspondence is therefore not what creates the strong relation.

### Plain-language reading

Hahn leaves less unresolved purity loss and more visible Bell relation than Ramsey, and the two amounts nearly
balance. But both quantities move monotonically and come from the same density matrices. We can scramble which
nearby Hahn wait is paired with which Ramsey wait and still obtain an equally strong or stronger correlation.

So this dataset shows a complementary accounting relation. It does not isolate a timed parcel moving from the
unresolved component into the visible component.

## 5. What is now supported

Supported on this dataset:

1. purity-defined unresolved structure follows a highly repeatable accumulation path across four Bell identities;
2. its aligned time structure generalizes to a held-out Bell state;
3. the structure is far stronger than independently shuffled time order;
4. the same broad waveform appears under Q8's algebraic residual definition;
5. ARA's `self + Other = 2` decomposition exposes a real protocol difference flattened by the single grey total:
   Ramsey is self-dominant, whereas Hahn is mixed at the movement-rate level.

Not supported:

1. the entire unresolved component is one pure Phase B;
2. the Hahn waveform passes the dominant self-identity gate;
3. correct Ramsey/Hahn time pairing uniquely identifies a handover;
4. a new hidden quantum degree of freedom, an external environmental wave or a causal transfer outside the
   measured two-qubit account;
5. a new quantum law or proof of universal fractality.

## 6. Correct ARA label after Q15

The most faithful present label is:

\[
\boxed{
\text{purity-defined unresolved ARA mode}
\quad\text{or}\quad
\text{candidate Phase-B account}.
}
\]

`Phase B` may remain the hypothesis being tested, but it should not yet be used as an established physical name.

This result does not invalidate the Ramsey/Hahn quadrant. Ideal equal-duration Ramsey and Hahn control kernels are
still an exact sum/difference pair. It says only that the present sparse, already-open records do not promote the
grey unresolved total into one pure handover child.

## 7. Next decisive test

The clean next test is a new common-clock Ramsey/Hahn dataset or simulation whose protocol is frozen before its
outcomes are inspected:

1. use identical total evolution durations;
2. measure native phase-sensitive observables, not only purity and compact Bell totals;
3. separate echo-refocusable phase dispersion from irreversible relaxation and leakage;
4. train the unresolved self-mode on some Bell preparations and predict untouched preparations;
5. freeze a wait-specific handover curve;
6. test it against monotonic-time, density-matrix-accounting and wait-rematching controls.

Only a self-dominant unresolved mode plus a time-specific transfer that beats those controls should promote it to
a calibrated Phase B.

## Reproduction

Protocol:

- `Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_PROTOCOL_v1_FROZEN.md`
- SHA-256:
  `8d79aab4260343f51806ea22b563919aecf519904b1fc72c202854c56be23fe2`

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q15_unresolved_self_identity_te_ara_test.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q15_unresolved_self_identity_te_ara_validate.py'
```

Validation status: `PASS`, with zero reported failures.

Artifacts:

- `Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_RESULTS.json`
- `Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_METRICS.csv`
- `Q15_UNRESOLVED_PHASE_B_HANDOVER_RECORDS.csv`
- `Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA.svg`
- `Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_VALIDATION.json`

## 25 July 2026 post-result method correction

The frozen Q15 calculation and its numerical verdict remain unchanged, but `self + Other = 2` should not be read
as a complete TE-ARA identity decomposition. Under the clarified ARA canon, Phase A and Phase B are mandatory:

\[
\mathrm{Phase\ A}+\mathrm{Phase\ B}+\sum\mathrm{Other}=2.
\]

Q15 measured recurring unresolved-mode participation versus a state-specific remainder; it did not independently
identify that mode's own Phase A and Phase B. The result remains a proxy/coherence audit and candidate Phase-B
account, not a measured complete hidden identity. Full correction:
`Q15_TE_ARA_METHOD_CORRECTION_2026-07-25.md`.
