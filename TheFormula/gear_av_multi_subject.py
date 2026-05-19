"""gear_av_multi_subject.py — multi-subject AV-node hidden-coupler test.

Run the same AV-node gear-mechanical test across multiple NSR ECG subjects.
Check if framework predictions (stable coupler, sized gear, delay-attenuation
correlation) hold reproducibly.
"""
import os, glob
import numpy as np
import wfdb
from scipy.signal import find_peaks, butter, sosfiltfilt

NSR_DIR = '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0'
def log(s): print(s, flush=True)

# Find ECG records (the .hea files define each record)
hea_files = sorted(glob.glob(os.path.join(NSR_DIR, '*.hea')))
log(f'Found {len(hea_files)} NSR record headers')

def test_subject(record_path):
    try:
        # Load up to 30 sec of ECG
        rec = wfdb.rdrecord(record_path, sampto=30000)
        if rec.p_signal is None or rec.p_signal.shape[1] == 0: return None
        FS = int(rec.fs)
        ecg = rec.p_signal[:, 0].astype(float)
    except Exception as e:
        return {'error': str(e)}
    
    # High-pass filter
    sos = butter(4, 0.5/(FS/2), btype='high', output='sos')
    ecg_hp = sosfiltfilt(sos, ecg)
    
    # R-peaks
    thresh = np.percentile(ecg_hp, 95) * 0.5
    r_peaks, _ = find_peaks(ecg_hp, height=thresh, distance=int(0.4*FS))
    if len(r_peaks) < 30: return None
    
    P_START = int(0.20*FS); P_END = int(0.08*FS)
    R_BL_BACK = int(0.30*FS); R_BL_FRONT = int(0.20*FS)
    
    p_amps, r_amps, pr_ratios, pr_ints = [], [], [], []
    for ri in r_peaks:
        if ri - R_BL_BACK < 0 or ri + 5 >= len(ecg_hp): continue
        p_win = ecg_hp[ri-P_START:ri-P_END]
        if len(p_win) < 5: continue
        p_amp = p_win.max() - np.median(p_win)
        r_bl = np.median(ecg_hp[ri-R_BL_BACK:ri-R_BL_FRONT])
        r_amp = ecg_hp[ri] - r_bl
        if r_amp <= 0: continue
        p_amps.append(p_amp); r_amps.append(r_amp); pr_ratios.append(p_amp/r_amp)
        pr_ints.append((ri - (np.argmax(p_win) + ri-P_START))/FS*1000)
    
    if len(pr_ratios) < 20: return None
    pr_ratios = np.array(pr_ratios); pr_ints = np.array(pr_ints)
    return {
        'n_beats': len(pr_ratios),
        'hr_bpm': 60*FS*len(r_peaks)/len(ecg),
        'pr_ratio_mean': float(pr_ratios.mean()),
        'pr_ratio_cv': float(pr_ratios.std()/pr_ratios.mean()) if pr_ratios.mean() > 0 else 0,
        'pr_interval_mean': float(pr_ints.mean()),
        'pr_interval_cv': float(pr_ints.std()/pr_ints.mean()) if pr_ints.mean() > 0 else 0,
        'correlation': float(np.corrcoef(pr_ints, pr_ratios)[0,1]) if pr_ints.std()>0 and pr_ratios.std()>0 else 0,
    }

# Test up to 10 subjects
log(f'\n{"subject":>12} | {"n_beats":>8} | {"HR (bpm)":>9} | {"P/R mean":>9} | {"P/R CV":>7} | {"PR (ms)":>8} | {"PR CV":>6} | {"PR↔P/R corr":>12}')
log('-'*100)

results = []
for hea in hea_files[:10]:
    rec_name = os.path.splitext(os.path.basename(hea))[0]
    record_path = os.path.join(NSR_DIR, rec_name)
    r = test_subject(record_path)
    if r is None: continue
    if 'error' in r:
        log(f'{rec_name:>12} | ERROR: {r["error"][:60]}')
        continue
    log(f'{rec_name:>12} | {r["n_beats"]:>8d} | {r["hr_bpm"]:>9.1f} | {r["pr_ratio_mean"]:>9.4f} | {r["pr_ratio_cv"]:>7.3f} | {r["pr_interval_mean"]:>8.1f} | {r["pr_interval_cv"]:>6.3f} | {r["correlation"]:>+12.3f}')
    results.append(r)

if results:
    pr_means = np.array([r['pr_ratio_mean'] for r in results])
    pr_cvs = np.array([r['pr_ratio_cv'] for r in results])
    pri_means = np.array([r['pr_interval_mean'] for r in results])
    pri_cvs = np.array([r['pr_interval_cv'] for r in results])
    corrs = np.array([r['correlation'] for r in results])
    
    log(f'\n=== AGGREGATE ACROSS {len(results)} SUBJECTS ===')
    log(f'P/R ratio:    mean = {pr_means.mean():.4f}, range [{pr_means.min():.4f}, {pr_means.max():.4f}], across-subject CV = {pr_means.std()/pr_means.mean():.3f}')
    log(f'P/R ratio CV: mean = {pr_cvs.mean():.3f}  (low CV = within-subject coupler stability)')
    log(f'PR interval:  mean = {pri_means.mean():.1f} ms, range [{pri_means.min():.1f}, {pri_means.max():.1f}], across-subject CV = {pri_means.std()/pri_means.mean():.3f}')
    log(f'PR interval CV: mean = {pri_cvs.mean():.3f}  (low CV = stable conduction)')
    log(f'PR↔P/R correlation: mean = {corrs.mean():+.3f}, range [{corrs.min():+.3f}, {corrs.max():+.3f}]')
    log(f'  Subjects with NEGATIVE correlation (framework-predicted direction): {(corrs<0).sum()}/{len(corrs)}')
    log(f'')
    log(f'=== FRAMEWORK PREDICTION CHECK ===')
    log(f'1. PR interval mean within clinical norm 120-200ms: {(120 <= pri_means.mean() <= 200)} ({pri_means.mean():.0f}ms)')
    log(f'2. P/R ratio non-trivial gear ratio (<0.5, not π-leak): all subjects {(pr_means < 0.5).all()}')
    log(f'3. PR interval CV stable (<0.2): {(pri_cvs < 0.2).all()} (mean {pri_cvs.mean():.3f})')
    log(f'4. PR↔P/R correlation negative (predicted direction): {(corrs<0).sum()}/{len(corrs)} subjects')

log('\n=== Done ===')
