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

"""
permute(score, magic=b'') returns a deterministic pseudo-random
permutation of the keys of the score dict, reproducible "forever"
and across multiple languages.

>>> cands = 'ABCDE'
>>> score = dict(zip(cands, range(len(cands))))
>>> score
{'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
>>> squash = lambda iterable: ''.join(iterable)
>>> squash(score)
'ABCDE'
>>> expected = permute(score)
>>> squash(expected)
'DCAEB'

The order of dict entries doesn't matter. Internally, the entries
are processed by lexicographic order of the keys' UTF-8 encoding.

>>> from itertools import permutations
>>> count = 0
>>> items = list(score.items())
>>> for newitems in permutations(items):
...     count += 1
...     newscore = dict(newitems)
...     got = permute(newscore)
...     assert got == expected
>>> count
120

The JavaScript implementation gives the same results.

>>> try:
...     from run_node import node_permute
... except ModuleNotFoundError:
...     node_permute = permute
>>> got = node_permute(score)
>>> squash(got)
'DCAEB'
>>> assert got == expected

Any change to the socre dict can change the permutation.

>>> for name in score:
...     orig = score[name]
...     score[name] += 1
...     print(squash(permute(score)))
...     score[name] = orig
DCBAE
ADBEC
CBAED
ECBDA
ADCBE
>>> assert permute(score) == expected

The optional "magic" argument can be used to inject some true
randomness. For example, pass `secrets.token_bytes(8))`. It's highly
recommended. Any bytes object can be used, provided it can't be guessed,
and every bit can make a difference. 8 bytes offers strong protection
against manipulation with scant overhead.

>>> seen = set()
>>> for magicint in range(10):
...    magicbytes = magicint.to_bytes(8, 'little')
...    got = squash(permute(score, magicbytes))
...    print(magicint, got)
...    seen.add(got)
...    gotjs = squash(node_permute(score, magicbytes))
...    assert got == gotjs
0 ECDAB
1 AEDBC
2 DBCEA
3 DECAB
4 CABED
5 ADBCE
6 DCBAE
7 BDACE
8 AEBDC
9 DECBA
>>> len(seen)
10

The default is the empty byte string.
>>> got = permute(score, b'')
>>> squash(got)
'DCAEB'
>>> assert got == expected
"""

import hashlib

__all__ = ["permute"]

# Calling _canonical_salt({}) will return a digest with the hash of
# VERSION. See versions.txt for history.
VERSION = b"STAR-TIE-512-v1"

# Return little-endian represetation of int `n`, with a zero byte added
# to both ends. The latter is to prevent ints from being mistaken for
# UTF-8 bytes when catenating fields (UTF-8 never contains a zero byte
# unless it's a single-character 0 byte, which won't appear in candidate
# names).
def _int2bytes(n: int) -> bytearray:
    if n < 0:
        raise ValueError("n must be nonnegative")
    out = bytearray([0])
    while n:
        out.append(n & 0xff)
        n >>= 8
    out.append(0)
    return out

def _canonical_salt(score: dict[str, int],
                    magic: bytes=b'') -> hashlib._Hash:
    h = hashlib.sha512(VERSION + magic)
    # Sort candidate names by raw UTF-8 bytes
    items = [(name.encode("utf-8"), s)
             for name, s in score.items()]
    items.sort()
    for name_bytes, stars in items:
        h.update(name_bytes + _int2bytes(stars))
    return h

def _make_key(cand: str,
             score: dict[str, int],
              salt: hashlib._Hash) -> bytes:
    h = salt.copy()
    h.update(cand.encode("utf-8") + _int2bytes(score[cand]))
    return h.digest()

def permute(score: dict[str, int],
            magic: bytes=b'') -> list[str]:
    salt = _canonical_salt(score, magic)
    return sorted(score.keys(),
                  key=lambda c: _make_key(c, score, salt))

# Example
# score = {"Alice": 5, "Bob": 3, "Charlie": 7}
# print(permute(score))

assert _canonical_salt({}).hexdigest() == hashlib.sha512(VERSION).hexdigest()

if __name__ == "__main__":
    import doctest
    outcome = doctest.testmod()
    print("doctest result:", outcome)
