-- decomposition
SELECT * FROM decomposition ORDER BY CASE pair WHEN 'AB' THEN 1 WHEN 'AC' THEN 2 ELSE 3 END;

-- paths
SELECT * FROM controlled_path ORDER BY pair, lambda, point_type;

-- uncertainty
SELECT pair, COUNT(*) AS n_draws, AVG(parallel_residual_arcsec2) AS mean_parallel, AVG(perpendicular_residual_arcsec2) AS mean_perpendicular FROM uncertainty_samples GROUP BY pair ORDER BY pair;

-- global_clean_fit
SELECT * FROM global_clean_fit ORDER BY measurement;