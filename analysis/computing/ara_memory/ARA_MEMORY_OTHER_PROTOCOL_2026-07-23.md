# Frozen protocol — ARA `Other` memory, compression and security test

**Frozen:** 23 July 2026, before running the primary experiment  
**Orientation:** two child values are compressed upward into one parent value; their signed unresolved difference
is retained as `Other`. Reconstruction walks downward from parent plus `Other` to the original children.

## 1. Claims are separated before testing

This protocol tests five distinct statements:

1. **lossless restoration:** parent plus every retained `Other` coefficient reconstructs the original bytes exactly;
2. **compression:** the retained `Other` coefficients have lower coded entropy than the original bytes in suitable
   structured data;
3. **failure control:** incompressible random data does not acquire a false compression win;
4. **confidentiality:** an unkeyed `Other` representation is or is not secret from someone who knows the transform;
5. **authenticated encryption compatibility:** standard authenticated encryption can protect the compressed
   residual stream and reject tampering.

No result in one category counts as evidence for another.

## 2. Frozen reversible ARA transform

For every ordered child pair \(a,b\), define

\[
\underbrace{m}_{\substack{\text{parent/coarse value}\\\text{compressed whole}}}
=
b+\left\lfloor\frac{a-b}{2}\right\rfloor,
\qquad
\underbrace{d}_{\substack{\text{signed child difference}\\\text{retained Other}}}
=a-b.
\]

The inverse is

\[
b=m-\left\lfloor\frac d2\right\rfloor,
\qquad
a=b+d.
\]

This pair transform is applied recursively to the parent values until each fixed-size block has one root parent.
The stored representation is:

1. a header containing version, original length and block size;
2. one root parent per block;
3. every signed `Other` coefficient, coarse level to fine level, encoded with signed zig-zag variable integers.

This is an ARA interpretation of a reversible integer lifting/Haar-style transform. It is not claimed as a new
compression theorem.

## 3. Frozen datasets

Each dataset contains exactly `65,536` bytes:

1. `smooth_telemetry` — quantized slow and fast cyclic sensor structure with deterministic small noise;
2. `piecewise_memory` — repeated records, counters, status fields and slowly changing blocks;
3. `ara_text` — UTF-8 bytes from canonical ARA Markdown files;
4. `python_source` — UTF-8 bytes from sorted repository Python source files;
5. `uniform_random` — deterministic pseudorandom bytes used only as an incompressible control.

The primary ARA block size is `1,024` bytes. Sensitivity sizes `64`, `256` and `4,096` are reported but cannot
replace the primary result.

## 4. Frozen comparisons

For each dataset:

- raw bytes compressed with `zlib` level 9;
- ordinary previous-byte signed delta coding followed by `zlib` level 9;
- ARA parent/`Other` serialization followed by `zlib` level 9.

All container overhead is counted.

## 5. Frozen restoration criteria

Lossless restoration passes only if:

- every dataset and block-size combination reconstructs byte-for-byte;
- original and restored SHA-256 hashes match;
- the independent validator's separate inverse implementation also reconstructs all datasets.

## 6. Frozen compression criteria

The compression hypothesis passes narrowly only if, at the primary `1,024` block size:

- `ARA + zlib` is at least `5%` smaller than raw `zlib` on both structured numeric datasets;
- all restoration checks pass;
- the uniform-random control does **not** improve by more than `1%`.

Text and source code are diagnostic generalization sets. They are reported but are not allowed to replace the two
predeclared structured datasets.

## 7. Frozen security tests

### Test S1 — public-transform attacker

Give the attacker the ARA byte stream and the public transform, but no secret because none exists. Attempt exact
reconstruction.

If the attacker succeeds, the unkeyed `Other` representation provides zero confidentiality.

### Test S2 — authenticated wrapper

Compress the ARA representation and protect it with AES-256-GCM using a unique 96-bit nonce per deterministic test
vector. Test:

1. decrypt, decompress and restore exactly;
2. flip one ciphertext bit and require authentication failure;
3. record the nonce-plus-tag overhead;
4. confirm that compressing ciphertext does not materially reduce it.

The key and nonces are public deterministic **test vectors**, never production key-management guidance. Any security
belongs to AES-GCM, not to ARA preprocessing.

## 8. Prime-replacement fence

The experiment cannot establish a replacement for RSA, Diffie–Hellman or other public-key constructions.
That would require, at minimum:

1. a keyed public/private construction;
2. a one-way problem with a trapdoor or equivalent key-establishment assumption;
3. chosen-plaintext, chosen-ciphertext, related-key and structural cryptanalysis;
4. security reductions or sustained independent attack;
5. constant-time implementation and side-channel review.

Without those, ARA `Other` is a reversible representation or compression preconditioner, not a public-key
cryptosystem.

## 9. Verdict language

- restoration: `CONFIRMED` only for the implemented reversible transform and tested vectors;
- compression: `SUPPORTED`, `MIXED` or `NOT SUPPORTED` by frozen dataset class;
- naïve encryption: `FAILED` if public inversion recovers the plaintext;
- authenticated wrapper: `COMPATIBLE WITH STANDARD ENCRYPTION`, never `ARA ENCRYPTION PROVED`;
- prime replacement: `NOT ESTABLISHED`.
