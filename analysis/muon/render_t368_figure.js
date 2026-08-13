const fs = require('fs');
const sharp = require('sharp');

const svg = 'T368_MUON_DECAY_HANDOVER_FIGURE.svg';
const png = 'T368_MUON_DECAY_HANDOVER_FIGURE.png';

sharp(fs.readFileSync(svg), { density: 180 })
  .png()
  .toFile(png)
  .then(() => process.stdout.write(`${png}\n`));
