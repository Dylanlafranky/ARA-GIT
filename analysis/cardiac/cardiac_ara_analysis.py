"""
Cardiac ARA Analysis — Blind Prediction Test
=============================================
Decompose the human heart into 8 coupled subsystems.
Compute ARA ratios from standard cardiology phase durations.
Make failure-mode predictions based ONLY on ARA theory.
Then validate against known cardiac pathology.

Data sources: Standard resting HR = 72 bpm (cycle = 833ms)
Phase durations from Guyton's Medical Physiology, Braunwald's Heart Disease,
and standard ECG/hemodynamic reference values.
"""

import json

# ============================================================
# STEP 1: Define subsystems with phase durations
# ============================================================

# At resting HR = 72 bpm, cardiac cycle = 833 ms
CYCLE_MS = 833

subsystems = {
    "SA Node (Pacemaker)": {
        "description": "Sinoatrial node — the heart's natural pacemaker",
        "accumulation_label": "Phase 4: slow diastolic depolarization",
        "release_label": "Phase 0: rapid upstroke + repolarization",
        "T_accumulation_ms": 750,  # slow drift to threshold
        "T_release_ms": 80,        # rapid firing + reset
        "source": "Guyton Ch.10; SA node action potential morphology",
        "notes": "Calcium-channel mediated upstroke (slower than ventricular sodium). Free-running, no external clock."
    },
    "AV Node (Conduction Gate)": {
        "description": "Atrioventricular node — delays signal to synchronise atria/ventricles",
        "accumulation_label": "AV nodal delay (AH interval)",
        "release_label": "His-Purkinje transmission (HV interval)",
        "T_accumulation_ms": 90,   # AH interval ~50-120ms, typical ~90ms
        "T_release_ms": 45,        # HV interval ~35-55ms, typical ~45ms
        "source": "Braunwald Ch.35; intracardiac electrophysiology (AH/HV intervals)",
        "notes": "Functions as a gate. Holds signal (AV delay), then transmits via fast His-Purkinje system."
    },
    "Atrial Mechanical (Atrial Kick)": {
        "description": "Atrial filling from veins → contraction into ventricles",
        "accumulation_label": "Passive + active venous filling",
        "release_label": "Atrial contraction (the 'kick')",
        "T_accumulation_ms": 730,  # atria fill most of the cycle
        "T_release_ms": 100,       # atrial systole ~100ms
        "source": "Guyton Ch.9; atrial pressure waveform",
        "notes": "Long fill, short snap. Contributes ~20-30% of ventricular filling."
    },
    "Ventricular Pump (Ejection)": {
        "description": "Ventricular filling → ejection cycle — the main pump",
        "accumulation_label": "Diastolic filling (passive + atrial kick)",
        "release_label": "Systolic ejection",
        "T_accumulation_ms": 530,  # diastole
        "T_release_ms": 300,       # systole (isovolumetric contraction + ejection)
        "source": "Guyton Ch.9; Wiggers diagram",
        "notes": "The core pump cycle. Blood accumulates, then is ejected."
    },
    "Ventricular Myocyte (Muscle)": {
        "description": "Cardiac muscle cell contraction and relaxation cycle",
        "accumulation_label": "Contraction (tension/force generation)",
        "release_label": "Relaxation (lusitropy, calcium reuptake)",
        "T_accumulation_ms": 300,  # systolic contraction
        "T_release_ms": 530,       # diastolic relaxation
        "source": "Braunwald Ch.21; myocardial mechanics",
        "notes": "The muscle itself: fast tension buildup, slow relaxation. An engine."
    },
    "Coronary Perfusion": {
        "description": "Blood supply to the heart muscle itself",
        "accumulation_label": "Systolic compression (coronaries squeezed, O₂ debt builds)",
        "release_label": "Diastolic flow (coronaries open, O₂ delivered)",
        "T_accumulation_ms": 300,  # systole — coronaries compressed by contracting muscle
        "T_release_ms": 530,       # diastole — 70-80% of coronary flow occurs here
        "source": "Guyton Ch.21; coronary flow physiology",
        "notes": "Heart feeds itself during relaxation. Oxygen debt accumulates during contraction."
    },
    "Ventricular Action Potential (Electrical)": {
        "description": "Electrical depolarisation-repolarisation cycle of ventricular myocytes",
        "accumulation_label": "Recovery / resting (Phase 4, ion gradient restoration)",
        "release_label": "Action potential (Phases 0-3, QT interval)",
        "T_accumulation_ms": 470,  # Phase 4 resting interval (833ms - ~360ms QT)
        "T_release_ms": 360,       # QT interval ~360-400ms at 72bpm (corrected from literature)
        "source": "Braunwald Ch.33; QT interval physiology",
        "notes": "Ion pumps restore gradients (accumulate Phase 4), then sodium/calcium channels fire (release Phases 0-3)."
    },
    "Respiratory Sinus Arrhythmia (Coupling)": {
        "description": "Heart rate modulation locked to breathing cycle",
        "accumulation_label": "Inspiration (HR accelerates, vagal withdrawal)",
        "release_label": "Expiration (HR decelerates, vagal return)",
        "T_accumulation_ms": 1800,  # inspiration ~1.8s at rest
        "T_release_ms": 2900,       # expiration ~2.9s at rest (from breath ARA data)
        "source": "NeuroKit2 dataset; respiratory physiology",
        "notes": "The cardiac-respiratory bridge. Operates at breathing timescale, not heartbeat timescale."
    }
}

# ============================================================
# STEP 2: Compute ARA ratios
# ============================================================

print("=" * 80)
print("CARDIAC ARA ANALYSIS — BLIND PREDICTION TEST")
print("=" * 80)
print(f"\nResting HR: 72 bpm | Cycle: {CYCLE_MS} ms")
print(f"Subsystems: {len(subsystems)}")
print()

PHI = 1.6180339887

results = {}
for name, data in subsystems.items():
    ara = data["T_release_ms"] / data["T_accumulation_ms"]

    # Classify on ARA scale
    if ara < 0.15:
        classification = "Extreme snap (trigger)"
        zone = "trigger"
    elif ara < 0.4:
        classification = "Consumer snap"
        zone = "consumer_snap"
    elif ara < 0.8:
        classification = "Consumer"
        zone = "consumer"
    elif 0.8 <= ara < 1.15:
        classification = "Pacemaker / forced symmetry"
        zone = "pacemaker"
    elif 1.15 <= ara < 1.45:
        classification = "Shock absorber / managed"
        zone = "managed"
    elif 1.45 <= ara < 1.75:
        classification = "Sustained engine (φ zone)"
        zone = "phi"
    elif 1.75 <= ara < 2.0:
        classification = "Exothermic source"
        zone = "exothermic"
    else:
        classification = "Beyond scale"
        zone = "extreme"

    phi_deviation = abs(ara - PHI) / PHI * 100

    results[name] = {
        **data,
        "ARA": round(ara, 3),
        "classification": classification,
        "zone": zone,
        "phi_deviation": round(phi_deviation, 1)
    }

# Print results table
print(f"{'Subsystem':<45} {'T_acc':>6} {'T_rel':>6} {'ARA':>7} {'Classification':<30}")
print("-" * 100)
for name, r in results.items():
    print(f"{name:<45} {r['T_accumulation_ms']:>5}ms {r['T_release_ms']:>5}ms {r['ARA']:>7.3f} {r['classification']:<30}")

# ============================================================
# STEP 3: BLIND PREDICTIONS (from ARA theory alone)
# ============================================================

print("\n" + "=" * 80)
print("BLIND PREDICTIONS — Based only on ARA theory")
print("=" * 80)

predictions = {
    "SA Node (Pacemaker)": {
        "ARA": results["SA Node (Pacemaker)"]["ARA"],
        "prediction": (
            "EXTREME SNAP (ARA = 0.107). This is a trigger — long accumulation, "
            "near-instantaneous release. ARA theory predicts:\n"
            "  1. If ARA increases (release slows), the trigger becomes unreliable/sluggish\n"
            "  2. If the trigger couples to another oscillator at a rational ratio,\n"
            "     expect frequency-locking (the trigger fires at integer multiples instead of freely)\n"
            "  3. Complete failure = ARA → 0 (accumulates forever, never fires)"
        )
    },
    "AV Node (Conduction Gate)": {
        "ARA": results["AV Node (Conduction Gate)"]["ARA"],
        "prediction": (
            "CONSUMER (ARA = 0.500). A gate — holds signal (90ms AV delay), transmits (45ms HV).\n"
            "  1. If ARA increases (delay lengthens disproportionately), signals arrive late.\n"
            "     The gate becomes progressively leakier.\n"
            "  2. CRITICAL: The AV node sits between two oscillators (atria above, ventricles below).\n"
            "     If the atrial rate exceeds the node's recovery time, the node can only pass\n"
            "     every 2nd, 3rd, or Nth impulse — INTEGER CONDUCTION RATIOS (2:1, 3:1).\n"
            "     This is the canonical ARA resonance-destruction prediction.\n"
            "  3. Complete failure = gate blocks everything. Signal chain breaks, oscillators decouple."
        )
    },
    "Atrial Mechanical (Atrial Kick)": {
        "ARA": results["Atrial Mechanical (Atrial Kick)"]["ARA"],
        "prediction": (
            "CONSUMER SNAP (ARA = 0.137). Long slow fill, fast contraction.\n"
            "  1. If ARA approaches 1.0 (fill time ≈ contraction time), the organized\n"
            "     snap degrades into disorganized motion — the chamber can't complete\n"
            "     either phase cleanly\n"
            "  2. Multiple competing wavefronts could emerge if the single organized\n"
            "     contraction fragments\n"
            "  3. Loss of the snap = loss of the 'kick' contribution to downstream filling"
        )
    },
    "Ventricular Pump (Ejection)": {
        "ARA": results["Ventricular Pump (Ejection)"]["ARA"],
        "prediction": (
            "CONSUMER (ARA = 0.566). Moderate asymmetry — fills longer than it ejects.\n"
            "  1. If ARA decreases (ejection weakens relative to filling), output drops\n"
            "  2. If ARA increases toward 1.0 (systole lengthens OR diastole shortens),\n"
            "     filling time is compressed — the pump starves itself\n"
            "  3. Since this subsystem is coupled to coronary perfusion (which also needs\n"
            "     diastole), anything that shortens diastole cascades into oxygen debt"
        )
    },
    "Ventricular Myocyte (Muscle)": {
        "ARA": results["Ventricular Myocyte (Muscle)"]["ARA"],
        "prediction": (
            "EXOTHERMIC SOURCE (ARA = 1.767). Fast contraction, slow relaxation — an engine.\n"
            "  1. If ARA decreases toward 1.0 (relaxation time shortens), the muscle\n"
            "     can't fully relax between contractions — it stiffens\n"
            "  2. A stiffened muscle changes the pump's filling dynamics (coupled to\n"
            "     ventricular pump ARA)\n"
            "  3. If the muscle thickens (hypertrophies), relaxation takes even longer,\n"
            "     potentially pushing ARA > 2.0 into resonant instability"
        )
    },
    "Coronary Perfusion": {
        "ARA": results["Coronary Perfusion"]["ARA"],
        "prediction": (
            "EXOTHERMIC SOURCE (ARA = 1.767). Oxygen debt builds during contraction,\n"
            "delivered during relaxation.\n"
            "  1. If ARA decreases (diastole shortens), O₂ delivery drops below demand.\n"
            "     The heart literally starves itself during fast rates.\n"
            "  2. CRITICAL CASCADE: Coronary perfusion shares its release phase with\n"
            "     ventricular myocyte relaxation. Anything that shortens diastole hits BOTH\n"
            "     subsystems simultaneously — double failure mode.\n"
            "  3. If coronary vessels narrow (reducing flow rate), the system needs MORE\n"
            "     diastolic time to deliver the same O₂ — but can't get it at high HR."
        )
    },
    "Ventricular Action Potential (Electrical)": {
        "ARA": results["Ventricular Action Potential (Electrical)"]["ARA"],
        "prediction": (
            "CONSUMER (ARA = 0.766). Ion gradients restore during Phase 4 (~470ms),\n"
            "  then discharge during the action potential (~360ms QT interval).\n"
            "  1. If release lengthens (APD prolongation, ARA increases), the refractory\n"
            "     window extends — the next cycle's accumulation starts before the previous\n"
            "     release finishes. The wavefront can meet itself.\n"
            "  2. A wavefront meeting itself = re-entrant circuit = self-sustaining\n"
            "     rotational electrical activity\n"
            "  3. If multiple re-entrant circuits form simultaneously, organized rhythm\n"
            "     degrades into electrical chaos"
        )
    },
    "Respiratory Sinus Arrhythmia (Coupling)": {
        "ARA": results["Respiratory Sinus Arrhythmia (Coupling)"]["ARA"],
        "prediction": (
            "φ ZONE (ARA = 1.611). Within 0.4% of phi. The MOST STABLE subsystem.\n"
            "  1. This is the golden ratio coupling — maximally non-resonant. ARA theory\n"
            "     predicts this is the LAST subsystem to fail.\n"
            "  2. Loss of this φ-coupling (ARA → 1.0, rigid symmetry) should be a\n"
            "     UNIVERSAL EARLY WARNING of system-wide cardiac degradation\n"
            "  3. The variability itself IS the health signal. Reduction in beat-to-beat\n"
            "     variation = movement away from φ = approaching resonant lock-in.\n"
            "  4. This should be the single strongest predictor of cardiac mortality."
        )
    }
}

for name, pred in predictions.items():
    print(f"\n{'─' * 60}")
    print(f"  {name} (ARA = {pred['ARA']})")
    print(f"{'─' * 60}")
    print(f"  {pred['prediction']}")

# ============================================================
# STEP 4: Define coupling network
# ============================================================

print("\n" + "=" * 80)
print("COUPLING NETWORK")
print("=" * 80)

couplings = [
    ("SA Node (Pacemaker)", "AV Node (Conduction Gate)", "Electrical trigger → gate", "strong"),
    ("SA Node (Pacemaker)", "Atrial Mechanical (Atrial Kick)", "Trigger → contraction", "strong"),
    ("AV Node (Conduction Gate)", "Ventricular Pump (Ejection)", "Gate → pump timing", "strong"),
    ("AV Node (Conduction Gate)", "Ventricular Action Potential (Electrical)", "Gate → electrical activation", "strong"),
    ("Ventricular Action Potential (Electrical)", "Ventricular Myocyte (Muscle)", "Electrical → mechanical", "strong"),
    ("Ventricular Myocyte (Muscle)", "Ventricular Pump (Ejection)", "Muscle force → ejection", "strong"),
    ("Ventricular Pump (Ejection)", "Coronary Perfusion", "Pump pressure → coronary compression", "strong"),
    ("Coronary Perfusion", "Ventricular Myocyte (Muscle)", "O₂ delivery → muscle function", "strong"),
    ("Ventricular Myocyte (Muscle)", "Coronary Perfusion", "Contraction → coronary squeeze", "moderate"),
    ("Respiratory Sinus Arrhythmia (Coupling)", "SA Node (Pacemaker)", "Vagal modulation → pacemaker rate", "moderate"),
    ("Atrial Mechanical (Atrial Kick)", "Ventricular Pump (Ejection)", "Atrial kick → ventricular preload", "moderate"),
    ("Ventricular Pump (Ejection)", "Respiratory Sinus Arrhythmia (Coupling)", "Cardiac output → baroreflex → RSA", "weak"),
]

for src, dst, label, strength in couplings:
    print(f"  [{strength:>8}] {src:<45} → {dst}")
    print(f"           {label}")

# ============================================================
# STEP 5: Summary statistics
# ============================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

ara_values = [r["ARA"] for r in results.values()]
phi_hits = [name for name, r in results.items() if r["phi_deviation"] < 5]
extreme_snaps = [name for name, r in results.items() if r["ARA"] < 0.15]
consumers = [name for name, r in results.items() if 0.15 <= r["ARA"] < 0.8]
engines = [name for name, r in results.items() if 1.45 <= r["ARA"] < 2.0]

print(f"  ARA range: {min(ara_values):.3f} – {max(ara_values):.3f}")
print(f"  φ-zone hits (within 5%): {len(phi_hits)} — {', '.join(phi_hits)}")
print(f"  Extreme snaps (< 0.15): {len(extreme_snaps)} — {', '.join(extreme_snaps)}")
print(f"  Consumers (0.15-0.8): {len(consumers)} — {', '.join(consumers)}")
print(f"  Engines/Sources (1.45-2.0): {len(engines)} — {', '.join(engines)}")

# Output JSON for HTML consumption
output = {
    "subsystems": {k: {
        "ARA": v["ARA"],
        "classification": v["classification"],
        "zone": v["zone"],
        "T_acc": v["T_accumulation_ms"],
        "T_rel": v["T_release_ms"],
        "phi_dev": v["phi_deviation"]
    } for k, v in results.items()},
    "predictions": {k: v["prediction"] for k, v in predictions.items()}
}

with open("cardiac_ara_results.json", "w") as f:
    json.dump(output, f, indent=2)

print("\nResults saved to cardiac_ara_results.json")
print("\n✓ Analysis complete. Ready for validation against known cardiology.")
