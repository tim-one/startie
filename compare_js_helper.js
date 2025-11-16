const fs = require('fs');
const { permute } = require('./permute'); // your Node implementation

// Read JSON dict from stdin
const input = fs.readFileSync(0, 'utf8');
const score = JSON.parse(input);

// Compute permutation
const result = permute(score);

// Write result back to stdout as JSON
process.stdout.write(JSON.stringify(result));
