/// Deterministic pseudo-random tiebreaking for STAR elections.
/// Rust port of startie
///
/// Produces a reproducible permutation of candidate names by sorting them
/// using SHA-512 hashes of (canonical_salt, candidate_name) pairs.
/// Results match the Python and JavaScript implementations.
use sha2::{Digest, Sha512};

const VERSION: &[u8] = b"STAR-TIE-512-v1";

/// Encode a non-negative integer as little-endian bytes with a zero byte
/// on each end. This prevents integer bytes from being confused with UTF-8
/// bytes when fields are concatenated.
fn int2bytes(n: i64) -> Vec<u8> {
    assert!(n >= 0, "n must be nonnegative");
    let mut bytes = vec![0u8]; // leading zero
    let mut val = n as u64;
    while val > 0 {
        bytes.push((val & 0xFF) as u8);
        val >>= 8;
    }
    bytes.push(0); // trailing zero
    bytes
}

/// Build the canonical salt: SHA-512 state after hashing VERSION + magic +
/// all scores in UTF-8-sorted name order.
fn canonical_salt(candidates: &mut [(String, i64)], magic: &[u8]) -> Sha512 {
    let mut h = Sha512::new();
    h.update(VERSION);
    h.update(magic);

    // Sort by raw UTF-8 bytes of the name
    candidates.sort_by(|a, b| a.0.as_bytes().cmp(b.0.as_bytes()));

    // Hash the scores in that order
    for (_, score) in candidates.iter() {
        h.update(int2bytes(*score));
    }
    h
}

/// Compute the sort key for a single candidate: hash(salt + name_utf8).
fn make_key(name_utf8: &[u8], salt: &Sha512) -> Vec<u8> {
    let mut h = salt.clone();
    h.update(name_utf8);
    h.finalize_reset().to_vec()
}

/// Return a deterministic pseudo-random permutation of candidate names.
///
/// `scores` maps candidate names to their scores (totals from the scoring phase).
/// `magic` is optional extra entropy bytes (highly recommended for real elections).
///
/// The result is reproducible across Python, JavaScript, and this Rust implementation.
pub fn permute(scores: &[(String, i64)], magic: &[u8]) -> Vec<String> {
    let mut candidates: Vec<(String, i64)> = scores.to_vec();

    // Build the canonical salt (also sorts candidates by UTF-8 name)
    let salt = canonical_salt(&mut candidates, magic);

    // Compute hash keys and sort by them
    let mut keyed: Vec<(Vec<u8>, String)> = candidates
        .iter()
        .map(|(name, _)| (make_key(name.as_bytes(), &salt), name.clone()))
        .collect();
    keyed.sort_by(|a, b| a.0.cmp(&b.0));

    keyed.into_iter().map(|(_, name)| name).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn matches_python_reference_output() {
        let scores: Vec<(String, i64)> = vec![
            ("A".into(), 0),
            ("B".into(), 1),
            ("C".into(), 2),
            ("D".into(), 3),
            ("E".into(), 4),
        ];
        let result = permute(&scores, b"");
        let joined: String = result.iter().map(|s| s.as_str()).collect();
        assert_eq!(joined, "BEACD");
    }

    #[test]
    fn order_of_input_does_not_matter() {
        let scores1: Vec<(String, i64)> = vec![("A".into(), 0), ("B".into(), 1), ("C".into(), 2)];
        let scores2: Vec<(String, i64)> = vec![("C".into(), 2), ("A".into(), 0), ("B".into(), 1)];
        assert_eq!(permute(&scores1, b""), permute(&scores2, b""));
    }

    #[test]
    fn magic_changes_permutation() {
        let scores: Vec<(String, i64)> = vec![
            ("A".into(), 0),
            ("B".into(), 1),
            ("C".into(), 2),
            ("D".into(), 3),
            ("E".into(), 4),
        ];
        let r1 = permute(&scores, b"");
        let r2 = permute(&scores, &[42]);
        assert_ne!(r1, r2);
    }

    #[test]
    fn magic_8byte_matches_python() {
        let scores: Vec<(String, i64)> = vec![
            ("A".into(), 0),
            ("B".into(), 1),
            ("C".into(), 2),
            ("D".into(), 3),
            ("E".into(), 4),
        ];
        let join = |r: &[String]| -> String { r.iter().map(|s| s.as_str()).collect() };

        assert_eq!(join(&permute(&scores, &0u64.to_le_bytes())), "ABCDE");
        assert_eq!(join(&permute(&scores, &1u64.to_le_bytes())), "BACED");
        assert_eq!(join(&permute(&scores, &2u64.to_le_bytes())), "CDBEA");
        assert_eq!(join(&permute(&scores, &3u64.to_le_bytes())), "EBCDA");
    }

    #[test]
    fn int2bytes_encodes_correctly() {
        assert_eq!(int2bytes(0), vec![0, 0]);
        assert_eq!(int2bytes(1), vec![0, 1, 0]);
        assert_eq!(int2bytes(256), vec![0, 0, 1, 0]);
    }

    #[test]
    fn equal_scores_still_permutes() {
        let scores: Vec<(String, i64)> = vec![
            ("A".into(), 1),
            ("B".into(), 1),
            ("C".into(), 1),
            ("D".into(), 1),
        ];
        let result = permute(&scores, b"");
        assert_eq!(result.len(), 4);
        let joined: String = result.iter().map(|s| s.as_str()).collect();
        assert_eq!(joined, "BDCA");
    }
}
