/// Deterministic pseudo-random tiebreaking for STAR elections.
/// Rust port of startie
///
/// Produces a reproducible permutation of candidate names by sorting them
/// using SHA-512 hashes of (canonical_salt, candidate_name) pairs.
/// Results match the Python and JavaScript implementations.
use sha2::{Digest, Sha512};

const VERSION: &[u8] = b"STAR-TIE-512-v2";

/// Encode a non-negative integer as an 8-byte little-endian value.
/// This fixed-width representation removes variable-length concatenation
/// ambiguities.
fn int2bytes(n: i64) -> [u8; 8] {
    assert!(n >= 0, "n must be nonnegative");
    (n as u64).to_le_bytes()
}

/// Build the canonical salt digest: SHA-512 digest of VERSION + magic +
/// all scores in UTF-8-sorted name order.
fn canonical_salt_digest(candidates: &mut [(String, i64)], magic: &[u8]) -> Vec<u8> {
    let mut h = Sha512::new();
    h.update(VERSION);
    h.update(magic);

    // Sort by raw UTF-8 bytes of the name
    candidates.sort_by(|a, b| a.0.as_bytes().cmp(b.0.as_bytes()));

    // Hash the scores in that order
    for (_, score) in candidates.iter() {
        h.update(int2bytes(*score));
    }
    h.finalize().to_vec()
}

/// Compute the sort key for a single candidate: hash(salt_digest + name_utf8).
fn make_key(name_utf8: &[u8], salt_digest: &[u8]) -> Vec<u8> {
    let mut h = Sha512::new();
    h.update(salt_digest);
    h.update(name_utf8);
    h.finalize().to_vec()
}

/// Return a deterministic pseudo-random permutation of candidate names.
///
/// `scores` maps candidate names to their scores (totals from the scoring phase).
/// `magic` is mandatory extra entropy bytes for adversarial or high-stakes elections.
///
/// The result is reproducible across Python, JavaScript, and this Rust implementation.
pub fn permute(scores: &[(String, i64)], magic: &[u8]) -> Vec<String> {
    if !magic.is_empty() && magic.len() != 8 {
        panic!("magic must be 0 or 8 bytes for STAR-TIE-512-v2");
    }
    let mut candidates: Vec<(String, i64)> = scores.to_vec();

    // Build the canonical salt digest (also sorts candidates by UTF-8 name)
    let salt_digest = canonical_salt_digest(&mut candidates, magic);

    // Compute hash keys and sort by them
    let mut keyed: Vec<(Vec<u8>, String)> = candidates
        .iter()
        .map(|(name, _)| (make_key(name.as_bytes(), &salt_digest), name.clone()))
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
        assert_eq!(joined, "ABDEC");
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
        let r2 = permute(&scores, &0u64.to_le_bytes());
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

        assert_eq!(join(&permute(&scores, &0u64.to_le_bytes())), "CBDEA");
        assert_eq!(join(&permute(&scores, &1u64.to_le_bytes())), "ADCEB");
        assert_eq!(join(&permute(&scores, &2u64.to_le_bytes())), "CADEB");
        assert_eq!(join(&permute(&scores, &3u64.to_le_bytes())), "DCABE");
    }

    #[test]
    fn int2bytes_encodes_correctly() {
        assert_eq!(int2bytes(0), [0, 0, 0, 0, 0, 0, 0, 0]);
        assert_eq!(int2bytes(1), [1, 0, 0, 0, 0, 0, 0, 0]);
        assert_eq!(int2bytes(256), [0, 1, 0, 0, 0, 0, 0, 0]);
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
        assert_eq!(joined, "DBAC");
    }
}
