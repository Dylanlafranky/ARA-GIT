SELECT
  'Centre ' || center_mod6 || ', lane ' || offset_lane_mod6 AS lane_label,
  center_mod6,
  offset_lane_mod6,
  center_count,
  offset_count_per_center,
  observation_count,
  parent_progress_mean,
  parent_progress_sd,
  parent_progress_median,
  prime_rate,
  survivor_rate,
  divisible_by_3_rate,
  divisible_by_5_rate
FROM pn10c_lane_summary
WHERE center_group = 'prime'
  AND direction = 'all'
ORDER BY center_mod6, offset_lane_mod6;
