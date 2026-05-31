#!/usr/bin/env python3
"""
fetch_data.py  —  download all real data needed to reproduce the EnergyRatio leanness tests.
================================================================================================
Writes cached files to /tmp (the paths the analysis scripts expect). Run this FIRST, then run
club_lean.py / popdist2.py / lean.py / club_pop.py.

Data sources (all public, real):
  - Kepler light curves        : lightkurve / MAST   (golden stars + control Cepheid)
  - OGLE-IV double-mode tables : astrouw.edu.pl/ogle (RRd, Cep F+1O, RRc)
  - Netzel & Smolec 2019 RR0.61: VizieR J/MNRAS/487/5584 (table1 = RR0.61 club)

Requires: lightkurve, astropy, numpy, scipy  (pip install lightkurve --break-system-packages)
"""
import warnings; warnings.filterwarnings('ignore')
import urllib.request as R
import numpy as np

def kepler(name, fname, qidx=3):
    import lightkurve as lk
    sr = lk.search_lightcurve(name, mission='Kepler', cadence='long')
    lc = sr[qidx].download().remove_nans().normalize()
    t = np.asarray(lc.time.value); f = np.asarray(lc.flux.value)
    np.savez(fname, t=t, f=f); print("  saved", fname, len(t), "pts")

def grab(url, path):
    open(path, 'wb').write(R.urlopen(url, timeout=60).read()); print("  saved", path)

if __name__ == "__main__":
    print("Kepler light curves (golden club + control):")
    kepler('KIC 5520878', '/tmp/golden_kic5520878_q3.npz', 2)   # the golden star, Q03
    for k in ('4064484', '8832417', '9453114'):
        kepler('KIC '+k, '/tmp/club_%s.npz' % k, 3)             # the other 3 golden stars
    kepler('V1154 Cyg', '/tmp/cep_v1154.npz', 3)                # control: classical Cepheid

    print("OGLE-IV double-mode catalogs:")
    B = "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/"
    grab(B+"blg/rrlyr/RRd.dat", '/tmp/RRd.dat')
    grab(B+"lmc/cep/cepF1O.dat", '/tmp/cepF1O.dat')
    grab(B+"blg/rrlyr/RRc.dat",  '/tmp/RRc.dat')

    print("Netzel & Smolec 2019 RR0.61 census (VizieR J/MNRAS/487/5584):")
    V = "https://cdsarc.cds.unistra.fr/ftp/J/MNRAS/487/5584/"
    grab(V+"table1.dat", '/tmp/ns_table1.dat')   # RR0.61 (period ratio ~0.61 = 1/phi)
    grab(V+"ReadMe",     '/tmp/ns_ReadMe')
    print("\nDone. Now run: python club_lean.py ; python popdist2.py ; python lean.py ; python club_pop.py")
