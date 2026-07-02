"""
Element 5a - STRICTLY CAUSAL forecast of the 2-mode reconstruction.

Direct linear forecaster on lagged past samples of the mode coefficients.
Causality discipline (all enforced here):
  - mode shapes (SVD) fit on the TRAINING half only; test half never touches it
  - centering uses the training mean only
  - NO non-causal filters (no filtfilt / Hilbert); features are past samples only
  - forecast weights fit on training pairs only, applied out-of-sample
  - target at origin+h is held-out truth, never a feature
  - baselines: persistence (last value) and one-period-ago (1.333 s)

Honest result: raw skill looks high (~0.92 @ 5 s) BUT the one-period-ago baseline
scores ~0.98 flat at every horizon and ties/beats the model -> the regime is
quasi-periodic (a clock), NOT a demonstration of forecasting chaos. Only mode 3
(0.6%) is genuinely chaotic and dies within ~1 s.

Run:  python 06_forecast_causal.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pendulum_common import load_triple, rest_centered, OUT_DIR

P_LAG = 80          # lag window (~1.6 s at 50 Hz)
LAM = 1e-2          # ridge
PDOM_S = 1.333      # one dominant period (s) for the period-ago baseline


def setup(run="run1"):
    t, th_raw, vel, fs = load_triple(run, decimate=200)  # 50 Hz
    th = rest_centered(th_raw)
    X = np.vstack([th[1], th[2], th[3]]).T
    N = len(X); split = N // 2
    mu = X[:split].mean(0)
    Xc = X - mu
    _, _, Vt = np.linalg.svd(Xc[:split], full_matrices=False)  # CAUSAL: train-only modes
    return t, Xc, Vt, fs, N, split


def build(c, h, t0, t1, p):
    rows = range(t0, t1 - h)
    return (np.array([c[t - p:t] for t in rows]),
            np.array([c[t + h] for t in rows]),
            list(rows))


def main(run="run1"):
    t, Xc, Vt, fs, N, split = setup(run)
    K = 3
    coeffs = Xc @ Vt[:K].T
    Pdom = int(round(PDOM_S * fs))
    print(f"strictly-causal direct forecast | train={split/fs:.0f}s test={(N-split)/fs:.0f}s | "
          f"lags={P_LAG} ({P_LAG/fs:.1f}s)")
    print("per-mode skill (corr) and model-vs-baselines for the chaotic mode2:")
    print(f'{"horizon":<8}{"mode1":>8}{"mode2":>8}{"mode3":>8} | {"AR / persist / periodAgo (mode2)":>34}')
    for hs in [0.2, 0.5, 1, 2, 3, 5]:
        h = int(round(hs * fs)); skill = []; perA = None; persA = None; arA = None
        for k in range(K):
            Xtr, ytr, _ = build(coeffs[:, k], h, P_LAG, split, P_LAG)
            w = np.linalg.solve(Xtr.T @ Xtr + LAM * np.eye(P_LAG), Xtr.T @ ytr)
            Xte, yte, rows = build(coeffs[:, k], h, split, N, P_LAG)
            ph = Xte @ w
            skill.append(np.corrcoef(ph, yte)[0, 1])
            if k == 1:
                idx = np.array(rows) + h
                # persistence = predict y(t+h) with the value at the forecast origin t = y((t+h)-h)
                persA = np.corrcoef(coeffs[idx - h, k], coeffs[idx, k])[0, 1]
                # period-ago = predict y(t+h) with the value one dominant period earlier
                perA = np.corrcoef(coeffs[idx - Pdom, k], coeffs[idx, k])[0, 1]
                arA = skill[1]
        print(f"{str(hs)+'s':<8}{skill[0]:8.3f}{skill[1]:8.3f}{skill[2]:8.3f} | "
              f"AR {arA:.3f} / persist {persA:.3f} / periodAgo {perA:.3f}")

    # figure: 2s forecast vs truth (reconstructed angles), all arms, with period-ago baseline
    H = 2.0; h = int(round(H * fs)); K2 = 2
    coeffs2 = Xc @ Vt[:K2].T
    predC = np.full((N, K2), np.nan)
    for k in range(K2):
        Xtr, ytr, _ = build(coeffs2[:, k], h, P_LAG, split, P_LAG)
        w = np.linalg.solve(Xtr.T @ Xtr + LAM * np.eye(P_LAG), Xtr.T @ ytr)
        Xte, yte, rows = build(coeffs2[:, k], h, split, N, P_LAG)
        ph = Xte @ w
        for r, tt in enumerate(rows):
            predC[tt + h, k] = ph[r]
    valid = ~np.isnan(predC[:, 0]); idx = np.where(valid)[0]
    Xhat = np.full((N, 3), np.nan); Xhat[valid] = predC[valid, :K2] @ Vt[:K2]
    XpA = np.full((N, 3), np.nan); XpA[idx] = coeffs2[idx - Pdom, :K2] @ Vt[:K2]
    cols = ["#74c0fc", "#ffa94d", "#ff6b6b"]; names = ["arm1", "arm2", "arm3"]
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), facecolor="#0e1116", sharex=True)
    for j in range(3):
        ax = axes[j]; ax.set_facecolor("#161b22")
        ax.plot(t[valid], Xc[valid, j], lw=1.7, color=cols[j], label=f"{names[j]} TRUTH")
        ax.plot(t[valid], Xhat[valid, j], lw=1.1, color="#ffffff", ls="--", label="causal forecast (2s ahead)")
        ax.plot(t[valid], XpA[valid, j], lw=0.9, color="#888", ls=":", label="period-ago baseline")
        cf = np.corrcoef(Xhat[valid, j], Xc[valid, j])[0, 1]
        cp = np.corrcoef(XpA[valid, j], Xc[valid, j])[0, 1]
        ax.set_title(f"{names[j]} (held-out test) - forecast corr {cf:.3f} vs period-ago {cp:.3f}", color="#eee", fontsize=10)
        ax.legend(fontsize=8, facecolor="#161b22", labelcolor="#ddd", loc="upper right")
        ax.tick_params(colors="#aaa"); ax.set_ylabel("angle (rad)", color="#bbb", fontsize=8)
        ax.axhline(0, color="#3fb950", ls=":", lw=0.6)
    axes[2].set_xlabel("time (s)  [test half held out]", color="#ccc"); plt.tight_layout()
    out = os.path.join(OUT_DIR, "pendulum_forecast_vs_truth.png")
    plt.savefig(out, dpi=140, facecolor="#0e1116"); print("saved", out)


if __name__ == "__main__":
    main()
