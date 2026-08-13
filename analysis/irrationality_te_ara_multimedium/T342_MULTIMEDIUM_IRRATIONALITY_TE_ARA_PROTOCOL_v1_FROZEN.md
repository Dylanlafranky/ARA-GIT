# T342 frozen protocol — multi-medium Irrationality TE-ARA movement grammar

**Frozen:** 5 August 2026, after source-metadata inspection and before any
T342 numerical source was scored  
**Test ID:** `T342-MULTIMEDIUM-IRRATIONALITY-TE-ARA-v1`  
**Originator of the ARA hypothesis:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## 1. Question

Does one predeclared Irrationality Di-ARA/TE-ARA movement grammar survive
translation across materially different systems that contract, expand,
circulate, transmit or relax?

The primary question concerns the geometry:

1. are radial contraction/expansion and angular forward/reverse traversal both
   populated;
2. does chronological movement hand over locally around the four sectors more
   coherently than order-destroying controls;
3. does that result survive reversible ARA relabellings?

The secondary question concerns landmarks: do line-dominant observations
prefer `1/e <-> e`, and do circle-dominant observations prefer the reciprocal
golden turn, over fixed rational, irrational and fitted alternatives?

The secondary constants cannot rescue failure of the primary movement grammar.
Conversely, a successful movement grammar does not establish universal `e` or
Phi constants.

## 2. Frozen common coordinate

Every eligible lineage supplies two ordered physical channels `(u_t,v_t)`.
Their domain-specific physical meanings are frozen in section 7. Location and
scale parameters are calculated from the first 40% of that same lineage only,
unless zero is already a physical origin and both channels share units.

After the frozen centring/scaling rule,

\[
z_t=u_t+i v_t.
\]

For consecutive eligible states,

\[
q_t=\frac{z_{t+1}}{z_t}=s_t e^{i\Delta\theta_t},
\qquad
s_t>0,
\qquad
\Delta\theta_t\in(-\pi,\pi].
\]

The two ARA cuts are

\[
X_t=\frac{2s_t}{1+s_t},
\qquad
Y_t=1+\frac{\Delta\theta_t}{\pi}.
\]

`X` is the radial/diameter cut: contraction versus expansion. `Y` is the
angular/circumference cut: reverse versus forward traversal. Each is a full
ARA coordinate on `0..2`; neither is merely an extra label attached to the
other.

For complete TE-ARA bookkeeping, retain the opposing readings

\[
X_t^{\rm anti}=2-X_t,
\qquad
Y_t^{\rm anti}=2-Y_t.
\]

Therefore `X + X_anti = 2` and `Y + Y_anti = 2` are definitional closure
identities, not empirical results. T342 tests how observations move through
that complete geometry.

The signed local coordinates are

\[
a_t=\log s_t,
\qquad
b_t=\Delta\theta_t.
\]

They define the four oriented sectors:

| sector | radial sign | traversal sign |
|---|---:|---:|
| contracting reverse | `a < 0` | `b < 0` |
| expanding reverse | `a > 0` | `b < 0` |
| expanding forward | `a > 0` | `b > 0` |
| contracting forward | `a < 0` | `b > 0` |

The cyclic sector order is exactly the table order. Boundaries within
`1e-12` of either axis are recorded separately and excluded from four-sector
transition scoring.

## 3. Eligibility and split

Each independent lineage is divided chronologically:

- first 40%: calibration, including frozen centring/scaling parameters;
- next 30%: evaluation;
- final 30%: untouched holdout.

No transition may cross a lineage or split boundary.

A state is amplitude-valid when both consecutive radii exceed

\[
h=\max(10^{-12},Q_{0.05}^{\rm cal}(|z|\mid |z|>0)).
\]

The fifth-percentile floor is fixed before scoring and prevents unstable
division at the local origin. It is reported for every lineage. Missing,
non-finite and duplicated-time observations are omitted; no interpolation,
smoothing, Fourier transform, NMF, PCA or target-selected rotation is allowed.

A domain is inferentially eligible when its holdout contains at least 1,000
non-boundary transitions, at least 100 changed-sector transitions, and all
four sectors.

## 4. Primary ordered-grammar measurements

### 4.1 Four-sector coverage

Report the holdout share of every sector. A coverage pass requires every
sector to contain at least 1% of non-boundary steps. This is only a usability
gate; four signs alone are not evidence of ordered geometry.

### 4.2 Local handover adjacency

For each changed-sector transition, call a move adjacent when it changes by
one step around the frozen cyclic order and diagonal when it changes by two.

\[
A=\frac{N_{\rm adjacent}}
        {N_{\rm adjacent}+N_{\rm diagonal}}.
\]

Same-sector persistence is excluded from `A` so a slowly sampled or highly
persistent record cannot pass merely by standing still.

### 4.3 Ordered information

Calculate the normalized mutual information between consecutive sector
states:

\[
I_N=\frac{I(Q_t;Q_{t+1})}{H(Q_{t+1})}.
\]

This asks how much the present oriented ARA state tells us about the next one.
It is not called causal information.

### 4.4 Time-order null

Use 1,000 deterministic shuffles (`seed=3422026 + domain offset`). Shuffle the
sector order separately inside each lineage and split, retaining its length
and sector counts. Recompute `A` and `I_N`.

The chronological result passes each endpoint when it exceeds at least 95%
of its shuffled values:

\[
p=\frac{1+\#\{T_{null}\geq T_{obs}\}}{1001}<0.05.
\]

### 4.5 Symmetry checks

Recompute each domain after:

1. reversing chronological order inside each lineage;
2. swapping the two axes with `z'=v+i u`;
3. reversing one pole convention with `z'=-z`.

These transformations should relabel orientation while preserving coverage,
adjacency and ordered information to numerical tolerance. They are
implementation/symmetry checks, not independent evidence.

### 4.6 Domain and cross-domain primary verdict

A domain passes when it is eligible, passes four-sector coverage, and both
ordered endpoints beat their shuffle nulls at `p<0.05`.

Cross-domain support requires:

- at least five eligible domains; and
- at least 70% of eligible domains passing.

Anything below that is `PARTIAL / DOMAIN-SPECIFIC` if at least two domains
pass, or `NOT SUPPORTED` otherwise.

This gate tests a transferable relational grammar. Because smooth dynamical
systems can also favour local sector transitions, a pass is not proof that
ARA is the unique description.

## 5. Secondary pure-axis landmark audit

Define the unsigned line and circle magnitudes

\[
R=|\log s|,
\qquad
C=\frac{|\Delta\theta|}{2\pi},
\]

and the Di-ARA mixing angle

\[
\gamma=\operatorname{atan2}(|Y-1|,|X-1|).
\]

Use frozen 15-degree cones:

- line-dominant: `gamma <= 15 degrees`;
- circle-dominant: `gamma >= 75 degrees`.

Each cone requires at least 30 observations and at least 10 observations from
both orientations of its own axis.

Fixed radial candidates are plastic constant, `sqrt(2)`, `3/2`, Phi, `2` and
`e`. Fixed circular candidates are `1/4`, `1/3`, `1/e`, `3/8`, `phi^-2`,
`2/5` and `sqrt(2)-1` turns. Calibration medians are transferred unchanged as
identity-specific fitted controls.

Strong line support requires `e` to be the nearest fixed candidate in holdout,
absolute error at most `0.10`, and no worse error than the fitted control.
Strong circle support applies the analogous rule to `phi^-2`, with absolute
error at most `0.05` turns. Results are domain-level; values are never pooled
across media to create a universal median.

## 6. Additional descriptive movement measures

Report, without affecting the verdict:

- contraction/expansion and forward/reverse balance;
- same-sector persistence;
- clockwise versus counter-clockwise adjacent handovers;
- median TE-ARA coordinates `X` and `Y` by split;
- relation-plane density and transition matrices;
- domain-specific event traces;
- line/circle cone sensitivity at 10 and 20 degrees.

## 7. Frozen public-domain battery

### A. Mechanical pendulum

- Source: dynamicslab *MultiArm-Pendulum*, Zenodo
  `10.5281/zenodo.6633719`.
- Lineages: three free-swing runs crossed with arms 1, 2 and 3.
- Native channels: rest-centred arm angle and recorded angular velocity.
- The angular origin is the circular mean from calibration; velocity origin
  is physical zero. Each axis is divided by its calibration 95th percentile
  absolute magnitude. No filtering; native sample order is retained.

### B. Hydraulic test rig

- Source: UCI *Condition monitoring of hydraulic systems*, DOI
  `10.24432/C5CW21`.
- Lineages: all 2,205 sixty-second load cycles.
- Native channels: synchronized raw `PS1` and `PS2` pressure at 100 Hz.
- Each channel uses the calibration-cycle median as origin and calibration
  95th percentile absolute departure as scale. No cycle-crossing transition.

### C. Gas-liquid bubble motion

- Source: Pandey et al., *Bubble dynamics data for oscillating gas flow in a
  quasi-2D fluidized bed*, Zenodo `10.5281/zenodo.15102957`.
- Lineages: tracker-continuous `(source video, bubble ID)` tracks with at least
  eight strictly consecutive recorded frames.
- Native channels: recorded `x_velocity` and `y_velocity` in metres/second.
- Physical zero is retained; both axes use one shared calibration 95th
  percentile speed scale. No smoothing or track reconstruction.

### D. Cold-room thermal/humidity movement

- Source: Henrichs, Stoll and Krupitzer, *Temperature and Humidity Time Series
  of Cold Storage Room Monitoring*, Zenodo `10.5281/zenodo.15130001`.
- Lineages: the nine raw DHT22 logger files in `Raw.zip`.
- Native channels: recorded temperature and relative humidity at five-second
  cadence.
- Repeated headers are removed exactly; no missing values are imputed. Each
  channel uses its own calibration median and calibration 95th percentile
  absolute departure because the units differ.
- Door-opening intervals from `experiment_actions.csv` are reported as a
  frozen sensitivity, not used to select the primary full-record result.

### E. Acoustic impulse decay

- Source: OpenAIR, University of York, CC BY 4.0; Spring Lane Building real
  stereo room impulse responses.
- Lineages: the ten alphabetically listed `*_stereo_trimmed.wav` files in the
  public `stereo/` directory.
- Native channels: left and right recorded pressure samples.
- Physical zero is retained and both axes share the file's peak absolute
  pressure scale. The lineage starts at the first sample attaining the joint
  peak and continues through the supplied trimmed record. No envelope,
  spectrogram or Fourier transform is used.

### F. Recorded trapped-ion qutrit

- Source: *Sustained state-independent quantum contextual correlations from a
  single ion*, public `ExpDataYuOh.csv`; inherited checksum-locked Q53
  extraction.
- Lineages: the three frozen Q53 projection planes.
- Native relation: inherited `circle_strength` and `circle_heading` form
  `z=strength*exp(2*pi*i*heading)`. No new rotation or state reconstruction is
  fitted in T342.

### G. River path transfer

- Source: inherited T335 public river/thalweg field extraction.
- Lineages: the 41 intact ordered elevation-rank paths.
- Native relation: inherited consecutive `scale_ratio_s` and
  `turn_delta_rad`, converted directly to `q=s*exp(i*delta)`.
- This is an ordered spatial transfer rather than a temporal decay and is
  reported both inside the broad cross-domain battery and separately.

## 8. Evidence roles

Pendulum, hydraulic, bubble, qutrit and river numerical sources have been
opened in earlier ARA work. T342 is a newly frozen cross-question on them, not
independent discovery evidence.

Cold-room and acoustic numerical files have not been opened for T342 at
freeze. They are the fresh-source replications. Source metadata and filenames
were inspected to determine suitability before freezing.

## 9. Required outputs

- frozen protocol and SHA-256;
- source audit with URLs, licenses, file hashes and exclusions;
- reproducible Python analysis and independent validator;
- companion executable notebook;
- lineage/data-quality table;
- holdout domain summary, transition matrices and 1,000-null distributions;
- fixed-landmark and cone-sensitivity tables;
- machine-readable JSON/CSV;
- multi-panel figure and interactive HTML explorer;
- technical report with result-first wording and explicit limitations;
- claim/provenance updates only after validation.

## 10. Immediate rejection conditions

Reject or quarantine any domain if:

- its two axes were chosen after viewing T342 scores;
- a transform beyond the frozen centring/scaling creates its relation plane;
- transitions cross files, tracks, cycles or split boundaries;
- fewer than five domains remain inferentially eligible;
- the validator cannot reproduce source hashes, counts and primary metrics;
- fixed constants are promoted after a failed primary grammar;
- definitional TE-ARA closure is reported as an empirical discovery.

