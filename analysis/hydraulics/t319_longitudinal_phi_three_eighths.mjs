#!/usr/bin/env node
/**
 * T319 — longitudinal Phi-motion / 3/8-structure test.
 *
 * Implements the frozen protocol without interpolation or fitted smoothing.
 * The source workbooks are the public Dryad files from:
 *   https://doi.org/10.5061/dryad.4xgxd25hg
 *
 * The velocity workbooks repeat a source-provided depth-averaged streamwise
 * speed Us through the supplied columns us and us/Us.  We recover that same
 * source quantity algebraically as us / (us/Us) at every vertical sample and
 * use the median repeated value at each longitudinal station.  This is an
 * extraction of the authors' normalizer, not a fitted velocity model.
 */

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SOURCE = path.join(HERE, "source_bedrock_bends");
const OUTPUT_PREFIX = "T319_LONGITUDINAL_PHI_THREE_EIGHTHS";
const MATCH_TOLERANCE_M = 1e-6;
const EXACT_SEPARATION = (3 - Math.sqrt(5)) / 2 - 3 / 8;

const files = {
  plainVelocity: path.join(SOURCE, "Plain-bed-velocity.xlsx"),
  undulatingVelocity: path.join(SOURCE, "Undulating-bed-velocity.xlsx"),
  depth: path.join(SOURCE, "Water-depth.xlsx"),
  protocol: path.join(HERE, "H2_LONGITUDINAL_PHI_THREE_EIGHTHS_PROTOCOL_v2_FROZEN.md"),
};

const PHI = (1 + Math.sqrt(5)) / 2;
const candidates = {
  phi: [2 - PHI, PHI],
  three_eighths: [3 / 8, 2 - 3 / 8],
  one_third: [1 / 3, 2 - 1 / 3],
  two_fifths: [2 / 5, 2 - 2 / 5],
  half: [1 / 2, 3 / 2],
  ridge: [1],
};

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function finiteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function median(values) {
  const x = [...values].sort((a, b) => a - b);
  const m = Math.floor(x.length / 2);
  return x.length % 2 ? x[m] : (x[m - 1] + x[m]) / 2;
}

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

async function workbookValues(filePath) {
  const input = await FileBlob.load(filePath);
  const workbook = await SpreadsheetFile.importXlsx(input);
  const sheet = workbook.worksheets.getItemAt(0);
  return sheet.getUsedRange(true).values;
}

function runNameFromHeader(value) {
  if (typeof value !== "string") return null;
  const match = value.match(/\b([PU]RUN\d+)\b/i);
  return match ? match[1].toUpperCase() : null;
}

function parseVelocity(values) {
  const result = new Map();
  for (let start = 0; start < values[0].length; start += 1) {
    const run = runNameFromHeader(values[0][start]);
    if (!run) continue;
    const expected = ["distance", "z", "us", "un", "uz", "us/us", "us/u"];
    const actual = values[1].slice(start, start + 7).map((v) => String(v ?? "").toLowerCase());
    // The plain-bed workbook also labels two-column MLW-curve blocks with
    // the run name.  They are not centreline velocity blocks.
    if (!actual[0].includes(expected[0])) continue;
    assert(actual[0].includes(expected[0]), `${run}: unexpected distance header`);
    assert(actual[2].startsWith(expected[2]), `${run}: unexpected us header`);
    assert(actual[5] === expected[5], `${run}: expected source us/Us column`);

    const stationSamples = new Map();
    for (let r = 2; r < values.length; r += 1) {
      const s = values[r][start];
      const us = values[r][start + 2];
      const ratio = values[r][start + 5];
      if (!finiteNumber(s) || !finiteNumber(us) || !finiteNumber(ratio) || ratio === 0) continue;
      const key = s.toFixed(9);
      if (!stationSamples.has(key)) stationSamples.set(key, { s, estimates: [] });
      stationSamples.get(key).estimates.push(us / ratio);
    }

    const stations = [...stationSamples.values()]
      .map(({ s, estimates }) => ({
        s,
        Us: median(estimates),
        repeats: estimates.length,
        recoverySpread: Math.max(...estimates) - Math.min(...estimates),
      }))
      .sort((a, b) => a.s - b.s);
    assert(stations.length >= 3, `${run}: too few velocity stations`);
    result.set(run, stations);
  }
  return result;
}

function parseDepth(values) {
  const result = new Map();
  for (let start = 0; start < values[0].length; start += 1) {
    const run = runNameFromHeader(values[0][start]);
    if (!run) continue;
    const unitHeader = String(values[1][start + 1] ?? "").toLowerCase();
    const multiplier = unitHeader.includes("mm") ? 1e-3 : unitHeader.includes("cm") ? 1e-2 : 1;
    const sourceUnit = unitHeader.includes("mm") ? "mm" : unitHeader.includes("cm") ? "cm" : "m";
    const stations = [];
    for (let r = 2; r < values.length; r += 1) {
      const s = values[r][start];
      const rawDepth = values[r][start + 1];
      if (!finiteNumber(s) || !finiteNumber(rawDepth)) continue;
      stations.push({ s, depthM: rawDepth * multiplier, rawDepth, sourceUnit });
    }
    stations.sort((a, b) => a.s - b.s);
    assert(stations.length >= 3, `${run}: too few depth stations`);
    result.set(run, stations);
  }
  return result;
}

function nearestStation(stations, s) {
  let best = null;
  for (const station of stations) {
    const delta = Math.abs(station.s - s);
    if (!best || delta < best.delta) best = { station, delta };
  }
  return best;
}

function joinOnSharedSupport(velocity, depth) {
  const rows = [];
  for (const d of depth) {
    const nearest = nearestStation(velocity, d.s);
    if (nearest && nearest.delta <= MATCH_TOLERANCE_M) {
      rows.push({ ...nearest.station, ...d, matchDeltaM: nearest.delta });
    }
  }
  rows.sort((a, b) => a.s - b.s);
  assert(rows.length >= 3, "Too few exactly shared longitudinal stations");
  const s0 = rows[0].s;
  const s1 = rows[rows.length - 1].s;
  assert(s1 > s0, "Degenerate shared support");
  return rows.map((row) => ({ ...row, x: (2 * (row.s - s0)) / (s1 - s0) }));
}

function peakRows(rows, field) {
  const maxValue = Math.max(...rows.map((r) => r[field]));
  const tolerance = Math.max(1e-12, Math.abs(maxValue) * 1e-10);
  return rows.filter((r) => Math.abs(r[field] - maxValue) <= tolerance);
}

function localResolution(rows, peak) {
  const index = rows.indexOf(peak);
  const gaps = [];
  if (index > 0) gaps.push(peak.x - rows[index - 1].x);
  if (index + 1 < rows.length) gaps.push(rows[index + 1].x - peak.x);
  return gaps.length ? Math.max(...gaps) : Number.POSITIVE_INFINITY;
}

function candidateScore(peaks, loci) {
  let best = { distance: Number.POSITIVE_INFINITY, peakX: null, locus: null };
  for (const peak of peaks) {
    for (const locus of loci) {
      const distance = Math.abs(peak.x - locus);
      if (distance < best.distance) best = { distance, peakX: peak.x, locus };
    }
  }
  return best;
}

function winners(scores) {
  const min = Math.min(...scores.map((s) => s.distance));
  return scores.filter((s) => Math.abs(s.distance - min) <= 1e-12).map((s) => s.candidate);
}

function csvEscape(value) {
  if (value === null || value === undefined) return "";
  if (Array.isArray(value)) value = value.join("|");
  const s = String(value);
  return /[",\n\r]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

function writeCsv(filePath, rows) {
  assert(rows.length > 0, `Cannot write empty CSV ${filePath}`);
  const keys = Object.keys(rows[0]);
  const text = [keys.join(","), ...rows.map((row) => keys.map((k) => csvEscape(row[k])).join(","))].join("\n") + "\n";
  fs.writeFileSync(filePath, text, "utf8");
}

function groupMean(rows, key) {
  return rows.reduce((sum, row) => sum + row[key], 0) / rows.length;
}

const [plainValues, undulatingValues, depthValues] = await Promise.all([
  workbookValues(files.plainVelocity),
  workbookValues(files.undulatingVelocity),
  workbookValues(files.depth),
]);

const velocity = new Map([...parseVelocity(plainValues), ...parseVelocity(undulatingValues)]);
const depths = parseDepth(depthValues);
const eligibleRuns = [...depths.keys()].filter((run) => velocity.has(run)).sort();
assert(eligibleRuns.length === 7, `Expected seven paired runs, found ${eligibleRuns.length}`);

const runRows = [];
const stationRows = [];
const scoreRows = [];

for (const run of eligibleRuns) {
  const family = run.startsWith("P") ? "plain" : "undulating";
  const joined = joinOnSharedSupport(velocity.get(run), depths.get(run));
  const motionPeaks = peakRows(joined, "Us");
  const structurePeaks = peakRows(joined, "depthM");
  const motionResolution = Math.max(...motionPeaks.map((p) => localResolution(joined, p)));
  const structureResolution = Math.max(...structurePeaks.map((p) => localResolution(joined, p)));
  const exactResolutionEligible = motionResolution < EXACT_SEPARATION && structureResolution < EXACT_SEPARATION;

  for (const row of joined) {
    stationRows.push({
      run,
      family,
      s_m: row.s,
      x_ara: row.x,
      Us_m_per_s: row.Us,
      depth_m: row.depthM,
      depth_source_value: row.rawDepth,
      depth_source_unit: row.sourceUnit,
      Us_recovery_repeats: row.repeats,
      Us_recovery_spread: row.recoverySpread,
      source_match_delta_m: row.matchDeltaM,
      motion_peak: motionPeaks.includes(row) ? 1 : 0,
      structure_peak: structurePeaks.includes(row) ? 1 : 0,
    });
  }

  const motionScores = [];
  const structureScores = [];
  for (const [candidate, loci] of Object.entries(candidates)) {
    const m = candidateScore(motionPeaks, loci);
    const d = candidateScore(structurePeaks, loci);
    const mRow = { run, family, observable: "motion", candidate, ...m };
    const dRow = { run, family, observable: "structure", candidate, ...d };
    motionScores.push(mRow);
    structureScores.push(dRow);
    scoreRows.push(mRow, dRow);
  }

  const motionWinners = winners(motionScores);
  const structureWinners = winners(structureScores);
  const phiMotion = motionScores.find((r) => r.candidate === "phi");
  const eighthsStructure = structureScores.find((r) => r.candidate === "three_eighths");
  const phiStructure = structureScores.find((r) => r.candidate === "phi");
  const eighthsMotion = motionScores.find((r) => r.candidate === "three_eighths");
  const predictedPairDistance = phiMotion.distance + eighthsStructure.distance;
  const swappedPairDistance = eighthsMotion.distance + phiStructure.distance;

  runRows.push({
    run,
    family,
    shared_station_count: joined.length,
    support_s0_m: joined[0].s,
    support_s1_m: joined[joined.length - 1].s,
    motion_peak_x: motionPeaks.map((p) => p.x),
    motion_peak_s_m: motionPeaks.map((p) => p.s),
    motion_peak_Us_m_per_s: motionPeaks.map((p) => p.Us),
    structure_peak_x: structurePeaks.map((p) => p.x),
    structure_peak_s_m: structurePeaks.map((p) => p.s),
    structure_peak_depth_m: structurePeaks.map((p) => p.depthM),
    motion_local_resolution_x: motionResolution,
    structure_local_resolution_x: structureResolution,
    exact_phi_vs_three_eighths_eligible: exactResolutionEligible ? 1 : 0,
    motion_closest_candidates: motionWinners,
    structure_closest_candidates: structureWinners,
    motion_phi_distance: phiMotion.distance,
    motion_three_eighths_distance: eighthsMotion.distance,
    structure_phi_distance: phiStructure.distance,
    structure_three_eighths_distance: eighthsStructure.distance,
    predicted_pair_distance: predictedPairDistance,
    swapped_pair_distance: swappedPairDistance,
    predicted_minus_swapped: predictedPairDistance - swappedPairDistance,
    exact_run_verdict: exactResolutionEligible
      ? (motionWinners.includes("phi") && structureWinners.includes("three_eighths") ? "SUPPORTED" : "NOT_SUPPORTED")
      : "INCONCLUSIVE_RESOLUTION",
  });
}

const aggregateRows = [];
for (const family of ["plain", "undulating", "all"]) {
  const subset = scoreRows.filter((r) => family === "all" || r.family === family);
  for (const observable of ["motion", "structure"]) {
    for (const candidate of Object.keys(candidates)) {
      const rows = subset.filter((r) => r.observable === observable && r.candidate === candidate);
      aggregateRows.push({
        family,
        observable,
        candidate,
        run_count: rows.length,
        mean_absolute_distance: groupMean(rows, "distance"),
        median_absolute_distance: median(rows.map((r) => r.distance)),
        wins: runRows.filter((r) => (family === "all" || r.family === family) && (observable === "motion" ? r.motion_closest_candidates : r.structure_closest_candidates).includes(candidate)).length,
      });
    }
  }
}

const pairedSummary = ["plain", "undulating", "all"].map((family) => {
  const rows = runRows.filter((r) => family === "all" || r.family === family);
  return {
    family,
    run_count: rows.length,
    mean_predicted_pair_distance: groupMean(rows, "predicted_pair_distance"),
    mean_swapped_pair_distance: groupMean(rows, "swapped_pair_distance"),
    mean_predicted_minus_swapped: groupMean(rows, "predicted_minus_swapped"),
    predicted_pair_better_runs: rows.filter((r) => r.predicted_minus_swapped < 0).length,
    swapped_pair_better_runs: rows.filter((r) => r.predicted_minus_swapped > 0).length,
    tied_runs: rows.filter((r) => r.predicted_minus_swapped === 0).length,
    exact_resolution_eligible_runs: rows.filter((r) => r.exact_phi_vs_three_eighths_eligible === 1).length,
  };
});

const sourceHashes = {};
for (const [name, filePath] of Object.entries(files)) sourceHashes[name] = sha256(filePath);

const result = {
  test_id: "T319",
  title: "Longitudinal Phi-motion / 3/8-structure separation",
  run_date: "2026-08-02",
  frozen_protocol_sha256: sourceHashes.protocol,
  source_doi: "10.5061/dryad.4xgxd25hg",
  source_files_sha256: {
    "Plain-bed-velocity.xlsx": sourceHashes.plainVelocity,
    "Undulating-bed-velocity.xlsx": sourceHashes.undulatingVelocity,
    "Water-depth.xlsx": sourceHashes.depth,
  },
  observable_definition: {
    motion: "raw longitudinal location of maximum source-provided depth-averaged streamwise speed Us",
    structure: "raw longitudinal location of maximum centreline water depth",
    orientation: "increasing source distance from bend entry maps to ARA 0->2",
    joining: `exact source station match within ${MATCH_TOLERANCE_M} m; no interpolation`,
    Us_recovery: "median of repeated algebraic values us/(us/Us) at each station",
  },
  candidate_loci: candidates,
  phi_three_eighths_separation: EXACT_SEPARATION,
  eligible_runs: eligibleRuns,
  ineligible_runs: [{ run: "PRUN4", reason: "No matching water-depth series in the released Water-depth.xlsx workbook" }],
  exact_verdict: runRows.some((r) => r.exact_phi_vs_three_eighths_eligible === 1)
    ? "MIXED_OR_RUN_SPECIFIC"
    : "INCONCLUSIVE_RESOLUTION",
  exact_verdict_reason: runRows.some((r) => r.exact_phi_vs_three_eighths_eligible === 1)
    ? "At least one run met the preregistered resolution gate; inspect run results."
    : "No run's local raw station spacing was fine enough to distinguish 0.381966 from 0.375 on the frozen gate.",
  coarse_descriptive_result: {
    motion_phi_closest_runs: runRows.filter((r) => r.motion_closest_candidates.includes("phi")).length,
    structure_three_eighths_closest_runs: runRows.filter((r) => r.structure_closest_candidates.includes("three_eighths")).length,
    plain_pattern: "All four plain-bed runs have observed motion maxima at x=0 and structure maxima at x=5/3.",
    undulating_pattern: "The three undulating-bed runs have different observed maxima; no common Phi-motion / 3/8-structure placement appears.",
    interpretation_boundary: "These raw-grid observations do not support the declared separation, but the preregistered exact verdict remains resolution-inconclusive because all local station gaps exceed the Phi-versus-3/8 separation.",
  },
  run_results: runRows,
  candidate_aggregate: aggregateRows,
  paired_summary: pairedSummary,
};

writeCsv(path.join(HERE, `${OUTPUT_PREFIX}_STATIONS.csv`), stationRows);
writeCsv(path.join(HERE, `${OUTPUT_PREFIX}_RUNS.csv`), runRows);
writeCsv(path.join(HERE, `${OUTPUT_PREFIX}_CANDIDATE_SUMMARY.csv`), aggregateRows);
writeCsv(path.join(HERE, `${OUTPUT_PREFIX}_PAIR_SUMMARY.csv`), pairedSummary);
fs.writeFileSync(path.join(HERE, `${OUTPUT_PREFIX}_RESULTS.json`), JSON.stringify(result, null, 2) + "\n", "utf8");

console.log(JSON.stringify({
  exactVerdict: result.exact_verdict,
  runResults: runRows,
  pairedSummary,
  candidateAggregate: aggregateRows,
}, null, 2));
