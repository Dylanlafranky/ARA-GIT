# T371 — COHERENT pion–muon Di-ARA handover

**Frozen:** 13 August 2026, after source-schema inspection and before reading the 2021 event values or fitting any outcome  
**Evidence class:** public unbinned physical data; known-decay crosswalk/calibration  
**Status at freeze:** `EXACT ENOUGH TO TEST`

## Question

Does the detected stopped-pion neutrino population require the ordered pair

\[
\pi^+\to\nu_\mu+\mu^+
\quad\longrightarrow\quad
\mu^+\to e^++\nu_e+\bar\nu_\mu,
\]

rather than one undifferentiated release branch?

In ARA language, the proposed relation is a two-stage Di-ARA handover:

\[
\text{prompt pion release}
\longrightarrow
\text{open muon interval}
\longrightarrow
\text{delayed muon release}.
\]

This is a recovery/crosswalk of a known decay chain, not a test of whether ARA
predicts a previously unknown particle or decay law.

## Who, what, when, where, why and how

- **Who:** neutrinos from stopped positive-pion chains at the Spallation
  Neutron Source, observed through coherent elastic neutrino–nucleus
  scattering in COHERENT's CsI[Na] detector.
- **What:** the prompt `nu_mu` population produced at pion decay and the
  delayed `nu_e + anti-nu_mu` population produced when the muon child decays.
  The detector is flavor-blind within each timing population, so the two
  delayed flavors remain one observed branch.
- **When:** reconstructed recoil time `0 <= t_rec < 6 microseconds` relative to
  the beam pulse.
- **Where:** reconstructed recoil energy `0 <= PE < 60` in the public 2021 CsI
  sample. Beam-coincident events are the candidate population; the immediately
  preceding anti-coincident region supplies the measured steady background.
- **Why:** this is the closest public measurement found to the proposed
  same-parent/sibling handover. It observes the prompt and delayed children in
  the same detector and the same source cycles.
- **How:** fit the chronological prompt and delayed neutrino timing templates
  together after retaining steady-state, prompt-neutron and
  neutrino-induced-neutron backgrounds as separate components. Compare with
  prompt-only, delayed-only, unordered and time-shuffled controls. Only after
  the data-only/component fit is complete is the collaboration's supplied
  flavor-resolved source model used as the physical crosscheck.

## Source

- COHERENT Collaboration, `arXiv:2110.07730v2` ancillary release.
- Event files: `dataBeamOnC.txt`, `dataBeamOnAC.txt`.
- Background files: `brnPE.txt`, `brnTrec.txt`, `ninPE.txt`, `ninTrec.txt`.
- Source file: `snsFlux2D.root`, containing separate flavor histograms.
- The release reports 13.99 GWhr exposure and the analysis region above.

SHA-256 hashes of every consumed source file must be written to the result
record before the verdict is issued.

## Native instrument

### Observed 2D record

Bin the unbinned events in fixed bins:

- energy: six 10-PE bins on `[0,60)`;
- time: twelve 0.5-microsecond bins on `[0,6)`.

The beam-coincident and anti-coincident counts are kept separate in the
likelihood; no negative-count clipping is allowed.

### Four component families

1. measured steady-state background from the anti-coincident record;
2. prompt beam-related neutrons from the released PE and timing shapes;
3. neutrino-induced neutrons from the released PE and timing shapes;
4. CEvNS signal decomposed into:
   - prompt `nu_mu`;
   - delayed `nu_e + anti-nu_mu`.

The prompt and delayed CEvNS normalizations are non-negative free parameters.
Background normalizations use the collaboration's published constraints. No
ARA landmark, golden-ratio landmark or forced `x_A+x_B=2` condition enters the
fit.

### ARA compression after extraction

If the fitted detected prompt and delayed totals are `P` and `D`, record

\[
x_P=\frac{2P}{P+D},\qquad x_D=\frac{2D}{P+D}.
\]

Their sum is two by construction and is bookkeeping only. The empirical
finding is where the pair rests, its uncertainty, its chronological separation
and whether both branches are required. No success claim may be based merely
on `x_P+x_D=2`.

## Primary measurements

1. fitted prompt and delayed CEvNS counts with bootstrap intervals;
2. likelihood improvement of the ordered two-branch model over prompt-only,
   delayed-only and one-free-shape single-branch controls;
3. chronological-order advantage over 1,000 fixed-seed time-bin permutations
   of the two signal templates;
4. time of the prompt crest, delayed crest and prompt/delayed equality
   handover, with uncertainty;
5. energy distributions of events probabilistically assigned to each branch;
6. post-extraction ARA coordinates `(x_P,x_D)` and the cumulative 0–2 release
   path.

## Frozen gates

The verdict `TWO-STAGE DI-ARA HANDOVER RECOVERED` requires:

1. source hashes, event totals and analysis boundaries reproduce correctly;
2. both fitted signal normalizations have 95% bootstrap intervals above zero;
3. the ordered two-branch model improves AIC by at least 10 over each
   prompt-only and delayed-only model;
4. no more than 10 of 1,000 time permutations fit as well as the registered
   chronological order;
5. the delayed crest occurs after the prompt crest in at least 95% of bootstrap
   replicates;
6. both branches retain direction under energy-bin and time-bin leave-one-out
   checks.

If both branches are detected but the order/permutation gate fails, report
`TWO POPULATIONS WITHOUT ORDERED-HANDOVER SUPPORT`. If one branch is not
resolved, report `PUBLIC RECORD DOES NOT RESOLVE BOTH HANDOVERS`.

## Scientific boundary

The experiment does not observe a pion, its muon child and all neutrinos from
one individually tagged decay as a linked event. It observes ensemble recoil
populations from many repeated stopped-pion chains. A pass therefore shows
that the population retains the known two-stage lineage and that ARA can
represent it without flattening the stages. It does not establish event-level
entanglement, prove the universal fractal-sphere proposal, distinguish `nu_e`
from `anti-nu_mu`, or show that neutrinos climb back into a pion cycle.

