import numpy as np
recs=['a01er','a02er','a03er','b01er']
def fc(a,b): return np.corrcoef(a,b)[0,1] if a.std()>0 and b.std()>0 else 0.0
H=[15,30,60,120,180]
agg={h:{'self':[],'o2':[]} for h in H}
for rec in recs:
    rr=np.load(f'/tmp/rr_{rec}.npy'); o2=np.load(f'/tmp/o2_{rec}.npy')
    n=len(rr); half=n//2
    # oxygen recent trend over last 15 beats (directional, no period needed)
    w=15
    slope=np.zeros(n)
    for i in range(w,n): slope[i]=o2[i]-o2[i-w]
    for h in H:
        idx=np.arange(half,n-h); 
        if len(idx)<40: continue
        y=rr[idx+h]; tr=np.arange(w,half-h); ytr=rr[tr+h]
        # self
        Xt=np.c_[np.ones(len(tr)),rr[tr]]; c1=np.linalg.lstsq(Xt,ytr,rcond=None)[0]
        sp=np.c_[np.ones(len(idx)),rr[idx]]@c1
        # +O2 value + O2 trend
        Xt2=np.c_[np.ones(len(tr)),rr[tr],o2[tr],slope[tr]]; c2=np.linalg.lstsq(Xt2,ytr,rcond=None)[0]
        op=np.c_[np.ones(len(idx)),rr[idx],o2[idx],slope[idx]]@c2
        agg[h]['self'].append(fc(sp,y)); agg[h]['o2'].append(fc(op,y))
print(f"{'h(beats)':>8}{'~min':>6}{'RRself':>9}{'+O2':>8}{'O2 adds':>9}{'  per-record O2-adds'}")
for h in H:
    s=np.array(agg[h]['self']); o=np.array(agg[h]['o2']); d=o-s
    pr=' '.join(f'{v:+.2f}' for v in d)
    print(f"{h:>8}{h/67:>6.1f}{s.mean():>9.3f}{o.mean():>8.3f}{d.mean():>+9.3f}   [{pr}]")
