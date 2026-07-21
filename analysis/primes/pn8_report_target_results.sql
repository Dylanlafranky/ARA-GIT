WITH target_results (
  exponent,
  public_offset,
  crossing_gap,
  target_bin,
  m2_rank,
  m2_log_loss_bits,
  top3_hit
) AS (
  VALUES
    (50, 151, 208, 16, 8, 4.247109216288599, 'No'),
    (100, 267, 1064, 21, 2, 3.1046904625665066, 'Yes'),
    (150, 67, 340, 12, 8, 4.2607651760274905, 'No'),
    (200, 357, 546, 21, 5, 3.925999418556223, 'No'),
    (250, 1227, 1260, 15, 16, 4.845457181117699, 'No')
)
SELECT
  exponent,
  public_offset,
  crossing_gap,
  target_bin,
  m2_rank,
  m2_log_loss_bits,
  top3_hit
FROM target_results
ORDER BY exponent ASC;

