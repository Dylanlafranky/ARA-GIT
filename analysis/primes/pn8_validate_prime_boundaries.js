"use strict";

// Post-reveal independent probable-prime and boundary scan for PN8.
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const HERE = __dirname;
const INPUTS = path.join(HERE, "PN8_BELOW_BOUNDARY_INPUTS.json");
const REVEAL = path.join(HERE, "PN8_PUBLIC_REVEAL_SOURCE.json");
const OUTPUT = path.join(HERE, "PN8_PRIME_BOUNDARY_VALIDATION.json");
const EXPECTED_INPUTS = "327E14D1CEF9EE4770889D565DEE2C36B41FF078204FFE3574166F887FFFD7FC";
const EXPECTED_REVEAL = "E73183E4573D426CA2E8D874E1BD64054DDA5758335879EE68B3C39595C85004";
const CHECKS = 96;

function sha256(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex").toUpperCase();
}

function prime(value) {
  return crypto.checkPrimeSync(value, { checks: CHECKS });
}

function noPrimeStrictlyBetween(left, right) {
  let candidate = left + 2n;
  while (candidate < right) {
    if (prime(candidate)) return { passed: false, unexpected_prime: String(candidate) };
    candidate += 2n;
  }
  return { passed: true, unexpected_prime: null };
}

function main() {
  if (sha256(INPUTS) !== EXPECTED_INPUTS) throw new Error("Input hash mismatch");
  if (sha256(REVEAL) !== EXPECTED_REVEAL) throw new Error("Reveal hash mismatch");
  const inputs = JSON.parse(fs.readFileSync(INPUTS, "utf8"));
  const reveals = JSON.parse(fs.readFileSync(REVEAL, "utf8"));
  const revealByExponent = new Map(reveals.reveals.map(row => [row.exponent, row]));
  const checks = [];
  for (const target of inputs.targets) {
    const exponent = target.exponent;
    const boundary = BigInt(target.boundary);
    const known = target.primes.map(BigInt);
    const revealed = revealByExponent.get(exponent);
    const nextPrime = BigInt(revealed.first_prime_above_boundary);
    for (let index = 0; index < known.length; index += 1) {
      checks.push({name:`n${exponent}_known_prime_${index}`, passed:prime(known[index]), value:String(known[index])});
    }
    for (let index = 0; index < known.length - 1; index += 1) {
      const between = noPrimeStrictlyBetween(known[index], known[index + 1]);
      checks.push({name:`n${exponent}_known_pair_${index}_consecutive`, ...between});
    }
    const belowBoundary = noPrimeStrictlyBetween(known[3], boundary + 1n);
    checks.push({name:`n${exponent}_greatest_prime_below_boundary`, ...belowBoundary});
    checks.push({name:`n${exponent}_revealed_target_prime`, passed:prime(nextPrime), value:String(nextPrime)});
    const aboveBoundary = noPrimeStrictlyBetween(boundary - 1n, nextPrime);
    checks.push({name:`n${exponent}_first_prime_above_boundary`, ...aboveBoundary});
  }
  const packet = {
    test_id: "PN8/PRIME-BOUNDARY-VALIDATION-v1",
    method: "Node.js crypto.checkPrimeSync with 96 checks plus exhaustive odd-candidate scans inside every local interval",
    formal_primality_certificates: false,
    checks_total: checks.length,
    checks_passed: checks.filter(row => row.passed).length,
    all_passed: checks.every(row => row.passed),
    checks,
    validator_sha256: sha256(__filename),
  };
  fs.writeFileSync(OUTPUT, JSON.stringify(packet, null, 2) + "\n", "utf8");
  process.stdout.write(JSON.stringify({checks_total:packet.checks_total, checks_passed:packet.checks_passed, all_passed:packet.all_passed}, null, 2) + "\n");
  if (!packet.all_passed) process.exitCode = 1;
}

main();
