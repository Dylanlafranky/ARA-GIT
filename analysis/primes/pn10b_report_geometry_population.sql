SELECT
    metric,
    prime_n,
    prime_mean,
    prime_median,
    prime_min,
    prime_max,
    composite_n,
    composite_mean,
    composite_median,
    standardized_difference
FROM pn10b_geometry_population
ORDER BY metric;
