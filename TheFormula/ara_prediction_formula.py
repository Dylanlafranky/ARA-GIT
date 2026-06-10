"""
ARA PREDICTION FORMULA - generalized, system-agnostic (7 June 2026)
===================================================================
One reusable forecaster for any oscillatory series (ENSO, sunspots, heart RR/ECG, ...). Strict-causal,
honest by construction. Three named parts:
  GEOMETRY (shape)   : engine clock - dominant cycle, causal phase, projected forward (un-hedged motion).
  ENERGY (magnitude) : reservoir proxy (trailing accumulation) + ARA asymmetry (skew). Sizes the swings.
  TRAINING (skill)   : ridge on home-lags + above -> optimal delta readout (skill, at the cost of an
                       uncertainty-proportional hedge lag = the ARA-1.0 shadow).

Outputs three layers: prediction (best estimate, hedged/accurate/slightly-late),
warning (un-hedged, full amplitude = how big it's loading), confidence (energy-predicted residual envelope).
Do NOT shift the lag away (future-leak or lead-shortening); roll the data forward instead. Score skill on
the CHANGE (persistence=0). Magnitude is a calibrated LEAN, not an exact peak (irreducible ARA-1.0 core).

Usage:
    import ara_prediction_formula as A
    r = A.ara_forecast(series, period=None, horizon=6, leading=None)
"""
import numpy as np

PHI = (1+5**0.5)/2

def _trail_mean(x, w):
    return np.array([np.mean(x[max(0,i-w+1):i+1]) for i in range(len(x))])

def _trail_skew(x, w):
    out = np.zeros(len(x))
    for i in range(len(x)):
        a = x[max(0,i-w+1):i+1]
        if len(a) >= 6:
            m = a.mean(); s = a.std()
            out[i] = np.mean(((a-m)/s)**3) if s > 1e-9 else 0.0
    return out

def _dominant_period(x, hi_frac=0.5):
    x = x - x.mean(); nfft = len(x)
    X = np.abs(np.fft.rfft(x*np.hanning(nfft)))**2
    f = np.fft.rfftfreq(nfft, 1.0); per = np.where(f>0, 1/f, np.inf)
    band = (per >= 4) & (per <= hi_frac*nfft)
    return float(per[band][np.argmax(X[band])]) if band.any() else nfft/4

def _causal_bandpass(x, period, bandwidth=0.25, order=2):
    from scipy.signal import butter, sosfilt
    n = len(x); fc = 1.0/period
    lo = max(1e-6,(1-bandwidth)*fc/0.5); hi = min(0.999,(1+bandwidth)*fc/0.5)
    if lo >= hi: return np.zeros(n)
    sos = butter(order, [lo,hi], btype='bandpass', output='sos')
    return sosfilt(sos, x-x.mean())

def _ridge(X, y, Xt, pen=0.2):
    mu = X.mean(0); sd = X.std(0); sd[sd<1e-9] = 1
    A = (X-mu)/sd; B = (Xt-mu)/sd
    A = np.column_stack([np.ones(len(A)),A]); B = np.column_stack([np.ones(len(B)),B])
    R = np.eye(A.shape[1])*pen; R[0,0] = 0
    return B @ np.linalg.solve(A.T@A+R, A.T@y)

def _corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float); m=np.isfinite(a)&np.isfinite(b)
    return float(np.corrcoef(a[m],b[m])[0,1]) if m.sum()>3 else np.nan

def _bestlag(x,y,mx=10):
    best=(0,-9); n=len(x)
    for L in range(-mx,mx+1):
        a,b=(x[:n-L],y[L:]) if L>=0 else (x[-L:],y[:n+L])
        c=_corr(a,b)
        if np.isfinite(c) and c>best[1]: best=(L,c)
    return best

def ara_forecast(series, period=None, horizon=6, leading=None, train_frac=1/PHI):
    """Strict-causal ARA forecast. Returns prediction + warning + confidence + honest diagnostics."""
    ni = np.asarray(series, float); n = len(ni)
    P = float(period) if period else _dominant_period(ni)
    cut = int(n*train_frac); h = int(horizon)
    gold = _causal_bandpass(ni, P, 0.25)
    v = gold - np.concatenate([[gold[0]], gold[:-1]]); om = 2*np.pi/P
    Ago = np.sqrt(gold**2 + (v/om)**2); th = np.arctan2(-v/om, gold)
    L = _trail_mean(ni, max(12,int(P)))
    fp = th + 2*np.pi*h/P
    reservoir = _trail_mean(-ni, max(3,int(P/6)))
    rz = (reservoir - np.nanmean(reservoir))/(np.nanstd(reservoir)+1e-9)
    araskew = _trail_skew(ni, max(8,int(P/3)))
    home_lags = [l for l in [1,2,3,6,12,int(round(P/4)),int(round(P/2)),int(round(P))] if 0<l<n//3]
    start = max(home_lags)+2
    def feat(o, with_lead):
        cols = [np.array([[ni[t-l] for l in home_lags] for t in o]),
                Ago[o]*np.cos(fp[o]), Ago[o]*np.sin(fp[o]),
                rz[o], araskew[o], (rz[o]*Ago[o])]
        if with_lead and leading is not None:
            lz = (np.asarray(leading,float)-np.nanmean(leading))/(np.nanstd(leading)+1e-9)
            cols += [lz[o], lz[np.maximum(0,o-max(1,h//2))]]
        return np.column_stack(cols)
    use_lead = leading is not None
    o = np.arange(start, n-h); tr = o[o+h<cut]; te = o[o>=cut]
    if len(te) < 20:
        return {"error":"series too short for this horizon", "period":P}
    d = ni[tr+h]-ni[tr]
    pred = ni[te] + _ridge(feat(tr,use_lead), d, feat(te,use_lead))
    truth = ni[te+h]; cur = ni[te]; persistence = cur.copy()
    sig_train = np.std(ni[tr+h] - L[tr+h])
    dev = pred - L[te]; dz = (dev - dev.mean())/(np.std(dev)+1e-9)
    warning = L[te] + dz*sig_train
    res_tr = ni[tr+h] - (ni[tr] + _ridge(feat(tr,use_lead), d, feat(tr,use_lead)))
    cf = lambda idx: np.column_stack([Ago[idx], rz[idx], araskew[idx]])
    confidence = np.clip(_ridge(cf(tr), np.abs(res_tr), cf(te)), 0.05, None)
    return {
        "period": P, "horizon": h, "n_test": len(te),
        "prediction": pred, "truth": truth, "warning": warning, "confidence": confidence,
        "test_index": te,
        "skill_on_change": _corr(pred-cur, truth-cur),
        "direction_hit": float(np.mean(np.sign(pred-cur)[truth!=cur]==np.sign(truth-cur)[truth!=cur])),
        "value_corr": _corr(pred, truth),
        "persistence_corr": _corr(persistence, truth),
        "amp_ratio": np.std(pred-L[te])/np.std(truth-L[te]),
        "warning_amp_ratio": np.std(warning-L[te])/np.std(truth-L[te]),
        "lag_months": _bestlag(pred, truth)[0],
        "note": "skill_on_change is the honest metric (persistence=0). lag is the MMSE hedge, not a leak; "
                "supply a LEADING series to tighten it. magnitude is a lean, not an exact peak.",
    }

if __name__ == "__main__":
    rng = np.random.default_rng(0); t = np.arange(1200)
    x = np.sin(2*np.pi*t/48) + 0.4*np.sin(2*np.pi*t/19) + 0.3*rng.standard_normal(1200)
    r = ara_forecast(x, horizon=6)
    print("synthetic:", {k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()
          if k in ("period","skill_on_change","value_corr","persistence_corr","lag_months","amp_ratio","warning_amp_ratio")})
