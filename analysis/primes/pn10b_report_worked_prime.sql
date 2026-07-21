SELECT
    gate_rank,
    gate_q,
    remainder,
    phase_a,
    phase_b,
    signed_orientation,
    coupling_to_next_rank
FROM pn10b_worked_prime_children
ORDER BY gate_rank;
