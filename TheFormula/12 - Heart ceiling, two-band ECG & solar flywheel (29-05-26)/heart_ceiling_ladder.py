import numpy as np, sys, json
recs=sys.argv[1:] or ['slp59']
HS=[10,30,60,120,300,600,1200]; W=15
def ffill(d):
    d=d.copy()
    for k in range(1,len(d)):
        if not np.isfinite(d[k]): d[k]=d[k-1]
    m=np.nanmean(d[np.isfinite(d)]) if np.isfinite(d).any() else 0.0
    d[~np.isfinite(d)]=m; return d
def feat(rr,drv,i):
    f=[1.0,rr[i],rr[i]-rr[i-W]]
    for d in drv:
        f+=[d[i], d[i]-d[i-W]]
    return f
def run(rr,drv,h):
    n=len(rr); idx=np.arange(W,n-h)
    X=np.array([feat(rr,drv,i) for i in idx]); y=rr[idx+h]
    m=len(idx); tr=slice(0,m//2); te=slice(m//2,m)
    mu=X[tr].mean(0); sd=X[tr].std(0); sd[sd==0]=1; Xs=(X-mu)/sd
    b,*_=np.linalg.lstsq(Xs[tr],y[tr],rcond=None)
    p=Xs[te]@b; a=y[te]
    return np.nan if p.std()<1e-6 else np.corrcoef(p,a)[0,1]
def pers(rr,h):
    n=len(rr); idx=np.arange(W,n-h); te=idx[len(idx)//2:]
    return np.corrcoef(rr[te],rr[te+h])[0,1]
out={}
for r in recs:
    z=np.load(f'/tmp/LAD_{r}.npz')
    rr=z['rr']; breath=ffill(z['resp']); bp=ffill(z['bp']); o2=ffill(z['o2']); stage=ffill(z['stage'])
    ladder=[('heart',[]),('+breath',[breath]),('+pressure',[breath,bp]),('+oxygen',[breath,bp,o2]),('+sleep-stage',[breath,bp,o2,stage])]
    rec={}
    for h in HS:
        rec[h]={'persist':pers(rr,h)}
        for nm,drv in ladder: rec[h][nm]=run(rr,drv,h)
    out[r]=rec
# print mean across recs
names=['heart','+breath','+pressure','+oxygen','+sleep-stage']
print("beats(time)   pers   "+"  ".join(f"{n:>12}" for n in names))
secs={10:'8s',30:'25s',60:'50s',120:'1.7m',300:'4m',600:'8m',1200:'17m'}
for h in HS:
    row=[np.nanmean([out[r][h][n] for r in recs]) for n in names]
    pz=np.nanmean([out[r][h]['persist'] for r in recs])
    print(f"{h:>4}({secs[h]:>4})  {pz:+.3f}  "+"  ".join(f"{v:+.3f}      " for v in row))
print("\nincremental lift each rung adds (mean):")
print("beats   breath  pressure  oxygen  stage")
for h in HS:
    vals=[np.nanmean([out[r][h][n] for r in recs]) for n in names]
    inc=[vals[i+1]-vals[i] for i in range(4)]
    print(f"{h:>4}   "+"  ".join(f"{v:+.3f}" for v in inc))
json.dump({r:{str(h):out[r][h] for h in HS} for r in out},open('/tmp/ladder_result.json','w'),indent=1)
