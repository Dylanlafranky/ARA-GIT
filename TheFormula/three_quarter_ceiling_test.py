"""
three_quarter_ceiling_test.py

Falsifiable test of the framework's "3/4 universal ceiling" claim:

  Self-organizing systems can occupy at most 3/4 of the displacement from
  balance (ARA = 1.0) toward either singularity (ARA = 0 or ARA = 2).
  Operational range: [0.25, 1.75].

  Anything outside this range should be either:
    (a) a "snap" system falling into time-singularity (ARA > 2)
    (b) a transient or measurement artifact
    (c) a genuine refutation of the framework's universal ceiling claim

Method:
  - Parse the master ARA catalog (F:\SystemFormulaFolder\master_ara_visualization.html)
  - Extract every (name, system, domain, ARA) tuple
  - Tabulate the distribution
  - Identify systems outside [0.25, 1.75]
  - Classify each outsider: snap-class (>2), or genuine outlier
  - Report whether the prediction holds
"""
import re, json, os
from collections import Counter, defaultdict

VIS_PATH = "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/master_ara_visualization.html"
OUT      = "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/TheFormula/three_quarter_ceiling_data.js"

# Parse the JS data array from the HTML
with open(VIS_PATH) as f:
    text = f.read()

# Match: { name: '...', system: '...', domain: '...', ara: NN, period: NN }
pattern = re.compile(
    r"\{\s*name:\s*'([^']+)',\s*system:\s*'([^']+)',\s*domain:\s*'([^']+)',\s*ara:\s*([\d\.eE+-]+),\s*period:\s*([\d\.eE+-]+)\s*\}"
)
records = []
for match in pattern.finditer(text):
    name, system, domain, ara_str, period_str = match.groups()
    try:
        ara = float(ara_str)
        period = float(period_str)
    except:
        continue
    records.append(dict(name=name, system=system, domain=domain, ara=ara, period=period))

print(f"Parsed {len(records)} systems from master ARA catalog")

# === Distribution analysis ===
buckets = {
    "deep_consumer (0..0.25)":    [],
    "operational_consumer (0.25..0.95)": [],
    "balance (0.95..1.05)":       [],
    "operational_engine (1.05..1.75)": [],
    "operational_donor (1.70..1.80)":  [],
    "extreme (1.75..2.0)":        [],
    "harmonic (1.95..2.05)":      [],
    "snap (2.05..10)":            [],
    "deep_snap (>10)":            [],
}

for r in records:
    a = r['ara']
    if a < 0.25: buckets["deep_consumer (0..0.25)"].append(r)
    elif 0.25 <= a < 0.95: buckets["operational_consumer (0.25..0.95)"].append(r)
    elif 0.95 <= a < 1.05: buckets["balance (0.95..1.05)"].append(r)
    elif 1.05 <= a < 1.70: buckets["operational_engine (1.05..1.75)"].append(r)
    elif 1.70 <= a < 1.80: buckets["operational_donor (1.70..1.80)"].append(r)
    elif 1.80 <= a < 1.95: buckets["extreme (1.75..2.0)"].append(r)
    elif 1.95 <= a < 2.05: buckets["harmonic (1.95..2.05)"].append(r)
    elif 2.05 <= a < 10:   buckets["snap (2.05..10)"].append(r)
    else:                   buckets["deep_snap (>10)"].append(r)

print(f"\n{'BUCKET':<35} {'COUNT':>5}  EXAMPLES")
print(f"{'─'*35} {'─'*5}  {'─'*40}")
for bucket, items in buckets.items():
    examples = ", ".join(f"{r['name']} ({r['ara']:.2f})" for r in items[:3])
    if len(items) > 3:
        examples += f", … +{len(items)-3} more"
    print(f"{bucket:<35} {len(items):>5}  {examples}")

# === Test the 3/4 ceiling claim ===
in_range  = [r for r in records if 0.25 <= r['ara'] <= 1.75]
out_range = [r for r in records if r['ara'] < 0.25 or r['ara'] > 1.75]
in_pct = 100.0 * len(in_range) / len(records)

print(f"\n{'='*70}")
print(f"3/4 CEILING TEST: do systems sit in [0.25, 1.75]?")
print(f"{'='*70}")
print(f"  In range  [0.25 ≤ ARA ≤ 1.75]: {len(in_range)}/{len(records)}  ({in_pct:.1f}%)")
print(f"  Out range:                     {len(out_range)}/{len(records)}  ({100-in_pct:.1f}%)")

# Classify the outliers
print(f"\n--- Outliers above 1.75 ---")
above = sorted([r for r in records if r['ara'] > 1.75], key=lambda r: r['ara'])
for r in above:
    classification = "SNAP" if r['ara'] > 2.0 else "ZONE-1.75-2.0"
    print(f"  {r['ara']:>7.2f}  {classification:>12}  {r['name']:<35}  ({r['domain']})")

print(f"\n--- Outliers below 0.25 ---")
below = sorted([r for r in records if r['ara'] < 0.25], key=lambda r: r['ara'])
for r in below:
    print(f"  {r['ara']:>7.4f}  {r['name']:<35}  ({r['domain']})")

# === Subdivide outliers by reasonable categories ===
above_175_below_2 = [r for r in records if 1.75 < r['ara'] < 2.0]
at_2 = [r for r in records if 1.95 <= r['ara'] <= 2.05]
snap_zone = [r for r in records if r['ara'] > 2.05]

print(f"\n{'='*70}")
print(f"REFINED VERDICT")
print(f"{'='*70}")
print(f"  Systems strictly inside [0.25, 1.75]:           {len(in_range)} / {len(records)}  ({in_pct:.1f}%)")
print(f"  Systems in (1.75, 2.0):                         {len(above_175_below_2)}")
print(f"  Systems at exactly 2.0 (pure harmonic):         {len(at_2)}")
print(f"  Systems > 2.05 (snap zone, into time-singularity): {len(snap_zone)}")
print(f"  Systems < 0.25 (deep consumer, falling into space-singularity):  {len([r for r in records if r['ara'] < 0.25])}")

# Framework-consistent interpretation
self_organizing_count = len(in_range)
boundary_at_2 = len(at_2)
snap_count = len(snap_zone)

print(f"\nFramework prediction: self-organizing systems should sit in [0.25, 1.75].")
print(f"  - Systems at the boundary at 2.0 are 'pure harmonic' — NOT self-organizing")
print(f"    (per framework: they've handed off all time-content, just resonate passively)")
print(f"  - Systems past 2.05 are 'snap' — falling into time-singularity")
print(f"")
if len(above_175_below_2) == 0:
    print(f"  ✓ NO SYSTEMS in (1.75, 2.0). The 3/4 ceiling holds at the time end.")
else:
    print(f"  ⚠ {len(above_175_below_2)} systems in (1.75, 2.0) — partial refutation:")
    for r in above_175_below_2:
        print(f"    - {r['name']} (ARA={r['ara']:.2f}, {r['domain']})")

below_025 = [r for r in records if r['ara'] < 0.25]
if len(below_025) == 0:
    print(f"  ✓ NO SYSTEMS below 0.25. The 3/4 ceiling holds at the space end.")
else:
    print(f"  ⚠ {len(below_025)} systems below 0.25 — possible refutation:")
    for r in below_025:
        print(f"    - {r['name']} (ARA={r['ara']:.4f}, {r['domain']})")

# Save data
out = dict(
    n_systems=len(records),
    in_range_count=len(in_range),
    out_range_count=len(out_range),
    in_range_pct=in_pct,
    above_175=above,
    below_025=below,
    buckets={k: len(v) for k, v in buckets.items()},
)
with open(OUT, 'w') as f:
    f.write("window.THREE_QUARTER = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved → {OUT}")
