# Frozen protocol — Q6 CHSH coherence ladder

**Protocol ID:** `Q6-CHSH-COHERENCE-v1`  
**Ledger ID:** `T264`  
**Frozen:** 24 July 2026, 12:23 AEST  
**Test class:** post-Q5 known-source calibration plus physically prepared Bell-state check  
**Source:** Figshare DOI `10.6084/m9.figshare.14160476.v2`

## Inputs

Use the same four checksum-locked raw-current archives, decoder, record classification and Pauli expectation
reconstruction as Q5 without changing a threshold or relabelling a state:

- `Phi-plus`
- `Phi-minus`
- `Psi-plus`
- `Psi-minus`

Required source checksums and orientation maps are inherited verbatim from
`Q5_BELL_FOUR_STATE_PROTOCOL_v1_FROZEN.md`.

## Derived objects

For every physically prepared state:

1. reconstruct all nine two-qubit expectations `XX,XY,XZ,YX,YY,YZ,ZX,ZY,ZZ`;
2. assemble the \(3\times3\) correlation tensor \(T\);
3. calculate descending singular values \(s_1,s_2,s_3\);
4. calculate \(S_{\max}=2\sqrt{s_1^2+s_2^2}\);
5. count retained relation axes \(r_{0.5}=\#\{s_i\ge0.50\}\).

Construct three equal-state-weight controls:

- `Phi-classical = 0.5 Phi-plus + 0.5 Phi-minus`;
- `Psi-classical = 0.5 Psi-plus + 0.5 Psi-minus`;
- `Bell-uniform-mixed = 0.25` times the sum of all four Bell states.

Do not pool unequal record counts. Average the state expectation tensors with the declared equal weights.

## Frozen bootstrap

- Seed: `2026072406`.
- Replicates: `5,000`.
- Resample complete classified records with replacement inside every state and measurement orientation.
- Reconstruct each state tensor for every draw.
- Form each control from independently resampled state tensors using the same fixed equal weights.
- Report percentile `95%` intervals and gate-stability proportions.

## Frozen gates

All gates must pass for `SUPPORTED`; any failure gives `NOT SUPPORTED`. A decoder/source failure gives
`INCONCLUSIVE`.

### Physically prepared Bell states

1. `B1`: all four have \(S_{\max}>2.00\).
2. `B2`: all four have \(S_{\max}\ge2.30\).
3. `B3`: all four have \(s_2\ge0.50\).
4. `B4`: all four have exactly three retained relation axes at threshold `0.50`.
5. `B5`: each Bell state's bootstrap fraction with \(S_{\max}>2.00\) is at least `0.95`.

### Reconstructed classical controls

6. `C1`: both classical controls have \(S_{\max}\le2.00\).
7. `C2`: both have \(s_1\ge0.75\).
8. `C3`: both have \(s_2\le0.25\).
9. `C4`: both have exactly one retained relation axis at threshold `0.50`.
10. `C5`: each classical control's bootstrap fraction with \(S_{\max}\le2.10\) is at least `0.90`.

### Reconstructed fully mixed control and ordering

11. `M1`: the uniform control has \(S_{\max}\le0.50\).
12. `M2`: the uniform control has \(s_1\le0.25\).
13. `M3`: the uniform control has zero retained relation axes at threshold `0.50`.
14. `M4`: its bootstrap fraction with \(S_{\max}\le0.50\) is at least `0.95`.
15. `O1`: mean Bell \(S_{\max}\) minus mean classical-control \(S_{\max}\) is at least `0.50`.
16. `O2`: the point-estimate retained-axis sequence is exactly `3,3,3,3 / 1,1 / 0`.

## Required outputs

- state/control tensor and singular-value table;
- CHSH and bootstrap table;
- gate table and two-output verdict;
- independent validator that does not import the primary runner;
- explicit separation of physically prepared rows from algebraically reconstructed controls.

## Interpretation boundary

A pass recovers an established quantum coherence ladder through the frozen ARA parent/child language. It does not
make the reconstructed controls into new experiments and does not constitute a new quantum prediction.

