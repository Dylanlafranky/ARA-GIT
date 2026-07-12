# ARA Double-Helix Prediction Result

**Date:** 2026-07-11  
**Protocol:** frozen in PREREGISTRATION.md before primary/replication scoring  
**Verdict:** **FAIL**

## What was tested

The ARA model used the same causal local harmonic states as the rolling-circle control, then added:

- half-cycle phase/anti-phase consensus;
- full-cycle closure defect as helix pitch;
- train-only asymmetric accumulation/release projection;
- no fitted relation or closure weights.

## nsr047

Selected periods: [155, 208, 416] downsampled steps.  
Release fractions: [0.5634, 0.4599, 0.5048].  
ARA coordinates: [0.8732, 1.0803, 0.9904].

| h | circle corr | ARA corr | corr lift | circle MAE | ARA MAE | MAE lift | circle dir | ARA dir | transition lift |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | +0.873 | +0.873 | -0.000 | 46.753 | 46.782 | -0.029 | 0.590 | 0.589 | -0.001 |
| 3 | +0.763 | +0.763 | -0.000 | 65.630 | 65.696 | -0.066 | 0.621 | 0.620 | -0.001 |
| 6 | +0.747 | +0.747 | -0.000 | 73.880 | 73.931 | -0.051 | 0.630 | 0.630 | -0.000 |
| 12 | +0.741 | +0.741 | -0.000 | 83.471 | 83.365 | +0.106 | 0.614 | 0.614 | +0.000 |
| 24 | +0.721 | +0.721 | -0.001 | 95.205 | 94.579 | +0.626 | 0.600 | 0.600 | +0.002 |
| 48 | +0.669 | +0.666 | -0.003 | 116.050 | 114.312 | +1.738 | 0.604 | 0.602 | -0.002 |

### Full model comparison

| h | model | corr | MAE | direction | quadrant | amp ratio |
|---:|---|---:|---:|---:|---:|---:|
| 1 | persistence | +0.865 | 47.178 | 0.040 | 0.446 | 0.000 |
| 1 | ar_ridge | +0.873 | 47.247 | 0.580 | 0.556 | 0.427 |
| 1 | rolling_circle | +0.552 | 117.040 | 0.547 | 0.474 | 1.601 |
| 1 | shape_only | +0.552 | 117.116 | 0.548 | 0.477 | 1.601 |
| 1 | relation_only | +0.539 | 118.916 | 0.546 | 0.471 | 1.620 |
| 1 | ara_helix | +0.537 | 119.195 | 0.546 | 0.476 | 1.622 |
| 1 | ar_plus_circle | +0.873 | 46.753 | 0.590 | 0.567 | 0.425 |
| 1 | ar_plus_ara | +0.873 | 46.782 | 0.589 | 0.565 | 0.425 |
| 3 | persistence | +0.698 | 71.207 | 0.032 | 0.443 | 0.000 |
| 3 | ar_ridge | +0.762 | 67.150 | 0.612 | 0.552 | 0.458 |
| 3 | rolling_circle | +0.545 | 118.100 | 0.578 | 0.478 | 1.069 |
| 3 | shape_only | +0.545 | 118.157 | 0.578 | 0.479 | 1.069 |
| 3 | relation_only | +0.534 | 119.536 | 0.577 | 0.478 | 1.080 |
| 3 | ara_helix | +0.532 | 119.813 | 0.577 | 0.481 | 1.082 |
| 3 | ar_plus_circle | +0.763 | 65.630 | 0.621 | 0.564 | 0.455 |
| 3 | ar_plus_ara | +0.763 | 65.696 | 0.620 | 0.564 | 0.455 |
| 6 | persistence | +0.655 | 77.878 | 0.031 | 0.425 | 0.000 |
| 6 | ar_ridge | +0.745 | 76.475 | 0.625 | 0.553 | 0.543 |
| 6 | rolling_circle | +0.537 | 119.485 | 0.592 | 0.489 | 1.001 |
| 6 | shape_only | +0.537 | 119.515 | 0.590 | 0.489 | 1.001 |
| 6 | relation_only | +0.528 | 120.324 | 0.588 | 0.487 | 1.009 |
| 6 | ara_helix | +0.527 | 120.598 | 0.587 | 0.488 | 1.010 |
| 6 | ar_plus_circle | +0.747 | 73.880 | 0.630 | 0.563 | 0.538 |
| 6 | ar_plus_ara | +0.747 | 73.931 | 0.630 | 0.562 | 0.538 |
| 12 | persistence | +0.637 | 82.296 | 0.028 | 0.426 | 0.000 |
| 12 | ar_ridge | +0.741 | 87.368 | 0.611 | 0.528 | 0.623 |
| 12 | rolling_circle | +0.522 | 122.153 | 0.591 | 0.480 | 0.975 |
| 12 | shape_only | +0.522 | 122.139 | 0.592 | 0.483 | 0.975 |
| 12 | relation_only | +0.518 | 121.832 | 0.589 | 0.481 | 0.979 |
| 12 | ara_helix | +0.517 | 122.102 | 0.589 | 0.483 | 0.980 |
| 12 | ar_plus_circle | +0.741 | 83.471 | 0.614 | 0.533 | 0.615 |
| 12 | ar_plus_ara | +0.741 | 83.365 | 0.614 | 0.533 | 0.615 |
| 24 | persistence | +0.630 | 84.398 | 0.024 | 0.431 | 0.000 |
| 24 | ar_ridge | +0.722 | 100.062 | 0.599 | 0.505 | 0.669 |
| 24 | rolling_circle | +0.495 | 127.172 | 0.578 | 0.466 | 0.967 |
| 24 | shape_only | +0.495 | 127.084 | 0.578 | 0.467 | 0.966 |
| 24 | relation_only | +0.500 | 124.742 | 0.577 | 0.468 | 0.964 |
| 24 | ara_helix | +0.498 | 124.975 | 0.576 | 0.468 | 0.965 |
| 24 | ar_plus_circle | +0.721 | 95.205 | 0.600 | 0.506 | 0.654 |
| 24 | ar_plus_ara | +0.721 | 94.579 | 0.600 | 0.507 | 0.653 |
| 48 | persistence | +0.571 | 94.421 | 0.025 | 0.421 | 0.000 |
| 48 | ar_ridge | +0.673 | 122.419 | 0.603 | 0.474 | 0.725 |
| 48 | rolling_circle | +0.464 | 133.988 | 0.583 | 0.454 | 0.887 |
| 48 | shape_only | +0.463 | 133.848 | 0.584 | 0.441 | 0.886 |
| 48 | relation_only | +0.477 | 128.786 | 0.584 | 0.457 | 0.878 |
| 48 | ara_helix | +0.475 | 128.844 | 0.582 | 0.454 | 0.878 |
| 48 | ar_plus_circle | +0.669 | 116.050 | 0.604 | 0.482 | 0.699 |
| 48 | ar_plus_ara | +0.666 | 114.312 | 0.602 | 0.481 | 0.694 |

Causal prefix audit: {'prefix_end': 8033, 'max_coefficient_difference': 0.0, 'passed': True}

## nsr053

Selected periods: [141, 223, 407] downsampled steps.  
Release fractions: [0.4043, 0.4455, 0.3061].  
ARA coordinates: [1.1913, 1.1091, 1.3879].

| h | circle corr | ARA corr | corr lift | circle MAE | ARA MAE | MAE lift | circle dir | ARA dir | transition lift |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | +0.957 | +0.957 | +0.000 | 38.493 | 38.388 | +0.105 | 0.586 | 0.589 | +0.004 |
| 3 | +0.919 | +0.919 | +0.000 | 48.941 | 48.788 | +0.153 | 0.628 | 0.630 | +0.002 |
| 6 | +0.905 | +0.905 | -0.000 | 55.047 | 54.905 | +0.142 | 0.612 | 0.613 | +0.005 |
| 12 | +0.883 | +0.883 | +0.000 | 67.713 | 66.928 | +0.785 | 0.585 | 0.587 | +0.003 |
| 24 | +0.856 | +0.856 | +0.001 | 85.158 | 82.360 | +2.798 | 0.556 | 0.565 | +0.012 |
| 48 | +0.822 | +0.825 | +0.003 | 112.919 | 101.667 | +11.252 | 0.531 | 0.544 | +0.016 |

### Full model comparison

| h | model | corr | MAE | direction | quadrant | amp ratio |
|---:|---|---:|---:|---:|---:|---:|
| 1 | persistence | +0.953 | 39.345 | 0.045 | 0.468 | 0.000 |
| 1 | ar_ridge | +0.957 | 37.225 | 0.616 | 0.618 | 0.397 |
| 1 | rolling_circle | +0.608 | 131.562 | 0.530 | 0.431 | 2.684 |
| 1 | shape_only | +0.488 | 140.131 | 0.531 | 0.431 | 2.868 |
| 1 | relation_only | +0.612 | 130.696 | 0.528 | 0.430 | 2.674 |
| 1 | ara_helix | +0.529 | 137.277 | 0.528 | 0.428 | 2.810 |
| 1 | ar_plus_circle | +0.957 | 38.493 | 0.586 | 0.605 | 0.402 |
| 1 | ar_plus_ara | +0.957 | 38.388 | 0.589 | 0.607 | 0.402 |
| 3 | persistence | +0.898 | 53.961 | 0.034 | 0.477 | 0.000 |
| 3 | ar_ridge | +0.919 | 47.243 | 0.644 | 0.625 | 0.461 |
| 3 | rolling_circle | +0.596 | 132.548 | 0.565 | 0.452 | 1.835 |
| 3 | shape_only | +0.476 | 140.978 | 0.565 | 0.452 | 1.959 |
| 3 | relation_only | +0.605 | 131.395 | 0.566 | 0.454 | 1.824 |
| 3 | ara_helix | +0.521 | 137.861 | 0.568 | 0.455 | 1.916 |
| 3 | ar_plus_circle | +0.919 | 48.941 | 0.628 | 0.636 | 0.468 |
| 3 | ar_plus_ara | +0.919 | 48.788 | 0.630 | 0.635 | 0.468 |
| 6 | persistence | +0.877 | 58.955 | 0.027 | 0.489 | 0.000 |
| 6 | ar_ridge | +0.906 | 52.415 | 0.640 | 0.608 | 0.437 |
| 6 | rolling_circle | +0.579 | 133.954 | 0.570 | 0.444 | 1.683 |
| 6 | shape_only | +0.459 | 142.165 | 0.574 | 0.449 | 1.794 |
| 6 | relation_only | +0.594 | 132.391 | 0.573 | 0.447 | 1.668 |
| 6 | ara_helix | +0.511 | 138.681 | 0.577 | 0.453 | 1.750 |
| 6 | ar_plus_circle | +0.905 | 55.047 | 0.612 | 0.613 | 0.449 |
| 6 | ar_plus_ara | +0.905 | 54.905 | 0.613 | 0.614 | 0.449 |
| 12 | persistence | +0.853 | 66.573 | 0.027 | 0.484 | 0.000 |
| 12 | ar_ridge | +0.884 | 61.040 | 0.624 | 0.591 | 0.501 |
| 12 | rolling_circle | +0.546 | 136.620 | 0.581 | 0.454 | 1.564 |
| 12 | shape_only | +0.427 | 144.321 | 0.585 | 0.459 | 1.661 |
| 12 | relation_only | +0.573 | 134.261 | 0.585 | 0.459 | 1.541 |
| 12 | ara_helix | +0.491 | 140.171 | 0.587 | 0.462 | 1.612 |
| 12 | ar_plus_circle | +0.883 | 67.713 | 0.585 | 0.585 | 0.524 |
| 12 | ar_plus_ara | +0.883 | 66.928 | 0.587 | 0.587 | 0.522 |
| 24 | persistence | +0.822 | 75.691 | 0.030 | 0.465 | 0.000 |
| 24 | ar_ridge | +0.861 | 70.273 | 0.635 | 0.590 | 0.563 |
| 24 | rolling_circle | +0.481 | 141.654 | 0.593 | 0.477 | 1.470 |
| 24 | shape_only | +0.372 | 148.111 | 0.596 | 0.479 | 1.547 |
| 24 | relation_only | +0.529 | 137.947 | 0.598 | 0.482 | 1.434 |
| 24 | ara_helix | +0.453 | 143.001 | 0.601 | 0.485 | 1.492 |
| 24 | ar_plus_circle | +0.856 | 85.158 | 0.556 | 0.532 | 0.599 |
| 24 | ar_plus_ara | +0.856 | 82.360 | 0.565 | 0.552 | 0.593 |
| 48 | persistence | +0.789 | 84.305 | 0.022 | 0.462 | 0.000 |
| 48 | ar_ridge | +0.834 | 77.610 | 0.635 | 0.577 | 0.582 |
| 48 | rolling_circle | +0.377 | 149.199 | 0.612 | 0.482 | 1.420 |
| 48 | shape_only | +0.309 | 152.713 | 0.616 | 0.487 | 1.461 |
| 48 | relation_only | +0.450 | 144.297 | 0.616 | 0.487 | 1.373 |
| 48 | ara_helix | +0.394 | 147.434 | 0.621 | 0.493 | 1.409 |
| 48 | ar_plus_circle | +0.822 | 112.919 | 0.531 | 0.471 | 0.625 |
| 48 | ar_plus_ara | +0.825 | 101.667 | 0.544 | 0.487 | 0.612 |

Causal prefix audit: {'prefix_end': 7039, 'max_coefficient_difference': 0.0, 'passed': True}

## Preregistered decision

- Primary horizons winning both correlation and MAE: **0/6**.
- Mean correlation lift, primary: **-0.001**.
- Mean correlation lift, replication: **+0.001**.
- Mean transition-direction lift, primary: **-0.001**.
- Mean transition-direction lift, replication: **+0.007**.

The verdict above is mechanical under the frozen pass/failure rules. Any reinterpretation belongs in a separately labelled follow-up, not in this result.
