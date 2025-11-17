# The basic idea is to sort names via a key that's a crypto hash of
# the name and its score.

# To work the same way aross all implementations, we have to use the
# UTF-8 encoding of the name, so that its hash is well defined. The byte
# encoding of other representations depends on the language in use.
# UTF-8 is supported everywhere, but has to be forced.

# If we used the name alone, then the permutation would depend _only_ on
# the candidates' names. 100% predictable and trivial to manipulate.

# Folding in the score too makes it unpredictable in the small, but
# still kind of exploitable in the large: it's feasible to predict a
# range of scores, and then play games with a name, adjusting via
# poke-nnd-hope to find a spelling that leaves the name near the start
# of the permutation across the range of plausible scores. Unicode
# offers a world of possibilities for fiddling names in ways that appear
# very similar(or even identical). Also minor spelling variations.

# So we want it "even more unpredictable". A standard way to do that is
# to use a "salt": another unpredictable value folded in to _every_
# hash.

# My first attempt at that folded in sum(soore.values()) as the salt.
# Unpredictable - but biased! By the central limit theorem, the sua
# of scores tends to follow a normal distribution, regardless of the
# distibution of the scores themselves. So some salts were more
# likely than others, & that biased the distribution of permutations
# produced.

# The sum of all scores throws away too much information. What we want
# instead is something that's extremely likely to be different between
# _any_ two distinct score dicts. Use that as a salt, and then any
# change to the score dict will almost certainly change every name's
# key.

# So what does work for a salt is building a canonical representation of
# the entire score dict, a catenation of
#      name score name score name score ...
# where the names are in increasing order of their UTF-8 byte
# representations. That will produce the same stream of bytes on all
# platforms.

import hashlib

__all__ = ["permute"]

# Calling _canonical_salt({}) will return a digest with the hash of
# VERSION. See versions.txt for history.
VERSION = b"STAR-TIE-512-v1"

# Return little-endian represetation of int `n`,
# followed by 4 zero bytes.
def _int2bytes(n: int) -> bytearray:
    if n < 0:
        raise ValueError("n must be nonnegative")
    out = bytearray()
    while n:
        out.append(n & 0xff)
        n >>= 8
    out.extend(b"\x00\x00\x00\x00")
    return out

def _canonical_salt(score: dict[str, int]) -> hashlib._Hash:
    h = hashlib.sha512(VERSION)
    # Sort candidate names by raw UTF-8 bytes
    items = [(name.encode("utf-8"), s)
             for name, s in score.items()]
    items.sort()
    for name_bytes, stars in items:
        h.update(name_bytes + b'\x00' + _int2bytes(stars))
    return h

def _make_key(cand: str,
              score: dict[str, int],
              salt: hashlib._Hash) -> bytes:
    h = salt.copy()
    h.update(cand.encode("utf-8"))
    h.update(_int2bytes(score[cand]))
    return h.digest()

def permute(score: dict[str, int]) -> list[str]:
    salt = _canonical_salt(score)
    return sorted(score.keys(),
                  key=lambda c: _make_key(c, score, salt))

# Example
# score = {"Alice": 5, "Bob": 3, "Charlie": 7}
# print(permute(score))

assert _canonical_salt({}).hexdigest() == hashlib.sha512(VERSION).hexdigest()
