import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const path = "F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/muon/data/quarknet/Clean_Lifetime_19feb21.xlsx";
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const summary = await workbook.inspect({
  kind: "workbook,sheet,table,region",
  maxChars: 16000,
  tableMaxRows: 50,
  tableMaxCols: 14,
  tableMaxCellChars: 200,
});
process.stdout.write(summary.ndjson);
