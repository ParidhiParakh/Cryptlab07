"""
brute_force_dictionary.py

Cryptanalysis Algorithm 1: Brute-Force Key Search with Dictionary
Scoring.

Since a Shift Cipher only has 26 possible keys, an attacker can
simply try every key (brute force) and use a scoring function to
decide which resulting candidate plaintext is "most English".

Dictionary-scoring algorithm
-----------------------------
    1. Decrypt the ciphertext with every key k = 0 .. 25.
    2. Tokenize the resulting candidate plaintext into words
       (alphabetic runs, lower-cased).
    3. score(k) = number of candidate words that are found in a
       large English dictionary file.
    4. The key with the HIGHEST score is chosen as the predicted
       key, since genuine English plaintext will contain far more
       real dictionary words than any of the 25 wrong shifts.

When this attack tends to fail
-------------------------------
    - Very short ciphertexts (few words) give too little signal —
      a wrong key can occasionally match 1-2 dictionary words by
      chance.
    - Ciphertext made mostly of proper nouns, numbers, abbreviations
      or technical jargon may not match many dictionary entries even
      under the correct key.
    - A dictionary that is too small (missing common words) will
      under-score the correct key.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from shift_cipher import decrypt

DEFAULT_DICTIONARY_PATH = (
    Path(__file__).resolve().parent.parent / "dictionary" / "english_words.txt"
)

_WORD_RE = re.compile(r"[a-zA-Z']+")


def load_dictionary(path: Path = DEFAULT_DICTIONARY_PATH) -> Set[str]:
    """Load a newline-separated word list into a lowercase set."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return {line.strip().lower() for line in f if line.strip()}


def _tokenize(text: str) -> List[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]


def score_text(text: str, dictionary: Set[str]) -> int:
    """Number of tokens in `text` that are valid dictionary words."""
    words = _tokenize(text)
    if not words:
        return 0
    return sum(1 for w in words if w in dictionary)


def brute_force_dictionary_attack(
    ciphertext: str, dictionary: Set[str]
) -> Tuple[int, Dict[int, int], Dict[int, str]]:
    """
    Try all 26 keys, score each candidate plaintext against the
    dictionary, and return:
        best_key   - the key with the highest dictionary score
        scores     - {key: score} for all 26 keys
        candidates - {key: decrypted candidate text} for all 26 keys
    """
    scores: Dict[int, int] = {}
    candidates: Dict[int, str] = {}

    for key in range(26):
        candidate = decrypt(ciphertext, key)
        candidates[key] = candidate
        scores[key] = score_text(candidate, dictionary)

    best_key = max(scores, key=scores.get)
    return best_key, scores, candidates


if __name__ == "__main__":
    from shift_cipher import encrypt

    dictionary = load_dictionary()
    pt = "The quick brown fox jumps over the lazy dog"
    key = 7
    ct = encrypt(pt, key)

    best_key, scores, candidates = brute_force_dictionary_attack(ct, dictionary)
    print(f"Ciphertext         : {ct}")
    print(f"Actual key         : {key}")
    print(f"Predicted key      : {best_key}")
    print(f"Recovered plaintext: {candidates[best_key]}")
    print("\nAll key scores (sorted best first):")
    for k in sorted(scores, key=scores.get, reverse=True):
        print(f"  key={k:2d}  score={scores[k]:3d}  text={candidates[k]!r}")
