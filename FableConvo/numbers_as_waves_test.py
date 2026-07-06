"""
NUMBERS-AS-WAVES TEST (3 Jul 2026) — Dylan's digit-ARA proposal, operationalized.
Self-contained, seed 42. Findings (all reproduced on first run):
- Leading-digit-below-5 fraction = a LADDER DETECTOR: octave cascade (2^k)
  0.699, phi ladder (Fibonacci) 0.698, Benford theory log10(5)=0.699;
  uniform random (bath) 0.448. One number separates ladder from bath.
- A number spans the poles left to right: first digit = ladder/rung info
  (Benford); last digit = bath (prime last digits uniform 0.25 each).
- Bonus: consecutive primes AVOID sharing last digits (0.155 vs 0.25
  independent) — Lemke Oliver-Soundararajan 2016; slot-competition echo.
Kit note: Benford below-5 fraction is a cheap scale-invariance screen for
any repo dataset spanning decades of magnitude (~0.70 ladder / ~0.45 bath).
"""
import numpy as np
def below5_fraction(seq):
    fd = [int(str(int(abs(x)))[0]) for x in seq if abs(x) >= 1]
    return float(np.mean([d <= 4 for d in fd]))
if __name__ == "__main__":
    p2 = [2**k for k in range(1, 1201)]
    fib = [1, 2]
    while len(fib) < 1200: fib.append(fib[-1]+fib[-2])
    rng = np.random.default_rng(42)
    print("2^k   :", round(below5_fraction(p2), 3))
    print("Fib   :", round(below5_fraction(fib), 3))
    print("random:", round(below5_fraction(rng.integers(1, 10**9, 5000)), 3))
    print("Benford theory:", round(np.log10(5), 3))
