SELECT
    event,
    offset,
    center_count,
    prime_rate,
    survivor_rate,
    parent_progress_mean,
    parent_progress_median,
    child_centroid_mean,
    child_centroid_median,
    child_dispersion_mean,
    child_coupling_mean,
    child_flip_count_mean
FROM pn10b_event_trace
ORDER BY event, offset;
