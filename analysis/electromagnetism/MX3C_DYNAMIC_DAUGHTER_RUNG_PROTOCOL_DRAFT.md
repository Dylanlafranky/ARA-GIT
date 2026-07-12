# MX3c dynamic daughter-rung angle protocol

**Status:** DEVELOPMENT RUN / PRESSURE-DERIVED ANGLE NULL / PRESSURE STATE MARKER POSITIVE  
**Tier:** development on the existing archive; confirmation requires new noise/seed realisations

## Clarified claim

The 25-degree value used in MX3b was a heuristic fixed probe, not a proposed universal angle. The proposed ARA
mechanism is that the viewing direction is itself a changing wave supplied by the next coupled rung down. The analogy
is the heart example: an aggregate heart series sits near a cancellation ridge, while blood pressure carries adjacent
directional state.

For the plasma example, the parent ridge coordinates remain

\[
\underbrace{q(t)}_{\substack{\text{position along}\text{the identity ridge}}}
=
\frac{(G-1)+(F-1)}{\sqrt2},
\qquad
\underbrace{d(t)}_{\substack{\text{signed crossing}\text{of the ridge}}}
=
\frac{(G-1)-(F-1)}{\sqrt2}.
\]

The local parent-trajectory direction is

\[
\underbrace{\theta_{\mathrm{geom}}(t)}_{\substack{\text{observed direction}\text{through the ARA plane}}}
=
\operatorname{atan2}\!\left(\dot d(t),\dot q(t)\right).
\]

This angle is an outcome to explain, not a freely fitted predictor.

## Primary daughter-wave candidate

Use the spatial pressure/velocity-spread wave derived from the phase-space distribution:

\[
\underbrace{P(x,t)}_{\substack{\text{plasma pressure-like}\text{daughter observable}}}
=
\int
\underbrace{\left[v-\bar v(x,t)\right]^2}_{\text{local velocity spread}}
\underbrace{f(x,v,t)}_{\text{particle distribution}}
\,dv.
\]

At the already frozen identity mode (k_0=5), define its direction relative to the particle-source parent wave:

\[
\underbrace{\theta_{P}(t)}_{\substack{\text{next-rung}\text{daughter-wave angle}}}
=
\arg\!\left[
\widehat P_{k_0}(t)
\widehat\rho_{F,k_0}(t)^*
\right].
\]

The dynamic ARA reading is then

\[
\underbrace{Z_{\downarrow}(t)}_{\substack{\text{parent ridge read from}\text{the daughter-wave direction}}}
=
\underbrace{q(t)\cos\theta_P(t)}_{\text{along-ridge contribution}}
+
\underbrace{d(t)\sin\theta_P(t)}_{\text{cross-ridge contribution}}.
\]

The angle must come entirely from the pressure wave. It must not be chosen to maximise trapping prediction.

## Secondary comparators

- current/drift moment (J(x,t)=\int v f\,dv);
- third central moment or heat-flux-like wave (H(x,t)=\int(v-\bar v)^3f\,dv);
- fixed 25-degree MX3b projection;
- (q) alone, (d) alone and the full two-coordinate ((q,d)) model;
- field RMS, fundamental-mode fraction and absolute closure;
- independently estimated trapped fraction and mutual information as outcomes, never angle inputs.

Pressure is primary because Dylan's clarification specifically proposes an adjacent pressure-like rung. Current and
third-moment angles are disclosed controls, not alternatives from which the best is silently selected.

## Tests

1. **Circular direction association:** test whether (	heta_P(t)) predicts (	heta_{\mathrm{geom}}(t)) on held-out
   times using circular error and resultant length.
2. **Lead relation:** predeclare a small lag grid and test whether the daughter angle leads rather than merely follows
   the parent turn. Correct for all tested lags.
3. **Matched-amplitude identity state:** compare (Z_{\downarrow}) before and after the trapping peak using one-to-one
   amplitude matching without reused slices.
4. **Incremental state information:** compare amplitude+mode, fixed-angle, ((q,d)), daughter magnitude alone and
   daughter-directed (Z_{\downarrow}).
5. **Noise/seed convergence:** repeat unchanged in the full MX3 simulation family.

## Nulls

- circularly shift (	heta_P(t)) relative to (q,d);
- phase-randomise the pressure wave while preserving its spectrum;
- use pressure magnitude without its angle;
- use randomly selected fixed angles with the same model count;
- reverse time to test whether apparent lead direction survives;
- compare with current and third-moment controls under the same multiplicity correction.

## Success rule

The dynamic-rung hypothesis receives development support only if the pressure-derived angle:

- predicts held-out parent turning direction;
- contributes beyond pressure magnitude, (q,d), field amplitude and ordinary coherence;
- separates matched-amplitude identity states using one-to-one pairs;
- has a stable lead relation;
- survives phase-shift/random-angle nulls.

Substantial support additionally requires the same frozen construction to transfer across particle counts, seeds and
the held-out beam configuration.

## Failure rule

The claim is not supported if the apparent gain comes from pressure magnitude alone, only appears after angle/lag
selection, does not lead the parent direction, fails the shuffled-angle nulls or changes across numerical noise levels.

## Plain-language version

Do not ask which fixed viewing angle makes the plasma look best. Measure a smaller pressure-like wave inside the
plasma and let that wave supply the changing viewing direction. Then test whether it tells us which way the larger
identity is turning before the larger measurement reveals it. That is the direct plasma version of using blood
pressure to recover directional information missing from the aggregate heart ridge.

## Development result - 12 July 2026

The primary directional test failed. Pressure-angle versus parent-tangent resultant was 0.1045. Circular-shift null
\(p=0.9680\) and phase-randomised null \(p=0.9820\) place the observation below almost all null associations. The best
lag was -8 slices at the negative boundary, meaning pressure lagged rather than led the parent turn. A constant
training orientation offset rotated by nearly \(\pi\) in the held-late regime.

The pressure-directed scalar scored held-late \(R^2=0.9566\), but its angle was nearly constant and the scalar behaved
like another fixed parent projection. Adding it to \((q,d)\) reduced \(R^2\) from 0.8747 to 0.8305. It therefore did
not supply incremental daughter-direction information.

Pressure magnitude did carry a different result: across 36 one-to-one amplitude-matched pairs, its pre/post effect was
\(d_z=-0.8276\), with every post-peak value lower. Magnitude alone scored only \(R^2=0.1972\) held-late. It is a
strong development hysteresis/state marker, not a stable continuous trapping predictor.

**Decision:** reject pressure spatial phase as the missing dynamic angle. Retain pressure magnitude as an adjacent
state-variable lead for future independent testing. Do not promote the general next-rung claim from this result.

Post-test causal correction: Dylan's daughter wave is proposed to be born after the parent collision, not to lead the
parent. The MX3c lead requirement therefore tested the wrong causal version of the hypothesis. The observed negative
lag is qualitatively compatible with a following daughter, but it was at the tested boundary and the spatial-phase
association failed both null families. Thus pressure spatial phase remains rejected; the parent-to-daughter claim is
transferred to MX3d for a direct harmonic inheritance/bicoherence test.

Outputs: `MX3C_DYNAMIC_DAUGHTER_REPORT.md`, `MX3C_DYNAMIC_DAUGHTER_RESULTS.json`, and
`MX3C_DYNAMIC_DAUGHTER_RESULT.png`.
