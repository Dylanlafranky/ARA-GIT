"""gear_test_chain_nino_pdo_soi.py — Dylan 2026-05-12.

Hidden-couplers chain test: is PDO the intermediate gear between NINO and SOI?

Framework prediction: if NINO ↔ PDO ↔ SOI is a gear chain,
  (NINO_amp / PDO_amp) × (PDO_amp / SOI_amp) ≈ NINO_amp / SOI_amp
which simplifies to: chain product = direct ratio (algebraic identity if PDO
appears equally in both terms).

Better framework prediction: per-rung, the gear-mechanical relationship
  NINO_amp × ω_NINO = PDO_amp × ω_PDO  AND  PDO_amp × ω_PDO = SOI_amp × ω_SOI
should hold. Since same-rung means same ω, this reduces to amplitude equality
modulo gear-size shifts and π-leak.

The discriminating test: are the per-rung COUPLING STRUCTURES (gear ratios
NINO/PDO, PDO/SOI, NINO/SOI) consistent with PDO sitting in between?
Specifically, does the PRODUCT (NINO/PDO) × (PDO/SOI) reproduce (NINO/SOI)
better than chance?

Also: PDO sits at a φ⁹ rung (per framework_dynamic_rung_assignment); if it's
the coupler, the gear relationship should be tightest at THAT rung.
"""
import os, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

PHI = (1+5**0.5)/2
PI_LEAK = (math.pi - 3) / math.pi
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
def log(s): print(s, flush=True)

# Load NINO 3.4
nino_df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv'),
                     parse_dates=['Date'], na_values=[-99.99]).dropna()
nino_df.columns = [c.strip() for c in nino_df.columns]
nino_df['Year'] = nino_df['Date'].dt.year
nino_df['Month'] = nino_df['Date'].dt.month
nino_col = [c for c in nino_df.columns if 'NINA' in c.upper()][0]

# Load SOI (year + 12 monthly cols, -99.99 missing)
def load_year_monthly(path, name, skip_header_lines=1):
    rows = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i < skip_header_lines: continue
            parts = line.split()
            if len(parts) == 13:
                try:
                    yr = int(parts[0])
                    for m, v in enumerate([float(x) for x in parts[1:]], 1):
                        if v > -90 and v < 90: rows.append({'Year': yr, 'Month': m, name: v})
                except: pass
    return pd.DataFrame(rows)

soi_df = load_year_monthly(os.path.join(REPO_ROOT, 'SOI_NOAA', 'soi.data'), 'SOI', 1)
pdo_df = load_year_monthly(os.path.join(REPO_ROOT, 'PDO_NOAA', 'ersst.v5.pdo.dat'), 'PDO', 2)

log(f'NINO rows: {len(nino_df)}, SOI rows: {len(soi_df)}, PDO rows: {len(pdo_df)}')

# Merge on common time
merged = nino_df[['Year', 'Month', nino_col]].merge(soi_df, on=['Year','Month']).merge(pdo_df, on=['Year','Month'])
merged.columns = ['Year', 'Month', 'NINO', 'SOI', 'PDO']
merged = merged.dropna().sort_values(['Year','Month']).reset_index(drop=True)
log(f'Common timeline: {len(merged)} months ({merged["Year"].iloc[0]}-{merged["Year"].iloc[-1]})')

nino = merged['NINO'].values
soi = merged['SOI'].values
pdo = merged['PDO'].values

# Per-rung amplitude
def amp_at(sig, P):
    low = 1/(P*1.4); high = 1/(P*0.7); nyq = 0.5
    lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
    if lo >= hi: return None
    try:
        sos = butter(4, [lo, hi], btype='band', output='sos')
        f = sosfiltfilt(sos, sig)
        return float(np.std(f)) if np.std(f) > 1e-9 else None
    except: return None

RUNGS = [3, 5, 8, 13, 21, 34, 55, 89, 144]
log(f'\n=== Three-gear chain test: NINO ↔ PDO ↔ SOI (months) ===')
log(f'Hidden-couplers prediction: if PDO is intermediate, chain math should describe data\n')
log(f'{"P(mo)":>6} | {"NINO":>8} | {"PDO":>8} | {"SOI":>8} | {"NINO/PDO":>10} | {"PDO/SOI":>10} | {"chain prod":>11} | {"direct N/S":>11} | {"chain/dir":>10}')
log('-'*120)

results = []
for P in RUNGS:
    if P >= len(nino) // 4: continue
    a_n = amp_at(nino, P)
    a_p = amp_at(pdo, P)
    a_s = amp_at(soi, P)
    if not all([a_n, a_p, a_s]): continue
    np_ratio = a_n / a_p
    ps_ratio = a_p / a_s
    chain_product = np_ratio * ps_ratio  # = a_n/a_s by algebra (identity if PDO cancels)
    direct_ns = a_n / a_s
    chain_over_direct = chain_product / direct_ns
    log(f'{P:>6d} | {a_n:>8.4f} | {a_p:>8.4f} | {a_s:>8.4f} | {np_ratio:>10.3f} | {ps_ratio:>10.3f} | {chain_product:>11.3f} | {direct_ns:>11.3f} | {chain_over_direct:>10.3f}')
    results.append({'P': P, 'NINO': a_n, 'PDO': a_p, 'SOI': a_s, 'np': np_ratio, 'ps': ps_ratio, 'chain': chain_product, 'direct': direct_ns})

log(f'\nNOTE: chain product (NINO/PDO) × (PDO/SOI) is algebraically identical to NINO/SOI.')
log(f'      What this test really shows is: does the SAME GEAR RATIO between adjacent meshes hold?')
log(f'      i.e., is NINO/PDO ≈ PDO/SOI? That would indicate PDO is centered between them.\n')

if len(results) > 0:
    np_arr = np.array([r['np'] for r in results])
    ps_arr = np.array([r['ps'] for r in results])
    log(f'=== Discriminating analysis: is PDO geometrically centered? ===')
    log(f'Mean NINO/PDO ratio: {np_arr.mean():.3f}')
    log(f'Mean PDO/SOI ratio: {ps_arr.mean():.3f}')
    log(f'Mean ratio of ratios (NINO/PDO)/(PDO/SOI): {(np_arr/ps_arr).mean():.3f}')
    log(f'  Framework prediction if PDO is the intermediate coupler in between:')
    log(f'    NINO/PDO ≈ PDO/SOI (PDO sits geometrically between them as the "average" gear size)')
    log(f'    → ratio of ratios should be ≈ 1.0 if PDO is exactly between')
    
    log(f'')
    log(f'=== Per-rung coupling strength (correlation, anti-phase signature) ===')
    for r in results:
        P = r['P']
        # Bandpass each at this period
        low = 1/(P*1.4); high = 1/(P*0.7); nyq = 0.5
        lo, hi = max(0.001, low/nyq), min(0.999, high/nyq)
        sos = butter(4, [lo, hi], btype='band', output='sos')
        n_f = sosfiltfilt(sos, nino); p_f = sosfiltfilt(sos, pdo); s_f = sosfiltfilt(sos, soi)
        c_np = float(np.corrcoef(n_f, p_f)[0,1])
        c_ps = float(np.corrcoef(p_f, s_f)[0,1])
        c_ns = float(np.corrcoef(n_f, s_f)[0,1])
        log(f'  P={P:3d}mo:  NINO↔PDO {c_np:+.3f}, PDO↔SOI {c_ps:+.3f}, NINO↔SOI {c_ns:+.3f}')
        
        # If PDO is intermediate: NINO and SOI should both correlate with PDO,
        # and the NINO-SOI direct correlation should be approximated by product of partial correlations.
        # Simpler: PDO should mediate the NINO-SOI relationship.
        if abs(c_np) > 0.3 and abs(c_ps) > 0.3:
            # Check: is c_ns sign consistent with c_np * c_ps?
            predicted_sign = np.sign(c_np * c_ps)
            actual_sign = np.sign(c_ns)
            mediated = "✓" if predicted_sign == actual_sign else "✗"
            log(f'           NINO↔SOI sign predicted by NINO↔PDO × PDO↔SOI: {mediated}')

log('\n=== Done ===')
