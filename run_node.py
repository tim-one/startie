import json, subprocess

# node_permute runs the Node implementation using Node
def node_permute(score: dict[str, int],
                 magic: bytes=b'') -> list[str]:

    args = {'magic': list(magic),
            'score': score,
               }
    # Launch Node.js and feed JSON dict via stdin
    try:
        proc = subprocess.run(
            ["node", "permute_stdinout.js"],
            input=json.dumps(args).encode(),
            capture_output=True,
            check=True,
        )
    except Exception as e:
        print(e)
        print(e.cmd)
        print(e.output)
        print(e.stderr)
        raise
    return json.loads(proc.stdout)
