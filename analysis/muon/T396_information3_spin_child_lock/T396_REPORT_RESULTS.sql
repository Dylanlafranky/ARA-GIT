-- DuckDB reproduction queries for the bounded T396 report datasets.
-- Run from this directory.

CREATE OR REPLACE VIEW nll_models AS
SELECT
  model,
  CAST(mean_nll AS DOUBLE) AS mean_nll,
  CAST(delta_vs_parent AS DOUBLE) AS gain_vs_parent
FROM read_csv_auto('T396_NLL_COMPARISON.csv', header = true);

CREATE OR REPLACE VIEW sensitivity AS
SELECT
  CAST(polarization AS DOUBLE) AS polarization,
  'Factorized two-cut fusion' AS estimator,
  CAST(additive_incremental_gain AS DOUBLE) AS gain,
  CAST(additive_gain_ci95_low AS DOUBLE) AS ci_low,
  CAST(additive_gain_ci95_high AS DOUBLE) AS ci_high,
  CAST(holdout_n AS BIGINT) AS holdout_n
FROM read_csv_auto('T396_SENSITIVITY.csv', header = true)
UNION ALL
SELECT
  CAST(polarization AS DOUBLE) AS polarization,
  'Dense joint histogram' AS estimator,
  CAST(incremental_gain AS DOUBLE) AS gain,
  CAST(gain_ci95_low AS DOUBLE) AS ci_low,
  CAST(gain_ci95_high AS DOUBLE) AS ci_high,
  CAST(holdout_n AS BIGINT) AS holdout_n
FROM read_csv_auto('T396_SENSITIVITY.csv', header = true);

CREATE OR REPLACE VIEW child_surface AS
SELECT
  printf('%.3f', CAST(parent_center AS DOUBLE)) AS parent_cut,
  printf('%.3f', CAST(relation_center AS DOUBLE)) AS spin_relation,
  CAST(observed_child_mean AS DOUBLE) AS observed_child_mean,
  CAST(predicted_child_mean AS DOUBLE) AS predicted_child_mean,
  CAST(n AS BIGINT) AS n
FROM read_csv_auto('T396_CHILD_SURFACE.csv', header = true);

SELECT * FROM nll_models;
SELECT * FROM sensitivity;
SELECT * FROM child_surface;
