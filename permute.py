"""
permute(score, magic=b'') returns a deterministic pseudo-random
permutation of the keys of the score dict, reproducible "forever"
and across multiple languages.

>>> VERSION # if this changes, test output will change too
b'STAR-TIE-512-v1'
>>> cands = 'ABCDE'
>>> score = dict(zip(cands, range(len(cands))))
>>> score
{'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
>>> squash = lambda iterable: ''.join(iterable)
>>> squash(score)
'ABCDE'
>>> expected = permute(score)
>>> squash(expected)
'BEACD'

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
'BEACD'
>>> assert got == expected

Any change to the socre dict can change the permutation.

>>> for name in score:
...     orig = score[name]
...     score[name] = orig + 1
...     print(squash(permute(score)))
...     if orig: # can't have a negative "score"
...         score[name] = orig - 1
...         print(squash(permute(score)))
...     score[name] = orig
DECAB
DCABE
ACBED
EABCD
CBDAE
BDACE
BDACE
ABDCE
BEDCA
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
0 ABCDE
1 BACED
2 CDBEA
3 EBCDA
4 AEDCB
5 BADEC
6 DCAEB
7 DEACB
8 DCBAE
9 DEABC
>>> len(seen)
10

The default is the empty byte string.
>>> got = permute(score, b'')
>>> squash(got)
'BEACD'
>>> assert got == expected
"""

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

# Later: after more thought, folding thn names into the salt didn't
# really help. It's the scores alone that vary across an election's
# score dicts. So we only need to fold in the scores in a canonicalized
# order of names.

# And then there's no need to fold the score into the hash of a
# candidate's name. The scores are already in the salt.

import hashlib
from operator import itemgetter as _get

__all__ = ["permute"]

# Calling _canonical_salt([]) will return a digest with the hash of
# VERSION. See versions.txt for history.
VERSION = b"STAR-TIE-512-v1"

# We compute varius stuff from the score dict. For simplicity and better
# "looks a lot alike" with the Node.js implementation, work instead with
# little lists that remember intermediate results. Curiously, to my eyes
# this makes the Javascript easier to follow, but the Python code a
# little harder!
_NAME_INDEX, _UTF_INDEX, _STARS_INDEX, _HASH_INDEX = range(4)
_get_NAME,   _get_UTF,   _get_STARS,   _get_HASH = map(_get, range(4))

def _get_items(score: dict[str, int]) -> \
               list[list[str, bytes, bytes, bytes]]:
    return [[name, name.encode(), _int2bytes(stars), None]
            for name, stars in score.items()]

# Return little-endian represetation of int `n`, with a zero byte added
# to both ends. The latter is to prevent ints from being mistaken for
# UTF-8 bytes when catenating fields (UTF-8 never contains a zero byte
# unless it's a single-character 0 byte, which won't appear in candidate
# names).
def _int2bytes(n: int) -> bytea:
    if n < 0:
        raise ValueError("n must be nonnegative")
    return (  b'\x00'
            + n.to_bytes(-(n.bit_length() // -8), 'little')
            + b'\x00')

def _canonical_salt(items: list,
                    magic: bytes=b'') -> hashlib._Hash:
    h = hashlib.sha512(VERSION + magic)
    # Sort candidate names by raw UTF-8 bytes.
    items.sort(key=_get_UTF)
    # Hash the scorea in order of UTF-8.
    h.update(b''.join(map(_get_STARS, items)))
    return h

def _make_key(utf: bytes,
              salt: hashlib._Hash) -> bytes:
    h = salt.copy()
    h.update(utf)
    return h.digest()

def permute(score: dict[str, int],
            magic: bytes=b'') -> list[str]:
    items = _get_items(score)
    salt = _canonical_salt(items, magic)
    for item in items:
        item[_HASH_INDEX] = _make_key(item[_UTF_INDEX], salt)
    items.sort(key=_get_HASH)
    return list(map(_get_NAME, items))

# Example
# score = {"Alice": 5, "Bob": 3, "Charlie": 7}
# print(permute(score))

assert _canonical_salt([]).hexdigest() == hashlib.sha512(VERSION).hexdigest()

if __name__ == "__main__":
    import doctest
    outcome = doctest.testmod()
    print("doctest result:", outcome)
