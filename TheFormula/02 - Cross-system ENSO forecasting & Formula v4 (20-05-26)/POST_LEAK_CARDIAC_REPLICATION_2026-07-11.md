# Post-leak cardiac replication — frozen protocol

**Frozen:** 2026-07-11, before running the replication subjects below.

## Question

Does the recovered 2026-04-30 ARA method repeat its advantage over its matched Fourier comparator on other heart records?

The original `nsr050` calculation must first be reproduced exactly. The result must then be separated into two distinct tasks:

1. **Online one-step prediction:** the true previous test beat may update the next prediction.
2. **Cold 25% prediction:** no true value after the 75% split may update any test prediction.

The old report called the first task a “5.99-hour cold forecast.” That label is incorrect. The calculation is causal, but it consumes the test sequence one beat at a time.

## Frozen replication subjects

Use `nsr051`, `nsr052`, `nsr053`, and `nsr054`.

Reason for selection: they are the next four record identifiers after the original `nsr050`. A repository text search found no saved result for these subjects under the exact cardiac ARA-vs-Fourier protocol. No outcome from these four records was calculated before this selection was written.

## Frozen method

- Use the full beat record.
- Keep RR intervals from 300 through 1800 ms, inclusive.
- Use the first 75% of elapsed time for fitting and the last 25% for testing.
- Candidate ARA periods are the original `phi^k` ladder for `k = 0..22`, retaining periods with at least two cycles in training.
- Preserve the original 6-value ARA grid, 5-value phase grid, greedy subsystem selection, 0.05 stopping threshold, and 10-subsystem maximum.
- Preserve the original coupling type and coupling-strength code.
- Match Fourier to the original reported parameter count: `3 × selected ARA subsystems + 1`, then use as many sine/cosine frequency pairs as fit within that count.
- Choose Fourier frequencies from training only.
- Apply the fixed residual coefficient `1/phi^3` to both ARA and Fourier.
- Report correlation and MAE.
- Also report a one-step persistence baseline: predict that the next RR interval equals the previous observed RR interval.
- Do not tune any choice on replication results.

## Decision rules

Report all four subjects, not only wins.

For each subject:

- **Comparator win:** ARA online correlation exceeds Fourier online correlation and ARA online MAE is lower.
- **Practical online win:** ARA also exceeds one-step persistence on both metrics.
- **Cold win:** ARA true-cold correlation exceeds Fourier true-cold correlation and ARA true-cold MAE is lower.

The original `nsr050` result counts only as reproduction, not replication.

## Reproduction result recorded before replication

The recovered code reproduced the saved values to displayed precision:

| Method | Correlation | MAE |
|---|---:|---:|
| ARA online one-step | +0.685481 | 114.762 ms |
| Fourier online one-step | +0.307833 | 128.753 ms |
| ARA true cold | -0.217722 | 149.290 ms |
| Fourier true cold | -0.376407 | 167.585 ms |
| One-step persistence | +0.950827 | 21.752 ms |

The frozen executable is `post_leak_cardiac_replication.py`. Machine-readable results are written to `post_leak_cardiac_replication_results.json`.

## Replication results

The frozen run completed without changing the method between subjects.

### Online one-step task

| Subject | ARA corr | Fourier corr | Corr difference | ARA MAE | Fourier MAE | MAE difference | ARA beats both Fourier metrics? |
|---|---:|---:|---:|---:|---:|---:|:---:|
| nsr051 | +0.024 | +0.416 | -0.392 | 145.9 | 131.4 | +14.5 | No |
| nsr052 | +0.814 | +0.388 | +0.426 | 135.4 | 147.7 | -12.4 | **Yes** |
| nsr053 | +0.155 | +0.766 | -0.611 | 176.5 | 136.0 | +40.5 | No |
| nsr054 | +0.328 | +0.320 | +0.007 | 180.7 | 177.6 | +3.1 | No |
| **Four-subject mean difference** |  |  | **-0.142** |  |  | **+11.4** | **1 of 4** |

A positive MAE difference means ARA made the larger error. ARA therefore lost to the matched Fourier comparator on average across the frozen replication set.

### Required simple baseline

| Subject | ARA online corr | Persistence corr | ARA online MAE | Persistence MAE |
|---|---:|---:|---:|---:|
| nsr051 | +0.024 | +0.965 | 145.9 | 24.9 |
| nsr052 | +0.814 | +0.973 | 135.4 | 20.0 |
| nsr053 | +0.155 | +0.982 | 176.5 | 25.0 |
| nsr054 | +0.328 | +0.916 | 180.7 | 25.7 |

The ARA online method did not beat persistence on either metric for any subject. This shows that the high one-step correlations mainly reflect the very strong similarity of adjacent RR intervals, which a simple local baseline captures much better.

### True cold task

| Subject | ARA cold corr | Fourier cold corr | ARA cold MAE | Fourier cold MAE | Train-mean MAE |
|---|---:|---:|---:|---:|---:|
| nsr051 | -0.505 | +0.044 | 189.9 | 171.0 | 162.1 |
| nsr052 | -0.399 | -0.449 | 176.4 | 192.7 | 165.1 |
| nsr053 | -0.706 | +0.026 | 230.9 | 177.5 | 175.0 |
| nsr054 | -0.241 | -0.057 | 236.3 | 232.2 | 225.6 |

ARA had negative cold correlation on all four subjects and worse MAE than the training-mean baseline on all four. It beat both Fourier metrics only on `nsr052`, but neither method was useful there in absolute terms.

## Verdict

The historical `+0.686` versus `+0.308` result is **exactly reproducible**, but its original interpretation is not.

1. It was an online, one-beat-ahead calculation that consumed 29,420 true test observations after the first test beat. It was not a 5.99-hour cold prediction.
2. Its ARA-over-Fourier advantage replicated on both metrics in only 1 of 4 frozen subjects.
3. The mean replication difference favoured Fourier by 0.142 correlation and 11.4 ms MAE.
4. A one-step persistence baseline decisively beat both approaches on every subject.
5. With test updates removed, ARA did not produce useful cold forecasts.
6. The old full-resolution table reported “7 parameters,” but the recovered code selected **7 ARA subsystems** and counted each as three parameters plus a centerline: **22 ARA parameters**. It therefore fitted 10 Fourier frequencies, or **21 Fourier coefficients**. The methods were approximately parameter-matched under the old rule, but the displayed parameter count was wrong. Candidate selection over 22 rungs or the FFT frequency grid adds uncounted selection flexibility to both sides.

The defensible status is therefore: **reproduced historical computation; failed as a general ARA forecasting result under post-leak replication.** The `nsr052` contrast remains an interesting subject-specific result, but it cannot support a general claim without a separately motivated mechanism that predicts in advance which subjects should benefit.
