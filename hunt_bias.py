from math import erf, sqrt
import string
import secrets
import hashlib
from random import choices, choice

from permute import permute

try:
    from scipy.stats import chi2 as chi2_dist
except ImportError:
    chi2_dist = None

cand_names = string.digits + string.ascii_uppercase

def run_test(NCANDS, HILIMIT=11, total_permutations=128_000):
    scorerange = range(HILIMIT)
    cands = cand_names[:NCANDS]
    matrix = {c: [0] * NCANDS for c in cands}
    
    # We want a stable score set for one 'run' to see if a specific score + salt causes issues.
    # But the user asked to hunt for a seed/magic that causes a bad run.
    # A 'run' here is 128,000 permutations with DIFFERENT magic bytes.
    # If the algorithm is biased, it should show up across many magics for a given NCANDS.
    # Actually, if the bias is IN the algorithm, any large run should show it if N is large enough.
    
    print(f"Hunting for bias with NCANDS={NCANDS}...")
    
    batch = 2**7
    total_permutations += -total_permutations % batch

    ndone = 0
    # Fixed scores for this hunt to see if specific score distributions trigger it
    # though with random magic it shouldn't matter if the hash is good.
    score = dict(zip(cands, choices(scorerange, k=NCANDS)))
    
    for _ in range(total_permutations // batch):
        for _ in range(batch):
            # Slightly vary score to keep it dynamic as in check_positional
            score[choice(cands)] += 1
            magic = secrets.token_bytes(8)
            p = permute(score, magic)
            for rank, cand in enumerate(p):
                matrix[cand][rank] += 1
        ndone += batch

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
    
    return chi, df, z, matrix

if __name__ == '__main__':
    NCANDS = 10 # Start with a reasonable number
    threshold = 2.5 # Higher threshold to catch clear outliers
    
    iteration = 0
    while True:
        iteration += 1
        chi_val, df_val, z_val, mat = run_test(NCANDS, total_permutations=128_000)
        print(f"Iteration {iteration}: z={z_val:.2f}, chisq={chi_val:.1f}")
        
        if z_val > threshold:
            print(f"\nTarget hit! z={z_val:.2f}")
            print("Matrix (candidate: [counts for pos 0, 1, 2, ...]):")
            cands = cand_names[:NCANDS]
            expect = 128_000 / NCANDS
            for c in cands:
                row = mat[c]
                diffs = [v - int(expect) for v in row]
                print(f"{c}: {row} (diffs: {diffs})")
            break
        
        # If we don't find it in 20 iterations, maybe increase NCANDS
        if iteration >= 20:
            print("No high bias found with NCANDS=10, trying NCANDS=20")
            NCANDS = 20
            iteration = 0
        if NCANDS == 20 and iteration >= 20:
            print("No high bias found with NCANDS=20. The algorithm might be better than suspected or we need more permutations.")
            break
