"""
ara_framework.py — canonical implementation of the ARA framework.

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
        home_k: the rung where the system naturally lives. For ECG-like
                systems home_k = 8 corresponds to ~47 beats (autonomic envelope);
                for ENSO home_k = 8 corresponds to ~47 months (ENSO period).
                Pick this from physical knowledge of the system.
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
    print("  see F:/SystemFormulaFolder/TheFormula/canonical_benchmark.py")


if __name__ == "__main__":
    _self_test()
