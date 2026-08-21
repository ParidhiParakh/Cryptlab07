"""
chi_square_attack.py

Cryptanalysis Algorithm 2: Chi-Square Statistic Attack.

English text has a well-known, stable letter-frequency distribution
(e.g. 'e' ~12.7%, 't' ~9.1%, ... 'z' ~0.07%). A Shift Cipher merely
rotates this distribution around the alphabet — it does not change
its *shape*. So for the correct key, the letter-frequency histogram
of the decrypted candidate plaintext should closely match the known
English distribution, while wrong keys produce a mismatched
histogram.

Chi-square algorithm
---------------------
    1. For each key k = 0..25, decrypt the ciphertext.
    2. Count letter frequencies (A-Z, case-insensitive) in the
       candidate plaintext -> observed counts O_i.
    3. Compute expected counts E_i = (expected English frequency of
       letter i) * (total letters in candidate text).
    4. Compute the chi-square statistic:
           chi^2 = sum_i ( (O_i - E_i)^2 / E_i )
       summed over the 26 letters.
    5. The key with the SMALLEST chi-square statistic is the best
       statistical fit to English and is chosen as the predicted key.

This method is purely statistical: it needs no dictionary at all,
and can succeed even on ciphertexts full of unusual/rare words — but
it needs enough letters for frequencies to be meaningful. A common
rule of thumb in cryptanalysis courses is that fewer than ~20-30
letters of ciphertext makes the letter-frequency signal too noisy to
trust.
"""

from collections import Counter
from typing import Dict, Tuple

from shift_cipher import decrypt

# Standard English single-letter frequency table (in percent), the
# same reference distribution used throughout classical
# cryptanalysis literature.
ENGLISH_FREQUENCIES: Dict[str, float] = {
    'a': 8.167, 'b': 1.492, 'c': 2.782, 'd': 4.253, 'e': 12.702,
    'f': 2.228, 'g': 2.015, 'h': 6.094, 'i': 6.966, 'j': 0.153,
    'k': 0.772, 'l': 4.025, 'm': 2.406, 'n': 6.749, 'o': 7.507,
    'p': 1.929, 'q': 0.095, 'r': 5.987, 's': 6.327, 't': 9.056,
    'u': 2.758, 'v': 0.978, 'w': 2.360, 'x': 0.150, 'y': 1.974,
    'z': 0.074,
}


def letter_counts(text: str) -> Counter:
    """Case-insensitive count of A-Z letters only (ignores everything else)."""
    return Counter(ch.lower() for ch in text if ch.isalpha())


def chi_square_statistic(text: str) -> float:
    """
    Compute the chi-square statistic comparing the letter-frequency
    distribution of `text` against the standard English distribution.
    Lower values mean a closer match to English.
    """
    counts = letter_counts(text)
    total_letters = sum(counts.values())
    if total_letters == 0:
        return float("inf")

    chi2 = 0.0
    for letter, expected_pct in ENGLISH_FREQUENCIES.items():
        observed = counts.get(letter, 0)
        expected = expected_pct / 100.0 * total_letters
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    return chi2


def chi_square_attack(
    ciphertext: str,
) -> Tuple[int, Dict[int, float], Dict[int, str]]:
    """
    Try all 26 keys, compute the chi-square statistic for each
    candidate plaintext, and return:
        best_key   - the key with the LOWEST chi-square statistic
        scores     - {key: chi-square value} for all 26 keys
        candidates - {key: decrypted candidate text} for all 26 keys
    """
    scores: Dict[int, float] = {}
    candidates: Dict[int, str] = {}

    for key in range(26):
        candidate = decrypt(ciphertext, key)
        candidates[key] = candidate
        scores[key] = chi_square_statistic(candidate)

    best_key = min(scores, key=scores.get)
    return best_key, scores, candidates


if __name__ == "__main__":
    from shift_cipher import encrypt

    pt = "The quick brown fox jumps over the lazy dog"
    key = 7
    ct = encrypt(pt, key)

    best_key, scores, candidates = chi_square_attack(ct)
    print(f"Ciphertext         : {ct}")
    print(f"Actual key         : {key}")
    print(f"Predicted key      : {best_key}")
    print(f"Recovered plaintext: {candidates[best_key]}")
    print("\nAll key chi-square scores (sorted best first, lower = better):")
    for k in sorted(scores, key=scores.get):
        print(f"  key={k:2d}  chi2={scores[k]:8.2f}  text={candidates[k]!r}")
