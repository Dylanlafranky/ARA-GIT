# T338 source ledger

All primary sources are public NOAA series.

| File | Role | Source |
|---|---|---|
| `nino34_long_anom.csv` | Oceanic grandchild state | NOAA PSL monthly Niño 3.4 HadISST anomaly; source URL is embedded in the CSV header |
| `soi.data` | Atmospheric grandchild state | NOAA PSL/CPC monthly SOI |
| `wwv_west.dat` | Western ocean reservoir retained separately | NOAA PMEL GTMBA warm-water volume, 120°E–155°W |
| `wwv_east.dat` | Eastern ocean reservoir retained separately | NOAA PMEL GTMBA warm-water volume, 155°W–80°W |
| `wpac850.data` | Western atmospheric inflow cut | NOAA CPC 850-hPa trade-wind index, 135°E–180°W |
| `cpac850.data` | Central atmospheric inflow cut | NOAA CPC 850-hPa trade-wind index, 175°W–140°W |
| `epac850.data` | Eastern atmospheric inflow cut | NOAA CPC 850-hPa trade-wind index, 135°W–120°W |
| `olr.data` | Atmospheric-state replication | NOAA CPC equatorial OLR index |
| `heatcentra.data` | Ocean-reservoir replication | NOAA CPC/GODAS 0–300 m central-Pacific heat-content anomaly |

Source endpoints:

- <https://psl.noaa.gov/data/timeseries/month/>
- <https://www.pmel.noaa.gov/tao/wwv/data/>
- <https://www.cpc.ncep.noaa.gov/data/indices/>
- <https://psl.noaa.gov/data/correlation/heatcentra.data>

Local copies are evidence inputs, not hand-edited derivatives. The runner must
record SHA-256 hashes before parsing.

