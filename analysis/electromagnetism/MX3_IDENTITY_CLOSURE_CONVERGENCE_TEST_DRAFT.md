# MX3 draft — noise-controlled identity-closure convergence test

**Prepared:** 12 July 2026  
**Status:** `PROPOSED / NOT RUN / REQUIRES SIMULATION DESIGN FREEZE`  
**Question:** Does the TE-ARA field/particle closure index measure physical coherent-identity formation, or does it
merely improve as particle noise falls and field amplitude rises?

## Outcome first

Run the same deliberately seeded two-stream instability at several particle-noise levels, with a noise-free continuum
Vlasov–Poisson reference if feasible. Keep the physical instability identical while changing measurement/discreteness
noise. Compare the candidate ARA identity-closure index against independently measured particle trapping and
phase-space structure.

This is more decisive than another uncontrolled example because the strongest remaining alternative is finite-particle
signal-to-noise.

## Candidate coordinate

\[
\underbrace{C_{\mathrm{id}}(t)}_{\substack{\text{candidate 0--1}\\\text{identity-closure index}}}
=
1-\frac{
\left|
\underbrace{\mathrm{TE\!-\!ARA}_{\rho,G}(t)}_{\text{field-predicted source participation}}
-
\underbrace{\mathrm{TE\!-\!ARA}_{\rho,F}(t)}_{\text{particle-measured source participation}}
\right|
}{2}.
\]

\(C_{\mathrm{id}}=1\) means the two independently obtained source views assign the same participation fraction to the
declared identity family. It does not by itself prove particle trapping, causality or a unique physical identity.

## Controlled simulation family

Use identical:

- beam drift, thermal speed and density;
- domain, grid, timestep and boundary conditions;
- deliberately imposed small mode-5 perturbation;
- identity-family declaration;
- output cadence and analysis code.

Vary only particle/distribution noise:

1. continuum or very-high-resolution Vlasov–Poisson reference;
2. at least four effective particles-per-cell levels spanning roughly two orders of magnitude;
3. at least ten random particle seeds per level;
4. one held-out beam drift or thermal-speed configuration for transfer.

The imposed coherent seed is essential: if the instability is allowed to begin from numerical noise, changing
particles per cell also changes physical onset time and confounds the test.

Exact particle counts, solver and seeds must be frozen before outcomes.

## Independent ground-truth diagnostics

Measure without using \(C_{\mathrm{id}}\):

1. electric-field mode amplitude and energy;
2. field–particle power \(J\cdot E\);
3. trapped-particle fraction inside the independently reconstructed wave-potential separatrix;
4. distribution flattening or plateau formation near resonant velocity;
5. phase-space-vortex/hole coherence using a predeclared image/moment statistic;
6. ordinary field/particle spectral coherence;
7. nonlinear saturation time.

The primary physical identity-onset label should use trapped-particle fraction plus phase-space-vortex coherence, not
field amplitude alone.

## Predeclared competing explanations

### Physical identity-closure marker

- \(C_{\mathrm{id}}\) converges to a non-trivial continuum trajectory as particle count rises.
- Its transition aligns with independently measured trapping/coherent-structure onset.
- It adds onset/state information after field amplitude and ordinary coherence are controlled.
- The same threshold transfers to different particle seeds and the held-out beam configuration.

### Noise/SNR marker

- \(1-C_{\mathrm{id}}\) scales primarily as \(N_{\mathrm{ppc}}^{-1/2}\).
- \(C_{\mathrm{id}}\) approaches one trivially before physical trapping in the continuum/high-count limit.
- Field amplitude and generic spectral coherence explain the same transition.
- Thresholds change with particle count, seed or smoothing.

### Descriptive but non-unique coherence marker

- \(C_{\mathrm{id}}\) follows physical organisation but adds no held-out information beyond standard coherence or
  trapping metrics.

This outcome would still validate the ARA coordinate as a compact restatement, but not establish a new diagnostic.

## Primary comparisons

### Noise convergence

\[
\underbrace{1-C_{\mathrm{id}}}_{\text{identity mismatch}}
\stackrel{?}{=}
\underbrace{\alpha N_{\mathrm{ppc}}^{-1/2}}_{\text{finite-particle noise}}
+
\underbrace{g(\text{physical state})}_{\text{noise-independent remainder}}.
\]

A physical contribution requires a reproducible nonzero state-dependent remainder after noise extrapolation.

### Incremental onset information

\[
\underbrace{\text{trapping/coherent onset}}_{\text{independent target}}
\sim
\underbrace{E_{\mathrm{rms}}+\text{ordinary coherence}+\text{noise level}}_{\text{control model}}
+
\underbrace{C_{\mathrm{id}}}_{\text{ARA-added coordinate}}.
\]

Report held-out onset classification, timing error and calibration. Do not select the onset threshold on the held-out
configuration.

### Matched-amplitude comparison

Compare slices with the same field amplitude before and after trapping/saturation. If \(C_{\mathrm{id}}\) separates
those states while amplitude is fixed, it is not merely an amplitude gauge.

## Necessary nulls and safeguards

- matched random harmonic families;
- shuffled particle phases while preserving spectra;
- time-shuffled \(C_{\mathrm{id}}\);
- alternative grid resolution at fixed particles per Debye length;
- analysis with and without permitted smoothing, frozen before confirmation;
- report every particle-count level and seed;
- do not redefine the identity family after viewing phase-space vortices;
- do not promote a lead that appears only at one noise level.

## Decision rule

### Substantial support

The same \(C_{\mathrm{id}}\) definition:

- converges across particle count toward the continuum reference;
- tracks independently labelled trapping/coherent onset;
- adds held-out value beyond amplitude, noise and standard coherence;
- transfers to the changed beam configuration.

### Useful but established-equivalent

It converges and tracks onset but adds nothing beyond standard diagnostics.

### Not supported

It is explained by \(N_{\mathrm{ppc}}^{-1/2}\), amplitude or smoothing; or its threshold fails to transfer.

## Sequence

1. Run the already-frozen MX1 Tang transfer first; do not alter MX1.
2. Freeze MX3 solver, counts, seeds, onset labels, baselines and thresholds.
3. Run simulation calibration cases.
4. Hash the analysis and freeze the held-out beam configuration.
5. Open and score the held-out configuration once.
6. Only then consider ENSO or LLM identity-closure claims.

## Plain-language version

Create the same plasma event several times, but make the particle picture progressively cleaner. If the TE-ARA closure
curve merely improves in proportion to cleaner measurement, it is a noise meter. If it settles onto the same physical
curve and changes specifically when particles become trapped into a coherent phase-space structure—even when field
amplitude is held constant—then it is measuring identity formation in a non-trivial way.

## MX3a existing-data feasibility result — 12 July 2026

The single available Alves/OSIRIS realisation was analysed across all 459 slices as development-only feasibility.
This does not satisfy MX3 because particle count, particle seed and a continuum reference do not vary.

The phase-space distribution visibly develops coherent repeated trapped/vortical structure. On 299 eligible slices,
the candidate \(C_{\mathrm{id}}\) correlates 0.8428 with normalised position–momentum mutual information, 0.7612 with
velocity-bin phase coherence and 0.7519 with an approximate fundamental-wave trapped fraction. It also correlates
0.8293 with field RMS, leaving amplitude as a strong competing explanation.

The pre-peak versus post-peak matched-amplitude test is the central null. Eighty pairs matched within 1% field RMS
produce post-minus-pre \(C_{\mathrm{id}}=-0.00080\), mutual information \(=+0.00099\), and approximate trapped
fraction \(=+0.02622\). The current scalar closure index therefore does not separate structural history at fixed
amplitude in this archive.

A chronological 70/30 development model improves approximate-trapping \(R^2\) from 0.7071 to 0.8461 when closure is
added to field RMS and fundamental-mode fraction. Mutual-information and rank-2 held-late models remain strongly
negative in \(R^2\) and provide no predictive support.

The visual check also established a necessary definition fence: \(C_{\mathrm{id}}\) is undefined before coherent-mode
eligibility. Two near-zero summaries can agree trivially and create a high raw closure value without a formed
identity.

**MX3a status:** `ORGANISATION VISIBLE / CLOSURE CO-MOVES / MATCHED-AMPLITUDE SEPARATION NULL / FULL NOISE CONVERGENCE STILL REQUIRED`.

Detailed output: `MX3A_EXISTING_DATA_REPORT.md` and `MX3A_EXISTING_DATA_RESULTS.json`.

## MX3b angled-ridge development result - 12 July 2026

The predeclared 25-degree ARA view tested whether absolute distance from \(G=F\) had discarded direction along the
ridge. Define

\[
q=\frac{(G-1)+(F-1)}{\sqrt2},\qquad
d=\frac{(G-1)-(F-1)}{\sqrt2},\qquad
Z_\theta=q\cos\theta+d\sin\theta.
\]

On the final 30% chronological block, the amplitude-plus-mode baseline scored \(R^2=0.7071\), absolute closure 0.8461,
ridge-parallel \(q\) 0.9581 and predeclared \(Z_{25^\circ}\) 0.9475. Retaining ridge position therefore adds useful
late-state information.

The angle did not validate as a stable law. Every angle had negative \(R^2\) on the earlier internal validation block;
25 degrees scored -6.3285 there. Pure \(q\) slightly beat 25 degrees held-late. A one-to-one 36-pair amplitude match
gave only \(d_z=0.1190\) for the 25-degree projection, versus \(d_z=0.8796\) for independently estimated trapping.
Direct field-particle phase was nearly fixed and did not improve the result.

**MX3b status:** `RIDGE-TANGENT INFORMATION POSITIVE / ANGLE-SPECIFIC TRANSFER NOT SUPPORTED`.

Detailed output: `MX3B_ANGLED_RIDGE_REPORT.md` and `MX3B_ANGLED_RIDGE_RESULTS.json`.

Post-test clarification: 25 degrees was a heuristic fixed probe, not the proposed law. The intended angle is a
changing daughter wave supplied by the next coupled rung. MX3c therefore uses a pressure/velocity-spread wave to
provide the angle independently, analogous to blood pressure supplying state absent from an aggregate heart ridge.
See `MX3C_DYNAMIC_DAUGHTER_RUNG_PROTOCOL_DRAFT.md`.

MX3c development result: the pressure spatial-phase angle failed the directional nulls (resultant 0.1045;
circular-shift \(p=0.9680\); phase-randomised \(p=0.9820\)) and lagged rather than led. Pressure magnitude strongly
separated one-to-one matched-amplitude states \(d_z=-0.8276\), but did not predict the continuous held-late trapping
trajectory well \(R^2=0.1972\). Pressure remains an adjacent state-marker candidate; its spatial phase is rejected as
the missing daughter angle.

Dylan subsequently corrected the causal direction: an echo daughter should be born after the parent collision. MX3c's
lead requirement is therefore retired, without converting its failed spatial-phase nulls into support. MX3d now tests
positive parent-to-daughter lag, harmonic phase inheritance, bicoherence and independent daughter persistence. See
`MX3D_PARENT_COLLISION_DAUGHTER_ECHO_PROTOCOL_DRAFT.md`.

MX3d development result: the declared \(k=10\) daughter followed parent \(k=5\) by 19 field slices and 31 particle
slices. Phase closure rose from 0.2873 baseline to 0.9848 during sub-threshold formation and remained 0.9352 after
onset. Field/particle bicoherence was 0.8376/0.8334 at the 97.48th/94.96th control percentiles. The daughter persisted
262 slices and had field/particle TE correlation 0.9991. Six of eight gates passed; circular-shift locality and the
particle 95th-percentile gate failed. Status: strong development support for nonlinear daughter identity, not
universal/fractal confirmation.

MX3e then tested Dylan's sharper next-generation prediction: daughter self-coupling
\(k=10+k=10\rightarrow20\). The k20 field/particle onsets followed k10 by 63/57 slices. Phase concentration rose from
0.3146 baseline to 0.8439 before visible k20 onset and remained 0.8481 afterwards; random-phase \(p=0.0010\).
Field/particle bicoherence was 0.5760/0.6022 at the 90th percentile among routes summing to 20. The mixed
\(k=5+k=15\rightarrow20\) route was much weaker, while \(k=9+k=11\rightarrow20\) was stronger than 10+10, indicating
a coupling web rather than unique genealogy. The fine k20 mode persisted 199 slices, carried mean field-power fraction
0.001739 and had field/particle TE correlation 0.9988. All eight development criteria passed. See
`MX3E_GRANDDAUGHTER_REPORT.md`.

MX3g predeclared k40 and k80. k40 is jointly detectable and passes 6/8 gates, but exact 20+20 coupling is weak;
stronger routes form a broad web, including near-ridge 19+21 in particles. k80 crosses only the field threshold at
3.2 samples per wavelength; no particle identity is recovered. k160 exceeds Nyquist. The operational floor lies
between k40 and k80 in this archive, but is numerical rather than a demonstrated physical singularity. No phase flip
is testable. See `MX3G_GREAT_GRANDCHILD_FLOOR_REPORT.md`.
