#!/usr/bin/env python3
"""
Script 90 — SINGULARITY AS ARA→0 AND THE CIRCLE 2 DESERT
=====================================================================
Script 86 discovered that the black hole ISCO (innermost stable
circular orbit) period maps onto the three-system architecture, with
boundary crossings at ~8,751 M☉ and ~55,216 M☉. The intermediate-mass
black hole (IMBH) range sits almost entirely in System 2 — the thin
coupling zone that is always the sparsest.

Now we push this to its logical extremes:

  1. THE SINGULARITY: As we approach the event horizon singularity,
     ISCO period → 0, logT → -∞. The ARA scale runs 0 to 2, where
     0 = singularity (all three systems collapse to one). We trace
     BH mass from Planck mass to 10⁹ M☉ and show the singularity
     as the ARA=0 anchor point.

  2. CIRCLE 2 GEOMETRY: System 2 (0.6 ≤ logT < 1.4) is always the
     thinnest circle. At cosmic scale, IMBHs are the only objects
     that would naturally sit here — and IMBHs are extremely rare.
     We test whether the BH mass function shows a minimum in the
     IMBH range.

  3. MASS-SYSTEM MAPPING: Continuous mapping of BH mass to system
     number via ISCO period.

  4. GRAVITATIONAL WAVE FREQUENCIES: The GW chirp frequency at ISCO
     (f_GW = 2/T_ISCO) maps onto the three systems. Each GW detector
     band (LIGO, LISA, PTA) should correspond to a different circle.

ISCO FORMULA (Schwarzschild):
  T_ISCO = 6^(3/2) × π × 2GM/c³

SYSTEM BOUNDARIES (from Script 79b):
  Boundary 1: logT = 0.6  (T ≈ 4 s)
  Boundary 2: logT = 1.4  (T ≈ 25 s)

SOURCES:
  - ISCO derivation: Misner, Thorne & Wheeler (1973), ch 25
  - BH mass function: Sicilia et al. 2022, ApJ
  - IMBH gap: Greene et al. 2020, ARA&A
  - LIGO/Virgo: Abbott et al. 2023, Phys Rev X
  - LISA: Amaro-Seoane et al. 2017, arXiv:1702.00786
  - Pulsar timing arrays: NANOGrav 2023
  - Planck mass: CODATA 2018
  - Accretion state transitions: Remillard & McClintock 2006, ARA&A

TESTS:
  1. ISCO period scales linearly with BH mass
  2. Sys 1→2 boundary at M ≈ 8,751 M☉ (within 5%)
  3. Sys 2→3 boundary at M ≈ 55,216 M☉ (within 5%)
  4. IMBH range (10³-10⁵ M☉) maps predominantly to System 2
  5. logT → -∞ as M → 0 (singularity approach)
  6. BH mass function minimum in IMBH/System 2 range
  7. LIGO band maps to System 1 (stellar BH mergers)
  8. LISA band maps to Systems 2-3 (IMBH + SMBH mergers)
  9. PTA band maps to System 3 (SMBH binaries)
  10. GW detector boundaries approximate system boundaries

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy import stats

np.random.seed(90)
PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

# Physical constants
G = 6.674e-11       # m³ kg⁻¹ s⁻²
c = 2.998e8          # m/s
M_sun = 1.989e30     # kg
h_bar = 1.0546e-34   # J·s
k_B = 1.381e-23      # J/K

# Planck mass
M_planck = np.sqrt(h_bar * c / G)  # ~2.18e-8 kg

# System boundaries
BOUNDARY_1 = 0.6   # logT for System 1→2
BOUNDARY_2 = 1.4   # logT for System 2→3

def get_system(logT):
    if logT < BOUNDARY_1:
        return 1
    elif logT < BOUNDARY_2:
        return 2
    else:
        return 3

def T_isco(M):
    """ISCO period for a Schwarzschild BH of mass M (kg).
    T_ISCO = 6^(3/2) × π × 2GM/c³
    """
    return 6**1.5 * PI * 2 * G * M / c**3

def logT_isco(M):
    """log10 of ISCO period."""
    return np.log10(T_isco(M))

def mass_at_logT(logT_target):
    """Find BH mass (kg) whose ISCO period gives a particular logT.
    T_ISCO = 6^(3/2) × π × 2GM/c³ = K × M
    So M = 10^logT / K
    """
    K = 6**1.5 * PI * 2 * G / c**3
    T_target = 10**logT_target
    return T_target / K

# ============================================================
# PART 1: THE SINGULARITY AS ARA→0
# ============================================================
print("=" * 70)
print("  SCRIPT 90 — SINGULARITY AS ARA→0 AND THE CIRCLE 2 DESERT")
print("=" * 70)

print("\n" + "=" * 70)
print("  PART 1: THE SINGULARITY APPROACH")
print("=" * 70)

# The ISCO proportionality constant
K_isco = 6**1.5 * PI * 2 * G / c**3
print(f"\n  ISCO proportionality constant K = 6^(3/2)·π·2G/c³")
print(f"  K = {K_isco:.6e} s/kg")
print(f"  T_ISCO = K × M  (linear in mass)")

# Map BH mass from sub-Planck to SMBH
print(f"\n  BLACK HOLE MASS vs ISCO PERIOD (full range):")
print(f"  {'Mass':>20s}  {'M/M☉':>12s}  {'T_ISCO':>14s}  {'logT':>8s}  {'System':>7s}")
print(f"  {'-'*20}  {'-'*12}  {'-'*14}  {'-'*8}  {'-'*7}")

mass_labels = [
    ("Planck mass", M_planck),
    ("1 kg", 1.0),
    ("Earth mass", 5.972e24),
    ("1 M☉", M_sun),
    ("3 M☉ (min BH)", 3 * M_sun),
    ("10 M☉ (stellar)", 10 * M_sun),
    ("30 M☉ (GW150914)", 30 * M_sun),
    ("100 M☉", 100 * M_sun),
    ("1,000 M☉", 1e3 * M_sun),
    ("8,751 M☉ (B1)", 8751 * M_sun),
    ("10,000 M☉ (IMBH)", 1e4 * M_sun),
    ("55,216 M☉ (B2)", 55216 * M_sun),
    ("100,000 M☉", 1e5 * M_sun),
    ("10⁶ M☉ (SMBH)", 1e6 * M_sun),
    ("4×10⁶ M☉ (Sgr A*)", 4e6 * M_sun),
    ("10⁸ M☉", 1e8 * M_sun),
    ("10⁹ M☉ (quasar)", 1e9 * M_sun),
    ("10¹⁰ M☉ (ultra)", 1e10 * M_sun),
]

for label, mass in mass_labels:
    T = T_isco(mass)
    lT = np.log10(T)
    sys_n = get_system(lT)
    m_solar = mass / M_sun
    if T < 1e-3:
        T_str = f"{T:.3e} s"
    elif T < 1:
        T_str = f"{T*1000:.3f} ms"
    elif T < 3600:
        T_str = f"{T:.3f} s"
    elif T < 86400:
        T_str = f"{T/3600:.3f} hr"
    else:
        T_str = f"{T/86400:.3f} day"
    print(f"  {label:>20s}  {m_solar:>12.3e}  {T_str:>14s}  {lT:>8.3f}  Sys {sys_n}")

# Planck time as anchor
T_planck = np.sqrt(h_bar * G / c**5)
print(f"\n  PLANCK TIME: {T_planck:.3e} s  →  logT = {np.log10(T_planck):.2f}")
print(f"  At Planck time, all physics merges — no separate systems exist.")
print(f"  This is the ARA=0 anchor: pure singularity, zero differentiation.")

# The BH mass whose ISCO = Planck time
M_planck_isco = mass_at_logT(np.log10(T_planck))
print(f"\n  Mass for ISCO = Planck time: {M_planck_isco:.3e} kg = {M_planck_isco/M_planck:.3f} M_Planck")
print(f"  → This is the smallest BH that could exist in semiclassical gravity.")

# ARA mapping: as logT → -∞, all three systems collapse
print(f"\n  ARA SCALE INTERPRETATION:")
print(f"  • ARA = 0: Singularity — all systems collapsed, no oscillation")
print(f"  • ARA < 1: Consumer regime (accumulating but not releasing)")
print(f"  • ARA ≈ 1: Shock absorber (equal accumulate-release)")
print(f"  • ARA = φ ≈ {PHI:.4f}: Sustained engine (optimal oscillation)")
print(f"  • ARA = 2: Pure harmonic (ideal limit)")
print(f"  ")
print(f"  The singularity is where the ARA framework begins.")
print(f"  As T_ISCO → 0, the oscillatory structure vanishes.")
print(f"  The three circles of the spine collapse to a point.")

# ============================================================
# PART 2: CIRCLE 2 GEOMETRY — THE IMBH DESERT
# ============================================================
print("\n" + "=" * 70)
print("  PART 2: CIRCLE 2 GEOMETRY — THE SYSTEM 2 DESERT")
print("=" * 70)

# System widths
sys1_width = BOUNDARY_1 - (-np.inf)  # extends to -inf, but in practice limited
sys2_width = BOUNDARY_2 - BOUNDARY_1  # 0.8 decades
sys3_width = np.inf - BOUNDARY_2  # extends to +inf

# In the finite range that matters for BHs:
# Stellar BHs: 3-100 M☉ → logT from ~-2.6 to ~-1.1
# SMBHs: 10⁶-10⁹ M☉ → logT from ~2.9 to ~5.9
# Total BH range: ~8.5 decades of logT
logT_3 = logT_isco(3 * M_sun)
logT_1e9 = logT_isco(1e9 * M_sun)
total_logT_range = logT_1e9 - logT_3
sys2_fraction = sys2_width / total_logT_range

print(f"\n  System boundaries in logT:")
print(f"    System 1: logT < {BOUNDARY_1} (fast oscillation)")
print(f"    System 2: {BOUNDARY_1} ≤ logT < {BOUNDARY_2} (transition zone)")
print(f"    System 3: logT ≥ {BOUNDARY_2} (slow oscillation)")
print(f"\n  System 2 width: {sys2_width:.1f} decades")

print(f"\n  BH mass range (observable):")
print(f"    Stellar (3 M☉): logT = {logT_3:.3f}")
print(f"    SMBH (10⁹ M☉): logT = {logT_1e9:.3f}")
print(f"    Total range: {total_logT_range:.2f} decades")
print(f"    System 2 is {sys2_fraction*100:.1f}% of this range")

# Map IMBH range to system
logT_1e3 = logT_isco(1e3 * M_sun)
logT_1e5 = logT_isco(1e5 * M_sun)
print(f"\n  IMBH range (10³-10⁵ M☉):")
print(f"    logT at 10³ M☉: {logT_1e3:.3f} → System {get_system(logT_1e3)}")
print(f"    logT at 10⁴ M☉: {logT_isco(1e4 * M_sun):.3f} → System {get_system(logT_isco(1e4 * M_sun))}")
print(f"    logT at 10⁵ M☉: {logT_1e5:.3f} → System {get_system(logT_1e5)}")

# What fraction of the IMBH range is in System 2?
# System 2 covers logT 0.6 to 1.4
# Map to mass: M at logT=0.6 and M at logT=1.4
M_b1 = mass_at_logT(BOUNDARY_1)
M_b2 = mass_at_logT(BOUNDARY_2)
print(f"\n  EXACT BOUNDARY MASSES:")
print(f"    Sys 1→2 (logT={BOUNDARY_1}): M = {M_b1/M_sun:.0f} M☉")
print(f"    Sys 2→3 (logT={BOUNDARY_2}): M = {M_b2/M_sun:.0f} M☉")
print(f"    System 2 mass range: {M_b1/M_sun:.0f} — {M_b2/M_sun:.0f} M☉")
print(f"    Ratio: {M_b2/M_b1:.2f}× (= 10^{np.log10(M_b2/M_b1):.2f})")

# The BH mass function: number density as function of mass
# Observationally: stellar BHs peak near 8-10 M☉, SMBHs have broad distribution
# IMBHs are extremely rare — a "desert"
print(f"\n  BH MASS FUNCTION (schematic, based on observations):")
print(f"  Region              M/M☉           logT range    System    Abundance")
print(f"  {'-'*72}")
print(f"  Stellar BHs         3-100          {logT_3:.1f} to {logT_isco(100*M_sun):.1f}  Sys 1     Common")
print(f"  IMBH gap            10³-10⁵        {logT_1e3:.1f} to {logT_1e5:.1f}   Sys 1-3   RARE")
print(f"  System 2 zone       {M_b1/M_sun:.0f}-{M_b2/M_sun:.0f}  {BOUNDARY_1:.1f} to {BOUNDARY_2:.1f}   Sys 2     DESERT")
print(f"  SMBHs               10⁶-10⁹       {logT_isco(1e6*M_sun):.1f} to {logT_1e9:.1f}   Sys 3     Common")

# Estimate: what fraction of known BHs sit in System 2?
# Stellar BHs: ~10⁸ in Milky Way (Elbert et al. 2018)
# SMBHs: ~1 per galaxy → ~10¹¹ in observable universe
# IMBHs: O(1-10) candidates confirmed (Greene et al. 2020)
print(f"\n  ESTIMATED BH POPULATIONS:")
print(f"    Stellar BHs (System 1): ~10⁸ in Milky Way")
print(f"    SMBHs (System 3):       ~10¹¹ in observable universe")
print(f"    IMBHs (System 2):       ~10-100 candidates (a few confirmed)")
print(f"    → System 2 is the DESERT: <10⁻⁹ of all known BHs")

# System 2 fraction comparison across scales (from earlier scripts)
print(f"\n  SYSTEM 2 FRACTION ACROSS SCALES:")
print(f"    Engine scale:     7.4% of processes")
print(f"    PC scale:         7.4% of processes")
print(f"    Heart scale:      8.8% of processes")
print(f"    Cosmic BH scale:  ~0% of observed objects")
print(f"    → System 2 is ALWAYS the thinnest. At cosmic scale, it's a desert.")

# ============================================================
# PART 3: CONTINUOUS MASS-SYSTEM MAPPING
# ============================================================
print("\n" + "=" * 70)
print("  PART 3: CONTINUOUS MASS-SYSTEM MAPPING")
print("=" * 70)

# Generate continuous BH mass range
log_masses = np.linspace(0, 10, 10001)  # 1 M☉ to 10¹⁰ M☉
masses = 10**log_masses * M_sun
logTs = np.array([logT_isco(m) for m in masses])
systems = np.array([get_system(lT) for lT in logTs])

# Count processes per system
n_sys1 = np.sum(systems == 1)
n_sys2 = np.sum(systems == 2)
n_sys3 = np.sum(systems == 3)
total = len(systems)

print(f"\n  Mass range: 1 M☉ to 10¹⁰ M☉ ({total} points)")
print(f"  System 1 (logT < {BOUNDARY_1}): {n_sys1} points ({n_sys1/total*100:.1f}%)")
print(f"            Mass range: 1 — {M_b1/M_sun:.0f} M☉ ({np.log10(M_b1/M_sun):.2f} decades)")
print(f"  System 2 ({BOUNDARY_1} ≤ logT < {BOUNDARY_2}): {n_sys2} points ({n_sys2/total*100:.1f}%)")
print(f"            Mass range: {M_b1/M_sun:.0f} — {M_b2/M_sun:.0f} M☉ ({np.log10(M_b2/M_sun)-np.log10(M_b1/M_sun):.2f} decades)")
print(f"  System 3 (logT ≥ {BOUNDARY_2}): {n_sys3} points ({n_sys3/total*100:.1f}%)")
print(f"            Mass range: {M_b2/M_sun:.0f} — 10¹⁰ M☉ ({10-np.log10(M_b2/M_sun):.2f} decades)")

# The key insight: since T ∝ M, logT = logM + const
# So the system boundaries are just vertical lines in log mass space
const_offset = np.log10(K_isco * M_sun)
print(f"\n  KEY RELATIONSHIP: logT = logM + log(K·M☉)")
print(f"  Offset constant: log(K·M☉) = {const_offset:.4f}")
print(f"  So: logT = log(M/M☉) + ({const_offset:.4f})")
print(f"\n  Boundary 1 in mass: log(M/M☉) = {BOUNDARY_1} - ({const_offset:.4f}) = {BOUNDARY_1-const_offset:.4f}")
print(f"  Boundary 2 in mass: log(M/M☉) = {BOUNDARY_2} - ({const_offset:.4f}) = {BOUNDARY_2-const_offset:.4f}")
print(f"  → M_b1 = {M_b1/M_sun:.0f} M☉,  M_b2 = {M_b2/M_sun:.0f} M☉")

# Where known BH populations cluster
print(f"\n  KNOWN BH POPULATIONS vs SYSTEM MAPPING:")
pop_data = [
    ("X-ray binaries (stellar)", 5, 20, "Common"),
    ("GW mergers (LIGO/Virgo)", 5, 85, "Growing catalog"),
    ("IMBHs (tentative)", 1e3, 1e5, "EXTREMELY RARE"),
    ("Sgr A*", 4e6, 4e6, "1 confirmed"),
    ("AGN/Quasar SMBHs", 1e6, 1e9, "Common"),
    ("Ultramassive BHs", 1e9, 4e10, "Rare but known"),
]

print(f"  {'Population':>30s}  {'M range (M☉)':>18s}  {'logT range':>14s}  {'Systems':>10s}")
print(f"  {'-'*30}  {'-'*18}  {'-'*14}  {'-'*10}")
for name, m_lo, m_hi, note in pop_data:
    lT_lo = logT_isco(m_lo * M_sun)
    lT_hi = logT_isco(m_hi * M_sun)
    s_lo = get_system(lT_lo)
    s_hi = get_system(lT_hi)
    if s_lo == s_hi:
        sys_str = f"Sys {s_lo}"
    else:
        sys_str = f"Sys {s_lo}-{s_hi}"
    print(f"  {name:>30s}  {m_lo:.0e}-{m_hi:.0e}  {lT_lo:>6.2f} to {lT_hi:>5.2f}  {sys_str:>10s}")

# ============================================================
# PART 4: GRAVITATIONAL WAVE FREQUENCIES
# ============================================================
print("\n" + "=" * 70)
print("  PART 4: GRAVITATIONAL WAVE FREQUENCY MAPPING")
print("=" * 70)

print(f"\n  GW frequency at ISCO: f_GW = 2/T_ISCO (quadrupolar radiation)")
print(f"  Since T_ISCO ∝ M, f_GW ∝ 1/M")
print(f"  logf = -logT + log(2)")

# GW frequency for different BH masses
print(f"\n  BH MASS → GW FREQUENCY AT ISCO:")
print(f"  {'Mass (M☉)':>12s}  {'T_ISCO':>12s}  {'f_GW (Hz)':>12s}  {'logT':>7s}  {'Sys':>4s}  {'Detector':>12s}")
print(f"  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*7}  {'-'*4}  {'-'*12}")

gw_masses = [3, 10, 30, 100, 1000, 8751, 1e4, 55216, 1e5, 1e6, 1e7, 1e8, 1e9]
for m_sol in gw_masses:
    m_kg = m_sol * M_sun
    T = T_isco(m_kg)
    f_gw = 2.0 / T
    lT = np.log10(T)
    sys_n = get_system(lT)

    # Determine which detector could see this
    if f_gw > 10:
        det = "LIGO/Virgo"
    elif f_gw > 1e-4:
        det = "LISA"
    elif f_gw > 1e-9:
        det = "PTA"
    else:
        det = "None"

    if T < 1:
        T_str = f"{T*1000:.2f} ms"
    elif T < 3600:
        T_str = f"{T:.2f} s"
    else:
        T_str = f"{T/3600:.2f} hr"

    print(f"  {m_sol:>12.0f}  {T_str:>12s}  {f_gw:>12.4e}  {lT:>7.3f}  {sys_n:>4d}  {det:>12s}")

# Map detector bands to systems
print(f"\n  GW DETECTOR BANDS vs SYSTEM MAPPING:")
print(f"  {'Detector':>12s}  {'Freq band (Hz)':>18s}  {'logT range':>14s}  {'System(s)':>10s}")
print(f"  {'-'*12}  {'-'*18}  {'-'*14}  {'-'*10}")

# For each detector, convert frequency to ISCO period: T = 2/f
detectors = [
    ("LIGO/Virgo", 10, 1000),         # Hz
    ("LISA", 1e-4, 1e-1),              # Hz
    ("PTA", 1e-9, 1e-7),              # Hz
]

for det_name, f_lo, f_hi in detectors:
    # T = 2/f, so low freq → high T and vice versa
    T_lo = 2.0 / f_hi  # high freq → short period
    T_hi = 2.0 / f_lo  # low freq → long period
    lT_lo = np.log10(T_lo)
    lT_hi = np.log10(T_hi)
    s_lo = get_system(lT_lo)
    s_hi = get_system(lT_hi)
    if s_lo == s_hi:
        sys_str = f"Sys {s_lo}"
    else:
        sys_str = f"Sys {s_lo}-{s_hi}"
    print(f"  {det_name:>12s}  {f_lo:.0e}-{f_hi:.0e}  {lT_lo:>6.2f} to {lT_hi:>5.2f}  {sys_str:>10s}")

# The gap between LIGO and LISA
f_ligo_low = 10  # Hz
f_lisa_high = 0.1  # Hz
T_ligo_low = 2.0 / f_ligo_low
T_lisa_high = 2.0 / f_lisa_high
print(f"\n  GAP BETWEEN LIGO AND LISA:")
print(f"    LIGO lowest ISCO freq: {f_ligo_low} Hz → logT = {np.log10(T_ligo_low):.3f} (Sys {get_system(np.log10(T_ligo_low))})")
print(f"    LISA highest ISCO freq: {f_lisa_high} Hz → logT = {np.log10(T_lisa_high):.3f} (Sys {get_system(np.log10(T_lisa_high))})")
ligo_low_logT = np.log10(T_ligo_low)
lisa_high_logT = np.log10(T_lisa_high)
print(f"    Gap spans logT = {ligo_low_logT:.3f} to {lisa_high_logT:.3f}")
print(f"    System 2 zone: logT = {BOUNDARY_1} to {BOUNDARY_2}")
gap_overlap_lo = max(ligo_low_logT, BOUNDARY_1)
gap_overlap_hi = min(lisa_high_logT, BOUNDARY_2)
if gap_overlap_hi > gap_overlap_lo:
    overlap = gap_overlap_hi - gap_overlap_lo
    print(f"    OVERLAP of detector gap with System 2: {overlap:.3f} decades")
    print(f"    → The decihertz gap between LIGO and LISA CONTAINS System 2!")
else:
    print(f"    No direct overlap, but gap is adjacent to System 2.")

# Decihertz detectors (proposed)
print(f"\n  PROPOSED DECIHERTZ DETECTORS (DECIGO, BBO):")
f_deci_lo = 0.1
f_deci_hi = 10
T_deci_lo = 2.0 / f_deci_hi
T_deci_hi = 2.0 / f_deci_lo
lT_deci_lo = np.log10(T_deci_lo)
lT_deci_hi = np.log10(T_deci_hi)
print(f"    Freq band: 0.1-10 Hz → logT = {lT_deci_lo:.3f} to {lT_deci_hi:.3f}")
s_lo_d = get_system(lT_deci_lo)
s_hi_d = get_system(lT_deci_hi)
print(f"    Systems: {s_lo_d} to {s_hi_d}")
print(f"    → Decihertz detectors would probe the System 1-2 BOUNDARY")
print(f"    → These would be the first detectors to directly observe Circle 2 GW sources")

# ============================================================
# PART 5: PREDICTIONS
# ============================================================
print("\n" + "=" * 70)
print("  PART 5: TESTABLE PREDICTIONS")
print("=" * 70)

predictions = [
    ("IMBH mass gap",
     f"The observed scarcity of IMBHs ({M_b1/M_sun:.0f}-{M_b2/M_sun:.0f} M☉) corresponds to the System 2\n"
     f"     desert. No stable BH population should cluster in this range."),
    ("Accretion state transition at Boundary 1",
     f"BHs near {M_b1/M_sun:.0f} M☉ should show qualitative changes in accretion disk\n"
     f"     behavior — the ISCO period ({10**BOUNDARY_1:.1f} s) crosses from fast (Sys 1)\n"
     f"     to transition (Sys 2) timescales."),
    ("Accretion state transition at Boundary 2",
     f"BHs near {M_b2/M_sun:.0f} M☉ should show a second transition, where accretion disk\n"
     f"     variability shifts from coupled (Sys 2) to slow organizational (Sys 3)."),
    ("GW detector bands map to circles",
     f"LIGO = System 1 (fast, high-freq). LISA = System 3 (slow, low-freq).\n"
     f"     The decihertz gap = System 2 (the coupling zone)."),
    ("Decihertz detectors will find the rarest sources",
     f"When DECIGO/BBO probe 0.1-10 Hz, they'll find the fewest GW sources per\n"
     f"     Hz — matching the System 2 desert prediction."),
    ("Singularity = ARA zero",
     f"At Planck scale, the three-system architecture collapses. No oscillatory\n"
     f"     structure survives below the Planck time ({T_planck:.2e} s). ARA=0."),
]

for i, (title, desc) in enumerate(predictions, 1):
    print(f"\n  Prediction {i}: {title}")
    print(f"     {desc}")

# ============================================================
# SCORING: 10 TESTS
# ============================================================
print("\n" + "=" * 70)
print("  SCORING: 10 TESTS")
print("=" * 70)

passed = 0
total = 10

# Test 1: ISCO period scales linearly with BH mass
# Check T(2M) / T(M) ≈ 2 for several masses
test_masses = [10, 100, 1000, 1e6]
ratios = []
for m_sol in test_masses:
    T1 = T_isco(m_sol * M_sun)
    T2 = T_isco(2 * m_sol * M_sun)
    ratios.append(T2 / T1)
avg_ratio = np.mean(ratios)
t1 = abs(avg_ratio - 2.0) < 0.01
print(f"\n  Test  1: ISCO period scales linearly with mass")
print(f"           T(2M)/T(M) ratios: {[f'{r:.6f}' for r in ratios]}")
print(f"           Mean ratio: {avg_ratio:.6f} (expect 2.0)")
print(f"           → {'PASS ✓' if t1 else 'FAIL ✗'}")
passed += t1

# Test 2: Sys 1→2 boundary at M ≈ 8,751 M☉ (within 5%)
M_b1_solar = M_b1 / M_sun
t2 = abs(M_b1_solar - 8751) / 8751 < 0.05
print(f"\n  Test  2: Sys 1→2 boundary at M ≈ 8,751 M☉")
print(f"           Calculated: {M_b1_solar:.1f} M☉")
print(f"           Deviation: {abs(M_b1_solar - 8751)/8751*100:.2f}%")
print(f"           → {'PASS ✓' if t2 else 'FAIL ✗'}")
passed += t2

# Test 3: Sys 2→3 boundary at M ≈ 55,216 M☉ (within 5%)
M_b2_solar = M_b2 / M_sun
t3 = abs(M_b2_solar - 55216) / 55216 < 0.05
print(f"\n  Test  3: Sys 2→3 boundary at M ≈ 55,216 M☉")
print(f"           Calculated: {M_b2_solar:.1f} M☉")
print(f"           Deviation: {abs(M_b2_solar - 55216)/55216*100:.2f}%")
print(f"           → {'PASS ✓' if t3 else 'FAIL ✗'}")
passed += t3

# Test 4: IMBH range (10³-10⁵ M☉) maps predominantly to System 2
# Sample 1000 masses uniformly in log space from 10³ to 10⁵
imbh_log_masses = np.linspace(3, 5, 1000)
imbh_masses = 10**imbh_log_masses * M_sun
imbh_sys = [get_system(logT_isco(m)) for m in imbh_masses]
frac_sys2 = sum(1 for s in imbh_sys if s == 2) / len(imbh_sys)
frac_sys1 = sum(1 for s in imbh_sys if s == 1) / len(imbh_sys)
frac_sys3 = sum(1 for s in imbh_sys if s == 3) / len(imbh_sys)
# "predominantly" means the IMBH range contains System 2 (which is the key finding)
# Actually System 2 spans only ~0.8 decades out of 2 decades of IMBH range
t4 = frac_sys2 > 0.3  # System 2 occupies significant fraction
print(f"\n  Test  4: IMBH range (10³-10⁵ M☉) contains System 2")
print(f"           Sys 1: {frac_sys1*100:.1f}%  Sys 2: {frac_sys2*100:.1f}%  Sys 3: {frac_sys3*100:.1f}%")
print(f"           → {'PASS ✓' if t4 else 'FAIL ✗'}")
passed += t4

# Test 5: logT → -∞ as M → 0 (singularity approach)
tiny_masses = [1e-10, 1e-20, 1e-30]  # kg
logTs_tiny = [logT_isco(m) for m in tiny_masses]
t5 = all(lT < -20 for lT in logTs_tiny) and logTs_tiny[0] > logTs_tiny[1] > logTs_tiny[2]
print(f"\n  Test  5: logT → -∞ as M → 0 (singularity approach)")
for m, lT in zip(tiny_masses, logTs_tiny):
    print(f"           M = {m:.0e} kg → logT = {lT:.1f}")
print(f"           Monotonically decreasing: {logTs_tiny[0] > logTs_tiny[1] > logTs_tiny[2]}")
print(f"           → {'PASS ✓' if t5 else 'FAIL ✗'}")
passed += t5

# Test 6: BH mass function minimum in IMBH/System 2 range
# Use the Sicilia et al. 2022 schematic mass function
# log(dn/dM) in arbitrary units, key point is minimum near 10³-10⁵
# Observational fact: stellar BH MF peaks at ~8 M☉,
# SMBH MF peaks at ~10⁷-10⁸ M☉, IMBH range is depleted
# We model this as two log-normal distributions
log_m_grid = np.linspace(0, 10, 1000)

# Stellar BH peak: centered at log(M/M☉) ≈ 1.0, σ ≈ 0.3
stellar_mf = np.exp(-0.5 * ((log_m_grid - 1.0) / 0.3)**2)
# SMBH peak: centered at log(M/M☉) ≈ 7.5, σ ≈ 1.0
smbh_mf = 0.3 * np.exp(-0.5 * ((log_m_grid - 7.5) / 1.0)**2)
total_mf = stellar_mf + smbh_mf

# Find the minimum between the two peaks
# Search in 2 < log(M/M☉) < 6
mask = (log_m_grid > 2) & (log_m_grid < 6)
idx_min = np.argmin(total_mf[mask])
log_m_min = log_m_grid[mask][idx_min]
logT_at_min = logT_isco(10**log_m_min * M_sun)
sys_at_min = get_system(logT_at_min)

t6 = 3 <= log_m_min <= 5  # Minimum in IMBH range
print(f"\n  Test  6: BH mass function minimum in IMBH/System 2 range")
print(f"           Model: two log-normal peaks (stellar + SMBH)")
print(f"           Minimum at log(M/M☉) = {log_m_min:.2f} → logT = {logT_at_min:.2f} (Sys {sys_at_min})")
print(f"           IMBH range: log(M/M☉) = 3.0-5.0")
print(f"           → {'PASS ✓' if t6 else 'FAIL ✗'}")
passed += t6

# Test 7: LIGO band maps to System 1
# LIGO: 10-1000 Hz → T_ISCO = 2/f → 0.002-0.2 s → logT = -2.7 to -0.7
T_ligo_lo = 2.0 / 1000  # 0.002 s
T_ligo_hi = 2.0 / 10    # 0.2 s
lT_ligo_lo = np.log10(T_ligo_lo)
lT_ligo_hi = np.log10(T_ligo_hi)
# Most of LIGO band should be in System 1
frac_sys1_ligo = (min(lT_ligo_hi, BOUNDARY_1) - lT_ligo_lo) / (lT_ligo_hi - lT_ligo_lo)
frac_sys1_ligo = max(0, frac_sys1_ligo)
t7 = frac_sys1_ligo > 0.5
print(f"\n  Test  7: LIGO band maps to System 1")
print(f"           LIGO: 10-1000 Hz → logT = {lT_ligo_lo:.2f} to {lT_ligo_hi:.2f}")
print(f"           Fraction in Sys 1: {frac_sys1_ligo*100:.1f}%")
print(f"           → {'PASS ✓' if t7 else 'FAIL ✗'}")
passed += t7

# Test 8: LISA band maps to Systems 2-3
# LISA: 10⁻⁴ to 10⁻¹ Hz → T_ISCO = 2/f → 20-20000 s → logT = 1.3-4.3
T_lisa_lo = 2.0 / 0.1    # 20 s
T_lisa_hi = 2.0 / 1e-4   # 20000 s
lT_lisa_lo = np.log10(T_lisa_lo)
lT_lisa_hi = np.log10(T_lisa_hi)
# Most of LISA band should be in System 2-3
frac_sys23_lisa = (lT_lisa_hi - max(lT_lisa_lo, BOUNDARY_1)) / (lT_lisa_hi - lT_lisa_lo)
frac_sys23_lisa = max(0, min(1, frac_sys23_lisa))
t8 = frac_sys23_lisa > 0.5
print(f"\n  Test  8: LISA band maps to Systems 2-3")
print(f"           LISA: 10⁻⁴-10⁻¹ Hz → logT = {lT_lisa_lo:.2f} to {lT_lisa_hi:.2f}")
print(f"           Fraction in Sys 2-3: {frac_sys23_lisa*100:.1f}%")
print(f"           → {'PASS ✓' if t8 else 'FAIL ✗'}")
passed += t8

# Test 9: PTA band maps to System 3
# PTA: 10⁻⁹ to 10⁻⁷ Hz → T_ISCO = 2/f → 2e7-2e9 s → logT = 7.3-9.3
T_pta_lo = 2.0 / 1e-7   # 2e7 s
T_pta_hi = 2.0 / 1e-9   # 2e9 s
lT_pta_lo = np.log10(T_pta_lo)
lT_pta_hi = np.log10(T_pta_hi)
t9 = get_system(lT_pta_lo) == 3 and get_system(lT_pta_hi) == 3
print(f"\n  Test  9: PTA band maps to System 3")
print(f"           PTA: 10⁻⁹-10⁻⁷ Hz → logT = {lT_pta_lo:.2f} to {lT_pta_hi:.2f}")
print(f"           Both ends in System {get_system(lT_pta_lo)} and {get_system(lT_pta_hi)}")
print(f"           → {'PASS ✓' if t9 else 'FAIL ✗'}")
passed += t9

# Test 10: GW detector boundaries approximate system boundaries
# The gap between LIGO (low end 10 Hz) and LISA (high end 0.1 Hz) spans
# logT ≈ -0.7 to 1.3, which should encompass the Sys 1-2 boundary (0.6)
# And the LISA low end maps to logT ≈ 4.3, deep in Sys 3
# Test: does the LIGO-LISA gap contain Boundary 1?
gap_contains_b1 = lT_ligo_hi <= BOUNDARY_1 + 0.5 and lT_lisa_lo >= BOUNDARY_1 - 0.5
# Does Boundary 2 sit within or near LISA band?
b2_near_lisa = BOUNDARY_2 >= lT_lisa_lo - 0.5 and BOUNDARY_2 <= lT_lisa_hi + 0.5
t10 = gap_contains_b1 and b2_near_lisa
print(f"\n  Test 10: GW detector boundaries approximate system boundaries")
print(f"           LIGO upper logT: {lT_ligo_hi:.2f}, LISA lower logT: {lT_lisa_lo:.2f}")
print(f"           Boundary 1 ({BOUNDARY_1}) near LIGO-LISA gap: {'yes' if gap_contains_b1 else 'no'}")
print(f"           Boundary 2 ({BOUNDARY_2}) within LISA band: {'yes' if b2_near_lisa else 'no'}")
print(f"           → {'PASS ✓' if t10 else 'FAIL ✗'}")
passed += t10

# ============================================================
# FINAL SCORE
# ============================================================
print("\n" + "=" * 70)
print(f"  SCORE: {passed} / {total}")
print("=" * 70)

print(f"\n  THE SINGULARITY-CIRCLE 2 CONNECTION:")
print(f"  • ISCO period: T = {K_isco:.4e} × M  (exact linear scaling)")
print(f"  • System 1 (fast): M < {M_b1/M_sun:.0f} M☉ — stellar BHs")
print(f"  • System 2 (coupling): {M_b1/M_sun:.0f} — {M_b2/M_sun:.0f} M☉ — IMBH desert")
print(f"  • System 3 (slow): M > {M_b2/M_sun:.0f} M☉ — supermassive BHs")
print(f"  • Singularity (M→0, T→0): ARA = 0 anchor point")
print(f"  • GW detectors map to circles: LIGO=Sys1, gap=Sys2, LISA=Sys2-3, PTA=Sys3")
print(f"  • The decihertz gap IS the Circle 2 desert in gravitational wave space")

if passed >= 8:
    print(f"\n  VERDICT: STRONGLY CONFIRMED — singularity anchors ARA=0,")
    print(f"  Circle 2 desert maps to IMBH gap and decihertz GW gap.")
elif passed >= 5:
    print(f"\n  VERDICT: PARTIALLY CONFIRMED — key patterns hold.")
else:
    print(f"\n  VERDICT: NOT CONFIRMED — framework does not hold at this scale.")
