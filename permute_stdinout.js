// Helper to run the Node version _from_ Python.
// Read a JSON representation of permute's arguments
// from stdin, and write the permutation to stdout,
// again as JSON.
// Python invokes this via the subprocess module.
const fs = require('fs');
const {permute} = require('./permute.js');

// Read JSON dict from stdin
const input = fs.readFileSync(0, 'utf8');
const args = JSON.parse(input);

// Compute permutation
const result = permute(args.score, Buffer.from(args.magic));

// Write result back to stdout as JSON
process.stdout.write(JSON.stringify(result));
