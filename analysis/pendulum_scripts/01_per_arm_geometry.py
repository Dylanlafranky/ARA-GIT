"""
Element 1 - the geometry of each arm on its own.

For each arm: amplitude, velocity amplitude, dominant period, spectral
concentration, clock-likeness; plus period ratios and amplitude ratios between
arms. Saves a phase-portrait + spectrum figure.

Expected (run1): all three arms share dominant period 1.333 s (period ratios
1.000); amplitude ladder A1 0.31 < A2 0.43 < A3 0.78 rad; arm-2 most clock-like.

Run:  python 01_per_arm_geometry.py
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
    N = len(th[1])
    print(f"ELEMENT 1 - each arm on its own  (run={run}, fs={fs:.0f} Hz)")
    print(f'{"arm":<5}{"amp(rad)":>10}{"velamp":>9}{"domP(s)":>9}{"specConc":>10}{"clocklike":>11}')
    res = {}
    for i in (1, 2, 3):
        x = th[i] - th[i].mean()
        amp = x.std() * np.sqrt(2)
        va = vel[i].std() * np.sqrt(2)
        f = np.fft.rfftfreq(N, 1 / fs)
        P = np.abs(np.fft.rfft(x * np.hanning(N))) ** 2
        f, P = f[1:], P[1:]
        fp = f[np.argmax(P)]
        conc = P.max() / P.sum()
        band = (f > 0.8 * fp) & (f < 1.2 * fp)
        clk = P[band].sum() / P.sum()
        res[i] = dict(amp=amp, va=va, domP=1 / fp, fp=fp, conc=conc, clk=clk)
        print(f"arm{i:<2}{amp:10.3f}{va:9.2f}{1/fp:9.3f}{conc:10.4f}{clk:11.2f}")
    print("\nperiod ratios:  P1/P2=%.3f  P2/P3=%.3f  P1/P3=%.3f" % (
        res[1]["domP"]/res[2]["domP"], res[2]["domP"]/res[3]["domP"], res[1]["domP"]/res[3]["domP"]))
    # NOTE (phi quarantine): no directional handover is defined for these amplitude
    # ratios, so phi must NOT be invoked here even as a target. Reporting the raw
    # ratios only; comparison constants are deliberately omitted to avoid seeding a
    # post-hoc phi fit (n=1; not an ARA phi claim).
    print("amp ratios:     A2/A1=%.3f  A3/A2=%.3f  A3/A1=%.3f   (raw ratios; no handover defined -> NOT a phi claim)" % (
        res[2]["amp"]/res[1]["amp"], res[3]["amp"]/res[2]["amp"], res[3]["amp"]/res[1]["amp"]))

    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5), facecolor="#0e1116")
    col = {1: "#74c0fc", 2: "#ffa94d", 3: "#ff6b6b"}
    for j, i in enumerate((1, 2, 3)):
        ax = axes[0, j]; ax.set_facecolor("#161b22")
        ax.scatter(th[i], vel[i], s=0.3, c=np.arange(N), cmap="turbo", alpha=0.4)
        ax.set_title(f"arm{i}: phase portrait", color="#eee", fontsize=9)
        ax.set_xlabel("angle from rest (rad)", color="#bbb", fontsize=8)
        ax.set_ylabel("angular vel", color="#bbb", fontsize=8); ax.tick_params(colors="#999", labelsize=7)
        ax = axes[1, j]; ax.set_facecolor("#161b22")
        f = np.fft.rfftfreq(N, 1 / fs)
        P = np.abs(np.fft.rfft((th[i] - th[i].mean()) * np.hanning(N))) ** 2
        ax.semilogy(f[1:], P[1:], lw=0.6, color=col[i]); ax.set_xlim(0, 4)
        ax.axvline(res[i]["fp"], color="#3fb950", ls="--", lw=0.8)
        ax.set_title(f'arm{i}: spectrum (domP={res[i]["domP"]:.2f}s)', color="#eee", fontsize=9)
        ax.set_xlabel("freq (Hz)", color="#bbb", fontsize=8); ax.tick_params(colors="#999", labelsize=7)
    plt.tight_layout()
    out = os.path.join(OUT_DIR, "pendulum_element1_perarm.png")
    plt.savefig(out, dpi=140, facecolor="#0e1116")
    print("saved", out)


if __name__ == "__main__":
    main()
