SELECT
  'Centre ' || center_mod6 || ' mod 6' AS center_orientation,
  center_mod6,
  offset,
  offset_lane_mod6,
  center_count,
  parent_progress_mean,
  parent_progress_median,
  prime_rate,
  survivor_rate,
  divisible_by_3_rate,
  divisible_by_5_rate
FROM pn10c_offset_profile
WHERE center_group = 'prime'
  AND offset BETWEEN -30 AND 30
ORDER BY center_mod6, offset;
