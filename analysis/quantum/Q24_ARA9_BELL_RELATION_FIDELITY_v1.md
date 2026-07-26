# Q24 ARA^9 Bell relation fidelity note

**Date:** 26 July 2026  
**Purpose:** preserve Dylan's geometry without allowing either ARA language or established quantum language to
silently replace the other.

## Controlling ARA statement

ARA^9 was previously described as three axes with nine couplings or nine addressable readings. In Q24, two
parents each supply three declared cuts. Their full ordered coupling therefore occupies a \(3\times3\) field.

The mapping is:

| ARA | Mathematics / established quantum |
|---|---|
| three cuts of parent A | first local Pauli/Bloch vector \(\mathbf a\) |
| three cuts of parent B | second local Pauli/Bloch vector \(\mathbf b\) |
| nine joint cuts | correlation tensor \(T_{ij}\) |
| what the two children do separately | outer product \(\mathbf a\mathbf b^\mathsf T\) |
| informative third / parent relation | connected tensor \(C=T-\mathbf a\mathbf b^\mathsf T\) |
| ARA^9 diameter cells | \(X^{(9)}=1-C\) |
| retained relation directions | singular values of \(C\) above a declared threshold |
| three-direction closure strength | \(h=|\det C|^{1/3}\) |
| flip/orientation reversal | \(\det C<0\) |

## Important non-equivalences

- ARA^9 is not automatically the same object as every historical nine-value packet. The Bell mapping lands on
  the nine-coefficient coupling-operator branch.
- A connected correlation is not automatically entanglement. Separable classical mixtures can retain one strong
  connected direction.
- A high relation-dominance share does not itself distinguish Bell from classical structure when local marginals
  are small. Direction count and balance carry the distinction here.
- The ARA `1.0` cells mean zero connected relation on that declared cut. They do not by themselves mean
  cancellation, resonance, stillness or missing energy.
- Q24's \(D_R\) is a normalized bookkeeping ratio, not TE-ARA and not a physical energy.

## Evidence classification

`CALIBRATED prior-geometry identification on already-open public data`.

The April/July ARA^9 geometry clearly predates Q24, but Q6 had already calculated the Bell tensors and singular
values. Q24 therefore supports faithfulness and mathematical fit, not an independent predictive hit.

## Result retained

The connected ARA^9 object returned:

```text
Bell:       3,3,3,3
classical:  1,1
uniform:    0
```

in both the raw-current linear reconstruction and the physical-state companion. Frozen result `16/16`;
independent validation `860/860`.

