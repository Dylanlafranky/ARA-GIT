# ARA `Other` memory, compression and security test

**Orientation:** child values compress upward into a parent; the signed child difference is retained as `Other`.
Restoration walks downward from the parent plus every retained `Other` coefficient.

**Date:** 23 July 2026  
**Status:** exact restoration confirmed; compression mixed; naïve confidentiality failed; authenticated-encryption
compatibility confirmed; prime replacement not established.

## Answer first

The computing idea is real, but its strongest form is **reversible predictive representation**, not universal
compression or standalone encryption.

The frozen ARA pair transform reconstructed every byte exactly in `20/20` dataset/block tests. An independent
implementation also reconstructed all `20/20`, and all `65,536` possible byte pairs satisfied the elementary
parent-plus-`Other` inverse.

Compression depended on the data:

- smooth telemetry: `ARA + zlib` was `19.23%` smaller than raw zlib;
- record-heavy memory: `74.13%` larger;
- ARA text: `118.56%` larger;
- Python source: `146.80%` larger;
- uniform random control: `22.85%` larger.

Ordinary previous-byte delta coding also beat ARA on the smooth telemetry (`22,378` versus `29,008` bytes).
Therefore the frozen universal compression claim failed.

The unkeyed `Other` stream provided **zero confidentiality**: an attacker who knew the public transform restored
the original exactly. AES-256-GCM successfully protected the compressed stream and rejected one-bit tampering, but
that security came from AES-GCM, not from hiding data in an ARA sphere.

## Frozen transform

For ordered children \(a,b\):

\[
\underbrace{m}_{\text{parent}}
=
b+\left\lfloor\frac{a-b}{2}\right\rfloor,
\qquad
\underbrace{d}_{\text{retained Other}}
=a-b.
\]

The inverse is:

\[
b=m-\left\lfloor\frac d2\right\rfloor,
\qquad
a=b+d.
\]

The transform recursively combines child pairs until a block has one parent root. The residual tree preserves the
details needed to walk back down.

Plainly: the parent remembers the broad local value; `Other` remembers what was lost when two children became one.
If every `Other` is retained, decompression is exact.

This is mathematically close to an integer lifting or reversible Haar-style transform. ARA supplies a useful
relational interpretation, but the reversible-transform family is established computing practice.

## Primary compression results

All datasets contained exactly `65,536` bytes. The frozen primary block was `1,024` bytes.

| Dataset | Class | Raw zlib | Delta + zlib | ARA + zlib | ARA versus raw |
|---|---|---:|---:|---:|---:|
| smooth telemetry | structured numeric | 35,915 | **22,378** | 29,008 | **+19.23%** |
| piecewise memory | structured numeric | **14,424** | 17,651 | 25,117 | −74.13% |
| ARA text | generalization | **25,256** | 32,483 | 55,200 | −118.56% |
| Python source | generalization | **19,526** | 25,647 | 48,190 | −146.80% |
| uniform random | incompressible control | **65,562** | 85,692 | 80,542 | −22.85% |

Positive means ARA produced fewer bytes than raw zlib. Negative means it produced more.

The same qualitative pattern held at block sizes `64`, `256`, `1,024` and `4,096`: the smooth signal benefited,
while every other class grew. The result is therefore not an unlucky single block-size choice.

## Why the compression split occurred

Smooth telemetry has small, correlated differences. The ARA residual tree concentrates much of its information
into small signed coefficients that zlib can encode efficiently.

Record-heavy memory, text and code already contain repetition that raw zlib exploits directly. The recursive pair
transform breaks many repeated byte sequences into a wider coefficient alphabet, destroying useful locality.
Uniform random data has no structure to remove, so the transform adds headers and variable-integer expansion.

This produces a clean rule:

> `Other` compresses only when the chosen parent predicts its children well enough that the residual description is
> cheaper than the original structure it disrupts.

That is a model-selection problem, not a universal consequence of reversibility.

## Restoration result

Restoration is the strongest result:

- `5` datasets × `4` block sizes = `20/20` exact reconstructions;
- original and restored SHA-256 hashes matched;
- independent reference decoder matched all encoded streams and sizes;
- all `256 × 256 = 65,536` elementary byte pairs inverted exactly.

This supports an ARA memory architecture in which a parent summary and a recursively retained `Other` tree provide
multi-resolution access. It does **not** mean damaged or missing `Other` coefficients can be recreated. Error
recovery would require redundancy or an error-correcting code in addition to the transform.

## Security result

### Unkeyed `Other`

The attacker was given the ARA stream and public transform. It recovered the original SHA-256 exactly.

Verdict: **FAILED as encryption**.

Moving the residual to a less obvious position is obscurity, not a cryptographic secret. A keyed placement rule
would itself need to behave like a secure pseudorandom permutation; at that point the security would come from the
keyed cryptographic primitive.

### Authenticated wrapper

The pipeline

\[
\text{data}
\rightarrow
\text{ARA residual representation}
\rightarrow
\text{zlib}
\rightarrow
\text{AES-256-GCM}
\]

restored exactly and rejected a one-bit ciphertext mutation. The nonce plus authentication-tag overhead was `28`
bytes. Compressing the ciphertext increased it by `16` bytes, as expected for high-entropy encrypted data.

NIST specifies GCM as authenticated encryption with associated data. This result shows compatibility with that
standard pattern; it does not turn the preceding transform into a cipher:
https://csrc.nist.gov/pubs/sp/800/38/d/final

Compression before encryption must also be used cautiously. If confidential and attacker-controlled data share a
compression context, output length can leak information; current TLS guidance explicitly warns about CRIME/BREACH
style attacks:
https://www.rfc-editor.org/rfc/rfc9325.html#section-3.3

## Does this replace primes?

No—not from the tested result.

Bulk data is normally protected with symmetric authenticated encryption; it does not require RSA-style prime
factorization for every byte. Public-key cryptography solves a different problem: establishing keys or verifying
signatures when the parties do not already share a secret.

An ARA `Other` public-key replacement would need an independently hard one-way construction, public/private key
separation, a trapdoor or equivalent key-establishment mechanism, and extensive cryptanalysis. None was defined in
this experiment.

Alternatives to factoring already exist. NIST's current post-quantum standards include the lattice-based ML-KEM
key-establishment standard and lattice/hash-based signatures:
https://csrc.nist.gov/News/2024/postquantum-cryptography-fips-approved

The strongest current computing claim is therefore:

> ARA parent-plus-`Other` is an exact hierarchical residual representation and a potentially useful preconditioner
> for smooth correlated data. It is not presently a universal compressor, cipher, key-exchange system or
> replacement for prime-based public-key methods.

## Best next test

The next useful direction is adaptive parent selection:

1. retain the same exact child/parent/`Other` inverse;
2. choose between raw, previous-byte delta, pair-lifting and record-aware predictors per block;
3. pay the exact selector/header cost;
4. freeze the selector on development data;
5. test unseen sensor, image, audio, memory-page, text and random files.

This would test whether ARA is valuable as a **container for selecting the correct local relation**, rather than as
one fixed transform forced onto every identity.

## Reproduction

```powershell
python analysis/computing/ara_memory/ara_memory_other_test.py
python analysis/computing/ara_memory/validate_ara_memory_other.py
```

Artifacts:

- `ARA_MEMORY_OTHER_PROTOCOL_2026-07-23.md`
- `ARA_MEMORY_OTHER_RESULTS.json`
- `ARA_MEMORY_OTHER_SUMMARY.csv`
- `ARA_MEMORY_OTHER_VALIDATION.json`
