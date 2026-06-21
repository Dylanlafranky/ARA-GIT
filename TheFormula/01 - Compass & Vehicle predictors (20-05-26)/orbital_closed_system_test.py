"""
Closed-system orbital test of the framework's point prediction.

Setup: simulate Sun + Jupiter + Saturn for 8000 years.
Track Jupiter's osculating eccentricity sampled every year.

Dylan's prediction (2026-05-01): closed-system point prediction should work,
BUT ~5% will come from other orbital bodies — the coastline paradox.

Tests:
  M1 mean-only baseline
  M2 AR-blind (persistence)
  M3 Jupiter-only framework forecast (closed-system mode)
  M4 LR with Saturn feeder (broadband)
  M5 Framework with Saturn feeder (topology + flow)

Hypothesis:
  - M3 should be MUCH better than for ECG/ENSO (closed system, point pred works)
  - M5 - M3 should be small but positive (Saturn ~5% perturbation)
  - M5 - M4 should be positive (framework structure beats plain LR)
"""
import json, os, math
import numpy as np
from scipy.integrate import solve_ivp

PHI = 1.6180339887498949
G = 4*np.pi**2  # AU^3 / M_sun / yr^2

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

OUT = _resolve(r"F:\SystemFormulaFolder\TheFormula\orbital_closed_data.js")

# --- Bodies: Sun, Jupiter, Saturn (real-ish masses and orbits) ---
masses = np.array([1.0, 9.5479e-4, 2.8589e-4])  # solar masses
a_jup, e_jup = 5.2026, 0.0489
a_sat, e_sat = 9.5549, 0.0565

def kepler_init_xy(a, e, M_central=1.0, true_anom=0.0, omega=0.0):
    """Place body at given true anomaly; return position and velocity."""
    p = a * (1 - e**2)
    r = p / (1 + e*np.cos(true_anom))
    # In orbital plane (omega rotates the orbit)
    nu = true_anom + omega
    pos = np.array([r*np.cos(nu), r*np.sin(nu), 0.0])
    # Velocity
    h = np.sqrt(G * M_central * p)
    vr = (G*M_central/h) * e * np.sin(true_anom)
    vt = h / r
    vel = np.array([vr*np.cos(nu) - vt*np.sin(nu),
                    vr*np.sin(nu) + vt*np.cos(nu), 0.0])
    return pos, vel

# Initial state — distinct true anomalies and orbital orientations
pj, vj = kepler_init_xy(a_jup, e_jup, M_central=1.0, true_anom=0.0, omega=0.0)
ps, vs = kepler_init_xy(a_sat, e_sat, M_central=1.0, true_anom=np.pi/3, omega=np.pi/4)

# Move to barycenter frame
pos = np.array([np.zeros(3), pj, ps])
vel = np.array([np.zeros(3), vj, vs])
# Sun pos/vel from momentum conservation
pos[0] = -(masses[1]*pos[1] + masses[2]*pos[2]) / masses[0]
vel[0] = -(masses[1]*vel[1] + masses[2]*vel[2]) / masses[0]

y0 = np.concatenate([pos.flatten(), vel.flatten()])

def rhs(t, y):
    pos = y[:9].reshape(3,3)
    vel = y[9:18].reshape(3,3)
    acc = np.zeros((3,3))
    for i in range(3):
        for j in range(3):
            if i==j: continue
            r = pos[j] - pos[i]
            dist = np.sqrt(np.dot(r,r))
            acc[i] += G * masses[j] * r / dist**3
    return np.concatenate([vel.flatten(), acc.flatten()])

T_END = 8000.0  # years
DT_SAMPLE = 1.0  # years
t_eval = np.arange(0, T_END, DT_SAMPLE)
print(f"Integrating Sun-Jupiter-Saturn for {T_END:.0f} years (sampling every {DT_SAMPLE} yr)...")
sol = solve_ivp(rhs, (0, T_END), y0, t_eval=t_eval, method='DOP853', rtol=1e-10, atol=1e-13)
print(f"Integration ok, n_samples={len(sol.t)}, final time {sol.t[-1]:.0f}")

# Compute osculating eccentricity of Jupiter (relative to Sun) at each time
def osculating_elements(pos_rel, vel_rel, mu):
    """Return (a, e) given relative position and velocity from central body."""
    r_vec = pos_rel; v_vec = vel_rel
    r = np.linalg.norm(r_vec); v2 = np.dot(v_vec, v_vec)
    h_vec = np.cross(r_vec, v_vec)
    e_vec = np.cross(v_vec, h_vec)/mu - r_vec/r
    e = np.linalg.norm(e_vec)
    energy = v2/2 - mu/r
    a = -mu/(2*energy)
    return a, e

ecc_jup = np.zeros(len(sol.t))
ecc_sat = np.zeros(len(sol.t))
a_jup_t = np.zeros(len(sol.t))
a_sat_t = np.zeros(len(sol.t))
for i in range(len(sol.t)):
    p_sun = sol.y[0:3, i]; v_sun = sol.y[9:12, i]
    p_jup = sol.y[3:6, i] - p_sun; v_jup = sol.y[12:15, i] - v_sun
    p_sat = sol.y[6:9, i] - p_sun; v_sat = sol.y[15:18, i] - v_sun
    a, e = osculating_elements(p_jup, v_jup, G*(masses[0]+masses[1]))
    a_jup_t[i] = a; ecc_jup[i] = e
    a, e = osculating_elements(p_sat, v_sat, G*(masses[0]+masses[2]))
    a_sat_t[i] = a; ecc_sat[i] = e

print(f"Jupiter ecc:  min={ecc_jup.min():.5f} mean={ecc_jup.mean():.5f} max={ecc_jup.max():.5f} std={ecc_jup.std():.5f}")
print(f"Saturn  ecc:  min={ecc_sat.min():.5f} mean={ecc_sat.mean():.5f} max={ecc_sat.max():.5f} std={ecc_sat.std():.5f}")

# === FRAMEWORK TEST ===
N = len(ecc_jup); SPLIT = N//2
y_tr = ecc_jup[:SPLIT]; y_te = ecc_jup[SPLIT:]
sat_tr = ecc_sat[:SPLIT]; sat_te = ecc_sat[SPLIT:]
mean_tr = float(np.mean(y_tr))
print(f"Train n={SPLIT}, Test n={N-SPLIT}, mean={mean_tr:.5f}, train std={np.std(y_tr):.5f}, test std={np.std(y_te):.5f}")

# φ-rungs in years — Jupiter period ~11.86 yr is φ^5.05; Great Inequality ~880 yr is φ^14
# Use rungs k=5..15 covering 12 yr to ~1900 yr
def rung_band(arr, period_yr, dt=1.0, bw=0.4):
    """Bandpass at period_yr ±bw fraction (default ±40%, was ±20%)."""
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_yr; f_lo = (1-bw)*f_c; f_hi = (1+bw)*f_c
    F[(freqs<f_lo)|(freqs>f_hi)] = 0
    return np.real(np.fft.irfft(F, n=n))

RUNGS = [(k, PHI**k) for k in range(5, 16)]
print(f"Rungs (years): {[(k, round(p,1)) for k,p in RUNGS]}")

R_jup = {k: rung_band(ecc_jup, p) for k,p in RUNGS}
R_sat = {k: rung_band(ecc_sat, p) for k,p in RUNGS}

# Coupling matrix on training half
print("\nJupiter ← Saturn coupling matrix (train corr by rung):")
print("  J\\S  " + "  ".join([f"k={k:>2d}" for k,_ in RUNGS]))
CM = {}
for tk,_ in RUNGS:
    row = []
    for sk,_ in RUNGS:
        a = R_jup[tk][:SPLIT]; b = R_sat[sk][:SPLIT]
        if np.std(a)<1e-12 or np.std(b)<1e-12: c = 0.0
        else: c = float(np.corrcoef(a,b)[0,1])
        CM[(tk,sk)] = c; row.append(c)
    print(f"  k={tk:2d}  " + "  ".join([f"{c:+.2f}" for c in row]))

# --- Baselines ---
def metrics(y, p):
    if np.std(p)<1e-12: corr=0.0
    else: corr = float(np.corrcoef(y,p)[0,1])
    return dict(corr=corr,
                rmse=float(np.sqrt(np.mean((y-p)**2))),
                mae=float(np.mean(np.abs(y-p))),
                pred_std=float(np.std(p)))

n_te = len(y_te)
M1 = np.full(n_te, mean_tr)
M2 = np.zeros(n_te); M2[0] = y_tr[-1]
for i in range(1, n_te): M2[i] = M2[i-1]*0.999 + 0.001*mean_tr

# --- M3: Jupiter-only framework forecast (per-rung AR) ---
def fit_ar1(s):
    if np.std(s)<1e-12: return 0.0, float(np.mean(s))
    a = float(np.corrcoef(s[:-1], s[1:])[0,1])
    return (0.0 if not np.isfinite(a) else a), float(np.mean(s))

ar = {k: fit_ar1(R_jup[k][:SPLIT]) for k,_ in RUNGS}
M3 = np.full(n_te, mean_tr)
for k,_ in RUNGS:
    a, mu = ar[k]; prev = R_jup[k][SPLIT-1]
    for i in range(n_te):
        v = mu + a*(prev - mu); M3[i] += v; prev = v

# --- M4: LR Jupiter ~ Saturn (broadband contemporaneous) ---
X_tr = np.column_stack([sat_tr, np.ones_like(sat_tr)])
beta, *_ = np.linalg.lstsq(X_tr, y_tr, rcond=None)
M4 = np.column_stack([sat_te, np.ones_like(sat_te)]) @ beta

# --- M5: framework with Saturn feeder (per-rung within structure) ---
M5 = np.full(n_te, mean_tr)
rung_coefs = {}
for k,_ in RUNGS:
    X = np.column_stack([R_sat[k][:SPLIT], np.ones(SPLIT)])
    y = R_jup[k][:SPLIT]
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rung_coefs[k] = b
    Xt = np.column_stack([R_sat[k][SPLIT:], np.ones(n_te)])
    M5 += Xt @ b

# --- M5b: M5 + AR memory blend ---
M5b = np.full(n_te, mean_tr)
for k,_ in RUNGS:
    a, mu = ar[k]; prev = R_jup[k][SPLIT-1]
    Xt = np.column_stack([R_sat[k][SPLIT:], np.ones(n_te)])
    feeder = Xt @ rung_coefs[k]
    for i in range(n_te):
        v = 0.5*(mu + a*(prev - mu)) + 0.5*feeder[i]
        M5b[i] += v; prev = v

# --- Metrics ---
R = dict(
    M1_mean=metrics(y_te, M1),
    M2_AR=metrics(y_te, M2),
    M3_Jupiter_only=metrics(y_te, M3),
    M4_LR_Saturn=metrics(y_te, M4),
    M5_FW_Saturn=metrics(y_te, M5),
    M5b_FW_AR=metrics(y_te, M5b),
)
print(f"\n========= TEST RESULTS (n={n_te}) =========")
print(f"True test std: {np.std(y_te):.5f}")
for name, r in R.items():
    print(f"  {name:18s}: corr={r['corr']:+.4f}  rmse={r['rmse']:.5f}  pred_std={r['pred_std']:.5f}")
print(f"\nKey deltas:")
print(f"  M3 (Jupiter-only closed): {R['M3_Jupiter_only']['corr']:+.4f}")
print(f"  M5 - M3 (Saturn feeder lift): {R['M5_FW_Saturn']['corr'] - R['M3_Jupiter_only']['corr']:+.4f}")
print(f"  M5 - M4 (framework vs plain LR): {R['M5_FW_Saturn']['corr'] - R['M4_LR_Saturn']['corr']:+.4f}")
print(f"  M5b - M5 (AR memory addition): {R['M5b_FW_AR']['corr'] - R['M5_FW_Saturn']['corr']:+.4f}")

# Save
out = dict(
    times=sol.t.tolist(),
    ecc_jup=ecc_jup.tolist(),
    ecc_sat=ecc_sat.tolist(),
    a_jup=a_jup_t.tolist(),
    a_sat=a_sat_t.tolist(),
    split_idx=int(SPLIT),
    preds=dict(
        M1=M1.tolist(), M2=M2.tolist(), M3=M3.tolist(),
        M4=M4.tolist(), M5=M5.tolist(), M5b=M5b.tolist(),
    ),
    metrics=R,
    rungs=[[k,p] for k,p in RUNGS],
    coupling={f"{k1}_{k2}":v for (k1,k2),v in CM.items()},
    rung_coefs={str(k): list(map(float,v)) for k,v in rung_coefs.items()},
    lr_coefs=dict(saturn=float(beta[0]), const=float(beta[1])),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ORBITAL_CLOSED = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
