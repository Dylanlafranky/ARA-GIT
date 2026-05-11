"""
lightning_neuron_shape_match.py — vertical-ARA same-physics test.

Dylan 2026-05-11: ECG ↔ ENSO share architectural class but have different
substrate physics, which is why their shapes match only roughly. Lightning ↔
neuron are LITERALLY the same physics (charge accumulation → threshold →
discharge through conductive medium → refractory) at scales ~10⁶ apart.

If vertical-ARA claims "same shape at different scales after time-rescaling,"
this is the cleanest possible test. Same physics, vastly different scale.

Lightning return-stroke current (canonical Heidler function, IEEE std):
  I(t) = (I_peak / η) * (t/τ_rise)^n / (1 + (t/τ_rise)^n) * exp(-t/τ_decay)
  Typical: τ_rise ≈ 1 μs, τ_decay ≈ 50 μs, n = 2

Action potential (canonical Hodgkin-Huxley shape):
  Depolarization: ~1 ms, fast rising spike to +30 mV
  Repolarization: ~2 ms, fast falling
  Afterhyperpolarization: ~3 ms, slow recovery below resting
  Resting: -70 mV; spike peak: +30 mV; AHP nadir: -80 mV

Both are relaxation-oscillator outputs of the same architecture.

Method:
  1. Generate both canonical waveforms at 200 phase samples (normalized [0,1]).
  2. Fourier-coefficient distance between them + ~10 null candidates.
  3. Compare ranking.

Source attributions:
  Heidler 1985, 'Travelling current source model'
  Hodgkin & Huxley 1952, J Physiol 117:500-544
  Both are textbook canonical forms, peer-reviewed since.
"""
import os, json, math
import numpy as np

PHI = (1+5**0.5)/2

# ============================================================================
# 1. LIGHTNING RETURN-STROKE CURRENT (Heidler function)
# ============================================================================
print("[1/4] Generating canonical lightning return-stroke waveform...")

# Heidler function for return-stroke current
def heidler(t, I_peak=30.0, tau_rise=1.0, tau_decay=50.0, n=2.0):
    """Heidler function — canonical lightning return-stroke shape.
       t in microseconds, I in kA. Returns normalized [0,1] for shape comparison."""
    # Heidler: I(t) = (I_peak/η) × (t/τ1)^n / (1 + (t/τ1)^n) × exp(-t/τ2)
    eta = np.exp(-(tau_rise/tau_decay) * (n * tau_decay/tau_rise)**(1/n))
    pos = t > 0
    out = np.zeros_like(t)
    x = t[pos] / tau_rise
    out[pos] = (I_peak/eta) * (x**n) / (1 + x**n) * np.exp(-t[pos]/tau_decay)
    return out

# Sample over a window long enough to capture rise + most of decay
# Window: 0 to 200 us (4× decay time), 200 samples
t_us = np.linspace(0, 200, 200)
lightning_raw = heidler(t_us)
lightning = (lightning_raw - lightning_raw.min()) / max(1e-9, lightning_raw.max() - lightning_raw.min())
print(f'  Peak at t = {t_us[np.argmax(lightning)]:.2f} μs, decay to 10% by t = {t_us[next(i for i, v in enumerate(lightning) if i > np.argmax(lightning) and v < 0.1)]:.1f} μs')

# ============================================================================
# 2. ACTION POTENTIAL (simplified Hodgkin-Huxley shape)
# ============================================================================
print("\n[2/4] Generating canonical action potential waveform...")

def action_potential(t, t_spike=1.0):
    """Simplified action potential — analytical form matching HH numerical output.
       Rest = -70 mV; spike peak ≈ +30 mV at t_spike; AHP nadir ≈ -80 mV after.
       t in ms. Returns mV-scaled signal, will normalize later."""
    resting = -70.0
    out = np.full_like(t, resting)
    # Fast depolarization (sigmoidal rise into spike)
    rise = 1.0 / (1 + np.exp(-15*(t - t_spike + 0.15)))
    # Fast repolarization (sigmoidal fall)
    fall = 1.0 / (1 + np.exp(15*(t - t_spike - 0.4)))
    spike = 100.0 * rise * fall  # spike amplitude 100 mV (from -70 to +30)
    # Afterhyperpolarization (slow undershoot)
    ahp_t = t - t_spike - 0.6
    ahp = np.where(ahp_t > 0, -10.0 * np.exp(-ahp_t/2.0) * (1 - np.exp(-ahp_t/0.5)), 0.0)
    return resting + spike + ahp

# Sample over a window: 0 to 8 ms, 200 samples
t_ms = np.linspace(0, 8.0, 200)
ap_raw = action_potential(t_ms)
ap = (ap_raw - ap_raw.min()) / max(1e-9, ap_raw.max() - ap_raw.min())
print(f'  Peak at t = {t_ms[np.argmax(ap)]:.2f} ms, AHP minimum at t = {t_ms[np.argmin(ap[100:])+100]:.2f} ms')

# ============================================================================
# 3. ALIGN AND COMPARE
# ============================================================================
print("\n[3/4] Aligning peaks and computing Fourier distances...")

def align_to(target, candidate):
    tp = int(np.argmax(target)); cp = int(np.argmax(candidate))
    return np.roll(candidate, tp - cp)

ap_aligned = align_to(lightning, ap)

# Same null candidates as ECG test, plus a few extras tuned to spike-class
n = 200
phase = np.linspace(0, 2*np.pi, n, endpoint=False)
nulls = {
    'pure sine': np.sin(phase),
    'sharp peak (sech-shape)': 1.0 / np.cosh(3*np.cos(phase/2)),
    'sawtooth slow-rise': np.where(phase < np.pi, phase/np.pi, 2-phase/np.pi),
    'sawtooth fast-rise': np.where(phase < np.pi*0.3, phase/(np.pi*0.3), (2*np.pi-phase)/(2*np.pi-np.pi*0.3)),
    'symmetric Gaussian peak': np.exp(-((phase - np.pi)**2) / 1.0),
    'fast-spike + slow-recovery': np.exp(-((phase - np.pi)**2) / 0.5) - 0.3*np.exp(-((phase - np.pi*1.6)**2) / 2.0),
    'narrow Gaussian (sharp)': np.exp(-((phase - np.pi)**2) / 0.3),
    'wide Gaussian (blunt)': np.exp(-((phase - np.pi)**2) / 2.0),
    'right-skewed log-normal': np.where(phase>0, np.exp(-((np.log(np.maximum(phase, 1e-9)/np.pi))**2)/0.5), 0),
}

def norm(x): return (x - x.min()) / max(1e-9, x.max() - x.min())

def fourier_params(shape, k_max=6):
    s = shape - shape.mean()
    F = np.fft.fft(s)
    a = F[:k_max+1]
    amp = np.abs(a); ph = np.angle(a)
    R = [amp[k]/amp[1] if amp[1] > 0 else 0.0 for k in range(2, k_max+1)]
    phi = [float(np.mod(ph[k] - k*ph[1] + np.pi, 2*np.pi) - np.pi) for k in range(2, k_max+1)]
    return np.array(R + phi)

def dist(a, b): return float(np.linalg.norm(a - b))

p_light = fourier_params(lightning)
p_neuron = fourier_params(ap_aligned)
d_main = dist(p_light, p_neuron)

results = [('Action potential (vs lightning)', d_main)]
for name, sig in nulls.items():
    s_n = norm(sig)
    s_aligned = align_to(lightning, s_n)
    p_null = fourier_params(s_aligned)
    results.append((name, dist(p_light, p_null)))

results.sort(key=lambda x: x[1])

print()
print(f"{'comparison':<40} {'Fourier-dist':>13} {'rank':>5}")
print('-' * 65)
for rank, (name, d) in enumerate(results, 1):
    marker = ' ← AP' if name.startswith('Action potential') else ''
    print(f"  {name:<38} {d:>13.4f} {rank:>5}{marker}")

ap_rank = next(i for i, (name, _) in enumerate(results, 1) if name.startswith('Action potential'))

# ============================================================================
# 4. VERDICT
# ============================================================================
print()
print('=' * 65)
print('VERDICT')
print('=' * 65)
print(f'Action potential ranks #{ap_rank} of {len(results)} candidates by Fourier-coefficient distance to lightning.')
print(f'Time-scale gap: lightning τ_decay ~ 50 μs, AP duration ~ 5 ms → ratio ~ 100x.')
print(f'  In φ-rungs: log_φ(100) ≈ {math.log(100)/math.log(PHI):.1f} rungs.')
print()

def corr(a, b): return float(np.corrcoef(a, b)[0,1])
c_main = corr(lightning, ap_aligned)
print(f'Gross correlation lightning↔AP (after peak alignment): {c_main:+.3f}')
print()
if ap_rank == 1:
    print('  → STRONG: action potential is the closest match. Lightning and neuron AP')
    print('    share Fourier-shape template — same physics, same shape after time-rescaling.')
    print('    Vertical-ARA same-physics claim CONFIRMED.')
elif ap_rank <= 3:
    print('  → MODERATE: action potential in top 3. Same-physics claim partially supported.')
elif ap_rank <= 5:
    print('  → MIXED: action potential mid-pack. Some shape similarity but not template-identical.')
else:
    print('  → WEAK: action potential below most null candidates. Same-physics claim fails.')

# Save
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lightning_neuron_shape_match_data.js')
payload = dict(
    date='2026-05-11',
    lightning_waveform=[float(x) for x in lightning],
    action_potential_waveform=[float(x) for x in ap_aligned],
    fourier_distance_lightning_ap=d_main,
    ap_rank=ap_rank,
    null_results=[{'name': n, 'distance': float(d)} for n, d in results],
    gross_corr_lightning_ap=c_main,
    scale_ratio_us_to_ms=100.0,
    scale_phi_rungs=math.log(100)/math.log(PHI),
    phi=PHI,
)
with open(OUT, 'w') as f:
    f.write("window.LIGHTNING_NEURON_SHAPE = " + json.dumps(payload, default=str) + ";\n")
print(f'\nSaved -> {OUT}')
