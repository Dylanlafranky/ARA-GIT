"""ara_golden_tree_walk.py — Dylan 14 Jun 2026.
Map a system as an ARA-driven turtle walk on the recursive golden (36 deg) tree.
One step per COMPLETED WAVE: measure that cycle's rise/fall ARA, then turn
  +36 deg if ARA>1  (upper branch) | -36 deg if ARA<1 (lower branch) | straight if ~1.
The accumulated path = the system's route through the fractal. One walk per system/sub-system.
Validates: clock->straight, engine->closed golden decagon (360/36=10), snap->mirror decagon, ENSO->meander.
"""
import numpy as np
from scipy.signal import find_peaks

def per_cycle_ara(sig, min_dist=5):
    tr,_=find_peaks(-np.asarray(sig,float),distance=min_dist); a=[]
    for i in range(len(tr)-1):
        seg=sig[tr[i]:tr[i+1]]
        if len(seg)<4: continue
        pk=int(np.argmax(seg)); rise=pk; fall=len(seg)-pk
        if rise>0 and fall>0: a.append(fall/rise)
    return a

def walk(aras, turn=36.0, L=12.0, ang0=90.0, tol=0.05):
    ang=ang0; x=y=0.0; pts=[(0.0,0.0)]
    for a in aras:
        if a>1+tol: ang+=turn
        elif a<1-tol: ang-=turn
        r=np.radians(ang); x+=L*np.cos(r); y+=L*np.sin(r); pts.append((x,y))
    return pts
# usage: pts = walk(per_cycle_ara(signal))   -> draw the polyline.
