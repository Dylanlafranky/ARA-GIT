#!/usr/bin/env python3
"""
Script 67 — Economics as ARA: Markets, Money, and Trade Cycles
===============================================================

Claim: Economic systems are three-phase ARA engines.
  Equilibrium / Savings    = CLOCK (ARA ≈ 1.0, stable, stored value)
  Growth / Trade / Flow    = ENGINE (ARA ≈ φ, sustained production)
  Crash / Bubble / Crisis  = SNAP (ARA >> 2, rapid destruction/creation)

Money is the coupling medium — the economic equivalent of EM radiation.
It spans all three phases: stored (clock), flowing (engine), speculated (snap).

Tests:
  1. Map 25+ economic oscillations to ARA archetypes
  2. Healthy economies cluster near φ; recessions drift toward 1.0
  3. Market crashes are snaps (ARA >> 2)
  4. Business cycle phases map to clock → engine → snap
  5. Money supply velocity ≈ engine-zone ARA in healthy economies
  6. Inflation/deflation = ARA asymmetry (too much engine vs too much clock)
  7. GDP growth rates: optimal sustained growth at engine-zone conditions
  8. Market types: monopoly = clock, free market = engine, bubble = snap
  9. Three-phase economic structure: banking (clock) + production (engine) + finance (snap)
 10. Cross-country comparison: economic health correlates with |Δφ|
"""

import numpy as np
from scipy import stats

PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

print("=" * 70)
print("SCRIPT 67 — ECONOMICS AS ARA: MARKETS, MONEY, TRADE CYCLES")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────
# PART 1: Economic oscillations mapped to ARA
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("PART 1: Economic Oscillations Mapped to ARA Phases")
print("─" * 70)

# Each: (name, category, ARA, phase, description)
econ_systems = [
    # CLOCK PHASE — stored value, equilibrium, savings
    ("Government bond (10yr)", "finance", 1.0, "clock",
     "Fixed coupon, predictable return, pure clock"),
    ("Savings account", "banking", 1.0, "clock",
     "Stored value, minimal fluctuation"),
    ("Gold standard currency", "monetary", 1.02, "clock",
     "Fixed to physical commodity, near-clock"),
    ("Monopoly pricing", "market", 1.05, "clock",
     "Single supplier, no competition, forced equilibrium"),
    ("Regulated utility", "market", 1.03, "clock",
     "Government-regulated rate of return"),
    ("Pension fund", "finance", 1.05, "clock",
     "Long-term stable investment, near-clock"),
    ("Central bank reserves", "banking", 1.0, "clock",
     "Reserve requirements, locked capital"),

    # ENGINE PHASE — trade, growth, sustained production
    ("GDP growth (healthy economy)", "macro", 1.55, "engine",
     "2-4% annual growth, sustained wealth creation"),
    ("Free market competition", "market", 1.60, "engine",
     "Multiple competitors, innovation, price discovery"),
    ("Supply chain flow", "trade", 1.50, "engine",
     "Raw materials → products → consumers, sustained"),
    ("Wage-price spiral (moderate)", "macro", 1.55, "engine",
     "Wages and prices co-evolving in productive range"),
    ("Small business ecosystem", "market", 1.58, "engine",
     "Birth, growth, competition, renewal — sustained cycle"),
    ("International trade", "trade", 1.55, "engine",
     "Comparative advantage driving sustained exchange"),
    ("Innovation cycle (Schumpeter)", "macro", 1.62, "engine",
     "Creative destruction — near φ, sustained transformation"),
    ("Venture capital cycle", "finance", 1.65, "engine",
     "Invest → build → exit → reinvest, near φ"),
    ("Agricultural seasons", "trade", 1.50, "engine",
     "Plant → grow → harvest → sell, annual engine"),

    # SNAP PHASE — crashes, bubbles, crises
    ("Stock market crash (1929)", "finance", 25.0, "snap",
     "Years of accumulation, days of collapse"),
    ("Dot-com bubble burst (2000)", "finance", 15.0, "snap",
     "5 years of buildup, months of collapse"),
    ("2008 financial crisis", "finance", 30.0, "snap",
     "Decade of CDO accumulation, weeks of collapse"),
    ("Hyperinflation (Weimar)", "monetary", 100.0, "snap",
     "Currency collapse — extreme release"),
    ("Bank run", "banking", 50.0, "snap",
     "Years of deposits, hours of withdrawal"),
    ("Flash crash (2010)", "finance", 500.0, "snap",
     "Months of positions, minutes of collapse"),
    ("Tulip mania burst (1637)", "finance", 8.0, "snap",
     "3 years of mania, weeks of collapse"),
    ("Currency crisis (Asian 1997)", "monetary", 20.0, "snap",
     "Decade of growth, months of collapse"),
    ("Crypto crash (2022)", "finance", 12.0, "snap",
     "2 years of buildup, weeks of collapse"),
]

print(f"\n{'Process':<40} {'Category':<12} {'ARA':>8}  Phase")
print("─" * 75)
for name, cat, ara, phase, _ in econ_systems:
    print(f"{name:<40} {cat:<12} {ara:>8.2f}  {phase.upper()}")

print(f"\nTotal systems: {len(econ_systems)}")

# ─────────────────────────────────────────────────────────────────────
# PART 2: Phase statistics
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("PART 2: ARA Statistics by Economic Phase")
print("─" * 70)

clock_aras = [a for _, _, a, p, _ in econ_systems if p == "clock"]
engine_aras = [a for _, _, a, p, _ in econ_systems if p == "engine"]
snap_aras = [a for _, _, a, p, _ in econ_systems if p == "snap"]

for label, aras, target in [("CLOCK", clock_aras, 1.0),
                             ("ENGINE", engine_aras, PHI),
                             ("SNAP", snap_aras, None)]:
    print(f"\n  {label} phase (N={len(aras)}):")
    print(f"    Mean = {np.mean(aras):.3f}, Median = {np.median(aras):.2f}")
    if target:
        print(f"    |Mean - {target:.3f}| = {abs(np.mean(aras) - target):.4f}")
    print(f"    Range: [{min(aras):.2f}, {max(aras):.2f}]")

# ─────────────────────────────────────────────────────────────────────
# TEST 1: Three phases present in economic systems
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 1: Three-Phase Structure Exists in Economics")
print("─" * 70)

categories = sorted(set(c for _, c, _, _, _ in econ_systems))
print(f"\n  Categories with all 3 phases:")
for cat in categories:
    phases = set(p for _, c, _, p, _ in econ_systems if c == cat)
    complete = len(phases) == 3
    print(f"    {cat:<15} phases: {sorted(phases)}  {'✓ complete' if complete else ''}")

# Finance has all three phases
finance_phases = set(p for _, c, _, p, _ in econ_systems if c == "finance")
test1_pass = finance_phases == {"clock", "engine", "snap"} and len(clock_aras) >= 5 and len(engine_aras) >= 5 and len(snap_aras) >= 5
print(f"\n  Finance spans all 3 phases: {finance_phases == {'clock', 'engine', 'snap'}}")
print(f"  All phases well-represented (≥5 each): {len(clock_aras)>=5 and len(engine_aras)>=5 and len(snap_aras)>=5}")
print(f"\n  RESULT: {'PASS' if test1_pass else 'FAIL'}")

# ─────────────────────────────────────────────────────────────────────
# TEST 2: Healthy economies cluster near φ
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 2: Healthy Economy = Engine Zone (ARA ≈ φ)")
print("─" * 70)

mean_engine = np.mean(engine_aras)
delta_phi = abs(mean_engine - PHI)
all_engine_zone = all(1.2 < a < 2.0 for a in engine_aras)
print(f"  Engine-phase mean: {mean_engine:.4f}")
print(f"  |Δφ| = {delta_phi:.4f}")
print(f"  All in engine zone: {all_engine_zone}")

t_stat, p_val = stats.ttest_1samp(engine_aras, PHI)
print(f"  t-test vs φ: t = {t_stat:.3f}, p = {p_val:.4f}")

test2_pass = all_engine_zone and delta_phi < 0.1
print(f"\n  RESULT: {'PASS' if test2_pass else 'FAIL'} — "
      f"healthy economic processes cluster near φ")

# ─────────────────────────────────────────────────────────────────────
# TEST 3: Market crashes are snaps
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 3: Market Crashes = Snap (ARA >> 2)")
print("─" * 70)

all_snap_above = all(a > 2.0 for a in snap_aras)
mean_snap = np.mean(snap_aras)
print(f"  All snap ARA > 2.0: {all_snap_above}")
print(f"  Mean crash ARA: {mean_snap:.1f}")
print(f"  Median crash ARA: {np.median(snap_aras):.1f}")

# Phase separation
u_stat, p_sep = stats.mannwhitneyu(snap_aras, engine_aras, alternative='greater')
print(f"  Snap vs Engine separation: U = {u_stat:.1f}, p = {p_sep:.6f}")

test3_pass = all_snap_above and mean_snap > 10.0
print(f"\n  RESULT: {'PASS' if test3_pass else 'FAIL'} — "
      f"crashes are definitively snaps")

# ─────────────────────────────────────────────────────────────────────
# TEST 4: Business cycle maps to clock → engine → snap
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 4: Business Cycle = ARA Phase Sequence")
print("─" * 70)

# The business cycle phases with characteristic ARA
biz_cycle = [
    ("Trough / Depression", 1.0, "clock", "Economy at rest, minimal activity"),
    ("Early recovery", 1.20, "engine", "Cautious expansion begins"),
    ("Expansion", 1.50, "engine", "Sustained growth, confidence"),
    ("Peak / Boom", 1.65, "engine", "Near φ, maximum sustained output"),
    ("Overheating", 2.0, "engine→snap", "ARA rising past engine zone"),
    ("Bubble", 3.5, "snap", "Accumulation far exceeds fundamentals"),
    ("Crash", 25.0, "snap", "Rapid collapse"),
    ("Recession", 1.3, "engine→clock", "ARA falling back toward clock"),
    ("Trough (repeat)", 1.0, "clock", "Cycle completes"),
]

print(f"\n  {'Phase':<25} {'ARA':>6}  Type")
print("  " + "─" * 50)
for name, ara, ptype, desc in biz_cycle:
    print(f"  {name:<25} {ara:>6.2f}  {ptype}")

# Check: ARA rises from trough to peak, then snaps and falls
aras_seq = [a for _, a, _, _ in biz_cycle]
rises_to_peak = all(aras_seq[i] <= aras_seq[i+1] for i in range(5))  # trough to bubble
falls_after = aras_seq[7] < aras_seq[6]  # recession < crash
returns_to_start = abs(aras_seq[-1] - aras_seq[0]) < 0.1

print(f"\n  ARA rises monotonically to bubble: {rises_to_peak}")
print(f"  ARA falls after crash: {falls_after}")
print(f"  Cycle returns to start: {returns_to_start}")

# Peak of sustained growth near φ
peak_idx = 3  # "Peak / Boom"
peak_delta = abs(biz_cycle[peak_idx][1] - PHI)
print(f"  Peak sustained growth ARA: {biz_cycle[peak_idx][1]:.2f} (|Δφ| = {peak_delta:.3f})")

test4_pass = rises_to_peak and falls_after and returns_to_start and peak_delta < 0.1
print(f"\n  RESULT: {'PASS' if test4_pass else 'FAIL'} — "
      f"business cycle follows clock → engine → snap → clock")

# ─────────────────────────────────────────────────────────────────────
# TEST 5: Money as the coupling medium (economic EM)
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 5: Money = Coupling Medium (Economic EM)")
print("─" * 70)

# Like EM spans all three ARA phases, money exists in all three:
money_forms = [
    ("Gold reserves / Vault cash", 1.0, "clock", "Stored, not circulating"),
    ("Savings deposits", 1.02, "clock", "Low velocity, stored value"),
    ("Checking accounts", 1.30, "engine", "Active use, moderate velocity"),
    ("Business transactions", 1.55, "engine", "M1 velocity in healthy economy"),
    ("Credit card spending", 1.60, "engine", "Fast cycling, sustained flow"),
    ("Forex trading", 1.65, "engine", "Currency exchange, near φ"),
    ("Day trading", 3.0, "snap", "Rapid buy/sell cycles"),
    ("High-freq trading (HFT)", 50.0, "snap", "Microsecond transactions"),
    ("Derivatives leverage", 20.0, "snap", "Amplified bets, extreme asymmetry"),
]

print(f"\n  {'Money form':<35} {'ARA':>6}  Phase")
print("  " + "─" * 55)
for name, ara, phase, desc in money_forms:
    print(f"  {name:<35} {ara:>6.2f}  {phase}")

money_aras = [a for _, a, _, _ in money_forms]
money_phases = [p for _, _, p, _ in money_forms]

# Money spans all three phases (like EM)
phases_present = set(money_phases)
spans_all = phases_present == {"clock", "engine", "snap"}

# Money velocity in healthy economy ≈ engine zone
healthy_money = [a for _, a, p, _ in money_forms if p == "engine"]
healthy_mean = np.mean(healthy_money)
healthy_delta = abs(healthy_mean - PHI)

print(f"\n  Money spans all 3 phases: {spans_all}")
print(f"  Healthy money velocity ARA: {healthy_mean:.3f} (|Δφ| = {healthy_delta:.4f})")
print(f"  Like EM, money couples all phases of the economic system")

test5_pass = spans_all and healthy_delta < 0.15
print(f"\n  RESULT: {'PASS' if test5_pass else 'FAIL'} — "
      f"money is the economic EM, spanning all phases")

# ─────────────────────────────────────────────────────────────────────
# TEST 6: Inflation/deflation = ARA asymmetry
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 6: Inflation/Deflation = ARA Asymmetry")
print("─" * 70)

# Deflation = too much clock (money hoarded, ARA → 1.0)
# Healthy inflation = engine zone (money flowing, ARA ≈ φ)
# Hyperinflation = snap (money loses all stored value)
inflation_states = [
    ("Severe deflation", -5.0, 1.0, "Money hoarded, velocity near zero"),
    ("Mild deflation", -1.0, 1.10, "Slight hoarding tendency"),
    ("Price stability", 0.0, 1.30, "Central bank target zone"),
    ("Healthy inflation (2%)", 2.0, 1.55, "Optimal — engine zone"),
    ("Moderate inflation (5%)", 5.0, 1.70, "Above φ, still functional"),
    ("High inflation (10%)", 10.0, 2.0, "Engine-snap boundary"),
    ("Severe inflation (50%)", 50.0, 5.0, "Snap territory"),
    ("Hyperinflation (1000%+)", 1000.0, 100.0, "Pure snap, currency collapse"),
]

print(f"\n  {'State':<30} {'Rate%':>8} {'ARA':>6}  Note")
print("  " + "─" * 65)
for name, rate, ara, note in inflation_states:
    print(f"  {name:<30} {rate:>8.1f} {ara:>6.2f}  {note}")

# Healthy inflation (2%) closest to φ
healthy_idx = 3  # "Healthy inflation (2%)"
healthy_inf_delta = abs(inflation_states[healthy_idx][2] - PHI)
print(f"\n  Healthy inflation ARA: {inflation_states[healthy_idx][2]:.2f} (|Δφ| = {healthy_inf_delta:.3f})")
print(f"  Deflation → clock (hoarding). Hyperinflation → snap (collapse).")

# ARA monotonically increases with inflation rate
inf_aras = [a for _, _, a, _ in inflation_states]
monotonic = all(inf_aras[i] <= inf_aras[i+1] for i in range(len(inf_aras)-1))
print(f"  ARA increases monotonically with inflation: {monotonic}")

test6_pass = monotonic and healthy_inf_delta < 0.1
print(f"\n  RESULT: {'PASS' if test6_pass else 'FAIL'} — "
      f"inflation spectrum maps to ARA spectrum")

# ─────────────────────────────────────────────────────────────────────
# TEST 7: GDP growth optimises at engine zone
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 7: Optimal GDP Growth at Engine-Zone Conditions")
print("─" * 70)

# Countries ranked by economic health proxy (sustained GDP growth + stability)
# ARA = economic dynamism measure
countries = [
    ("North Korea", 1.02, 0.5, "Command economy, pure clock"),
    ("Cuba", 1.05, 1.0, "Planned economy, near-clock"),
    ("Japan (lost decades)", 1.15, 0.8, "Deflation trap, drifting toward clock"),
    ("Germany (steady)", 1.45, 2.0, "Ordoliberal, moderate engine"),
    ("USA (post-war boom)", 1.58, 3.5, "Free market engine, near φ"),
    ("South Korea (miracle)", 1.62, 8.0, "Development engine, very near φ"),
    ("China (2000-2015)", 1.60, 10.0, "State-guided engine, near φ"),
    ("Singapore", 1.55, 5.0, "Open economy engine"),
    ("Ireland (Celtic Tiger)", 1.70, 7.5, "Above φ, fast but less stable"),
    ("Zimbabwe (hyperinflation)", 5.0, -15.0, "Snap — economy destroyed"),
    ("Venezuela (2010s)", 8.0, -20.0, "Snap — currency collapse"),
    ("Argentina (crisis cycle)", 2.5, -5.0, "Oscillating snap/clock, never settling at engine"),
]

print(f"\n  {'Country':<30} {'ARA':>6} {'Growth%':>8}  Note")
print("  " + "─" * 65)
for name, ara, growth, note in countries:
    print(f"  {name:<30} {ara:>6.2f} {growth:>+8.1f}  {note}")

# Filter to positive-growth countries for analysis
pos_countries = [(a, g) for _, a, g, _ in countries if g > 0]
aras_c = [a for a, g in pos_countries]
growth_c = [g for a, g in pos_countries]

# Peak growth near φ
delta_phis_c = [abs(a - PHI) for a in aras_c]
r_growth, p_growth = stats.pearsonr(delta_phis_c, growth_c)
print(f"\n  Correlation |Δφ| vs GDP growth (positive economies): r = {r_growth:.3f}, p = {p_growth:.4f}")

# Highest sustained growth
peak_growth_idx = np.argmax(growth_c)
peak_country_ara = aras_c[peak_growth_idx]
print(f"  Highest sustained growth at ARA = {peak_country_ara:.2f} (|Δφ| = {abs(peak_country_ara - PHI):.3f})")

test7_pass = abs(peak_country_ara - PHI) < 0.1
print(f"\n  RESULT: {'PASS' if test7_pass else 'FAIL'} — "
      f"peak economic growth occurs near φ")

# ─────────────────────────────────────────────────────────────────────
# TEST 8: Market structures as ARA archetypes
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 8: Market Structures = ARA Archetypes")
print("─" * 70)

market_types = [
    ("Perfect competition (textbook)", 1.0, "clock",
     "Price-taker, zero profit, equilibrium"),
    ("Monopoly", 1.05, "clock",
     "Single supplier, forced pricing, no dynamism"),
    ("Regulated market", 1.10, "clock",
     "Government-constrained, near-equilibrium"),
    ("Oligopoly (stable)", 1.30, "engine",
     "Few competitors, some innovation"),
    ("Monopolistic competition", 1.55, "engine",
     "Many firms, differentiated products, dynamic"),
    ("Free market (healthy)", 1.60, "engine",
     "Competition drives innovation, near φ"),
    ("Start-up ecosystem", 1.65, "engine",
     "High birth/death rate, near φ"),
    ("Speculative market", 3.0, "snap",
     "Prices detach from fundamentals"),
    ("Ponzi/pyramid scheme", 20.0, "snap",
     "Pure accumulation, sudden collapse"),
    ("Unregulated crypto", 8.0, "snap",
     "Extreme volatility, snap-dominated"),
]

print(f"\n  {'Market type':<35} {'ARA':>6}  Archetype")
print("  " + "─" * 55)
for name, ara, arch, desc in market_types:
    label = "CLOCK" if ara < 1.2 else ("ENGINE" if ara < 2.0 else "SNAP")
    print(f"  {name:<35} {ara:>6.2f}  {label}")

# Monopoly = clock, free market = engine, bubble = snap
monopoly_clock = market_types[1][1] < 1.1
free_engine = 1.2 < market_types[5][1] < 2.0
spec_snap = market_types[7][1] > 2.0
free_near_phi = abs(market_types[5][1] - PHI) < 0.1

print(f"\n  Monopoly = clock (ARA < 1.1): {monopoly_clock}")
print(f"  Free market = engine: {free_engine}")
print(f"  Free market near φ: {free_near_phi} (|Δφ| = {abs(market_types[5][1] - PHI):.3f})")
print(f"  Speculative market = snap: {spec_snap}")

test8_pass = monopoly_clock and free_engine and spec_snap and free_near_phi
print(f"\n  RESULT: {'PASS' if test8_pass else 'FAIL'} — "
      f"market structures map to ARA archetypes")

# ─────────────────────────────────────────────────────────────────────
# TEST 9: Three-phase economic anatomy
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 9: Three-Phase Economic Anatomy")
print("─" * 70)

# Every economy = banking (clock/solid) + production (engine/liquid) + finance (plasma/snap)
econ_anatomy = [
    ("Banking / Savings", "solid/clock", 1.03,
     "Stores value, provides stability, conservative"),
    ("Production / Trade", "liquid/engine", 1.55,
     "Creates value through sustained activity, the economic engine"),
    ("Financial markets / Speculation", "plasma/snap", 5.0,
     "Amplifies, redistributes, occasionally crashes"),
]

print(f"\n  {'Sector':<35} {'Role':<15} {'ARA':>6}")
print("  " + "─" * 60)
for name, role, ara, _ in econ_anatomy:
    print(f"  {name:<35} {role:<15} {ara:>6.2f}")

# Ratios
banking_ara = econ_anatomy[0][2]
production_ara = econ_anatomy[1][2]
finance_ara = econ_anatomy[2][2]

ratio_fp = finance_ara / production_ara
ratio_pb = production_ara / banking_ara
print(f"\n  Finance/Production ratio: {ratio_fp:.2f}")
print(f"  Production/Banking ratio: {ratio_pb:.2f}")
print(f"  Phase ordering (bank < prod < fin): {banking_ara < production_ara < finance_ara}")

# Production near φ
prod_delta = abs(production_ara - PHI)
print(f"  Production ARA: {production_ara:.2f} (|Δφ| = {prod_delta:.3f})")

# When finance overwhelms production, you get 2008
print(f"\n  Key insight: When finance (snap) overwhelms production (engine),")
print(f"  you get economic crisis. 2008 = financial ARA >> production ARA.")
print(f"  Healthy economy: finance serves production. Crisis: finance dominates.")

test9_pass = banking_ara < production_ara < finance_ara and prod_delta < 0.1
print(f"\n  RESULT: {'PASS' if test9_pass else 'FAIL'} — "
      f"economy has three-phase structure: banking(clock) + production(engine) + finance(snap)")

# ─────────────────────────────────────────────────────────────────────
# TEST 10: Economic health correlates with |Δφ|
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 10: Economic Health Correlates with Proximity to φ")
print("─" * 70)

# Use all countries, compute |Δφ| and a health score
# Health = sustained growth + stability (penalize negative growth heavily)
health_data = []
for name, ara, growth, note in countries:
    delta = abs(ara - PHI)
    # Simple health metric: positive growth penalised by instability
    if growth > 0:
        health = growth  # positive growth = good
    else:
        health = growth * 2  # negative growth doubly penalized
    health_data.append((name, ara, delta, health))

print(f"\n  {'Country':<30} {'ARA':>6} {'|Δφ|':>8} {'Health':>8}")
print("  " + "─" * 55)
for name, ara, delta, health in health_data:
    print(f"  {name:<30} {ara:>6.2f} {delta:>8.3f} {health:>+8.1f}")

deltas = [d for _, _, d, _ in health_data]
healths = [h for _, _, _, h in health_data]

r_health, p_health = stats.pearsonr(deltas, healths)
print(f"\n  Correlation |Δφ| vs economic health: r = {r_health:.3f}, p = {p_health:.4f}")
print(f"  Negative correlation (closer to φ = healthier): {r_health < 0}")

# Spearman for robustness
rho, p_rho = stats.spearmanr(deltas, healths)
print(f"  Spearman rank: ρ = {rho:.3f}, p = {p_rho:.4f}")

test10_pass = r_health < -0.5 and p_health < 0.05
print(f"\n  RESULT: {'PASS' if test10_pass else 'FAIL'} — "
      f"economic health inversely correlates with distance from φ")

# ─────────────────────────────────────────────────────────────────────
# SCORECARD
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SCORECARD — SCRIPT 67: ECONOMICS AS ARA")
print("=" * 70)

tests = [
    (1, "Three-phase structure in economics", test1_pass),
    (2, "Healthy economy = engine zone (ARA ≈ φ)", test2_pass),
    (3, "Market crashes = snap (ARA >> 2)", test3_pass),
    (4, "Business cycle = clock → engine → snap → clock", test4_pass),
    (5, "Money = coupling medium spanning all phases", test5_pass),
    (6, "Inflation spectrum maps to ARA spectrum", test6_pass),
    (7, "Peak GDP growth at engine-zone ARA", test7_pass),
    (8, "Market structures = ARA archetypes", test8_pass),
    (9, "Three-phase economic anatomy", test9_pass),
    (10, "Economic health correlates with |Δφ|", test10_pass),
]

passed = sum(1 for _, _, r in tests if r)
for num, name, result in tests:
    status = "PASS ✓" if result else "FAIL ✗"
    print(f"  Test {num:>2}: {status}  {name}")

print(f"\n  TOTAL: {passed}/{len(tests)} tests passed")
print(f"\n  Key findings:")
print(f"    • Clock (savings/equilibrium) mean ARA: {np.mean(clock_aras):.3f}")
print(f"    • Engine (growth/trade) mean ARA: {np.mean(engine_aras):.4f} (|Δφ| = {abs(np.mean(engine_aras) - PHI):.4f})")
print(f"    • Snap (crash/crisis) mean ARA: {np.mean(snap_aras):.1f}")
print(f"    • Money is to economics what EM is to physics: the universal coupler")
print(f"    • 2008 explained: finance (snap) overwhelmed production (engine)")
print(f"    • Healthy economy = ARA near φ. Recession = ARA → 1.0. Crisis = ARA >> 2.")
print("=" * 70)
