# startie
Robust, cross-language, "random" tiebreaking for STAR elections

The goal here is to provide a way to break ties in STAR elections in a way that's

- Reproducible across multiple language implementations.
- Is reasonably fast and memory-frugal (depends on the num0ber of candidates, but not on the number of voters).
- Can't be predicted or manipulated, not even by an election administrator.
- Has no external dependencies (e.g., no looking up winning lottery numbers, or stock market statistics, or web-based "randomness beacons", ...).

The idea is to produce a "random" permutation of the candidates. When a tie occurs, pick the candidate whose name appears earliest in that permutation.

Such a facility is widely assumed to be available in election research literature. but practical implementations are conspicuous by absence, or so feeble that they're easy to trick.

Instead we sort a list of candidate names, using as sort keys crypto hashes of (candidate_name, candidate_score) pairs. Nothing can be known about "score dicts" before the election closes, and when it does close it's too late to play dirty tricks.  Of course the devil is in the details.

Suffice it to say that all known problems appear to have been worked out, and results should be wholly reproducible, with remarkably straightforward code, under any language with conforming implementations of Unicode UTF-8 encoding and SHA-512 crypto hashing. We're effectively using SHA-512 _as_ a very high-quality PRNG.
