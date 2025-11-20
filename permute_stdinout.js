const fs = require('fs');
const {permute} = require('./permute.js');

// Read JSON dict from stdin
const input = fs.readFileSync(0, 'utf8');
const args = JSON.parse(input);

// Compute permutation
const result = permute(args.score, Buffer.from(args.magic));

// Write result back to stdout as JSON
process.stdout.write(JSON.stringify(result));
