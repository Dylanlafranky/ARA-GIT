# Reproducibility Notes

**Public-release note, May 2026**

This repo contains current work, older exploratory scripts, visualizations, transcripts, and superseded attempts. Not every file is expected to run cleanly. The goal of this note is to make that explicit instead of leaving reviewers to discover it accidentally.

## Intended Minimal Setup

```bash
python -m pip install -r requirements.txt
python ara_framework.py
```

The current `requirements.txt` includes the main scientific stack used by the framework:

```text
numpy
scipy
pandas
matplotlib
neurokit2
wfdb
lightkurve
yfinance
requests
```

Some LLM scripts also require packages such as `torch` and `transformers`; those are not part of the minimal predictor install.

## Known Public-Release Issues

These were found during an outside-style audit of the local folder.

| Area | Issue |
|---|---|
| Hardcoded paths | Several scripts still point to old local paths such as `/sessions/amazing-cool-archimedes/...`. These should be replaced with repo-relative paths before asking others to rerun them. |
| Broken exploratory scripts | Some old `TheFormula` scripts have syntax or indentation errors. Treat these as archived experiments unless fixed. |
| Missing LLM dependencies | LLM scripts compile, but running them requires a separate ML environment with model weights/cache access. |
| Claim/data mismatches | A few public-facing headline numbers were stronger than the saved artifacts I reviewed. `CLAIMS_STATUS.md` lists the main ones. |
| Baseline comparisons | Forecast claims should report persistence, AR/Fourier, and non-phi log-ladder controls beside the ARA result. |

## Preregistered `home_k` Rule

For any public benchmark, choose `home_k` before scoring:

```text
home_k = round(log(ground_cycle_period) / log(phi))
```

Use the same time unit as the data. If more than one ground cycle is scientifically plausible, list all candidates before running the test and report all candidate results. Do not choose `home_k` from forecast performance.

## Recommended Validation Harness

The repo would be much stronger with one command that:

1. Downloads or locates public data.
2. Runs the canonical ARA predictor.
3. Runs persistence, AR/Fourier, and simple ML baselines.
4. Runs phi against nearby log bases such as sqrt(2), 1.5, 1.6, 1.7, and an optimized free base.
5. Reports correlation, MAE, directional accuracy, and skill versus persistence.
6. Separates descriptive classification, tracking, and blind forecasting.

Until that exists, please treat the repository as an inspectable research record rather than a turnkey benchmark package.
