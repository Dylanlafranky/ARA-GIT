# Camshaft φ provenance audit

**Date:** 12 July 2026.  
**Status:** the mechanical analogy is useful; the claimed universal/F1 `φ` optimum is not established.

## Origin of the claim

The surviving transcript is `journey/transcripts/early_sessions/ARA_Session_Transcript_Apr18-21.txt`, lines
approximately 3749–3923. An AI-generated explanation chose a representative racing-cam advertised duration of
`275°` over a four-stroke `720°` cycle and formed

```text
closed / open = (720 - 275) / 275 = 445 / 275 = 1.61818...
```

That numerical equality is real. It does not show that Formula 1 engineers selected `φ`, that `275°` is a universal
optimum, or that an engineering optimization independently returned the golden ratio. Indeed,

```text
D_phi = 720 / (1 + phi) = 275.016...
```

so choosing a duration near `275°` essentially guarantees the complement ratio will look golden.

The transcript's cited commercial articles explain valve duration, overlap, manifold-wave tuning, and reversion.
They do not establish a universal golden optimum. The transcript also shifted between “racing” and “Formula 1”
without evidence that the example was an F1 cam specification.

## What established engineering does support

Valve lift, duration, timing, and overlap are jointly optimized for a particular engine, speed range, intake and
exhaust geometry, constraints, and measurement convention. Reverse flow/reversion is real. An SAE Formula Student
study, for example, reduced overlap to mitigate reverse exhaust flow and used a validated engine model to optimize
lift, duration, and timing; it did not report a universal `φ` condition:

- McClintock et al., “Camshaft Design for an Inlet-Restricted FSAE Engine,” SAE Technical Paper 2008-32-0073,
  <https://doi.org/10.4271/2008-32-0073>.

Advertised duration also depends on the lift threshold used to declare the valve “open,” so ratios from different
cam cards are not automatically comparable.

## What remains useful to ARA

The engine is still an excellent explicit accumulation–handover–release system:

- chamber pressure and spring/valvetrain energy can be measured separately;
- intake and exhaust pulses have phase, overlap, reflection, and reversion;
- timing can be changed experimentally;
- torque, volumetric efficiency, emissions, stress and loss provide independent outcomes.

The repository's later `0.39/0.61` two-band dominance result on 54 ECG records and ENSO is a separate empirical
claim. It must not inherit validation from the `275°` cam example.

## Clean future test

1. Freeze one definition of valve-open duration and one operating-condition family.
2. Collect a broad cam/engine dataset including non-`275°` designs.
3. Predict the optimum duty before reading performance results.
4. Compare `φ` against nearby ratios and a domain engine model that uses RPM, runner geometry, overlap and lift.
5. Score torque/efficiency and reversion separately.

Until that test exists, call the camshaft a **physical analogy and prospective test bed**, not independent
confirmation of `φ` or a Formula 1 engineering result.
