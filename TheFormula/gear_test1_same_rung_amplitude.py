"""gear_test1_same_rung_amplitude.py — Dylan 2026-05-12.

Test 1 from framework_gear_mechanics_anchor.md:
For known anti-phase matched-rung pair (NINO 3.4 ↔ SOI), the gear law predicts
gear ratio = 1 (same rung), so amplitudes at each rung should be ≈ equal.

Also sanity-check: anti-phase coupling correlation should be strongly negative
at the matched rungs (already documented but re-verifying).
"""
import os, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1+5**0.5)/2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
def log(s): print(s, flush=True)

# ============================================================================
# Load NINO 3.4
# ============================================================================
nino_df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv'),
                     parse_dates=['Date'], na_values=[-99.99])
nino_df.columns = [c.strip() for c in nino_df.columns]
nino_df = nino_df.dropna()
nino_df['Year'] = nino_df['Date'].dt.year
nino_df['Month'] = nino_df['Date'].dt.month
nino_col = [c for c in nino_df.columns if 'NINA' in c.upper() or 'NINO' in c.upper()][0]
log(f'NINO column: {nino_col}, rows: {len(nino_df)}, {nino_df["Date"].min()} → {nino_df["Date"].max()}')

# ============================================================================
# Load SOI (space-delimited, year + 12 monthly cols)
# ============================================================================
soi_rows = []
with open(os.path.join(REPO_ROOT, 'SOI_NOAA', 'soi.data')) as f:
    for line in f:
        parts = line.split()
        if len(parts) == 13:
            try:
                yr = int(parts[0])
                vals = [float(v) for v in parts[1:]]
                for m, v in enumerate(vals, 1):
                    if v > -90:  # filter missing
                        soi_rows.append({'Year': yr, 'Month': m, 'SOI': v})
            except: pass
soi_df = pd.DataFrame(soi_rows)
log(f'SOI rows: {len(soi_df)}, {soi_df["Year"].min()} → {soi_df["Year"].max()}')

# ============================================================================
# Align on common time range
# ============================================================================
merged = pd.merge(nino_df[['Year', 'Month', nino_col]], soi_df, on=['Year', 'Month']).sort_values(['Year', 'Month'])
merged.columns = ['Year', 'Month', 'NINO', 'SOI']
merged = merged.dropna()
nino = merged['NINO'].values
soi = merged['SOI'].values
log(f'Common range: {len(merged)} months, {merged["Year"].iloc[0]}-{merged["Month"].iloc[0]:02d} → {merged["Year"].iloc[-1]}-{merged["Month"].iloc[-1]:02d}')
log(f'NINO mean={nino.mean():.3f}, std={nino.std():.3f}')
log(f'SOI  mean={soi.mean():.3f}, std={soi.std():.3f}')
log(f'Overall NINO↔SOI corr: {np.corrcoef(nino, soi)[0,1]:+.3f}  (anti-phase signature)')

# ============================================================================
# Per-rung amplitude (std) + per-rung NINO↔SOI correlation
# ============================================================================
def bandpass_amp_and_filtered(sig, P):
    low = 1/(P*1.4); high = 1/(P*0.7); nyq = 0.5
    lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
    if lo >= hi: return None, None
    try:
        sos = butter(4, [lo, hi], btype='band', output='sos')
        f = sosfiltfilt(sos, sig)
        if np.std(f) < 1e-9: return None, None
        return float(np.std(f)), f
    except: return None, None

# Fibonacci periods in months (φ-rungs)
RUNGS_MONTHS = [3, 5, 8, 13, 21, 34, 55, 89, 144]

log(f'\n=== TEST 1: Gear-law same-rung amplitude equality (NINO ↔ SOI) ===')
log(f'{"Period (months)":>15} | {"NINO amp":>10} | {"SOI amp":>10} | {"ratio NINO/SOI":>16} | {"|deviation from 1|":>20} | {"per-rung corr":>14}')
log('-'*100)

results = []
for P in RUNGS_MONTHS:
    if P >= len(nino) // 4: continue  # need at least 4 cycles
    n_amp, n_filt = bandpass_amp_and_filtered(nino, P)
    s_amp, s_filt = bandpass_amp_and_filtered(soi, P)
    if n_amp is None or s_amp is None: continue
    ratio = n_amp / s_amp
    dev = abs(ratio - 1.0)
    per_rung_corr = float(np.corrcoef(n_filt, s_filt)[0, 1])
    log(f'{P:>15d} | {n_amp:>10.4f} | {s_amp:>10.4f} | {ratio:>16.3f} | {dev:>20.3f} | {per_rung_corr:>+14.3f}')
    results.append({'P': P, 'nino_amp': n_amp, 'soi_amp': s_amp, 'ratio': ratio, 'dev': dev, 'corr': per_rung_corr})

# ============================================================================
# Verdict
# ============================================================================
if results:
    ratios = [r['ratio'] for r in results]
    devs = [r['dev'] for r in results]
    corrs = [r['corr'] for r in results]
    log(f'\n=== VERDICT ===')
    log(f'Mean ratio NINO/SOI:        {np.mean(ratios):.3f}')
    log(f'Mean |dev from 1.0|:        {np.mean(devs):.3f}')
    log(f'Median ratio:               {np.median(ratios):.3f}')
    log(f'Mean per-rung corr:         {np.mean(corrs):+.3f}  (negative = anti-phase, as framework predicts)')
    log(f'')
    log(f'Gear-law prediction: ratio ≈ 1.0 (same rung → gear ratio 1 → equal amplitudes).')
    if np.mean(devs) < 0.2:
        log(f'  ✓ STRONG fit: mean deviation {np.mean(devs):.3f} < 0.2')
    elif np.mean(devs) < 0.5:
        log(f'  ~ MODERATE fit: mean deviation {np.mean(devs):.3f} (0.2 to 0.5)')
    else:
        log(f'  ✗ POOR fit: mean deviation {np.mean(devs):.3f} > 0.5')
    log(f'')
    log(f'Anti-phase coupling sanity check: mean per-rung corr = {np.mean(corrs):+.3f}')
    if np.mean(corrs) < -0.5:
        log(f'  ✓ Strong anti-phase coupling confirmed')
    elif np.mean(corrs) < -0.2:
        log(f'  ~ Moderate anti-phase coupling')
    else:
        log(f'  ✗ Anti-phase coupling weaker than expected')

log('\n=== Done ===')
