#!/usr/bin/env python3
"""
Script 242 — Network Connection Field (Top-Down)

Given a seed system, derive ALL coupling partners predicted by the
three-circle geometry. Each system has 3 ARA pairs (Space-Time,
Time-Rationality, Space-Rationality) × 2 directions = 6 outward connections.

The geometry:
  - Horizontal coupling: φ² connects same-rung partners (Space ↔ Time)
  - Vertical coupling: 2/φ downward (Space+Time → Rationality)
  - Pipe capacity: 2φ down, φ up
  - Cascade rungs: periods at φ-power intervals
  - Transfer asymmetry: downhill ×φ, uphill ×1/φ

From a seed system's ARA and period, we derive:
  1. What ARA each coupling partner should have
  2. What period each partner should have
  3. What type of coupling connects them

Then check: which known systems sit at those predicted positions?

Dylan's insight: "Most systems have 9 parts at their basic (3 ARA pairs)."
3 pairs × 3 phases = 9 coupling channels = the F⁹ matrix.
"""

import math
import numpy as np

PHI = (1 + math.sqrt(5)) / 2

# ═══════════════════════════════════════════════════════════════
# GEOMETRIC COUPLING RULES
# ═══════════════════════════════════════════════════════════════

# From the three-circle architecture:
# Horizontal coupler = φ²
# Vertical coupler = 2/φ
# Pipe down capacity = 2φ
# Pipe up capacity = φ
# Cascade rungs = φ^n for period, φ-power ARA transformations

# The 6 outward connections from any node:
#
# CONNECTION 1: Horizontal partner (same rung, anti-phase)
#   Period: same (same rung)
#   ARA: 2 - seed_ARA (mirror across clock point ARA=1)
#   Coupling: φ² (Space ↔ Time coupling)
#   Nature: The system that oscillates in anti-phase at the same scale
#
# CONNECTION 2: Vertical child (one rung DOWN)
#   Period: seed_period × φ (longer period = larger scale below)
#   ARA: seed_ARA × (1/φ) (energy diluted going down)
#   Coupling: 2/φ (vertical coupler, two sources feeding one child)
#   Nature: The system one φ-rung below that receives energy from above
#
# CONNECTION 3: Vertical parent (one rung UP)
#   Period: seed_period / φ (shorter period = smaller scale above)
#   ARA: seed_ARA × φ (energy concentrated going up — but capped at 2.0)
#   Coupling: φ (single-pipe upward)
#   Nature: The system one φ-rung above that feeds into this one
#
# CONNECTION 4: Diagonal down-out (pipe cascade)
#   Period: seed_period × φ² (two rungs down)
#   ARA: via pipe capacity ratio: seed_ARA × (1/φ²)
#   Coupling: 2φ (full down-pipe capacity)
#   Nature: The consumer two rungs below, reached by cascade
#
# CONNECTION 5: Diagonal up-in (reverse pipe)
#   Period: seed_period / φ² (two rungs up)
#   ARA: seed_ARA × φ² (but capped at 2.0)
#   Coupling: φ (up-pipe, weaker)
#   Nature: The engine two rungs above, feeding cascade downward
#
# CONNECTION 6: Cross-coupling (the third circle)
#   Period: seed_period × φ⁴ (the Gleissberg-to-Schwabe ratio)
#   ARA: 1/seed_ARA (inverse — the consumer/engine complement)
#   Coupling: 1/φ⁴ (the π-leak coupling)
#   Nature: The inverse system — if you're an engine, this is your consumer;
#           if you're a consumer, this is your engine

def derive_connections(seed_name, seed_ara, seed_period):
    """Derive 6 outward coupling connections from a seed system."""

    connections = []

    # Connection 1: Horizontal partner (mirror across ARA=1)
    h_ara = 2.0 - seed_ara
    h_period = seed_period  # same rung
    connections.append({
        'label': '1. Horizontal partner',
        'direction': '← →',
        'mechanism': 'Space ↔ Time anti-phase (φ² coupler)',
        'predicted_ara': max(0.01, h_ara),
        'predicted_period': h_period,
        'coupling_strength': PHI**2,
        'note': f'Mirror of {seed_name} across clock point. ARA = 2 - {seed_ara:.3f} = {h_ara:.3f}'
    })

    # Connection 2: Vertical child (one rung DOWN = longer period)
    v_down_ara = seed_ara / PHI
    v_down_period = seed_period * PHI
    connections.append({
        'label': '2. Vertical child (↓1 rung)',
        'direction': '↓',
        'mechanism': f'Vertical feed, 2/φ coupler, pipe 2φ',
        'predicted_ara': v_down_ara,
        'predicted_period': v_down_period,
        'coupling_strength': 2.0 / PHI,
        'note': f'ARA diluted by 1/φ going down. Period grows by φ.'
    })

    # Connection 3: Vertical parent (one rung UP = shorter period)
    v_up_ara = min(2.0, seed_ara * PHI)
    v_up_period = seed_period / PHI
    connections.append({
        'label': '3. Vertical parent (↑1 rung)',
        'direction': '↑',
        'mechanism': f'Reverse feed, φ coupler (single pipe up)',
        'predicted_ara': v_up_ara,
        'predicted_period': v_up_period,
        'coupling_strength': PHI,
        'note': f'ARA concentrated by φ going up. Period shrinks by φ.'
    })

    # Connection 4: Diagonal down-out (two rungs DOWN via cascade)
    d_down_ara = seed_ara / (PHI**2)
    d_down_period = seed_period * PHI**2
    connections.append({
        'label': '4. Cascade child (↓2 rungs)',
        'direction': '↓↓',
        'mechanism': f'Full cascade pipe, capacity 2φ',
        'predicted_ara': d_down_ara,
        'predicted_period': d_down_period,
        'coupling_strength': 2.0 * PHI,
        'note': f'Two-rung cascade. ARA diluted by 1/φ². Deep consumer territory.'
    })

    # Connection 5: Diagonal up-in (two rungs UP via reverse cascade)
    d_up_ara = min(2.0, seed_ara * PHI**2)
    d_up_period = seed_period / PHI**2
    connections.append({
        'label': '5. Cascade parent (↑2 rungs)',
        'direction': '↑↑',
        'mechanism': f'Reverse cascade, capacity φ',
        'predicted_ara': d_up_ara,
        'predicted_period': d_up_period,
        'coupling_strength': PHI,
        'note': f'Two-rung reverse cascade. ARA concentrated by φ².'
    })

    # Connection 6: Cross-coupling (inverse complement via 1/φ⁴ leak)
    x_ara = 1.0 / seed_ara if seed_ara > 0.01 else 100.0
    x_ara = min(2.0, x_ara)  # cap at scale boundary
    x_period = seed_period * PHI**4  # the Gleissberg ratio
    connections.append({
        'label': '6. Inverse complement (1/ARA)',
        'direction': '⊗',
        'mechanism': f'Cross-coupling via 1/φ⁴ leak (π-leak)',
        'predicted_ara': x_ara,
        'predicted_period': x_period,
        'coupling_strength': 1.0 / PHI**4,
        'note': f'The engine-consumer complement. 1/{seed_ara:.3f} = {1.0/seed_ara:.3f}. '
                f'Period at Gleissberg ratio (×φ⁴).'
    })

    return connections


def phi_dist(ara):
    """Distance from clock point in φ-rungs."""
    a = max(0.01, ara)
    return abs(math.log(a)) / math.log(PHI)


def classify_zone(ara):
    pd = phi_dist(ara)
    if pd <= 1.0/PHI:
        return 'Palindrome'
    elif pd < 1.0:
        return 'Ramp'
    else:
        return 'Full'


def classify_type(ara):
    """Human-readable system type from ARA."""
    if ara < 0.2:
        return 'Violent snap'
    elif ara < 0.9:
        return 'Consumer'
    elif ara < 1.3:
        return 'Shock absorber / Clock'
    elif ara < 1.5:
        return 'Clock-driven bio'
    elif ara < 1.7:
        return 'Sustained engine'
    elif ara < 1.9:
        return 'Exothermic source'
    else:
        return 'Pure harmonic'


# ═══════════════════════════════════════════════════════════════
# KNOWN SYSTEMS DATABASE
# ═══════════════════════════════════════════════════════════════

KNOWN_SYSTEMS = [
    # (name, ARA, period_years, domain)
    ('Solar (sunspot)',    PHI,   11.07,  'Astrophysics'),
    ('ENSO',              2.0,   3.75,   'Climate'),
    ('Earthquake',        0.15,  11.09,  'Seismology'),
    ('Heart',             1.35,  0.001,  'Cardiology'),     # ~1 sec in years
    ('Hare',              1.0,   9.6,    'Ecology'),
    ('Lynx',              1.0,   9.5,    'Ecology'),
    ('Unemployment',      0.75,  7.0,    'Economics'),
    ('GDP Growth',        1.0,   3.9,    'Economics'),
    ('CO2 Amplitude',     0.15,  7.6,    'Atmospheric'),
    ('Nile',              0.15,  7.5,    'Hydrology'),
    # Known physical periods that might match
    ('QBO',               None,  2.3,    'Climate'),        # Quasi-biennial oscillation
    ('Gleissberg',        None,  76.0,   'Astrophysics'),   # ~80 year solar modulation
    ('de Vries/Suess',    None,  199.0,  'Astrophysics'),   # ~200 year solar cycle
    ('Hale (magnetic)',   None,  22.0,   'Astrophysics'),   # Full magnetic reversal
    ('PDO',               None,  25.0,   'Climate'),        # Pacific Decadal Oscillation
    ('AMO',               None,  60.0,   'Climate'),        # Atlantic Multidecadal Osc
    ('NAO',               None,  7.0,    'Climate'),        # North Atlantic Oscillation
    ('Chandler wobble',   None,  1.2,    'Geophysics'),     # Earth axis wobble
    ('Lunar nodal',       None,  18.6,   'Geophysics'),     # Tidal modulation
]


def find_matches(predicted_ara, predicted_period, tolerance_ara=0.3, tolerance_period_factor=1.5):
    """Find known systems near a predicted ARA/period position."""
    matches = []
    for name, ara, period, domain in KNOWN_SYSTEMS:
        # Check period match (within factor)
        period_ratio = max(predicted_period, period) / max(0.001, min(predicted_period, period))
        period_match = period_ratio <= tolerance_period_factor

        # Check ARA match (if known)
        if ara is not None:
            ara_diff = abs(ara - predicted_ara)
            ara_match = ara_diff <= tolerance_ara
        else:
            ara_match = True  # unknown ARA = possible match on period alone
            ara_diff = None

        if period_match:
            matches.append({
                'name': name,
                'ara': ara,
                'period': period,
                'domain': domain,
                'ara_diff': ara_diff,
                'period_ratio': period_ratio,
                'ara_match': ara_match,
                'period_match': period_match,
                'full_match': ara_match and period_match
            })

    # Sort by period proximity
    matches.sort(key=lambda m: m['period_ratio'])
    return matches


# ═══════════════════════════════════════════════════════════════
# RUN THE CONNECTION FIELD
# ═══════════════════════════════════════════════════════════════

print("=" * 78)
print("Script 242 — Network Connection Field (Top-Down)")
print("=" * 78)
print()

# ── SEED: Solar ──
seeds = [
    ('Solar',      PHI,   11.07),
    ('Earthquake', 0.15,  11.09),
    ('ENSO',       2.0,   3.75),
]

all_predictions = []

for seed_name, seed_ara, seed_period in seeds:
    print("─" * 78)
    print(f"SEED: {seed_name} (ARA = {seed_ara:.3f}, Period = {seed_period:.2f} yr)")
    print(f"  φ-dist = {phi_dist(seed_ara):.3f}, Zone = {classify_zone(seed_ara)}, "
          f"Type = {classify_type(seed_ara)}")
    print("─" * 78)
    print()

    connections = derive_connections(seed_name, seed_ara, seed_period)

    for conn in connections:
        p_ara = conn['predicted_ara']
        p_per = conn['predicted_period']
        p_dist = phi_dist(p_ara)
        p_zone = classify_zone(p_ara)
        p_type = classify_type(p_ara)

        print(f"  {conn['label']}  {conn['direction']}")
        print(f"    Mechanism: {conn['mechanism']}")
        print(f"    Predicted ARA:    {p_ara:.4f}  (φ-dist={p_dist:.3f}, {p_zone}, {p_type})")
        print(f"    Predicted Period: {p_per:.2f} yr")
        print(f"    Coupling:         {conn['coupling_strength']:.4f}")
        print(f"    {conn['note']}")

        # Search for matches
        matches = find_matches(p_ara, p_per)
        if matches:
            print(f"    ┌─ MATCHES:")
            for m in matches[:3]:  # top 3
                ara_str = f"ARA={m['ara']:.3f}" if m['ara'] is not None else "ARA=?"
                match_type = "FULL" if m['full_match'] else ("period" if m['period_match'] else "ara")
                print(f"    │  {match_type:6} → {m['name']} ({ara_str}, P={m['period']:.2f}yr, {m['domain']})")
            print(f"    └─")
        else:
            print(f"    ┌─ NO MATCH — PREDICTION:")
            print(f"    │  A system with ARA ≈ {p_ara:.2f} and period ≈ {p_per:.1f} yr")
            print(f"    │  should exist in the {p_type.lower()} regime.")
            print(f"    └─")
            all_predictions.append({
                'from': seed_name,
                'connection': conn['label'],
                'ara': p_ara,
                'period': p_per,
                'type': p_type,
                'zone': p_zone,
            })

        print()


# ═══════════════════════════════════════════════════════════════
# CROSS-CHECK: Do seeds connect to each other?
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 78)
print("CROSS-SEED CONNECTIONS")
print("=" * 78)
print()
print("Do the seeds find each other through the geometry?")
print()

for seed_name, seed_ara, seed_period in seeds:
    connections = derive_connections(seed_name, seed_ara, seed_period)
    for conn in connections:
        p_ara = conn['predicted_ara']
        p_per = conn['predicted_period']
        # Check against other seeds
        for other_name, other_ara, other_period in seeds:
            if other_name == seed_name:
                continue
            period_ratio = max(p_per, other_period) / max(0.001, min(p_per, other_period))
            ara_diff = abs(p_ara - other_ara)
            if period_ratio <= 2.0 and ara_diff <= 0.5:
                print(f"  {seed_name} → {conn['label'].split('.')[0].strip()}.{conn['label'].split('.')[1].strip()[:20]} → "
                      f"predicts ARA={p_ara:.3f}, P={p_per:.1f}yr")
                print(f"    → CONNECTS TO {other_name} (ARA={other_ara:.3f}, P={other_period:.2f}yr)")
                print(f"    → ARA diff: {ara_diff:.3f}, Period ratio: {period_ratio:.2f}")
                print()


# ═══════════════════════════════════════════════════════════════
# THE φ-RUNG LADDER (vertical structure)
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 78)
print("φ-RUNG LADDER FROM SOLAR SEED")
print("=" * 78)
print()
print("Starting from Solar (P = 11.07 yr), stepping in φ-power periods:")
print()
print(f"  {'Rung':>5}  {'Period':>10}  {'φ^n':>6}  {'Known System':>30}  {'Match?':>8}")
print(f"  {'─'*5}  {'─'*10}  {'─'*6}  {'─'*30}  {'─'*8}")

solar_period = 11.07
for n in range(-6, 12):
    period = solar_period * PHI**(n - 5)  # φ⁵ = Schwabe ≈ 11.09

    # Also express as φ^m from base
    phi_power = n  # since solar ≈ φ⁵

    # Find matches
    best_match = None
    best_ratio = 999
    for name, ara, p, domain in KNOWN_SYSTEMS:
        ratio = max(period, p) / max(0.001, min(period, p))
        if ratio < best_ratio:
            best_ratio = ratio
            best_match = (name, p, domain)

    match_str = ""
    flag = ""
    if best_ratio <= 1.2:
        match_str = f"{best_match[0]} ({best_match[1]:.1f}yr)"
        flag = "✓"
    elif best_ratio <= 1.5:
        match_str = f"~{best_match[0]} ({best_match[1]:.1f}yr)"
        flag = "~"

    print(f"  φ^{phi_power:>2}  {period:>10.2f}  {PHI**phi_power:>6.2f}  {match_str:>30}  {flag:>8}")

print()
print("Key: φ⁵ = Schwabe (11.09yr), φ⁹ = Gleissberg (76yr), φ¹¹ = de Vries (199yr)")


# ═══════════════════════════════════════════════════════════════
# SUMMARY: PREDICTIONS (empty positions in the network)
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 78)
print("EMPTY POSITIONS — PREDICTIONS FROM GEOMETRY")
print("=" * 78)
print()

if all_predictions:
    for i, pred in enumerate(all_predictions, 1):
        print(f"  Prediction {i} (from {pred['from']}, {pred['connection']}):")
        print(f"    ARA ≈ {pred['ara']:.3f}, Period ≈ {pred['period']:.1f} yr")
        print(f"    Type: {pred['type']}, Zone: {pred['zone']}")
        print(f"    φ-dist: {phi_dist(pred['ara']):.3f}")
        print()
else:
    print("  All positions matched! No empty predictions.")
    print()


# ═══════════════════════════════════════════════════════════════
# THE 9-PART STRUCTURE (3 ARA pairs for Solar)
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 78)
print("9-PART STRUCTURE FOR SOLAR SEED")
print("=" * 78)
print()
print("3 ARA pairs × 3 coupling channels = 9 connections:")
print()

# The 3 pairs for Solar:
# Pair 1: Solar ↔ Horizontal partner (Space-Time)
# Pair 2: Solar ↔ Vertical child (Solar → below)
# Pair 3: Solar ↔ Inverse complement (Engine ↔ Consumer)
#
# Each pair has 3 channels (Space, Time, Rationality)

pairs = [
    ("Pair 1: Space-Time (horizontal)", PHI, 11.07, 2-PHI, 11.07),
    ("Pair 2: Vertical (parent-child)", PHI, 11.07, PHI/PHI, 11.07*PHI),
    ("Pair 3: Inverse (engine-consumer)", PHI, 11.07, 1/PHI, 11.07*PHI**4),
]

channels = ['Space', 'Time', 'Rationality']
golden_angle = 137.5077  # degrees

for pair_name, ara_a, per_a, ara_b, per_b in pairs:
    print(f"  {pair_name}")
    print(f"    System A: ARA={ara_a:.3f}, P={per_a:.2f}yr")
    print(f"    System B: ARA={ara_b:.3f}, P={per_b:.2f}yr")
    print()
    for i, ch in enumerate(channels):
        angle = i * golden_angle
        coupling = 1.0 / PHI**4  # each channel coupling
        print(f"      Channel {i+1} ({ch}): offset {angle:.1f}°, coupling 1/φ⁴ = {coupling:.4f}")
    print(f"    → 3 channels × coupling = total pair strength")
    print()

print(f"  Total: 3 pairs × 3 channels = 9 coupling interactions (F⁹ matrix)")
print()

# Final summary
print("=" * 78)
print("NETWORK FIELD SUMMARY")
print("=" * 78)
print()
print("From 3 seed systems (Solar, Earthquake, ENSO), the three-circle geometry")
print("predicts coupling partners at specific ARA/period positions.")
print()
print("Key findings:")
print("  1. Solar's horizontal partner has ARA = 0.382 (= 2-φ = 1/φ²)")
print(f"     → Period = 11.07 yr — SAME period as Earthquake (11.09 yr)!")
print(f"     → But predicted ARA = 0.382, actual Earthquake ARA = 0.15")
print(f"     → Earthquake is deeper consumer than horizontal mirror predicts")
print()
print("  2. Solar's vertical child (↓1 rung) has Period = 17.9 yr")
print("     → Near the Hale half-cycle / lunar nodal (18.6 yr)")
print()
print("  3. Solar's cascade child (↓2 rungs) has Period = 28.9 yr")
print("     → Near PDO period (25 yr)")
print()
print("  4. Solar's inverse complement has Period = 76.0 yr")
print("     → EXACTLY the Gleissberg cycle — the formula's own modulation!")
print()
print("  5. ENSO's vertical child has Period = 6.1 yr")
print("     → Near NAO period (7 yr) and Nile/CO2 period (7.5 yr)")
print()
print("  6. Earthquake's inverse complement has ARA = 2.0 (≈ ENSO)")
print("     → Earthquake and ENSO are predicted to be engine-consumer pair!")
