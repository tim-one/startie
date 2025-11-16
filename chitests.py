# #xpensive!

# Builds random score dicts and measures how well `permute()` does at
# producing all possible permutations equally often. This is the uuaal
# chi-squared statistic: the distribution may be too skewed _or_ too
# unifoom to be plausibly "really random".
#
# For reliability, we need to expect to see every permutation at least
# about 20 times - so over 70 million tries for just 10 candidates! At
# which point mpmath's gamminc is close to blowing up when computind the
# chi2 CDF (convergence too slow).
#
# Note that CDF values less thab 0.05 and greater than 0.95 are
# generally "suspicious". But not to fret over! If the process were
# truly random, we'd expect to see a CDF under 0.05 about 5% of time,
# and also a CDF over 0,95.

from collections import defaultdict
from math import factorial
from string import ascii_uppercase
from random import choices
from permute import permute

from mpmath import gammainc

def chi2_cdf(x, df):
    """Return probability that a value from a chi square distribution
       with `df` degrees of freedom has value >= `x`."""

    return float(gammainc(df/2, 0, x/2, True))

def check(NCANDS, HILIMIT=500):
    scorerange = range(HILIMIT)
    cands = ascii_uppercase[:NCANDS]
    nbins = factorial(NCANDS)
    expect = 50.0
    total = int(expect) * nbins
    counts = defaultdict(int)
    print("num cands", NCANDS, "high score limit", HILIMIT,
          "nbins", format(nbins, '_'),
          "expected per bin", expect)
    for i in range(total):
        score = dict(zip(cands, choices(scorerange, k=NCANDS)))
        counts[''.join(permute(score))] += 1
        if not i & 0xffff:
            print(format(i / total, '.2%'), end="\r")
    print(' ' * 50, end="\r")
    chi = 0.0
    for v in counts.values():
        chi += (v - expect)**2
    chi /= expect
    print("chisq", round(chi, 1),
          "- should be centered around", nbins - 1)
    print("chi CDF next; if nbins is large, this may blow up ...",
          end=' ')
    print(format(round(chi2_cdf(chi, nbins - 1), 3)))

for ncands in range(2, 10):
    for i in range(3):
        check(ncands)
    print()
