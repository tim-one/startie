# #xpensive!

# Builds random score dicts and measures how well `permute()` does at
# producing all possible permutations equally often. This is the uuaal
# chi-squared statistic: the distribution may be too skewed _or_ too
# unifoom to be plausibly "really random".
#
# For reliability, we need to expect to see every permutation at least
# about 20 times - so over 70 million tries for just 10 candidates! At
# which point mpmath's gamminc is close to blowing up when computing the
# chi2 CDF (convergence too slow).
#
# Note that CDF values less thab 0.05 and greater than 0.95 are
# generally "suspicious". But not to fret over! If the process were
# truly random, we'd expect to see a CDF under 0.05 about 5% of time,
# and also a CDF over 0,95.

from collections import defaultdict
from math import factorial, sqrt, nan
import string
from random import choices
from permute import permute

from mpmath import gammainc

cand_names = string.digits + string.ascii_uppercase
assert len(cand_names) == 36

def chi2_cdf(x, df):
    """Return probability that a value from a chi square distribution
       with `df` degrees of freedom has value <= `x`."""

    return float(gammainc(df/2, 0, x/2, True))

def check(NCANDS, HILIMIT=500):
    scorerange = range(HILIMIT)
    cands = cand_names[:NCANDS]
    nbins = factorial(NCANDS)
    df = nbins - 1
    expect = 10.0
    total = int(expect) * nbins
    counts = defaultdict(int)
    print("num cands", NCANDS, "high score limit", HILIMIT,
          "nbins", format(nbins, '_'),
          "expected per bin", expect)
    for i in range(1, total + 1):
        score = dict(zip(cands, choices(scorerange, k=NCANDS)))
        # Due to our choice of candidate names, a permutation can be
        # uniquely and compactly represented as a base-NCANDS integer
        # with NCANDS digits. Saves RAM over using string keys.
        counts[int(''.join(permute(score)), NCANDS)] += 1
        if not i & 0xffff:
            print(format(i / total, '.2%'), end="\r")
    print(' ' * 50, end="\r")
    missing = nbins - len(counts)
    assert missing >= 0
    chi = 0.0
    if missing:
        print("    OUCH!", missing, "bins are empty")
        chi = missing * expect**2
    for v in counts.values():
        chi += (v - expect)**2
    chi /= expect
    z = (chi - df) / sqrt(2 * df)
    print("    chisq", round(chi, 1),
          "- should be centered around", df,
          "and z is", format(z, "+.2f"))
    print("    chi CDF next; if nbins is large, this may blow up ...",
          end=' ')
    try:
        p = chi2_cdf(chi, df)
    except Exception as e:
        print("yup, blew up")
        print("       ", e)
    else:
        print(round(p, 3), end='')
        if not 0.05 <= p <= 0.95:
            print(' '.ljust(30, '*'), end='')
        print()

for ncands in range(2, 12):
    for i in range(5):
        check(ncands)
    print()
