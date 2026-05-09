#!/usr/bin/env python3
"""
Script 242b — Horizontal Mapping Across Each φ-Rung

The vertical ladder (242) shows WHERE the rungs are.
The horizontal mapping shows WHO sits at each rung and HOW they couple.

At each rung (fixed period), the ARA scale runs 0 → 2:
  0.0 = singularity (pure accumulation)
  1.0 = clock (balanced)
  2.0 = pure harmonic (pure release)

The horizontal partner rule: ARA_partner = 2 - ARA_self
  Solar (φ) ↔ partner at (2-φ) = 0.382
  ENSO (2.0) ↔ partner at 0.0 (singularity!)
  Earthquake (0.15) ↔ partner at 1.85

Dylan's insight: "The horizontal is going to be the interesting one."
This is where engine-consumer PAIRS live — same period, opposite ARA.

For each rung we ask:
  1. What systems do we know at this period?
  2. What does the mirror rule predict their partners should be?
  3. Do those partners exist? If so, what are they?
  4. If not — PREDICTION: a system with that ARA should exist at this period.
"""

import math
import numpy as np

PHI = (1 + math.sqrt(5)) / 2

# ═══════════════════════════════════════════════════════════════
# ALL KNOWN OSCILLATORY SYSTEMS WITH PERIODS
# ═══════════════════════════════════════════════════════════════

# (name, ARA, period_years, domain, notes)
SYSTEMS = [
    # Tested in formula (ARA measured)
    ('Solar',           PHI,    11.07,  'Astrophysics',  'Schwabe cycle, tested'),
    ('ENSO',            2.0,    3.75,   'Climate',       'El Niño, tested'),
    ('Earthquake',      0.15,   11.09,  'Seismology',    'Major EQ clustering, tested'),
    ('Heart',           1.35,   0.00019,'Cardiology',    '~1s period, tested'),
    ('Hare',            1.0,    9.6,    'Ecology',       'Snowshoe hare cycle, tested'),
    ('Lynx',            1.0,    9.5,    'Ecology',       'Canada lynx cycle, tested'),
    ('Unemployment',    0.75,   7.0,    'Economics',     'US recession cycle, tested'),
    ('GDP Growth',      1.0,    3.9,    'Economics',     'US business cycle, tested'),
    ('CO2 Amplitude',   0.15,   7.6,    'Atmospheric',   'Keeling seasonal, tested'),
    ('Nile',            0.15,   7.5,    'Hydrology',     'Aswan annual flow, tested'),

    # Known oscillatory systems (ARA not yet measured)
    ('QBO',             None,   2.3,    'Climate',       'Quasi-biennial oscillation, stratospheric wind'),
    ('NAO',             None,   7.0,    'Climate',       'North Atlantic Oscillation'),
    ('PDO',             None,   25.0,   'Climate',       'Pacific Decadal Oscillation'),
    ('AMO',             None,   60.0,   'Climate',       'Atlantic Multidecadal Oscillation'),
    ('Gleissberg',      None,   76.0,   'Astrophysics',  'Solar modulation envelope'),
    ('de Vries/Suess',  None,   199.0,  'Astrophysics',  'Long-term solar modulation'),
    ('Hale magnetic',   None,   22.0,   'Astrophysics',  'Full magnetic reversal cycle'),
    ('Lunar nodal',     None,   18.6,   'Geophysics',    'Tidal modulation cycle'),
    ('Chandler wobble', None,   1.2,    'Geophysics',    'Earth polar motion'),

    # Additional well-documented oscillations
    ('IOD',             None,   3.5,    'Climate',       'Indian Ocean Dipole'),
    ('MJO',             None,   0.10,   'Climate',       'Madden-Julian ~40 days'),
    ('Sunspot latitude',None,   11.0,   'Astrophysics',  'Butterfly diagram migration'),
    ('Solar wind',      None,   1.3,    'Astrophysics',  '~1.3 yr quasi-periodic'),
    ('Volcanic (VEI5+)',None,   50.0,   'Geology',       'Major eruption clustering'),
    ('Milankovitch obl',None,   41000,  'Geophysics',    'Obliquity cycle'),
    ('Milankovitch ecc',None,   100000, 'Geophysics',    'Eccentricity cycle'),
    ('Milankovitch pre',None,   23000,  'Geophysics',    'Precession cycle'),
]


def phi_dist(ara):
    if ara is None:
        return None
    a = max(0.01, ara)
    return abs(math.log(a)) / math.log(PHI)


def rung_number(period):
    """Which φ-rung is this period closest to? (φ⁵ = solar ≈ 11.07)"""
    if period <= 0:
        return None
    # log_φ(period) gives the rung
    return math.log(period) / math.log(PHI)


def nearest_rung(period):
    """Round to nearest integer φ-rung."""
    r = rung_number(period)
    return round(r)


def rung_period(n):
    """Period at rung n."""
    return PHI ** n


def rung_fit(period):
    """How close is this period to its nearest φ-rung? Returns (rung, ratio)."""
    r = nearest_rung(period)
    ideal = rung_period(r)
    ratio = max(period, ideal) / min(period, ideal)
    return r, ratio


# ═══════════════════════════════════════════════════════════════
# GROUP SYSTEMS BY RUNG
# ═══════════════════════════════════════════════════════════════

print("=" * 78)
print("Script 242b — Horizontal Mapping Across Each φ-Rung")
print("=" * 78)
print()

# Group systems by their nearest rung
rung_groups = {}
for name, ara, period, domain, notes in SYSTEMS:
    r, ratio = rung_fit(period)
    if ratio <= 1.6:  # within 60% of ideal period — reasonable match
        if r not in rung_groups:
            rung_groups[r] = []
        rung_groups[r].append({
            'name': name, 'ara': ara, 'period': period,
            'domain': domain, 'notes': notes,
            'rung': r, 'ideal_period': rung_period(r), 'ratio': ratio
        })

# Sort rungs
sorted_rungs = sorted(rung_groups.keys())

print("Systems grouped by φ-rung (period tolerance ≤ 1.6×):")
print()

for r in sorted_rungs:
    ideal = rung_period(r)
    systems = rung_groups[r]
    n_with_ara = sum(1 for s in systems if s['ara'] is not None)

    print(f"═══ φ^{r} — Period ≈ {ideal:.2f} yr {'═' * (50 - len(f'φ^{r} — Period ≈ {ideal:.2f} yr'))}")
    print()

    # Sort by ARA (None last)
    systems.sort(key=lambda s: s['ara'] if s['ara'] is not None else 99)

    for s in systems:
        ara_str = f"ARA={s['ara']:.3f}" if s['ara'] is not None else "ARA=?"
        pd_str = f"φ-dist={phi_dist(s['ara']):.3f}" if s['ara'] is not None else ""
        print(f"  {s['name']:<20} {ara_str:>12}  P={s['period']:.2f}yr  "
              f"({s['ratio']:.2f}× ideal)  {pd_str}")

    # ── Horizontal mirror analysis ──
    print()
    print(f"  HORIZONTAL MIRRORS (ARA_partner = 2 - ARA_self):")

    for s in systems:
        if s['ara'] is None:
            continue
        mirror_ara = 2.0 - s['ara']
        if mirror_ara < 0:
            mirror_ara = 0.0

        # Search for match at this rung
        match = None
        best_diff = 999
        for other in systems:
            if other['name'] == s['name']:
                continue
            if other['ara'] is not None:
                diff = abs(other['ara'] - mirror_ara)
                if diff < best_diff:
                    best_diff = diff
                    match = other

        if match and best_diff < 0.5:
            print(f"    {s['name']} ({s['ara']:.3f}) ↔ mirror at {mirror_ara:.3f} "
                  f"→ FOUND: {match['name']} ({match['ara']:.3f}), diff={best_diff:.3f}")
        elif match and best_diff < 1.0:
            print(f"    {s['name']} ({s['ara']:.3f}) ↔ mirror at {mirror_ara:.3f} "
                  f"→ NEAR: {match['name']} ({match['ara']:.3f}), diff={best_diff:.3f}")
        else:
            # What type would this be?
            if mirror_ara < 0.2:
                mtype = "violent snap"
            elif mirror_ara < 0.9:
                mtype = "consumer"
            elif mirror_ara < 1.3:
                mtype = "clock/absorber"
            elif mirror_ara < 1.5:
                mtype = "clock-bio"
            elif mirror_ara < 1.7:
                mtype = "engine"
            elif mirror_ara < 1.9:
                mtype = "exothermic"
            else:
                mtype = "pure harmonic"

            print(f"    {s['name']} ({s['ara']:.3f}) ↔ mirror at {mirror_ara:.3f} "
                  f"→ EMPTY ({mtype}) — PREDICTION: system with ARA≈{mirror_ara:.2f}, "
                  f"P≈{ideal:.1f}yr should exist")

    # ── Inverse complement (1/ARA) ──
    print()
    print(f"  INVERSE COMPLEMENTS (ARA_partner = 1/ARA, period × φ⁴):")

    for s in systems:
        if s['ara'] is None or s['ara'] < 0.01:
            continue
        inv_ara = 1.0 / s['ara']
        inv_period = s['period'] * PHI**4

        # Find match anywhere in SYSTEMS
        match = None
        best_score = 999
        for name, ara, period, domain, notes in SYSTEMS:
            if name == s['name']:
                continue
            period_ratio = max(inv_period, period) / max(0.001, min(inv_period, period))
            if period_ratio < 2.0:
                if ara is not None:
                    score = abs(ara - inv_ara) + (period_ratio - 1.0)
                else:
                    score = period_ratio - 1.0
                if score < best_score:
                    best_score = score
                    match = (name, ara, period, domain)

        if match:
            m_ara_str = f"ARA={match[1]:.3f}" if match[1] is not None else "ARA=?"
            print(f"    {s['name']} ({s['ara']:.3f}) → 1/ARA={inv_ara:.3f}, P≈{inv_period:.1f}yr "
                  f"→ {match[0]} ({m_ara_str}, P={match[2]:.1f}yr)")
        else:
            print(f"    {s['name']} ({s['ara']:.3f}) → 1/ARA={inv_ara:.3f}, P≈{inv_period:.1f}yr "
                  f"→ EMPTY — PREDICTION")

    print()


# ═══════════════════════════════════════════════════════════════
# THE HORIZONTAL FIELD — ARA × RUNG GRID
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 78)
print("THE HORIZONTAL FIELD — ARA × RUNG GRID")
print("=" * 78)
print()
print("Each cell shows what system (if any) sits at that (ARA, Rung) position.")
print("Horizontal partners are at symmetric positions across ARA=1.0.")
print()

# ARA bins
ara_bins = [
    (0.0, 0.2,  'Snap'),
    (0.2, 0.5,  'Consumer'),
    (0.5, 0.9,  'Near-clock'),
    (0.9, 1.1,  'Clock'),
    (1.1, 1.4,  'Absorber'),
    (1.4, 1.7,  'Engine'),
    (1.7, 1.9,  'Exothermic'),
    (1.9, 2.1,  'Harmonic'),
]

# Print header
header = f"{'Rung':>6} {'Period':>8} |"
for _, _, label in ara_bins:
    header += f" {label:^12} |"
print(header)
print("─" * len(header))

for r in range(-1, 12):
    ideal = rung_period(r)
    if ideal > 300 or ideal < 0.3:
        continue

    row = f"  φ^{r:>2} {ideal:>7.1f}yr |"

    for lo, hi, label in ara_bins:
        # Find systems at this rung in this ARA bin
        found = []
        if r in rung_groups:
            for s in rung_groups[r]:
                if s['ara'] is not None and lo <= s['ara'] < hi:
                    found.append(s['name'][:10])
                elif s['ara'] is None:
                    # Unknown ARA — mark with ?
                    pass

        if found:
            cell = ','.join(found)[:12]
        else:
            # Is this a mirror position of something?
            if r in rung_groups:
                mirrors_here = False
                for s in rung_groups[r]:
                    if s['ara'] is not None:
                        mirror = 2.0 - s['ara']
                        if lo <= mirror < hi:
                            mirrors_here = True
                if mirrors_here:
                    cell = "← MIRROR →"
                else:
                    cell = "·"
            else:
                cell = "·"

        row += f" {cell:^12} |"

    print(row)

print()
print("Legend: Named = known system, ← MIRROR → = predicted partner, · = empty")


# ═══════════════════════════════════════════════════════════════
# SPECIFIC HORIZONTAL PAIRS — THE KEY TEST
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 78)
print("HORIZONTAL PAIRS — THE KEY CONNECTIONS")
print("=" * 78)
print()
print("At each rung, which engine-consumer pairs does the geometry predict?")
print()

key_pairs = [
    ("φ⁵ (~11 yr)", 5, [
        ('Solar',      PHI,   'Tested engine'),
        ('Earthquake', 0.15,  'Tested consumer'),
    ]),
    ("φ⁴ (~6.8 yr)", 4, [
        ('CO2 Amp',    0.15,  'Tested consumer (half-system)'),
        ('Nile',       0.15,  'Tested consumer (half-system)'),
        ('Unemployment',0.75, 'Tested near-clock'),
        ('NAO',        None,  'Period match, ARA unknown'),
    ]),
    ("φ³ (~4.2 yr)", 3, [
        ('ENSO',       2.0,   'Tested pure harmonic'),
        ('GDP Growth', 1.0,   'Tested clock'),
        ('IOD',        None,  'Period match, ARA unknown'),
    ]),
    ("φ² (~2.6 yr)", 2, [
        ('QBO',        None,  'Period match, ARA unknown'),
    ]),
    ("φ⁷ (~29 yr)", 7, [
        ('PDO',        None,  'Period match, ARA unknown'),
    ]),
    ("φ⁹ (~76 yr)", 9, [
        ('Gleissberg', None,  'Period match, ARA unknown'),
        ('AMO',        None,  'Period ~60yr, rough match'),
    ]),
]

for rung_label, r, systems in key_pairs:
    ideal = rung_period(r)
    print(f"  {rung_label} (ideal {ideal:.2f} yr)")
    print()

    for name, ara, note in systems:
        if ara is not None:
            mirror = 2.0 - ara
            print(f"    {name:15} ARA={ara:.3f}  → mirror partner ARA={mirror:.3f}")
            print(f"      {note}")
            # What would the mirror be?
            if mirror < 0.2:
                print(f"      → Mirror is a VIOLENT SNAP (ARA={mirror:.3f})")
            elif mirror < 0.5:
                print(f"      → Mirror is a CONSUMER (ARA={mirror:.3f})")
            elif mirror < 0.9:
                print(f"      → Mirror is a NEAR-CLOCK (ARA={mirror:.3f})")
            elif mirror < 1.1:
                print(f"      → Mirror is a CLOCK (ARA={mirror:.3f})")
            elif mirror < 1.5:
                print(f"      → Mirror is an ABSORBER (ARA={mirror:.3f})")
            elif mirror < 1.7:
                print(f"      → Mirror is an ENGINE (ARA={mirror:.3f})")
            elif mirror < 1.9:
                print(f"      → Mirror is EXOTHERMIC (ARA={mirror:.3f})")
            else:
                print(f"      → Mirror is PURE HARMONIC (ARA={mirror:.3f})")
        else:
            print(f"    {name:15} ARA=?     → need to measure ARA first")
            print(f"      {note}")
        print()

    # What the geometry says about this rung
    if r == 5:
        print(f"    GEOMETRY: Solar (φ) and Earthquake (0.15) share this rung.")
        print(f"    Solar's mirror = 2-φ = 0.382. Earthquake at 0.15 is DEEPER than mirror.")
        print(f"    → Something at ARA ≈ 0.382 with P ≈ 11yr may be missing from our list.")
        print(f"    → Earthquake may couple to Solar through a DIFFERENT channel (not horizontal).")
        print(f"    → Candidate: Solar latitude migration? Sunspot area? Coronal mass ejections?")
    elif r == 4:
        print(f"    GEOMETRY: Three consumers (CO2, Nile, Unemployment) but NO ENGINE.")
        print(f"    → CO2 mirror = 1.85. Nile mirror = 1.85. Where is the ARA≈1.85 engine?")
        print(f"    → This is the MISSING HALF. The engine at this rung drives all three consumers.")
        print(f"    → Candidate: Ethiopian monsoon intensity? NAO if ARA≈1.85? Solar wind ~1.3yr?")
    elif r == 3:
        print(f"    GEOMETRY: ENSO (2.0) mirror = 0.0 (singularity!)")
        print(f"    → ENSO's horizontal partner is at the singularity boundary.")
        print(f"    → GDP (1.0) is the clock at this rung. Its mirror is also 1.0 — self-mirroring.")
        print(f"    → IOD (Indian Ocean Dipole) has similar period — if ARA ≈ 0, it's ENSO's partner.")

    print()
    print("  " + "─" * 70)
    print()

print()
print("=" * 78)
print("SUMMARY — WHAT THE HORIZONTAL MAP TELLS US")
print("=" * 78)
print()
print("1. φ⁵ RUNG (11 yr): Solar and Earthquake confirmed as rung-mates.")
print("   Solar's true horizontal mirror (ARA=0.382) may be an unmeasured solar")
print("   subsystem. Earthquake is deeper (ARA=0.15) — possibly a cascade child")
print("   that happens to share the same period.")
print()
print("2. φ⁴ RUNG (6.8 yr): THREE consumers (CO2, Nile, Unemployment) but NO ENGINE.")
print("   The geometry DEMANDS an engine at ARA≈1.85 with period ~7yr at this rung.")
print("   This is the missing half that explains why CO2 and Nile fail alone.")
print("   Prime candidate: Ethiopian monsoon or NAO (if its ARA is ≈1.85).")
print()
print("3. φ³ RUNG (4.2 yr): ENSO sits at ARA=2.0, the ceiling.")
print("   Its horizontal mirror is ARA=0.0 — the singularity. This means ENSO has")
print("   NO horizontal partner; it IS the boundary. GDP at ARA=1.0 self-mirrors.")
print()
print("4. PREDICTION: The engine at φ⁴ (~7yr, ARA≈1.85) is the most testable")
print("   missing piece. Finding it would explain the CO2 and Nile failures AND")
print("   validate the horizontal mirror rule.")
