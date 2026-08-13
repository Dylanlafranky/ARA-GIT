const fs = require('fs');
const sharp = require('sharp');

const svg = 'T369B_MUON_DAUGHTER_ANTIPHASE_FIGURE.svg';
const png = 'T369B_MUON_DAUGHTER_ANTIPHASE_FIGURE.png';

sharp(fs.readFileSync(svg), { density: 180 })
  .png()
  .toFile(png)
  .then(() => process.stdout.write(`${png}\n`));
