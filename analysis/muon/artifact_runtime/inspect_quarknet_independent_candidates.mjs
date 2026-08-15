import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const path = "F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/muon/data/quarknet/Clean_Lifetime_19feb21.xlsx";
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
for (const range of ["A45:M90", "A91:M130", "A131:M158"]) {
  const result = await workbook.inspect({
    kind: "region",
    sheetId: "Sheet1",
    range,
    maxChars: 18000,
    tableMaxRows: 60,
    tableMaxCols: 13,
    tableMaxCellChars: 180,
  });
  process.stdout.write(result.ndjson + "\n");
}
