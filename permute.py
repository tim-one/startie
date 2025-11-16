import hashlib

VERSION = b"STAR-TIE-512-v1"

def int2bytes(n: int) -> bytearray:
    if n < 0:
        raise ValueError("n must be nonnegative")
    out = bytearray()
    while n:
        out.append(n & 0xff)
        n >>= 8
    out.extend(b"\x00\x00\x00\x00")
    return out

def canonical_salt(score: dict[str, int]):
    # Sort candidate names by raw UTF-8 bytes
    items = sorted(score.items(),
                   key=lambda kv: kv[0].encode("utf-8"))
    stream = bytearray(VERSION)
    stream.extend(b'|')
    for name, stars in items:
        name_bytes = name.encode("utf-8")
        stream.extend(len(name_bytes).to_bytes(4, "little"))
        stream.extend(name_bytes)
        stream.extend(int2bytes(stars))
    return hashlib.sha512(stream)

def make_key(cand: str, score: dict[str, int], salt) -> bytes:
    h = salt.copy()
    h.update(cand.encode("utf-8"))
    h.update(int2bytes(score[cand]))
    return h.digest()

def permute(score: dict[str, int]) -> list[str]:
    salt = canonical_salt(score)
    return sorted(score.keys(),
                  key=lambda c: make_key(c, score, salt))

# Example
# score = {"Alice": 5, "Bob": 3, "Charlie": 7}
# print(permute(score))

if 0:
    from itertools import product
    from collections import defaultdict
    from math import factorial
    from string import ascii_uppercase
    from random import choices

    HILIMIT = 500
    scorerange = range(HILIMIT)
    NCANDS = 10
    cands = ascii_uppercase[:NCANDS]
    nbins = factorial(NCANDS)
    expect = 100.0
    total = int(expect) * nbins
    counts = defaultdict(int)
    for i in range(total):
        score = dict(zip(cands, choices(scorerange, k=NCANDS)))
        counts[''.join(permute(score))] += 1
        if not i & 0xffff:
            print(format(i / total, '.2%'), end="\r")
    print()
    #print(counts)
    from chi2util import chi2_cdf
    chi = 0.0
    for v in counts.values():
        chi += (v - expect)**2
    chi /= expect
    print(chi, chi2_cdf(chi, nbins - 1))
    if len(counts) != nbins:
       print("OUCH! number of bins", len(counts), "isn't", nbins)
