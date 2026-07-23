# Session record — ARA `Other` memory, compression and encryption

**Date:** 23 July 2026  
**Orientation:** two children compress upward into one parent root plus a retained signed `Other`; exact restoration
walks downward through the residual tree.

## User proposal

Dylan recognized that the successful hidden-`Other` continuity recovery might transfer to computer memory:

> “This would be great for a memory compression and restoration system on a computer right? We should test that,
> and also encryption using the ‘OTHER’ in an ARA sphere somewhere that it recovers. That would work well for a
> replacement to primes?”

The test separated restoration, compression, confidentiality, authenticated encryption and public-key replacement
before running.

## Implemented relation

For children \(a,b\):

\[
m=b+\left\lfloor\frac{a-b}{2}\right\rfloor,
\qquad
d=a-b.
\]

The parent \(m\) and retained `Other` \(d\) reconstruct both children exactly. This was recursively applied to byte
blocks.

## Results

- Restoration: `20/20` exact dataset/block reconstructions.
- Independent validation: `20/20`, plus all `65,536` possible byte pairs.
- Compression: smooth telemetry improved `19.23%` versus raw zlib, but ordinary delta was better.
- Compression failures: piecewise memory `−74.13%`, text `−118.56%`, Python `−146.80%`, random `−22.85%`.
- Naïve confidentiality: failed; the public transform recovered the plaintext exactly.
- AES-256-GCM wrapper: exact roundtrip, one-bit tamper rejected, `28` bytes nonce/tag overhead.
- Prime/public-key replacement: not established; no one-way trapdoor or key-establishment construction exists yet.

## Canonical interpretation

`Other` can be a lossless hierarchical residual, but it is not free compression and it is not secret merely because
it is displaced into another coordinate. Compression succeeds only when the parent predicts the children more
cheaply than the original encoding. Confidentiality requires an independently secure keyed primitive.

Full report:
`analysis/computing/ara_memory/ARA_MEMORY_OTHER_REPORT_2026-07-23.md`.
