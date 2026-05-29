import numpy as np
from numpy.linalg import lstsq
recs=['slp01a','slp02a','slp03','slp04']; W=15; HS=[5,10,20]
def slope(x):
    s=np.zeros(len(x)); s[W:]=x[W:]-x[:-W]; return s
def fit(keys,d,tr,te,y_tr,y_te):
    cols_tr=[np.ones(len(tr))]+[d[k][tr] for k in keys]
    cols_te=[np.ones(len(te))]+[d[k][te] for k in keys]
    Xtr=np.column_stack(cols_tr); Xte=np.column_stack(cols_te)
    mu=Xtr.mean(0); sd=Xtr.std(0); sd[sd==0]=1; sd[0]=1; mu[0]=0
    Xtr=(Xtr-mu)/sd; Xte=(Xte-mu)/sd
    b,*_=lstsq(Xtr,y_tr,rcond=None); pred=Xte@b
    return np.corrcoef(pred,y_te)[0,1], pred.std()
print(f"{'rec':<8}{'h':>4}{'heart':>8}{'+bp':>8}{'liftBP':>8}{'predSD':>8}")
for rec in recs:
    rr=np.load(f'/tmp/s_rr_{rec}.npy')
    d={'rr':rr,'bp':np.load(f'/tmp/s_bp_{rec}.npy')}
    d['rr_s']=slope(rr); d['bp_s']=slope(d['bp'])
    n=len(rr); half=n//2
    for h in HS:
        tr=np.arange(W,half-h); te=np.arange(half,n-h)
        y_tr=rr[tr+h]; y_te=rr[te+h]
        ch,_=fit(['rr','rr_s'],d,tr,te,y_tr,y_te)
        cb,sd=fit(['rr','rr_s','bp','bp_s'],d,tr,te,y_tr,y_te)
        print(f"{rec:<8}{h:>4}{ch:>8.2f}{cb:>8.2f}{cb-ch:>+8.3f}{sd:>8.1f}")
