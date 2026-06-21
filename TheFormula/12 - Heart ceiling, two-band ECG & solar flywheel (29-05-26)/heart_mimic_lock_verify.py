import numpy as np
recs=['041','230','417','476']; HS=[5,10,20,40,80]; W=15
print("strict-causal checks: persistence floor + +both predSD (test half)")
for r in recs:
    rr=np.load(f'/tmp/m_rr_{r}.npy'); spo2=np.load(f'/tmp/m_spo2_{r}.npy'); bp=np.load(f'/tmp/m_bp_{r}.npy')
    n=len(rr); ps=[]
    for h in HS:
        idx=np.arange(W,n-h); m=len(idx); te=idx[m//2:]
        pcorr=np.corrcoef(rr[te], rr[te+h])[0,1]
        ps.append(round(pcorr,3))
    print(f"{r}: persistence corr {dict(zip(HS,ps))}")
