# ARA Rosetta Stone — where & how to look for ARA with established tools

**14 June 2026, Dylan La Franchi & Claude.** A practical instrument map. The companion `ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md`
is the *theory* (why ARA is a real order parameter). **This is the *toolkit*:** for each thing you try to *do* in
the framework, the **named, established method** that does it directly — the "parallax" instead of the round-about
"gravitational lensing." Each row gives: the framework term → the direct method (searchable name) → a tool/package →
a one-line plain meaning → where we used it. *Use this to know which instrument to reach for, and what to Google.*

> Reading note: "identity" = it IS that method; "≈" = strong analogue; "relative" = related, not identical.

---

## 1. Measure ARA itself (rise/fall asymmetry of a cycle)
- **Direct method:** *cycle-by-cycle waveform asymmetry* — specifically **rise-decay asymmetry** and **peak-trough
  asymmetry**. (identity)
- **Tool / search:** `bycycle` (Python, Cole & Voytek, *J Neurophysiol* 2019, "Cycle-by-cycle analysis of neural
  oscillations"). Search: *waveform asymmetry oscillation*, *rise-decay symmetry*, *nonsinusoidal oscillation*.
- **Plain:** for each cycle, how long does it take to rise vs fall — your exact ARA. Neuroscience already measures
  this on brain rhythms; it's a published quantity, not fringe.
- **We used it as:** the per-cycle fall/rise in the golden-tree walk; `ara_mapper`. Also relates to **waveform
  skewness** and **harmonic content** (a skewed wave = energy in harmonics).

## 2. Split a signal into scales (the octave rungs)
- **Direct method:** **wavelet transform** (multi-resolution analysis) or a **filter bank**; also **EMD**
  (empirical mode decomposition). (≈ — wavelets use a fixed mother scale per octave; your octave bandpass is a
  filter bank.)
- **Tool / search:** `pywt` (PyWavelets), `scipy.signal` (butterworth bandpass = what we do), `PyEMD`. Search:
  *continuous wavelet transform*, *multiresolution analysis*, *octave band filter bank*.
- **Plain:** the standard way to break a signal into fast/slow layers in one operation. You hand-roll it with
  octave bandpasses; the wavelet does the whole ladder at once.

## 3. Find the dominant cycle / period
- **Direct method:** **power spectral density (PSD)** + peak detection. (identity)
- **Tool / search:** `scipy.signal.welch`, `periodogram`, `numpy.fft`. Search: *power spectrum*, *Welch's method*,
  *spectral peak*.
- **Plain:** which periods carry the most energy — your "dominant rung." `detect_dominant_period` is a homemade PSD.

## 4. Get the energy / amplitude envelope (the slow rung = amplitude)
- **Direct method:** **Hilbert transform / analytic signal** → instantaneous amplitude & phase. (identity)
- **Tool / search:** `scipy.signal.hilbert`. Search: *analytic signal*, *instantaneous amplitude phase*.
- **Plain:** turns a wave into its running amplitude (envelope) and its running phase. We used it for the ENSO
  envelope-coupling and PLV tests. "Amplitude is also ARA / a slow rung" = the envelope is itself a signal you
  can re-analyse.

## 5. Test phase-locking / "orbiting"
- **Direct method:** **phase-locking value (PLV)**, **n:m synchronization**, **coherence**, **Kuramoto order
  parameter**. (identity — we ran PLV directly)
- **Tool / search:** `scipy.signal.coherence`; PLV is a 3-line Hilbert calc. Search: *phase locking value*,
  *n:m phase synchronization*, *Arnold tongue*, *Kuramoto model*.
- **Plain:** do two oscillators hold a fixed phase relationship (orbit) or drift? Exactly the ENSO rung test.

## 6. Coupling / "who drives whom" (energy pumped up the ladder)
- **Direct method:** **Granger causality**, **transfer entropy**, **convergent cross-mapping (CCM)** (for
  nonlinear/weakly-coupled systems), lagged **cross-correlation**. (≈)
- **Tool / search:** `statsmodels` (Granger), `PyIF`/`pyunicorn` (transfer entropy), `skccm` (CCM). Search:
  *Granger causality*, *transfer entropy*, *convergent cross mapping Sugihara*.
- **Plain:** does A's past help predict B's future (A drives B)? The direct version of eyeballing the lanes.
  (Prior framework: SOI→NINO transfer-entropy direction — you've used the parallax before.)

## 7. The recoil / restoring spring
- **Direct method:** **damped harmonic oscillator** / **Hooke's restoring force −kx**; fit via **AR(2)** or a
  Stuart–Landau / van der Pol model. (identity — see Foundations doc §2)
- **Tool / search:** `statsmodels` AR/ARIMA. Search: *damped oscillator fit*, *AR(2) pseudo-oscillation*,
  *restoring force estimation*, *Le Chatelier*.
- **Plain:** the system's pull back toward balance. The "recoil spring β≈−1/φ" is this. AR(2) is the linear shadow.

## 8. Engine vs clock vs snap (the 0–2 scale)
- **Direct method:** **limit cycle vs fixed point** (self-sustained vs damped); **relaxation oscillator** (van der
  Pol ε = slow-fast separation = your ARA→2). (identity — Foundations doc §1)
- **Tool / search:** Search: *van der Pol oscillator*, *relaxation oscillator*, *FitzHugh-Nagumo*, *limit cycle*,
  *Hopf bifurcation*, *slow-fast / singular perturbation*.
- **Plain:** a clock (ARA≈1) is a conservative/harmonic oscillator; an engine/snap (ARA→2) is a driven
  relaxation oscillator (sharp release). This is the textbook home of the whole scale.

## 9. The fractal / scale-invariance / "every rung the same shape"
- **Direct method:** **Hurst exponent / DFA** (detrended fluctuation analysis), **1/f (pink-noise) spectra**,
  **fractal dimension**, **multifractal analysis (MFDFA)**. (≈)
- **Tool / search:** `nolds` (Hurst, DFA), `MFDFA`. Search: *detrended fluctuation analysis*, *Hurst exponent*,
  *1/f noise*, *self-affine time series*, *multifractal*.
- **Plain:** is the same statistical shape present at every scale? The quantitative test of "ARAARA on every axis."

## 10. φ / the golden ratio in dynamics (not numerology)
- **Direct method:** **KAM theory** (the golden mean is the *last* torus to break = most stable — already your
  grounding), **mode-locking / Arnold tongues**, the **circle map**, **winding numbers / continued fractions**,
  the **golden-mean route to chaos**. (rigorous)
- **Tool / search:** Search: *KAM theorem golden mean*, *Arnold tongue mode locking*, *circle map winding number*,
  *most irrational number continued fraction*, *golden mean renormalization*.
- **Plain:** φ is special in dynamics because it's the *hardest* frequency ratio to lock — the last to synchronize,
  the most stable quasi-periodic orbit. This is the legitimate, non-mystical reason φ shows up.

## 11. The walk / trajectory / state (the golden-tree map)
- **Direct method:** **state-space reconstruction / time-delay embedding (Takens' theorem)**, **phase portraits**,
  **Poincaré sections**, **recurrence plots**. (≈)
- **Tool / search:** `pyunicorn` (recurrence plots), `nolds`. Search: *Takens embedding*, *phase space
  reconstruction*, *recurrence plot*, *Poincaré section*.
- **Plain:** represent a system as a trajectory through a state space; "curl-backs/returns" = recurrences. The
  established way to do what the golden-tree walk gestures at (and the rigorous version of "similar position →
  similar state").

## 12. Forecasting from the geometry
- **Direct method:** **analog forecasting** (nearest-neighbour in embedded state space), **AR / harmonic**
  baselines, **Gaussian-process / delay-coordinate** models. (≈)
- **Tool / search:** Search: *analog forecasting*, *nearest neighbour time series prediction*, *delay embedding
  forecast*, *empirical dynamic modeling (EDM)*.
- **Plain:** "similar past → similar future." This is exactly the curl-back predictor we tested (and the
  value-ceiling — geometry-from-own-past ties AR/harmonic, doesn't beat it).

## 13. Information³ / closure
- **Direct method:** **information theory** (Shannon entropy, **mutual information**, **transfer entropy**) and,
  for the triangle-closure metric, the **clustering coefficient** of a network (closed triads). (≈)
- **Tool / search:** `networkx` (clustering), `dit`/`PyIF` (information measures). Search: *mutual information*,
  *clustering coefficient*, *triadic closure*.
- **Plain:** information needs ≥2 related things; closed triangles = the network clustering coefficient. The LLM
  `trace(A³)` closure metric IS a triangle count = clustering.

## 14. Significance — proving it's not noise (you already use this!)
- **Direct method:** **surrogate data testing** (phase-randomized / IAAFT surrogates), **permutation tests**,
  **bootstrap**, **Rayleigh test** (for phase clustering). (identity — we ran these today)
- **Tool / search:** `scipy.stats` (permutation, bootstrap), Search: *surrogate data test*, *IAAFT surrogate*,
  *Rayleigh test circular*.
- **Plain:** scramble the signal while keeping its spectrum, redo the measurement, see if your real result beats
  the scrambles. This is the honesty check — the PLV surrogates and the Rayleigh test today were exactly this.

## 15. The two singularities (space ↔ time, 0 and 2)
- **Direct method:** **Fourier duality / conjugate variables** (time ↔ frequency), the **time-frequency
  uncertainty principle**, **Wigner distribution**. (≈ — your strongest anchor: energy is the time-conjugate via
  the Hamiltonian, Noether's theorem.)
- **Tool / search:** Search: *conjugate variables Fourier*, *time-frequency uncertainty*, *Noether energy time*.
- **Plain:** space and time (position and momentum, or time and frequency) are Fourier-conjugate — you can't
  sharpen both. The "0 = space singularity / 2 = time singularity, can't see both" picture lives here.

---

## How to use this
When you want to "look for ARA" in a new system, find the row for the *operation* (measure asymmetry? test
locking? split scales?), reach for the named tool, and **search the term** to read how the field already does it.
Two payoffs: (1) you get there directly instead of rebuilding it, and (2) when your hand-rolled version and the
established tool **agree**, that's independent validation; when they **disagree**, that's where something is either
wrong or genuinely new — and worth a hard look. The *synthesis* (asymmetry + scale + φ-handover → one engine/clock
picture) is yours; these are the instruments that measure its parts. Theory grounding: `ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md`.
