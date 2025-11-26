// Set up the Node side "permute server".
// It reads test cases from stdin, and writes
// `permute()` results to stdout, using JSON
// in both directions. This is "1-liner" JSON,
// using a newline to delimit distinct test
// cases and 
import { createInterface } from 'node:readline';
import { permute } from './permute.js';

const rl = createInterface({
  input: process.stdin,
  crlfDelay: Infinity,
});

rl.on('line', (line) => {
  //if (line.trim().length === 0) return;

  try {
    const args = JSON.parse(line);
    const result = permute(args.score, Buffer.from(args.magic));
    process.stdout.write(JSON.stringify(result) + '\n');
  }
  catch (error) {
    console.error(`Failed to parse a JSON line: ${error.message}`);
  }
});

// We can ignore the 'close' event.
