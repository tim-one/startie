import random, sys, secrets, doctest
from itertools import filterfalse
from permute import permute  # Python implementation
from run_node import node_permute

__test__ = {'main':
"""
Capture some actual outputs to make sure results remain the same.

>>> random.seed(32476783687364)
>>> import string
>>> candidates = list(string.ascii_uppercase)
>>> for i in range(10):
...     cands = random.sample(candidates, random.randrange(2, 11))
...     scores = [random.randrange(100)
...               for i in range(len(cands))]
...     score = dict(zip(cands, scores))
...     magicint = random.randrange(1 << 64)
...     magic = magicint.to_bytes(8, 'little')
...     print("score", score)
...     print("magic 0x" + magic.hex())
...     py_result = permute(score, magic)
...     js_result = node_permute(score, magic)
...     print(py_result, py_result == js_result)
...     assert py_result == js_result
score {'D': 44, 'H': 43, 'V': 73, 'K': 47, 'G': 47, 'R': 7}
magic 0x6534defa3e6bdf69
['V', 'K', 'H', 'R', 'D', 'G'] True
score {'A': 28, 'H': 15, 'F': 27, 'V': 54}
magic 0x00c30bfae3baab68
['H', 'V', 'F', 'A'] True
score {'X': 76, 'D': 32, 'H': 4, 'E': 85, 'G': 59, 'L': 96, 'J': 22, 'N': 38, 'C': 43, 'T': 69}
magic 0xb1fb8ce49ee5e1db
['L', 'G', 'C', 'T', 'N', 'X', 'J', 'D', 'E', 'H'] True
score {'S': 14, 'T': 81, 'C': 91, 'O': 74, 'Q': 2}
magic 0xd13223588fda6ca4
['S', 'O', 'Q', 'T', 'C'] True
score {'M': 26, 'Y': 44, 'W': 18}
magic 0x27adc9eb95fa0627
['W', 'Y', 'M'] True
score {'Z': 57, 'L': 61, 'D': 80, 'C': 30, 'M': 95, 'T': 78, 'V': 38, 'G': 57, 'Q': 47, 'K': 38}
magic 0x3d7beac4badba914
['G', 'C', 'K', 'M', 'Z', 'V', 'L', 'T', 'Q', 'D'] True
score {'D': 33, 'Q': 91, 'K': 28, 'Y': 70, 'O': 21, 'B': 60}
magic 0xd0eae35067feb7be
['O', 'B', 'K', 'Q', 'D', 'Y'] True
score {'F': 36, 'G': 52}
magic 0x4ecc14afce878d1c
['F', 'G'] True
score {'Y': 76, 'P': 45, 'O': 8, 'M': 63, 'W': 97, 'V': 87}
magic 0xe264c8c0a070662a
['O', 'P', 'W', 'V', 'M', 'Y'] True
score {'L': 32, 'M': 61, 'N': 84, 'U': 93, 'S': 34}
magic 0x4afb51805314e9f9
['N', 'M', 'L', 'S', 'U'] True
"""
}

FORBIDDEN_CODEPOINTS = range(0xD800, 0xDFFF + 1) # surrogates
print(format(len(FORBIDDEN_CODEPOINTS), '_'),
      "forbidden code points")
ISBADCP = FORBIDDEN_CODEPOINTS.__contains__
ALLCP = range(0x110000)

if 1:
    # verify by brute force that Python has the same idea.
    for i in ALLCP:
        cp = chr(i)
        try:
            ignore = cp.encode("utf-8")
        except:
            assert ISBADCP(i), (i, hex(i))
        else:
            assert not ISBADCP(i), (i, hex(i))

if __name__ == "__main__":
    import doctest
    outcome = doctest.testmod()
    print("doctest result:", outcome)

def random_unicode_string(length=10):
    assert length >= 0
    got = []
    while need := length - len(got):
        assert need > 0
        trial = random.choices(ALLCP, k=need)
        got.extend(filterfalse(ISBADCP, trial))
    assert len(got) == length
    return ''.join(map(chr, got))

def random_score_dict(num_candidates=10, max_score=500):
    # Random candidate names from full plausibie Unicode set.
    return {random_unicode_string(random.randint(1, 30)):
            random.randint(0, max_score)
            for i in range(num_candidates)}

    # Generate candidate names like "C0", "C1", ...
    return {f"C{i}": random.randint(0, max_score)
            for i in range(num_candidates)}

def main(output=None):
    trials = 1000
    for t in range(trials):
        magic = secrets.token_bytes(8)
        score = random_score_dict(num_candidates=12, max_score=5000)
        py_perm = permute(score, magic)
        node_perm = node_permute(score, magic)
        if py_perm != node_perm:
            print("? Mismatch on trial", t)
            print("Score dict:", score)
            print("Python:", py_perm)
            print("Node:  ", node_perm)
            sys.exit(1)
        if output:
            print(py_perm, file=output)
        print(t+1, "of", trials, "done", end="\r")
    print()
    print(f"All {trials} trials matched")

if __name__ == "__main__":
    if 0: # enable this for some debugging output
        with open("output.txt", "w", encoding="utf-8") as f:
            main(f)
    else:
        main()
