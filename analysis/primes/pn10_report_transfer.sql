SELECT
    cutoff,
    method,
    absolute_q,
    development_purity,
    evaluation_purity,
    purity_transfer_error,
    evaluation_brier,
    evaluation_remaining_composites
FROM pn10_transfer
ORDER BY cutoff, method;

