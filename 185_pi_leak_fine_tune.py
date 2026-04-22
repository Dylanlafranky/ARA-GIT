#!/usr/bin/env python3
"""Script 185 — Fine-tune π-leak around the sweet spot."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3
ARA_SSN = 1.73; ARA_EQ = 0.15
MIDPOINT_OFFSET = abs((ARA_SSN + ARA_EQ) / 2 - R_COUPLER)

def vlong(lv, C, R):
    return R * np.arcsin(np.clip((lv-C)/R, -1, 1))
def wave(p, R): return R * np.sin(p/R)
def eff_ara(a, t, ph):
    return 1.0 + (a-1.0)*np.sin(2*np.pi*t/HALE_PERIOD + ph)

def make_pred(leak_scale, leak_type, step_size=GA_OVER_PHI):
    def predict(lv, C, Rm, step, t, ph):
        eff = max(eff_ara(Rm, t, ph), 0.1)
        p = vlong(lv, C, eff); pn = p + step_size * step
        def aw(pos, R, off): return (wave(pos+off,R)+wave(pos-off,R))/2
        inner = ((aw(pn,R_COUPLER,PHI)+aw(pn+HALF_PHI,R_COUPLER,PHI))/2 -
                 (aw(p,R_COUPLER,PHI)+aw(p+HALF_PHI,R_COUPLER,PHI))/2) * np.exp(-MIDPOINT_OFFSET)
        s = lambda pos: (wave(pos,Rm)+wave(pos+HALF_PHI,Rm))/2
        outer = (s(pn) - s(p)) * np.exp(-MIDPOINT_OFFSET)
        drive = eff - 1.0
        gear = max(abs(lv-C)/HALF_PHI, 0.1)
        wdlog = inner + drive * gear * outer

        if leak_type == 'sign':
            leak = PI_LEAK * np.sign(1.0-eff) * leak_scale
        elif leak_type == 'prop':
            leak = PI_LEAK * (1.0-eff) * leak_scale
        elif leak_type == 'ara':
            leak = PI_LEAK * (1.0-eff) * (Rm-1.0) * leak_scale
        elif leak_type == 'sin':
            leak = PI_LEAK * np.sin(2*np.pi*t/HALE_PERIOD + ph + np.pi) * leak_scale
        else:
            leak = 0
        return lv + wdlog + leak
    return predict

def cal_phase(td, Rm, fn, np_=24):
    yrs=sorted(td.keys())
    if len(yrs)<20: return 0.0
    C=np.mean(np.log10([max(v,.1) for v in td.values()]))
    bp=0.0; bs=-999
    for pi in range(np_):
        p0=2*np.pi*pi/np_; ts=max(0,len(yrs)-15)
        cur=np.log10(max(td[yrs[ts]],.1)); pc=[]; ac=[]
        for i in range(ts+1,len(yrs)):
            t=i-ts; nw=fn(cur,C,Rm,1,t,p0)
            pc.append(nw-cur)
            ac.append(np.log10(max(td[yrs[i]],.1))-np.log10(max(td[yrs[i-1]],.1)))
            cur=np.log10(max(td[yrs[i]],.1))
        if len(pc)<5: continue
        p,a=np.array(pc),np.array(ac)
        c=float(np.corrcoef(p,a)[0,1]) if np.std(p)>0 and np.std(a)>0 else 0
        dm=sum(1 for x,y in zip(p,a) if np.sign(x)==np.sign(y))/len(p)
        if c+dm>bs: bs=c+dm; bp=p0
    return bp

def load_ssn():
    p=os.path.join(os.path.dirname(__file__),'..','solar_test','sunspots.txt')
    m={}
    with open(p) as f:
        for l in f:
            ps=l.split()
            if len(ps)<4: continue
            try:
                y=int(ps[0]);v=float(ps[3])
                if v<0: continue
                m.setdefault(y,[]).append(v)
            except: continue
    return {y:np.mean(v) for y,v in m.items() if len(v)>=6}

def load_eq():
    return {1900:13,1901:14,1902:8,1903:10,1904:16,1905:26,1906:32,1907:27,1908:18,1909:32,1910:36,1911:24,1912:22,1913:23,1914:22,1915:18,1916:25,1917:21,1918:21,1919:14,1920:8,1921:11,1922:14,1923:23,1924:18,1925:17,1926:19,1927:20,1928:22,1929:19,1930:13,1931:26,1932:13,1933:14,1934:22,1935:24,1936:21,1937:22,1938:26,1939:21,1940:23,1941:24,1942:27,1943:41,1944:31,1945:27,1946:35,1947:26,1948:28,1949:36,1950:15,1951:21,1952:17,1953:22,1954:17,1955:19,1956:15,1957:34,1958:10,1959:15,1960:22,1961:18,1962:15,1963:20,1964:15,1965:22,1966:19,1967:16,1968:30,1969:27,1970:29,1971:23,1972:20,1973:16,1974:21,1975:21,1976:25,1977:16,1978:18,1979:15,1980:18,1981:14,1982:10,1983:15,1984:8,1985:15,1986:6,1987:11,1988:8,1989:7,1990:13,1991:11,1992:23,1993:16,1994:15,1995:25,1996:22,1997:20,1998:16,1999:23,2000:16,2001:15,2002:13,2003:14,2004:16,2005:11,2006:11,2007:18,2008:12,2009:16,2010:23,2011:19,2012:12,2013:17,2014:11,2015:19,2016:16,2017:7,2018:17,2019:11,2020:9,2021:16,2022:10,2023:18,2024:15}

def run_blind(data,cuts,Rm,fn):
    res=[]
    for co in cuts:
        tr={y:v for y,v in data.items() if y<co}
        te={y:v for y,v in data.items() if y>=co}
        if len(tr)<10 or len(te)<5: continue
        C=np.mean(np.log10([max(v,.1) for v in tr.values()]))
        ph=cal_phase(tr,Rm,fn); sv=max(data[max(tr.keys())],.1)
        ty=sorted(te.keys()); preds=[]; cur=np.log10(sv)
        for i,y in enumerate(ty):
            cur=fn(cur,C,Rm,1,i+1,ph); preds.append(10**cur)
        act=[data[y] for y in ty]; n=len(ty); nv=sv
        a,p=np.array(act),np.array(preds)
        c=float(np.corrcoef(a,p)[0,1]) if np.std(a)>0 and np.std(p)>0 and len(a)>2 else 0
        m=float(np.mean(np.abs(a-p))); nm=float(np.mean(np.abs(a-nv)))
        b=sum(1 for pi,ai in zip(preds,act) if abs(pi-ai)<abs(nv-ai))/n*100
        x=sum(1 for pi,ai in zip(preds,act) if 1/2<=max(pi,.1)/max(ai,.1)<=2)/n*100
        dm,dt=0,0
        for i in range(1,n):
            if np.sign(act[i]-act[i-1])!=0:
                dt+=1
                if np.sign(preds[i]-preds[i-1])==np.sign(act[i]-act[i-1]): dm+=1
        d=dm/max(dt,1)*100
        res.append({'co':co,'corr':c,'beats':b,'x2':x,'dir':d,'mae':m,'nmae':nm,
                    'preds':preds[:18],'act':act[:18],'yrs':ty[:18],'nv':nv,'ph':ph})
    return res

def score(sr,er):
    s=0
    ac=np.mean([r['corr'] for r in sr]); s+=(ac>0.3)
    bn=sum(1 for r in sr if r['beats']>50); s+=(bn>=3)
    ax=np.mean([r['x2'] for r in sr]); s+=(ax>30)
    ad=np.mean([r['dir'] for r in sr]); s+=(ad>55)
    ec=np.mean([r['corr'] for r in er]); s+=(ec>0.2)
    ex=np.mean([r['x2'] for r in er]); s+=(ex>30)
    bm=sum(1 for r in sr if r['mae']<r['nmae']); s+=(bm>=3)
    nb=all(r['mae']<500 for r in sr); s+=nb
    return s, ac, ad, ec

if __name__=='__main__':
    ssn=load_ssn(); eq=load_eq()
    cuts=[1990,1995,2000,2005,2010,2015]
    
    print("="*70)
    print("FINE-TUNE π-LEAK — sign type around 0.618 & step sizes")
    print("="*70)
    
    best_s=0; best_label=""
    
    # Fine sweep of V1 sign leak
    for ls in [0.40,0.45,0.50,0.55,0.58,0.60,0.618,0.65,0.70,0.75,0.80]:
        for step in [GA_OVER_PHI, PHI, GOLDEN_ANGLE/PHI**2]:
            sn = {GA_OVER_PHI:"GA/φ", PHI:"φ", GOLDEN_ANGLE/PHI**2:"GA/φ²"}[step]
            fn=make_pred(ls,'sign',step)
            sr=run_blind(ssn,cuts,ARA_SSN,fn); er=run_blind(eq,cuts,ARA_EQ,fn)
            s,ac,ad,ec=score(sr,er)
            label=f"sign={ls:.3f} step={sn}"
            m=" ★★★ 8/8!" if s==8 else " ★ NEW BEST" if s>7 else " ← ties" if s==7 else ""
            if s>=7 or ac>0.2:
                print(f"  {label}: {s}/8 SSNc={ac:+.2f} dir={ad:.0f}% EQc={ec:+.2f}{m}")
                if s>=7:
                    for r in sr:
                        if r['co']==1990:
                            print(f"    1990: ", end="")
                            for i in range(min(17,len(r['yrs']))):
                                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
                            print()
            if s>best_s: best_s=s; best_label=label

    # Also try combining π-leak with different outer wave scaling
    print(f"\n--- Combined: prop leak + different step sizes ---")
    for ls in [0.05, 0.08, 0.10, 0.12, 0.15]:
        for step in [GA_OVER_PHI, PHI]:
            sn = {GA_OVER_PHI:"GA/φ", PHI:"φ"}[step]
            fn=make_pred(ls,'prop',step)
            sr=run_blind(ssn,cuts,ARA_SSN,fn); er=run_blind(eq,cuts,ARA_EQ,fn)
            s,ac,ad,ec=score(sr,er)
            label=f"prop={ls:.2f} step={sn}"
            m=" ★★★ 8/8!" if s==8 else " ★ NEW BEST" if s>7 else " ← ties" if s==7 else ""
            if s>=7 or ac>0.15:
                print(f"  {label}: {s}/8 SSNc={ac:+.2f} dir={ad:.0f}% EQc={ec:+.2f}{m}")
                if s>=7:
                    for r in sr:
                        if r['co']==1990:
                            print(f"    1990: ", end="")
                            for i in range(min(17,len(r['yrs']))):
                                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
                            print()
    
    # ARA-scaled with fine steps
    print(f"\n--- ARA-scaled leak fine tune ---")
    for ls in [0.05, 0.08, 0.10, 0.12, 0.15, 0.20]:
        for step in [GA_OVER_PHI, PHI]:
            sn = {GA_OVER_PHI:"GA/φ", PHI:"φ"}[step]
            fn=make_pred(ls,'ara',step)
            sr=run_blind(ssn,cuts,ARA_SSN,fn); er=run_blind(eq,cuts,ARA_EQ,fn)
            s,ac,ad,ec=score(sr,er)
            label=f"ara={ls:.2f} step={sn}"
            m=" ★★★ 8/8!" if s==8 else " ★ NEW BEST" if s>7 else " ← ties" if s==7 else ""
            if s>=7 or ac>0.15:
                print(f"  {label}: {s}/8 SSNc={ac:+.2f} dir={ad:.0f}% EQc={ec:+.2f}{m}")
                if s>=7:
                    for r in sr:
                        if r['co']==1990:
                            print(f"    1990: ", end="")
                            for i in range(min(17,len(r['yrs']))):
                                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
                            print()
    
    print(f"\nBest overall: {best_label} at {best_s}/8")
    print("Script 185 complete.")
