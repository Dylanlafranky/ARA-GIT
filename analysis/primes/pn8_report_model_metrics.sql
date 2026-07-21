WITH model_metrics (
  model,
  mean_log_loss_bits,
  top1_hits,
  top3_hits,
  targets,
  comparison_role
) AS (
  VALUES
    ('ARA-M2', 4.076804290911303, 0, 1, 5, 'primary'),
    ('ARA-IID', 4.487415444268502, 1, 1, 5, 'ARA baseline'),
    ('Uniform 24-bin', 4.584962500721156, NULL, NULL, 5, 'uniform baseline'),
    ('ARA-M1', 4.643777806993624, 1, 1, 5, 'ARA baseline')
)
SELECT
  model,
  mean_log_loss_bits,
  top1_hits,
  top3_hits,
  targets,
  comparison_role
FROM model_metrics
ORDER BY mean_log_loss_bits ASC;

