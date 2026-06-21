"""
multispecies_vertical_ara_test.py

Test the framework's vertical-ARA prediction across mammalian species:
after rescaling each species' time axis by its home rung period,
the local cycle shape (amplitude profile within ±N rungs of peak)
should match across species.

Data: PhysioZoo (PhysioNet) — Mouse, Rabbit, Dog + our existing nsr001 human.
Each species has multiple records (we average across them).

Strict-causal: bandpasses are causal Butterworth IIR. Each species is
processed independently; profiles are compared in dimensionless rung-
relative space.
"""
import os, glob, json
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
# Repo root: parent dir if this script is in TheFormula/, else current dir
REPO_ROOT = _PARENT if os.path.basename(_HERE) == "TheFormula" else _HERE

PHI = 1.6180339887498949

DATA_DIR = os.path.join(REPO_ROOT, "PhysioZoo")
HUMAN_RR = os.path.join(REPO_ROOT, "TheFormula/nsr001_rr.csv")
OUT      = os.path.join(REPO_ROOT, "TheFormula/multispecies_vertical_ara_data.js")

# --- load PhysioZoo peak files ---
def parse_peaks_file(path):
    """Returns (fs_hz, peak_indices) for valid PhysioZoo peak file, or None."""
    with open(path) as f:
        text = f.read()
    if 'Mammal:' not in text:
        return None
    fs = None
    peaks = []
    for line in text.split('\n'):
        s = line.strip()
        if s.startswith('Fs:'):
            fs = int(s.split()[-1])
        elif s and s[0].isdigit():
            try: peaks.append(int(s))
            except: pass
    if fs is None or not peaks: return None
    return fs, np.array(peaks)

species_records = {'Mouse': [], 'Rabbit': [], 'Dog': []}
for path in sorted(glob.glob(os.path.join(DATA_DIR, "peaks_*.txt"))):
    base = os.path.basename(path)
    sp = None
    for s in species_records:
        if base.startswith(f"peaks_{s}_"): sp = s; break
    if sp is None: continue
    parsed = parse_peaks_file(path)
    if parsed is None: continue
    fs, peaks = parsed
    if len(peaks) < 50: continue
    rr_seconds = np.diff(peaks) / fs
    species_records[sp].append((base, fs, peaks, rr_seconds))

print("Loaded records:")
for sp, recs in species_records.items():
    if not recs: continue
    total_peaks = sum(len(r[2]) for r in recs)
    total_dur = sum((r[2][-1] - r[2][0]) / r[1] for r in recs)
    mean_rr = np.mean(np.concatenate([r[3] for r in recs]))
    print(f"  {sp}: {len(recs)} records, {total_peaks} peaks, total {total_dur/60:.1f} min, mean RR = {mean_rr*1000:.1f} ms ({60/mean_rr:.0f} bpm)")

# --- load human nsr001 RR ---
hdf = pd.read_csv(HUMAN_RR)
human_rr_ms = hdf['rr_ms'].values
human_rr_s = human_rr_ms / 1000.0
print(f"  Human nsr001: 1 record, {len(human_rr_ms)} beats, total {sum(human_rr_s)/60:.1f} min, mean RR = {np.mean(human_rr_ms):.1f} ms ({60000/np.mean(human_rr_ms):.0f} bpm)")

# --- build per-species time-grid signal ---
# For each species, concatenate RR intervals into a continuous "RR vs beat-number" time series,
# then resample onto a uniform time grid (in seconds) so we can apply φ-rung bandpass.
def to_uniform_signal(rr_s, dt_s):
    """Convert variable-spaced RR intervals to a uniformly sampled signal in seconds.
       At each time t, signal value = local mean RR (ms) interpolated."""
    t_event = np.cumsum(rr_s)  # time of each beat
    rr_ms_at_event = rr_s * 1000.0
    t_uniform = np.arange(0, t_event[-1] - dt_s, dt_s)
    sig = np.interp(t_uniform, t_event, rr_ms_at_event)
    return t_uniform, sig

species_signals = {}
for sp in ['Mouse', 'Rabbit', 'Dog']:
    if not species_records[sp]: continue
    # concatenate per-record signals
    longest = max(species_records[sp], key=lambda r: r[2][-1])
    rr_s = longest[3]
    mean_rr = float(np.mean(rr_s))
    # dt: 1/10 of mean RR is fine grid
    dt_s = mean_rr / 10
    t, sig = to_uniform_signal(rr_s, dt_s)
    species_signals[sp] = dict(t=t, sig=sig - np.mean(sig), dt=dt_s, mean_rr=mean_rr,
                                home_period_s=mean_rr,
                                duration_s=t[-1])
    print(f"  {sp}: home_period={mean_rr:.3f}s, dt={dt_s:.3f}s, sig_len={len(sig)} samples, dur={t[-1]:.1f}s")

# Add human
mean_rr_human = float(np.mean(human_rr_s))
dt_human = mean_rr_human / 10
t_h, sig_h = to_uniform_signal(human_rr_s, dt_human)
species_signals['Human'] = dict(t=t_h, sig=sig_h - np.mean(sig_h), dt=dt_human,
                                 mean_rr=mean_rr_human, home_period_s=mean_rr_human,
                                 duration_s=t_h[-1])
print(f"  Human: home_period={mean_rr_human:.3f}s, dt={dt_human:.3f}s, sig_len={len(sig_h)} samples, dur={t_h[-1]:.1f}s")

# --- causal bandpass — SOS form for numerical stability at narrow bands ---
def causal_bandpass(arr, period_samples, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_samples; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

# --- per-species amplitude profile across φ-rungs RELATIVE to home period ---
# We sweep relative rungs (rel_k from -3 to +6 around home), compute the RMS amplitude
# of the bandpassed signal at that rung. Then normalize to peak = 1 for each species.

REL_RUNGS = list(range(-3, 20))  # extended out to ~φ^19 (BRAC envelope range for human)

species_profiles = {}
for sp, info in species_signals.items():
    home_p_samples = info['home_period_s'] / info['dt']
    sig = info['sig']
    n_total = len(sig)
    if n_total < 200:
        print(f"  {sp}: skipping (signal too short)")
        continue
    profile = []
    for rk in REL_RUNGS:
        period_samples = home_p_samples * (PHI ** rk)
        # tightened rung-pinning: only test rungs where 4 × period <= signal length
        # (avoids filter instability at edge of stable band)
        if 4 * period_samples > n_total:
            profile.append(np.nan)
            continue
        bp = causal_bandpass(sig, period_samples)
        # Use the warm-stripped tail to compute amplitude
        warm = max(60, int(0.4 * len(bp)))
        amp = float(np.std(bp[warm:]))
        profile.append(amp)
    species_profiles[sp] = profile
    valid = [(rk, a) for rk, a in zip(REL_RUNGS, profile) if not np.isnan(a)]
    if valid:
        peak_rk, peak_amp = max(valid, key=lambda x: x[1])
        print(f"  {sp}: peak at rel_rung={peak_rk:+d} (amp={peak_amp:.2f}), profile pinned at {len(valid)} of {len(REL_RUNGS)} rungs")

# --- normalise each species by its peak and align by peak rung ---
def aligned_normalised(profile):
    arr = np.array(profile, dtype=float)
    if np.all(np.isnan(arr)): return None, None
    peak_idx = int(np.nanargmax(arr))
    peak_val = arr[peak_idx]
    if peak_val < 1e-9: return None, None
    norm = arr / peak_val
    return peak_idx, norm

print("\n=== Per-species peak-aligned normalised amplitude profile ===")
print(f"  rel_rung -> {REL_RUNGS}")
print(f"  rel-to-peak axis (offset by each species' peak rung):")
peaks = {}
profiles_aligned = {}
for sp, prof in species_profiles.items():
    peak_idx, norm = aligned_normalised(prof)
    if norm is None: continue
    peaks[sp] = REL_RUNGS[peak_idx]
    # compute profile re-indexed by offset from peak
    offsets = np.array(REL_RUNGS) - REL_RUNGS[peak_idx]
    profiles_aligned[sp] = dict(offsets=offsets.tolist(), values=norm.tolist())
    fmt = "  ".join(f"{v:.2f}" if not np.isnan(v) else " -- " for v in norm)
    print(f"  {sp:>7} (peak rel-rung={REL_RUNGS[peak_idx]:+d}): {fmt}")

# --- pairwise correlations at peak-aligned rungs (within ±N) ---
def pairwise_within_N(N):
    pairs = []
    species_list = list(profiles_aligned.keys())
    for i, sp1 in enumerate(species_list):
        for sp2 in species_list[i+1:]:
            v1 = np.array(profiles_aligned[sp1]['values'])
            v2 = np.array(profiles_aligned[sp2]['values'])
            o1 = np.array(profiles_aligned[sp1]['offsets'])
            o2 = np.array(profiles_aligned[sp2]['offsets'])
            common_offsets = sorted(set(o1[~np.isnan(v1)]) & set(o2[~np.isnan(v2)]) & set(range(-N, N+1)))
            if len(common_offsets) < 3: continue
            x = np.array([v1[np.where(o1 == o)[0][0]] for o in common_offsets])
            y = np.array([v2[np.where(o2 == o)[0][0]] for o in common_offsets])
            if np.std(x) < 1e-9 or np.std(y) < 1e-9: continue
            corr = float(np.corrcoef(x, y)[0,1])
            mean_diff = float(np.mean(np.abs(x - y)))
            pairs.append((sp1, sp2, len(common_offsets), corr, mean_diff))
    return pairs

print("\n=== Pairwise profile correlation across species (±N rungs of peak) ===")
for N in [2, 3, 5]:
    print(f"\n--- within ±{N} rungs ---")
    print(f"  {'pair':>20}  {'n':>3}  {'corr':>7}  {'mean |Δ|':>9}")
    for sp1, sp2, n, corr, dm in pairwise_within_N(N):
        print(f"  {(sp1+' vs '+sp2):>20}  {n:>3}  {corr:+.3f}  {dm:.3f}")

# --- save ---
out = dict(method="multi-species vertical-ARA — PhysioZoo + nsr001 human",
           species=list(species_signals.keys()),
           home_periods_s={sp: info['home_period_s'] for sp, info in species_signals.items()},
           rel_rungs=REL_RUNGS,
           profiles=species_profiles,
           peaks=peaks,
           profiles_aligned=profiles_aligned,
           pairs_pm2=pairwise_within_N(2),
           pairs_pm3=pairwise_within_N(3),
           pairs_pm5=pairwise_within_N(5))
with open(OUT, 'w') as f:
    f.write("window.MULTISPECIES = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
{OUT}")
