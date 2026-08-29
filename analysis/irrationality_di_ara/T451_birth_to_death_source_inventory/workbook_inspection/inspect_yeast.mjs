import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const source = "F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/irrationality_di_ara/T451_birth_to_death_source_inventory/source/yeast/supplementary/pone.0167394.s005.xlsx";
const input = await FileBlob.load(source);
const workbook = await SpreadsheetFile.importXlsx(input);

const overview = await workbook.inspect({
  kind: "workbook,sheet,table,region",
  maxChars: 18000,
  tableMaxRows: 8,
  tableMaxCols: 10,
  tableMaxCellChars: 80,
});

console.log(overview.ndjson);

for (const sheetName of ["Table c", "Table d", "Table e"]) {
  const sheet = workbook.worksheets.getItem(sheetName);
  console.log(JSON.stringify({ sheet: sheetName, tail: sheet.getRange("A25:J35").values }));
}

const alignedSheets = ["Table c", "Table d", "Table e"].map((name) =>
  workbook.worksheets.getItem(name).getRange("B3:DC35").values,
);
const cellSummaries = [];
for (let col = 0; col < 106; col += 1) {
  const counts = alignedSheets.map((matrix) => matrix.reduce((n, row) => n + (typeof row[col] === "number" && Number.isFinite(row[col]) ? 1 : 0), 0));
  const internalGaps = alignedSheets.map((matrix) => {
    const occupied = matrix.map((row) => typeof row[col] === "number" && Number.isFinite(row[col]));
    const last = occupied.lastIndexOf(true);
    return last < 0 ? 0 : occupied.slice(0, last + 1).filter((x) => !x).length;
  });
  cellSummaries.push({ counts, internalGaps });
}
console.log(JSON.stringify({
  alignedCells: cellSummaries.length,
  allThreeCountsMatch: cellSummaries.filter((x) => x.counts[0] === x.counts[1] && x.counts[1] === x.counts[2]).length,
  noInternalGapsAllThree: cellSummaries.filter((x) => x.internalGaps.every((n) => n === 0)).length,
  minObservedGenerations: Math.min(...cellSummaries.map((x) => x.counts[0])),
  maxObservedGenerations: Math.max(...cellSummaries.map((x) => x.counts[0])),
}));
