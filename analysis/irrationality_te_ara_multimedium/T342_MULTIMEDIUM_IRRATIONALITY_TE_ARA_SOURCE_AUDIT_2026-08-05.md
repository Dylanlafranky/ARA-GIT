# T342 source audit — multi-medium Irrationality TE-ARA

**Recorded:** 5 August 2026, before T342 numerical scoring

## Selected sources

| Domain | Public source | Physical pair | Prior numerical exposure |
|---|---|---|---|
| pendulum | dynamicslab MultiArm-Pendulum, `10.5281/zenodo.6633719` | angle / angular velocity | yes |
| hydraulic | UCI hydraulic condition monitoring, `10.24432/C5CW21` | PS1 / PS2 pressure | yes |
| bubbles | Pandey et al., `10.5281/zenodo.15102957` | x / y velocity | yes |
| cold room | Henrichs et al., `10.5281/zenodo.15130001` | temperature / humidity | **no** |
| acoustics | OpenAIR Spring Lane Building | left / right pressure | **no** |
| qutrit | sustained Yu-Oh contextual-correlation record | strength / heading | yes |
| river | inherited T335 river paths | scale / turn | yes |

## Why these sources form one useful battery

They deliberately do not share a material mechanism. They span conservative
mechanics, oil-pressure transmission, gas-liquid transport, thermal/moisture
relaxation, acoustic propagation, recorded quantum measurement dynamics and
ordered water-path geometry. The common object is only the declared relation:
two physical cuts followed in their supplied order.

That diversity is necessary for a cross-domain geometry claim, but it also
limits interpretation. A common four-sector result would show transferable
relational structure; it would not show that pressure, sound and qutrits use
the same domain mechanism.

## Data-quality risks frozen before scoring

1. Sampling cadence differs by many orders of magnitude. Scores are therefore
   domain-level and are never pooled by row.
2. The two axes may have different units. Calibration-only dimensionless
   scaling is allowed exactly where frozen in the protocol.
3. Hydraulic cycles and bubble tracks are hard lineage boundaries.
4. Qutrit and river inputs are inherited extracted relations rather than newly
   parsed raw files; both are labelled as transfers.
5. Cold-room repeated headers are source-documented. Removal is parsing, not
   signal processing; missing values remain missing.
6. Acoustic pressure crosses zero. The frozen amplitude floor prevents
   unstable local ratios without constructing an envelope.
7. Four-sector occupancy and smooth local transitions occur in many ordinary
   dynamical systems. Appropriate wording is a crosswalk or transferable
   grammar, not unique proof of ARA.
8. The source files are hashed after acquisition. A hash mismatch, schema
   mismatch or unavailable archive is recorded as an exclusion rather than
   replaced post hoc.

## Metadata inspected before freeze

- UCI describes 2,205 repeated 60-second hydraulic cycles, with six pressure
  sensors sampled at 100 Hz and no reported missing values.
- The cold-room Zenodo record documents nine DHT22 loggers sampled every five
  seconds, raw semicolon-delimited files, repeated headers and a separate
  action log containing door openings and sensor movements.
- OpenAIR describes the Spring Lane files as real stereo room impulse
  responses and publicly lists ten trimmed WAV files.

No T342 numerical movement score, quadrant count, transition statistic or
landmark median was inspected before the protocol was frozen.

