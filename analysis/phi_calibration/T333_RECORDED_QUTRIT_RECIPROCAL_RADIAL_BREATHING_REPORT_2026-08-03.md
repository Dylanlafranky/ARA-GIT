# T333 — recorded-qutrit reciprocal radial breathing

**Date:** 3 August 2026  
**Frozen verdict:** **NOT SUPPORTED for universal
\(1/\phi\leftrightarrow\phi\) radial endpoints**  
**Coordinate result:** **a stable reciprocal radial breath and all four complex
ARA quadrants are present**  
**Independent validation:** **PASS — 14/14 checks**

## Answer first

The external-vector geometry survived the move from the Phi-containing muon
scheduler to a real recorded quantum measurement sequence, but **Phi did not
survive as the primary numerical radial pole**.

Using Q53's frozen algebraic whole-circle centre, the first half of the record
gave

\[
0.552668\longleftrightarrow1.808822,
\]

and the untouched second half gave

\[
\boxed{0.553331\longleftrightarrow1.806922}.
\]

The two endpoint products were `0.999678` and `0.999826`. The radial motion is
therefore extraordinarily reciprocal and stable across time, but its measured
scale is approximately

\[
\alpha\approx1.809,
\]

not \(\phi\approx1.618\).

The exact frozen Phi pair won only `3/21` primary plane-lag cells. The octave
candidate was closer in the remaining `18/21`. A reciprocal scale fitted only
on the first half, `1.809114`, predicted the second half with log-distance
`0.002251`; exact Phi's distance was `0.221000`. The universal
reciprocal-Phi endpoint claim therefore fails the registered specificity,
absolute-endpoint and fitted-control gates.

What remains important is that the ordered record was substantially more
Phi-ward than the same amplitudes shuffled in time. All three cuts and the
pooled record beat every one of `500` registered nulls
(`p=1/501=0.001996`). Thus time order changes the breathing scale; it simply
does not move it all the way to Phi in the primary coordinate.

## Plain-language ARA reading

Each retained Q53 event is the movement of one complete fitted circle. T333
kept both pieces of that movement:

- how strong or radially large the movement was;
- which way it pointed.

Comparing one event with a later event produced:

\[
q=\frac{z_{t+\ell}}{z_t}=s e^{i\delta}.
\]

`s` says whether the next whole-vector contracts or expands. `delta` says
whether it turns forward or reverse. This gives four ARA states without
importing a Fourier transform or imposing Phi:

1. contracting–reverse;
2. contracting–forward;
3. expanding–reverse;
4. expanding–forward.

All four appeared in every sphere cut. At lag one each occupied almost exactly
one quarter of the record. That confirms the full two-axis coordinate is
usable, although the exceptionally even shares are also consistent with the
source experiment's randomized selection of measurement rays. Equal quadrant
occupancy is therefore not by itself evidence of an ARA mechanism.

The deeper result is the repeatable radial scale:

```text
                    calibration       holdout
contraction          0.552668          0.553331
expansion            1.808822          1.806922
product              0.999678          0.999826
fitted alpha         1.809114          fixed from calibration
```

In ARA terms, this looks like a **time-facing radial breathing coordinate**,
but the amount of breath is identity- and measurement-definition-sensitive.
The geometry is clearer than the proposed universal constant.

## Frozen primary results

### Endpoint stability across the three sphere cuts

| sphere cut | contraction | expansion | product | closest fixed pair |
|---|---:|---:|---:|---|
| \((\psi_0,\psi_1)\) | 0.554043 | 1.804655 | 0.999857 | octave |
| \((\psi_1,\psi_2)\) | 0.552852 | 1.808858 | 1.000031 | octave |
| \((\psi_2,\psi_0)\) | 0.553105 | 1.807141 | 0.999539 | octave |
| pooled | **0.553331** | **1.806922** | **0.999826** | octave |

The three independently oriented cuts agree very closely. Relative to the
registered golden endpoints, contraction was about `10.4–10.5%` below
\(1/\phi\) and expansion was about `11.5–11.8%` above \(\phi\). All three
therefore failed the frozen 10% absolute-endpoint gate.

### Fixed-pair competition

Across the `21` primary holdout cells:

- octave \((1/2,2)\): `18` wins;
- reciprocal Phi \((1/\phi,\phi)\): `3` wins;
- every other registered pair: `0` wins.

The pooled score was slightly closer to octave (`0.202871`) than Phi
(`0.221000`). Neither fixed value describes the data nearly as accurately as
the first-half fitted reciprocal scale (`0.002251` on holdout).

### Temporal-order control

| cut | observed Phi distance | shuffle 5th percentile | empirical p |
|---|---:|---:|---:|
| \((\psi_0,\psi_1)\) | 0.218458 | 0.253092 | 0.001996 |
| \((\psi_1,\psi_2)\) | 0.222937 | 0.253537 | 0.001996 |
| \((\psi_2,\psi_0)\) | 0.221529 | 0.252055 | 0.001996 |
| pooled | **0.221000** | **0.254028** | **0.001996** |

The real ordering consistently narrows the breathing scale relative to
blockwise temporal permutation. This is evidence that the sequence order
carries radial information. It is not evidence that the endpoint equals Phi:
the ordered endpoint remains approximately `1.807`.

## Estimator split: useful clue, not a rescue

The two frozen sensitivity centres behaved differently:

| centre definition | contraction | expansion | product | fitted reciprocal \(\alpha\) | Phi cell wins |
|---|---:|---:|---:|---:|---:|
| algebraic fitted-circle centre — **primary** | 0.553331 | 1.806922 | 0.999826 | 1.807079 | 3/21 |
| point centroid | 0.589264 | 1.699874 | 1.001674 | 1.698453 | 21/21 |
| extrema midpoint | 0.589508 | 1.697993 | 1.000980 | 1.697162 | 21/21 |

The centroid and extrema constructions independently move toward the golden
pair and select Phi over the other widely spaced fixed candidates in all
cells. But their endpoints are still roughly `4.6–5.1%` away from exact Phi,
and all three centre definitions are derived from the same measured circuits.
Most importantly, the primary definition was frozen in advance. Sensitivities
cannot replace it after the result.

Scientifically, the split says that radial scale is not invariant to how the
whole circle's centre is defined. That is precisely the kind of
identity/measurement dependence ARA allows, but it blocks a claim that one
universal numerical endpoint has been recovered here.

## Gate table

| gate | result |
|---|---|
| G0 — source and implementation integrity | **PASS**; validator 14/14 |
| G1 — usable four-quadrant coordinate | **PASS**; every quadrant ≈25% in every cut |
| G2 — Phi wins at least 15/21 primary cells | **FAIL**; 3/21 |
| G3 — absolute golden endpoints in at least two cuts | **FAIL**; 0/3 |
| G4 — ordered record beats temporal null | **PASS**; 3/3 and pooled p=0.001996 |
| G5 — Phi beats first-half fitted reciprocal scale | **FAIL**; 0.221000 vs 0.002251 |
| G6 — centre sensitivity | **MIXED**; both secondary centres move Phi-ward |

Only one of the four substantive endpoint/order gates G2–G5 passed. The
frozen verdict is therefore **NOT SUPPORTED**, not partial support.

## What this changes

T333 rejects two over-compressed claims:

1. the asymmetric pair \(1/e\leftrightarrow\phi\) is not the recorded radial
   breath here;
2. reciprocal \(1/\phi\leftrightarrow\phi\) is not a universal radial pair in
   the frozen primary external-vector definition.

It strengthens a narrower architecture:

\[
\boxed{
q_t=s_t e^{i\delta_t}
}
\]

is a useful ARA decomposition of recorded whole-vector change, and the radial
component can form a stable approximately reciprocal pair. Its value must be
measured for the identity and centre definition rather than assumed to be
Phi, octave or \(e\).

This is compatible with keeping \(1/e\) as a separate exponential-decay
landmark. T333 did not test a decay envelope, so it neither supports nor
rejects that narrower role.

## Best next test

The next experiment should not hunt for another constant first. It should ask
why the same hardware record produces approximately `1.807` for the fitted
circle centre but approximately `1.698` for two simpler centres.

A useful frozen follow-up would:

1. derive all centre constructions from one explicit ARA identity boundary;
2. test whether their radial \(\alpha\) values transform predictably under
   translation, scale, noise and circle-shape distortion;
3. use one centre rule to predict another on a withheld sphere cut;
4. then carry the predeclared rule to a second independent time-resolved
   archive.

If the endpoint moves arbitrarily with estimator choice, it is a coordinate
artefact. If the movement follows a stable cross-centre transformation and
predicts a second archive, it becomes evidence for a genuine radial hierarchy.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\phi_calibration\t333_recorded_qutrit_reciprocal_radial_breathing.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\phi_calibration\validate_t333_recorded_qutrit_reciprocal_radial_breathing.py'
```

Artifacts:

- frozen protocol:
  `T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_PROTOCOL_v1_FROZEN.md`;
- machine-readable result:
  `T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_RESULTS.json`;
- all `126` estimator × split × cut × lag cells:
  `T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_CELLS.csv`;
- four-quadrant audit:
  `T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_QUADRANTS.csv`;
- all `2,000` null rows:
  `T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_NULLS.csv`;
- independent validator:
  `T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_VALIDATION.json`;
- figure:
  `T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING.png`.

## Evidence boundary

The underlying archive is real recorded hardware data, but the external
whole-circle vectors are a Q53 measurement-derived construction. T333 asks a
new frozen question on an archive that had already been opened for a different
test. It therefore provides strong internal cross-question evidence, not a
pristine independent discovery. The next archive must be selected and frozen
before its corresponding radial endpoints are inspected.
