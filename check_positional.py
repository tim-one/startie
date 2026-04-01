from math import erf, sqrt
import string
import secrets
from random import choices, choice

from permute import permute

try:
    from scipy.stats import chi2 as chi2_dist
except ImportError:
    chi2_dist = None

try:
    from mpmath import ncdf
except ImportError:
    ncdf = None

cand_names = string.digits + string.ascii_uppercase
assert len(cand_names) == 36


def check_positional(NCANDS, HILIMIT=11, total_permutations=128_000):
    scorerange = range(HILIMIT)
    cands = cand_names[:NCANDS]

    matrix = {c: [0] * NCANDS for c in cands}

    batch = 2**7
    total_permutations += -total_permutations % batch

    print(f"num cands {NCANDS} | high score limit {HILIMIT}")
    print(f"testing {total_permutations:,} permutations...")

    ndone = 0
    for _ in range(total_permutations // batch):
        score = dict(zip(cands, choices(scorerange, k=NCANDS)))
        for _ in range(batch):
            score[choice(cands)] += 1
            magic = secrets.token_bytes(8)
            p = permute(score, magic)
            for rank, cand in enumerate(p):
                matrix[cand][rank] += 1

        ndone += batch
        if not ndone & 0xFFFF:
            print(f"{ndone / total_permutations:.2%}", end="\r")
    print(' ' * 50, end="\r")

    expect = total_permutations / NCANDS
    chi = 0.0
    for c in cands:
        for rank in range(NCANDS):
            observed = matrix[c][rank]
            chi += (observed - expect) ** 2
    chi /= expect

    df = (NCANDS - 1) ** 2
    sigma = sqrt(2.0 * df) if df > 0 else 1.0
    z = (chi - df) / sigma if df > 0 else 0.0

    print(f"    chisq {round(chi, 1)} - should be centered around {df} and z is {z:+.2f}")

    p = None
    if chi2_dist is not None:
        p = float(chi2_dist.cdf(chi, df))
        print(f"    p-value (scipy) {round(p, 5)}")
    else:
        # fallback normal approximation for chi-square CDF
        if df > 0:
            z_norm = (chi - df) / (2.0 * sqrt(df))
            p = 0.5 * (1.0 + erf(z_norm))
            print(f"    p-value (normal approx) {round(p, 5)}")
        else:
            p = 0.5
            print(f"    p-value (df=0 fallback) {round(p, 5)}")

    if p is not None and not 0.05 <= p <= 0.95:
        print(' '.ljust(40, '*'))
    print("\n")


if __name__ == '__main__':
    for ncands in list(range(2, 21)) + [30]:
        for i in range(3):
            check_positional(ncands)
