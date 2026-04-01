const crypto = require('crypto');

const VERSION = "STAR-TIE-512-v2";

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
  let x = (typeof n === 'bigint') ? n : BigInt(n);
  if (x < 0n) throw new Error("n must be nonnegative");
  if (x > 0xFFFFFFFFFFFFFFFFn) throw new Error("n is too large");
  const buf = Buffer.alloc(8);
  for (let i = 0; i < 8; i++) {
    buf[i] = Number(x & 0xFFn);
    x >>= 8n;
  }
  return buf;
}

function canonicalSalt(items, magic) {
  const buffers = [Buffer.from(VERSION, 'utf8')];
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
  if (magic.length !== 0 && magic.length !== 8) {
    throw new Error("magic must be 0 or 8 bytes for STAR-TIE-512-v2");
  }
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

module.exports = {"permute": permute, "VERSION": VERSION}

// Example
// const score = { Alice: 5, Bob: 3, Charlie: 7 };
// console.log(permute(score));
