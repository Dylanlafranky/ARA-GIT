"""
PRIMES/ZETA MAPPING — VERIFICATION SCRIPT (3 Jul 2026, per TEST_PROTOCOL)
==========================================================================
Companion to ARA_MAPPING_PRIMES.md §5. Verification of ESTABLISHED numerics
(known-referee use): reproduces the two textbook facts the mapping cites.
 V1 SLOT COMPETITION: spacing histogram of the first 100k zeta zeros
    (unfolded) vs GUE Wigner surmise vs Poisson. Prediction (established,
    Montgomery-Odlyzko): repulsion — the histogram DIES at zero spacing,
    matching GUE, not Poisson.
 V2 THE THINNING LADDER: mean prime gap near x vs ln x (Prime Number
    Theorem). Prediction (theorem): the points ride the ln x line.
DATA: auto-downloads Odlyzko's zeros1 table (first 100,000 zeros) from
http://www.dtc.umn.edu/~odlyzko/zeta_tables/zeros1 if not present.
NO CLAIM beyond reproduction. Nothing here bears on RH (see mapping doc §6).
"""
import os, urllib.request, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ZURL = "http://www.dtc.umn.edu/~odlyzko/zeta_tables/zeros1"
ZFILE = "zeros1.txt"
if not os.path.exists(ZFILE):
    print("[fetch] downloading Odlyzko zeros table...")
    urllib.request.urlretrieve(ZURL, ZFILE)
z = np.loadtxt(ZFILE)
print(f"zeros loaded: {len(z)} (first {z[0]:.3f}, last {z[-1]:.1f})")

# V1: unfold (local mean spacing at height t is 2*pi/log(t/2pi)), histogram
gaps = np.diff(z)
s = gaps * np.log(z[:-1] / (2*np.pi)) / (2*np.pi)
xs = np.linspace(0, 3, 300)
wigner_gue = (32/np.pi**2) * xs**2 * np.exp(-4*xs**2/np.pi)
poisson = np.exp(-xs)
tiny = np.mean(s < 0.1)
print(f"V1: fraction of spacings < 0.1: measured {tiny:.4f} | "
      f"Poisson would give {1-np.exp(-0.1):.4f} | GUE ~ 0.0011")

# V2: primes to 10^7 by sieve; mean gap in log-spaced windows
N = 10_000_000
sieve = np.ones(N+1, bool); sieve[:2] = False
for i in range(2, int(N**0.5)+1):
    if sieve[i]: sieve[i*i::i] = False
primes = np.nonzero(sieve)[0]
print(f"primes found: {len(primes)}")
centers, means = [], []
for lo in np.geomspace(1e3, 8e6, 12):
    hi = lo*1.5
    m = (primes >= lo) & (primes < hi)
    if m.sum() > 50:
        centers.append(np.sqrt(lo*hi)); means.append(np.diff(primes[m]).mean())

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
ax = axes[0]
ax.hist(s, bins=80, range=(0,3), density=True, color="#9bbfe8", label="measured: 100k real zeta zeros")
ax.plot(xs, wigner_gue, color="#2a78d6", lw=2, label="slot-competition curve (GUE)")
ax.plot(xs, poisson, color="#999", lw=2, ls="--", label="no competition (random/Poisson)")
ax.set_xlabel("gap between neighbouring zeros (normalised)")
ax.set_ylabel("how often")
ax.set_title("The primes' hidden notes refuse to share a slot", fontsize=11)
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax = axes[1]
ax.semilogx(centers, means, "o", color="#2a78d6", label="measured mean prime gap")
xx = np.geomspace(1e3, 1.2e7, 100)
ax.semilogx(xx, np.log(xx), "-", color="#999", label="ln x (the predicted ladder)")
ax.set_xlabel("position x on the number line")
ax.set_ylabel("average gap between primes")
ax.set_title("The prime ladder thins exactly on schedule", fontsize=11)
ax.legend(fontsize=9); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("PRIMES_ZETA_FIGURE.png", dpi=150)
print("figure saved")
