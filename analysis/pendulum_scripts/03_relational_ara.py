"""
Relational ARA between arms - each arm read in its neighbour's frame (the bend).

bend(A->B) = 1 + wrap(theta_B - theta_A)/pi :  1.0 = arms inline (rest relation),
0/2 = one arm folded straight back over the other (singularity). Computes the
three relational traces, where they sit (ridge vs poles), pairwise correlation,
and saves a 4-panel figure (time series, distributions, phase portrait, full
lower-joint trace).

Expected (run1): upper joint (bend 1-2) hugs the ridge (std 0.04, 98% near 1.0);
lower joint (bend 2-3) ~3x wider (std 0.12); none reach the poles (gentle run).

Run:  python 03_relational_ara.py
"""
import os
import itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pendulum_common import load_triple, rest_centered, wrap, OUT_DIR


def main(run="run1"):
    t, th_raw, vel, fs = load_triple(run, decimate=10)
    # Define the bend on REST-RELATIVE angles so the inline/rest relation lands
    # exactly on the 1.0 ridge even when arms' rest angles differ slightly.
    # (Old version used raw th_B - th_A, which assumes equal rest angles and can
    # offset the ridge from 1.0.)
    th = rest_centered(th_raw)
    bend = {
        "12": 1 + wrap(th[2] - th[1]) / np.pi,
        "23": 1 + wrap(th[3] - th[2]) / np.pi,
        "13": 1 + wrap(th[3] - th[1]) / np.pi,
    }
    print(f"RELATIONAL ARA between arms (run={run}; 1.0=inline ridge, 0/2=folded singularity)")
    for k in ["12", "23", "13"]:
        b = bend[k]
        ridge = np.mean(np.abs(b - 1) < 0.1) * 100
        pole = np.mean(np.minimum(np.abs(b - 0), np.abs(b - 2)) < 0.25) * 100
        print(f"  bend{k}: range [{b.min():.3f},{b.max():.3f}]  std {b.std():.3f}  "
              f"%near-ridge {ridge:.0f}  %near-pole {pole:.1f}")
    print("correlations:")
    for a, c in itertools.combinations(["12", "23", "13"], 2):
        print(f"  bend{a} vs bend{c}: r={np.corrcoef(bend[a], bend[c])[0, 1]:+.2f}")

    fig = plt.figure(figsize=(13, 8), facecolor="#0e1116")
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.24)
    col = {"12": "#74c0fc", "23": "#ff6b6b", "13": "#b197fc"}
    ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor("#161b22"); w = t < 12
    for k in ["12", "23", "13"]:
        ax.plot(t[w], bend[k][w], lw=0.8, color=col[k], label=f"bend {k}")
    for y, c in [(1, "#3fb950"), (0, "#666"), (2, "#666")]:
        ax.axhline(y, color=c, ls="--" if y == 1 else "-", lw=1 if y == 1 else 0.6)
    ax.set_title("Relational ARA vs time (0-12s)", color="#eee", fontsize=10)
    ax.legend(fontsize=7, facecolor="#161b22", labelcolor="#ddd"); ax.tick_params(colors="#aaa"); ax.set_ylabel("ARA", color="#ccc")
    ax = fig.add_subplot(gs[0, 1]); ax.set_facecolor("#161b22")
    for k in ["12", "23", "13"]:
        ax.hist(bend[k], bins=120, alpha=0.5, color=col[k], label=f"bend {k}", density=True)
    ax.axvline(1, color="#3fb950", ls="--", lw=1)
    ax.set_title("Where each relation sits", color="#eee", fontsize=10)
    ax.legend(fontsize=7, facecolor="#161b22", labelcolor="#ddd"); ax.tick_params(colors="#aaa"); ax.set_xlabel("ARA", color="#ccc")
    ax = fig.add_subplot(gs[1, 0]); ax.set_facecolor("#161b22")
    ax.scatter(bend["12"], bend["23"], s=0.4, c=t, cmap="turbo", alpha=0.5)
    ax.axvline(1, color="#3fb950", ls="--", lw=0.7); ax.axhline(1, color="#3fb950", ls="--", lw=0.7)
    ax.set_xlabel("bend 1-2 (upper joint)", color="#ccc"); ax.set_ylabel("bend 2-3 (lower joint)", color="#ccc")
    ax.set_title("Relational phase portrait (colour=time)", color="#eee", fontsize=10); ax.tick_params(colors="#aaa")
    ax = fig.add_subplot(gs[1, 1]); ax.set_facecolor("#161b22")
    ax.plot(t, bend["23"], lw=0.3, color="#ff6b6b")
    for y, c in [(1, "#3fb950"), (0, "#888"), (2, "#888")]:
        ax.axhline(y, color=c, ls="--" if y == 1 else "-", lw=1 if y == 1 else 0.6)
    ax.set_title("Lower joint (bend 2-3) full record", color="#eee", fontsize=10)
    ax.tick_params(colors="#aaa"); ax.set_xlabel("time (s)", color="#ccc"); ax.set_ylabel("ARA", color="#ccc")
    out = os.path.join(OUT_DIR, "pendulum_relational_ara.png")
    plt.savefig(out, dpi=140, facecolor="#0e1116", bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
