import json, random, subprocess, sys
from permute import permute  # Python implementation

def random_score_dict(num_candidates=10, max_score=500):
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

def main():
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
        print(py_perm)
        print(t+1, "of", trials, "done", end="\r")
    print()
    print(f"All {trials} trials matched")

if __name__ == "__main__":
    main()
