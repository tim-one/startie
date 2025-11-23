# Verify the Python examples in README.md.

from permute import permute
import doctest, sys

FNAME = "README.md"

outcome = doctest.testfile(FNAME)
print("doctest of", FNAME, "outcome:", outcome)
if outcome.failed:
    sys.exit(1)
