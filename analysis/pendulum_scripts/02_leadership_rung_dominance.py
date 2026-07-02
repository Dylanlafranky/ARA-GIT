"""
Leadership (who leads each big swing, 3-way) and rung -> dominance.

For each arm-1 swing, find the nearest turn of arms 2 and 3 within +-0.5 s;
the leader is whichever arm turns first. Then per arm: share of swings led,
number of dominance blocks (runs), mean and max block length. Replicates the
"lowest rung = dominant wave" finding across runs and saves the 3-way figure.

Expected: arm-3 (bottom) leads ~41-44% in all 3 runs and holds the longest
blocks; arm-1/arm-2 split the rest (~27-30%), order not stable. ~80 switches.

Run:  python 02_leadership_rung_dominance.py
"""
import os
import numpy as np
from itertools import groupby
from scipy.signal import find_peaks
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pendulum_common import load_triple, ara_position, OUT_DIR, RUNS

PDOM_S = 1.333   # shared dominant period (s); real turns are ~half a period apart
PROM = 0.02      # ara-position prominence floor (~0.06 rad) to reject noise extrema


def leaders_of(run):
    t, th_raw, vel, fs = load_triple(run, decimate=20)  # 500 Hz
    ara = ara_position(th_raw)
    dist = max(1, int(0.4 * PDOM_S * fs))  # min spacing between genuine turns

    def ext(x):
        # Turning points = prominence-filtered maxima of x and of -x, with a
        # minimum spacing of ~0.4 period. Replaces the old bare gradient-sign-change
        # detector, which counted every micro-jitter zero-crossing and let the
        # noisiest/most-broadband arm (arm-3) register spurious early turns -
        # the exact confound that could inflate the "lowest rung leads" share.
        hi, _ = find_peaks(x, prominence=PROM, distance=dist)
        lo, _ = find_peaks(-x, prominence=PROM, distance=dist)
        return np.sort(np.concatenate([hi, lo]))

    E = {i: ext(ara[i]) for i in (1, 2, 3)}
    leaders, times = [], []
    for i1 in E[1]:
        cand = {1: i1}
        ok = True
        for a in (2, 3):
            j = E[a][np.argmin(np.abs(E[a] - i1))]
            if abs(j - i1) / fs < 0.5:
                cand[a] = j
            else:
                ok = False
        if not ok:
            continue
        leaders.append(min(cand, key=lambda a: cand[a]))
        times.append(t[i1])
    return np.array(leaders), np.array(times)


def main():
    print("RUNG -> DOMINANCE  (arm1=top rung, arm3=bottom rung)")
    print(f'  {"run":<6}{"arm":<6}{"share%":>8}{"#blocks":>9}{"meanlen":>9}{"maxlen":>8}')
    for run in RUNS:
        L, _ = leaders_of(run)
        s = [x for x in L]
        runs = {1: [], 2: [], 3: []}
        for k, g in groupby(s):
            runs[k].append(len(list(g)))
        nsw = int(np.sum(np.diff(L) != 0))
        for a in (1, 2, 3):
            share = 100 * np.mean(L == a)
            nb = len(runs[a]); ml = np.mean(runs[a]) if runs[a] else 0; mx = max(runs[a]) if runs[a] else 0
            print(f"  {run:<6}arm{a:<3}{share:8.0f}{nb:9d}{ml:9.2f}{mx:8d}")
        print(f"  {run}: {len(L)} swings, {nsw} leadership switches\n")

    # figure for run1
    L, T = leaders_of("run1")
    cmap = {1: "#74c0fc", 2: "#ffa94d", 3: "#ff6b6b"}
    fig, ax = plt.subplots(figsize=(12, 3.2), facecolor="#0e1116"); ax.set_facecolor("#161b22")
    ax.scatter(T, L, c=[cmap[l] for l in L], s=28)
    ax.set_yticks([1, 2, 3]); ax.set_yticklabels(["arm1 (blue)", "arm2 (orange)", "arm3 (red)"], color="#ddd")
    ax.set_xlabel("time (s)", color="#ccc")
    ax.set_title("Who leads each big swing - 3-way, over time (real triple-pendulum data)", color="#eee", fontsize=11)
    ax.tick_params(colors="#aaa")
    out = os.path.join(OUT_DIR, "pendulum_leadership_3way.png")
    plt.tight_layout(); plt.savefig(out, dpi=140, facecolor="#0e1116", bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
