/**
 * Fast streaming extractor for Q53.
 *
 * This is a compiled-runtime equivalent of the frozen Python reconstruction.
 * It reads only recorded ray/photon pairs and writes fixed-width external
 * centreline events for the three predeclared qutrit sphere cuts.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import readline from "node:readline";

const SOURCE =
  "F:\\SystemFormulaFolder\\external_data\\quantum\\eth_single_ion_contextuality_2017\\ExpDataYuOh.csv";
const OUT =
  "F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\quantum";
const EXPECTED_SHA =
  "5410775C307EDEA9F68E95133CF0A733B6CD34E7D9D774B6509472FACE74D55D";
const PLANE_NAMES = ["psi0_psi1", "psi1_psi2", "psi2_psi0"];
const EPS = 1e-12;
const INCONSISTENCY_EPS = 1e-10;
const RECORD_BYTES = 64;

const rawRays = [
  [0, 1, -1],
  [-1, 0, 1],
  [1, -1, 0],
  [0, 1, 1],
  [1, 0, 1],
  [1, 1, 0],
  [-1, 1, 1],
  [1, -1, 1],
  [1, 1, -1],
  [1, 1, 1],
  [1, 0, 0],
  [0, 1, 0],
  [0, 0, 1],
];
const RAYS = rawRays.map((r) => {
  const n = Math.hypot(r[0], r[1], r[2]);
  return [r[0] / n, r[1] / n, r[2] / n];
});

async function sha256(path) {
  const hash = crypto.createHash("sha256");
  const stream = fs.createReadStream(path);
  for await (const chunk of stream) hash.update(chunk);
  return hash.digest("hex").toUpperCase();
}

function firstNonzeroPositive(x, y, z) {
  if (Math.abs(x) > EPS) return x > 0;
  if (Math.abs(y) > EPS) return y > 0;
  if (Math.abs(z) > EPS) return z > 0;
  return true;
}

function solveSymmetric3(a, b, c, d, e, f, y0, y1, y2) {
  const det =
    a * (d * f - e * e) -
    b * (b * f - c * e) +
    c * (b * e - c * d);
  const scale = Math.max(
    Math.abs(a),
    Math.abs(b),
    Math.abs(c),
    Math.abs(d),
    Math.abs(e),
    Math.abs(f),
    1,
  );
  if (!Number.isFinite(det) || Math.abs(det) <= 1e-12 * scale ** 3)
    return null;
  const dx =
    y0 * (d * f - e * e) -
    b * (y1 * f - e * y2) +
    c * (y1 * e - d * y2);
  const dy =
    a * (y1 * f - e * y2) -
    y0 * (b * f - c * e) +
    c * (b * y2 - y1 * c);
  const dz =
    a * (d * y2 - y1 * e) -
    b * (b * y2 - y1 * c) +
    y0 * (b * e - d * c);
  return [dx / det, dy / det, dz / det];
}

function median(values) {
  values.sort((a, b) => a - b);
  const n = values.length;
  return n % 2
    ? values[Math.floor(n / 2)]
    : 0.5 * (values[n / 2 - 1] + values[n / 2]);
}

class EventWriter {
  constructor(path) {
    this.fd = fs.openSync(path, "w");
    this.capacity = 65536;
    this.buffer = Buffer.allocUnsafe(this.capacity * RECORD_BYTES);
    this.used = 0;
    this.count = 0;
  }

  write(values) {
    const offset = this.used * RECORD_BYTES;
    this.buffer.writeBigInt64LE(BigInt(values[0]), offset);
    for (let i = 1; i < 8; i++)
      this.buffer.writeDoubleLE(values[i], offset + 8 * i);
    this.used++;
    this.count++;
    if (this.used === this.capacity) this.flush();
  }

  flush() {
    if (!this.used) return;
    fs.writeSync(this.fd, this.buffer, 0, this.used * RECORD_BYTES);
    this.used = 0;
  }

  close() {
    this.flush();
    fs.closeSync(this.fd);
  }
}

class PlaneTracker {
  constructor(path) {
    this.writer = new EventWriter(path);
    this.points = [];
    this.lastCircles = [];
    this.completeCircuits = 0;
    this.shortCircuits = 0;
    this.singularFits = 0;
    this.reset();
  }

  reset() {
    this.points.length = 0;
    this.startIndex = -1;
    this.startQ = null;
    this.lastQ = null;
    this.direction = 0;
    this.transitions = 0;
    this.lastCircles.length = 0;
  }

  begin(q, u, v, index) {
    this.points.length = 0;
    this.points.push([u, v]);
    this.startIndex = index;
    this.startQ = q;
    this.lastQ = q;
    this.direction = 0;
    this.transitions = 0;
  }

  quadrant(u, v) {
    return v >= 0 ? (u >= 0 ? 0 : 1) : u >= 0 ? 3 : 2;
  }

  add(u, v, index) {
    const boundary = Math.abs(u) <= EPS || Math.abs(v) <= EPS;
    if (this.lastQ === null) {
      if (boundary) return;
      this.begin(this.quadrant(u, v), u, v, index);
      return;
    }
    this.points.push([u, v]);
    if (boundary) return;
    const q = this.quadrant(u, v);
    if (q === this.lastQ) return;
    const diff = (q - this.lastQ + 4) % 4;
    const step = diff === 1 ? 1 : diff === 3 ? -1 : 0;
    if (step === 0) {
      this.begin(q, u, v, index);
      return;
    }
    if (this.direction === 0) {
      this.direction = step;
      this.transitions = 1;
      this.lastQ = q;
      return;
    }
    if (step !== this.direction) {
      this.begin(q, u, v, index);
      return;
    }
    this.transitions++;
    this.lastQ = q;
    if (this.transitions >= 4 && q === this.startQ) {
      this.finish(index);
      this.begin(q, u, v, index);
    }
  }

  finish(endIndex) {
    this.completeCircuits++;
    if (this.points.length < 6) {
      this.shortCircuits++;
      this.lastCircles.length = 0;
      return;
    }
    const fit = this.fit(endIndex);
    if (fit === null) {
      this.singularFits++;
      this.lastCircles.length = 0;
      return;
    }
    this.lastCircles.push(fit);
    if (this.lastCircles.length > 3) this.lastCircles.shift();
    if (this.lastCircles.length === 3) this.event();
  }

  fit(endIndex) {
    const n = this.points.length;
    let su = 0,
      sv = 0,
      suu = 0,
      svv = 0,
      suv = 0,
      yub = 0,
      yvb = 0,
      sb = 0;
    let minU = Infinity,
      maxU = -Infinity,
      minV = Infinity,
      maxV = -Infinity;
    for (const [u, v] of this.points) {
      const rr = u * u + v * v;
      su += u;
      sv += v;
      suu += u * u;
      svv += v * v;
      suv += u * v;
      yub += 2 * u * rr;
      yvb += 2 * v * rr;
      sb += rr;
      minU = Math.min(minU, u);
      maxU = Math.max(maxU, u);
      minV = Math.min(minV, v);
      maxV = Math.max(maxV, v);
    }
    const solution = solveSymmetric3(
      4 * suu,
      4 * suv,
      2 * su,
      4 * svv,
      2 * sv,
      n,
      yub,
      yvb,
      sb,
    );
    if (solution === null) return null;
    const [cu, cv, k] = solution;
    const radius2 = k + cu * cu + cv * cv;
    if (!Number.isFinite(radius2) || radius2 <= EPS) return null;
    const radius = Math.sqrt(radius2);
    const residuals = this.points.map(
      ([u, v]) => Math.abs(Math.hypot(u - cu, v - cv) - radius) / radius,
    );
    return {
      start: this.startIndex,
      end: endIndex,
      circleU: cu,
      circleV: cv,
      centroidU: su / n,
      centroidV: sv / n,
      extremaU: 0.5 * (minU + maxU),
      extremaV: 0.5 * (minV + maxV),
      radius,
      residual: median(residuals),
    };
  }

  headingStrength(du, dv, meanRadius) {
    const strength = Math.hypot(du, dv) / meanRadius;
    if (strength <= EPS) return [NaN, strength];
    let heading = Math.atan2(dv, du) / (2 * Math.PI);
    heading -= Math.floor(heading);
    return [heading, strength];
  }

  event() {
    const [previous, current, following] = this.lastCircles;
    const meanRadius =
      (previous.radius + current.radius + following.radius) / 3;
    if (meanRadius <= EPS) return;
    const [ch, cs] = this.headingStrength(
      following.circleU - previous.circleU,
      following.circleV - previous.circleV,
      meanRadius,
    );
    const [mh, ms] = this.headingStrength(
      following.centroidU - previous.centroidU,
      following.centroidV - previous.centroidV,
      meanRadius,
    );
    const [eh, es] = this.headingStrength(
      following.extremaU - previous.extremaU,
      following.extremaV - previous.extremaV,
      meanRadius,
    );
    this.writer.write([
      Math.floor((current.start + current.end) / 2),
      current.residual,
      ch,
      cs,
      mh,
      ms,
      eh,
      es,
    ]);
  }

  close() {
    this.writer.close();
  }
}

function forEachInt(line, callback) {
  let field = 0;
  let value = 0;
  let sign = 1;
  let have = false;
  for (let i = 0; i <= line.length; i++) {
    const code = i < line.length ? line.charCodeAt(i) : 44;
    if (code >= 48 && code <= 57) {
      value = value * 10 + (code - 48);
      have = true;
    } else if (code === 45) {
      sign = -1;
    } else if (code === 44 && have) {
      callback(field++, sign * value);
      value = 0;
      sign = 1;
      have = false;
    }
  }
}

const hash = await sha256(SOURCE);
if (hash !== EXPECTED_SHA) throw new Error(`Source hash mismatch: ${hash}`);

const trackers = PLANE_NAMES.map(
  (name) =>
    new PlaneTracker(
      `${OUT}\\Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_${name}.bin`,
    ),
);
let physicalRows = 0;
let validRows = 0;
let omittedRows = 0;
let measurements = 0;
let inconsistencies = 0;
let unitFailures = 0;
let known = false;
let firstValidRow = true;
let sx = 0,
  sy = 0,
  sz = 0;
const started = performance.now();

const input = readline.createInterface({
  input: fs.createReadStream(SOURCE, { highWaterMark: 1 << 20 }),
  crlfDelay: Infinity,
});

for await (const line of input) {
  physicalRows++;
  if (!line.length) continue;
  if (line[0] === "o") {
    omittedRows++;
    continue;
  }
  validRows++;
  const analyzeRow = !firstValidRow;
  let rayLabel = 0;
  forEachInt(line, (field, value) => {
    if ((field & 1) === 0) {
      rayLabel = value;
      return;
    }
    const photons = value;
    measurements++;
    let [rx, ry, rz] = RAYS[rayLabel - 1];
    if (photons >= 6) {
      if (known) {
        const dot = sx * rx + sy * ry + sz * rz;
        if (
          dot < -EPS ||
          (Math.abs(dot) <= EPS && !firstNonzeroPositive(rx, ry, rz))
        ) {
          rx = -rx;
          ry = -ry;
          rz = -rz;
        }
      } else if (!firstNonzeroPositive(rx, ry, rz)) {
        rx = -rx;
        ry = -ry;
        rz = -rz;
      }
      sx = rx;
      sy = ry;
      sz = rz;
      known = true;
    } else if (known) {
      const dot = sx * rx + sy * ry + sz * rz;
      const nx = sx - dot * rx;
      const ny = sy - dot * ry;
      const nz = sz - dot * rz;
      const norm = Math.hypot(nx, ny, nz);
      if (norm <= INCONSISTENCY_EPS) {
        inconsistencies++;
        known = false;
        for (const tracker of trackers) tracker.reset();
        return;
      }
      sx = nx / norm;
      sy = ny / norm;
      sz = nz / norm;
    }
    if (analyzeRow && known) {
      const norm2 = sx * sx + sy * sy + sz * sz;
      if (Math.abs(norm2 - 1) > 1e-9) unitFailures++;
      trackers[0].add(sx, sy, measurements);
      trackers[1].add(sy, sz, measurements);
      trackers[2].add(sz, sx, measurements);
    }
  });
  firstValidRow = false;
  if (validRows % 5000 === 0) {
    const elapsed = (performance.now() - started) / 1000;
    console.log(
      `rows=${validRows.toLocaleString()} measurements=${measurements.toLocaleString()} elapsed=${elapsed.toFixed(1)}s`,
    );
  }
}

for (const tracker of trackers) tracker.close();
const extraction = Object.fromEntries(
  PLANE_NAMES.map((name, index) => [
    name,
    {
      complete_circuits: trackers[index].completeCircuits,
      short_circuits: trackers[index].shortCircuits,
      singular_fits: trackers[index].singularFits,
      external_events: trackers[index].writer.count,
    },
  ]),
);
const metadata = {
  source: SOURCE,
  sha256: hash,
  physical_rows: physicalRows,
  valid_rows: validRows,
  omitted_rows: omittedRows,
  measurements,
  reconstruction_inconsistencies: inconsistencies,
  unit_norm_failures: unitFailures,
  elapsed_seconds: (performance.now() - started) / 1000,
  extraction,
};
fs.writeFileSync(
  `${OUT}\\Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EXTRACTION.json`,
  JSON.stringify(metadata, null, 2),
  "utf8",
);
console.log(JSON.stringify(metadata, null, 2));

