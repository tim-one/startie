const crypto = require('crypto');

// We compute various stuff from the names and scores. For
// simplicity, work with a list of new objects that remembers
// this stuff. Saves, e.g., repeated decorate-sort-undecorate
// dances.
function makeItems(score) {
    return Object.keys(score).map(name => ({
      name: name,
      utf: Buffer.from(name, 'utf8'),
      stars: int2bytes(score[name]),
      hash: undefined
    }));
}

function int2bytes(n) {
  if (n < 0) throw new Error("n must be nonnegative");
  const bytes = [0];
  let x = n;
  while (x > 0) {
    bytes.push(x & 0xff);
    x = Math.floor(x / 256);
  }
  bytes.push(0);
  return Buffer.from(bytes);
}

function canonicalSalt(items, magic) {
  const buffers = [Buffer.from("STAR-TIE-512-v1", 'utf8')];
  buffers.push(magic);
  // fold in scores by canonical order of UTF-8 names
  items.sort((a, b) => a.utf.compare(b.utf));
  for (const item of items) {
    buffers.push(item.stars);
  }
  return Buffer.concat(buffers);
}

function makeKey(utf, salt) {
  const h = crypto.createHash('sha512');
  h.update(salt);
  h.update(utf);
  return h.digest();
}

const EMPTY_BUFFER = Buffer.alloc(0);

function permute(score, magic=EMPTY_BUFFER) {
  const items = makeItems(score);
  const salt = canonicalSalt(items, magic);
  // create crypto hashes
  for (const item of items) {
    item.hash = makeKey(item.utf, salt);
  }
  // and return names sorted by hash
  items.sort((a, b) => a.hash.compare(b.hash));
  return items.map(item => item.name);
}

module.exports = {"permute" : permute}

// Example
// const score = { Alice: 5, Bob: 3, Charlie: 7 };
// console.log(permute(score));
