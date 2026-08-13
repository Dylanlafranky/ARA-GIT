# T371 — COHERENT stopped-pion → muon Di-ARA handover

**Date:** 13 August 2026  
**Frozen verdict:** **TWO-STAGE DI-ARA HANDOVER RECOVERED**  
**Claim class:** strong recovery/crosswalk of a known decay lineage; not a new-particle or universal-geometry discovery

## Result first

The public COHERENT CsI[Na] record resolves the stopped-pion source into the
ordered pair proposed for this test:

\[
\underbrace{\pi^+\to\nu_\mu+\mu^+}_{\text{prompt pion release}}
\quad\longrightarrow\quad
\underbrace{\mu^+\to e^++\nu_e+\bar\nu_\mu}_{\text{delayed muon release}}.
\]

The registered two-component fit recovered:

- **prompt `nu_mu`:** **60.18** detected recoils, 95% bootstrap interval
  **[32.42, 89.20]**;
- **delayed `nu_e + anti-nu_mu`:** **258.94** detected recoils, interval
  **[187.92, 333.30]**.

Together these give **319.12** fitted CEvNS recoils, close to COHERENT's
published full-fit result of **306 +/- 20**. T371 is an independent compact
reconstruction and is not expected to reproduce every profiled systematic in
the collaboration analysis.

The prompt crest occurs in the first 0.5-microsecond bin, centred at
**0.25 us**. The delayed crest is one bin later, at **0.75 us**. Their
instantaneous fitted contributions become equal at **0.492 us**, with a
bootstrap interval **[0.325, 0.763] us**. Half of the fitted total release has
accumulated by **1.146 us**; this is the cumulative ARA ridge and is not the
same event as instantaneous branch equality.

### Native-resolution correction (T372)

The original cumulative figure plotted completed 0.5-microsecond bins at
their centres. Interpolating that display at the equality line produced an
apparent cumulative coordinate of `0.494`; that is not a valid native
integral. T372 reconstructed the supplied source timing at its native
1-nanosecond resolution. The corrected equality is **0.636 us**, at cumulative
ARA coordinate **0.437** (95% parametric-bootstrap interval
**[0.179,0.692]**). Exact `0.5` remains inside the uncertainty but is not
confirmed. The original T371 frozen verdict about two ordered branches is
unchanged; only the post-result child-half interpretation is corrected.

Primary correction:
`T372_CHILD_HALF_HANDOVER_GRADIENT_REPORT_2026-08-13.md`.

All six frozen gates passed.

## Plain-language ARA reading

This does not look like one neutrino identity simply fading with time. It
looks like one sharp release handing the record to a second, slower release:

1. the pion branch appears promptly;
2. its muon sibling persists for an open interval;
3. the muon branch then releases two neutrino children over a longer tail.

That is a Di-ARA rather than one flattened ARA because two coupled handovers
share the same repeated parent chain. We can preserve both branches, their
order and their different shapes without pretending the delayed pair is four
separately observed quadrants. COHERENT cannot distinguish `nu_e` from
`anti-nu_mu` event by event in this neutral-current record.

## Why this is not merely an early/late histogram

The raw timing excess has a large early peak, but prompt beam-related neutrons
also occupy that region. Delayed neutrinos and neutrino-induced neutrons have
very similar timing tails. Therefore timing alone is ambiguous.

T371 used the released two-dimensional recoil-energy × arrival-time record and
kept four families explicit:

- steady background measured in the anti-coincident window;
- prompt beam-related neutrons;
- neutrino-induced neutrons;
- CEvNS signal split into prompt and delayed neutrino branches.

The energy axis separates components whose timing shapes look alike. Only
after this extraction were the two neutrino branches compressed onto an ARA
pair.

## Frozen controls

| comparison | result |
|---|---:|
| full ordered pair vs prompt-only | ΔAIC **+57.68** for the pair |
| full ordered pair vs delayed-only | ΔAIC **+18.48** for the pair |
| correct order vs prompt/delayed timing swapped | ΔAIC **+12.85** for correct order |
| 1,000 random time-bin permutations | **0/1,000** fit as well |
| leave one of six energy bins out | both branches positive in **6/6** |
| leave one of twelve time bins out | both branches positive in **12/12** |

The physically fixed combined CEvNS template was **1.86 AIC units better**
than allowing the prompt/delayed ratio to float independently. This is an
important restraint: the data strongly require the known two-stage shape, but
do not justify a new free branch-ratio law beyond the supplied physical model.

## ARA 0–2 compression

After extraction only, the detected shares give

\[
x_{\rm prompt}=0.377,
\qquad
x_{\rm delayed}=1.623,
\qquad
x_{\rm prompt}+x_{\rm delayed}=2.
\]

The 95% intervals are `[0.201, 0.601]` and `[1.399, 1.799]`.

The pair lies strikingly close to `(2-phi, phi) = (0.382, 1.618)`, but **this is
not evidence for Phi here**:

1. the sum of two is forced by the declared compression;
2. the intervals are broad;
3. the standard detector-weighted decay model predicts
   `(0.341, 1.659)` before fitting the branch ratio;
4. that fixed physical ratio fits slightly better than two free branch
   normalizations.

The evidential result is the independently resolved order and two-stage
shape—not proximity to a preferred landmark.

## Side-by-side translation

| ARA | Established particle description |
|---|---|
| Prompt parent release | `pi+ -> mu+ + nu_mu` |
| Open child interval | stopped muon lifetime distribution |
| Delayed child release | `mu+ -> e+ + nu_e + anti-nu_mu` |
| Di-ARA parent | repeated stopped-pion chain containing both releases |
| Instantaneous branch equality at 0.492 us | point where fitted prompt and delayed event rates are equal |
| Cumulative ARA ridge at 1.146 us | time by which half the fitted neutrino-induced recoil population has arrived |
| Delayed pair remains compressed | flavor-blind CEvNS does not resolve `nu_e` from `anti-nu_mu` event by event |

## Frozen gates

| gate | result |
|---|---:|
| G1 source hashes, counts and boundaries | **PASS** |
| G2 both 95% intervals above zero | **PASS** |
| G3 ΔAIC ≥ 10 over each single physical branch | **PASS** |
| G4 at most 10/1,000 permutations as good | **PASS — 0/1,000** |
| G5 delayed crest follows prompt crest | **PASS** |
| G6 both branches survive every leave-one-bin check | **PASS** |

## Scientific boundary

These are ensemble populations from many source cycles. The archive does not
tag one pion, its particular muon child and all of that event's neutrinos as a
linked family. A pass therefore shows that the known parent–child lineage is
retained in the population and that an ARA-first two-stage representation
recovers it cleanly.

It does **not**:

- prove ARA's universal fractal-sphere hypothesis;
- discover the pion–muon chain, which is established physics;
- establish a new Phi law;
- show that neutrinos climb back into a later pion identity;
- resolve `nu_e` and `anti-nu_mu` as separate delayed children in this detector;
- establish event-level entanglement between prompt and delayed detections.

## Reproduction

```powershell
$env:PYTHONPATH='F:\SystemFormulaFolder\.codex_python_packages'
$env:MPLCONFIGDIR='F:\SystemFormulaFolder\.matplotlib'
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\muon\t371_coherent_pion_muon_diara.py'
```

Source: `arXiv:2110.07730v2` ancillary material. Every consumed source hash is
stored in `T371_COHERENT_PION_MUON_DIARA_RESULTS.json`.
