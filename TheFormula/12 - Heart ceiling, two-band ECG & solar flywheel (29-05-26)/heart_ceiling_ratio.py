import numpy as np, json
# times in MINUTES, heart-alone corr (means)
sleep_t=[0.13,0.42,0.83,1.67,4.0,8.0,17.0]
sleep_c=[0.449,0.398,0.379,0.300,0.212,0.129,0.014]
awake_t=[0.13,0.37,0.75,1.5,3.75,7.5,15.0]
awake_c=[0.224,0.113,0.079,0.101,-0.062,-0.029,0.047]

def cross(ts,cs,thr):
    # first time the (smoothed) curve drops below thr, interp
    ts=np.array(ts);cs=np.array(cs)
    for i in range(1,len(cs)):
        if cs[i-1]>=thr and cs[i]<thr:
            f=(cs[i-1]-thr)/(cs[i-1]-cs[i])
            return ts[i-1]+f*(ts[i]-ts[i-1])
    return None

print("thr   sleep_wall  awake_wall  ratio   phi^? ")
phi=1.6180339887
for thr in [0.15,0.10,0.05,0.0]:
    s=cross(sleep_t,sleep_c,thr); a=cross(awake_t,awake_c,thr)
    if s and a:
        rt=s/a; k=np.log(rt)/np.log(phi)
        print(f"{thr:+.2f}  {s:6.2f}m   {a:6.2f}m   {rt:5.2f}   phi^{k:.2f}")
    else:
        print(f"{thr:+.2f}  s={s} a={a}")
print(f"\nphi={phi:.3f} phi^2={phi**2:.3f} phi^3={phi**3:.3f} phi^4={phi**4:.3f}")
# amplitude ratio at matched short horizons
print("\nshort-horizon skill ratio sleep/awake:")
for i in range(4):
    print(f"  ~{sleep_t[i]:.2f}m: {sleep_c[i]/awake_c[i]:.2f}")
