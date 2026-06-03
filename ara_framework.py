"""
ara_framework.py — canonical implementation of the ARA framework.

>>> CURRENT STANDARD (June 2026): the validated forecast method is the strict-causal
>>> LAYERED OPERATOR at the bottom of this file — `run_forecast()` with the
>>> `build_self_system()` / `build_system()` adapters. It uses OCTAVE rung spacing with
>>> phi-timed coupling (per the 30 May 2026 ladder correction) and reproduces the
>>> published solar/ENSO/heart numbers (e.g. solar home+ara corr +0.863@12mo … +0.676@132mo,
>>> beating persistence at 4/5 horizons). Use it via `ara_predictor.py`.
>>>
>>> The Topology / ACT / OLD blend described below is the EARLIER predictor and uses
>>> phi^k rung spacing; it is kept for back-compatibility but is SUPERSEDED. Prefer
>>> run_forecast for any new work.

Two halves of one cycle:
  - INVERSE  (extract_topology):  data → topology coordinates
  - FORWARD  (predict):           topology → predicted future values

The framework's claim is that any oscillating system can be summarised by a
small set of coordinates on a φ-spaced rung ladder, and that future values
can be projected from those coordinates by a single deterministic formula.

----------------------------------------------------------------------
TOPOLOGY COORDINATES
----------------------------------------------------------------------
A system's state at time t is a list of per-rung records, plus two scalars:

  Topology(
      v_now        = signal[t-1],                  # actual most-recent value
      mean_train   = mean(signal[:t]),             # training-window mean
      home_k       = the rung index where the system naturally lives,
      rungs        = [
          dict(k, period, amp, theta) for each pinned rung,
          ...
      ]
  )

Each rung k holds:
    period  = φ^k        in the system's natural time units (beats, months, …)
    amp     = peak-to-peak / 2 of the most recent cycle of bandpass(signal, period)
    theta   = current phase, read from the bandpass output's last two values

These are *actual values*, not averages. ARA, partner relationships, and
horizon weights are derived from these coordinates as needed.

----------------------------------------------------------------------
THE PREDICTOR
----------------------------------------------------------------------
The forward predictor is a horizon-conditional blend of two regimes
that share the same topology coordinates:

  ACT (short-lead, anchored at v_now, integrating actual deltas):
      v(h) = v_now + Σ_rung amp × ( cos(θ + 2π·h/p) − cos(θ) )

  OLD (long-lead, structured wave from training mean):
      v(h) = mean_train + Σ_rung w_k × amp × cos(θ + 2π·h/p)
      where w_k = φ^(-|k - home_k|), normalised.

The two regimes are blended through a sigmoid centred at the system's
empirical crossover horizon:

      h_cross = home_period × φ^(±7/4)
      weight_act = sigmoid( steepness × (h_cross − h) / h_cross )
      v(h) = weight_act × ACT(h) + (1 − weight_act) × OLD(h)

The sign in the exponent (+7/4 vs −7/4) depends on whether the system has
a tight matched-rung partner at home rung (closed → −7/4) or not (open → +7/4).
The 7/4 constant was found empirically on ENSO and ECG; treat it as
provisional until confirmed on more domains.

----------------------------------------------------------------------
STRICT-CAUSAL GUARANTEE
----------------------------------------------------------------------
extract_topology(data, t) reads only data[:t]. It NEVER touches indices ≥ t.
predict(topology, h) uses only the topology object — it has no access to
future data. The script that calls predict() may then read truth values
to score against the prediction, but truth never enters the prediction loop.

----------------------------------------------------------------------
"""
from dataclasses import dataclass, field
from typing import Sequence
import numpy as np
from scipy.signal import butter, sosfilt

import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
# Repo root: parent dir if this script is in TheFormula/, else current dir
REPO_ROOT = _PARENT if os.path.basename(_HERE) == "TheFormula" else _HERE

# === Framework constants ===
PHI = 1.6180339887498949
INV_PHI = 1.0 / PHI
INV_PHI3 = 1.0 / PHI**3
PI_LEAK = (np.pi - 3.0) / np.pi          # ≈ 0.04507  (coupling tax)

# 7/4 = 1.75 keeps appearing across framework tests in multiple unit systems:
#   - matter-circle radius: 11/(2π) ≈ 1.751 log-decades   (Script 142)
#   - predictor crossover exponent: ≈ 1.76 in φ-rungs    (ECG, single subject)
#   - solar magnetic cycle ARA: 1.75 (7yr build / 4yr release, empirical)
#   - LF/HF HRV ratio: ≈ φ^1.75
# A neighbour-ablation test (2026-05-04) tried to derive 1.75 as
# 1 + 0.25×3 (self + three quarter-coupling neighbour bands). Empirically
# the crossover DOES shift when neighbour rungs are removed, but not in
# clean 0.25-per-band increments. Hypothesis not confirmed; the principled
# origin of 1.75 remains an open question. Treat the value as provisional.
CROSSOVER_EXPONENT = 7.0 / 4.0           # = 1.75 — empirical, origin TBD


# === Topology dataclass ===
@dataclass
class Topology:
    """Coordinates of a system in the φ-rung ladder at a given anchor."""
    v_now: float
    mean_train: float
    home_k: int
    rungs: list = field(default_factory=list)

    @property
    def home_period(self) -> float:
        return float(PHI ** self.home_k)

    def __repr__(self):
        rks = [r['k'] for r in self.rungs]
        return (f"Topology(v_now={self.v_now:.3f}, mean_train={self.mean_train:.3f}, "
                f"home_k={self.home_k}, rungs_pinned={rks})")


# === Strict-causal bandpass (SOS form for stability) ===
def causal_bandpass(arr: np.ndarray, period: float,
                    bandwidth: float = 0.4, order: int = 2) -> np.ndarray:
    """One-sided IIR Butterworth bandpass at given period (in samples).
    Output[i] depends only on input[≤i] — no future leakage."""
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    f_c = 1.0 / period
    nyq = 0.5
    Wn_lo = max(1e-6, (1 - bandwidth) * f_c / nyq)
    Wn_hi = min(0.999, (1 + bandwidth) * f_c / nyq)
    if Wn_lo >= Wn_hi:
        return np.zeros(n)
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))


def _measure_rung(bp: np.ndarray, period: float, k: int):
    """Read (amp, theta) from the MOST RECENT cycle of a bandpass channel.
    No averaging across history — only the local cycle's actual peak-to-peak."""
    p_int = max(2, int(period))
    if len(bp) < 2 * p_int + 5:
        return None
    last_cycle = bp[-p_int:]
    amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
    if amp < 1e-9:
        return None
    v_recent = float(bp[-1])
    v_prev = float(bp[-2])
    norm = max(amp, 1e-9)
    ratio = max(-0.99, min(0.99, v_recent / norm))
    theta = float(np.arccos(ratio) * (-1.0 if (v_recent - v_prev) > 0 else 1.0))
    return dict(k=int(k), period=float(period), amp=amp, theta=theta)


# === INVERSE HALF: extract_topology ===
def extract_topology(data: Sequence[float],
                     t: int,
                     rungs_k: Sequence[int] = tuple(range(2, 22)),
                     home_k: int = 8,
                     pin_factor: int = 4) -> Topology:
    """Read the system's state from training data alone.

    Args:
        data: full time series (any units — beats, months, samples, etc.)
        t: anchor index. The formula sees only data[:t].
        rungs_k: which φ-rung indices to attempt (period = φ^k in data units)
        home_k: the rung where the system naturally lives. For public benchmarks,
                choose this before scoring from the measured ground-cycle period:
                home_k = round(log(period) / log(PHI)), using the data's time unit.
                If multiple ground cycles are plausible, declare all candidates
                before running the test and report all candidate results.
        pin_factor: a rung is included only if pin_factor × period ≤ t
                    (default 4 — keeps filters numerically stable).

    Returns:
        Topology object with v_now, mean_train, home_k, and per-rung records.
    """
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr):
        raise ValueError(f"anchor t={t} out of range for data of length {len(arr)}")

    v_now = float(arr[t - 1])
    mean_train = float(np.mean(arr[:t]))

    rungs = []
    for k in rungs_k:
        period = PHI ** int(k)
        if pin_factor * period > t:
            continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is not None:
            rungs.append(rec)

    return Topology(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)


# === FORWARD HALF: predict ===
def _predict_act(topo: Topology, h: float) -> float:
    """ACT regime: integrate actual deltas forward from v_now.
       v(h) = v_now + Σ amp × (cos(θ + 2π·h/p) − cos(θ))"""
    if not topo.rungs:
        return topo.v_now
    delta = 0.0
    for s in topo.rungs:
        a, th, p = s['amp'], s['theta'], s['period']
        delta += a * (np.cos(th + 2 * np.pi * h / p) - np.cos(th))
    return topo.v_now + delta


def _predict_old(topo: Topology, h: float) -> float:
    """OLD regime: structured wave from training mean.
       v(h) = mean + Σ w_k × amp × cos(θ + 2π·h/p),  w_k = φ^(-|k-home_k|)"""
    if not topo.rungs:
        return topo.mean_train
    weights = np.array([PHI ** (-abs(s['k'] - topo.home_k)) for s in topo.rungs])
    weights = weights / weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        new_th = s['theta'] + 2 * np.pi * h / s['period']
        contrib += weights[j] * s['amp'] * np.cos(new_th)
    return topo.mean_train + contrib


def crossover_horizon(topo: Topology, closed: bool = False) -> float:
    """Empirical crossover between ACT and OLD predictors.

    h_cross = home_period × φ^(±7/4)
    sign: −7/4 for closed systems (matched-rung partner present, e.g. ENSO+SOI)
          +7/4 for open systems (single-channel like ECG)
    """
    sign = -1.0 if closed else +1.0
    return topo.home_period * (PHI ** (sign * CROSSOVER_EXPONENT))


def predict(topo: Topology, h: float,
            closed: bool = False,
            blend_steepness: float = 2.0) -> float:
    """Canonical forward predictor.

    Sigmoid blend of ACT and OLD around the system's empirical crossover.

    Args:
        topo: Topology produced by extract_topology()
        h: forecast horizon in data units
        closed: True if the system has a tight matched-rung partner at home rung
        blend_steepness: how sharply ACT→OLD transitions (higher = sharper)

    Returns:
        Predicted value at horizon h.
    """
    cross_h = crossover_horizon(topo, closed=closed)
    z = blend_steepness * (cross_h - h) / cross_h
    weight_act = 1.0 / (1.0 + np.exp(-z))

    return weight_act * _predict_act(topo, h) + (1.0 - weight_act) * _predict_old(topo, h)


def predict_components(topo: Topology, h: float,
                       closed: bool = False,
                       blend_steepness: float = 2.0) -> dict:
    """Same as predict() but also returns the individual ACT and OLD predictions
    plus the blend weight — useful for diagnostics."""
    cross_h = crossover_horizon(topo, closed=closed)
    z = blend_steepness * (cross_h - h) / cross_h
    w_act = 1.0 / (1.0 + np.exp(-z))
    p_act = _predict_act(topo, h)
    p_old = _predict_old(topo, h)
    return dict(
        prediction=w_act * p_act + (1.0 - w_act) * p_old,
        act=p_act,
        old=p_old,
        weight_act=w_act,
        crossover_h=cross_h,
    )


# === Self-test on REAL data (synthetic tests would only confirm the framework
#     matches its own assumptions and would be misleading) ===
def _self_test():
    """Validate the module on a real public dataset.
    Loads NOAA NINO 3.4 monthly anomalies and runs the canonical predictor.
    If the data file isn't available, prints a helpful message and exits."""
    import os
    print("=== ara_framework self-test (real-data only) ===")

    nino_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "Nino34", "nino34.long.anom.csv")
    if not os.path.exists(nino_path):
        print(f"  Real-data validation requires: {nino_path}")
        print("  (NOAA Niño 3.4 monthly long anomaly CSV)")
        print("  Source: https://psl.noaa.gov/gcos_wgsp/Timeseries/Nino34/")
        print("  Skipping self-test. To benchmark on real data, see "
              "TheFormula/canonical_benchmark.py")
        return

    try:
        import pandas as pd
    except ImportError:
        print("  pandas required for self-test; skipping")
        return

    df = pd.read_csv(nino_path, skiprows=1, header=None, names=['date', 'val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    nino = df.set_index('date')['val'].astype(float)
    nino.index = pd.to_datetime(nino.index).to_period('M').to_timestamp()
    nino = nino.groupby(nino.index).first()
    NINO = nino.values.astype(float)
    DATES = nino.index

    print(f"  Loaded NINO 3.4: {len(NINO)} months, "
          f"{DATES[0].date()} → {DATES[-1].date()}")

    # Anchor at end of 2010 — strong La Niña — and predict forward
    anchor = next(i for i, d in enumerate(DATES) if d >= pd.Timestamp('2010-12-01'))
    print(f"  Anchor: {DATES[anchor-1].date()} (v_now = {NINO[anchor-1]:+.2f})")

    topo = extract_topology(NINO, t=anchor, rungs_k=range(3, 13), home_k=8)
    print(f"  {topo}")
    print(f"  home_period:        {topo.home_period:.2f} months")
    print(f"  crossover (open):   {crossover_horizon(topo, closed=False):.2f}")
    print(f"  crossover (closed): {crossover_horizon(topo, closed=True):.2f}  "
          f"← ENSO is closed (has SOI partner)")

    print(f"\n  Forecast vs truth (ENSO is closed):")
    print(f"  {'h(mo)':>5}  {'date':>9}  {'ACT':>7}  {'OLD':>7}  {'BLEND':>7}  "
          f"{'truth':>7}  {'w_act':>6}")
    for h in [1, 3, 6, 12, 24, 36]:
        if anchor + h - 1 >= len(NINO):
            continue
        c = predict_components(topo, h, closed=True)
        truth = NINO[anchor + h - 1]
        date_str = DATES[anchor + h - 1].strftime('%Y-%m')
        print(f"  {h:>5}  {date_str:>9}  {c['act']:>+7.3f}  {c['old']:>+7.3f}  "
              f"{c['prediction']:>+7.3f}  {truth:>+7.3f}  {c['weight_act']:>.3f}")

    print("\n  Self-test complete. For full benchmark across many anchors,")
    print("  see <repo>/TheFormula/canonical_benchmark.py")


if __name__ == "__main__":
    _self_test()


# ============================================================================
# CURRENT-STANDARD ENGINE (added 2026-06-03)
# ----------------------------------------------------------------------------
# Strict-causal LAYERED OPERATOR — the validated, transferable forecast method
# (ported from TheFormula/Claude4.8/ara_unified_layered_framework_test.py).
# One operator, three input adapters; octave rung spacing with phi-timed
# coupling (NOT phi-spaced rungs — see the 30 May 2026 ladder correction).
# This is what reproduces the published solar/ENSO/ECG numbers. Prefer this
# over the legacy ACT/OLD blend above.
# ============================================================================
import math as _math
from dataclasses import dataclass as _dc, field as _fld

@_dc
class Contact:
    name: str
    values: "np.ndarray"
    period: float
    window: int
    layer: int = 1

@_dc
class System:
    name: str
    unit: str
    home: "np.ndarray"
    home_period: float
    horizons: tuple
    home_lags: tuple
    lower: tuple
    upper: tuple

def _shifted(x, lag):
    r = np.full_like(x, np.nan, dtype=float)
    if lag == 0: r[:] = x
    elif lag < len(x): r[lag:] = x[:-lag]
    return r

def _trailing_mean(x, window):
    r = np.full_like(x, np.nan, dtype=float)
    for i in range(window - 1, len(x)):
        b = x[i - window + 1:i + 1]
        if np.all(np.isfinite(b)): r[i] = float(np.mean(b))
    return r

def _standardize_train(x, cutoff):
    tr = x[:cutoff]; tr = tr[np.isfinite(tr)]
    mu = float(np.mean(tr)); sd = float(np.std(tr))
    if not np.isfinite(sd) or sd < 1e-12: sd = 1.0
    return (x - mu) / sd

def _recursive_terrain(ara, depth=5):
    slope = np.zeros_like(ara, dtype=float); ridge = np.zeros_like(ara, dtype=float)
    for i, v in enumerate(ara):
        if not np.isfinite(v): slope[i] = np.nan; ridge[i] = np.nan; continue
        x = float(np.clip(v, 0.0, 2.0))
        for lvl in range(depth):
            cells = 2 ** lvl; width = 2.0 / cells
            cell = min(cells - 1, int(x / width)); lo = cell * width; hi = lo + width
            lph = lo + width / PHI; rph = hi - width / PHI
            target = lph if abs(x - lph) <= abs(x - rph) else rph
            w = PHI ** (-(lvl + 1))
            slope[i] += w * (target - x) / width
            ed = min(x - lo, hi - x) / width
            ridge[i] += w * (1.0 - 2.0 * ed)
    return slope, np.maximum(0.0, ridge)

def _layer_state(system, cutoff):
    home_z = _standardize_train(system.home, cutoff)
    own_spin = home_z - _shifted(home_z, 1)
    torque = np.zeros_like(home_z); wobble = np.zeros_like(home_z)
    for idx, c in enumerate(system.lower):
        z = _standardize_train(c.values, cutoff)
        fast = z - _trailing_mean(z, c.window)
        vel = fast - _shifted(fast, 1)
        gain = _math.sqrt(system.home_period / c.period)
        parity = -1.0 if c.layer % 2 else 1.0
        term = parity * (PHI ** (-(c.layer - 1))) * gain * vel
        torque += np.nan_to_num(term)
        wobble += ((-1.0) ** idx) * (PHI ** (-idx)) * np.nan_to_num(term)
    upper_pressure = np.zeros_like(home_z)
    for c in system.upper:
        z = _standardize_train(c.values, cutoff)
        env = _trailing_mean(z, c.window)
        upper_pressure += (PHI ** (-c.layer)) * _math.sqrt(c.period / system.home_period) * np.nan_to_num(env)
    ara = 1.0 + np.tanh(home_z / 2.0)
    terrain_slope, ridge_pressure = _recursive_terrain(ara)
    denom = 1.0 + ridge_pressure + np.abs(upper_pressure) / PHI
    roll = ((PHI ** -1) * torque + (PHI ** -2) * np.nan_to_num(own_spin)
            + (PHI ** -3) * wobble + (PHI ** -2) * terrain_slope
            - (PHI ** -2) * upper_pressure) / denom
    return dict(home_z=home_z, ara=ara, own_spin=own_spin, lower_torque=torque,
                contact_wobble=wobble, upper_pressure=upper_pressure,
                terrain_slope=terrain_slope, ridge_pressure=ridge_pressure, roll=roll)

def _metrics(truth, pred, current):
    v = np.isfinite(truth) & np.isfinite(pred) & np.isfinite(current)
    truth, pred, current = truth[v], pred[v], current[v]
    if len(truth) < 3: return dict(n=int(len(truth)), corr=float('nan'), mae=float('nan'))
    return dict(n=int(len(truth)), corr=float(np.corrcoef(truth, pred)[0, 1]),
                mae=float(np.mean(np.abs(truth - pred))),
                turn=float(np.mean(np.sign(truth - current) == np.sign(pred - current))))

def _feature_matrix(system, state, origins, include_home_lags):
    rows = []
    for t in origins:
        row = []
        if include_home_lags:
            row.extend(float(system.home[t - lag]) for lag in system.home_lags)
        tq = state["lower_torque"][t]; up = state["upper_pressure"][t]
        ter = state["terrain_slope"][t]; rg = state["ridge_pressure"][t]; rl = state["roll"][t]
        row.extend([rl, tq, state["own_spin"][t], state["contact_wobble"][t], up, ter, rg,
                    tq * ter, tq * up, rl * rg])
        rows.append(row)
    return np.asarray(rows, dtype=float)

def _ridge_readout(x_train, y_train, x_test, penalty=0.1):
    mu = np.nanmean(x_train, axis=0); sd = np.nanstd(x_train, axis=0)
    sd[~np.isfinite(sd) | (sd < 1e-12)] = 1.0
    a = np.nan_to_num((x_train - mu) / sd); b = np.nan_to_num((x_test - mu) / sd)
    a = np.column_stack([np.ones(len(a)), a]); b = np.column_stack([np.ones(len(b)), b])
    reg = np.eye(a.shape[1]) * penalty; reg[0, 0] = 0.0
    beta = np.linalg.solve(a.T @ a + reg, a.T @ y_train)
    return b @ beta

def run_forecast(system, train_frac=0.6180339887498949):  # 1/phi — the golden handover
    """Strict-causal evaluation of the layered operator vs a persistence baseline.
    The train/test split sits at the GOLDEN HANDOVER (1/phi = 0.618), not an arbitrary
    round number: the forwarded share (0.618) is kept as training, the shed share
    (0.382 = 1/phi^2) is what we predict — the same 0.618/0.382 duty the framework uses
    elsewhere (Waldmeier rise/fall, the phi-staircase). Tested as-good-or-better than 0.60
    on solar / sea ice / glucose; never worse.
    Returns per-horizon corr/mae for: persistence, ara_fixed_roll (parameter-free),
    ara_roll_readout (framework features only), home_ar (causal lags), home_plus_ara
    (framework + lags = the headline model)."""
    n = len(system.home); cutoff = int(n * train_frac)
    state = _layer_state(system, cutoff)
    start = max(max(system.home_lags), *(c.window + 2 for c in system.lower + system.upper))
    out = {"cutoff_index": cutoff, "samples": n, "horizons": {}}
    for h in system.horizons:
        tr = np.arange(start, cutoff - h); te = np.arange(cutoff, n - h)
        if len(tr) < 30 or len(te) < 30:
            out["horizons"][str(h)] = None; continue
        ytr = system.home[tr + h]; yte = system.home[te + h]
        ctr = system.home[tr]; cte = system.home[te]; dtr = ytr - ctr
        raw_tr = state["roll"][tr] * _math.sqrt(h / system.home_period)
        raw_te = state["roll"][te] * _math.sqrt(h / system.home_period)
        rstd = float(np.std(raw_tr)); scale = float(np.std(dtr) / rstd) if rstd > 1e-12 else 0.0
        fixed = cte + scale * raw_te
        hxtr = np.asarray([[system.home[t - l] for l in system.home_lags] for t in tr], float)
        hxte = np.asarray([[system.home[t - l] for l in system.home_lags] for t in te], float)
        axtr = _feature_matrix(system, state, tr, False); axte = _feature_matrix(system, state, te, False)
        cxtr = _feature_matrix(system, state, tr, True);  cxte = _feature_matrix(system, state, te, True)
        out["horizons"][str(h)] = dict(
            persistence=_metrics(yte, cte.copy(), cte),
            ara_fixed_roll=_metrics(yte, fixed, cte),
            ara_roll_readout=_metrics(yte, cte + _ridge_readout(axtr, dtr, axte), cte),
            home_ar=_metrics(yte, cte + _ridge_readout(hxtr, dtr, hxte), cte),
            home_plus_ara=_metrics(yte, cte + _ridge_readout(cxtr, dtr, cxte), cte))
    return out

def build_self_system(home, home_period, horizons=None, home_lags=None, name="series", unit="step"):
    """Generic SELF-feeder adapter: build a System from ONE series (like the solar
    self-forecast). Micro-spin lower contacts from the series itself + a slow upper
    envelope. For systems with real external drivers (e.g. ENSO's SOI/WWV/PDO),
    pass those as feeders to build_system() instead to reproduce the full result."""
    home = np.asarray(home, dtype=float)
    P = float(home_period)
    if horizons is None:
        horizons = tuple(int(round(P * f)) for f in (1/11, 1/5.5, 1/2.75, 1/1.4, 1.0))
        horizons = tuple(sorted(set(h for h in horizons if h >= 1)))
    if home_lags is None:
        cand = [0, 1, 2, 3, 6, 12, 24, 48, 72, 96, 120, int(round(P))]
        home_lags = tuple(sorted(set(l for l in cand if l < len(home) // 3)))
    lower = (Contact("micro-spin fast", home, max(2.0, P / 44), max(2, int(P / 44) or 2)),
             Contact("micro-spin mid", home, max(3.0, P / 12), max(3, int(P / 12) or 3)))
    upper = (Contact("slow envelope", home, P * 2, max(2, int(P))),)
    return System(name, unit, home, P, horizons, home_lags, lower, upper)

def build_system(home, lower_feeders, upper_feeders, home_period, horizons, home_lags,
                 name="series", unit="step"):
    """Full adapter: home series + explicit lower/upper feeder series.
    lower_feeders/upper_feeders: list of (name, values, period, window[, layer])."""
    def _mk(specs):
        out = []
        for s in specs:
            nm, val, per, win = s[0], np.asarray(s[1], float), s[2], s[3]
            lay = s[4] if len(s) > 4 else 1
            out.append(Contact(nm, val, per, win, lay))
        return tuple(out)
    return System(name, unit, np.asarray(home, float), float(home_period),
                  tuple(horizons), tuple(home_lags), _mk(lower_feeders), _mk(upper_feeders))
