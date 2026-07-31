# T317 — Solar-System Barycentric ARA Pair

**Registered:** 31 July 2026, before downloading the new multi-body tables  
**Status:** crosswalk/calibration, not a blind discovery  
**Primary question:** When the Solar System is defined natively as
Sun Phase A plus the combined planetary systems Phase B, what parts of the
ARA description are independently measured, what parts are forced by
barycentric conservation, and what non-forced internal structure remains?

## Prior knowledge and contamination boundary

The following are established before the run and cannot count as discoveries:

1. In a Solar-System barycentric frame, total momentum is conserved and the
   Sun's momentum is approximately opposite the combined momentum of the
   other bodies.
2. Jupiter is expected to be a major driver of the Sun's barycentric motion.
3. The earlier orbital T309 result used Earth relative to the Sun as a child
   projected directly against a fixed Galactic parent. Dylan then corrected
   the intended Solar-System ARA identity to Sun Phase A versus the planets
   collectively as Phase B.

The test may establish a faithful numerical crosswalk and quantify residual,
composition and cadence structure. It cannot claim that ARA independently
discovered barycentric conservation, Jupiter's importance or planetary
periods.

## Public source and frozen population

NASA/JPL Horizons geometric vector tables:

- target `10`: Sun;
- targets `1`–`9`: Mercury through Pluto system barycentres;
- centre `500@0`: Solar-System barycentre;
- frame: ecliptic ICRF/J2000;
- correction: none;
- units: km and km/s;
- time scale: TDB;
- interval: `1900-01-01` through `2101-01-01`;
- cadence: five days.

The long interval is chosen before inspection so Jupiter-, Saturn- and slower
planetary contributions can be separated. The primary eight-planet Phase B
uses targets `1`–`8`. Target `9` is an extended-system sensitivity, not part
of the primary planet definition.

Mass weights are the DE440 gravitational parameters published by JPL. Since
every term is multiplied by the same gravitational constant, GM-weighted
velocity has the same relative vector geometry as momentum without requiring
an estimate of \(G\):

\[
\mathbf p_i^\star=(GM)_i\mathbf v_i.
\]

## Frozen ARA assignment

\[
\underbrace{\mathbf A(t)}_{\text{Sun / Phase A}}
=
(GM)_\odot\mathbf v_\odot(t),
\]

\[
\underbrace{\mathbf B_8(t)}_{\text{eight planetary systems / Phase B}}
=
\sum_{i=1}^{8}(GM)_i\mathbf v_i(t).
\]

The extended sensitivity is

\[
\mathbf B_9(t)=\sum_{i=1}^{9}(GM)_i\mathbf v_i(t).
\]

The independently measured magnitude coordinates are

\[
x_A(t)=
\frac{2\lVert\mathbf A(t)\rVert}
{\lVert\mathbf A(t)\rVert+\lVert\mathbf B(t)\rVert},
\qquad
x_B(t)=
\frac{2\lVert\mathbf B(t)\rVert}
{\lVert\mathbf A(t)\rVert+\lVert\mathbf B(t)\rVert}.
\]

Their sum of two is normalization and must not be counted as evidence. The
informative quantities are the independently observed balance, opposition
and residual:

\[
\theta_{\rm opp}(t)
=
\angle\!\left(\mathbf A(t),-\mathbf B(t)\right),
\]

\[
h_{\rm Other}(t)
=
\frac{2\lVert\mathbf A(t)+\mathbf B(t)\rVert}
{\lVert\mathbf A(t)\rVert+\lVert\mathbf B(t)\rVert}.
\]

The same calculations will be repeated for GM-weighted positions. Position
closure and velocity closure answer different questions and will not be
combined.

## Frozen primary gates

These gates test whether the selected measured object correctly reconstructs
the known whole. Passing them is validation of the ARA crosswalk, not new
physics.

For the extended nine-system calculation:

1. median velocity \(x_A\) lies in `[0.995, 1.005]`;
2. median velocity \(x_B\) lies in `[0.995, 1.005]`;
3. median velocity opposition error is below `0.05°`;
4. median velocity Other is below `0.005` TE-ARA units;
5. median position opposition error is below `0.05°`;
6. median position Other is below `0.005` TE-ARA units.

The eight-planet version is primary for the semantic claim “planets”; the
nine-system version tests whether the omitted Pluto-system term materially
improves closure. The known residual from asteroids and other integrated
bodies is retained as Other rather than silently assigned to either pole.

## Non-forced descriptive analyses

The following are exploratory measurements, not frozen pass/fail claims:

1. each planetary system's signed projection onto the combined Phase-B
   direction;
2. each system's absolute GM-weighted movement share;
3. which system is the largest instantaneous contributor and how often;
4. the strongest periods in the Sun and combined-planet vector components;
5. how much the eight-to-nine-system extension reduces the unresolved Other;
6. how closely the completed Solar-System barycentric velocity follows an
   externally supplied modern Galactocentric parent vector after internal
   A/B cancellation.

The final item is bookkeeping at the next rung:

\[
\mathbf V_{\rm whole}(t)
=
\mathbf V_{\rm Galactic}
+
\frac{\mathbf A(t)+\mathbf B(t)}
{(GM)_\odot+\sum_i(GM)_i}.
\]

It must not be described as a new Galactic dynamical model.

## Controls and failure conditions

1. **Frame control:** all bodies must have the same centre, reference plane,
   units, time scale, dates and cadence.
2. **Source integrity:** raw Horizons responses and parsed vectors are
   retained with SHA-256 hashes.
3. **Mass control:** every GM value is recorded from the same JPL DE440 table.
4. **Eight versus nine:** Pluto is a named sensitivity, not an after-the-fact
   rescue.
5. **Forced-identity warning:** \(x_A+x_B=2\) is algebraically forced.
6. **Conservation warning:** near opposition is expected from established
   barycentric mechanics. Only the quantified residual, composition and
   cadence provide additional descriptive information.
7. **No `7.5° : 15°` target:** this corrected Solar-System A/B test does not
   inherit the earlier Earth-child/Galactic-parent numeric gate.
8. **Failure:** if the extended pair misses any primary gate after source and
   implementation checks, the proposed measured object is not accepted as a
   faithful numerical Solar-System ARA crosswalk.

## Required outputs

- complete reproducer and public-data downloader;
- compact time-series and planetary-composition tables;
- JSON numerical record with hashes and gate results;
- static technical figure;
- technical Markdown record;
- independent validator that does not import the analysis script;
- updates to the calibration README, Claims Status and Provenance Ledger.

