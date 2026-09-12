"""
Vigenere Cipher Cryptanalysis
=============================
Breaks a Vigenere-encrypted ciphertext using:
    1. Kasiski Examination  -> guesses the key length
    2. Index of Coincidence -> confirms the best key length
    3. Frequency Analysis   -> recovers each letter of the key
    4. Verification         -> re-encrypts the plaintext to double check


HOW TO RUN
----------
1. Open a terminal and move into your Cryptlab07 folder.
2. Run:
       python attacks/vigenere_kasiski_attack.py
   (You can also run it directly from inside the attacks folder with
   just:  python vigenere_kasiski_attack.py  -- it will still find the
   datasets folder correctly.)
3. No extra libraries are needed, everything used is from the
   Python standard library (os, collections, math).

OUTPUT
------
The script prints, in order:
    - the cleaned ciphertext
    - Kasiski candidate key lengths (with vote counts)
    - Index of Coincidence score for each candidate
    - the final estimated key length
    - a frequency table (A-Z counts) for every group
    - the recovered key
    - the recovered plaintext
    - a verification result (True/False)
"""

import os
from collections import Counter


# ----------------------------------------------------------------------
# Standard English letter frequency table (in %).
# Used later to figure out which Caesar shift was used on each group.
# ----------------------------------------------------------------------
ENGLISH_FREQ = {
    'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2, 'G': 2.0,
    'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.77, 'L': 4.0, 'M': 2.4, 'N': 6.7,
    'O': 7.5, 'P': 1.9, 'Q': 0.095, 'R': 6.0, 'S': 6.3, 'T': 9.1, 'U': 2.8,
    'V': 0.98, 'W': 2.4, 'X': 0.15, 'Y': 2.0, 'Z': 0.074
}


# ========================================================================
# STEP 1: PREPROCESSING
# ========================================================================
def clean_ciphertext(text):
    """
    Remove spaces, digits, punctuation and line breaks, and convert
    everything to uppercase, leaving only the letters A-Z.
    """
    return ''.join(ch.upper() for ch in text if ch.isalpha())


# ========================================================================
# STEP 2: KASISKI EXAMINATION
# ========================================================================
def find_repeated_patterns(text, seq_len=3):
    """
    Slide a window of length `seq_len` across the text and record the
    starting position of every occurrence of every substring.
    Only sequences that repeat 2+ times are kept, because a repeated
    sequence in the ciphertext usually means the SAME plaintext sequence
    was encrypted with the SAME part of the key (a coincidence that lets
    us guess the key length).

    Returns: { "ABC": [pos1, pos2, ...], ... }
    """
    positions = {}
    for i in range(len(text) - seq_len + 1):
        seq = text[i:i + seq_len]
        positions.setdefault(seq, []).append(i)

    # keep only patterns that occurred more than once
    repeated = {seq: pos_list for seq, pos_list in positions.items() if len(pos_list) > 1}
    return repeated


def calculate_distances(repeated_patterns):
    """
    For every repeated pattern, compute the distance between every pair
    of its occurrences. These distances are all likely multiples of the
    true key length.
    """
    distances = []
    for pos_list in repeated_patterns.values():
        for i in range(len(pos_list) - 1):
            for j in range(i + 1, len(pos_list)):
                distances.append(pos_list[j] - pos_list[i])
    return distances


def find_factors(number, max_len=20):
    """
    Return every factor of `number` between 2 and `max_len`.
    (Vigenere keys used in practice/exercises are rarely longer than 20.)
    """
    factors = []
    for i in range(2, max_len + 1):
        if number % i == 0:
            factors.append(i)
    return factors


def kasiski_analysis(ciphertext, seq_len=3):
    """
    Runs the full Kasiski test:
        1. find repeated sequences of length `seq_len`
        2. measure the distance between repeats
        3. factor every distance
        4. tally how many times each factor appears

    A factor that shows up very often across all the distances is a
    strong candidate for the key length (because it evenly divides many
    of the repeat-distances).

    Returns a list of (key_length, votes) sorted by votes, descending.
    """
    repeated = find_repeated_patterns(ciphertext, seq_len)
    distances = calculate_distances(repeated)

    factor_votes = Counter()
    for dist in distances:
        for factor in find_factors(dist):
            factor_votes[factor] += 1

    return factor_votes.most_common()


# ========================================================================
# INDEX OF COINCIDENCE (used to double-check the Kasiski guess)
# ========================================================================
def calculate_ic(text):
    """
    The Index of Coincidence (IC) estimates the probability that two
    random letters picked from the text are identical.
        - Plain English text has an IC around 0.065 - 0.070
        - Random / poorly-grouped ciphertext has an IC around 0.038

    We use this to check which candidate key length produces groups
    that individually "look like" English (i.e. each group was
    encrypted with a single, consistent Caesar shift).
    """
    n = len(text)
    if n <= 1:
        return 0.0
    freqs = Counter(text)
    numerator = sum(f * (f - 1) for f in freqs.values())
    denominator = n * (n - 1)
    return numerator / denominator


def best_key_length_by_ic(ciphertext, candidates):
    """
    For each candidate key length: split the ciphertext into that many
    groups, compute the average IC across the groups, and compare it to
    the expected English IC (~0.067). The candidate whose average IC is
    closest to 0.067 is chosen as the final key length.

    Returns (best_length, {length: avg_ic, ...})
    """
    scores = {}
    for length in candidates:
        groups = split_into_groups(ciphertext, length)
        avg_ic = sum(calculate_ic(g) for g in groups) / len(groups)
        scores[length] = avg_ic

    best_length = min(scores, key=lambda k: abs(scores[k] - 0.067))
    return best_length, scores


# ========================================================================
# STEP 3 & 4: SPLITTING INTO GROUPS + FREQUENCY ANALYSIS
# ========================================================================
def split_into_groups(ciphertext, key_length):
    """
    Split the ciphertext into `key_length` groups, where group i holds
    every letter at a position where (position % key_length == i).
    All letters inside one group were encrypted with the SAME key
    letter, so each group behaves like ordinary Caesar-cipher text.
    """
    groups = ['' for _ in range(key_length)]
    for index, ch in enumerate(ciphertext):
        groups[index % key_length] += ch
    return groups


def frequency_analysis(group):
    """
    Count how many times each letter A-Z appears in a single group.
    Returns a dict: {"A": count, "B": count, ..., "Z": count}
    """
    counts = Counter(group)
    return {letter: counts.get(letter, 0) for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}


def print_frequency_table(groups):
    """
    Nicely prints the A-Z frequency count for every group.
    """
    for idx, group in enumerate(groups):
        freqs = frequency_analysis(group)
        print(f"\nGroup {idx + 1} (length={len(group)} letters):")
        row = "  "
        for letter, count in freqs.items():
            row += f"{letter}:{count:<3} "
        print(row)


# ========================================================================
# STEP 5: FINDING THE SHIFT / KEY
# ========================================================================
def find_shift(group):
    """
    Try every possible Caesar shift (0-25) on this group. For each
    shift, "undo" it and compare the resulting letter frequencies to
    standard English frequencies using a chi-squared style score:

        score = sum( (observed - expected)^2 / expected )

    A LOW score means the decrypted letters closely match normal
    English text, so the shift with the lowest score is our best guess
    for the key letter used on this group.
    """
    best_shift = 0
    best_score = float('inf')

    for shift in range(26):
        # decrypt (undo the shift) for every letter in the group
        decrypted = ''.join(
            chr((ord(ch) - ord('A') - shift) % 26 + ord('A')) for ch in group
        )
        counts = Counter(decrypted)
        n = len(decrypted)

        score = 0.0
        for letter, expected_pct in ENGLISH_FREQ.items():
            expected = expected_pct / 100 * n
            observed = counts.get(letter, 0)
            score += (observed - expected) ** 2 / (expected if expected > 0 else 1)

        if score < best_score:
            best_score = score
            best_shift = shift

    return best_shift


def find_key(ciphertext, key_length):
    """
    Splits the ciphertext into groups, finds the best shift for each
    group, and converts each shift number into a key LETTER
    (shift 0 -> 'A', shift 1 -> 'B', ... shift 25 -> 'Z').
    """
    groups = split_into_groups(ciphertext, key_length)
    key = ''
    for group in groups:
        shift = find_shift(group)
        key += chr(shift + ord('A'))
    return key


# ========================================================================
# STEP 6: ENCRYPTION / DECRYPTION
# ========================================================================
def vigenere_decrypt(ciphertext, key):
    """
    Standard Vigenere decryption.
    For each ciphertext letter, subtract the shift of the matching key
    letter (the key repeats/cycles for the whole length of the text).
    """
    plaintext = ''
    for i, ch in enumerate(ciphertext):
        shift = ord(key[i % len(key)]) - ord('A')
        plaintext += chr((ord(ch) - ord('A') - shift) % 26 + ord('A'))
    return plaintext


def vigenere_encrypt(plaintext, key):
    """
    Standard Vigenere encryption.
    For each plaintext letter, add the shift of the matching key letter.
    This is used afterwards to VERIFY the recovered key and plaintext.
    """
    ciphertext = ''
    for i, ch in enumerate(plaintext):
        shift = ord(key[i % len(key)]) - ord('A')
        ciphertext += chr((ord(ch) - ord('A') + shift) % 26 + ord('A'))
    return ciphertext


# ========================================================================
# STEP 8: VERIFICATION
# ========================================================================
def verify(original_ciphertext, recovered_plaintext, recovered_key):
    """
    Re-encrypts the recovered plaintext with the recovered key and
    checks whether the result matches the original ciphertext exactly.
    """
    re_encrypted = vigenere_encrypt(recovered_plaintext, recovered_key)
    return re_encrypted == original_ciphertext


# ========================================================================
# MAIN PROGRAM
# ========================================================================
def main():
    # Work out file paths relative to THIS script's location, so it
    # matches the Cryptlab07/attacks and Cryptlab07/datasets structure
    # no matter where the project folder is on disk.
    script_dir = os.path.dirname(os.path.abspath(__file__))     # .../Cryptlab07/attacks
    project_root = os.path.dirname(script_dir)                  # .../Cryptlab07
    dataset_path = os.path.join(project_root, "datasets", "ciphertextass6cd.txt")

    # The ciphertext given for this group (Odd Group No. -> Ciphertext 1).
    # If datasets/ciphertext1.txt does not already exist, it is created
    # automatically so the project's datasets folder is populated.
    raw_ciphertext = """DAZFI SFSPA VQLSN PXYSZ WXALC DAFGQ UISMT PHZGA
MKTTF TCCFX KFCRG GLPFE TZMMM ZOZDE ADWVZ WMWKV GQSOH QSVHP
WFKLS LEASE PWHMJ EGKPU RVSXJ XVBWV POSDE TEQTX OBZIK WCXLW
NUOVJ MJCLL OEOFA ZENVM JILOW ZEKAZ EJAQD ILSWW ESGUG KTZGQ
ZVRMN WTQSE OTKTK PBSTA MQVER MJEGL JQRTL GFJYG SPTZP GTACM
OECBX SESCI YGUFP KVILL TWDKS ZODFW FWEAA PQTFS TQIRG MPMEL
RYELH QSVWB AWMOS DELHM UZGPG YEKZU KWTAM ZJMLS EVJQT GLAWV
OVVXH KWQIL IEUYS ZWXAH HUSZO GMUZQ CIMVZ UVWIF JJHPW VXFSE
TZEDF"""

    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
    if not os.path.exists(dataset_path):
        with open(dataset_path, "w") as f:
            f.write(raw_ciphertext)

    with open(dataset_path, "r") as f:
        raw_text = f.read()

    # ---------------- STEP 1: Preprocess ----------------
    ciphertext = clean_ciphertext(raw_text)
    print("=" * 65)
    print("STEP 1: Cleaned Ciphertext")
    print("=" * 65)
    print(ciphertext)
    print(f"\nTotal letters: {len(ciphertext)}")

    # ---------------- STEP 2: Kasiski Examination ----------------
    print("\n" + "=" * 65)
    print("STEP 2: Kasiski Examination - Candidate Key Lengths")
    print("=" * 65)
    ranked_candidates = kasiski_analysis(ciphertext, seq_len=3)
    print(f"{'Key length':<12}{'Votes'}")
    for length, votes in ranked_candidates[:10]:
        print(f"{length:<12}{votes}")

    # Confirm the best candidate using Index of Coincidence
    top_candidates = [length for length, _ in ranked_candidates[:6]] or [1]
    best_length, ic_scores = best_key_length_by_ic(ciphertext, top_candidates)

    print("\nIndex of Coincidence per candidate (English target ~0.067):")
    for length, score in ic_scores.items():
        print(f"   key length {length:<3} -> avg IC = {score:.4f}")

    print(f"\n>>> ESTIMATED KEY LENGTH: {best_length}")

    # ---------------- STEP 3 & 4: Groups + Frequency Analysis ----------------
    print("\n" + "=" * 65)
    print("STEP 3 & 4: Splitting into Groups + Frequency Analysis")
    print("=" * 65)
    groups = split_into_groups(ciphertext, best_length)
    print_frequency_table(groups)

    # ---------------- STEP 5: Recover the key ----------------
    print("\n" + "=" * 65)
    print("STEP 5: Recovering the Key")
    print("=" * 65)
    recovered_key = find_key(ciphertext, best_length)
    print(f">>> RECOVERED KEY: {recovered_key}")

    # ---------------- STEP 6: Decrypt ----------------
    print("\n" + "=" * 65)
    print("STEP 6: Decrypting the Ciphertext")
    print("=" * 65)
    recovered_plaintext = vigenere_decrypt(ciphertext, recovered_key)
    print(recovered_plaintext)

    # ---------------- STEP 8: Verify ----------------
    print("\n" + "=" * 65)
    print("STEP 8: Verification (re-encrypt and compare)")
    print("=" * 65)
    is_correct = verify(ciphertext, recovered_plaintext, recovered_key)
    print("Re-encrypted ciphertext matches the original:", is_correct)


if __name__ == "__main__":
    main()