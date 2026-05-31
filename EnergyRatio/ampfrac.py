import numpy as np, re
PHI=(1+5**0.5)/2
def parse(path):
    rows=[]
    for ln in open(path,encoding='latin1'):
        toks=ln.split()
        # find period token indices (7-8 decimals, >0.05)
        pidx=[i for i,t in enumerate(toks) if re.fullmatch(r'\d+\.\d{7,8}',t) and float(t)>0.05]
        if len(pidx)<2: continue
        i1,i2=pidx[0],pidx[1]
        try:
            P1=float(toks[i1]); A1=float(toks[i1+3])   # amp = 3 after period
            P2=float(toks[i2]); A2=float(toks[i2+3])
        except: continue
        if A1<=0 or A2<=0: continue
        # short period = overtone = small/fast/time mode ; long = fundamental/space
        if P1<P2: Pov,Aov,Pf,Af=P1,A1,P2,A2
        else:     Pov,Aov,Pf,Af=P2,A2,P1,A1
        ratio=Pf/Pov                       # freq ratio f_ov/f_fund (closeness to high end/phi)
        small_frac=Aov**2/(Aov**2+Af**2)   # energy in the small/fast mode
        tot=Aov+Af                         # total pulsation amplitude (brightness)
        rows.append((ratio,small_frac,tot,Pf))
    return np.array(rows)
def rep(name,R):
    ratio,sf,tot,pf=R[:,0],R[:,1],R[:,2],R[:,3]
    print("%-12s n=%d"%(name,len(R)))
    print("   corr(small-mode energy fraction , freq-ratio) = %+.3f"%np.corrcoef(sf,ratio)[0,1])
    print("   corr(total amplitude 'brightness' , freq-ratio) = %+.3f"%np.corrcoef(tot,ratio)[0,1])
    hi=ratio>=np.percentile(ratio,67); lo=ratio<=np.percentile(ratio,33)
    print("   near-phi third: small-frac %.3f, amp %.3f | far third: small-frac %.3f, amp %.3f"%(
        sf[hi].mean(),tot[hi].mean(),sf[lo].mean(),tot[lo].mean()))
rrd=parse('/tmp/RRd.dat'); cep=parse('/tmp/cepF1O.dat')
print("YOUR TEST: does small-mode energy fraction (or brightness) track closeness-to-phi?\n")
rep("RRd",rrd); rep("Cep F1O",cep)
print("\ngolden star: small-mode energy fraction ~0.2%% (tiny), but freq-ratio highest (1.583).")
