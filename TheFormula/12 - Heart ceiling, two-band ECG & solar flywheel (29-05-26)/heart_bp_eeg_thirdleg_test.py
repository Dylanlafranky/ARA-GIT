import numpy as np
from numpy.linalg import lstsq

recs=['slp01a','slp02a','slp03','slp04']
W=15  # trend window (past only)
HS=[5,10,20,40,80]

def slope(x):
    s=np.zeros(len(x)); s[W:]=x[W:]-x[:-W]; return s

def zev(x):  # causal-safe standardize using train stats only (passed externally)
    return x

# model sets: list of (name, feature-builder columns from a dict)
def build(feat_keys, d, idx):
    cols=[np.ones(len(idx))]
    for k in feat_keys:
        cols.append(d[k][idx])
    return np.c_[cols].T if False else np.column_stack(cols)

results={}  # name -> {h: [corrs per rec]}
pers={h:[] for h in HS}
models={
 'heart':['rr','rr_s'],
 '+resp':['rr','rr_s','resp','resp_s'],
 '+bp':['rr','rr_s','bp','bp_s'],
 '+brain':['rr','rr_s','delta','delta_s','beta','beta_s'],
 '+bp+brain':['rr','rr_s','bp','bp_s','delta','delta_s','beta','beta_s'],
 'ALL':['rr','rr_s','resp','resp_s','bp','bp_s','delta','delta_s','beta','beta_s'],
}
for m in models: results[m]={h:[] for h in HS}

for rec in recs:
    rr=np.load(f'/tmp/s_rr_{rec}.npy')
    d={'rr':rr,'resp':np.load(f'/tmp/s_resp_{rec}.npy'),
       'bp':np.load(f'/tmp/s_bp_{rec}.npy'),
       'delta':np.log(np.load(f'/tmp/s_delta_{rec}.npy')+1e-9),
       'beta':np.log(np.load(f'/tmp/s_beta_{rec}.npy')+1e-9)}
    for base in ['rr','resp','bp','delta','beta']:
        d[base+'_s']=slope(d[base])
    n=len(rr); half=n//2
    for h in HS:
        # train pairs t in [W, half-h), test t in [half, n-h)
        tr=np.arange(W,half-h); te=np.arange(half,n-h)
        y_tr=rr[tr+h]; y_te=rr[te+h]
        # persistence on test
        pc=np.corrcoef(rr[te], y_te)[0,1]
        pers[h].append(pc)
        for mname,keys in models.items():
            Xtr=build(keys,d,tr); Xte=build(keys,d,te)
            # standardize columns by train mean/std (except intercept col 0)
            mu=Xtr.mean(0); sd=Xtr.std(0); sd[sd==0]=1; sd[0]=1; mu[0]=0
            Xtr=(Xtr-mu)/sd; Xte=(Xte-mu)/sd
            beta,*_=lstsq(Xtr,y_tr,rcond=None)
            pred=Xte@beta
            c=np.corrcoef(pred,y_te)[0,1]
            results[mname][h].append(c)

print("beats~ms:", {r:int(np.load(f'/tmp/s_rr_{r}.npy').mean()) for r in recs})
print(f"\n{'h(beats)':<9}{'pers':>7}", end='')
for m in models: print(f"{m:>11}", end='')
print()
for h in HS:
    print(f"{h:<9}{np.mean(pers[h]):>7.2f}", end='')
    for m in models:
        print(f"{np.mean(results[m][h]):>11.2f}", end='')
    print()
print("\n-- LIFT over heart-only (mean corr across 4 recs) --")
print(f"{'h':<9}", end='')
for m in models:
    if m=='heart': continue
    print(f"{m:>11}", end='')
print()
for h in HS:
    print(f"{h:<9}", end='')
    for m in models:
        if m=='heart': continue
        lift=np.mean(results[m][h])-np.mean(results['heart'][h])
        print(f"{lift:>+11.3f}", end='')
    print()
