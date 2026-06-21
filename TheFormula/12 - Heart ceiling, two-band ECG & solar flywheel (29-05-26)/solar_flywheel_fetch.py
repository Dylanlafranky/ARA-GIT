# Download + cache SILSO monthly mean total sunspot number (1749+). Source: SIDC/Royal Obs Belgium.
import urllib.request as r, numpy as np
raw=r.urlopen("https://www.sidc.be/SILSO/INFO/snmtotcsv.php",timeout=30).read().decode()
rows=[l.split(';') for l in raw.strip().split('\n')]
yr=np.array([float(x[2]) for x in rows]); ssn=np.array([float(x[3]) for x in rows])
ok=ssn>=0; yr,ssn=yr[ok],ssn[ok]
np.savez('solar_silso_monthly.npz',yr=yr,ssn=ssn)
print("months:",len(ssn),"span:",yr[0],"->",yr[-1])
