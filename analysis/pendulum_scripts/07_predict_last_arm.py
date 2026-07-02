"""
Element 5b - predict the LAST (deepest, most chaotic) arm from the structure.

Hold arm-3 out entirely and predict it strictly causally from ONLY arms 1-2's
past windows (never arm-3 as input). Compare to arm-3's own self-AR for context.
Saves a nowcast + 2s-forecast vs truth figure.

Causality: weights fit on training half only; features are past samples of
arms 1-2 at or before the origin; target arm-3 at origin+h is held-out truth.

Expected: arm-3 from arms 1-2 only = corr 0.99 nowcast through 2s, and it BEATS
arm-3's own self-AR at 2s (0.988 vs 0.959) -> the deepest arm is slaved to the
shallower structure (better forecast from the calm arms than from itself).
Boundary: holds because this regime is locked/quasi-periodic; a chaotic/tumbling
regime would give arm-3 independent content and degrade this.

Run:  python 07_predict_last_arm.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pendulum_common import load_triple, rest_centered, OUT_DIR

P_LAG = 80
LAM = 1e-1


def setup(run="run1"):
    t, th_raw, vel, fs = load_triple(run, decimate=200)  # 50 Hz
    th = rest_centered(th_raw)
    N = len(th[1]); split = N // 2
    th = {i: th[i] - th[i][:split].mean() for i in (1, 2, 3)}
    return t, th, fs, N, split


def predict_arm3(th, N, split, h, use_self=False):
    rows = range(P_LAG, split - h)
    if use_self:
        F = np.array([th[3][t - P_LAG:t] for t in rows])
    else:
        F = np.array([np.concatenate([th[1][t - P_LAG:t], th[2][t - P_LAG:t]]) for t in rows])
    y = np.array([th[3][t + h] for t in rows])
    w = np.linalg.solve(F.T @ F + LAM * np.eye(F.shape[1]), F.T @ y)
    rows2 = list(range(split, N - h))
    if use_self:
        Ft = np.array([th[3][t - P_LAG:t] for t in rows2])
    else:
        Ft = np.array([np.concatenate([th[1][t - P_LAG:t], th[2][t - P_LAG:t]]) for t in rows2])
    yt = np.array([th[3][t + h] for t in rows2])
    pr = Ft @ w
    full = np.full(N, np.nan)
    for r, t in enumerate(rows2):
        full[t + h] = pr[r]
    return np.corrcoef(pr, yt)[0, 1], full


def main(run="run1"):
    t, th, fs, N, split = setup(run)
    print("PREDICT ARM-3 from ONLY arms 1-2 history - strictly causal")
    print(f'{"horizon":<9}{"from arms1-2":>14}{"arm3 self-AR":>14}')
    for hs in [0.0, 0.2, 0.5, 1.0, 2.0]:
        h = int(round(hs * fs))
        c_oth, _ = predict_arm3(th, N, split, h, False)
        c_self, _ = predict_arm3(th, N, split, h, True)
        print(f'{("NOWCAST" if hs==0 else str(hs)+"s"):<9}{c_oth:14.3f}{c_self:14.3f}')

    fig, axes = plt.subplots(2, 1, figsize=(13, 7.5), facecolor="#0e1116", sharex=True)
    for ax, hs, lab in [(axes[0], 0.0, "NOWCAST (infer arm-3 now)"), (axes[1], 2.0, "2s-ahead FORECAST")]:
        h = int(round(hs * fs))
        c, pr = predict_arm3(th, N, split, h, False)
        v = ~np.isnan(pr); ax.set_facecolor("#161b22")
        ax.plot(t[v], th[3][v], lw=1.7, color="#ff6b6b", label="arm-3 TRUTH")
        ax.plot(t[v], pr[v], lw=1.1, color="#ffffff", ls="--", label="arm-3 predicted from ONLY arms 1-2")
        ax.set_title(f"{lab} - arm-3 from arms 1-2 only, held-out test   corr {c:.3f}", color="#eee", fontsize=10)
        ax.legend(fontsize=8.5, facecolor="#161b22", labelcolor="#ddd", loc="upper right")
        ax.tick_params(colors="#aaa"); ax.set_ylabel("arm-3 angle (rad)", color="#bbb", fontsize=8)
        ax.axhline(0, color="#3fb950", ls=":", lw=0.6)
    axes[1].set_xlabel("time (s)  [test half held out]", color="#ccc"); plt.tight_layout()
    out = os.path.join(OUT_DIR, "pendulum_predict_last_arm.png")
    plt.savefig(out, dpi=140, facecolor="#0e1116"); print("saved", out)


if __name__ == "__main__":
    main()
