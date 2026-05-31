# Endpoint (A-node) vs Exchange-channel mix test — REAL EEG (slpdb)
Date: 2026-05-30. Data: PhysioNet slpdb EEG, 18 cached records, fs=250 Hz, raw.

## Hypothesis (from exchange-channel reading of ENSO)
An A-node builds its own phi-tower (mix test PASSES, z>=2). A pure exchange channel /
tether only INHERITS structure (mix test FAILS: phase-scrambling costs little -> low z).
Test: raw EEG anchored at theta scale = A-node (predict PASS). Gamma (30-50 Hz) amplitude
envelope = the theta<->gamma shuttle = exchange (predict FAIL).

## Method
dot(x,P): r1,r2,r3 = P, P*phi, P*phi^2 at P_theta=41.7 samp (~6 Hz).
gen = bp(bp(x,r1)*bp(x,r2), r3); ac = bp(x,r3); recon = peak xcorr(gen,ac);
z vs 15 phase-randomized spectrum-matched surrogate nulls. Caveat noted: envelope is a
derived signal, but its slow-band spectrum is intact so r3 is NOT removed (not the
rigged-to-fail trap of pre-isolating the target rung).

## Result — PREDICTION NOT SUPPORTED (came back opposite)
| signal | n | z_med | recon_med | pass(z>=2) |
|---|---|---|---|---|
| A-node (raw EEG) | 5 | +3.2 | +0.118 | 60% |
| Exchange (gamma env) | 5 | **+19.1** | +0.362 | **100%** |

Per record (z A-node | z exchange): 14.5|19.1, 0.5|15.2, 0.8|29.0, 3.2|14.4, 10.5|21.3.
Records where A-node PASSES and exchange FAILS: **0/5**.

The "exchange" signal built its phi-tower MORE strongly than the raw signal in every record.

## Reading
The gamma amplitude envelope is NOT a passive tether. It carries its own nested
cross-frequency hierarchy (envelope-of-gamma is itself rhythmically self-organized), so it
self-builds even harder than broadband EEG. My operationalization of "exchange channel" as
a band-amplitude envelope is therefore WRONG — an envelope is still an A-node-like builder,
not a pure R/tether.

## Net (third cross-check)
Three independent attempts to exhibit the "endpoints PASS / exchange FAILS" split have now
all failed to produce it:
  1. Brown/Gold ENSO meta-bands — not a phi pair (EXCHANGE_LOOP_RESULT.md)
  2. Jupiter/Saturn orbital — wrong lattice, integer-resonance clockwork (EXCHANGE_ORBITAL_RESULT.md)
  3. Brain gamma envelope — "exchange" self-builds harder than the endpoint (this file)

The exchange-channel READING of ENSO still rests ONLY on its original P2 fingerprint
(recon +0.67 / z +0.7 = high inherited structure, low self-build). We still have NO
independent system where a genuine exchange channel fails the mix test while its endpoints
pass. Open problem: we have not yet found/defined a TRUE exchange signal (one defined
independently of our own filtering, like ENSO's published index = difference of two systems).
A band-envelope is not it.
