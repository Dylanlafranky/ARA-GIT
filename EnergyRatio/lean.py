import numpy as np, re
PHI=(1+5**0.5)/2
def parse(path):
    rows=[]
    for ln in open(path,encoding='latin1'):
        toks=ln.split()
        pidx=[i for i,t in enumerate(toks) if re.fullmatch(r'\d+\.\d{7,8}',t) and float(t)>0.05]
        if len(pidx)<2: continue
        i1,i2=pidx[0],pidx[1]
        def g(i,o):
            try: return float(toks[i+o])
            except: return np.nan
        P1,A1,R21_1=float(toks[i1]),g(i1,3),g(i1,4)
        P2,A2,R21_2=float(toks[i2]),g(i2,3),g(i2,4)
        if not(A1>0 and A2>0): continue
        # dominant mode = larger amplitude; use its R21 as harmonic-spray (waste) proxy
        if A1>=A2: R21=R21_1
        else:      R21=R21_2
        if not np.isfinite(R21): continue
        ratio=max(P1,P2)/min(P1,P2)
        rows.append((ratio,R21))
    return np.array(rows)
def rep(n,R):
    ratio,r21=R[:,0],R[:,1]
    print("%-12s n=%d  corr(harmonic-spray R21 , freq-ratio)=%+.3f"%(n,len(R),np.corrcoef(r21,ratio)[0,1]))
    hi=ratio>=np.percentile(ratio,67); lo=ratio<=np.percentile(ratio,33)
    print("            near-phi third mean R21=%.3f  |  far third mean R21=%.3f  (lower=leaner)"%(r21[hi].mean(),r21[lo].mean()))
rrd=parse('/tmp/RRd.dat'); cep=parse('/tmp/cepF1O.dat')
print("YOUR TEST: are phi-near stars LEANER (lower harmonic spray R21)?\n")
rep("RRd",rrd); rep("Cep F1O",cep)
print("\ngolden star harmonic spray R21 = A(2f)/A(f1) = 0.016/0.147 = %.3f"%(0.016/0.147))
print("(for scale, population mean R21 RRd=%.3f Cep=%.3f)"%(rrd[:,1].mean(),cep[:,1].mean()))
