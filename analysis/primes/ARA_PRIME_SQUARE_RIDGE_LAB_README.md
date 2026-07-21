# ARA Prime Music-Box Resonance Lab

**Date:** 21 July 2026  
**Artifact class:** interactive exact crosswalk and teaching instrument  
**Mathematical engine:** postponed/incremental Sieve of Eratosthenes  
**ARA reading:** prime-child activation, collision multiplicity, factor-diameter closure, recurrent resonance, and
an audible child-wave scale

## What the instrument does

The lab generates every prime through `5,000` exactly while showing the calculation as accumulating prime-child
periods. For each prime `p`, its first independently necessary composite strike is scheduled at `p^2`; later strikes
occur at `p^2+p`, `p^2+2p`, and so on. A node reached by one or more active children is composite. A quiet node is
prime and registers another child.

"Independently necessary" is loadbearing. Multiples such as `2p` and `3p` can occur below `p^2`, but smaller primes
have already marked them. The `p` lane adds new sieve information only from `p^2` onward. In ARA language, `p^2` is
the child's activation boundary at this measurement grain, not its first arithmetic multiple.

## The two exact ridge coordinates

PN10 defined the factor-diameter coordinate

\[
x_n(d)=\frac{2\log d}{\log n}.
\]

At `n=p^2`, factor `p` meets its reflection:

\[
x_{p^2}(p)=1.
\]

That is the **square ridge**: one child is self-reflected at the factor midpoint.

A different event occurs when several children first synchronize and collectively exhaust the declared parent:

\[
n=\prod_{p\in P}p=\operatorname{lcm}(P),
\qquad
\sum_{p\in P}x_n(p)=2.
\]

That is a **fundamental resonance**. Later multiples of the same child product are **harmonic repeats** unless an
additional active child joins and the enlarged set again multiplies exactly to the node.

## Visual categories

- **Quiet / prime:** no active child schedule reaches the node.
- **Ordinary child collision:** one or more children strike, without square or collective full closure.
- **Square ridge:** `n=p^2`; the newly independent child occupies factor position `1.0`.
- **Fundamental resonance:** at least three active children strike and their distinct product equals `n`.
- **Harmonic repeat:** the same three-or-more-child phase set strikes again at a multiple of its fundamental product.
- **Primorial rung:** the special fundamental sequence using consecutive primes from 2: `30`, `210`, `2,310`,
  `30,030`, and onward.
- **Not scanned:** the exact sieve has not yet advanced to the displayed node.

The categories are deliberately separate. Collision count alone does not establish either a square ridge or full
resonance closure.

## Music-box mapping

Each active prime-child lane receives the next note of an ascending C-major scale. The assignment is permanent for
the instrument rather than recalculated for the currently visible window:

`p=2 -> C4`, `3 -> D4`, `5 -> E4`, `7 -> F4`, `11 -> G4`, `13 -> A4`, `17 -> B4`, `19 -> C5`, and onward.

Because only children with `p^2 <= 5,000` can become active here, the audible range ends at `p=67 -> G6`. Quiet
prime nodes are rests. Composite nodes sound the notes of the children that actually strike them, ordered upward as
a short music-box arpeggio. Consequently, node 510 sounds `C4-D4-E4-B4`, matching children `2,3,5,17` exactly.

The checked **Music box** switch enables sound. Browsers require a user action before audio begins, so Play, Step,
Go, or selecting a number supplies that action. This sonification is a representation of the exact collision web;
musical consonance is not being used as mathematical evidence.

## What each view shows

### Number-line scan

The current interval is coloured by the categories above. Selection changes the detailed factor view without
pretending a future node has already been generated.

### Fundamental resonance ladder

The ladder shows the consecutive-prime primorial closures:

- `30 = 2*3*5` -- first 3-child closure;
- `210 = 2*3*5*7` -- first 4-child closure;
- `2,310 = 2*3*5*7*11` -- first 5-child closure;
- `30,030 = 2*3*5*7*11*13` -- next rung, outside the instrument's current range.

### Prime child waves

Each lane is one prime period and carries its permanent note label. Ordinary strikes are small circles, square
activations are diamonds, fundamental resonances are filled circles, harmonic repeats are rings, and primorial
closures are squares. A resonance label states its child order, such as `R4` for four-child closure.

### Selected-node factor diameter

The `0-2` diameter places factor `1` at `0`, `sqrt(n)` at `1`, and `n` at `2`. The view shows each active child,
its reflected factor, its exact ARA position, and its role at the selected node.

## Worked landmarks

- `49=7^2`: child 7 makes its first independent strike at factor position `1.0`.
- `50`: children 2 and 5 strike together; this is an ordinary two-voice collision.
- `510=2*3*5*17`: four child periods phase-lock for the first time as this exact set. Their ARA positions sum to
  `2`; this is a fundamental four-child resonance, not a square ridge.
- `1,020=2*510`: the same four-child set aligns again, so this is a harmonic repeat of 510.
- `3,570=2*3*5*7*17`: child 7 joins the 510 family and produces a new five-child fundamental closure.
- `4,620=2*(2*3*5*7*11)`: five children synchronize, but their distinct product is 2,310, so this is a harmonic
  repeat rather than a new full closure.

## Exactness and limitation

The browser engine was independently reconstructed in Python and compared with a conventional sieve through
`5,000`:

- `669` primes recovered with zero classification errors;
- every active collision voice matched a true prime divisor not exceeding `sqrt(n)`;
- every child began its independent schedule at `p^2`;
- every checked prime square landed at ARA `1.0`;
- reflected factor closure had maximum floating-point error `4.44e-16`;
- first fundamental closures were exactly `30`, `210`, and `2,310` for orders 3, 4, and 5;
- 510, 1,020, 3,570, and 4,620 received the intended fundamental/repeat classifications;
- active child notes rise strictly through the declared C-major mapping;
- the 510 event chord is exactly `C4-D4-E4-B4`.

All `24/24` checks pass. The default 510 view was rendered headlessly and visually inspected.

This is an exact ARA representation of established modular, factor, least-common-multiple, primorial, and sieve
structure. It is not a new faster prime algorithm or a new prime theorem. Its added value is the coordinated view of
child activation, recurrent phase alignment, collective closure, and factor reflection in one instrument.

## Files

- `ARA_PRIME_SQUARE_RIDGE_LAB.html` -- standalone interactive instrument (filename retained for compatibility)
- `ARA_PRIME_MUSIC_BOX_LAB_RENDER.png` -- rendered QA view at 510
- `validate_ara_prime_square_ridge_lab.py` -- independent mathematical and artifact validator
- `ARA_PRIME_SQUARE_RIDGE_LAB_VALIDATION.json` -- 24-check validation receipt
- `FableConvo/NOTE_PRIME_510_RESONANCE_RIDGE_2026-07-21.md` -- derivation of the 510 crosswalk
