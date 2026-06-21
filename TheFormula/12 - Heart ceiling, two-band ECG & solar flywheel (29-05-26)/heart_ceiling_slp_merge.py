import numpy as np, wfdb, sys
r=sys.argv[1]
parts=[np.load(f'/tmp/CH_{r}_{i}.npz') for i in range(6)]
rr=np.concatenate([p['rr'] for p in parts])
bp=np.concatenate([p['bp'] for p in parts])
resp=np.concatenate([p['resp'] for p in parts])
o2=np.concatenate([p['o2'] for p in parts])
bt=np.concatenate([p['bt'] for p in parts])
# sleep stage per beat (causal step-hold)
ann=wfdb.rdann(r,'st',pn_dir='slpdb')
sm={'W':0,'R':1,'1':2,'2':3,'3':4,'4':5}
es=[];et=[]
for s,a in zip(ann.sample,ann.aux_note):
    tok=a.split()[0] if a.split() else ''
    if tok in sm: es.append(sm[tok]);et.append(s)
es=np.array(es);et=np.array(et)
stg=np.array([es[np.searchsorted(et,c,side='right')-1] if c>=et[0] else es[0] for c in bt],dtype=float)
# clean o2: valid range 50-100
o2=np.where((o2>=50)&(o2<=100),o2,np.nan)
np.savez(f'/tmp/LAD_{r}.npz',rr=rr,bp=bp,resp=resp,o2=o2,stage=stg,bt=bt)
print(f"{r}: total beats={len(rr)} span={ (bt[-1]-bt[0])/250/3600:.1f}h")
print(f"  o2 valid {np.isfinite(o2).mean():.2f} span {np.nanmax(o2)-np.nanmin(o2):.0f}  stage std {stg.std():.2f} range {int(stg.min())}-{int(stg.max())}")
