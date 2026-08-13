const fs = require('fs');
const sharp = require('sharp');

const svg = 'T369C_MUON_DAUGHTER_ENERGY_BRANCH_FIGURE.svg';
const png = 'T369C_MUON_DAUGHTER_ENERGY_BRANCH_FIGURE.png';

sharp(fs.readFileSync(svg), { density: 180 })
  .png()
  .toFile(png)
  .then(() => process.stdout.write(`${png}\n`));
