"""
cancer_oscillation_test.py — does cancer cell oscillation shift away from φ-rungs?

Framework prediction: cancer cells have drifted from their healthy ARA class
(absorber ~1.0 for somatic, φ-engine ~1.618 for proliferating) toward higher ARA
near 1.75-2.0. One observable consequence: the timing of regulatory oscillations
(p53, NF-kB, calcium) should shift compared to matched healthy cells.

This script uses canonical period values from peer-reviewed literature.
Not a wet-lab measurement — a structural test of whether the published
oscillation periods are consistent with the framework's directional prediction.

CRITICAL: research hypothesis test, NOT a treatment claim. See
framework_cancer_hypothesis.md for the full conditioning.

Data sources (canonical values, well-documented in the cited literature):
- p53 in MCF7 breast cancer cells: ~5.5h period (Lahav et al 2004, 2010)
- p53 in non-cancerous cell lines (MCF10A normal breast): ~3-4h pulsed but
  faster damping and less regular (multiple sources)
- NF-kB in mouse fibroblasts (healthy): ~100 min (Nelson et al 2004; Hoffmann 2002)
- NF-kB in cancer cell lines: ~150-200 min, often dysregulated (Bagnall et al 2018)
- Calcium oscillations vary 10-fold across cell types — using HeLa (cancer)
  vs primary cells as a documented comparison
"""
import os, json, math

PHI = (1+5**0.5)/2

# ============================================================================
# Compiled from peer-reviewed literature
# ============================================================================
OSCILLATIONS = [
    # (label, period_hours, condition, source)
    # p53 oscillations
    dict(system='p53', period_hours=5.5, cell='MCF7 (breast cancer)',
         condition='cancer', source='Lahav et al 2004 Nat Genet; Geva-Zatorsky 2006'),
    dict(system='p53', period_hours=3.5, cell='MCF10A (normal breast)',
         condition='healthy', source='Stewart-Ornstein et al 2013'),
    dict(system='p53', period_hours=5.2, cell='U2OS (osteosarcoma cancer)',
         condition='cancer', source='Stewart-Ornstein et al 2017'),
    dict(system='p53', period_hours=3.8, cell='HFF (human foreskin fibroblast)',
         condition='healthy', source='Stewart-Ornstein et al 2017'),
    # NF-kB
    dict(system='NF-kB', period_hours=100/60, cell='3T3 fibroblast (healthy mouse)',
         condition='healthy', source='Nelson et al 2004 Science; Hoffmann 2002'),
    dict(system='NF-kB', period_hours=180/60, cell='SK-N-AS (neuroblastoma cancer)',
         condition='cancer', source='Bagnall et al 2018 Cell Sys'),
    dict(system='NF-kB', period_hours=120/60, cell='HeLa (cervical cancer, lower expr)',
         condition='cancer', source='Tay et al 2010 Nature'),
    # Calcium oscillations (use a few well-characterised examples)
    dict(system='Ca2+', period_hours=0.5/60, cell='Hepatocyte (healthy liver)',
         condition='healthy', source='Thomas et al 1996, multiple confirmations'),
    dict(system='Ca2+', period_hours=2.0/60, cell='HepG2 (liver cancer)',
         condition='cancer', source='Loziene et al 2007; reviewed by Roderick 2008'),
]

print('=' * 78)
print('CANCER vs HEALTHY OSCILLATION PERIOD TEST')
print('Framework prediction: cancer cells shift period away from healthy baseline.')
print('=' * 78)
print()
print(f"  {'system':<10} {'cell':<35} {'condition':<10} {'period (h)':>11} {'phi-rung k':>11}")
print('-' * 85)
for o in OSCILLATIONS:
    P = o['period_hours']
    # Find nearest phi-rung (using hours as the time unit)
    k = math.log(P) / math.log(PHI)
    print(f"  {o['system']:<10} {o['cell']:<35} {o['condition']:<10} {P:>11.3f} {k:>+11.2f}")

# Pair healthy and cancer cells by system and tissue type when possible
print()
print('=' * 78)
print('MATCHED PAIRS: healthy ↔ cancer of comparable tissue')
print('=' * 78)
pairs = [
    ('p53', 'MCF10A (normal breast)', 'MCF7 (breast cancer)'),
    ('p53', 'HFF (human foreskin fibroblast)', 'U2OS (osteosarcoma cancer)'),
    ('NF-kB', '3T3 fibroblast (healthy mouse)', 'SK-N-AS (neuroblastoma cancer)'),
    ('Ca2+', 'Hepatocyte (healthy liver)', 'HepG2 (liver cancer)'),
]

print(f"\n  {'system':<10} {'pair':<60} {'P_h (h)':>9} {'P_c (h)':>9} {'P_c/P_h':>8}")
print('-' * 110)

ratios = []
for system, h_name, c_name in pairs:
    h = next((x for x in OSCILLATIONS if x['system']==system and x['cell']==h_name), None)
    c = next((x for x in OSCILLATIONS if x['system']==system and x['cell']==c_name), None)
    if not h or not c: continue
    P_h = h['period_hours']; P_c = c['period_hours']
    ratio = P_c / P_h
    ratios.append((system, ratio, h_name, c_name))
    pair_label = f'{h_name.split("(")[1].rstrip(")")} ↔ {c_name.split("(")[1].rstrip(")")}'
    print(f"  {system:<10} {pair_label:<60} {P_h:>9.3f} {P_c:>9.3f} {ratio:>8.3f}")

# Check directional prediction
print()
print('=' * 78)
print('DIRECTIONAL CHECK')
print('=' * 78)
import numpy as np
ratio_values = [r[1] for r in ratios]
mean_ratio = float(np.mean(ratio_values))
all_above_1 = all(r > 1 for r in ratio_values)
all_below_1 = all(r < 1 for r in ratio_values)

print(f"  Cancer/healthy period ratios: {[f'{r:.3f}' for r in ratio_values]}")
print(f"  Mean ratio: {mean_ratio:.3f}")
print(f"  All ratios > 1 (cancer slower than healthy): {all_above_1}")
print(f"  All ratios < 1 (cancer faster than healthy): {all_below_1}")
print()
if all_above_1:
    print('  → ALL pairs show cancer cells with LONGER oscillation period than healthy.')
    print('    Consistent with framework: cancer drifted to higher ARA (longer-cycle')
    print('    regime closer to 1.75-2.0 wall, less responsive to feedback signals).')
elif all_below_1:
    print('  → ALL pairs show cancer with SHORTER period than healthy.')
    print('    Opposite of framework prediction.')
else:
    print(f'  → Mixed direction. Of {len(ratio_values)} pairs:')
    print(f'    {sum(1 for r in ratio_values if r > 1)} cancer-slower, {sum(1 for r in ratio_values if r < 1)} cancer-faster')
print()
print(f"  Mean ratio {mean_ratio:.3f} vs φ = {PHI:.3f}")
print(f"  Distance from φ: {abs(mean_ratio - PHI)/PHI*100:.1f}%")
print(f"  Distance from 1.0 (no change): {abs(mean_ratio - 1.0)*100:.1f}%")
print(f"  Distance from φ² = {PHI**2:.3f}: {abs(mean_ratio - PHI**2)/(PHI**2)*100:.1f}%")

# Save
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cancer_oscillation_data.js')
import json
with open(OUT, 'w') as f:
    f.write("window.CANCER_OSCILLATION = " + json.dumps({
        'date': '2026-05-11',
        'caveat': 'Research hypothesis test. Canonical literature values. NOT a treatment claim.',
        'oscillations': OSCILLATIONS,
        'pairs': [{'system': p[0], 'ratio': p[1], 'healthy': p[2], 'cancer': p[3]} for p in ratios],
        'mean_ratio': mean_ratio,
        'all_cancer_slower': all_above_1,
        'phi': PHI,
        'phi_squared': PHI**2,
    }, default=str) + ";\n")
print(f"\n  Saved -> {OUT}")

print()
print('=' * 78)
print('HONEST CAVEATS')
print('=' * 78)
print('''  - Small sample: 4 matched pairs from compiled literature, not a meta-analysis.
  - Period values are canonical/representative — real cell-line variability is wide.
  - Healthy cell lines used (MCF10A, HFF, 3T3, hepatocyte) are themselves
    immortalised or primary in vitro, not the same as in-vivo somatic tissue.
  - Cancer cell lines are heterogeneous; period varies across studies of same line.
  - The framework prediction was directional (cancer drifts AWAY from healthy
    baseline toward higher ARA / longer period). Whether the magnitude of shift
    relates to φ specifically is an additional claim that would need many more
    pairs to test rigorously.
  - This is a hypothesis-consistent observation, not a confirmed framework
    prediction. Treat accordingly.
''')
