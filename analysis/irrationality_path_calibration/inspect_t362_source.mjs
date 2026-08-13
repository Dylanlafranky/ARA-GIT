import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const source = "F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/irrationality_path_calibration/T362_SOURCE_Acosta_2019_Figure1Data.xlsx";
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(source));

const sheets = await workbook.inspect({
  kind: "sheet",
  include: "id,name",
  maxChars: 12000,
});
process.stdout.write(`${sheets.ndjson}\n`);

const names = ["Fig1a", "Fig1b", "Fig1c", "Fig1d", "Fig1e", "Fig1f"];
for (const name of names) {
  try {
    const region = await workbook.inspect({
      kind: "region",
      sheetId: name,
      range: "A1:L24",
      maxChars: 12000,
    });
    process.stdout.write(`\n=== ${name} ===\n${region.ndjson}\n`);
  } catch (error) {
    process.stdout.write(`\n=== ${name} ERROR ===\n${String(error)}\n`);
  }
}
