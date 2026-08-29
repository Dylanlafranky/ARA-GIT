# T448B — frozen 24-hour directional handover follow-up

T448's frozen shared-terminal-point gates failed before this follow-up was defined. T448B cannot alter that result.

## Who

The same 47 individual flies are used. Experiments 1–3 remain development; experiment 4 remains untouched holdout.

## What

For every hour with a one-day history, subtract the same fly's three-coordinate state exactly 24 hours earlier. This produces a three-coordinate displacement through the visible lifecycle shadow while holding Zeitgeber phase constant.

The development terminal direction is the median final-six-hour displacement vector across development flies. Holdout vectors are decomposed into:

- progress parallel to the frozen terminal direction;
- residual movement perpendicular to that direction;
- alignment cosine and total displacement magnitude.

This is a time-facing change cut through the behavioural state. It is not a claim that the 24-hour difference is time itself.

## When and where

Each current hour is compared with the same individual and same circadian phase one day earlier. The relational address is individual state → one-cycle displacement → development terminal direction → untouched holdout alignment.

## Why

T448 showed that several holdout terminal points lie beyond, rather than near, the development terminal centre. T448B tests the pre-declared alternative that collapse follows a shared direction or branch whose endpoint is distorted by experiment and individual asymmetry.

## How and frozen gates

1. Freeze the median three-coordinate terminal displacement vector using development flies only.
2. Project every holdout 24-hour displacement onto that vector without rotation or refitting.
3. Compare the real final-six-hour block with 2,000 within-fly circularly shifted fake endpoint blocks.

Gates frozen before viewing directional results:

- **Gate D:** real holdout mean parallel progress exceeds the 95th percentile of shifted endpoints.
- **Gate E:** at least 65% of holdout terminal observations have positive alignment and the median alignment cosine is at least +0.30.
- **Gate F:** the signed three-coordinate projection AUROC for final-six-hour versus earlier holdout displacements exceeds the best signed single-coordinate change by at least 0.02.

The perpendicular component is descriptive: a large value indicates distortion/branch variation even if the shared direction passes.
