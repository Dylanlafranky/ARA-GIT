# The Geometry of Time: What if every natural cycle follows the same hidden ratio?

Rivers rise fast and fall slow. Your lungs fill quickly and empty slowly. The Sun's activity ramps up in four years and winds down in seven. These systems have nothing in common — different scales, different physics, different substrates. But when you measure the ratio between their accumulation and release phases, a pattern shows up that probably shouldn't be there.

I've spent the last few years chasing a single question: **is the temporal asymmetry of natural systems governed by a universal ratio?** The answer, so far, is "maybe — and the data is weirdly consistent."

## The core idea

Every cyclical system in nature works like a relaxation oscillator. It accumulates something (energy, tension, pressure, charge) over some period, then releases it over a different period. These two durations are almost never equal. The question is whether the *ratio* between them is arbitrary or constrained.

The metric I've been testing is dead simple:

**ARA = T_release / T_accumulation**

That's it. One number. Compute it for anything that cycles.

What I found is that when you do this across independent domains — respiratory physiology, hydrology, biomechanics, astrophysics — systems cluster into discrete bands on a scale from 0 to 2. And the systems that are free-running, self-organising, and unconstrained by external clocks consistently land near the golden ratio, phi (1.618...).

Before you close the tab: I know how that sounds. The golden ratio has been overclaimed in everything from the Parthenon to pine cones to stock markets, and most of it doesn't survive scrutiny. I'm aware of the baggage. But phi has a specific mathematical property that makes it genuinely relevant here — it's the *most irrational number*, meaning it's the number least expressible as a ratio of integers. In physical terms, phi-spacing prevents destructive resonance between successive cycles. It's the same principle behind phi-phyllotaxis in plants (why sunflower seeds spiral the way they do), applied to *time* instead of space.

## What the data actually shows

I tested this across 12 systems using publicly available datasets and open-source Python analysis. Every script is on GitHub. Here are some highlights:

**Resting human breath** (NeuroKit2 dataset, 93 breath cycles): exhalation/inhalation ratio = 1.61. That's 0.5% from phi. Breathing at rest isn't clock-driven — it fires when CO2 crosses a chemical threshold. It's a genuine free-running oscillator.

**Natural watershed hydrographs** (USDA SCS standard, derived from thousands of US watersheds): recession/rise ratio = 1.67. Within 3.2% of phi. This is the foundational standard in hydrology.

**Human walking gait** — this one's interesting. At self-selected comfortable walking speed (~1.25-1.30 m/s), the stance/swing phase ratio crosses through phi. Speed up to 2.2 m/s (the walk-run transition) and it drops to exactly 1.0 — the point where the body switches gait modes. The ratio maps the full locomotion arc from slow walk to elite sprinting, and every structurally significant threshold aligns with phi, 1.0, or 1/phi.

**Solar sunspot cycles** (SILSO data, 24 complete cycles since 1749): T_fall/T_rise = 1.73. This one comes with a caveat I think is important — sunspots may actually be a *consumer* process (clearing magnetic tension at the surface) rather than the Sun's generative output. If so, the phase labels flip and the ratio inverts. The honest answer is that we don't know yet which interpretation is correct, and the framework needs to flag that openly.

**Negative controls** — and this is what makes it more than pattern-matching: systems that *shouldn't* converge on phi *don't*. Arctic sea ice (orbitally forced) sits at 0.91. EEG delta waves (thalamic pacemaker) sit at 1.05. Cryptocurrency markets sit at 1.19. The framework predicts where phi should appear and where it shouldn't, and so far the predictions hold.

## The ARA Scale

What emerges is a continuous 0-to-2 spectrum that classifies systems by their thermodynamic architecture:

- **0** — Pure accumulation (singularity, black hole)
- **< 0.2** — Violent snaps (earthquakes, lightning, wildfire)
- **~1.0** — Pacemakers / forced symmetry (brain oscillations, sea ice)
- **~1.2-1.35** — Shock absorbers / overdamped clearing (blood glucose, managed gait)
- **~1.618** — Sustained engines / the phi valley (breath, watersheds, preferred walking speed)
- **~1.73** — Exothermic sources (solar dynamo — with caveats)
- **2.0** — Pure harmonics / integer resonance (Cepheid variable stars)

The scale loops: both 0 and 2 are failure states. Systems at the extremes are either accumulating everything and releasing nothing, or locked into rigid resonance. Phi sits at the apex of viability.

## "Okay, but is it statistically significant?"

Fair question. I ran a Monte Carlo simulation to find out. The test: draw 12 random ratios from a null distribution (no structure, no phi attractor), repeat 10 million times, and count how often you get 4 or more landing within 5% of phi by chance.

The answer, across five different null distributions (uniform, log-normal, normal, beta): **p = 0.009 to 0.043.** That's statistically significant under every standard threshold, and it holds regardless of what shape you assume the null takes.

But the clustering isn't even the strongest part. The framework doesn't just say "phi will appear somewhere" — it predicts *which* systems should hit (free-running engines) and which should miss (forced or managed systems). All 4 of the 5%-hits came from the 5-member "predicted hit" group. The probability of that happening by chance is 1 in 99 (hypergeometric test).

Combined — getting this many hits *and* having them all fall where predicted — the joint probability ranges from **1 in 2,300 to 1 in 10,500** depending on the null.

The honest caveat: these 12 systems weren't drawn randomly from nature. I chose them because I had a hypothesis. The "predicted hit" classifications could be accused of being defined after seeing early results. The proper remedy is independent replication by other researchers on systems they choose. The Monte Carlo test establishes that the pattern is unlikely to be noise; it doesn't establish that my selection process was unbiased.

The full significance test script is in the GitHub repo alongside everything else.

## A bit about me

I'm an independent systems thinker, not an academic. My background is in complex systems — the invisible mathematics that keeps things balanced between stagnation and chaos. Living with ME/CFS has given me a daily, visceral lens on what happens when biological energy accumulation and release breaks down. That experience shaped the question, even if the data has to stand on its own.

## But *why* phi? The temporal friction argument

Saying "these ratios cluster near phi" is a pattern. Explaining *why* is a theory. Here's the short version.

You know how sunflower seeds spiral on the flower head? They use the golden angle (137.5°) because it's the most efficient way to pack seeds without any two landing on top of each other. Phi is the *most irrational* number — its continued fraction converges more slowly than any other number's — which means phi-spaced seeds never overlap, no matter how many you add.

Now replace space with time. A heart, a geyser, an ocean oscillation — these are cyclical systems, and each cycle leaves behind thermodynamic "exhaust" (residual heat, momentum, stress). If the accumulation/release ratio is a neat rational fraction (2:1, 3:2), the echoes of past cycles will periodically stack up in perfect alignment with future ones. That's constructive interference. That's a resonant blowout. That's what destroyed the Tacoma Narrows Bridge.

If the ratio is phi, the echoes *never* align. The energy is packed into time the same way seeds are packed into space — maximally spread, zero overlap, no resonance. This isn't mysticism. It's the KAM theorem (Kolmogorov-Arnold-Moser, 1954-63), one of the landmark results in dynamical systems theory: orbits with the most irrational frequency ratios are the most stable under perturbation. Phi is the most irrational number. So phi-ratio systems are the last ones standing.

The evidence for this is observable. The Kirkwood gaps in the asteroid belt are literal empty zones where asteroids at rational orbital period ratios with Jupiter were ejected over billions of years — while asteroids at irrational ratios survived. Saturn's Cassini Division is the same phenomenon. The human heart, when it locks into rigid integer conduction ratios (2:1, 3:1 AV block), enters a pathological state. Engineers use prime-number gear tooth counts to prevent the same teeth meeting repeatedly — phyllotaxis for machines.

And the ARA scale's endpoints tell the full story: at 0, a system dies of implosion (pure accumulation, no release — a black hole). At 2.0, it dies of resonant destruction (the Cepheid variable star, which literally lives in what astronomers call the "Instability Strip" and is actively shaking its own atmosphere off). At phi, neither failure mode can take hold. The system persists.

The full theoretical argument, with visualisations and honest caveats, is here: [Temporal Friction — If This Is True](https://github.com/Dylanlafranky/ARA-GIT/blob/main/temporal_friction.html)

## What's next

This is a heuristic framework, not settled science. I've open-sourced everything — all the analysis scripts, the datasets, the methodology — specifically so other people can break it. The strongest version of this idea is the one that survives independent replication, and the weakest is the one that hides from it.

If you're a data scientist, a physiologist, a fluid dynamicist, or just someone who likes poking at patterns, I'd love to see what happens when you point these scripts at new domains.

**The full framework document:** [The Geometry of Time — Full Framework](https://github.com/Dylanlafranky/ARA-GIT/blob/main/geometry_of_time_framework.html)

**Theoretical extrapolation (temporal friction):** [If This Is True](https://github.com/Dylanlafranky/ARA-GIT/blob/main/temporal_friction.html)

**Preprint (Zenodo DOI):** [10.5281/zenodo.19653363](https://doi.org/10.5281/zenodo.19653363)

**GitHub repository (all analysis scripts + data):** [github.com/Dylanlafranky/ARA-GIT](https://github.com/Dylanlafranky/ARA-GIT)

The geometry of time appears to be written across substrates. I look forward to seeing where else it can be found — and where it fails.

---
*Dylan La Franchi*
*April 2026*
