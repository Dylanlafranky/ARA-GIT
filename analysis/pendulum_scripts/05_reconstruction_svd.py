"""
Element 4 - reconstruct the motion from data modes (SVD / proper-orthogonal decomp).

SVD of the three rest-centred angles. Reports variance per mode, the mode shapes
(common vs differential), reconstruction fidelity from the top-k modes, and
saves two figures: mode shapes / coefficients, and true-vs-2-mode-reconstruction
per arm.

Expected (run1): mode1 89% (common clock, all same sign, weights = amplitude
ladder), mode2 10.4% (arm1 vs arm3 anti-phase); 2 modes = 99.4% variance,
reconstruction corr 0.984 / 0.994 / 1.000 for arms 1/2/3.

This is an IN-SAMPLE decomposition (shows the motion lives in 2 modes); for
out-of-sample forecasting see 06 and 07.

MEASUREMENT CATEGORY: SVD/POD is a standard decomposition. Reading mode-1 as
"the common-mode clock" and mode-2 as "the 1v3 anti-phase pair" is an
ARA-INSPIRED INTERPRETATION of that decomposition, not a canonical ARA reading
(SVD modes are not themselves ARA). The mapping is reported as a lens; the
numbers (variance, reconstruction corr) stand on their own as standard POD.

Run:  python 05_reconstruction_svd.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pendulum_common import load_triple, rest_centered, OUT_DIR


def main(run="run1"):
    t, th_raw, vel, fs = load_triple(run, decimate=10)
    th = rest_centered(th_raw)
    X = np.vstack([th[1], th[2], th[3]]).T
    Xc = X - X.mean(0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = S ** 2 / np.sum(S ** 2)
    print(f"RECONSTRUCTION via data modes (run={run})")
    print("variance explained per mode:", np.round(var, 3))
    print("mode shapes (arm participation):")
    for k in range(3):
        v = Vt[k] * np.sign(Vt[k][np.argmax(np.abs(Vt[k]))])
        tag = "COMMON" if (np.all(v > 0) or np.all(v < 0)) else ("DIFFERENTIAL 1v3" if v[0] * v[2] < 0 else "mixed")
        print(f"  mode{k+1} ({var[k]*100:4.1f}%): arm1={v[0]:+.2f} arm2={v[1]:+.2f} arm3={v[2]:+.2f}  -> {tag}")
    print("reconstruction fidelity (corr per arm):")
    for k in (1, 2, 3):
        Xk = U[:, :k] @ np.diag(S[:k]) @ Vt[:k]
        c = [np.corrcoef(Xk[:, j], Xc[:, j])[0, 1] for j in range(3)]
        print(f"  top-{k}: arm1 {c[0]:.3f}  arm2 {c[1]:.3f}  arm3 {c[2]:.3f}")

    # figure 1: mode shapes + coefficients
    tc = U * S
    fig = plt.figure(figsize=(13, 5), facecolor="#0e1116"); gs = fig.add_gridspec(1, 2, wspace=0.25)
    ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor("#161b22")
    x = np.arange(3); w = 0.25
    for k in range(3):
        v = Vt[k] * np.sign(Vt[k][np.argmax(np.abs(Vt[k]))])
        ax.bar(x + (k - 1) * w, v, w, label=f"mode{k+1} ({var[k]*100:.0f}%)")
    ax.set_xticks(x); ax.set_xticklabels(["arm1", "arm2", "arm3"], color="#ddd")
    ax.axhline(0, color="#888", lw=0.6); ax.set_title("Mode shapes", color="#eee", fontsize=10)
    ax.legend(fontsize=7, facecolor="#161b22", labelcolor="#ddd"); ax.tick_params(colors="#aaa")
    ax = fig.add_subplot(gs[0, 1]); ax.set_facecolor("#161b22"); ww = t < 12
    ax.plot(t[ww], tc[ww, 0], lw=0.8, color="#3fb950", label="mode1 common (clock)")
    ax.plot(t[ww], tc[ww, 1], lw=0.8, color="#b197fc", label="mode2 differential (1v3)")
    ax.set_title("Mode time-coefficients (0-12s)", color="#eee", fontsize=10)
    ax.legend(fontsize=7, facecolor="#161b22", labelcolor="#ddd"); ax.tick_params(colors="#aaa")
    out1 = os.path.join(OUT_DIR, "pendulum_reconstruction.png")
    plt.tight_layout(); plt.savefig(out1, dpi=140, facecolor="#0e1116", bbox_inches="tight"); print("saved", out1)

    # figure 2: true vs 2-mode reconstruction per arm
    X2 = U[:, :2] @ np.diag(S[:2]) @ Vt[:2]
    cols = ["#74c0fc", "#ffa94d", "#ff6b6b"]; names = ["arm1", "arm2", "arm3"]; W = t <= 20
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), facecolor="#0e1116", sharex=True)
    for j in range(3):
        ax = axes[j]; ax.set_facecolor("#161b22")
        ax.plot(t[W], Xc[W, j], lw=1.6, color=cols[j], label=f"{names[j]} TRUE")
        ax.plot(t[W], X2[W, j], lw=1.1, color="#ffffff", ls="--", label=f"{names[j]} reconstructed (2 modes)")
        c = np.corrcoef(Xc[:, j], X2[:, j])[0, 1]
        ax.set_title(f"{names[j]} - true vs 2-mode reconstruction (corr 60s = {c:.3f})", color="#eee", fontsize=10)
        ax.legend(fontsize=8, facecolor="#161b22", labelcolor="#ddd", loc="upper right")
        ax.tick_params(colors="#aaa"); ax.set_ylabel("angle (rad)", color="#bbb", fontsize=8)
        ax.axhline(0, color="#3fb950", ls=":", lw=0.7)
    axes[2].set_xlabel("time (s)", color="#ccc"); plt.tight_layout()
    out2 = os.path.join(OUT_DIR, "pendulum_recon_vs_true.png")
    plt.savefig(out2, dpi=140, facecolor="#0e1116"); print("saved", out2)


if __name__ == "__main__":
    main()
