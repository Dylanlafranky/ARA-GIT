import urllib.request as u, urllib.parse as up, numpy as np, re, sys
def fetch(cmd,start,stop,step):
    q={"format":"text","COMMAND":f"'{cmd}'","OBJ_DATA":"'NO'","MAKE_EPHEM":"'YES'",
       "EPHEM_TYPE":"'VECTORS'","CENTER":"'500@0'","START_TIME":f"'{start}'",
       "STOP_TIME":f"'{stop}'","STEP_SIZE":f"'{step}'","VEC_TABLE":"'2'","OUT_UNITS":"'AU-D'"}
    url="https://ssd.jpl.nasa.gov/api/horizons.api?"+up.urlencode(q)
    txt=u.urlopen(url,timeout=120).read().decode()
    body=txt.split("$$SOE")[1].split("$$EOE")[0]
    jd=[];X=[];Y=[];VX=[];VY=[]; lines=[l for l in body.splitlines() if l.strip()]; i=0
    while i<len(lines):
        m=re.match(r"\s*([\d.]+)\s*=",lines[i])
        if m:
            jd.append(float(m.group(1)))
            xm=re.findall(r"[XYZ]\s*=\s*([-\d.E+]+)",lines[i+1])
            vm=re.findall(r"V[XYZ]\s*=\s*([-\d.E+]+)",lines[i+2])
            X.append(float(xm[0]));Y.append(float(xm[1]));VX.append(float(vm[0]));VY.append(float(vm[1])); i+=3
        else: i+=1
    return np.array(jd),np.array(X),np.array(Y),np.array(VX),np.array(VY)
name=sys.argv[1]; cmd=sys.argv[2]
jd,X,Y,VX,VY=fetch(cmd,"1000-01-01","8000-01-01","60d")
np.savez(f"/tmp/orb/{name}.npz",jd=jd,X=X,Y=Y,VX=VX,VY=VY)
print(name,"N=",len(jd),"span_yr=%.0f"%((jd[-1]-jd[0])/365.25))
