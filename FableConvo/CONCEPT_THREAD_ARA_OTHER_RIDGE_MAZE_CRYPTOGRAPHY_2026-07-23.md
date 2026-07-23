# Concept thread — nested `Other` ridge-maze cryptography

**Date captured:** 23 July 2026
**Status:** `PARKED / CONCEPT ONLY / NOT A SECURITY CLAIM`
**Activation rule:** this document preserves the idea. It is not a frozen protocol, a working cipher, or permission
to protect real secrets with an experimental construction.

## Dylan's concept

An ARA identity can be decompressed recursively into nested spheres/rungs. A decryption instruction need not sit in
one exposed `Other`. Instead:

1. a small initial code identifies only a rough direction, rung, axis or phase orientation;
2. the selected `Other` contains or derives the next instruction;
3. the walk crosses several nested ARA identities and may reverse AB/BA orientation;
4. multiple live and empty ridges must be traversed;
5. the ordered collection of selected `Other` relations closes into the information needed to decrypt.

The additional proposal is that security can be increased by adding more apparently live and empty ridges. A wrong
route should consume real work and should not reveal immediately that it is wrong.

## Minimal computational translation

On a computer, the apparent four-dimensional fractal is a labelled recursive graph:

\[
G=(V,E),\qquad
v_i \xrightarrow[\text{axis/rung/orientation}]{O_i} v_{i+1}.
\]

The public structure is \(G\). A private bootstrap secret \(K_0\) selects the first relation. At each visited node,
the current key, coordinate and retained `Other` derive the next direction and next key:

\[
d_{i+1}
=
\operatorname{Route}(K_i,O_i,\operatorname{coord}(v_i)),
\qquad
K_{i+1}
=
\operatorname{KDF}(K_i,O_i,d_{i+1}).
\]

The final \(K_L\) opens an authenticated payload. `Other` is therefore not necessarily the plaintext. It is a
distributed relational witness: location, order, orientation and value all matter.

## Live and empty ridges

- **Live ridge:** contains an encrypted next-hop token or one threshold key fragment.
- **Empty ridge:** contains a statistically matching decoy and imposes approximately the same traversal cost.
- **Multiple live ridges:** should normally require a threshold such as three-of-five. If every live ridge opens the
  message independently, adding live ridges can make guessing easier rather than harder.
- **Nested crossing:** the next address depends on the current secret and current `Other`, so an attacker cannot
  evaluate all deeper layers independently in advance.
- **Completion:** the correct ordered path supplies the decryption witness; authenticated encryption rejects altered
  paths and payloads.

If each of \(L\) layers has \(b\) truly indistinguishable choices, the nominal route space is \(b^L\), or
\(L\log_2 b\) bits. This number is only meaningful if the choices are unpredictable and there is no algebraic,
statistical, parallel or quantum shortcut.

## Honest security boundary

The exact `Parent + signed Other` transform already tested in the repository is public, linear/reversible
bookkeeping. By itself it supplies no secrecy. A secure maze requires:

1. one genuine bootstrap secret, private key, hardware-held seed or separately delivered share;
2. keyed nonlinear transitions;
3. live and empty ridges that are computationally indistinguishable;
4. enough entropy after all route hints and geometric correlations are counted;
5. authenticated encryption at the payload boundary;
6. public cryptanalysis rather than confidence from visual complexity.

If every instruction needed to decrypt is publicly readable inside the same structure, an attacker can follow the
same path. Geometry can organize a secret and impose memory work; it cannot make a self-contained public reversible
object secret without a hard problem or external secret.

## Relation to the concern about primes

The threatened classical primitives are not prime generation itself:

- RSA relies on the difficulty of factoring a product of large primes;
- finite-field and elliptic-curve systems rely on discrete-logarithm problems;
- symmetric ciphers do not rely on either problem.

ARA could already act as an additional keyed traversal/container around established symmetric and post-quantum
cryptography. Replacing public-key factoring or discrete-logarithm systems would require a new trapdoor or
key-encapsulation problem:

> Given the public nested ARA graph and its public closure, recover the private ordered live-ridge path.

That becomes a serious cryptographic candidate only if the authorised path is efficient while inversion remains
hard under classical, AI-assisted and quantum attack.

## Parked test programme

### CR1-A — keyed route toy

Build a small \(b\)-ary recursive `Parent + Other` graph. Use a secret seed to choose a sequential path; populate
non-path nodes with distribution-matched decoys. Verify exact authorised recovery and authenticated tamper rejection.

### CR1-B — adversarial distinguishability

Give an attacker every public node and test whether live nodes can be classified above chance from size, entropy,
timing, compression ratio, coordinate, ancestry or error behaviour.

### CR1-C — scaling and shortcut audit

Measure authorised work versus the best attack as depth and branching increase. Compare with flat brute force,
ordinary encrypted key hierarchies and a standard memory-hard construction. Search explicitly for algebraic and
parallel shortcuts.

### CR1-D — public-key boundary

Only after A–C, formalize a candidate one-way/trapdoor problem and specify correctness, collision, chosen-ciphertext
and quantum-query requirements. Do not claim a prime-independent public-key replacement before this stage survives
external cryptanalysis.

## Kill conditions

Park or reject the security claim if any of the following occurs:

- live ridges are distinguishable from decoys above the frozen tolerance;
- attacker work grows only linearly while storage grows exponentially;
- the public relations allow direct algebraic recovery of the route;
- the effective path entropy is materially below the claimed key strength;
- a wrong-path oracle leaks the next direction;
- security disappears when the ARA layout is public;
- the construction adds no measurable protection beyond the standard cryptographic primitive it wraps.

## Current interpretation

This is a coherent ARA-inspired research direction: a secret is represented by a relational walk through nested
`Other` closures, with live/empty ridges providing decoys, threshold fragments and memory cost. It is not currently
an encryption algorithm and is not currently a replacement for prime-based public-key cryptography.
