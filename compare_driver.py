import json, random, subprocess, sys, secrets
from itertools import filterfalse
from permute import permute  # Python implementation

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

def run_node(score, magic):
    # Launch Node.js and feed JSON dict via stdin
    try:
        args = {'magic': list(magic),
                'score': score,
               }
        proc = subprocess.run(
            ["node", "permute_stdinout.js"],
            input=json.dumps(args).encode(),
            capture_output=True,
            check=True,
        )
    except Exception as e:
        print(e)
        print(dir(e))
        print(e.args)
        print(e.cmd)
        print(e.output)
        print(e.stderr)
        raise
    return json.loads(proc.stdout)

def main(output=None):
    trials = 1000
    for t in range(trials):
        magic = secrets.token_bytes(8)
        score = random_score_dict(num_candidates=12, max_score=5000)
        py_perm = permute(score, magic)
        node_perm = run_node(score, magic)
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
