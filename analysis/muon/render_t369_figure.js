const fs = require('fs');
const sharp = require('sharp');

const svg = 'T369_MUON_CAPTURE_DAUGHTER_CLOSURE_FIGURE.svg';
const png = 'T369_MUON_CAPTURE_DAUGHTER_CLOSURE_FIGURE.png';

sharp(fs.readFileSync(svg), { density: 180 })
  .png()
  .toFile(png)
  .then(() => process.stdout.write(`${png}\n`));
