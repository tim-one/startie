import json, random, subprocess, sys
from itertools import filterfalse
from permute import permute  # Python implementation

FORBIDDEN_CODEPOINTS = (
      # surrogates
      set(range(0xD800, 0xDFFF + 1))
      # non-characters
    | set(range(0xFDD0, 0xFDEF + 1))
      # non-characters at the end of each plane
    | set(hi | lo
          for hi in range(0x000000, 0x10FFFF + 1, 0x10000)
          for lo in (0xFFFE, 0xFFFF)))

print(format(len(FORBIDDEN_CODEPOINTS), '_'),
      "forbidden code points")
ALLCP = range(0x110000)
ISBADCP = FORBIDDEN_CODEPOINTS.__contains__

def random_unicode_string(length=10):
    got = []
    while len(got) < length:
        trial = random.choices(ALLCP, k=length-len(got))
        got.extend(filterfalse(ISBADCP, trial))
    return ''.join(map(chr, got))

def random_score_dict(num_candidates=10, max_score=500):
    # Random candidate names from full plausibie Unicode set.
    return {random_unicode_string(random.randint(1, 30)):
            random.randint(0, max_score)
            for i in range(num_candidates)}

    # Generate candidate names like "C0", "C1", ...
    return {f"C{i}": random.randint(0, max_score)
            for i in range(num_candidates)}

def run_node(score):
    # Launch Node.js and feed JSON dict via stdin
    try:
        proc = subprocess.run(
            ["node", "permute_test.js"],
            input=json.dumps(score).encode(),
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
        score = random_score_dict(num_candidates=12, max_score=5000)
        py_perm = permute(score)
        node_perm = run_node(score)
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
