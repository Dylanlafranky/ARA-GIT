# EnergyRatio

Tests of **how efficiently a system moves energy/information per cycle** — the "energy budget" / leanness side of the ARA framework. Sister folders: `Mapping/` (where systems sit on the ARA scale) and `TheFormula/` (forecasting).

Core idea: φ is the framework's efficient/balance ratio. A system whose internal mode ratio sits near φ should run **leaner** — spilling less energy into wasteful harmonic distortion per cycle — than systems at off-φ (especially near-rational) ratios. This ties to the φ-rung **entropy-decay** result (φ = most-irrational packing = least entropy leaked per cycle; see `../TheFormula/Claude4.8/PHI_RUNG_ENTROPY_DECAY_RESULT.md`).

## First result — Golden stars run leaner (31 May 2026)

Full writeup: **`GOLDEN_STARS_LEAN_RESULT.md`**. Real Kepler + OGLE photometry. Leanness = **R21 = A(2f)/A(f₁)** (harmonic spray; lower = leaner).

| Class | mode ratio | leanness R21 |
|---|---|---|
| Single-mode classical Cepheid | integer harmonics only, φ absent | 0.28 (fattest) |
| Ordinary double-mode (433 OGLE) | 1.34–1.42 (near-rational) | 0.16 / 0.19 |
| Near-φ "golden" club (4 Kepler RRc) | within ~2% of φ | ≈0.11 (leanest) |

Population: 949 OGLE RR0.61 stars 3.6% leaner than 18,318 ordinary RRc (p=0.016); **within club, corr(|Px/P1O − 1/φ|, R21) = −0.347** — closer to exact 1/φ = leaner.

Mechanism is consistent with KAM theory (φ most-irrational → harmonics can't lock and grow → energy stays lean; rational ratios let overtones reinforce → waste). The *measured leanness gradient* and cross-domain framing are the framework's new contribution; the golden stars themselves (Lindner 2015) and KAM stability are prior art.

## Reproduce

```bash
pip install lightkurve --break-system-packages   # also pulls astropy
python fetch_data.py        # downloads Kepler light curves + OGLE/VizieR catalogs to /tmp
python club_lean.py         # 4 Kepler golden stars: f1, harmonics, 2nd-mode ratio, R21
python popdist2.py          # OGLE double-mode population: frequency-ratio distribution
python lean.py              # OGLE crowd: R21 vs ratio (within-crowd)
python club_pop.py          # RR0.61 cross-match: club vs crowd leanness + within-club gradient
```

## Scripts
- `fetch_data.py` — downloads all real data (Kepler via lightkurve/MAST; OGLE; VizieR Netzel 2019).
- `golden_prewhiten.py` — iterative prewhitening frequency extraction (one Kepler star).
- `club_lean.py` — the 4 golden stars, raw photometry → R21 + 2nd-mode ratio.
- `popdist2.py` — 433 OGLE double-mode stars → frequency-ratio histogram, φ placement.
- `lean.py` — OGLE crowd R21-vs-ratio (leanness within the off-φ population).
- `club_pop.py` — 949 RR0.61 stars vs 18k ordinary RRc; within-club gradient toward 1/φ.
- `tsratio.py`, `ampfrac.py` — density / amplitude / small-mode-fraction proxies that **failed** first (kept for the honest trail; only R21 leanness worked).

## Caveats
n=4 Kepler club is a known related class (re-found, not discovered); R21 is one (clean, physical) leanness proxy; against same-type RRc the class gap is modest (3.6%) — the within-club gradient toward exact φ is the backbone; golden-star 2nd modes may be non-radial vs the crowd's radial overtones.

## Next
RR0.68 group; LMC/SMC RR0.61; a 2nd leanness proxy (R31, light-curve skew); whether the φ-club is also more transient (strange-nonchaotic / shorter stable lifetime).
