from __future__ import annotations

from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
BLOCK = 1000
DT = 0.000002
STRESS_START = 7730.449370
DISP_START = 7729.800000
OFFSET = round((STRESS_START - DISP_START) / DT)


def load_values(name: str) -> np.ndarray:
    path = ROOT / name
    return np.loadtxt(path, skiprows=1, dtype=np.float64)


def aggregate(values: np.ndarray) -> dict[str, np.ndarray]:
    n = len(values) // BLOCK
    matrix = values[: n * BLOCK].reshape(n, BLOCK)
    return {
        "mean": matrix.mean(axis=1),
        "std": matrix.std(axis=1),
        "min": matrix.min(axis=1),
        "max": matrix.max(axis=1),
        "first": matrix[:, 0],
        "last": matrix[:, -1],
    }


stress = load_values("T362_SOURCE_Event101_ShearStress_S20_x73.15mm.txt")
print("stress", len(stress), np.quantile(stress, [0, .001, .01, .5, .99, .999, 1]).tolist())
s = aggregate(stress)
del stress

disp = load_values("T362_SOURCE_Event101_FaultDisplacement_L3_x70mm.txt")
print("disp", len(disp), "offset", OFFSET, np.quantile(disp, [0, .001, .01, .5, .99, .999, 1]).tolist())
disp = disp[OFFSET:]
d = aggregate(disp)
del disp

n = min(len(s["mean"]), len(d["mean"]))
time = STRESS_START + (np.arange(n) * BLOCK + BLOCK / 2) * DT
out = {"time": time}
for prefix, data in (("stress", s), ("disp", d)):
    for key, values in data.items():
        out[f"{prefix}_{key}"] = values[:n]
np.savez_compressed(ROOT / "T362_SOURCE_EVENT101_QA_2MS.npz", **out)

drop = s["mean"][:n-1] - s["mean"][1:n]
slip = d["mean"][1:n] - d["mean"][:n-1]
for label, values in (("stress_drop", drop), ("disp_increment", slip)):
    order = np.argsort(values)[-20:][::-1]
    print(label)
    for i in order[:10]:
        print(i, float(time[i]), float(values[i]), float(s["mean"][i]), float(d["mean"][i]))

print("aligned bins", n, "time", float(time[0]), float(time[-1]))
