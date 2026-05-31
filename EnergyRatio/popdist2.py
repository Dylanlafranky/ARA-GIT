import numpy as np, re
PHI=(1+5**0.5)/2
def ratios(path):
    out=[]
    for ln in open(path,encoding='latin1'):
        per=[float(x) for x in re.findall(r'\d+\.\d{7,8}', ln) if float(x)>0.05]
        if len(per)>=2:
            p=sorted(per)[:2] if len(per)==2 else None
            # take the two largest plausible periods (the two mode periods), avoid dupes
            cand=sorted(set(per))
            if len(cand)>=2:
                p1,p2=cand[0],cand[1]
                out.append(max(p1,p2)/min(p1,p2))
    return np.array(out)
rrd=ratios('/tmp/RRd.dat'); cep=ratios('/tmp/cepF1O.dat')
def summ(n,r): print("%-22s n=%-4d  freq-ratio mean %.4f  median %.4f  range %.4f-%.4f"%(n,len(r),r.mean(),np.median(r),r.min(),r.max()))
print("DOUBLE-MODE PULSATOR FREQUENCY RATIOS (real OGLE data)\n")
summ("RRd (double RR Lyr)",rrd); summ("Cep F+1O (double Cep)",cep)
allr=np.concatenate([rrd,cep]); gs=1.583
print("\nLandmarks: phi=%.4f  golden-star=%.3f"%(PHI,gs))
print("RRd mean is %+.1f%% from phi ; Cep mean is %+.1f%% from phi"%((rrd.mean()-PHI)/PHI*100,(cep.mean()-PHI)/PHI*100))
print("golden star 1.583 is %+.1f%% from phi"%((gs-PHI)/PHI*100))
print("population max ratio = %.4f ; phi = %.4f ; #stars >= golden(1.583): %d/%d"%(allr.max(),PHI,np.sum(allr>=gs),len(allr)))
print("\nHistogram (freq ratio):")
bins=np.arange(1.30,1.70,0.02); h,_=np.histogram(allr,bins=bins)
for i,c in enumerate(h):
    mark=" <-PHI" if bins[i]<=PHI<bins[i+1] else (" <-golden" if bins[i]<=gs<bins[i+1] else "")
    print("  %.2f-%.2f |%-3d %s%s"%(bins[i],bins[i+1],c,"#"*c,mark))
