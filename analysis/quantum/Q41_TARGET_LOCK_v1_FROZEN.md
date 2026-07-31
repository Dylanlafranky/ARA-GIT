# Q41 target lock — frozen before target access

Date: 2026-07-27 (Australia/Brisbane)

Test ID: `Q41-CADENCE-STRAND-REVERSAL-v1`

## Frozen documents

- Fidelity packet SHA-256:
  `fe1574a6afa6f440cb999d3fd07bf6113c674e15ee4b6e958cbc754370990646`
- Protocol SHA-256:
  `325bc7ac959af0c5327e4d1b4566391d55806a18bf1a87516747cd021c3ef595`

## Frozen target

- Zenodo DOI: `10.5281/zenodo.16753415`
- Archive:
  `unnati_submit_12_inhomo_v1_random.hdf5.zip`
- Deposited MD5:
  `f342ff3dda39915da3332db65cc7c2c8`
- HDF member:
  `unnati_submit_12_inhomo_v1_random.hdf5`
- Branch:
  `c2_2local connectivity`

The target was selected using public record metadata only. It had not been
downloaded, extracted or inspected in the local Q41 directory when the
fidelity packet, protocol and this lock were written.

## Frozen addition to Q40

Keep the Q40 visible reversal flag. Also reverse when:

1. the closure-plane angular period lies in `[7.35, 7.65]`;
2. its lag-15 two-coordinate return correlation is at least `0.95`; and
3. the target visit is the already defined Ba quadrant (`q4 = 1`).

No other target-dependent classifier, coefficient, threshold or exception may
be added after target access.

## Allowed development fitting

Only the previously declared development-affine comparator may fit
coefficients, and it may use samples 0–249 only. The Q41 strand rule has no
target-fitted coefficient.

## Reveal order

1. verify archive MD5 and schema;
2. derive closure and connected-correlation caches;
3. construct all cycle windows and Q41/control predictions without reading
   the fourth connected identity;
4. write and SHA-256 hash the prediction artifact;
5. reveal fourth identities and score;
6. validate with an independent script.

