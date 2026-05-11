"""Lung breath shape vs forest year-cycle shape (BIDMC + Mauna Loa)."""
import os, json, math
import numpy as np
import requests
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import wfdb

PHI = (1 + 5**0.5) / 2

# 1. LUNG
print("[1/4] Loading lung respiration (BIDMC)...")
N = 3
breath_shapes = []
sub_breaths = []
for i in range(1, N+1):
    sid = f'bidmc{i:02d}'
    try:
        r = wfdb.rdrecord(sid, pn_dir='bidmc')
    except Exception as e:
        print(f'  {sid}: {e}'); continue
    ri = next((j for j,n in enumerate(r.sig_name) if n.startswith('RESP')), None)
    if ri is None: continue
    sig = r.p_signal[:, ri]; fs = r.fs
    sm = gaussian_filter1d(sig, max(1, int(fs*0.2)))
    troughs, _ = find_peaks(-sm, distance=int(fs*2))
    n_b = 0
    for k in range(len(troughs)-1):
        a, b = troughs[k], troughs[k+1]
        if b-a < int(fs*2.5) or b-a > int(fs*8): continue
        cyc = sig[a:b]
        xo = np.linspace(0,1,len(cyc)); xn = np.linspace(0,1,100)
        c = np.interp(xn, xo, cyc)
        c = (c - c.min()) / max(1e-9, c.max()-c.min())
        breath_shapes.append(c); n_b += 1
    sub_breaths.append((sid, n_b))
    print(f'  {sid}: {n_b} breaths')
breath_shapes = np.array(breath_shapes)
print(f'  Total: {len(breath_shapes)} breaths')
mean_breath = breath_shapes.mean(axis=0)

# 2. FOREST
print("\n[2/4] Loading Mauna Loa CO2 monthly...")
rr = requests.get('https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt',
                  timeout=20, headers={'User-Agent':'Mozilla/5.0'})
rows = []
for line in rr.text.split('\n'):
    if line.startswith('#') or not line.strip(): continue
    p = line.split()
    if len(p) >= 6:
        try:
            rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3])))
        except: pass
co2 = np.array(rows, dtype=float)
print(f'  {len(co2)} months, {co2[0,0]:.0f}-{co2[-1,0]:.0f}')

raw = co2[:, 3]
window = 60
trend = np.convolve(raw, np.ones(window)/window, mode='same')
detr = raw - trend
months = co2[:, 1].astype(int)
year12 = np.zeros(12); count = np.zeros(12)
for i in range(len(co2)):
    m = months[i] - 1
    year12[m] += detr[i]; count[m] += 1
year12 /= np.maximum(count, 1)
xo = np.linspace(0,1,12); xn = np.linspace(0,1,100)
year100 = np.interp(xn, xo, year12)
year_norm = (year100 - year100.min()) / max(1e-9, year100.max() - year100.min())
print(f'  CO2 year-cycle: peak month {int(np.argmax(year12)+1)}, trough month {int(np.argmin(year12)+1)}')

# 3. SHAPE COMPARISON
print("\n[3/4] Comparing shapes...")
bp = int(np.argmax(mean_breath))
yp = int(np.argmax(year_norm))
print(f'  breath peak at phase {bp}/100, year peak at phase {yp}/100')
shift = bp - yp
year_aligned = np.roll(year_norm, shift)

def corr(a, b):
    return float(np.corrcoef(a, b)[0,1])

# direct: breath = lung volume, year = atmospheric CO2 (winter high)
# But "lung volume up" corresponds to "biomass up" not "CO2 up"
# Atmospheric CO2 is INVERSE of biomass cycle (biomass rises in growing season = CO2 falls)
# So compare mean_breath (volume) to INVERTED year (biomass-direction)
year_biomass = 1.0 - year_norm
yb_peak = int(np.argmax(year_biomass))
year_biomass_aligned = np.roll(year_biomass, bp - yb_peak)

c_co2 = corr(mean_breath, year_aligned)
c_biomass = corr(mean_breath, year_biomass_aligned)

# Asymmetry: fraction of cycle on rise side (trough to peak) vs fall side
def asym(shape):
    p = int(np.argmax(shape)); t = int(np.argmin(shape)); n = len(shape)
    if p > t:
        rise = p - t; fall = (n - p) + t
    else:
        rise = (n - t) + p; fall = t - p
    return fall / rise if rise > 0 else float('nan')

a_breath = asym(mean_breath)
a_year = asym(year_norm)
a_biomass = asym(year_biomass)

# 4. REPORT
print("\n[4/4] RESULTS")
print('='*70)
print(f'  Breath asymmetry (T_fall/T_rise):           {a_breath:.3f}')
print(f'  Year-cycle CO2 asymmetry:                    {a_year:.3f}')
print(f'  Year-cycle BIOMASS asymmetry (inverted CO2): {a_biomass:.3f}')
print(f'  φ = {PHI:.3f}')
print()
print(f'  Shape correlation: breath vs CO2 direction:   {c_co2:+.3f}')
print(f'  Shape correlation: breath vs BIOMASS direction: {c_biomass:+.3f}')
print()
mx = max(abs(c_co2), abs(c_biomass))
direction = 'biomass-direction' if abs(c_biomass) > abs(c_co2) else 'CO2-direction'
if mx > 0.7:
    print(f'  → STRONG shape match ({direction}). Templates overlay after time-rescaling.')
elif mx > 0.4:
    print(f'  → MODERATE shape match ({direction}). Templates are related.')
else:
    print(f'  → Weak shape match. Shapes diverge.')

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lung_forest_shape_match_data.js')
with open(OUT, 'w') as f:
    f.write("window.LUNG_FOREST_SHAPE = " + json.dumps(dict(
        date='2026-05-11',
        n_breaths=int(len(breath_shapes)),
        n_subjects=len(sub_breaths),
        n_co2_months=int(len(co2)),
        n_co2_years=int(co2[-1,0]-co2[0,0]),
        mean_breath=[float(x) for x in mean_breath],
        year_cycle_co2=[float(x) for x in year_norm],
        year_cycle_biomass=[float(x) for x in year_biomass],
        year_aligned_to_breath=[float(x) for x in year_aligned],
        biomass_aligned_to_breath=[float(x) for x in year_biomass_aligned],
        corr_breath_co2=c_co2,
        corr_breath_biomass=c_biomass,
        breath_asymmetry=float(a_breath),
        year_co2_asymmetry=float(a_year),
        year_biomass_asymmetry=float(a_biomass),
        phi=PHI,
    ), default=str) + ";\n")
print(f'\nSaved -> {OUT}')
