# startie
Robust, cross-language, "random" tiebreaking for STAR elections

The goal here is to provide a way to break ties in STAR elections that's:

- Reproducible across multiple language implementations.
- Is reasonably fast and memory-frugal (depends on the number of candidates, but not on the number of voters).
- Can't be predicted or manipulated, not even by an election administrator.
- Has no external dependencies (e.g., no looking up winning lottery numbers, or stock market statistics, or web-based "randomness beacons", ...).

The idea is to produce a "random" permutation of the candidates. When a tie occurs, pick the candidate whose name appears earliest in that permutation.

Such a facility is widely assumed to be available in election research literature. but practical implementations are conspicuous by absence, or so feeble that they're easy to trick.

Instead we sort a list of candidate names, using as sort keys crypto hashes of (candidate_name, candidate_score) pairs. Nothing can be known about "score dicts" before the election closes, and when it does close it's too late to play dirty tricks.  Of course the devil is in the details.

Suffice it to say that all known problems appear to have been worked out, and results should be wholly reproducible, with remarkably straightforward code, under any language with conforming implementations of Unicode UTF-8 encoding and SHA-512 crypto hashing. We're effectively using SHA-512 _as_ a very high-quality PRNG.

## API

The primary files are `permute.py` and `permute.js`. Each supplies one function, `permute(score)`. which takes a dict (Python. or Object in Node) mapping names (Unicode strings) to scores (ints), and returns a "randomly permuted" list of names (the score dict's keys).

## Other

`compare_driver.py` constructs random score dicts and ensures that the Python and Node implementations produce the same permutations. Edit it to change the number of test cases run, the number of candidates, and the maximum candidate score. That's less work for you too than trying to remember command line conventions :wink:.

`chitests.py` uses chi-squared tests to measure how well `permute()` passes out all possible permutations about equally often. This gets very expensive even for as few as 10 candidates - and substantially larger than that would run out of RAM too! This work grows with the factorial of the number of candidates.

## Q&A

**Q:** What remains to be done? Do you want help?

**A:** I'm happy with the design and the Python code, and testing has gone very well. But I'm not a native JavaScript speaker, and would really appreciate it if someone who is reviewed the JS code for "common sense" and idiomatic expression. Most of it was pasted from code suggested by a chatbot! It works, but is still a foreign language to me.

**Q:** When building the "canonical salt", the Python code returns a hashlib object, but the JS code a buffer of raw bytes. Is that an error?

**A:** Sure hope not :wink:. This is due to that JS's crypto-hash API doesn't appear to offer a `.copy()` method. We're feeding the same initial raw bytes into the hash for every candidates' sort key, and using `.copy()` for that is the _purpose_ of `.copy()`. It's not really for efficiency (although it is faster), but for conceptual clarity. The JS code has no choice but to feed those raw prefix bytes into the key hashes repeatedly. The outcomes in the end are identical.

**Q:** Unicode always causes problems. Which ones have you missed?

**A:** Time will tell, but none that I know of. There are several standard ways of encoding Unicode code points, but correctly implemented conversions between any pair are lossless and reversible. We use UTF-8 because every language can convert to that, and a sequence of bytes is exactly what this algorithm needs. There's generally a minor problem when computing a crypto hash from multiple fields: the input bytes of one field are catenated with the inputs bytes of the next, and the idea that they're _different_ fields gets lost. But, in UTF-8, a zero byte never appears unless it's the one-character ANSI 0 byte, and candidate names will never contain one of those. So we generally alternate UTF-8 input fields with integer fields, and the latter are guaranteed (by construction) to have a 0 byte at each end. So one field can't be accidentally mistaken as part of a different field.

Other _potential_ problems could come from "normalization", fancy schemes that actually change code points. We certainly do none of that, and I doubt any voting service would either. They're just using Unicode to display candidate names faithfully, not analyzing them or doing computation on them.

## Acks

- Thanks to Larry Hastings, for talks about this kind of approach when he was writing his lovely [starvote](https://github.com/larryhastings/starvote) library. The idea here is similar, but less ambitious, simpler, and much less tied to Python quirks. Larry uses a crypto hash to seed Python's Mersenne Twister; we don't use a conventional PRNG at all. Larry goes on to build a crypto hash of all the ballots, but we only look at the score dict. That's partly for efficiency, but also looking forward to a future when STAR is the only voting method in use 😄. Then "precinct summability" becomes important - there may not be a "collection of ballots" in one place _to_ look at, just a sum of score dicts aggregated from different precincts.

- Thanks to the folks at the [STAR voting service](https://bettervoting.com/). for discussions, interest, encouragement, and contributing code to an earlier attempt at writing a cross-language "good enough" pseudo-random list shuffler. I've given up on that, as finding a "provably fair and secure" way to _seed_ it proved to be a bottomless pit. If the STAR folks adopt this new approach, I'll pester Larry to add it as an optional way for `starvote` to break ties too.

- And special thanks to ChatGPT-5! It knows a whole lot more about JavaScript than I know, and most of its suggestions worked on the first try. It also showed shockingly deep insights into the nuances of the problem domain, such as why the central limit theorem played a key role in why an earlier attempt produced demonstrably biased permutations.


