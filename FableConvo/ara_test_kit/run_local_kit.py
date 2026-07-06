"""
run_local_kit.py - wire the ARA test kit to local real data and run it.
Written 2026-07-02. Builds tidy one-column series from the workspace sources,
then drives each portable test (setting its CONFIG at runtime; the test files
themselves are left untouched) and prints all output.

Data + classification (per the kit's stated optimization-freedom rule):
  ENGINES (class A, self-organizing):  solar sunspots, ENSO Nino3.4, PDO
  FORCED/CLOCK/SUBSTRATE (class B):    QBO, pendulum arm2, pendulum arm3
  BATH ANCHOR (synthetic control):     white noise (labelled, test 7 only)

Test 3 horse: SIGNED_HORSE = "17" is the pre-registered horse from the kit
README / session notes (golden-spiral pitch). NOT chosen post hoc here.
Everything is real measured data except the explicit noise control.
"""
import os, sys, io, contextlib
import numpy as np
import scipy.io as sio

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
R = "/sessions/exciting-peaceful-archimedes/mnt/SystemFormulaFolder"
DD = "/tmp/kitdata"
os.makedirs(DD, exist_ok=True)
np.random.seed(0)


def w1(name, arr):
    p = os.path.join(DD, name)
    np.savetxt(p, np.asarray(arr, float), fmt="%.6f")
    return p


def build_series():
    paths = {}
    # solar: SILSO monthly SN, column 3 (semicolon)
    sn = []
    for ln in open(os.path.join(R, "SILSO_Solar/SN_m_tot_V2.0.csv")):
        t = ln.split(";")
        if len(t) > 3:
            try:
                v = float(t[3])
                if v >= 0:
                    sn.append(v)
            except ValueError:
                pass
    paths["solar"] = (w1("solar.csv", sn), 12.0, "A")
    # ENSO nino3.4 anomaly (drop -99.99 missing)
    ni = []
    for ln in open(os.path.join(R, "Nino34/nino34.long.anom.csv")):
        t = ln.replace(",", " ").split()
        try:
            v = float(t[-1])
            if v > -90:
                ni.append(v)
        except (ValueError, IndexError):
            pass
    paths["enso"] = (w1("enso.csv", ni), 12.0, "A")
    # PDO: year + 12 monthly, 2 header lines
    pdo = []
    for ln in open(os.path.join(R, "PDO_NOAA/ersst.v5.pdo.dat")):
        t = ln.split()
        if len(t) == 13 and t[0].isdigit():
            for v in t[1:]:
                try:
                    fv = float(v)
                    if fv > -90:
                        pdo.append(fv)
                except ValueError:
                    pass
    paths["pdo"] = (w1("pdo.csv", pdo), 12.0, "A")
    # QBO: skip first header line, year + 12 monthly
    qbo = []
    for ln in open(os.path.join(R, "QBO_NOAA/qbo.data")):
        t = ln.split()
        if len(t) == 13 and t[0].isdigit() and int(t[0]) > 1900:
            for v in t[1:]:
                try:
                    qbo.append(float(v))
                except ValueError:
                    pass
    paths["qbo"] = (w1("qbo.csv", qbo), 12.0, "B")
    # pendulum arms 2 & 3 from free-swing run 1, rest-centred, decimate to 50 Hz
    m = sio.loadmat(os.path.join(R, "GIT/ARA-GIT/analysis/pendulum_scripts/data/pend_triple.mat"))
    for i, tag in ((2, "pend_arm2"), (3, "pend_arm3")):
        x = m[f"Theta{i}"].ravel()[::200]
        r = np.arctan2(np.mean(np.sin(x)), np.mean(np.cos(x)))
        xr = (x - r + np.pi) % (2 * np.pi) - np.pi
        paths[tag] = (w1(tag + ".csv", xr), 50.0, "B")
    # synthetic bath anchor (control, test 7 only)
    paths["noise_ctrl"] = (w1("noise_ctrl.csv", np.random.randn(3000)), 1.0, "bath")
    return paths


def hdr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def main():
    P = build_series()
    for k, (pth, fs, cls) in P.items():
        n = sum(1 for _ in open(pth))
        print(f"  built {k:<11} n={n:<6} fs={fs:<5} class={cls}")

    import test1_duty_table as t1
    import test2_lagshape as t2
    import test3_modal_angle as t3
    import test7_lottery_star_line as t7
    import test_bridge_phasestep as tb
    import test8_cascade_optimum as t8

    hdr("TEST 1 - golden-duty two-column table")
    t1.DUTIES_CSV = None
    t1.SERIES = {k: (p, fs, c) for k, (p, fs, c) in P.items() if c in ("A", "B")}
    t1.main()

    hdr("TEST 2 - lag shape (structure vs leak)")
    t2.SERIES = {k: (P[k][0], P[k][1]) for k in ("solar", "enso", "pdo")}
    t2.main()

    hdr("TEST 3 - modal angle race (SIGNED_HORSE = 17, pre-registered)")
    t3.SIGNED_HORSE = "17"
    t3.SERIES = {
        "solar": (P["solar"][0], 12.0, "engine"),
        "enso": (P["enso"][0], 12.0, "engine"),
        "pdo": (P["pdo"][0], 12.0, "engine"),
        "qbo": (P["qbo"][0], 12.0, "clock"),
        "pend_arm2": (P["pend_arm2"][0], 50.0, "conservative"),
        "noise": (P["noise_ctrl"][0], 1.0, "bath"),
    }
    t3.main()

    hdr("TEST 7 - lottery-to-star FDT line")
    t7.SERIES = {k: (P[k][0], P[k][1]) for k in
                 ("solar", "enso", "pdo", "qbo", "pend_arm2", "pend_arm3", "noise_ctrl")}
    t7.main()

    hdr("BRIDGE - handover phase-step per cycle")
    tb.SERIES = {k: (P[k][0], P[k][1]) for k in ("solar", "qbo", "enso", "pdo")}
    tb.main()

    hdr("TEST 8 - cascade optimum (pure engineering; placeholder params)")
    t8.main()


if __name__ == "__main__":
    main()
