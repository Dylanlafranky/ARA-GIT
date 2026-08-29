# T396 portable-report chart map

| Report section | Analytical question | Chart family / type | Fields | Supported takeaway | Palette policy | Source |
|---|---|---|---|---|---|---|
| Second observed relation | Do two observed cuts outperform either cut alone? | comparison / horizontal bar | model, mean holdout NLL | both two-cut estimators beat either one-cut model; the analytic oracle remains best | single blue identity palette plus ordered labels | `T396_NLL_COMPARISON.csv` |
| Polarization sensitivity | Does the incremental relation track the physical spin coupling? | change / two-series line | polarization, gain vs parent, estimator | factorized gain decreases monotonically and vanishes at zero polarization; dense grid becomes sparse below full polarization | categorical blue-gold plus labelled zero reference | `T396_SENSITIVITY.csv` |
| Hidden child surface | Does the hidden split vary across both observed coordinates? | matrix / heatmap | parent cut, spin relation, observed child mean | neither observed coordinate is a complete lookup by itself | sequential blue intensity plus explicit axes and tooltips | `T396_CHILD_SURFACE.csv` |

The HTML artifact was structurally verified by the packaged portable-report
builder. Browser-level visual verification was not available because the
headless Chromium runtime was absent and the in-app browser blocks local
`file:` navigation.
