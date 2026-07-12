# MX3g great-grandchild and resolution-floor result

**Tier:** DEVELOPMENT / SAME INSPECTED ARCHIVE  
**Predeclared sequence:** k20 -> k40 -> k80  
**Grid:** 256 cells; Nyquist mode k=128

## Resolution geometry

- k40: 6.40 samples per wavelength;
- k80: 3.20 samples per wavelength;
- next doubling k160: beyond Nyquist and not representable.

## Generation results

- 20_to_40: 6/8 gates; field lag 54 slices; phase R=0.2945, p=0.0020; field/particle bicoherence=0.1873/0.2480; TE corr=0.9667.
- 40_to_80: not jointly detectable; 1/2 gates.

## Exploratory flip

{
  "testable": false
}

The flip calculation is descriptive only. A phase-closure sign change was not fixed as the physical ARA singularity
observable before inspection, and k80 is marginally resolved. No flip claim may be promoted from this archive.

## Verdict

k40 is a detectable fine identity candidate but not a clean k20+k20 self-coupled descendant. It passes
6/8 gates: field and particle onsets are ordered after k20, amplitude SNR
is 14.84, it persists 29 slices, and field/particle TE
correlation is 0.9667. But post-onset phase concentration is only
0.2945, and exact-ridge k20+k20 bicoherence ranks at only the
0.20/0.40 field/particle route percentiles.

The strongest k40 routes are
6+34 in the field and
19+21 in particles. The near-ridge 19+21 route is among the strongest,
while exact 20+20 is weak. The fine identity is therefore web-generated rather than a clean binary doubling.

k80 crosses the field threshold but never the particle threshold. At 3.2 samples per wavelength it does not qualify
as an independently recovered identity. The descent reaches the operational floor between k40 and k80. Since k80
never becomes jointly eligible, no physical phase flip is testable; k160 is also beyond the grid Nyquist limit.

**Status:** `K40 WEAK WEB-GENERATED IDENTITY 6/8 / K80 FIELD-ONLY FLOOR / FLIP NOT TESTABLE`.

## Fences

- k80 has only 3.2 samples per wavelength and is vulnerable to grid/deposition artifacts.
- k160 cannot exist as a resolved mode on this grid; this is a hard numerical floor, not automatically a physical
  singularity or universal rung flip.
- Fine-mode identity requires field/particle agreement, phase inheritance, route bicoherence and noise convergence;
  amplitude alone does not count.
