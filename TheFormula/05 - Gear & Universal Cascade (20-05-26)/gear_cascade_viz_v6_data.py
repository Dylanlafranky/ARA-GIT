"""V6 viz data: HONEST champion (no leakage). Shows what today's mechanics
actually deliver when AR memory uses pattern B (past code's method).
"""
import os, json, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from universal_cascade_v2_honest_patternB import UCv2P, nino, soi_a, pdo_a, m_df, train_n, test_idx

_HERE = os.path.dirname(os.path.abspath(__file__))
HORIZONS = [1, 3, 6, 12, 22]

# Configs: baseline + amp+compass (no AR) + honest pattern B champion + LEAKY old (for comparison/warning)
configs = {
    'baseline':       dict(),
    'amp_compass':    dict(amp_mode='global', compass_gear=True),
    'honest_champion': dict(amp_mode='global', compass_gear=True,
                            ar_memory_mode='pattern_B_honest', ar_shortest_horizon=6),
    'leaky_old':      dict(amp_mode='global', compass_gear=True,
                            ar_memory_mode='LEAKY_old'),
}

predictions = {}
for h in HORIZONS:
    test_starts = [t for t in test_idx if t + h < len(m_df)]
    actual = [float(nino[t + h]) for t in test_starts]
    pers = [float(nino[t]) for t in test_starts]
    dates = [pd.Timestamp(m_df.loc[t + h, 'Date']).strftime('%Y-%m-%d') for t in test_starts]
    series = {'dates': dates, 'actual': actual, 'persistence': pers}
    stats = {}
    for name, kw in configs.items():
        uc = UCv2P(ara=2.0, dom_P=48, n_rungs=5, **kw)
        uc.fit(nino, [soi_a, pdo_a], train_n, h)
        preds = uc.predict_sequence(test_starts, full_actual=nino)
        p = np.array(preds); a = np.array(actual)
        p_adj = (p - p.mean() + a.mean()).tolist()
        series[name] = p_adj
        stats[name + '_mae'] = float(np.abs(np.array(p_adj) - a).mean())
        stats[name + '_corr'] = float(np.corrcoef(p_adj, a)[0, 1])
    pa = np.array(pers); aa = np.array(actual)
    stats['persistence_mae'] = float(np.abs(pa - aa).mean())
    stats['persistence_corr'] = float(np.corrcoef(pa, aa)[0, 1])
    predictions[str(h)] = {**series, **stats}
    print(f'h={h:3d}: base {stats["baseline_mae"]:.3f}/{stats["baseline_corr"]:+.3f} | '
          f'amp+comp {stats["amp_compass_mae"]:.3f}/{stats["amp_compass_corr"]:+.3f} | '
          f'HONEST {stats["honest_champion_mae"]:.3f}/{stats["honest_champion_corr"]:+.3f} | '
          f'LEAKY(do_not_trust) {stats["leaky_old_mae"]:.3f}/{stats["leaky_old_corr"]:+.3f} | '
          f'pers {stats["persistence_mae"]:.3f}/{stats["persistence_corr"]:+.3f}')

out = {'horizons': HORIZONS, 'predictions': predictions,
       'system': 'ENSO (NINO 3.4)', 'ara': 2.0, 'period': '48 months',
       'note': 'HONEST champion: amp+compass+AR_pattern_B (h_ar=6). No future-leakage.'}
with open(os.path.join(_HERE, 'gear_cascade_viz_v6_data.js'), 'w') as f:
    f.write('window.cascadeVizData = '); json.dump(out, f); f.write(';')
print('Saved v6 HONEST viz data')
