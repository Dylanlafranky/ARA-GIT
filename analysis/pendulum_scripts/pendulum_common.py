"""
Shared helpers for the triple-pendulum ARA deconstruction scripts.

Data: dynamicslab "MultiArm-Pendulum" (public).
  GitHub: https://github.com/dynamicslab/MultiArm-Pendulum  (Datas/ folder)
  Zenodo: https://doi.org/10.5281/zenodo.6633719
  Paper:  Kaheman et al. 2022, arXiv:2205.06231

This module expects the three triple-pendulum free-swing runs as .mat files,
each containing the keys:  Theta1, Theta2, Theta3, dTheta1, dTheta2, dTheta3, Time, dt
(600001 samples, dt = 1e-4 s, ~60 s at 10 kHz).

Point the scripts at your local copy with the PENDULUM_DATA environment variable,
e.g.  PENDULUM_DATA=/path/to/data  python 01_per_arm_geometry.py
Default is ./data next to these scripts. Rename your three triple runs to the
RUNS filenames below (or edit RUNS to match your filenames).

ARA-POSITION CONVENTION (Dylan's coordinate):
  rest (arm hanging down, inline with parent) = ARA 1.0  (the cancellation ridge)
  straight up = ARA 0 == 2  (the same folded singularity)
  ARA = 1 + wrap(theta - rest)/pi
In THIS dataset theta=0 is UP and rest/down is +-pi, so 'rest' is found per arm
by the circular mean of its angle (do NOT assume rest = 0).
"""
import os
import numpy as np
import scipy.io as sio

DATA_DIR = os.environ.get(
    "PENDULUM_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
)
OUT_DIR = os.environ.get(
    "PENDULUM_OUT", os.path.dirname(os.path.abspath(__file__))
)

# Map logical run name -> filename on disk. Edit if your filenames differ.
# Free-swing triple runs (conservative; the original deconstruction used these).
# Canonical source names are TripleDataFreeSwing_{1,2,3}_Dt_0_0001.mat - the
# pend_triple/tri2/tri3 copies are byte-identical renames.
RUNS = {"run1": "pend_triple.mat", "run2": "tri2.mat", "run3": "tri3.mat"}

# Driven / excited runs ("WithControl" = cart driven back and forth = an EXTERNAL
# driver, so the system is NON-CONSERVATIVE). Same Theta/dTheta keys as free-swing,
# so load_triple()/load_triple_driven work directly. NOTE (verified): these runs are
# actually GENTLER than free-swing (arm-3 max ~0.93 rad vs 1.73 free) - they do NOT
# reach the over-the-top singularity. Their value is the external forcing + the
# broken energy conservation, not higher energy.
DRIVEN = {"triple1": "TripleDataWithControl_1_Dt_0_0001.mat"}


def load_triple_driven(run="triple1", decimate=10):
    """Load a driven triple run (same return signature as load_triple)."""
    return load_triple(run, decimate=decimate, runs=DRIVEN)


def wrap(a):
    """Wrap angle(s) to (-pi, pi]."""
    return (a + np.pi) % (2 * np.pi) - np.pi


def load_triple(run="run1", decimate=10, runs=None):
    """Load one triple-pendulum run.

    Returns: t (s), th{1,2,3} raw angle (rad), vel{1,2,3} angular velocity, fs (Hz).
    decimate=10 -> 1000 Hz; 20 -> 500 Hz; 200 -> 50 Hz.
    `runs` selects the name->filename map (default RUNS = free-swing; pass DRIVEN
    for the driven runs).
    """
    runs = RUNS if runs is None else runs
    path = os.path.join(DATA_DIR, runs[run])
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find {path}.\nDownload the dynamicslab MultiArm-Pendulum "
            f"triple-pendulum runs (see module docstring) and set PENDULUM_DATA, "
            f"or edit RUNS to match your filenames."
        )
    m = sio.loadmat(path)
    q = decimate
    t = m["Time"].ravel()[::q]
    th = {i: m[f"Theta{i}"].ravel()[::q] for i in (1, 2, 3)}
    vel = {i: m[f"dTheta{i}"].ravel()[::q] for i in (1, 2, 3)}
    dt = float(np.asarray(m["dt"]).ravel()[0])
    fs = 1.0 / (dt * q)
    return t, th, vel, fs


def rest_of(x):
    """Circular-mean rest position of an angle series (hanging-down equilibrium)."""
    return np.arctan2(np.mean(np.sin(x)), np.mean(np.cos(x)))


def rest_centered(th):
    """Each arm's angle relative to its own rest (rest -> 0)."""
    return {i: wrap(th[i] - rest_of(th[i])) for i in th}


def ara_position(th):
    """ARA-position per arm: 1.0 at rest ridge, 0/2 at the straight-up singularity."""
    return {i: 1.0 + wrap(th[i] - rest_of(th[i])) / np.pi for i in th}
