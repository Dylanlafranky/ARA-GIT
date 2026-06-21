import numpy as np, json
rr=np.load('/tmp/rr_a01er.npy'); o2=np.load('/tmp/o2_a01er.npy')
n=len(rr); half=n//2; h=20; w=15
slope=np.zeros(n)
for i in range(w,n): slope[i]=o2[i]-o2[i-w]
tr=np.arange(w,half-h); ytr=rr[tr+h]
X1=np.c_[np.ones(len(tr)),rr[tr]]; c1=np.linalg.lstsq(X1,ytr,rcond=None)[0]
X2=np.c_[np.ones(len(tr)),rr[tr],o2[tr],slope[tr]]; c2=np.linalg.lstsq(X2,ytr,rcond=None)[0]
idx=np.arange(half,n-h)
actual=rr[idx+h]
pself=np.c_[np.ones(len(idx)),rr[idx]]@c1
po2=np.c_[np.ones(len(idx)),rr[idx],o2[idx],slope[idx]]@c2
o2now=o2[idx]
tmin=(np.cumsum(rr)/1000/60)[idx+h]
def corr(a,b): return float(np.corrcoef(a,b)[0,1])
# show a clear ~6 min window in the test set
m=(tmin>=tmin[0]+2)&(tmin<=tmin[0]+9)
def L(a): return [round(float(v),1) for v in a[m]]
json.dump({
 't':[round(float(v),2) for v in tmin[m]],
 'act':L(actual),'self':L(pself),'o2pred':L(po2),'o2':L(o2now),
 'cs':round(corr(pself,actual),3),'co':round(corr(po2,actual),3),'h':h
}, open('/tmp/fc.json','w'))
print('window pts',int(m.sum()),'corr self',round(corr(pself,actual),3),'corr +O2',round(corr(po2,actual),3))
