import numpy as np, re
PHI=(1+5**0.5)/2
def pairs(path):
    P=[]
    for ln in open(path,encoding='latin1'):
        per=sorted(set(float(x) for x in re.findall(r'\d+\.\d{7,8}', ln) if float(x)>0.05))
        if len(per)>=2:
            p_short,p_long=per[0],per[1]
            P.append((p_long,p_short))   # fundamental(long), overtone(short)
    return np.array(P)
def analyze(name,P):
    pf=P[:,0]; ratio=P[:,0]/P[:,1]   # freq ratio f_ov/f_fund = P_fund/P_ov
    c=np.corrcoef(pf,ratio)[0,1]
    print("%-20s n=%d"%(name,len(P)))
    print("   corr(P_fund , freq-ratio) = %+.3f  (shorter P = denser = more 'time-condensed')"%c)
    print("   denser third (short P) mean ratio %.4f vs diffuse third %.4f"%(
        ratio[np.argsort(pf)[:len(pf)//3]].mean(), ratio[np.argsort(pf)[-len(pf)//3:]].mean()))
    return pf,ratio
rrd=pairs('/tmp/RRd.dat'); cep=pairs('/tmp/cepF1O.dat')
print("Does closeness-to-phi track density (period)?  Real OGLE double-mode stars.\n")
a=analyze("RRd",rrd); b=analyze("Cep F1O",cep)
# across the two classes: RR Lyrae denser than Cepheids
print("\nAcross classes:")
print("   RRd  : median P_fund %.3f d, mean ratio %.4f"%(np.median(rrd[:,0]),(rrd[:,0]/rrd[:,1]).mean()))
print("   Cep  : median P_fund %.3f d, mean ratio %.4f"%(np.median(cep[:,0]),(cep[:,0]/cep[:,1]).mean()))
print("   golden star: P_fund 0.269 d (densest), ratio 1.583 (highest, near phi=%.3f)"%PHI)
