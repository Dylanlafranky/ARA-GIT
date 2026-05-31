import numpy as np, re
PHI=(1+5**0.5)/2
# club IDs (RR0.61) and their period ratios
club={}
for ln in open('/tmp/ns_table1.dat',encoding='latin1'):
    t=ln.split()
    if t and t[0].startswith('OGLE'):
        try: club[t[0]]=float(t[5])  # Px/P1O
        except: pass
# R21 for all RRc
def r21_of(ln):
    t=ln.split()
    pidx=[i for i,x in enumerate(t) if re.fullmatch(r'\d+\.\d{7,8}',x) and float(x)>0.05]
    if not pidx: return None,None
    i=pidx[0]
    try: return t[0], float(t[i+4])
    except: return t[0],None
club_r=[]; ctrl_r=[]
for ln in open('/tmp/RRc.dat',encoding='latin1'):
    nm,r=r21_of(ln)
    if r is None or not np.isfinite(r): continue
    (club_r if nm in club else ctrl_r).append(r)
club_r=np.array(club_r); ctrl_r=np.array(ctrl_r)
print("LEANNESS (harmonic spray R21, LOWER=leaner) — OGLE RRc, real data\n")
print("  phi-club (RR0.61, period ratio~0.61=1/phi):  n=%d  mean R21 = %.4f  median %.4f"%(len(club_r),club_r.mean(),np.median(club_r)))
print("  control (ordinary single-mode RRc):           n=%d  mean R21 = %.4f  median %.4f"%(len(ctrl_r),ctrl_r.mean(),np.median(ctrl_r)))
print("  difference: club is %.1f%% leaner (lower R21)"%((ctrl_r.mean()-club_r.mean())/ctrl_r.mean()*100))
# significance
from scipy import stats
t,p=stats.mannwhitneyu(club_r,ctrl_r,alternative='less')
print("  Mann-Whitney (club < control): p = %.2e"%p)
print("\n  For reference (earlier): Kepler golden club R21~0.111 ; double-mode RRd 0.162 ; single-mode Cep 0.28")
# does leanness deepen the closer Px/P1O is to exactly 1/phi=0.618?
ids=[k for k in club]; rr={}
for ln in open('/tmp/RRc.dat',encoding='latin1'):
    nm,r=r21_of(ln)
    if nm in club and r is not None and np.isfinite(r): rr[nm]=r
pr=np.array([club[k] for k in rr]); r21=np.array([rr[k] for k in rr])
dist=np.abs(pr-1/PHI)
print("\n  within club: corr(|Px/P1O - 1/phi| , R21) = %+.3f  (n=%d) [negative => closer to 1/phi = leaner]"%(np.corrcoef(dist,r21)[0,1],len(pr)))
