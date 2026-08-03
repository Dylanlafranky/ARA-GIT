import fs from "node:fs/promises";
import { Workbook } from "@oai/artifact-tool";

const csvPath = process.argv[2];
if (!csvPath) throw new Error("Usage: inspect_csv.mjs <csv-path>");

const csvText = await fs.readFile(csvPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Raw" });
const summary = await workbook.inspect({
  kind: "sheet,region",
  sheetId: "Raw",
  range: "A1:V16",
  maxChars: 12000,
  tableMaxRows: 16,
  tableMaxCols: 20,
  tableMaxCellChars: 120,
});
process.stdout.write(summary.ndjson);
