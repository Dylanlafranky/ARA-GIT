#!/usr/bin/env node
/** Independent source-level validation for T319. */

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SOURCE = path.join(HERE, "source_bedrock_bends");
const RESULT_PATH = path.join(HERE, "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_RESULTS.json");
const OUT_PATH = path.join(HERE, "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_VALIDATION.json");
const SEPARATION = (3 - Math.sqrt(5)) / 2 - 3 / 8;
const TOL = 1e-6;

function check(ok, label, detail = null) {
  return { label, pass: Boolean(ok), detail };
}

function hash(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function runName(value) {
  const m = typeof value === "string" ? value.match(/\b([PU]RUN\d+)\b/i) : null;
  return m ? m[1].toUpperCase() : null;
}

async function values(filePath) {
  const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(filePath));
  return wb.worksheets.getItemAt(0).getUsedRange(true).values;
}

function med(x) {
  x = [...x].sort((a, b) => a - b);
  const k = Math.floor(x.length / 2);
  return x.length % 2 ? x[k] : (x[k - 1] + x[k]) / 2;
}

function parseVelocity(table) {
  const out = new Map();
  for (let c = 0; c < table[0].length; c += 1) {
    const run = runName(table[0][c]);
    if (!run || !String(table[1][c] ?? "").toLowerCase().includes("distance")) continue;
    const grouped = new Map();
    for (let r = 2; r < table.length; r += 1) {
      const s = table[r][c];
      const us = table[r][c + 2];
      const ratio = table[r][c + 5];
      if (![s, us, ratio].every(Number.isFinite) || ratio === 0) continue;
      const key = s.toFixed(9);
      if (!grouped.has(key)) grouped.set(key, { s, estimates: [] });
      grouped.get(key).estimates.push(us / ratio);
    }
    out.set(run, [...grouped.values()].map((x) => ({ s: x.s, Us: med(x.estimates) })).sort((a, b) => a.s - b.s));
  }
  return out;
}

function parseDepth(table) {
  const out = new Map();
  for (let c = 0; c < table[0].length; c += 1) {
    const run = runName(table[0][c]);
    if (!run) continue;
    const unit = String(table[1][c + 1] ?? "").toLowerCase();
    const scale = unit.includes("mm") ? 1e-3 : unit.includes("cm") ? 1e-2 : 1;
    const rows = [];
    for (let r = 2; r < table.length; r += 1) {
      const s = table[r][c];
      const d = table[r][c + 1];
      if (Number.isFinite(s) && Number.isFinite(d)) rows.push({ s, depthM: d * scale });
    }
    out.set(run, rows.sort((a, b) => a.s - b.s));
  }
  return out;
}

function join(v, d) {
  const rows = [];
  for (const depth of d) {
    let nearest = v[0];
    for (const candidate of v) if (Math.abs(candidate.s - depth.s) < Math.abs(nearest.s - depth.s)) nearest = candidate;
    if (Math.abs(nearest.s - depth.s) <= TOL) rows.push({ ...nearest, ...depth });
  }
  const s0 = rows[0].s;
  const s1 = rows.at(-1).s;
  return rows.map((r) => ({ ...r, x: 2 * (r.s - s0) / (s1 - s0) }));
}

function peaks(rows, field) {
  const top = Math.max(...rows.map((r) => r[field]));
  const tol = Math.max(1e-12, Math.abs(top) * 1e-10);
  return rows.filter((r) => Math.abs(r[field] - top) <= tol);
}

function resolution(rows, p) {
  const i = rows.indexOf(p);
  const gaps = [];
  if (i > 0) gaps.push(p.x - rows[i - 1].x);
  if (i + 1 < rows.length) gaps.push(rows[i + 1].x - p.x);
  return Math.max(...gaps);
}

const sourceFiles = ["Plain-bed-velocity.xlsx", "Undulating-bed-velocity.xlsx", "Water-depth.xlsx"];
const [plain, undulating, water] = await Promise.all(sourceFiles.map((name) => values(path.join(SOURCE, name))));
const velocity = new Map([...parseVelocity(plain), ...parseVelocity(undulating)]);
const depth = parseDepth(water);
const recomputed = [];
for (const run of [...depth.keys()].filter((x) => velocity.has(x)).sort()) {
  const rows = join(velocity.get(run), depth.get(run));
  const mp = peaks(rows, "Us");
  const dp = peaks(rows, "depthM");
  recomputed.push({
    run,
    stationCount: rows.length,
    motionPeakX: mp.map((x) => x.x),
    structurePeakX: dp.map((x) => x.x),
    motionResolution: Math.max(...mp.map((x) => resolution(rows, x))),
    structureResolution: Math.max(...dp.map((x) => resolution(rows, x))),
  });
}

const reported = JSON.parse(fs.readFileSync(RESULT_PATH, "utf8"));
const checks = [];
checks.push(check(recomputed.length === 7, "seven paired runs", recomputed.map((x) => x.run)));
checks.push(check(reported.frozen_protocol_sha256.toUpperCase() === "D4E3D7ECE8A7C1ADA9568AE609C84135A6A19F0497D1E57115C4CCF59B6884AA", "frozen protocol hash unchanged"));
for (const item of recomputed) {
  const target = reported.run_results.find((r) => r.run === item.run);
  checks.push(check(Boolean(target), `${item.run} appears in reported runs`));
  if (!target) continue;
  const arraysClose = (a, b) => a.length === b.length && a.every((x, i) => Math.abs(x - b[i]) <= 1e-12);
  checks.push(check(item.stationCount === target.shared_station_count, `${item.run} shared station count`, item.stationCount));
  checks.push(check(arraysClose(item.motionPeakX, target.motion_peak_x), `${item.run} motion maximum reproduced`, item.motionPeakX));
  checks.push(check(arraysClose(item.structurePeakX, target.structure_peak_x), `${item.run} structure maximum reproduced`, item.structurePeakX));
  checks.push(check(Math.abs(item.motionResolution - target.motion_local_resolution_x) <= 1e-12, `${item.run} motion resolution reproduced`, item.motionResolution));
  checks.push(check(Math.abs(item.structureResolution - target.structure_local_resolution_x) <= 1e-12, `${item.run} structure resolution reproduced`, item.structureResolution));
  checks.push(check(item.motionResolution >= SEPARATION || item.structureResolution >= SEPARATION, `${item.run} cannot resolve Phi from 3/8`, { separation: SEPARATION, motion: item.motionResolution, structure: item.structureResolution }));
}
checks.push(check(reported.exact_verdict === "INCONCLUSIVE_RESOLUTION", "reported exact verdict follows frozen resolution gate", reported.exact_verdict));
checks.push(check(reported.source_files_sha256["Plain-bed-velocity.xlsx"] === hash(path.join(SOURCE, "Plain-bed-velocity.xlsx")), "plain source hash"));
checks.push(check(reported.source_files_sha256["Undulating-bed-velocity.xlsx"] === hash(path.join(SOURCE, "Undulating-bed-velocity.xlsx")), "undulating source hash"));
checks.push(check(reported.source_files_sha256["Water-depth.xlsx"] === hash(path.join(SOURCE, "Water-depth.xlsx")), "depth source hash"));

const validation = {
  test_id: "T319",
  validation_date: "2026-08-02",
  pass: checks.every((x) => x.pass),
  independent_recomputation: "Reloaded the three source workbooks and independently rebuilt shared stations, source Us, maxima, and local resolution without importing the analysis script.",
  checks,
  artifact_sha256: {},
};
for (const name of [
  "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_RESULTS.json",
  "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_RUNS.csv",
  "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_STATIONS.csv",
  "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_CANDIDATE_SUMMARY.csv",
  "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_PAIR_SUMMARY.csv",
  "T319_LONGITUDINAL_PHI_THREE_EIGHTHS_FIGURE.png",
]) validation.artifact_sha256[name] = hash(path.join(HERE, name));

fs.writeFileSync(OUT_PATH, JSON.stringify(validation, null, 2) + "\n", "utf8");
console.log(JSON.stringify({ pass: validation.pass, checks: checks.length, failures: checks.filter((x) => !x.pass) }, null, 2));
