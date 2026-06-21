"""
cepheid_coupled_pair_test.py — Dylan's coupled-pair hypothesis on Cepheid variables.

Dylan 2026-05-11:
    The original Script 98 measured a Cepheid light curve and got ARA ≈ 2.5,
    classifying it as a "snap." But 2.5 sits ABOVE the pure-harmonics ceiling
    at 2.0, on the wrong side of the scale to be a snap (snaps live below 0.2).

    2.5 is suspiciously close to φ² ≈ 2.618 — exactly what a COUPLED-PAIR of
    engines at φ each should produce when measured naively as one number.

    Cepheids are known to support multiple pulsation modes — fundamental + first
    overtone, with double-mode "beat" Cepheids being well-documented. So "two
    coupled subsystems" isn't speculation here; it's the established astrophysics.

This script tests the prediction.

DATA: OGLE-IV Galactic Disk Cepheid catalog (public, plain text).
  https://www.astrouw.edu.pl/ogle/ogle4/OCVS/gd/cep/

For each Cepheid:
  - Fold the light curve at its catalogued period(s)
  - Measure the rise time vs fall time in the folded curve
  - ARA = T_fall / T_rise  (>1 = engine territory, slow fall after fast rise)

PREDICTIONS (from framework_above_2_coupled_pair.md):
  1. Single-mode (F-only or 1O-only) Cepheids: ARA ≈ φ (~1.618). They're one engine.
  2. Double-mode (F/1O) Cepheids: composite light curve ARA ≈ φ² (~2.618).
     Each mode component, isolated, should sit near φ.
  3. Composite ARA / single-mode ARA ≈ φ (the ARA-of-ARA recovers engine at next level).

If predictions land:
  - The original Script 98 "ARA=2.5=snap" was a measurement on a multi-mode star.
    Framework reading is correct after Fourier decomposition.
  - Cepheid row in MASTER_PREDICTION_LEDGER.md flips from FAILED to CONFIRMED.

If predictions don't land:
  - The coupled-pair audit rule needs revision; the >2 reading on Cepheids has
    a different origin than the framework currently proposes.

Real data only (per Dylan's standing rule).
"""
import os, sys, json, math
import numpy as np
import requests

PHI = (1 + 5**0.5) / 2
PHI_SQ = PHI * PHI
OGLE_BASE = "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/gd/cep"

# --- Sample selection: pick ~5 of each type that are well-sampled ---
# Manually selected after browsing — well-sampled, no obvious issues
SAMPLES = {
    'F (fundamental only)': [
        ('OGLE-GD-CEP-0002', 1.5809397),
        ('OGLE-GD-CEP-0003', 4.6324134),
        ('OGLE-GD-CEP-0007', 4.5602694),
    ],
    '1O (first overtone only)': [
        ('OGLE-GD-CEP-0001', None),   # need to look up — will fetch from cep1O.dat
        ('OGLE-GD-CEP-0005', None),
        ('OGLE-GD-CEP-0016', None),
    ],
    'F/1O (double-mode beat Cepheids)': [
        ('OGLE-GD-CEP-0009', (1.6762002, 1.2147192)),  # (P_F, P_1O)
        ('OGLE-GD-CEP-0012', (0.6557437, 0.5040448)),
        ('OGLE-GD-CEP-0031', (0.4055173, 0.3076162)),
    ],
}


def fetch_periods_1O():
    """Get periods for 1O-only Cepheids from cep1O.dat."""
    r = requests.get(f"{OGLE_BASE}/cep1O.dat", timeout=15)
    periods = {}
    for line in r.text.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 4:
            periods[parts[0]] = float(parts[3])
    return periods


def fetch_lightcurve(star_id):
    """Fetch I-band photometry. Returns (hjd, mag, err) arrays."""
    url = f"{OGLE_BASE}/phot/I/{star_id}.dat"
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        return None
    data = []
    for line in r.text.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 2:
            try:
                t = float(parts[0]); m = float(parts[1])
                e = float(parts[2]) if len(parts) > 2 else 0.01
                data.append((t, m, e))
            except ValueError:
                continue
    if len(data) < 30:
        return None
    arr = np.array(data)
    return arr[:, 0], arr[:, 1], arr[:, 2]


def phase_fold(t, m, period, n_bins=50):
    """Phase-fold and bin the light curve. Returns (phase_centers, mean_mag)."""
    phase = ((t - t[0]) / period) % 1.0
    bins = np.linspace(0, 1, n_bins + 1)
    centers = 0.5 * (bins[:-1] + bins[1:])
    binned = np.full(n_bins, np.nan)
    for i in range(n_bins):
        mask = (phase >= bins[i]) & (phase < bins[i+1])
        if mask.sum() > 0:
            binned[i] = np.median(m[mask])
    # Fill any NaNs by linear interpolation
    if np.any(np.isnan(binned)):
        ok = ~np.isnan(binned)
        if ok.sum() >= 3:
            binned = np.interp(centers, centers[ok], binned[ok])
    return centers, binned


def measure_ara(phase, mag):
    """ARA = T_fall / T_rise on a folded magnitude curve.
       Smaller magnitude = brighter. Rise = mag decreasing, fall = mag increasing.
       Find the cycle's bright peak (mag min) and faint dip (mag max).
       T_rise = phase time from max-mag to min-mag (faint→bright)
       T_fall = phase time from min-mag to next max-mag (bright→faint)
    """
    if mag is None or len(mag) < 10 or np.any(np.isnan(mag)):
        return None
    # Wrap so we can find a clean cycle
    # Find global min (brightest) and max (faintest) phases
    i_min = int(np.argmin(mag))  # brightest
    i_max = int(np.argmax(mag))  # faintest
    n = len(mag)

    # Rise: from faintest (i_max) to brightest (i_min) — going forward
    if i_min > i_max:
        rise_len = i_min - i_max
        fall_len = (n - i_min) + i_max
    else:
        # wrapped: faintest is later, so rise goes through end
        rise_len = (n - i_max) + i_min
        fall_len = i_max - i_min
    if rise_len < 1 or fall_len < 1:
        return None
    return fall_len / rise_len


def fourier_components(t, m, periods):
    """Fit a multi-mode Fourier model with given periods (list of fundamental periods).
       For each period P, fits a1*cos(2π t/P) + b1*sin(2π t/P) + a2*cos(4π t/P) + b2*sin(4π t/P).
       Returns dict of per-mode reconstructed light curves at original times."""
    n = len(t)
    cols = [np.ones(n)]  # constant
    col_labels = ['const']
    for P in periods:
        for k in [1, 2, 3]:  # fundamental + 2nd + 3rd harmonic of this mode
            omega = 2 * np.pi * k / P
            cols.append(np.cos(omega * t)); col_labels.append(f'P{P:.3f}_cos{k}')
            cols.append(np.sin(omega * t)); col_labels.append(f'P{P:.3f}_sin{k}')
    A = np.column_stack(cols)
    coeffs, *_ = np.linalg.lstsq(A, m, rcond=None)
    # Build per-mode reconstruction at a fine phase grid (used for ARA measurement)
    return coeffs, col_labels


def reconstruct_at_phase(period, coeffs, col_labels, phase_grid):
    """Given fitted coefficients and phase grid (0..1), reconstruct that mode's contribution."""
    n = len(phase_grid)
    sig = np.zeros(n)
    for k in [1, 2, 3]:
        a_key = f'P{period:.3f}_cos{k}'
        b_key = f'P{period:.3f}_sin{k}'
        if a_key in col_labels and b_key in col_labels:
            ia = col_labels.index(a_key)
            ib = col_labels.index(b_key)
            omega_phase = 2 * np.pi * k
            sig += coeffs[ia] * np.cos(omega_phase * phase_grid)
            sig += coeffs[ib] * np.sin(omega_phase * phase_grid)
    return sig


def analyze_star(star_id, period_info, label, periods_1O_lookup):
    """Returns dict of ARA measurements."""
    lc = fetch_lightcurve(star_id)
    if lc is None:
        return None
    t, m, e = lc
    n_obs = len(t)

    out = {'star_id': star_id, 'type': label, 'n_obs': n_obs}

    if isinstance(period_info, tuple):
        P_F, P_1O = period_info
        out['P_F'] = P_F
        out['P_1O'] = P_1O
        out['P_ratio'] = P_1O / P_F  # should be ~0.71 for classical Cepheids

        # Composite ARA: just fold at fundamental period, measure
        ph_c, mag_c = phase_fold(t, m, P_F)
        out['ara_composite_at_P_F'] = measure_ara(ph_c, mag_c)
        ph_c2, mag_c2 = phase_fold(t, m, P_1O)
        out['ara_composite_at_P_1O'] = measure_ara(ph_c2, mag_c2)

        # Fourier decomposition: fit both periods simultaneously, then reconstruct each
        coeffs, labels = fourier_components(t, m, [P_F, P_1O])
        phase_grid = np.linspace(0, 1, 200)
        # P_F component
        sig_F = reconstruct_at_phase(P_F, coeffs, labels, phase_grid)
        out['ara_mode_F'] = measure_ara(phase_grid, -sig_F)  # negate: mag-style (brighter=lower)
        # P_1O component
        sig_1O = reconstruct_at_phase(P_1O, coeffs, labels, phase_grid)
        out['ara_mode_1O'] = measure_ara(phase_grid, -sig_1O)

    else:
        P = period_info if period_info is not None else periods_1O_lookup.get(star_id)
        if P is None:
            return None
        out['P'] = P
        ph, mag = phase_fold(t, m, P)
        out['ara_folded'] = measure_ara(ph, mag)
        # Also do Fourier decomp on the single mode
        coeffs, labels = fourier_components(t, m, [P])
        phase_grid = np.linspace(0, 1, 200)
        sig = reconstruct_at_phase(P, coeffs, labels, phase_grid)
        out['ara_mode_reconstructed'] = measure_ara(phase_grid, -sig)

    return out


def main():
    print("=" * 70)
    print("Cepheid Coupled-Pair Test — testing Dylan's φ² hypothesis")
    print("=" * 70)
    print(f"φ = {PHI:.4f}, φ² = {PHI_SQ:.4f}")
    print()

    print("Fetching 1O period catalog...")
    periods_1O = fetch_periods_1O()
    print(f"  {len(periods_1O)} first-overtone Cepheid periods loaded\n")

    all_results = []
    for type_label, stars in SAMPLES.items():
        print(f"--- {type_label} ---")
        for star_id, p_info in stars:
            res = analyze_star(star_id, p_info, type_label, periods_1O)
            if res is None:
                print(f"  {star_id}: FETCH FAILED")
                continue

            if type_label.startswith('F/1O'):
                pr = res.get('P_ratio')
                print(f"  {star_id}  P_F={res['P_F']:.4f}d  P_1O={res['P_1O']:.4f}d  ratio={pr:.4f}")
                print(f"      composite ARA (folded at P_F):  {res['ara_composite_at_P_F']:.3f}")
                print(f"      composite ARA (folded at P_1O): {res['ara_composite_at_P_1O']:.3f}")
                print(f"      mode F (Fourier):               {res['ara_mode_F']:.3f}")
                print(f"      mode 1O (Fourier):              {res['ara_mode_1O']:.3f}")
            else:
                print(f"  {star_id}  P={res['P']:.4f}d  n={res['n_obs']}")
                print(f"      folded ARA: {res['ara_folded']:.3f}   Fourier reconstruction: {res['ara_mode_reconstructed']:.3f}")
            all_results.append(res)
        print()

    # Summary statistics by type
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Predictions:")
    print(f"  Single-mode (F-only or 1O-only) Cepheids:    ARA ≈ φ  = {PHI:.3f}")
    print(f"  Double-mode (F/1O) composite light curve:    ARA ≈ φ² = {PHI_SQ:.3f}")
    print(f"  Each isolated mode of a double-mode star:    ARA ≈ φ  = {PHI:.3f}")
    print()

    f_vals = [r['ara_folded'] for r in all_results
              if r['type'].startswith('F (') and r.get('ara_folded') is not None]
    o_vals = [r['ara_folded'] for r in all_results
              if r['type'].startswith('1O') and r.get('ara_folded') is not None]
    d_comp = [r['ara_composite_at_P_F'] for r in all_results
              if r['type'].startswith('F/1O') and r.get('ara_composite_at_P_F') is not None]
    d_mode_F = [r['ara_mode_F'] for r in all_results
                if r['type'].startswith('F/1O') and r.get('ara_mode_F') is not None]
    d_mode_1O = [r['ara_mode_1O'] for r in all_results
                 if r['type'].startswith('F/1O') and r.get('ara_mode_1O') is not None]

    def stat(arr, label, target):
        if not arr:
            print(f"  {label:38} (no data)")
            return
        m = float(np.mean(arr))
        s = float(np.std(arr))
        dev = abs(m - target) / target * 100
        print(f"  {label:38} mean={m:.3f}  std={s:.3f}  ({dev:.1f}% from {target:.3f})")

    print("F-only Cepheids:")
    stat(f_vals, "raw folded ARA", PHI)
    print()
    print("1O-only Cepheids:")
    stat(o_vals, "raw folded ARA", PHI)
    print()
    print("F/1O double-mode Cepheids:")
    stat(d_comp, "composite (folded at P_F)", PHI_SQ)
    stat(d_mode_F, "isolated mode F (Fourier)", PHI)
    stat(d_mode_1O, "isolated mode 1O (Fourier)", PHI)

    # Save
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cepheid_coupled_pair_data.js')
    payload = {
        'date': '2026-05-11',
        'phi': PHI, 'phi_sq': PHI_SQ,
        'predictions': {
            'single_mode_ara': PHI,
            'double_mode_composite_ara': PHI_SQ,
            'double_mode_isolated_component_ara': PHI,
        },
        'samples': all_results,
        'data_source': 'OGLE-IV Galactic Disk Cepheids (https://www.astrouw.edu.pl/ogle/ogle4/OCVS/gd/cep/)'
    }
    with open(OUT, 'w') as f:
        f.write("window.CEPHEID_COUPLED_PAIR = " + json.dumps(payload, default=str) + ";\n")
    print()
    print(f"Saved -> {OUT}")


if __name__ == '__main__':
    main()
