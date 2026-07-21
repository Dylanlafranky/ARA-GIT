SELECT
    gate_rank,
    series,
    phase_a,
    median_a,
    p10_a,
    p90_a,
    population
FROM pn10b_child_rank_profile
ORDER BY series, gate_rank;
