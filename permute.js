const crypto = require('crypto');

function int2bytes(n) {
  if (n < 0) throw new Error("n must be nonnegative");
  const bytes = [];
  let x = n;
  while (x > 0) {
    bytes.push(x & 0xff);
    x = Math.floor(x / 256);
  }
  bytes.push(0, 0, 0, 0);
  return Buffer.from(bytes);
}

function canonicalSalt(score) {
  const items = Object.entries(score)
    .sort((a, b) => Buffer.from(a[0], 'utf8').compare(Buffer.from(b[0], 'utf8')));
  const stream = [];
  stream.push(...Buffer.from("STAR-TIE-512-v1|", 'utf8'));
  for (const [name, stars] of items) {
    const nameBytes = Buffer.from(name, 'utf8');
    const lenBuf = Buffer.alloc(4);
    lenBuf.writeUInt32LE(nameBytes.length);
    stream.push(...lenBuf, ...nameBytes, ...int2bytes(stars));
  }
//  return crypto.createHash('sha512').update(Buffer.from(stream)).digest();
  return Buffer.from(stream);
}

function makeKey(cand, score, salt) {
  const h = crypto.createHash('sha512');
  h.update(salt);
  h.update(Buffer.from(cand, 'utf8'));
  h.update(int2bytes(score[cand]));
  return h.digest();
}

function permute(score) {
  const salt = canonicalSalt(score);
  return Object.keys(score).sort((a, b) => makeKey(a, score, salt).compare(makeKey(b, score, salt)));
}

module.exports = {"permute" : permute}

// Example
// const score = { Alice: 5, Bob: 3, Charlie: 7 };
// console.log(permute(score));
