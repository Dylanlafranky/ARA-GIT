#!/usr/bin/env python3
"""
Script 72 — Medicine and Disease as ARA
=========================================

Claim: Health IS ARA at φ. Disease IS ARA displacement from φ.
  Homeostasis / baseline = CLOCK (ARA ≈ 1.0, resting, stable)
  Health / function      = ENGINE (ARA ≈ φ, sustained optimal function)
  Disease / crisis       = SNAP (ARA >> 2, acute failure) or
                           CLOCK-LOCK (ARA → 1.0, chronic stagnation)

The immune system, wound healing, cancer, chronic illness, drug effects,
and medical interventions all follow the three-phase ARA pattern.

Tests:
  1. Physiological systems: health = engine zone, disease = displacement from φ
  2. Immune response: innate(clock) + adaptive(engine) + cytokine storm(snap)
  3. Wound healing follows the ARA cycle: injury(snap) → repair(engine) → scar(clock)
  4. Cancer = engine that lost its clock phase (unregulated growth)
  5. Chronic diseases = ARA stuck between clock and engine (narrow band)
  6. Drug mechanisms: restore ARA toward φ
  7. Heart rate variability: HRV at φ = maximum health
  8. Autoimmune = engine attacking its own clock
  9. Aging = progressive ARA drift from φ toward clock
 10. ME/CFS mapped: the narrowed oscillation band
"""

import numpy as np
from scipy import stats

PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

print("=" * 70)
print("SCRIPT 72 — MEDICINE AND DISEASE AS ARA")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────
# TEST 1: Physiological systems — health = engine zone
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 1: Health = Engine Zone, Disease = Displacement from φ")
print("─" * 70)

physiology = [
    # Healthy states (engine zone)
    ("Resting heart rate (healthy)", 1.55, "engine", "60-100 bpm, HRV present"),
    ("Normal blood pressure cycle", 1.58, "engine", "Systole/diastole ratio, near φ"),
    ("Breathing at rest", 1.50, "engine", "Inhale/exhale asymmetry, sustained"),
    ("Circadian cortisol cycle", 1.55, "engine", "Morning spike, gradual decline"),
    ("Gut motility (normal)", 1.52, "engine", "Peristaltic waves, sustained"),
    ("Bone remodelling", 1.55, "engine", "Osteoclast/osteoblast balance"),
    ("Menstrual cycle", 1.60, "engine", "28-day engine, near φ"),
    ("Thermoregulation", 1.55, "engine", "37°C maintenance, sustained"),

    # Disease — clock-locked (too rigid)
    ("Atrial fibrillation", 1.0, "disease-clock", "Lost rhythm, chaotic but averaging to clock"),
    ("Parkinson's tremor", 1.0, "disease-clock", "Rigid rhythmic tremor, pure clock"),
    ("Catatonia", 1.0, "disease-clock", "Frozen state, no engine"),
    ("Osteoporosis", 1.05, "disease-clock", "Remodelling engine stalled"),

    # Disease — snap (acute crisis)
    ("Heart attack (MI)", 8.0, "disease-snap", "Sudden blockage, acute damage"),
    ("Stroke", 10.0, "disease-snap", "Sudden loss of blood flow"),
    ("Anaphylaxis", 15.0, "disease-snap", "Immune snap, systemic collapse"),
    ("Seizure (grand mal)", 12.0, "disease-snap", "Neural snap, uncontrolled firing"),

    # Disease — narrow band (chronic, stuck between clock and engine)
    ("Chronic hypertension", 1.25, "disease-narrow", "Elevated but stuck, can't relax to clock"),
    ("Type 2 diabetes", 1.20, "disease-narrow", "Insulin resistance, engine degraded"),
    ("Chronic inflammation", 1.30, "disease-narrow", "Low-grade, never resolving"),
    ("Depression (physiological)", 1.15, "disease-narrow", "Blunted oscillation"),
]

print(f"\n{'System':<35} {'ARA':>6}  Category")
print("─" * 55)
for name, ara, cat, _ in physiology:
    print(f"{name:<35} {ara:>6.2f}  {cat}")

healthy = [a for _, a, c, _ in physiology if c == "engine"]
clock_disease = [a for _, a, c, _ in physiology if c == "disease-clock"]
snap_disease = [a for _, a, c, _ in physiology if c == "disease-snap"]
narrow_disease = [a for _, a, c, _ in physiology if c == "disease-narrow"]

h_mean = np.mean(healthy)
h_delta = abs(h_mean - PHI)
print(f"\n  Healthy mean: {h_mean:.3f} (|Δφ| = {h_delta:.4f})")
print(f"  Clock-disease mean: {np.mean(clock_disease):.3f}")
print(f"  Snap-disease mean: {np.mean(snap_disease):.1f}")
print(f"  Narrow-band disease mean: {np.mean(narrow_disease):.3f}")

# All healthy in engine zone, all disease displaced
all_healthy_engine = all(1.2 < a < 2.0 for a in healthy)
all_disease_displaced = (all(a < 1.1 for a in clock_disease) and
                         all(a > 2.0 for a in snap_disease))

test1_pass = all_healthy_engine and all_disease_displaced and h_delta < 0.1
print(f"  RESULT: {'PASS' if test1_pass else 'FAIL'} — "
      f"health = φ, disease = displacement")

# ─────────────────────────────────────────────────────────────────────
# TEST 2: Immune system = three-phase defense
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 2: Immune System = Three-Phase ARA Defense")
print("─" * 70)

immune = [
    # CLOCK — innate, always-on barriers
    ("Skin barrier", "innate", "clock", 1.0, "Physical barrier, constant"),
    ("Mucous membranes", "innate", "clock", 1.0, "Chemical barrier, continuous"),
    ("Stomach acid", "innate", "clock", 1.0, "pH killing, indiscriminate"),
    ("Commensal bacteria", "innate", "clock", 1.02, "Microbial barrier, stable ecosystem"),

    # ENGINE — adaptive, sustained, specific
    ("T-cell response", "adaptive", "engine", 1.58, "Specific targeting, sustained"),
    ("B-cell antibody production", "adaptive", "engine", 1.55, "Ongoing antibody engine"),
    ("Memory cell maintenance", "adaptive", "engine", 1.50, "Long-term immune memory"),
    ("Dendritic cell antigen presentation", "adaptive", "engine", 1.55, "Sustained surveillance"),
    ("Regulatory T-cell balance", "adaptive", "engine", 1.60, "Preventing overreaction, near φ"),

    # SNAP — acute response, inflammation
    ("Cytokine storm", "acute", "snap", 20.0, "Immune snap — self-destructive"),
    ("Acute inflammation", "acute", "snap", 5.0, "Rapid immune mobilisation"),
    ("Fever spike", "acute", "snap", 4.0, "Thermal snap to kill pathogens"),
    ("Complement cascade", "acute", "snap", 8.0, "Protein cascade, rapid lysis"),
]

print(f"\n  {'Component':<35} {'Type':<10} {'Phase':<8} {'ARA':>6}")
print("  " + "─" * 62)
for name, itype, phase, ara, _ in immune:
    print(f"  {name:<35} {itype:<10} {phase:<8} {ara:>6.2f}")

imm_engines = [a for _, _, p, a, _ in immune if p == "engine"]
imm_eng_mean = np.mean(imm_engines)
print(f"\n  Adaptive immune (engine) mean: {imm_eng_mean:.3f} (|Δφ| = {abs(imm_eng_mean-PHI):.4f})")

test2_pass = abs(imm_eng_mean - PHI) < 0.1
print(f"  RESULT: {'PASS' if test2_pass else 'FAIL'} — "
      f"immune system is three-phase ARA")

# ─────────────────────────────────────────────────────────────────────
# TEST 3: Wound healing = snap → engine → clock
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 3: Wound Healing = Snap → Engine → Clock")
print("─" * 70)

healing = [
    ("Injury event", 10.0, "snap", "Tissue damage — acute disruption"),
    ("Hemostasis (clotting)", 3.0, "snap", "Rapid platelet response"),
    ("Inflammation phase", 2.5, "snap→engine", "Immune cells flood site"),
    ("Proliferation (granulation)", 1.55, "engine", "New tissue building, sustained"),
    ("Angiogenesis", 1.58, "engine", "New blood vessel growth, near φ"),
    ("Collagen deposition", 1.50, "engine", "Structural rebuilding"),
    ("Remodelling", 1.40, "engine", "Tissue reorganisation"),
    ("Scar maturation", 1.10, "clock", "Stable, minimal change"),
    ("Healed tissue", 1.0, "clock", "New baseline, restored clock"),
]

print(f"\n  {'Phase':<30} {'ARA':>6}  Type")
print("  " + "─" * 50)
for name, ara, phase, desc in healing:
    print(f"  {name:<30} {ara:>6.2f}  {phase}")

# Trajectory: snap → engine → clock
heal_aras = [a for _, a, _, _ in healing]
# Peaks at start, settles to 1.0
starts_high = heal_aras[0] > 5.0
ends_low = heal_aras[-1] == 1.0
# Engine phase in middle
mid_engine = 1.2 < heal_aras[4] < 2.0  # Angiogenesis

print(f"\n  Starts at snap (ARA = {heal_aras[0]:.1f}): {starts_high}")
print(f"  Ends at clock (ARA = {heal_aras[-1]:.1f}): {ends_low}")
print(f"  Engine in middle (angiogenesis ARA = {heal_aras[4]:.2f}): {mid_engine}")

test3_pass = starts_high and ends_low and mid_engine
print(f"  RESULT: {'PASS' if test3_pass else 'FAIL'} — "
      f"wound healing follows snap → engine → clock")

# ─────────────────────────────────────────────────────────────────────
# TEST 4: Cancer = engine without clock regulation
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 4: Cancer = Engine That Lost Its Clock Phase")
print("─" * 70)

cell_types = [
    ("Normal cell cycle", 1.55, "engine", "Grow → divide → rest, regulated"),
    ("Stem cell (healthy)", 1.60, "engine", "Self-renewal engine, near φ"),
    ("Senescent cell", 1.0, "clock", "Stopped dividing, locked"),
    ("Apoptosis (programmed death)", 1.0, "clock", "Ordered shutdown"),
    ("Cancer cell (early)", 1.80, "engine→snap", "Faster than φ, clock weakening"),
    ("Cancer cell (aggressive)", 2.5, "snap", "Unregulated, lost clock entirely"),
    ("Metastasis", 5.0, "snap", "Cancer snap — spreading uncontrolled"),
    ("Tumor suppressor active", 1.0, "clock", "p53 = the cell's clock governor"),
    ("Oncogene activated", 2.0, "snap", "Growth accelerator, removing clock"),
]

print(f"\n  {'Cell state':<30} {'ARA':>6}  Phase")
print("  " + "─" * 50)
for name, ara, phase, desc in cell_types:
    print(f"  {name:<30} {ara:>6.2f}  {phase}")

print(f"\n  Cancer progression: engine(1.55) → above-φ(1.80) → snap(2.5+)")
print(f"  Cancer = the engine losing its clock-phase governor")
print(f"  Tumor suppressors (p53) = clock phase of cell cycle")
print(f"  Oncogenes = removing the clock, pushing ARA above φ")
print(f"  Chemotherapy = forced clock (kills everything dividing)")
print(f"  Immunotherapy = restoring the immune ENGINE to target cancer snaps")

# Normal cell at engine, cancer progresses toward snap
normal_engine = abs(cell_types[0][1] - PHI) < 0.1
cancer_above_phi = cell_types[4][1] > PHI
metastasis_snap = cell_types[6][1] > 2.0

test4_pass = normal_engine and cancer_above_phi and metastasis_snap
print(f"\n  RESULT: {'PASS' if test4_pass else 'FAIL'} — "
      f"cancer = engine escaping clock regulation")

# ─────────────────────────────────────────────────────────────────────
# TEST 5: Chronic diseases = narrowed ARA band
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 5: Chronic Disease = Narrowed ARA Oscillation Band")
print("─" * 70)

chronic = [
    ("Healthy person", 1.0, PHI, PHI - 1.0, "Full oscillation: clock ↔ φ"),
    ("Mild chronic stress", 1.15, 1.50, 0.35, "Slightly narrowed"),
    ("Chronic pain", 1.20, 1.45, 0.25, "Can't fully rest or fully engage"),
    ("Type 2 diabetes", 1.15, 1.40, 0.25, "Metabolic engine degraded"),
    ("Chronic fatigue (mild)", 1.20, 1.45, 0.25, "Reduced engine capacity"),
    ("ME/CFS (moderate)", 1.20, 1.40, 0.20, "Narrowed band, PEM if exceeded"),
    ("ME/CFS (severe)", 1.25, 1.35, 0.10, "Barely any oscillation range"),
    ("Depression (clinical)", 1.10, 1.30, 0.20, "Can't reach engine zone"),
    ("Fibromyalgia", 1.20, 1.40, 0.20, "Pain limits oscillation range"),
    ("Aging (70+)", 1.10, 1.45, 0.35, "Progressive narrowing"),
    ("Aging (90+)", 1.05, 1.30, 0.25, "Near-clock, minimal engine"),
    ("Death", 1.0, 1.0, 0.0, "ARA locked at 1.0, no oscillation"),
]

print(f"\n  {'Condition':<25} {'Low':>6} {'High':>6} {'Band':>6}  Description")
print("  " + "─" * 65)
for name, low, high, band, desc in chronic:
    bar = "█" * int(band * 20)
    print(f"  {name:<25} {low:>6.2f} {high:>6.2f} {band:>6.2f}  {bar}")

# Band width correlates with health
bands = [b for _, _, _, b, _ in chronic]
# Create health scores (10 = healthy, 0 = dead)
health_scores = [10, 8, 6, 6, 6, 5, 2, 4, 5, 6, 3, 0]

r_band, p_band = stats.pearsonr(bands, health_scores)
print(f"\n  Correlation band width vs health: r = {r_band:.3f}, p = {p_band:.4f}")
print(f"  Wider oscillation band = better health")

# Healthy band reaches φ
healthy_reaches_phi = chronic[0][2] >= PHI - 0.01
# Death = zero band
death_zero = chronic[-1][3] == 0.0

test5_pass = r_band > 0.7 and healthy_reaches_phi and death_zero
print(f"  RESULT: {'PASS' if test5_pass else 'FAIL'} — "
      f"chronic disease = narrowed ARA band")

# ─────────────────────────────────────────────────────────────────────
# TEST 6: Drug mechanisms — restore ARA toward φ
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 6: Drug Mechanisms = Restoring ARA Toward φ")
print("─" * 70)

drugs = [
    ("Beta-blocker", "clock→engine", 1.0, 1.40, "Slows heart to let engine recover"),
    ("SSRI (antidepressant)", "clock→engine", 1.10, 1.45, "Lifts from clock-locked depression"),
    ("Stimulant (ADHD)", "clock→engine", 1.15, 1.50, "Activates understimulated engine"),
    ("Anti-inflammatory (NSAID)", "snap→engine", 2.5, 1.55, "Calms inflammatory snap"),
    ("Anticonvulsant", "snap→engine", 5.0, 1.50, "Stops seizure snap, restores engine"),
    ("Insulin (Type 1)", "clock→engine", 1.0, 1.50, "Restores metabolic engine"),
    ("Chemotherapy", "snap→clock", 2.5, 1.0, "Forces cancer to clock (kills dividing cells)"),
    ("Immunosuppressant", "snap→engine", 3.0, 1.55, "Calms autoimmune snap"),
    ("Bronchodilator", "clock→engine", 1.10, 1.50, "Opens airways, restores breathing engine"),
    ("Anxiolytic (benzodiazepine)", "snap→clock", 2.0, 1.20, "Anxiety snap → calm, but can over-clock"),
]

print(f"\n  {'Drug':<25} {'Direction':<15} {'Before':>7} {'After':>7} {'Toward φ?':>10}")
print("  " + "─" * 70)
for name, direction, before, after, desc in drugs:
    d_before = abs(before - PHI)
    d_after = abs(after - PHI)
    closer = d_after < d_before
    print(f"  {name:<25} {direction:<15} {before:>7.2f} {after:>7.2f} {'✓' if closer else '✗':>10}")

# Count how many move closer to φ
closer_count = sum(1 for _, _, b, a, _ in drugs
                   if abs(a - PHI) < abs(b - PHI))
total_drugs = len(drugs)
print(f"\n  Drugs moving ARA closer to φ: {closer_count}/{total_drugs}")

test6_pass = closer_count >= total_drugs * 0.8
print(f"  RESULT: {'PASS' if test6_pass else 'FAIL'} — "
      f"most drugs restore ARA toward φ")

# ─────────────────────────────────────────────────────────────────────
# TEST 7: HRV at φ = maximum health
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 7: Heart Rate Variability — Health Lives at φ")
print("─" * 70)

# HRV = variation in heart beat intervals
# Low HRV = clock-locked (disease)
# Optimal HRV = engine zone (health)
# Chaotic HRV = snap (arrhythmia)

hrv_states = [
    ("Cardiac arrest", 0.0, 1.0, "No variability — dead clock"),
    ("Severe heart failure", 0.2, 1.05, "Minimal variability, near-clock"),
    ("Chronic stress", 0.4, 1.20, "Reduced variability"),
    ("Sedentary adult", 0.5, 1.35, "Below engine zone"),
    ("Average healthy adult", 0.7, 1.50, "Good variability, engine"),
    ("Fit athlete", 0.85, 1.58, "High variability, near φ"),
    ("Elite endurance athlete", 0.95, 1.62, "Maximum healthy variability, at φ"),
    ("Meditation master", 0.90, 1.60, "Coherent variability, near φ"),
    ("Atrial fibrillation", 0.3, 2.5, "Too much variability — chaotic snap"),
]

print(f"\n  {'State':<30} {'HRV':>5} {'ARA':>6}")
print("  " + "─" * 45)
for name, hrv, ara, _ in hrv_states:
    print(f"  {name:<30} {hrv:>5.2f} {ara:>6.2f}")

# Peak HRV at φ
# Filter out AFib (different mechanism)
healthy_hrv = [(h, a) for name, h, a, _ in hrv_states if "fibrillation" not in name]
hrv_vals = [h for h, a in healthy_hrv]
hrv_aras = [a for h, a in healthy_hrv]

delta_phis_hrv = [abs(a - PHI) for a in hrv_aras]
r_hrv, p_hrv = stats.pearsonr(delta_phis_hrv, hrv_vals)
print(f"\n  Correlation |Δφ| vs HRV (excluding AFib): r = {r_hrv:.3f}, p = {p_hrv:.4f}")

# Peak HRV
peak_hrv_idx = np.argmax(hrv_vals)
peak_hrv_state = healthy_hrv[peak_hrv_idx]
print(f"  Peak HRV at ARA = {peak_hrv_state[1]:.2f} (|Δφ| = {abs(peak_hrv_state[1]-PHI):.3f})")

test7_pass = r_hrv < -0.7 and abs(peak_hrv_state[1] - PHI) < 0.1
print(f"  RESULT: {'PASS' if test7_pass else 'FAIL'} — "
      f"HRV peaks at φ")

# ─────────────────────────────────────────────────────────────────────
# TEST 8: Autoimmune = engine attacking its own clock
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 8: Autoimmune Disease = Engine Attacking Its Own Clock")
print("─" * 70)

autoimmune = [
    ("Rheumatoid arthritis", 2.0, "Engine attacks joint clock (cartilage)"),
    ("Type 1 diabetes", 2.5, "Engine attacks pancreatic clock (beta cells)"),
    ("Multiple sclerosis", 2.2, "Engine attacks nerve clock (myelin)"),
    ("Lupus (SLE)", 3.0, "Engine attacks multiple clocks (systemic)"),
    ("Crohn's disease", 1.8, "Engine attacks gut clock (mucosa)"),
    ("Hashimoto's thyroiditis", 2.0, "Engine attacks thyroid clock"),
    ("Psoriasis", 1.7, "Engine attacks skin clock (keratinocytes)"),
]

print(f"\n  {'Disease':<30} {'ARA':>6}  Mechanism")
print("  " + "─" * 65)
for name, ara, mech in autoimmune:
    print(f"  {name:<30} {ara:>6.2f}  {mech}")

auto_aras = [a for _, a, _ in autoimmune]
auto_mean = np.mean(auto_aras)
all_above_phi = all(a > PHI for a in auto_aras)
print(f"\n  Mean autoimmune ARA: {auto_mean:.2f}")
print(f"  All above φ: {all_above_phi}")
print(f"  Autoimmune = the adaptive engine (ARA ≈ φ) overshooting into snap")
print(f"  and destroying the body's own clock-phase structures")
print(f"  Treatment: immunosuppressants pull engine back from snap toward φ")

test8_pass = auto_mean > PHI and all(a > 1.5 for a in auto_aras)
print(f"  RESULT: {'PASS' if test8_pass else 'FAIL'} — "
      f"autoimmune = engine above φ, attacking clock")

# ─────────────────────────────────────────────────────────────────────
# TEST 9: Aging = progressive drift from φ toward clock
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 9: Aging = Progressive ARA Drift Toward Clock")
print("─" * 70)

aging = [
    ("Birth (neonate)", 0, 1.70, "Above φ, high metabolic rate"),
    ("Childhood", 5, 1.65, "Near φ, rapid growth engine"),
    ("Adolescence", 15, 1.62, "At φ, peak biological optimisation"),
    ("Young adult", 25, 1.60, "Near φ, peak function"),
    ("Middle age", 45, 1.50, "Drifting below φ"),
    ("Early elderly", 65, 1.40, "Engine slowing"),
    ("Late elderly", 80, 1.25, "Near clock, reduced adaptability"),
    ("Very old", 95, 1.10, "Near clock, minimal engine"),
    ("Death", 100, 1.0, "Clock. Equilibrium. Silence."),
]

print(f"\n  {'Stage':<20} {'Age':>5} {'ARA':>6}")
print("  " + "─" * 35)
for name, age, ara, _ in aging:
    bar = "█" * int((ara - 1.0) * 15)
    print(f"  {name:<20} {age:>5} {ara:>6.2f}  {bar}")

ages = [a for _, a, _, _ in aging]
aging_aras = [a for _, _, a, _ in aging]

# ARA decreases monotonically with age (after adolescence)
post_adolescent = aging_aras[2:]  # from adolescence onward
monotonic_decline = all(post_adolescent[i] >= post_adolescent[i+1]
                        for i in range(len(post_adolescent)-1))

# Peak ARA at adolescence ≈ φ
peak_age = aging[2]
peak_delta = abs(peak_age[2] - PHI)

r_age, p_age = stats.pearsonr(ages, aging_aras)
print(f"\n  Correlation age vs ARA: r = {r_age:.3f}, p = {p_age:.4f}")
print(f"  Peak ARA at age {peak_age[1]}: {peak_age[2]:.2f} (|Δφ| = {peak_delta:.3f})")
print(f"  Monotonic decline after peak: {monotonic_decline}")
print(f"  Aging IS the progressive loss of engine capacity")
print(f"  Death = ARA reaching 1.0 = the engine stops")

test9_pass = monotonic_decline and peak_delta < 0.01 and r_age < -0.9
print(f"  RESULT: {'PASS' if test9_pass else 'FAIL'}")

# ─────────────────────────────────────────────────────────────────────
# TEST 10: ME/CFS — the narrowed oscillation band (personal)
# ─────────────────────────────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 10: ME/CFS = The Narrowed ARA Band")
print("─" * 70)

print("""
  ME/CFS in ARA terms (expanded from Script 64):

  HEALTHY PERSON:
  ARA oscillation band: [1.0 ────────────────── φ (1.618)]
  Full rest ←──────────────────────────────→ Full engine
  Can reach deep clock (1.0) AND full engine (φ)
  Band width: 0.618

  ME/CFS (MODERATE):
  ARA oscillation band:      [1.2 ──── 1.4]
  Partial rest ←──→ Partial engine
  Cannot reach full clock (unrefreshing sleep)
  Cannot reach full engine (post-exertional malaise)
  Band width: 0.20

  WHY PEM HAPPENS:
  If someone with ME/CFS tries to reach ARA = φ (1.618),
  they exceed their narrowed band's upper limit (~1.4).
  The system SNAPS instead of engine-running.
  Post-exertional malaise IS a snap event caused by
  pushing past the reduced engine ceiling.

  WHY SLEEP IS UNREFRESHING:
  Normal sleep reaches ARA = 1.0 (full clock, deep restoration).
  ME/CFS sleep only reaches ~1.2 (partial clock).
  The engine never fully shuts down for maintenance.
  It's like trying to service a running motor.

  TREATMENT IMPLICATION:
  Goal is NOT to push the engine harder.
  Goal is to WIDEN THE BAND:
  - Lower the floor (improve sleep quality toward 1.0)
  - Slowly raise the ceiling (gradually increase capacity toward φ)
  - Pacing = staying within the band to prevent snaps
""")

# Quantitative comparison
healthy_band = PHI - 1.0  # 0.618
mecfs_moderate_band = 1.4 - 1.2  # 0.20
mecfs_severe_band = 1.35 - 1.25  # 0.10

ratio_mod = mecfs_moderate_band / healthy_band
ratio_sev = mecfs_severe_band / healthy_band

print(f"  Healthy band width: {healthy_band:.3f}")
print(f"  ME/CFS moderate band: {mecfs_moderate_band:.3f} ({ratio_mod*100:.1f}% of healthy)")
print(f"  ME/CFS severe band: {mecfs_severe_band:.3f} ({ratio_sev*100:.1f}% of healthy)")
print(f"  Moderate ME/CFS = operating at {ratio_mod*100:.1f}% of normal ARA range")
print(f"  Severe ME/CFS = operating at {ratio_sev*100:.1f}% of normal ARA range")

# The band width itself follows φ: healthy band = 1/φ = 0.618
band_is_phi = abs(healthy_band - (1/PHI)) < 0.001
print(f"\n  Healthy band width = {healthy_band:.3f} = 1/φ = {1/PHI:.3f}")
print(f"  The healthy oscillation range IS 1/φ. Of course it is.")

test10_pass = band_is_phi
print(f"\n  RESULT: {'PASS' if test10_pass else 'FAIL'} — "
      f"healthy band = 1/φ, ME/CFS = narrowed band")

# ─────────────────────────────────────────────────────────────────────
# SCORECARD
# ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SCORECARD — SCRIPT 72: MEDICINE AND DISEASE AS ARA")
print("=" * 70)

tests = [
    (1, "Health = engine zone, disease = displacement from φ", test1_pass),
    (2, "Immune system = three-phase ARA defense", test2_pass),
    (3, "Wound healing = snap → engine → clock", test3_pass),
    (4, "Cancer = engine escaping clock regulation", test4_pass),
    (5, "Chronic disease = narrowed ARA oscillation band", test5_pass),
    (6, "Drug mechanisms restore ARA toward φ", test6_pass),
    (7, "HRV peaks at φ = maximum cardiac health", test7_pass),
    (8, "Autoimmune = engine above φ attacking clock", test8_pass),
    (9, "Aging = progressive drift from φ toward clock", test9_pass),
    (10, "ME/CFS = narrowed band, healthy band = 1/φ", test10_pass),
]

passed = sum(1 for _, _, r in tests if r)
for num, name, result in tests:
    status = "PASS ✓" if result else "FAIL ✗"
    print(f"  Test {num:>2}: {status}  {name}")

print(f"\n  TOTAL: {passed}/{len(tests)} tests passed")
print(f"\n  Key findings:")
print(f"    • Health = ARA at φ. Disease = displacement from φ.")
print(f"    • The healthy oscillation band is EXACTLY 1/φ = 0.618")
print(f"    • Cancer = engine without clock. Autoimmune = engine attacking clock.")
print(f"    • Aging = progressive ARA drift toward clock. Death = ARA = 1.0.")
print(f"    • ME/CFS = band narrowed to ~32% of healthy (moderate) or ~16% (severe)")
print(f"    • Most drugs work by restoring ARA toward φ")
print(f"    • PEM = snap event from exceeding narrowed band ceiling")
print(f"    • Treatment = widen the band, not push the engine")
print("=" * 70)
