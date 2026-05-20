"""Universal Cascade v3 — ports Compass + φ-Tube Ensemble mechanics
into a system-agnostic class, with HONEST AR memory (no future leakage).

Architecture (all universal — no system-specific code):
  1. Configurable rung ladder (default 10 rungs spanning φ^(-k_span/2) to φ^(k_span/2))
  2. Per-rung phase state (amp, theta) read causally from bandpass
  3. Per-rung ARA computed causally from peak-shape asymmetry
  4. ARA-driven valves: g = ½(1+tanh(5·(cos+1−2v)))  per rung
  5. Cross-rung 1/φ⁴ damping (Three-Circles)
  6. Generalized anti-phase feeder coupling (Walker-Circulation pattern, system-agnostic)
  7. Compass tick: step = step_mean × tanh(Δ/step_mean), walked forward h steps
  8. Elastic walls at ±wall_sigma·σ with elasticity 1/φ
  9. AR memory γ = 1/φ³ × honest short-horizon residual (Pattern B)
 10. 9-perturbation ensemble along amp (Y) and phase (Z) axes at home rung
 11. Output: ensemble mean + ensemble σ uncertainty band

Default test: ENSO 2001-2025 blind, identical protocol to past best.
"""
import os, math, time
import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = (1 + 5**0.5) / 2
INV_PHI = 1.0 / PHI
INV_PHI3 = 1.0 / (PHI**3)
INV_PHI4 = 1.0 / (PHI**4)


def causal_bandpass(arr, period_units, bw=0.4, order=2):
    """Causal bandpass — no future leakage (uses lfilter, not filtfilt)."""
    n = len(arr); fc = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*fc/nyq); Wn_hi = min(0.999, (1+bw)*fc/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
    return lfilter(b, a, arr - np.mean(arr))


def read_amp_theta(bp_signal, recent_window=50):
    """Read instantaneous amplitude and phase from end of a bandpassed signal."""
    if len(bp_signal) < 2: return 0.0, 0.0
    r = min(recent_window, len(bp_signal))
    amp = float(np.std(bp_signal[-r:]) * np.sqrt(2)) + 1e-9
    last = bp_signal[-1]; rate = bp_signal[-1] - bp_signal[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)


def per_rung_ARA_causal(arr_train, period):
    """Compute ARA at a rung from peak-shape asymmetry (causal)."""
    bp = causal_bandpass(arr_train, period, bw=0.85)
    if len(bp) < 3 * int(period): return 1.0
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2: return 1.0
    aras = []
    for i in range(len(peaks)-1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg)-1)))
        aras.append((1 - f_t) / f_t)
    if not aras: return 1.0
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


class UniversalCascadeV3:
    """System-agnostic compass + ensemble cascade.

    Same class, different ARA/period for different systems.
    No system-specific code. All framework constants explicit.
    """
    def __init__(self,
                 dom_P,                  # dominant period of target system
                 k_span=(4, 14),         # rung range as k integers (PHI**k for periods)
                 k_ref=None,             # home rung (default: middle of span)
                 wall_sigma=1.5,         # elastic walls at ±wall_sigma · σ
                 gamma=INV_PHI3,         # AR memory weight (framework constant)
                 ensemble=True,          # use 9-perturbation ensemble
                 feeder_coupling_strength=5.0,  # K_REF amplification for anti-phase feeders
                 ):
        self.dom_P = dom_P
        self.k_span = k_span
        self.rungs = [(k, dom_P * (PHI ** (k - k_span[0] - (k_span[1]-k_span[0])//2)))
                      for k in range(k_span[0], k_span[1])]
        # Above puts k_ref at middle; cleaner: just use raw k and a configurable k_ref
        # Override: cleaner construction
        self.rungs = [(k, PHI ** k) for k in range(k_span[0], k_span[1])]
        self.n_rungs = len(self.rungs)
        if k_ref is None:
            k_ref = (k_span[0] + k_span[1]) // 2
        self.k_ref = k_ref
        self.k_ref_idx = next(i for i, (k, _) in enumerate(self.rungs) if k == k_ref)
        # Log-distance rung weights
        rw = np.array([1.0 / (1.0 + np.log(abs(k - k_ref) + 1)) for k, _ in self.rungs])
        self.rung_weights = rw / np.sum(rw)
        self.wall_sigma = wall_sigma
        self.gamma = gamma
        self.ensemble = ensemble
        self.feeder_coupling_strength = feeder_coupling_strength

    # ---------- State and prediction ----------
    def _read_state(self, arr_train, feeders_train):
        """Read current oscillator state from training-only data (CAUSAL)."""
        state = {}
        # Target
        for ri, (k, p) in enumerate(self.rungs):
            bp = causal_bandpass(arr_train, p)
            a, th = read_amp_theta(bp)
            state[('target', ri)] = (a, th)
        # Feeders
        for fname, farr in feeders_train.items():
            for ri, (k, p) in enumerate(self.rungs):
                bp = causal_bandpass(farr, p)
                a, th = read_amp_theta(bp)
                state[(fname, ri)] = (a, th)
        return state

    def _read_valves(self, arr_train):
        """Per-rung ARA-driven valve (causal)."""
        valves = []
        for k, p in self.rungs:
            ara_k = per_rung_ARA_causal(arr_train, p)
            valves.append(1.0 / (1.0 + ara_k))
        return valves

    def _amp_predict(self, state, h, mean_train, valves,
                     feeder_scales, target_scale):
        """Predict amplitude at h steps ahead from oscillator state."""
        target_rung_future = []
        cos_vals = []
        for ri, (k, p) in enumerate(self.rungs):
            a, th = state[('target', ri)]
            new_th = th + 2 * np.pi * h / p
            cos_val = np.cos(new_th)
            cos_vals.append(cos_val)
            v = valves[ri]
            g = 0.5 * (1 + np.tanh(5.0 * (cos_val + (1 - 2*v))))
            target_rung_future.append(a * cos_val * g)
        target_rung_future = np.array(target_rung_future)
        # Cross-rung 1/φ⁴ damping (Three-Circles)
        for ri in range(self.n_rungs - 1):
            a1 = state[('target', ri)][0]
            a2 = state[('target', ri+1)][0]
            target_rung_future[ri] += INV_PHI4 * a1 * a2 * cos_vals[ri] * cos_vals[ri+1]
        own_pred = float(np.dot(self.rung_weights, target_rung_future))

        # Generalized anti-phase feeder coupling
        feeder_pred = 0.0
        for fname, fscale in feeder_scales.items():
            f_norm = []
            for ri, (k, p) in enumerate(self.rungs):
                a_f, th_f = state[(fname, ri)]
                proj = a_f * np.cos(th_f + 2 * np.pi * h / p)
                f_norm.append(proj / fscale * target_scale)
            f_norm = np.array(f_norm)
            # K_REF matched-rung amplification
            feeder_pred += -1.0 * f_norm[self.k_ref_idx] * self.rung_weights[self.k_ref_idx] * self.feeder_coupling_strength
            # Off-rung decay (1/φ^|Δk| × 1/φ⁴)
            for ri in range(self.n_rungs):
                if ri == self.k_ref_idx: continue
                feeder_pred += -1.0 * (INV_PHI ** abs(self.rungs[ri][0] - self.k_ref)) * INV_PHI4 * f_norm[ri] * self.rung_weights[ri]
        return mean_train + own_pred + feeder_pred

    def _compass_walk(self, h, state, mean_train, valves,
                      feeder_scales, target_scale,
                      start_pos, step_mean, wall_high, wall_low,
                      last_residual):
        """Walk forward h steps with tanh-bounded compass ticks and elastic walls."""
        cur_pos = start_pos
        prev_amp = start_pos
        for tau in range(1, h+1):
            amp = self._amp_predict(state, tau, mean_train, valves, feeder_scales, target_scale)
            amp += self.gamma * last_residual  # AR memory inside the walk
            delta = amp - prev_amp
            step = step_mean * np.tanh(delta / max(step_mean, 1e-9))
            new_pos = cur_pos + step
            if new_pos > wall_high:
                new_pos = wall_high - (new_pos - wall_high) * INV_PHI
            elif new_pos < wall_low:
                new_pos = wall_low + (wall_low - new_pos) * INV_PHI
            cur_pos = new_pos
            prev_amp = amp
        return cur_pos

    def _perturbed_state(self, base_state, kind):
        """Perturb the home rung along amp/phase axes."""
        if kind == 'baseline':
            return base_state
        new_state = dict(base_state)
        a, th = base_state[('target', self.k_ref_idx)]
        if kind == 'Y+':   new_state[('target', self.k_ref_idx)] = (a * 1.3, th)
        elif kind == 'Y-': new_state[('target', self.k_ref_idx)] = (a * 0.7, th)
        elif kind == 'Z+': new_state[('target', self.k_ref_idx)] = (a, th + np.pi/4)
        elif kind == 'Z-': new_state[('target', self.k_ref_idx)] = (a, th - np.pi/4)
        elif kind == 'YZ++': new_state[('target', self.k_ref_idx)] = (a * 1.2, th + np.pi/6)
        elif kind == 'YZ+-': new_state[('target', self.k_ref_idx)] = (a * 1.2, th - np.pi/6)
        elif kind == 'YZ-+': new_state[('target', self.k_ref_idx)] = (a * 0.8, th + np.pi/6)
        elif kind == 'YZ--': new_state[('target', self.k_ref_idx)] = (a * 0.8, th - np.pi/6)
        return new_state

    PERTURBATIONS = ['baseline', 'Y+', 'Y-', 'Z+', 'Z-', 'YZ++', 'YZ+-', 'YZ-+', 'YZ--']

    # ---------- Rolling forecast ----------
    def rolling_forecast(self, full_target, feeders_full, train_end, horizons):
        """Run rolling-origin forecast with strict causal/honest protocol.

        Returns: dict[horizon] -> list of (refit_t, ens_mean, ens_std, baseline_pred, truth)
        """
        N = len(full_target)
        results = {h: [] for h in horizons}
        last_residual = 0.0  # honest pattern-B AR

        for refit_t in range(train_end, N - max(horizons)):
            # Causal: only use data up to refit_t (exclusive of refit_t? — past code used [:refit_t])
            arr_train = full_target[:refit_t]
            feeders_train = {fn: fa[:refit_t] for fn, fa in feeders_full.items()}

            mean_train = float(np.mean(arr_train))
            sigma_train = float(np.std(arr_train))
            target_scale = sigma_train + 1e-9
            feeder_scales = {fn: float(np.std(fa)) + 1e-9 for fn, fa in feeders_train.items()}
            step_mean = float(np.mean(np.abs(np.diff(arr_train))))
            wall_high = mean_train + self.wall_sigma * sigma_train
            wall_low = mean_train - self.wall_sigma * sigma_train

            base_state = self._read_state(arr_train, feeders_train)
            valves = self._read_valves(arr_train)
            start_pos = float(full_target[refit_t - 1])

            for h in horizons:
                if refit_t + h - 1 >= N: continue
                truth = float(full_target[refit_t + h - 1])

                if self.ensemble:
                    preds_per_pert = []
                    for pk in self.PERTURBATIONS:
                        ps = self._perturbed_state(base_state, pk)
                        p = self._compass_walk(h, ps, mean_train, valves,
                                                feeder_scales, target_scale,
                                                start_pos, step_mean, wall_high, wall_low,
                                                last_residual)
                        preds_per_pert.append(p)
                    ens_mean = float(np.mean(preds_per_pert))
                    ens_std = float(np.std(preds_per_pert))
                    baseline_pred = preds_per_pert[0]
                else:
                    baseline_pred = self._compass_walk(h, base_state, mean_train, valves,
                                                        feeder_scales, target_scale,
                                                        start_pos, step_mean, wall_high, wall_low,
                                                        last_residual)
                    ens_mean = baseline_pred
                    ens_std = 0.0

                results[h].append((refit_t, ens_mean, ens_std, baseline_pred, truth))

            # HONEST pattern-B AR update: use the SHORTEST-horizon prediction made at THIS refit
            # whose target time will be observed before the next refit
            shortest_h = min(horizons)
            if results[shortest_h]:
                last = results[shortest_h][-1]
                # last = (refit_t, ens_mean, ens_std, baseline_pred, truth)
                # truth at refit_t + shortest_h - 1 was passed in from full_target;
                # in real time, this would be observable at refit_t + shortest_h - 1 which is
                # before next refit at refit_t + 1 (since shortest_h >= 1)
                # ONLY USE IT after the truth time has actually passed
                target_time_of_short_pred = last[0] + shortest_h - 1
                if target_time_of_short_pred <= refit_t:
                    # safe: truth at target_time_of_short_pred was observed by refit_t
                    last_residual = last[4] - last[1]  # truth - ens_mean
                # else: don't update yet (we don't yet observe the truth in real time)
                # NOTE: For monthly ENSO with shortest_h=1, target_time = refit_t, which equals refit_t now,
                # so the truth IS available at next loop iteration but NOT yet at current refit_t.
                # Pattern B updates AFTER current refit, so next refit will use it.
                # Simpler: just always update if shortest_h <= 1 (causal by construction)
                if shortest_h <= 1:
                    last_residual = last[4] - last[1]

        return results


def metrics(records, persistence_lookup):
    if not records: return None
    preds = np.array([r[1] for r in records])  # ens_mean
    truths = np.array([r[4] for r in records])
    pers = np.array([persistence_lookup(r[0]) for r in records])
    if np.std(preds) > 1e-9 and np.std(truths) > 1e-9:
        corr = float(np.corrcoef(preds, truths)[0, 1])
    else:
        corr = 0.0
    mae = float(np.mean(np.abs(preds - truths)))
    p_mae = float(np.mean(np.abs(pers - truths)))
    p_corr = float(np.corrcoef(pers, truths)[0, 1]) if np.std(pers) > 1e-9 else 0.0
    return dict(mae=mae, corr=corr, pers_mae=p_mae, pers_corr=p_corr,
                avg_tube_sigma=float(np.mean([r[2] for r in records])))


# ===== ENSO test =====
if __name__ == '__main__':
    _HERE = os.path.dirname(os.path.abspath(__file__))
    REPO = os.path.dirname(_HERE)
    nino_df = pd.read_csv(os.path.join(REPO, 'Nino34', 'nino34.long.anom.csv'),
                          parse_dates=['Date'], na_values=[-99.99]).dropna()
    nino_df.columns = [c.strip() for c in nino_df.columns]
    nino_df['Year'] = nino_df['Date'].dt.year
    nino_df['Month'] = nino_df['Date'].dt.month
    nino_col = [c for c in nino_df.columns if 'NINA' in c.upper()][0]
    def load_ym(path, name, skip=1):
        rows = []
        with open(path) as f:
            for i, l in enumerate(f):
                if i < skip: continue
                p = l.split()
                if len(p) == 13:
                    try:
                        yr = int(p[0])
                        for m, v in enumerate([float(x) for x in p[1:]], 1):
                            if -90 < v < 90: rows.append({'Year': yr, 'Month': m, name: v})
                    except: pass
        return pd.DataFrame(rows)
    soi_df = load_ym(os.path.join(REPO, 'SOI_NOAA', 'soi.data'), 'SOI', 1)
    pdo_df = load_ym(os.path.join(REPO, 'PDO_NOAA', 'ersst.v5.pdo.dat'), 'PDO', 2)
    m_df = nino_df[['Year', 'Month', nino_col, 'Date']].merge(soi_df, on=['Year', 'Month']).merge(pdo_df, on=['Year', 'Month'])
    m_df.columns = ['Year', 'Month', 'NINO', 'Date', 'SOI', 'PDO']
    m_df = m_df.dropna().sort_values('Date').reset_index(drop=True)
    train_n = int((m_df['Year'] <= 2000).sum())
    nino = np.asarray(m_df['NINO'].values, dtype=float)
    soi = np.asarray(m_df['SOI'].values, dtype=float)
    pdo = np.asarray(m_df['PDO'].values, dtype=float)

    print(f'ENSO data: {len(nino)} months, train_n={train_n}, test=2001+ ({len(nino)-train_n} months)\n')

    HORIZONS = [1, 3, 6, 12, 22]

    # ===== Config 1: SOI feeder only (matches past Compass+Ensemble) =====
    print('=== Config A: Compass+Ensemble, SOI feeder, 10 rungs k=4..13 ===')
    uc = UniversalCascadeV3(dom_P=1.0, k_span=(4, 14), k_ref=8, ensemble=True,
                            feeder_coupling_strength=5.0)
    # Note: rungs use PHI**k as periods (in months); k=4..13 → 6.85 to 1597 months
    t0 = time.time()
    res = uc.rolling_forecast(nino, {'SOI': soi}, train_n, HORIZONS)
    print(f'  ran in {time.time()-t0:.1f}s')
    def pers_lookup(t): return float(nino[t - 1])
    print(f'  {"h":>3}  {"MAE":>6}  {"corr":>7}  {"persMAE":>8}  {"persCorr":>9}  {"tubeSig":>8}')
    for h in HORIZONS:
        m = metrics(res[h], pers_lookup)
        if m:
            v = 'WIN' if m['mae'] < m['pers_mae'] and m['corr'] > m['pers_corr'] else ''
            print(f'  {h:>3}  {m["mae"]:>.3f}  {m["corr"]:>+.3f}  {m["pers_mae"]:>8.3f}  {m["pers_corr"]:>+9.3f}  {m["avg_tube_sigma"]:>8.3f}  {v}')

    # ===== Config 2: SOI + PDO feeders (more info, see if it helps universally) =====
    print('\n=== Config B: Compass+Ensemble, SOI+PDO feeders, 10 rungs ===')
    uc2 = UniversalCascadeV3(dom_P=1.0, k_span=(4, 14), k_ref=8, ensemble=True,
                             feeder_coupling_strength=5.0)
    t0 = time.time()
    res2 = uc2.rolling_forecast(nino, {'SOI': soi, 'PDO': pdo}, train_n, HORIZONS)
    print(f'  ran in {time.time()-t0:.1f}s')
    for h in HORIZONS:
        m = metrics(res2[h], pers_lookup)
        if m:
            v = 'WIN' if m['mae'] < m['pers_mae'] and m['corr'] > m['pers_corr'] else ''
            print(f'  {h:>3}  {m["mae"]:>.3f}  {m["corr"]:>+.3f}  {m["pers_mae"]:>8.3f}  {m["pers_corr"]:>+9.3f}  {m["avg_tube_sigma"]:>8.3f}  {v}')

    # ===== Config 3: Baseline only (no ensemble) =====
    print('\n=== Config C: Baseline (no ensemble), SOI feeder ===')
    uc3 = UniversalCascadeV3(dom_P=1.0, k_span=(4, 14), k_ref=8, ensemble=False,
                             feeder_coupling_strength=5.0)
    t0 = time.time()
    res3 = uc3.rolling_forecast(nino, {'SOI': soi}, train_n, HORIZONS)
    print(f'  ran in {time.time()-t0:.1f}s')
    for h in HORIZONS:
        m = metrics(res3[h], pers_lookup)
        if m:
            v = 'WIN' if m['mae'] < m['pers_mae'] and m['corr'] > m['pers_corr'] else ''
            print(f'  {h:>3}  {m["mae"]:>.3f}  {m["corr"]:>+.3f}  {m["pers_mae"]:>8.3f}  {m["pers_corr"]:>+9.3f}  {m["avg_tube_sigma"]:>8.3f}  {v}')
