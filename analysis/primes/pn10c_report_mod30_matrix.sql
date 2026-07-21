SELECT
  center_mod5,
  black_child_m_mod5,
  offset_mod30,
  predicted_factor5_collision,
  center_count,
  offset_count_per_center,
  observation_count,
  parent_progress_mean,
  parent_progress_median,
  prime_rate,
  survivor_rate,
  divisible_by_5_rate
FROM pn10c_mod30_matrix
WHERE center_group = 'prime'
ORDER BY center_mod5, black_child_m_mod5;
