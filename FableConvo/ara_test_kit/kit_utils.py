"""
kit_utils.py — shared instruments for the ARA test kit (2 Jul 2026 session).
numpy + scipy only. All functions take a 1-D series x and sample rate fs.
NOTE on filtering: descriptive measurements (duty, phase, floors) may use
zero-phase filters; they must NEVER feed a prediction target (repo rule).
bath_share is strictly causal by construction.
DUTY WARNING (bug caught by smoke test, 2 Jul): asymmetry lives in the
HARMONICS. Never measure duty on a narrowband signal — a bandpass around f0
turns every wave into a symmetric sinusoid (duty = 0.5 forever). Use the
lowpass that keeps ~5 harmonics.
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt, hilbert, find_peaks
from scipy.fft import rfft, rfftfreq


def read_series(path, col=-1):
    """Load a CSV/whitespace file; return last (or chosen) numeric column."""
    vals = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in "#;":
                continue
            parts = line.replace(",", " ").split()
            try:
                vals.append(float(parts[col]))
            except (ValueError, IndexError):
                continue
    return np.asarray(vals, float)


def dominant_period(x, fs, fmin=None):
    """Dominant period from the FFT peak."""
    x = x - np.mean(x)
    f = rfftfreq(len(x), 1 / fs)
    A = np.abs(rfft(x))
    lo = 1 if fmin is None else max(1, int(fmin * len(x) / fs))
    i = lo + np.argmax(A[lo:])
    return 1.0 / f[i]


def bandpass(x, fs, f0, width=0.35, order=4):
    """Zero-phase bandpass around f0. Descriptive use only (phase extraction)."""
    ny = fs / 2
    lo, hi = max(f0 * (1 - width), 1e-9) / ny, min(f0 * (1 + width) / ny, 0.99)
    sos = butter(order, [lo, hi], btype="band", output="sos")
    return sosfiltfilt(sos, x - np.mean(x))   # SOS: stable at narrow/low bands


def lowpass(x, fs, fc, order=4):
    """Zero-phase lowpass. Descriptive use only."""
    sos = butter(order, min(fc / (fs / 2), 0.99), btype="low", output="sos")
    return sosfiltfilt(sos, x - np.mean(x))


def two_bands(x, fs, min_sep=1.6):
    """(f_slow, f_fast): two strongest spectral peaks separated by >= min_sep.
    Transparent generic; substitute the canonical mapper for authoritative runs."""
    x = x - np.mean(x)
    f = rfftfreq(len(x), 1 / fs)
    A = np.abs(rfft(x)); A[0] = 0
    i1 = np.argmax(A)
    mask = (f < f[i1] / min_sep) | (f > f[i1] * min_sep)
    A2 = np.where(mask, A, 0); A2[0] = 0
    i2 = np.argmax(A2)
    fa, fb = sorted([f[i1], f[i2]])
    return fa, fb


def duty_fraction(x, fs, f0=None, keep_harmonics=12):
    """Mean rise fraction of the dominant cycle: (trough->peak)/(trough->trough).
    Returns (duty, n_cycles). 0.5 = symmetric. Measured on a LOWPASS keeping
    ~keep_harmonics harmonics (see DUTY WARNING in module docstring)."""
    if f0 is None:
        f0 = 1.0 / dominant_period(x, fs)
    xb = lowpass(x, fs, keep_harmonics * f0)
    P = fs / f0
    pk, _ = find_peaks(xb, distance=int(0.6 * P))
    tr, _ = find_peaks(-xb, distance=int(0.6 * P))
    duties = []
    for p in pk:
        prev_tr = tr[tr < p]
        next_tr = tr[tr > p]
        if len(prev_tr) and len(next_tr):
            rise = p - prev_tr[-1]
            full = next_tr[0] - prev_tr[-1]
            if 0.2 * P < full < 2.5 * P:
                duties.append(rise / full)
    return (float(np.mean(duties)), len(duties)) if duties else (np.nan, 0)


def cycle_floor(x, fs, k=1, f0=None, use_envelope=False):
    """Autocorrelation of the series (or envelope) at lag = k dominant periods."""
    if f0 is None:
        f0 = 1.0 / dominant_period(x, fs)
    sig = np.abs(hilbert(x - np.mean(x))) if use_envelope else x - np.mean(x)
    lag = int(round(k * fs / f0))
    if lag >= len(sig) - 10:
        return np.nan
    a, b = sig[:-lag], sig[lag:]
    return float(np.corrcoef(a, b)[0, 1])


def damping_angle_deg(x, fs, f0=None, kmax=4):
    """Angle from the circle-axis: rho(k) ~ r^k across k cycles;
    zeta = -ln(r)/(2*pi); angle = arcsin(zeta), degrees.
    0 = pure oscillation; 90 = pure decay. Assumes light damping, one mode."""
    floors = [cycle_floor(x, fs, k, f0) for k in range(1, kmax + 1)]
    floors = [f for f in floors if np.isfinite(f) and f > 0]
    if len(floors) < 2:
        return np.nan, floors
    ks = np.arange(1, len(floors) + 1)
    slope = np.polyfit(ks, np.log(floors), 1)[0]  # ln r
    zeta = min(max(-slope / (2 * np.pi), 0.0), 1.0)
    return float(np.degrees(np.arcsin(zeta))), floors


def bath_share(x, fs, p=None, lam=1e-2):
    """STRICTLY CAUSAL: ridge AR on past p samples; first half train, second
    half test. Returns test residual variance ratio = un-modelable share
    (Mori-Zwanzig orthogonal part), in [0,1]."""
    x = np.asarray(x, float)
    if p is None:
        P = dominant_period(x, fs)
        p = min(max(8, int(2 * fs * P)), len(x) // 6)
    N = len(x); split = N // 2
    X = np.column_stack([x[i:N - p + i] for i in range(p)])
    y = x[p:]
    idx = np.arange(p, N)
    tr, te = idx < split, idx >= split
    mu = X[tr].mean(0)
    Xc = X - mu
    A = Xc[tr].T @ Xc[tr] + lam * np.eye(p)
    b = Xc[tr].T @ (y[tr] - y[tr].mean())
    w = np.linalg.solve(A, b)
    resid = y[te] - (Xc[te] @ w + y[tr].mean())
    return float(np.var(resid) / np.var(y[te]))


CONSTANTS = {
    "1/e (no geometry)": 0.36788,
    "3/8 (Fib convergent)": 0.375,
    "1/phi^2 (anti-phi)": 0.38197,
    "2/5 (Fib convergent/pentagram)": 0.400,
}
ANGLES = {
    "golden angle": 137.5078,
    "pentagram step (2/5)": 144.0,
    "anti-phase lock": 180.0,
}


def dominance_duty(x, fs, min_sep=1.6):
    """THE FRAMEWORK'S REGISTERED DUTY (added 2 Jul after Dylan's catch):
    fraction of time the FAST band's envelope dominates the SLOW band's —
    a relational, caught-in-motion quantity (the repo's golden duty: 54-heart
    green/brown, QBO, Waldmeier are THIS, not waveform rise/fall).
    Returns (dominance_fraction, f_slow, f_fast). Envelopes are normalized to
    equal median so 'dominance' means relative excursion, not raw amplitude.
    Substitute the canonical mapper's band split for authoritative runs."""
    fa, fb = two_bands(x, fs, min_sep)
    ea = np.abs(hilbert(bandpass(x, fs, fa)))
    eb = np.abs(hilbert(bandpass(x, fs, fb)))
    ea = ea / max(np.mean(ea), 1e-12)   # MEAN norm (median creates ties in
    eb = eb / max(np.mean(eb), 1e-12)   # quiet periods; caught by smoke test)
    frac = float(np.mean(eb > ea))
    return frac, fa, fb
