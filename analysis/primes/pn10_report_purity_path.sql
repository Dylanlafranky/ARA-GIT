SELECT
    cutoff,
    interval,
    prime_purity,
    survivors,
    remaining_composites
FROM pn10_purity_path
ORDER BY interval, cutoff;

