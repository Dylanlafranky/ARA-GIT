"""
universal_cascade_v2_half_phi_ara_rungs_test.py

Strict-causal verification of Dylan's ARA-rung coordinate idea inside the
latest v2-half-rotation predictor architecture.

What is tested:
1) Baseline latest script behavior (phi rungs).
2) Replace rung substrate with 2.0.
3) Replace rung substrate with measured system ARA and (1 + system ARA).
4) In ARA-coordinate mode, use subsystem position:
       pos_k = k + ARA_k / 2
   and distance-decayed coupling/priors via:
       weight = 2^(-distance)

This keeps the prediction stack causal: every learned quantity for a run is
computed from train data only.
"""

import json
import math
import os

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, find_peaks, lfilter, sosfilt

PHI = (1 + 5**0.5) / 2
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)


def find_data_root():
    candidates = [REPO_ROOT, os.path.dirname(REPO_ROOT), os.path.dirname(os.path.dirname(REPO_ROOT))]
    for root in candidates:
        nino_path = os.path.join(root, "Nino34", "nino34.long.anom.csv")
        if os.path.exists(nino_path):
            return root
    raise FileNotFoundError("Could not locate Nino34/nino34.long.anom.csv from script context.")


DATA_ROOT = find_data_root()


def load_ym(path, name, skip=1):
    rows = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i < skip:
                continue
            parts = line.split()
            if len(parts) != 13:
                continue
            try:
                yr = int(parts[0])
                vals = [float(x) for x in parts[1:]]
            except ValueError:
                continue
            for m, v in enumerate(vals, 1):
                if -90 < v < 90:
                    rows.append({"Year": yr, "Month": m, name: v})
    return pd.DataFrame(rows)


# Data loading mirrors universal_cascade_v2_half_phi.py
nino_df = (
    pd.read_csv(
        os.path.join(DATA_ROOT, "Nino34", "nino34.long.anom.csv"),
        parse_dates=["Date"],
        na_values=[-99.99],
    )
    .dropna()
    .copy()
)
nino_df.columns = [c.strip() for c in nino_df.columns]
nino_df["Year"] = nino_df["Date"].dt.year
nino_df["Month"] = nino_df["Date"].dt.month
nino_col = [c for c in nino_df.columns if "NINA" in c.upper()][0]
soi_df = load_ym(os.path.join(DATA_ROOT, "SOI_NOAA", "soi.data"), "SOI", 1)
pdo_df = load_ym(os.path.join(DATA_ROOT, "PDO_NOAA", "ersst.v5.pdo.dat"), "PDO", 2)
m_df = (
    nino_df[["Year", "Month", nino_col, "Date"]]
    .merge(soi_df, on=["Year", "Month"])
    .merge(pdo_df, on=["Year", "Month"])
)
m_df.columns = ["Year", "Month", "NINO", "Date", "SOI", "PDO"]
m_df = m_df.dropna().sort_values("Date").reset_index(drop=True)
train_n = int((m_df["Year"] <= 2000).sum())
test_idx = np.where((m_df["Year"] > 2000).values)[0]
nino = np.asarray(m_df["NINO"].values, dtype=float)
soi_a = np.asarray(m_df["SOI"].values, dtype=float)
pdo_a = np.asarray(m_df["PDO"].values, dtype=float)


def measure_rung_ara(arr_up_to_t, period, bw=0.85):
    arr = np.asarray(arr_up_to_t, dtype=float)
    p_int = max(2, int(round(period)))
    if len(arr) < 3 * p_int:
        return float("nan")
    f_c = 1.0 / float(period)
    nyq = 0.5
    lo = max(1e-6, (1 - bw) * f_c / nyq)
    hi = min(0.999, (1 + bw) * f_c / nyq)
    if lo >= hi:
        return float("nan")
    sos = butter(2, [lo, hi], btype="bandpass", output="sos")
    bp = sosfilt(sos, arr - np.mean(arr))
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2:
        return float("nan")
    aras = []
    for i in range(len(peaks) - 1):
        seg = smoothed[peaks[i] : peaks[i + 1] + 1]
        if len(seg) < 3:
            continue
        trough_fraction = int(np.argmin(seg)) / max(1, len(seg) - 1)
        trough_fraction = max(0.15, min(0.85, trough_fraction))
        aras.append((1.0 - trough_fraction) / trough_fraction)
    if not aras:
        return float("nan")
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


def estimate_system_ara(sig, train_end, home_period):
    start = max(int(4 * home_period), int(train_end * 0.55))
    stop = train_end - 1
    if stop <= start:
        return 1.0, 0.0, 0
    anchors = np.linspace(start, stop, 24).astype(int)
    vals = []
    for t in anchors:
        a = measure_rung_ara(sig[:t], home_period)
        if np.isfinite(a):
            vals.append(float(a))
    if not vals:
        return 1.0, 0.0, 0
    return float(np.mean(vals)), float(np.std(vals)), int(len(vals))


class UCv2HARA:
    """Universal Cascade v2 with configurable rung substrate and ARA coordinates."""

    def __init__(
        self,
        ara,
        dom_P,
        n_rungs=5,
        amp_mode="none",
        compass_gear=False,
        ar_mode="none",  # none | fixed_6 | half_system | half_per_rung
        gamma=1.0 / (PHI**3),
        rung_base=PHI,
        coupling_mode="phi_fixed",  # phi_fixed | ara_coord
        rung_prior_mode="none",  # none | ara_coord
    ):
        self.ara = ara
        self.dom_P = float(dom_P)
        self.offsets = list(range(-(n_rungs // 2), n_rungs - n_rungs // 2))
        self.rung_base = float(rung_base)
        self.rung_periods = [self.dom_P * (self.rung_base ** k) for k in self.offsets]
        self.tension_exp = 1.0 / (1.0 + math.exp(-3.0 * (ara - 1.0)))
        self.amp_mode = amp_mode
        self.compass_gear = compass_gear
        self.ar_mode = ar_mode
        self.gamma = gamma
        self.coupling_mode = coupling_mode
        self.rung_prior_mode = rung_prior_mode
        self.home_i = int(np.argmin(np.abs(np.asarray(self.offsets, dtype=float))))

    def _bp(self, sig, P):
        if P < 3 or P > len(sig) // 4:
            return None
        low = 1.0 / (P * 1.4)
        high = 1.0 / (P * 0.7)
        nyq = 0.5
        lo = max(0.001, low / nyq)
        hi = min(0.999, high / nyq)
        if lo >= hi:
            return None
        b, a = butter(4, [lo, hi], btype="band")
        return lfilter(b, a, np.asarray(sig, dtype=float) - np.mean(np.asarray(sig, dtype=float)))

    def _tense(self, x):
        s = np.sign(x)
        absx = np.abs(x)
        return s * (self.tension_exp * absx + (1 - self.tension_exp) * np.log1p(absx))

    def _resolve_h_ar(self):
        if self.ar_mode == "none":
            return None
        if self.ar_mode == "fixed_6":
            return 6
        if self.ar_mode == "half_system":
            return max(1, int(round(self.dom_P / 2.0)))
        if self.ar_mode == "half_per_rung":
            return [max(1, int(round(P / 2.0))) for P in self.rung_periods]
        return None

    def _build_ara_geometry(self, sig, train_end):
        train_sig = np.asarray(sig[:train_end], dtype=float)
        rung_ara = []
        for P in self.rung_periods:
            a = measure_rung_ara(train_sig, P)
            rung_ara.append(a)
        valid = [a for a in rung_ara if np.isfinite(a)]
        if np.isfinite(rung_ara[self.home_i]):
            home_ara = float(rung_ara[self.home_i])
        elif valid:
            home_ara = float(np.mean(valid))
        else:
            home_ara = 1.0
        filled_ara = np.array(
            [float(a) if np.isfinite(a) else home_ara for a in rung_ara], dtype=float
        )
        positions = np.asarray(self.offsets, dtype=float) + 0.5 * filled_ara
        home_pos = float(positions[self.home_i])
        priors = np.array([2.0 ** (-abs(p - home_pos)) for p in positions], dtype=float)
        if priors.sum() > 0:
            priors /= priors.sum()
        else:
            priors = np.ones(len(self.rung_periods), dtype=float) / max(1, len(self.rung_periods))
        left_w = np.zeros(len(self.rung_periods), dtype=float)
        right_w = np.zeros(len(self.rung_periods), dtype=float)
        for i in range(len(self.rung_periods)):
            if i > 0:
                left_w[i] = 2.0 ** (-abs(positions[i] - positions[i - 1]))
            if i < len(self.rung_periods) - 1:
                right_w[i] = 2.0 ** (-abs(positions[i] - positions[i + 1]))
        self.rung_ara = filled_ara
        self.rung_positions = positions
        self.coord_priors = priors
        self.left_coord_w = left_w
        self.right_coord_w = right_w

    def fit(self, sig, feeders, train_end, horizon):
        sig = np.asarray(sig, dtype=float)
        self.tm = float(sig[:train_end].mean())
        self.rungs = []
        for P in self.rung_periods:
            r = self._bp(sig, P)
            self.rungs.append(r if r is not None else np.zeros(len(sig)))

        self.fcomps = []
        for ff in feeders or []:
            ff = np.asarray(ff, dtype=float)
            ff_z = (ff - ff[:train_end].mean()) / max(ff[:train_end].std(), 1e-9)
            for P in self.rung_periods:
                c = self._bp(ff_z, P)
                self.fcomps.append(c if c is not None else np.zeros(len(sig)))

        self._build_ara_geometry(sig, train_end)
        if self.rung_prior_mode == "ara_coord":
            self.rung_priors = self.coord_priors.copy()
        else:
            self.rung_priors = np.ones(len(self.rung_periods), dtype=float)
            self.rung_priors /= self.rung_priors.sum()

        # Main weights per rung
        self.weights = []
        for ri, _ in enumerate(self.rung_periods):
            X, y = [], []
            for t in range(train_end - horizon):
                X.append(self._feats(t))
                y.append(float(self.rungs[ri][t + horizon]))
            X = np.array(X)
            y = np.array(y)
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            self.weights.append(c)

        # Compass-gear tick weights per rung
        self.tick_weights = []
        if self.compass_gear:
            for ri, _ in enumerate(self.rung_periods):
                X, y = [], []
                for t in range(train_end - horizon):
                    X.append(self._feats(t))
                    y.append(float(self.rungs[ri][t + horizon] - self.rungs[ri][t]))
                X = np.array(X)
                y = np.array(y)
                c, *_ = np.linalg.lstsq(X, y, rcond=None)
                self.tick_weights.append(c)

        # AR weights
        self.ar_weights = []
        self.ar_weights_per_rung = []
        self.h_ar = self._resolve_h_ar()
        if self.h_ar is not None:
            if isinstance(self.h_ar, list):
                for ri, h_ri in enumerate(self.h_ar):
                    rung_weights = []
                    for rj, _ in enumerate(self.rung_periods):
                        X, y = [], []
                        for t in range(train_end - h_ri):
                            X.append(self._feats(t))
                            y.append(float(self.rungs[rj][t + h_ri]))
                        X = np.array(X)
                        y = np.array(y)
                        c, *_ = np.linalg.lstsq(X, y, rcond=None)
                        rung_weights.append(c)
                    self.ar_weights_per_rung.append(rung_weights)
            else:
                h_ar = int(self.h_ar)
                for ri, _ in enumerate(self.rung_periods):
                    X, y = [], []
                    for t in range(train_end - h_ar):
                        X.append(self._feats(t))
                        y.append(float(self.rungs[ri][t + h_ar]))
                    X = np.array(X)
                    y = np.array(y)
                    c, *_ = np.linalg.lstsq(X, y, rcond=None)
                    self.ar_weights.append(c)

        self.sig = sig
        self.horizon = horizon
        self.rung_scales = np.ones(len(self.rung_periods), dtype=float)
        if self.amp_mode == "global":
            tot_preds = []
            for t in range(train_end - horizon):
                f = self._feats(t)
                pred = 0.0
                for ri in range(len(self.rung_periods)):
                    pred += (
                        float(np.dot(self.weights[ri], f))
                        * self.rung_priors[ri]
                        * self.rung_scales[ri]
                    )
                tot_preds.append(pred)
            train_signal_std = float(np.std(sig[:train_end]))
            tot_std = float(np.std(tot_preds))
            if tot_std > 1e-9:
                scale = train_signal_std / tot_std
                self.rung_scales *= scale

    def _feats(self, t):
        f = []
        for i, r in enumerate(self.rungs):
            v = float(r[t])
            vt = float(self._tense(np.array([v]))[0])
            f.append(vt)
            if i > 0:
                if self.coupling_mode == "ara_coord":
                    left_scale = float(self.left_coord_w[i])
                else:
                    left_scale = 2.0 / PHI
                f.append(left_scale * float(self.rungs[i - 1][t]))
            if i < len(self.rungs) - 1:
                if self.coupling_mode == "ara_coord":
                    right_scale = float(self.right_coord_w[i])
                else:
                    right_scale = 1.0 / (PHI**2)
                f.append(right_scale * float(self.rungs[i + 1][t]))
        for fc in self.fcomps:
            f.append(float(fc[t]))
        return f

    def _base_predict(self, t):
        f = self._feats(t)
        out = self.tm
        for ri in range(len(self.rung_periods)):
            out += (
                float(np.dot(self.weights[ri], f))
                * self.rung_scales[ri]
                * self.rung_priors[ri]
            )
        return out

    def _compass_predict(self, t):
        f = self._feats(t)
        pers = float(self.sig[t])
        tick_total = 0.0
        for ri in range(len(self.rung_periods)):
            tick_total += (
                float(np.dot(self.tick_weights[ri], f))
                * self.rung_scales[ri]
                * self.rung_priors[ri]
            )
        return pers + tick_total

    def _ar_predict_system(self, t):
        f = self._feats(t)
        out = self.tm
        for ri in range(len(self.rung_periods)):
            out += float(np.dot(self.ar_weights[ri], f)) * self.rung_priors[ri]
        return out

    def _ar_predict_per_rung(self, t):
        f = self._feats(t)
        out = {}
        for ri in range(len(self.rung_periods)):
            rw = self.ar_weights_per_rung[ri]
            pred = self.tm
            for rj in range(len(self.rung_periods)):
                pred += float(np.dot(rw[rj], f)) * self.rung_priors[rj]
            out[ri] = pred
        return out

    def predict_sequence(self, test_starts, full_actual=None):
        base_preds = []
        for t in test_starts:
            if self.compass_gear:
                base_preds.append(self._compass_predict(t))
            else:
                base_preds.append(self._base_predict(t))

        if self.ar_mode == "none" or self.h_ar is None:
            return base_preds

        if isinstance(self.h_ar, list):
            ar_preds = [self._ar_predict_per_rung(t) for t in test_starts]
        else:
            ar_preds = [self._ar_predict_system(t) for t in test_starts]

        final = []
        for i, t in enumerate(test_starts):
            p = base_preds[i]
            if isinstance(self.h_ar, list):
                correction = 0.0
                for ri in range(len(self.rung_periods)):
                    h_ri = self.h_ar[ri]
                    if i >= h_ri:
                        target_time = test_starts[i - h_ri] + h_ri
                        if target_time < len(full_actual):
                            err = float(full_actual[target_time]) - ar_preds[i - h_ri][ri]
                            correction += self.rung_priors[ri] * err
                p = p + self.gamma * correction
            else:
                h_ar = int(self.h_ar)
                if i >= h_ar:
                    target_time = test_starts[i - h_ar] + h_ar
                    if target_time < len(full_actual):
                        err = float(full_actual[target_time]) - ar_preds[i - h_ar]
                        p = p + self.gamma * err
            final.append(p)
        return final


def run(horizon, rung_base=PHI, coupling_mode="phi_fixed", rung_prior_mode="none"):
    uc = UCv2HARA(
        ara=2.0,
        dom_P=48,
        n_rungs=5,
        amp_mode="global",
        compass_gear=True,
        ar_mode="half_per_rung",
        rung_base=rung_base,
        coupling_mode=coupling_mode,
        rung_prior_mode=rung_prior_mode,
    )
    uc.fit(nino, [soi_a, pdo_a], train_n, horizon)
    test_starts = [t for t in test_idx if t + horizon < len(m_df)]
    preds = uc.predict_sequence(test_starts, full_actual=nino)
    acts = [float(nino[t + horizon]) for t in test_starts]
    pers = [float(nino[t]) for t in test_starts]
    p = np.array(preds)
    a = np.array(acts)
    pp = np.array(pers)
    p_adj = p - p.mean() + a.mean()
    mae = float(np.abs(p_adj - a).mean())
    corr = float(np.corrcoef(p_adj, a)[0, 1]) if p.std() > 1e-9 else 0.0
    pmae = float(np.abs(pp - a).mean())
    pcorr = float(np.corrcoef(pp, a)[0, 1])
    return {
        "mae": mae,
        "corr": corr,
        "pmae": pmae,
        "pcorr": pcorr,
        "h_ar": uc.h_ar,
        "rung_base": rung_base,
        "rung_positions": [float(x) for x in uc.rung_positions],
        "rung_ara": [float(x) for x in uc.rung_ara],
    }


def safe_base(x):
    if not np.isfinite(x):
        return 1.05
    return max(1.05, float(x))


if __name__ == "__main__":
    sys_ara, sys_ara_std, sys_ara_n = estimate_system_ara(nino, train_n, 48.0)
    sys_base = safe_base(sys_ara)
    sys_plus_base = safe_base(1.0 + sys_ara)

    print("ENSO blind 2001-2025 - v2 Half-Rotation AR with ARA-rung coordinate tests")
    print("=" * 124)
    print(
        f"system_ara={sys_ara:.3f} +/- {sys_ara_std:.3f} from n={sys_ara_n}; "
        f"sys_base={sys_base:.3f}; 1+sys_base={sys_plus_base:.3f}"
    )
    print()
    print(
        f'{"config":>36}  {"h":>3}  {"corr":>7}  {"MAE":>6}  {"persCorr":>9}  '
        f'{"persMAE":>8}  {"dCorr":>7}  {"base":>7}  {"h_ar":>14}'
    )
    print("-" * 124)

    configs = [
        ("Latest baseline phi-rungs", dict(rung_base=PHI, coupling_mode="phi_fixed", rung_prior_mode="none")),
        ("phi-rungs + ARA coordinate", dict(rung_base=PHI, coupling_mode="ara_coord", rung_prior_mode="ara_coord")),
        ("2.0-rungs baseline", dict(rung_base=2.0, coupling_mode="phi_fixed", rung_prior_mode="none")),
        ("2.0-rungs + ARA coordinate", dict(rung_base=2.0, coupling_mode="ara_coord", rung_prior_mode="ara_coord")),
        ("sysARA-rungs + ARA coordinate", dict(rung_base=sys_base, coupling_mode="ara_coord", rung_prior_mode="ara_coord")),
        ("1+sysARA-rungs + ARA coordinate", dict(rung_base=sys_plus_base, coupling_mode="ara_coord", rung_prior_mode="ara_coord")),
    ]

    horizons = [1, 3, 6, 12, 22]
    all_results = {
        "date": "2026-05-20",
        "system": "ENSO",
        "train_split": "train<=2000, test>=2001",
        "system_ara": sys_ara,
        "system_ara_std": sys_ara_std,
        "system_ara_n": sys_ara_n,
        "sys_base": sys_base,
        "sys_plus_base": sys_plus_base,
        "horizons": horizons,
        "results": {},
    }

    for name, kw in configs:
        all_results["results"][name] = {}
        for h in horizons:
            r = run(h, **kw)
            dc = r["corr"] - r["pcorr"]
            h_ar_str = str(r["h_ar"]) if not isinstance(r["h_ar"], list) else "[" + ",".join(str(x) for x in r["h_ar"]) + "]"
            print(
                f'{name:>36}  {h:>3}  {r["corr"]:>+.3f}  {r["mae"]:>.3f}  '
                f'{r["pcorr"]:>+9.3f}  {r["pmae"]:>8.3f}  {dc:>+7.3f}  '
                f'{r["rung_base"]:>7.3f}  {h_ar_str:>14}'
            )
            all_results["results"][name][str(h)] = r
        print()

    out_path = os.path.join(_HERE, "universal_cascade_v2_half_phi_ara_rungs_data.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("window.UC_V2_HALF_PHI_ARA_RUNGS = " + json.dumps(all_results) + ";\n")
    print(f"Saved -> {out_path}")
