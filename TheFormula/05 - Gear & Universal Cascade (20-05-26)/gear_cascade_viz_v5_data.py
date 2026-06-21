"""V5 viz data: champion stack (amp+ar+compass) vs baseline + individual ingredients."""
import os, json, math, sys
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universal_cascade_v2_test import UCv2, nino, soi_a, pdo_a, m_df, train_n, test_idx

PHI = (1 + 5**0.5) / 2
_HERE = os.path.dirname(os.path.abspath(__file__))

HORIZONS = [1, 3, 6, 12, 22]
predictions = {}

# Configs to display
configs = {
    'baseline':   dict(),
    'amp_global': dict(amp_mode='global'),
    'amp_ar':     dict(amp_mode='global', ar_memory=True),
    'champion':   dict(amp_mode='global', ar_memory=True, compass_gear=True),  # amp+ar+compass
}

for h in HORIZONS:
    test_starts = [t for t in test_idx if t + h < len(m_df)]
    actual = [float(nino[t + h]) for t in test_starts]
    pers = [float(nino[t]) for t in test_starts]
    dates = [pd.Timestamp(m_df.loc[t + h, 'Date']).strftime('%Y-%m-%d') for t in test_starts]

    series = {'dates': dates, 'actual': actual, 'persistence': pers}
    stats = {}
    for name, kw in configs.items():
        uc = UCv2(ara=2.0, dom_P=48, n_rungs=5, **kw)
        uc.fit(nino, [soi_a, pdo_a], train_n, h)
        preds = uc.predict_sequence(test_starts, full_actual=nino)
        p = np.array(preds); a = np.array(actual)
        p_adj = (p - p.mean() + a.mean()).tolist()
        series[name] = p_adj
        mae = float(np.abs(np.array(p_adj) - a).mean())
        corr = float(np.corrcoef(p_adj, a)[0, 1])
        stats[name + '_mae'] = mae
        stats[name + '_corr'] = corr

    pa = np.array(pers); aa = np.array(actual)
    stats['persistence_mae'] = float(np.abs(pa - aa).mean())
    stats['persistence_corr'] = float(np.corrcoef(pa, aa)[0, 1])

    predictions[str(h)] = {**series, **stats}
    print(f'h={h:3d}: baseline {stats["baseline_mae"]:.3f}/{stats["baseline_corr"]:+.3f} | '
          f'amp {stats["amp_global_mae"]:.3f}/{stats["amp_global_corr"]:+.3f} | '
          f'amp+ar {stats["amp_ar_mae"]:.3f}/{stats["amp_ar_corr"]:+.3f} | '
          f'CHAMPION {stats["champion_mae"]:.3f}/{stats["champion_corr"]:+.3f} | '
          f'pers {stats["persistence_mae"]:.3f}/{stats["persistence_corr"]:+.3f}')

out = {'horizons': HORIZONS, 'predictions': predictions,
       'system': 'ENSO (NINO 3.4)', 'ara': 2.0, 'period': '48 months'}
with open(os.path.join(_HERE, 'gear_cascade_viz_v5_data.js'), 'w') as f:
    f.write('window.cascadeVizData = '); json.dump(out, f); f.write(';')
print('Saved v5 viz data')
