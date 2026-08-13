const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { marked } = require('marked');
const { chromium } = require('playwright');
const katex = require('katex');

const ROOT = __dirname;
const INPUT = path.join(ROOT, 'ARA_PAPER_V2_MANUSCRIPT.md');
const HTML_DIR = path.join(ROOT, 'output', 'html');
const PDF_DIR = path.join(ROOT, 'output', 'pdf');
const TMP_DIR = path.join(ROOT, 'tmp', 'pdfs');
const HTML_OUT = path.join(HTML_DIR, 'ARA_Geometric_Relational_Framework_V2_DRAFT.html');
const PDF_OUT = path.join(PDF_DIR, 'ARA_Geometric_Relational_Framework_V2_DRAFT.pdf');

for (const dir of [HTML_DIR, PDF_DIR, TMP_DIR]) fs.mkdirSync(dir, { recursive: true });
const katexDist = path.dirname(require.resolve('katex/dist/katex.min.css'));
fs.cpSync(path.join(katexDist, 'fonts'), path.join(HTML_DIR, 'fonts'), { recursive: true });
const katexCss = fs.readFileSync(path.join(katexDist, 'katex.min.css'), 'utf8');

let markdown = fs.readFileSync(INPUT, 'utf8');
const displayMath = [];
const inlineMath = [];

markdown = markdown.replace(/\\\[([\s\S]*?)\\\]/g, (_, tex) => {
  const id = displayMath.push(tex.trim()) - 1;
  return `\n\nARA_DISPLAY_MATH_${id}_TOKEN\n\n`;
});

markdown = markdown.replace(/\$([^$\n]+?)\$/g, (_, tex) => {
  const id = inlineMath.push(tex.trim()) - 1;
  return `ARA_INLINE_MATH_${id}_TOKEN`;
});

marked.use({ gfm: true, breaks: false });
let body = marked.parse(markdown);

for (let i = 0; i < displayMath.length; i += 1) {
  const token = `ARA_DISPLAY_MATH_${i}_TOKEN`;
  const rendered = katex.renderToString(displayMath[i], {
    displayMode: true,
    throwOnError: false,
    strict: false,
  });
  const node = `<div class="math-display">${rendered}</div>`;
  body = body.replace(`<p>${token}</p>`, node).replace(token, node);
}

for (let i = 0; i < inlineMath.length; i += 1) {
  const token = `ARA_INLINE_MATH_${i}_TOKEN`;
  const rendered = katex.renderToString(inlineMath[i], {
    displayMode: false,
    throwOnError: false,
    strict: false,
  });
  body = body.replaceAll(token, `<span class="math-inline">${rendered}</span>`);
}

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Accumulation–Release Asymmetry — A Geometric Relational Framework</title>
<style>
  ${katexCss}
  @page { size: A4; margin: 22mm 19mm 22mm 19mm; }
  :root { --ink: #17202b; --muted: #536273; --accent: #145da0; --rule: #b8c4d0; --soft: #eef4f8; }
  * { box-sizing: border-box; }
  html { font-size: 10.7pt; }
  body { color: var(--ink); font-family: Georgia, 'Times New Roman', serif; line-height: 1.46; margin: 0; }
  h1, h2, h3, h4 { color: #102b46; font-family: Arial, Helvetica, sans-serif; line-height: 1.18; break-after: avoid; }
  h1 { font-size: 29pt; margin: 37mm 0 4mm; letter-spacing: -0.6px; }
  h1 + h2 { color: var(--accent); font-size: 17pt; font-weight: 500; margin: 0 0 14mm; break-before: auto; border: 0; }
  h2 { font-size: 18pt; margin: 0 0 7mm; padding-bottom: 2.5mm; border-bottom: 1.4px solid var(--accent); break-before: page; }
  h3 { font-size: 13.4pt; margin: 8mm 0 3mm; }
  h4 { font-size: 11.4pt; margin: 6mm 0 2mm; }
  p { margin: 0 0 3.4mm; orphans: 3; widows: 3; }
  strong { color: #102b46; }
  a { color: #145da0; text-decoration: none; overflow-wrap: anywhere; }
  hr { border: 0; border-top: 1px solid var(--rule); margin: 10mm 0; }
  ul, ol { margin: 2mm 0 4mm 7mm; padding-left: 5mm; }
  li { margin: 1.2mm 0; break-inside: avoid; }
  blockquote { margin: 4mm 0; padding: 3mm 5mm; border-left: 3px solid var(--accent); background: var(--soft); color: #27384a; }
  code { font-family: 'Cascadia Mono', Consolas, monospace; font-size: 8.7pt; color: #7a2c20; overflow-wrap: anywhere; }
  pre { white-space: pre-wrap; background: #f6f8fa; border: 1px solid #d7dee5; padding: 3mm; break-inside: avoid; }
  table { width: 100%; border-collapse: collapse; margin: 4mm 0 6mm; font-size: 8.15pt; line-height: 1.28; break-inside: auto; }
  thead { display: table-header-group; }
  tr { break-inside: avoid; }
  th { background: #dce9f3; color: #102b46; font-family: Arial, Helvetica, sans-serif; text-align: left; }
  th, td { border: 0.65px solid #aebbc7; padding: 1.8mm 2mm; vertical-align: top; }
  .math-display { margin: 3.5mm 0 5mm; text-align: center; overflow: hidden; break-inside: avoid; }
  .math-display .katex { font-size: 1.04em; }
  .math-inline { white-space: nowrap; }
  .katex-display { margin: 0; }
  body > p:nth-of-type(1) { font-size: 12pt; }
  body > p:nth-of-type(2), body > p:nth-of-type(3), body > p:nth-of-type(4) { color: var(--muted); }
  h1 ~ hr:first-of-type { margin-top: 24mm; }
  @media print {
    a { color: #174d78; }
    h2, h3, h4 { break-after: avoid-page; }
  }
</style>
</head>
<body>
${body}
</body>
</html>`;

fs.writeFileSync(HTML_OUT, html, 'utf8');

(async () => {
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  const browser = await chromium.launch({ headless: true, executablePath: edgePath });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  await page.goto(pathToFileURL(HTML_OUT).href, { waitUntil: 'load', timeout: 120000 });
  await page.emulateMedia({ media: 'print' });
  await page.pdf({
    path: PDF_OUT,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:7.5px;color:#65717e;width:100%;padding:0 19mm;text-align:right;font-family:Arial,sans-serif;">Accumulation–Release Asymmetry · Draft v2</div>',
    footerTemplate: '<div style="font-size:7.5px;color:#65717e;width:100%;padding:0 19mm;display:flex;justify-content:space-between;font-family:Arial,sans-serif;"><span>Dylan La Franchi · August 2026</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '22mm', right: '19mm', bottom: '22mm', left: '19mm' },
    preferCSSPageSize: true,
  });
  await browser.close();
  process.stdout.write(JSON.stringify({ html: HTML_OUT, pdf: PDF_OUT }) + '\n');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
