"use strict";

// PN8 may inspect only candidates below each frozen power-of-ten boundary.
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const HERE = __dirname;
const PROTOCOL = path.join(HERE, "PN8_POWER_OF_TEN_PUBLIC_REVEAL_PROTOCOL.md");
const MODEL = path.join(HERE, "PN7C_FROZEN_MODELS.npz");
const OUTPUT = path.join(HERE, "PN8_BELOW_BOUNDARY_INPUTS.json");
const EXPECTED_PROTOCOL = "E6FB6D621DB98298E9D14E167EDB6345EB114199BD06DA54258C6F4D38813AE9";
const EXPECTED_MODEL = "9141AA398C6A6694C3C5F3ECA954681D4AD8091C01310D13C6703DB30668F3A2";
const EXPONENTS = [50, 100, 150, 200, 250];
const CHECKS = 64;

function sha256(filename) {
  return crypto.createHash("sha256").update(fs.readFileSync(filename)).digest("hex").toUpperCase();
}

function largestFourBelow(boundary) {
  let candidate = boundary - 1n;
  if ((candidate & 1n) === 0n) candidate -= 1n;
  const descending = [];
  let candidatesTested = 0;
  while (descending.length < 4) {
    if (!(candidate < boundary)) throw new Error("Downward-only boundary invariant failed");
    candidatesTested += 1;
    if (crypto.checkPrimeSync(candidate, { checks: CHECKS })) descending.push(candidate);
    candidate -= 2n;
  }
  const primes = descending.reverse();
  return {
    primes: primes.map(String),
    candidates_tested_below_boundary: candidatesTested,
    furthest_tested_candidate: String(candidate + 2n),
    greatest_prime_below_boundary: String(primes[3]),
    distance_from_boundary: String(boundary - primes[3]),
  };
}

function main() {
  if (sha256(PROTOCOL) !== EXPECTED_PROTOCOL) throw new Error("Protocol hash mismatch");
  if (sha256(MODEL) !== EXPECTED_MODEL) throw new Error("Frozen model hash mismatch");
  const targets = [];
  for (const exponent of EXPONENTS) {
    const boundary = 10n ** BigInt(exponent);
    const result = largestFourBelow(boundary);
    targets.push({ exponent, boundary: String(boundary), ...result });
    process.stdout.write(JSON.stringify({ exponent, ...result }, null, 2) + "\n");
  }
  const packet = {
    test_id: "PN8/BELOW-BOUNDARY-INPUTS-v1",
    protocol_sha256: EXPECTED_PROTOCOL,
    frozen_model_sha256: EXPECTED_MODEL,
    exponents: EXPONENTS,
    primality_method: {
      implementation: "Node.js crypto.checkPrimeSync (OpenSSL-backed probable-prime test)",
      checks: CHECKS,
      formal_certificate: false,
    },
    directional_barrier: {
      candidates_at_or_above_boundary_tested: 0,
      internet_target_lookup_performed_by_script: false,
      above_boundary_target_constructed: false,
    },
    targets,
    builder_sha256: sha256(__filename),
  };
  fs.writeFileSync(OUTPUT, JSON.stringify(packet, null, 2) + "\n", "utf8");
  process.stdout.write(JSON.stringify({ output: path.basename(OUTPUT), sha256: sha256(OUTPUT) }, null, 2) + "\n");
}

main();
