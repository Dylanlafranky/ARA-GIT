SELECT
  model,
  feature_count,
  log_loss_bits,
  brier,
  auc,
  top_decile_lift,
  calibration_error
FROM pn10b_metrics
WHERE stage = 'pooled_D_E_to_fresh_F'
ORDER BY log_loss_bits ASC;
