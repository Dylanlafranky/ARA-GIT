SELECT
  comparison,
  first_model,
  second_model,
  gain_bits_per_event,
  ci95_low,
  ci95_high,
  positive_blocks,
  blocks,
  draws
FROM pn10b_comparisons
ORDER BY comparison ASC;
